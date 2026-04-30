"""P4 gate: Scout LLM includes the oracle bundle for ≥ 3 / 5 debug targets.

Uses the 5 debug dossiers picked by `scripts/pick_debug_targets.py` and
the latest evaluation's `benchmark_top_model_id` to identify the oracle
bundle (the one containing the empirically-best PGS).

The oracle bundle was verified in P4 prep to be present in the dossier
for all 5 targets; the gate therefore tests whether the Scout prompt is
good enough to identify it. Skipped automatically without
OPENAI_API_KEY.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from experiments.contribution3.transfer.agent import _run_scout
from experiments.contribution3.transfer.common import (
    load_candidate_dossiers,
    target_dossiers_json,
)
from experiments.contribution3.transfer.state import AgentTrace

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Scout P4 test requires OPENAI_API_KEY (real LLM call).",
)

DEBUG_TARGETS_FILE = (
    Path(__file__).resolve().parents[1] / "scripts" / "debug_targets.json"
)


def _load_debug_targets():
    if not DEBUG_TARGETS_FILE.exists():
        pytest.skip(f"debug_targets.json not found at {DEBUG_TARGETS_FILE}")
    return json.loads(DEBUG_TARGETS_FILE.read_text())


def _find_oracle_bundle(dossier, oracle_pgs_id: str) -> str | None:
    for b in dossier.candidates:
        if oracle_pgs_id in (b.candidate_pgs_ids or []):
            return b.bundle_id
    return None


def test_scout_includes_oracle_bundle_on_3_of_5():
    debug_targets = _load_debug_targets()
    dossiers = load_candidate_dossiers(target_dossiers_json("unified"))
    by_id = {d.target.target_id: d for d in dossiers}

    results: list[tuple[str, bool, int, bool]] = []
    for pick in debug_targets:
        target_id = pick.get("target_id")
        oracle_pgs = pick.get("benchmark_top_model_id")
        if not target_id or not oracle_pgs:
            continue
        dossier = by_id.get(target_id)
        if dossier is None:
            continue
        oracle_bundle = _find_oracle_bundle(dossier, oracle_pgs)
        if oracle_bundle is None:
            # Oracle PGS truly not in dossier — honest retrieval ceiling case.
            results.append((target_id, False, 0, False))
            continue

        bundle_lookup = {b.bundle_id: b for b in dossier.candidates}
        trace = AgentTrace(target_id=target_id, target_label=dossier.target.target_label)
        directive = _run_scout(
            target=dossier.target,
            bundle_lookup=bundle_lookup,
            trace=trace,
        )
        hit = oracle_bundle in directive.probe_bundle_ids
        results.append(
            (target_id, hit, len(directive.probe_bundle_ids), directive.used_biology_retrieval)
        )
        print(
            f"[P4] {target_id} oracle_bundle={oracle_bundle} "
            f"probe_len={len(directive.probe_bundle_ids)} "
            f"bio={directive.used_biology_retrieval} hit={hit}"
        )

    hits = sum(1 for _, h, _, _ in results if h)
    print(f"[P4 gate] Scout hit oracle in {hits}/{len(results)} debug targets")
    assert hits >= 3, (
        f"P4 FAIL: only {hits}/{len(results)} targets included oracle; "
        f"detail: {results}"
    )
