"""Offline simulation for unified TransferConfig on the new 80-target set.

Goal
----
Find a single TransferConfig that maximises exact oracle hits across the 80 ICD
targets in union_selected_icds.json, without distinguishing binary_to_binary vs
binary_to_continuous at runtime.

Data availability
-----------------
Only 42 of 80 targets have frozen run data (19 from b2b-only, 21 from b2c-only,
2 shared E08/J33). The remaining 38 will need LLM runs and are NOT evaluated here.

Mode: fast_full only (pre-cached evidence, analytical scoring).
Does NOT call any LLM or online tool.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from experiments.contribution3.transfer.agent import (
    BINARY_TO_BINARY_CONFIG,
    BINARY_TO_CONTINUOUS_CONFIG,
    UNIFIED_CONFIG,
    TransferConfig,
    _is_significant_gc,
)
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    TargetTraitQuery,
    TraitBundle,
    is_self_like_bundle,
    load_candidate_dossiers,
    load_trait_bundle_index,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import CandidateEvidenceCard

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BENCHMARK_DIR = PROJECT_ROOT / "experiments/contribution3/cross_list/benchmark_contrib1_latest"
TARGET_LIST_JSON = BENCHMARK_DIR / "union_selected_icds.json"

ROOTCODE_AUC_MATRIX = (
    PROJECT_ROOT / "experiments/contribution1/result/aou_binary"
    / "prs_adjauc_matrix_binary_combined_rootcode.csv"
)
NONTARGET_AUC_MATRIX = (
    PROJECT_ROOT / "experiments/contribution1/result/aou_extend_trait"
    / "prs_adjauc_matrix_binary_extend_qc.csv"
)

B2B_RESULTS = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_binary"
    / "all-tools__20260412_212843/results.json"
)
B2C_RESULTS = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_continuous"
    / "all-tools__20260412_232811/results.json"
)
B2B_DOSSIERS = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_binary"
    / "candidate_dossiers.json"
)
B2C_DOSSIERS = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_continuous"
    / "candidate_dossiers.json"
)


# ---------------------------------------------------------------------------
# BundleCache – config-invariant pre-extracted evidence
# ---------------------------------------------------------------------------

@dataclass
class BundleCache:
    bundle_id: str
    is_oracle: bool
    archetype: str
    fidelity: float
    lexical: int
    tokens: int
    n_models: int
    prior: float
    is_proxy: bool
    n_models_50: int
    model_support: float
    anti_dom: float
    model_ok: bool
    model_low: bool
    has_gc: bool
    rg: float
    rg_abs: float
    p_sig: bool
    gc_raw_discount: float
    has_ot: bool
    ot_overlap: float
    ot_count: int
    ot_conf_hm: bool
    ot_genetic: bool
    ot_lit_dom: bool
    ot_ta_match: bool
    ot_ta_both: bool
    ot_ancestors: int
    ot_phenotype: float
    ot_no_shared: bool
    has_h2: bool
    h2_ceiling: float


def _gc_raw_discount(gc) -> float:
    if gc is None:
        return 0.0
    if getattr(gc, "source", "gwas_atlas") == "llm_estimated":
        return {"High": 1.0, "Moderate": 0.7, "Low": 0.3}.get(
            getattr(gc, "confidence", None) or "", 0.0
        )
    mult = 1.0
    for res in (gc.target_resolution, gc.candidate_resolution):
        if res is None:
            continue
        conf = getattr(res, "confidence", "Unresolved")
        if conf == "High":
            pass
        elif conf == "Moderate":
            mult *= 0.7
        elif conf == "Low":
            mult *= 0.3
        else:
            mult *= 0.0
    return mult


def _precompute_bundle_cache(
    cards: list[CandidateEvidenceCard],
    oracle_id: str,
) -> list[BundleCache]:
    out = []
    for card in cards:
        gc = card.gc
        h2 = card.h2
        ot = card.open_targets
        n = card.n_models

        rg_val = float(gc.rg) if gc and gc.rg is not None else 0.0
        p_sig = _is_significant_gc(gc)
        gc_disc = _gc_raw_discount(gc) if gc else 0.0

        ot_ov = float(ot.weighted_shared_target_overlap_score) if ot else 0.0
        ot_cnt = int(ot.shared_target_count) if ot else 0
        ot_chm = bool(ot and ot.confidence_level in {"High", "Moderate"})
        ot_gen = bool(ot and ot.genetic_support_present)
        ot_ld = bool(ot and ot.literature_dominance_warning)
        ot_ta = bool(ot and ot.therapeutic_area_match)
        ot_tab = bool(ot and ot.source_therapeutic_areas and ot.candidate_therapeutic_areas)
        ot_anc = int(ot.shared_ancestor_count) if ot else 0
        ot_ph = float(ot.phenotype_overlap_score) if ot else 0.0
        ot_ns = bool(ot and ot.pair_status == "no_shared_targets")

        if h2:
            cap = float(h2.candidate_signal_capacity or 0.0)
            ceil = float(h2.shared_signal_ceiling_proxy or cap)
            h2_c = max(cap, ceil)
        else:
            h2_c = 0.0

        out.append(BundleCache(
            bundle_id=card.bundle_id,
            is_oracle=(card.bundle_id == oracle_id),
            archetype=card.archetype,
            fidelity=card.phenotype_fidelity_score,
            lexical=card.lexical_match_score,
            tokens=card.shared_token_count,
            n_models=n,
            prior=card.transferability_prior_score,
            is_proxy=(card.archetype == "administrative/exposure/treatment/family-history proxy"),
            n_models_50=min(n, 50),
            model_support=math.log1p(min(max(n, 0), 100)),
            anti_dom=math.log(n / 50) if n > 50 else 0.0,
            model_ok=(n >= 5),
            model_low=(n < 3),
            has_gc=(gc is not None and gc.rg is not None),
            rg=rg_val,
            rg_abs=abs(rg_val),
            p_sig=p_sig,
            gc_raw_discount=gc_disc,
            has_ot=(ot is not None),
            ot_overlap=ot_ov,
            ot_count=ot_cnt,
            ot_conf_hm=ot_chm,
            ot_genetic=ot_gen,
            ot_lit_dom=ot_ld,
            ot_ta_match=ot_ta,
            ot_ta_both=ot_tab,
            ot_ancestors=ot_anc,
            ot_phenotype=ot_ph,
            ot_no_shared=ot_ns,
            has_h2=(h2 is not None),
            h2_ceiling=h2_c,
        ))
    return out


# ---------------------------------------------------------------------------
# Analytical scoring (mirrors _score_bundle_fast from offline_tune_unified_config)
# ---------------------------------------------------------------------------

def score_bundle(b: BundleCache, cfg: TransferConfig) -> float:
    # GC discount
    if cfg.apply_gc_resolution_discount and b.has_gc:
        gc_d = max(b.gc_raw_discount, cfg.gc_discount_floor)
    else:
        gc_d = 1.0 if b.has_gc else 0.0

    # cheap_rank
    cheap = b.fidelity * 2.0 + b.n_models_50 / 80.0 + b.lexical / 250.0 + b.tokens * 0.08
    if b.has_gc:
        gc_m = cfg.gc_cheap_rank_significant if b.p_sig else cfg.gc_cheap_rank_nonsignificant
        cheap += b.rg_abs * gc_m * gc_d
    if b.is_proxy:
        cheap -= 1.4

    # statistical_overlap
    if b.has_gc:
        if b.p_sig:
            stat = min(1.5, b.rg_abs / 0.20)
        else:
            stat = min(0.5, b.rg_abs / 0.40)
        stat *= gc_d
    else:
        stat = 0.0

    # mechanistic_overlap
    if b.has_ot:
        mech = min(1.5, b.ot_overlap / 0.30)
        if b.ot_lit_dom:
            mech = max(0.0, mech - 0.25)
        if not b.ot_ta_match and b.ot_ta_both:
            mech *= 0.4
        if b.ot_ancestors >= 3:
            mech += 0.3
        elif b.ot_ancestors >= 1:
            mech += 0.1
        if b.ot_phenotype >= 0.15:
            mech += 0.35
        elif b.ot_phenotype >= 0.05:
            mech += 0.15
    else:
        mech = 0.0

    # signal_capacity
    sig = min(1.0, b.h2_ceiling / 0.010) if b.has_h2 else 0.0

    # utility
    util = (stat * cfg.w_statistical_overlap
            + mech * cfg.w_mechanistic_overlap
            + sig * cfg.w_signal_capacity
            + b.fidelity * cfg.w_phenotype_fidelity)

    # concordance
    gc_strong = b.has_gc and b.p_sig and b.rg_abs >= 0.30 and gc_d > 0
    ot_strong = b.has_ot and b.ot_conf_hm and b.ot_genetic and b.ot_overlap >= 0.35
    ot_supp = b.has_ot and b.ot_overlap >= 0.20 and b.ot_count >= 1
    if gc_strong and ot_strong:
        util += cfg.concordance_bonus
    elif b.has_gc and b.p_sig and ot_supp and not gc_strong:
        util += cfg.concordance_bonus * 0.5
    elif gc_strong and b.ot_no_shared and not ot_supp:
        util += cfg.concordance_penalty

    if b.model_ok:
        util += 0.15
    elif b.model_low:
        util -= 0.2
    if b.is_proxy:
        util -= 1.6

    # selection priority
    score = (cfg.w_transferability_prior * b.prior
             + cfg.w_selection_utility * util
             + cfg.w_selection_cheap_rank * cheap
             + cfg.w_selection_fidelity * b.fidelity
             + cfg.w_selection_model_support * b.model_support)
    if cfg.w_selection_anti_dominance > 0.0 and b.n_models > 50:
        score -= cfg.w_selection_anti_dominance * b.anti_dom
    if cfg.w_ot_exceptional > 0.0 and b.ot_overlap > 2.0:
        score += cfg.w_ot_exceptional * (b.ot_overlap - 2.0)
    return score


def select_primary(bundles: list[BundleCache], cfg: TransferConfig) -> str | None:
    if not bundles:
        return None
    best = max(bundles, key=lambda b: score_bundle(b, cfg))
    return best.bundle_id


# ---------------------------------------------------------------------------
# Oracle computation (directly from AUC matrices)
# ---------------------------------------------------------------------------

_AUC_CACHE: dict[str, pd.DataFrame] = {}


def _col_to_pgs_id(col: str) -> str:
    text = str(col).strip()
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


def _load_auc_matrix(source: str) -> pd.DataFrame:
    if source in _AUC_CACHE:
        return _AUC_CACHE[source]
    path = NONTARGET_AUC_MATRIX if source == "nontarget_pgs" else ROOTCODE_AUC_MATRIX
    mat = pd.read_csv(path, index_col=0)
    mat.columns = [_col_to_pgs_id(c) for c in mat.columns]
    _AUC_CACHE[source] = mat
    return mat


def _resolve_target_source(target_id: str) -> str:
    """Determine which AUC matrix contains this target. Prefer rootcode."""
    rootcode = _load_auc_matrix("rootcode_main_analysis")
    if target_id in rootcode.index:
        return "rootcode_main_analysis"
    nontarget = _load_auc_matrix("nontarget_pgs")
    if target_id in nontarget.index:
        return "nontarget_pgs"
    raise KeyError(f"Target {target_id} not in any AUC matrix")


_BUNDLE_INDEX: list[TraitBundle] | None = None


def _get_bundle_index() -> dict[str, TraitBundle]:
    global _BUNDLE_INDEX
    if _BUNDLE_INDEX is None:
        _BUNDLE_INDEX = load_trait_bundle_index()
    return {b.bundle_id: b for b in _BUNDLE_INDEX}


def _competition_ranks(auc_by_bundle: dict[str, float]) -> dict[str, int]:
    ranked = sorted(auc_by_bundle, key=lambda bid: (-auc_by_bundle[bid], bid))
    ranks: dict[str, int] = {}
    prev_auc: float | None = None
    current_rank = 0
    for idx, bid in enumerate(ranked, start=1):
        auc = auc_by_bundle[bid]
        if prev_auc is None or auc != prev_auc:
            current_rank = idx
            prev_auc = auc
        ranks[bid] = current_rank
    return ranks


def _compute_oracle(
    target_id: str,
    target: TargetTraitQuery,
    target_source: str,
) -> tuple[str | None, int | None]:
    """Find best non-self bundle by AUC rank."""
    mat = _load_auc_matrix(target_source)
    if target_id not in mat.index:
        return None, None

    auc_row = mat.loc[target_id]
    auc_by_pgs = {str(pid): float(v) for pid, v in auc_row.items() if pd.notna(v)}

    bundle_index = _get_bundle_index()
    auc_by_bundle: dict[str, float] = {}
    for bid, bundle in bundle_index.items():
        vals = [auc_by_pgs[pid] for pid in bundle.candidate_pgs_ids if pid in auc_by_pgs]
        if vals:
            auc_by_bundle[bid] = max(vals)

    ranks = _competition_ranks(auc_by_bundle)

    candidates = []
    for bid, rank in ranks.items():
        bundle = bundle_index.get(bid)
        if bundle is None or is_self_like_bundle(target, bundle):
            continue
        candidates.append((bid, rank))
    if not candidates:
        return None, None
    bid, rank = min(candidates, key=lambda x: (x[1], x[0]))
    return bid, rank


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _cards_from_row(row: dict) -> list[CandidateEvidenceCard]:
    decision = row.get("decision") or {}
    raw = (decision.get("evidence_state") or {}).get("candidate_cards") or []
    return [CandidateEvidenceCard.model_validate(c) for c in raw]


def _load_results(results_path: Path) -> dict[str, dict]:
    results = json.loads(results_path.read_text())
    return {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results
        if (r.get("target") or {}).get("target_id")
    }


def _load_dossier_targets(dossiers_path: Path) -> dict[str, TargetTraitQuery]:
    """Load dossiers and extract TargetTraitQuery for oracle computation."""
    dossiers = load_candidate_dossiers(dossiers_path)
    return {d.target.target_id: d.target for d in dossiers}


# ---------------------------------------------------------------------------
# Prepared records
# ---------------------------------------------------------------------------

# (tid, bundle_caches, oracle_id, source_family)
PreparedRecord = tuple[str, list[BundleCache], str, str]


def build_prepared(
    b2b_results: dict[str, dict],
    b2c_results: dict[str, dict],
    b2b_targets: dict[str, TargetTraitQuery],
    b2c_targets: dict[str, TargetTraitQuery],
    target_ids: set[str],
) -> list[PreparedRecord]:
    """Build prepared set: only targets in target_ids, prefer b2b for shared."""
    out: list[PreparedRecord] = []
    seen: set[str] = set()

    # B2B first (includes shared targets like E08, J33)
    for tid in sorted(b2b_results):
        if tid not in target_ids:
            continue
        row = b2b_results[tid]
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        target_q = b2b_targets.get(tid)
        if target_q is None:
            continue
        try:
            target_source = _resolve_target_source(tid)
        except KeyError:
            continue
        oracle_id, _ = _compute_oracle(tid, target_q, target_source)
        if not oracle_id:
            continue
        cards = _cards_from_row(row)
        if oracle_id not in {c.bundle_id for c in cards}:
            continue
        caches = _precompute_bundle_cache(cards, oracle_id)
        seen.add(tid)
        out.append((tid, caches, oracle_id, "b2b"))

    # B2C (skip already-seen)
    for tid in sorted(b2c_results):
        if tid in seen or tid not in target_ids:
            continue
        row = b2c_results[tid]
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        target_q = b2c_targets.get(tid)
        if target_q is None:
            continue
        try:
            target_source = _resolve_target_source(tid)
        except KeyError:
            continue
        oracle_id, _ = _compute_oracle(tid, target_q, target_source)
        if not oracle_id:
            continue
        cards = _cards_from_row(row)
        if oracle_id not in {c.bundle_id for c in cards}:
            continue
        caches = _precompute_bundle_cache(cards, oracle_id)
        seen.add(tid)
        out.append((tid, caches, oracle_id, "b2c"))

    return out


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(prepared: list[PreparedRecord], cfg: TransferConfig) -> tuple[int, set[str]]:
    hits: set[str] = set()
    for tid, caches, oracle_id, _ in prepared:
        primary = select_primary(caches, cfg)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


def evaluate_split(prepared: list[PreparedRecord]) -> tuple[int, set[str]]:
    """Reference baseline: use original b2b/b2c config per source family."""
    hits: set[str] = set()
    for tid, caches, oracle_id, fam in prepared:
        cfg = BINARY_TO_CONTINUOUS_CONFIG if fam == "b2c" else BINARY_TO_BINARY_CONFIG
        primary = select_primary(caches, cfg)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


# ---------------------------------------------------------------------------
# Config sampling
# ---------------------------------------------------------------------------

def sample_full_config(rng: random.Random) -> TransferConfig:
    return TransferConfig(
        w_statistical_overlap=rng.uniform(0.5, 4.5),
        w_mechanistic_overlap=rng.uniform(0.5, 4.5),
        w_signal_capacity=rng.uniform(0.2, 2.0),
        w_phenotype_fidelity=rng.uniform(1.0, 5.0),
        concordance_bonus=rng.uniform(0.2, 1.4),
        concordance_penalty=rng.uniform(-0.9, -0.1),
        gc_cheap_rank_significant=rng.uniform(0.5, 3.5),
        gc_cheap_rank_nonsignificant=rng.uniform(0.1, 1.5),
        apply_gc_resolution_discount=True,
        gc_discount_floor=rng.uniform(0.0, 0.5),
        shortlist_strategy=rng.choice(["dual_track", "gc_first"]),
        shortlist_cap=52,
        gc_track_size=8,
        semantic_track_size=12,
        prior_track_size=10,
        selection_track_size=32,
        support_track_size=10,
        allow_ot_promotion=False,
        w_transferability_prior=10 ** rng.uniform(-2.0, 0.7),
        w_selection_utility=10 ** rng.uniform(-3.0, -0.3),
        w_selection_cheap_rank=rng.uniform(0.005, 0.15),
        w_selection_fidelity=rng.uniform(0.01, 0.18),
        w_selection_model_support=rng.uniform(0.0003, 0.03),
        w_selection_anti_dominance=rng.uniform(0.0, 0.15),
        w_ot_exceptional=rng.uniform(0.0, 0.25),
    )


# ---------------------------------------------------------------------------
# Perturb-around-best (local search phase)
# ---------------------------------------------------------------------------

def _perturb_config(rng: random.Random, base: TransferConfig, scale: float = 0.15) -> TransferConfig:
    """Small random perturbation around a base config."""
    def u(val, lo, hi):
        delta = (hi - lo) * scale
        return max(lo, min(hi, val + rng.uniform(-delta, delta)))

    def log_u(val, lo_exp, hi_exp):
        log_val = math.log10(max(val, 1e-6))
        delta = (hi_exp - lo_exp) * scale
        new_log = max(lo_exp, min(hi_exp, log_val + rng.uniform(-delta, delta)))
        return 10 ** new_log

    return TransferConfig(
        w_statistical_overlap=u(base.w_statistical_overlap, 0.5, 4.5),
        w_mechanistic_overlap=u(base.w_mechanistic_overlap, 0.5, 4.5),
        w_signal_capacity=u(base.w_signal_capacity, 0.2, 2.0),
        w_phenotype_fidelity=u(base.w_phenotype_fidelity, 1.0, 5.0),
        concordance_bonus=u(base.concordance_bonus, 0.2, 1.4),
        concordance_penalty=u(base.concordance_penalty, -0.9, -0.1),
        gc_cheap_rank_significant=u(base.gc_cheap_rank_significant, 0.5, 3.5),
        gc_cheap_rank_nonsignificant=u(base.gc_cheap_rank_nonsignificant, 0.1, 1.5),
        apply_gc_resolution_discount=True,
        gc_discount_floor=u(base.gc_discount_floor, 0.0, 0.5),
        shortlist_strategy=base.shortlist_strategy,
        shortlist_cap=52,
        gc_track_size=8,
        semantic_track_size=12,
        prior_track_size=10,
        selection_track_size=32,
        support_track_size=10,
        allow_ot_promotion=False,
        w_transferability_prior=log_u(base.w_transferability_prior, -2.0, 0.7),
        w_selection_utility=log_u(base.w_selection_utility, -3.0, -0.3),
        w_selection_cheap_rank=u(base.w_selection_cheap_rank, 0.005, 0.15),
        w_selection_fidelity=u(base.w_selection_fidelity, 0.01, 0.18),
        w_selection_model_support=u(base.w_selection_model_support, 0.0003, 0.03),
        w_selection_anti_dominance=u(base.w_selection_anti_dominance, 0.0, 0.15),
        w_ot_exceptional=u(base.w_ot_exceptional, 0.0, 0.25),
    )


# ---------------------------------------------------------------------------
# Per-target diagnostic
# ---------------------------------------------------------------------------

def print_per_target_detail(
    prepared: list[PreparedRecord],
    cfg: TransferConfig,
) -> None:
    """Print per-target: oracle_id, selected_id, match, top-3 scores."""
    print(f"\n{'tid':<6} {'oracle':<30} {'selected':<30} {'match':<6} {'oracle_score':>12} {'selected_score':>14}")
    print("-" * 110)
    for tid, caches, oracle_id, fam in sorted(prepared, key=lambda r: r[0]):
        primary = select_primary(caches, cfg)
        match = "HIT" if primary == oracle_id else "MISS"
        oracle_score = next((score_bundle(b, cfg) for b in caches if b.bundle_id == oracle_id), 0.0)
        selected_score = next((score_bundle(b, cfg) for b in caches if b.bundle_id == primary), 0.0)
        oracle_short = oracle_id[:28] if oracle_id else "?"
        selected_short = (primary or "?")[:28]
        print(f"{tid:<6} {oracle_short:<30} {selected_short:<30} {match:<6} {oracle_score:>12.6f} {selected_score:>14.6f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Offline unified config tuning for 80 targets.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trials", type=int, default=500_000, help="Random search trials (phase 1).")
    parser.add_argument("--local-trials", type=int, default=200_000, help="Local perturbation trials (phase 2).")
    args = parser.parse_args()

    print(f"=== offline_tune_80targets  seed={args.seed}  trials={args.trials}  local={args.local_trials} ===")

    # Load target list
    target_ids_80 = set(json.loads(TARGET_LIST_JSON.read_text()))
    print(f"\nTarget list: {len(target_ids_80)} ICD codes")

    # Load frozen run data
    print("\n[1/5] Loading frozen run data and computing oracle from AUC matrices...")
    b2b_results = _load_results(B2B_RESULTS)
    b2c_results = _load_results(B2C_RESULTS)
    b2b_targets = _load_dossier_targets(B2B_DOSSIERS)
    b2c_targets = _load_dossier_targets(B2C_DOSSIERS)

    b2b_tids = set(b2b_results) & target_ids_80
    b2c_tids = set(b2c_results) & target_ids_80
    shared_tids = b2b_tids & b2c_tids
    covered_tids = b2b_tids | b2c_tids
    uncovered_tids = target_ids_80 - covered_tids

    print(f"  B2B targets in 80-list: {len(b2b_tids)}")
    print(f"  B2C targets in 80-list: {len(b2c_tids)}")
    print(f"  Shared: {len(shared_tids)} ({', '.join(sorted(shared_tids))})")
    print(f"  Covered: {len(covered_tids)}/80")
    print(f"  Uncovered (no frozen data): {len(uncovered_tids)} → {', '.join(sorted(uncovered_tids))}")

    # Build prepared set
    print("\n[2/5] Building prepared set (oracle must be in frozen shortlist)...")
    prepared = build_prepared(b2b_results, b2c_results, b2b_targets, b2c_targets, target_ids_80)
    n_prep = len(prepared)
    print(f"  Achievable targets (oracle in frozen shortlist): {n_prep}")
    for tid, _, oracle_id, fam in sorted(prepared, key=lambda r: r[0]):
        print(f"    {tid:<6} oracle={oracle_id:<35} source={fam}")

    unreachable = covered_tids - {r[0] for r in prepared}
    if unreachable:
        print(f"  Unreachable (oracle NOT in frozen shortlist): {len(unreachable)} → {', '.join(sorted(unreachable))}")

    # Baselines
    print("\n[3/5] Computing baselines...")
    n_split, hits_split = evaluate_split(prepared)
    n_b2b, hits_b2b = evaluate(prepared, BINARY_TO_BINARY_CONFIG)
    n_b2c, hits_b2c = evaluate(prepared, BINARY_TO_CONTINUOUS_CONFIG)
    n_unified, hits_unified = evaluate(prepared, UNIFIED_CONFIG)

    print(f"  Split config (b2b→B2B, b2c→B2C): {n_split}/{n_prep}")
    print(f"    hits: {', '.join(sorted(hits_split))}")
    print(f"  B2B config on all:                {n_b2b}/{n_prep}")
    print(f"    hits: {', '.join(sorted(hits_b2b))}")
    print(f"  B2C config on all:                {n_b2c}/{n_prep}")
    print(f"    hits: {', '.join(sorted(hits_b2c))}")
    print(f"  Current UNIFIED_CONFIG on all:    {n_unified}/{n_prep}")
    print(f"    hits: {', '.join(sorted(hits_unified))}")

    # Phase 1: Global random search — start from best single config (not split)
    best_n = 0
    best_hits: set[str] = set()
    best_cfg = UNIFIED_CONFIG

    for label, cfg, n, hits in [
        ("B2B", BINARY_TO_BINARY_CONFIG, n_b2b, hits_b2b),
        ("B2C", BINARY_TO_CONTINUOUS_CONFIG, n_b2c, hits_b2c),
        ("UNIFIED", UNIFIED_CONFIG, n_unified, hits_unified),
    ]:
        if n > best_n:
            best_n, best_hits, best_cfg = n, hits, cfg
    print(f"  Best single-config baseline: {best_n}/{n_prep}")
    print(f"  Split reference (upper bound guide): {n_split}/{n_prep}")

    print(f"\n[4/5] Phase 1: Global random search ({args.trials:,} trials)...")
    rng = random.Random(args.seed)

    for t in range(args.trials):
        cfg = sample_full_config(rng)
        n, hits = evaluate(prepared, cfg)
        if n > best_n:
            best_n, best_hits, best_cfg = n, hits, cfg
            print(f"  [trial {t:>8,}] new best {best_n}/{n_prep}: {', '.join(sorted(best_hits))}")

    print(f"\n  Phase 1 result: {best_n}/{n_prep}")
    print(f"  Matched: {', '.join(sorted(best_hits))}")

    # Phase 2: Local perturbation around best
    print(f"\n[5/5] Phase 2: Local perturbation ({args.local_trials:,} trials)...")
    rng2 = random.Random(args.seed + 1)

    for t in range(args.local_trials):
        # Alternate between small and medium perturbations
        scale = 0.05 if t % 3 == 0 else (0.15 if t % 3 == 1 else 0.30)
        cfg = _perturb_config(rng2, best_cfg, scale=scale)
        n, hits = evaluate(prepared, cfg)
        if n > best_n:
            best_n, best_hits, best_cfg = n, hits, cfg
            print(f"  [local {t:>8,}] new best {best_n}/{n_prep}: {', '.join(sorted(best_hits))}")

    # Final report
    print(f"\n{'='*80}")
    print(f"FINAL RESULT: {best_n}/{n_prep} achievable  ({best_n}/80 total)")
    print(f"{'='*80}")
    print(f"Matched: {', '.join(sorted(best_hits))}")

    missed = sorted(r[0] for r in prepared if r[0] not in best_hits)
    print(f"Missed (achievable but not won): {', '.join(missed)}")

    gained = sorted(best_hits - hits_split)
    lost = sorted(hits_split - best_hits)
    print(f"Gained vs split: {', '.join(gained) or '(none)'}")
    print(f"Lost vs split:   {', '.join(lost) or '(none)'}")

    print(f"\nBest unified config (16 params):")
    fields = [
        "w_statistical_overlap", "w_mechanistic_overlap", "w_signal_capacity",
        "w_phenotype_fidelity", "concordance_bonus", "concordance_penalty",
        "gc_cheap_rank_significant", "gc_cheap_rank_nonsignificant",
        "gc_discount_floor", "shortlist_strategy",
        "w_transferability_prior", "w_selection_utility",
        "w_selection_cheap_rank", "w_selection_fidelity",
        "w_selection_model_support", "w_selection_anti_dominance",
        "w_ot_exceptional",
    ]
    for f in fields:
        val = getattr(best_cfg, f)
        if isinstance(val, float):
            print(f"  {f} = {val:.6f}")
        else:
            print(f"  {f} = {val!r}")

    # Per-target detail
    print_per_target_detail(prepared, best_cfg)

    # Output config as Python literal for copy-paste into agent.py
    print(f"\n\n# --- Copy-paste config for agent.py ---")
    print(f"UNIFIED_CONFIG = TransferConfig(")
    for f in fields:
        val = getattr(best_cfg, f)
        if isinstance(val, float):
            print(f"    {f}={val:.6f},")
        else:
            print(f"    {f}={val!r},")
    # Fixed structural params
    print(f"    shortlist_cap=52,")
    print(f"    gc_track_size=8,")
    print(f"    semantic_track_size=12,")
    print(f"    prior_track_size=10,")
    print(f"    selection_track_size=32,")
    print(f"    support_track_size=10,")
    print(f"    apply_gc_resolution_discount=True,")
    print(f"    allow_ot_promotion=False,")
    print(f")")


if __name__ == "__main__":
    main()
