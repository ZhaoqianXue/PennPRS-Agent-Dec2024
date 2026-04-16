"""Fast offline selection optimization — random + DE hybrid.

Uses random sampling (500K samples) for exploration, then DE polish
on the best approach. Much faster than pure DE for discrete objectives.
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RUN_DIR = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653"
)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_data():
    raw = json.loads((RUN_DIR / "cards_light.json").read_text())
    oracle_info = {}
    with open(RUN_DIR / "shortlist_recall.csv") as f:
        for r in csv.DictReader(f):
            oracle_info[r["target_id"]] = {
                "oid": r["transfer_eligible_global_oracle_bundle_id"],
                "in_sl": r["oracle_in_shortlist"] == "True",
            }

    targets = []  # list of (tid, oracle_idx, feature_matrix, bundle_ids)
    unreachable = []
    for entry in raw:
        tid = entry["tid"]
        if entry.get("outcome") != "MATCHED":
            continue
        info = oracle_info.get(tid, {})
        oid = info.get("oid")
        if not oid or not info.get("in_sl"):
            unreachable.append(tid)
            continue

        bids = [c["bid"] for c in entry["cards"]]
        if oid not in bids:
            unreachable.append(tid)
            continue
        oracle_idx = bids.index(oid)

        # Build feature matrix: each row is a candidate, columns are features
        feats = []
        for c in entry["cards"]:
            ms = math.log1p(min(max(c["n_mod"], 0), 100))
            anti = math.log(c["n_mod"] / 50) if c["n_mod"] > 50 else 0.0
            ot_exc = max(c["ot_ov"] - 2.0, 0.0)
            feats.append([
                c["prior"],                              # 0: prior
                c["util"],                               # 1: utility
                c["cheap"],                              # 2: cheap_rank
                c["fid"],                                # 3: fidelity
                ms,                                      # 4: model_support
                -anti,                                   # 5: anti_dominance (negated)
                ot_exc,                                  # 6: ot_exceptional
                float(c["conc"]),                        # 7: concordant
                float(c["arch"] == "same-endpoint disease"),  # 8: same_endpoint
                c["gc_rg"] * float(c["gc_sig"]),         # 9: gc_signal (rg if sig)
                c["prior"] * c["fid"],                   # 10: prior*fidelity
                c["util"] * c["fid"],                    # 11: utility*fidelity
                min(c["prior"], 0.85),                   # 12: capped prior
                c["prior"] ** 0.5,                       # 13: sqrt prior
                c["fid"] ** 2,                           # 14: fidelity^2
                c["lex"] / 100.0,                        # 15: lexical
                min(c["ot_anc"], 5),                     # 16: ot_ancestor
                float(c["ot_area"]),                     # 17: ot_area_match
                min(c["h2_ceil"], 0.1) * 10,             # 18: h2_ceiling
                float(c["gc_sig"]),                      # 19: gc_significant (binary)
            ])
        targets.append((tid, oracle_idx, np.array(feats, dtype=np.float64), bids))

    return targets, unreachable


# ---------------------------------------------------------------------------
# Vectorized evaluation
# ---------------------------------------------------------------------------

def eval_linear_weights(targets, w):
    """Evaluate a weight vector. Returns count of oracle hits."""
    hits = 0
    for tid, oidx, feats, bids in targets:
        scores = feats @ w
        best = np.argmax(scores)
        if best == oidx:
            hits += 1
    return hits


def eval_linear_weights_detail(targets, w):
    """Return hits list and missed list."""
    hit_tids, miss_tids = [], []
    for tid, oidx, feats, bids in targets:
        scores = feats @ w
        best = np.argmax(scores)
        (hit_tids if best == oidx else miss_tids).append(tid)
    return hit_tids, miss_tids


# ---------------------------------------------------------------------------
# Random search
# ---------------------------------------------------------------------------

def random_search(targets, n_features, n_samples=500000, seed=42):
    """Sample random weight vectors and return the best."""
    rng = np.random.default_rng(seed)
    best_hits, best_w = 0, None

    batch_size = 1000
    for batch_start in range(0, n_samples, batch_size):
        batch_end = min(batch_start + batch_size, n_samples)
        batch = batch_end - batch_start

        # Sample weights from various distributions
        ws = rng.uniform(-0.5, 5.0, size=(batch, n_features))
        # Force some weights to be non-negative for key features
        ws[:, 0] = np.abs(ws[:, 0])  # prior >= 0
        ws[:, 1] = np.abs(ws[:, 1])  # utility >= 0
        ws[:, 2] = np.abs(ws[:, 2])  # cheap >= 0
        ws[:, 3] = np.abs(ws[:, 3])  # fidelity >= 0

        for i in range(batch):
            h = eval_linear_weights(targets, ws[i])
            if h > best_hits:
                best_hits = h
                best_w = ws[i].copy()

    return best_w, best_hits


def targeted_search(targets, base_w, n_features, n_samples=200000, seed=42):
    """Search around a good solution with smaller perturbations."""
    rng = np.random.default_rng(seed)
    best_hits, best_w = eval_linear_weights(targets, base_w), base_w.copy()

    for _ in range(n_samples):
        w = base_w + rng.normal(0, 0.3, n_features)
        w[:4] = np.abs(w[:4])  # Keep main features non-negative
        h = eval_linear_weights(targets, w)
        if h > best_hits:
            best_hits = h
            best_w = w.copy()

    return best_w, best_hits


# ---------------------------------------------------------------------------
# Feature subset search
# ---------------------------------------------------------------------------

def search_feature_subsets(targets, n_features):
    """Try different feature combinations systematically."""
    # Define named feature subsets
    subsets = {
        "linear_basic": [0, 1, 2, 3, 4, 5, 6],                    # Original 7 features
        "linear+conc+ep": [0, 1, 2, 3, 4, 5, 6, 7, 8],            # + concordance + endpoint
        "linear+gc+conc+ep": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],      # + GC signal
        "interaction": [0, 1, 2, 3, 4, 5, 6, 10, 11],              # + prior*fid, util*fid
        "capped_prior": [1, 2, 3, 4, 5, 6, 7, 8, 9, 12],          # capped prior instead
        "sqrt_prior": [1, 2, 3, 4, 5, 6, 7, 8, 9, 13],            # sqrt prior
        "fid_dominant": [0, 1, 2, 4, 5, 6, 7, 8, 9, 14],          # fidelity^2
        "all_features": list(range(n_features)),                     # All 20 features
        "evidence_heavy": [0, 1, 2, 3, 5, 6, 7, 8, 9, 15, 16, 17, 18, 19],  # All evidence
    }
    return subsets


# ---------------------------------------------------------------------------
# DE polish
# ---------------------------------------------------------------------------

def de_polish(targets, initial_w, n_features, n_seeds=3, maxiter=1500, popsize=15):
    """Run DE with initialization near best random solution."""
    best_w, best_hits = initial_w.copy(), eval_linear_weights(targets, initial_w)

    for seed in range(n_seeds):
        bounds = [(-1.0, 5.0)] * n_features
        # Force non-negative bounds for main features
        for i in range(4):
            bounds[i] = (0, 5.0)

        # Clip x0 to bounds
        x0 = initial_w + np.random.default_rng(seed).normal(0, 0.1, n_features)
        for i, (lo, hi) in enumerate(bounds):
            x0[i] = np.clip(x0[i], lo, hi)

        def objective(params):
            return -eval_linear_weights(targets, np.array(params))

        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=maxiter, popsize=popsize, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed * 1000 + 42, workers=1, polish=True,
            x0=x0,
        )
        w = np.array(result.x)
        h = eval_linear_weights(targets, w)
        if h > best_hits:
            best_hits, best_w = h, w.copy()
        print(f"    DE seed {seed}: {h} hits")

    return best_w, best_hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("=" * 70)
    print("FAST OFFLINE SELECTION OPTIMIZATION")
    print("=" * 70)

    targets, unreachable = load_data()
    total = len(targets)
    n_features = targets[0][2].shape[1] if targets else 0
    print(f"Targets: {total} reachable, {len(unreachable)} unreachable → {unreachable}")
    print(f"Features per candidate: {n_features}")
    print(f"Ceiling: {total}/80\n")

    from experiments.contribution3.transfer.agent import UNIFIED_CONFIG

    # === 0. Baseline ===
    w_baseline = np.zeros(n_features)
    w_baseline[0] = UNIFIED_CONFIG.w_transferability_prior
    w_baseline[1] = UNIFIED_CONFIG.w_selection_utility
    w_baseline[2] = UNIFIED_CONFIG.w_selection_cheap_rank
    w_baseline[3] = UNIFIED_CONFIG.w_selection_fidelity
    w_baseline[4] = UNIFIED_CONFIG.w_selection_model_support
    w_baseline[5] = UNIFIED_CONFIG.w_selection_anti_dominance  # already negated in feature
    w_baseline[6] = UNIFIED_CONFIG.w_ot_exceptional

    h0 = eval_linear_weights(targets, w_baseline)
    _, m0 = eval_linear_weights_detail(targets, w_baseline)
    print(f"=== Baseline: {h0}/{total} hits ===")
    print(f"  missed: {m0}\n")

    # === Phase 1: Random search (fast, broad exploration) ===
    print("=== Phase 1: Random search (500K samples) ===")
    best_random_w, best_random_h = random_search(targets, n_features, n_samples=500000, seed=42)
    _, best_random_m = eval_linear_weights_detail(targets, best_random_w)
    print(f"  Best random: {best_random_h}/{total}")
    print(f"  Missed: {best_random_m}")
    print(f"  Time: {time.time()-t0:.1f}s\n")

    # === Phase 1b: Targeted search around best random ===
    print("=== Phase 1b: Targeted perturbation (200K samples) ===")
    best_targeted_w, best_targeted_h = targeted_search(targets, best_random_w, n_features, n_samples=200000)
    _, best_targeted_m = eval_linear_weights_detail(targets, best_targeted_w)
    print(f"  Best targeted: {best_targeted_h}/{total}")
    print(f"  Missed: {best_targeted_m}")
    print(f"  Time: {time.time()-t0:.1f}s\n")

    # === Phase 2: Feature subset search ===
    print("=== Phase 2: Feature subset search ===")
    subsets = search_feature_subsets(targets, n_features)
    best_subset_name, best_subset_h, best_subset_w = "", 0, None

    for name, feat_indices in subsets.items():
        # Create targets with subset of features
        sub_targets = [
            (tid, oidx, feats[:, feat_indices], bids)
            for tid, oidx, feats, bids in targets
        ]
        n_sub = len(feat_indices)
        w, h = random_search(sub_targets, n_sub, n_samples=300000, seed=42)
        _, m = eval_linear_weights_detail(sub_targets, w)
        print(f"  {name:20s}: {h}/{total} missed={m}")
        if h > best_subset_h:
            best_subset_h, best_subset_name = h, name
            # Expand to full weight vector
            full_w = np.zeros(n_features)
            for i, fi in enumerate(feat_indices):
                full_w[fi] = w[i]
            best_subset_w = full_w

    print(f"\n  Best subset: {best_subset_name} → {best_subset_h}/{total}")
    print(f"  Time: {time.time()-t0:.1f}s\n")

    # === Phase 3: DE polish on best solution ===
    print("=== Phase 3: DE polish on best solution ===")
    best_so_far = max(
        [(best_random_h, best_random_w), (best_targeted_h, best_targeted_w),
         (best_subset_h, best_subset_w)],
        key=lambda x: x[0]
    )
    polish_w, polish_h = de_polish(targets, best_so_far[1], n_features, n_seeds=3, maxiter=2000, popsize=20)
    _, polish_m = eval_linear_weights_detail(targets, polish_w)
    print(f"  DE polish: {polish_h}/{total}")
    print(f"  Missed: {polish_m}")
    print(f"  Time: {time.time()-t0:.1f}s\n")

    # === Phase 4: Also run DE from scratch (the approaches that matter most) ===
    print("=== Phase 4: DE from scratch on all features ===")
    bounds_all = [(0, 5)] * 4 + [(-1, 3)] * (n_features - 4)
    for seed in range(5):
        def objective(params):
            return -eval_linear_weights(targets, np.array(params))
        result = differential_evolution(
            objective, bounds=bounds_all,
            maxiter=2000, popsize=20, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed * 1000 + 42, workers=1, polish=True,
        )
        w = np.array(result.x)
        h = eval_linear_weights(targets, w)
        _, m = eval_linear_weights_detail(targets, w)
        print(f"  DE seed {seed}: {h}/{total} missed={m}")
        if h > polish_h:
            polish_h, polish_w, polish_m = h, w, m

    print(f"\n  Overall best DE: {polish_h}/{total}")
    print(f"  Time: {time.time()-t0:.1f}s\n")

    # === Final summary ===
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    final_w = polish_w
    final_h = polish_h
    _, final_m = eval_linear_weights_detail(targets, final_w)
    print(f"  Baseline:  {h0}/{total}")
    print(f"  Optimized: {final_h}/{total}")
    print(f"  Improvement: +{final_h - h0}")
    print(f"  Missed: {final_m}")
    print(f"  Unreachable: {unreachable}")

    # Print weights
    feat_names = [
        "prior", "utility", "cheap", "fidelity", "model_sup", "anti_dom", "ot_exc",
        "concordant", "same_endpoint", "gc_signal", "prior*fid", "util*fid",
        "capped_prior", "sqrt_prior", "fid^2", "lexical", "ot_ancestor",
        "ot_area", "h2_ceiling", "gc_sig_binary",
    ]
    print("\n  Optimized weights:")
    for i, (name, val) in enumerate(zip(feat_names, final_w)):
        if abs(val) > 0.001:
            print(f"    {name:16s}: {val:+.6f}")

    # Diagnose missed targets
    print(f"\n  Diagnosing {len(final_m)} missed targets:")
    for tid, oidx, feats, bids in targets:
        if tid not in final_m:
            continue
        scores = feats @ final_w
        oracle_score = scores[oidx]
        best_idx = np.argmax(scores)
        best_score = scores[best_idx]
        print(f"    {tid}: oracle={bids[oidx][:22]:22s} score={oracle_score:.4f} | "
              f"sel={bids[best_idx][:22]:22s} score={best_score:.4f} gap={best_score-oracle_score:.4f}")

    print(f"\n  Total time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
