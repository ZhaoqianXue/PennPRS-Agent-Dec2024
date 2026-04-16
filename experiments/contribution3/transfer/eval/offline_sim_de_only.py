"""Focused DE optimization for selection weights.

Uses 20 expanded features, runs 10 DE seeds with high iterations.
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
                float(c["conc"]),
                float(c["arch"] == "same-endpoint disease"),
                c["gc_rg"] * float(c["gc_sig"]),
                c["prior"] * c["fid"],
                c["util"] * c["fid"],
                min(c["prior"], 0.85),
                c["prior"] ** 0.5,
                c["fid"] ** 2,
                c["lex"] / 100.0,
                min(c["ot_anc"], 5),
                float(c["ot_area"]),
                min(c["h2_ceil"], 0.1) * 10,
                float(c["gc_sig"]),
            ])
        targets.append((tid, oracle_idx, np.array(feats, dtype=np.float64), bids))
    return targets, unreachable


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
    print("FOCUSED DE OPTIMIZATION — 20 features, multiple seeds")
    print("=" * 60)

    targets, unreachable = load_data()
    total = len(targets)
    nf = targets[0][2].shape[1]
    print(f"Targets: {total} reachable, {len(unreachable)} unreachable → {unreachable}")
    print(f"Features: {nf}, Ceiling: {total}/80\n")

    # Baseline
    from experiments.contribution3.transfer.agent import UNIFIED_CONFIG
    w0 = np.zeros(nf)
    w0[0] = UNIFIED_CONFIG.w_transferability_prior
    w0[1] = UNIFIED_CONFIG.w_selection_utility
    w0[2] = UNIFIED_CONFIG.w_selection_cheap_rank
    w0[3] = UNIFIED_CONFIG.w_selection_fidelity
    w0[4] = UNIFIED_CONFIG.w_selection_model_support
    w0[5] = UNIFIED_CONFIG.w_selection_anti_dominance
    w0[6] = UNIFIED_CONFIG.w_ot_exceptional
    h0 = eval_weights(targets, w0)
    _, m0 = eval_detail(targets, w0)
    print(f"Baseline: {h0}/{total} | missed: {m0}\n")

    bounds = [(0, 5)] * 4 + [(-1, 5)] * (nf - 4)
    best_w, best_h = w0.copy(), h0

    for seed in range(15):
        def objective(params):
            return -eval_weights(targets, np.array(params))

        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=3000, popsize=20, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed * 1000 + 42, workers=1, polish=True,
        )
        w = np.array(result.x)
        h = eval_weights(targets, w)
        _, m = eval_detail(targets, w)
        marker = " *** NEW BEST" if h > best_h else ""
        print(f"  seed {seed:2d}: {h}/{total} [{time.time()-t0:.0f}s] missed={m}{marker}")
        if h > best_h:
            best_h, best_w = h, w.copy()

    print(f"\n{'=' * 60}")
    print(f"BEST: {best_h}/{total} (baseline: {h0})")
    _, best_m = eval_detail(targets, best_w)
    print(f"Missed: {best_m}")

    print("\nWeights:")
    for name, val in zip(FEAT_NAMES, best_w):
        if abs(val) > 0.001:
            print(f"  {name:16s}: {val:+.6f}")

    # Diagnose missed
    print(f"\nDiagnostics ({len(best_m)} missed):")
    for tid, oidx, feats, bids in targets:
        if tid not in best_m:
            continue
        scores = feats @ best_w
        os = scores[oidx]
        bi = np.argmax(scores)
        bs = scores[bi]
        of = feats[oidx]
        bf = feats[bi]
        print(f"  {tid}: oracle={bids[oidx][:22]:22s}(P={of[0]:.3f} U={of[1]:.2f} C={of[2]:.2f} F={of[3]:.3f}) s={os:.4f}")
        print(f"        sel   ={bids[bi][:22]:22s}(P={bf[0]:.3f} U={bf[1]:.2f} C={bf[2]:.2f} F={bf[3]:.3f}) s={bs:.4f} Δ={bs-os:.4f}")

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
