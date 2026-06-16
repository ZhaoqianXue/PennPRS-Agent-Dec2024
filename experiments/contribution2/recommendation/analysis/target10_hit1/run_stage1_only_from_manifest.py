"""Run production Stage1 only from a prepared clean manifest.

Analysis-only helper for measuring the carried-forward candidate universe. It
does not cap or reorder candidates after the model response; carried candidates
are exactly the valid IDs emitted by the production Stage1 decision.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr


FORBIDDEN_PROMPT_PATTERNS = (
    r"selection_proxy",
    r"first-pass proxy",
    r"mandatory first-pass",
    r"Select the rank-1",
    r"rank-1 proxy",
    r"proxy winner",
    r"external-validation performance",
    r"external validation shortlist",
    r"benchmark-selection",
    r"benchmark selection",
)

FORBIDDEN_CONTEXT_KEYS = {
    "benchmark_ranked_ids",
    "benchmark_auc_by_id",
    "benchmark_topk_ids",
    "benchmark_top_percent_ids",
}

REQUIRED_STAGE1_FRAGMENTS = (
    "2 and 10",
    "bounded evidence-profile shortlist",
    "not a numeric score",
    "not a proxy rank",
    "not a runner-side truncation",
    "Do not pad",
    "Do not exceed 10",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_raw_context_json(request: dict[str, Any]) -> str:
    message = request["request"]["body"]["messages"][1]["content"]
    marker = "Context:\n"
    idx = message.find(marker)
    if idx < 0:
        raise RuntimeError(f"{request['custom_id']}: Context marker not found")
    return message[idx + len(marker):]


def _context_json_for_stage1(request: dict[str, Any]) -> str:
    return pr._context_json_with_skill_context(_extract_raw_context_json(request))


def _candidate_ids_from_request(request: dict[str, Any], context_json: str) -> set[str]:
    ids = {str(pgs_id) for pgs_id in request.get("candidate_model_ids") or []}
    if ids:
        return ids
    context = json.loads(context_json)
    models = context.get("direct_models", {}).get("models") or []
    return {str(model.get("id")) for model in models if model.get("id")}


def _rank_map(request: dict[str, Any]) -> dict[str, int]:
    return {
        str(pgs_id): idx + 1
        for idx, pgs_id in enumerate(request.get("benchmark_ranked_ids") or [])
    }


def _best_carried_rank(carried_ids: list[str], ranks: dict[str, int]) -> int | None:
    present = [ranks[pgs_id] for pgs_id in carried_ids if pgs_id in ranks]
    return min(present) if present else None


def _find_forbidden_context_keys(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in FORBIDDEN_CONTEXT_KEYS:
                hits.append(path)
            hits.extend(_find_forbidden_context_keys(child, path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            hits.extend(_find_forbidden_context_keys(child, f"{prefix}[{idx}]"))
    return hits


def _inspect_stage1_requests(manifest: dict[str, Any]) -> dict[str, Any]:
    if pr._manifest_uses_general_biomedical_llm(manifest):
        raise ValueError("Stage1-only within-agent inspection requires a with-skill manifest")

    forbidden_prompt_hits: list[dict[str, str]] = []
    missing_required_fragments: list[dict[str, str]] = []
    forbidden_context_hits: list[dict[str, Any]] = []
    order_match_violations: list[dict[str, Any]] = []
    top1_first_violations: list[dict[str, Any]] = []

    for request in manifest["requests"]:
        ontology = request["ontology"]
        context_json = _context_json_for_stage1(request)
        messages = pr._stage1_messages_for_arm(
            context_json,
            top_k=None,
            objective="support",
            general_biomedical_llm=False,
        )
        joined = "\n\n".join(message["content"] for message in messages)
        for pattern in FORBIDDEN_PROMPT_PATTERNS:
            if re.search(pattern, joined, re.I):
                forbidden_prompt_hits.append({"ontology": ontology, "pattern": pattern})
        for fragment in REQUIRED_STAGE1_FRAGMENTS:
            if fragment not in joined:
                missing_required_fragments.append({"ontology": ontology, "fragment": fragment})

        context = json.loads(context_json)
        context_hits = _find_forbidden_context_keys(context)
        if context_hits:
            forbidden_context_hits.append({"ontology": ontology, "paths": context_hits})

        if request.get("candidate_order_matches_benchmark_order"):
            order_match_violations.append({
                "ontology": ontology,
                "candidate_order_matches_benchmark_order": True,
            })
        if request.get("benchmark_top1_position_in_candidate_order") == 1:
            top1_first_violations.append({
                "ontology": ontology,
                "benchmark_top1_position_in_candidate_order": 1,
            })

    return {
        "request_count": len(manifest["requests"]),
        "general_biomedical_llm": False,
        "production_top_k": None,
        "stage1_bound_is_prompt_led": True,
        "required_stage1_fragments": list(REQUIRED_STAGE1_FRAGMENTS),
        "forbidden_prompt_hits": forbidden_prompt_hits,
        "missing_required_fragments": missing_required_fragments,
        "forbidden_context_key_hits": forbidden_context_hits,
        "candidate_order_match_violations": order_match_violations,
        "benchmark_top1_first_violations": top1_first_violations,
        "clean_candidate_order": not order_match_violations and not top1_first_violations,
        "passed": not (
            forbidden_prompt_hits
            or missing_required_fragments
            or forbidden_context_hits
            or order_match_violations
            or top1_first_violations
        ),
    }


def _summarize_rows(
    *,
    manifest: dict[str, Any],
    stage1_rows: list[dict[str, Any]],
    model: str,
    elapsed_seconds: float,
) -> dict[str, Any]:
    request_by_id = {request["custom_id"]: request for request in manifest["requests"]}
    rows: list[dict[str, Any]] = []
    top1_carried = 0
    top5_carried = 0
    bounded_violations: list[dict[str, Any]] = []
    carried_sizes: list[int] = []

    for stage1_row in stage1_rows:
        request = request_by_id[stage1_row["custom_id"]]
        ranks = _rank_map(request)
        context_json = stage1_row.get("context_json") or _context_json_for_stage1(request)
        candidate_ids = _candidate_ids_from_request(request, context_json)
        decision = stage1_row.get("decision") or {}
        carried = pr._select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=candidate_ids,
            top_k=None,
        )
        carried_ranks = [ranks.get(pgs_id) for pgs_id in carried]
        best_rank = _best_carried_rank(carried, ranks)
        row_top1 = best_rank == 1
        row_top5 = best_rank is not None and best_rank <= 5
        carried_size = len(carried)
        carried_sizes.append(carried_size)
        top1_carried += int(row_top1)
        top5_carried += int(row_top5)
        if candidate_ids and not (2 <= carried_size <= 10):
            bounded_violations.append({
                "ontology": request["ontology"],
                "carried_size": carried_size,
                "carried_set": carried,
            })
        rows.append({
            "ontology": request["ontology"],
            "custom_id": stage1_row["custom_id"],
            "stage1_best": decision.get("best_model_id"),
            "stage1_best_rank": ranks.get(decision.get("best_model_id")),
            "carried_set": carried,
            "carried_size": carried_size,
            "carried_ranks": carried_ranks,
            "best_carried_rank": best_rank,
            "top1_carried": row_top1,
            "top5_carried": row_top5,
            "outcome": decision.get("outcome"),
            "confidence": decision.get("confidence"),
            "error": stage1_row.get("error"),
            "rationale": decision.get("rationale"),
        })

    n = len(rows)
    aggregate = {
        "top1_carried": f"{top1_carried}/{n}",
        "top5_carried": f"{top5_carried}/{n}",
        "bounded_2_10_violations": len(bounded_violations),
        "carried_size_min": min(carried_sizes) if carried_sizes else None,
        "carried_size_median": statistics.median(carried_sizes) if carried_sizes else None,
        "carried_size_mean": round(statistics.mean(carried_sizes), 2) if carried_sizes else None,
        "carried_size_max": max(carried_sizes) if carried_sizes else None,
    }
    aggregate["gate_minimum_passed"] = (
        top1_carried >= 4
        and top5_carried >= 7
        and not bounded_violations
    )
    aggregate["gate_v3_retention_passed"] = (
        top1_carried >= 5
        and top5_carried >= 8
        and not bounded_violations
    )

    return {
        "run_type": "stage1_only_from_clean_manifest",
        "manifest": manifest.get("run_tag") or manifest.get("experiment"),
        "model": model,
        "production_top_k": None,
        "stage1_bound_is_prompt_led": True,
        "stage2_calls": 0,
        "elapsed_seconds": round(elapsed_seconds, 1),
        "aggregate": aggregate,
        "bounded_violations": bounded_violations,
        "cost": pr._summarize_usage_cost(model),
        "rows": rows,
    }


def _run_stage1_only(
    *,
    manifest: dict[str, Any],
    output_dir: Path,
    model: str,
    workers: int,
) -> dict[str, Any]:
    inspection = _inspect_stage1_requests(manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "stage1_request_inspection.json").write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not inspection["passed"]:
        raise SystemExit(f"Stage1 request inspection failed; see {output_dir / 'stage1_request_inspection.json'}")

    client = pr._client()
    pr._reset_usage_records()
    started = time.time()
    stage1_rows_by_id: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                pr._run_stage1_for_request,
                client,
                model,
                request,
                None,
                "support",
                False,
            ): request
            for request in manifest["requests"]
        }
        done = 0
        for future in as_completed(futures):
            row = future.result()
            stage1_rows_by_id[row["custom_id"]] = row
            done += 1
            status = "ok" if row.get("error") is None else "ERR"
            print(f"  [stage1 {done}/{len(futures)}] {status} {row['ontology']}")

    request_order = [request["custom_id"] for request in manifest["requests"]]
    stage1_rows = [stage1_rows_by_id[custom_id] for custom_id in request_order]
    summary = _summarize_rows(
        manifest=manifest,
        stage1_rows=stage1_rows,
        model=model,
        elapsed_seconds=time.time() - started,
    )
    summary["inspection"] = inspection

    (output_dir / "experiment_pairwise_rerank_stage1_results.json").write_text(
        json.dumps(stage1_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage1_only_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage1_only_usage_records.json").write_text(
        json.dumps(list(pr._USAGE_RECORDS), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--inspect-only", action="store_true")
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    if args.inspect_only:
        inspection = _inspect_stage1_requests(manifest)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "stage1_request_inspection.json").write_text(
            json.dumps(inspection, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(inspection, indent=2, ensure_ascii=False))
        if not inspection["passed"]:
            raise SystemExit(1)
        return

    summary = _run_stage1_only(
        manifest=manifest,
        output_dir=args.output_dir,
        model=args.model,
        workers=args.workers,
    )
    print(json.dumps(summary["aggregate"], indent=2, ensure_ascii=False))
    if summary.get("cost"):
        print(json.dumps(summary["cost"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
