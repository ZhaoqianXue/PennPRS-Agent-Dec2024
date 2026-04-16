"""Find config achieving ~75/80 with cap ≈ 100 (must include G30).

G30 bottleneck: oracle at support rank 104.
Key idea: give support track more bandwidth via weighted round-robin or
two-phase merge (standard shortlist + deep support append).
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


# ---------- Merge algorithms ----------

def _merge_weighted(track_ids, weights, cap):
    """Weighted round-robin: track i contributes weights[i] entries per round."""
    shortlist, seen = [], set()
    ptrs = [0] * len(track_ids)
    while len(shortlist) < cap:
        added = False
        for i, track in enumerate(track_ids):
            for _ in range(weights[i]):
                while ptrs[i] < len(track):
                    bid = track[ptrs[i]]
                    ptrs[i] += 1
                    if bid not in seen:
                        seen.add(bid)
                        shortlist.append(bid)
                        added = True
                        break
                if len(shortlist) >= cap:
                    return shortlist
        if not added:
            break
    return shortlist


def _merge_two_phase(track_ids, deep_track_idx, deep_size, cap):
    """Phase 1: round-robin from all tracks (small sizes).
    Phase 2: append remaining entries from deep track up to deep_size.
    Total capped at cap."""
    shortlist, seen = [], set()
    # Phase 1: standard round-robin
    max_len = max((len(t) for t in track_ids), default=0)
    for idx in range(max_len):
        for track in track_ids:
            if idx >= len(track):
                continue
            bid = track[idx]
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    # Phase 2: fill from deep track
    deep = track_ids[deep_track_idx]
    for bid in deep[:deep_size]:
        if bid not in seen:
            seen.add(bid)
            shortlist.append(bid)
            if len(shortlist) >= cap:
                return shortlist
    return shortlist


def _merge_multi_deep(track_ids, deep_configs, cap):
    """Phase 1: standard round-robin from track_ids (using their given sizes).
    Phase 2: for each (track_idx, deep_size), append unseen entries up to deep_size.
    Total capped at cap."""
    shortlist, seen = [], set()
    # Phase 1: standard round-robin
    max_len = max((len(t) for t in track_ids), default=0)
    for idx in range(max_len):
        for track in track_ids:
            if idx >= len(track):
                continue
            bid = track[idx]
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    # Phase 2: deep fills
    for track_idx, deep_size in deep_configs:
        full_track = track_ids[track_idx]
        # We need the FULL track, not truncated. This is handled by caller.
        for bid in full_track[:deep_size]:
            if bid not in seen:
                seen.add(bid)
                shortlist.append(bid)
                if len(shortlist) >= cap:
                    return shortlist
    return shortlist


# ---------- Evaluation helpers ----------

def oracle_in(d, merge_fn, tracks, cap, **kw):
    sl = merge_fn(tracks, cap=cap, **kw)
    return d.oracle_id in sl


def eval_config(data, merge_fn, track_builder, cap, **kw):
    """Returns (total_hits, must_miss_list, all_miss_list, mean_sl_size)."""
    hit = 0
    must_miss = []
    all_miss = []
    sizes = []
    for d in data:
        tracks = track_builder(d)
        sl = merge_fn(tracks, cap=cap, **kw)
        sizes.append(len(sl))
        if d.oracle_id in sl:
            hit += 1
        else:
            all_miss.append(d.tid)
            if d.tid in MUST_INCLUDE:
                must_miss.append(d.tid)
    return hit, must_miss, all_miss, sum(sizes) / len(sizes)


def main():
    data = load_and_precompute()
    total = len(data)

    # ====== Approach 1: Weighted round-robin, support gets heavy weight ======
    print("=" * 80)
    print("APPROACH 1: Weighted round-robin (support heavy)")
    print("=" * 80)

    # Track order: prior, sel, same_endpoint, gc, sem, sup
    # Give support 5-15x weight to reach rank 104 faster
    for sup_w in [5, 8, 10, 12, 15]:
        for sem_w in [1, 2, 3]:
            weights = [1, 1, 1, 1, sem_w, sup_w]
            label = f"sup×{sup_w} sem×{sem_w}"
            for p, s, g, sm, sp in [(3, 20, 15, 30, 104), (3, 30, 25, 40, 104), (3, 54, 45, 65, 104)]:
                for cap in [80, 90, 100, 110, 120]:
                    def build_tracks(d, p=p, s=s, g=g, sm=sm, sp=sp):
                        return [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
                                d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp]]
                    h, mm, am, sl_mean = eval_config(data, _merge_weighted, build_tracks, cap, weights=weights)
                    g30_ok = 'G30' not in mm
                    if h >= 72 and g30_ok:
                        print(f"  {label} p={p} s={s} g={g} sm={sm} sp={sp} cap={cap}: "
                              f"{h}/{total} must_miss={mm} sl_mean={sl_mean:.0f}")

    # ====== Approach 2: Two-phase merge (RR + deep support append) ======
    print("\n" + "=" * 80)
    print("APPROACH 2: Two-phase (round-robin + deep support append)")
    print("=" * 80)

    # Phase 1 tracks are small (for diversity), Phase 2 appends deep support
    for p, s, g, sm, sp_rr in [(3, 20, 8, 25, 12), (3, 30, 15, 30, 15),
                                 (3, 25, 10, 25, 10), (1, 20, 8, 20, 8)]:
        for cap in [80, 90, 100, 110]:
            def build_tracks(d, p=p, s=s, g=g, sm=sm, sp_rr=sp_rr):
                return [d.prior_ranked[:p], d.selection_ranked[:s], d.same_endpoint_ids,
                        d.gc_ranked[:g], d.semantic_ranked[:sm], d.support_ranked[:sp_rr]]
            # Deep support track is index 5, extend to rank 104
            h, mm, am, sl_mean = eval_config(
                data, _merge_two_phase, build_tracks, cap,
                deep_track_idx=5, deep_size=104)
            g30_ok = 'G30' not in mm
            if h >= 65 and g30_ok:
                print(f"  p={p} s={s} g={g} sm={sm} sp_rr={sp_rr} deep_sup=104 cap={cap}: "
                      f"{h}/{total} must_miss={mm} sl_mean={sl_mean:.0f}")

    # ====== Approach 3: Multi-deep (RR + deep semantic + deep support + deep gc) ======
    print("\n" + "=" * 80)
    print("APPROACH 3: Multi-deep (RR + deep sem/sup/gc/sel)")
    print("=" * 80)

    for p, s_rr, g_rr, sm_rr, sp_rr in [(1, 10, 5, 10, 5), (3, 15, 8, 15, 8),
                                           (3, 20, 10, 20, 10)]:
        for cap in [85, 90, 95, 100, 105, 110]:
            def build_tracks(d, p=p, s=s_rr, g=g_rr, sm=sm_rr, sp=sp_rr):
                # For phase 2, we need full-length tracks for deep fill.
                # Pass full-length tracks; phase 1 uses the small sizes via the track slice,
                # phase 2 uses deep_configs to extend.
                return [d.prior_ranked[:p], d.selection_ranked[:max(s, 54)],
                        d.same_endpoint_ids,
                        d.gc_ranked[:max(g, 45)], d.semantic_ranked[:max(sm, 65)],
                        d.support_ranked[:104]]

            # deep_configs: after round-robin exhausts small tracks,
            # extend sel to 54, gc to 45, sem to 65, sup to 104
            h, mm, am, sl_mean = eval_config(
                data, _merge_multi_deep, build_tracks, cap,
                deep_configs=[(1, 54), (3, 45), (4, 65), (5, 104)])
            g30_ok = 'G30' not in mm
            if h >= 70 and g30_ok:
                print(f"  p={p} s_rr={s_rr} g_rr={g_rr} sm_rr={sm_rr} sp_rr={sp_rr} cap={cap}: "
                      f"{h}/{total} must_miss={mm} sl_mean={sl_mean:.0f}")

    # ====== Approach 4: Pure multi-deep with minimal RR ======
    print("\n" + "=" * 80)
    print("APPROACH 4: Minimal RR (5 rounds) + sequential deep fill")
    print("=" * 80)

    for cap in range(85, 121, 5):
        # Minimal round-robin: 5 rounds from all tracks
        # Then sequential: sup→sem→gc→sel (deepest first)
        def build_tracks_full(d):
            return [d.prior_ranked[:5], d.selection_ranked[:54],
                    d.same_endpoint_ids,
                    d.gc_ranked[:45], d.semantic_ranked[:65],
                    d.support_ranked[:104]]

        def merge_minimal_rr(tracks, cap, rr_rounds=5):
            shortlist, seen = [], set()
            # Phase 1: limited round-robin
            for idx in range(rr_rounds):
                for track in tracks:
                    if idx >= len(track):
                        continue
                    bid = track[idx]
                    if bid not in seen:
                        seen.add(bid)
                        shortlist.append(bid)
                        if len(shortlist) >= cap:
                            return shortlist
            # Phase 2: sequential deep fill (sup, sem, gc, sel)
            for ti in [5, 4, 3, 1]:
                for bid in tracks[ti]:
                    if bid not in seen:
                        seen.add(bid)
                        shortlist.append(bid)
                        if len(shortlist) >= cap:
                            return shortlist
            return shortlist

        h, mm, am, sl_mean = eval_config(data, merge_minimal_rr, build_tracks_full, cap)
        g30_ok = 'G30' not in mm
        print(f"  rr=5 cap={cap}: {h}/{total} must_miss={mm} sl_mean={sl_mean:.0f} G30={'OK' if g30_ok else 'MISS'}")

    # ====== Approach 5: Best-rank merge (sort by best rank across all tracks) ======
    print("\n" + "=" * 80)
    print("APPROACH 5: Best-rank merge (union sorted by best_rank)")
    print("=" * 80)

    def merge_best_rank(tracks, cap):
        """Union of all tracks, sorted by best rank across tracks, take top-cap."""
        # Build best_rank for each bundle
        best_rank = {}
        for track in tracks:
            for rank, bid in enumerate(track):
                if bid not in best_rank or rank < best_rank[bid]:
                    best_rank[bid] = rank
        sorted_bids = sorted(best_rank.keys(), key=lambda b: (best_rank[b], b))
        return sorted_bids[:cap]

    for s, g, sm, sp in [(54, 45, 65, 104), (40, 35, 50, 104), (30, 25, 40, 104)]:
        for cap in range(85, 121, 5):
            def build_t(d, s=s, g=g, sm=sm, sp=sp):
                return [d.prior_ranked[:10], d.selection_ranked[:s],
                        d.same_endpoint_ids,
                        d.gc_ranked[:g], d.semantic_ranked[:sm],
                        d.support_ranked[:sp]]
            h, mm, am, sl_mean = eval_config(data, merge_best_rank, build_t, cap)
            g30_ok = 'G30' not in mm
            if h >= 70 and g30_ok:
                print(f"  s={s} g={g} sm={sm} sp={sp} cap={cap}: {h}/{total} must_miss={mm} sl_mean={sl_mean:.0f}")

    # ====== Summary: which approach + cap achieves best with G30? ======
    print("\n" + "=" * 80)
    print("SUMMARY: Minimum cap per approach for all 13 must-include")
    print("=" * 80)


if __name__ == "__main__":
    main()
