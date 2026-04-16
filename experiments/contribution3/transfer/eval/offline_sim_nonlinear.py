"""Non-linear feature engineering + DE optimization.

Tests several feature engineering approaches that add non-linearity
without requiring a fundamentally different model:
1. Piecewise linear features (breakpoints at key thresholds)
2. Relative features (ratio to pool max/mean)
3. Dominance features (count of features in top-K)
4. Combined: raw + piecewise + relative + dominance
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution

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


# --- Feature builders ---

def build_piecewise(feats: np.ndarray) -> np.ndarray:
    """Add piecewise linear features with breakpoints."""
    n = feats.shape[0]
    extras = []
    # Prior breakpoints: elite (>0.93), good (>0.85), low (<0.7)
    extras.append(np.maximum(feats[:, 0] - 0.93, 0))  # elite prior
    extras.append(np.maximum(0.70 - feats[:, 0], 0))   # low prior penalty
    # Model support: cap at 3.5 (anti-generalist) and excess
    extras.append(np.minimum(feats[:, 4], 3.5))         # capped model_sup
    extras.append(np.maximum(feats[:, 4] - 3.5, 0))     # excess model_sup
    # Utility breakpoints
    extras.append(np.maximum(feats[:, 1] - 5.0, 0))     # high utility
    extras.append(np.minimum(feats[:, 1], 3.0))          # capped utility
    # Fidelity breakpoint
    extras.append(np.maximum(feats[:, 3] - 0.8, 0))     # high fidelity bonus
    # Anti-dominance: heavy penalty for very high n_models
    extras.append(np.maximum(feats[:, 5] + 0.5, 0))     # strong anti-dom (feats[5] = -anti)
    return np.hstack([feats, np.column_stack(extras)])


def build_relative(feats: np.ndarray) -> np.ndarray:
    """Add features relative to pool statistics."""
    n = feats.shape[0]
    extras = []
    key_cols = [0, 1, 2, 3, 4, 15]  # prior, utility, cheap, fidelity, model_sup, lexical
    for col in key_cols:
        col_max = feats[:, col].max()
        col_mean = feats[:, col].mean()
        if col_max > 0:
            extras.append(feats[:, col] / col_max)       # ratio to max
        else:
            extras.append(np.zeros(n))
        extras.append(feats[:, col] - col_mean)          # deviation from mean
    return np.hstack([feats, np.column_stack(extras)])


def build_dominance(feats: np.ndarray) -> np.ndarray:
    """Add count-based dominance features."""
    n = feats.shape[0]
    from scipy.stats import rankdata
    extras = []
    # For key features, compute "is in top K" indicators
    key_cols = [0, 1, 3, 4, 7, 8, 9, 15]  # prior, util, fid, model_sup, conc, same_ep, gc_sig, lex
    for k in [3, 5, 10]:
        in_top_k = np.zeros(n)
        for col in key_cols:
            ranks = rankdata(-feats[:, col], method='min')  # 1 = best
            in_top_k += (ranks <= k).astype(float)
        extras.append(in_top_k)
    # Total "rank score": sum of percentile ranks across key features
    rank_sum = np.zeros(n)
    for col in key_cols:
        ranks = rankdata(feats[:, col], method='average')
        rank_sum += ranks / n
    extras.append(rank_sum)
    return np.hstack([feats, np.column_stack(extras)])


def build_full(feats: np.ndarray) -> np.ndarray:
    """Combine raw + piecewise + relative + dominance."""
    f1 = build_piecewise(feats)
    n_pw = f1.shape[1] - feats.shape[1]

    rel_extras = build_relative(feats)[:, feats.shape[1]:]
    dom_extras = build_dominance(feats)[:, feats.shape[1]:]

    return np.hstack([f1, rel_extras, dom_extras])


# --- Evaluation ---

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


def run_de(targets, nf, label, n_seeds=10, maxiter=2500, popsize=20):
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
        marker = " *** NEW BEST" if h > best_h else ""
        print(f"  seed {seed:2d}: {h}/{len(targets)} [{time.time()-t0:.0f}s]{marker}")
        if h > best_h:
            best_h, best_w = h, w.copy()

    _, best_m = eval_detail(targets, best_w)
    print(f"  BEST: {best_h}/{len(targets)}, missed: {sorted(best_m)}")
    return best_w, best_h, best_m


def main():
    t0 = time.time()
    print("=" * 70)
    print("NON-LINEAR FEATURE ENGINEERING OPTIMIZATION")
    print("=" * 70)

    targets_raw = load_data()
    total = len(targets_raw)
    nf = targets_raw[0][2].shape[1]
    print(f"Targets: {total} reachable, raw features: {nf}")

    # === 1. Piecewise linear features ===
    targets_pw = [
        (tid, oidx, build_piecewise(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    nf_pw = targets_pw[0][2].shape[1]
    w1, h1, m1 = run_de(targets_pw, nf_pw, "Piecewise linear", n_seeds=10)

    # === 2. Relative features ===
    targets_rel = [
        (tid, oidx, build_relative(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    nf_rel = targets_rel[0][2].shape[1]
    w2, h2, m2 = run_de(targets_rel, nf_rel, "Relative features", n_seeds=10)

    # === 3. Dominance features ===
    targets_dom = [
        (tid, oidx, build_dominance(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    nf_dom = targets_dom[0][2].shape[1]
    w3, h3, m3 = run_de(targets_dom, nf_dom, "Dominance features", n_seeds=10)

    # === 4. Full combined ===
    targets_full = [
        (tid, oidx, build_full(feats), bids)
        for tid, oidx, feats, bids in targets_raw
    ]
    nf_full = targets_full[0][2].shape[1]
    w4, h4, m4 = run_de(targets_full, nf_full, "Full combined", n_seeds=12, maxiter=3000)

    # === Summary ===
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Raw baseline (prev):    32/{total}")
    print(f"  Piecewise ({nf_pw}f):      {h1}/{total}")
    print(f"  Relative ({nf_rel}f):       {h2}/{total}")
    print(f"  Dominance ({nf_dom}f):      {h3}/{total}")
    print(f"  Full combined ({nf_full}f): {h4}/{total}")

    # Best overall
    results = [("Piecewise", h1, m1), ("Relative", h2, m2),
               ("Dominance", h3, m3), ("Full", h4, m4)]
    best = max(results, key=lambda x: x[1])
    print(f"\n  BEST: {best[0]} → {best[1]}/{total}")
    print(f"  Missed: {sorted(best[2])}")

    # Compare to raw baseline
    raw_missed = {'B18', 'B20', 'C22', 'C54', 'C56', 'D04', 'D05', 'D50', 'E79', 'F05',
                  'F11', 'F14', 'F22', 'F34', 'F44', 'F60', 'G30', 'I11', 'I15', 'I44',
                  'J96', 'K02', 'K04', 'K21', 'K25', 'K65', 'L02', 'L05', 'L56', 'L57',
                  'L68', 'M05', 'M34', 'N10', 'N21', 'N52', 'N60', 'N84', 'N91', 'N97',
                  'Q23', 'S52'}
    for label, h, m in results:
        m_set = set(m)
        recovered = raw_missed - m_set
        lost = m_set - raw_missed
        if recovered:
            print(f"\n  {label} recovered: {sorted(recovered)}")
        if lost:
            print(f"  {label} lost:      {sorted(lost)}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
