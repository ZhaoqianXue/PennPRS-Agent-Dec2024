"""Batch runner for the c2 holistic final selector (Full PRS Agent, two-step).

Despite this module's history (it was misleadingly named `pairwise_rerank_batch`),
the final selector here is a single holistic judge per disease: one LLM call that
sees the evidence-determined candidate set carried forward from the ranked decision
and picks the best. It is not pairwise comparison.
It uses the canonical compact Stage-2 selector prompt plus `pr._build_topk_user_message`,
building one final-selection request per disease (not C(k,2) pairwise requests).

TRUE pairwise (C(k,2) two-way judges + Borda) has no batch implementation; it lives
only in the synchronous `run_experiment_pairwise_rerank.py` and
`run_experiment_consistency_routed_pairwise.py`.

Flow (both calls through OpenAI Batch): consume an already-prepared with-domain /
harness manifest -> the first call emits a primary pick plus evidence-supported
alternatives -> the final selector picks from that carried-forward set. `--top-k`
defaults to `all` (no cap); an explicit integer is a legacy ablation option.
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

from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _extract_message_content(content: Any) -> str:
    return without_domain._extract_message_content(content)


def _batch_body(*, model: str, messages: list[dict[str, str]], response_format: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": model,
        "messages": messages,
        "response_format": response_format,
        "temperature": 0,
        "seed": 42,
    }


def _submit_batch(client: OpenAI, *, requests_path: Path, metadata: dict[str, str]) -> dict[str, Any]:
    with requests_path.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata=metadata,
    )
    return {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "request_file": str(requests_path),
        "status": batch.status,
        "batch": batch.model_dump(),
    }


def _poll_batch(
    client: OpenAI,
    *,
    batch_id: str,
    job_path: Path,
    label: str,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    while True:
        batch = client.batches.retrieve(batch_id)
        payload = {
            "batch_id": batch.id,
            "status": batch.status,
            "input_file_id": batch.input_file_id,
            "output_file_id": batch.output_file_id,
            "error_file_id": batch.error_file_id,
            "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
            "batch": batch.model_dump(),
        }
        _write_json(job_path, payload)
        counts = payload.get("request_counts") or {}
        print(f"[{label}] status={batch.status} counts={counts}")
        if batch.status in {"completed", "failed", "expired", "cancelled"}:
            return payload
        time.sleep(poll_interval_seconds)


def _download_batch_outputs(
    client: OpenAI,
    *,
    job: dict[str, Any],
    output_path: Path,
    error_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if job.get("status") != "completed":
        raise RuntimeError(f"Batch {job.get('batch_id')} is not completed: {job.get('status')}")
    if not job.get("output_file_id"):
        raise RuntimeError(f"Batch {job.get('batch_id')} completed without output_file_id")

    raw_output = client.files.retrieve_content(job["output_file_id"])
    output_path.write_text(raw_output, encoding="utf-8")

    errors: dict[str, str] = {}
    if job.get("error_file_id"):
        raw_error = client.files.retrieve_content(job["error_file_id"])
        error_path.write_text(raw_error, encoding="utf-8")
        errors = without_domain._parse_error_file(raw_error)
    return _read_jsonl(output_path), errors


def _parse_stage1_record(record: dict[str, Any]) -> dict[str, Any]:
    custom_id = record.get("custom_id")
    response = record.get("response") or {}
    status_code = response.get("status_code")
    if status_code != 200:
        body = response.get("body") or {}
        error_payload = body.get("error") or record.get("error") or body
        return {
            "custom_id": custom_id,
            "decision": None,
            "error": f"HTTP {status_code}: {json.dumps(error_payload, ensure_ascii=False)}",
        }
    try:
        choices = (response.get("body") or {}).get("choices") or []
        if not choices:
            raise ValueError("No choices returned")
        message = (choices[0] or {}).get("message") or {}
        content = _extract_message_content(message.get("content"))
        decision = pr.Step1RankedDecision.model_validate_json(content)
        return {"custom_id": custom_id, "decision": decision.model_dump(), "error": None}
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "decision": None,
            "error": f"Failed to parse Stage1 response: {type(exc).__name__}: {exc}",
        }


def _parse_stage2_record(record: dict[str, Any], *, ranked_candidate_ids: list[str]) -> dict[str, Any]:
    custom_id = record.get("custom_id")
    response = record.get("response") or {}
    status_code = response.get("status_code")
    if status_code != 200:
        body = response.get("body") or {}
        error_payload = body.get("error") or record.get("error") or body
        return {
            "custom_id": custom_id,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"HTTP {status_code}: {json.dumps(error_payload, ensure_ascii=False)}",
        }
    try:
        choices = (response.get("body") or {}).get("choices") or []
        if not choices:
            raise ValueError("No choices returned")
        message = (choices[0] or {}).get("message") or {}
        content = _extract_message_content(message.get("content"))
        verdict = pr.TopKJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in set(ranked_candidate_ids):
            return {
                "custom_id": custom_id,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in shortlist",
            }
        return {
            "custom_id": custom_id,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"Failed to parse Stage2 response: {type(exc).__name__}: {exc}",
        }


def _parse_stage1_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    custom_id = record.get("custom_id")
    response = record.get("response") or {}
    status_code = response.get("status_code")
    if status_code != 200:
        body = response.get("body") or {}
        error_payload = body.get("error") or record.get("error") or body
        return {
            "custom_id": custom_id,
            "candidate_audits": [],
            "error": f"HTTP {status_code}: {json.dumps(error_payload, ensure_ascii=False)}",
        }
    try:
        choices = (response.get("body") or {}).get("choices") or []
        if not choices:
            raise ValueError("No choices returned")
        message = (choices[0] or {}).get("message") or {}
        content = _extract_message_content(message.get("content"))
        verdict = pr.Stage1ShortlistAuditJudgment.model_validate_json(content)
        payload = verdict.model_dump()
        payload["custom_id"] = custom_id
        payload["error"] = None
        return payload
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "candidate_audits": [],
            "error": f"Failed to parse Stage1 audit response: {type(exc).__name__}: {exc}",
        }


def _parse_stage2_audit_record(
    record: dict[str, Any],
    *,
    ranked_candidate_ids: list[str],
    frozen_winner_model_id: Optional[str],
) -> dict[str, Any]:
    custom_id = record.get("custom_id")
    response = record.get("response") or {}
    status_code = response.get("status_code")
    if status_code != 200:
        body = response.get("body") or {}
        error_payload = body.get("error") or record.get("error") or body
        return {
            "custom_id": custom_id,
            "ranked_candidate_ids": ranked_candidate_ids,
            "frozen_winner_model_id": frozen_winner_model_id,
            "candidate_audits": [],
            "error": f"HTTP {status_code}: {json.dumps(error_payload, ensure_ascii=False)}",
        }
    try:
        choices = (response.get("body") or {}).get("choices") or []
        if not choices:
            raise ValueError("No choices returned")
        message = (choices[0] or {}).get("message") or {}
        content = _extract_message_content(message.get("content"))
        verdict = pr.AuditedTopKJudgment.model_validate_json(content)
        payload = verdict.model_dump()
        payload["custom_id"] = custom_id
        payload["ranked_candidate_ids"] = ranked_candidate_ids
        payload["frozen_winner_model_id"] = frozen_winner_model_id
        payload["error"] = None
        if verdict.winner_model_id != frozen_winner_model_id:
            payload["error"] = (
                f"audit winner '{verdict.winner_model_id}' did not equal "
                f"frozen winner '{frozen_winner_model_id}'"
            )
        return payload
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ranked_candidate_ids": ranked_candidate_ids,
            "frozen_winner_model_id": frozen_winner_model_id,
            "candidate_audits": [],
            "error": f"Failed to parse Stage2 audit response: {type(exc).__name__}: {exc}",
        }


def _context_json_from_request(request: dict[str, Any]) -> str:
    original_user = request["request"]["body"]["messages"][1]["content"]
    raw_context_json = pr._json_payload_from_user_message(original_user)
    if raw_context_json is None:
        raise RuntimeError(f"{request['custom_id']}: could not locate input JSON marker")
    return raw_context_json


def _build_stage1_requests(
    *,
    manifest: dict[str, Any],
    model: str,
    top_k: Optional[int],
    stage1_objective: str,
) -> list[dict[str, Any]]:
    pr._ensure_not_general_biomedical_rerank_manifest(manifest)
    rows: list[dict[str, Any]] = []
    general_biomedical_llm = pr._manifest_uses_general_biomedical_llm(manifest)
    for request in manifest["requests"]:
        raw_context_json = _context_json_from_request(request)
        context_json = (
            pr._general_biomedical_context_json(raw_context_json)
            if general_biomedical_llm else pr._context_json_with_skill_context(raw_context_json)
        )
        rows.append({
            "custom_id": request["custom_id"],
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": _batch_body(
                model=model,
                messages=pr._stage1_messages_for_arm(
                    context_json,
                    top_k=top_k,
                    objective=stage1_objective,
                    general_biomedical_llm=general_biomedical_llm,
                ),
                response_format=pr._stage1_response_format(),
            ),
        })
    return rows


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    return pr._candidate_summary_lookup(disease_metadata)


def _skill_context_by_ontology(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    general_biomedical_llm = pr._manifest_uses_general_biomedical_llm(manifest)
    for request in manifest["requests"]:
        ontology = request["ontology"]
        if ontology in out:
            continue
        if general_biomedical_llm:
            out[ontology] = {}
            continue
        try:
            ctx = json.loads(_context_json_from_request(request))
            out[ontology] = pr._skill_context_from_context(ctx)
        except Exception:
            out[ontology] = {}
    return out


def _build_stage2_requests(
    *,
    manifest: dict[str, Any],
    stage1_results: dict[str, dict[str, Any]],
    model: str,
    top_k: Optional[int],
    objective: str,
) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, dict[str, Any]]]:
    pr._ensure_not_general_biomedical_rerank_manifest(manifest)
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    skill_context_by_ontology = _skill_context_by_ontology(manifest)
    general_biomedical_llm = pr._manifest_uses_general_biomedical_llm(manifest)
    ranked_candidates_by_ontology: dict[str, list[str]] = {}
    stage1_decision_by_ontology: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        decision = (stage1_results.get(custom_id) or {}).get("decision") or {}
        stage1_decision_by_ontology[ontology] = decision
        ranked_candidates = pr._select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=set(request["candidate_model_ids"]),
            top_k=top_k,
        )
        ranked_candidates_by_ontology[ontology] = ranked_candidates
        if len(ranked_candidates) < 2:
            continue
        messages = pr._topk_messages_for_arm(
            target_trait=ontology,
            target_ancestry=_target_ancestry_from_request(request),
            ranked_candidate_ids=ranked_candidates,
            candidate_summaries=candidate_summary_by_ontology.get(ontology, {}),
            skill_context=skill_context_by_ontology.get(ontology, {}),
            objective=objective,
            general_biomedical_llm=general_biomedical_llm,
        )
        rows.append({
            "custom_id": f"stage2__{custom_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": _batch_body(
                model=model,
                messages=messages,
                response_format=pr._topk_response_format(),
            ),
        })
    return rows, ranked_candidates_by_ontology, stage1_decision_by_ontology


def _target_ancestry_from_request(request: dict[str, Any]) -> Optional[str]:
    try:
        value = json.loads(_context_json_from_request(request)).get("target_ancestry")
    except Exception:
        return None
    return str(value).strip() if value else None


def _build_stage1_audit_requests(
    *,
    manifest: dict[str, Any],
    stage1_results: dict[str, dict[str, Any]],
    model: str,
) -> list[dict[str, Any]]:
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    skill_context_by_ontology = _skill_context_by_ontology(manifest)
    rows: list[dict[str, Any]] = []
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        decision = (stage1_results.get(custom_id) or {}).get("decision") or {}
        user_message = pr._build_stage1_audit_user_message(
            target_trait=ontology,
            target_ancestry=_target_ancestry_from_request(request),
            candidate_summaries=candidate_summary_by_ontology.get(ontology, {}),
            stage1_decision=decision,
            skill_context=skill_context_by_ontology.get(ontology, {}),
        )
        rows.append({
            "custom_id": f"stage1_audit__{custom_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": _batch_body(
                model=model,
                messages=[
                    {"role": "system", "content": pr.STAGE1_AUDIT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                response_format=pr._stage1_audit_response_format(),
            ),
        })
    return rows


def _final_pick_by_ontology(
    *,
    manifest: dict[str, Any],
    stage2_results_by_custom_id: dict[str, dict[str, Any]],
    ranked_candidates_by_ontology: dict[str, list[str]],
    stage1_decision_by_ontology: dict[str, dict[str, Any]],
) -> dict[str, Optional[str]]:
    final_pick_by_ontology: dict[str, Optional[str]] = {}
    for request in manifest["requests"]:
        ontology = request["ontology"]
        custom_id = request["custom_id"]
        ranked_candidates = ranked_candidates_by_ontology.get(ontology) or []
        if len(ranked_candidates) < 2:
            final_pick_by_ontology[ontology] = stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            continue
        stage2_custom_id = f"stage2__{custom_id}"
        result = stage2_results_by_custom_id.get(stage2_custom_id) or {}
        if result.get("winner_model_id"):
            final_pick_by_ontology[ontology] = result["winner_model_id"]
        else:
            final_pick_by_ontology[ontology] = ranked_candidates[0] if ranked_candidates else None
    return final_pick_by_ontology


def _build_stage2_audit_requests(
    *,
    manifest: dict[str, Any],
    stage2_results_by_custom_id: dict[str, dict[str, Any]],
    ranked_candidates_by_ontology: dict[str, list[str]],
    final_pick_by_ontology: dict[str, Optional[str]],
    model: str,
    objective: str,
) -> list[dict[str, Any]]:
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    skill_context_by_ontology = _skill_context_by_ontology(manifest)
    rows: list[dict[str, Any]] = []
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        ranked_candidates = ranked_candidates_by_ontology.get(ontology) or []
        frozen_winner = final_pick_by_ontology.get(ontology)
        if not frozen_winner or len(ranked_candidates) < 2:
            continue
        stage2_custom_id = f"stage2__{custom_id}"
        stage2_decision = stage2_results_by_custom_id.get(stage2_custom_id) or {
            "winner_model_id": frozen_winner,
            "source": "stage1_fallback",
        }
        user_message = pr._build_stage2_audit_user_message(
            target_trait=ontology,
            target_ancestry=_target_ancestry_from_request(request),
            ranked_candidate_ids=ranked_candidates,
            candidate_summaries=candidate_summary_by_ontology.get(ontology, {}),
            skill_context=skill_context_by_ontology.get(ontology, {}),
            frozen_winner_model_id=frozen_winner,
            stage2_decision=stage2_decision,
        )
        objective_block = pr._objective_block(objective)
        system_prompt = (
            f"{pr.TOPK_AUDIT_SYSTEM_PROMPT}\n\n{objective_block}"
            if objective_block else pr.TOPK_AUDIT_SYSTEM_PROMPT
        )
        rows.append({
            "custom_id": f"stage2_audit__{custom_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": _batch_body(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                response_format=pr._topk_audit_response_format(),
            ),
        })
    return rows


def _configure_summary_paths(output_run_dir: Path, manifest: dict[str, Any]) -> None:
    without_domain.RESULTS_JSON = output_run_dir / "experiment_topk_holistic_rerank_batch_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_topk_holistic_rerank_batch_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_topk_holistic_rerank_batch_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_topk_holistic_rerank_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_errors.jsonl"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
    without_domain._configure_benchmark_sources(
        union_csv=manifest.get("union_csv"),
        ground_truth_dir=manifest.get("ground_truth_dir"),
    )


def _build_final_outputs(
    *,
    manifest: dict[str, Any],
    output_run_dir: Path,
    stage1_results: dict[str, dict[str, Any]],
    stage2_results_by_custom_id: dict[str, dict[str, Any]],
    ranked_candidates_by_ontology: dict[str, list[str]],
    stage1_decision_by_ontology: dict[str, dict[str, Any]],
    stage1_job: dict[str, Any],
    stage2_job: dict[str, Any],
    top_k: Optional[int],
    objective: str,
    stage1_objective: str,
    model: str,
) -> dict[str, Any]:
    final_pick_by_ontology: dict[str, Optional[str]] = {}
    stage2_by_ontology: dict[str, dict[str, Any]] = {}
    for request in manifest["requests"]:
        ontology = request["ontology"]
        custom_id = request["custom_id"]
        ranked_candidates = ranked_candidates_by_ontology.get(ontology) or []
        if len(ranked_candidates) < 2:
            final_pick_by_ontology[ontology] = stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            continue
        stage2_custom_id = f"stage2__{custom_id}"
        result = stage2_results_by_custom_id.get(stage2_custom_id) or {}
        stage2_by_ontology[ontology] = {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidates,
            "winner_model_id": result.get("winner_model_id"),
            "confidence": result.get("confidence"),
            "rationale": result.get("rationale"),
            "error": result.get("error"),
        }
        if result.get("winner_model_id"):
            final_pick_by_ontology[ontology] = result["winner_model_id"]
        else:
            final_pick_by_ontology[ontology] = ranked_candidates[0] if ranked_candidates else None

    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        s1 = stage1_results.get(custom_id) or {}
        if s1.get("error"):
            error_map[custom_id] = s1["error"]
            continue
        decision = s1.get("decision") or {}
        final_pick = final_pick_by_ontology.get(ontology)
        confidence = decision.get("confidence") or "Moderate"
        rationale = decision.get("rationale") or ""
        if final_pick != decision.get("best_model_id"):
            confidence = "Moderate"
            rationale = (rationale + " | Batch top-k final selection promoted runner-up to primary.").strip()
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": decision.get("outcome") or "DIRECT_HIGH_QUALITY",
                "best_model_id": final_pick,
                "confidence": confidence,
                "rationale": rationale,
            }],
            "error": None,
        }

    _configure_summary_paths(output_run_dir, manifest)
    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    candidate_range = pr._candidate_range_metadata(evaluator="topk_judge", top_k=top_k)
    summary["execution_mode"] = "pairwise_rerank_openai_batch"
    summary["model"] = model
    summary["pairwise_rerank"] = {
        "evaluator": "topk_judge",
        "prompt_profile": (
            "general_biomedical_llm"
            if pr._manifest_uses_general_biomedical_llm(manifest)
            else "prs_agent_specialist"
        ),
        "objective": objective,
        "stage1_objective": stage1_objective,
        "stage1_count": len(stage1_results),
        "stage2_count": len(stage2_results_by_custom_id),
        **candidate_range,
        "borda_revised_count": sum(
            1
            for ontology in ranked_candidates_by_ontology
            if (
                len(ranked_candidates_by_ontology.get(ontology) or []) >= 2
                and final_pick_by_ontology.get(ontology) is not None
                and final_pick_by_ontology.get(ontology)
                != stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            )
        ),
        "ontologies_with_invalid_ranked_alternatives": sum(
            1 for ranked_candidates in ranked_candidates_by_ontology.values()
            if len(ranked_candidates) < 2
        ),
        "ranked_candidates_by_ontology": ranked_candidates_by_ontology,
        "top3_by_ontology": {
            ontology: ranked_candidates[:3]
            for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
        },
        "stage1_batch": stage1_job,
        "stage2_batch": stage2_job,
    }
    cost_parts = []
    for job in [stage1_job, stage2_job]:
        estimate = without_domain._estimate_batch_cost((job.get("batch") or {}))
        if estimate:
            cost_parts.append(estimate)
    if cost_parts:
        total_cost = sum((c.get("estimated_total_cost_usd") or 0.0) for c in cost_parts)
        summary["cost"] = {
            "method": "sum_of_stage1_stage2_batch_usage",
            "estimated_total_cost_usd": round(total_cost, 4),
            "stage_costs": cost_parts,
        }

    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_results.json", trial_results)
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_summary.json", summary)
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_results.json", list(stage2_by_ontology.values()))
    return summary


def _run_audit_batches(
    *,
    client: OpenAI,
    manifest: dict[str, Any],
    output_run_dir: Path,
    stage1_results: dict[str, dict[str, Any]],
    stage2_results_by_custom_id: dict[str, dict[str, Any]],
    ranked_candidates_by_ontology: dict[str, list[str]],
    stage1_decision_by_ontology: dict[str, dict[str, Any]],
    model: str,
    objective: str,
    run_tag: str,
    poll_interval_seconds: int,
    enabled_stages: set[str],
) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "non_interventional": True,
        "enabled_stages": sorted(enabled_stages),
        "stage1": [],
        "stage2": [],
        "jobs": {},
    }
    if not enabled_stages:
        return trace

    if "stage1" in enabled_stages:
        stage1_audit_requests = _build_stage1_audit_requests(
            manifest=manifest,
            stage1_results=stage1_results,
            model=model,
        )
        requests_path = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_audit_requests.jsonl"
        _write_jsonl(requests_path, stage1_audit_requests)
        job = _submit_batch(
            client,
            requests_path=requests_path,
            metadata={"experiment": "topk_holistic_rerank_batch_stage1_audit", "run_tag": run_tag},
        )
        job_path = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_audit_job.json"
        _write_json(job_path, job)
        job = _poll_batch(
            client,
            batch_id=job["batch_id"],
            job_path=job_path,
            label="stage1-audit",
            poll_interval_seconds=poll_interval_seconds,
        )
        records, error_map = _download_batch_outputs(
            client,
            job=job,
            output_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_audit_output.jsonl",
            error_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_audit_errors.jsonl",
        )
        parsed = []
        for record in records:
            item = _parse_stage1_audit_record(record)
            item["error"] = item.get("error") or error_map.get(record.get("custom_id"))
            parsed.append(item)
        trace["stage1"] = parsed
        trace["jobs"]["stage1"] = job
        _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_audit_results.json", parsed)

    if "stage2" in enabled_stages:
        final_pick_by_ontology = _final_pick_by_ontology(
            manifest=manifest,
            stage2_results_by_custom_id=stage2_results_by_custom_id,
            ranked_candidates_by_ontology=ranked_candidates_by_ontology,
            stage1_decision_by_ontology=stage1_decision_by_ontology,
        )
        stage2_audit_requests = _build_stage2_audit_requests(
            manifest=manifest,
            stage2_results_by_custom_id=stage2_results_by_custom_id,
            ranked_candidates_by_ontology=ranked_candidates_by_ontology,
            final_pick_by_ontology=final_pick_by_ontology,
            model=model,
            objective=objective,
        )
        requests_path = output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_audit_requests.jsonl"
        _write_jsonl(requests_path, stage2_audit_requests)
        if stage2_audit_requests:
            job = _submit_batch(
                client,
                requests_path=requests_path,
                metadata={"experiment": "topk_holistic_rerank_batch_stage2_audit", "run_tag": run_tag},
            )
            job_path = output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_audit_job.json"
            _write_json(job_path, job)
            job = _poll_batch(
                client,
                batch_id=job["batch_id"],
                job_path=job_path,
                label="stage2-audit",
                poll_interval_seconds=poll_interval_seconds,
            )
            records, error_map = _download_batch_outputs(
                client,
                job=job,
                output_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_audit_output.jsonl",
                error_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_audit_errors.jsonl",
            )
            ranked_by_stage2_audit_custom_id = {
                f"stage2_audit__{request['custom_id']}": ranked_candidates_by_ontology.get(request["ontology"], [])
                for request in manifest["requests"]
            }
            frozen_by_stage2_audit_custom_id = {
                f"stage2_audit__{request['custom_id']}": final_pick_by_ontology.get(request["ontology"])
                for request in manifest["requests"]
            }
            parsed = []
            for record in records:
                custom_id = record.get("custom_id")
                item = _parse_stage2_audit_record(
                    record,
                    ranked_candidate_ids=ranked_by_stage2_audit_custom_id.get(custom_id, []),
                    frozen_winner_model_id=frozen_by_stage2_audit_custom_id.get(custom_id),
                )
                item["error"] = item.get("error") or error_map.get(custom_id)
                parsed.append(item)
            trace["stage2"] = parsed
            trace["jobs"]["stage2"] = job
            _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_audit_results.json", parsed)

    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_audit_trace.json", trace)
    return trace


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pr._ensure_not_general_biomedical_rerank_manifest(manifest)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_model = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", args.model).strip("-")
    dataset_label = without_domain._dataset_label_from_union_path(Path(manifest["union_csv"]))
    safe_tag = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", args.run_tag).strip("-")
    output_run_dir = (
        Path(__file__).parent.parent / "runs"
        / f"topk-holistic-rerank-batch-{safe_model}-t1__{dataset_label}__{safe_tag}-{timestamp}"
    )
    output_run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_manifest.json", manifest)
    print(f"Run directory: {output_run_dir}")
    print(f"Input manifest: {manifest_path} ({len(manifest['requests'])} requests)")

    stage1_requests = _build_stage1_requests(
        manifest=manifest,
        model=args.model,
        top_k=args.top_k,
        stage1_objective=args.stage1_objective,
    )
    stage1_requests_path = output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_requests.jsonl"
    _write_jsonl(stage1_requests_path, stage1_requests)
    print(f"Prepared Stage 1 batch requests: {len(stage1_requests)}")
    if args.mode == "prepare":
        return {"run_dir": str(output_run_dir), "prepared_stage1_requests": len(stage1_requests)}

    client = _client()
    stage1_job = _submit_batch(
        client,
        requests_path=stage1_requests_path,
        metadata={"experiment": "topk_holistic_rerank_batch_stage1", "run_tag": args.run_tag},
    )
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_job.json", stage1_job)
    print(f"Submitted Stage 1 batch: {stage1_job['batch_id']}")
    stage1_job = _poll_batch(
        client,
        batch_id=stage1_job["batch_id"],
        job_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_job.json",
        label="stage1",
        poll_interval_seconds=args.poll_interval_seconds,
    )
    stage1_records, stage1_error_map = _download_batch_outputs(
        client,
        job=stage1_job,
        output_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_output.jsonl",
        error_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_errors.jsonl",
    )
    stage1_results: dict[str, dict[str, Any]] = {}
    for record in stage1_records:
        parsed = _parse_stage1_record(record)
        custom_id = parsed["custom_id"]
        request = next((r for r in manifest["requests"] if r["custom_id"] == custom_id), None)
        stage1_results[custom_id] = {
            "custom_id": custom_id,
            "ontology": request["ontology"] if request else None,
            "decision": parsed.get("decision"),
            "context_json": _context_json_from_request(request) if request else None,
            "error": parsed.get("error") or stage1_error_map.get(custom_id),
        }
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_stage1_results.json", list(stage1_results.values()))
    stage1_failures = sum(1 for r in stage1_results.values() if r.get("error"))
    print(f"Collected Stage 1: {len(stage1_results)} results, failures={stage1_failures}")

    stage2_requests, ranked_candidates_by_ontology, stage1_decision_by_ontology = _build_stage2_requests(
        manifest=manifest,
        stage1_results=stage1_results,
        model=args.model,
        top_k=args.top_k,
        objective=args.objective,
    )
    stage2_requests_path = output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_requests.jsonl"
    _write_jsonl(stage2_requests_path, stage2_requests)
    print(f"Prepared Stage 2 batch requests: {len(stage2_requests)}")

    stage2_job = _submit_batch(
        client,
        requests_path=stage2_requests_path,
        metadata={"experiment": "topk_holistic_rerank_batch_stage2", "run_tag": args.run_tag},
    )
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_job.json", stage2_job)
    print(f"Submitted Stage 2 batch: {stage2_job['batch_id']}")
    stage2_job = _poll_batch(
        client,
        batch_id=stage2_job["batch_id"],
        job_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_job.json",
        label="stage2",
        poll_interval_seconds=args.poll_interval_seconds,
    )
    stage2_records, stage2_error_map = _download_batch_outputs(
        client,
        job=stage2_job,
        output_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_output.jsonl",
        error_path=output_run_dir / "experiment_topk_holistic_rerank_batch_stage2_errors.jsonl",
    )
    ranked_by_stage2_custom_id = {
        f"stage2__{request['custom_id']}": ranked_candidates_by_ontology.get(request["ontology"], [])
        for request in manifest["requests"]
    }
    stage2_results_by_custom_id: dict[str, dict[str, Any]] = {}
    for record in stage2_records:
        custom_id = record.get("custom_id")
        parsed = _parse_stage2_record(
            record,
            ranked_candidate_ids=ranked_by_stage2_custom_id.get(custom_id, []),
        )
        parsed["error"] = parsed.get("error") or stage2_error_map.get(custom_id)
        stage2_results_by_custom_id[custom_id] = parsed
    stage2_failures = sum(1 for r in stage2_results_by_custom_id.values() if r.get("error"))
    print(f"Collected Stage 2: {len(stage2_results_by_custom_id)} results, failures={stage2_failures}")

    summary = _build_final_outputs(
        manifest=manifest,
        output_run_dir=output_run_dir,
        stage1_results=stage1_results,
        stage2_results_by_custom_id=stage2_results_by_custom_id,
        ranked_candidates_by_ontology=ranked_candidates_by_ontology,
        stage1_decision_by_ontology=stage1_decision_by_ontology,
        stage1_job=stage1_job,
        stage2_job=stage2_job,
        top_k=args.top_k,
        objective=args.objective,
        stage1_objective=args.stage1_objective,
        model=args.model,
    )
    enabled_audit_stages = pr._enabled_audit_stages(
        getattr(args, "emit_audit_trace", False),
        getattr(args, "audit_stages", "both"),
    )
    audit_trace_summary = {
        "enabled": bool(enabled_audit_stages),
        "stages": sorted(enabled_audit_stages),
        "non_interventional": True,
    }
    if enabled_audit_stages:
        audit_trace = _run_audit_batches(
            client=client,
            manifest=manifest,
            output_run_dir=output_run_dir,
            stage1_results=stage1_results,
            stage2_results_by_custom_id=stage2_results_by_custom_id,
            ranked_candidates_by_ontology=ranked_candidates_by_ontology,
            stage1_decision_by_ontology=stage1_decision_by_ontology,
            model=args.model,
            objective=args.objective,
            run_tag=args.run_tag,
            poll_interval_seconds=args.poll_interval_seconds,
            enabled_stages=enabled_audit_stages,
        )
        audit_trace_summary["path"] = str(output_run_dir / "experiment_topk_holistic_rerank_batch_audit_trace.json")
        audit_trace_summary["stage1_count"] = len(audit_trace.get("stage1") or [])
        audit_trace_summary["stage2_count"] = len(audit_trace.get("stage2") or [])
    summary.setdefault("pairwise_rerank", {})["audit_trace"] = audit_trace_summary
    _write_json(output_run_dir / "experiment_topk_holistic_rerank_batch_summary.json", summary)
    print(f"Summary: {output_run_dir / 'experiment_topk_holistic_rerank_batch_summary.json'}")
    trial_h = summary.get("trial_hit_at_k") or {}
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, accuracy={v.get('accuracy')}")
    return summary


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenAI Batch runner for pairwise-rerank top-k Full PRS Agent")
    parser.add_argument("--manifest", required=True, help="Prepared harness / with-domain manifest JSON")
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--mode", choices=["prepare", "run"], default="run")
    parser.add_argument("--top-k", type=pr._parse_top_k, default=None,
                        help="Candidate-set cap for Stage 2. Default 'all' (no cap): the carried-forward "
                             "set is exactly what the model ranked in contention, so its size is "
                             "evidence-determined. An integer opts a legacy ablation back into a fixed count.")
    parser.add_argument("--objective", choices=["support", "hidden_benchmark", "hidden_benchmark_h5_guard", "performance_proxy", "metric_first", "same_context"], default="support")
    parser.add_argument("--stage1-objective", choices=["support", "hidden_benchmark", "hidden_benchmark_h5_guard", "performance_proxy", "metric_first", "same_context"], default="support")
    parser.add_argument("--poll-interval-seconds", type=int, default=30)
    parser.add_argument("--emit-audit-trace", action="store_true",
                        help="After final picks are frozen, submit non-interventional Stage 1/2 audit batches.")
    parser.add_argument("--audit-stages", choices=["stage1", "stage2", "both"], default="both",
                        help="Audit stages to emit when --emit-audit-trace is set.")
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
