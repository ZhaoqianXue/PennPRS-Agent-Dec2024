"""Focused verification: find minimum track sizes with cap=300 for 80/80."""

from __future__ import annotations
import json, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.offline_sim_shortlist_80 import (
    load_and_precompute, TargetTrackData
)
from experiments.contribution3.transfer.agent import UNIFIED_CONFIG

def count_hits(data: list[TargetTrackData], p, s, g, sm, sp, cap) -> int:
    return sum(1 for d in data if d.oracle_in_shortlist(p, s, g, sm, sp, cap))

def missing(data: list[TargetTrackData], p, s, g, sm, sp, cap) -> list[str]:
    return [d.tid for d in data if not d.oracle_in_shortlist(p, s, g, sm, sp, cap)]

def main():
    data = load_and_precompute()
    total = len(data)

    # Verify Phase 2 result: uniform 240, cap=300
    h = count_hits(data, 240, 240, 240, 240, 240, 300)
    print(f"Verify: uniform=240, cap=300: {h}/{total}")

    # Binary search each track down while keeping others at 240
    print("\n=== Binary search minimum per-track (others=240, cap=300) ===")
    for name, idx in [("prior", 0), ("sel", 1), ("gc", 2), ("sem", 3), ("sup", 4)]:
        lo, hi = 1, 240
        while lo < hi:
            mid = (lo + hi) // 2
            args = [240, 240, 240, 240, 240]
            args[idx] = mid
            h = count_hits(data, *args, 300)
            if h == total:
                hi = mid
            else:
                lo = mid + 1
        args = [240, 240, 240, 240, 240]
        args[idx] = lo
        h = count_hits(data, *args, 300)
        ms = missing(data, *args, 300)
        print(f"  {name}: min={lo} ({h}/{total}), missing={ms}")

    # Now find joint minimum
    # From the individual minimums, we know each track's minimum with others at 240.
    # But jointly, we need to find smaller values.

    # Test specific configs
    print("\n=== Test specific configs with cap=300 ===")
    configs = [
        (240, 240, 50, 140, 110),   # based on Phase 3 analysis
        (240, 60, 50, 140, 110),
        (240, 55, 50, 140, 110),
        (240, 55, 50, 135, 110),
        (240, 55, 50, 135, 105),
        (240, 55, 48, 135, 105),
        (240, 55, 48, 132, 105),
        # Try smaller prior
        (200, 55, 48, 135, 110),
        (180, 55, 48, 135, 110),
        (150, 55, 48, 135, 110),
        (100, 55, 48, 135, 110),
        (80, 55, 48, 135, 110),
        (60, 55, 48, 135, 110),
        (50, 55, 48, 135, 110),
    ]
    for p, s, g, sm, sp in configs:
        h = count_hits(data, p, s, g, sm, sp, 300)
        ms = missing(data, p, s, g, sm, sp, 300)
        status = "OK" if h == total else f"MISSING {ms}"
        print(f"  p={p:3d} s={s:3d} g={g:3d} sm={sm:3d} sp={sp:3d}: {h}/{total} {status}")

    # The problem: M1A oracle has best rank 237 on prior track.
    # With round-robin across 6 tracks, prior's 237th entry appears late.
    # Need prior large enough AND cap large enough.

    # Test: find minimum cap with uniform=240
    print("\n=== Binary search minimum cap with uniform=240 ===")
    lo, hi = 200, 300
    while lo < hi:
        mid = (lo + hi) // 2
        h = count_hits(data, 240, 240, 240, 240, 240, mid)
        if h == total:
            hi = mid
        else:
            lo = mid + 1
    print(f"  Minimum cap (uniform=240): {lo} ({count_hits(data, 240, 240, 240, 240, 240, lo)}/{total})")
    print(f"  Missing at cap={lo-1}: {missing(data, 240, 240, 240, 240, 240, lo-1)}")

    # Now try: what if we just increase cap but keep modest track sizes?
    # Key: each track needs to be large enough to contain the oracle,
    # AND the merge must not fill up before reaching it.
    print("\n=== Smart configs: match requirement per track ===")
    # Requirements from analysis:
    # M1A: prior≥237 (best on prior)
    # N61: sem≥131 (best on sem)
    # D03: sem≥113
    # G30: sup≥104
    # G43: prior≥128 or sem≥167
    # I85: prior≥120 or sem≥204
    # N91: sup≥91
    # N97: sem≥65
    # All others need ≤65 on their best track

    smart_configs = [
        # prior, sel, gc, sem, sup, cap
        (240, 55, 48, 135, 105, 300),
        (240, 55, 48, 135, 105, 280),
        (240, 55, 48, 135, 105, 260),
        (240, 55, 48, 135, 105, 250),
        (240, 55, 48, 205, 105, 280),
        (240, 55, 48, 205, 105, 260),
        (240, 55, 48, 205, 105, 250),
        (240, 55, 48, 205, 105, 240),
        (240, 240, 48, 205, 105, 250),
        (240, 240, 240, 240, 240, 250),
        (240, 240, 240, 240, 240, 260),
        (240, 240, 240, 240, 240, 270),
        (240, 240, 240, 240, 240, 280),
        (240, 240, 240, 240, 240, 290),
    ]
    for p, s, g, sm, sp, cap in smart_configs:
        h = count_hits(data, p, s, g, sm, sp, cap)
        ms = missing(data, p, s, g, sm, sp, cap)
        status = "OK" if h == total else f"MISSING {ms}"
        print(f"  p={p:3d} s={s:3d} g={g:3d} sm={sm:3d} sp={sp:3d} cap={cap:3d}: {h}/{total} {status}")

    # Fine-tune: binary search cap with prior=240, sem=205, others moderate
    print("\n=== Fine-tune cap ===")
    for p, s, g, sm, sp in [(240, 240, 240, 240, 240)]:
        lo, hi = 250, 300
        while lo < hi:
            mid = (lo + hi) // 2
            h = count_hits(data, p, s, g, sm, sp, mid)
            if h == total:
                hi = mid
            else:
                lo = mid + 1
        ms_below = missing(data, p, s, g, sm, sp, lo-1)
        print(f"  p={p} s={s} g={g} sm={sm} sp={sp}: min cap={lo}, missing at cap={lo-1}: {ms_below}")

    # Test with even larger values to find real minimum cap
    for p, s, g, sm, sp in [(300, 300, 300, 300, 300), (400, 400, 400, 400, 400)]:
        lo, hi = 200, 400
        while lo < hi:
            mid = (lo + hi) // 2
            h = count_hits(data, p, s, g, sm, sp, mid)
            if h == total:
                hi = mid
            else:
                lo = mid + 1
        ms_below = missing(data, p, s, g, sm, sp, lo-1)
        print(f"  p={p} s={s} g={g} sm={sm} sp={sp}: min cap={lo}, missing at cap={lo-1}: {ms_below}")


if __name__ == "__main__":
    main()
