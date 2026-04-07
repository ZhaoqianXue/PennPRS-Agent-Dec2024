"""
Contribution3: Build Cross-Trait Transfer Benchmark

Redesign of the cross-trait transfer evaluation framework with two key changes
from the original build_cross_list.py:

1. Disease-level aggregation: ground truth is defined at the cross-disease level
   (not individual PGS model level), since the Cross Trait Transfer module outputs
   a disease recommendation, not a specific PGS model.

2. Complete ranking: for each target trait, ALL cross diseases are ranked by their
   best model's AUC on the target — not just those passing a screening threshold.
   This enables Hit@k and NRS evaluation consistent with Contribution2.

3. Refined target selection criteria:
   - Disease-level assessment (n_qualifying_diseases, not n_qualifying_models)
   - Support requirement: n_qualifying_diseases >= K_MIN (default 1)
   - Clinical utility floor: best cross disease AUC > MIN_TOP_CROSS_AUC
   - Cross-ranking clustering requirement: best_split_gap >= MIN_BEST_SPLIT_GAP
   - Type B targets additionally require self AUC < MAX_SELF_AUC (default 0.60)

Screening criteria (MIN_IMPROVEMENT, MIN_TOP_CROSS_AUC, MIN_BEST_SPLIT_GAP)
define TARGET SELECTION only. The evaluation ground truth is the complete
disease-level AUC ranking.

Usage:
    python build_benchmark.py
    python build_benchmark.py --delta 0.03 --kmin 2   # sensitivity analysis
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd

# Reuse data loading and mapping functions from the existing pipeline.
from build_cross_list import (
    CONTRIB1_RESULT_DIR,
    CONTRIB1_LOINC_RESULT_DIR,
    _col_to_pgs_id,
    _pgs_id_to_col,
    _get_self_auc_info,
    load_rootcode_auc_matrix,
    load_main_analysis_input_icds,
    build_pgs_to_ontology_map_full,
    build_icd_to_self_pgs_full,
    build_icd_to_ontologies_full,
    get_icd_description_map_full,
    build_pgs_ontology_to_icd_map,
    build_pgs_to_binary_trait_map,
    build_pgs_to_continuous_trait_map,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
CROSS_LIST_DIR = SCRIPT_DIR.parent
BENCHMARK_DIR = CROSS_LIST_DIR / "benchmark"
B2B_DIR = BENCHMARK_DIR / "binary_to_binary"
B2C_DIR = BENCHMARK_DIR / "binary_to_continuous"

# ---------------------------------------------------------------------------
# Default parameters (overridable via CLI for sensitivity analysis)
# ---------------------------------------------------------------------------
DEFAULT_DELTA = 0.025            # AUC improvement threshold (disease-level)
DEFAULT_K_MIN = 1                # min qualifying cross diseases
DEFAULT_MIN_TOP_CROSS_AUC = 0.55 # clinical utility floor
DEFAULT_MIN_BEST_SPLIT_GAP = 0.025  # require a visible break in cross ranking
DEFAULT_MAX_SELF_AUC = 0.60      # only transfer when self PRS is still weak


def _get_best_split_info(
    ranking: list[dict],
    auc_key: str = "disease_best_auc",
) -> tuple[Optional[float], Optional[int]]:
    """Return the largest adjacent AUC gap and the Top-k split where it occurs."""
    if len(ranking) < 2:
        return None, None

    aucs = [float(row[auc_key]) for row in ranking]
    gaps = [aucs[i] - aucs[i + 1] for i in range(len(aucs) - 1)]
    best_gap = max(gaps)
    best_k = gaps.index(best_gap) + 1
    return round(best_gap, 6), best_k


# ---------------------------------------------------------------------------
# Core: disease-level ground truth for binary-to-binary
# ---------------------------------------------------------------------------

def build_b2b_benchmark(
    matrix: pd.DataFrame,
    allowed_input_icds: set[str],
    *,
    delta: float = DEFAULT_DELTA,
    k_min: int = DEFAULT_K_MIN,
    min_top_cross_auc: float = DEFAULT_MIN_TOP_CROSS_AUC,
    min_best_split_gap: float = DEFAULT_MIN_BEST_SPLIT_GAP,
    max_self_auc: float = DEFAULT_MAX_SELF_AUC,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    For each binary target trait, compute the complete disease-level ranking
    of ALL cross diseases (not just those beating self).

    Returns:
        target_selection: one row per candidate target, with selection decision
        ground_truth: one row per (selected_target, cross_disease), ranked by AUC
    """
    pgs_to_ontology = build_pgs_to_ontology_map_full()
    icd_to_self_pgs = build_icd_to_self_pgs_full()
    icd_to_ontologies = build_icd_to_ontologies_full()
    icd_desc_map = get_icd_description_map_full()
    pgs_ontology_to_icd = build_pgs_ontology_to_icd_map()

    known_pgs_ids = set(pgs_to_ontology.keys())
    pgs_columns = list(matrix.columns)

    target_rows = []
    gt_rows = []

    for input_icd in matrix.index:
        input_icd = str(input_icd).strip()
        if input_icd not in allowed_input_icds:
            continue

        input_ontologies = icd_to_ontologies.get(input_icd, [])
        input_ontology_set = set(input_ontologies)
        input_ontology_str = "; ".join(sorted(input_ontologies))
        input_desc = icd_desc_map.get(input_icd, "")

        self_pgs_ids = icd_to_self_pgs.get(input_icd, set())
        auc_row = matrix.loc[input_icd]
        self_best_auc, self_best_pgs = _get_self_auc_info(auc_row, self_pgs_ids)
        has_self = self_best_auc is not None

        # ------------------------------------------------------------------
        # Collect ALL cross models and aggregate by output ICD root
        # ------------------------------------------------------------------
        # disease_icd -> list of (pgs_id, auc) tuples
        disease_models: dict[str, list[tuple[str, float]]] = {}
        # disease_icd -> set of ontology strings
        disease_ontologies: dict[str, set[str]] = {}

        for col in pgs_columns:
            pgs_id = _col_to_pgs_id(col)

            if pgs_id in self_pgs_ids:
                continue
            if pgs_id not in known_pgs_ids:
                continue

            val = auc_row[col]
            if not (pd.notna(val) and isinstance(val, (int, float))):
                continue
            cross_auc = float(val)

            # Map this PGS to its source disease ICD root(s)
            source_ontologies = pgs_to_ontology.get(pgs_id, set())
            # Exclude ontologies that overlap with the target (self-alias)
            filtered_ontologies = source_ontologies - input_ontology_set

            if not filtered_ontologies:
                continue

            # Map ontologies to ICD roots
            seen_icds = set()
            for ont in filtered_ontologies:
                cross_icd = pgs_ontology_to_icd.get((pgs_id, ont))
                if cross_icd and cross_icd != input_icd and cross_icd not in seen_icds:
                    seen_icds.add(cross_icd)
                    disease_models.setdefault(cross_icd, []).append((pgs_id, cross_auc))
                    disease_ontologies.setdefault(cross_icd, set()).add(ont)

        # ------------------------------------------------------------------
        # Aggregate: per-disease best AUC
        # ------------------------------------------------------------------
        disease_ranking = []
        for d_icd, models in disease_models.items():
            best_pgs, best_auc = max(models, key=lambda x: x[1])
            d_onts = sorted(disease_ontologies[d_icd])
            d_desc = icd_desc_map.get(d_icd, "")
            improvement = (best_auc - self_best_auc) if has_self else None

            disease_ranking.append({
                "cross_icd": d_icd,
                "cross_ontology": "; ".join(d_onts),
                "cross_description": d_desc,
                "n_pgs_models": len(models),
                "disease_best_auc": round(best_auc, 6),
                "best_pgs_id": best_pgs,
                "auc_improvement": round(improvement, 6) if improvement is not None else None,
            })

        # Sort by disease_best_auc descending
        disease_ranking.sort(key=lambda x: x["disease_best_auc"], reverse=True)

        # Assign rank
        for rank_idx, dr in enumerate(disease_ranking, 1):
            dr["rank"] = rank_idx

        best_split_gap, best_split_k = _get_best_split_info(disease_ranking)

        # ------------------------------------------------------------------
        # Apply target selection criteria
        # ------------------------------------------------------------------
        n_total_cross_diseases = len(disease_ranking)

        if has_self:
            qualifying = [
                dr for dr in disease_ranking
                if dr["auc_improvement"] is not None
                and dr["auc_improvement"] > delta
            ]
        else:
            # Type A: any cross disease with AUC > min_top_cross_auc qualifies
            qualifying = [
                dr for dr in disease_ranking
                if dr["disease_best_auc"] > min_top_cross_auc
            ]

        n_qualifying = len(qualifying)
        top_improvement = qualifying[0]["auc_improvement"] if (qualifying and has_self) else None
        top_cross_auc = disease_ranking[0]["disease_best_auc"] if disease_ranking else None
        has_clear_cluster = (
            best_split_gap is not None and best_split_gap >= min_best_split_gap
        )

        # Selection decision
        if has_self:
            self_auc_ok = self_best_auc < max_self_auc
            selected = (
                self_auc_ok
                and n_qualifying >= k_min
                and top_cross_auc is not None
                and top_cross_auc > min_top_cross_auc
                and has_clear_cluster
            )
            if selected:
                reason = (
                    f"self_AUC={self_best_auc:.4f}<{max_self_auc}, "
                    f"n_qualifying={n_qualifying}>=k_min({k_min}), "
                    f"top_AUC={top_cross_auc:.4f}>{min_top_cross_auc}, "
                    f"best_split_gap={best_split_gap:.4f}>={min_best_split_gap}"
                )
            else:
                reasons = []
                if not self_auc_ok:
                    reasons.append(f"self_AUC={self_best_auc:.4f}>={max_self_auc}")
                if n_qualifying < k_min:
                    reasons.append(f"n_qualifying={n_qualifying}<k_min({k_min})")
                if top_cross_auc is not None and top_cross_auc <= min_top_cross_auc:
                    reasons.append(f"top_AUC={top_cross_auc:.4f}<={min_top_cross_auc}")
                if not has_clear_cluster:
                    split_str = "NA" if best_split_gap is None else f"{best_split_gap:.4f}"
                    reasons.append(f"best_split_gap={split_str}<{min_best_split_gap}")
                if not disease_ranking:
                    reasons.append("no_cross_diseases")
                reason = "; ".join(reasons) if reasons else "no_qualifying_diseases"
        else:
            selected = n_qualifying >= 1 and has_clear_cluster
            if selected:
                reason = (
                    f"type_A, n_qualifying={n_qualifying}, "
                    f"best_split_gap={best_split_gap:.4f}>={min_best_split_gap}"
                )
            else:
                reasons = []
                if n_qualifying < 1:
                    reasons.append("type_A, no_cross_AUC>0.55")
                if not has_clear_cluster:
                    split_str = "NA" if best_split_gap is None else f"{best_split_gap:.4f}"
                    reasons.append(f"best_split_gap={split_str}<{min_best_split_gap}")
                reason = "; ".join(reasons) if reasons else "type_A_not_selected"

        target_rows.append({
            "input_type": "B" if has_self else "A",
            "input_icd": input_icd,
            "input_ontology": input_ontology_str,
            "input_description": input_desc,
            "self_n_models": len(self_pgs_ids),
            "self_best_auc": round(self_best_auc, 6) if has_self else None,
            "self_best_pgs": self_best_pgs,
            "n_total_cross_diseases": n_total_cross_diseases,
            "n_qualifying_diseases": n_qualifying,
            "top_cross_disease_auc": round(top_cross_auc, 6) if top_cross_auc else None,
            "top_auc_improvement": round(top_improvement, 6) if top_improvement is not None else None,
            "best_split_gap": best_split_gap,
            "best_split_k": best_split_k,
            "selected": selected,
            "selection_reason": reason,
        })

        # Ground truth: only for selected targets
        if selected:
            for dr in disease_ranking:
                gt_rows.append({
                    "target_icd": input_icd,
                    "target_ontology": input_ontology_str,
                    "target_description": input_desc,
                    "self_best_auc": round(self_best_auc, 6) if has_self else None,
                    "cross_icd": dr["cross_icd"],
                    "cross_ontology": dr["cross_ontology"],
                    "cross_description": dr["cross_description"],
                    "n_pgs_models": dr["n_pgs_models"],
                    "disease_best_auc": dr["disease_best_auc"],
                    "best_pgs_id": dr["best_pgs_id"],
                    "auc_improvement": dr["auc_improvement"],
                    "best_split_gap": best_split_gap,
                    "best_split_k": best_split_k,
                    "rank": dr["rank"],
                    "total_cross_diseases": n_total_cross_diseases,
                    "beats_self": (
                        dr["auc_improvement"] > delta
                        if dr["auc_improvement"] is not None
                        else None
                    ),
                })

    return pd.DataFrame(target_rows), pd.DataFrame(gt_rows)


