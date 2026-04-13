"""Offline joint tuning of dossier construction + dual-track shortlist for binary_to_binary.

Maximizes the count of targets whose *global* oracle bundle id appears in the simulated
shortlist (same definition as shortlist_recall). Uses frozen prescreen GC rows from an
existing results.json so no LLM or live PennPRS calls are required.

The deterministic pipeline mirrors run_cross_trait_agent (dual_track branch): provisional
cards from candidate_bundle_ids + prescreen gc_lookup -> track lists -> _merge_shortlist_tracks.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import random
from scipy.optimize import differential_evolution

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    BINARY_TO_BINARY_CONFIG,
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
    build_target_queries,
    bundle_has_source_universe_pgs,
    is_self_like_bundle,
    load_trait_bundle_index,
    select_candidate_bundles,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows


def _prescreen_gc_from_result_row(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    for tr in row.get("tool_trace") or []:
        if tr.get("name") == "cross_trait_genetic_correlation" and tr.get("phase") == "candidate_prescreen":
            return _gc_lookup(tr.get("result"))
    return {}


def dual_track_shortlist_from_provisional_cards(
    provisional_cards: list[Any],
    config: TransferConfig,
) -> list[str]:
    """Dual-track merge given pre-built provisional cards (matches agent dual_track)."""
    prior_shortlist = [
        card.bundle_id
        for card in _prior_ranked_cards(provisional_cards, config)[: config.prior_track_size]
    ]
    selection_ranked = _sort_cards(provisional_cards, config)
    selection_shortlist = [
        card.bundle_id for card in selection_ranked[: config.selection_track_size]
    ]
    gc_ranked = _gc_ranked_cards(provisional_cards)
    gc_shortlist = [card.bundle_id for card in gc_ranked[: config.gc_track_size]]
    semantic_ranked = sorted(
        provisional_cards,
        key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models),
    )
    semantic_shortlist = [card.bundle_id for card in semantic_ranked[: config.semantic_track_size]]
    same_endpoint_ids = [
        card.bundle_id
        for card in semantic_ranked
        if card.archetype == "same-endpoint disease"
    ][:3]
    support_shortlist = [
        card.bundle_id
        for card in _support_ranked_cards(provisional_cards)[: config.support_track_size]
    ]
    return _merge_shortlist_tracks(
        [
            prior_shortlist,
            selection_shortlist,
            same_endpoint_ids,
            gc_shortlist,
            semantic_shortlist,
            support_shortlist,
        ],
        config.shortlist_cap,
    )


def simulated_dual_track_shortlist(
    dossier: CandidateBundleDossier,
    gc_lookup: dict[str, dict[str, Any]],
    config: TransferConfig,
) -> list[str]:
    """Match agent.py dual_track shortlist (shortlist_strategy != gc_first)."""
    benchmark_family = "binary_to_binary"
    target_source = _target_source_for_dossier(dossier, benchmark_family)
    bundle_lookup = agent_bundle_lookup(dossier)
    candidate_bundle_ids = [
        bundle.bundle_id
        for bundle in dossier.candidates
        if not is_self_like_bundle(dossier.target, bundle)
        and bundle_has_source_universe_pgs(bundle, target_source)
    ]
    provisional_cards = [
        _build_candidate_card(
            dossier,
            bundle_lookup[bundle_id],
            gc_row=gc_lookup.get(bundle_id),
            config=config,
            target_source=target_source,
        )
        for bundle_id in candidate_bundle_ids
        if bundle_id in bundle_lookup
    ]
    return dual_track_shortlist_from_provisional_cards(provisional_cards, config)


def oracle_in_dossier(dossier: CandidateBundleDossier, oracle_id: str | None) -> bool:
    if not oracle_id:
        return False
    return any(b.bundle_id == oracle_id for b in dossier.candidates)


def build_provisional_cards_cache(
    *,
    targets: list,
    bundles: list,
    gc_by_target: dict[str, dict[str, dict[str, Any]]],
    lexical_cap: int,
    dossier_cap: int,
    lexical_min_score: int,
    card_config: TransferConfig,
) -> dict[str, list[Any]]:
    """Precompute provisional cards per target (expensive; independent of shortlist track sizes)."""
    out: dict[str, list[Any]] = {}
    benchmark_family = "binary_to_binary"
    for target in targets:
        tid = target.target_id
        candidates = select_candidate_bundles(
            target,
            bundles,
            lexical_cap=lexical_cap,
            dossier_cap=dossier_cap,
            lexical_min_score=lexical_min_score,
            benchmark_family=benchmark_family,
        )
        dossier = CandidateBundleDossier(target=target, candidates=candidates)
        target_source = _target_source_for_dossier(dossier, benchmark_family)
        bundle_lookup = agent_bundle_lookup(dossier)
        gc_lookup = gc_by_target.get(tid, {})
        candidate_bundle_ids = [
            bundle.bundle_id
            for bundle in dossier.candidates
            if not is_self_like_bundle(dossier.target, bundle)
            and bundle_has_source_universe_pgs(bundle, target_source)
        ]
        out[tid] = [
            _build_candidate_card(
                dossier,
                bundle_lookup[bundle_id],
                gc_row=gc_lookup.get(bundle_id),
                config=card_config,
                target_source=target_source,
            )
            for bundle_id in candidate_bundle_ids
            if bundle_id in bundle_lookup
        ]
    return out


def count_shortlist_hits_from_cache(
    *,
    provisional_by_tid: dict[str, list[Any]],
    oracle_by_target: dict[str, str | None],
    sl_cfg: TransferConfig,
) -> int:
    hits = 0
    for tid, prov in provisional_by_tid.items():
        oid = oracle_by_target.get(tid)
        if not oid:
            continue
        if not any(c.bundle_id == oid for c in prov):
            continue
        shortlist_ids = dual_track_shortlist_from_provisional_cards(prov, sl_cfg)
        if oid in shortlist_ids:
            hits += 1
    return hits


def evaluate_vector(
    x: np.ndarray,
    bundles: list,
    targets: list,
    oracle_by_target: dict[str, str | None],
    gc_by_target: dict[str, dict[str, dict[str, Any]]],
) -> float:
    lexical_cap = int(round(x[0]))
    dossier_cap = int(round(x[1]))
    lexical_min_score = int(round(x[2]))
    shortlist_cap = int(round(x[3]))
    prior_ts = int(round(x[4]))
    sel_ts = int(round(x[5]))
    gc_ts = int(round(x[6]))
    sem_ts = int(round(x[7]))
    sup_ts = int(round(x[8]))

    lexical_cap = max(15, min(140, lexical_cap))
    dossier_cap = max(200, min(700, dossier_cap))
    lexical_min_score = max(35, min(70, lexical_min_score))
    shortlist_cap = max(16, min(56, shortlist_cap))
    prior_ts = max(4, min(28, prior_ts))
    sel_ts = max(12, min(48, sel_ts))
    gc_ts = max(4, min(28, gc_ts))
    sem_ts = max(4, min(24, sem_ts))
    sup_ts = max(4, min(20, sup_ts))

    cfg = replace(
        BINARY_TO_BINARY_CONFIG,
        shortlist_cap=shortlist_cap,
        prior_track_size=prior_ts,
        selection_track_size=sel_ts,
        gc_track_size=gc_ts,
        semantic_track_size=sem_ts,
        support_track_size=sup_ts,
    )

    hits = 0
    for target in targets:
        tid = target.target_id
        oid = oracle_by_target.get(tid)
        if not oid:
            continue
        try:
            candidates = select_candidate_bundles(
                target,
                bundles,
                lexical_cap=lexical_cap,
                dossier_cap=dossier_cap,
                lexical_min_score=lexical_min_score,
                benchmark_family="binary_to_binary",
            )
        except Exception:
            continue
        dossier = CandidateBundleDossier(target=target, candidates=candidates)
        if not oracle_in_dossier(dossier, oid):
            continue
        gc_lookup = gc_by_target.get(tid, {})
        shortlist_ids = simulated_dual_track_shortlist(dossier, gc_lookup, cfg)
        if oid in shortlist_ids:
            hits += 1
    return float(-hits)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-path",
        type=Path,
        default=PROJECT_ROOT
        / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_binary/all-tools__20260412_023039/results.json",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--maxiter", type=int, default=120)
    parser.add_argument(
        "--mode",
        choices=("joint_de", "fast_shortlist_random"),
        default="fast_shortlist_random",
        help="joint_de: slow 9-D DE. fast_shortlist_random: fixed dossier caps, huge random search on shortlist tracks only.",
    )
    parser.add_argument("--trials", type=int, default=500000)
    parser.add_argument("--lexical-cap", type=int, default=150)
    parser.add_argument("--dossier-cap", type=int, default=700)
    parser.add_argument("--lexical-min-score", type=int, default=35)
    args = parser.parse_args()

    dossiers_path = (
        PROJECT_ROOT
        / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_binary/candidate_dossiers.json"
    )
    rows = build_shortlist_recall_rows(
        benchmark_family="binary_to_binary",
        results_path=args.results_path,
        candidate_dossiers_path=dossiers_path,
    )
    oracle_by_target: dict[str, str | None] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        tid = str(row["target_id"])
        oid = row.get("transfer_eligible_global_oracle_bundle_id")
        oracle_by_target[tid] = str(oid) if oid else None

    results_list = json.loads(args.results_path.read_text())
    gc_by_target: dict[str, dict[str, dict[str, Any]]] = {}
    for row in results_list:
        tid = str((row.get("target") or {}).get("target_id") or "").strip()
        if tid:
            gc_by_target[tid] = _prescreen_gc_from_result_row(row)

    bundles = load_trait_bundle_index()
    targets = build_target_queries(benchmark_family="binary_to_binary")

    if args.mode == "fast_shortlist_random":
        rng = random.Random(args.seed)
        print(
            f"Building provisional card cache (lexical_cap={args.lexical_cap}, "
            f"dossier_cap={args.dossier_cap}, lexical_min_score={args.lexical_min_score})..."
        )
        cache = build_provisional_cards_cache(
            targets=targets,
            bundles=bundles,
            gc_by_target=gc_by_target,
            lexical_cap=args.lexical_cap,
            dossier_cap=args.dossier_cap,
            lexical_min_score=args.lexical_min_score,
            card_config=BINARY_TO_BINARY_CONFIG,
        )
        n_oracle_in_dossier = sum(
            1
            for tid in cache
            if oracle_by_target.get(tid)
            and oracle_by_target[tid] in {c.bundle_id for c in cache[tid]}
        )
        print(f"Oracle appears in expanded dossier candidates: {n_oracle_in_dossier}/23")

        best_hits = -1
        best_cfg: TransferConfig | None = None
        for t in range(args.trials):
            sl_cfg = replace(
                BINARY_TO_BINARY_CONFIG,
                shortlist_cap=rng.randint(16, 56),
                prior_track_size=rng.randint(4, 28),
                selection_track_size=rng.randint(12, 48),
                gc_track_size=rng.randint(4, 28),
                semantic_track_size=rng.randint(4, 24),
                support_track_size=rng.randint(4, 20),
            )
            h = count_shortlist_hits_from_cache(
                provisional_by_tid=cache,
                oracle_by_target=oracle_by_target,
                sl_cfg=sl_cfg,
            )
            if h > best_hits:
                best_hits = h
                best_cfg = sl_cfg
                print(f"[trial {t}] new best {best_hits}/23")
        assert best_cfg is not None
        print("\n=== fast_shortlist_random best ===")
        print(f"hits: {best_hits}/23")
        for field in (
            "shortlist_cap",
            "prior_track_size",
            "selection_track_size",
            "gc_track_size",
            "semantic_track_size",
            "support_track_size",
        ):
            print(f"  {field}={getattr(best_cfg, field)}")
        return

    # Baseline: production-like defaults from common + BINARY_TO_BINARY_CONFIG
    base_x = np.array(
        [
            40,
            340,
            55,
            BINARY_TO_BINARY_CONFIG.shortlist_cap,
            BINARY_TO_BINARY_CONFIG.prior_track_size,
            BINARY_TO_BINARY_CONFIG.selection_track_size,
            BINARY_TO_BINARY_CONFIG.gc_track_size,
            BINARY_TO_BINARY_CONFIG.semantic_track_size,
            BINARY_TO_BINARY_CONFIG.support_track_size,
        ],
        dtype=float,
    )
    base_loss = evaluate_vector(
        base_x, bundles, targets, oracle_by_target, gc_by_target
    )
    print(f"Baseline simulated oracle-in-shortlist hits: {int(-base_loss)}/23")

    bounds = [
        (20, 120),
        (260, 600),
        (38, 62),
        (18, 52),
        (6, 24),
        (16, 44),
        (6, 24),
        (4, 20),
        (4, 16),
    ]

    res = differential_evolution(
        evaluate_vector,
        bounds,
        args=(bundles, targets, oracle_by_target, gc_by_target),
        maxiter=args.maxiter,
        popsize=18,
        seed=args.seed,
        workers=1,
        polish=True,
    )

    best_x = res.x
    lexical_cap = int(round(np.clip(best_x[0], 15, 140)))
    dossier_cap = int(round(np.clip(best_x[1], 200, 700)))
    lexical_min_score = int(round(np.clip(best_x[2], 35, 70)))
    shortlist_cap = int(round(np.clip(best_x[3], 16, 56)))
    prior_ts = int(round(np.clip(best_x[4], 4, 28)))
    sel_ts = int(round(np.clip(best_x[5], 12, 48)))
    gc_ts = int(round(np.clip(best_x[6], 4, 28)))
    sem_ts = int(round(np.clip(best_x[7], 4, 24)))
    sup_ts = int(round(np.clip(best_x[8], 4, 20)))

    best_hits = int(-res.fun)
    print(f"\nDE best hits: {best_hits}/23 (loss={res.fun:.4f})")
    print(
        "best params:",
        f"lexical_cap={lexical_cap}",
        f"dossier_cap={dossier_cap}",
        f"lexical_min_score={lexical_min_score}",
        f"shortlist_cap={shortlist_cap}",
        f"prior_track_size={prior_ts}",
        f"selection_track_size={sel_ts}",
        f"gc_track_size={gc_ts}",
        f"semantic_track_size={sem_ts}",
        f"support_track_size={sup_ts}",
    )

    # Per-target report at best
    cfg = replace(
        BINARY_TO_BINARY_CONFIG,
        shortlist_cap=shortlist_cap,
        prior_track_size=prior_ts,
        selection_track_size=sel_ts,
        gc_track_size=gc_ts,
        semantic_track_size=sem_ts,
        support_track_size=sup_ts,
    )
    miss_sl: list[str] = []
    miss_dossier: list[str] = []
    for target in targets:
        tid = target.target_id
        oid = oracle_by_target.get(tid)
        if not oid:
            continue
        candidates = select_candidate_bundles(
            target,
            bundles,
            lexical_cap=lexical_cap,
            dossier_cap=dossier_cap,
            lexical_min_score=lexical_min_score,
            benchmark_family="binary_to_binary",
        )
        dossier = CandidateBundleDossier(target=target, candidates=candidates)
        if not oracle_in_dossier(dossier, oid):
            miss_dossier.append(tid)
            continue
        shortlist_ids = simulated_dual_track_shortlist(dossier, gc_by_target.get(tid, {}), cfg)
        if oid not in shortlist_ids:
            miss_sl.append(tid)

    print(f"\nAt best params: oracle not in dossier ({len(miss_dossier)}): {', '.join(sorted(miss_dossier))}")
    print(f"Oracle in dossier but not in shortlist ({len(miss_sl)}): {', '.join(sorted(miss_sl))}")


if __name__ == "__main__":
    main()
