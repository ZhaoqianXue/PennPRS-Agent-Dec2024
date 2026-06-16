"""
Contribution3: Build Cross List (rootcode only)

Reverse-engineering approach: using C1's rootcode cross-disease AUC matrix to
identify diseases that benefit from PRS model transfer.

Terminology:
  - target_trait: the trait needing transfer (user query)
    - Type A: target_trait has NO self benchmark score
    - Type B: target_trait HAS a self benchmark score
  - cross_trait: the trait whose PRS models are recommended for the target_trait
    (cross-trait PRS output)

Selection criterion:
  Type A (no self score): require at least one non-self PGS model with known source ontology.
  Type B (has self score): require cross AUC > best self AUC.
  When self AUC exists: require (cross AUC - self best AUC) > 0.025 for retained cross models.
  The top retained cross model must also have AUC > 0.55.
  Target traits with self best AUC > 0.60 are excluded (self PRS already strong).

  Target traits here are restricted to the same set as Contribution2 main analysis:
  ICD root rows with include_in_analysis == 1 in
  `contribution1/result/aou_icd_260217/prs_adjauc_metadata_260217_rootcode.csv`
  (case_count >= 200 in Contribution1 QC).

PGS models with unknown source ontology are excluded (cannot build disease-level mapping).

Outputs generated here:
  - binary -> binary cross list (existing disease-to-disease transfer)
  - binary -> continuous cross list (new disease-to-measurement transfer)

Cross-list workflow (see report): partition screened inputs into Type A/Type B by
self-score availability, retain qualifying cross-list target traits, then map cross
traits and perform Cross-Trait Transfer.

Usage:
  python build_cross_list.py
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
CROSS_LIST_DIR = SCRIPT_DIR.parent
RUNS_DIR = CROSS_LIST_DIR / "runs"
BINARY_TO_BINARY_RUNS_DIR = RUNS_DIR / "binary_to_binary"
BINARY_TO_CONTINUOUS_RUNS_DIR = RUNS_DIR / "binary_to_continuous"
CONTINUOUS_TO_BINARY_RUNS_DIR = RUNS_DIR / "continuous_to_binary"
CONTINUOUS_TO_CONTINUOUS_RUNS_DIR = RUNS_DIR / "continuous_to_continuous"

# Primary binary (disease) AoU adjAUC matrices from the current Contribution1
# ICD snapshot.
CONTRIB1_RESULT_DIR = (
    CROSS_LIST_DIR.parent.parent
    / "contribution1"
    / "result"
    / "aou_icd_260217"
)
CONTRIB1_ROOTCODE_ADJ_AUC_MATRIX_NAME = "prs_adjauc_matrix_260217_rootcode.csv"
CONTRIB1_ROOTCODE_ADJ_AUC_METADATA_NAME = "prs_adjauc_metadata_260217_rootcode.csv"
CONTRIB1_LOINC_RESULT_DIR = (
    CROSS_LIST_DIR.parent.parent
    / "contribution1"
    / "result"
    / "aou_loinc_260225"
)
CONTRIB1_PREPROCESS_DIR = (
    CROSS_LIST_DIR.parent.parent
    / "contribution1"
    / "disease_preprocess"
)
# Type A: skip targets where best self AUC is already above this (cross-transfer not prioritized)
TYPE_A_MAX_SELF_BEST_AUC = 0.60

# Type A: when self AUC exists, keep only cross models with improvement above this margin
TYPE_A_MIN_IMPROVEMENT = 0.025

# AUC-based Type A: require the retained cross model itself to be strong enough.
TYPE_A_MIN_TOP_CROSS_AUC = 0.55

# Continuous-input Type A: skip targets where self incremental R2 is already strong
CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2 = 0.05

# Continuous-input Type A: keep only disease donors with meaningful incremental-R2 gain
CONTINUOUS_TYPE_A_MIN_IMPROVEMENT = 0.0025

# Incremental-R2-based Type A: require the retained cross model to clear a
# minimal absolute predictive signal threshold.
CONTINUOUS_TYPE_A_MIN_TOP_CROSS_INCREMENTAL_R2 = 0.02


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_icd_description(desc: str) -> str:
    desc = str(desc).strip()
    return re.sub(r"^[01]\s+", "", desc, count=1)


def _parse_pgs_ids(pgs_str: str) -> list[str]:
    try:
        out = ast.literal_eval(pgs_str)
        return list(out) if isinstance(out, (list, tuple)) else [out]
    except (ValueError, SyntaxError):
        return []


def _col_to_pgs_id(col: str) -> str:
    col = str(col).strip()
    if "__" in col:
        return col.rsplit("__", 1)[-1]
    return col.replace("_hmPOS_GRCh38", "")


def _pgs_id_to_col(pgs_id: str) -> str:
    return f"{pgs_id}_hmPOS_GRCh38"


def _input_type_from_has_self(has_self_score: bool) -> str:
    return "B" if has_self_score else "A"


def _display_or_dash(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and pd.isna(value):
        return "-"
    text = str(value).strip()
    return text if text and text.lower() != "nan" else "-"


def _display_positive_count_or_dash(value: object) -> str:
    try:
        count = int(value)
    except (TypeError, ValueError):
        return "-"
    return str(count) if count > 0 else "-"


def load_rootcode_auc_matrix() -> pd.DataFrame:
    matrix_path = CONTRIB1_RESULT_DIR / CONTRIB1_ROOTCODE_ADJ_AUC_MATRIX_NAME
    if not matrix_path.exists():
        raise FileNotFoundError(f"Matrix not found: {matrix_path}")
    return pd.read_csv(matrix_path, index_col=0)


def load_loinc_incremental_r2_matrix() -> pd.DataFrame:
    matrix_path = CONTRIB1_LOINC_RESULT_DIR / "prs_incrementalr2_matrix_260225_loinccode.csv"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Matrix not found: {matrix_path}")
    return pd.read_csv(matrix_path, index_col=0)


def build_pgs_to_ontology_map_full() -> dict[str, set[str]]:
    """Build PGS_ID -> set of source ontology names from the FULL pgs_id_list
    (221 ontologies, not the QC-filtered adjauc_metadata)."""
    pgs_id_list_path = CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv"
    pgs_id_list = pd.read_csv(pgs_id_list_path)

    pgs_to_ont: dict[str, set[str]] = {}
    for _, row in pgs_id_list.iterrows():
        ontology = str(row["ontology"]).strip()
        pgs_ids = _parse_pgs_ids(str(row["pgs_ids"]))
        for pid in pgs_ids:
            if pid not in pgs_to_ont:
                pgs_to_ont[pid] = set()
            pgs_to_ont[pid].add(ontology)
    return pgs_to_ont


def build_pgs_to_continuous_trait_map() -> dict[str, list[dict[str, str]]]:
    """
    Map PGS_ID -> continuous trait metadata from the LOINC incremental R2 output.

    The metadata file is used only as a trait mapping / QC filter:
    the transfer score itself still comes from the disease AUC matrix.
    """
    meta_path = CONTRIB1_LOINC_RESULT_DIR / "prs_incrementalr2_metadata_260225_loinccode.csv"
    if not meta_path.exists():
        raise FileNotFoundError(f"Continuous metadata not found: {meta_path}")

    meta = pd.read_csv(meta_path)
    include = pd.to_numeric(meta["include_in_analysis"], errors="coerce").fillna(0).astype(int) == 1

    out: dict[str, list[dict[str, str]]] = {}
    seen: set[tuple[str, str, str, str]] = set()
    for _, row in meta.loc[include].iterrows():
        loinc = str(row["loinc"]).strip()
        ontology = str(row["ontology"]).strip()
        description = _clean_icd_description(row.get("description", ""))
        for pid in _parse_pgs_ids(str(row["pgs_ids"])):
            key = (pid, loinc, ontology, description)
            if key in seen:
                continue
            seen.add(key)
            out.setdefault(pid, []).append({
                "output_loinc": loinc,
                "output_ontology": ontology,
                "output_description": description,
            })

    for traits in out.values():
        traits.sort(key=lambda t: (t["output_ontology"], t["output_loinc"]))

    return out


def build_loinc_trait_map_full() -> dict[str, dict[str, str]]:
    """Build LOINC code -> ontology/description from the full LOINC metadata."""
    meta_path = CONTRIB1_LOINC_RESULT_DIR / "prs_incrementalr2_metadata_260225_loinccode.csv"
    if not meta_path.exists():
        raise FileNotFoundError(f"Continuous metadata not found: {meta_path}")

    meta = pd.read_csv(meta_path)
    out: dict[str, dict[str, str]] = {}
    for _, row in meta.iterrows():
        loinc = str(row["loinc"]).strip()
        if loinc in out:
            continue
        out[loinc] = {
            "input_ontology": str(row["ontology"]).strip(),
            "input_description": _clean_icd_description(row.get("description", "")),
        }
    return out


def build_loinc_to_self_pgs_full() -> dict[str, set[str]]:
    """Build LOINC code -> set of self PGS IDs from the full LOINC metadata."""
    meta_path = CONTRIB1_LOINC_RESULT_DIR / "prs_incrementalr2_metadata_260225_loinccode.csv"
    if not meta_path.exists():
        raise FileNotFoundError(f"Continuous metadata not found: {meta_path}")

    meta = pd.read_csv(meta_path)
    out: dict[str, set[str]] = {}
    for _, row in meta.iterrows():
        loinc = str(row["loinc"]).strip()
        out.setdefault(loinc, set()).update(_parse_pgs_ids(str(row["pgs_ids"])))
    return out


def build_pgs_to_binary_trait_map() -> dict[str, list[dict[str, str]]]:
    """Map PGS_ID -> binary disease metadata from the full rootcode disease list."""
    pgs_id_list_path = CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv"
    if not pgs_id_list_path.exists():
        raise FileNotFoundError(f"Disease metadata not found: {pgs_id_list_path}")

    pgs_id_list = pd.read_csv(pgs_id_list_path)
    out: dict[str, list[dict[str, str]]] = {}
    seen: set[tuple[str, str, str, str]] = set()
    for _, row in pgs_id_list.iterrows():
        output_icd = str(row["icd_root"]).strip()
        output_ontology = str(row["ontology"]).strip()
        output_description = _clean_icd_description(row.get("description", ""))
        for pid in _parse_pgs_ids(str(row["pgs_ids"])):
            key = (pid, output_icd, output_ontology, output_description)
            if key in seen:
                continue
            seen.add(key)
            out.setdefault(pid, []).append({
                "output_icd": output_icd,
                "output_ontology": output_ontology,
                "output_description": output_description,
            })

    for traits in out.values():
        traits.sort(key=lambda t: (t["output_ontology"], t["output_icd"]))

    return out


def build_icd_to_ontologies_full() -> dict[str, list[str]]:
    """Build root ICD code -> list of ontology names from the FULL pgs_id_list."""
    pgs_id_list = pd.read_csv(CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv")

    icd_to_ont: dict[str, list[str]] = {}
    for _, row in pgs_id_list.iterrows():
        icd = str(row["icd_root"]).strip()
        ont = str(row["ontology"]).strip()
        if icd not in icd_to_ont:
            icd_to_ont[icd] = []
        if ont not in icd_to_ont[icd]:
            icd_to_ont[icd].append(ont)
    return icd_to_ont


def build_icd_to_self_pgs_full() -> dict[str, set[str]]:
    """Build root ICD code -> set of self PGS IDs from the FULL pgs_id_list."""
    pgs_id_list = pd.read_csv(CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv")

    icd_to_pgs: dict[str, set[str]] = {}
    for _, row in pgs_id_list.iterrows():
        icd = str(row["icd_root"]).strip()
        pgs_ids = _parse_pgs_ids(str(row["pgs_ids"]))
        if icd not in icd_to_pgs:
            icd_to_pgs[icd] = set()
        icd_to_pgs[icd].update(pgs_ids)
    return icd_to_pgs


def get_icd_description_map_full() -> dict[str, str]:
    """Build root ICD code -> description from the FULL pgs_id_list."""
    pgs_id_list = pd.read_csv(CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv")

    desc_map: dict[str, str] = {}
    for _, row in pgs_id_list.iterrows():
        icd = str(row["icd_root"]).strip()
        desc = _clean_icd_description(row.get("description", ""))
        if icd not in desc_map and desc:
            desc_map[icd] = desc
    return desc_map


def build_pgs_ontology_to_icd_map() -> dict[tuple[str, str], str]:
    """
    Map (PGS_ID, ontology name) -> root ICD code.
    """
    pgs_id_list = pd.read_csv(CONTRIB1_PREPROCESS_DIR / "pgs_id_list_260217.csv")
    out: dict[tuple[str, str], str] = {}
    for _, row in pgs_id_list.iterrows():
        ontology = str(row["ontology"]).strip()
        icd = str(row["icd_root"]).strip()
        for pid in _parse_pgs_ids(str(row["pgs_ids"])):
            out[(pid, ontology)] = icd
    return out


def format_top_output_icd(
    top_cross_pgs: Optional[str],
    top_output_disease: Optional[str],
    pgs_ontology_to_icd: dict[tuple[str, str], str],
) -> str:
    """ICD string(s) for the top cross PGS, aligned with top_output_disease ontologies."""
    if not top_cross_pgs or not top_output_disease:
        return ""
    parts: list[str] = []
    seen: set[str] = set()
    for ont in str(top_output_disease).split("; "):
        ont = ont.strip()
        if not ont:
            continue
        icd = pgs_ontology_to_icd.get((top_cross_pgs, ont))
        if icd and icd not in seen:
            seen.add(icd)
            parts.append(icd)
    return "; ".join(parts)


def load_main_analysis_input_icds() -> set[str]:
    """
    ICD codes eligible for Type A (same as C2 / C1 primary analysis).

    Uses prs_adjauc_metadata include_in_analysis == 1 (AoU case_count >= 200 QC).
    """
    meta_path = CONTRIB1_RESULT_DIR / CONTRIB1_ROOTCODE_ADJ_AUC_METADATA_NAME
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata not found: {meta_path}")

    meta = pd.read_csv(meta_path)
    inc = meta["include_in_analysis"]
    if inc.dtype == bool:
        mask = inc
    else:
        mask = pd.to_numeric(inc, errors="coerce").fillna(0).astype(int) == 1

    return set(meta.loc[mask, "icd_root"].astype(str).str.strip())


def load_main_analysis_input_loincs() -> set[str]:
    """
    LOINC traits eligible for continuous-input Type A.

    Uses prs_incrementalr2_metadata include_in_analysis == 1.
    """
    meta_path = CONTRIB1_LOINC_RESULT_DIR / "prs_incrementalr2_metadata_260225_loinccode.csv"
    if not meta_path.exists():
        raise FileNotFoundError(f"Continuous metadata not found: {meta_path}")

    meta = pd.read_csv(meta_path)
    inc = meta["include_in_analysis"]
    if inc.dtype == bool:
        mask = inc
    else:
        mask = pd.to_numeric(inc, errors="coerce").fillna(0).astype(int) == 1

    return set(meta.loc[mask, "loinc"].astype(str).str.strip())


def _get_self_auc_info(
    auc_row: pd.Series,
    self_pgs_ids: set[str],
) -> tuple[Optional[float], Optional[str]]:
    self_best_auc = None
    self_best_pgs = None
    self_aucs: dict[str, float] = {}
    for pid in self_pgs_ids:
        col = _pgs_id_to_col(pid)
        if col in auc_row.index:
            val = auc_row[col]
            if pd.notna(val) and isinstance(val, (int, float)):
                self_aucs[pid] = float(val)
    if self_aucs:
        self_best_pgs = max(self_aucs, key=self_aucs.get)
        self_best_auc = self_aucs[self_best_pgs]
    return self_best_auc, self_best_pgs


# ---------------------------------------------------------------------------
# Benchmarked binary inputs in the C1 AUC matrix
# ---------------------------------------------------------------------------

def build_type_a_cross_list(
    matrix: pd.DataFrame,
    allowed_input_icds: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build cross list for benchmarked binary target traits.

    For each binary target trait, find non-self PGS models (with KNOWN source ontology)
    that have AUC > self best AUC, and trace them to their mapped cross trait.
    """
    n_matrix_traits = len(matrix.index)
    n_skipped = sum(1 for t in matrix.index if str(t).strip() not in allowed_input_icds)

    # Use FULL pgs_id_list for mappings (221 ontologies, not QC-filtered metadata)
    pgs_to_ontology = build_pgs_to_ontology_map_full()
    icd_to_self_pgs = build_icd_to_self_pgs_full()
    icd_to_ontologies = build_icd_to_ontologies_full()
    icd_desc_map = get_icd_description_map_full()
    pgs_ontology_to_icd = build_pgs_ontology_to_icd_map()

    # Set of all PGS IDs with known source ontology
    known_pgs_ids = set(pgs_to_ontology.keys())

    pgs_columns = list(matrix.columns)

    rows = []
    summary_rows = []
    n_skipped_high_self = 0

    for input_icd in matrix.index:
        input_icd = str(input_icd).strip()
        if input_icd not in allowed_input_icds:
            continue

        input_ontologies = icd_to_ontologies.get(input_icd, [])
        input_ontology_str = "; ".join(sorted(input_ontologies)) if input_ontologies else ""
        input_desc = icd_desc_map.get(input_icd, "")

        self_pgs_ids = icd_to_self_pgs.get(input_icd, set())

        auc_row = matrix.loc[input_icd]

        self_best_auc, self_best_pgs = _get_self_auc_info(auc_row, self_pgs_ids)

        has_self_auc = self_best_auc is not None

        if (
            has_self_auc
            and self_best_auc is not None
            and self_best_auc > TYPE_A_MAX_SELF_BEST_AUC
        ):
            n_skipped_high_self += 1
            continue

        # Find cross-disease models (only those with known source ontology)
        cross_models = []
        for col in pgs_columns:
            pgs_id = _col_to_pgs_id(col)

            # Skip self models
            if pgs_id in self_pgs_ids:
                continue

            # Skip unknown source (cannot build disease-level mapping)
            if pgs_id not in known_pgs_ids:
                continue

            val = auc_row[col]
            if not (pd.notna(val) and isinstance(val, (int, float))):
                continue
            cross_auc = float(val)

            # Apply criterion: cross AUC > self best AUC (only if has self)
            if has_self_auc and cross_auc <= self_best_auc:
                continue

            # Determine output_disease ontology
            output_ontologies = pgs_to_ontology.get(pgs_id, set())
            # Exclude ontologies that are also input (self-alias)
            output_ontologies_filtered = output_ontologies - set(input_ontologies)

            if not output_ontologies_filtered:
                continue  # effectively a self model

            output_ontology_str = "; ".join(sorted(output_ontologies_filtered))

            cross_models.append({
                "output_pgs_id": pgs_id,
                "output_disease": output_ontology_str,
                "cross_auc": round(cross_auc, 6),
            })

        cross_models.sort(key=lambda x: x["cross_auc"], reverse=True)
        raw_cross_models = list(cross_models)

        if has_self_auc and self_best_auc is not None:
            cross_models = [
                cm for cm in cross_models
                if (cm["cross_auc"] - self_best_auc) > TYPE_A_MIN_IMPROVEMENT
            ]
        if cross_models and cross_models[0]["cross_auc"] <= TYPE_A_MIN_TOP_CROSS_AUC:
            cross_models = []

        # Detail rows
        for cm in cross_models:
            auc_improvement = None
            if self_best_auc is not None:
                auc_improvement = round(cm["cross_auc"] - self_best_auc, 6)

            rows.append({
                "input_type": _input_type_from_has_self(has_self_auc),
                "input_icd": input_icd,
                "input_ontology": input_ontology_str,
                "input_description": input_desc,
                "has_self_auc": has_self_auc,
                "self_n_models": len(self_pgs_ids),
                "self_best_auc": round(self_best_auc, 6) if self_best_auc is not None else None,
                "self_best_pgs": self_best_pgs,
                "output_pgs_id": cm["output_pgs_id"],
                "output_disease": cm["output_disease"],
                "cross_auc": cm["cross_auc"],
                "auc_improvement": auc_improvement,
            })

        # Summary row
        n_cross = len(cross_models)
        top_cross_auc = cross_models[0]["cross_auc"] if cross_models else None
        top_cross_pgs = cross_models[0]["output_pgs_id"] if cross_models else None
        top_output_disease = cross_models[0]["output_disease"] if cross_models else None
        raw_n_cross = len(raw_cross_models)
        raw_top_cross_auc = raw_cross_models[0]["cross_auc"] if raw_cross_models else None
        raw_top_cross_pgs = raw_cross_models[0]["output_pgs_id"] if raw_cross_models else None
        raw_top_output_disease = raw_cross_models[0]["output_disease"] if raw_cross_models else None

        unique_output_diseases = set()
        for cm in cross_models:
            for ont in cm["output_disease"].split("; "):
                unique_output_diseases.add(ont)

        summary_rows.append({
            "input_type": _input_type_from_has_self(has_self_auc),
            "input_icd": input_icd,
            "input_ontology": input_ontology_str,
            "input_description": input_desc,
            "has_self_auc": has_self_auc,
            "self_n_models": len(self_pgs_ids),
            "self_best_auc": round(self_best_auc, 6) if self_best_auc is not None else None,
            "n_cross_models_beating_self": n_cross,
            "raw_n_cross_models": raw_n_cross,
            "n_unique_output_diseases": len(unique_output_diseases),
            "top_cross_auc": top_cross_auc,
            "top_cross_pgs": top_cross_pgs,
            "top_output_icd": format_top_output_icd(
                top_cross_pgs, top_output_disease, pgs_ontology_to_icd
            ),
            "top_output_disease": top_output_disease,
            "raw_top_cross_auc": raw_top_cross_auc,
            "raw_top_output_icd": format_top_output_icd(
                raw_top_cross_pgs, raw_top_output_disease, pgs_ontology_to_icd
            ),
            "raw_top_output_disease": raw_top_output_disease,
            "top_auc_improvement": (
                round(top_cross_auc - self_best_auc, 6)
                if top_cross_auc is not None and self_best_auc is not None
                else None
            ),
        })

    print(
        f"  Main analysis filter (rootcode): {len(allowed_input_icds)} ICDs in metadata "
        f"(include_in_analysis==1); matrix rows={n_matrix_traits}, skipped={n_skipped}, "
        f"skipped self_best>{TYPE_A_MAX_SELF_BEST_AUC}={n_skipped_high_self}, "
        f"processed={len(summary_rows)}"
    )

    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


