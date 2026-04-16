"""Fine-grained search within strict old-value limits.
Constraints: p≤10, s≤50, g≤8, sm≤25, sp≤12, cap≤50.
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


def main():
    data = load_and_precompute()
    total = len(data)

    # Fine grid: all params within old limits
    print("=== Fine grid search: p≤10, s≤50, g≤8, sm≤25, sp≤12, cap≤50 ===")
    best_h = 0
    best_cfgs = []
    for cap in range(30, 51):
        for p in range(1, 11):
            for s in range(5, 51, 5):
                for g in range(1, 9):
                    for sm in range(1, 26, 2):
                        for sp in range(1, 13):
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_h:
                                best_h = h
                                best_cfgs = [(p, s, g, sm, sp, cap)]
                            elif h == best_h:
                                best_cfgs.append((p, s, g, sm, sp, cap))

    print(f"Best: {best_h}/{total}")
    # Show top configs with smallest total track budget
    best_cfgs.sort(key=lambda c: (c[5], sum(c[:5])))  # sort by cap then total budget
    seen = set()
    for cfg in best_cfgs[:20]:
        p, s, g, sm, sp, cap = cfg
        key = (p, s, g, sm, sp, cap)
        if key not in seen:
            seen.add(key)
            ms = miss_list(data, p, s, g, sm, sp, cap)
            sizes = []
            for d in data:
                sl = _merge_shortlist_tracks(
                    [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
                     d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]], cap)
                sizes.append(len(sl))
            print(f"  p={p:2d} s={s:2d} g={g} sm={sm:2d} sp={sp:2d} cap={cap:2d}: {best_h}/{total} "
                  f"miss={ms} sl_mean={sum(sizes)/len(sizes):.1f} sl_max={max(sizes)}")

    # Also check: what if we relax cap slightly (51-60)?
    print(f"\n=== Relaxed cap (51-75), same track limits ===")
    for cap in [55, 60, 65, 70, 75]:
        # Use best track config from above
        p, s, g, sm, sp, _ = best_cfgs[0]
        h = hits(data, p, s, g, sm, sp, cap)
        ms = miss_list(data, p, s, g, sm, sp, cap) if h < total else []
        print(f"  p={p:2d} s={s:2d} g={g} sm={sm:2d} sp={sp:2d} cap={cap}: {h}/{total} miss={ms}")

    # Also find best for each cap in [30..75]
    print(f"\n=== Best per cap (track limits: p≤10, s≤50, g≤8, sm≤25, sp≤12) ===")
    for cap in range(30, 76, 5):
        best_hc = 0
        best_cc = None
        for p in range(1, 11, 2):
            for s in [10, 20, 30, 40, 50]:
                for g in [1, 3, 5, 8]:
                    for sm in [1, 5, 10, 15, 20, 25]:
                        for sp in [1, 4, 8, 12]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h > best_hc:
                                best_hc = h
                                best_cc = (p, s, g, sm, sp)
        p, s, g, sm, sp = best_cc
        ms = miss_list(data, p, s, g, sm, sp, cap)
        print(f"  cap={cap:2d}: p={p:2d} s={s:2d} g={g} sm={sm:2d} sp={sp:2d}: {best_hc}/{total} miss={ms}")


if __name__ == "__main__":
    main()
