"""Batch-surface ReAct refinement harness for Contribution 2.

This runner tests the architecture dimension that the chat.completions ReAct
rounds could not isolate: delivery surface. Stage 1 is a fresh Batch API
single-shot initial pick using the prepared iterD/minimal-lift request bodies.
Stage 2 is a single-agent ReAct refinement loop, also executed through Batch
API turns. The harness parses tool calls between batch turns, executes the
local get_heritability_records tool, appends observations, and resubmits the
next batch turn until the agent emits a final JSON decision or hits budget.

It is still an agent harness: the Stage 2 LLM decides whether to call the h2
tool, whether to revise, and when to terminate. The benchmark is used only by
the shared summary builder after decisions are complete.
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

from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from experiments.contribution2.recommendation.scripts.run_experiment_react_refinement import (
    FinalDecision,
    Step1Decision,
    _final_response_format,
    _h2_call_safe,
    _h2_tool_schema,
    _refinement_system_prompt,
    _stage2_user_message,
)


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

    records: list[dict[str, Any]] = []
    for line in raw_output.splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


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
    message = (choices[0] or {}).get("message") or {}
    return message, None


def _parse_stage1(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    out: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for record in records:
        custom_id = record.get("custom_id")
        message, err = _body_message(record)
        if err:
            errors[custom_id] = err
            continue
        try:
            decision = Step1Decision.model_validate_json(_extract_message_content(message.get("content")))
            out[custom_id] = decision.model_dump()
        except Exception as exc:
            errors[custom_id] = f"stage1 parse {type(exc).__name__}: {exc}"
    return out, errors


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        row["ontology"]: list(row.get("candidate_models_visible_to_llm") or [])
        for row in disease_metadata
    }


def _stage2_batch_request(
    *,
    custom_id: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    seed: int,
) -> dict[str, Any]:
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": messages,
            "tools": [_h2_tool_schema()],
            "tool_choice": "auto",
            "temperature": temperature,
            "seed": seed,
            "response_format": _final_response_format(),
        },
    }


def _initial_stage2_state(
    *,
    manifest: dict[str, Any],
    stage1_decisions: dict[str, dict[str, Any]],
    refinement_mode: str,
) -> dict[str, dict[str, Any]]:
    candidates = _candidate_summary_lookup(manifest["disease_metadata"])
    by_custom: dict[str, dict[str, Any]] = {}
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        initial_decision = stage1_decisions.get(custom_id)
        if not initial_decision:
            continue
        candidate_models = candidates.get(ontology, [])
        messages = [
            {"role": "system", "content": _refinement_system_prompt(refinement_mode)},
            {"role": "user", "content": _stage2_user_message(ontology, candidate_models, initial_decision)},
        ]
        by_custom[custom_id] = {
            "custom_id": custom_id,
            "ontology": ontology,
            "candidate_models": candidate_models,
            "initial_decision": initial_decision,
            "messages": messages,
            "tool_call_log": [],
            "final_decision": None,
            "error": None,
        }
    return by_custom


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


def _apply_stage2_record(state: dict[str, Any], message: dict[str, Any]) -> bool:
    """Apply one assistant message. Return True if another batch turn is needed."""
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        try:
            final_decision = FinalDecision.model_validate_json(
                _extract_message_content(message.get("content"))
            ).model_dump()
        except Exception as exc:
            state["error"] = f"stage2 final parse {type(exc).__name__}: {exc}"
            state["final_decision"] = state["initial_decision"]
            return False

        candidate_ids = {str(m.get("id")) for m in state["candidate_models"] if m.get("id")}
        bid = final_decision.get("best_model_id")
        if final_decision.get("outcome") == "NO_MATCH_FOUND":
            final_decision["best_model_id"] = None
        elif not bid or str(bid).strip() not in candidate_ids:
            state["error"] = f"stage2 invalid best_model_id={bid!r}; fallback to Stage1"
            state["final_decision"] = state["initial_decision"]
            return False
        state["final_decision"] = final_decision
        return False

    state["messages"].append(_assistant_message_from_tool_calls(message))
    for tc in tool_calls:
        fn = tc.get("function") or {}
        name = fn.get("name")
        args = fn.get("arguments") or "{}"
        if name != "get_heritability_records":
            obs = f"ERROR: unknown tool {name!r}"
        else:
            try:
                parsed_args = json.loads(args) if args else {}
            except Exception as exc:
                obs = f"ERROR parsing arguments: {type(exc).__name__}: {exc}"
            else:
                trait = str(parsed_args.get("trait") or state["ontology"]).strip()
                obs = _h2_call_safe(trait)
        state["tool_call_log"].append({
            "tool_name": name,
            "arguments": args,
            "observation_preview": obs[:400],
        })
        state["messages"].append({
            "role": "tool",
            "tool_call_id": tc.get("id"),
            "content": obs,
        })
    return True


def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    temperature: float,
    seed: int,
    refinement_mode: str,
    max_iterations: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"Run directory: {output_run_dir}")
    print(f"Loaded manifest: {manifest_path} ({len(manifest['requests'])} requests)")
    client = _client()

    # Stage 1: fresh Batch API initial pick, using the exact prepared request bodies.
    stage1_requests = []
    for row in manifest["requests"]:
        req = dict(row["request"])
        body = dict(req["body"])
        body["model"] = model
        body["temperature"] = temperature
        body["seed"] = seed
        req["body"] = body
        stage1_requests.append(req)
    stage1_jsonl = output_run_dir / "experiment_react_refinement_batch_stage1_requests.jsonl"
    _write_jsonl(stage1_jsonl, stage1_requests)
    stage1_records = _submit_batch_and_wait(
        client=client,
        jsonl_path=stage1_jsonl,
        output_jsonl_path=output_run_dir / "experiment_react_refinement_batch_stage1_output.jsonl",
        error_jsonl_path=output_run_dir / "experiment_react_refinement_batch_stage1_errors.jsonl",
        job_json_path=output_run_dir / "experiment_react_refinement_batch_stage1_job.json",
        metadata={"experiment": "contribution2_react_refinement", "stage": "stage1"},
        poll_interval_seconds=poll_interval_seconds,
    )
    stage1_decisions, stage1_errors = _parse_stage1(stage1_records)
    _write_json(output_run_dir / "experiment_react_refinement_batch_stage1_decisions.json", stage1_decisions)
    print(f"Stage 1 parsed: {len(stage1_decisions)} decisions, {len(stage1_errors)} errors")

    states = _initial_stage2_state(
        manifest=manifest,
        stage1_decisions=stage1_decisions,
        refinement_mode=refinement_mode,
    )
    active = set(states)
    for iteration in range(max_iterations):
        if not active:
            break
        requests = [
            _stage2_batch_request(
                custom_id=custom_id,
                model=model,
                messages=states[custom_id]["messages"],
                temperature=temperature,
                seed=seed,
            )
            for custom_id in sorted(active)
        ]
        stage_jsonl = output_run_dir / f"experiment_react_refinement_batch_stage2_iter{iteration}_requests.jsonl"
        _write_jsonl(stage_jsonl, requests)
        records = _submit_batch_and_wait(
            client=client,
            jsonl_path=stage_jsonl,
            output_jsonl_path=output_run_dir / f"experiment_react_refinement_batch_stage2_iter{iteration}_output.jsonl",
            error_jsonl_path=output_run_dir / f"experiment_react_refinement_batch_stage2_iter{iteration}_errors.jsonl",
            job_json_path=output_run_dir / f"experiment_react_refinement_batch_stage2_iter{iteration}_job.json",
            metadata={"experiment": "contribution2_react_refinement", "stage": f"stage2_iter{iteration}"},
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
                state["final_decision"] = state["initial_decision"]
                continue
            needs_next = _apply_stage2_record(state, message)
            if needs_next:
                next_active.add(custom_id)
        active = next_active
        print(f"Stage 2 iter {iteration}: remaining active={len(active)}")

    for custom_id in active:
        states[custom_id]["error"] = "stage2 max_iterations reached; fallback to Stage1"
        states[custom_id]["final_decision"] = states[custom_id]["initial_decision"]

    full_results = []
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = dict(stage1_errors)
    revised = 0
    h2_calls = 0
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        state = states.get(custom_id)
        if not state:
            error_map.setdefault(custom_id, "missing stage2 state")
            continue
        final = state.get("final_decision") or state.get("initial_decision")
        init = state.get("initial_decision")
        if init and final and init.get("best_model_id") != final.get("best_model_id"):
            revised += 1
        h2_calls += sum(1 for row in state.get("tool_call_log") or [] if row.get("tool_name") == "get_heritability_records")
        full_results.append({
            "custom_id": custom_id,
            "ontology": state["ontology"],
            "initial_decision": init,
            "final_decision": final,
            "tool_call_log": state.get("tool_call_log") or [],
            "error": state.get("error"),
        })
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [final],
            "error": None,
        }

    _write_json(output_run_dir / "experiment_react_refinement_batch_full_results.json", full_results)
    without_domain.RESULTS_JSON = output_run_dir / "experiment_react_refinement_batch_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_react_refinement_batch_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_react_refinement_batch_report.md"
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
    summary["execution_mode"] = "react_refinement_batch_surface"
    summary["react_refinement_batch"] = {
        "refinement_mode": refinement_mode,
        "stage1_decisions": len(stage1_decisions),
        "stage1_errors": len(stage1_errors),
        "stage2_revised_count": revised,
        "h2_call_count": h2_calls,
        "max_iterations": max_iterations,
    }
    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    print(f"Results: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Contribution2 batch-surface ReAct refinement")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--refinement-mode", choices=["default", "balanced_challenge", "optional_h2_challenge"], default="balanced_challenge")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--poll-interval-seconds", type=int, default=20)
    args = parser.parse_args()

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir = base_runs / f"react-refinement-batch-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=run_dir,
        model=args.model,
        temperature=args.temperature,
        seed=args.seed,
        refinement_mode=args.refinement_mode,
        max_iterations=args.max_iterations,
        poll_interval_seconds=args.poll_interval_seconds,
    )
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = (summary.get("trial_hit_at_k") or {}).get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, accuracy={v.get('accuracy')}")
    print(f"\nmeta: {json.dumps(summary.get('react_refinement_batch') or {}, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
