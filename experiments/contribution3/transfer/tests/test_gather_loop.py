"""P3 gate: the Gather ReAct loop populates the EvidenceRegistry.

Uses a mock Scout (fixed 20 bundle probe list) and stubbed tool functions
that return deterministic synthetic raw evidence. No network, no real LLM
unless OPENAI_API_KEY is set.

Gate: after Gather halts, ≥ 15 / 20 bundles have at least one populated
evidence slot (gc, ot, or h2_source) and total tool calls ≤ 25.
"""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from experiments.contribution3.transfer.agent import _run_gather
from experiments.contribution3.transfer.harness import BudgetGuard, ToolDispatcher
from experiments.contribution3.transfer.state import AgentTrace, EvidenceRegistry

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Gather P3 test requires OPENAI_API_KEY (real LLM call for RoundDirective).",
)


def _make_target():
    return SimpleNamespace(
        target_id="T_GATHER",
        target_code="GATHER_TEST",
        target_label="Synthetic Gather Target",
        aliases=["synthetic_target_alias"],
        target_type="binary",
    )


class _StubBundle(SimpleNamespace):
    pass


def _build_bundles(n: int) -> list[_StubBundle]:
    bundles: list[_StubBundle] = []
    for i in range(n):
        bundles.append(
            _StubBundle(
                bundle_id=f"bundle_{i:02d}",
                canonical_label=f"Candidate Trait {i:02d}",
                aliases=[],
                n_models=max(1, 5 + (i % 4)),
                source_efo_ids=[],
                source_mondo_ids=[],
                candidate_pgs_ids=[f"PGS_FAKE_{i:02d}_{j}" for j in range(3)],
                bundle_type="synthetic",
            )
        )
    return bundles


def test_gather_populates_registry_under_budget():
    target = _make_target()
    bundles = _build_bundles(20)
    bundle_lookup = {b.bundle_id: b for b in bundles}
    registry = EvidenceRegistry(stale_rounds=3)
    for b in bundles:
        registry.set_bundle_meta(
            bundle_id=b.bundle_id,
            canonical_label=b.canonical_label,
            aliases=b.aliases,
            n_models=b.n_models,
            efo_ids=[],
            mondo_ids=[],
        )

    budget = BudgetGuard(max_tool_calls=25)
    trace = AgentTrace(target_id=target.target_id, target_label=target.target_label)

    # Stubbed tool functions produce deterministic synthetic raw fields.
    dispatcher = ToolDispatcher(
        bundle_universe={b.bundle_id: b for b in bundles},
        target_label=target.target_label,
        target_aliases=list(target.aliases),
        registry=registry,
        budget=budget,
    )

    def _tool_ot(bundle_id: str, **_kwargs):
        b = bundle_lookup.get(bundle_id)
        if b is None:
            return {"error": "unknown_bundle_id"}
        idx = int(bundle_id.split("_")[-1])
        payload = {
            "target_label": target.target_label,
            "candidate_label": b.canonical_label,
            "shared_targets": [
                {
                    "gene": f"GENE{k}",
                    "target_id": f"ENSG000000{idx:02d}{k}",
                    "source_score": 0.6,
                    "candidate_score": 0.5,
                    "source_datatype_scores": [],
                    "candidate_datatype_scores": [],
                }
                for k in range(max(1, 3 - idx % 3))
            ],
            "ancestors": [],
            "pathways": [],
            "phenotypes": [],
            "therapeutic_areas": [],
        }
        registry.set_ot(bundle_id, payload, round_idx=-1)
        return payload

    dispatcher.register("get_open_targets_overlap", _tool_ot)

    probe_ids = [b.bundle_id for b in bundles]
    _run_gather(
        target=target,
        probe_ids=probe_ids,
        bundle_lookup=bundle_lookup,
        registry=registry,
        dispatcher=dispatcher,
        budget=budget,
        max_rounds=6,
        trace=trace,
    )

    populated = 0
    for bid in probe_ids:
        ev = registry.get(bid)
        if ev is None:
            continue
        if ev.gc is not None or ev.ot is not None or ev.h2_source is not None:
            populated += 1

    print(
        f"[P3] halt_reason={trace.gather_halt_reason} "
        f"tool_calls={trace.gather_tool_calls_consumed} "
        f"populated={populated}/{len(probe_ids)}"
    )
    assert trace.gather_tool_calls_consumed <= 25, "tool-call budget exceeded"
    assert populated >= 15, (
        f"Only {populated}/20 bundles have any evidence; expected ≥15. "
        f"Halt={trace.gather_halt_reason}, calls={trace.gather_tool_calls_consumed}"
    )
    assert trace.gather_halt_reason in {"llm_terminated", "budget_exhausted_before_done"}
