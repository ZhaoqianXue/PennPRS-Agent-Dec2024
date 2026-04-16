"""Offline simulation for unified 80-target selection quality & shortlist oracle optimization.

Uses frozen candidate_cards + prescreen GC from all-tools__20260413_124729/results.json.

Goals
-----
1. Report per-target oracle vs selected rank gap (selection quality analysis).
2. Find selection weight vector maximizing exact oracle hits (selected == oracle globally).
3. Report shortlist oracle hit achievability (which targets CAN be fixed via reweighting vs
   which need shortlist reconstruction).

Does NOT call any LLM or live tool. All scoring is deterministic.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    UNIFIED_CONFIG,
    TransferConfig,
    _choose_primary_card,
    _bundle_lookup as agent_bundle_lookup,
    _decision_mode_from_cards,
    _default_frontier_ids,
    _normalize_frontier_ids,
    _sort_cards,
)
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    load_candidate_dossiers,
    target_dossiers_json,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows
from experiments.contribution3.transfer.prompts.transfer_prompt import CandidateEvidenceCard

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cards_from_row(row: dict) -> list[CandidateEvidenceCard]:
    decision = row.get("decision") or {}
    raw = (decision.get("evidence_state") or {}).get("candidate_cards") or []
    return [CandidateEvidenceCard.model_validate(c) for c in raw]


def _deterministic_primary(
    dossier: CandidateBundleDossier,
    cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> str | None:
    """Mirror the deterministic frontier + primary selection (no LLM judge/verify)."""
    if not cards:
        return None
    sorted_cards = _sort_cards(cards, config)
    mode = _decision_mode_from_cards(sorted_cards)
    frontier = _default_frontier_ids(sorted_cards, mode)
    normalized = _normalize_frontier_ids(
        dossier=dossier, cards=sorted_cards, candidate_ids=frontier
    )
    by_id = {c.bundle_id: c for c in sorted_cards}
    selected = [by_id[bid] for bid in normalized if bid in by_id]
    if not selected:
        return None
    primary = _choose_primary_card(selected, config)
    return primary.bundle_id if primary else None


def _selection_priority_score_from_fields(
    prior: float,
    utility: float,
    cheap: float,
    fidelity: float,
    n_models: int,
    ot_overlap: float,
    w: tuple[float, ...],
) -> float:
    """Recompute selection_priority_score directly from extracted fields."""
    w_prior, w_util, w_cheap, w_fid, w_sup, w_anti, w_ot_exc = w
    model_support = math.log1p(min(max(n_models, 0), 100))
    score = (
        w_prior * prior
        + w_util * utility
        + w_cheap * cheap
        + w_fid * fidelity
        + w_sup * model_support
    )
    if w_anti > 0 and n_models > 50:
        score -= w_anti * math.log(n_models / 50)
    if w_ot_exc > 0 and ot_overlap > 2.0:
        score += w_ot_exc * (ot_overlap - 2.0)
    return score


# ---------------------------------------------------------------------------
# Pre-extract fields from frozen cards (fast eval)
# ---------------------------------------------------------------------------

def _extract_card_fields(card: CandidateEvidenceCard) -> dict:
    ot_overlap = 0.0
    if card.open_targets is not None:
        ot_overlap = float(card.open_targets.weighted_shared_target_overlap_score or 0)
    return {
        "bundle_id": card.bundle_id,
        "prior": card.transferability_prior_score,
        "utility": card.utility_score,
        "cheap": card.cheap_rank_score,
        "fidelity": card.phenotype_fidelity_score,
        "n_models": card.n_models,
        "ot_overlap": ot_overlap,
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data() -> dict:
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
    oracle_rank_by_target: dict[str, int | None] = {}
    in_shortlist: dict[str, bool] = {}
    in_dossier: dict[str, bool] = {}
    shortlist_best_rank: dict[str, int | None] = {}
    selected_rank: dict[str, int | None] = {}
    selected_id: dict[str, str | None] = {}

    for rrow in recall_rows:
        if rrow.get("status") != "ok":
            continue
        tid = str(rrow["target_id"])
        oracle_by_target[tid] = str(rrow.get("transfer_eligible_global_oracle_bundle_id") or "") or None
        oracle_rank_by_target[tid] = rrow.get("transfer_eligible_global_oracle_rank")
        in_shortlist[tid] = bool(rrow.get("oracle_in_shortlist"))
        in_dossier[tid] = bool(rrow.get("oracle_in_candidate_dossier"))
        shortlist_best_rank[tid] = rrow.get("shortlist_best_rank")
        selected_rank[tid] = rrow.get("selected_bundle_rank")
        selected_id[tid] = str(rrow.get("selected_bundle_id") or "") or None

    return {
        "results": results_by_target,
        "dossiers": dossiers_by_target,
        "oracle": oracle_by_target,
        "oracle_rank": oracle_rank_by_target,
        "in_shortlist": in_shortlist,
        "in_dossier": in_dossier,
        "shortlist_best_rank": shortlist_best_rank,
        "selected_rank": selected_rank,
        "selected_id": selected_id,
    }


# ---------------------------------------------------------------------------
# Build prepared records
# ---------------------------------------------------------------------------

# (tid, dossier, oracle_id, oracle_rank, frozen_cards, card_fields_by_id)
PreparedRecord = tuple[str, CandidateBundleDossier, str, int, list[CandidateEvidenceCard], dict[str, dict]]


def build_prepared(data: dict) -> tuple[list[PreparedRecord], list[str]]:
    """Return records where oracle is in shortlist (can be fixed by reweighting)
    and list of unreachable targets (oracle not in shortlist)."""
    prepared: list[PreparedRecord] = []
    unreachable: list[str] = []

    for tid, row in sorted(data["results"].items()):
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oracle_id = data["oracle"].get(tid)
        oracle_rank = data["oracle_rank"].get(tid)
        dossier = data["dossiers"].get(tid)
        if not oracle_id or oracle_rank is None or dossier is None:
            continue
        cards = _cards_from_row(row)
        card_ids = {c.bundle_id for c in cards}
        if oracle_id not in card_ids:
            unreachable.append(tid)
            continue
        fields_by_id = {c.bundle_id: _extract_card_fields(c) for c in cards}
        prepared.append((tid, dossier, oracle_id, oracle_rank, cards, fields_by_id))

    return prepared, unreachable


# ---------------------------------------------------------------------------
# Fast evaluation with raw field vectors
# ---------------------------------------------------------------------------

def eval_fast(prepared: list[PreparedRecord], w: tuple[float, ...]) -> tuple[int, list[str]]:
    """Count exact oracle hits for weight vector w."""
    hits = []
    for tid, _dossier, oracle_id, _oracle_rank, _cards, fields_by_id in prepared:
        # Score all cards with w
        best_id = max(
            fields_by_id,
            key=lambda bid: _selection_priority_score_from_fields(**{k: v for k, v in fields_by_id[bid].items() if k != "bundle_id"}, w=w),
        )
        if best_id == oracle_id:
            hits.append(tid)
    return len(hits), hits


def eval_full_deterministic(
    prepared: list[PreparedRecord],
    config: TransferConfig,
) -> tuple[int, list[str]]:
    """Full deterministic eval using _deterministic_primary (matches agent exactly)."""
    hits = []
    for tid, dossier, oracle_id, _oracle_rank, cards, _fields in prepared:
        primary = _deterministic_primary(dossier, cards, config)
        if primary == oracle_id:
            hits.append(tid)
    return len(hits), hits


# ---------------------------------------------------------------------------
# Diagnosis: per-target gap analysis
# ---------------------------------------------------------------------------

def diagnose(prepared: list[PreparedRecord], data: dict, config: TransferConfig) -> None:
    current_w = (
        config.w_transferability_prior,
        config.w_selection_utility,
        config.w_selection_cheap_rank,
        config.w_selection_fidelity,
        config.w_selection_model_support,
        config.w_selection_anti_dominance,
        config.w_ot_exceptional,
    )
    print("\n=== Per-target selection quality diagnosis ===")
    print(f"{'TID':<6} {'Oracle':>6} {'Select':>6} {'Gap':>6} {'OracleLabel':<35} {'SelectedLabel':<35} {'OracleInShortlist'}")
    for tid, dossier, oracle_id, oracle_rank, cards, fields_by_id in prepared:
        sel_rank = data["selected_rank"].get(tid)
        sel_id = data["selected_id"].get(tid)
        gap = (sel_rank or 0) - oracle_rank
        oracle_label = next((c.canonical_label for c in cards if c.bundle_id == oracle_id), "?")
        sel_label = next((c.canonical_label for c in cards if c.bundle_id == sel_id), "?") if sel_id else "?"
        is_sl = data["in_shortlist"].get(tid)

        # Find oracle rank in frozen cards by selection score
        oracle_score = _selection_priority_score_from_fields(**{k: v for k, v in fields_by_id[oracle_id].items() if k != "bundle_id"}, w=current_w)
        scores = [(bid, _selection_priority_score_from_fields(**{k: v for k, v in f.items() if k != "bundle_id"}, w=current_w)) for bid, f in fields_by_id.items()]
        scores.sort(key=lambda x: -x[1])
        oracle_rank_in_cards = next((i+1 for i, (bid, _) in enumerate(scores) if bid == oracle_id), None)

        status = "✓" if sel_rank == oracle_rank else f"rank#{oracle_rank_in_cards}inCards"
        print(f"{tid:<6} {oracle_rank:>6} {sel_rank or '?':>6} {gap:>6} {oracle_label[:33]:<35} {sel_label[:33]:<35} {str(is_sl):<5} {status}")


# ---------------------------------------------------------------------------
# Weight optimization
# ---------------------------------------------------------------------------

def optimize_weights(
    prepared: list[PreparedRecord],
    n_trials: int = 300000,
    seed: int = 42,
) -> tuple[tuple[float, ...], int, list[str]]:
    """Use differential_evolution to maximize exact oracle hits."""

    def objective(params: list[float]) -> float:
        w = tuple(max(0, p) for p in params)
        # Don't allow all-zero weights
        if sum(w) < 0.01:
            return 0.0
        hits, _ = eval_fast(prepared, w)
        return -hits  # minimize negative hits

    # Bounds: [w_prior, w_utility, w_cheap, w_fidelity, w_support, w_anti, w_ot_exc]
    bounds = [
        (0.0, 5.0),   # w_prior
        (0.0, 1.0),   # w_utility
        (0.0, 1.0),   # w_cheap
        (0.0, 5.0),   # w_fidelity
        (0.0, 1.0),   # w_support
        (0.0, 1.0),   # w_anti
        (0.0, 2.0),   # w_ot_exc
    ]

    rng = np.random.default_rng(seed)
    result = differential_evolution(
        objective,
        bounds=bounds,
        maxiter=min(n_trials // 15, 5000),
        popsize=15,
        tol=0,
        mutation=(0.5, 1.5),
        recombination=0.9,
        seed=int(rng.integers(0, 2**31)),
        workers=1,
        polish=True,
    )
    best_w = tuple(max(0.0, v) for v in result.x)
    hits, hit_ids = eval_fast(prepared, best_w)
    return best_w, hits, hit_ids


# ---------------------------------------------------------------------------
# Grid search over a curated space
# ---------------------------------------------------------------------------

def grid_search(prepared: list[PreparedRecord]) -> tuple[tuple[float, ...], int, list[str]]:
    """Fast grid search focusing on the key tension dimensions."""
    best_hits = 0
    best_w: tuple[float, ...] = ()
    best_ids: list[str] = []

    # Key insight: tension between w_prior (favors BMI) and w_fidelity (favors disease-specific)
    # Also: w_ot_exceptional (OT-strong bundles, sometimes wrong)
    for w_prior in [0.0, 0.3, 0.6, 1.0, 1.5, 2.0, 3.0]:
        for w_fid in [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
            for w_ot_exc in [0.0, 0.1, 0.2, 0.326, 0.5, 0.8]:
                for w_util in [0.0, 0.003, 0.01, 0.05, 0.1]:
                    for w_anti in [0.0, 0.03, 0.08, 0.15]:
                        w = (w_prior, w_util, 0.005, w_fid, 0.002, w_anti, w_ot_exc)
                        hits, hit_ids = eval_fast(prepared, w)
                        if hits > best_hits:
                            best_hits = hits
                            best_w = w
                            best_ids = hit_ids

    return best_w, best_hits, best_ids


# ---------------------------------------------------------------------------
# Shortlist oracle analysis
# ---------------------------------------------------------------------------

def analyze_shortlist(data: dict) -> None:
    print("\n=== Shortlist oracle analysis ===")
    in_sl = sum(1 for v in data["in_shortlist"].values() if v)
    in_dos = sum(1 for v in data["in_dossier"].values() if v)
    total = len(data["oracle"])
    print(f"Dossier oracle recall: {in_dos}/{total}")
    print(f"Shortlist oracle recall: {in_sl}/{total}")
    print("\nTargets NOT in dossier:")
    for tid in sorted(data["oracle"]):
        if not data["in_dossier"].get(tid):
            print(f"  {tid}: oracle={data['oracle'][tid]}, oracle_rank={data['oracle_rank'][tid]}")
    print("\nTargets in dossier but NOT in shortlist:")
    for tid in sorted(data["oracle"]):
        if data["in_dossier"].get(tid) and not data["in_shortlist"].get(tid):
            print(f"  {tid}: oracle={data['oracle'][tid]}, oracle_rank={data['oracle_rank'][tid]}, shortlist_best={data['shortlist_best_rank'].get(tid)}")
    print("\nTargets in shortlist but wrong selection:")
    exact = 0
    for tid in sorted(data["oracle"]):
        orank = data["oracle_rank"].get(tid)
        srank = data["selected_rank"].get(tid)
        if orank is not None and srank is not None and orank == srank:
            exact += 1
    print(f"Exact oracle hits (selected_rank == oracle_rank): {exact}/{total}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--grid", action="store_true")
    parser.add_argument("--optimize", action="store_true")
    parser.add_argument("--trials", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("Loading data...")
    data = load_data()
    analyze_shortlist(data)

    print("\nBuilding prepared records...")
    prepared, unreachable = build_prepared(data)
    print(f"Prepared: {len(prepared)} (oracle in shortlist), unreachable: {len(unreachable)} (oracle NOT in shortlist)")
    print(f"Unreachable targets: {unreachable}")

    # Baseline with current config
    current_hits, current_hit_ids = eval_full_deterministic(prepared, UNIFIED_CONFIG)
    print(f"\nCurrent UNIFIED_CONFIG: {current_hits}/{len(prepared)} exact oracle hits in reachable set")
    print(f"  (out of 80 total: {current_hits}/80)")
    missing = [tid for tid, *_ in prepared if tid not in current_hit_ids]
    print(f"  Missed: {missing}")

    if args.diagnose:
        diagnose(prepared, data, UNIFIED_CONFIG)

    if args.grid:
        print("\nRunning grid search...")
        best_w, best_hits, best_ids = grid_search(prepared)
        print(f"Grid best: {best_hits}/{len(prepared)} hits")
        print(f"  w = (prior={best_w[0]:.4f}, util={best_w[1]:.4f}, cheap={best_w[2]:.4f}, "
              f"fid={best_w[3]:.4f}, sup={best_w[4]:.4f}, anti={best_w[5]:.4f}, ot_exc={best_w[6]:.4f})")
        missed = [tid for tid, *_ in prepared if tid not in best_ids]
        print(f"  Missed (reachable): {missed}")

    if args.optimize:
        print(f"\nRunning differential evolution ({args.trials} max evals)...")
        best_w, best_hits, best_ids = optimize_weights(prepared, n_trials=args.trials, seed=args.seed)
        print(f"Optimized: {best_hits}/{len(prepared)} exact oracle hits in reachable set")
        print(f"  w_transferability_prior = {best_w[0]:.6f}")
        print(f"  w_selection_utility     = {best_w[1]:.6f}")
        print(f"  w_selection_cheap_rank  = {best_w[2]:.6f}")
        print(f"  w_selection_fidelity    = {best_w[3]:.6f}")
        print(f"  w_selection_model_support = {best_w[4]:.6f}")
        print(f"  w_selection_anti_dominance = {best_w[5]:.6f}")
        print(f"  w_ot_exceptional        = {best_w[6]:.6f}")
        missed = [tid for tid, *_ in prepared if tid not in best_ids]
        print(f"  Missed (reachable): {missed}")


if __name__ == "__main__":
    main()
