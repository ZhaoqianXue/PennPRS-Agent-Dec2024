"""Max-of-percentile-experts with degeneracy constraints.

Investigates whether a NON-DEGENERATE version can beat 72/80 linear ceiling.
Key constraint: no single feature weight can dominate all others.
"""
from __future__ import annotations
import math, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.verify_max_pct import (
    load_all, build_pct_data, FEAT_KEYS,
)

def eval_max_pct_topK(prebuilt, w, K):
    """Evaluate max-of-percentile with ACTUAL top-K shortlist selection.

    Unlike the rank-based eval (which exploits ties), this sorts by score
    and takes the top K, with random tie-breaking simulated via averaging.
    """
    w = np.abs(np.array(w))
    hits = 0
    details = []
    for tid, oidx, pct, bids in prebuilt:
        if oidx < 0:
            continue
        weighted = pct * w[np.newaxis, :]
        scores = np.max(weighted, axis=1)
        oracle_score = scores[oidx]

        n_strictly_better = int(np.sum(scores > oracle_score))
        n_tied = int(np.sum(scores == oracle_score))

        # With actual top-K: oracle is included iff n_strictly_better < K
        # But if there are ties at the boundary, it depends on tie-breaking.
        # Worst case: oracle is last among ties
        # Best case: oracle is first among ties
        # Expected case: oracle has 1/n_tied chance per tied slot

        # Conservative: oracle included only if ALL tied candidates fit
        conservative_in = (n_strictly_better + n_tied) <= K
        # Optimistic: oracle included if ANY tied slot is available
        optimistic_in = n_strictly_better < K
        # Expected: probability-based
        if n_strictly_better >= K:
            prob_in = 0.0
        elif n_strictly_better + n_tied <= K:
            prob_in = 1.0
        else:
            available_slots = K - n_strictly_better
            prob_in = available_slots / n_tied

        hits += 1 if conservative_in else 0
        details.append({
            "tid": tid, "n_better": n_strictly_better, "n_tied": n_tied,
            "conservative": conservative_in, "optimistic": optimistic_in,
            "prob": prob_in,
        })

    expected_hits = sum(d["prob"] for d in details)
    conservative_hits = sum(1 for d in details if d["conservative"])
    optimistic_hits = sum(1 for d in details if d["optimistic"])
    return conservative_hits, optimistic_hits, expected_hits, details


def optimize_constrained(prebuilt, K, max_weight_ratio=3.0, n_seeds=10):
    """Optimize max-of-percentile weights with constraint that no single
    weight exceeds max_weight_ratio × median(weights).

    Uses a penalty term to discourage degeneracy.
    """
    n_feats = len(FEAT_KEYS)

    def objective(params):
        w = np.abs(np.array(params))

        # Penalty for weight concentration
        w_sorted = np.sort(w)[::-1]
        ratio = w_sorted[0] / (np.median(w) + 1e-6)
        penalty = max(0, ratio - max_weight_ratio) * 10

        hits = 0
        for tid, oidx, pct, bids in prebuilt:
            if oidx < 0:
                continue
            weighted = pct * w[np.newaxis, :]
            scores = np.max(weighted, axis=1)
            oracle_score = scores[oidx]

            # Use CONSERVATIVE criterion: all tied must fit
            n_better = int(np.sum(scores > oracle_score))
            n_tied = int(np.sum(scores == oracle_score))
            if n_better + n_tied <= K:
                hits += 1

        return -(hits - penalty)

    bounds = [(0.1, 10)] * n_feats
    best_w = None
    best_score = float('inf')

    for seed in range(n_seeds):
        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=500, popsize=20, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed, workers=1, polish=True,
        )
        if result.fun < best_score:
            best_score = result.fun
            best_w = result.x

    return best_w, -best_score


