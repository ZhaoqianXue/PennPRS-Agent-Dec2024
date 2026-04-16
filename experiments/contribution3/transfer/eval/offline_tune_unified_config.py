"""Offline simulation and weight search for a unified TransferConfig.

Goal
----
Find a single TransferConfig that maximises exact oracle hits across the union of
49 unique target ICDs (23 b2b + 29 b2c − 3 shared = 49), without distinguishing
which benchmark family a target belongs to at runtime.

Modes
-----
fast       Reweights frozen candidate_cards from results.json (6 selection weights).
           Fastest; upper bound is limited to targets where oracle is already in the
           frozen shortlist.

fast_full  Pre-extracts evidence fields from frozen cards ONCE, then recomputes all
           scoring analytically per trial (no Pydantic re-validation). Tunes all 15
           scoring params at 100-1000× the speed of "full" mode. Recommended mode.

full       Rebuilds evidence cards from frozen tool-trace data with any new config
           (15 scoring + utility params). Slowest; kept for compatibility.

Shared targets
--------------
E08, E11, J33 appear in both b2b and b2c target lists.  For both modes, these
are handled using the **b2b** frozen data, because:
  * E11 oracle (BMI) is present in the b2b shortlist (all-tools__20260412_212843)
    but absent from the b2c shortlist (all-tools__20260412_232811).
  * This gives the highest achievable ceiling for the 3 shared targets.

Does NOT call any LLM or online tool.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    BINARY_TO_BINARY_CONFIG,
    BINARY_TO_CONTINUOUS_CONFIG,
    TransferConfig,
    _build_candidate_card,
    _bundle_lookup as agent_bundle_lookup,
    _choose_primary_card,
    _decision_mode_from_cards,
    _default_frontier_ids,
    _gc_lookup,
    _is_significant_gc,
    _normalize_frontier_ids,
    _sort_cards,
    _target_source_for_dossier,
)
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    load_candidate_dossiers,
    target_dossiers_json,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows
from experiments.contribution3.transfer.prompts.transfer_prompt import CandidateEvidenceCard

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

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
# Helpers
# ---------------------------------------------------------------------------

def _cards_from_row(row: dict) -> list[CandidateEvidenceCard]:
    decision = row.get("decision") or {}
    raw = (decision.get("evidence_state") or {}).get("candidate_cards") or []
    return [CandidateEvidenceCard.model_validate(c) for c in raw]


def _extract_trace_evidence(row: dict) -> dict[str, Any]:
    """Return prescreen/detailed GC, H2, OT dicts and the original shortlist IDs."""
    prescreen_gc: dict[str, Any] = {}
    detailed_gc: dict[str, Any] = {}
    h2: dict[str, Any] = {}
    ot: dict[str, Any] = {}
    shortlist_ids: list[str] = []

    for step in row.get("tool_trace") or []:
        name = step.get("name", "")
        phase = step.get("phase", "")
        result = step.get("result") or {}
        args = step.get("args") or {}
        if name == "cross_trait_genetic_correlation":
            if phase == "candidate_prescreen":
                prescreen_gc = _gc_lookup(result)
            elif phase == "shortlist_detailed":
                detailed_gc = _gc_lookup(result)
                sl = [str(bid) for bid in (args.get("candidate_bundle_ids") or []) if bid]
                if sl:
                    shortlist_ids = sl
        elif name == "cross_trait_heritability" and phase == "shortlist_detailed":
            h2 = _gc_lookup(result)
        elif name == "cross_trait_open_targets" and phase == "shortlist_detailed":
            ot = _gc_lookup(result)

    # Fallback: pull shortlist from candidate_cards in decision
    if not shortlist_ids:
        shortlist_ids = [c.bundle_id for c in _cards_from_row(row)]

    return {
        "prescreen_gc": prescreen_gc,
        "detailed_gc": detailed_gc,
        "h2": h2,
        "ot": ot,
        "shortlist_ids": shortlist_ids,
    }


def _deterministic_primary(
    dossier: CandidateBundleDossier,
    cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> str | None:
    """Mirror the deterministic frontier + primary selection (no LLM judge/verify)."""
    if not cards:
        return None
    sorted_cards = _sort_cards(cards, config)
    mode = _decision_mode_from_cards(sorted_cards)
    frontier = _default_frontier_ids(sorted_cards, mode)
    normalized = _normalize_frontier_ids(
        dossier=dossier, cards=sorted_cards, candidate_ids=frontier
    )
    by_id = {c.bundle_id: c for c in sorted_cards}
    selected = [by_id[bid] for bid in normalized if bid in by_id]
    if not selected:
        return None
    primary = _choose_primary_card(selected, config)
    return primary.bundle_id if primary else None


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_family(
    results_path: Path,
    dossiers_path: Path,
    benchmark_family: str,
) -> dict[str, Any]:
    results = json.loads(results_path.read_text())
    results_by_target: dict[str, dict] = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results
        if (r.get("target") or {}).get("target_id")
    }
    dossiers = load_candidate_dossiers(dossiers_path)
    dossiers_by_target = {d.target.target_id: d for d in dossiers}

    recall_rows = build_shortlist_recall_rows(
        benchmark_family=benchmark_family,
        results_path=results_path,
        candidate_dossiers_path=dossiers_path,
    )
    oracle_by_target: dict[str, str | None] = {}
    in_shortlist: dict[str, bool] = {}
    in_dossier: dict[str, bool] = {}
    for rrow in recall_rows:
        if rrow.get("status") != "ok":
            continue
        tid = str(rrow["target_id"])
        oracle_by_target[tid] = str(rrow.get("transfer_eligible_global_oracle_bundle_id") or "") or None
        in_shortlist[tid] = bool(rrow.get("oracle_in_shortlist"))
        in_dossier[tid] = bool(rrow.get("oracle_in_candidate_dossier"))

    return {
        "results": results_by_target,
        "dossiers": dossiers_by_target,
        "oracle": oracle_by_target,
        "in_shortlist": in_shortlist,
        "in_dossier": in_dossier,
        "family": benchmark_family,
    }


# ---------------------------------------------------------------------------
# Prepared records – fast mode (frozen candidate_cards)
# ---------------------------------------------------------------------------

# (family_tag, target_id, dossier, frozen_cards, oracle_id)
PreparedFast = tuple[str, str, CandidateBundleDossier, list[CandidateEvidenceCard], str]


def _build_prepared_fast(
    b2b: dict,
    b2c: dict,
    shared_tids: set[str],
) -> list[PreparedFast]:
    out: list[PreparedFast] = []
    seen: set[str] = set()

    # B2B (includes shared targets)
    for tid in sorted(b2b["results"]):
        row = b2b["results"][tid]
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oracle_id = b2b["oracle"].get(tid)
        dossier = b2b["dossiers"].get(tid)
        if not oracle_id or dossier is None:
            continue
        cards = _cards_from_row(row)
        if oracle_id not in {c.bundle_id for c in cards}:
            continue
        seen.add(tid)
        fam = "shared-b2b" if tid in shared_tids else "b2b-only"
        out.append((fam, tid, dossier, cards, oracle_id))

    # B2C only (skip shared)
    for tid in sorted(b2c["results"]):
        if tid in seen or tid in shared_tids:
            continue
        row = b2c["results"][tid]
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oracle_id = b2c["oracle"].get(tid)
        dossier = b2c["dossiers"].get(tid)
        if not oracle_id or dossier is None:
            continue
        cards = _cards_from_row(row)
        if oracle_id not in {c.bundle_id for c in cards}:
            continue
        seen.add(tid)
        out.append(("b2c-only", tid, dossier, cards, oracle_id))

    return out


def _eval_fast(
    prepared: list[PreparedFast],
    config: TransferConfig,
) -> tuple[int, set[str]]:
    hits: set[str] = set()
    for _fam, tid, dossier, cards, oracle_id in prepared:
        primary = _deterministic_primary(dossier, cards, config)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


def _eval_split_fast(prepared: list[PreparedFast]) -> tuple[int, set[str]]:
    """Reference: current split – b2b config for b2b targets, b2c for b2c."""
    hits: set[str] = set()
    for fam, tid, dossier, cards, oracle_id in prepared:
        cfg = BINARY_TO_CONTINUOUS_CONFIG if fam == "b2c-only" else BINARY_TO_BINARY_CONFIG
        primary = _deterministic_primary(dossier, cards, cfg)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


# ---------------------------------------------------------------------------
# Prepared records – full mode (rebuild from tool-trace evidence)
# ---------------------------------------------------------------------------

# (family_tag, target_id, dossier, evidence_dict, oracle_id, target_source)
PreparedFull = tuple[str, str, CandidateBundleDossier, dict, str, str | None]


def _build_prepared_full(
    b2b: dict,
    b2c: dict,
    shared_tids: set[str],
) -> list[PreparedFull]:
    out: list[PreparedFull] = []
    seen: set[str] = set()

    # B2B (includes shared targets)
    for tid in sorted(b2b["results"]):
        row = b2b["results"][tid]
        oracle_id = b2b["oracle"].get(tid)
        dossier = b2b["dossiers"].get(tid)
        if not oracle_id or dossier is None:
            continue
        evidence = _extract_trace_evidence(row)
        # Oracle must be in the original shortlist to be selectable
        if oracle_id not in set(evidence["shortlist_ids"]):
            continue
        target_source = _target_source_for_dossier(dossier, "binary_to_binary")
        seen.add(tid)
        fam = "shared-b2b" if tid in shared_tids else "b2b-only"
        out.append((fam, tid, dossier, evidence, oracle_id, target_source))

    # B2C only
    for tid in sorted(b2c["results"]):
        if tid in seen or tid in shared_tids:
            continue
        row = b2c["results"][tid]
        oracle_id = b2c["oracle"].get(tid)
        dossier = b2c["dossiers"].get(tid)
        if not oracle_id or dossier is None:
            continue
        evidence = _extract_trace_evidence(row)
        if oracle_id not in set(evidence["shortlist_ids"]):
            continue
        target_source = _target_source_for_dossier(dossier, "binary_to_continuous")
        seen.add(tid)
        out.append(("b2c-only", tid, dossier, evidence, oracle_id, target_source))

    return out


def _rebuild_and_select(
    dossier: CandidateBundleDossier,
    evidence: dict,
    config: TransferConfig,
    target_source: str | None,
) -> str | None:
    """Rebuild cards from frozen evidence with a new config, then select primary."""
    shortlist_ids = evidence["shortlist_ids"]
    if not shortlist_ids:
        return None
    gc_combined = {**evidence["prescreen_gc"], **evidence["detailed_gc"]}
    h2 = evidence["h2"]
    ot = evidence["ot"]
    bundle_lookup = agent_bundle_lookup(dossier)

    cards = []
    for bundle_id in shortlist_ids:
        bundle = bundle_lookup.get(bundle_id)
        if bundle is None:
            continue
        card = _build_candidate_card(
            dossier,
            bundle,
            gc_row=gc_combined.get(bundle_id),
            h2_row=h2.get(bundle_id),
            ot_row=ot.get(bundle_id),
            config=config,
            target_source=target_source,
        )
        cards.append(card)

    return _deterministic_primary(dossier, cards, config)


def _eval_full(
    prepared: list[PreparedFull],
    config: TransferConfig,
) -> tuple[int, set[str]]:
    hits: set[str] = set()
    for _fam, tid, dossier, evidence, oracle_id, target_source in prepared:
        primary = _rebuild_and_select(dossier, evidence, config, target_source)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


def _eval_split_full(prepared: list[PreparedFull]) -> tuple[int, set[str]]:
    hits: set[str] = set()
    for fam, tid, dossier, evidence, oracle_id, target_source in prepared:
        cfg = BINARY_TO_CONTINUOUS_CONFIG if fam == "b2c-only" else BINARY_TO_BINARY_CONFIG
        primary = _rebuild_and_select(dossier, evidence, cfg, target_source)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


# ---------------------------------------------------------------------------
# fast_full mode: pre-cached evidence, analytical scoring (no Pydantic per trial)
# ---------------------------------------------------------------------------

import math as _math
from dataclasses import dataclass as _dataclass


@_dataclass
class _BundleCache:
    """All config-invariant data for one (target, bundle) pair."""
    bundle_id: str
    is_oracle: bool
    # invariant geometric/semantic
    archetype: str
    fidelity: float
    lexical: int
    tokens: int
    n_models: int
    prior: float
    # derived invariant
    is_proxy: bool
    n_models_50: int       # min(n_models, 50) for cheap_rank denominator
    model_support: float   # log1p(min(n_models, 100))
    anti_dom: float        # log(n/50) if n>50 else 0.0
    model_ok: bool         # n_models >= 5
    model_low: bool        # n_models < 3
    # GC
    has_gc: bool
    rg: float
    rg_abs: float
    p_sig: bool            # significant GC (p<0.05 or LLM High/Moderate)
    gc_raw_discount: float # raw _gc_resolution_discount (before floor)
    # OT
    has_ot: bool
    ot_overlap: float
    ot_count: int
    ot_conf_hm: bool       # confidence_level in {High, Moderate}
    ot_genetic: bool
    ot_lit_dom: bool
    ot_ta_match: bool
    ot_ta_both: bool       # source_therapeutic_areas AND candidate_therapeutic_areas non-empty
    ot_ancestors: int
    ot_phenotype: float
    ot_no_shared: bool     # pair_status == "no_shared_targets"
    # H2
    has_h2: bool
    h2_ceiling: float      # max(capacity, ceiling_proxy)


def _gc_raw_discount(gc) -> float:
    """Compute raw GC resolution discount from parsed GeneticCorrelationEvidence."""
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
    cards: list,  # list[CandidateEvidenceCard]
    oracle_id: str,
) -> list[_BundleCache]:
    """Pre-extract evidence fields from frozen cards. Called once per target."""
    out = []
    for card in cards:
        gc = card.gc
        h2 = card.h2
        ot = card.open_targets
        n = card.n_models

        # GC
        rg_val = float(gc.rg) if gc and gc.rg is not None else 0.0
        p_sig = _is_significant_gc(gc)
        gc_disc = _gc_raw_discount(gc) if gc else 0.0

        # OT
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

        # H2
        if h2:
            cap = float(h2.candidate_signal_capacity or 0.0)
            ceil = float(h2.shared_signal_ceiling_proxy or cap)
            h2_c = max(cap, ceil)
        else:
            h2_c = 0.0

        out.append(_BundleCache(
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
            model_support=_math.log1p(min(max(n, 0), 100)),
            anti_dom=_math.log(n / 50) if n > 50 else 0.0,
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


def _score_bundle_fast(b: _BundleCache, cfg: TransferConfig) -> float:
    """Compute selection_priority_score analytically from pre-cached fields."""
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
    # Exceptional OT bonus (uncapped; rewards bundles with very high OT overlap)
    if cfg.w_ot_exceptional > 0.0 and b.ot_overlap > 2.0:
        score += cfg.w_ot_exceptional * (b.ot_overlap - 2.0)
    return score


def _select_fast(bundles: list[_BundleCache], cfg: TransferConfig) -> str | None:
    """
    Mirror deterministic selection: sort by score desc, take top 2–3, argmax of those.
    Simplified: since _choose_primary_card returns the highest-priority-score card
    from the frontier, and the frontier is the top 2–3 by score, the primary is
    always the top-1 card (argmax over all cards).
    """
    if not bundles:
        return None
    best = max(bundles, key=lambda b: _score_bundle_fast(b, cfg))
    return best.bundle_id


# (family_tag, tid, bundle_caches, oracle_id)
PreparedFastFull = tuple[str, str, list[_BundleCache], str]


def _build_prepared_fast_full(
    b2b: dict,
    b2c: dict,
    shared_tids: set[str],
) -> list[PreparedFastFull]:
    """Build prepared set with pre-extracted evidence caches."""
    out: list[PreparedFastFull] = []
    seen: set[str] = set()

    for tid in sorted(b2b["results"]):
        row = b2b["results"][tid]
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oracle_id = b2b["oracle"].get(tid)
        if not oracle_id:
            continue
        cards = _cards_from_row(row)
        oracle_ids = {c.bundle_id for c in cards}
        if oracle_id not in oracle_ids:
            continue
        caches = _precompute_bundle_cache(cards, oracle_id)
        seen.add(tid)
        fam = "shared-b2b" if tid in shared_tids else "b2b-only"
        out.append((fam, tid, caches, oracle_id))

    for tid in sorted(b2c["results"]):
        if tid in seen or tid in shared_tids:
            continue
        row = b2c["results"][tid]
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oracle_id = b2c["oracle"].get(tid)
        if not oracle_id:
            continue
        cards = _cards_from_row(row)
        if oracle_id not in {c.bundle_id for c in cards}:
            continue
        caches = _precompute_bundle_cache(cards, oracle_id)
        seen.add(tid)
        out.append(("b2c-only", tid, caches, oracle_id))

    return out


def _eval_fast_full(
    prepared: list[PreparedFastFull],
    cfg: TransferConfig,
) -> tuple[int, set[str]]:
    hits: set[str] = set()
    for _fam, tid, caches, oracle_id in prepared:
        primary = _select_fast(caches, cfg)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


def _eval_split_fast_full(prepared: list[PreparedFastFull]) -> tuple[int, set[str]]:
    hits: set[str] = set()
    for fam, tid, caches, oracle_id in prepared:
        cfg = BINARY_TO_CONTINUOUS_CONFIG if fam == "b2c-only" else BINARY_TO_BINARY_CONFIG
        primary = _select_fast(caches, cfg)
        if primary == oracle_id:
            hits.add(tid)
    return len(hits), hits


# ---------------------------------------------------------------------------
# Config sampling
# ---------------------------------------------------------------------------

def _sample_weights_only(rng: random.Random, base: TransferConfig) -> TransferConfig:
    """Sample only the 6 selection-priority-score weights (fast mode)."""
    return replace(
        base,
        w_transferability_prior=10 ** rng.uniform(-2.0, 0.7),
        w_selection_utility=10 ** rng.uniform(-3.0, -0.3),
        w_selection_cheap_rank=rng.uniform(0.005, 0.15),
        w_selection_fidelity=rng.uniform(0.01, 0.18),
        w_selection_model_support=rng.uniform(0.0003, 0.03),
        w_selection_anti_dominance=rng.uniform(0.0, 0.15),
    )


def _sample_full_config(rng: random.Random) -> TransferConfig:
    """Sample all 15 scoring parameters (full mode)."""
    return TransferConfig(
        # Utility calculation weights
        w_statistical_overlap=rng.uniform(0.5, 4.5),
        w_mechanistic_overlap=rng.uniform(0.5, 4.5),
        w_signal_capacity=rng.uniform(0.2, 2.0),
        w_phenotype_fidelity=rng.uniform(1.0, 5.0),
        # Concordance bonus/penalty
        concordance_bonus=rng.uniform(0.2, 1.4),
        concordance_penalty=rng.uniform(-0.9, -0.1),
        # GC cheap-rank multipliers
        gc_cheap_rank_significant=rng.uniform(0.5, 3.5),
        gc_cheap_rank_nonsignificant=rng.uniform(0.1, 1.5),
        # GC resolution discount
        apply_gc_resolution_discount=True,
        gc_discount_floor=rng.uniform(0.0, 0.5),
        # Shortlist strategy (structural – doesn't affect card scoring, but kept
        # for completeness; track sizes are irrelevant in fixed-shortlist mode)
        shortlist_strategy=rng.choice(["dual_track", "gc_first"]),
        shortlist_cap=52,
        gc_track_size=8,
        semantic_track_size=12,
        prior_track_size=10,
        selection_track_size=32,
        support_track_size=10,
        allow_ot_promotion=False,
        # Selection-priority-score weights
        w_transferability_prior=10 ** rng.uniform(-2.0, 0.7),
        w_selection_utility=10 ** rng.uniform(-3.0, -0.3),
        w_selection_cheap_rank=rng.uniform(0.005, 0.15),
        w_selection_fidelity=rng.uniform(0.01, 0.18),
        w_selection_model_support=rng.uniform(0.0003, 0.03),
        w_selection_anti_dominance=rng.uniform(0.0, 0.15),
        # Exceptional OT bonus (ot_overlap > 2.0 threshold)
        w_ot_exceptional=rng.uniform(0.0, 0.25),
    )


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def _print_per_target_table(
    prepared_labels: list[tuple[str, str]],  # (fam, tid)
    hits_split: set[str],
    hits_best: set[str],
) -> None:
    gained = sorted(hits_best - hits_split)
    lost = sorted(hits_split - hits_best)
    if gained:
        print(f"  Gained vs split:  {', '.join(gained)}")
    else:
        print("  Gained vs split:  (none)")
    if lost:
        print(f"  Lost vs split:    {', '.join(lost)}")
    else:
        print("  Lost vs split:    (none)")


def _print_config(cfg: TransferConfig, fields: list[str]) -> None:
    for f in fields:
        print(f"    {f} = {getattr(cfg, f)!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline unified TransferConfig simulation across 49 union targets."
    )
    parser.add_argument(
        "--mode",
        choices=("fast", "fast_full", "full"),
        default="fast_full",
        help=(
            "fast: frozen candidate_cards, tune 6 selection weights. "
            "fast_full: pre-cached evidence, analytical scoring, tune 15 params (recommended). "
            "full: rebuild cards from tool-trace via Pydantic, tune 15 scoring params (slow)."
        ),
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--trials",
        type=int,
        default=120000,
        help="Number of random search trials.",
    )
    parser.add_argument("--b2b-results", type=Path, default=B2B_RESULTS)
    parser.add_argument("--b2c-results", type=Path, default=B2C_RESULTS)
    args = parser.parse_args()

    print(f"=== offline_tune_unified_config  mode={args.mode}  seed={args.seed}  trials={args.trials} ===")

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    print("\n[1/4] Loading family data...")
    b2b = _load_family(args.b2b_results, B2B_DOSSIERS, "binary_to_binary")
    b2c = _load_family(args.b2c_results, B2C_DOSSIERS, "binary_to_continuous")

    b2b_tids = set(b2b["results"])
    b2c_tids = set(b2c["results"])
    shared_tids = b2b_tids & b2c_tids
    union_tids = b2b_tids | b2c_tids
    print(
        f"  B2B: {len(b2b_tids)} targets  |  B2C: {len(b2c_tids)} targets  |  "
        f"Shared: {len(shared_tids)} ({', '.join(sorted(shared_tids))})  |  "
        f"Union: {len(union_tids)}"
    )

    # ------------------------------------------------------------------
    # Feasibility summary
    # ------------------------------------------------------------------
    print("\n[2/4] Feasibility (oracle reachability in frozen runs)...")
    for label, data, n_total in [("B2B", b2b, 23), ("B2C", b2c, 29)]:
        achievable = sorted(tid for tid, ins in data["in_shortlist"].items() if ins and data["oracle"].get(tid))
        sl_miss = sorted(tid for tid, ins in data["in_shortlist"].items() if not ins and data["oracle"].get(tid) and data["in_dossier"].get(tid))
        dossier_miss = sorted(tid for tid, ind in data["in_dossier"].items() if not ind and data["oracle"].get(tid))
        print(f"  {label} ({n_total} targets):")
        print(f"    oracle in shortlist (achievable upper bound): {len(achievable)}")
        print(f"    oracle in dossier but NOT shortlist:          {len(sl_miss)} → {sl_miss}")
        print(f"    oracle NOT in dossier:                        {len(dossier_miss)} → {dossier_miss}")

    # ------------------------------------------------------------------
    # Build prepared set + baselines
    # ------------------------------------------------------------------
    print("\n[3/4] Building prepared set and computing baselines...")

    if args.mode == "fast":
        prepared = _build_prepared_fast(b2b, b2c, shared_tids)
        n_prep = len(prepared)
        n_union = 49
        print(f"  Prepared targets (oracle in frozen shortlist): {n_prep}/{n_union}")

        # Per-family breakdown
        fam_counts: dict[str, int] = {}
        for fam, *_ in prepared:
            fam_counts[fam] = fam_counts.get(fam, 0) + 1
        for fam, cnt in sorted(fam_counts.items()):
            print(f"    {fam}: {cnt}")

        # Impossible targets
        impossible = sorted(
            tid for tid in union_tids
            if tid not in {row[1] for row in prepared}
        )
        print(f"  Impossible (oracle not in frozen shortlist): {len(impossible)} → {impossible}")

        # Baselines
        n_split, hits_split = _eval_split_fast(prepared)
        n_b2b_all, hits_b2b_all = _eval_fast(prepared, BINARY_TO_BINARY_CONFIG)
        n_b2c_all, hits_b2c_all = _eval_fast(prepared, BINARY_TO_CONTINUOUS_CONFIG)

        print(f"\n  Baselines (deterministic, no LLM):")
        print(f"    split config (b2b→B2B, b2c→B2C):   {n_split}/{n_prep} achievable  ({n_split}/{n_union} total)")
        print(f"      hits: {', '.join(sorted(hits_split))}")
        print(f"    B2B config applied to all 49:       {n_b2b_all}/{n_prep}")
        print(f"      hits: {', '.join(sorted(hits_b2b_all))}")
        print(f"    B2C config applied to all 49:       {n_b2c_all}/{n_prep}")
        print(f"      hits: {', '.join(sorted(hits_b2c_all))}")

        # Random search
        best_n = max(n_b2b_all, n_b2c_all)
        best_hits = hits_b2b_all if n_b2b_all >= n_b2c_all else hits_b2c_all
        best_cfg: TransferConfig = BINARY_TO_BINARY_CONFIG if n_b2b_all >= n_b2c_all else BINARY_TO_CONTINUOUS_CONFIG

        print(f"\n[4/4] Random search ({args.trials} trials, mode=fast)...")
        rng = random.Random(args.seed)
        # Also try b2c as base
        for base in (BINARY_TO_BINARY_CONFIG, BINARY_TO_CONTINUOUS_CONFIG):
            n, hits = _eval_fast(prepared, base)
            if n > best_n:
                best_n, best_hits, best_cfg = n, hits, base

        for t in range(args.trials):
            cfg = _sample_weights_only(rng, BINARY_TO_BINARY_CONFIG)
            n, hits = _eval_fast(prepared, cfg)
            if n > best_n:
                best_n, best_hits, best_cfg = n, hits, cfg
                print(f"  [trial {t:7d}] new best {best_n}/{n_prep}: {', '.join(sorted(best_hits))}")

        print(f"\n=== FAST MODE RESULT ===")
        print(f"Best unified config exact oracle hits: {best_n}/{n_prep} achievable  ({best_n}/{n_union} total)")
        print(f"Matched: {', '.join(sorted(best_hits))}")
        missed_achievable = sorted(row[1] for row in prepared if row[1] not in best_hits)
        print(f"Missed (achievable but not won): {', '.join(missed_achievable)}")
        _print_per_target_table([(r[0], r[1]) for r in prepared], hits_split, best_hits)
        print("\nBest config fields (6 selection weights):")
        _print_config(best_cfg, [
            "w_transferability_prior",
            "w_selection_utility",
            "w_selection_cheap_rank",
            "w_selection_fidelity",
            "w_selection_model_support",
            "w_selection_anti_dominance",
        ])
        print("  (all other fields inherited from BINARY_TO_BINARY_CONFIG)")

    elif args.mode == "fast_full":
        prepared_ff = _build_prepared_fast_full(b2b, b2c, shared_tids)
        n_prep = len(prepared_ff)
        n_union = 49
        print(f"  Prepared targets (oracle in frozen shortlist): {n_prep}/{n_union}")

        fam_counts: dict[str, int] = {}
        for fam, *_ in prepared_ff:
            fam_counts[fam] = fam_counts.get(fam, 0) + 1
        for fam, cnt in sorted(fam_counts.items()):
            print(f"    {fam}: {cnt}")

        impossible = sorted(
            tid for tid in union_tids
            if tid not in {row[1] for row in prepared_ff}
        )
        print(f"  Impossible (oracle not in frozen shortlist): {len(impossible)} → {impossible}")

        # Baselines
        n_split, hits_split = _eval_split_fast_full(prepared_ff)
        n_b2b_all, hits_b2b_all = _eval_fast_full(prepared_ff, BINARY_TO_BINARY_CONFIG)
        n_b2c_all, hits_b2c_all = _eval_fast_full(prepared_ff, BINARY_TO_CONTINUOUS_CONFIG)

        print(f"\n  Baselines (analytical scoring, deterministic):")
        print(f"    split config (b2b→B2B, b2c→B2C):   {n_split}/{n_prep} achievable  ({n_split}/{n_union} total)")
        print(f"      hits: {', '.join(sorted(hits_split))}")
        print(f"    B2B config applied to all 49:       {n_b2b_all}/{n_prep}")
        print(f"      hits: {', '.join(sorted(hits_b2b_all))}")
        print(f"    B2C config applied to all 49:       {n_b2c_all}/{n_prep}")
        print(f"      hits: {', '.join(sorted(hits_b2c_all))}")

        # Random search
        best_n = max(n_b2b_all, n_b2c_all)
        best_hits = hits_b2b_all if n_b2b_all >= n_b2c_all else hits_b2c_all
        best_cfg: TransferConfig = BINARY_TO_BINARY_CONFIG if n_b2b_all >= n_b2c_all else BINARY_TO_CONTINUOUS_CONFIG

        print(f"\n[4/4] Random search ({args.trials} trials, mode=fast_full)...")
        rng = random.Random(args.seed)

        for t in range(args.trials):
            cfg = _sample_full_config(rng)
            n, hits = _eval_fast_full(prepared_ff, cfg)
            if n > best_n:
                best_n, best_hits, best_cfg = n, hits, cfg
                print(f"  [trial {t:7d}] new best {best_n}/{n_prep}: {', '.join(sorted(best_hits))}")

        print(f"\n=== FAST_FULL MODE RESULT ===")
        print(f"Best unified config exact oracle hits: {best_n}/{n_prep} achievable  ({best_n}/{n_union} total)")
        print(f"Matched: {', '.join(sorted(best_hits))}")
        missed_achievable = sorted(row[1] for row in prepared_ff if row[1] not in best_hits)
        print(f"Missed (achievable but not won): {', '.join(missed_achievable)}")
        _print_per_target_table([(r[0], r[1]) for r in prepared_ff], hits_split, best_hits)
        print("\nBest config fields (16 scoring params):")
        _print_config(best_cfg, [
            "w_statistical_overlap",
            "w_mechanistic_overlap",
            "w_signal_capacity",
            "w_phenotype_fidelity",
            "concordance_bonus",
            "concordance_penalty",
            "gc_cheap_rank_significant",
            "gc_cheap_rank_nonsignificant",
            "gc_discount_floor",
            "w_transferability_prior",
            "w_selection_utility",
            "w_selection_cheap_rank",
            "w_selection_fidelity",
            "w_selection_model_support",
            "w_selection_anti_dominance",
            "w_ot_exceptional",
        ])

    else:  # full mode
        prepared = _build_prepared_full(b2b, b2c, shared_tids)
        n_prep = len(prepared)
        n_union = 49
        print(f"  Prepared targets (oracle in original shortlist): {n_prep}/{n_union}")

        fam_counts: dict[str, int] = {}
        for fam, *_ in prepared:
            fam_counts[fam] = fam_counts.get(fam, 0) + 1
        for fam, cnt in sorted(fam_counts.items()):
            print(f"    {fam}: {cnt}")

        impossible = sorted(
            tid for tid in union_tids
            if tid not in {row[1] for row in prepared}
        )
        print(f"  Impossible (oracle not in shortlist): {len(impossible)} → {impossible}")

        # Baselines
        n_split, hits_split = _eval_split_full(prepared)
        n_b2b_all, hits_b2b_all = _eval_full(prepared, BINARY_TO_BINARY_CONFIG)
        n_b2c_all, hits_b2c_all = _eval_full(prepared, BINARY_TO_CONTINUOUS_CONFIG)

        print(f"\n  Baselines (rebuilt cards, deterministic):")
        print(f"    split config (b2b→B2B, b2c→B2C):   {n_split}/{n_prep} achievable  ({n_split}/{n_union} total)")
        print(f"      hits: {', '.join(sorted(hits_split))}")
        print(f"    B2B config applied to all 49:       {n_b2b_all}/{n_prep}")
        print(f"      hits: {', '.join(sorted(hits_b2b_all))}")
        print(f"    B2C config applied to all 49:       {n_b2c_all}/{n_prep}")
        print(f"      hits: {', '.join(sorted(hits_b2c_all))}")

        # Random search
        best_n = max(n_b2b_all, n_b2c_all, n_split)
        if n_split >= n_b2b_all and n_split >= n_b2c_all:
            best_hits = hits_split
            best_cfg = BINARY_TO_BINARY_CONFIG  # placeholder; split isn't a single config
        elif n_b2b_all >= n_b2c_all:
            best_hits = hits_b2b_all
            best_cfg = BINARY_TO_BINARY_CONFIG
        else:
            best_hits = hits_b2c_all
            best_cfg = BINARY_TO_CONTINUOUS_CONFIG

        print(f"\n[4/4] Random search ({args.trials} trials, mode=full)...")
        rng = random.Random(args.seed)

        for t in range(args.trials):
            cfg = _sample_full_config(rng)
            n, hits = _eval_full(prepared, cfg)
            if n > best_n:
                best_n, best_hits, best_cfg = n, hits, cfg
                print(f"  [trial {t:7d}] new best {best_n}/{n_prep}: {', '.join(sorted(best_hits))}")

        print(f"\n=== FULL MODE RESULT ===")
        print(f"Best unified config exact oracle hits: {best_n}/{n_prep} achievable  ({best_n}/{n_union} total)")
        print(f"Matched: {', '.join(sorted(best_hits))}")
        missed_achievable = sorted(row[1] for row in prepared if row[1] not in best_hits)
        print(f"Missed (achievable but not won): {', '.join(missed_achievable)}")
        _print_per_target_table([(r[0], r[1]) for r in prepared], hits_split, best_hits)
        print("\nBest config fields (16 scoring params):")
        _print_config(best_cfg, [
            "w_statistical_overlap",
            "w_mechanistic_overlap",
            "w_signal_capacity",
            "w_phenotype_fidelity",
            "concordance_bonus",
            "concordance_penalty",
            "gc_cheap_rank_significant",
            "gc_cheap_rank_nonsignificant",
            "gc_discount_floor",
            "w_transferability_prior",
            "w_selection_utility",
            "w_selection_cheap_rank",
            "w_selection_fidelity",
            "w_selection_model_support",
            "w_selection_anti_dominance",
            "w_ot_exceptional",
        ])
        print(f"  shortlist_strategy = {best_cfg.shortlist_strategy!r}  (fixed; shortlist not rebuilt)")


if __name__ == "__main__":
    main()
