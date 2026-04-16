"""Offline shortlist-oracle simulation for the unified 80-target benchmark.

Uses frozen prescreen GC from all-tools__20260413_154807/results.json (80/80 dossier
oracle recall) to systematically find shortlist track sizes that maximize oracle recall.

Key optimization: pre-computes full track rankings once per target, then uses fast
merge simulation to test many configs.

Does NOT call any LLM or live tool.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    UNIFIED_CONFIG,
    TransferConfig,
    _build_candidate_card,
    _bundle_lookup as agent_bundle_lookup,
    _gc_lookup,
    _gc_ranked_cards,
    _merge_shortlist_tracks,
    _prior_ranked_cards,
    _sort_cards,
    _support_ranked_cards,
    _target_source_for_dossier,
)
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    bundle_has_source_universe_pgs,
    is_self_like_bundle,
    load_candidate_dossiers,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows

UNIFIED_RESULTS = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_154807/results.json"
)
UNIFIED_DOSSIERS = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "candidate_dossiers.json"
)


def _prescreen_gc_from_result_row(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    for tr in row.get("tool_trace") or []:
        if tr.get("name") == "cross_trait_genetic_correlation" and tr.get("phase") == "candidate_prescreen":
            return _gc_lookup(tr.get("result"))
    return {}


class TargetTrackData:
    """Pre-computed track rankings for one target."""
    __slots__ = ("tid", "oracle_id", "prior_ranked", "selection_ranked",
                 "gc_ranked", "semantic_ranked", "same_endpoint_ids",
                 "support_ranked")

    def __init__(self, tid, oracle_id, prior_ranked, selection_ranked,
                 gc_ranked, semantic_ranked, same_endpoint_ids, support_ranked):
        self.tid = tid
        self.oracle_id = oracle_id
        self.prior_ranked = prior_ranked
        self.selection_ranked = selection_ranked
        self.gc_ranked = gc_ranked
        self.semantic_ranked = semantic_ranked
        self.same_endpoint_ids = same_endpoint_ids
        self.support_ranked = support_ranked

    def oracle_rank_in(self, track: list[str]) -> int:
        try:
            return track.index(self.oracle_id) + 1
        except ValueError:
            return 9999

    def oracle_in_shortlist(self, prior_sz, sel_sz, gc_sz, sem_sz, sup_sz, cap) -> bool:
        shortlist = _merge_shortlist_tracks(
            [
                self.prior_ranked[:prior_sz],
                self.selection_ranked[:sel_sz],
                self.same_endpoint_ids,
                self.gc_ranked[:gc_sz],
                self.semantic_ranked[:sem_sz],
                self.support_ranked[:sup_sz],
            ],
            cap,
        )
        return self.oracle_id in shortlist


def load_and_precompute(config: TransferConfig = UNIFIED_CONFIG) -> list[TargetTrackData]:
    print("Loading results.json ...")
    results = json.loads(UNIFIED_RESULTS.read_text())
    results_by_target = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results
        if (r.get("target") or {}).get("target_id")
    }
    del results

    print("Loading candidate dossiers...")
    dossiers = load_candidate_dossiers(UNIFIED_DOSSIERS)
    dossiers_by_target = {d.target.target_id: d for d in dossiers}

    print("Building shortlist recall rows...")
    recall_rows = build_shortlist_recall_rows(
        benchmark_family="unified",
        results_path=UNIFIED_RESULTS,
        candidate_dossiers_path=UNIFIED_DOSSIERS,
    )
    oracle_by_target: dict[str, str | None] = {}
    in_dossier: dict[str, bool] = {}
    for rrow in recall_rows:
        if rrow.get("status") != "ok":
            continue
        tid = str(rrow["target_id"])
        oracle_by_target[tid] = str(rrow.get("transfer_eligible_global_oracle_bundle_id") or "") or None
        in_dossier[tid] = bool(rrow.get("oracle_in_candidate_dossier"))

    print("Pre-computing track rankings...")
    data_list: list[TargetTrackData] = []
    for tid, oracle_id in sorted(oracle_by_target.items()):
        if not in_dossier.get(tid) or not oracle_id:
            continue
        dossier = dossiers_by_target.get(tid)
        result_row = results_by_target.get(tid)
        if dossier is None or result_row is None:
            continue

        gc_lookup_map = _prescreen_gc_from_result_row(result_row)
        target_source = _target_source_for_dossier(dossier, "unified")
        bundle_lookup_map = agent_bundle_lookup(dossier)
        candidate_bundle_ids = [
            b.bundle_id
            for b in dossier.candidates
            if not is_self_like_bundle(dossier.target, b)
            and bundle_has_source_universe_pgs(b, target_source)
        ]
        provisional_cards = [
            _build_candidate_card(
                dossier,
                bundle_lookup_map[bid],
                gc_row=gc_lookup_map.get(bid),
                config=config,
                target_source=target_source,
            )
            for bid in candidate_bundle_ids
            if bid in bundle_lookup_map
        ]

        prior_ranked = [c.bundle_id for c in _prior_ranked_cards(provisional_cards, config)]
        selection_ranked = [c.bundle_id for c in _sort_cards(provisional_cards, config)]
        gc_ranked = [c.bundle_id for c in _gc_ranked_cards(provisional_cards)]
        semantic_ranked_cards = sorted(
            provisional_cards,
            key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models),
        )
        semantic_ranked = [c.bundle_id for c in semantic_ranked_cards]
        same_endpoint_ids = [
            c.bundle_id for c in semantic_ranked_cards if c.archetype == "same-endpoint disease"
        ][:3]
        support_ranked = [c.bundle_id for c in _support_ranked_cards(provisional_cards)]

        data_list.append(TargetTrackData(
            tid=tid,
            oracle_id=oracle_id,
            prior_ranked=prior_ranked,
            selection_ranked=selection_ranked,
            gc_ranked=gc_ranked,
            semantic_ranked=semantic_ranked,
            same_endpoint_ids=same_endpoint_ids,
            support_ranked=support_ranked,
        ))

    print(f"Pre-computed rankings for {len(data_list)} targets")
    return data_list


def main() -> None:
    data_list = load_and_precompute()
    total = len(data_list)
    cfg = UNIFIED_CONFIG

    # Baseline
    base_hits = sum(1 for d in data_list
                    if d.oracle_in_shortlist(cfg.prior_track_size, cfg.selection_track_size,
                                             cfg.gc_track_size, cfg.semantic_track_size,
                                             cfg.support_track_size, cfg.shortlist_cap))
    print(f"\nBaseline: prior={cfg.prior_track_size} sel={cfg.selection_track_size} "
          f"gc={cfg.gc_track_size} sem={cfg.semantic_track_size} sup={cfg.support_track_size} "
          f"cap={cfg.shortlist_cap}: {base_hits}/{total}")

    # Diagnose each target's oracle rank per track
    print(f"\n{'TID':6s} {'Oracle':35s} {'Prior':>6s} {'Sel':>6s} {'GC':>6s} {'Sem':>6s} {'Sup':>6s} {'Same':>5s} {'Best':>5s} {'InSL':>5s}")
    for d in data_list:
        pr = d.oracle_rank_in(d.prior_ranked)
        sr = d.oracle_rank_in(d.selection_ranked)
        gr = d.oracle_rank_in(d.gc_ranked)
        smr = d.oracle_rank_in(d.semantic_ranked)
        spr = d.oracle_rank_in(d.support_ranked)
        in_same = "Y" if d.oracle_id in d.same_endpoint_ids else "N"
        best = min(pr, sr, gr, smr, spr)
        in_sl = d.oracle_in_shortlist(cfg.prior_track_size, cfg.selection_track_size,
                                       cfg.gc_track_size, cfg.semantic_track_size,
                                       cfg.support_track_size, cfg.shortlist_cap)
        if not in_sl:
            flag = " *** MISSING"
        else:
            flag = ""
        print(f"{d.tid:6s} {d.oracle_id:35s} {pr:6d} {sr:6d} {gr:6d} {smr:6d} {spr:6d} {in_same:>5s} {best:5d} {'Y' if in_sl else 'N':>5s}{flag}")

    # Analyze: what is the minimum best-track rank for missing oracles?
    missing = []
    for d in data_list:
        if not d.oracle_in_shortlist(cfg.prior_track_size, cfg.selection_track_size,
                                      cfg.gc_track_size, cfg.semantic_track_size,
                                      cfg.support_track_size, cfg.shortlist_cap):
            best = min(d.oracle_rank_in(d.prior_ranked), d.oracle_rank_in(d.selection_ranked),
                      d.oracle_rank_in(d.gc_ranked), d.oracle_rank_in(d.semantic_ranked),
                      d.oracle_rank_in(d.support_ranked))
            missing.append((d.tid, d.oracle_id, best))
    missing.sort(key=lambda x: x[2])
    print(f"\n{len(missing)} missing oracles sorted by best track rank:")
    for tid, oid, best in missing:
        print(f"  {tid:6s} {oid:35s} best_rank={best}")

    # Phase 1: Sweep cap with large tracks to find ceiling
    print("\n=== Phase 1: cap sweep (all tracks=500) ===")
    for cap in [75, 100, 120, 150, 180, 200, 250, 300]:
        hits = sum(1 for d in data_list if d.oracle_in_shortlist(500, 500, 500, 500, 500, cap))
        print(f"  cap={cap:4d}: {hits}/{total}")
        if hits == total:
            break

    # Phase 2: For each cap, find minimum uniform track size
    print("\n=== Phase 2: per-cap minimum uniform track size ===")
    for cap in [100, 120, 150, 180, 200, 250, 300]:
        for ts in range(10, 301, 5):
            hits = sum(1 for d in data_list if d.oracle_in_shortlist(ts, ts, ts, ts, ts, cap))
            if hits == total:
                print(f"  cap={cap:4d}: uniform track_size={ts} -> {hits}/{total}")
                break
        else:
            hits = sum(1 for d in data_list if d.oracle_in_shortlist(300, 300, 300, 300, 300, cap))
            print(f"  cap={cap:4d}: track_size=300 -> {hits}/{total} (not enough)")

    # Phase 3: Targeted optimization - increase each track independently
    print("\n=== Phase 3: Targeted track expansion ===")
    # Start from baseline and iteratively increase the most beneficial track
    best_prior, best_sel, best_gc, best_sem, best_sup, best_cap = (
        cfg.prior_track_size, cfg.selection_track_size, cfg.gc_track_size,
        cfg.semantic_track_size, cfg.support_track_size, cfg.shortlist_cap
    )
    current_hits = base_hits

    # Try increasing each track size in steps and report
    for cap_try in [75, 100, 120, 150, 200, 250, 300]:
        print(f"\n  --- With cap={cap_try} ---")
        # For each missing target, which track would capture it at smallest size?
        for d in data_list:
            if d.oracle_in_shortlist(cfg.prior_track_size, cfg.selection_track_size,
                                      cfg.gc_track_size, cfg.semantic_track_size,
                                      cfg.support_track_size, cap_try):
                continue
            pr = d.oracle_rank_in(d.prior_ranked)
            sr = d.oracle_rank_in(d.selection_ranked)
            gr = d.oracle_rank_in(d.gc_ranked)
            smr = d.oracle_rank_in(d.semantic_ranked)
            spr = d.oracle_rank_in(d.support_ranked)
            best_track = min(
                ("prior", pr), ("sel", sr), ("gc", gr), ("sem", smr), ("sup", spr),
                key=lambda x: x[1]
            )
            # Check if it actually makes the merge at cap_try
            for try_sz in range(best_track[1], min(best_track[1] + 50, 400)):
                sizes = {
                    "prior": cfg.prior_track_size,
                    "sel": cfg.selection_track_size,
                    "gc": cfg.gc_track_size,
                    "sem": cfg.semantic_track_size,
                    "sup": cfg.support_track_size,
                }
                sizes[best_track[0]] = try_sz
                if d.oracle_in_shortlist(sizes["prior"], sizes["sel"], sizes["gc"],
                                          sizes["sem"], sizes["sup"], cap_try):
                    print(f"    {d.tid}: needs {best_track[0]}≥{try_sz} (oracle rank in {best_track[0]}={best_track[1]})")
                    break

    # Phase 4: Greedy expansion - start from baseline, keep adding track size to capture one more oracle
    print("\n=== Phase 4: Greedy expansion from baseline ===")
    for cap_try in [100, 120, 150, 200, 250]:
        p, s, g, sm, sp = cfg.prior_track_size, cfg.selection_track_size, cfg.gc_track_size, cfg.semantic_track_size, cfg.support_track_size
        hits = sum(1 for d in data_list if d.oracle_in_shortlist(p, s, g, sm, sp, cap_try))
        print(f"\n  Starting with cap={cap_try}: {hits}/{total}")

        while hits < total:
            # For each missing target, find cheapest expansion
            best_expansion = None
            for d in data_list:
                if d.oracle_in_shortlist(p, s, g, sm, sp, cap_try):
                    continue
                # Try expanding each track
                for track_name, current_sz, ranked_list in [
                    ("prior", p, d.prior_ranked),
                    ("sel", s, d.selection_ranked),
                    ("gc", g, d.gc_ranked),
                    ("sem", sm, d.semantic_ranked),
                    ("sup", sp, d.support_ranked),
                ]:
                    oracle_rank = d.oracle_rank_in(ranked_list)
                    if oracle_rank >= 9999:
                        continue
                    needed = oracle_rank
                    if needed <= current_sz:
                        # Oracle is already within track size, but not in shortlist due to cap
                        # Need to increase cap instead
                        continue
                    cost = needed - current_sz  # how much we need to grow this track
                    if best_expansion is None or cost < best_expansion[1]:
                        best_expansion = (track_name, cost, needed, d.tid)

            if best_expansion is None:
                # Check if it's a cap issue
                for d in data_list:
                    if d.oracle_in_shortlist(p, s, g, sm, sp, cap_try):
                        continue
                    # Try with larger cap
                    if d.oracle_in_shortlist(p, s, g, sm, sp, 500):
                        print(f"    {d.tid}: captured at cap=500 but not at cap={cap_try} -> cap issue")
                break

            track_name, cost, needed, tid = best_expansion
            if track_name == "prior":
                p = needed
            elif track_name == "sel":
                s = needed
            elif track_name == "gc":
                g = needed
            elif track_name == "sem":
                sm = needed
            elif track_name == "sup":
                sp = needed

            new_hits = sum(1 for d in data_list if d.oracle_in_shortlist(p, s, g, sm, sp, cap_try))
            gained = new_hits - hits
            hits = new_hits
            print(f"    Expand {track_name} to {needed} (for {tid}): {hits}/{total} (+{gained})")

        print(f"  Final: prior={p} sel={s} gc={g} sem={sm} sup={sp} cap={cap_try}: {hits}/{total}")


if __name__ == "__main__":
    main()
