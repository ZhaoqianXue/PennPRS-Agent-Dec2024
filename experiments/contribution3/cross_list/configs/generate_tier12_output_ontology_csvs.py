"""
Generate concise Tier 1/2 binary-to-binary output ontology CSVs.

Outputs:
  - input_output_ontology_summary__tier12_21disease.csv
  - input_output_ontology_pairs__tier12_21disease.csv

Both outputs are restricted to the 21 Tier 1/2 input diseases from phase 2.
Only binary-to-binary pairs are used here, because the requested output entity
is output ontology / disease rather than continuous traits.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]

PHASE2_DIR = (
    PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "analysis" / "phase2"
)
B2B_RUN_DIR = (
    PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "runs" / "binary_to_binary"
)
CONTRIB1_PREPROCESS_DIR = (
    PROJECT_ROOT / "experiments" / "contribution1" / "disease_preprocess"
)
OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "candidate_set_tier12__21disease"
)

READY_FOR_TRANSFER_CSV = PHASE2_DIR / "ready_for_transfer.csv"
B2B_ANNOTATED_PAIRS_CSV = PHASE2_DIR / "b2b_annotated_pairs.csv"
B2B_SUMMARY_CSV = B2B_RUN_DIR / "cross_list_summary.csv"
B2B_DISEASE_LEVEL_CSV = B2B_RUN_DIR / "cross_list_disease_level.csv"
PGS_ID_LIST_CSV = CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv"

SUMMARY_CSV = OUTPUT_DIR / "input_output_ontology_summary__tier12_21disease.csv"
PAIRS_CSV = OUTPUT_DIR / "input_output_ontology_pairs__tier12_21disease.csv"


def _parse_pgs_ids(raw: str) -> list[str]:
    raw = str(raw).strip()
    if not raw:
        return []
    try:
        parsed = ast.literal_eval(raw)
    except Exception:
        parsed = None
    if isinstance(parsed, list):
        return [str(x).strip() for x in parsed if str(x).strip()]
    return [x.strip() for x in raw.strip("[]").replace("'", "").split(",") if x.strip()]


def _load_selected_inputs() -> pd.DataFrame:
    ready = pd.read_csv(READY_FOR_TRANSFER_CSV)
    ready = ready.loc[ready["overall_tier"].isin([1, 2]), ["input_icd", "input_ontology"]].drop_duplicates()
    return ready.rename(columns={"input_icd": "Input ICD", "input_ontology": "Input Ontology"})


def _build_pgs_ontology_to_icd() -> dict[tuple[str, str], str]:
    pgs_id_list = pd.read_csv(PGS_ID_LIST_CSV)
    out: dict[tuple[str, str], str] = {}
    for _, row in pgs_id_list.iterrows():
        ontology = str(row["ontology"]).strip()
        icd = str(row["icd_root"]).strip()
        for pid in _parse_pgs_ids(row["pgs_ids"]):
            out[(pid, ontology)] = icd
    return out


def _format_output_icd(best_cross_pgs: str, output_ontology: str, pgs_ontology_to_icd: dict[tuple[str, str], str]) -> str:
    if not best_cross_pgs or not output_ontology:
        return ""
    parts: list[str] = []
    seen: set[str] = set()
    for ontology in str(output_ontology).split("; "):
        ontology = ontology.strip()
        if not ontology:
            continue
        icd = pgs_ontology_to_icd.get((str(best_cross_pgs).strip(), ontology))
        if icd and icd not in seen:
            seen.add(icd)
            parts.append(icd)
    return "; ".join(parts)


def _load_pair_rows(selected_inputs: pd.DataFrame) -> pd.DataFrame:
    disease_level = pd.read_csv(B2B_DISEASE_LEVEL_CSV)
    annotated = pd.read_csv(B2B_ANNOTATED_PAIRS_CSV)
    selected_icds = set(selected_inputs["Input ICD"])

    tier_lookup = (
        annotated.loc[annotated["input_id"].isin(selected_icds), ["input_id", "output_name", "tier", "plausibility"]]
        .drop_duplicates()
        .rename(
            columns={
                "input_id": "Input ICD",
                "output_name": "Output Ontology",
                "tier": "Pair Tier",
                "plausibility": "Plausibility",
            }
        )
    )

    pgs_ontology_to_icd = _build_pgs_ontology_to_icd()

    pairs = disease_level.rename(
        columns={
            "input_icd": "Input ICD",
            "input_ontology": "Input Ontology",
            "self_best_auc": "Input Best AUC",
            "output_disease": "Output Ontology",
            "n_models": "Output PRS Model Count",
            "best_cross_auc": "Output AUC",
            "best_cross_pgs": "Best Cross PGS",
            "best_auc_improvement": "Improvement",
        }
    )

    pairs = pairs.loc[pairs["Input ICD"].isin(selected_icds)].copy()
    pairs = pairs.merge(tier_lookup, on=["Input ICD", "Output Ontology"], how="left")
    pairs = pairs.loc[pairs["Pair Tier"].isin([1, 2])].copy()
    pairs["Output ICD"] = pairs.apply(
        lambda row: _format_output_icd(row["Best Cross PGS"], row["Output Ontology"], pgs_ontology_to_icd),
        axis=1,
    )

    pairs = pairs[
        [
            "Input Ontology",
            "Input ICD",
            "Output Ontology",
            "Output ICD",
            "Output PRS Model Count",
            "Input Best AUC",
            "Output AUC",
            "Improvement",
            "Pair Tier",
            "Plausibility",
        ]
    ].sort_values(
        ["Input Ontology", "Pair Tier", "Improvement", "Output Ontology"],
        ascending=[True, True, False, True],
    )

    return pairs


def _load_top_summary_lookup(selected_inputs: pd.DataFrame) -> pd.DataFrame:
    summary = pd.read_csv(B2B_SUMMARY_CSV)
    summary = summary.loc[summary["input_icd"].isin(set(selected_inputs["Input ICD"]))].copy()
    return summary.rename(
        columns={
            "input_icd": "Input ICD",
            "self_best_auc": "Input Best AUC",
            "top_cross_auc": "Top Output AUC",
            "top_auc_improvement": "Top Improvement",
        }
    )[
        ["Input ICD", "Input Best AUC", "Top Output AUC", "Top Improvement"]
    ]


def _build_summary(pairs: pd.DataFrame, top_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (input_ontology, input_icd), group in pairs.groupby(["Input Ontology", "Input ICD"], sort=False):
        ordered = group.sort_values(["Pair Tier", "Improvement", "Output Ontology"], ascending=[True, False, True])
        output_ontologies = ordered["Output Ontology"].drop_duplicates().tolist()
        output_icds = []
        seen_pairs: set[tuple[str, str]] = set()
        for _, row in ordered.iterrows():
            key = (row["Output Ontology"], row["Output ICD"])
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            output_icds.append(str(row["Output ICD"]).strip())

        top_row = top_summary.loc[top_summary["Input ICD"] == input_icd].iloc[0]
        rows.append(
            {
                "Input Ontology": input_ontology,
                "Input ICD": input_icd,
                "Output Ontology": "; ".join(output_ontologies),
                "Output ICD": "; ".join(output_icds),
                "Output Ontology Count": len(output_ontologies),
                "Input Best AUC": top_row["Input Best AUC"],
                "Top Output AUC": top_row["Top Output AUC"],
                "Top Improvement": top_row["Top Improvement"],
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["Output Ontology Count", "Top Improvement", "Input Ontology"],
        ascending=[False, False, True],
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    selected_inputs = _load_selected_inputs()
    pairs = _load_pair_rows(selected_inputs)
    top_summary = _load_top_summary_lookup(selected_inputs)
    summary = _build_summary(pairs, top_summary)

    summary.to_csv(SUMMARY_CSV, index=False)
    pairs.to_csv(PAIRS_CSV, index=False)

    print(f"Wrote {SUMMARY_CSV}")
    print(f"Wrote {PAIRS_CSV}")
    print(f"Summary rows: {len(summary)}")
    print(f"Pair rows: {len(pairs)}")


if __name__ == "__main__":
    main()
