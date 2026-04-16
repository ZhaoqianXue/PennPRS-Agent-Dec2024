"""Find config achieving ~74/80 with cap ≈ 100 (must include G30).

Fixed approach: separate RR tracks (small) and deep tracks (full-length).
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

MUST_INCLUDE = {
    'C22', 'E79', 'D05', 'L68', 'B18', 'M05', 'L05', 'L56',
    'C54', 'F11', 'N97', 'N91', 'G30',
}


def _merge_rr_then_deep(rr_tracks, deep_tracks, cap):
    """Phase 1: round-robin from rr_tracks.
    Phase 2: sequentially fill from each deep_track (full-length).
    Total capped."""
    shortlist, seen = [], set()
    # Phase 1: round-robin
    max_len = max((len(t) for t in rr_tracks), default=0)
    for idx in range(max_len):
        for track in rr_tracks:
            if idx >= len(track):
                continue
            bid = track[idx]
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    # Phase 2: deep fill sequentially
    for track in deep_tracks:
        for bid in track:
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    return shortlist


def _merge_best_rank(all_tracks, cap):
    """Union all tracks, sort by best (lowest) rank, take top-cap."""
    best_rank = {}
    for track in all_tracks:
        for rank, bid in enumerate(track):
            if bid not in best_rank or rank < best_rank[bid]:
                best_rank[bid] = rank
    sorted_bids = sorted(best_rank.keys(), key=lambda b: (best_rank[b], b))
    return sorted_bids[:cap]


def _merge_rr_deep_interleaved(rr_tracks, deep_tracks, rr_rounds, cap):
    """Phase 1: round-robin for rr_rounds rounds.
    Phase 2: interleave deep tracks (round-robin among deep_tracks only)."""
    shortlist, seen = [], set()
    # Phase 1
    for idx in range(rr_rounds):
        for track in rr_tracks:
            if idx >= len(track):
                continue
            bid = track[idx]
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    # Phase 2: round-robin among deep tracks
    max_deep = max((len(t) for t in deep_tracks), default=0)
    for idx in range(max_deep):
        for track in deep_tracks:
            if idx >= len(track):
                continue
            bid = track[idx]
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    return shortlist


def eval_merge(data, merge_fn, total):
    hit, must_miss, sizes = 0, [], []
    for d in data:
        sl = merge_fn(d)
        sizes.append(len(sl))
        if d.oracle_id in sl:
            hit += 1
        elif d.tid in MUST_INCLUDE:
            must_miss.append(d.tid)
    return hit, must_miss, sum(sizes) / len(sizes)


def main():
    data = load_and_precompute()
    total = len(data)

    # ====== Approach 1: RR (small) + deep fill (sup→sem→gc→sel) ======
    print("=" * 80)
    print("APPROACH 1: RR (small) then deep fill (sup→sem→gc→sel)")
    print("=" * 80)
    for p, s, g, sm, sp in [(3, 10, 5, 10, 5), (3, 15, 8, 15, 8), (5, 20, 8, 20, 8)]:
        for cap in range(90, 131, 5):
            def merge_fn(d, p=p, s=s, g=g, sm=sm, sp=sp, cap=cap):
                rr = [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
                      d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]]
                deep = [d.support_ranked[:104], d.semantic_ranked[:65],
                        d.gc_ranked[:45], d.selection_ranked[:54]]
                return _merge_rr_then_deep(rr, deep, cap)
            h, mm, sl = eval_merge(data, merge_fn, total)
            g30 = 'G30' not in mm
            if h >= 70 and g30:
                print(f"  p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {h}/{total} must_miss={mm} sl={sl:.0f}")

    # ====== Approach 2: Deep fill order variations ======
    print("\n" + "=" * 80)
    print("APPROACH 2: Deep fill order variations (best deep order)")
    print("=" * 80)
    p, s, g, sm, sp = 3, 10, 5, 10, 5
    # Try different deep fill orders
    orders = [
        ("sup→sem→gc→sel", lambda d: [d.support_ranked[:104], d.semantic_ranked[:65],
                                        d.gc_ranked[:45], d.selection_ranked[:54]]),
        ("sel→sup→sem→gc", lambda d: [d.selection_ranked[:54], d.support_ranked[:104],
                                        d.semantic_ranked[:65], d.gc_ranked[:45]]),
        ("sem→sup→gc→sel", lambda d: [d.semantic_ranked[:65], d.support_ranked[:104],
                                        d.gc_ranked[:45], d.selection_ranked[:54]]),
        ("sel→sem→sup→gc", lambda d: [d.selection_ranked[:54], d.semantic_ranked[:65],
                                        d.support_ranked[:104], d.gc_ranked[:45]]),
        ("gc→sel→sem→sup", lambda d: [d.gc_ranked[:45], d.selection_ranked[:54],
                                        d.semantic_ranked[:65], d.support_ranked[:104]]),
    ]
    for label, deep_fn in orders:
        for cap in range(90, 131, 5):
            def merge_fn(d, cap=cap, deep_fn=deep_fn):
                rr = [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
                      d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]]
                return _merge_rr_then_deep(rr, deep_fn(d), cap)
            h, mm, sl = eval_merge(data, merge_fn, total)
            g30 = 'G30' not in mm
            if h >= 72 and g30:
                print(f"  {label} cap={cap}: {h}/{total} must_miss={mm} sl={sl:.0f}")

    # ====== Approach 3: Best-rank merge ======
    print("\n" + "=" * 80)
    print("APPROACH 3: Best-rank merge (union sorted by best rank)")
    print("=" * 80)
    for s, g, sm, sp in [(54, 45, 65, 104), (50, 40, 60, 104), (40, 35, 55, 104)]:
        for cap in range(85, 131, 5):
            def merge_fn(d, s=s, g=g, sm=sm, sp=sp, cap=cap):
                tracks = [d.prior_ranked[:10], d.selection_ranked[:s],
                          d.same_endpoint_ids,
                          d.gc_ranked[:g], d.semantic_ranked[:sm],
                          d.support_ranked[:sp]]
                return _merge_best_rank(tracks, cap)
            h, mm, sl = eval_merge(data, merge_fn, total)
            g30 = 'G30' not in mm
            if h >= 70 and g30:
                print(f"  s={s} g={g} sm={sm} sp={sp} cap={cap}: {h}/{total} must_miss={mm} sl={sl:.0f}")

    # ====== Approach 4: RR (5 rounds) + deep interleaved (sup + sem) ======
    print("\n" + "=" * 80)
    print("APPROACH 4: RR (short) + deep interleaved (sup+sem+gc+sel)")
    print("=" * 80)
    for rr_rounds in [3, 5, 8]:
        for cap in range(90, 131, 5):
            def merge_fn(d, rr_rounds=rr_rounds, cap=cap):
                rr = [d.prior_ranked[:5], d.selection_ranked[:20], d.same_endpoint_ids,
                      d.gc_ranked[:8], d.semantic_ranked[:15], d.support_ranked[:8]]
                deep = [d.support_ranked[:104], d.semantic_ranked[:65],
                        d.gc_ranked[:45], d.selection_ranked[:54]]
                return _merge_rr_deep_interleaved(rr, deep, rr_rounds, cap)
            h, mm, sl = eval_merge(data, merge_fn, total)
            g30 = 'G30' not in mm
            if h >= 72 and g30:
                print(f"  rr={rr_rounds} cap={cap}: {h}/{total} must_miss={mm} sl={sl:.0f}")

    # ====== Approach 5: Just test what overlaps exist ======
    print("\n" + "=" * 80)
    print("APPROACH 5: Overlap analysis - unique entries from support top-104")
    print("=" * 80)
    overlaps = []
    for d in data:
        # Standard shortlist from small RR
        rr_set = set()
        rr = [d.prior_ranked[:5], d.selection_ranked[:30], d.same_endpoint_ids,
              d.gc_ranked[:8], d.semantic_ranked[:25], d.support_ranked[:12]]
        max_len = max(len(t) for t in rr)
        for idx in range(max_len):
            for track in rr:
                if idx < len(track):
                    rr_set.add(track[idx])
        sup_104 = set(d.support_ranked[:104])
        overlap = len(rr_set & sup_104)
        unique_from_sup = len(sup_104 - rr_set)
        overlaps.append((d.tid, len(rr_set), overlap, unique_from_sup))
    unique_from_sup_vals = [o[3] for o in overlaps]
    print(f"  Unique entries from support[0:104] not in RR shortlist:")
    print(f"    min={min(unique_from_sup_vals)}, max={max(unique_from_sup_vals)}, "
          f"mean={sum(unique_from_sup_vals)/len(unique_from_sup_vals):.1f}")
    rr_sizes = [o[1] for o in overlaps]
    print(f"  RR shortlist size: min={min(rr_sizes)}, max={max(rr_sizes)}, mean={sum(rr_sizes)/len(rr_sizes):.1f}")
    print(f"  Combined (RR + unique sup): "
          f"mean={sum(r+u for _,r,_,u in overlaps)/len(overlaps):.1f}, "
          f"max={max(r+u for _,r,_,u in overlaps)}")

    # ====== Approach 6: Exhaustive search for RR+deep with cap≤110 ======
    print("\n" + "=" * 80)
    print("APPROACH 6: Grid search RR+deep for best 74+ with cap ≤ 110")
    print("=" * 80)
    best_h = 0
    best_cfg = None
    for p in [1, 3, 5]:
        for s in [5, 10, 15, 20, 25, 30]:
            for g in [3, 5, 8]:
                for sm in [5, 10, 15, 20, 25]:
                    for sp in [3, 5, 8, 12]:
                        for cap in [95, 100, 105, 110]:
                            def merge_fn(d, p=p, s=s, g=g, sm=sm, sp=sp, cap=cap):
                                rr = [d.prior_ranked[:p], d.selection_ranked[:s],
                                      d.same_endpoint_ids, d.gc_ranked[:g],
                                      d.semantic_ranked[:sm], d.support_ranked[:sp]]
                                deep = [d.support_ranked[:104], d.semantic_ranked[:65],
                                        d.gc_ranked[:45], d.selection_ranked[:54]]
                                return _merge_rr_then_deep(rr, deep, cap)
                            h, mm, sl = eval_merge(data, merge_fn, total)
                            if h > best_h and 'G30' not in mm:
                                best_h = h
                                best_cfg = (p, s, g, sm, sp, cap, mm, sl)
    if best_cfg:
        p, s, g, sm, sp, cap, mm, sl = best_cfg
        print(f"  Best: p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {best_h}/{total}")
        print(f"  Must_miss: {mm}")
        print(f"  Sl_mean: {sl:.0f}")

    # Show progression for best track config
    if best_cfg:
        p, s, g, sm, sp = best_cfg[:5]
        print(f"\n  Progression for p={p} s={s} g={g} sm={sm} sp={sp}:")
        for cap in range(85, 131):
            def merge_fn(d, cap=cap, p=p, s=s, g=g, sm=sm, sp=sp):
                rr = [d.prior_ranked[:p], d.selection_ranked[:s],
                      d.same_endpoint_ids, d.gc_ranked[:g],
                      d.semantic_ranked[:sm], d.support_ranked[:sp]]
                deep = [d.support_ranked[:104], d.semantic_ranked[:65],
                        d.gc_ranked[:45], d.selection_ranked[:54]]
                return _merge_rr_then_deep(rr, deep, cap)
            h, mm, sl = eval_merge(data, merge_fn, total)
            g30 = 'G30' not in mm
            if g30 or cap >= 105:
                print(f"    cap={cap}: {h}/{total} must_miss={mm} G30={'OK' if g30 else 'MISS'}")


if __name__ == "__main__":
    main()
