"""Replay production Stage2 from a frozen Stage1-only carrier artifact.

Analysis-only helper for target10 tuning. It does not rerun Stage1 and does not
change the carried-forward candidate universe. The Stage2 winner is evaluated
against the benchmark ranks already recorded for the frozen carried set.
"""

from __future__ import annotations

import argparse
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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_map(stage1_row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    context = json.loads(stage1_row["context_json"])
    models = context.get("direct_models", {}).get("models") or []
    return context, {str(model.get("id")): model for model in models if model.get("id")}


def _rank_map(summary_row: dict[str, Any]) -> dict[str, int]:
    carried = list(summary_row.get("carried_set") or [])
    ranks = list(summary_row.get("carried_ranks") or [])
    return {
        str(pgs_id): int(rank)
        for pgs_id, rank in zip(carried, ranks)
        if pgs_id and rank is not None
    }


def _inspect_messages(
    *,
    stage1_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    stage1_by_custom_id = {row["custom_id"]: row for row in stage1_rows}
    forbidden_hits: list[dict[str, str]] = []
    digest_violations: list[dict[str, Any]] = []
    raw_candidate_missing: list[str] = []
    universe_mismatches: list[dict[str, Any]] = []
    digest_truncation_count = 0

    for summary_row in summary_rows:
        ontology = summary_row["ontology"]
        ranked_ids = list(summary_row.get("carried_set") or [])
        stage1_row = stage1_by_custom_id[summary_row["custom_id"]]
        context, candidate_summaries = _candidate_map(stage1_row)
        decision = stage1_row.get("decision") or {}
        carried = pr._select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=set(candidate_summaries),
            top_k=None,
        )
        if carried != ranked_ids:
            universe_mismatches.append({
                "ontology": ontology,
                "from_stage1_decision": carried,
                "from_stage1_summary": ranked_ids,
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
        joined = "\n\n".join(message["content"] for message in messages)
        for pattern in FORBIDDEN_PROMPT_PATTERNS:
            if re.search(pattern, joined, re.I):
                forbidden_hits.append({"ontology": ontology, "pattern": pattern})

        user_message = messages[-1]["content"]
        payload = json.loads(user_message.split("Context:\n", 1)[1])
        if "candidates" not in payload:
            raw_candidate_missing.append(ontology)
        for item in payload.get("selection_record_digest") or []:
            bad_keys = FORBIDDEN_DIGEST_KEYS.intersection(item)
            if bad_keys:
                digest_violations.append({
                    "ontology": ontology,
                    "pgs_id": item.get("pgs_id"),
                    "keys": sorted(bad_keys),
                })
            if item.get("performance_digest_truncated"):
                digest_truncation_count += 1

    return {
        "request_count": len(summary_rows),
        "forbidden_prompt_hits": forbidden_hits,
        "digest_violations": digest_violations,
        "raw_candidate_missing": raw_candidate_missing,
        "stage2_universe_mismatches": universe_mismatches,
        "stage2_universe_equals_stage1_carried_forward": not universe_mismatches,
        "digest_truncated_candidate_count": digest_truncation_count,
        "passed": not (
            forbidden_hits or digest_violations or raw_candidate_missing or universe_mismatches
        ),
    }


def _run_replay(
    *,
    stage1_dir: Path,
    output_dir: Path,
    model: str,
    workers: int,
) -> dict[str, Any]:
    stage1_rows = _load_json(stage1_dir / "experiment_pairwise_rerank_stage1_results.json")
    summary = _load_json(stage1_dir / "stage1_only_summary.json")
    summary_rows = list(summary.get("rows") or [])
    stage1_by_custom_id = {row["custom_id"]: row for row in stage1_rows}

    output_dir.mkdir(parents=True, exist_ok=True)
    inspection = _inspect_messages(stage1_rows=stage1_rows, summary_rows=summary_rows)
    (output_dir / "stage2_request_inspection.json").write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not inspection["passed"]:
        raise SystemExit(f"Request inspection failed; see {output_dir / 'stage2_request_inspection.json'}")

    client = pr._client()
    pr._reset_usage_records()
    started = time.time()
    replay_rows: list[dict[str, Any]] = []

    def submit(summary_row: dict[str, Any]) -> dict[str, Any]:
        stage1_row = stage1_by_custom_id[summary_row["custom_id"]]
        context, candidate_summaries = _candidate_map(stage1_row)
        return pr._run_stage2_for_topk(
            client,
            model,
            ontology=summary_row["ontology"],
            ranked_candidate_ids=list(summary_row.get("carried_set") or []),
            candidate_summaries=candidate_summaries,
            target_ancestry=context.get("target_ancestry"),
            skill_context=context.get("skill_context") or {},
            objective="support",
            general_biomedical_llm=False,
        )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(submit, row): row["ontology"] for row in summary_rows}
        for future in as_completed(futures):
            replay_rows.append(future.result())

    ontology_order = [row["ontology"] for row in summary_rows]
    replay_rows.sort(key=lambda row: ontology_order.index(row["ontology"]))
    replay_by_ontology = {row["ontology"]: row for row in replay_rows}

    report_rows: list[dict[str, Any]] = []
    hit1 = hit5 = oracle_hit = 0
    for summary_row in summary_rows:
        ontology = summary_row["ontology"]
        replay_row = replay_by_ontology[ontology]
        ranks = _rank_map(summary_row)
        winner = replay_row.get("winner_model_id")
        winner_rank = ranks.get(winner)
        best_rank = summary_row.get("best_carried_rank")
        row_hit1 = winner_rank == 1
        row_hit5 = winner_rank is not None and winner_rank <= 5
        row_oracle = winner_rank == best_rank
        hit1 += int(row_hit1)
        hit5 += int(row_hit5)
        oracle_hit += int(row_oracle)
        report_rows.append({
            "ontology": ontology,
            "carried_size": summary_row.get("carried_size"),
            "top1_carried": summary_row.get("top1_carried"),
            "top5_carried": summary_row.get("top5_carried"),
            "best_carried_rank": best_rank,
            "winner_model_id": winner,
            "winner_rank": winner_rank,
            "winner_is_best_carried": row_oracle,
            "hit1": row_hit1,
            "hit5": row_hit5,
            "error": replay_row.get("error"),
            "rationale": replay_row.get("rationale"),
            "ranked_candidate_ids": list(summary_row.get("carried_set") or []),
            "carried_ranks": list(summary_row.get("carried_ranks") or []),
        })

    usage_cost = pr._summarize_usage_cost(model)
    out = {
        "run_type": "stage2_only_replay_from_frozen_stage1_only_artifact",
        "source_stage1_dir": str(stage1_dir),
        "model": model,
        "stage1_frozen": True,
        "stage1_calls": 0,
        "stage2_calls": len(replay_rows),
        "elapsed_seconds": round(time.time() - started, 1),
        "aggregate": {
            "oracle_best_carried_selected": f"{oracle_hit}/{len(report_rows)}",
            "hit1": f"{hit1}/{len(report_rows)}",
            "hit5": f"{hit5}/{len(report_rows)}",
            "top1_carried": summary.get("aggregate", {}).get("top1_carried"),
            "top5_carried": summary.get("aggregate", {}).get("top5_carried"),
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
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_replay_usage_records.json").write_text(
        json.dumps(list(pr._USAGE_RECORDS), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--inspect-only", action="store_true")
    args = parser.parse_args()

    stage1_rows = _load_json(args.stage1_dir / "experiment_pairwise_rerank_stage1_results.json")
    summary_rows = _load_json(args.stage1_dir / "stage1_only_summary.json").get("rows") or []
    if args.inspect_only:
        inspection = _inspect_messages(stage1_rows=stage1_rows, summary_rows=summary_rows)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "stage2_request_inspection.json").write_text(
            json.dumps(inspection, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(inspection, indent=2, ensure_ascii=False))
        if not inspection["passed"]:
            raise SystemExit(1)
        return

    summary = _run_replay(
        stage1_dir=args.stage1_dir,
        output_dir=args.output_dir,
        model=args.model,
        workers=args.workers,
    )
    print(json.dumps(summary["aggregate"], indent=2, ensure_ascii=False))
    if summary.get("cost"):
        print(json.dumps(summary["cost"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
