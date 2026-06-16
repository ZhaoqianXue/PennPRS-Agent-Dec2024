from __future__ import annotations

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.driver import (
    CONDITION_TOOLS,
    TRANSFER_ABLATIONS,
    run_cross_trait_agent,
    write_agent_results,
)
from experiments.contribution3.transfer.common import DEFAULT_TRANSFER_ABLATION
from experiments.contribution3.transfer.common import (
    BENCHMARK_FAMILIES,
    BUNDLE_INDEX_JSON,
    build_candidate_dossiers,
    build_trait_bundle_index,
    condition_recommendations_json,
    condition_results_json,
    evaluation_dir,
    load_candidate_dossiers,
    load_trait_bundle_index,
    normalize_transfer_ablation,
    target_dossiers_json,
    write_candidate_dossiers,
    write_trait_bundle_index,
)
from experiments.contribution3.transfer.direct_baseline import (
    DIRECT_BASELINE_CONDITION,
    run_direct_baseline,
    write_direct_artifacts,
)


def cmd_prepare_assets(_: argparse.Namespace) -> None:
    bundles = build_trait_bundle_index()
    write_trait_bundle_index(bundles, BUNDLE_INDEX_JSON)
    dossiers = build_candidate_dossiers(bundles, benchmark_family=_.benchmark_family)
    dossiers_path = target_dossiers_json(_.benchmark_family)
    write_candidate_dossiers(dossiers, dossiers_path)
    print(
        f"Prepared {len(bundles)} bundles and {len(dossiers)} target dossiers under {dossiers_path.parent}",
        flush=True,
    )


def _ensure_assets(benchmark_family: str):
    bundles = load_trait_bundle_index(BUNDLE_INDEX_JSON) if BUNDLE_INDEX_JSON.exists() else build_trait_bundle_index()
    if not BUNDLE_INDEX_JSON.exists():
        write_trait_bundle_index(bundles, BUNDLE_INDEX_JSON)
    dossiers_path = target_dossiers_json(benchmark_family)
    dossiers = (
        load_candidate_dossiers(dossiers_path)
        if dossiers_path.exists()
        else build_candidate_dossiers(bundles, benchmark_family=benchmark_family)
    )
    if not dossiers_path.exists():
        write_candidate_dossiers(dossiers, dossiers_path)
    return bundles, dossiers


def _resolve_run_id(raw_run_id: str | None) -> str:
    return raw_run_id.strip() if raw_run_id and raw_run_id.strip() else datetime.now().strftime("%Y%m%d_%H%M%S")


def _resolve_ablation(raw_ablation: str | None) -> str:
    label = normalize_transfer_ablation(raw_ablation)
    if label not in TRANSFER_ABLATIONS:
        raise ValueError(f"Unsupported ablation: {raw_ablation}. Expected one of {', '.join(TRANSFER_ABLATIONS)}.")
    return label


def _split_ablation_list(raw: str | None) -> list[str]:
    if not raw:
        return list(TRANSFER_ABLATIONS)
    values = [
        _resolve_ablation(item)
        for item in str(raw).split(",")
        if str(item).strip()
    ]
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered or list(TRANSFER_ABLATIONS)


