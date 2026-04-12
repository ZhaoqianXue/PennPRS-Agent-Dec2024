"""
Contribution2 Disease Selection Script

Select diseases from All of Us benchmark (contribution1) based on three criteria:
1. Top PRS model AUC has distinguishability from the rest (for Agent to identify optimal model)
2. Overall AUC not too low (mean AUC of all candidate models > threshold)
3. Exception allowlist for broad-recognition diseases, plus niche blacklist

Output: runs/intermediate/selected_diseases_contribution2*.csv and selection_report.md

Usage:
  python select_diseases_contribution2.py           # rootcode (default)
  python select_diseases_contribution2.py --childrencode  # childrencode
  python select_diseases_contribution2.py --min-n-models 3  # legacy threshold
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Iterable

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONTRIB2_DIR = Path(__file__).parent.parent.parent
CONTRIB1_BINARY_RESULT_DIR = CONTRIB2_DIR.parent / "contribution1" / "result" / "aou_binary"
CONTRIB1_LEGACY_ICD_RESULT_DIR = CONTRIB2_DIR.parent / "contribution1" / "result" / "aou_icd_260217"
DISEASE_SELECTION_DIR = Path(__file__).parent.parent
OUTPUT_RUNS_DIR = DISEASE_SELECTION_DIR / "runs"
OUTPUT_INTERMEDIATE_DIR = OUTPUT_RUNS_DIR / "intermediate"
OUTPUT_METRICS_DIR = DISEASE_SELECTION_DIR / "metrics"

CONTRIB1_ADJAUC_INPUTS = {
    "rootcode": {
        "matrix": CONTRIB1_BINARY_RESULT_DIR / "prs_adjauc_matrix_binary_combined_rootcode.csv",
        "metadata": CONTRIB1_BINARY_RESULT_DIR / "prs_adjauc_metadata_binary_combined_rootcode.csv",
        "case_count": CONTRIB1_BINARY_RESULT_DIR / "trait_case_count_binary_combined_rootcode.csv",
        "label": "aou_binary/binary_combined_rootcode",
    },
    # The colleague update includes a refreshed child-code case-count file, but
    # not the matching child-code AUC matrix/metadata. Keep child-code selection
    # on the legacy paired files until those refreshed inputs exist.
    "childrencode": {
        "matrix": CONTRIB1_LEGACY_ICD_RESULT_DIR / "prs_adjauc_matrix_260217_childrencode.csv",
        "metadata": CONTRIB1_LEGACY_ICD_RESULT_DIR / "prs_adjauc_metadata_260217_childrencode.csv",
        "case_count": CONTRIB1_LEGACY_ICD_RESULT_DIR / "trait_case_count_260217_childrencode.csv",
        "label": "aou_icd_260217/childrencode",
    },
}

# ---------------------------------------------------------------------------
# Selection criteria parameters
# ---------------------------------------------------------------------------
MIN_MEAN_AUC = 0.5  # Mean AUC across all candidate models (QC3)
DEFAULT_MIN_N_MODELS = 2

# Criterion 1: Top vs Rest - any of (T1 vs Rest, T2 vs Rest, T3 vs Rest, T4 vs Rest, T5 vs Rest) >= threshold
# Pass if at least one cliff exists in the top tier
MIN_TOP_VS_REST_GAP = 0.025
QC1_TOP_K = 5

# Hard minimum on Top-1 AUC: best model must perform at least this well
MIN_TOP1_AUC = 0.55

# ---------------------------------------------------------------------------
# Criterion 2: Exception allowlist (hard-add) + niche blacklist
# Curated ontology names that should be allowed through even if QC1 is weak.
# Non-matching diseases are neutral; they are not excluded by QC2.
# ---------------------------------------------------------------------------
EXCEPTION_ALLOWLIST_ONTOLOGIES = [
    "acute lymphoblastic leukemia",
    "atrial flutter",
    "asthma",
    "atrial fibrillation",
    "basal cell carcinoma",
    "bipolar disorder",
    "breast carcinoma",
    "chronic kidney disease",
    "chronic obstructive pulmonary disease",
    "coronary artery disease",
    "dilated cardiomyopathy",
    "glaucoma",
    "gout",
    "heart failure",
    "hypertension",
    "knee osteoarthritis",
    "lung cancer",
    "major depressive disorder",
    "melanoma",
    "myocardial infarction",
    "nephrolithiasis",
    "osteoporosis",
    "ovarian carcinoma",
    "parkinson disease",
    "psoriasis",
    "rheumatoid arthritis",
    "sarcoidosis",
    "systemic lupus erythematosus",
    "urinary bladder cancer",
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
    "diabetic eye disease", "corneal dystrophy", "iron metabolism disease",
    "alcohol-induced mental disorder",
    "congenital vitamin k-dependent coagulation factors deficiency",
    "nasal cavity polyp", "prolapse of female genital organ",
    "skin carcinoma in situ", "testicular neoplasm",
    "prostate disease",
]

# Specific diseases intentionally kept in the current 75-disease union even
# though their names contain a broader blacklist keyword.
BLACKLIST_EXEMPT_ONTOLOGIES = {
    "atopic eczema",
    "congenital vitamin k-dependent coagulation factors deficiency",
    "corneal dystrophy",
    "dupuytren contracture",
    "iron metabolism disease",
    "nasal cavity polyp",
    "skin carcinoma in situ",
}

# ---------------------------------------------------------------------------
# Parent/child and near-synonym overlap handling.
# 1) Some overlap groups should keep whichever label has stronger model coverage
#    (more N Models, then more evaluated AUCs, then higher Max/Mean).
# 2) Some umbrella labels are still too broad and should be suppressed only when
#    a more appropriate label from the same family is present.
# ---------------------------------------------------------------------------
MODEL_COUNT_PRIORITY_OVERLAP_GROUPS: tuple[set[str], ...] = (
    {"acute lymphoblastic leukemia", "lymphoid leukemia"},
    {"acute kidney injury", "kidney failure"},
    {"age-related macular degeneration", "macular degeneration"},
    {"breast carcinoma", "estrogen-receptor negative breast cancer", "estrogen-receptor positive breast cancer"},
    {"coronary artery disease", "coronary atherosclerosis"},
    {"hypertension", "essential hypertension", "increased blood pressure"},
    {"hyperthyroidism", "graves disease", "thyrotoxicosis"},
    {"lung cancer", "lung carcinoma"},
    {"major depressive disorder", "depressive disorder"},
    {"nephrolithiasis", "urolithiasis"},
    {"nodular goiter", "multinodular goiter", "nontoxic goiter"},
    {"ovarian carcinoma", "ovarian neoplasm", "ovarian serous carcinoma"},
    {"pulmonary fibrosis", "idiopathic pulmonary fibrosis"},
    {"systemic lupus erythematosus", "lupus erythematosus"},
    {"urinary bladder cancer", "urinary bladder carcinoma"},
    {"uterine carcinoma", "uterine cancer", "endometrial cancer", "endometrial carcinoma"},
)

ASYMMETRIC_ONTOLOGY_SUPPRESSION_RULES: dict[str, set[str]] = {
    "basal cell carcinoma": {"keratinocyte carcinoma", "non-melanoma skin carcinoma", "skin cancer", "skin carcinoma"},
    "coronary artery disease": {"heart disease"},
    "dilated cardiomyopathy": {"cardiomyopathy"},
    "heart failure": {"congestive heart failure"},
    "hypertrophic cardiomyopathy": {"cardiomyopathy"},
    "macular degeneration": {"retinopathy"},
    "age-related macular degeneration": {"retinopathy"},
    "squamous cell carcinoma": {"skin cancer"},
}

# Specific disease labels intentionally preserved even when a broader family
# label from the same ICD branch is present.
SUPPRESSION_EXEMPT_ONTOLOGIES = {
    "retinopathy",
}


def _parse_pgs_ids(pgs_str: str) -> list[str]:
    """Parse pgs_ids from string representation of list."""
    try:
        out = ast.literal_eval(pgs_str)
        return list(out) if isinstance(out, (list, tuple)) else [out]
    except (ValueError, SyntaxError):
        return []


def _normalize_ontology_name(name: str) -> str:
    return " ".join(str(name).lower().split())


def _representative_sort_columns(df: pd.DataFrame) -> tuple[list[str], list[bool]]:
    sort_cols = [c for c in ["n_models", "n_with_auc", "max_auc", "mean_auc", "source_rank"] if c in df.columns]
    return sort_cols, [False] * len(sort_cols)


def _apply_model_count_priority_overlap_groups(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    if df.empty or label_col not in df.columns:
        return df

    normalized = df[label_col].map(_normalize_ontology_name)
    keep_mask = pd.Series(True, index=df.index)
    sort_cols, ascending = _representative_sort_columns(df)

    for overlap_group in MODEL_COUNT_PRIORITY_OVERLAP_GROUPS:
        mask = normalized.isin(overlap_group)
        if mask.sum() <= 1:
            continue

        group_df = df.loc[mask].copy()
        group_df["__normalized_label"] = normalized.loc[mask]
        if sort_cols:
            representative = group_df.sort_values(sort_cols, ascending=ascending).iloc[0]
        else:
            representative = group_df.iloc[0]
        keep_label = representative["__normalized_label"]
        keep_mask.loc[mask & (normalized != keep_label)] = False

    return df.loc[keep_mask].copy()


def _collect_subsumed_ontology_names(names: Iterable[str]) -> set[str]:
    normalized_names = {_normalize_ontology_name(name) for name in names}
    suppressed: set[str] = set()
    for preferred, redundant_names in ASYMMETRIC_ONTOLOGY_SUPPRESSION_RULES.items():
        if preferred in normalized_names:
            suppressed.update(normalized_names.intersection(redundant_names))
    return suppressed - SUPPRESSION_EXEMPT_ONTOLOGIES


def _apply_ontology_overlap_rules(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    if df.empty or label_col not in df.columns:
        return df

    df = _apply_model_count_priority_overlap_groups(df, label_col)
    normalized = df[label_col].map(_normalize_ontology_name)
    suppressed = _collect_subsumed_ontology_names(normalized.tolist())
    if not suppressed:
        return df

    return df[~normalized.isin(suppressed)].copy()


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


def contrib1_adjauc_input_paths(suffix: str) -> dict[str, Path | str]:
    try:
        paths = CONTRIB1_ADJAUC_INPUTS[suffix]
    except KeyError as exc:
        raise ValueError(f"Unknown Contribution1 AUC suffix: {suffix}") from exc

    missing = [str(path) for key, path in paths.items() if key != "label" and not Path(path).exists()]
    if missing:
        joined = "\n  - ".join(missing)
        raise FileNotFoundError(f"Contribution1 AUC input files are missing:\n  - {joined}")
    return paths


def load_contrib1_adjauc_inputs(suffix: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = contrib1_adjauc_input_paths(suffix)
    return (
        pd.read_csv(Path(paths["matrix"])),
        pd.read_csv(Path(paths["metadata"])),
        pd.read_csv(Path(paths["case_count"])),
    )


def main(use_childrencode: bool = False, min_n_models: int = DEFAULT_MIN_N_MODELS) -> None:
    suffix = "childrencode" if use_childrencode else "rootcode"
    trait_col = "icd" if use_childrencode else "icd_root"

    # -----------------------------------------------------------------------
    # Load data
    # -----------------------------------------------------------------------
    matrix, metadata, trait_case_count = load_contrib1_adjauc_inputs(suffix)

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
        if len(pgs_ids) < min_n_models:
            continue

        auc_series = _get_trait_auc_for_models(matrix, icd_trait, pgs_ids)
        if auc_series.empty or len(auc_series) < min_n_models:
            continue

        auc_values = auc_series.dropna().values
        if len(auc_values) < min_n_models:
            continue

        # Top-1 through Top-10 = sorted by AUC descending
        sorted_auc = sorted(auc_values, reverse=True)
        top_aucs = [float(sorted_auc[i]) if i < len(sorted_auc) else None for i in range(10)]
        top1_auc, top2_auc, top3_auc = top_aucs[0], top_aucs[1], top_aucs[2]
        max_auc = float(max(auc_values))
        min_auc = float(min(auc_values))
        mean_auc = float(pd.Series(auc_values).mean())
        median_auc = float(pd.Series(auc_values).median())

        # QC1 uses adjacent ranked AUC differences, not a top-k average.
        # After sorting AUCs descending, "Tk vs Rest" means:
        #   gap_k = AUC(rank k) - AUC(rank k+1)
        # A disease passes QC1 if any gap among k=1..5 is large enough.
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
    gap_cols = [f"top{i}_vs_rest_gap" for i in range(1, QC1_TOP_K + 1)]
    max_gap = df[gap_cols].fillna(-1).max(axis=1)
    df["c1_distinguishable"] = (max_gap >= MIN_TOP_VS_REST_GAP) | (df["n_models"] == 2)

    # Criterion 2: Exception allowlist (hard-add), with blacklist taking precedence.
    def _qc2_exception_allow(name: str) -> bool:
        name_lower = _normalize_ontology_name(name)
        for k in NICHE_EXCLUSION_KEYWORDS:
            if k in name_lower and name_lower not in BLACKLIST_EXEMPT_ONTOLOGIES:
                return False
        return name_lower in EXCEPTION_ALLOWLIST_ONTOLOGIES

    df["c2_exception_allowlist"] = df["ontology"].apply(_qc2_exception_allow)

    # Criterion 3: AUC thresholds (Mean >= 0.5 AND Top-1 >= 0.55) - filtering step
    df["c3_auc_ok"] = (df["mean_auc"] >= MIN_MEAN_AUC) & (df["top1_auc"] >= MIN_TOP1_AUC)

    # QC1/QC2/QC3 explicit columns for report
    df["qc1_t1_t5_vs_rest_ge_0025"] = df["c1_distinguishable"].map({True: "Yes", False: "No"})
    df["qc2_exception_allowlist"] = df["c2_exception_allowlist"].map({True: "Yes", False: "No"})
    df["qc3_auc_ok"] = df["c3_auc_ok"].map({True: "Yes", False: "No"})

    # Staged selection (not intersection):
    # Step 1 (QC1): Distinguishability-based selection
    # Step 2 (QC2): Exception allowlist hard-add -> pool = QC1 OR QC2
    # Step 3 (QC3): Filter pool by AUC thresholds
    # Step 4: Exclude blacklisted ontologies entirely (hard exclusion)
    def _is_blacklisted(name: str) -> bool:
        name_lower = _normalize_ontology_name(name)
        return (
            name_lower not in BLACKLIST_EXEMPT_ONTOLOGIES
            and any(k in name_lower for k in NICHE_EXCLUSION_KEYWORDS)
        )

    pool = df[df["c2_exception_allowlist"] | df["c1_distinguishable"]]
    pool = pool[~pool["ontology"].apply(_is_blacklisted)]
    selected = pool[pool["c3_auc_ok"]].copy()
    selected = selected.sort_values("mean_auc", ascending=False)
    selected = _apply_ontology_overlap_rules(selected, "ontology")

    # Rootcode: dedup by icd_root (one per root). Prefer the ontology with the
    # most evaluated AUCs; break ties by max AUC. Childrencode keeps all rows.
    if use_childrencode:
        selected_final = selected.reset_index(drop=True)
    else:
        selected_final = selected.sort_values(
            ["n_with_auc", "max_auc"],
            ascending=[False, False],
        ).drop_duplicates("icd_root", keep="first").reset_index(drop=True)
    # Sort: QC1=Yes first, then QC2 allowlisted rows, then by mean_auc descending
    selected_final = selected_final.sort_values(
        ["c1_distinguishable", "c2_exception_allowlist", "mean_auc"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    # Output: keep both QC1-selected rows and QC2 exception-allowlisted rows.
    selected_output = selected_final.reset_index(drop=True)

    # Build table-matching CSV (same columns, order, and format as report table)
    icd_col = "icd_trait" if use_childrencode else "icd_root"
    qc1_col = f"QC1 (≥{MIN_TOP_VS_REST_GAP})"
    qc2_col = "QC2 (Allowlist)"

    def _cell(val):
        return "-" if pd.isna(val) or val == "" else val

    table_rows = []
    for _, r in selected_output.iterrows():
        top_vals = [_cell(r.get(f"top{i}_auc")) for i in range(1, 11)]
        qc1_val = r.get("qc1_t1_t5_vs_rest_ge_0025", "Yes" if r.get("c1_distinguishable") else "No")
        qc2_val = r.get("qc2_exception_allowlist", "Yes" if r.get("c2_exception_allowlist") else "No")
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
            qc2_col: qc2_val,
        })
    table_df = pd.DataFrame(table_rows)

    # -----------------------------------------------------------------------
    # Save outputs
    # -----------------------------------------------------------------------
    out_suffix = f"_{suffix}" if use_childrencode else ""
    OUTPUT_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_METRICS_DIR.mkdir(parents=True, exist_ok=True)
    table_df.to_csv(OUTPUT_INTERMEDIATE_DIR / f"selected_diseases_contribution2{out_suffix}.csv", index=False)

    # Metrics: same schema as table (all ontologies, table columns only)
    metrics_rows = []
    for _, r in df.iterrows():
        top_vals = [_cell(r.get(f"top{i}_auc")) for i in range(1, 11)]
        qc1_val = r.get("qc1_t1_t5_vs_rest_ge_0025", "Yes" if r.get("c1_distinguishable") else "No")
        qc2_val = r.get("qc2_exception_allowlist", "Yes" if r.get("c2_exception_allowlist") else "No")
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
            qc2_col: qc2_val,
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
        "- Sort all candidate PRS models for a disease by AUC in descending order.",
        "- For each k in {1, 2, 3, 4, 5}, compute `gap_k = AUC(rank k) - AUC(rank k+1)`.",
        f"- Pass QC1 if any `gap_k >= {MIN_TOP_VS_REST_GAP}`; this means there is a clear cliff between two adjacent ranks within the top 5.",
        "- This is not `Top-k average - rest average`; it is always an adjacent-rank difference.",
        "- Special case: if a disease has exactly 2 candidate models, QC1 is treated as passed.",
        "",
        "### QC2: Exception Allowlist",
        "- **Allowlist**: Ontology name is an exact curated match in EXCEPTION_ALLOWLIST_ONTOLOGIES and is force-kept even if QC1 is weak.",
        "- **Non-match**: Neutral. It is not excluded by QC2.",
        "- **Blacklist**: Exclude if matches NICHE_EXCLUSION_KEYWORDS.",
        "",
        "### QC3: AUC Thresholds (filtering step)",
        f"- **Mean AUC** >= {MIN_MEAN_AUC}, **Top-1 AUC** >= {MIN_TOP1_AUC}.",
        "",
        "### QC4: Parent/Child and Near-Synonym Overlap Resolution",
        "- For designated overlap groups, keep the label with stronger model coverage: higher `N Models`, then higher `N With AUC`, then higher `Max`, then higher `Mean`.",
        "- For a smaller set of umbrella labels, apply asymmetric suppression when a more appropriate label from the same family is already present.",
        "- Examples: `lymphoid leukemia` vs `acute lymphoblastic leukemia` uses model-count priority; `heart failure` suppresses `congestive heart failure`.",
        "",
        "### Staged Logic (no intersection, no count limit)",
        f"- **Base eligibility**: At least {min_n_models} candidate PGS models with evaluated AUC.",
        "- **QC1**: Primary selection by top-model distinguishability.",
        "- **QC2**: Exception allowlist hard-add.",
        "- **QC1 + QC2**: Pool = QC1 OR QC2.",
        "- **QC3**: Filter pool by AUC thresholds."
        + " Then resolve parent/child or near-synonym label overlaps before the source-specific dedup step."
        + (
            " Dedup by ICD root, preferring the ontology with the most evaluated AUCs and then higher max AUC."
            if not use_childrencode
            else " No dedup (each ICD children code independent)."
        ),
        "",
        "## Selected Diseases",
        "",
        f"Total selected (after QC3 and dedup): {len(selected_output)}",
        "",
        f"| Ontology | ICD | N Models | Max | Mean | Median | Min | Top-1 | Top-2 | Top-3 | Top-4 | Top-5 | Top-6 | Top-7 | Top-8 | Top-9 | Top-10 | Case N | QC1 (≥{MIN_TOP_VS_REST_GAP}) | QC2 (Allowlist) |",
        "|----------|-----|----------|-----|------|--------|-----|-------|-------|-------|-------|-------|-------|-------|-------|--------|--------|-----|---------------------|-----------------|",
    ]
    icd_col = "icd_trait" if use_childrencode else "icd_root"
    for _, r in selected_output.iterrows():
        med = r["median_auc"] if pd.notna(r.get("median_auc")) else "-"
        mx = r["max_auc"] if pd.notna(r.get("max_auc")) else "-"
        top_cols = [r.get(f"top{i}_auc") if pd.notna(r.get(f"top{i}_auc")) else "-" for i in range(1, 11)]
        top_str = " | ".join(str(v) for v in top_cols)
        qc1 = r.get("qc1_t1_t5_vs_rest_ge_0025", "Yes" if r.get("c1_distinguishable") else "No")
        qc2 = r.get("qc2_exception_allowlist", "Yes" if r.get("c2_exception_allowlist") else "No")
        report_lines.append(
            f"| {r['ontology']} | {r[icd_col]} | {r['n_models']} | {mx} | {r['mean_auc']} | {med} | {r['min_auc']} | {top_str} | {r['case_num']} | {qc1} | {qc2} |"
        )
    report_lines.extend([
        "",
        "## Summary Statistics",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Ontologies passing QC1 (T1..T5 vs Rest >= {MIN_TOP_VS_REST_GAP}) | {df['c1_distinguishable'].sum()} |",
        f"| Ontologies on QC2 exception allowlist | {df['c2_exception_allowlist'].sum()} |",
        f"| Ontologies passing QC3 (Mean AUC >= {MIN_MEAN_AUC} & Top-1 >= {MIN_TOP1_AUC}) | {df['c3_auc_ok'].sum()} |",
        f"| Final selected (QC1 or QC2 allowlist, after QC3) | {len(selected_output)} |",
        f"| Total pool before QC3 filter | {len(pool)} |",
    ])

    report_path = OUTPUT_RUNS_DIR / f"disease_selection_report{out_suffix}.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(
        f"Selected {len(selected_output)} diseases (QC1 or QC2 allowlist, {code_label}, min_n_models={min_n_models}). "
        f"Outputs written to {DISEASE_SELECTION_DIR}"
    )
    print(f"  - runs/intermediate/selected_diseases_contribution2{out_suffix}.csv")
    print(f"  - runs/disease_selection_report{out_suffix}.md")
    print(f"  - metrics/disease_selection_full_metrics{out_suffix}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contribution2 disease selection")
    parser.add_argument(
        "--childrencode",
        action="store_true",
        help="Use childrencode data (ICD sub-codes) instead of rootcode",
    )
    parser.add_argument(
        "--min-n-models",
        type=int,
        default=DEFAULT_MIN_N_MODELS,
        help="Minimum number of candidate PGS models required to enter disease selection (default: 2).",
    )
    args = parser.parse_args()
    main(use_childrencode=args.childrencode, min_n_models=args.min_n_models)
