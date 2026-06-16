"""Run C3 Type-A-only evaluation on the recomputed legacy no-AoU disease list.

This is a focused runner for the post-leak-fix Type A subset:

  experiments/contribution3/cross_list/benchmark_legacy80_no_aou_recomputed
  -> Type A rows only (59 targets)

It creates a TypeA59 benchmark view, patches the transfer/evaluation code to
read that view, runs the strict GPT-only direct baseline and/or the retained
PRS Agent condition, and evaluates both with the same end-to-end metrics used
by the main C3 evaluation code.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer import common as c3_common  # noqa: E402
from experiments.contribution3.transfer.direct_baseline import (  # noqa: E402
    DIRECT_BASELINE_CONDITION,
    build_direct_result_record,
    invoke_direct_selection,
    write_direct_artifacts,
)
from experiments.contribution3.transfer.driver import (  # noqa: E402
    run_cross_trait_agent,
    write_agent_results,
)
from experiments.contribution3.transfer.eval.evaluate_end_to_end import (  # noqa: E402
    evaluate_end_to_end_condition,
)


SOURCE_BENCHMARK_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy80_no_aou_recomputed"
)
TYPEA59_BENCHMARK_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy80_no_aou_recomputed_typeA59"
)
DEFAULT_RUN_ID_PREFIX = "typeA59_legacy80_no_aou_recomputed"
DEFAULT_AGENT_CONDITION = "all-tools"
DEFAULT_ABLATION = c3_common.DEFAULT_TRANSFER_ABLATION


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def ensure_typea59_benchmark_view() -> list[str]:
    source = SOURCE_BENCHMARK_DIR / "unified" / "target_selection.csv"
    if not source.exists():
        raise FileNotFoundError(f"Missing recomputed benchmark target list: {source}")

    df = pd.read_csv(source)
    type_a = df[df["input_type"].astype(str).str.strip() == "A"].copy()
    if len(type_a) != 59:
        raise ValueError(f"Expected 59 Type A targets, found {len(type_a)} in {source}")

    unified_dir = TYPEA59_BENCHMARK_DIR / "unified"
    unified_dir.mkdir(parents=True, exist_ok=True)
    type_a.to_csv(unified_dir / "target_selection.csv", index=False)

    config = {
        "name": TYPEA59_BENCHMARK_DIR.name,
        "source_benchmark": str(SOURCE_BENCHMARK_DIR.relative_to(PROJECT_ROOT)),
        "source_target_selection": str(source.relative_to(PROJECT_ROOT)),
        "subset": "Type A only",
        "target_count": int(len(type_a)),
        "target_ids": type_a["input_icd"].astype(str).tolist(),
    }
    _write_json(TYPEA59_BENCHMARK_DIR / "benchmark_config.json", config)
    return config["target_ids"]


def patch_benchmark_dir() -> None:
    """Point common/evaluation helpers at the TypeA59 benchmark view."""
    c3_common.BENCHMARK_DIR = TYPEA59_BENCHMARK_DIR
    c3_common.benchmark_target_source_lookup.cache_clear()
    c3_common.source_universe_pgs_ids.cache_clear()


def build_typea59_dossiers(target_filter: set[str] | None = None):
    bundles = (
        c3_common.load_trait_bundle_index(c3_common.BUNDLE_INDEX_JSON)
        if c3_common.BUNDLE_INDEX_JSON.exists()
        else c3_common.build_trait_bundle_index()
    )
    if not c3_common.BUNDLE_INDEX_JSON.exists():
        c3_common.write_trait_bundle_index(bundles, c3_common.BUNDLE_INDEX_JSON)

    dossiers = c3_common.build_candidate_dossiers(bundles, benchmark_family="unified")
    if len(dossiers) != 59:
        raise ValueError(f"Expected 59 TypeA59 dossiers, built {len(dossiers)}")
    if target_filter:
        dossiers = [
            dossier
            for dossier in dossiers
            if dossier.target.target_id in target_filter
        ]
        missing = sorted(target_filter - {dossier.target.target_id for dossier in dossiers})
        if missing:
            raise ValueError(f"Requested target IDs not found in TypeA59 dossiers: {missing}")

    dossier_suffix = (
        "_".join(sorted(target_filter))
        if target_filter
        else "candidate_dossiers"
    )
    dossier_path = (
        c3_common.RUNS_DIR
        / "unified"
        / f"{DEFAULT_RUN_ID_PREFIX}_{dossier_suffix}.json"
    )
    c3_common.write_candidate_dossiers(dossiers, dossier_path)
    return dossiers, dossier_path


def run_baseline(
    dossiers,
    *,
    run_id: str,
    workers: int,
    ablation: str,
    force: bool,
) -> dict[str, Any]:
    results_path = c3_common.condition_results_json(
        DIRECT_BASELINE_CONDITION,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    if results_path.exists() and not force:
        print(f"[baseline] existing results found, skipping run: {results_path}", flush=True)
    else:
        if results_path.exists():
            results_path.unlink()
            rec_path = c3_common.condition_recommendations_json(
                DIRECT_BASELINE_CONDITION,
                benchmark_family="unified",
                run_id=run_id,
                ablation=ablation,
            )
            if rec_path.exists():
                rec_path.unlink()
        results = _run_direct_baseline_incremental(
            dossiers,
            run_id=run_id,
            workers=workers,
            ablation=ablation,
        )
        write_direct_artifacts(
            results,
            condition=DIRECT_BASELINE_CONDITION,
            benchmark_family="unified",
            run_id=run_id,
            ablation=ablation,
        )

    return evaluate_end_to_end_condition(
        condition=DIRECT_BASELINE_CONDITION,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )


def _run_direct_baseline_incremental(dossiers, *, run_id: str, workers: int, ablation: str) -> list[dict[str, Any]]:
    results_path = c3_common.condition_results_json(
        DIRECT_BASELINE_CONDITION,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )

    def write_partial(rows: list[dict[str, Any]]) -> None:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    if workers <= 1:
        results = []
        for dossier in dossiers:
            selection = invoke_direct_selection(dossier)
            result = build_direct_result_record(dossier, selection, condition=DIRECT_BASELINE_CONDITION)
            results.append(result)
            print(
                f"[{DIRECT_BASELINE_CONDITION}] ({len(results)}/{len(dossiers)}) "
                f"{result['target']['target_id']}: {result['decision'].get('best_cross_trait')} "
                f"-> {result['decision'].get('best_model_id')}",
                flush=True,
            )
            write_partial(results)
        return results

    results_lock = threading.Lock()
    results: list[dict[str, Any] | None] = [None] * len(dossiers)
    done_count = 0

    def process(idx: int, dossier):
        selection = invoke_direct_selection(dossier)
        return idx, build_direct_result_record(dossier, selection, condition=DIRECT_BASELINE_CONDITION)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process, idx, dossier): idx for idx, dossier in enumerate(dossiers)}
        for future in as_completed(futures):
            idx, result = future.result()
            with results_lock:
                results[idx] = result
                done_count += 1
                current = done_count
                write_partial([row for row in results if row is not None])
            print(
                f"[{DIRECT_BASELINE_CONDITION}] ({current}/{len(dossiers)}) "
                f"{result['target']['target_id']}: {result['decision'].get('best_cross_trait')} "
                f"-> {result['decision'].get('best_model_id')}",
                flush=True,
            )

    return [row for row in results if row is not None]


def run_agent(
    dossiers,
    *,
    run_id: str,
    workers: int,
    ablation: str,
    force: bool,
) -> dict[str, Any]:
    condition = DEFAULT_AGENT_CONDITION
    results_path = c3_common.condition_results_json(
        condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    if results_path.exists() and not force:
        print(f"[agent] existing results found, skipping run: {results_path}", flush=True)
    else:
        if results_path.exists():
            results_path.unlink()
            rec_path = c3_common.condition_recommendations_json(
                condition,
                benchmark_family="unified",
                run_id=run_id,
                ablation=ablation,
            )
            if rec_path.exists():
                rec_path.unlink()
        results = _run_agent_incremental(
            dossiers,
            run_id=run_id,
            workers=workers,
            ablation=ablation,
        )
        write_agent_results(results, results_path)
        _write_agent_recommendations(results, run_id=run_id, ablation=ablation)

    return evaluate_end_to_end_condition(
        condition=condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )


def _run_agent_incremental(dossiers, *, run_id: str, workers: int, ablation: str) -> list[dict[str, Any]]:
    condition = DEFAULT_AGENT_CONDITION
    results_path = c3_common.condition_results_json(
        condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )

    def write_partial(rows: list[dict[str, Any]]) -> None:
        write_agent_results(rows, results_path)

    if workers <= 1:
        results = []
        for dossier in dossiers:
            result = run_cross_trait_agent(
                dossier,
                condition=condition,
                benchmark_family="unified",
                ablation=ablation,
            )
            results.append(result)
            print(
                f"[{condition}][{ablation}] ({len(results)}/{len(dossiers)}) "
                f"{result['target']['target_id']}: {result['decision'].get('outcome')} "
                f"{result['decision'].get('best_cross_trait') or '-'} "
                f"-> {result['decision'].get('best_model_id') or '-'}",
                flush=True,
            )
            write_partial(results)
        return results

    results_lock = threading.Lock()
    results: list[dict[str, Any] | None] = [None] * len(dossiers)
    done_count = 0

    def process(idx: int, dossier):
        return idx, run_cross_trait_agent(
            dossier,
            condition=condition,
            benchmark_family="unified",
            ablation=ablation,
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process, idx, dossier): idx for idx, dossier in enumerate(dossiers)}
        for future in as_completed(futures):
            idx, result = future.result()
            with results_lock:
                results[idx] = result
                done_count += 1
                current = done_count
                write_partial([row for row in results if row is not None])
            print(
                f"[{condition}][{ablation}] ({current}/{len(dossiers)}) "
                f"{result['target']['target_id']}: {result['decision'].get('outcome')} "
                f"{result['decision'].get('best_cross_trait') or '-'} "
                f"-> {result['decision'].get('best_model_id') or '-'}",
                flush=True,
            )

    return [row for row in results if row is not None]


def _write_agent_recommendations(results: list[dict[str, Any]], *, run_id: str, ablation: str) -> Path:
    recommendations = []
    for row in results:
        decision = row.get("decision") or {}
        target = row.get("target") or {}
        record = {
            "target": target,
            "condition": DEFAULT_AGENT_CONDITION,
            "transfer_decision": decision,
            "recommendation": None,
        }
        if decision.get("outcome") == "MATCHED":
            stage2 = decision.get("stage2") or {}
            model_frontier = (
                decision.get("model_frontier")
                or stage2.get("model_frontier")
                or stage2.get("recommended_models")
                or []
            )
            best_model_id = decision.get("best_model_id") or stage2.get("primary_model_id")
            recommended_ids = decision.get("recommended_model_ids") or [
                model.get("pgs_id") for model in model_frontier if model.get("pgs_id")
            ]
            record["recommendation"] = {
                "original_target_trait": str(target.get("target_label") or "").strip(),
                "matched_cross_trait": decision.get("best_cross_trait"),
                "matched_bundle_id": decision.get("primary_bundle_id") or decision.get("best_bundle_id"),
                "frontier_bundle_ids": decision.get("frontier_bundle_ids") or [],
                "frontier_bundle_weights": decision.get("frontier_bundle_weights") or {},
                "candidate_pgs_ids": decision.get("candidate_pgs_ids") or [],
                "retrieval": {
                    "hydrated_model_count": stage2.get("model_universe_size"),
                    "frontier_model_count": len(model_frontier),
                    "bundles_hydrated": stage2.get("bundles_hydrated")
                    or list((decision.get("search_trace") or {}).get("model_budget_by_bundle", {}).keys()),
                    "universe_matches_candidate_ids": (
                        True if best_model_id and best_model_id in (decision.get("candidate_pgs_ids") or []) else None
                    ),
                    "missing_candidate_pgs_ids": [],
                },
                "decision": {
                    "outcome": "DIRECT_HIGH_QUALITY" if best_model_id else "NO_MATCH_FOUND",
                    "best_model_id": best_model_id,
                    "confidence": stage2.get("confidence", decision.get("confidence", "Low")),
                    "rationale": stage2.get("decision_rationale", ""),
                },
                "recommended_model_ids": recommended_ids,
            }
        recommendations.append(record)

    outpath = c3_common.condition_recommendations_json(
        DEFAULT_AGENT_CONDITION,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    _write_json(outpath, recommendations)
    return outpath


def write_comparison(run_id: str, ablation: str) -> Path:
    eval_dir = c3_common.evaluation_dir("unified", run_id=run_id, ablation=ablation)
    baseline_detail = pd.read_csv(eval_dir / f"{DIRECT_BASELINE_CONDITION}__end_to_end_eval_detail.csv")
    agent_detail = pd.read_csv(eval_dir / f"{DEFAULT_AGENT_CONDITION}__end_to_end_eval_detail.csv")

    merged = baseline_detail.merge(
        agent_detail,
        on=["target_id", "target_description", "input_type", "target_source"],
        suffixes=("_baseline", "_prs_agent"),
    )
    merged["delta_selected_auc"] = merged["selected_model_auc_prs_agent"] - merged["selected_model_auc_baseline"]
    merged["delta_gpr"] = merged["selected_model_gpr_prs_agent"] - merged["selected_model_gpr_baseline"]
    merged["delta_auc_regret"] = (
        merged["absolute_auc_regret_baseline"] - merged["absolute_auc_regret_prs_agent"]
    )
    outpath = eval_dir / "typeA59_baseline_vs_prs_agent_detail.csv"
    merged.to_csv(outpath, index=False)

    baseline_summary = json.loads((eval_dir / f"{DIRECT_BASELINE_CONDITION}__end_to_end_eval_summary.json").read_text())
    agent_summary = json.loads((eval_dir / f"{DEFAULT_AGENT_CONDITION}__end_to_end_eval_summary.json").read_text())
    summary = {
        "run_id": run_id,
        "benchmark": str(TYPEA59_BENCHMARK_DIR.relative_to(PROJECT_ROOT)),
        "n_targets": int(len(merged)),
        "baseline_condition": DIRECT_BASELINE_CONDITION,
        "prs_agent_condition": DEFAULT_AGENT_CONDITION,
        "baseline": _extract_summary_metrics(baseline_summary),
        "prs_agent": _extract_summary_metrics(agent_summary),
        "delta_prs_agent_minus_baseline": _delta_summary(
            _extract_summary_metrics(agent_summary),
            _extract_summary_metrics(baseline_summary),
        ),
        "paired_auc": {
            "mean_delta_selected_auc": round(float(merged["delta_selected_auc"].mean()), 6),
            "median_delta_selected_auc": round(float(merged["delta_selected_auc"].median()), 6),
            "n_improved_auc": int((merged["delta_selected_auc"] > 0).sum()),
            "n_tied_auc": int((merged["delta_selected_auc"] == 0).sum()),
            "n_worse_auc": int((merged["delta_selected_auc"] < 0).sum()),
        },
    }
    summary_path = eval_dir / "typeA59_baseline_vs_prs_agent_summary.json"
    _write_json(summary_path, summary)
    print(f"Wrote comparison detail -> {outpath}", flush=True)
    print(f"Wrote comparison summary -> {summary_path}", flush=True)
    return summary_path


def _extract_summary_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    official = summary.get("official_metrics") or {}
    return {
        "coverage": summary.get("coverage"),
        "mean_selected_auc": summary.get("mean_selected_auc"),
        "mean_gpr": official.get("mean_gpr"),
        "mean_absolute_auc_regret": official.get("mean_absolute_auc_regret"),
        "hit_at_percent": official.get("hit_at_percent") or {},
        "legacy_hit_at_percent": (summary.get("diagnostics") or {}).get("legacy_hit_at_percent") or {},
    }


def _delta_summary(agent: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    def sub(a, b):
        return round(float(a) - float(b), 6) if a is not None and b is not None else None

    return {
        "coverage": sub(agent.get("coverage"), baseline.get("coverage")),
        "mean_selected_auc": sub(agent.get("mean_selected_auc"), baseline.get("mean_selected_auc")),
        "mean_gpr": sub(agent.get("mean_gpr"), baseline.get("mean_gpr")),
        "mean_absolute_auc_regret": sub(
            agent.get("mean_absolute_auc_regret"),
            baseline.get("mean_absolute_auc_regret"),
        ),
        "hit_at_percent": {
            key: sub(agent["hit_at_percent"].get(key), baseline["hit_at_percent"].get(key))
            for key in sorted(set(agent["hit_at_percent"]) | set(baseline["hit_at_percent"]))
        },
        "legacy_hit_at_percent": {
            key: sub(agent["legacy_hit_at_percent"].get(key), baseline["legacy_hit_at_percent"].get(key))
            for key in sorted(set(agent["legacy_hit_at_percent"]) | set(baseline["legacy_hit_at_percent"]))
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--condition", choices=["baseline", "agent", "both"], default="both")
    parser.add_argument("--ablation", default=DEFAULT_ABLATION)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--target-ids",
        default="",
        help="Optional comma-separated target IDs to run from the TypeA59 benchmark.",
    )
    args = parser.parse_args()

    run_id = args.run_id.strip() or f"{DEFAULT_RUN_ID_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    target_ids = ensure_typea59_benchmark_view()
    patch_benchmark_dir()
    target_filter = {
        target_id.strip()
        for target_id in args.target_ids.split(",")
        if target_id.strip()
    }
    dossiers, dossier_path = build_typea59_dossiers(target_filter or None)

    manifest = {
        "run_id": run_id,
        "condition": args.condition,
        "ablation": args.ablation,
        "workers": args.workers,
        "target_count": len(target_ids),
        "target_ids": [dossier.target.target_id for dossier in dossiers],
        "source_target_count": len(target_ids),
        "target_filter": sorted(target_filter),
        "benchmark_dir": str(TYPEA59_BENCHMARK_DIR.relative_to(PROJECT_ROOT)),
        "candidate_dossiers": str(dossier_path.relative_to(PROJECT_ROOT)),
    }
    manifest_path = (
        c3_common.evaluation_dir("unified", run_id=run_id, ablation=args.ablation)
        / "typeA59_run_manifest.json"
    )
    _write_json(manifest_path, manifest)
    print(f"Prepared TypeA59 benchmark view with {len(target_ids)} targets.", flush=True)
    print(f"Candidate dossiers -> {dossier_path}", flush=True)
    print(f"Run manifest -> {manifest_path}", flush=True)

    if args.condition in {"baseline", "both"}:
        run_baseline(dossiers, run_id=run_id, workers=args.workers, ablation=args.ablation, force=args.force)
    if args.condition in {"agent", "both"}:
        run_agent(dossiers, run_id=run_id, workers=args.workers, ablation=args.ablation, force=args.force)
    if args.condition == "both":
        write_comparison(run_id, args.ablation)


if __name__ == "__main__":
    main()
