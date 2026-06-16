"""Recompute the C3 cross-trait disease list on the original paired80 universe.

This keeps the original paired80 target universe:
  - Type A: legacy `aou_extend_trait`
  - Type B: legacy rootcode main-analysis matrix

and recomputes screening after the Contribution1 no-AoU/All-of-Us PGS-column
filter. The default `min_best_split_gap=0` matches the final disease-list
screening used by `benchmark_contrib1_latest/rebuild_outputs.py`; the stricter
historical default can be checked with `--min-best-split-gap 0.025`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]
CONFIGS_DIR = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "configs"
LATEST_DIR = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "benchmark_contrib1_latest"
if str(CONFIGS_DIR) not in sys.path:
    sys.path.insert(0, str(CONFIGS_DIR))
if str(LATEST_DIR) not in sys.path:
    sys.path.insert(0, str(LATEST_DIR))

import build_benchmark as bb  # noqa: E402
import build_cross_list as bcl  # noqa: E402
import rebuild_outputs as latest_rebuild  # noqa: E402


LEGACY_NO_AOU = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "legacy_no_aou_pgs"
OLD_PAIRED80 = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy_no_aou_pgs"
    / "unified"
    / "target_selection.csv"
)
OUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy80_no_aou_recomputed"
)


def _load_matrices() -> tuple[pd.DataFrame, pd.DataFrame]:
    type_a = pd.read_csv(
        LEGACY_NO_AOU / "aou_extend_trait" / "prs_adjauc_matrix_binary_extend_qc.csv",
        index_col=0,
    )
    type_b = pd.read_csv(
        LEGACY_NO_AOU / "aou_binary" / "prs_adjauc_matrix_binary_combined_rootcode.csv",
        index_col=0,
    )
    return type_a, type_b


def _apply_canonical_descriptions(df: pd.DataFrame, titles: dict[str, str]) -> pd.DataFrame:
    out = df.copy()
    if "input_icd" in out.columns and "input_description" in out.columns:
        mapped = out["input_icd"].astype(str).str.strip().map(titles)
        out["input_description"] = mapped.where(mapped.notna(), out["input_description"])
    if "target_icd" in out.columns and "target_description" in out.columns:
        mapped = out["target_icd"].astype(str).str.strip().map(titles)
        out["target_description"] = mapped.where(mapped.notna(), out["target_description"])
    return out


def _primary_posthoc_filter(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "selected" not in out.columns:
        return out
    for idx, row in out[out["selected"]].iterrows():
        icd = str(row.get("input_icd", "") or "").strip()
        desc = row.get("input_description", "")
        ont = row.get("input_ontology", "")
        reason = (
            "manual_icd_blocklist"
            if icd in latest_rebuild.POST_HOC_ICD_BLOCKLIST
            else latest_rebuild._primary_post_hoc_reason(desc, ont)
        )
        if reason:
            out.at[idx, "selected"] = False
            prior = str(row.get("selection_reason", "") or "")
            tag = f"dropped_post_hoc: {reason}"
            out.at[idx, "selection_reason"] = f"{prior}; {tag}" if prior else tag
    return out


def _concat_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [f for f in frames if f is not None and not f.empty]
    if not nonempty:
        return pd.DataFrame()
    nonempty = [f.dropna(axis=1, how="all") for f in nonempty]
    return pd.concat(nonempty, ignore_index=True, sort=False)


def _build_union(b2b: pd.DataFrame, b2c: pd.DataFrame) -> pd.DataFrame:
    b2b_sel = b2b[b2b["selected"]].copy()
    b2c_sel = b2c[b2c["selected"]].copy()
    rows: list[dict[str, object]] = []
    for icd in sorted(set(b2b_sel["input_icd"].astype(str)) | set(b2c_sel["input_icd"].astype(str))):
        rb = b2b_sel[b2b_sel["input_icd"].astype(str) == icd]
        rc = b2c_sel[b2c_sel["input_icd"].astype(str) == icd]
        row = rb.iloc[0] if len(rb) else rc.iloc[0]
        is_b = (
            "B" in set(rb.get("input_type", pd.Series(dtype=str)).astype(str))
            or "B" in set(rc.get("input_type", pd.Series(dtype=str)).astype(str))
        )
        rows.append(
            {
                "input_type": "B" if is_b else "A",
                "target_source": "rootcode_main_analysis" if is_b else "extend_trait",
                "input_icd": icd,
                "input_ontology": row.get("input_ontology", ""),
                "input_description": row.get("input_description", ""),
                "selected": True,
                "coverage": "both" if len(rb) and len(rc) else ("b2b_only" if len(rb) else "b2c_only"),
            }
        )
    return pd.DataFrame(rows)


def _union_posthoc_filter(union: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if union.empty:
        return union, union.copy()
    reasons = []
    for _, row in union.iterrows():
        reasons.append(
            latest_rebuild._union_exclusion_reason(
                row.get("input_description", ""),
                row.get("input_ontology", ""),
                row.get("input_icd", ""),
            )
            or ""
        )
    out = union.copy()
    out["_exclude"] = reasons
    kept = out[out["_exclude"] == ""].drop(columns=["_exclude"]).copy()
    excluded = out[out["_exclude"] != ""].rename(columns={"_exclude": "exclusion_reason"}).copy()
    return kept, excluded


def _write_outputs(
    out_dir: Path,
    b2b: pd.DataFrame,
    b2b_gt: pd.DataFrame,
    b2c: pd.DataFrame,
    b2c_gt: pd.DataFrame,
    union: pd.DataFrame,
    excluded: pd.DataFrame,
    params: dict[str, object],
) -> None:
    b2b_dir = out_dir / "binary_to_binary"
    b2c_dir = out_dir / "binary_to_continuous"
    unified_dir = out_dir / "unified"
    for path in (b2b_dir, b2c_dir, unified_dir):
        path.mkdir(parents=True, exist_ok=True)

    b2b.to_csv(b2b_dir / "target_selection.csv", index=False)
    b2b_gt.to_csv(b2b_dir / "ground_truth_ranking.csv", index=False)
    b2c.to_csv(b2c_dir / "target_selection.csv", index=False)
    b2c_gt.to_csv(b2c_dir / "ground_truth_ranking.csv", index=False)
    union.to_csv(out_dir / "union_selected_targets.csv", index=False)
    union[["input_type", "target_source", "input_icd", "input_ontology", "input_description", "selected"]].to_csv(
        unified_dir / "target_selection.csv",
        index=False,
    )
    (out_dir / "union_selected_icds.json").write_text(
        json.dumps(sorted(union["input_icd"].astype(str).tolist()), indent=2) + "\n",
        encoding="utf-8",
    )
    excluded.to_csv(out_dir / "union_excluded_targets.csv", index=False)

    old = pd.read_csv(OLD_PAIRED80)
    old_set = set(old["input_icd"].astype(str))
    new_set = set(union["input_icd"].astype(str))
    comparison = pd.DataFrame(
        [
            {"status": "added_vs_old80", "input_icd": icd}
            for icd in sorted(new_set - old_set)
        ]
        + [
            {"status": "removed_vs_old80", "input_icd": icd}
            for icd in sorted(old_set - new_set)
        ]
    )
    comparison.to_csv(out_dir / "comparison_vs_old80.csv", index=False)

    config = {
        **params,
        "name": out_dir.name,
        "original_paired80_target_count": int(len(old)),
        "recomputed_target_count": int(len(union)),
        "type_counts": {str(k): int(v) for k, v in union["input_type"].value_counts().items()},
        "coverage_counts": {str(k): int(v) for k, v in union["coverage"].value_counts().items()},
        "source_universe": {
            "type_a": "experiments/contribution1/result/legacy_no_aou_pgs/aou_extend_trait",
            "type_b": "experiments/contribution1/result/legacy_no_aou_pgs/aou_binary",
        },
        "old_paired80_target_selection": str(OLD_PAIRED80.relative_to(PROJECT_ROOT)),
    }
    (out_dir / "benchmark_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-best-split-gap", type=float, default=0.0)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    bcl.CONTRIB1_LOINC_RESULT_DIR = LEGACY_NO_AOU / "aou_continuous"
    bb.CONTRIB1_LOINC_RESULT_DIR = LEGACY_NO_AOU / "aou_continuous"

    type_a_matrix, type_b_matrix = _load_matrices()
    allowed_a = set(type_a_matrix.index.astype(str))
    allowed_b = set(type_b_matrix.index.astype(str))
    titles = latest_rebuild._load_canonical_icd_titles(latest_rebuild.ICD_CANONICAL_TITLES_PATH)

    params = {
        "delta": bb.DEFAULT_DELTA,
        "k_min": bb.DEFAULT_K_MIN,
        "min_top_cross_auc": bb.DEFAULT_MIN_TOP_CROSS_AUC,
        "min_best_split_gap": float(args.min_best_split_gap),
        "max_self_auc": bb.DEFAULT_MAX_SELF_AUC,
    }

    b2b_b, b2b_gt_b = bb.build_b2b_benchmark(type_b_matrix, allowed_b, min_best_split_gap=args.min_best_split_gap)
    b2c_b, b2c_gt_b = bb.build_b2c_benchmark(type_b_matrix, allowed_b, min_best_split_gap=args.min_best_split_gap)
    b2b_a, b2b_gt_a = bb.build_b2b_type_a_benchmark(type_a_matrix, allowed_a, min_best_split_gap=args.min_best_split_gap)
    b2c_a, b2c_gt_a = bb.build_b2c_type_a_benchmark(type_a_matrix, allowed_a, min_best_split_gap=args.min_best_split_gap)

    for frame in (b2b_b, b2c_b, b2b_gt_b, b2c_gt_b):
        frame["target_source"] = "rootcode_main_analysis"
    for frame in (b2b_a, b2c_a, b2b_gt_a, b2c_gt_a):
        frame["target_source"] = "extend_trait"

    b2b = _primary_posthoc_filter(_apply_canonical_descriptions(_concat_frames([b2b_a, b2b_b]), titles))
    b2c = _primary_posthoc_filter(_apply_canonical_descriptions(_concat_frames([b2c_a, b2c_b]), titles))
    b2b_gt = _apply_canonical_descriptions(_concat_frames([b2b_gt_a, b2b_gt_b]), titles)
    b2c_gt = _apply_canonical_descriptions(_concat_frames([b2c_gt_a, b2c_gt_b]), titles)

    union, excluded = _union_posthoc_filter(_build_union(b2b, b2c))
    _write_outputs(args.output_dir, b2b, b2b_gt, b2c, b2c_gt, union, excluded, params)

    print(f"Old paired80 count: {len(pd.read_csv(OLD_PAIRED80))}")
    print(f"Recomputed count: {len(union)}")
    print(f"Type counts: {union['input_type'].value_counts().to_dict()}")
    print(f"Coverage counts: {union['coverage'].value_counts().to_dict()}")
    print(f"Wrote: {args.output_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
