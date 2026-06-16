"""Replay Stage2 from a frozen double-stage run.

This is an analysis-only helper. It reads a completed double-stage run, freezes
the carried-forward candidate universe from its Stage2 artifact, and reruns only
the current Stage2 selector prompt on that universe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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

FORBIDDEN_DIGEST_KEYS = {"selection_proxy", "rank", "score", "tier", "winner"}
STAGE2_CANDIDATE_ORDER_CHOICES = ("source", "stable_hash_shuffle")
DEFAULT_STAGE2_CANDIDATE_ORDER = pr.STAGE2_CANDIDATE_ORDER_SOURCE
DEFAULT_STAGE2_CANDIDATE_ORDER_SEED = pr.STAGE2_CANDIDATE_ORDER_SEED


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_selected_ontologies(
    *,
    ontology_values: list[str] | None,
    ontologies_file: Path | None,
) -> set[str] | None:
    values: list[str] = []
    for value in ontology_values or []:
        values.extend(part.strip() for part in value.split(",") if part.strip())
    if ontologies_file is not None:
        raw = ontologies_file.read_text(encoding="utf-8").strip()
        if raw:
            if raw.startswith("["):
                loaded = json.loads(raw)
                if not isinstance(loaded, list):
                    raise ValueError("--ontologies-file JSON must be a list")
                values.extend(str(item).strip() for item in loaded if str(item).strip())
            else:
                values.extend(
                    line.strip()
                    for line in raw.splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                )
    selected = {value for value in values if value}
    return selected or None


def _filter_stage2_rows(
    stage2_rows: list[dict[str, Any]],
    selected_ontologies: set[str] | None,
) -> list[dict[str, Any]]:
    if not selected_ontologies:
        return stage2_rows
    available = {str(row.get("ontology")) for row in stage2_rows}
    missing = sorted(selected_ontologies - available)
    if missing:
        raise ValueError(f"Selected ontologies not present in source Stage2 rows: {missing}")
    return [
        row for row in stage2_rows
        if str(row.get("ontology")) in selected_ontologies
    ]


def _order_stage2_candidate_ids(
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_order: str,
    candidate_order_seed: str,
) -> list[str]:
    ids = [pgs_id for pgs_id in ranked_candidate_ids if pgs_id]
    if candidate_order == "source":
        return ids
    if candidate_order == "stable_hash_shuffle":
        return sorted(
            ids,
            key=lambda pgs_id: (
                hashlib.sha256(
                    f"{candidate_order_seed}\0{ontology}\0{pgs_id}".encode("utf-8")
                ).hexdigest(),
                pgs_id,
            ),
        )
    raise ValueError(f"Unsupported Stage2 candidate order: {candidate_order}")


def _candidate_map(stage1_row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    context = json.loads(stage1_row["context_json"])
    models = context.get("direct_models", {}).get("models") or []
    return context, {str(model.get("id")): model for model in models if model.get("id")}


def _rank_map(result_row: dict[str, Any]) -> dict[str, int]:
    return {pgs_id: idx + 1 for idx, pgs_id in enumerate(result_row.get("benchmark_ranked_ids") or [])}


def _user_message_payload(user_message: str) -> dict[str, Any]:
    for marker in ("Input JSON:\n", "Context:\n"):
        if marker in user_message:
            return json.loads(user_message.split(marker, 1)[1])
    raise ValueError("Stage2 user message does not contain an Input JSON or Context payload")


def _inspect_messages(
    *,
    stage1_rows: list[dict[str, Any]],
    stage2_rows: list[dict[str, Any]],
    stage2_candidate_order: str = DEFAULT_STAGE2_CANDIDATE_ORDER,
    stage2_candidate_order_seed: str = DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
) -> dict[str, Any]:
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    forbidden_hits = []
    digest_violations = []
    raw_candidate_missing = []
    universe_mismatches = []
    digest_truncation_count = 0
    request_count = 0

    for stage2_row in stage2_rows:
        ontology = stage2_row["ontology"]
        source_ranked_ids = list(stage2_row.get("ranked_candidate_ids") or [])
        ranked_ids = _order_stage2_candidate_ids(
            ontology=ontology,
            ranked_candidate_ids=source_ranked_ids,
            candidate_order=stage2_candidate_order,
            candidate_order_seed=stage2_candidate_order_seed,
        )
        stage1_row = stage1_by_ontology[ontology]
        context, candidate_summaries = _candidate_map(stage1_row)
        decision = stage1_row.get("decision") or {}
        carried = pr._select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=set(candidate_summaries),
            top_k=None,
        )
        if set(carried) != set(ranked_ids):
            universe_mismatches.append({
                "ontology": ontology,
                "from_stage1_decision": carried,
                "from_stage2_artifact": source_ranked_ids,
                "llm_visible_stage2_order": ranked_ids,
            })

        messages = pr._topk_messages_for_arm(
            target_trait=ontology,
            target_ancestry=context.get("target_ancestry"),
            ranked_candidate_ids=ranked_ids,
            candidate_summaries=candidate_summaries,
            skill_context=context.get("skill_context") or {},
            objective="support",
            general_biomedical_llm=False,
        )
        request_count += 1
        joined = "\n\n".join(message["content"] for message in messages)
        for pattern in FORBIDDEN_PROMPT_PATTERNS:
            if re.search(pattern, joined, re.I):
                forbidden_hits.append({"ontology": ontology, "pattern": pattern})

        user_message = messages[-1]["content"]
        payload = _user_message_payload(user_message)
        if "candidates" not in payload:
            raw_candidate_missing.append(ontology)
        for item in payload.get("selection_record_digest") or []:
            if FORBIDDEN_DIGEST_KEYS.intersection(item):
                digest_violations.append({
                    "ontology": ontology,
                    "pgs_id": item.get("pgs_id"),
                    "keys": sorted(FORBIDDEN_DIGEST_KEYS.intersection(item)),
                })
            if item.get("performance_digest_truncated"):
                digest_truncation_count += 1

    return {
        "request_count": request_count,
        "forbidden_prompt_hits": forbidden_hits,
        "digest_violations": digest_violations,
        "raw_candidate_missing": raw_candidate_missing,
        "stage2_universe_mismatches": universe_mismatches,
        "stage2_universe_equals_stage1_carried_forward": not universe_mismatches,
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "digest_truncated_candidate_count": digest_truncation_count,
    }


def _run_replay(
    *,
    run_dir: Path,
    output_dir: Path,
    model: str,
    workers: int,
    selected_ontologies: set[str] | None = None,
    stage2_candidate_order: str = DEFAULT_STAGE2_CANDIDATE_ORDER,
    stage2_candidate_order_seed: str = DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
) -> dict[str, Any]:
    stage1_rows = _load_json(run_dir / "experiment_pairwise_rerank_stage1_results.json")
    source_stage2_rows = _load_json(run_dir / "experiment_pairwise_rerank_stage2_results.json")
    source_stage2_rows = _filter_stage2_rows(source_stage2_rows, selected_ontologies)
    result_rows = _load_json(run_dir / "experiment_pairwise_rerank_results.json")
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    result_by_ontology = {row["ontology"]: row for row in result_rows}

    output_dir.mkdir(parents=True, exist_ok=True)
    inspection = _inspect_messages(
        stage1_rows=stage1_rows,
        stage2_rows=source_stage2_rows,
        stage2_candidate_order=stage2_candidate_order,
        stage2_candidate_order_seed=stage2_candidate_order_seed,
    )
    (output_dir / "stage2_request_inspection.json").write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if (
        inspection["forbidden_prompt_hits"]
        or inspection["digest_violations"]
        or inspection["raw_candidate_missing"]
        or inspection["stage2_universe_mismatches"]
    ):
        raise SystemExit(f"Request inspection failed; see {output_dir / 'stage2_request_inspection.json'}")

    client = pr._client()
    pr._reset_usage_records()
    started = time.time()
    replay_rows: list[dict[str, Any]] = []

    def submit(stage2_row: dict[str, Any]) -> dict[str, Any]:
        ontology = stage2_row["ontology"]
        context, candidate_summaries = _candidate_map(stage1_by_ontology[ontology])
        ranked_candidate_ids = _order_stage2_candidate_ids(
            ontology=ontology,
            ranked_candidate_ids=list(stage2_row.get("ranked_candidate_ids") or []),
            candidate_order=stage2_candidate_order,
            candidate_order_seed=stage2_candidate_order_seed,
        )
        return pr._run_stage2_for_topk(
            client,
            model,
            ontology=ontology,
            ranked_candidate_ids=ranked_candidate_ids,
            candidate_summaries=candidate_summaries,
            target_ancestry=context.get("target_ancestry"),
            skill_context=context.get("skill_context") or {},
            objective="support",
            general_biomedical_llm=False,
        )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(submit, row): row["ontology"] for row in source_stage2_rows}
        for future in as_completed(futures):
            replay_rows.append(future.result())

    ontology_order = [row["ontology"] for row in source_stage2_rows]
    replay_rows.sort(key=lambda row: ontology_order.index(row["ontology"]))
    usage_cost = pr._summarize_usage_cost(model)

    report_rows = []
    hit1 = hit5 = top1_carried = top5_carried = 0
    for row in replay_rows:
        ontology = row["ontology"]
        ranked_ids = list(row.get("ranked_candidate_ids") or [])
        ranks = _rank_map(result_by_ontology[ontology])
        winner = row.get("winner_model_id")
        winner_rank = ranks.get(winner)
        best_carried = min(
            ((pgs_id, ranks.get(pgs_id)) for pgs_id in ranked_ids),
            key=lambda item: item[1] if item[1] is not None else 10**9,
        )
        row_top1_carried = best_carried[1] == 1
        row_top5_carried = best_carried[1] is not None and best_carried[1] <= 5
        row_hit1 = winner_rank == 1
        row_hit5 = winner_rank is not None and winner_rank <= 5
        top1_carried += int(row_top1_carried)
        top5_carried += int(row_top5_carried)
        hit1 += int(row_hit1)
        hit5 += int(row_hit5)
        report_rows.append({
            "ontology": ontology,
            "carried_size": len(ranked_ids),
            "top1_carried": row_top1_carried,
            "top5_carried": row_top5_carried,
            "best_carried_id": best_carried[0],
            "best_carried_rank": best_carried[1],
            "winner_model_id": winner,
            "winner_rank": winner_rank,
            "hit1": row_hit1,
            "hit5": row_hit5,
            "error": row.get("error"),
            "rationale": row.get("rationale"),
            "ranked_candidate_ids": ranked_ids,
        })

    summary = {
        "run_type": "stage2_only_replay_from_frozen_double_stage_run",
        "source_run_dir": str(run_dir),
        "model": model,
        "selected_ontologies": sorted(selected_ontologies) if selected_ontologies else None,
        "stage1_frozen": True,
        "stage1_calls": 0,
        "stage2_calls": len(replay_rows),
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "elapsed_seconds": round(time.time() - started, 1),
        "aggregate": {
            "hit1": f"{hit1}/{len(replay_rows)}",
            "hit5": f"{hit5}/{len(replay_rows)}",
            "top1_carried": f"{top1_carried}/{len(replay_rows)}",
            "top5_carried": f"{top5_carried}/{len(replay_rows)}",
        },
        "cost": usage_cost,
        "inspection": inspection,
        "rows": report_rows,
    }
    (output_dir / "stage2_replay_results.json").write_text(
        json.dumps(replay_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_replay_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_replay_usage_records.json").write_text(
        json.dumps(list(pr._USAGE_RECORDS), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument(
        "--stage2-candidate-order",
        choices=STAGE2_CANDIDATE_ORDER_CHOICES,
        default=DEFAULT_STAGE2_CANDIDATE_ORDER,
        help="Analysis-only LLM-visible order for frozen carried Stage2 candidates.",
    )
    parser.add_argument(
        "--stage2-candidate-order-seed",
        default=DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
        help="Seed string for analysis-only stable_hash_shuffle Stage2 candidate ordering.",
    )
    parser.add_argument(
        "--ontology",
        action="append",
        default=None,
        help="Replay only this ontology. May be repeated or comma-separated.",
    )
    parser.add_argument(
        "--ontologies-file",
        type=Path,
        default=None,
        help="Optional newline-delimited or JSON-list ontology file for subset replay.",
    )
    args = parser.parse_args()

    run_dir = args.run_dir
    output_dir = args.output_dir
    selected_ontologies = _load_selected_ontologies(
        ontology_values=args.ontology,
        ontologies_file=args.ontologies_file,
    )
    source_stage2_rows = _filter_stage2_rows(
        _load_json(run_dir / "experiment_pairwise_rerank_stage2_results.json"),
        selected_ontologies,
    )
    if args.inspect_only:
        inspection = _inspect_messages(
            stage1_rows=_load_json(run_dir / "experiment_pairwise_rerank_stage1_results.json"),
            stage2_rows=source_stage2_rows,
            stage2_candidate_order=args.stage2_candidate_order,
            stage2_candidate_order_seed=args.stage2_candidate_order_seed,
        )
        inspection["selected_ontologies"] = (
            sorted(selected_ontologies) if selected_ontologies else None
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "stage2_request_inspection.json").write_text(
            json.dumps(inspection, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(inspection, indent=2, ensure_ascii=False))
        return

    summary = _run_replay(
        run_dir=run_dir,
        output_dir=output_dir,
        model=args.model,
        workers=args.workers,
        selected_ontologies=selected_ontologies,
        stage2_candidate_order=args.stage2_candidate_order,
        stage2_candidate_order_seed=args.stage2_candidate_order_seed,
    )
    print(json.dumps(summary["aggregate"], indent=2, ensure_ascii=False))
    if summary.get("cost"):
        print(json.dumps(summary["cost"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
