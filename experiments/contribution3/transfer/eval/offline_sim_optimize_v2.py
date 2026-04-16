"""Offline selection optimization v2 — fast, uses cards_light.json.

Goal: maximize exact oracle matches (selected_bundle == oracle_bundle)
across 80 unified targets by finding the best scoring function.

Does NOT call any LLM or live tool. All scoring is deterministic.
Uses pre-extracted card features from cards_light.json (~5MB).
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

RUN_DIR = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653"
)
CARDS_LIGHT = RUN_DIR / "cards_light.json"
SHORTLIST_RECALL_CSV = RUN_DIR / "shortlist_recall.csv"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

PreparedRecord = tuple[str, str, dict[str, dict]]  # (tid, oracle_id, fields_by_id)


def load_data() -> tuple[list[PreparedRecord], list[str]]:
    """Load from cards_light.json + shortlist_recall.csv."""
    # Load oracle info from CSV
    oracle_by_target: dict[str, str | None] = {}
    in_shortlist: dict[str, bool] = {}
    with open(SHORTLIST_RECALL_CSV) as f:
        for row in csv.DictReader(f):
            tid = row["target_id"]
            oracle_by_target[tid] = row.get("transfer_eligible_global_oracle_bundle_id") or None
            in_shortlist[tid] = row.get("oracle_in_shortlist") == "True"

    # Load card features
    raw = json.loads(CARDS_LIGHT.read_text())

    prepared: list[PreparedRecord] = []
    unreachable: list[str] = []

    for entry in raw:
        tid = entry["tid"]
        if entry.get("outcome") != "MATCHED":
            continue
        oracle_id = oracle_by_target.get(tid)
        if not oracle_id or not in_shortlist.get(tid):
            unreachable.append(tid)
            continue

        fields_by_id: dict[str, dict] = {}
        for c in entry["cards"]:
            bid = c["bid"]
            fields_by_id[bid] = {
                "bundle_id": bid,
                "prior": c["prior"],
                "utility": c["util"],
                "cheap": c["cheap"],
                "fidelity": c["fid"],
                "n_models": c["n_mod"],
                "lexical": c["lex"],
                "shared_tokens": c["stok"],
                "archetype": c["arch"],
                "gc_rg": c["gc_rg"],
                "gc_p": c["gc_p"],
                "gc_z": c["gc_z"],
                "gc_significant": c["gc_sig"],
                "ot_overlap": c["ot_ov"],
                "ot_shared_count": c["ot_sc"],
                "ot_area_match": c["ot_area"],
                "ot_ancestor": c["ot_anc"],
                "ot_pheno": c["ot_ph"],
                "ot_genetic_support": c["ot_gen"],
                "ot_supported": c["ot_sup"],
                "h2_ceiling": c["h2_ceil"],
                "concordant": c["conc"],
                "is_same_endpoint": c["arch"] == "same-endpoint disease",
                "is_adjacent": c["arch"] == "adjacent disease family",
                "is_composite": c["arch"] == "composite liability trait",
                "is_endophenotype": c["arch"] == "mechanistic endophenotype / organ-function measurement",
                "is_proxy": c["arch"] == "administrative/exposure/treatment/family-history proxy",
                "utility_x_fidelity": c["util"] * c["fid"],
                "prior_x_fidelity": c["prior"] * c["fid"],
            }

        if oracle_id not in fields_by_id:
            unreachable.append(tid)
            continue
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


def score_dampened_prior(f: dict, w: tuple) -> float:
    """prior^alpha dampens high-prior generalists."""
    alpha, w_core, beta, w_fid, w_util, w_cheap, w_anti, w_ot_exc = w
    alpha = max(alpha, 0.05)
    beta = max(beta, 0.05)
    s = w_core * (f["prior"] ** alpha) + w_fid * (f["fidelity"] ** beta)
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


def score_prior_ceiling(f: dict, w: tuple) -> float:
    """min(prior, cap) clips extreme priors."""
    cap, w_prior, w_fid, w_util, w_cheap, w_anti, w_ot_exc = w
    cap = max(cap, 0.1)
    p = min(f["prior"], cap)
    s = w_prior * p + w_fid * f["fidelity"]
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


def score_concordance_endpoint(f: dict, w: tuple) -> float:
    """Linear + concordance + endpoint bonus + GC bonus."""
    w_prior, w_util, w_cheap, w_fid, w_sup, w_anti, w_ot_exc, w_conc, w_endpoint, w_gc_bonus = w
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_prior * f["prior"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"] + w_sup * ms
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    if f["concordant"]:
        s += w_conc
    if f["is_same_endpoint"]:
        s += w_endpoint
    if f["gc_significant"]:
        s += w_gc_bonus * f["gc_rg"]
    return s


def score_interaction(f: dict, w: tuple) -> float:
    """Linear + interaction terms."""
    w_prior, w_util, w_cheap, w_fid, w_sup, w_anti, w_ot_exc, w_pf, w_uf = w
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_prior * f["prior"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"] + w_sup * ms
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    s += w_pf * f["prior_x_fidelity"]
    s += w_uf * f["utility_x_fidelity"]
    return s


def score_two_stage(f: dict, w: tuple) -> float:
    """Two-stage: utility-dominant with prior modulation."""
    w_util, w_cheap, w_fid, w_prior_mod, w_anti, w_ot_exc, w_conc, w_gc = w
    s = w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"]
    s += w_prior_mod * f["prior"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    if f["concordant"]:
        s += w_conc
    if f["gc_significant"]:
        s += w_gc * f["gc_rg"]
    return s


def score_expanded(f: dict, w: tuple) -> float:
    """Expanded feature set with all evidence signals."""
    (w_prior, w_util, w_cheap, w_fid, w_anti, w_ot_exc,
     w_gc_rg, w_gc_sig_bonus, w_ot_area, w_ot_anc,
     w_h2, w_conc, w_endpoint, w_lexical) = w
    s = w_prior * f["prior"] + w_util * f["utility"] + w_cheap * f["cheap"] + w_fid * f["fidelity"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    if f["gc_significant"]:
        s += w_gc_rg * f["gc_rg"] + w_gc_sig_bonus
    if f["ot_area_match"]:
        s += w_ot_area
    s += w_ot_anc * min(f["ot_ancestor"], 5)
    s += w_h2 * min(f["h2_ceiling"], 0.1) * 10
    if f["concordant"]:
        s += w_conc
    if f["is_same_endpoint"]:
        s += w_endpoint
    s += w_lexical * f["lexical"] / 100.0
    return s


def score_cheap_dominant(f: dict, w: tuple) -> float:
    """cheap_rank_score already encodes GC+fidelity+lexical+models.
    Pair it with prior + OT bonus."""
    w_cheap, w_prior, w_ot_exc, w_anti, w_conc = w
    s = w_cheap * f["cheap"] + w_prior * f["prior"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    if f["concordant"]:
        s += w_conc
    return s


def score_rank_based(fields_by_id: dict[str, dict], w: tuple) -> str:
    """Reciprocal rank aggregation."""
    w_pr, w_ur, w_fr, w_cr, w_ot_exc = w
    bids = list(fields_by_id.keys())
    if not bids:
        return ""

    def rank_by(key: str) -> dict[str, int]:
        sorted_bids = sorted(bids, key=lambda b: (-fields_by_id[b][key], b))
        return {b: i + 1 for i, b in enumerate(sorted_bids)}

    pr = rank_by("prior")
    ur = rank_by("utility")
    fr = rank_by("fidelity")
    cr = rank_by("cheap")

    best_bid, best_s = "", -float("inf")
    for bid in bids:
        f = fields_by_id[bid]
        s = w_pr / pr[bid] + w_ur / ur[bid] + w_fr / fr[bid] + w_cr / cr[bid]
        if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
            s += w_ot_exc * (f["ot_overlap"] - 2.0)
        if s > best_s or (s == best_s and bid < best_bid):
            best_s, best_bid = s, bid
    return best_bid


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def eval_scoring(prepared: list[PreparedRecord], scorer, w: tuple) -> tuple[int, list[str], list[str]]:
    hits, missed = [], []
    for tid, oracle_id, fields_by_id in prepared:
        best_id = max(fields_by_id, key=lambda bid: (scorer(fields_by_id[bid], w), bid))
        (hits if best_id == oracle_id else missed).append(tid)
    return len(hits), hits, missed


def eval_rank_based(prepared: list[PreparedRecord], w: tuple) -> tuple[int, list[str], list[str]]:
    hits, missed = [], []
    for tid, oracle_id, fields_by_id in prepared:
        best_id = score_rank_based(fields_by_id, w)
        (hits if best_id == oracle_id else missed).append(tid)
    return len(hits), hits, missed


def optimize_scoring(prepared, scorer, bounds, label="", n_seeds=8, maxiter=4000, popsize=25):
    best_w, best_hits = None, -1
    for seed in range(n_seeds):
        def objective(params, _s=seed):
            return -eval_scoring(prepared, scorer, tuple(params))[0]

        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=maxiter, popsize=popsize, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed * 1000 + 42, workers=1, polish=True,
        )
        w = tuple(result.x)
        h = eval_scoring(prepared, scorer, w)[0]
        if h > best_hits:
            best_hits, best_w = h, w
        if label:
            print(f"    seed {seed}: {h} hits")
    return best_w, best_hits


def optimize_rank_based(prepared, bounds, n_seeds=8, maxiter=4000, popsize=25):
    best_w, best_hits = None, -1
    for seed in range(n_seeds):
        def objective(params, _s=seed):
            return -eval_rank_based(prepared, tuple(params))[0]

        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=maxiter, popsize=popsize, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed * 1000 + 42, workers=1, polish=True,
        )
        w = tuple(result.x)
        h = eval_rank_based(prepared, w)[0]
        if h > best_hits:
            best_hits, best_w = h, w
        print(f"    seed {seed}: {h} hits")
    return best_w, best_hits


def diagnose_missed(prepared, scorer, w, label=""):
    """Show why oracle lost for each missed target."""
    _, _, missed = eval_scoring(prepared, scorer, w)
    if not missed:
        print(f"  [{label}] All targets hit!")
        return
    print(f"\n  [{label}] {len(missed)} missed targets:")
    for tid, oracle_id, fields_by_id in prepared:
        if tid not in missed:
            continue
        of = fields_by_id[oracle_id]
        os = scorer(of, w)
        best_id = max(fields_by_id, key=lambda bid: (scorer(fields_by_id[bid], w), bid))
        bf = fields_by_id[best_id]
        bs = scorer(bf, w)
        print(f"    {tid}: oracle={oracle_id[:20]:20s} P={of['prior']:.3f} U={of['utility']:6.2f} "
              f"C={of['cheap']:5.2f} F={of['fidelity']:.3f} score={os:.4f}")
        print(f"          sel   ={best_id[:20]:20s} P={bf['prior']:.3f} U={bf['utility']:6.2f} "
              f"C={bf['cheap']:5.2f} F={bf['fidelity']:.3f} score={bs:.4f}  gap={bs-os:.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("OFFLINE SELECTION OPTIMIZATION v2 (fast)")
    print("=" * 70)

    prepared, unreachable = load_data()
    total = len(prepared)
    print(f"Reachable: {total}, Unreachable: {len(unreachable)} → {unreachable}")
    print(f"Ceiling: {total}/80\n")

    from experiments.contribution3.transfer.agent import UNIFIED_CONFIG

    # === 0. Baseline ===
    print("=== 0. Baseline (UNIFIED_CONFIG) ===")
    w0 = (
        UNIFIED_CONFIG.w_transferability_prior, UNIFIED_CONFIG.w_selection_utility,
        UNIFIED_CONFIG.w_selection_cheap_rank, UNIFIED_CONFIG.w_selection_fidelity,
        UNIFIED_CONFIG.w_selection_model_support, UNIFIED_CONFIG.w_selection_anti_dominance,
        UNIFIED_CONFIG.w_ot_exceptional,
    )
    h0, _, m0 = eval_scoring(prepared, score_linear, w0)
    print(f"  {h0}/{total} hits | missed: {m0}\n")

    # === 1. Linear optimized ===
    print("=== 1. Linear ===")
    bounds1 = [(0, 5), (0, 3), (0, 3), (0, 5), (0, 1), (0, 1), (0, 3)]
    w1, h1 = optimize_scoring(prepared, score_linear, bounds1, "linear")
    _, _, m1 = eval_scoring(prepared, score_linear, w1)
    print(f"  BEST: {h1}/{total} | W: prior={w1[0]:.4f} util={w1[1]:.4f} cheap={w1[2]:.4f} "
          f"fid={w1[3]:.4f} sup={w1[4]:.4f} anti={w1[5]:.4f} ot={w1[6]:.4f}")
    print(f"  missed: {m1}\n")

    # === 2. Dampened prior ===
    print("=== 2. Dampened prior ===")
    bounds2 = [(0.05, 3), (0, 5), (0.05, 3), (0, 5), (0, 3), (0, 3), (0, 1), (0, 3)]
    w2, h2 = optimize_scoring(prepared, score_dampened_prior, bounds2, "dampened")
    _, _, m2 = eval_scoring(prepared, score_dampened_prior, w2)
    print(f"  BEST: {h2}/{total} | missed: {m2}\n")

    # === 3. Prior ceiling ===
    print("=== 3. Prior ceiling ===")
    bounds3 = [(0.1, 1.0), (0, 5), (0, 5), (0, 3), (0, 3), (0, 1), (0, 3)]
    w3, h3 = optimize_scoring(prepared, score_prior_ceiling, bounds3, "ceiling")
    _, _, m3 = eval_scoring(prepared, score_prior_ceiling, w3)
    print(f"  BEST: {h3}/{total} | missed: {m3}\n")

    # === 4. Concordance + endpoint + GC ===
    print("=== 4. Concordance+endpoint+GC ===")
    bounds4 = [(0, 5), (0, 3), (0, 3), (0, 5), (0, 1), (0, 1), (0, 3), (0, 3), (0, 3), (0, 3)]
    w4, h4 = optimize_scoring(prepared, score_concordance_endpoint, bounds4, "conc+ep")
    _, _, m4 = eval_scoring(prepared, score_concordance_endpoint, w4)
    print(f"  BEST: {h4}/{total} | missed: {m4}\n")

    # === 5. Interaction ===
    print("=== 5. Interaction ===")
    bounds5 = [(0, 5), (0, 3), (0, 3), (0, 5), (0, 1), (0, 1), (0, 3), (0, 5), (0, 3)]
    w5, h5 = optimize_scoring(prepared, score_interaction, bounds5, "interaction")
    _, _, m5 = eval_scoring(prepared, score_interaction, w5)
    print(f"  BEST: {h5}/{total} | missed: {m5}\n")

    # === 6. Two-stage ===
    print("=== 6. Two-stage ===")
    bounds6 = [(0, 5), (0, 3), (0, 5), (0, 3), (0, 1), (0, 3), (0, 3), (0, 3)]
    w6, h6 = optimize_scoring(prepared, score_two_stage, bounds6, "two-stage")
    _, _, m6 = eval_scoring(prepared, score_two_stage, w6)
    print(f"  BEST: {h6}/{total} | missed: {m6}\n")

    # === 7. Expanded features ===
    print("=== 7. Expanded ===")
    bounds7 = [(0,5),(0,3),(0,3),(0,5),(0,1),(0,3),(0,3),(0,2),(0,2),(0,2),(0,2),(0,3),(0,3),(0,3)]
    w7, h7 = optimize_scoring(prepared, score_expanded, bounds7, "expanded")
    _, _, m7 = eval_scoring(prepared, score_expanded, w7)
    print(f"  BEST: {h7}/{total} | missed: {m7}\n")

    # === 8. cheap-dominant ===
    print("=== 8. Cheap-dominant ===")
    bounds8 = [(0, 5), (0, 5), (0, 3), (0, 1), (0, 3)]
    w8, h8 = optimize_scoring(prepared, score_cheap_dominant, bounds8, "cheap-dom")
    _, _, m8 = eval_scoring(prepared, score_cheap_dominant, w8)
    print(f"  BEST: {h8}/{total} | missed: {m8}\n")

    # === 9. Rank-based ===
    print("=== 9. Rank-based ===")
    bounds9 = [(0, 5), (0, 5), (0, 5), (0, 5), (0, 3)]
    w9, h9 = optimize_rank_based(prepared, bounds9)
    _, _, m9 = eval_rank_based(prepared, w9)
    print(f"  BEST: {h9}/{total} | missed: {m9}\n")

    # === Summary ===
    print("=" * 70)
    print("SUMMARY (sorted by hits)")
    print("=" * 70)
    results = [
        ("0. Baseline", h0, m0, w0, score_linear),
        ("1. Linear opt", h1, m1, w1, score_linear),
        ("2. Dampened prior", h2, m2, w2, score_dampened_prior),
        ("3. Prior ceiling", h3, m3, w3, score_prior_ceiling),
        ("4. Conc+EP+GC", h4, m4, w4, score_concordance_endpoint),
        ("5. Interaction", h5, m5, w5, score_interaction),
        ("6. Two-stage", h6, m6, w6, score_two_stage),
        ("7. Expanded", h7, m7, w7, score_expanded),
        ("8. Cheap-dom", h8, m8, w8, score_cheap_dominant),
        ("9. Rank-based", h9, m9, w9, None),
    ]
    for name, h, m, w, _ in sorted(results, key=lambda x: -x[1]):
        print(f"  {name:25s}: {h:2d}/{total}")

    # Always-missed
    all_missed = [set(m) for _, _, m, _, _ in results]
    always = set.intersection(*all_missed) if all_missed else set()
    print(f"\n  Always missed by ALL: {sorted(always)}")
    print(f"  Unreachable (not in shortlist): {unreachable}")

    # Best approach diagnostics
    best = max(results, key=lambda x: x[1])
    print(f"\n  BEST: {best[0]} → {best[1]}/{total}")
    if best[4] is not None:
        diagnose_missed(prepared, best[4], best[3], best[0])

    # Print weights for the best approach
    print(f"\n  Best weights: {best[3]}")


if __name__ == "__main__":
    main()