def cmd_run(args: argparse.Namespace) -> None:
    _, dossiers = _ensure_assets(args.benchmark_family)
    run_id = _resolve_run_id(getattr(args, "run_id", None))
    ablation = _resolve_ablation(getattr(args, "ablation", DEFAULT_TRANSFER_ABLATION))
    target_filter = {
        target_id.strip()
        for target_id in (args.target_ids.split(",") if args.target_ids else [])
        if target_id.strip()
    }
    if target_filter:
        dossiers = [dossier for dossier in dossiers if dossier.target.target_id in target_filter]

    n_workers = getattr(args, "workers", 1) or 1
    conditions = list(CONDITION_TOOLS) if args.condition == "all" else [args.condition]
    for condition in conditions:
        outpath = condition_results_json(
            condition,
            benchmark_family=args.benchmark_family,
            run_id=run_id,
            ablation=ablation,
        )
        if outpath.exists():
            raise FileExistsError(
                f"Refusing to overwrite existing transfer run output: {outpath}. "
                "Choose a new --run-id or remove the existing run directory."
            )

        stop_after = getattr(args, "stop_after", None) or None
        if n_workers <= 1:
            # Sequential (original) path
            results = []
            for dossier in dossiers:
                result = run_cross_trait_agent(
                    dossier,
                    condition=condition,
                    benchmark_family=args.benchmark_family,
                    ablation=ablation,
                    stop_after=stop_after,
                )
                results.append(result)
                print(
                    f"[{condition}][{ablation}] {result['target']['target_id']}: "
                    f"{result['decision']['outcome']} "
                    f"{result['decision'].get('best_cross_trait') or '-'}",
                    flush=True,
                )
                write_agent_results(results, outpath)
        else:
            # Parallel path — each target is independent; LLM calls are I/O-bound.
            results_lock = threading.Lock()
            results: list[dict] = [None] * len(dossiers)  # type: ignore[list-item]
            done_count = 0

            def _process(idx: int, dossier):
                return idx, run_cross_trait_agent(
                    dossier,
                    condition=condition,
                    benchmark_family=args.benchmark_family,
                    ablation=ablation,
                    stop_after=stop_after,
                )

            print(
                f"[{condition}][{ablation}] Running {len(dossiers)} targets with {n_workers} workers ...",
                flush=True,
            )
            with ThreadPoolExecutor(max_workers=n_workers) as pool:
                futures = {
                    pool.submit(_process, i, d): i
                    for i, d in enumerate(dossiers)
                }
                for future in as_completed(futures):
                    idx, result = future.result()
                    with results_lock:
                        results[idx] = result
                        done_count += 1
                    print(
                        f"[{condition}][{ablation}] ({done_count}/{len(dossiers)}) "
                        f"{result['target']['target_id']}: "
                        f"{result['decision']['outcome']} "
                        f"{result['decision'].get('best_cross_trait') or '-'}",
                        flush=True,
                    )
            # Write once after all complete (preserves original target order)
            write_agent_results(results, outpath)

        print(
            f"[{condition}][{ablation}] run_id={run_id} wrote {len(results)} decisions -> {outpath}",
            flush=True,
        )


