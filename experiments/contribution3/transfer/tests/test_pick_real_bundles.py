"""P5 gate: given the oracle supporting bundle at rank-1, the Pick stage
selects the oracle PGS as primary (or includes it in the frontier).

Uses the 5 debug targets. For each, constructs a synthetic Judge output
with the oracle bundle at rank 1, then calls `_run_pick`. Gate:
`primary_pgs_id` or any frontier entry's `pgs_id` equals the oracle PGS
for at least 4/5 targets.

This isolates the Pick stage from Judge's quality.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from experiments.contribution3.transfer.agent import _run_pick
from experiments.contribution3.transfer.common import (
    load_candidate_dossiers,
    target_dossiers_json,
)
from experiments.contribution3.transfer.harness import BudgetGuard
from experiments.contribution3.transfer.schemas import RankedBundle
from experiments.contribution3.transfer.state import AgentTrace, EvidenceRegistry

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Pick P5 test requires OPENAI_API_KEY (real LLM call).",
)

DEBUG_TARGETS_FILE = (
    Path(__file__).resolve().parents[1] / "scripts" / "debug_targets.json"
)


def _load_debug_targets():
    if not DEBUG_TARGETS_FILE.exists():
        pytest.skip("debug_targets.json not present")
    return json.loads(DEBUG_TARGETS_FILE.read_text())


def _find_oracle_bundle(dossier, oracle_pgs_id: str):
    for b in dossier.candidates:
        if oracle_pgs_id in (b.candidate_pgs_ids or []):
            return b
    return None


def test_pick_selects_oracle_pgs_4_of_5():
    debug = _load_debug_targets()
    dossiers = load_candidate_dossiers(target_dossiers_json("unified"))
    by_id = {d.target.target_id: d for d in dossiers}

    hits = 0
    total = 0
    details: list[str] = []
    for pick in debug:
        target_id = pick.get("target_id")
        oracle_pgs = pick.get("benchmark_top_model_id")
        if not target_id or not oracle_pgs:
            continue
        dossier = by_id.get(target_id)
        if dossier is None:
            continue
        oracle_bundle = _find_oracle_bundle(dossier, oracle_pgs)
        if oracle_bundle is None:
            details.append(f"[P5] {target_id}: oracle_pgs {oracle_pgs} not in any dossier bundle — skipped")
            continue

        total += 1
        bundle_lookup = {b.bundle_id: b for b in dossier.candidates}
        registry = EvidenceRegistry()
        for b in dossier.candidates:
            registry.set_bundle_meta(
                bundle_id=b.bundle_id,
                canonical_label=b.canonical_label,
                aliases=list(b.aliases or []),
                n_models=int(b.n_models or 0),
                efo_ids=list(b.source_efo_ids or []),
                mondo_ids=list(b.source_mondo_ids or []),
            )
        trace = AgentTrace(target_id=target_id, target_label=dossier.target.target_label)
        # Only feed the oracle bundle at rank 1 (isolating Pick).
        top_k = [
            RankedBundle(
                bundle_id=oracle_bundle.bundle_id,
                rank=1,
                confidence="High",
                rationale="synthetic top-1 for P5 test",
                evidence_cited=[],
            )
        ]
        frontier = _run_pick(
            target=dossier.target,
            top_k_bundles=top_k,
            bundle_lookup=bundle_lookup,
            registry=registry,
            budget=BudgetGuard(max_tool_calls=40),
            frontier_budget_per_bundle=8,
            trace=trace,
        )
        picked = (
            {fm.pgs_id for fm in frontier.frontier} if frontier is not None else set()
        )
        hit = oracle_pgs in picked
        hits += int(hit)
        details.append(
            f"[P5] {target_id} oracle={oracle_pgs} primary={frontier.primary_pgs_id if frontier else None} "
            f"frontier={sorted(picked)} hit={hit}"
        )

    for d in details:
        print(d)
    assert total >= 4, f"P5 data shortfall: only {total} targets with oracle in dossier"
    assert hits >= 4, f"P5 FAIL: Pick hit oracle in only {hits}/{total} targets"
