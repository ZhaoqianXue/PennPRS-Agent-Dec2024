"""Coordinate search around DE-optimal weights.

Fast local search: perturb each weight individually and in combinations,
looking for 33/74 or better from the 32/74 baseline.
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path
import numpy as np
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RUN_DIR = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653"
)


def load_data():
    raw = json.loads((RUN_DIR / "cards_light.json").read_text())
    oracle_info = {}
    with open(RUN_DIR / "shortlist_recall.csv") as f:
        for r in csv.DictReader(f):
            oracle_info[r["target_id"]] = {
                "oid": r["transfer_eligible_global_oracle_bundle_id"],
                "in_sl": r["oracle_in_shortlist"] == "True",
            }
    targets = []
    for entry in raw:
        tid = entry["tid"]
        if entry.get("outcome") != "MATCHED":
            continue
        info = oracle_info.get(tid, {})
        oid = info.get("oid")
        if not oid or not info.get("in_sl"):
            continue
        bids = [c["bid"] for c in entry["cards"]]
        if oid not in bids:
            continue
        oracle_idx = bids.index(oid)
        feats = []
        for c in entry["cards"]:
            ms = math.log1p(min(max(c["n_mod"], 0), 100))
            anti = math.log(c["n_mod"] / 50) if c["n_mod"] > 50 else 0.0
            ot_exc = max(c["ot_ov"] - 2.0, 0.0)
            feats.append([
                c["prior"], c["util"], c["cheap"], c["fid"], ms, -anti, ot_exc,
                float(c["conc"]), float(c["arch"] == "same-endpoint disease"),
                c["gc_rg"] * float(c["gc_sig"]), c["prior"] * c["fid"],
                c["util"] * c["fid"], min(c["prior"], 0.85), c["prior"] ** 0.5,
                c["fid"] ** 2, c["lex"] / 100.0, min(c["ot_anc"], 5),
                float(c["ot_area"]), min(c["h2_ceil"], 0.1) * 10, float(c["gc_sig"]),
            ])
        targets.append((tid, oracle_idx, np.array(feats, dtype=np.float64), bids))
    return targets


FEAT_NAMES = [
    "prior", "utility", "cheap", "fidelity", "model_sup", "anti_dom", "ot_exc",
    "concordant", "same_endpoint", "gc_signal", "prior*fid", "util*fid",
    "capped_prior", "sqrt_prior", "fid^2", "lexical", "ot_ancestor",
    "ot_area", "h2_ceiling", "gc_sig_binary",
]


def eval_weights(targets, w):
    hits = 0
    for _, oidx, feats, _ in targets:
        if np.argmax(feats @ w) == oidx:
            hits += 1
    return hits


def eval_detail(targets, w):
    hit_tids, miss_tids = [], []
    for tid, oidx, feats, _ in targets:
        (hit_tids if np.argmax(feats @ w) == oidx else miss_tids).append(tid)
    return hit_tids, miss_tids


def main():
    t0 = time.time()
    targets = load_data()
    total = len(targets)
    nf = targets[0][2].shape[1]

    from experiments.contribution3.transfer.agent import UNIFIED_CONFIG as cfg
    w0 = np.array([
        cfg.w_transferability_prior, cfg.w_selection_utility,
        cfg.w_selection_cheap_rank, cfg.w_selection_fidelity,
        cfg.w_selection_model_support, cfg.w_selection_anti_dominance,
        cfg.w_ot_exceptional, cfg.w_selection_concordant,
        cfg.w_selection_same_endpoint, cfg.w_selection_gc_signal,
        cfg.w_selection_prior_x_fidelity, cfg.w_selection_util_x_fidelity,
        cfg.w_selection_capped_prior, cfg.w_selection_sqrt_prior,
        cfg.w_selection_fidelity_sq, cfg.w_selection_lexical,
        cfg.w_selection_ot_ancestor, cfg.w_selection_ot_area,
        cfg.w_selection_h2_ceiling, cfg.w_selection_gc_sig_binary,
    ])

    h0 = eval_weights(targets, w0)
    _, m0 = eval_detail(targets, w0)
    print(f"Baseline: {h0}/{total}")
    print(f"Missed: {sorted(m0)}\n")

    # === Phase 1: Single-weight perturbations ===
    print("=" * 70)
    print("PHASE 1: Single-weight perturbations")
    print("=" * 70)
    deltas = [-2.0, -1.0, -0.5, -0.2, -0.1, 0.1, 0.2, 0.5, 1.0, 2.0]
    improvements = []
    for i in range(nf):
        for d in deltas:
            w = w0.copy()
            w[i] += d
            h = eval_weights(targets, w)
            if h > h0:
                _, m = eval_detail(targets, w)
                recovered = set(m0) - set(m)
                lost = set(m) - set(m0)
                improvements.append((h, i, d, recovered, lost))

    if improvements:
        improvements.sort(reverse=True, key=lambda x: (x[0], -abs(x[2])))
        print(f"\n{len(improvements)} single-weight improvements found:")
        seen = set()
        for h, i, d, recovered, lost in improvements[:20]:
            key = (i, d)
            if key in seen:
                continue
            seen.add(key)
            print(f"  {FEAT_NAMES[i]:16s} {d:+.1f}: {h}/{total} "
                  f"recovered={sorted(recovered)} lost={sorted(lost)}")
    else:
        print("  No single-weight improvements found.")

    # === Phase 2: Fine-grained search on best single improvements ===
    print(f"\n{'=' * 70}")
    print("PHASE 2: Fine-grained single-weight search")
    print("=" * 70)
    for i in range(nf):
        best_h, best_d = h0, 0
        for d in np.arange(-3.0, 3.01, 0.05):
            w = w0.copy()
            w[i] += d
            h = eval_weights(targets, w)
            if h > best_h:
                best_h, best_d = h, d
        if best_h > h0:
            w = w0.copy()
            w[i] += best_d
            _, m = eval_detail(targets, w)
            recovered = set(m0) - set(m)
            lost = set(m) - set(m0)
            print(f"  {FEAT_NAMES[i]:16s} {best_d:+.2f}: {best_h}/{total} "
                  f"recovered={sorted(recovered)} lost={sorted(lost)}")

    # === Phase 3: Pairwise perturbations on promising features ===
    print(f"\n{'=' * 70}")
    print("PHASE 3: Pairwise perturbations")
    print("=" * 70)
    # Find features that appeared in single-weight improvements
    promising_features = set()
    for _, i, _, _, _ in improvements:
        promising_features.add(i)
    promising_features = sorted(promising_features)
    print(f"Testing pairs of {len(promising_features)} features: {[FEAT_NAMES[i] for i in promising_features]}")

    best_pair_h = h0
    best_pair_info = None
    fine_deltas = np.arange(-2.0, 2.01, 0.2)
    for i, j in combinations(promising_features, 2):
        for di in fine_deltas:
            for dj in fine_deltas:
                w = w0.copy()
                w[i] += di
                w[j] += dj
                h = eval_weights(targets, w)
                if h > best_pair_h:
                    best_pair_h = h
                    best_pair_info = (i, j, di, dj)

    if best_pair_info:
        i, j, di, dj = best_pair_info
        w = w0.copy()
        w[i] += di
        w[j] += dj
        _, m = eval_detail(targets, w)
        recovered = set(m0) - set(m)
        lost = set(m) - set(m0)
        print(f"  Best pair: {FEAT_NAMES[i]} {di:+.1f}, {FEAT_NAMES[j]} {dj:+.1f}: "
              f"{best_pair_h}/{total} recovered={sorted(recovered)} lost={sorted(lost)}")
    else:
        print("  No pairwise improvement found.")

    # === Phase 4: Greedy combination of improvements ===
    print(f"\n{'=' * 70}")
    print("PHASE 4: Greedy stacking of improvements")
    print("=" * 70)
    # Sort single improvements by gain
    unique_improv = {}
    for h, i, d, rec, lost in improvements:
        key = (i, d)
        if key not in unique_improv or h > unique_improv[key][0]:
            unique_improv[key] = (h, i, d, rec, lost)
    sorted_improv = sorted(unique_improv.values(), reverse=True, key=lambda x: x[0])

    w_best = w0.copy()
    h_best = h0
    applied = []
    for h, i, d, rec, lost in sorted_improv:
        w_try = w_best.copy()
        w_try[i] += d
        h_try = eval_weights(targets, w_try)
        if h_try > h_best:
            w_best = w_try
            h_best = h_try
            applied.append((FEAT_NAMES[i], d))
            _, m_new = eval_detail(targets, w_best)
            print(f"  +{FEAT_NAMES[i]:16s} {d:+.1f}: {h_best}/{total} missed={sorted(m_new)}")

    print(f"\n  Greedy best: {h_best}/{total}")
    if applied:
        print(f"  Applied: {applied}")

    # === Phase 5: Large-scale random perturbation (fast) ===
    print(f"\n{'=' * 70}")
    print("PHASE 5: Random perturbation (1M samples)")
    print("=" * 70)
    rng = np.random.default_rng(42)
    best_rand_h, best_rand_w = h0, w0.copy()
    for batch_i in range(100):
        perturbations = rng.normal(0, 0.3, size=(10000, nf))
        for p in perturbations:
            w = w0 + p
            h = eval_weights(targets, w)
            if h > best_rand_h:
                best_rand_h = h
                best_rand_w = w.copy()
    _, m_rand = eval_detail(targets, best_rand_w)
    print(f"  Best random: {best_rand_h}/{total}")
    if best_rand_h > h0:
        recovered = set(m0) - set(m_rand)
        lost = set(m_rand) - set(m0)
        print(f"  Recovered: {sorted(recovered)}")
        print(f"  Lost: {sorted(lost)}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
