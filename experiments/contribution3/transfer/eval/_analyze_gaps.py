"""Analyze score gaps for missed targets and unreachable oracle features.

Two analyses:
1. For 42 reachable-but-missed targets: how close is oracle to top-ranked?
2. For 6 unreachable targets: what do oracle bundles look like in dossier?
"""
from __future__ import annotations
import csv, json, math, sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RUN_DIR = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653"
)

UNREACHABLE = {"D03", "E01", "G43", "I85", "M1A", "N61"}


def load_reachable_data():
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
        targets.append((tid, oracle_idx, np.array(feats, dtype=np.float64), bids, entry["cards"]))
    return targets, oracle_info


def main():
    from experiments.contribution3.transfer.agent import UNIFIED_CONFIG as cfg
    targets, oracle_info = load_reachable_data()

    # Build weight vector
    w = np.array([
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

    # --- Analysis 1: Score gaps for 42 missed targets ---
    print("=" * 70)
    print("ANALYSIS 1: Score gaps for reachable-but-missed targets")
    print("=" * 70)

    gaps = []
    for tid, oidx, feats, bids, cards in targets:
        scores = feats @ w
        sel_idx = np.argmax(scores)
        if sel_idx != oidx:
            gap = scores[sel_idx] - scores[oidx]
            oracle_rank = int(np.sum(scores > scores[oidx])) + 1
            n_cands = len(scores)
            gaps.append((tid, gap, oracle_rank, n_cands, bids[oidx], bids[sel_idx],
                         scores[oidx], scores[sel_idx]))

    gaps.sort(key=lambda x: x[1])  # sort by gap ascending (closest first)

    print(f"\n{len(gaps)} missed targets, sorted by score gap (smallest first):\n")
    print(f"{'Target':6s} {'Gap':>8s} {'OracleRank':>10s} {'Oracle':>24s} {'Selected':>24s} "
          f"{'OScore':>8s} {'SScore':>8s}")
    for tid, gap, orank, n, obid, sbid, oscore, sscore in gaps:
        print(f"{tid:6s} {gap:8.4f} {orank:4d}/{n:<4d}   {obid[:22]:22s}  {sbid[:22]:22s}  "
              f"{oscore:8.4f} {sscore:8.4f}")

    # Summary statistics
    gap_vals = [g[1] for g in gaps]
    ranks = [g[2] for g in gaps]
    print(f"\nGap statistics:")
    print(f"  min={min(gap_vals):.4f}  median={np.median(gap_vals):.4f}  "
          f"mean={np.mean(gap_vals):.4f}  max={max(gap_vals):.4f}")
    print(f"  Oracle rank: min={min(ranks)}  median={np.median(ranks):.0f}  "
          f"mean={np.mean(ranks):.1f}  max={max(ranks)}")
    close = sum(1 for g in gap_vals if g < 0.5)
    medium = sum(1 for g in gap_vals if 0.5 <= g < 2.0)
    far = sum(1 for g in gap_vals if g >= 2.0)
    print(f"  Close (<0.5): {close}  Medium (0.5-2.0): {medium}  Far (>2.0): {far}")

    # --- Analysis 2: Feature analysis for near-misses ---
    print("\n" + "=" * 70)
    print("ANALYSIS 2: Feature comparison for 10 closest misses")
    print("=" * 70)

    feat_names = [
        "prior", "utility", "cheap", "fidelity", "model_sup", "anti_dom", "ot_exc",
        "concordant", "same_endpoint", "gc_signal", "prior*fid", "util*fid",
        "capped_prior", "sqrt_prior", "fid^2", "lexical", "ot_ancestor",
        "ot_area", "h2_ceiling", "gc_sig_binary",
    ]
    for tid, gap, orank, n, obid, sbid, oscore, sscore in gaps[:10]:
        for _, oidx, feats, bids, cards in targets:
            if bids[0] == gaps[0][4] or True:  # find the target
                pass
        # Find target data
        for t_tid, t_oidx, t_feats, t_bids, t_cards in targets:
            if t_tid == tid:
                sel_idx = np.argmax(t_feats @ w)
                of = t_feats[t_oidx]
                sf = t_feats[sel_idx]
                print(f"\n  {tid}: gap={gap:.4f}, oracle_rank={orank}/{n}")
                print(f"    Oracle={obid[:30]}  Selected={sbid[:30]}")
                print(f"    {'Feature':16s} {'Oracle':>8s} {'Selected':>8s} {'Diff':>8s} {'Weight':>8s} {'Contribution':>12s}")
                for i, (fn, wv) in enumerate(zip(feat_names, w)):
                    diff = of[i] - sf[i]
                    contrib = diff * wv
                    if abs(contrib) > 0.01:
                        print(f"    {fn:16s} {of[i]:8.4f} {sf[i]:8.4f} {diff:+8.4f} {wv:8.4f} {contrib:+12.4f}")
                break

    # --- Analysis 3: Unreachable targets summary ---
    print("\n" + "=" * 70)
    print("ANALYSIS 3: Unreachable target oracle info from shortlist_recall.csv")
    print("=" * 70)
    with open(RUN_DIR / "shortlist_recall.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            tid = r["target_id"]
            if tid in UNREACHABLE:
                print(f"\n  {tid}:")
                for k, v in r.items():
                    print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