def optimize_expected(prebuilt, K, n_seeds=10):
    """Optimize expected recall under random tie-breaking (no constraint)."""
    n_feats = len(FEAT_KEYS)

    def objective(params):
        w = np.abs(np.array(params))
        expected = 0
        for tid, oidx, pct, bids in prebuilt:
            if oidx < 0:
                continue
            weighted = pct * w[np.newaxis, :]
            scores = np.max(weighted, axis=1)
            oracle_score = scores[oidx]
            n_better = int(np.sum(scores > oracle_score))
            n_tied = int(np.sum(scores == oracle_score))
            if n_better >= K:
                prob = 0.0
            elif n_better + n_tied <= K:
                prob = 1.0
            else:
                prob = (K - n_better) / n_tied
            expected += prob
        return -expected

    bounds = [(0.1, 10)] * n_feats
    best_w = None
    best_score = float('inf')

    for seed in range(n_seeds):
        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=500, popsize=20, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed, workers=1, polish=True,
        )
        if result.fun < best_score:
            best_score = result.fun
            best_w = result.x

    return best_w, -best_score


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    prebuilt = build_pct_data(data)
    print(f"Loaded {total} targets\n")

    # === 1. Evaluate the degenerate K=95 weights with ACTUAL top-K ===
    from experiments.contribution3.transfer.eval.verify_max_pct import W_K95
    print("=" * 80)
    print("DEGENERATE WEIGHTS (K=95) - actual top-K evaluation")
    print("=" * 80)
    for K in [90, 95, 100, 110, 120]:
        cons, opt, exp, details = eval_max_pct_topK(prebuilt, W_K95, K)
        print(f"  K={K}: conservative={cons}/{total} optimistic={opt}/{total} expected={exp:.1f}/{total}")
        if K == 95:
            tied = [(d["tid"], d["n_tied"]) for d in details if d["n_tied"] > 10]
            print(f"    Targets with >10 ties: {len(tied)}")
            miss_cons = [d["tid"] for d in details if not d["conservative"]]
            print(f"    Conservative misses: {miss_cons[:20]}")

    # === 2. Constrained optimization (prevent degeneracy) ===
    print("\n" + "=" * 80)
    print("CONSTRAINED OPTIMIZATION (max_weight_ratio=3)")
    print("=" * 80)
    for K in [90, 95, 100, 110, 120, 130, 150]:
        w, score = optimize_constrained(prebuilt, K, max_weight_ratio=3.0, n_seeds=5)
        cons, opt, exp, details = eval_max_pct_topK(prebuilt, w, K)
        print(f"  K={K}: conservative={cons}/{total} expected={exp:.1f}/{total} "
              f"weights={np.round(np.abs(w), 2)}")
        miss_cons = [d["tid"] for d in details if not d["conservative"]]
        if miss_cons:
            print(f"    Misses: {miss_cons}")

    # === 3. Expected-value optimization (no constraint but proper tie handling) ===
    print("\n" + "=" * 80)
    print("EXPECTED-VALUE OPTIMIZATION (random tie-breaking)")
    print("=" * 80)
    for K in [90, 95, 100, 110, 120, 130, 150]:
        w, score = optimize_expected(prebuilt, K, n_seeds=5)
        cons, opt, exp, details = eval_max_pct_topK(prebuilt, w, K)
        w_abs = np.abs(w)
        ratio = w_abs.max() / (np.median(w_abs) + 1e-6)
        print(f"  K={K}: conservative={cons}/{total} expected={exp:.1f}/{total} "
              f"max/med_ratio={ratio:.1f} weights={np.round(w_abs, 2)}")
        miss_cons = [d["tid"] for d in details if not d["conservative"]]
        if miss_cons:
            print(f"    Misses: {miss_cons}")

    # === 4. Two-stage: max-pct for main + rescue for hard targets ===
    print("\n" + "=" * 80)
    print("HYBRID: max-pct main ranking + rescue tracks")
    print("=" * 80)

    # Use constrained weights for main ranking, then rescue
    for main_K in [70, 80, 90]:
        w_main, _ = optimize_constrained(prebuilt, main_K, max_weight_ratio=3.0, n_seeds=3)
        w_abs = np.abs(np.array(w_main))

        for rescue_budget in [20, 30, 40, 50]:
            cap = main_K + rescue_budget
            hits = 0
            misses = []
            for tid, oidx, pct, bids in prebuilt:
                if oidx < 0:
                    continue
                n = len(bids)
                # Main ranking
                weighted = pct * w_abs[np.newaxis, :]
                scores = np.max(weighted, axis=1)
                order = np.argsort(-scores)
                shortlist_idx = set(order[:main_K].tolist())

                # Rescue: add candidates by individual features
                rescue_feats = ["fidelity", "cheap", "log_models", "gc_rg"]
                per_feat_budget = rescue_budget // len(rescue_feats)
                for fi, fname in enumerate(rescue_feats):
                    fj = FEAT_KEYS.index(fname)
                    feat_order = np.argsort(-pct[:, fj])
                    added = 0
                    for idx in feat_order:
                        if len(shortlist_idx) >= cap:
                            break
                        if idx not in shortlist_idx:
                            shortlist_idx.add(idx)
                            added += 1
                            if added >= per_feat_budget:
                                break

                if oidx in shortlist_idx:
                    hits += 1
                else:
                    misses.append(tid)

            if hits >= 73:
                print(f"  main={main_K} rescue={rescue_budget} cap={cap}: {hits}/{total} miss={misses}")


if __name__ == "__main__":
    main()
