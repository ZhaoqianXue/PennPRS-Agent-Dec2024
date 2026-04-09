from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    CONDITION_TOOLS,
    run_cross_trait_agent,
    write_agent_results,
)
from experiments.contribution3.transfer.common import (
    BENCHMARK_FAMILIES,
    BUNDLE_INDEX_JSON,
    build_candidate_dossiers,
    build_trait_bundle_index,
    condition_recommendations_json,
    condition_results_json,
    load_candidate_dossiers,
    load_trait_bundle_index,
    target_dossiers_json,
    write_candidate_dossiers,
    write_trait_bundle_index,
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


def cmd_run(args: argparse.Namespace) -> None:
    bundles, dossiers = _ensure_assets(args.benchmark_family)
    toolbox = None
    target_filter = {
        target_id.strip()
        for target_id in (args.target_ids.split(",") if args.target_ids else [])
        if target_id.strip()
    }
    if target_filter:
        dossiers = [dossier for dossier in dossiers if dossier.target.target_id in target_filter]

    conditions = list(CONDITION_TOOLS) if args.condition == "all" else [args.condition]
    for condition in conditions:
        if toolbox is None:
            from experiments.contribution3.transfer.tools import CrossTraitToolbox

            toolbox = CrossTraitToolbox(bundles)
        results = []
        outpath = condition_results_json(condition, benchmark_family=args.benchmark_family)
        for dossier in dossiers:
            result = run_cross_trait_agent(dossier, condition=condition, toolbox=toolbox)
            results.append(result)
            print(
                f"[{condition}] {result['target']['target_id']}: "
                f"{result['decision']['outcome']} "
                f"{result['decision'].get('best_cross_trait') or '-'}",
                flush=True,
            )
            write_agent_results(results, outpath)
        print(f"[{condition}] wrote {len(results)} decisions -> {outpath}", flush=True)


def cmd_recommend(args: argparse.Namespace) -> None:
    from experiments.contribution3.transfer.contribution2_adapter import (
        recommend_best_model_for_cross_trait,
    )

    condition = args.condition
    results_path = condition_results_json(condition, benchmark_family=args.benchmark_family)
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
            frontier_bundle_ids = decision.get("frontier_bundle_ids") or (
                [decision.get("primary_bundle_id")] if decision.get("primary_bundle_id") else []
            )
            record["recommendation"] = recommend_best_model_for_cross_trait(
                original_target_trait=str(record["target"].get("target_label") or "").strip(),
                matched_cross_trait=decision.get("best_cross_trait"),
                matched_bundle_id=decision.get("primary_bundle_id") or decision.get("best_bundle_id"),
                candidate_pgs_ids=decision.get("candidate_pgs_ids") or [],
                frontier_bundle_ids=frontier_bundle_ids,
                frontier_bundle_weights=decision.get("frontier_bundle_weights") or {},
                candidate_pgs_ids_union=decision.get("candidate_pgs_ids_union")
                or decision.get("candidate_pgs_ids")
                or [],
                bundle_evidence_tags=decision.get("bundle_evidence_tags") or {},
                evidence_state=decision.get("evidence_state") or {},
                use_domain_knowledge=(condition != "gpt-only"),
            )
            print(
                f"[{condition}] {record['target'].get('target_id')}: "
                f"{decision.get('best_cross_trait') or decision.get('primary_bundle_id') or '-'} -> "
                f"{record['recommendation']['decision'].get('best_model_id')}",
                flush=True,
            )
        else:
            print(
                f"[{condition}] {record['target'].get('target_id')}: "
                f"{decision.get('outcome') or 'NO_DECISION'}",
                flush=True,
            )
        recommendations.append(record)
    outpath = condition_recommendations_json(condition, benchmark_family=args.benchmark_family)
    outpath.write_text(json.dumps(recommendations, indent=2, ensure_ascii=False))
    print(
        f"[{condition}] wrote {len(recommendations)} contribution2 recommendations -> {outpath}",
        flush=True,
    )


def cmd_evaluate_end_to_end(args: argparse.Namespace) -> None:
    from experiments.contribution3.transfer.eval.evaluate_end_to_end import (
        evaluate_end_to_end_condition,
    )

    summary = evaluate_end_to_end_condition(
        condition=args.condition,
        benchmark_family=args.benchmark_family,
    )
    print(
        f"[{args.condition}] benchmark_family={args.benchmark_family} "
        f"coverage={summary.get('coverage'):.4f} "
        f"mean_gpr={summary.get('official_metrics', {}).get('mean_gpr')} "
        f"hit@5%={summary.get('official_metrics', {}).get('hit_at_percent', {}).get('top_5pct')}",
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
        default="binary_to_binary",
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
        default="binary_to_binary",
    )
    run_parser.add_argument(
        "--target-ids",
        default="",
        help="Optional comma-separated target ICD/root codes for focused debugging runs.",
    )

    recommend_parser = subparsers.add_parser("recommend")
    recommend_parser.add_argument(
        "--condition",
        choices=list(CONDITION_TOOLS.keys()),
        default="all-tools",
    )
    recommend_parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="binary_to_binary",
    )

    eval_parser = subparsers.add_parser("evaluate-end-to-end")
    eval_parser.add_argument(
        "--condition",
        choices=list(CONDITION_TOOLS.keys()),
        default="all-tools",
    )
    eval_parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="binary_to_binary",
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
    elif args.command == "generate-docs":
        cmd_generate_docs(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
