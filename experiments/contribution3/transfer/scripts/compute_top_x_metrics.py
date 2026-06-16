"""Compute top_X_in_supporting_bundles and top_X_in_model_frontier metrics.

For each target, collect:
  - supporting_bundle_pgs_union: union of candidate_pgs_ids across all
    Judge-ranked supporting bundles.
  - model_frontier_pgs: pgs_id list from decision.model_frontier.

Then for each percentile cutoff (0.5%, 2.5%, 5%, 10%) check whether any
PGS in each set is in the target's AUC top-X%. Aggregate across the
subset and print target thresholds.

Usage:
  python -m experiments.contribution3.transfer.scripts.compute_top_x_metrics \
      --run-id p8b_20target_20260423 \
      --benchmark-family unified \
      --condition all-tools
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (  # noqa: E402
    _normalize_target_source,
    condition_results_json,
    evaluation_dir,
    load_benchmark_target_selection,
)


ROOT = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "legacy_no_aou_pgs"


def _col_to_pgs(c: str) -> str:
    s = str(c).strip().replace("_hmPOS_GRCh38", "")
    return s.split("__")[-1] if "__" in s else s


@lru_cache(maxsize=2)
def _matrix(source: str) -> pd.DataFrame:
    if source in ("nontarget_pgs", "extend_trait"):
        path = ROOT / "aou_extend_trait" / "prs_adjauc_matrix_binary_extend_qc.csv"
    else:
        path = ROOT / "aou_binary" / "prs_adjauc_matrix_binary_combined_rootcode.csv"
    return pd.read_csv(path, index_col=0)


def _top_pct_pgs_set(target_code: str, source: str, pct: float) -> set[str] | None:
    mat = _matrix(source)
    if target_code not in mat.index:
        return None
    row = mat.loc[target_code]
    auc = {_col_to_pgs(c): float(v) for c, v in row.items() if pd.notna(v)}
    ranked = sorted(auc, key=lambda k: (-auc[k], k))
    cutoff = max(1, int(len(ranked) * pct))
    return set(ranked[:cutoff])


def _target_source(tid: str, benchmark_family: str) -> str:
    try:
        df = load_benchmark_target_selection(
            benchmark_family=benchmark_family, selected_only=True
        )
        row = df[df["input_icd"].astype(str).str.strip() == str(tid).strip()]
        if row.empty:
            return "rootcode_main_analysis"
        return _normalize_target_source(row.iloc[0].get("target_source"))
    except Exception:
        return "rootcode_main_analysis"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", required=True)
    p.add_argument("--benchmark-family", default="unified")
    p.add_argument("--condition", default="all-tools")
    p.add_argument("--ablation", default="full")
    p.add_argument("--subset", type=str, default="", help="Optional comma-separated target_id filter.")
    args = p.parse_args()

    results_path = condition_results_json(
        args.condition,
        benchmark_family=args.benchmark_family,
        run_id=args.run_id,
        ablation=args.ablation,
    )
    if not results_path.exists():
        print(f"Results file not found: {results_path}", file=sys.stderr)
        sys.exit(1)
    blobs = json.loads(results_path.read_text())

    subset = (
        {t.strip() for t in args.subset.split(",") if t.strip()}
        if args.subset
        else None
    )
    blobs = [b for b in blobs if not subset or b["target"]["target_id"] in subset]

    summary: dict[str, int] = {
        f"top_{lbl}_{kind}": 0
        for lbl in ("0_5", "2_5", "5", "10")
        for kind in ("support", "frontier")
    }
    n = 0
    per_target: list[dict] = []
    for blob in blobs:
        tid = blob["target"]["target_id"]
        src = _target_source(tid, args.benchmark_family)
        dec = blob.get("decision") or {}
        support_pgs = set(
            dec.get("candidate_pgs_ids_union")
            or dec.get("candidate_pgs_ids")
            or []
        )
        frontier_pgs = {
            m.get("pgs_id") for m in (dec.get("model_frontier") or []) if m.get("pgs_id")
        }
        row = {"target_id": tid, "source": src}
        has_any_pool = False
        for pct, lbl in [(0.005, "0_5"), (0.025, "2_5"), (0.05, "5"), (0.10, "10")]:
            pool = _top_pct_pgs_set(tid, src, pct)
            if pool is None:
                row[f"top_{lbl}_support"] = None
                row[f"top_{lbl}_frontier"] = None
                continue
            has_any_pool = True
            s_hit = bool(support_pgs & pool)
            f_hit = bool(frontier_pgs & pool)
            row[f"top_{lbl}_support"] = s_hit
            row[f"top_{lbl}_frontier"] = f_hit
            summary[f"top_{lbl}_support"] += int(s_hit)
            summary[f"top_{lbl}_frontier"] += int(f_hit)
        if has_any_pool:
            n += 1
        per_target.append(row)

    print(f"=== top_X metrics (n={n}) ===")
    for k in ("0_5", "2_5", "5", "10"):
        s = summary[f"top_{k}_support"]
        f = summary[f"top_{k}_frontier"]
        print(
            f"  top_{k:4}  support {s}/{n} ({s/n:.3f})   frontier {f}/{n} ({f/n:.3f})"
            if n else f"  top_{k:4}  no data"
        )

    print("\n=== per-target (hit flags) ===")
    for r in per_target:
        flags = "  ".join(
            f"{k}={'1' if r[k] else '0' if r[k] is False else '-'}"
            for k in (
                "top_0_5_support", "top_0_5_frontier",
                "top_2_5_support", "top_2_5_frontier",
                "top_5_support", "top_5_frontier",
                "top_10_support", "top_10_frontier",
            )
        )
        print(f"  {r['target_id']:5s} {flags}")


if __name__ == "__main__":
    main()
