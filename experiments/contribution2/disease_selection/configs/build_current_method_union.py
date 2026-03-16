"""
Build a canonicalized current-method union from the latest rootcode and childrencode
selection logic without touching the frozen 30-disease benchmark union.

Usage:
  python experiments/contribution2/disease_selection/configs/build_current_method_union.py
  python experiments/contribution2/disease_selection/configs/build_current_method_union.py --require-qc1
  python experiments/contribution2/disease_selection/configs/build_current_method_union.py --min-n-models 3
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.disease_selection.configs import select_diseases_contribution2 as base


OUTPUT_RUNS_DIR = Path(__file__).parent.parent / "runs"
OUTPUT_INTERMEDIATE_DIR = OUTPUT_RUNS_DIR / "intermediate"
DEFAULT_REQUIRE_QC1 = False
DEFAULT_CURRENT_UNION_STEM = "selected_diseases_contribution2_current_union__75disease"

# Keep the broader canonical disease label for each merge group.
CANONICAL_MERGE_GROUPS: dict[str, set[str]] = {
    "glaucoma": {"glaucoma", "open-angle glaucoma"},
    "myocardial infarction": {"myocardial infarction", "acute myocardial infarction"},
    "melanoma": {"melanoma", "cutaneous melanoma"},
    "kidney cancer": {"kidney cancer", "renal carcinoma"},
    "ovarian carcinoma": {"ovarian carcinoma", "ovarian serous carcinoma"},
    "prostate cancer": {"prostate cancer", "prostate carcinoma"},
    "sleep apnea": {"sleep apnea", "obstructive sleep apnea"},
    "nodular goiter": {"nodular goiter", "multinodular goiter"},
    "peripheral vascular disease": {"peripheral vascular disease", "peripheral arterial disease"},
    "hyperthyroidism": {"hyperthyroidism", "graves disease"},
}


def _compute_selected_raw(
    use_childrencode: bool,
    min_n_models: int,
    require_qc1: bool = DEFAULT_REQUIRE_QC1,
) -> pd.DataFrame:
    suffix = "childrencode" if use_childrencode else "rootcode"
    trait_col = "icd" if use_childrencode else "icd_root"

    matrix = pd.read_csv(base.CONTRIB1_RESULT_DIR / f"prs_adjauc_matrix_260217_{suffix}.csv")
    metadata = pd.read_csv(base.CONTRIB1_RESULT_DIR / f"prs_adjauc_metadata_260217_{suffix}.csv")
    trait_case_count = pd.read_csv(base.CONTRIB1_RESULT_DIR / f"trait_case_count_260217_{suffix}.csv")

    included = metadata[metadata["include_in_analysis"] == 1]
    case_map = trait_case_count.drop_duplicates("ICD10_code").set_index("ICD10_code")["case_count"]

    rows: list[dict[str, object]] = []
    for _, mrow in included.iterrows():
        ontology = mrow["ontology"]
        icd_root = mrow["icd_root"]
        icd_trait = mrow[trait_col]
        pgs_ids = base._parse_pgs_ids(str(mrow["pgs_ids"]))
        if len(pgs_ids) < min_n_models:
            continue

        auc_series = base._get_trait_auc_for_models(matrix, icd_trait, pgs_ids)
        if auc_series.empty or len(auc_series) < min_n_models:
            continue

        auc_values = auc_series.dropna().values
        if len(auc_values) < min_n_models:
            continue

        sorted_auc = sorted(auc_values, reverse=True)
        top_aucs = [float(sorted_auc[i]) if i < len(sorted_auc) else None for i in range(10)]
        top_vs_rest_gaps = [
            float(sorted_auc[k]) - float(sorted_auc[k + 1]) if k + 1 < len(sorted_auc) else None
            for k in range(5)
        ]

        rows.append({
            "ontology": ontology,
            "normalized_ontology": base._normalize_ontology_name(ontology),
            "icd_root": icd_root,
            "icd_trait": icd_trait,
            "source": "childrencode" if use_childrencode else "rootcode",
            "source_rank": 1 if use_childrencode else 0,
            "n_models": len(pgs_ids),
            "n_with_auc": len(auc_series.dropna()),
            "max_auc": round(float(max(auc_values)), 4),
            "mean_auc": round(float(pd.Series(auc_values).mean()), 4),
            "median_auc": round(float(pd.Series(auc_values).median()), 4),
            "min_auc": round(float(min(auc_values)), 4),
            **{
                f"top{i + 1}_auc": round(v, 4) if v is not None else None
                for i, v in enumerate(top_aucs)
            },
            **{
                f"top{i + 1}_vs_rest_gap": round(top_vs_rest_gaps[i], 4) if top_vs_rest_gaps[i] is not None else None
                for i in range(5)
            },
            "case_num": int(case_map.get(icd_trait, 0)) if icd_trait in case_map.index else 0,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    gap_cols = [f"top{i}_vs_rest_gap" for i in range(1, base.QC1_TOP_K + 1)]
    max_gap = df[gap_cols].fillna(-1).max(axis=1)
    df["c1_distinguishable"] = (max_gap >= base.MIN_TOP_VS_REST_GAP) | (df["n_models"] == 2)

    def _qc2_exception_allow(name: str) -> bool:
        name_lower = base._normalize_ontology_name(name)
        for k in base.NICHE_EXCLUSION_KEYWORDS:
            if k in name_lower and name_lower not in base.BLACKLIST_EXEMPT_ONTOLOGIES:
                return False
        return name_lower in base.EXCEPTION_ALLOWLIST_ONTOLOGIES

    def _is_blacklisted(name: str) -> bool:
        name_lower = base._normalize_ontology_name(name)
        return (
            name_lower not in base.BLACKLIST_EXEMPT_ONTOLOGIES
            and any(k in name_lower for k in base.NICHE_EXCLUSION_KEYWORDS)
        )

    df["c2_exception_allowlist"] = df["ontology"].apply(_qc2_exception_allow)
    df["c3_auc_ok"] = (df["mean_auc"] >= base.MIN_MEAN_AUC) & (df["top1_auc"] >= base.MIN_TOP1_AUC)

    if require_qc1:
        pool = df[df["c2_exception_allowlist"] | df["c1_distinguishable"]]
    else:
        pool = df.copy()
    pool = pool[~pool["ontology"].apply(_is_blacklisted)]
    selected = pool[pool["c3_auc_ok"]].copy()
    selected = selected.sort_values("mean_auc", ascending=False)
    selected = base._apply_ontology_overlap_rules(selected, "ontology")

    if use_childrencode:
        selected_final = selected.reset_index(drop=True)
    else:
        selected_final = selected.sort_values(
            ["n_with_auc", "max_auc"],
            ascending=[False, False],
        ).drop_duplicates("icd_root", keep="first").reset_index(drop=True)

    return selected_final.sort_values(
        ["c1_distinguishable", "c2_exception_allowlist", "mean_auc"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def _canonical_name(name: str) -> str:
    normalized = base._normalize_ontology_name(name)
    for canonical, group in CANONICAL_MERGE_GROUPS.items():
        if normalized in group:
            return canonical
    return normalized


def _representative_row(group: pd.DataFrame) -> pd.Series:
    canonical = group["canonical_ontology"].iloc[0]
    canonical_rows = group[group["normalized_ontology"] == canonical]
    candidates = canonical_rows if not canonical_rows.empty else group

    return candidates.sort_values(
        ["n_with_auc", "max_auc", "mean_auc", "source_rank"],
        ascending=[False, False, False, False],
    ).iloc[0]


def _lookup_source(group: pd.DataFrame, representative: pd.Series) -> str:
    canonical = group["canonical_ontology"].iloc[0]
    canonical_sources = set(group.loc[group["normalized_ontology"] == canonical, "source"].tolist())
    if len(canonical_sources) == 1:
        return next(iter(canonical_sources))
    return str(representative["source"])


def _source_coverage(group: pd.DataFrame) -> str:
    sources = set(group["source"].tolist())
    if sources == {"rootcode", "childrencode"}:
        return "both"
    if sources == {"childrencode"}:
        return "childrencode"
    return "rootcode"


def _cell(value: object) -> object:
    return "-" if pd.isna(value) or value == "" else value


def build_current_method_union(
    min_n_models: int,
    require_qc1: bool = DEFAULT_REQUIRE_QC1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    root_df = _compute_selected_raw(
        use_childrencode=False,
        min_n_models=min_n_models,
        require_qc1=require_qc1,
    )
    child_df = _compute_selected_raw(
        use_childrencode=True,
        min_n_models=min_n_models,
        require_qc1=require_qc1,
    )

    combined = pd.concat([root_df, child_df], ignore_index=True)
    combined["canonical_ontology"] = combined["ontology"].apply(_canonical_name)
    combined = base._apply_ontology_overlap_rules(combined, "canonical_ontology")

    output_rows: list[dict[str, object]] = []
    detail_rows: list[dict[str, object]] = []
    for canonical, group in combined.groupby("canonical_ontology", sort=True):
        representative = _representative_row(group)
        lookup_source = _lookup_source(group, representative)
        source_coverage = _source_coverage(group)
        merged_ontologies = sorted(group["ontology"].unique().tolist())
        icd_value = representative["icd_trait"] if lookup_source == "childrencode" else representative["icd_root"]

        output_rows.append({
            "Ontology": canonical,
            "ICD": icd_value,
            "N Models": int(representative["n_models"]),
            "Max": representative["max_auc"],
            "Mean": representative["mean_auc"],
            "Median": representative["median_auc"],
            "Min": representative["min_auc"],
            **{
                f"Top-{i}": _cell(representative.get(f"top{i}_auc"))
                for i in range(1, 11)
            },
            "Case N": int(representative["case_num"]),
            "QC1 (≥0.025)": "Yes" if representative["c1_distinguishable"] else "No",
            "Source": lookup_source,
        })

        detail_rows.append({
            "Canonical Ontology": canonical,
            "Representative Ontology": representative["ontology"],
            "Lookup Source": lookup_source,
            "Source Coverage": source_coverage,
            "Representative Source": representative["source"],
            "Merged Ontologies": "; ".join(merged_ontologies),
            "ICD": icd_value,
            "N Models": int(representative["n_models"]),
            "N With AUC": int(representative["n_with_auc"]),
            "Max": representative["max_auc"],
            "Mean": representative["mean_auc"],
            "Median": representative["median_auc"],
            "Min": representative["min_auc"],
            **{
                f"Top-{i}": _cell(representative.get(f"top{i}_auc"))
                for i in range(1, 11)
            },
            "Case N": int(representative["case_num"]),
            "QC1 (≥0.025)": "Yes" if representative["c1_distinguishable"] else "No",
            "QC2 (Allowlist)": "Yes" if representative["c2_exception_allowlist"] else "No",
        })

    output_df = pd.DataFrame(output_rows).sort_values("Ontology").reset_index(drop=True)
    detail_df = pd.DataFrame(detail_rows).sort_values("Canonical Ontology").reset_index(drop=True)
    return output_df, detail_df


def _output_suffix(min_n_models: int, require_qc1: bool) -> str:
    if min_n_models == base.DEFAULT_MIN_N_MODELS and not require_qc1:
        return "__75disease"
    suffix_parts: list[str] = []
    if min_n_models != base.DEFAULT_MIN_N_MODELS:
        suffix_parts.append(f"min{min_n_models}")
    if require_qc1:
        suffix_parts.append("qc1required")
    return f"__{'_'.join(suffix_parts)}" if suffix_parts else ""


def main(min_n_models: int, require_qc1: bool = DEFAULT_REQUIRE_QC1) -> None:
    OUTPUT_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)

    root_df = _compute_selected_raw(
        use_childrencode=False,
        min_n_models=min_n_models,
        require_qc1=require_qc1,
    )
    child_df = _compute_selected_raw(
        use_childrencode=True,
        min_n_models=min_n_models,
        require_qc1=require_qc1,
    )
    raw_union_count = len(set(root_df["ontology"]).union(set(child_df["ontology"])))

    union_df, detail_df = build_current_method_union(
        min_n_models=min_n_models,
        require_qc1=require_qc1,
    )
    out_suffix = _output_suffix(min_n_models=min_n_models, require_qc1=require_qc1)
    csv_dir = OUTPUT_RUNS_DIR if min_n_models == base.DEFAULT_MIN_N_MODELS else OUTPUT_INTERMEDIATE_DIR
    if min_n_models == base.DEFAULT_MIN_N_MODELS:
        csv_path = csv_dir / f"{DEFAULT_CURRENT_UNION_STEM}.csv"
    else:
        csv_path = csv_dir / f"selected_diseases_contribution2_current_union{out_suffix}.csv"
    detail_csv_path = OUTPUT_INTERMEDIATE_DIR / f"selected_diseases_contribution2_current_union_details{out_suffix}.csv"
    report_path = OUTPUT_RUNS_DIR / f"selected_diseases_contribution2_current_union_report{out_suffix}.md"
    union_df.to_csv(csv_path, index=False)
    detail_df.to_csv(detail_csv_path, index=False)

    merged_groups = detail_df[detail_df["Merged Ontologies"].str.contains("; ", regex=False)].copy()
    report_lines = [
        "# Current-Method Canonical Union",
        "",
        f"- Base eligibility: `min_n_models = {min_n_models}`",
        f"- QC1 gate: `{'enabled (pool = QC1 OR QC2 allowlist)' if require_qc1 else 'disabled (QC1 retained as diagnostic column only)'}`",
        f"- Raw current-method ontology union size (before canonical merge): `{raw_union_count}`",
        f"- Canonical merged union size: `{len(union_df)}`",
        f"- Output CSV can be used directly by `recommendation/configs/generate_evaluated_pgs_list.py`; manual `Target_TopK` annotation is no longer required.",
        "",
        "## Canonical Merge Rule",
        "",
        "- Before canonical grouping, resolve designated parent/child or near-synonym overlap groups by model coverage, then suppress a small set of over-broad umbrella labels.",
        "- Prefer the manually specified canonical ontology label for each merge group.",
        "- If multiple rows share the canonical label, prefer larger `N With AUC`.",
        "- If still tied, prefer larger `Max`.",
        "- Final deterministic fallback: higher `Mean`, then `childrencode` over `rootcode`.",
        "",
        "## Collapsed Groups",
        "",
        f"Groups collapsed: `{len(merged_groups)}`",
        "",
        "| Canonical Ontology | Representative Ontology | Lookup Source | Source Coverage | Merged Ontologies | N With AUC | Max |",
        "|--------------------|-------------------------|---------------|-----------------|-------------------|------------|-----|",
    ]
    for _, row in merged_groups.iterrows():
        report_lines.append(
            f"| {row['Canonical Ontology']} | {row['Representative Ontology']} | {row['Lookup Source']} | {row['Source Coverage']} | {row['Merged Ontologies']} | {row['N With AUC']} | {row['Max']} |"
        )

    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Canonical current-method union written to {csv_path}")
    print(f"Canonical current-method union details written to {detail_csv_path}")
    print(f"Raw union size: {raw_union_count}")
    print(f"Merged union size: {len(union_df)}")
    print(f"Collapsed groups: {len(merged_groups)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build canonical current-method union")
    parser.add_argument(
        "--min-n-models",
        type=int,
        default=base.DEFAULT_MIN_N_MODELS,
        help=f"Minimum number of candidate PGS models required to enter disease selection (default: {base.DEFAULT_MIN_N_MODELS}).",
    )
    parser.add_argument(
        "--require-qc1",
        action="store_true",
        help="Require QC1 or QC2 allowlist to enter the pool. Default current union keeps QC1 as a diagnostic column only.",
    )
    args = parser.parse_args()
    main(min_n_models=args.min_n_models, require_qc1=args.require_qc1)
