"""
Contribution2 Disease Selection Script

Select diseases from All of Us benchmark (contribution1) based on three criteria:
1. Top PRS model AUC has distinguishability from the rest (for Agent to identify optimal model)
2. Overall AUC not too low (mean AUC of all candidate models > threshold)
3. Genetic significance and broad recognition (not niche)

Output: selected_diseases_contribution2.csv and selection_report.md

Usage:
  python select_diseases_contribution2.py           # rootcode (default)
  python select_diseases_contribution2.py --childrencode  # childrencode
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONTRIB2_DIR = Path(__file__).parent.parent.parent
CONTRIB1_RESULT_DIR = CONTRIB2_DIR.parent / "contribution1" / "result" / "aou_icd_260217"
DISEASE_SELECTION_DIR = Path(__file__).parent.parent
OUTPUT_RUNS_DIR = DISEASE_SELECTION_DIR / "runs"
OUTPUT_METRICS_DIR = DISEASE_SELECTION_DIR / "metrics"

# ---------------------------------------------------------------------------
# Selection criteria parameters
# ---------------------------------------------------------------------------
MIN_MEAN_AUC = 0.5  # Mean AUC across all candidate models (QC3)
MIN_N_MODELS = 3

# Criterion 1: Top vs Rest - any of (T1 vs Rest, T2 vs Rest, T3 vs Rest) >= threshold
# Pass if at least one cliff exists in the top tier
MIN_TOP_VS_REST_GAP = 0.025

# Hard minimum on Top-1 AUC: best model must perform at least this well
MIN_TOP1_AUC = 0.55

# ---------------------------------------------------------------------------
# Criterion 2: Genetic significance (keyword screening)
# Curated domains and traits with broad genetic epidemiology recognition
# Excludes: rare conditions, non-genetic traits, very niche phenotypes
# ---------------------------------------------------------------------------
GENETICALLY_SIGNIFICANT_KEYWORDS = [
    "alzheimer", "parkinson", "dementia",
    "schizophrenia", "bipolar", "depressive", "depression", "adhd", "autism", "anxiety",
    "coronary", "atrial fibrillation", "myocardial", "heart failure", "hypertension",
    "breast", "prostate", "lung", "melanoma", "ovarian", "colorectal", "bladder", "renal",
    "thyroid",
    "type 2 diabetes", "diabetes", "obesity",
    "rheumatoid", "lupus", "psoriasis", "inflammatory bowel", "celiac", "ankylosing", "spondylitis",
    "asthma", "copd", "chronic obstructive", "chronic kidney", "gout", "osteoporosis",
    "age-related macular", "glaucoma", "hearing", "graves", "hashimoto",
]

NICHE_EXCLUSION_KEYWORDS = [
    "abnormal ekg", "vaginal", "pelvic organ prolapse", "hemorrhoid",
    "common wart", "sunburn", "seborrheic keratosis", "epidermal inclusion cyst",
    "follicular cyst", "acne", "cellulitis", "phlebitis", "varicose",
    "radius fracture", "bone fracture", "intervertebral disc", "spondylosis",
    "syncope", "device complication", "drug allergy",
    "rh isoimmunization", "slipped epiphyses",
    "dupuytren contracture", "corneal disease", "overnutrition",
    "atopic eczema", "her2-negative breast carcinoma", "her2 negative breast",
    "diabetic eye disease",
]


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


def main(use_childrencode: bool = False) -> None:
    suffix = "childrencode" if use_childrencode else "rootcode"
    trait_col = "icd" if use_childrencode else "icd_root"

    # -----------------------------------------------------------------------
    # Load data
    # -----------------------------------------------------------------------
    matrix = pd.read_csv(CONTRIB1_RESULT_DIR / f"prs_adjauc_matrix_260217_{suffix}.csv")
    metadata = pd.read_csv(CONTRIB1_RESULT_DIR / f"prs_adjauc_metadata_260217_{suffix}.csv")
    trait_case_count = pd.read_csv(CONTRIB1_RESULT_DIR / f"trait_case_count_260217_{suffix}.csv")

    # Filter to included traits (case_count >= 200 from postprocess)
    included = metadata[metadata["include_in_analysis"] == 1]
    case_map = trait_case_count.drop_duplicates("ICD10_code").set_index("ICD10_code")["case_count"]

    # -----------------------------------------------------------------------
    # Compute per-ontology metrics
    # -----------------------------------------------------------------------
    rows = []
    for _, mrow in included.iterrows():
        ontology = mrow["ontology"]
        icd_root = mrow["icd_root"]
        icd_trait = mrow[trait_col]
        pgs_ids = _parse_pgs_ids(str(mrow["pgs_ids"]))
        if len(pgs_ids) < MIN_N_MODELS:
            continue

        auc_series = _get_trait_auc_for_models(matrix, icd_trait, pgs_ids)
        if auc_series.empty or len(auc_series) < MIN_N_MODELS:
            continue

        auc_values = auc_series.dropna().values
        if len(auc_values) < MIN_N_MODELS:
            continue

        # Top-1 through Top-10 = sorted by AUC descending
        sorted_auc = sorted(auc_values, reverse=True)
        top_aucs = [float(sorted_auc[i]) if i < len(sorted_auc) else None for i in range(10)]
        top1_auc, top2_auc, top3_auc = top_aucs[0], top_aucs[1], top_aucs[2]
        max_auc = float(max(auc_values))
        min_auc = float(min(auc_values))
        mean_auc = float(pd.Series(auc_values).mean())
        median_auc = float(pd.Series(auc_values).median())

        # Top-k vs Rest gaps: Tk vs Rest = Top-k - Top-(k+1)
        top_vs_rest_gaps = []
        for k in range(5):
            if k + 1 < len(sorted_auc):
                top_vs_rest_gaps.append(float(sorted_auc[k]) - float(sorted_auc[k + 1]))
            else:
                top_vs_rest_gaps.append(None)

        case_num = int(case_map.get(icd_trait, 0)) if icd_trait in case_map.index else 0

        def _rnd(x):
            return round(x, 4) if x is not None else None

        rows.append({
            "ontology": ontology,
            "icd_root": icd_root,
            "icd_trait": icd_trait,
            "n_models": len(pgs_ids),
            "n_with_auc": len(auc_series.dropna()),
            "max_auc": round(max_auc, 4),
            "mean_auc": round(mean_auc, 4),
            "median_auc": round(median_auc, 4),
            "min_auc": round(min_auc, 4),
            **{f"top{i+1}_auc": round(v, 4) if v is not None else None for i, v in enumerate(top_aucs)},
            **{f"top{i+1}_vs_rest_gap": _rnd(top_vs_rest_gaps[i]) for i in range(5)},
            "case_num": case_num,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        print("No ontologies passed initial filters.")
        return

    # -----------------------------------------------------------------------
    # Apply criteria
    # -----------------------------------------------------------------------
    # Criterion 1: Any of (T1..T5 vs Rest) >= threshold
    gap_cols = [f"top{i}_vs_rest_gap" for i in range(1, 6)]
    max_gap = df[gap_cols].fillna(-1).max(axis=1)
    df["c1_distinguishable"] = (max_gap >= MIN_TOP_VS_REST_GAP) | (df["n_models"] == 2)

    # Criterion 2: Genetic significance (keyword screening: whitelist - blacklist)
    def _genetic_ok(name: str) -> bool:
        name_lower = name.lower()
        for k in NICHE_EXCLUSION_KEYWORDS:
            if k in name_lower:
                return False
        for k in GENETICALLY_SIGNIFICANT_KEYWORDS:
            if k in name_lower:
                return True
        return False

    df["c2_genetic_significance"] = df["ontology"].apply(_genetic_ok)

    # Criterion 3: AUC thresholds (Mean >= 0.5 AND Top-1 >= 0.55) - filtering step
    df["c3_auc_ok"] = (df["mean_auc"] >= MIN_MEAN_AUC) & (df["top1_auc"] >= MIN_TOP1_AUC)

    # QC1/QC2/QC3 explicit columns for report
    df["qc1_t1_t5_vs_rest_ge_0025"] = df["c1_distinguishable"].map({True: "Yes", False: "No"})
    df["qc2_genetic_significance"] = df["c2_genetic_significance"].map({True: "Yes", False: "No"})
    df["qc3_auc_ok"] = df["c3_auc_ok"].map({True: "Yes", False: "No"})

    # Staged selection (not intersection):
    # Step 1 (QC2): Genetic significance = whitelist add, blacklist subtract
    # Step 2 (QC1): Add those with distinguishability -> pool = QC2 OR QC1 (additive)
    # Step 3 (QC3): Filter pool by AUC thresholds
    # Step 4: Exclude blacklisted ontologies entirely (hard exclusion)
    def _is_blacklisted(name: str) -> bool:
        name_lower = name.lower()
        return any(k in name_lower for k in NICHE_EXCLUSION_KEYWORDS)

    pool = df[df["c2_genetic_significance"] | df["c1_distinguishable"]]
    pool = pool[~pool["ontology"].apply(_is_blacklisted)]
    selected = pool[pool["c3_auc_ok"]].copy()
    selected = selected.sort_values("mean_auc", ascending=False)

    # Rootcode: dedup by icd_root (one per root). Childrencode: no dedup, keep each children code.
    if use_childrencode:
        selected_final = selected.reset_index(drop=True)
    else:
        selected_final = selected.drop_duplicates("icd_root", keep="first").reset_index(drop=True)
    # Sort: QC1=Yes first, then by mean_auc descending
    selected_final = selected_final.sort_values(
        ["c1_distinguishable", "mean_auc"],
        ascending=[False, False],
    ).reset_index(drop=True)

    # Output: QC1=Yes only (hide QC1=No per user request)
    selected_output = selected_final[selected_final["c1_distinguishable"]].reset_index(drop=True)

    # Build table-matching CSV (same columns, order, and format as report table)
    icd_col = "icd_trait" if use_childrencode else "icd_root"
    qc1_col = f"QC1 (≥{MIN_TOP_VS_REST_GAP})"

    def _cell(val):
        return "-" if pd.isna(val) or val == "" else val

    table_rows = []
    for _, r in selected_output.iterrows():
        top_vals = [_cell(r.get(f"top{i}_auc")) for i in range(1, 11)]
        qc1_val = r.get("qc1_t1_t5_vs_rest_ge_0025", "Yes" if r.get("c1_distinguishable") else "No")
        table_rows.append({
            "Ontology": r["ontology"],
            "ICD": r[icd_col],
            "N Models": _cell(r.get("n_models")),
            "Max": _cell(r.get("max_auc")),
            "Mean": _cell(r.get("mean_auc")),
            "Median": _cell(r.get("median_auc")),
            "Min": _cell(r.get("min_auc")),
            **{f"Top-{i}": top_vals[i - 1] for i in range(1, 11)},
            "Case N": _cell(r.get("case_num")),
            qc1_col: qc1_val,
        })
    table_df = pd.DataFrame(table_rows)

    # -----------------------------------------------------------------------
    # Save outputs
    # -----------------------------------------------------------------------
    out_suffix = f"_{suffix}" if use_childrencode else ""
    OUTPUT_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_METRICS_DIR.mkdir(parents=True, exist_ok=True)
    table_df.to_csv(OUTPUT_RUNS_DIR / f"selected_diseases_contribution2{out_suffix}.csv", index=False)

    # Metrics: same schema as table (all ontologies, table columns only)
    metrics_rows = []
    for _, r in df.iterrows():
        top_vals = [_cell(r.get(f"top{i}_auc")) for i in range(1, 11)]
        qc1_val = r.get("qc1_t1_t5_vs_rest_ge_0025", "Yes" if r.get("c1_distinguishable") else "No")
        metrics_rows.append({
            "Ontology": r["ontology"],
            "ICD": r[icd_col],
            "N Models": _cell(r.get("n_models")),
            "Max": _cell(r.get("max_auc")),
            "Mean": _cell(r.get("mean_auc")),
            "Median": _cell(r.get("median_auc")),
            "Min": _cell(r.get("min_auc")),
            **{f"Top-{i}": top_vals[i - 1] for i in range(1, 11)},
            "Case N": _cell(r.get("case_num")),
            qc1_col: qc1_val,
        })
    pd.DataFrame(metrics_rows).to_csv(
        OUTPUT_METRICS_DIR / f"disease_selection_full_metrics{out_suffix}.csv", index=False
    )

    # -----------------------------------------------------------------------
    # Report
    # -----------------------------------------------------------------------
    code_label = "childrencode" if use_childrencode else "rootcode"
    report_lines = [
        f"# Contribution2 Disease Selection Report ({code_label})",
        "",
        "## Selection Criteria",
        "",
        "### QC1: Top PRS Model Distinguishability",
        "- **Tk vs Rest**: Top-k AUC - Top-(k+1) AUC (cliff between rank k and k+1).",
        f"- **Threshold**: Pass if any of (T1, T2, T3, T4, T5 vs Rest) >= {MIN_TOP_VS_REST_GAP}.",
        "",
        "### QC2: Genetic Significance (keyword screening)",
        "- **Whitelist**: Ontology name matches GENETICALLY_SIGNIFICANT_KEYWORDS.",
        "- **Blacklist**: Exclude if matches NICHE_EXCLUSION_KEYWORDS.",
        "",
        "### QC3: AUC Thresholds (filtering step)",
        f"- **Mean AUC** >= {MIN_MEAN_AUC}, **Top-1 AUC** >= {MIN_TOP1_AUC}.",
        "",
        "### Staged Logic (no intersection, no count limit)",
        "- **QC2**: Genetic significance pool (whitelist add, blacklist subtract).",
        "- **QC1 + QC2**: Pool = QC2 OR QC1 (additive: genetic significance OR distinguishability).",
        "- **QC3**: Filter pool by AUC thresholds."
        + (" Dedup by ICD root." if not use_childrencode else " No dedup (each ICD children code independent)."),
        "",
        "## Selected Diseases",
        "",
        f"Total selected (QC1=Yes only): {len(selected_output)}",
        "",
        f"| Ontology | ICD | N Models | Max | Mean | Median | Min | Top-1 | Top-2 | Top-3 | Top-4 | Top-5 | Top-6 | Top-7 | Top-8 | Top-9 | Top-10 | Case N | QC1 (≥{MIN_TOP_VS_REST_GAP}) |",
        "|----------|-----|----------|-----|------|--------|-----|-------|-------|-------|-------|-------|-------|-------|-------|--------|--------|-----|---------------------|",
    ]
    icd_col = "icd_trait" if use_childrencode else "icd_root"
    for _, r in selected_output.iterrows():
        med = r["median_auc"] if pd.notna(r.get("median_auc")) else "-"
        mx = r["max_auc"] if pd.notna(r.get("max_auc")) else "-"
        top_cols = [r.get(f"top{i}_auc") if pd.notna(r.get(f"top{i}_auc")) else "-" for i in range(1, 11)]
        top_str = " | ".join(str(v) for v in top_cols)
        qc1 = r.get("qc1_t1_t5_vs_rest_ge_0025", "Yes" if r.get("c1_distinguishable") else "No")
        report_lines.append(
            f"| {r['ontology']} | {r[icd_col]} | {r['n_models']} | {mx} | {r['mean_auc']} | {med} | {r['min_auc']} | {top_str} | {r['case_num']} | {qc1} |"
        )
    report_lines.extend([
        "",
        "## Summary Statistics",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Ontologies passing QC1 (T1..T5 vs Rest >= {MIN_TOP_VS_REST_GAP}) | {df['c1_distinguishable'].sum()} |",
        f"| Ontologies passing QC2 (genetic significance) | {df['c2_genetic_significance'].sum()} |",
        f"| Ontologies passing QC3 (Mean AUC >= {MIN_MEAN_AUC} & Top-1 >= {MIN_TOP1_AUC}) | {df['c3_auc_ok'].sum()} |",
        f"| Final selected (QC1=Yes) | {len(selected_output)} |",
        f"| Total pool before QC1 filter | {len(selected_final)} |",
    ])

    report_path = OUTPUT_RUNS_DIR / f"disease_selection_report{out_suffix}.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Selected {len(selected_output)} diseases (QC1=Yes only, {code_label}). Outputs written to {DISEASE_SELECTION_DIR}")
    print(f"  - runs/selected_diseases_contribution2{out_suffix}.csv")
    print(f"  - runs/disease_selection_report{out_suffix}.md")
    print(f"  - metrics/disease_selection_full_metrics{out_suffix}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contribution2 disease selection")
    parser.add_argument(
        "--childrencode",
        action="store_true",
        help="Use childrencode data (ICD sub-codes) instead of rootcode",
    )
    args = parser.parse_args()
    main(use_childrencode=args.childrencode)
