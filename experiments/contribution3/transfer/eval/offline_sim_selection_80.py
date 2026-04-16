"""Offline selection quality optimization for 80-target unified benchmark.

Tests multiple scoring approaches to maximize exact oracle hits:
1. Linear weights (baseline, grid search)
2. Multiplicative interaction terms (prior * fidelity)
3. Rank-based scoring (reciprocal ranks within shortlist)
4. Evidence-boosted scoring (concordance bonus)
5. Expanded feature set (utility^2, fidelity * prior, etc.)

Uses frozen candidate_cards from all-tools__20260413_154807/results.json.
Does NOT call any LLM or live tool.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import UNIFIED_CONFIG, _is_significant_gc
from experiments.contribution3.transfer.common import load_candidate_dossiers
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows
from experiments.contribution3.transfer.prompts.transfer_prompt import CandidateEvidenceCard

UNIFIED_RESULTS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_154807/results.json"
)
UNIFIED_DOSSIERS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "candidate_dossiers.json"
)


def _cards_from_row(row: dict) -> list[CandidateEvidenceCard]:
    decision = row.get("decision") or {}
    raw = (decision.get("evidence_state") or {}).get("candidate_cards") or []
    return [CandidateEvidenceCard.model_validate(c) for c in raw]


def _extract_fields(card: CandidateEvidenceCard) -> dict:
    ot_overlap = 0.0
    gc_significant = False
    gc_rg = 0.0
    ot_supported = False
    if card.open_targets is not None:
        ot_overlap = float(card.open_targets.weighted_shared_target_overlap_score or 0)
        ot_supported = (ot_overlap >= 0.20 and (card.open_targets.shared_target_count or 0) >= 1)
    if card.gc is not None and card.gc.rg is not None:
        gc_rg = abs(float(card.gc.rg or 0.0))
        gc_significant = _is_significant_gc(card.gc)

    is_same_endpoint = card.archetype == "same-endpoint disease"
    is_composite = card.archetype == "composite liability trait"
    is_endophenotype = card.archetype == "mechanistic endophenotype / organ-function measurement"
    concordant = gc_significant and ot_supported

    return {
        "bundle_id": card.bundle_id,
        "prior": card.transferability_prior_score,
        "utility": card.utility_score,
        "cheap": card.cheap_rank_score,
        "fidelity": card.phenotype_fidelity_score,
        "n_models": card.n_models,
        "ot_overlap": ot_overlap,
        "gc_rg": gc_rg,
        "gc_significant": gc_significant,
        "ot_supported": ot_supported,
        "concordant": concordant,
        "is_same_endpoint": is_same_endpoint,
        "is_composite": is_composite,
        "is_endophenotype": is_endophenotype,
        "utility_x_fidelity": card.utility_score * card.phenotype_fidelity_score,
        "prior_x_fidelity": card.transferability_prior_score * card.phenotype_fidelity_score,
    }


PreparedRecord = tuple[str, str, dict[str, dict]]  # (tid, oracle_id, fields_by_id)


def load_data() -> tuple[list[PreparedRecord], list[str]]:
    results = json.loads(UNIFIED_RESULTS.read_text())
    results_by_target = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results if (r.get("target") or {}).get("target_id")
    }
    del results

    recall_rows = build_shortlist_recall_rows(
        benchmark_family="unified",
        results_path=UNIFIED_RESULTS,
        candidate_dossiers_path=UNIFIED_DOSSIERS,
    )
    oracle_by_target: dict[str, str | None] = {}
    in_shortlist: dict[str, bool] = {}
    for rrow in recall_rows:
        if rrow.get("status") != "ok":
            continue
        tid = str(rrow["target_id"])
        oracle_by_target[tid] = str(rrow.get("transfer_eligible_global_oracle_bundle_id") or "") or None
        in_shortlist[tid] = bool(rrow.get("oracle_in_shortlist"))

    prepared: list[PreparedRecord] = []
    unreachable: list[str] = []
    for tid, row in sorted(results_by_target.items()):
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oracle_id = oracle_by_target.get(tid)
        if not oracle_id or not in_shortlist.get(tid):
            unreachable.append(tid)
            continue
        cards = _cards_from_row(row)
        card_ids = {c.bundle_id for c in cards}
        if oracle_id not in card_ids:
            unreachable.append(tid)
            continue
        fields_by_id = {c.bundle_id: _extract_fields(c) for c in cards}
        prepared.append((tid, oracle_id, fields_by_id))

    return prepared, unreachable


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_linear(f: dict, w: tuple) -> float:
    """Standard linear: (prior, util, cheap, fid, sup, anti, ot_exc)"""
    w_prior, w_util, w_cheap, w_fid, w_sup, w_anti, w_ot_exc = w
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_prior * f["prior"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"] + w_sup * ms
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


def score_with_interaction(f: dict, w: tuple) -> float:
    """Linear + interaction terms: (prior, util, cheap, fid, sup, anti, ot_exc, uf_interact, pf_interact)"""
    w_prior, w_util, w_cheap, w_fid, w_sup, w_anti, w_ot_exc, w_uf, w_pf = w
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_prior * f["prior"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"] + w_sup * ms
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    # Interaction terms
    s += w_uf * f["utility_x_fidelity"]
    s += w_pf * f["prior_x_fidelity"]
    return s


def score_with_concordance(f: dict, w: tuple) -> float:
    """Linear + concordance + archetype bonuses: (prior, util, cheap, fid, sup, anti, ot_exc, conc, endpoint_bonus)"""
    w_prior, w_util, w_cheap, w_fid, w_sup, w_anti, w_ot_exc, w_conc, w_endpoint = w
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_prior * f["prior"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"] + w_sup * ms
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    # Concordance: both GC and OT support
    if f["concordant"]:
        s += w_conc
    # Same-endpoint disease archetype bonus
    if f["is_same_endpoint"]:
        s += w_endpoint
    return s


def score_prior_x_fidelity(f: dict, w: tuple) -> float:
    """Multiplicative prior*fidelity + additive terms: (w_pf, w_util, w_cheap, w_sup, w_anti, w_ot_exc, w_conc)"""
    w_pf, w_util, w_cheap, w_sup, w_anti, w_ot_exc, w_conc = w
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_pf * f["prior_x_fidelity"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_sup * ms
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    if f["concordant"]:
        s += w_conc
    return s


def score_rank_based(fields_by_id: dict[str, dict], w: tuple) -> str:
    """Rank-based scoring: rank cards within shortlist, then combine reciprocal ranks.
    w = (w_prior_rank, w_util_rank, w_fid_rank, w_cheap_rank, w_sup_rank, w_ot_exc)"""
    w_pr, w_ur, w_fr, w_cr, w_sr, w_ot_exc = w
    bids = list(fields_by_id.keys())
    if not bids:
        return ""

    # Compute ranks for each dimension
    def rank_by(key: str, reverse: bool = True) -> dict[str, int]:
        sorted_bids = sorted(bids, key=lambda b: (-fields_by_id[b][key] if reverse else fields_by_id[b][key], b))
        return {b: i + 1 for i, b in enumerate(sorted_bids)}

    prior_ranks = rank_by("prior")
    util_ranks = rank_by("utility")
    fid_ranks = rank_by("fidelity")
    cheap_ranks = rank_by("cheap")
    sup_ranks = rank_by("n_models")
    n = len(bids)

    best_bid = ""
    best_score = -float("inf")
    for bid in bids:
        f = fields_by_id[bid]
        s = (w_pr / prior_ranks[bid] + w_ur / util_ranks[bid] + w_fr / fid_ranks[bid]
             + w_cr / cheap_ranks[bid] + w_sr / sup_ranks[bid])
        if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
            s += w_ot_exc * (f["ot_overlap"] - 2.0)
        if s > best_score or (s == best_score and bid < best_bid):
            best_score = s
            best_bid = bid
    return best_bid


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def eval_scoring(prepared: list[PreparedRecord], scorer, w: tuple) -> tuple[int, list[str]]:
    """Count exact oracle hits for a scoring function."""
    hits = []
    for tid, oracle_id, fields_by_id in prepared:
        best_id = max(fields_by_id, key=lambda bid: scorer(fields_by_id[bid], w))
        if best_id == oracle_id:
            hits.append(tid)
    return len(hits), hits


def eval_rank_based(prepared: list[PreparedRecord], w: tuple) -> tuple[int, list[str]]:
    hits = []
    for tid, oracle_id, fields_by_id in prepared:
        best_id = score_rank_based(fields_by_id, w)
        if best_id == oracle_id:
            hits.append(tid)
    return len(hits), hits


def optimize_scoring(prepared, scorer, bounds, n_trials=500000, seed=42):
    def objective(params):
        w = tuple(params)
        hits, _ = eval_scoring(prepared, scorer, w)
        return -hits

    rng = np.random.default_rng(seed)
    result = differential_evolution(
        objective, bounds=bounds,
        maxiter=min(n_trials // 15, 5000), popsize=15, tol=0,
        mutation=(0.5, 1.5), recombination=0.9,
        seed=int(rng.integers(0, 2**31)), workers=1, polish=True,
    )
    w = tuple(result.x)
    hits, hit_ids = eval_scoring(prepared, scorer, w)
    return w, hits, hit_ids


def optimize_rank_based(prepared, bounds, n_trials=500000, seed=42):
    def objective(params):
        w = tuple(params)
        hits, _ = eval_rank_based(prepared, w)
        return -hits

    rng = np.random.default_rng(seed)
    result = differential_evolution(
        objective, bounds=bounds,
        maxiter=min(n_trials // 15, 5000), popsize=15, tol=0,
        mutation=(0.5, 1.5), recombination=0.9,
        seed=int(rng.integers(0, 2**31)), workers=1, polish=True,
    )
    w = tuple(result.x)
    hits, hit_ids = eval_rank_based(prepared, w)
    return w, hits, hit_ids


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading data...")
    prepared, unreachable = load_data()
    total = len(prepared)
    print(f"Prepared: {total} (oracle in shortlist cards), unreachable: {len(unreachable)}")

    # === Approach 1: Standard linear (baseline) ===
    print("\n=== 1. Standard linear scoring ===")
    w_current = (
        UNIFIED_CONFIG.w_transferability_prior, UNIFIED_CONFIG.w_selection_utility,
        UNIFIED_CONFIG.w_selection_cheap_rank, UNIFIED_CONFIG.w_selection_fidelity,
        UNIFIED_CONFIG.w_selection_model_support, UNIFIED_CONFIG.w_selection_anti_dominance,
        UNIFIED_CONFIG.w_ot_exceptional,
    )
    h, ids = eval_scoring(prepared, score_linear, w_current)
    missed = [t for t, *_ in prepared if t not in ids]
    print(f"  Current weights: {h}/{total} hits. Missed: {missed}")

    print("  Optimizing...")
    bounds_linear = [(0, 5), (0, 1), (0, 1), (0, 5), (0, 1), (0, 1), (0, 2)]
    w_opt, h_opt, ids_opt = optimize_scoring(prepared, score_linear, bounds_linear)
    missed_opt = [t for t, *_ in prepared if t not in ids_opt]
    print(f"  Optimized: {h_opt}/{total} hits")
    print(f"  Weights: prior={w_opt[0]:.4f} util={w_opt[1]:.4f} cheap={w_opt[2]:.4f} "
          f"fid={w_opt[3]:.4f} sup={w_opt[4]:.4f} anti={w_opt[5]:.4f} ot_exc={w_opt[6]:.4f}")
    print(f"  Missed: {missed_opt}")

    # === Approach 2: Linear + interaction ===
    print("\n=== 2. Linear + interaction terms ===")
    bounds_interact = [(0, 5), (0, 1), (0, 1), (0, 5), (0, 1), (0, 1), (0, 2), (0, 3), (0, 5)]
    w_int, h_int, ids_int = optimize_scoring(prepared, score_with_interaction, bounds_interact)
    missed_int = [t for t, *_ in prepared if t not in ids_int]
    print(f"  Optimized: {h_int}/{total} hits")
    print(f"  Weights: prior={w_int[0]:.4f} util={w_int[1]:.4f} cheap={w_int[2]:.4f} "
          f"fid={w_int[3]:.4f} sup={w_int[4]:.4f} anti={w_int[5]:.4f} ot_exc={w_int[6]:.4f} "
          f"uf_interact={w_int[7]:.4f} pf_interact={w_int[8]:.4f}")
    print(f"  Missed: {missed_int}")

    # === Approach 3: Linear + concordance + archetype ===
    print("\n=== 3. Linear + concordance + endpoint bonus ===")
    bounds_conc = [(0, 5), (0, 1), (0, 1), (0, 5), (0, 1), (0, 1), (0, 2), (0, 3), (0, 3)]
    w_conc, h_conc, ids_conc = optimize_scoring(prepared, score_with_concordance, bounds_conc)
    missed_conc = [t for t, *_ in prepared if t not in ids_conc]
    print(f"  Optimized: {h_conc}/{total} hits")
    print(f"  Weights: prior={w_conc[0]:.4f} util={w_conc[1]:.4f} cheap={w_conc[2]:.4f} "
          f"fid={w_conc[3]:.4f} sup={w_conc[4]:.4f} anti={w_conc[5]:.4f} ot_exc={w_conc[6]:.4f} "
          f"concordance={w_conc[7]:.4f} endpoint_bonus={w_conc[8]:.4f}")
    print(f"  Missed: {missed_conc}")

    # === Approach 4: Multiplicative prior*fidelity ===
    print("\n=== 4. Multiplicative prior*fidelity ===")
    bounds_pf = [(0, 10), (0, 1), (0, 1), (0, 1), (0, 1), (0, 2), (0, 3)]
    w_pf, h_pf, ids_pf = optimize_scoring(prepared, score_prior_x_fidelity, bounds_pf)
    missed_pf = [t for t, *_ in prepared if t not in ids_pf]
    print(f"  Optimized: {h_pf}/{total} hits")
    print(f"  Weights: pf={w_pf[0]:.4f} util={w_pf[1]:.4f} cheap={w_pf[2]:.4f} "
          f"sup={w_pf[3]:.4f} anti={w_pf[4]:.4f} ot_exc={w_pf[5]:.4f} concordance={w_pf[6]:.4f}")
    print(f"  Missed: {missed_pf}")

    # === Approach 5: Rank-based scoring ===
    print("\n=== 5. Rank-based scoring ===")
    bounds_rank = [(0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 2)]
    w_rank, h_rank, ids_rank = optimize_rank_based(prepared, bounds_rank)
    missed_rank = [t for t, *_ in prepared if t not in ids_rank]
    print(f"  Optimized: {h_rank}/{total} hits")
    print(f"  Weights: prior_rank={w_rank[0]:.4f} util_rank={w_rank[1]:.4f} fid_rank={w_rank[2]:.4f} "
          f"cheap_rank={w_rank[3]:.4f} sup_rank={w_rank[4]:.4f} ot_exc={w_rank[5]:.4f}")
    print(f"  Missed: {missed_rank}")

    # === Summary ===
    print("\n=== SUMMARY ===")
    print(f"  1. Linear:           {h_opt}/{total}")
    print(f"  2. Interaction:      {h_int}/{total}")
    print(f"  3. Concordance:      {h_conc}/{total}")
    print(f"  4. Prior*Fidelity:   {h_pf}/{total}")
    print(f"  5. Rank-based:       {h_rank}/{total}")
    print(f"\n  Unreachable (oracle not in shortlist): {len(unreachable)}")
    print(f"  Total targets: 80, max reachable: {total}")

    # === Best approach: detailed analysis ===
    best_h = max(h_opt, h_int, h_conc, h_pf, h_rank)
    best_name = ["Linear", "Interaction", "Concordance", "Prior*Fidelity", "Rank-based"][
        [h_opt, h_int, h_conc, h_pf, h_rank].index(best_h)]
    best_missed = [missed_opt, missed_int, missed_conc, missed_pf, missed_rank][
        [h_opt, h_int, h_conc, h_pf, h_rank].index(best_h)]
    print(f"\n  Best: {best_name} with {best_h}/{total} hits")
    print(f"  Missed targets: {best_missed}")

    # Per-target analysis of the best approach
    all_missed_sets = [set(missed_opt), set(missed_int), set(missed_conc), set(missed_pf), set(missed_rank)]
    always_missed = set.intersection(*all_missed_sets)
    print(f"\n  Always missed (by ALL approaches): {sorted(always_missed)}")
    sometimes_hit = set.union(*[set(ids_opt), set(ids_int), set(ids_conc), set(ids_pf), set(ids_rank)]) - set(ids_opt)
    print(f"  Hit by at least one non-linear approach but missed by linear: {sorted(sometimes_hit & set(missed_opt))}")


if __name__ == "__main__":
    main()
