"""Analyze oracle ranks across ALL possible ranking dimensions.

For each must-include target, compute oracle rank on every available feature.
Find new track rankings that could bring hard oracles (esp G30) into top-30.
Then test shortlist oracle recall with new/modified tracks.
"""
from __future__ import annotations
import math, json, sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    UNIFIED_CONFIG, _build_candidate_card, _gc_lookup,
    _target_source_for_dossier, _merge_shortlist_tracks,
    _bundle_lookup as agent_bundle_lookup,
)
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier, bundle_has_source_universe_pgs,
    is_self_like_bundle, load_candidate_dossiers,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows
from experiments.contribution3.transfer.prompts.transfer_prompt import CandidateEvidenceCard

UNIFIED_RESULTS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_154807/results.json"
)
UNIFIED_DOSSIERS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "candidate_dossiers.json"
)

MUST_INCLUDE = {
    'C22', 'E79', 'D05', 'L68', 'B18', 'M05', 'L05', 'L56',
    'C54', 'F11', 'N97', 'N91', 'G30',
}


def _prescreen_gc(row):
    for tr in row.get("tool_trace") or []:
        if tr.get("name") == "cross_trait_genetic_correlation" and tr.get("phase") == "candidate_prescreen":
            return _gc_lookup(tr.get("result"))
    return {}


def rank_of(oracle_id, ranked_ids):
    try:
        return ranked_ids.index(oracle_id) + 1
    except ValueError:
        return 9999


