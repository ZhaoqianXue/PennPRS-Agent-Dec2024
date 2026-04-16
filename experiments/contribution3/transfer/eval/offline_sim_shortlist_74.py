"""Find minimal config achieving 74/80 oracle recall.

Must-include 13 targets and their best track + rank:
  semantic: C22(20), D05(24), L68(34), B18(40), M05(40), N97(65)
  support:  E79(23), L05(44), C54(46), N91(91), G30(104)
  gc:       L56(45)
  selection: F11(54)

Strategy:
1. Current round-robin with targeted track sizes + larger cap
2. Modified merge: weighted round-robin or priority-based
3. Hybrid: score-based pre-fill + round-robin top-up
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


MUST_INCLUDE = {
    'C22', 'E79', 'D05', 'L68', 'B18', 'M05', 'L05', 'L56',
    'C54', 'F11', 'N97', 'N91', 'G30',
}


def hits(data, p, s, g, sm, sp, cap):
    return sum(1 for d in data if d.oracle_in_shortlist(p, s, g, sm, sp, cap))


def miss_list(data, p, s, g, sm, sp, cap):
    return [d.tid for d in data if not d.oracle_in_shortlist(p, s, g, sm, sp, cap)]


def must_miss(data, p, s, g, sm, sp, cap):
    return [d.tid for d in data
            if d.tid in MUST_INCLUDE and not d.oracle_in_shortlist(p, s, g, sm, sp, cap)]


def shortlist_stats(data, p, s, g, sm, sp, cap):
    sizes = []
    for d in data:
        sl = _merge_shortlist_tracks(
            [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
             d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]], cap)
        sizes.append(len(sl))
    return min(sizes), max(sizes), sum(sizes) / len(sizes)


# ---------- Modified merge algorithms ----------

def _merge_weighted_round_robin(track_ids: list[list[str]],
                                 weights: list[int],
                                 cap: int) -> list[str]:
    """Weighted round-robin: track i contributes weights[i] entries per round."""
    shortlist: list[str] = []
    seen: set[str] = set()
    max_len = max((len(t) for t in track_ids), default=0)
    ptrs = [0] * len(track_ids)

    while len(shortlist) < cap:
        added_any = False
        for i, track in enumerate(track_ids):
            for _ in range(weights[i]):
                while ptrs[i] < len(track):
                    bid = track[ptrs[i]]
                    ptrs[i] += 1
                    if bid not in seen:
                        seen.add(bid)
                        shortlist.append(bid)
                        added_any = True
                        break
                if len(shortlist) >= cap:
                    return shortlist
        if not added_any:
            break
    return shortlist


def _merge_priority_fill(track_ids: list[list[str]],
                          priority_order: list[int],
                          round_robin_rounds: int,
                          cap: int) -> list[str]:
    """Hybrid: round-robin for first N rounds, then sequential fill by priority."""
    shortlist: list[str] = []
    seen: set[str] = set()

    # Phase 1: round-robin for diversity
    for idx in range(round_robin_rounds):
        for track in track_ids:
            if idx >= len(track):
                continue
            bid = track[idx]
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist

    # Phase 2: sequential fill by priority order
    for ti in priority_order:
        track = track_ids[ti]
        for bid in track:
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist

    return shortlist


def oracle_in_custom(d: TargetTrackData, merge_fn, p, s, g, sm, sp, cap, **kwargs):
    tracks = [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
              d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]]
    sl = merge_fn(tracks, cap=cap, **kwargs)
    return d.oracle_id in sl


def hits_custom(data, merge_fn, p, s, g, sm, sp, cap, **kwargs):
    return sum(1 for d in data if oracle_in_custom(d, merge_fn, p, s, g, sm, sp, cap, **kwargs))


def miss_custom(data, merge_fn, p, s, g, sm, sp, cap, **kwargs):
    return [d.tid for d in data if not oracle_in_custom(d, merge_fn, p, s, g, sm, sp, cap, **kwargs)]


def must_miss_custom(data, merge_fn, p, s, g, sm, sp, cap, **kwargs):
    return [d.tid for d in data
            if d.tid in MUST_INCLUDE and not oracle_in_custom(d, merge_fn, p, s, g, sm, sp, cap, **kwargs)]


def main():
    data = load_and_precompute()
    total = len(data)

    # ======= Approach A: Standard round-robin, find minimum cap =======
    print("=" * 80)
    print("APPROACH A: Standard round-robin with targeted track sizes")
    print("=" * 80)

    # Track size requirements for the 13 must-include targets:
    # sem ≥ 65, sup ≥ 104, gc ≥ 45, sel ≥ 54
    configs_a = [
        # (prior, sel, gc, sem, sup) - all targeted
        (10, 54, 45, 65, 104),
        (5,  54, 45, 65, 104),
        (3,  54, 45, 65, 104),
        # Smaller tracks
        (5,  40, 30, 50, 80),
        (5,  50, 45, 65, 104),
        # Even smaller prior
        (1,  54, 45, 65, 104),
    ]

    for p, s, g, sm, sp in configs_a:
        print(f"\n  p={p} s={s} g={g} sm={sm} sp={sp}:")
        for cap in range(50, 201, 10):
            h = hits(data, p, s, g, sm, sp, cap)
            mm = must_miss(data, p, s, g, sm, sp, cap)
            marker = " ***" if not mm else ""
            print(f"    cap={cap:3d}: {h}/{total}, must_miss={mm}{marker}")
            if not mm:
                # Found cap that covers all must-include
                sl_min, sl_max, sl_mean = shortlist_stats(data, p, s, g, sm, sp, cap)
                print(f"    → shortlist: min={sl_min} max={sl_max} mean={sl_mean:.1f}")
                break

    # Binary search minimum cap for best track config
    print("\n  Binary search minimum cap (p=3, s=54, g=45, sm=65, sp=104):")
    p, s, g, sm, sp = 3, 54, 45, 65, 104
    lo, hi = 50, 200
    while lo < hi:
        mid = (lo + hi) // 2
        mm = must_miss(data, p, s, g, sm, sp, mid)
        if not mm:
            hi = mid
        else:
            lo = mid + 1
    print(f"    Minimum cap: {lo}")
    h = hits(data, p, s, g, sm, sp, lo)
    ms = miss_list(data, p, s, g, sm, sp, lo)
    sl_min, sl_max, sl_mean = shortlist_stats(data, p, s, g, sm, sp, lo)
    print(f"    Result: {h}/{total}, miss={ms}")
    print(f"    Shortlist: min={sl_min} max={sl_max} mean={sl_mean:.1f}")

    # ======= Approach B: Weighted round-robin =======
    print("\n" + "=" * 80)
    print("APPROACH B: Weighted round-robin")
    print("=" * 80)
    # Give more bandwidth to semantic and support (they need deep coverage)
    # Track order: prior, selection, same_endpoint, gc, semantic, support
    weight_configs = [
        ([1, 2, 1, 1, 3, 3], "sem×3 sup×3 sel×2"),
        ([1, 1, 1, 1, 3, 5], "sem×3 sup×5"),
        ([1, 2, 1, 2, 3, 4], "sem×3 sup×4 gc×2 sel×2"),
        ([1, 1, 1, 1, 2, 3], "sem×2 sup×3"),
        ([1, 1, 1, 2, 4, 6], "sem×4 sup×6 gc×2"),
    ]

    p, s, g, sm, sp = 3, 54, 45, 65, 104
    for weights, label in weight_configs:
        print(f"\n  Weights: {label} (p={p} s={s} g={g} sm={sm} sp={sp})")
        for cap in range(50, 201, 10):
            h = hits_custom(data, _merge_weighted_round_robin, p, s, g, sm, sp, cap, weights=weights)
            mm = must_miss_custom(data, _merge_weighted_round_robin, p, s, g, sm, sp, cap, weights=weights)
            marker = " ***" if not mm else ""
            print(f"    cap={cap:3d}: {h}/{total}, must_miss={mm}{marker}")
            if not mm:
                break

    # Binary search best weighted config
    print("\n  Binary search min cap for best weighted config:")
    for weights, label in weight_configs:
        lo, hi = 50, 200
        while lo < hi:
            mid = (lo + hi) // 2
            mm = must_miss_custom(data, _merge_weighted_round_robin, p, s, g, sm, sp, mid, weights=weights)
            if not mm:
                hi = mid
            else:
                lo = mid + 1
        h = hits_custom(data, _merge_weighted_round_robin, p, s, g, sm, sp, lo, weights=weights)
        ms = miss_custom(data, _merge_weighted_round_robin, p, s, g, sm, sp, lo, weights=weights)
        print(f"    {label}: min_cap={lo}, {h}/{total}, miss={ms}")

    # ======= Approach C: Priority fill (round-robin + sequential) =======
    print("\n" + "=" * 80)
    print("APPROACH C: Priority fill (round-robin N rounds + sequential)")
    print("=" * 80)
    # Track indices: 0=prior, 1=sel, 2=same_endpoint, 3=gc, 4=sem, 5=sup
    # Priority: semantic and support go first in sequential phase
    priority_orders = [
        ([4, 5, 1, 3, 0, 2], "sem→sup→sel→gc→prior"),
        ([5, 4, 1, 3, 0, 2], "sup→sem→sel→gc→prior"),
        ([1, 4, 5, 3, 0, 2], "sel→sem→sup→gc→prior"),
    ]

    for rr_rounds in [5, 8, 10]:
        for priority, plabel in priority_orders:
            for cap in [80, 100, 120, 150]:
                h = hits_custom(data, _merge_priority_fill, p, s, g, sm, sp, cap,
                               priority_order=priority, round_robin_rounds=rr_rounds)
                mm = must_miss_custom(data, _merge_priority_fill, p, s, g, sm, sp, cap,
                                     priority_order=priority, round_robin_rounds=rr_rounds)
                if not mm:
                    ms = miss_custom(data, _merge_priority_fill, p, s, g, sm, sp, cap,
                                    priority_order=priority, round_robin_rounds=rr_rounds)
                    print(f"  rr={rr_rounds} {plabel} cap={cap}: {h}/{total} miss={ms} ***")
                    break

    # Binary search on best priority fill config
    print("\n  Binary search min cap for priority fill:")
    for rr_rounds in [5, 8, 10]:
        for priority, plabel in priority_orders:
            lo, hi = 50, 200
            while lo < hi:
                mid = (lo + hi) // 2
                mm = must_miss_custom(data, _merge_priority_fill, p, s, g, sm, sp, mid,
                                     priority_order=priority, round_robin_rounds=rr_rounds)
                if not mm:
                    hi = mid
                else:
                    lo = mid + 1
            h = hits_custom(data, _merge_priority_fill, p, s, g, sm, sp, lo,
                           priority_order=priority, round_robin_rounds=rr_rounds)
            ms = miss_custom(data, _merge_priority_fill, p, s, g, sm, sp, lo,
                            priority_order=priority, round_robin_rounds=rr_rounds)
            print(f"    rr={rr_rounds} {plabel}: min_cap={lo}, {h}/{total}, miss={ms}")

    # ======= Approach D: Optimal track sizes with standard round-robin =======
    # Try reducing track sizes while keeping just enough to cover must-include
    print("\n" + "=" * 80)
    print("APPROACH D: Optimize track sizes with standard round-robin")
    print("=" * 80)
    best_total = 999
    best_d = None
    for p in [1, 3, 5]:
        for s in [30, 40, 54]:
            for g in [20, 30, 45]:
                for sm in [40, 50, 65]:
                    for sp in [50, 70, 90, 104]:
                        for cap in range(60, 181, 5):
                            mm = must_miss(data, p, s, g, sm, sp, cap)
                            if not mm:
                                total_budget = p + s + g + sm + sp + cap
                                if total_budget < best_total:
                                    best_total = total_budget
                                    best_d = (p, s, g, sm, sp, cap)
                                break
    if best_d:
        p, s, g, sm, sp, cap = best_d
        h = hits(data, p, s, g, sm, sp, cap)
        ms = miss_list(data, p, s, g, sm, sp, cap)
        sl_min, sl_max, sl_mean = shortlist_stats(data, p, s, g, sm, sp, cap)
        print(f"  Best budget: p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {h}/{total}")
        print(f"  Miss: {ms}")
        print(f"  Shortlist: min={sl_min} max={sl_max} mean={sl_mean:.1f}")
        print(f"  Total budget (tracks+cap): {best_total}")


if __name__ == "__main__":
    main()
