"""Non-linear scoring approaches to break the 26/61 ceiling.

Key insight: BMI has prior≈0.94 but fidelity≈0.71. Disease-specific oracles have
prior≈0.70 but fidelity≈0.85+. Dampening prior reduces its dominance, letting
fidelity discriminate.

Approaches:
1. Dampened prior: prior^alpha * fidelity^beta + additive terms
2. Log prior: log(1+prior*K) + linear fidelity
3. Prior ceiling: min(prior, cap) + fidelity
4. Fidelity-dominant: fidelity^2 + sqrt(prior) + additive
5. Harmonic mean of prior & fidelity + additive
6. Conditional: different weights when n_models > threshold
"""
from __future__ import annotations
import math, sys
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.offline_sim_selection_80 import (
    load_data, eval_scoring, PreparedRecord,
)


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_dampened_prior(f: dict, w: tuple) -> float:
    """prior^alpha * w_core + fidelity^beta * w_fid + additive."""
    alpha, w_core, beta, w_fid, w_util, w_cheap, w_anti, w_ot_exc = w
    alpha = max(alpha, 0.05)
    beta = max(beta, 0.05)
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_core * (f["prior"] ** alpha) + w_fid * (f["fidelity"] ** beta)
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


def score_log_prior(f: dict, w: tuple) -> float:
    """log(1 + prior * K) replaces linear prior."""
    K, w_lp, w_fid, w_util, w_cheap, w_anti, w_ot_exc = w
    K = max(K, 0.1)
    s = w_lp * math.log1p(f["prior"] * K) + w_fid * f["fidelity"]
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
    ms = math.log1p(min(max(f["n_models"], 0), 100))
    s = w_prior * p + w_fid * f["fidelity"]
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


def score_fidelity_dominant(f: dict, w: tuple) -> float:
    """fidelity^beta + sqrt(prior) + additive."""
    beta, w_fid, w_sqp, w_util, w_cheap, w_anti, w_ot_exc, w_conc = w
    beta = max(beta, 0.05)
    s = w_fid * (f["fidelity"] ** beta) + w_sqp * math.sqrt(f["prior"])
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    if w_conc > 0 and f.get("concordant"):
        s += w_conc
    return s


def score_harmonic(f: dict, w: tuple) -> float:
    """Weighted harmonic mean of prior & fidelity + additive."""
    w_hm, w_util, w_cheap, w_anti, w_ot_exc, w_gc = w
    p = max(f["prior"], 0.001)
    fd = max(f["fidelity"], 0.001)
    hm = 2.0 * p * fd / (p + fd)  # harmonic mean
    s = w_hm * hm + w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    s += w_gc * f["gc_rg"]
    return s


def score_conditional(f: dict, w: tuple) -> float:
    """Different effective weights based on n_models threshold.
    w = (w_prior_lo, w_prior_hi, w_fid_lo, w_fid_hi, threshold,
         w_util, w_cheap, w_ot_exc)"""
    w_pl, w_ph, w_fl, w_fh, thresh, w_util, w_cheap, w_ot_exc = w
    thresh = max(thresh, 1)
    if f["n_models"] <= thresh:
        s = w_pl * f["prior"] + w_fl * f["fidelity"]
    else:
        s = w_ph * f["prior"] + w_fh * f["fidelity"]
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


def score_anti_model_count(f: dict, w: tuple) -> float:
    """Strong penalty proportional to sqrt(n_models) * prior.
    Targets specifically the prior*popularity interaction."""
    w_prior, w_fid, w_util, w_cheap, w_ot_exc, w_anti_scale, w_anti_thresh = w
    s = w_prior * f["prior"] + w_fid * f["fidelity"]
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    # Penalty scaled by prior * excess model count
    thresh = max(w_anti_thresh, 1)
    if f["n_models"] > thresh:
        excess = math.log(f["n_models"] / thresh)
        s -= w_anti_scale * f["prior"] * excess
    return s


def score_prior_gap_penalty(f: dict, w: tuple) -> float:
    """Prior rescaled by gap from a 'fair' baseline (median-ish prior).
    Bundles far above the baseline get diminishing returns."""
    baseline, gamma, w_prior, w_fid, w_util, w_cheap, w_ot_exc, w_anti = w
    baseline = max(baseline, 0.01)
    gamma = max(gamma, 0.01)
    # Rescale prior: diminishing returns above baseline
    p = f["prior"]
    if p > baseline:
        p = baseline + (p - baseline) ** gamma
    s = w_prior * p + w_fid * f["fidelity"]
    s += w_util * f["utility"] + w_cheap * f["cheap"]
    if w_anti > 0 and f["n_models"] > 50:
        s -= w_anti * math.log(f["n_models"] / 50)
    if w_ot_exc > 0 and f["ot_overlap"] > 2.0:
        s += w_ot_exc * (f["ot_overlap"] - 2.0)
    return s


