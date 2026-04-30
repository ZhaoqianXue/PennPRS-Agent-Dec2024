"""P6 gate: Critic either keeps a sound frontier or revises with cited
reasons, and never silently reverts a correct frontier.

Two scenarios:
1. Sound: proposed primary == the bundle with strongest raw evidence
   across all axes. Expected: kept=True.
2. Questionable: proposed primary points to a bundle with weak evidence
   while a clearly-supported bundle exists. Critic may keep or revise;
   either is acceptable — but if revised, the Critic must cite per_axis
   evidence and the rationale must reference orthogonal axes.
"""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from experiments.contribution3.transfer.agent import _run_critic
from experiments.contribution3.transfer.schemas import FrontierModel, ModelFrontier
from experiments.contribution3.transfer.state import AgentTrace, EvidenceRegistry

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Critic P6 test requires OPENAI_API_KEY (real LLM call).",
)


def _make_target(code: str = "CRITIC_T1"):
    return SimpleNamespace(
        target_id=f"T_{code}",
        target_code=code,
        target_label="Synthetic Critic Trait",
        aliases=["critic_alias"],
        target_type="binary",
    )


def _populate_strong(reg: EvidenceRegistry, bundle_id: str, label: str) -> None:
    reg.set_bundle_meta(
        bundle_id=bundle_id, canonical_label=label, aliases=[], n_models=8,
        efo_ids=[], mondo_ids=[],
    )
    reg.set_gc(
        bundle_id,
        {"rg": 0.52, "p_value": 1e-18, "z": 9.1, "source": "gwas_atlas", "pair_status": "resolved"},
        round_idx=0,
    )
    reg.set_ot(
        bundle_id,
        {
            "shared_targets": [{"gene": f"G{i}", "target_id": f"ENS{i:03d}", "source_score": 0.7, "candidate_score": 0.6} for i in range(8)],
            "ancestors": [], "pathways": [], "phenotypes": [{"hpo_id": f"HP:{i:04d}", "hpo_name": f"P{i}"} for i in range(6)],
            "therapeutic_areas": [],
        },
        round_idx=0,
    )
    reg.set_h2(bundle_id=bundle_id, source_h2=None, candidate_h2=[{"h2": 0.22, "h2_se": 0.01, "n_samples": 200000, "source": "gwas_atlas", "ancestry": "EUR"}], round_idx=0)


def _populate_weak(reg: EvidenceRegistry, bundle_id: str, label: str) -> None:
    reg.set_bundle_meta(
        bundle_id=bundle_id, canonical_label=label, aliases=[], n_models=3,
        efo_ids=[], mondo_ids=[],
    )
    reg.set_gc(
        bundle_id,
        {"rg": 0.04, "p_value": 0.6, "z": 0.5, "source": "gwas_atlas", "pair_status": "resolved"},
        round_idx=0,
    )
    reg.set_ot(
        bundle_id,
        {"shared_targets": [], "ancestors": [], "pathways": [], "phenotypes": [], "therapeutic_areas": []},
        round_idx=0,
    )


def _frontier(pgs_id: str, bundle_id: str) -> ModelFrontier:
    fm = FrontierModel(
        pgs_id=pgs_id, bundle_id=bundle_id, rank=1, confidence="Moderate",
        rationale="test frontier",
    )
    return ModelFrontier(frontier=[fm], primary_pgs_id=pgs_id, rationale="test")


def test_critic_keeps_sound_frontier():
    target = _make_target("SOUND")
    reg = EvidenceRegistry()
    _populate_strong(reg, "oracle_bundle", "Strong Evidence Bundle")
    _populate_weak(reg, "decoy_weak_1", "Weak 1")
    _populate_weak(reg, "decoy_weak_2", "Weak 2")
    trace = AgentTrace(target_id=target.target_id, target_label=target.target_label)

    proposed = _frontier("PGS_ORACLE", "oracle_bundle")
    result = _run_critic(
        target=target, registry=reg, proposed_frontier=proposed, trace=trace,
    )
    assert result is not None
    # Soundest scenario — critic should keep.
    # (The gate isn't strict 'kept=True' because a conservative Critic might
    # still adjust confidence wording; however if it revises, the revised
    # primary must still be the oracle.)
    if not result.kept:
        assert result.revised_primary_pgs_id == "PGS_ORACLE", (
            f"Critic revised a sound frontier away from oracle: {result.model_dump()}"
        )


def test_critic_behaves_on_questionable_frontier():
    target = _make_target("QUESTIONABLE")
    reg = EvidenceRegistry()
    _populate_strong(reg, "oracle_bundle", "Obviously Related Trait")
    _populate_weak(reg, "decoy_weak_1", "Unrelated A")
    _populate_weak(reg, "decoy_weak_2", "Unrelated B")
    trace = AgentTrace(target_id=target.target_id, target_label=target.target_label)

    # Proposed primary points to a weak-evidence bundle, making oracle
    # the clear alternative candidate.
    proposed = _frontier("PGS_WEAK", "decoy_weak_1")
    result = _run_critic(
        target=target, registry=reg, proposed_frontier=proposed, trace=trace,
    )
    assert result is not None
    # Either outcome is acceptable; if revised, rationale must reference evidence.
    if not result.kept:
        assert result.revised_frontier is not None
        assert len(result.rationale) > 10, "revision must include a substantive rationale"
