"""P2 gate: Judge LLM picks the 'oracle' bundle in hand-built fixtures.

Each fixture builds an EvidenceRegistry with ~6 fake bundles where one
bundle has clearly stronger evidence on the raw axes (significant rg,
shared OT targets, positive h2). The Judge must rank the oracle in the
top 5 for ≥ 4 of 5 fixtures.

This is a trait-agnostic test: none of the fixtures are tied to real
trait names. They use synthetic labels `TargetA`..`TargetE` and
candidate bundle IDs `oracle`, `decoy_gc_weak`, `decoy_ot_strong_wrong_trait`,
etc. The Judge sees only raw evidence shape, so its performance here
reflects prompt quality, not trait-specific lookup.

Skipped automatically if OPENAI_API_KEY is not set.
"""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from experiments.contribution3.transfer.agent import _run_judge
from experiments.contribution3.transfer.harness import BudgetGuard
from experiments.contribution3.transfer.state import AgentTrace, EvidenceRegistry

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Judge test requires OPENAI_API_KEY (real LLM call).",
)


def _make_target(name: str) -> SimpleNamespace:
    return SimpleNamespace(
        target_id=f"T_{name}",
        target_code=name,
        target_label=f"Synthetic Trait {name}",
        aliases=[f"alias_{name}_a", f"alias_{name}_b"],
        target_type="binary",
    )


def _populate(
    reg: EvidenceRegistry,
    bundle_id: str,
    *,
    label: str,
    rg: float | None = None,
    p_value: float | None = None,
    ot_shared: int = 0,
    h2: float | None = None,
    n_models: int = 4,
    note: str | None = None,
) -> None:
    reg.set_bundle_meta(
        bundle_id=bundle_id,
        canonical_label=label,
        aliases=[],
        n_models=n_models,
        efo_ids=[],
        mondo_ids=[],
    )
    if rg is not None:
        reg.set_gc(
            bundle_id,
            {
                "rg": rg,
                "p_value": p_value if p_value is not None else 0.001,
                "z": (rg / 0.05) if rg else 0.0,
                "source": "gwas_atlas",
                "pair_status": "resolved",
                "n_snps": 800000,
            },
            round_idx=0,
        )
    if ot_shared:
        reg.set_ot(
            bundle_id,
            {
                "shared_targets": [
                    {
                        "gene": f"G{i}",
                        "target_id": f"ENSG000000{i:02d}",
                        "source_score": 0.7,
                        "candidate_score": 0.6,
                        "source_datatype_scores": [],
                        "candidate_datatype_scores": [],
                    }
                    for i in range(ot_shared)
                ],
                "ancestors": [],
                "pathways": [],
                "phenotypes": [],
                "therapeutic_areas": [],
            },
            round_idx=0,
        )
    if h2 is not None:
        reg.set_h2(
            bundle_id=bundle_id,
            source_h2=[{"h2": h2, "h2_se": 0.01, "n_samples": 100000, "source": "gwas_atlas", "ancestry": "EUR"}],
            candidate_h2=None,
            round_idx=0,
        )
    if note:
        reg.add_note(bundle_id=bundle_id, round_idx=0, note=note)


# ---------------------------------------------------------------------------
# Five hand-built scenarios. Each one has exactly one `oracle` bundle_id
# where strong raw evidence converges across axes.
# ---------------------------------------------------------------------------

def _fixture_strong_gc_and_ot():
    reg = EvidenceRegistry()
    _populate(reg, "oracle", label="Closely Related", rg=0.58, p_value=2e-12, ot_shared=6, h2=0.18)
    _populate(reg, "decoy_lexical_only", label="Lexical Twin", rg=0.02, p_value=0.7, ot_shared=0, h2=0.05)
    _populate(reg, "decoy_weak_gc", label="Weak Correlate", rg=0.11, p_value=0.2, ot_shared=1, h2=0.02)
    _populate(reg, "decoy_many_models_only", label="Generic Big", rg=None, ot_shared=0, h2=None, n_models=190)
    _populate(reg, "decoy_negative_rg", label="Inverse", rg=-0.05, p_value=0.6, ot_shared=0, h2=0.01)
    return "strong_gc_and_ot", reg, "oracle"


def _fixture_ot_only_signal():
    reg = EvidenceRegistry()
    _populate(reg, "oracle", label="Shared Targets", rg=None, ot_shared=12, h2=0.10)
    _populate(reg, "decoy_empty", label="Empty", rg=None, ot_shared=0, h2=None)
    _populate(reg, "decoy_weak_only", label="Weak OT", rg=None, ot_shared=1, h2=0.04)
    _populate(reg, "decoy_big_generic", label="Generic Large", rg=None, ot_shared=0, h2=None, n_models=150)
    _populate(reg, "decoy_tiny", label="Tiny", rg=None, ot_shared=0, h2=None, n_models=2)
    return "ot_only_signal", reg, "oracle"


