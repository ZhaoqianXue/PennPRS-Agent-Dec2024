"""Final shortlist optimization: find minimum prior & cap for 80/80 and 79/80."""
from __future__ import annotations
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.offline_sim_shortlist_80 import (
    load_and_precompute, TargetTrackData
)

def hits(data, p, s, g, sm, sp, cap):
    return sum(1 for d in data if d.oracle_in_shortlist(p, s, g, sm, sp, cap))

def miss(data, p, s, g, sm, sp, cap):
    return [d.tid for d in data if not d.oracle_in_shortlist(p, s, g, sm, sp, cap)]

def main():
    data = load_and_precompute()
    total = len(data)

    # --- Find minimum prior for 80/80 with cap=280 ---
    print("=== Binary search min prior (s=55,g=48,sm=135,sp=105,cap=280) ===")
    for p in range(230, 245):
        h = hits(data, p, 55, 48, 135, 105, 280)
        ms = miss(data, p, 55, 48, 135, 105, 280) if h < total else []
        print(f"  prior={p}: {h}/{total} {ms}")

    # --- Binary search min cap with prior=240 ---
    print("\n=== Binary search min cap (p=240,s=55,g=48,sm=135,sp=105) ===")
    for cap in range(260, 295):
        h = hits(data, 240, 55, 48, 135, 105, cap)
        ms = miss(data, 240, 55, 48, 135, 105, cap) if h < total else []
        print(f"  cap={cap}: {h}/{total} {ms}")
        if h == total:
            break

    # --- Find minimum track sizes for 79/80 (excluding M1A) ---
    print("\n=== Configs for 79/80 ===")
    for cap in [150, 180, 200, 220, 250]:
        for p in [10, 20, 30, 50, 80, 130]:
            for s in [50, 55, 60, 80]:
                for g in [8, 30, 48]:
                    for sm in [25, 65, 100, 135, 170, 210]:
                        for sp in [12, 50, 80, 110]:
                            h = hits(data, p, s, g, sm, sp, cap)
                            if h >= 79:
                                ms = miss(data, p, s, g, sm, sp, cap)
                                if h == 79 and ms == ['M1A']:
                                    # 79/80 excluding only M1A
                                    print(f"  p={p:3d} s={s:3d} g={g:3d} sm={sm:3d} sp={sp:3d} cap={cap:3d}: {h}/{total} miss={ms}")
                                    break

    # --- Also verify: what shortlist size does the 80/80 config produce? ---
    print("\n=== Actual shortlist sizes with optimal config ===")
    from experiments.contribution3.transfer.agent import _merge_shortlist_tracks
    sizes = []
    for d in data:
        sl = _merge_shortlist_tracks(
            [d.prior_ranked[:240], d.selection_ranked[:55], d.same_endpoint_ids,
             d.gc_ranked[:48], d.semantic_ranked[:135], d.support_ranked[:105]],
            280,
        )
        sizes.append(len(sl))
    print(f"  Min shortlist size: {min(sizes)}")
    print(f"  Max shortlist size: {max(sizes)}")
    print(f"  Mean shortlist size: {sum(sizes)/len(sizes):.1f}")
    print(f"  Median shortlist size: {sorted(sizes)[len(sizes)//2]}")

    # Compare with baseline
    from experiments.contribution3.transfer.agent import UNIFIED_CONFIG as cfg
    sizes_base = []
    for d in data:
        sl = _merge_shortlist_tracks(
            [d.prior_ranked[:cfg.prior_track_size], d.selection_ranked[:cfg.selection_track_size],
             d.same_endpoint_ids, d.gc_ranked[:cfg.gc_track_size],
             d.semantic_ranked[:cfg.semantic_track_size], d.support_ranked[:cfg.support_track_size]],
            cfg.shortlist_cap,
        )
        sizes_base.append(len(sl))
    print(f"\n  Baseline mean shortlist: {sum(sizes_base)/len(sizes_base):.1f}, max: {max(sizes_base)}")


if __name__ == "__main__":
    main()