def cmd_recommend(args: argparse.Namespace) -> None:
    """Extract Stage 2 model recommendations from unified two-stage decision output.

    In the new pipeline, `run_cross_trait_agent` already produces `best_model_id`
    and `recommended_model_ids` via Stage 2 LLM. This command simply extracts
    them into the `contribution2_recommendations.json` format for eval compat.
    """
    condition = args.condition
    ablation = _resolve_ablation(getattr(args, "ablation", DEFAULT_TRANSFER_ABLATION))
    run_id = getattr(args, "run_id", None) or None
    results_path = condition_results_json(
        condition,
        benchmark_family=args.benchmark_family,
        run_id=run_id,
        ablation=ablation,
    )
    if not results_path.exists():
        raise FileNotFoundError(f"Agent results not found: {results_path}")
    results = json.loads(results_path.read_text())
    recommendations = []
    for row in results:
        decision = row.get("decision") or {}
        record = {
            "target": row.get("target") or {},
            "condition": condition,
            "transfer_decision": decision,
            "recommendation": None,
        }
        if decision.get("outcome") == "MATCHED":
            # Extract Stage 2 model recommendation from unified decision
            stage2 = decision.get("stage2") or {}
            model_frontier = decision.get("model_frontier") or stage2.get("model_frontier") or stage2.get("recommended_models", [])
            best_model_id = decision.get("best_model_id") or stage2.get("primary_model_id")
            recommended_ids = decision.get("recommended_model_ids") or [
                m["pgs_id"] for m in model_frontier if m.get("pgs_id")
            ]
            record["recommendation"] = {
                "original_target_trait": str(record["target"].get("target_label") or "").strip(),
                "matched_cross_trait": decision.get("best_cross_trait"),
                "matched_bundle_id": decision.get("primary_bundle_id") or decision.get("best_bundle_id"),
                "frontier_bundle_ids": decision.get("frontier_bundle_ids") or [],
                "frontier_bundle_weights": decision.get("frontier_bundle_weights") or {},
                "candidate_pgs_ids": decision.get("candidate_pgs_ids") or [],
                "retrieval": {
                    "hydrated_model_count": stage2.get("model_universe_size"),
                    "frontier_model_count": len(model_frontier),
                    "bundles_hydrated": stage2.get("bundles_hydrated") or list((decision.get("search_trace") or {}).get("model_budget_by_bundle", {}).keys()),
                    "universe_matches_candidate_ids": True if best_model_id and best_model_id in (decision.get("candidate_pgs_ids") or []) else None,
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
            print(
                f"[{condition}][{ablation}] {record['target'].get('target_id')}: "
                f"{decision.get('best_cross_trait') or '-'} -> {best_model_id}",
                flush=True,
            )
        else:
            print(
                f"[{condition}][{ablation}] {record['target'].get('target_id')}: "
                f"{decision.get('outcome') or 'NO_DECISION'}",
                flush=True,
            )
        recommendations.append(record)
    outpath = condition_recommendations_json(
        condition,
        benchmark_family=args.benchmark_family,
        run_id=run_id,
        ablation=ablation,
    )
    outpath.write_text(json.dumps(recommendations, indent=2, ensure_ascii=False))
    print(
        f"[{condition}][{ablation}] wrote {len(recommendations)} recommendations -> {outpath}",
        flush=True,
    )


def cmd_evaluate_end_to_end(args: argparse.Namespace) -> None:
    from experiments.contribution3.transfer.eval.evaluate_end_to_end import (
        evaluate_end_to_end_condition,
    )

    ablation = _resolve_ablation(getattr(args, "ablation", DEFAULT_TRANSFER_ABLATION))
    run_id = getattr(args, "run_id", None) or None
    summary = evaluate_end_to_end_condition(
        condition=args.condition,
        benchmark_family=args.benchmark_family,
        run_id=run_id,
        ablation=ablation,
    )
    print(
        f"[{args.condition}][{ablation}] benchmark_family={args.benchmark_family} "
        f"coverage={summary.get('coverage'):.4f} "
        f"mean_gpr={summary.get('official_metrics', {}).get('mean_gpr')} "
        f"hit@0.5%={summary.get('official_metrics', {}).get('hit_at_percent', {}).get('top_0_5pct')}",
        flush=True,
    )


def cmd_offline_unified(args: argparse.Namespace) -> None:
    run_id = _resolve_run_id(getattr(args, "run_id", None))
    ablation = _resolve_ablation(getattr(args, "ablation", DEFAULT_TRANSFER_ABLATION))

    if not getattr(args, "skip_prepare_assets", False):
        cmd_prepare_assets(argparse.Namespace(benchmark_family="unified"))

    run_args = argparse.Namespace(
        condition=args.condition,
        benchmark_family="unified",
        target_ids=getattr(args, "target_ids", ""),
        run_id=run_id,
        workers=getattr(args, "workers", 1),
        ablation=ablation,
    )
    cmd_run(run_args)

    recommend_args = argparse.Namespace(
        condition=args.condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    cmd_recommend(recommend_args)

    eval_args = argparse.Namespace(
        condition=args.condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    cmd_evaluate_end_to_end(eval_args)

    results_path = condition_results_json(
        args.condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    recommendations_path = condition_recommendations_json(
        args.condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    eval_root = evaluation_dir("unified", run_id=run_id, ablation=ablation)
    print(
        f"[offline-unified][{ablation}] completed run_id={run_id}\n"
        f"results={results_path}\n"
        f"recommendations={recommendations_path}\n"
        f"evaluation_dir={eval_root}",
        flush=True,
    )


def cmd_offline_ablation_sweep(args: argparse.Namespace) -> None:
    ablations = _split_ablation_list(getattr(args, "ablations", None))
    base_run_id = _resolve_run_id(getattr(args, "run_id", None))

    if not getattr(args, "skip_prepare_assets", False):
        cmd_prepare_assets(argparse.Namespace(benchmark_family="unified"))

    for ablation in ablations:
        offline_args = argparse.Namespace(
            condition=args.condition,
            target_ids=getattr(args, "target_ids", ""),
            workers=getattr(args, "workers", 1),
            run_id=base_run_id,
            ablation=ablation,
            skip_prepare_assets=True,
        )
        cmd_offline_unified(offline_args)


def cmd_offline_direct_baseline(args: argparse.Namespace) -> None:
    """Run the strict single-shot GPT-only no-harness unified baseline."""
    from experiments.contribution3.transfer.eval.evaluate_end_to_end import (
        evaluate_end_to_end_condition,
    )

    _, dossiers = _ensure_assets("unified")
    run_id = _resolve_run_id(getattr(args, "run_id", None))
    ablation = _resolve_ablation(getattr(args, "ablation", DEFAULT_TRANSFER_ABLATION))
    condition = getattr(args, "condition", DIRECT_BASELINE_CONDITION) or DIRECT_BASELINE_CONDITION

    target_filter = {
        target_id.strip()
        for target_id in (args.target_ids.split(",") if args.target_ids else [])
        if target_id.strip()
    }
    if target_filter:
        dossiers = [dossier for dossier in dossiers if dossier.target.target_id in target_filter]

    results_path = condition_results_json(
        condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    if results_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing direct baseline output: {results_path}. "
            "Choose a new --run-id or remove the existing run directory."
        )

    results = run_direct_baseline(
        dossiers,
        condition=condition,
        workers=getattr(args, "workers", 1),
    )
    results_path, recommendations_path = write_direct_artifacts(
        results,
        condition=condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    summary = evaluate_end_to_end_condition(
        condition=condition,
        benchmark_family="unified",
        run_id=run_id,
        ablation=ablation,
    )
    eval_root = evaluation_dir("unified", run_id=run_id, ablation=ablation)
    print(
        f"[offline-direct-baseline][{ablation}] completed run_id={run_id}\n"
        f"results={results_path}\n"
        f"recommendations={recommendations_path}\n"
        f"evaluation_dir={eval_root}\n"
        f"coverage={summary.get('coverage'):.4f} "
        f"mean_gpr={summary.get('official_metrics', {}).get('mean_gpr')} "
        f"hit@0.5%={summary.get('official_metrics', {}).get('hit_at_percent', {}).get('top_0_5pct')}",
        flush=True,
    )


def cmd_generate_docs(_: argparse.Namespace) -> None:
    from experiments.contribution3.transfer.eval.generate_markdown_reports import (
        generate_markdown_reports,
    )

    outputs = generate_markdown_reports()
    for label, path in outputs.items():
        print(f"Wrote {label} report -> {path}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the v4 tool-calling cross-trait transfer agent."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("prepare-assets")
    prepare_parser = subparsers.choices["prepare-assets"]
    prepare_parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="unified",
    )

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument(
        "--condition",
        choices=["all", *CONDITION_TOOLS.keys()],
        default="all",
    )
    run_parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="unified",
    )
    run_parser.add_argument(
        "--target-ids",
        default="",
        help="Optional comma-separated target ICD/root codes for focused debugging runs.",
    )
    run_parser.add_argument(
        "--run-id",
        default="",
        help=(
            "Optional run id for append-only transfer output. Defaults to current local timestamp "
            "YYYYMMDD_HHMMSS and writes results to "
            "runs/tool_calling_agent/<benchmark_family>/<condition>__<run-id>/results.json. "
            "candidate_dossiers.json remains directly under the benchmark-family directory."
        ),
    )
    run_parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help=(
            "Number of parallel worker threads for target processing. "
            "Each target's LLM calls are I/O-bound, so 4-8 workers give near-linear speedup. "
            "Default 1 (sequential) preserves incremental write-after-each-target behaviour."
        ),
    )
    run_parser.add_argument(
        "--ablation",
        choices=TRANSFER_ABLATIONS,
        default=DEFAULT_TRANSFER_ABLATION,
        help="Optional workflow ablation to apply during the transfer run.",
    )
    run_parser.add_argument(
        "--stop-after",
        choices=["bundle_posterior"],
        default=None,
        help=(
            "Short-circuit the agent after the named phase. "
            "'bundle_posterior' returns supporting_bundles only, skipping all "
            "model-picker phases (hydration + local champion + global frontier). "
            "Used for fast Stage-A (cross-trait) iteration."
        ),
    )
    recommend_parser = subparsers.add_parser("recommend")
    recommend_parser.add_argument(
        "--condition",
        choices=[*CONDITION_TOOLS.keys(), DIRECT_BASELINE_CONDITION],
        default="all-tools",
    )
    recommend_parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="unified",
    )
    recommend_parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id to read/write artifacts from a run-specific directory.",
    )
    recommend_parser.add_argument(
        "--ablation",
        choices=TRANSFER_ABLATIONS,
        default=DEFAULT_TRANSFER_ABLATION,
        help="Optional workflow ablation to read/write recommend artifacts under.",
    )

    eval_parser = subparsers.add_parser("evaluate-end-to-end")
    eval_parser.add_argument(
        "--condition",
        choices=[*CONDITION_TOOLS.keys(), DIRECT_BASELINE_CONDITION],
        default="all-tools",
    )
    eval_parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="unified",
    )
    eval_parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id to read/write evaluation artifacts from a run-specific directory.",
    )
    eval_parser.add_argument(
        "--ablation",
        choices=TRANSFER_ABLATIONS,
        default=DEFAULT_TRANSFER_ABLATION,
        help="Optional workflow ablation to evaluate.",
    )

    offline_unified_parser = subparsers.add_parser("offline-unified")
    offline_unified_parser.add_argument(
        "--condition",
        choices=list(CONDITION_TOOLS.keys()),
        default="all-tools",
        help="Offline unified benchmark run condition. Defaults to all-tools.",
    )
    offline_unified_parser.add_argument(
        "--target-ids",
        default="",
        help="Optional comma-separated subset of target IDs for focused offline debugging.",
    )
    offline_unified_parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id reused across run/recommend/evaluate artifacts.",
    )
    offline_unified_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel worker count for the unified 80-target offline run.",
    )
    offline_unified_parser.add_argument(
        "--ablation",
        choices=TRANSFER_ABLATIONS,
        default=DEFAULT_TRANSFER_ABLATION,
        help="Optional workflow ablation for the unified offline run.",
    )
    offline_unified_parser.add_argument(
        "--skip-prepare-assets",
        action="store_true",
        help="Skip prepare-assets if bundle index and candidate dossiers are already materialized.",
    )
    offline_ablation_parser = subparsers.add_parser("offline-ablation-sweep")
    offline_ablation_parser.add_argument(
        "--condition",
        choices=list(CONDITION_TOOLS.keys()),
        default="all-tools",
        help="Condition used for the unified ablation sweep.",
    )
    offline_ablation_parser.add_argument(
        "--target-ids",
        default="",
        help="Optional comma-separated subset of target IDs for focused ablation sweeps.",
    )
    offline_ablation_parser.add_argument(
        "--run-id",
        default="",
        help="Optional shared run id for all ablations in the sweep.",
    )
    offline_ablation_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel worker count for each ablation run.",
    )
    offline_ablation_parser.add_argument(
        "--ablations",
        default=",".join(TRANSFER_ABLATIONS),
        help="Comma-separated ablation list. Defaults to full,no_ot_verifier,no_h2,no_reflective_reprobe,no_local_champion.",
    )
    offline_ablation_parser.add_argument(
        "--skip-prepare-assets",
        action="store_true",
        help="Skip prepare-assets if bundle index and candidate dossiers are already materialized.",
    )

    offline_direct_parser = subparsers.add_parser("offline-direct-baseline")
    offline_direct_parser.add_argument(
        "--condition",
        default=DIRECT_BASELINE_CONDITION,
        help="Output condition label for the strict direct baseline.",
    )
    offline_direct_parser.add_argument(
        "--target-ids",
        default="",
        help="Optional comma-separated subset of target IDs for focused direct-baseline runs.",
    )
    offline_direct_parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id reused across run/recommend/evaluate artifacts.",
    )
    offline_direct_parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel worker count for direct GPT calls. Default 1.",
    )
    offline_direct_parser.add_argument(
        "--ablation",
        choices=TRANSFER_ABLATIONS,
        default=DEFAULT_TRANSFER_ABLATION,
        help="Artifact namespace used for comparison against tuned harness outputs.",
    )
    subparsers.add_parser("generate-docs")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "prepare-assets":
        cmd_prepare_assets(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "recommend":
        cmd_recommend(args)
    elif args.command == "evaluate-end-to-end":
        cmd_evaluate_end_to_end(args)
    elif args.command == "offline-unified":
        cmd_offline_unified(args)
    elif args.command == "offline-ablation-sweep":
        cmd_offline_ablation_sweep(args)
    elif args.command == "offline-direct-baseline":
        cmd_offline_direct_baseline(args)
    elif args.command == "generate-docs":
        cmd_generate_docs(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