def _fixture_gc_strong_p():
    reg = EvidenceRegistry()
    _populate(reg, "oracle", label="Genetic Partner", rg=0.42, p_value=1e-20, ot_shared=2, h2=0.16)
    _populate(reg, "decoy_weak_gc_high_p", label="Low Power", rg=0.50, p_value=0.3, ot_shared=0, h2=0.05)
    _populate(reg, "decoy_no_gc", label="No Overlap", rg=None, ot_shared=1, h2=0.03)
    _populate(reg, "decoy_marginal", label="Marginal", rg=0.12, p_value=0.04, ot_shared=0, h2=0.01)
    _populate(reg, "decoy_null", label="Null", rg=0.01, p_value=0.9, ot_shared=0, h2=None)
    return "gc_strong_p", reg, "oracle"


def _fixture_convergent_evidence():
    reg = EvidenceRegistry()
    _populate(reg, "oracle", label="Multi-Axis Match", rg=0.35, p_value=1e-8, ot_shared=4, h2=0.20, note="matches target on two mechanistic pathways")
    _populate(reg, "decoy_one_axis_only", label="Single-Axis", rg=0.34, p_value=5e-5, ot_shared=0, h2=None)
    _populate(reg, "decoy_unrelated_big", label="Big Unrelated", rg=None, ot_shared=0, h2=None, n_models=210)
    _populate(reg, "decoy_ambiguous", label="Ambiguous", rg=0.20, p_value=0.02, ot_shared=1, h2=0.08)
    _populate(reg, "decoy_weak_all", label="Weak All", rg=0.05, p_value=0.4, ot_shared=0, h2=0.02)
    return "convergent_evidence", reg, "oracle"


def _fixture_noisy_decoys():
    reg = EvidenceRegistry()
    _populate(reg, "oracle", label="Target Partner", rg=0.31, p_value=3e-7, ot_shared=5, h2=0.14)
    _populate(reg, "decoy_lexical_similar", label="Partner-Like Word", rg=0.02, p_value=0.8, ot_shared=0, h2=None)
    _populate(reg, "decoy_high_h2_only", label="High h2 Unrelated", rg=None, ot_shared=0, h2=0.55, n_models=80)
    _populate(reg, "decoy_many_ot_wrong", label="Promiscuous OT", rg=-0.01, p_value=0.9, ot_shared=9, h2=None,
              note="OT overlap here is mostly non-specific hub genes")
    _populate(reg, "decoy_medium", label="Medium Bundle", rg=0.12, p_value=0.08, ot_shared=1, h2=0.06)
    return "noisy_decoys", reg, "oracle"


ALL_FIXTURES = [
    _fixture_strong_gc_and_ot,
    _fixture_ot_only_signal,
    _fixture_gc_strong_p,
    _fixture_convergent_evidence,
    _fixture_noisy_decoys,
]


@pytest.mark.parametrize("builder", ALL_FIXTURES)
def test_judge_ranks_oracle_in_top5(builder):
    name, registry, oracle_id = builder()
    target = _make_target(name)
    trace = AgentTrace(target_id=target.target_id, target_label=target.target_label)
    ranking = _run_judge(
        target=target,
        registry=registry,
        budget=BudgetGuard(max_tool_calls=0),
        trace=trace,
    )
    assert ranking.ranked_bundles, f"[{name}] Judge returned empty ranking"
    top5 = [rb.bundle_id for rb in ranking.ranked_bundles[:5]]
    assert oracle_id in top5, f"[{name}] oracle '{oracle_id}' missing from top-5: {top5}"


def test_judge_overall_gate():
    """Aggregate gate: oracle in top-5 for ≥ 4 / 5 fixtures."""
    hits = 0
    details: list[str] = []
    for builder in ALL_FIXTURES:
        name, registry, oracle_id = builder()
        target = _make_target(name)
        trace = AgentTrace(target_id=target.target_id, target_label=target.target_label)
        ranking = _run_judge(
            target=target,
            registry=registry,
            budget=BudgetGuard(max_tool_calls=0),
            trace=trace,
        )
        top5 = [rb.bundle_id for rb in ranking.ranked_bundles[:5]]
        ok = oracle_id in top5
        hits += int(ok)
        details.append(f"  [{name}] oracle={oracle_id} top5={top5} hit={ok}")
    msg = "\n".join(details)
    assert hits >= 4, f"Judge P2 gate FAILED: only {hits}/5 fixtures hit oracle in top-5\n{msg}"
