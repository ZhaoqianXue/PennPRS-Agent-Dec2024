"""
Generate evaluated PGS IDs per ontology for Contribution2 Agent evaluation filter.

Reads Contribution1 metadata + AUC matrix and the union CSV to produce
ontology -> [PGS IDs with valid AUC in All of Us] mapping. Only models that appear
in the N Models count (i.e. passed All of Us evaluation) are included.

Output: recommendation/runs/evaluated_pgs_per_ontology.json, top_k_pgs_per_ontology.json

Usage:
  python generate_evaluated_pgs_list.py

Requirements:
  - experiments/contribution1/result/aou_icd_260217/prs_adjauc_matrix_260217_*.csv
  - experiments/contribution1/result/aou_icd_260217/prs_adjauc_metadata_260217_*.csv
  - experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_union.csv

If Contribution1 files are missing, prints a clear message and exits.
"""

from __future__ import annotations

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
UNION_CSV = CONTRIB2_DIR / "disease_selection" / "runs" / "selected_diseases_contribution2_union.csv"
OUTPUT_JSON = RECOMMENDATION_DIR / "runs" / "evaluated_pgs_per_ontology.json"
TOP_K_PGS_JSON = RECOMMENDATION_DIR / "runs" / "top_k_pgs_per_ontology.json"


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


def main() -> None:
    union_path = UNION_CSV
    if not union_path.exists():
        print(f"Union CSV not found: {union_path}")
        return

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

        key = _normalize_ontology(ontology)
        ontology_to_evaluated_pgs[key] = evaluated_pgs
        ontology_to_top_k_pgs[key] = sorted_pgs

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(ontology_to_evaluated_pgs, f, indent=2, sort_keys=True)

    with open(TOP_K_PGS_JSON, "w", encoding="utf-8") as f:
        json.dump(ontology_to_top_k_pgs, f, indent=2, sort_keys=True)

    print(f"Wrote {len(ontology_to_evaluated_pgs)} ontologies to {OUTPUT_JSON}")
    print(f"Wrote {len(ontology_to_top_k_pgs)} ontologies to {TOP_K_PGS_JSON}")


if __name__ == "__main__":
    main()