def main():
    print("Loading data...")
    results = json.loads(UNIFIED_RESULTS.read_text())
    results_by_target = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results if (r.get("target") or {}).get("target_id")
    }
    del results

    dossiers = load_candidate_dossiers(UNIFIED_DOSSIERS)
    dossiers_by_target = {d.target.target_id: d for d in dossiers}

    recall_rows = build_shortlist_recall_rows(
        benchmark_family="unified", results_path=UNIFIED_RESULTS,
        candidate_dossiers_path=UNIFIED_DOSSIERS)
    oracle_by_target = {}
    for rrow in recall_rows:
        if rrow.get("status") == "ok":
            tid = str(rrow["target_id"])
            oracle_by_target[tid] = str(rrow.get("transfer_eligible_global_oracle_bundle_id") or "")

    config = UNIFIED_CONFIG

    # Define ranking functions: (name, key_fn) - key_fn returns sort key (ascending = best)
    def make_rankings():
        return [
            ("prior",       lambda c: (-c.transferability_prior_score, c.bundle_id)),
            ("utility",     lambda c: (-c.utility_score, c.bundle_id)),
            ("cheap_rank",  lambda c: (-c.cheap_rank_score, c.bundle_id)),
            ("fidelity",    lambda c: (-c.phenotype_fidelity_score, c.bundle_id)),
            ("lexical",     lambda c: (-c.lexical_match_score, c.bundle_id)),
            ("n_models",    lambda c: (-c.n_models, c.bundle_id)),
            ("sem_current", lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models, c.bundle_id)),
            ("fid×util",    lambda c: (-(c.phenotype_fidelity_score * c.utility_score), c.bundle_id)),
            ("fid×cheap",   lambda c: (-(c.phenotype_fidelity_score * c.cheap_rank_score), c.bundle_id)),
            ("fid+util",    lambda c: (-(c.phenotype_fidelity_score + c.utility_score), c.bundle_id)),
            ("fid+cheap",   lambda c: (-(c.phenotype_fidelity_score + c.cheap_rank_score), c.bundle_id)),
            ("util+cheap",  lambda c: (-(c.utility_score + c.cheap_rank_score), c.bundle_id)),
            ("fid×prior",   lambda c: (-(c.phenotype_fidelity_score * c.transferability_prior_score), c.bundle_id)),
            ("util×prior",  lambda c: (-(c.utility_score * c.transferability_prior_score), c.bundle_id)),
            ("cheap×prior", lambda c: (-(c.cheap_rank_score * c.transferability_prior_score), c.bundle_id)),
            ("fid+lex+cheap", lambda c: (-(c.phenotype_fidelity_score + c.lexical_match_score + c.cheap_rank_score), c.bundle_id)),
            ("fid²",        lambda c: (-(c.phenotype_fidelity_score ** 2), c.bundle_id)),
            ("sqrt_prior×fid", lambda c: (-(math.sqrt(c.transferability_prior_score) * c.phenotype_fidelity_score), c.bundle_id)),
            ("harmonic_pf", lambda c: (-(2 * c.transferability_prior_score * c.phenotype_fidelity_score / max(c.transferability_prior_score + c.phenotype_fidelity_score, 0.001)), c.bundle_id)),
            ("fid+0.3util+0.3cheap", lambda c: (-(c.phenotype_fidelity_score + 0.3 * c.utility_score + 0.3 * c.cheap_rank_score), c.bundle_id)),
        ]

    # For each must-include target, compute oracle rank on every dimension
    print(f"\n{'TID':6s} {'oracle':35s}", end="")
    ranking_names = [name for name, _ in make_rankings()]
    for name in ranking_names:
        print(f" {name:>12s}", end="")
    print()
    print("-" * (42 + 13 * len(ranking_names)))

    all_track_data = {}  # tid -> {ranking_name: [ranked_ids]}

    for tid in sorted(oracle_by_target.keys()):
        oracle_id = oracle_by_target.get(tid)
        if not oracle_id:
            continue
        dossier = dossiers_by_target.get(tid)
        result_row = results_by_target.get(tid)
        if not dossier or not result_row:
            continue

        gc_lookup_map = _prescreen_gc(result_row)
        target_source = _target_source_for_dossier(dossier, "unified")
        bundle_lookup_map = agent_bundle_lookup(dossier)
        candidate_ids = [
            b.bundle_id for b in dossier.candidates
            if not is_self_like_bundle(dossier.target, b)
            and bundle_has_source_universe_pgs(b, target_source)
        ]
        cards = [
            _build_candidate_card(dossier, bundle_lookup_map[bid],
                                  gc_row=gc_lookup_map.get(bid), config=config,
                                  target_source=target_source)
            for bid in candidate_ids if bid in bundle_lookup_map
        ]

        rankings = make_rankings()
        track_ranks = {}
        track_ids = {}
        for name, key_fn in rankings:
            ranked = sorted(cards, key=key_fn)
            ranked_ids = [c.bundle_id for c in ranked]
            track_ranks[name] = rank_of(oracle_id, ranked_ids)
            track_ids[name] = ranked_ids

        all_track_data[tid] = track_ids

        if tid in MUST_INCLUDE:
            print(f"{tid:6s} {oracle_id:35s}", end="")
            for name in ranking_names:
                r = track_ranks[name]
                marker = "*" if r <= 30 else " "
                print(f" {r:>11d}{marker}", end="")
            print()

    # Find best NEW track for each hard target
    print("\n\n=== Best new ranking per must-include target ===")
    for tid in sorted(MUST_INCLUDE):
        if tid not in all_track_data:
            continue
        oracle_id = oracle_by_target[tid]
        best_name = None
        best_rank = 9999
        for name in ranking_names:
            r = rank_of(oracle_id, all_track_data[tid][name])
            if r < best_rank:
                best_rank = r
                best_name = name
        print(f"  {tid}: best={best_name}(rank={best_rank})")

    # Find which single new track would cover the most must-include targets in top-K
    print("\n=== Coverage: how many must-include oracles in top-K per ranking ===")
    for K in [20, 30, 40, 50, 65]:
        print(f"\n  Top-{K}:")
        coverage = {}
        for name in ranking_names:
            count = 0
            covered = []
            for tid in sorted(MUST_INCLUDE):
                if tid not in all_track_data:
                    continue
                oracle_id = oracle_by_target[tid]
                r = rank_of(oracle_id, all_track_data[tid][name])
                if r <= K:
                    count += 1
                    covered.append(tid)
            coverage[name] = (count, covered)
        for name, (count, covered) in sorted(coverage.items(), key=lambda x: -x[1][0]):
            if count >= 3:
                uncovered = sorted(MUST_INCLUDE - set(covered))
                print(f"    {name:>20s}: {count}/13 covered, miss={uncovered}")

    # Test shortlist with new tracks
    print("\n\n=== Test shortlist recall with new tracks (cap ≤ 100) ===")

    # For each promising new track, add it as track 7 and test
    existing_tracks = ["prior", "sem_current", "n_models"]  # keep 3 existing
    new_track_candidates = ["fid×util", "fid×cheap", "fid+util", "fid+cheap",
                            "util+cheap", "cheap_rank", "utility", "fidelity",
                            "fid+lex+cheap", "fid+0.3util+0.3cheap"]

    # Build GC track from prescreen data
    from experiments.contribution3.transfer.agent import _gc_ranked_cards

    for new_track_name in new_track_candidates:
        for cap in [90, 95, 100, 105]:
            # Build shortlist for each target using: prior(3) + sel(new_track, 50) +
            # same_endpoint(3) + gc(45) + semantic(65) + support(104) + new_track(50)
            total_hit = 0
            must_miss = []
            for tid, track_ids in sorted(all_track_data.items()):
                oracle_id = oracle_by_target.get(tid)
                if not oracle_id:
                    continue
                tracks = [
                    track_ids["prior"][:3],
                    track_ids[new_track_name][:50],  # new selection track
                    [],  # same_endpoint placeholder - use from sem_current
                    track_ids.get("cheap_rank", track_ids["prior"])[:15],  # gc substitute
                    track_ids["sem_current"][:40],
                    track_ids["n_models"][:50],
                    track_ids["fidelity"][:30],  # additional fidelity track
                ]
                sl = _merge_shortlist_tracks(tracks, cap)
                if oracle_id in sl:
                    total_hit += 1
                elif tid in MUST_INCLUDE:
                    must_miss.append(tid)
            g30_ok = 'G30' not in must_miss
            if total_hit >= 72 and g30_ok:
                print(f"  new={new_track_name:>20s} cap={cap}: {total_hit}/80 must_miss={must_miss}")

    # Best approach: use the highest-coverage ranking as a replacement for selection track
    print("\n\n=== Replace selection track with best new ranking ===")
    # Try replacing the selection track with various new rankings
    for sel_name in ["fid×util", "fid×cheap", "fid+util", "fid+cheap",
                     "utility", "cheap_rank", "fidelity", "fid+lex+cheap",
                     "fid+0.3util+0.3cheap", "harmonic_pf", "sqrt_prior×fid"]:
        for p_sz, sel_sz, gc_sz, sem_sz, sup_sz in [
            (3, 50, 45, 65, 104),
            (3, 40, 30, 50, 80),
            (3, 60, 45, 65, 104),
        ]:
            for cap in [90, 95, 100, 105, 110]:
                total_hit = 0
                must_miss = []
                for tid, track_ids in sorted(all_track_data.items()):
                    oracle_id = oracle_by_target.get(tid)
                    if not oracle_id:
                        continue
                    # same_endpoint: top-3 from semantic that are "same-endpoint"
                    # We approximate by using sem_current top entries
                    tracks = [
                        track_ids["prior"][:p_sz],
                        track_ids[sel_name][:sel_sz],
                        [],  # same_endpoint (not easily available here)
                        track_ids["cheap_rank"][:gc_sz],  # gc proxy: use cheap_rank
                        track_ids["sem_current"][:sem_sz],
                        track_ids["n_models"][:sup_sz],
                    ]
                    sl = _merge_shortlist_tracks(tracks, cap)
                    if oracle_id in sl:
                        total_hit += 1
                    elif tid in MUST_INCLUDE:
                        must_miss.append(tid)
                g30_ok = 'G30' not in must_miss
                if total_hit >= 73 and g30_ok:
                    print(f"  sel={sel_name:>20s} p={p_sz} s={sel_sz} g={gc_sz} sm={sem_sz} sp={sup_sz} "
                          f"cap={cap}: {total_hit}/80 must_miss={must_miss}")

    # Also try: use original GC ranking (not cheap_rank proxy)
    print("\n\n=== With proper GC track + new selection track ===")
    # Re-build with proper GC track
    for tid in sorted(all_track_data.keys()):
        dossier = dossiers_by_target.get(tid)
        result_row = results_by_target.get(tid)
        if not dossier or not result_row:
            continue
        gc_lookup_map = _prescreen_gc(result_row)
        target_source = _target_source_for_dossier(dossier, "unified")
        bundle_lookup_map = agent_bundle_lookup(dossier)
        candidate_ids = [
            b.bundle_id for b in dossier.candidates
            if not is_self_like_bundle(dossier.target, b)
            and bundle_has_source_universe_pgs(b, target_source)
        ]
        cards = [
            _build_candidate_card(dossier, bundle_lookup_map[bid],
                                  gc_row=gc_lookup_map.get(bid), config=config,
                                  target_source=target_source)
            for bid in candidate_ids if bid in bundle_lookup_map
        ]
        gc_ranked = [c.bundle_id for c in _gc_ranked_cards(cards)]
        same_endpoint = [c.bundle_id for c in sorted(cards, key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models)) if c.archetype == "same-endpoint disease"][:3]
        all_track_data[tid]["gc_proper"] = gc_ranked
        all_track_data[tid]["same_endpoint"] = same_endpoint

    for sel_name in ["fid×util", "fid×cheap", "fid+util", "fid+cheap",
                     "utility", "fidelity", "fid+lex+cheap",
                     "fid+0.3util+0.3cheap", "harmonic_pf"]:
        for p_sz, sel_sz, gc_sz, sem_sz, sup_sz in [
            (3, 50, 45, 65, 104), (3, 40, 30, 50, 104),
            (5, 50, 45, 65, 104), (3, 60, 50, 65, 104),
        ]:
            for cap in [90, 95, 100, 105, 110]:
                total_hit = 0
                must_miss = []
                for tid, track_ids in sorted(all_track_data.items()):
                    oracle_id = oracle_by_target.get(tid)
                    if not oracle_id:
                        continue
                    tracks = [
                        track_ids["prior"][:p_sz],
                        track_ids[sel_name][:sel_sz],
                        track_ids.get("same_endpoint", []),
                        track_ids["gc_proper"][:gc_sz],
                        track_ids["sem_current"][:sem_sz],
                        track_ids["n_models"][:sup_sz],
                    ]
                    sl = _merge_shortlist_tracks(tracks, cap)
                    if oracle_id in sl:
                        total_hit += 1
                    elif tid in MUST_INCLUDE:
                        must_miss.append(tid)
                g30_ok = 'G30' not in must_miss
                if total_hit >= 73 and g30_ok:
                    print(f"  sel={sel_name:>20s} p={p_sz} s={sel_sz} g={gc_sz} sm={sem_sz} sp={sup_sz} "
                          f"cap={cap}: {total_hit}/80 must_miss={must_miss}")


if __name__ == "__main__":
    main()
