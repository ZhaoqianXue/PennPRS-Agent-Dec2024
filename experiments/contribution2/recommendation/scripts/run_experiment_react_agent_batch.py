"""True single-agent ReAct harness for c2, executed on the OpenAI Batch surface.

This is not iterD refinement. The agent is not pre-fed the SKILL corpus or h2
records. It receives the target trait and visible candidate list, then controls
the loop:

  - call read_skill_section(section_id), or
  - call get_heritability_records(trait), or
  - terminate by emitting the FinalDecision JSON.

The harness runs each ReAct turn as a Batch API job, executes local tools
between turns, appends tool observations, and resubmits remaining active
conversations until termination or budget. This isolates the delivery-surface
dimension while preserving the "true ReAct" constraint.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from experiments.contribution2.recommendation.scripts.run_experiment_react_agent import (
    FinalDecision,
    _execute_tool,
    _final_response_format,
    _tool_schemas,
)
from src.server.core.within_prompts.archive.selectors_pre_cleanup_20260615 import (
    WITHIN_EVIDENCE_SUFFICIENCY_REACT_SYSTEM_PROMPT,
    WITHIN_GUARDED_REACT_SYSTEM_PROMPT,
    WITHIN_TRUE_REACT_SYSTEM_PROMPT,
)


TRUE_REACT_SYSTEM_PROMPT = WITHIN_TRUE_REACT_SYSTEM_PROMPT



EVIDENCE_SUFFICIENCY_SYSTEM_PROMPT = WITHIN_EVIDENCE_SUFFICIENCY_REACT_SYSTEM_PROMPT



GUARDED_REACT_SYSTEM_PROMPT = WITHIN_GUARDED_REACT_SYSTEM_PROMPT



def _system_prompt(prompt_mode: str) -> str:
    if prompt_mode == "minimal":
        return TRUE_REACT_SYSTEM_PROMPT
    if prompt_mode == "evidence_sufficiency":
        return EVIDENCE_SUFFICIENCY_SYSTEM_PROMPT
    if prompt_mode == "guarded":
        return GUARDED_REACT_SYSTEM_PROMPT
    raise ValueError(f"Unknown prompt mode: {prompt_mode}")


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False))
            handle.write("\n")


def _file_content(client: OpenAI, file_id: str) -> str:
    content = client.files.retrieve_content(file_id)
    if isinstance(content, bytes):
        return content.decode("utf-8")
    return str(content)


def _extract_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "".join(parts).strip()
    return str(content or "").strip()


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        row["ontology"]: list(row.get("candidate_models_visible_to_llm") or [])
        for row in disease_metadata
    }


def _initial_user_message(target_trait: str, candidate_models: list[dict[str, Any]]) -> str:
    payload = {
        "target_trait": target_trait,
        "candidate_models": candidate_models,
    }
    return (
        "Recommend the best PGS for the target trait below. The candidate list "
        "is fixed. Use read_skill_section and get_heritability_records only as "
        "needed, then emit the final JSON decision.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _submit_batch_and_wait(
    *,
    client: OpenAI,
    jsonl_path: Path,
    output_jsonl_path: Path,
    error_jsonl_path: Path,
    job_json_path: Path,
    metadata: dict[str, str],
    poll_interval_seconds: int,
) -> list[dict[str, Any]]:
    with jsonl_path.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata=metadata,
    )
    job = {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "request_file": str(jsonl_path),
        "status": batch.status,
        "batch": batch.model_dump(),
    }
    _write_json(job_json_path, job)
    print(f"Submitted batch {batch.id} for {jsonl_path.name}; status={batch.status}")

    terminal = {"completed", "failed", "expired", "cancelled", "cancelling"}
    while batch.status not in terminal:
        time.sleep(poll_interval_seconds)
        batch = client.batches.retrieve(batch.id)
        counts = batch.request_counts.model_dump() if batch.request_counts else None
        print(f"  batch {batch.id}: status={batch.status}, counts={counts}")

    job["status"] = batch.status
    job["batch"] = batch.model_dump()
    _write_json(job_json_path, job)
    if batch.status != "completed":
        raise RuntimeError(f"Batch {batch.id} ended with status={batch.status}")
    if not batch.output_file_id:
        raise RuntimeError(f"Batch {batch.id} completed without output_file_id")

    raw_output = _file_content(client, batch.output_file_id)
    output_jsonl_path.write_text(raw_output, encoding="utf-8")
    if batch.error_file_id:
        error_jsonl_path.write_text(_file_content(client, batch.error_file_id), encoding="utf-8")

    return [json.loads(line) for line in raw_output.splitlines() if line.strip()]


def _body_message(record: dict[str, Any]) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    custom_id = record.get("custom_id")
    response = record.get("response") or {}
    if response.get("status_code") != 200:
        body = response.get("body") or {}
        return None, f"{custom_id}: HTTP {response.get('status_code')}: {json.dumps(body.get('error') or body, ensure_ascii=False)}"
    body = response.get("body") or {}
    choices = body.get("choices") or []
    if not choices:
        return None, f"{custom_id}: no choices returned"
    return (choices[0] or {}).get("message") or {}, None


def _assistant_message_from_tool_calls(message: dict[str, Any]) -> dict[str, Any]:
    assistant: dict[str, Any] = {"role": "assistant"}
    content = message.get("content")
    if content:
        assistant["content"] = _extract_message_content(content)
    tool_calls = message.get("tool_calls") or []
    if tool_calls:
        assistant["tool_calls"] = [
            {
                "id": tc.get("id"),
                "type": tc.get("type") or "function",
                "function": {
                    "name": ((tc.get("function") or {}).get("name")),
                    "arguments": ((tc.get("function") or {}).get("arguments") or "{}"),
                },
            }
            for tc in tool_calls
        ]
    return assistant


def _batch_request(
    *,
    custom_id: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    seed: int,
) -> dict[str, Any]:
    tools = [tool for tool in _tool_schemas() if tool["function"]["name"] != "submit_recommendation"]
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": temperature,
            "seed": seed,
            "response_format": _final_response_format(),
        },
    }


def _missing_evidence_requirements(state: dict[str, Any], evidence_gate: str) -> list[str]:
    if evidence_gate == "none":
        return []

    skill_sections: list[str] = []
    used_h2 = False
    for entry in state.get("tool_call_log") or []:
        if entry.get("tool_name") == "get_heritability_records":
            used_h2 = True
        if entry.get("tool_name") == "read_skill_section":
            try:
                sid = json.loads(entry.get("arguments") or "{}").get("section_id")
            except Exception:
                sid = None
            if sid:
                skill_sections.append(str(sid))

    missing: list[str] = []
    if evidence_gate == "require_skill_h2":
        if not skill_sections:
            missing.append("read_skill_section")
        if not used_h2:
            missing.append("get_heritability_records")
        return missing

    if evidence_gate == "balanced_skill_h2":
        metric_sections = {"performance_metrics"}
        context_sections = {
            "trait_labels",
            "training_cohorts_ancestry",
            "publication_context",
            "validation_sample_size",
            "method_name",
        }
        if not any(sid in metric_sections for sid in skill_sections):
            missing.append("read_skill_section:performance_metrics")
        if not any(sid in context_sections for sid in skill_sections):
            missing.append("read_skill_section:context_section")
        if not used_h2:
            missing.append("get_heritability_records")
        return missing

    if evidence_gate == "core_skill_h2":
        if "decision_core" not in skill_sections:
            missing.append("read_skill_section:decision_core")
        if not used_h2:
            missing.append("get_heritability_records")
        return missing

    raise ValueError(f"Unknown evidence gate: {evidence_gate}")


def _apply_message(state: dict[str, Any], message: dict[str, Any], *, evidence_gate: str) -> bool:
    """Apply assistant message. Return True if the conversation remains active."""
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        try:
            parsed = FinalDecision.model_validate_json(
                _extract_message_content(message.get("content"))
            ).model_dump()
        except Exception as exc:
            state["error"] = f"final JSON parse {type(exc).__name__}: {exc}"
            return False
        if parsed.get("outcome") == "NO_MATCH_FOUND":
            parsed["best_model_id"] = None
        else:
            bid = parsed.get("best_model_id")
            if not bid or str(bid).strip() not in state["candidate_id_set"]:
                state["error"] = f"invalid best_model_id={bid!r}"
                return False

        missing = _missing_evidence_requirements(state, evidence_gate)
        if missing:
            state["evidence_gate_rejections"] = int(state.get("evidence_gate_rejections") or 0) + 1
            state["messages"].append({
                "role": "assistant",
                "content": json.dumps(parsed, ensure_ascii=False),
            })
            state["messages"].append({
                "role": "user",
                "content": (
                    "EvidenceGuard rejected this terminal answer because required "
                    f"tool evidence is missing: {', '.join(missing)}. Continue the "
                    "same ReAct loop, call the missing tool(s), then emit a revised "
                    "FinalDecision JSON grounded in those observations. The guard "
                    "does not judge which PGS is correct; it only enforces that "
                    "every final answer uses the prs_model_evaluator skill and h2."
                ),
            })
            state["tool_call_log"].append({
                "kind": "evidence_gate_rejection",
                "missing": missing,
                "terminal_preview": json.dumps(parsed, ensure_ascii=False)[:300],
            })
            return True

        state["decision"] = parsed
        state["messages"].append({"role": "assistant", "content": json.dumps(parsed, ensure_ascii=False)})
        return False

    state["messages"].append(_assistant_message_from_tool_calls(message))
    for tc in tool_calls:
        fn = tc.get("function") or {}
        name = fn.get("name")
        args = fn.get("arguments") or "{}"
        observation, _ = _execute_tool(
            name=name,
            arguments=args,
            target_trait=state["ontology"],
            candidate_id_set=state["candidate_id_set"],
        )
        state["tool_call_log"].append({
            "tool_name": name,
            "arguments": args,
            "observation_preview": observation[:300],
        })
        state["messages"].append({
            "role": "tool",
            "tool_call_id": tc.get("id"),
            "content": observation,
        })
    return True


def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    temperature: float,
    seed: int,
    max_iterations: int,
    poll_interval_seconds: int,
    prompt_mode: str,
    evidence_gate: str,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    candidate_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    print(f"Run directory: {output_run_dir}")
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests)")

    states: dict[str, dict[str, Any]] = {}
    for request in requests:
        ontology = request["ontology"]
        candidate_models = candidate_by_ontology.get(ontology, [])
        states[request["custom_id"]] = {
            "custom_id": request["custom_id"],
            "ontology": ontology,
            "candidate_models": candidate_models,
            "candidate_id_set": {str(m.get("id")) for m in candidate_models if m.get("id")},
            "messages": [
                {"role": "system", "content": _system_prompt(prompt_mode)},
                {"role": "user", "content": _initial_user_message(ontology, candidate_models)},
            ],
            "tool_call_log": [],
            "decision": None,
            "error": None,
            "evidence_gate_rejections": 0,
        }

    client = _client()
    active = set(states)
    for iteration in range(max_iterations):
        if not active:
            break
        batch_requests = [
            _batch_request(
                custom_id=custom_id,
                model=model,
                messages=states[custom_id]["messages"],
                temperature=temperature,
                seed=seed,
            )
            for custom_id in sorted(active)
        ]
        jsonl_path = output_run_dir / f"experiment_react_agent_batch_iter{iteration}_requests.jsonl"
        _write_jsonl(jsonl_path, batch_requests)
        records = _submit_batch_and_wait(
            client=client,
            jsonl_path=jsonl_path,
            output_jsonl_path=output_run_dir / f"experiment_react_agent_batch_iter{iteration}_output.jsonl",
            error_jsonl_path=output_run_dir / f"experiment_react_agent_batch_iter{iteration}_errors.jsonl",
            job_json_path=output_run_dir / f"experiment_react_agent_batch_iter{iteration}_job.json",
            metadata={"experiment": "contribution2_true_react_agent", "iteration": str(iteration)},
            poll_interval_seconds=poll_interval_seconds,
        )
        next_active: set[str] = set()
        for record in records:
            custom_id = record.get("custom_id")
            state = states.get(custom_id)
            if not state:
                continue
            message, err = _body_message(record)
            if err:
                state["error"] = err
                continue
            if _apply_message(state, message, evidence_gate=evidence_gate):
                next_active.add(custom_id)
        active = next_active
        print(f"ReAct iter {iteration}: remaining active={len(active)}")

    for custom_id in active:
        states[custom_id]["error"] = "max_iterations reached without terminal JSON"

    full_results: list[dict[str, Any]] = []
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in requests:
        custom_id = request["custom_id"]
        state = states[custom_id]
        decision = state.get("decision")
        full_results.append({
            "custom_id": custom_id,
            "ontology": state["ontology"],
            "decision": decision,
            "tool_call_log": state["tool_call_log"],
            "error": state.get("error"),
        })
        if decision is None:
            error_map[custom_id] = state.get("error") or "agent produced no decision"
        else:
            parsed_outputs[custom_id] = {
                "custom_id": custom_id,
                "decisions": [decision],
                "error": None,
            }

    _write_json(output_run_dir / "experiment_react_agent_batch_results.json", full_results)

    without_domain.RESULTS_JSON = output_run_dir / "experiment_react_agent_batch_trial_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_react_agent_batch_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_react_agent_batch_report.md"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
    without_domain._configure_benchmark_sources(
        union_csv=manifest.get("union_csv"),
        ground_truth_dir=manifest.get("ground_truth_dir"),
    )
    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )

    tool_use_counts: dict[str, int] = {}
    section_read_counts: dict[str, int] = {}
    no_decision_count = 0
    evidence_gate_rejections = 0
    for state in states.values():
        if state.get("decision") is None:
            no_decision_count += 1
        evidence_gate_rejections += int(state.get("evidence_gate_rejections") or 0)
        for entry in state.get("tool_call_log") or []:
            name = entry.get("tool_name") or "unknown"
            tool_use_counts[name] = tool_use_counts.get(name, 0) + 1
            if name == "read_skill_section":
                try:
                    sid = json.loads(entry.get("arguments") or "{}").get("section_id")
                except Exception:
                    sid = None
                if sid:
                    section_read_counts[sid] = section_read_counts.get(sid, 0) + 1

    summary["execution_mode"] = "true_react_agent_batch_surface"
    summary["react_agent_batch"] = {
        "max_iterations": max_iterations,
        "temperature": temperature,
        "seed": seed,
        "prompt_mode": prompt_mode,
        "evidence_gate": evidence_gate,
        "evidence_gate_rejections": evidence_gate_rejections,
        "tool_use_counts": tool_use_counts,
        "section_read_counts": section_read_counts,
        "no_decision_count": no_decision_count,
    }
    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    print(f"Results: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-surface true ReAct c2 agent")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-iterations", type=int, default=8)
    parser.add_argument("--poll-interval-seconds", type=int, default=20)
    parser.add_argument("--prompt-mode", choices=["minimal", "evidence_sufficiency", "guarded"], default="minimal")
    parser.add_argument(
        "--evidence-gate",
        choices=["none", "require_skill_h2", "balanced_skill_h2", "core_skill_h2"],
        default="none",
    )
    args = parser.parse_args()

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = (
        Path(__file__).parent.parent
        / "runs"
        / f"react-agent-batch-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    )
    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=run_dir,
        model=args.model,
        temperature=args.temperature,
        seed=args.seed,
        max_iterations=args.max_iterations,
        poll_interval_seconds=args.poll_interval_seconds,
        prompt_mode=args.prompt_mode,
        evidence_gate=args.evidence_gate,
    )
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = (summary.get("trial_hit_at_k") or {}).get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, accuracy={v.get('accuracy')}")
    print(f"\nReAct batch meta: {json.dumps(summary.get('react_agent_batch') or {}, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