def build_type_a_binary_to_continuous_cross_list(
    matrix: pd.DataFrame,
    allowed_input_icds: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build Type A cross list for binary disease inputs with continuous trait outputs.

    Uses the disease AUC matrix for scoring and the LOINC incremental-R2 metadata
    only to resolve PGS -> continuous trait mappings.
    """
    n_matrix_traits = len(matrix.index)
    n_skipped = sum(1 for t in matrix.index if str(t).strip() not in allowed_input_icds)

    icd_to_self_pgs = build_icd_to_self_pgs_full()
    icd_to_ontologies = build_icd_to_ontologies_full()
    icd_desc_map = get_icd_description_map_full()
    pgs_to_continuous_trait = build_pgs_to_continuous_trait_map()

    continuous_pgs_ids = set(pgs_to_continuous_trait.keys())
    continuous_trait_count = len({
        trait["output_loinc"]
        for traits in pgs_to_continuous_trait.values()
        for trait in traits
    })

    pgs_columns = list(matrix.columns)

    rows = []
    summary_rows = []
    n_skipped_high_self = 0

    for input_icd in matrix.index:
        input_icd = str(input_icd).strip()
        if input_icd not in allowed_input_icds:
            continue

        input_ontologies = icd_to_ontologies.get(input_icd, [])
        input_ontology_str = "; ".join(sorted(input_ontologies)) if input_ontologies else ""
        input_desc = icd_desc_map.get(input_icd, "")

        self_pgs_ids = icd_to_self_pgs.get(input_icd, set())
        auc_row = matrix.loc[input_icd]
        self_best_auc, self_best_pgs = _get_self_auc_info(auc_row, self_pgs_ids)
        has_self_auc = self_best_auc is not None

        if (
            has_self_auc
            and self_best_auc is not None
            and self_best_auc > TYPE_A_MAX_SELF_BEST_AUC
        ):
            n_skipped_high_self += 1
            continue

        cross_models = []
        for col in pgs_columns:
            pgs_id = _col_to_pgs_id(col)

            if pgs_id in self_pgs_ids:
                continue
            if pgs_id not in continuous_pgs_ids:
                continue

            val = auc_row[col]
            if not (pd.notna(val) and isinstance(val, (int, float))):
                continue
            cross_auc = float(val)

            if has_self_auc and cross_auc <= self_best_auc:
                continue

            for trait in pgs_to_continuous_trait[pgs_id]:
                cross_models.append({
                    "output_pgs_id": pgs_id,
                    "output_loinc": trait["output_loinc"],
                    "output_ontology": trait["output_ontology"],
                    "output_description": trait["output_description"],
                    "cross_auc": round(cross_auc, 6),
                })

        cross_models.sort(
            key=lambda x: (
                -x["cross_auc"],
                x["output_ontology"],
                x["output_loinc"],
                x["output_pgs_id"],
            )
        )
        raw_cross_models = list(cross_models)

        if has_self_auc and self_best_auc is not None:
            cross_models = [
                cm for cm in cross_models
                if (cm["cross_auc"] - self_best_auc) > TYPE_A_MIN_IMPROVEMENT
            ]
        if cross_models and cross_models[0]["cross_auc"] <= TYPE_A_MIN_TOP_CROSS_AUC:
            cross_models = []

        for cm in cross_models:
            auc_improvement = None
            if self_best_auc is not None:
                auc_improvement = round(cm["cross_auc"] - self_best_auc, 6)

            rows.append({
                "input_type": _input_type_from_has_self(has_self_auc),
                "input_icd": input_icd,
                "input_ontology": input_ontology_str,
                "input_description": input_desc,
                "has_self_auc": has_self_auc,
                "self_n_models": len(self_pgs_ids),
                "self_best_auc": round(self_best_auc, 6) if self_best_auc is not None else None,
                "self_best_pgs": self_best_pgs,
                "output_pgs_id": cm["output_pgs_id"],
                "output_loinc": cm["output_loinc"],
                "output_ontology": cm["output_ontology"],
                "output_description": cm["output_description"],
                "cross_auc": cm["cross_auc"],
                "auc_improvement": auc_improvement,
            })

        n_cross = len(cross_models)
        top_cross_auc = cross_models[0]["cross_auc"] if cross_models else None
        top_cross_pgs = cross_models[0]["output_pgs_id"] if cross_models else None
        top_output_loinc = cross_models[0]["output_loinc"] if cross_models else None
        top_output_ontology = cross_models[0]["output_ontology"] if cross_models else None
        top_output_description = cross_models[0]["output_description"] if cross_models else None
        raw_n_cross = len(raw_cross_models)
        raw_top_cross_auc = raw_cross_models[0]["cross_auc"] if raw_cross_models else None
        raw_top_cross_pgs = raw_cross_models[0]["output_pgs_id"] if raw_cross_models else None
        raw_top_output_loinc = raw_cross_models[0]["output_loinc"] if raw_cross_models else None
        raw_top_output_ontology = raw_cross_models[0]["output_ontology"] if raw_cross_models else None
        raw_top_output_description = (
            raw_cross_models[0]["output_description"] if raw_cross_models else None
        )
        unique_output_traits = {cm["output_loinc"] for cm in cross_models}

        summary_rows.append({
            "input_type": _input_type_from_has_self(has_self_auc),
            "input_icd": input_icd,
            "input_ontology": input_ontology_str,
            "input_description": input_desc,
            "has_self_auc": has_self_auc,
            "self_n_models": len(self_pgs_ids),
            "self_best_auc": round(self_best_auc, 6) if self_best_auc is not None else None,
            "n_cross_models_beating_self": n_cross,
            "raw_n_cross_models": raw_n_cross,
            "n_unique_output_traits": len(unique_output_traits),
            "top_cross_auc": top_cross_auc,
            "top_cross_pgs": top_cross_pgs,
            "top_output_loinc": top_output_loinc,
            "top_output_ontology": top_output_ontology,
            "top_output_description": top_output_description,
            "raw_top_cross_auc": raw_top_cross_auc,
            "raw_top_cross_pgs": raw_top_cross_pgs,
            "raw_top_output_loinc": raw_top_output_loinc,
            "raw_top_output_ontology": raw_top_output_ontology,
            "raw_top_output_description": raw_top_output_description,
            "top_auc_improvement": (
                round(top_cross_auc - self_best_auc, 6)
                if top_cross_auc is not None and self_best_auc is not None
                else None
            ),
        })

    print(
        f"  Continuous donor filter: {continuous_trait_count} LOINC traits in metadata; "
        f"matrix rows={n_matrix_traits}, skipped={n_skipped}, "
        f"skipped self_best>{TYPE_A_MAX_SELF_BEST_AUC}={n_skipped_high_self}, "
        f"processed={len(summary_rows)}"
    )

    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


def build_type_a_continuous_to_binary_cross_list(
    matrix: pd.DataFrame,
    allowed_input_loincs: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build Type A cross list for continuous trait inputs with binary disease outputs.

    Uses the LOINC incremental-R2 matrix for scoring and the rootcode disease
    metadata only to resolve PGS -> binary disease mappings.
    """
    n_matrix_traits = len(matrix.index)
    n_skipped = sum(1 for t in matrix.index if str(t).strip() not in allowed_input_loincs)

    loinc_trait_map = build_loinc_trait_map_full()
    loinc_to_self_pgs = build_loinc_to_self_pgs_full()
    pgs_to_binary_trait = build_pgs_to_binary_trait_map()

    binary_pgs_ids = set(pgs_to_binary_trait.keys())
    binary_trait_count = len({
        (trait["output_icd"], trait["output_ontology"])
        for traits in pgs_to_binary_trait.values()
        for trait in traits
    })

    pgs_columns = list(matrix.columns)

    rows = []
    summary_rows = []
    n_skipped_high_self = 0

    for input_loinc in matrix.index:
        input_loinc = str(input_loinc).strip()
        if input_loinc not in allowed_input_loincs:
            continue

        input_trait = loinc_trait_map.get(input_loinc, {})
        input_ontology = input_trait.get("input_ontology", "")
        input_description = input_trait.get("input_description", "")

        self_pgs_ids = loinc_to_self_pgs.get(input_loinc, set())
        score_row = matrix.loc[input_loinc]
        self_best_score, self_best_pgs = _get_self_auc_info(score_row, self_pgs_ids)
        has_self_score = self_best_score is not None

        if (
            has_self_score
            and self_best_score is not None
            and self_best_score > CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2
        ):
            n_skipped_high_self += 1
            continue

        cross_models = []
        for col in pgs_columns:
            pgs_id = _col_to_pgs_id(col)

            if pgs_id in self_pgs_ids:
                continue
            if pgs_id not in binary_pgs_ids:
                continue

            val = score_row[col]
            if not (pd.notna(val) and isinstance(val, (int, float))):
                continue
            cross_score = float(val)

            if has_self_score and cross_score <= self_best_score:
                continue

            for trait in pgs_to_binary_trait[pgs_id]:
                cross_models.append({
                    "output_pgs_id": pgs_id,
                    "output_icd": trait["output_icd"],
                    "output_ontology": trait["output_ontology"],
                    "output_description": trait["output_description"],
                    "cross_incremental_r2": round(cross_score, 6),
                })

        cross_models.sort(
            key=lambda x: (
                -x["cross_incremental_r2"],
                x["output_ontology"],
                x["output_icd"],
                x["output_pgs_id"],
            )
        )
        raw_cross_models = list(cross_models)

        if has_self_score and self_best_score is not None:
            cross_models = [
                cm for cm in cross_models
                if (cm["cross_incremental_r2"] - self_best_score)
                > CONTINUOUS_TYPE_A_MIN_IMPROVEMENT
            ]
        if (
            cross_models
            and cross_models[0]["cross_incremental_r2"]
            <= CONTINUOUS_TYPE_A_MIN_TOP_CROSS_INCREMENTAL_R2
        ):
            cross_models = []

        for cm in cross_models:
            score_improvement = None
            if self_best_score is not None:
                score_improvement = round(
                    cm["cross_incremental_r2"] - self_best_score,
                    6,
                )

            rows.append({
                "input_type": _input_type_from_has_self(has_self_score),
                "input_loinc": input_loinc,
                "input_ontology": input_ontology,
                "input_description": input_description,
                "has_self_incremental_r2": has_self_score,
                "self_n_models": len(self_pgs_ids),
                "self_best_incremental_r2": (
                    round(self_best_score, 6) if self_best_score is not None else None
                ),
                "self_best_pgs": self_best_pgs,
                "output_pgs_id": cm["output_pgs_id"],
                "output_icd": cm["output_icd"],
                "output_ontology": cm["output_ontology"],
                "output_description": cm["output_description"],
                "cross_incremental_r2": cm["cross_incremental_r2"],
                "incremental_r2_improvement": score_improvement,
            })

        n_cross = len(cross_models)
        top_cross_score = (
            cross_models[0]["cross_incremental_r2"] if cross_models else None
        )
        top_cross_pgs = cross_models[0]["output_pgs_id"] if cross_models else None
        top_output_icd = cross_models[0]["output_icd"] if cross_models else None
        top_output_ontology = (
            cross_models[0]["output_ontology"] if cross_models else None
        )
        top_output_description = (
            cross_models[0]["output_description"] if cross_models else None
        )
        raw_n_cross = len(raw_cross_models)
        raw_top_cross_score = (
            raw_cross_models[0]["cross_incremental_r2"] if raw_cross_models else None
        )
        raw_top_cross_pgs = (
            raw_cross_models[0]["output_pgs_id"] if raw_cross_models else None
        )
        raw_top_output_icd = raw_cross_models[0]["output_icd"] if raw_cross_models else None
        raw_top_output_ontology = (
            raw_cross_models[0]["output_ontology"] if raw_cross_models else None
        )
        raw_top_output_description = (
            raw_cross_models[0]["output_description"] if raw_cross_models else None
        )
        unique_output_diseases = {
            (cm["output_icd"], cm["output_ontology"]) for cm in cross_models
        }

        summary_rows.append({
            "input_type": _input_type_from_has_self(has_self_score),
            "input_loinc": input_loinc,
            "input_ontology": input_ontology,
            "input_description": input_description,
            "has_self_incremental_r2": has_self_score,
            "self_n_models": len(self_pgs_ids),
            "self_best_incremental_r2": (
                round(self_best_score, 6) if self_best_score is not None else None
            ),
            "n_cross_models_beating_self": n_cross,
            "raw_n_cross_models": raw_n_cross,
            "n_unique_output_diseases": len(unique_output_diseases),
            "top_cross_incremental_r2": top_cross_score,
            "top_cross_pgs": top_cross_pgs,
            "top_output_icd": top_output_icd,
            "top_output_disease": top_output_ontology,
            "top_output_description": top_output_description,
            "raw_top_cross_incremental_r2": raw_top_cross_score,
            "raw_top_cross_pgs": raw_top_cross_pgs,
            "raw_top_output_icd": raw_top_output_icd,
            "raw_top_output_disease": raw_top_output_ontology,
            "raw_top_output_description": raw_top_output_description,
            "top_incremental_r2_improvement": (
                round(top_cross_score - self_best_score, 6)
                if top_cross_score is not None and self_best_score is not None
                else None
            ),
        })

    print(
        f"  Binary donor filter: {binary_trait_count} rootcode diseases in metadata; "
        f"matrix rows={n_matrix_traits}, skipped={n_skipped}, "
        f"skipped self_best>{CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2}={n_skipped_high_self}, "
        f"processed={len(summary_rows)}"
    )

    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


def build_type_a_continuous_to_continuous_cross_list(
    matrix: pd.DataFrame,
    allowed_input_loincs: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build Type A cross list for continuous trait inputs with continuous trait outputs.

    Uses the LOINC incremental-R2 matrix for scoring and LOINC metadata to resolve
    PGS -> continuous trait mappings.
    """
    n_matrix_traits = len(matrix.index)
    n_skipped = sum(1 for t in matrix.index if str(t).strip() not in allowed_input_loincs)

    loinc_trait_map = build_loinc_trait_map_full()
    loinc_to_self_pgs = build_loinc_to_self_pgs_full()
    pgs_to_continuous_trait = build_pgs_to_continuous_trait_map()

    continuous_pgs_ids = set(pgs_to_continuous_trait.keys())
    continuous_trait_count = len({
        trait["output_loinc"]
        for traits in pgs_to_continuous_trait.values()
        for trait in traits
    })

    pgs_columns = list(matrix.columns)

    rows = []
    summary_rows = []
    n_skipped_high_self = 0

    for input_loinc in matrix.index:
        input_loinc = str(input_loinc).strip()
        if input_loinc not in allowed_input_loincs:
            continue

        input_trait = loinc_trait_map.get(input_loinc, {})
        input_ontology = input_trait.get("input_ontology", "")
        input_description = input_trait.get("input_description", "")

        self_pgs_ids = loinc_to_self_pgs.get(input_loinc, set())
        score_row = matrix.loc[input_loinc]
        self_best_score, self_best_pgs = _get_self_auc_info(score_row, self_pgs_ids)
        has_self_score = self_best_score is not None

        if (
            has_self_score
            and self_best_score is not None
            and self_best_score > CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2
        ):
            n_skipped_high_self += 1
            continue

        cross_models = []
        for col in pgs_columns:
            pgs_id = _col_to_pgs_id(col)

            if pgs_id in self_pgs_ids:
                continue
            if pgs_id not in continuous_pgs_ids:
                continue

            val = score_row[col]
            if not (pd.notna(val) and isinstance(val, (int, float))):
                continue
            cross_score = float(val)

            if has_self_score and cross_score <= self_best_score:
                continue

            for trait in pgs_to_continuous_trait[pgs_id]:
                if trait["output_loinc"] == input_loinc:
                    continue
                cross_models.append({
                    "output_pgs_id": pgs_id,
                    "output_loinc": trait["output_loinc"],
                    "output_ontology": trait["output_ontology"],
                    "output_description": trait["output_description"],
                    "cross_incremental_r2": round(cross_score, 6),
                })

        cross_models.sort(
            key=lambda x: (
                -x["cross_incremental_r2"],
                x["output_ontology"],
                x["output_loinc"],
                x["output_pgs_id"],
            )
        )
        raw_cross_models = list(cross_models)

        if has_self_score and self_best_score is not None:
            cross_models = [
                cm for cm in cross_models
                if (cm["cross_incremental_r2"] - self_best_score)
                > CONTINUOUS_TYPE_A_MIN_IMPROVEMENT
            ]
        if (
            cross_models
            and cross_models[0]["cross_incremental_r2"]
            <= CONTINUOUS_TYPE_A_MIN_TOP_CROSS_INCREMENTAL_R2
        ):
            cross_models = []

        for cm in cross_models:
            score_improvement = None
            if self_best_score is not None:
                score_improvement = round(
                    cm["cross_incremental_r2"] - self_best_score,
                    6,
                )

            rows.append({
                "input_type": _input_type_from_has_self(has_self_score),
                "input_loinc": input_loinc,
                "input_ontology": input_ontology,
                "input_description": input_description,
                "has_self_incremental_r2": has_self_score,
                "self_n_models": len(self_pgs_ids),
                "self_best_incremental_r2": (
                    round(self_best_score, 6) if self_best_score is not None else None
                ),
                "self_best_pgs": self_best_pgs,
                "output_pgs_id": cm["output_pgs_id"],
                "output_loinc": cm["output_loinc"],
                "output_ontology": cm["output_ontology"],
                "output_description": cm["output_description"],
                "cross_incremental_r2": cm["cross_incremental_r2"],
                "incremental_r2_improvement": score_improvement,
            })

        n_cross = len(cross_models)
        top_cross_score = (
            cross_models[0]["cross_incremental_r2"] if cross_models else None
        )
        top_cross_pgs = cross_models[0]["output_pgs_id"] if cross_models else None
        top_output_loinc = cross_models[0]["output_loinc"] if cross_models else None
        top_output_ontology = (
            cross_models[0]["output_ontology"] if cross_models else None
        )
        top_output_description = (
            cross_models[0]["output_description"] if cross_models else None
        )
        raw_n_cross = len(raw_cross_models)
        raw_top_cross_score = (
            raw_cross_models[0]["cross_incremental_r2"] if raw_cross_models else None
        )
        raw_top_cross_pgs = (
            raw_cross_models[0]["output_pgs_id"] if raw_cross_models else None
        )
        raw_top_output_loinc = (
            raw_cross_models[0]["output_loinc"] if raw_cross_models else None
        )
        raw_top_output_ontology = (
            raw_cross_models[0]["output_ontology"] if raw_cross_models else None
        )
        raw_top_output_description = (
            raw_cross_models[0]["output_description"] if raw_cross_models else None
        )
        unique_output_traits = {cm["output_loinc"] for cm in cross_models}

        summary_rows.append({
            "input_type": _input_type_from_has_self(has_self_score),
            "input_loinc": input_loinc,
            "input_ontology": input_ontology,
            "input_description": input_description,
            "has_self_incremental_r2": has_self_score,
            "self_n_models": len(self_pgs_ids),
            "self_best_incremental_r2": (
                round(self_best_score, 6) if self_best_score is not None else None
            ),
            "n_cross_models_beating_self": n_cross,
            "raw_n_cross_models": raw_n_cross,
            "n_unique_output_traits": len(unique_output_traits),
            "top_cross_incremental_r2": top_cross_score,
            "top_cross_pgs": top_cross_pgs,
            "top_output_loinc": top_output_loinc,
            "top_output_trait": top_output_ontology,
            "top_output_description": top_output_description,
            "raw_top_cross_incremental_r2": raw_top_cross_score,
            "raw_top_cross_pgs": raw_top_cross_pgs,
            "raw_top_output_loinc": raw_top_output_loinc,
            "raw_top_output_trait": raw_top_output_ontology,
            "raw_top_output_description": raw_top_output_description,
            "top_incremental_r2_improvement": (
                round(top_cross_score - self_best_score, 6)
                if top_cross_score is not None and self_best_score is not None
                else None
            ),
        })

    print(
        f"  Continuous donor filter: {continuous_trait_count} LOINC traits in metadata; "
        f"matrix rows={n_matrix_traits}, skipped={n_skipped}, "
        f"skipped self_best>{CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2}={n_skipped_high_self}, "
        f"processed={len(summary_rows)}"
    )

    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def generate_report(
    summary_a: pd.DataFrame,
    label: str,
    output_kind: str = "binary",
) -> str:
    if output_kind == "binary":
        title = f"# Contribution3: Cross List Report ({label})"
        output_mapping_text = (
            "- **Cross trait**: Trait whose PRS models are recommended for the "
            "target trait (binary trait resolved from PGS ontology mapping)"
        )
        workflow_step = (
            "**Determine cross traits** — for each retained target trait, link to "
            "retained cross PGS → ontology "
            "(see **Top Cross Trait** and `cross_list_detail_*.csv`)."
        )
        top_output_code_col = "top_output_icd"
        top_output_name_col = "top_output_disease"
        raw_top_output_code_col = "raw_top_output_icd"
        raw_top_output_name_col = "raw_top_output_disease"
        target_code_label = "Target ICD"
        target_name_label = "Target Trait"
        top_output_code_label = "Cross Trait ICD"
        top_output_name_label = "Top Cross Trait"
        n_unique_output_col = "n_unique_output_diseases"
        n_unique_output_label = "N Unique Cross Traits"
    elif output_kind == "continuous":
        title = f"# Contribution3: Binary-to-Continuous Cross List Report ({label})"
        output_mapping_text = (
            "- **Cross trait**: Trait whose PRS models are recommended for the "
            "target trait (continuous trait resolved from LOINC metadata mapping)"
        )
        workflow_step = (
            "**Determine cross traits** — for each retained target trait, link to "
            "retained cross PGS → LOINC trait metadata "
            "(see **Top Cross Trait** and `cross_list_detail_*.csv`)."
        )
        top_output_code_col = "top_output_loinc"
        top_output_name_col = "top_output_ontology"
        raw_top_output_code_col = "raw_top_output_loinc"
        raw_top_output_name_col = "raw_top_output_ontology"
        target_code_label = "Target ICD"
        target_name_label = "Target Trait"
        top_output_code_label = "Cross Trait LOINC"
        top_output_name_label = "Top Cross Trait"
        n_unique_output_col = "n_unique_output_traits"
        n_unique_output_label = "N Unique Cross Traits"
    else:
        raise ValueError(f"Unsupported output_kind: {output_kind}")

    lines = [
        title,
        "",
        "## Terminology",
        "",
        "- **Target trait**: Trait being predicted / transferred into",
        "  - Restricted to **main analysis** ICDs: `include_in_analysis == 1` in `prs_adjauc_metadata` (aligned with C2)",
        "  - **Type A**: target traits **without self AUC**",
        "  - **Type B**: target traits **with self AUC**",
        "  - All target traits in this report are in C1's AUC matrix, so benchmark validation is available.",
        output_mapping_text,
        "- PGS models with unknown source ontology are **excluded**",
        "",
        "## Cross-list workflow",
        "",
        "1. **Partition screened target traits** into Type A (without self AUC) and Type B (with self AUC).",
        "2. **Retain cross-list target traits** — Type A target traits need at least one qualifying cross model; Type B target traits need a cross model that beats self.",
        f"3. {workflow_step}",
        "4. **Cross-Trait Transfer** — adjust and validate transfer policy using these target-trait / cross-trait pairs.",
        "",
        "## Selection Criterion",
        "",
        "- Type A (without self AUC): require at least one non-self PGS model with a known mapped cross trait",
        "- Type B (with self AUC): require at least one non-self PGS model with cross AUC > best self AUC",
        f"- When self AUC exists: require **cross AUC − self best AUC > {TYPE_A_MIN_IMPROVEMENT}** per retained model",
        f"- Require **Top Cross AUC > {TYPE_A_MIN_TOP_CROSS_AUC}** for the target trait to enter the cross-list",
        f"- Exclude target traits with **self best AUC > {TYPE_A_MAX_SELF_BEST_AUC}** (strong self PRS)",
        "",
    ]

    total_a = len(summary_a)
    has_self = int(summary_a["has_self_auc"].sum())
    with_cross_has_self = int(
        ((summary_a["n_cross_models_beating_self"] > 0) & summary_a["has_self_auc"]).sum()
    )
    no_self_with_cross = int(
        ((summary_a["n_cross_models_beating_self"] > 0) & (~summary_a["has_self_auc"])).sum()
    )
    no_self_no_cross = int(
        ((summary_a["n_cross_models_beating_self"] == 0) & (~summary_a["has_self_auc"])).sum()
    )
    with_cross_any = int((summary_a["n_cross_models_beating_self"] > 0).sum())
    self_optimal = int(
        (summary_a["has_self_auc"] & (summary_a["n_cross_models_beating_self"] == 0)).sum()
    )

    type_a_total = no_self_with_cross + no_self_no_cross
    type_b_total = has_self
    cross_list_input_n = with_cross_has_self + no_self_with_cross

    lines.extend([
        "## Type A / Type B Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| **Cross-list target traits** (retained Type A ∪ retained Type B) | **{cross_list_input_n}** |",
        f"| — Retained Type A (Without Self AUC + qualifying cross) | {no_self_with_cross} |",
        f"| — Retained Type B (With Self AUC + cross beats self) | {with_cross_has_self} |",
        f"| Total screened rows in matrix filter | {total_a} |",
        f"| Type A total (Without Self AUC) | {type_a_total} |",
        f"| — Type A without qualifying cross | {no_self_no_cross} |",
        f"| Type B total (With Self AUC) | {type_b_total} |",
        f"| — Type B self optimal | {self_optimal} |",
        f"| Any cross candidates (Type A + Type B) | {with_cross_any} |",
        "",
        f"*Partition:* `Type A retained` ({no_self_with_cross}) + "
        f"`Type A no qualifying cross` ({no_self_no_cross}) + "
        f"`Type B beats self` ({with_cross_has_self}) + `Type B self optimal` ({self_optimal}) = **{total_a}**. "
        f"*Cross-list target traits* = {no_self_with_cross} + {with_cross_has_self} = **{cross_list_input_n}**.",
        "",
    ])

    no_self_df = summary_a[
        (~summary_a["has_self_auc"])
        & (summary_a["n_cross_models_beating_self"] > 0)
    ].sort_values("top_cross_auc", ascending=False)
    if len(no_self_df) > 0:
        lines.extend([
            "",
            "## Type A: Target Traits Without Self AUC",
            "",
            "*Included in the retained cross-list target traits.*",
            "",
            f"Total: {len(no_self_df)} target traits",
            "",
            f"| {target_code_label} | {target_name_label} | Top Cross AUC | {top_output_code_label} | {top_output_name_label} | N Cross Models |",
            "|-----------|--------------|---------------|-----------------|-----------------|----------------|",
        ])
        for _, r in no_self_df.iterrows():
            output_code = str(r.get(top_output_code_col, "") or "")[:40]
            lines.append(
                f"| {r['input_icd']} | {str(r['input_ontology'])[:40]} | "
                f"{r['top_cross_auc']} | {output_code} | {str(r[top_output_name_col])[:40]} | "
                f"{r['n_cross_models_beating_self']} |"
            )

    no_self_no_cross_df = summary_a[
        (~summary_a["has_self_auc"])
        & (summary_a["n_cross_models_beating_self"] == 0)
    ].sort_values("input_icd")
    if len(no_self_no_cross_df) > 0:
        lines.extend([
            "",
            "## Type A: Without Self AUC But No Qualifying Cross",
            "",
            "*Not included in the retained cross-list target traits under current rules; best available cross-trait evidence shown for reference.*",
            "",
            f"Total: {len(no_self_no_cross_df)} target traits",
            "",
            f"| {target_code_label} | {target_name_label} | Top Available Cross AUC | {top_output_code_label} | {top_output_name_label} | Available N Cross Models |",
            "|-----------|--------------|-------------------------|-----------------|-----------------|--------------------------|",
        ])
        for _, r in no_self_no_cross_df.iterrows():
            output_code = _display_or_dash(r.get(raw_top_output_code_col))
            lines.append(
                f"| {r['input_icd']} | {str(r['input_ontology'])[:40]} | "
                f"{_display_or_dash(r.get('raw_top_cross_auc'))} | {output_code[:40]} | "
                f"{_display_or_dash(r.get(raw_top_output_name_col))[:40]} | "
                f"{_display_positive_count_or_dash(r.get('raw_n_cross_models'))} |"
            )

    beating = summary_a[
        summary_a["has_self_auc"] & (summary_a["n_cross_models_beating_self"] > 0)
    ].sort_values("top_auc_improvement", ascending=False)
    lines.extend([
        "",
        "## Type B: Cross-Trait PRS Beats Self",
        "",
        "*Included in the retained cross-list target traits.*",
        "",
        f"Total: {len(beating)} target traits",
        "",
        f"| {target_code_label} | {target_name_label} | Self Best AUC | Top Cross AUC | Improvement | {top_output_code_label} | {top_output_name_label} | N Cross Models | {n_unique_output_label} |",
        "|-----------|--------------|---------------|---------------|-------------|-----------------|-----------------|----------------|----------------|",
    ])
    for _, r in beating.iterrows():
        output_code = str(r.get(top_output_code_col, "") or "")[:40]
        lines.append(
            f"| {r['input_icd']} | {r['input_ontology'][:40]} | "
            f"{r['self_best_auc']} | {r['top_cross_auc']} | "
            f"+{r['top_auc_improvement']:.4f} | {output_code} | {str(r[top_output_name_col])[:40]} | "
            f"{r['n_cross_models_beating_self']} | {r[n_unique_output_col]} |"
        )

    no_beating = summary_a[
        summary_a["has_self_auc"] & (summary_a["n_cross_models_beating_self"] == 0)
    ].sort_values("self_best_auc", ascending=False)
    lines.extend([
        "",
        "## Type B: Self Models Already Optimal",
        "",
        "*Not included in the retained cross-list target traits (self PRS sufficient under current rules; reference only).*",
        "",
        f"Total: {len(no_beating)} target traits",
        "",
        f"| {target_code_label} | {target_name_label} | Self Best AUC | Self N Models |",
        "|-----------|--------------|---------------|---------------|",
    ])
    for _, r in no_beating.iterrows():
        lines.append(
            f"| {r['input_icd']} | {r['input_ontology'][:50]} | "
            f"{r['self_best_auc']} | {r['self_n_models']} |"
        )

    return "\n".join(lines)


def generate_continuous_to_binary_report(
    summary_a: pd.DataFrame,
    label: str,
) -> str:
    lines = [
        f"# Contribution3: Continuous-to-Binary Cross List Report ({label})",
        "",
        "## Terminology",
        "",
        "- **Target trait**: Trait being predicted / transferred into",
        "  - Continuous target traits here are restricted to `include_in_analysis == 1` in `prs_incrementalr2_metadata`",
        "  - **Type A**: target traits **without self incremental R2**",
        "  - **Type B**: target traits **with self incremental R2**",
        "- **Cross trait**: Trait whose PRS models are recommended for the target trait (binary trait resolved from rootcode disease metadata)",
        "- PGS models with unknown source ontology are **excluded**",
        "",
        "## Cross-list workflow",
        "",
        "1. **Partition screened target traits** into Type A (without self incremental R2) and Type B (with self incremental R2).",
        "2. **Retain cross-list target traits** — Type A target traits need at least one qualifying cross model; Type B target traits need a cross model that beats self.",
        "3. **Determine cross traits** — for each retained continuous target trait, link retained cross PGS → rootcode disease metadata.",
        "4. **Cross-Trait Transfer** — evaluate whether disease PRS models can usefully transfer to the continuous trait.",
        "",
        "## Selection Criterion",
        "",
        "- Type A (without self incremental R2): require at least one non-self disease PGS model",
        "- Type B (with self incremental R2): require at least one non-self disease PGS model with cross incremental R2 > best self incremental R2",
        f"- When self incremental R2 exists: require **cross incremental R2 − self best incremental R2 > {CONTINUOUS_TYPE_A_MIN_IMPROVEMENT}** per retained model",
        f"- Require **Top Cross incremental R2 > {CONTINUOUS_TYPE_A_MIN_TOP_CROSS_INCREMENTAL_R2}** for the target trait to enter the cross-list",
        f"- Exclude target traits with **self best incremental R2 > {CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2}** (strong self PRS)",
        "",
    ]

    total_a = len(summary_a)
    has_self = int(summary_a["has_self_incremental_r2"].sum())
    no_self = total_a - has_self
    no_self_with_cross = int(
        (
            (summary_a["n_cross_models_beating_self"] > 0)
            & (~summary_a["has_self_incremental_r2"])
        ).sum()
    )
    no_self_no_cross = int(
        (
            (summary_a["n_cross_models_beating_self"] == 0)
            & (~summary_a["has_self_incremental_r2"])
        ).sum()
    )
    with_cross_has_self = int(
        (
            (summary_a["n_cross_models_beating_self"] > 0)
            & summary_a["has_self_incremental_r2"]
        ).sum()
    )
    with_cross_any = int((summary_a["n_cross_models_beating_self"] > 0).sum())
    self_optimal = int(
        (
            summary_a["has_self_incremental_r2"]
            & (summary_a["n_cross_models_beating_self"] == 0)
        ).sum()
    )
    cross_list_input_n = no_self_with_cross + with_cross_has_self

    lines.extend([
        "## Type A / Type B Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| **Cross-list target traits** (retained Type A ∪ retained Type B) | **{cross_list_input_n}** |",
        f"| — Retained Type A (Without Self incremental R2 + qualifying cross) | {no_self_with_cross} |",
        f"| — Retained Type B (With Self incremental R2 + cross beats self) | {with_cross_has_self} |",
        f"| Total screened rows in matrix filter | {total_a} |",
        f"| Type A total (Without Self incremental R2) | {no_self} |",
        f"| — Type A without qualifying cross | {no_self_no_cross} |",
        f"| Type B total (With Self incremental R2) | {has_self} |",
        f"| — Type B self optimal | {self_optimal} |",
        f"| Any cross candidates | {with_cross_any} |",
        "",
    ])

    no_self_df = summary_a[
        (~summary_a["has_self_incremental_r2"])
        & (summary_a["n_cross_models_beating_self"] > 0)
    ].sort_values("top_cross_incremental_r2", ascending=False)
    if len(no_self_df) > 0:
        lines.extend([
            "## Type A: Target Traits Without Self Incremental R2",
            "",
            "*Included in the retained cross-list target traits.*",
            "",
            f"Total: {len(no_self_df)} target traits",
            "",
            "| Target LOINC | Target Trait | Top Cross Incremental R2 | Cross Trait ICD | Top Cross Trait | N Cross Models |",
            "|--------------|--------------|--------------------------|-----------------|-----------------|----------------|",
        ])
        for _, r in no_self_df.iterrows():
            lines.append(
                f"| {r['input_loinc']} | {str(r['input_ontology'])[:40]} | "
                f"{r['top_cross_incremental_r2']} | {str(r['top_output_icd'])[:40]} | "
                f"{str(r['top_output_disease'])[:40]} | {r['n_cross_models_beating_self']} |"
            )

    no_self_no_cross_df = summary_a[
        (~summary_a["has_self_incremental_r2"])
        & (summary_a["n_cross_models_beating_self"] == 0)
    ].sort_values("input_loinc")
    if len(no_self_no_cross_df) > 0:
        lines.extend([
            "",
            "## Type A: Without Self Incremental R2 But No Qualifying Cross",
            "",
            "*Not included in the retained cross-list target traits under current rules; best available cross-trait evidence shown for reference.*",
            "",
            f"Total: {len(no_self_no_cross_df)} target traits",
            "",
            "| Target LOINC | Target Trait | Top Available Cross Incremental R2 | Cross Trait ICD | Top Cross Trait | Available N Cross Models |",
            "|--------------|--------------|------------------------------------|-----------------|-----------------|--------------------------|",
        ])
        for _, r in no_self_no_cross_df.iterrows():
            lines.append(
                f"| {r['input_loinc']} | {str(r['input_ontology'])[:40]} | "
                f"{_display_or_dash(r.get('raw_top_cross_incremental_r2'))} | "
                f"{_display_or_dash(r.get('raw_top_output_icd'))[:40]} | "
                f"{_display_or_dash(r.get('raw_top_output_disease'))[:40]} | "
                f"{_display_positive_count_or_dash(r.get('raw_n_cross_models'))} |"
            )

    beating = summary_a[
        summary_a["has_self_incremental_r2"]
        & (summary_a["n_cross_models_beating_self"] > 0)
    ].sort_values("top_incremental_r2_improvement", ascending=False)

    lines.extend([
        "",
        "## Type B: Cross-Trait PRS Beats Self",
        "",
        "*Included in the retained cross-list target traits.*",
        "",
        f"Total: {len(beating)} target traits",
        "",
        "| Target LOINC | Target Trait | Self Best Incremental R2 | Top Cross Incremental R2 | Improvement | Cross Trait ICD | Top Cross Trait | N Cross Models | N Unique Cross Traits |",
        "|--------------|--------------|--------------------------|--------------------------|-------------|-----------------|-----------------|----------------|-------------------------|",
    ])
    for _, r in beating.iterrows():
        lines.append(
            f"| {r['input_loinc']} | {str(r['input_ontology'])[:40]} | "
            f"{r['self_best_incremental_r2']} | {r['top_cross_incremental_r2']} | "
            f"+{r['top_incremental_r2_improvement']:.4f} | {str(r['top_output_icd'])[:40]} | "
            f"{str(r['top_output_disease'])[:40]} | {r['n_cross_models_beating_self']} | "
            f"{r['n_unique_output_diseases']} |"
        )

    no_beating = summary_a[
        summary_a["has_self_incremental_r2"]
        & (summary_a["n_cross_models_beating_self"] == 0)
    ].sort_values("self_best_incremental_r2", ascending=False)
    lines.extend([
        "",
        "## Type B: Self Models Already Optimal",
        "",
        "*Not included in the retained cross-list target traits (self PRS sufficient under current rules; reference only).*",
        "",
        f"Total: {len(no_beating)} target traits",
        "",
        "| Target LOINC | Target Trait | Self Best Incremental R2 | Self N Models |",
        "|--------------|--------------|--------------------------|---------------|",
    ])
    for _, r in no_beating.iterrows():
        lines.append(
            f"| {r['input_loinc']} | {str(r['input_ontology'])[:50]} | "
            f"{r['self_best_incremental_r2']} | {r['self_n_models']} |"
        )

    return "\n".join(lines)


def generate_continuous_to_continuous_report(
    summary_a: pd.DataFrame,
    label: str,
) -> str:
    lines = [
        f"# Contribution3: Continuous-to-Continuous Cross List Report ({label})",
        "",
        "## Terminology",
        "",
        "- **Target trait**: Trait being predicted / transferred into",
        "  - Continuous target traits here are restricted to `include_in_analysis == 1` in `prs_incrementalr2_metadata`",
        "  - **Type A**: target traits **without self incremental R2**",
        "  - **Type B**: target traits **with self incremental R2**",
        "- **Cross trait**: Trait whose PRS models are recommended for the target trait (continuous trait resolved from LOINC metadata mapping)",
        "- PGS models with unknown source ontology are **excluded**",
        "",
        "## Cross-list workflow",
        "",
        "1. **Partition screened target traits** into Type A (without self incremental R2) and Type B (with self incremental R2).",
        "2. **Retain cross-list target traits** — Type A target traits need at least one qualifying cross model; Type B target traits need a cross model that beats self.",
        "3. **Determine cross traits** — for each retained continuous target trait, link retained cross PGS → LOINC trait metadata.",
        "4. **Cross-Trait Transfer** — evaluate whether continuous-trait PRS models can usefully transfer to the target trait.",
        "",
        "## Selection Criterion",
        "",
        "- Type A (without self incremental R2): require at least one non-self continuous-trait PGS model",
        "- Type B (with self incremental R2): require at least one non-self continuous-trait PGS model with cross incremental R2 > best self incremental R2",
        f"- When self incremental R2 exists: require **cross incremental R2 − self best incremental R2 > {CONTINUOUS_TYPE_A_MIN_IMPROVEMENT}** per retained model",
        f"- Require **Top Cross incremental R2 > {CONTINUOUS_TYPE_A_MIN_TOP_CROSS_INCREMENTAL_R2}** for the target trait to enter the cross-list",
        f"- Exclude target traits with **self best incremental R2 > {CONTINUOUS_TYPE_A_MAX_SELF_BEST_INCREMENTAL_R2}** (strong self PRS)",
        "",
    ]

    total_a = len(summary_a)
    has_self = int(summary_a["has_self_incremental_r2"].sum())
    no_self = total_a - has_self
    no_self_with_cross = int(
        (
            (summary_a["n_cross_models_beating_self"] > 0)
            & (~summary_a["has_self_incremental_r2"])
        ).sum()
    )
    no_self_no_cross = int(
        (
            (summary_a["n_cross_models_beating_self"] == 0)
            & (~summary_a["has_self_incremental_r2"])
        ).sum()
    )
    with_cross_has_self = int(
        (
            (summary_a["n_cross_models_beating_self"] > 0)
            & summary_a["has_self_incremental_r2"]
        ).sum()
    )
    with_cross_any = int((summary_a["n_cross_models_beating_self"] > 0).sum())
    self_optimal = int(
        (
            summary_a["has_self_incremental_r2"]
            & (summary_a["n_cross_models_beating_self"] == 0)
        ).sum()
    )
    cross_list_input_n = no_self_with_cross + with_cross_has_self

    lines.extend([
        "## Type A / Type B Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| **Cross-list target traits** (retained Type A ∪ retained Type B) | **{cross_list_input_n}** |",
        f"| — Retained Type A (Without Self incremental R2 + qualifying cross) | {no_self_with_cross} |",
        f"| — Retained Type B (With Self incremental R2 + cross beats self) | {with_cross_has_self} |",
        f"| Total screened rows in matrix filter | {total_a} |",
        f"| Type A total (Without Self incremental R2) | {no_self} |",
        f"| — Type A without qualifying cross | {no_self_no_cross} |",
        f"| Type B total (With Self incremental R2) | {has_self} |",
        f"| — Type B self optimal | {self_optimal} |",
        f"| Any cross candidates | {with_cross_any} |",
        "",
    ])

    no_self_df = summary_a[
        (~summary_a["has_self_incremental_r2"])
        & (summary_a["n_cross_models_beating_self"] > 0)
    ].sort_values("top_cross_incremental_r2", ascending=False)
    if len(no_self_df) > 0:
        lines.extend([
            "## Type A: Target Traits Without Self Incremental R2",
            "",
            "*Included in the retained cross-list target traits.*",
            "",
            f"Total: {len(no_self_df)} target traits",
            "",
            "| Target LOINC | Target Trait | Top Cross Incremental R2 | Cross Trait LOINC | Top Cross Trait | N Cross Models |",
            "|--------------|--------------|--------------------------|-------------------|-----------------|----------------|",
        ])
        for _, r in no_self_df.iterrows():
            lines.append(
                f"| {r['input_loinc']} | {str(r['input_ontology'])[:40]} | "
                f"{r['top_cross_incremental_r2']} | {str(r['top_output_loinc'])[:40]} | "
                f"{str(r['top_output_trait'])[:40]} | {r['n_cross_models_beating_self']} |"
            )

    no_self_no_cross_df = summary_a[
        (~summary_a["has_self_incremental_r2"])
        & (summary_a["n_cross_models_beating_self"] == 0)
    ].sort_values("input_loinc")
    if len(no_self_no_cross_df) > 0:
        lines.extend([
            "",
            "## Type A: Without Self Incremental R2 But No Qualifying Cross",
            "",
            "*Not included in the retained cross-list target traits under current rules; best available cross-trait evidence shown for reference.*",
            "",
            f"Total: {len(no_self_no_cross_df)} target traits",
            "",
            "| Target LOINC | Target Trait | Top Available Cross Incremental R2 | Cross Trait LOINC | Top Cross Trait | Available N Cross Models |",
            "|--------------|--------------|------------------------------------|-------------------|-----------------|--------------------------|",
        ])
        for _, r in no_self_no_cross_df.iterrows():
            lines.append(
                f"| {r['input_loinc']} | {str(r['input_ontology'])[:40]} | "
                f"{_display_or_dash(r.get('raw_top_cross_incremental_r2'))} | "
                f"{_display_or_dash(r.get('raw_top_output_loinc'))[:40]} | "
                f"{_display_or_dash(r.get('raw_top_output_trait'))[:40]} | "
                f"{_display_positive_count_or_dash(r.get('raw_n_cross_models'))} |"
            )

    beating = summary_a[
        summary_a["has_self_incremental_r2"]
        & (summary_a["n_cross_models_beating_self"] > 0)
    ].sort_values("top_incremental_r2_improvement", ascending=False)

    lines.extend([
        "",
        "## Type B: Cross-Trait PRS Beats Self",
        "",
        "*Included in the retained cross-list target traits.*",
        "",
        f"Total: {len(beating)} target traits",
        "",
        "| Target LOINC | Target Trait | Self Best Incremental R2 | Top Cross Incremental R2 | Improvement | Cross Trait LOINC | Top Cross Trait | N Cross Models | N Unique Cross Traits |",
        "|--------------|--------------|--------------------------|--------------------------|-------------|-------------------|-----------------|----------------|-------------------------|",
    ])
    for _, r in beating.iterrows():
        lines.append(
            f"| {r['input_loinc']} | {str(r['input_ontology'])[:40]} | "
            f"{r['self_best_incremental_r2']} | {r['top_cross_incremental_r2']} | "
            f"+{r['top_incremental_r2_improvement']:.4f} | {str(r['top_output_loinc'])[:40]} | "
            f"{str(r['top_output_trait'])[:40]} | {r['n_cross_models_beating_self']} | "
            f"{r['n_unique_output_traits']} |"
        )

    no_beating = summary_a[
        summary_a["has_self_incremental_r2"]
        & (summary_a["n_cross_models_beating_self"] == 0)
    ].sort_values("self_best_incremental_r2", ascending=False)
    lines.extend([
        "",
        "## Type B: Self Models Already Optimal",
        "",
        "*Not included in the retained cross-list target traits (self PRS sufficient under current rules; reference only).*",
        "",
        f"Total: {len(no_beating)} target traits",
        "",
        "| Target LOINC | Target Trait | Self Best Incremental R2 | Self N Models |",
        "|--------------|--------------|--------------------------|---------------|",
    ])
    for _, r in no_beating.iterrows():
        lines.append(
            f"| {r['input_loinc']} | {str(r['input_ontology'])[:50]} | "
            f"{r['self_best_incremental_r2']} | {r['self_n_models']} |"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    BINARY_TO_BINARY_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    BINARY_TO_CONTINUOUS_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CONTINUOUS_TO_BINARY_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CONTINUOUS_TO_CONTINUOUS_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    # Remove old flat outputs from runs/ so only the three subfolders remain.
    for path in RUNS_DIR.glob("cross_list_*"):
        if path.is_file():
            path.unlink()

    matrix = load_rootcode_auc_matrix()
    allowed_input_icds = load_main_analysis_input_icds()
    print(f"\n{'='*60}")
    print("Building binary-to-binary cross list for rootcode...")
    print(f"{'='*60}")

    result_a = build_type_a_cross_list(matrix, allowed_input_icds)
    detail_a, summary_a = result_a

    detail_a.to_csv(BINARY_TO_BINARY_RUNS_DIR / "cross_list_detail.csv", index=False)
    summary_a.to_csv(BINARY_TO_BINARY_RUNS_DIR / "cross_list_summary.csv", index=False)

    # Disease-level aggregation (one row per input_icd x output_disease)
    if not detail_a.empty:
        beating = detail_a[detail_a["has_self_auc"] == True].copy()
        if not beating.empty:
            grouped = beating.groupby([
                "input_icd", "input_ontology", "self_best_auc",
                "output_disease",
            ]).agg(
                n_models=("output_pgs_id", "count"),
                best_cross_auc=("cross_auc", "max"),
                best_cross_pgs=("output_pgs_id", "first"),
                best_auc_improvement=("auc_improvement", "max"),
            ).reset_index()
            grouped = grouped.sort_values(
                ["input_icd", "best_cross_auc"], ascending=[True, False]
            )
            grouped.to_csv(
                BINARY_TO_BINARY_RUNS_DIR / "cross_list_disease_level.csv",
                index=False,
            )

    has_self = int(summary_a["has_self_auc"].sum())
    beating_n = int(
        ((summary_a["n_cross_models_beating_self"] > 0) & summary_a["has_self_auc"]).sum()
    )
    without_self_with_cross_n = int(
        ((summary_a["n_cross_models_beating_self"] > 0) & (~summary_a["has_self_auc"])).sum()
    )
    without_self_no_cross_n = int(
        ((summary_a["n_cross_models_beating_self"] == 0) & (~summary_a["has_self_auc"])).sum()
    )
    print(f"  Screened benchmarked binary target traits: {len(summary_a)}")
    print(f"    With self AUC: {has_self}")
    print(f"      - Cross beats self: {beating_n}")
    print(f"      - Self optimal: {has_self - beating_n}")
    print(f"    Without self AUC and qualifying cross: {without_self_with_cross_n}")
    print(f"    Without self AUC but no qualifying cross: {without_self_no_cross_n}")
    print(f"    Detail rows: {len(detail_a)}")

    print(f"\n{'='*60}")
    print("Building binary-to-continuous cross list for rootcode...")
    print(f"{'='*60}")

    detail_bc, summary_bc = build_type_a_binary_to_continuous_cross_list(
        matrix,
        allowed_input_icds,
    )
    detail_bc.to_csv(
        BINARY_TO_CONTINUOUS_RUNS_DIR / "cross_list_detail.csv",
        index=False,
    )
    summary_bc.to_csv(
        BINARY_TO_CONTINUOUS_RUNS_DIR / "cross_list_summary.csv",
        index=False,
    )

    if not detail_bc.empty:
        beating_bc = detail_bc[detail_bc["has_self_auc"] == True].copy()
        if not beating_bc.empty:
            grouped_bc = beating_bc.groupby([
                "input_icd", "input_ontology", "self_best_auc",
                "output_loinc", "output_ontology", "output_description",
            ]).agg(
                n_models=("output_pgs_id", "count"),
                best_cross_auc=("cross_auc", "max"),
                best_cross_pgs=("output_pgs_id", "first"),
                best_auc_improvement=("auc_improvement", "max"),
            ).reset_index()
            grouped_bc = grouped_bc.sort_values(
                ["input_icd", "best_cross_auc"], ascending=[True, False]
            )
            grouped_bc.to_csv(
                BINARY_TO_CONTINUOUS_RUNS_DIR / "cross_list_disease_level.csv",
                index=False,
            )

    has_self_bc = int(summary_bc["has_self_auc"].sum())
    beating_bc_n = int(
        ((summary_bc["n_cross_models_beating_self"] > 0) & summary_bc["has_self_auc"]).sum()
    )
    without_self_with_cross_bc_n = int(
        ((summary_bc["n_cross_models_beating_self"] > 0) & (~summary_bc["has_self_auc"])).sum()
    )
    without_self_no_cross_bc_n = int(
        ((summary_bc["n_cross_models_beating_self"] == 0) & (~summary_bc["has_self_auc"])).sum()
    )
    print(f"  Screened benchmarked binary target traits: {len(summary_bc)}")
    print(f"    With self AUC: {has_self_bc}")
    print(f"      - Cross beats self: {beating_bc_n}")
    print(f"      - Self optimal: {has_self_bc - beating_bc_n}")
    print(f"    Without self AUC and qualifying cross: {without_self_with_cross_bc_n}")
    print(f"    Without self AUC but no qualifying cross: {without_self_no_cross_bc_n}")
    print(f"    Detail rows: {len(detail_bc)}")

    print(f"\n{'='*60}")
    print("Building continuous-to-binary cross list...")
    print(f"{'='*60}")

    loinc_matrix = load_loinc_incremental_r2_matrix()
    allowed_input_loincs = load_main_analysis_input_loincs()
    detail_cb, summary_cb = build_type_a_continuous_to_binary_cross_list(
        loinc_matrix,
        allowed_input_loincs,
    )
    detail_cb.to_csv(CONTINUOUS_TO_BINARY_RUNS_DIR / "cross_list_detail.csv", index=False)
    summary_cb.to_csv(CONTINUOUS_TO_BINARY_RUNS_DIR / "cross_list_summary.csv", index=False)

    if not detail_cb.empty:
        beating_cb = detail_cb[detail_cb["has_self_incremental_r2"] == True].copy()
        if not beating_cb.empty:
            grouped_cb = beating_cb.groupby([
                "input_loinc", "input_ontology", "self_best_incremental_r2",
                "output_icd", "output_ontology", "output_description",
            ]).agg(
                n_models=("output_pgs_id", "count"),
                best_cross_incremental_r2=("cross_incremental_r2", "max"),
                best_cross_pgs=("output_pgs_id", "first"),
                best_incremental_r2_improvement=("incremental_r2_improvement", "max"),
            ).reset_index()
            grouped_cb = grouped_cb.sort_values(
                ["input_loinc", "best_cross_incremental_r2"],
                ascending=[True, False],
            )
            grouped_cb.to_csv(
                CONTINUOUS_TO_BINARY_RUNS_DIR / "cross_list_disease_level.csv",
                index=False,
            )

    has_self_cb = int(summary_cb["has_self_incremental_r2"].sum())
    beating_cb_n = int(
        (
            (summary_cb["n_cross_models_beating_self"] > 0)
            & summary_cb["has_self_incremental_r2"]
        ).sum()
    )
    print(f"  Screened benchmarked continuous target traits: {len(summary_cb)}")
    print(f"    With self incremental R2: {has_self_cb}")
    print(f"      - Cross beats self: {beating_cb_n}")
    print(f"      - Self optimal: {has_self_cb - beating_cb_n}")
    print(f"    Without self incremental R2: {len(summary_cb) - has_self_cb}")
    print(f"    Detail rows: {len(detail_cb)}")

    print(f"\n{'='*60}")
    print("Building continuous-to-continuous cross list...")
    print(f"{'='*60}")

    detail_cc, summary_cc = build_type_a_continuous_to_continuous_cross_list(
        loinc_matrix,
        allowed_input_loincs,
    )
    detail_cc.to_csv(
        CONTINUOUS_TO_CONTINUOUS_RUNS_DIR / "cross_list_detail.csv",
        index=False,
    )
    summary_cc.to_csv(
        CONTINUOUS_TO_CONTINUOUS_RUNS_DIR / "cross_list_summary.csv",
        index=False,
    )

    if not detail_cc.empty:
        beating_cc = detail_cc[detail_cc["has_self_incremental_r2"] == True].copy()
        if not beating_cc.empty:
            grouped_cc = beating_cc.groupby([
                "input_loinc", "input_ontology", "self_best_incremental_r2",
                "output_loinc", "output_ontology", "output_description",
            ]).agg(
                n_models=("output_pgs_id", "count"),
                best_cross_incremental_r2=("cross_incremental_r2", "max"),
                best_cross_pgs=("output_pgs_id", "first"),
                best_incremental_r2_improvement=("incremental_r2_improvement", "max"),
            ).reset_index()
            grouped_cc = grouped_cc.sort_values(
                ["input_loinc", "best_cross_incremental_r2"],
                ascending=[True, False],
            )
            grouped_cc.to_csv(
                CONTINUOUS_TO_CONTINUOUS_RUNS_DIR / "cross_list_disease_level.csv",
                index=False,
            )

    has_self_cc = int(summary_cc["has_self_incremental_r2"].sum())
    beating_cc_n = int(
        (
            (summary_cc["n_cross_models_beating_self"] > 0)
            & summary_cc["has_self_incremental_r2"]
        ).sum()
    )
    print(f"  Screened benchmarked continuous target traits: {len(summary_cc)}")
    print(f"    With self incremental R2: {has_self_cc}")
    print(f"      - Cross beats self: {beating_cc_n}")
    print(f"      - Self optimal: {has_self_cc - beating_cc_n}")
    print(f"    Without self incremental R2: {len(summary_cc) - has_self_cc}")
    print(f"    Detail rows: {len(detail_cc)}")

    report = generate_report(summary_a, "rootcode", output_kind="binary")
    (BINARY_TO_BINARY_RUNS_DIR / "cross_list_report.md").write_text(report, encoding="utf-8")
    report_bc = generate_report(
        summary_bc,
        "rootcode",
        output_kind="continuous",
    )
    (BINARY_TO_CONTINUOUS_RUNS_DIR / "cross_list_report.md").write_text(
        report_bc,
        encoding="utf-8",
    )
    report_cb = generate_continuous_to_binary_report(summary_cb, "loinccode")
    (CONTINUOUS_TO_BINARY_RUNS_DIR / "cross_list_report.md").write_text(
        report_cb,
        encoding="utf-8",
    )
    report_cc = generate_continuous_to_continuous_report(summary_cc, "loinccode")
    (CONTINUOUS_TO_CONTINUOUS_RUNS_DIR / "cross_list_report.md").write_text(
        report_cc,
        encoding="utf-8",
    )

    print("\nDone. Outputs in experiments/contribution3/cross_list/runs/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build Contribution3 cross list (rootcode only)"
    )
    parser.parse_args()
    main()
