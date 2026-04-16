"""Expanded features DE optimization.

Adds currently unused fields from cards_light.json that capture additional
target-bundle interaction signal:
- gc_rg_raw: absolute genetic correlation (not filtered by significance)
- gc_z: z-score of GC (continuous evidence strength)
- ot_ph: phenotype overlap from OpenTargets
- ot_gen: binary genetic support from OT
- ot_sc: shared drug target count from OT
- stok: shared token count (lexical)
- ot_sup: composite OT support flag

Also tests interaction features between evidence dimensions.
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


def load_data_base20():
    """Load data with original 20 features."""
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


def load_data_expanded():
    """Load data with expanded features (20 base + new features)."""
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
            gc_rg = c["gc_rg"]
            gc_z = c["gc_z"]
            gc_sig = float(c["gc_sig"])
            ot_ph = c["ot_ph"]
            ot_gen = float(c["ot_gen"])
            ot_sc = c["ot_sc"]
            ot_sup = float(c["ot_sup"])
            stok = c["stok"]
            fid = c["fid"]

            feats.append([
                # --- Base 20 features (indices 0-19) ---
                c["prior"], c["util"], c["cheap"], fid, ms, -anti, ot_exc,
                float(c["conc"]), float(c["arch"] == "same-endpoint disease"),
                gc_rg * gc_sig, c["prior"] * fid,
                c["util"] * fid, min(c["prior"], 0.85), c["prior"] ** 0.5,
                fid ** 2, c["lex"] / 100.0, min(c["ot_anc"], 5),
                float(c["ot_area"]), min(c["h2_ceil"], 0.1) * 10, gc_sig,
                # --- New raw features (indices 20-26) ---
                gc_rg,                          # 20: raw abs genetic correlation
                gc_z,                           # 21: GC z-score
                ot_ph,                          # 22: OT phenotype overlap
                ot_gen,                         # 23: OT genetic support (binary)
                min(ot_sc, 10),                 # 24: OT shared target count (capped)
                ot_sup,                         # 25: OT supported flag
                min(stok, 10) / 10.0,           # 26: shared tokens (normalized)
                # --- Cross-evidence interactions (indices 27-33) ---
                gc_rg * fid,                    # 27: GC*fidelity
                ot_ph * fid,                    # 28: OT_pheno*fidelity
                gc_rg * ot_ph,                  # 29: GC*OT_pheno
                float(stok > 0) * fid,          # 30: has_shared_tokens * fidelity
                gc_z * float(c["arch"] == "same-endpoint disease"),  # 31: gc_z*same_ep
                ot_ph * float(c["arch"] == "same-endpoint disease"),  # 32: ot_ph*same_ep
                # --- Piecewise features (indices 33-37) ---
                min(ms, 3.5),                   # 33: capped model_support
                max(ms - 3.5, 0),               # 34: excess model_support
                max(c["prior"] - 0.93, 0),      # 35: elite prior
                max(0.70 - c["prior"], 0),      # 36: low prior indicator
                max(fid - 0.8, 0),              # 37: high fidelity bonus
            ])
        targets.append((tid, oracle_idx, np.array(feats, dtype=np.float64), bids))
    return targets


FEAT_NAMES_EXPANDED = [
    # Base 20
    "prior", "utility", "cheap", "fidelity", "model_sup", "anti_dom", "ot_exc",
    "concordant", "same_endpoint", "gc_signal", "prior*fid", "util*fid",
    "capped_prior", "sqrt_prior", "fid^2", "lexical", "ot_ancestor",
    "ot_area", "h2_ceiling", "gc_sig_binary",
    # New raw 7
    "gc_rg_raw", "gc_z", "ot_pheno", "ot_genetic", "ot_shared_ct", "ot_supported", "shared_tok",
    # Cross-evidence interactions 6
    "gc_rg*fid", "ot_ph*fid", "gc_rg*ot_ph", "has_tok*fid", "gc_z*same_ep", "ot_ph*same_ep",
    # Piecewise 5
    "capped_ms", "excess_ms", "elite_prior", "low_prior", "high_fid",
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


def run_de(targets, nf, label, n_seeds=15, maxiter=3000, popsize=25):
    print(f"\n--- {label} ({nf} features, {n_seeds} seeds, iter={maxiter}, pop={popsize}) ---")
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
    print("EXPANDED FEATURES DE OPTIMIZATION")
    print("=" * 70)

    # === Load data ===
    targets_base = load_data_base20()
    targets_exp = load_data_expanded()
    total = len(targets_base)
    nf_base = targets_base[0][2].shape[1]
    nf_exp = targets_exp[0][2].shape[1]
    print(f"Targets: {total} reachable")
    print(f"Base features: {nf_base}, Expanded features: {nf_exp}")

    # === 1. Raw 20 baseline (verify) ===
    w0, h0, m0 = run_de(targets_base, nf_base, "Base 20 features", n_seeds=5, maxiter=2500, popsize=20)

    # === 2. Expanded 38 features ===
    w1, h1, m1 = run_de(targets_exp, nf_exp, "Expanded 38 features", n_seeds=15, maxiter=3000, popsize=25)

    # === 3. New features only (features 20-37) ===
    targets_new_only = [
        (tid, oidx, feats[:, 20:], bids)
        for tid, oidx, feats, bids in targets_exp
    ]
    nf_new = targets_new_only[0][2].shape[1]
    w2, h2, m2 = run_de(targets_new_only, nf_new, "New features only (18f)", n_seeds=10, maxiter=2500, popsize=20)

    # === Summary ===
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Base 20:         {h0}/{total}")
    print(f"  Expanded 38:     {h1}/{total}")
    print(f"  New only (18):   {h2}/{total}")

    raw_missed = set(m0)
    for label, h, m in [("Expanded", h1, m1), ("New only", h2, m2)]:
        m_set = set(m)
        recovered = raw_missed - m_set
        lost = m_set - raw_missed
        print(f"\n  {label}:")
        if recovered:
            print(f"    Recovered: {sorted(recovered)}")
        if lost:
            print(f"    Lost:      {sorted(lost)}")

    # Print expanded weights if they improved
    if h1 > h0:
        print(f"\n  Expanded feature weights (improvements):")
        for name, val in zip(FEAT_NAMES_EXPANDED, w1):
            if abs(val) > 0.001:
                print(f"    {name:16s}: {val:+.6f}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
