from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import CONDITION_TOOLS
from experiments.contribution3.transfer.common import (
    BUNDLE_INDEX_JSON,
    RUNS_DIR,
    SHORTLIST_CSV,
    TARGET_SUMMARY_CSV,
    build_trait_bundle_index,
    load_trait_bundle_index,
    resolve_bundle_ids_for_trait_text,
)


def _load_bundles():
    return load_trait_bundle_index(BUNDLE_INDEX_JSON) if BUNDLE_INDEX_JSON.exists() else build_trait_bundle_index()


def _tier_weight(tier: str) -> float:
    return {"1": 1.0, "2": 0.7}.get(str(tier), 0.0)


def _plausibility_weight(plausibility: str) -> float:
    return {"high": 1.0, "medium": 0.85, "low": 0.6}.get(str(plausibility).lower(), 0.0)


def build_silver_labels() -> tuple[dict[str, dict[str, float]], set[str]]:
    bundles = _load_bundles()
    shortlist = pd.read_csv(SHORTLIST_CSV)
    positives: dict[str, dict[str, float]] = {}
    resolution_hits = 0
    for _, row in shortlist.iterrows():
        target_id = str(row["target_id"]).strip()
        bundle_ids = resolve_bundle_ids_for_trait_text(str(row["cross_trait"]), bundles)
        if bundle_ids:
            resolution_hits += 1
        weight = _tier_weight(str(row["tier"])) * _plausibility_weight(str(row["plausibility"]))
        target_map = positives.setdefault(target_id, {})
        for bundle_id in bundle_ids:
            target_map[bundle_id] = max(target_map.get(bundle_id, 0.0), weight)

    all_targets = pd.read_csv(TARGET_SUMMARY_CSV)["target_icd"].astype(str).str.strip()
    unresolved_targets = {target for target in all_targets if target not in positives}
    print(
        f"Silver resolution rate: {resolution_hits}/{len(shortlist)} "
        f"({resolution_hits / len(shortlist):.1%})"
    )
    return positives, unresolved_targets


def _load_results(condition: str) -> list[dict[str, Any]]:
    path = RUNS_DIR / condition / "results.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def evaluate_condition(condition: str) -> pd.DataFrame:
    positives, abstain_gold = build_silver_labels()
    rows = []
    results = _load_results(condition)
    for row in results:
        target_id = row["target"]["target_id"]
        decision = row.get("decision") or {}
        predicted_bundle = decision.get("best_bundle_id")
        predicted_match = decision.get("outcome") == "MATCHED" and bool(predicted_bundle)
        positive_weights = positives.get(target_id, {})
        weighted_hit = positive_weights.get(predicted_bundle, 0.0) if predicted_match else 0.0
        abstain = decision.get("outcome") == "NO_MATCH"
        rows.append(
            {
                "condition": condition,
                "target_id": target_id,
                "predicted_bundle_id": predicted_bundle,
                "predicted_cross_trait": decision.get("best_cross_trait"),
                "outcome": decision.get("outcome"),
                "weighted_hit_at_1": weighted_hit,
                "weighted_mrr": weighted_hit,
                "has_positive_bundle": bool(positive_weights),
                "tool_calls": len(row.get("tool_trace") or []),
                "used_gc": any(t["name"] == "cross_trait_genetic_correlation" for t in row.get("tool_trace") or []),
                "used_h2": any(t["name"] == "cross_trait_heritability" for t in row.get("tool_trace") or []),
                "used_ot": any(t["name"] == "cross_trait_open_targets" for t in row.get("tool_trace") or []),
                "abstain_correct": abstain and target_id in abstain_gold,
                "matched_with_full_evidence": (
                    predicted_match
                    and any(t["name"] == "cross_trait_genetic_correlation" for t in row.get("tool_trace") or [])
                    and any(t["name"] == "cross_trait_heritability" for t in row.get("tool_trace") or [])
                    and any(t["name"] == "cross_trait_open_targets" for t in row.get("tool_trace") or [])
                ),
            }
        )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}
    matched = df[df["outcome"] == "MATCHED"]
    abstains = df[df["outcome"] == "NO_MATCH"]
    return {
        "n_targets": int(len(df)),
        "weighted_hit_at_1": float(df["weighted_hit_at_1"].mean()),
        "weighted_mrr": float(df["weighted_mrr"].mean()),
        "bundle_resolution_rate": float(df["has_positive_bundle"].mean()),
        "average_tool_calls": float(df["tool_calls"].mean()),
        "tool_coverage_gc": float(df["used_gc"].mean()),
        "tool_coverage_h2": float(df["used_h2"].mean()),
        "tool_coverage_ot": float(df["used_ot"].mean()),
        "matched_with_full_evidence_rate": float(df["matched_with_full_evidence"].mean()),
        "abstain_precision": float(abstains["abstain_correct"].mean()) if len(abstains) else None,
        "matched_rate": float((df["outcome"] == "MATCHED").mean()),
        "mean_weighted_hit_among_matches": (
            float(matched["weighted_hit_at_1"].mean()) if len(matched) else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate v4 cross-trait transfer agent outputs.")
    parser.add_argument(
        "--conditions",
        default="all-tools",
        help="Comma-separated conditions to evaluate. Use 'all' for all available conditions.",
    )
    args = parser.parse_args()

    conditions = list(CONDITION_TOOLS) if args.conditions == "all" else [c.strip() for c in args.conditions.split(",") if c.strip()]
    frames = []
    summaries = []
    for condition in conditions:
        df = evaluate_condition(condition)
        if df.empty:
            print(f"[{condition}] No results found.")
            continue
        frames.append(df)
        summary = summarize(df)
        summary["condition"] = condition
        summaries.append(summary)
        print(f"[{condition}] weighted_hit@1={summary['weighted_hit_at_1']:.4f} avg_tool_calls={summary['average_tool_calls']:.2f}")

    if not frames:
        return

    out_dir = RUNS_DIR / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    detail_df = pd.concat(frames, ignore_index=True)
    detail_path = out_dir / "cross_trait_transfer_eval_detail.csv"
    detail_df.to_csv(detail_path, index=False)
    summary_path = out_dir / "cross_trait_transfer_eval_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2, ensure_ascii=False))
    print(f"Wrote evaluation detail -> {detail_path}")
    print(f"Wrote evaluation summary -> {summary_path}")


if __name__ == "__main__":
    main()
