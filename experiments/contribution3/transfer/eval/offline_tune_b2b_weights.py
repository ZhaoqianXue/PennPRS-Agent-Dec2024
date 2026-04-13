"""Offline weight search for BINARY_TO_BINARY_CONFIG against frozen evidence cards.

Maximizes exact matches to the *global* transfer-eligible oracle bundle (same definition
as shortlist_recall). Does not call any LLM or online tools.

Hard ceiling: if the oracle bundle is not present in candidate_cards for a target, that
target can never be matched by reweighting selection scores alone.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    BINARY_TO_BINARY_CONFIG,
    TransferConfig,
    _choose_primary_card,
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


def _cards_from_result_row(row: dict) -> list[CandidateEvidenceCard]:
    decision = row.get("decision") or {}
    raw = (decision.get("evidence_state") or {}).get("candidate_cards") or []
    return [CandidateEvidenceCard.model_validate(c) for c in raw]


def deterministic_primary_bundle_id(
    dossier: CandidateBundleDossier,
    cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> str | None:
    """Mirror the deterministic frontier + primary choice (no LLM judge/verify)."""
    if not cards:
        return None
    sorted_cards = _sort_cards(cards, config)
    mode = _decision_mode_from_cards(sorted_cards)
    frontier = _default_frontier_ids(sorted_cards, mode)
    normalized = _normalize_frontier_ids(
        dossier=dossier,
        cards=sorted_cards,
        candidate_ids=frontier,
    )
    by_id = {c.bundle_id: c for c in sorted_cards}
    selected = [by_id[bid] for bid in normalized if bid in by_id]
    if not selected:
        return None
    primary = _choose_primary_card(selected, config)
    return primary.bundle_id if primary else None


def evaluate_config(
    *,
    prepared: list[tuple[str, CandidateBundleDossier, list[CandidateEvidenceCard], str]],
    config: TransferConfig,
) -> tuple[int, list[str]]:
    hits: list[str] = []
    for tid, dossier, cards, oracle_id in prepared:
        primary = deterministic_primary_bundle_id(dossier, cards, config)
        if primary == oracle_id:
            hits.append(tid)
    return len(hits), hits


def build_prepared(
    results_by_target: dict[str, dict],
    dossiers_by_target: dict[str, CandidateBundleDossier],
    oracle_by_target: dict[str, str | None],
) -> list[tuple[str, CandidateBundleDossier, list[CandidateEvidenceCard], str]]:
    """One entry per target where global oracle appears in frozen candidate cards."""
    out: list[tuple[str, CandidateBundleDossier, list[CandidateEvidenceCard], str]] = []
    for tid, row in sorted(results_by_target.items()):
        if (row.get("decision") or {}).get("outcome") != "MATCHED":
            continue
        oid = oracle_by_target.get(tid)
        dossier = dossiers_by_target.get(tid)
        if not oid or dossier is None:
            continue
        cards = _cards_from_result_row(row)
        if oid not in {c.bundle_id for c in cards}:
            continue
        out.append((tid, dossier, cards, oid))
    return out


def random_config(rng: random.Random) -> TransferConfig:
    return replace(
        BINARY_TO_BINARY_CONFIG,
        w_transferability_prior=10 ** rng.uniform(-2.0, 0.7),
        w_selection_utility=10 ** rng.uniform(-3.0, -0.3),
        w_selection_cheap_rank=rng.uniform(0.01, 0.12),
        w_selection_fidelity=rng.uniform(0.02, 0.14),
        w_selection_model_support=rng.uniform(0.0005, 0.02),
        w_selection_anti_dominance=rng.uniform(0.0, 0.12),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-path",
        type=Path,
        default=PROJECT_ROOT
        / "experiments/contribution3/transfer/runs/tool_calling_agent/binary_to_binary/all-tools__20260412_023039/results.json",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trials", type=int, default=40000)
    args = parser.parse_args()

    results = json.loads(args.results_path.read_text())
    results_by_target = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results
        if (r.get("target") or {}).get("target_id")
    }

    dossiers_path = target_dossiers_json("binary_to_binary")
    dossiers = load_candidate_dossiers(dossiers_path)
    dossiers_by_target = {d.target.target_id: d for d in dossiers}

    rows = build_shortlist_recall_rows(
        benchmark_family="binary_to_binary",
        results_path=args.results_path,
        candidate_dossiers_path=dossiers_path,
    )
    oracle_by_target: dict[str, str | None] = {}
    in_shortlist: dict[str, bool] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        tid = str(row["target_id"])
        oracle_by_target[tid] = str(row.get("transfer_eligible_global_oracle_bundle_id") or "") or None
        in_shortlist[tid] = bool(row.get("oracle_in_shortlist"))

    achievable = [tid for tid, ins in in_shortlist.items() if ins]
    impossible = [tid for tid in oracle_by_target if oracle_by_target[tid] and not in_shortlist.get(tid)]

    print("=== Offline oracle feasibility (frozen shortlist from results.json) ===")
    print(f"results: {args.results_path}")
    print(f"targets with global oracle IN shortlist (achievable upper bound): {len(achievable)}/23")
    print(f"targets where oracle NOT in shortlist (impossible by reweighting): {len(impossible)}/23")
    print(f"impossible target_ids: {', '.join(impossible)}")

    prepared = build_prepared(results_by_target, dossiers_by_target, oracle_by_target)
    print(f"prepared targets (oracle in candidate_cards): {len(prepared)}/23")

    base = BINARY_TO_BINARY_CONFIG
    n0, hits0 = evaluate_config(prepared=prepared, config=base)
    print(f"\nBaseline BINARY_TO_BINARY_CONFIG exact oracle hits: {n0}/23 (among all targets)")
    print(f"  matched: {', '.join(hits0)}")

    rng = random.Random(args.seed)
    best_n = n0
    best_cfg = base
    best_hits = hits0

    for t in range(args.trials):
        cfg = random_config(rng)
        n, hits = evaluate_config(prepared=prepared, config=cfg)
        if n > best_n:
            best_n, best_cfg, best_hits = n, cfg, hits
            print(f"[trial {t}] new best {best_n}/23: {', '.join(best_hits)}")

    print("\n=== Best found ===")
    print(
        f"exact_hits: {best_n}/23 "
        f"(subset: {best_n}/{len(prepared)} among targets where oracle is in cards; "
        f"hard ceiling {len(prepared)}/23)"
    )
    print(f"matched: {', '.join(best_hits)}")
    print("TransferConfig fields:")
    for field in (
        "w_transferability_prior",
        "w_selection_utility",
        "w_selection_cheap_rank",
        "w_selection_fidelity",
        "w_selection_model_support",
        "w_selection_anti_dominance",
    ):
        print(f"  {field}={getattr(best_cfg, field)}")


if __name__ == "__main__":
    main()
