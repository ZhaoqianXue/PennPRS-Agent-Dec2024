"""
Generate evaluated PGS IDs per ontology for Contribution2 Agent evaluation filter.

Reads Contribution1 metadata + AUC matrix and the union CSV to produce
ontology -> [PGS IDs with valid AUC in All of Us] mapping. Only models that appear
in the N Models count (i.e. passed All of Us evaluation) are included.

Outputs:
  - recommendation/runs/.../evaluated_pgs_per_ontology.json
  - recommendation/runs/.../top_k_pgs_per_ontology.json
  - recommendation/runs/.../benchmark_auc_per_ontology.json

Usage:
  python generate_evaluated_pgs_list.py
  python generate_evaluated_pgs_list.py --union-csv experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__67disease.csv

Requirements:
  - experiments/contribution1/result/aou_icd_260217/prs_adjauc_matrix_260217_*.csv
  - experiments/contribution1/result/aou_icd_260217/prs_adjauc_metadata_260217_*.csv
  - experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_union__30disease.csv

If Contribution1 files are missing, prints a clear message and exits.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONTRIB2_DIR = Path(__file__).parent.parent.parent
CONTRIB1_RESULT_DIR = CONTRIB2_DIR.parent / "contribution1" / "result" / "aou_icd_260217"
RECOMMENDATION_DIR = Path(__file__).parent.parent
DEFAULT_UNION_CSV = CONTRIB2_DIR / "disease_selection" / "runs" / "selected_diseases_contribution2_union__30disease.csv"
DEFAULT_OUTPUT_DIR = RECOMMENDATION_DIR / "runs" / "ground-truth__contribution1"
CURRENT_UNION_CSV = CONTRIB2_DIR / "disease_selection" / "runs" / "selected_diseases_contribution2_current_union__67disease.csv"
LEGACY_CURRENT_UNION_STEM = "selected_diseases_contribution2_current_union"
EVALUATED_JSON_NAME = "evaluated_pgs_per_ontology.json"
RANKED_JSON_NAME = "top_k_pgs_per_ontology.json"
BENCHMARK_AUC_JSON_NAME = "benchmark_auc_per_ontology.json"


def _parse_pgs_ids(pgs_str: str) -> list[str]:
    """Parse pgs_ids from string representation of list."""
    try:
        out = ast.literal_eval(pgs_str)
        return list(out) if isinstance(out, (list, tuple)) else [out]
    except (ValueError, SyntaxError):
        return []


def _get_trait_auc_for_models(
    matrix: pd.DataFrame,
    trait: str,
    pgs_ids: list[str],
) -> pd.Series:
    """Extract AUC values for given trait and PGS IDs from matrix."""
    row = matrix[matrix["trait"] == trait]
    if row.empty:
        return pd.Series(dtype=float)

    # Matrix columns: PGS000xxx_hmPOS_GRCh38
    pgs_to_col = {c.replace("_hmPOS_GRCh38", ""): c for c in matrix.columns if c != "trait"}
    vals = {}
    for pid in pgs_ids:
        col = pgs_to_col.get(pid)
        if col is not None:
            v = row[col].iloc[0]
            if pd.notna(v) and isinstance(v, (int, float)):
                vals[pid] = float(v)
    return pd.Series(vals)


def _normalize_ontology(s: str) -> str:
    """Normalize ontology for lookup key (lowercase, stripped)."""
    return (s or "").strip().lower()


def _default_output_dir_for_union(union_path: Path) -> Path:
    if union_path.resolve() == DEFAULT_UNION_CSV.resolve():
        return DEFAULT_OUTPUT_DIR
    if union_path.resolve() == CURRENT_UNION_CSV.resolve() or union_path.stem == LEGACY_CURRENT_UNION_STEM:
        return RECOMMENDATION_DIR / "runs" / f"ground-truth__{LEGACY_CURRENT_UNION_STEM}"
    return RECOMMENDATION_DIR / "runs" / f"ground-truth__{union_path.stem}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Contribution2 benchmark ground-truth JSON files from Contribution1 AoU outputs."
    )
    parser.add_argument(
        "--union-csv",
        type=str,
        default=str(DEFAULT_UNION_CSV),
        help="Path to the disease union CSV (default: frozen 30-disease union).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for ground-truth JSON files. Defaults to runs/ground-truth__<union-stem> for non-default unions.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    union_path = Path(args.union_csv)
    if not union_path.exists():
        print(f"Union CSV not found: {union_path}")
        return

    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir_for_union(union_path)
    output_json = output_dir / EVALUATED_JSON_NAME
    ranked_json = output_dir / RANKED_JSON_NAME
    benchmark_auc_json = output_dir / BENCHMARK_AUC_JSON_NAME

    union_df = pd.read_csv(union_path)
    if union_df.empty:
        print("Union CSV is empty.")
        return

    # Load Contribution1 data (both rootcode and childrencode)
    rootcode_matrix_path = CONTRIB1_RESULT_DIR / "prs_adjauc_matrix_260217_rootcode.csv"
    rootcode_meta_path = CONTRIB1_RESULT_DIR / "prs_adjauc_metadata_260217_rootcode.csv"
    childrencode_matrix_path = CONTRIB1_RESULT_DIR / "prs_adjauc_matrix_260217_childrencode.csv"
    childrencode_meta_path = CONTRIB1_RESULT_DIR / "prs_adjauc_metadata_260217_childrencode.csv"

    missing = []
    for p in [rootcode_matrix_path, rootcode_meta_path, childrencode_matrix_path, childrencode_meta_path]:
        if not p.exists():
            missing.append(str(p))
    if missing:
        print("Contribution1 result files not found. Generate them first (see Contribution1 pipeline).")
        for m in missing:
            print(f"  - {m}")
        return

    rootcode_matrix = pd.read_csv(rootcode_matrix_path)
    rootcode_metadata = pd.read_csv(rootcode_meta_path)
    childrencode_matrix = pd.read_csv(childrencode_matrix_path)
    childrencode_metadata = pd.read_csv(childrencode_meta_path)

    ontology_to_evaluated_pgs: dict[str, list[str]] = {}
    ontology_to_top_k_pgs: dict[str, list[str]] = {}
    ontology_to_benchmark_auc: dict[str, dict[str, float]] = {}

    for _, row in union_df.iterrows():
        ontology = str(row.get("Ontology", "")).strip()
        icd = str(row.get("ICD", "")).strip()
        source = str(row.get("Source", "")).strip().lower()

        if not ontology or not icd:
            continue

        if source in ("childrencode", "both"):
            meta = childrencode_metadata
            matrix = childrencode_matrix
            trait_col = "icd"
        else:
            meta = rootcode_metadata
            matrix = rootcode_matrix
            trait_col = "icd_root"

        # Match metadata row: ontology and ICD
        icd_col = "icd" if "icd" in meta.columns else "icd_trait"
        if trait_col == "icd":
            matches = meta[(meta["ontology"] == ontology) & (meta[icd_col] == icd)]
        else:
            matches = meta[(meta["ontology"] == ontology) & (meta["icd_root"] == icd)]

        if matches.empty:
            continue

        mrow = matches.iloc[0]
        pgs_ids = _parse_pgs_ids(str(mrow.get("pgs_ids", "[]")))
        if not pgs_ids:
            continue

        auc_series = _get_trait_auc_for_models(matrix, icd, pgs_ids)
        evaluated_pgs = auc_series.dropna().index.tolist()

        # Sorted by AUC descending (rank 1 = best)
        sorted_pgs = auc_series.sort_values(ascending=False).index.tolist()
        benchmark_auc = {
            pgs_id: round(float(auc_series[pgs_id]), 6)
            for pgs_id in sorted_pgs
            if pd.notna(auc_series.get(pgs_id))
        }

        key = _normalize_ontology(ontology)
        ontology_to_evaluated_pgs[key] = evaluated_pgs
        ontology_to_top_k_pgs[key] = sorted_pgs
        ontology_to_benchmark_auc[key] = benchmark_auc

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(ontology_to_evaluated_pgs, f, indent=2, sort_keys=True)

    with open(ranked_json, "w", encoding="utf-8") as f:
        json.dump(ontology_to_top_k_pgs, f, indent=2, sort_keys=True)

    with open(benchmark_auc_json, "w", encoding="utf-8") as f:
        json.dump(ontology_to_benchmark_auc, f, indent=2, sort_keys=True)

    print(f"Union CSV: {union_path}")
    print(f"Output dir: {output_dir}")
    print(f"Wrote {len(ontology_to_evaluated_pgs)} ontologies to {output_json}")
    print(f"Wrote {len(ontology_to_top_k_pgs)} ontologies to {ranked_json}")
    print(f"Wrote {len(ontology_to_benchmark_auc)} ontologies to {benchmark_auc_json}")


if __name__ == "__main__":
    main()
