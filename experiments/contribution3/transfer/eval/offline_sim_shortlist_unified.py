"""Offline shortlist-oracle simulation for the unified 80-target benchmark.

Uses frozen prescreen GC from all-tools__20260413_124729/results.json to simulate
different shortlist track configurations and measure oracle recall improvement.

Does NOT call any LLM or live tool.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
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
    / "all-tools__20260413_124729/results.json"
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


def _dual_track_shortlist(
    dossier: CandidateBundleDossier,
    gc_lookup_map: dict[str, dict[str, Any]],
    config: TransferConfig,
    benchmark_family: str = "unified",
) -> list[str]:
    """Simulate dual_track shortlist from provisional cards (matches agent dual_track)."""
    target_source = _target_source_for_dossier(dossier, benchmark_family)
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
    prior_shortlist = [
        c.bundle_id for c in _prior_ranked_cards(provisional_cards, config)[: config.prior_track_size]
    ]
    selection_ranked = _sort_cards(provisional_cards, config)
    selection_shortlist = [c.bundle_id for c in selection_ranked[: config.selection_track_size]]
    gc_ranked = _gc_ranked_cards(provisional_cards)
    gc_shortlist = [c.bundle_id for c in gc_ranked[: config.gc_track_size]]
    semantic_ranked = sorted(
        provisional_cards,
        key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models),
    )
    semantic_shortlist = [c.bundle_id for c in semantic_ranked[: config.semantic_track_size]]
    same_endpoint_ids = [
        c.bundle_id for c in semantic_ranked if c.archetype == "same-endpoint disease"
    ][:3]
    support_shortlist = [
        c.bundle_id for c in _support_ranked_cards(provisional_cards)[: config.support_track_size]
    ]
    return _merge_shortlist_tracks(
        [prior_shortlist, selection_shortlist, same_endpoint_ids, gc_shortlist, semantic_shortlist, support_shortlist],
        config.shortlist_cap,
    )


def load_simulation_data() -> dict:
    results = json.loads(UNIFIED_RESULTS.read_text())
    results_by_target = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results
        if (r.get("target") or {}).get("target_id")
    }
    dossiers = load_candidate_dossiers(UNIFIED_DOSSIERS)
    dossiers_by_target = {d.target.target_id: d for d in dossiers}

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

    # Extract prescreen GC per target
    prescreen_gc_by_target: dict[str, dict[str, dict[str, Any]]] = {}
    for tid, row in results_by_target.items():
        prescreen_gc_by_target[tid] = _prescreen_gc_from_result_row(row)

    return {
        "results": results_by_target,
        "dossiers": dossiers_by_target,
        "oracle": oracle_by_target,
        "in_dossier": in_dossier,
        "prescreen_gc": prescreen_gc_by_target,
    }


def simulate_shortlist_recall(data: dict, config: TransferConfig) -> tuple[int, int, dict]:
    """Simulate shortlist oracle recall for all targets in dossier."""
    in_shortlist_count = 0
    total_in_dossier = 0
    detail: dict[str, dict] = {}
    for tid, oracle_id in data["oracle"].items():
        if not data["in_dossier"].get(tid):
            continue
        total_in_dossier += 1
        dossier = data["dossiers"].get(tid)
        if dossier is None:
            continue
        gc_lookup_map = data["prescreen_gc"].get(tid, {})
        try:
            shortlist = _dual_track_shortlist(dossier, gc_lookup_map, config)
        except Exception:
            shortlist = []
        in_sl = bool(oracle_id and oracle_id in shortlist)
        if in_sl:
            in_shortlist_count += 1
        detail[tid] = {"oracle_id": oracle_id, "in_shortlist": in_sl, "shortlist_size": len(shortlist)}
    return in_shortlist_count, total_in_dossier, detail


def main() -> None:
    print("Loading simulation data...")
    data = load_simulation_data()
    total_targets = len(data["oracle"])
    total_in_dossier = sum(1 for v in data["in_dossier"].values() if v)
    print(f"Total targets: {total_targets}, in dossier: {total_in_dossier}")

    # Baseline
    base_hits, base_dos, _ = simulate_shortlist_recall(data, UNIFIED_CONFIG)
    print(f"\nBaseline UNIFIED_CONFIG (shortlist_cap={UNIFIED_CONFIG.shortlist_cap}, "
          f"semantic={UNIFIED_CONFIG.semantic_track_size}, selection={UNIFIED_CONFIG.selection_track_size}):")
    print(f"  Shortlist oracle recall: {base_hits}/{base_dos} (of {total_targets})")

    # Test different configurations
    test_configs = [
        (12, 32, 10, 52),   # baseline
        (20, 40, 12, 65),   # wider
        (20, 45, 12, 70),   # wider+
        (25, 50, 12, 75),   # widest
        (18, 38, 10, 60),   # moderate
    ]

    print("\n=== Shortlist oracle recall with different track sizes ===")
    best_hits = 0
    best_cfg_params = None
    for sem, sel, sup, cap in test_configs:
        cfg = replace(
            UNIFIED_CONFIG,
            semantic_track_size=sem,
            selection_track_size=sel,
            support_track_size=sup,
            shortlist_cap=cap,
        )
        hits, dos, detail = simulate_shortlist_recall(data, cfg)
        print(f"  semantic={sem}, selection={sel}, support={sup}, cap={cap}: "
              f"{hits}/{dos} (total {hits}/{total_targets})")
        if hits > best_hits:
            best_hits = hits
            best_cfg_params = (sem, sel, sup, cap)
            best_detail = detail

    print(f"\nBest: semantic={best_cfg_params[0]}, selection={best_cfg_params[1]}, "
          f"support={best_cfg_params[2]}, cap={best_cfg_params[3]}: {best_hits}/{total_in_dossier}")

    # Show which targets moved from unreachable to reachable
    cfg_best = replace(
        UNIFIED_CONFIG,
        semantic_track_size=best_cfg_params[0],
        selection_track_size=best_cfg_params[1],
        support_track_size=best_cfg_params[2],
        shortlist_cap=best_cfg_params[3],
    )
    _, _, base_detail = simulate_shortlist_recall(data, UNIFIED_CONFIG)
    _, _, best_detail_map = simulate_shortlist_recall(data, cfg_best)

    newly_captured = [
        tid for tid, info in best_detail_map.items()
        if info["in_shortlist"] and not base_detail.get(tid, {}).get("in_shortlist")
    ]
    lost = [
        tid for tid, info in base_detail.items()
        if info["in_shortlist"] and not best_detail_map.get(tid, {}).get("in_shortlist")
    ]
    print(f"\nNewly captured oracles: {newly_captured}")
    print(f"Lost oracles: {lost}")

    # Per-target oracle status with best config
    not_in_shortlist = [
        (tid, info["oracle_id"])
        for tid, info in best_detail_map.items()
        if not info["in_shortlist"]
    ]
    print(f"\nStill missing from shortlist with best config: {[t for t, _ in not_in_shortlist]}")


if __name__ == "__main__":
    main()