# ---------------------------------------------------------------------------
# Optimizer
# ---------------------------------------------------------------------------

def optimize(prepared, scorer, bounds, label, seeds=range(42, 52)):
    """Run differential_evolution with multiple seeds, return best."""
    best_h = -1
    best_w = None
    best_ids = None
    for seed in seeds:
        def objective(params):
            w = tuple(params)
            hits, _ = eval_scoring(prepared, scorer, w)
            return -hits

        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=3000, popsize=20, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed, workers=1, polish=True,
        )
        w = tuple(result.x)
        h, ids = eval_scoring(prepared, scorer, w)
        if h > best_h:
            best_h = h
            best_w = w
            best_ids = ids
    missed = [t for t, *_ in prepared if t not in best_ids]
    return best_w, best_h, best_ids, missed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading data...")
    prepared, unreachable = load_data()
    total = len(prepared)
    print(f"Prepared: {total}, unreachable: {len(unreachable)}\n")

    approaches = [
        ("1. Dampened prior (prior^alpha)",
         score_dampened_prior,
         [(0.05, 1.0), (0, 5), (0.05, 3.0), (0, 5), (0, 1), (0, 1), (0, 1), (0, 2)]),

        ("2. Log prior",
         score_log_prior,
         [(0.1, 50), (0, 5), (0, 5), (0, 1), (0, 1), (0, 1), (0, 2)]),

        ("3. Prior ceiling",
         score_prior_ceiling,
         [(0.3, 1.0), (0, 5), (0, 5), (0, 1), (0, 1), (0, 1), (0, 2)]),

        ("4. Fidelity-dominant + sqrt(prior)",
         score_fidelity_dominant,
         [(0.05, 3.0), (0, 10), (0, 5), (0, 1), (0, 1), (0, 1), (0, 2), (0, 3)]),

        ("5. Harmonic mean(prior, fid)",
         score_harmonic,
         [(0, 10), (0, 1), (0, 1), (0, 1), (0, 2), (0, 3)]),

        ("6. Conditional (lo/hi n_models)",
         score_conditional,
         [(0, 5), (0, 5), (0, 5), (0, 5), (1, 150), (0, 1), (0, 1), (0, 2)]),

        ("7. Anti-model-count * prior",
         score_anti_model_count,
         [(0, 5), (0, 5), (0, 1), (0, 1), (0, 2), (0, 5), (1, 120)]),

        ("8. Prior gap penalty (diminishing above baseline)",
         score_prior_gap_penalty,
         [(0.3, 0.95), (0.01, 1.0), (0, 5), (0, 5), (0, 1), (0, 1), (0, 2), (0, 1)]),
    ]

    results = []
    for label, scorer, bounds in approaches:
        print(f"=== {label} ===")
        w, h, ids, missed = optimize(prepared, scorer, bounds, label)
        results.append((label, h, w, missed))
        print(f"  Hits: {h}/{total}")
        print(f"  Weights: {', '.join(f'{v:.4f}' for v in w)}")
        print(f"  Missed: {missed}\n")

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for label, h, w, missed in sorted(results, key=lambda x: -x[1]):
        print(f"  {h}/{total}  {label}")

    # Find always-missed
    all_missed = [set(m) for _, _, _, m in results]
    always = set.intersection(*all_missed) if all_missed else set()
    ever_hit = set()
    for _, _, _, m in results:
        for t, *_ in prepared:
            if t not in m:
                ever_hit.add(t)
    print(f"\nAlways missed ({len(always)}): {sorted(always)}")
    print(f"Ever hit ({len(ever_hit)}): {sorted(ever_hit)}")
    print(f"Sometimes missed, sometimes hit: {sorted(ever_hit - set(t for t, *_ in prepared) + always)}")

    # Best approach: show which BMI-oracle targets are still hit
    best_label, best_h, best_w, best_missed = max(results, key=lambda x: x[1])
    bmi_oracle_tids = [t for t, o, _ in prepared if o == "efo_0004340"]
    bmi_oracle_hit = [t for t in bmi_oracle_tids if t not in best_missed]
    bmi_oracle_miss = [t for t in bmi_oracle_tids if t in best_missed]
    print(f"\nBest approach: {best_label}")
    print(f"  BMI-oracle targets hit: {len(bmi_oracle_hit)}/{len(bmi_oracle_tids)} {bmi_oracle_hit}")
    print(f"  BMI-oracle targets missed: {bmi_oracle_miss}")
    non_bmi_oracle_hit = [t for t, o, _ in prepared if o != "efo_0004340" and t not in best_missed]
    non_bmi_oracle_miss = [t for t, o, _ in prepared if o != "efo_0004340" and t in best_missed]
    print(f"  Non-BMI oracle hit: {len(non_bmi_oracle_hit)}/{len([1 for _,o,_ in prepared if o != 'efo_0004340'])} {non_bmi_oracle_hit}")


if __name__ == "__main__":
    main()
