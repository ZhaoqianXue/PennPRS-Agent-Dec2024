"""Rank-normalized features + DE optimization.

Instead of raw feature values, normalize each feature to percentile rank
within each target's candidate pool. This compresses generalist advantages
on model_support/prior and makes the competition fairer across targets.

Tests both raw and rank-normalized features with DE optimization.
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
from scipy.stats import rankdata

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RUN_DIR = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653"
)

FEAT_NAMES = [
    "prior", "utility", "cheap", "fidelity", "model_sup", "anti_dom", "ot_exc",
    "concordant", "same_endpoint", "gc_signal", "prior*fid", "util*fid",
    "capped_prior", "sqrt_prior", "fid^2", "lexical", "ot_ancestor",
    "ot_area", "h2_ceiling", "gc_sig_binary",
]


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
    return targets, unreachable


def rank_normalize(feats: np.ndarray) -> np.ndarray:
    """Normalize each feature column to percentile rank within the candidate pool."""
    n = feats.shape[0]
    if n <= 1:
        return np.zeros_like(feats)
    normed = np.zeros_like(feats)
    for col in range(feats.shape[1]):
        ranks = rankdata(feats[:, col], method='average')
        normed[:, col] = (ranks - 1) / (n - 1)  # [0, 1]
    return normed


def build_hybrid_features(feats: np.ndarray) -> np.ndarray:
    """Build hybrid feature matrix: raw features + rank-normalized features."""
    normed = rank_normalize(feats)
    return np.hstack([feats, normed])


def build_rank_only(feats: np.ndarray) -> np.ndarray:
    """Rank-normalized features only."""
    return rank_normalize(feats)


def build_raw_plus_interactions(feats: np.ndarray) -> np.ndarray:
    """Raw features + pairwise rank differences for key features."""
    normed = rank_normalize(feats)
    # Add rank-norm of key features: prior, utility, model_sup, fidelity, lexical
    key_cols = [0, 1, 3, 4, 15]  # prior, utility, fidelity, model_sup, lexical
    extra = normed[:, key_cols]
    return np.hstack([feats, extra])


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


def run_de(targets, nf, label, n_seeds=10, maxiter=3000, popsize=20):
    """Run DE optimization and return best weights + hits."""
    print(f"\n--- {label} ({nf} features, {n_seeds} seeds) ---")
    bounds = [(-3, 5)] * nf
    best_w, best_h = None, 0
    t0 = time.time()

    for seed in range(n_seeds):
        def objective(params):
            return -eval_weights(targets, np.array(params))

        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=maxiter, popsize=popsize, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed * 1000 + 42, workers=1, polish=True,
        )
        w = np.array(result.x)
        h = eval_weights(targets, w)
        _, m = eval_detail(targets, w)
        marker = " *** NEW BEST" if h > best_h else ""
        print(f"  seed {seed:2d}: {h}/{len(targets)} [{time.time()-t0:.0f}s]{marker}")
        if h > best_h:
            best_h, best_w = h, w.copy()

    _, best_m = eval_detail(targets, best_w)
    print(f"  BEST: {best_h}/{len(targets)}, missed: {best_m}")
    return best_w, best_h, best_m


def main():
    t0 = time.time()
    print("=" * 70)
    print("RANK-NORMALIZED FEATURE OPTIMIZATION")
    print("=" * 70)

    targets_raw, unreachable = load_data()
    total = len(targets_raw)
    nf = targets_raw[0][2].shape[1]
    print(f"Targets: {total} reachable, {len(unreachable)} unreachable")
    print(f"Raw features: {nf}")

    # === Approach 1: Rank-normalized features only ===
    targets_norm = [
        (tid, oidx, rank_normalize(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    w1, h1, m1 = run_de(targets_norm, nf, "Rank-normalized only", n_seeds=10, maxiter=2500)

    # === Approach 2: Hybrid (raw + rank-normalized) = 40 features ===
    targets_hybrid = [
        (tid, oidx, build_hybrid_features(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    nf_hybrid = targets_hybrid[0][2].shape[1]
    w2, h2, m2 = run_de(targets_hybrid, nf_hybrid, "Hybrid (raw + rank-norm)", n_seeds=10, maxiter=2500)

    # === Approach 3: Raw + key rank-norm features = 25 features ===
    targets_aug = [
        (tid, oidx, build_raw_plus_interactions(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    nf_aug = targets_aug[0][2].shape[1]
    w3, h3, m3 = run_de(targets_aug, nf_aug, "Raw + key rank-norms", n_seeds=10, maxiter=2500)

    # === Approach 4: Raw features (baseline for comparison) ===
    w4, h4, m4 = run_de(targets_raw, nf, "Raw features (baseline DE)", n_seeds=5, maxiter=2500)

    # === Summary ===
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Raw baseline (DE):      {h4}/{total}")
    print(f"  Rank-norm only:         {h1}/{total}")
    print(f"  Hybrid (raw+rank):      {h2}/{total}")
    print(f"  Raw + key rank-norms:   {h3}/{total}")

    # Compare missed sets
    print(f"\n  Raw baseline missed:    {sorted(m4)}")
    print(f"  Rank-norm missed:       {sorted(m1)}")
    print(f"  Hybrid missed:          {sorted(m2)}")
    print(f"  Raw+key missed:         {sorted(m3)}")

    # Uniquely recovered by each approach
    m4_set = set(m4)
    for label, m_list in [("Rank-norm", m1), ("Hybrid", m2), ("Raw+key", m3)]:
        m_set = set(m_list)
        recovered = m4_set - m_set
        lost = m_set - m4_set
        if recovered:
            print(f"\n  {label} recovered vs raw: {sorted(recovered)}")
        if lost:
            print(f"  {label} lost vs raw:      {sorted(lost)}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
