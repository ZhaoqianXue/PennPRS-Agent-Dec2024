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
    BUNDLE_INDEX_JSON,
    RUNS_DIR,
    TARGET_DOSSIERS_JSON,
    build_candidate_dossiers,
    build_trait_bundle_index,
    load_candidate_dossiers,
    load_trait_bundle_index,
    write_candidate_dossiers,
    write_trait_bundle_index,
)


def cmd_prepare_assets(_: argparse.Namespace) -> None:
    bundles = build_trait_bundle_index()
    write_trait_bundle_index(bundles, BUNDLE_INDEX_JSON)
    dossiers = build_candidate_dossiers(bundles)
    write_candidate_dossiers(dossiers, TARGET_DOSSIERS_JSON)
    print(
        f"Prepared {len(bundles)} bundles and {len(dossiers)} target dossiers under {RUNS_DIR}",
        flush=True,
    )


def _ensure_assets():
    bundles = load_trait_bundle_index(BUNDLE_INDEX_JSON) if BUNDLE_INDEX_JSON.exists() else build_trait_bundle_index()
    if not BUNDLE_INDEX_JSON.exists():
        write_trait_bundle_index(bundles, BUNDLE_INDEX_JSON)
    dossiers = load_candidate_dossiers(TARGET_DOSSIERS_JSON) if TARGET_DOSSIERS_JSON.exists() else build_candidate_dossiers(bundles)
    if not TARGET_DOSSIERS_JSON.exists():
        write_candidate_dossiers(dossiers, TARGET_DOSSIERS_JSON)
    return bundles, dossiers


def cmd_run(args: argparse.Namespace) -> None:
    bundles, dossiers = _ensure_assets()
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
        outpath = RUNS_DIR / condition / "results.json"
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
    results_path = RUNS_DIR / condition / "results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"Agent results not found: {results_path}")
    results = json.loads(results_path.read_text())
    recommendations = []
    for row in results:
        decision = row.get("decision") or {}
        if decision.get("outcome") != "MATCHED":
            continue
        recommendations.append(
            recommend_best_model_for_cross_trait(
                cross_trait_label=decision["best_cross_trait"],
                candidate_pgs_ids=decision.get("candidate_pgs_ids") or [],
            )
        )
        print(
            f"[{condition}] recommended model for {decision['best_cross_trait']}: "
            f"{recommendations[-1]['decision'].get('best_model_id')}",
            flush=True,
        )
    outpath = RUNS_DIR / condition / "contribution2_recommendations.json"
    outpath.write_text(json.dumps(recommendations, indent=2, ensure_ascii=False))
    print(
        f"[{condition}] wrote {len(recommendations)} contribution2 recommendations -> {outpath}",
        flush=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the v4 tool-calling cross-trait transfer agent."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("prepare-assets")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument(
        "--condition",
        choices=["all", *CONDITION_TOOLS.keys()],
        default="all",
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
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