# ---------------------------------------------------------------------------
# Core: disease-level ground truth for binary-to-continuous
# ---------------------------------------------------------------------------

def build_b2c_benchmark(
    matrix: pd.DataFrame,
    allowed_input_icds: set[str],
    *,
    delta: float = DEFAULT_DELTA,
    k_min: int = DEFAULT_K_MIN,
    min_top_cross_auc: float = DEFAULT_MIN_TOP_CROSS_AUC,
    min_best_split_gap: float = DEFAULT_MIN_BEST_SPLIT_GAP,
    max_self_auc: float = DEFAULT_MAX_SELF_AUC,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Binary target -> continuous cross trait benchmark.

    Cross diseases are continuous traits (LOINC codes). For each target ICD,
    rank all continuous traits by their best PGS model's AUC on the target.
    """
    icd_to_self_pgs = build_icd_to_self_pgs_full()
    icd_to_ontologies = build_icd_to_ontologies_full()
    icd_desc_map = get_icd_description_map_full()
    pgs_to_continuous_trait = build_pgs_to_continuous_trait_map()

    continuous_pgs_ids = set(pgs_to_continuous_trait.keys())
    pgs_columns = list(matrix.columns)

    target_rows = []
    gt_rows = []

    for input_icd in matrix.index:
        input_icd = str(input_icd).strip()
        if input_icd not in allowed_input_icds:
            continue

        input_ontologies = icd_to_ontologies.get(input_icd, [])
        input_ontology_str = "; ".join(sorted(input_ontologies))
        input_desc = icd_desc_map.get(input_icd, "")

        self_pgs_ids = icd_to_self_pgs.get(input_icd, set())
        auc_row = matrix.loc[input_icd]
        self_best_auc, self_best_pgs = _get_self_auc_info(auc_row, self_pgs_ids)
        has_self = self_best_auc is not None

        # ------------------------------------------------------------------
        # Collect cross models from continuous-source PGS and aggregate by LOINC
        # ------------------------------------------------------------------
        # loinc -> list of (pgs_id, auc)
        trait_models: dict[str, list[tuple[str, float]]] = {}
        # loinc -> (ontology, description)
        trait_meta: dict[str, tuple[str, str]] = {}

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

            for trait_info in pgs_to_continuous_trait[pgs_id]:
                loinc = trait_info["output_loinc"]
                trait_models.setdefault(loinc, []).append((pgs_id, cross_auc))
                if loinc not in trait_meta:
                    trait_meta[loinc] = (
                        trait_info["output_ontology"],
                        trait_info["output_description"],
                    )

        # ------------------------------------------------------------------
        # Aggregate: per-LOINC best AUC
        # ------------------------------------------------------------------
        trait_ranking = []
        for loinc, models in trait_models.items():
            best_pgs, best_auc = max(models, key=lambda x: x[1])
            ont, desc = trait_meta[loinc]
            improvement = (best_auc - self_best_auc) if has_self else None

            trait_ranking.append({
                "cross_loinc": loinc,
                "cross_ontology": ont,
                "cross_description": desc,
                "n_pgs_models": len(models),
                "disease_best_auc": round(best_auc, 6),
                "best_pgs_id": best_pgs,
                "auc_improvement": round(improvement, 6) if improvement is not None else None,
            })

        trait_ranking.sort(key=lambda x: x["disease_best_auc"], reverse=True)
        for rank_idx, tr in enumerate(trait_ranking, 1):
            tr["rank"] = rank_idx

        best_split_gap, best_split_k = _get_best_split_info(trait_ranking)

        # ------------------------------------------------------------------
        # Target selection (same criteria as B2B)
        # ------------------------------------------------------------------
        n_total = len(trait_ranking)

        if has_self:
            qualifying = [
                tr for tr in trait_ranking
                if tr["auc_improvement"] is not None
                and tr["auc_improvement"] > delta
            ]
        else:
            qualifying = [
                tr for tr in trait_ranking
                if tr["disease_best_auc"] > min_top_cross_auc
            ]

        n_qualifying = len(qualifying)
        top_improvement = qualifying[0]["auc_improvement"] if (qualifying and has_self) else None
        top_cross_auc = trait_ranking[0]["disease_best_auc"] if trait_ranking else None
        has_clear_cluster = (
            best_split_gap is not None and best_split_gap >= min_best_split_gap
        )

        if has_self:
            self_auc_ok = self_best_auc < max_self_auc
            selected = (
                self_auc_ok
                and n_qualifying >= k_min
                and top_cross_auc is not None
                and top_cross_auc > min_top_cross_auc
                and has_clear_cluster
            )
            if selected:
                reason = (
                    f"self_AUC={self_best_auc:.4f}<{max_self_auc}, "
                    f"n_qualifying={n_qualifying}>=k_min({k_min}), "
                    f"top_AUC={top_cross_auc:.4f}>{min_top_cross_auc}, "
                    f"best_split_gap={best_split_gap:.4f}>={min_best_split_gap}"
                )
            else:
                reasons = []
                if not self_auc_ok:
                    reasons.append(f"self_AUC={self_best_auc:.4f}>={max_self_auc}")
                if n_qualifying < k_min:
                    reasons.append(f"n_qualifying={n_qualifying}<k_min({k_min})")
                if top_cross_auc is not None and top_cross_auc <= min_top_cross_auc:
                    reasons.append(f"top_AUC={top_cross_auc:.4f}<={min_top_cross_auc}")
                if not has_clear_cluster:
                    split_str = "NA" if best_split_gap is None else f"{best_split_gap:.4f}"
                    reasons.append(f"best_split_gap={split_str}<{min_best_split_gap}")
                if not trait_ranking:
                    reasons.append("no_cross_traits")
                reason = "; ".join(reasons) if reasons else "no_qualifying_traits"
        else:
            selected = n_qualifying >= 1 and has_clear_cluster
            if selected:
                reason = (
                    f"type_A, n_qualifying={n_qualifying}, "
                    f"best_split_gap={best_split_gap:.4f}>={min_best_split_gap}"
                )
            else:
                reasons = []
                if n_qualifying < 1:
                    reasons.append("type_A, no_cross_AUC>0.55")
                if not has_clear_cluster:
                    split_str = "NA" if best_split_gap is None else f"{best_split_gap:.4f}"
                    reasons.append(f"best_split_gap={split_str}<{min_best_split_gap}")
                reason = "; ".join(reasons) if reasons else "type_A_not_selected"

        target_rows.append({
            "input_type": "B" if has_self else "A",
            "input_icd": input_icd,
            "input_ontology": input_ontology_str,
            "input_description": input_desc,
            "self_n_models": len(self_pgs_ids),
            "self_best_auc": round(self_best_auc, 6) if has_self else None,
            "self_best_pgs": self_best_pgs,
            "n_total_cross_traits": n_total,
            "n_qualifying_traits": n_qualifying,
            "top_cross_trait_auc": round(top_cross_auc, 6) if top_cross_auc else None,
            "top_auc_improvement": round(top_improvement, 6) if top_improvement is not None else None,
            "best_split_gap": best_split_gap,
            "best_split_k": best_split_k,
            "selected": selected,
            "selection_reason": reason,
        })

        if selected:
            for tr in trait_ranking:
                gt_rows.append({
                    "target_icd": input_icd,
                    "target_ontology": input_ontology_str,
                    "target_description": input_desc,
                    "self_best_auc": round(self_best_auc, 6) if has_self else None,
                    "cross_loinc": tr["cross_loinc"],
                    "cross_ontology": tr["cross_ontology"],
                    "cross_description": tr["cross_description"],
                    "n_pgs_models": tr["n_pgs_models"],
                    "disease_best_auc": tr["disease_best_auc"],
                    "best_pgs_id": tr["best_pgs_id"],
                    "auc_improvement": tr["auc_improvement"],
                    "best_split_gap": best_split_gap,
                    "best_split_k": best_split_k,
                    "rank": tr["rank"],
                    "total_cross_traits": n_total,
                    "beats_self": (
                        tr["auc_improvement"] > delta
                        if tr["auc_improvement"] is not None
                        else None
                    ),
                })

    return pd.DataFrame(target_rows), pd.DataFrame(gt_rows)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    b2b_targets: pd.DataFrame,
    b2b_gt: pd.DataFrame,
    b2c_targets: pd.DataFrame,
    b2c_gt: pd.DataFrame,
    params: dict,
) -> str:
    lines = [
        "# Cross-Trait Transfer Benchmark Report",
        "",
        "## Selection Rules",
        "",
        "| Scenario | Rule |",
        "|----------|------|",
        f"| Type A target | No self AUC benchmark is available. Keep it only if at least one cross disease/trait reaches AUC > {params['min_top_cross_auc']:.2f}. |",
        f"| Type B target | A self AUC benchmark is available. Keep it only if self AUC < {params['max_self_auc']:.2f} and at least {params['k_min']} cross disease/trait beats self by more than {params['delta']:.3f} AUC. |",
        f"| All targets: clustering requirement | Sort cross diseases/traits by AUC, compute all adjacent gaps `AUC_k - AUC_(k+1)`, and require `best_split_gap >= {params['min_best_split_gap']:.3f}`. |",
        f"| All selected targets | The top cross disease/trait must still reach AUC > {params['min_top_cross_auc']:.2f}. |",
        "",
    ]

    for label, targets, gt, cross_unit in [
        ("Binary-to-Binary", b2b_targets, b2b_gt, "disease"),
        ("Binary-to-Continuous", b2c_targets, b2c_gt, "trait"),
    ]:
        lines.append(f"## {label}")
        lines.append("")

        n_screened = len(targets)
        n_selected = int(targets["selected"].sum()) if not targets.empty else 0
        n_type_a = int((targets["input_type"] == "A").sum()) if not targets.empty else 0
        n_type_b = int((targets["input_type"] == "B").sum()) if not targets.empty else 0
        selected_a = int(((targets["input_type"] == "A") & targets["selected"]).sum()) if not targets.empty else 0
        selected_b = int(((targets["input_type"] == "B") & targets["selected"]).sum()) if not targets.empty else 0

        lines.append(f"- Screened target traits: **{n_screened}** (Type A: {n_type_a}, Type B: {n_type_b})")
        lines.append(f"- **Selected for benchmark: {n_selected}** (Type A: {selected_a}, Type B: {selected_b})")

        lines.append("")

        # Selected targets table
        if n_selected > 0:
            sel = targets[targets["selected"]].copy()
            sel = sel.sort_values("top_auc_improvement", ascending=False, na_position="last")

            lines.append(f"### Selected Targets ({label})")
            lines.append("")

            if label == "Binary-to-Binary":
                top_name_map = _build_top_cross_name_map(
                    b2b_gt,
                    cross_desc_col="cross_description",
                )
                lines.append("| ICD | Description | Type | Qualifying Diseases | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |")
                lines.append("|-----|-------------|------|---------------------|--------------|---------------|----------------|-----------------|------------|----------|")
                for _, r in sel.iterrows():
                    self_str = f"{r['self_best_auc']:.4f}" if pd.notna(r.get("self_best_auc")) else "-"
                    top_auc = f"{r['top_cross_disease_auc']:.4f}" if pd.notna(r.get("top_cross_disease_auc")) else "-"
                    top_name = top_name_map.get(str(r["input_icd"]), "-")
                    top_imp = f"+{r['top_auc_improvement']:.4f}" if pd.notna(r.get("top_auc_improvement")) else "-"
                    split_k = f"Top-{int(r['best_split_k'])}" if pd.notna(r.get("best_split_k")) else "-"
                    split_gap = f"{r['best_split_gap']:.4f}" if pd.notna(r.get("best_split_gap")) else "-"
                    lines.append(
                        f"| {r['input_icd']} | {r['input_description'][:40]} | {r['input_type']} "
                        f"| {r['n_qualifying_diseases']} / {r['n_total_cross_diseases']} "
                        f"| {self_str} | {top_auc} | {top_name[:60]} | {top_imp} | {split_k} | {split_gap} |"
                    )
            else:
                top_name_map = _build_top_cross_name_map(
                    b2c_gt,
                    cross_desc_col="cross_description",
                )
                lines.append("| ICD | Description | Type | Qualifying Traits | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |")
                lines.append("|-----|-------------|------|-------------------|--------------|---------------|----------------|-----------------|------------|----------|")
                for _, r in sel.iterrows():
                    self_str = f"{r['self_best_auc']:.4f}" if pd.notna(r.get("self_best_auc")) else "-"
                    top_auc = f"{r['top_cross_trait_auc']:.4f}" if pd.notna(r.get("top_cross_trait_auc")) else "-"
                    top_name = top_name_map.get(str(r["input_icd"]), "-")
                    top_imp = f"+{r['top_auc_improvement']:.4f}" if pd.notna(r.get("top_auc_improvement")) else "-"
                    split_k = f"Top-{int(r['best_split_k'])}" if pd.notna(r.get("best_split_k")) else "-"
                    split_gap = f"{r['best_split_gap']:.4f}" if pd.notna(r.get("best_split_gap")) else "-"
                    lines.append(
                        f"| {r['input_icd']} | {r['input_description'][:40]} | {r['input_type']} "
                        f"| {r['n_qualifying_traits']} / {r['n_total_cross_traits']} "
                        f"| {self_str} | {top_auc} | {top_name[:60]} | {top_imp} | {split_k} | {split_gap} |"
                    )

            lines.append("")

        # Rejected targets summary
        rejected = targets[~targets["selected"]]
        if not rejected.empty:
            lines.append(f"### Rejected Targets ({label}): {len(rejected)}")
            lines.append("")
            lines.append("Primary rejection reasons:")
            lines.append("")

            if label == "Binary-to-Binary":
                rejection_summary = _summarize_rejections(
                    rejected,
                    qualifying_col="n_qualifying_diseases",
                    top_auc_col="top_cross_disease_auc",
                    cross_label="disease",
                    params=params,
                )
            else:
                rejection_summary = _summarize_rejections(
                    rejected,
                    qualifying_col="n_qualifying_traits",
                    top_auc_col="top_cross_trait_auc",
                    cross_label="trait",
                    params=params,
                )

            lines.append("| Reason | Count |")
            lines.append("|--------|-------|")
            for reason, count in rejection_summary:
                lines.append(f"| {reason} | {count} |")
            lines.append("")

    # Sensitivity note
    lines.extend([
        "## Sensitivity Analysis Note",
        "",
        "To assess robustness of target selection to parameter choices, re-run with:",
        "```",
        "python build_benchmark.py --delta 0.02  # more lenient",
        "python build_benchmark.py --delta 0.03  # more strict",
        "python build_benchmark.py --kmin 2      # require two qualifying diseases",
        "python build_benchmark.py --min-best-split-gap 0.03  # require a larger cluster break",
        "python build_benchmark.py --max-self-auc 0.58  # stricter self-AUC gate",
        "```",
        "",
        "Compare the number of selected targets and ground truth rankings across runs.",
    ])

    return "\n".join(lines) + "\n"


def _build_top_cross_name_map(
    gt: pd.DataFrame,
    *,
    cross_desc_col: str,
) -> dict[str, str]:
    if gt.empty:
        return {}

    result: dict[str, str] = {}
    for target_icd, group in gt.groupby("target_icd"):
        group = group.sort_values("rank")
        top_auc = group["disease_best_auc"].max()
        top_rows = group[group["disease_best_auc"] == top_auc]

        names: list[str] = []
        seen: set[str] = set()
        for desc in top_rows[cross_desc_col]:
            name = str(desc).strip()
            if not name or name in seen:
                continue
            seen.add(name)
            names.append(name)
            if len(names) == 2:
                break

        result[str(target_icd)] = " / ".join(names) if names else "-"

    return result


def _summarize_rejections(
    rejected: pd.DataFrame,
    *,
    qualifying_col: str,
    top_auc_col: str,
    cross_label: str,
    params: dict,
) -> list[tuple[str, int]]:
    if rejected.empty:
        return []

    summary: list[tuple[str, int]] = []

    type_a = rejected[rejected["input_type"] == "A"]
    type_a_no_cross = type_a[type_a[top_auc_col].isna() | type_a[top_auc_col].le(params["min_top_cross_auc"])]
    if not type_a_no_cross.empty:
        summary.append((
            f"Type A: no cross {cross_label} above {params['min_top_cross_auc']:.2f}",
            len(type_a_no_cross),
        ))
    type_a_cluster = type_a[~type_a.index.isin(type_a_no_cross.index)]
    if not type_a_cluster.empty:
        summary.append((
            f"Type A: best split gap < {params['min_best_split_gap']:.3f}",
            len(type_a_cluster),
        ))

    type_b = rejected[rejected["input_type"] == "B"].copy()
    if type_b.empty:
        return summary

    remaining = type_b.copy()

    self_auc_too_high = remaining["self_best_auc"].ge(params["max_self_auc"])
    if self_auc_too_high.any():
        summary.append((
            f"Type B: self AUC >= {params['max_self_auc']:.2f}",
            int(self_auc_too_high.sum()),
        ))
        remaining = remaining[~self_auc_too_high]

    insufficient_support = remaining[qualifying_col].fillna(0).lt(params["k_min"])
    if insufficient_support.any():
        if params["k_min"] == 1:
            support_label = f"Type B: no qualifying cross {cross_label}"
        else:
            support_label = (
                f"Type B: fewer than {params['k_min']} qualifying cross {cross_label}s"
            )
        summary.append((
            support_label,
            int(insufficient_support.sum()),
        ))
        remaining = remaining[~insufficient_support]

    low_top_auc = remaining[top_auc_col].isna() | remaining[top_auc_col].le(params["min_top_cross_auc"])
    if low_top_auc.any():
        summary.append((
            f"Type B: top cross {cross_label} AUC <= {params['min_top_cross_auc']:.2f}",
            int(low_top_auc.sum()),
        ))
        remaining = remaining[~low_top_auc]

    low_split_gap = (
        remaining["best_split_gap"].isna()
        | remaining["best_split_gap"].lt(params["min_best_split_gap"])
    )
    if low_split_gap.any():
        summary.append((
            f"Type B: best split gap < {params['min_best_split_gap']:.3f}",
            int(low_split_gap.sum()),
        ))
        remaining = remaining[~low_split_gap]

    if not remaining.empty:
        summary.append(("Type B: other", len(remaining)))

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Contribution3 cross-trait transfer benchmark"
    )
    parser.add_argument("--delta", type=float, default=DEFAULT_DELTA,
                        help=f"AUC improvement threshold (default: {DEFAULT_DELTA})")
    parser.add_argument("--kmin", type=int, default=DEFAULT_K_MIN,
                        help=f"Min qualifying cross diseases (default: {DEFAULT_K_MIN})")
    parser.add_argument("--min-top-cross-auc", type=float, default=DEFAULT_MIN_TOP_CROSS_AUC,
                        help=f"Clinical utility floor (default: {DEFAULT_MIN_TOP_CROSS_AUC})")
    parser.add_argument("--min-best-split-gap", type=float, default=DEFAULT_MIN_BEST_SPLIT_GAP,
                        help=f"Minimum best split gap in cross ranking (default: {DEFAULT_MIN_BEST_SPLIT_GAP})")
    parser.add_argument("--max-self-auc", type=float, default=DEFAULT_MAX_SELF_AUC,
                        help=f"Type B self AUC upper bound (default: {DEFAULT_MAX_SELF_AUC})")
    args = parser.parse_args()

    params = {
        "delta": args.delta,
        "k_min": args.kmin,
        "min_top_cross_auc": args.min_top_cross_auc,
        "min_best_split_gap": args.min_best_split_gap,
        "max_self_auc": args.max_self_auc,
    }

    B2B_DIR.mkdir(parents=True, exist_ok=True)
    B2C_DIR.mkdir(parents=True, exist_ok=True)

    # Save config
    config_path = BENCHMARK_DIR / "benchmark_config.json"
    config_path.write_text(json.dumps(params, indent=2) + "\n", encoding="utf-8")

    # ----- Binary-to-Binary -----
    print(f"\n{'='*60}")
    print("Building binary-to-binary benchmark...")
    print(f"  Parameters: delta={params['delta']}, k_min={params['k_min']}, "
          f"min_top_cross_auc={params['min_top_cross_auc']}, min_best_split_gap={params['min_best_split_gap']}, "
          f"max_self_auc={params['max_self_auc']}")
    print(f"{'='*60}")

    matrix = load_rootcode_auc_matrix()
    allowed_icds = load_main_analysis_input_icds()

    b2b_targets, b2b_gt = build_b2b_benchmark(
        matrix, allowed_icds,
        delta=params["delta"],
        k_min=params["k_min"],
        min_top_cross_auc=params["min_top_cross_auc"],
        min_best_split_gap=params["min_best_split_gap"],
        max_self_auc=params["max_self_auc"],
    )

    b2b_targets.to_csv(B2B_DIR / "target_selection.csv", index=False)
    b2b_gt.to_csv(B2B_DIR / "ground_truth_ranking.csv", index=False)

    n_sel_b2b = int(b2b_targets["selected"].sum()) if not b2b_targets.empty else 0
    n_gt_b2b = len(b2b_gt)
    print(f"  Screened: {len(b2b_targets)} targets")
    print(f"  Selected: {n_sel_b2b} targets")
    print(f"  Ground truth: {n_gt_b2b} disease-level ranking rows")

    # ----- Binary-to-Continuous -----
    print(f"\n{'='*60}")
    print("Building binary-to-continuous benchmark...")
    print(f"{'='*60}")

    b2c_targets, b2c_gt = build_b2c_benchmark(
        matrix, allowed_icds,
        delta=params["delta"],
        k_min=params["k_min"],
        min_top_cross_auc=params["min_top_cross_auc"],
        min_best_split_gap=params["min_best_split_gap"],
        max_self_auc=params["max_self_auc"],
    )

    b2c_targets.to_csv(B2C_DIR / "target_selection.csv", index=False)
    b2c_gt.to_csv(B2C_DIR / "ground_truth_ranking.csv", index=False)

    n_sel_b2c = int(b2c_targets["selected"].sum()) if not b2c_targets.empty else 0
    n_gt_b2c = len(b2c_gt)
    print(f"  Screened: {len(b2c_targets)} targets")
    print(f"  Selected: {n_sel_b2c} targets")
    print(f"  Ground truth: {n_gt_b2c} trait-level ranking rows")

    # ----- Report -----
    report = generate_report(b2b_targets, b2b_gt, b2c_targets, b2c_gt, params)
    report_path = BENCHMARK_DIR / "benchmark_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Benchmark complete.")
    print(f"  B2B: {n_sel_b2b} targets, {n_gt_b2b} ground truth rows")
    print(f"  B2C: {n_sel_b2c} targets, {n_gt_b2c} ground truth rows")
    print(f"  Report: {report_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
