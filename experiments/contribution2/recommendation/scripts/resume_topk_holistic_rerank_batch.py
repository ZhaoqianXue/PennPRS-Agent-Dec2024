"""Resume a top-k holistic rerank Batch run from its run directory.

This is intentionally a recovery wrapper around
run_experiment_topk_holistic_rerank_batch.py. It does not change prompts,
selection logic, or scoring; it only resumes polling/collection for a run whose
OpenAI Batch job was already submitted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.scripts import run_experiment_topk_holistic_rerank_batch as batch


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _job_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"experiment_topk_holistic_rerank_batch_{stage}_job.json"


def _output_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"experiment_topk_holistic_rerank_batch_{stage}_output.jsonl"


def _error_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"experiment_topk_holistic_rerank_batch_{stage}_errors.jsonl"


def _parse_error_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return batch.without_domain._parse_error_file(path.read_text(encoding="utf-8"))


def _load_or_collect_stage1(
    *,
    client: Any,
    manifest: dict[str, Any],
    run_dir: Path,
    poll_interval_seconds: int,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    stage1_job_path = _job_path(run_dir, "stage1")
    if not stage1_job_path.exists():
        raise RuntimeError(f"Missing Stage 1 job file: {stage1_job_path}")
    stage1_job = _read_json(stage1_job_path)
    if stage1_job.get("status") != "completed":
        stage1_job = batch._poll_batch(
            client,
            batch_id=stage1_job["batch_id"],
            job_path=stage1_job_path,
            label="stage1",
            poll_interval_seconds=poll_interval_seconds,
        )

    results_path = run_dir / "experiment_topk_holistic_rerank_batch_stage1_results.json"
    if results_path.exists():
        rows = _read_json(results_path)
        return stage1_job, {row["custom_id"]: row for row in rows}

    output_path = _output_path(run_dir, "stage1")
    error_path = _error_path(run_dir, "stage1")
    if output_path.exists():
        stage1_records = batch._read_jsonl(output_path)
        stage1_error_map = _parse_error_map(error_path)
    else:
        stage1_records, stage1_error_map = batch._download_batch_outputs(
            client,
            job=stage1_job,
            output_path=output_path,
            error_path=error_path,
        )

    stage1_results: dict[str, dict[str, Any]] = {}
    for record in stage1_records:
        parsed = batch._parse_stage1_record(record)
        custom_id = parsed["custom_id"]
        request = next((r for r in manifest["requests"] if r["custom_id"] == custom_id), None)
        stage1_results[custom_id] = {
            "custom_id": custom_id,
            "ontology": request["ontology"] if request else None,
            "decision": parsed.get("decision"),
            "context_json": batch._context_json_from_request(request) if request else None,
            "error": parsed.get("error") or stage1_error_map.get(custom_id),
        }
    batch._write_json(results_path, list(stage1_results.values()))
    return stage1_job, stage1_results


def _load_or_collect_stage2(
    *,
    client: Any,
    manifest: dict[str, Any],
    run_dir: Path,
    stage1_results: dict[str, dict[str, Any]],
    model: str,
    top_k: int,
    objective: str,
    run_tag: str,
    poll_interval_seconds: int,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]], dict[str, dict[str, Any]]]:
    stage2_requests, ranked_candidates_by_ontology, stage1_decision_by_ontology = batch._build_stage2_requests(
        manifest=manifest,
        stage1_results=stage1_results,
        model=model,
        top_k=top_k,
        objective=objective,
    )
    stage2_requests_path = run_dir / "experiment_topk_holistic_rerank_batch_stage2_requests.jsonl"
    if not stage2_requests_path.exists():
        batch._write_jsonl(stage2_requests_path, stage2_requests)

    stage2_job_path = _job_path(run_dir, "stage2")
    if stage2_job_path.exists():
        stage2_job = _read_json(stage2_job_path)
    else:
        stage2_job = batch._submit_batch(
            client,
            requests_path=stage2_requests_path,
            metadata={"experiment": "topk_holistic_rerank_batch_stage2", "run_tag": run_tag},
        )
        batch._write_json(stage2_job_path, stage2_job)

    if stage2_job.get("status") != "completed":
        stage2_job = batch._poll_batch(
            client,
            batch_id=stage2_job["batch_id"],
            job_path=stage2_job_path,
            label="stage2",
            poll_interval_seconds=poll_interval_seconds,
        )

    output_path = _output_path(run_dir, "stage2")
    error_path = _error_path(run_dir, "stage2")
    if output_path.exists():
        stage2_records = batch._read_jsonl(output_path)
        stage2_error_map = _parse_error_map(error_path)
    else:
        stage2_records, stage2_error_map = batch._download_batch_outputs(
            client,
            job=stage2_job,
            output_path=output_path,
            error_path=error_path,
        )

    ranked_by_stage2_custom_id = {
        f"stage2__{request['custom_id']}": ranked_candidates_by_ontology.get(request["ontology"], [])
        for request in manifest["requests"]
    }
    stage2_results_by_custom_id: dict[str, dict[str, Any]] = {}
    for record in stage2_records:
        custom_id = record.get("custom_id")
        parsed = batch._parse_stage2_record(
            record,
            ranked_candidate_ids=ranked_by_stage2_custom_id.get(custom_id, []),
        )
        parsed["error"] = parsed.get("error") or stage2_error_map.get(custom_id)
        stage2_results_by_custom_id[custom_id] = parsed
    return stage2_job, stage2_results_by_custom_id, ranked_candidates_by_ontology, stage1_decision_by_ontology


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume a top-k holistic rerank Batch run")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--top-k", type=batch.pr._parse_top_k, default=None,
                        help="Candidate-set cap for Stage 2. Default 'all' (no cap): evidence-determined "
                             "carried-forward set. An integer opts a legacy ablation back into a fixed count.")
    parser.add_argument("--objective", default="performance_proxy")
    parser.add_argument("--stage1-objective", default="support")
    parser.add_argument("--poll-interval-seconds", type=int, default=30)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    manifest = _read_json(run_dir / "experiment_topk_holistic_rerank_batch_manifest.json")
    client = batch._client()

    stage1_job, stage1_results = _load_or_collect_stage1(
        client=client,
        manifest=manifest,
        run_dir=run_dir,
        poll_interval_seconds=args.poll_interval_seconds,
    )
    stage2_job, stage2_results_by_custom_id, ranked_candidates_by_ontology, stage1_decision_by_ontology = (
        _load_or_collect_stage2(
            client=client,
            manifest=manifest,
            run_dir=run_dir,
            stage1_results=stage1_results,
            model=args.model,
            top_k=args.top_k,
            objective=args.objective,
            run_tag=args.run_tag,
            poll_interval_seconds=args.poll_interval_seconds,
        )
    )
    summary = batch._build_final_outputs(
        manifest=manifest,
        output_run_dir=run_dir,
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
    summary.setdefault("pairwise_rerank", {})["audit_trace"] = {
        "enabled": False,
        "stages": [],
        "non_interventional": True,
    }
    batch._write_json(run_dir / "experiment_topk_holistic_rerank_batch_summary.json", summary)
    print(f"Summary: {run_dir / 'experiment_topk_holistic_rerank_batch_summary.json'}")
    print(f"Cost: {summary.get('cost')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
