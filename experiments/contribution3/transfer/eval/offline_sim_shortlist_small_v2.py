"""Smart search for best shortlist config with params ≤ old values, cap ≤ 50.

Strategy: use coarse grid to find promising regions, then refine.
Also test whether reducing the number of tracks helps (fewer tracks = more budget per track).
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


def shortlist_stats(data, p, s, g, sm, sp, cap):
    sizes = []
    for d in data:
        sl = _merge_shortlist_tracks(
            [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
             d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]], cap)
        sizes.append(len(sl))
    return min(sizes), max(sizes), sum(sizes) / len(sizes)


def main():
    data = load_and_precompute()
    total = len(data)

    # --- Phase 1: Coarse grid to find best hits ---
    print("=== Phase 1: Coarse grid (p≤10, s≤50, g≤8, sm≤25, sp≤12, cap≤50) ===")
    best_h = 0
    best_cfgs = []
    for cap in [35, 40, 45, 50]:
        for p in [1, 3, 5, 7, 10]:
            for s in [10, 20, 30, 40, 50]:
                for g in [1, 3, 5, 8]:
                    for sm in [1, 5, 10, 15, 20, 25]:
                        for sp in [1, 4, 8, 12]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_h:
                                best_h = h
                                best_cfgs = [(p, s, g, sm, sp, cap)]
                            elif h == best_h:
                                best_cfgs.append((p, s, g, sm, sp, cap))

    print(f"Best coarse: {best_h}/{total}")
    # Show compact configs
    best_cfgs.sort(key=lambda c: (c[5], sum(c[:5])))
    for cfg in best_cfgs[:10]:
        p, s, g, sm, sp, cap = cfg
        ms = miss_list(data, p, s, g, sm, sp, cap)
        print(f"  p={p:2d} s={s:2d} g={g} sm={sm:2d} sp={sp:2d} cap={cap:2d}: {best_h}/{total} miss={ms}")

    # --- Phase 2: Fine-tune around best coarse config ---
    p0, s0, g0, sm0, sp0, cap0 = best_cfgs[0]
    print(f"\n=== Phase 2: Fine-tune around p={p0} s={s0} g={g0} sm={sm0} sp={sp0} cap={cap0} ===")
    best_h2 = best_h
    best_cfg2 = best_cfgs[0]
    for cap in range(max(30, cap0 - 5), min(51, cap0 + 6)):
        for p in range(max(1, p0 - 3), min(11, p0 + 4)):
            for s in range(max(5, s0 - 10), min(51, s0 + 11)):
                for g in range(max(1, g0 - 2), min(9, g0 + 3)):
                    for sm in range(max(1, sm0 - 5), min(26, sm0 + 6)):
                        for sp in range(max(1, sp0 - 3), min(13, sp0 + 4)):
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_h2 or (h == best_h2 and sum([p, s, g, sm, sp]) < sum(best_cfg2[:5])):
                                best_h2 = h
                                best_cfg2 = (p, s, g, sm, sp, cap)

    p, s, g, sm, sp, cap = best_cfg2
    ms = miss_list(data, p, s, g, sm, sp, cap)
    sl_min, sl_max, sl_mean = shortlist_stats(data, p, s, g, sm, sp, cap)
    print(f"  Best: p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {best_h2}/{total}")
    print(f"  Miss: {ms}")
    print(f"  Shortlist: min={sl_min} max={sl_max} mean={sl_mean:.1f}")

    # --- Phase 3: Selection-dominated strategies ---
    # Key insight: selection track is most productive. What if we maximize its budget?
    print("\n=== Phase 3: Selection-dominated (minimize other tracks) ===")
    for cap in [40, 45, 50]:
        for s in range(10, 51):
            for p in [1, 2, 3]:
                for g in [1, 2, 3]:
                    for sm in [1, 3, 5]:
                        for sp in [1, 2, 3]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h >= best_h:
                                ms = miss_list(data, p, s, g, sm, sp, cap)
                                if h > best_h:
                                    print(f"  NEW BEST: ", end="")
                                    best_h = h
                                sl_min, sl_max, sl_mean = shortlist_stats(data, p, s, g, sm, sp, cap)
                                print(f"  p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: {h}/{total} "
                                      f"miss={ms} sl_mean={sl_mean:.1f}")

    # --- Phase 4: Try disabling tracks entirely (size=0 analog: set to 1) ---
    print("\n=== Phase 4: Dropping tracks (set to 1) ===")
    # What if we only use selection + one other track?
    for cap in [40, 45, 50]:
        for s in range(20, 51, 5):
            # Selection only
            h = hits(data, 1, s, 1, 1, 1, cap)
            if h >= best_h - 3:
                ms = miss_list(data, 1, s, 1, 1, 1, cap)
                print(f"  sel-only: p=1 s={s} g=1 sm=1 sp=1 cap={cap}: {h}/{total} miss_count={len(ms)}")
            # Selection + semantic
            for sm in [5, 10, 15, 20, 25]:
                h = hits(data, 1, s, 1, sm, 1, cap)
                if h >= best_h - 2:
                    ms = miss_list(data, 1, s, 1, sm, 1, cap)
                    print(f"  sel+sem:  p=1 s={s} g=1 sm={sm} sp=1 cap={cap}: {h}/{total} miss_count={len(ms)}")
            # Selection + gc
            for g in [3, 5, 8]:
                h = hits(data, 1, s, g, 1, 1, cap)
                if h >= best_h - 2:
                    ms = miss_list(data, 1, s, g, 1, 1, cap)
                    print(f"  sel+gc:   p=1 s={s} g={g} sm=1 sp=1 cap={cap}: {h}/{total} miss_count={len(ms)}")

    # --- Phase 5: Per-cap best summary ---
    print("\n=== Phase 5: Best per cap (coarse) ===")
    for cap in range(30, 76, 5):
        best_hc = 0
        best_cc = None
        for p in [1, 3, 5, 7, 10]:
            for s in [10, 20, 30, 40, 50]:
                for g in [1, 3, 5, 8]:
                    for sm in [1, 5, 10, 15, 20, 25]:
                        for sp in [1, 4, 8, 12]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_hc or (h == best_hc and best_cc and sum([p, s, g, sm, sp]) < sum(best_cc)):
                                best_hc = h
                                best_cc = (p, s, g, sm, sp)
        p, s, g, sm, sp = best_cc
        ms = miss_list(data, p, s, g, sm, sp, cap)
        print(f"  cap={cap:2d}: p={p:2d} s={s:2d} g={g} sm={sm:2d} sp={sp:2d}: {best_hc}/{total} miss_count={len(ms)}")


if __name__ == "__main__":
    main()
