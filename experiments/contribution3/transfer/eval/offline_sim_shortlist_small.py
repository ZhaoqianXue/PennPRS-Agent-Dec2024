"""Find max oracle recall with parameters ≤ old values and cap ≤ 50.

Old values: prior=10, sel=50, gc=8, sem=25, sup=12, cap=75.
User wants: all params ≤ old values, cap ≤ 50.
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.offline_sim_shortlist_80 import (
    load_and_precompute, TargetTrackData,
)
from experiments.contribution3.transfer.agent import _merge_shortlist_tracks


def hits(data, p, s, g, sm, sp, cap):
    return sum(1 for d in data if d.oracle_in_shortlist(p, s, g, sm, sp, cap))


def miss_list(data, p, s, g, sm, sp, cap):
    return [d.tid for d in data if not d.oracle_in_shortlist(p, s, g, sm, sp, cap)]


def shortlist_sizes(data, p, s, g, sm, sp, cap):
    sizes = []
    for d in data:
        sl = _merge_shortlist_tracks(
            [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
             d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]],
            cap,
        )
        sizes.append(len(sl))
    return sizes


def main():
    data = load_and_precompute()
    total = len(data)

    # --- Step 0: Per-target oracle rank in each track ---
    print(f"\n{'TID':6s} {'Oracle':35s} {'Prior':>6s} {'Sel':>6s} {'GC':>6s} {'Sem':>6s} {'Sup':>6s} {'Same':>5s} {'Best':>5s}")
    rank_info = []
    for d in data:
        pr = d.oracle_rank_in(d.prior_ranked)
        sr = d.oracle_rank_in(d.selection_ranked)
        gr = d.oracle_rank_in(d.gc_ranked)
        smr = d.oracle_rank_in(d.semantic_ranked)
        spr = d.oracle_rank_in(d.support_ranked)
        in_same = "Y" if d.oracle_id in d.same_endpoint_ids else "N"
        best = min(pr, sr, gr, smr, spr)
        rank_info.append((d.tid, d.oracle_id, pr, sr, gr, smr, spr, in_same, best))
        print(f"{d.tid:6s} {d.oracle_id:35s} {pr:6d} {sr:6d} {gr:6d} {smr:6d} {spr:6d} {in_same:>5s} {best:5d}")

    # Distribution of best-track rank
    best_ranks = sorted([r[8] for r in rank_info])
    print(f"\nBest-track rank distribution:")
    for threshold in [5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250]:
        count = sum(1 for r in best_ranks if r <= threshold)
        print(f"  Best rank ≤ {threshold:3d}: {count}/{total}")

    # --- Step 1: Theoretical ceiling per cap (with unlimited track sizes) ---
    print("\n=== Theoretical ceiling per cap (tracks=500) ===")
    for cap in [30, 40, 50, 60, 75, 100, 150, 200]:
        h = hits(data, 500, 500, 500, 500, 500, cap)
        ms = miss_list(data, 500, 500, 500, 500, 500, cap) if h < total else []
        print(f"  cap={cap:3d}: {h}/{total}  miss={ms}")

    # --- Step 2: Old config baseline ---
    print("\n=== Old config baseline ===")
    old_p, old_s, old_g, old_sm, old_sp = 10, 50, 8, 25, 12
    for cap in [50, 60, 75]:
        h = hits(data, old_p, old_s, old_g, old_sm, old_sp, cap)
        ms = miss_list(data, old_p, old_s, old_g, old_sm, old_sp, cap)
        print(f"  p={old_p} s={old_s} g={old_g} sm={old_sm} sp={old_sp} cap={cap}: {h}/{total}")
        print(f"    miss={ms}")

    # --- Step 3: Max out each track to old limits, try all combos ---
    print("\n=== Best within old limits (p≤10, s≤50, g≤8, sm≤25, sp≤12) ===")
    # Use max of old values
    for cap in [40, 45, 50, 55, 60, 75]:
        h = hits(data, 10, 50, 8, 25, 12, cap)
        print(f"  Old max, cap={cap}: {h}/{total}")

    # --- Step 4: What if we redistribute track budget differently? ---
    # The idea: some tracks might be wasted if they're highly correlated
    # Try: increase productive tracks, decrease less useful ones
    print("\n=== Track budget redistribution (total track slots ≤ 105, cap ≤ 50) ===")
    # Old total track slots: 10+50+8+25+12 = 105
    best_h = 0
    best_cfg = None
    for p in [5, 8, 10, 12, 15, 20, 25, 30]:
        for s in [10, 20, 30, 40, 50]:
            for g in [3, 5, 8, 10, 15]:
                for sm in [10, 15, 20, 25, 30, 40, 50]:
                    for sp in [5, 8, 10, 12, 15, 20]:
                        if p + s + g + sm + sp > 105:
                            continue
                        for cap in [40, 45, 50]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_h or (h == best_h and cap < best_cfg[5]):
                                best_h = h
                                best_cfg = (p, s, g, sm, sp, cap)
    p, s, g, sm, sp, cap = best_cfg
    ms = miss_list(data, p, s, g, sm, sp, cap)
    print(f"  Best: p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {best_h}/{total}")
    print(f"  Miss: {ms}")

    # Show shortlist size stats
    sizes = shortlist_sizes(data, p, s, g, sm, sp, cap)
    print(f"  Shortlist sizes: min={min(sizes)}, max={max(sizes)}, mean={sum(sizes)/len(sizes):.1f}")

    # --- Step 5: What if we allow slightly larger total budget? ---
    print("\n=== Slightly larger budget (total ≤ 150, cap ≤ 50) ===")
    best_h2 = 0
    best_cfg2 = None
    for p in [5, 10, 15, 20, 25, 30, 40, 50]:
        for s in [10, 20, 30, 40, 50]:
            for g in [3, 5, 8, 10, 15, 20]:
                for sm in [10, 20, 25, 30, 40, 50]:
                    for sp in [5, 10, 12, 15, 20, 25, 30]:
                        if p + s + g + sm + sp > 150:
                            continue
                        for cap in [45, 50]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_h2 or (h == best_h2 and (p + s + g + sm + sp) < sum(best_cfg2[:5])):
                                best_h2 = h
                                best_cfg2 = (p, s, g, sm, sp, cap)
    p, s, g, sm, sp, cap = best_cfg2
    ms = miss_list(data, p, s, g, sm, sp, cap)
    print(f"  Best: p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {best_h2}/{total}")
    print(f"  Miss: {ms}")
    sizes = shortlist_sizes(data, p, s, g, sm, sp, cap)
    print(f"  Shortlist sizes: min={min(sizes)}, max={max(sizes)}, mean={sum(sizes)/len(sizes):.1f}")

    # --- Step 6: For each target that's hard, which track can capture it? ---
    print("\n=== Hard targets: need best_rank > 12 ===")
    hard = [(d.tid, d.oracle_id, min(d.oracle_rank_in(d.prior_ranked), d.oracle_rank_in(d.selection_ranked),
                                      d.oracle_rank_in(d.gc_ranked), d.oracle_rank_in(d.semantic_ranked),
                                      d.oracle_rank_in(d.support_ranked)))
            for d in data
            if min(d.oracle_rank_in(d.prior_ranked), d.oracle_rank_in(d.selection_ranked),
                   d.oracle_rank_in(d.gc_ranked), d.oracle_rank_in(d.semantic_ranked),
                   d.oracle_rank_in(d.support_ranked)) > 12]
    hard.sort(key=lambda x: x[2])
    for tid, oid, best in hard:
        d = next(dd for dd in data if dd.tid == tid)
        pr = d.oracle_rank_in(d.prior_ranked)
        sr = d.oracle_rank_in(d.selection_ranked)
        gr = d.oracle_rank_in(d.gc_ranked)
        smr = d.oracle_rank_in(d.semantic_ranked)
        spr = d.oracle_rank_in(d.support_ranked)
        best_track = min([("prior", pr), ("sel", sr), ("gc", gr), ("sem", smr), ("sup", spr)], key=lambda x: x[1])
        print(f"  {tid:6s} best_rank={best:3d} on {best_track[0]:5s}  (p={pr} s={sr} g={gr} sm={smr} sp={spr})")

    # --- Step 7: Absolute ceiling with cap=50 ---
    # If we allow ANY track sizes (no limit), what's the max with cap=50?
    print("\n=== Absolute ceiling: cap=50, no track size limit ===")
    h = hits(data, 500, 500, 500, 500, 500, 50)
    ms = miss_list(data, 500, 500, 500, 500, 500, 50)
    print(f"  {h}/{total}  miss={ms}")

    # With cap=50 and unlimited tracks, what's the actual shortlist doing?
    # For misses: check what rank the oracle is in the merged shortlist
    for tid in ms:
        d = next(dd for dd in data if dd.tid == tid)
        sl = _merge_shortlist_tracks(
            [d.prior_ranked[:500], d.selection_ranked[:500], d.same_endpoint_ids,
             d.gc_ranked[:500], d.semantic_ranked[:500], d.support_ranked[:500]], 50)
        pr = d.oracle_rank_in(d.prior_ranked)
        sr = d.oracle_rank_in(d.selection_ranked)
        # Where is oracle in the all-track merge with no cap?
        sl_uncapped = _merge_shortlist_tracks(
            [d.prior_ranked[:500], d.selection_ranked[:500], d.same_endpoint_ids,
             d.gc_ranked[:500], d.semantic_ranked[:500], d.support_ranked[:500]], 9999)
        oracle_pos = sl_uncapped.index(d.oracle_id) + 1 if d.oracle_id in sl_uncapped else 9999
        print(f"    {tid}: oracle merge-pos={oracle_pos}, shortlist_size={len(sl)}, best_track_ranks: p={pr} s={sr}")


if __name__ == "__main__":
    main()
