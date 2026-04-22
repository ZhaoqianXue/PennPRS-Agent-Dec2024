import argparse
import json
from pathlib import Path

import pandas as pd

from experiments.contribution3.transfer import common as transfer_common
from experiments.contribution3.transfer import agent as transfer_agent
from experiments.contribution3.transfer.batch import run_batch
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    DEFAULT_TRANSFER_ABLATION,
    TargetTraitQuery,
    TraitBundle,
)
from experiments.contribution3.transfer.eval import evaluate_end_to_end as eval_mod
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    BundlePosteriorDecision,
    InitialSearchPlan,
    LocalChampionDecision,
    PerToolEvidence,
    PRSModelCandidate,
    ProbeRoundDecision,
    SupportingBundleSelection,
)
from src.server.core.tool_schemas import PGSModelSummary, PublicationMetadata


def _stub_model(model_id: str, trait: str, *, pgs_only_auc: float, full_model_auc: float) -> PGSModelSummary:
    return PGSModelSummary(
        id=model_id,
        trait_reported=trait,
        trait_efo=trait,
        method_name="LDpred2",
        variants_number=100000,
        ancestry_distribution="EUR",
        publication=PublicationMetadata(title="Test", journal="Nature Genetics"),
        date_release="2024-01-01",
        samples_training="n=125000",
        performance_metrics={
            "auc": pgs_only_auc,
            "r2": None,
            "pgs_only_auc": pgs_only_auc,
            "pgs_only_r2": None,
            "full_model_auc": full_model_auc,
            "full_model_r2": None,
            "incremental_auc": None,
            "selected_performance_id": "PPM1",
            "selected_validation_ancestry": "European",
            "record_count": 1,
            "classification_metrics": [],
            "other_metrics": [],
            "effect_sizes": [],
        },
        phenotyping_reported=trait,
        covariates="age; sex; PCs",
        training_development_cohorts=["UKB"],
        validation_sample_size="n=15000",
    )


def _resolution(query: str, system: str) -> dict:
    return {
        "query": query,
        "system": system,
        "best_id": query.replace(" ", "_"),
        "best_label": query,
        "matched_text": query,
        "confidence": "High",
        "alternatives": [],
    }


def test_build_candidate_card_sets_selection_priority_score():
    dossier = CandidateBundleDossier(
        target=TargetTraitQuery(
            target_id="T001",
            target_code="T001",
            target_label="target disease",
            aliases=["target syndrome"],
        ),
        candidates=[],
    )
    bundle = TraitBundle(
        bundle_id="bundle_1",
        canonical_label="adjacent disease",
        bundle_type="binary",
        aliases=["related disease"],
        candidate_pgs_ids=["PGS001"],
        n_models=2,
    )

    card = transfer_agent._build_candidate_card(
        dossier,
        bundle,
        gc_row={
            "target_resolution": _resolution("target disease", "gwas_atlas"),
            "candidate_resolution": _resolution("adjacent disease", "gwas_atlas"),
            "pair_status": "resolved_pair_found",
            "resolution_status": "resolved",
            "pair_evidence_completeness": "complete",
            "lookup_coverage": 1.0,
            "expand_recommendation": "stop",
            "rg": 0.32,
            "p_value": 0.01,
            "confidence": "High",
            "supports": ["Strong GC."],
            "against": [],
            "uncertainties": [],
        },
        h2_row={
            "ancestry": "EUR",
            "target_profile": [{"trait_name": "target disease", "h2_obs": 0.12, "match_score": 99.0}],
            "candidate_profile": [{"trait_name": "adjacent disease", "h2_obs": 0.08, "match_score": 99.0}],
            "target_best_h2": 0.12,
            "candidate_best_h2": 0.08,
            "candidate_signal_capacity": 0.08,
            "shared_signal_ceiling_proxy": 0.08,
            "signal_capacity_score": 0.8,
            "estimate_confidence": "High",
            "ancestry_coverage": ["EUR"],
            "resolution_status": "resolved",
            "confidence_tier": "High",
            "supports": ["Good signal capacity."],
            "against": [],
            "uncertainties": [],
        },
        config=transfer_agent.DEFAULT_CONFIG,
    )

    assert card.selection_priority_score != 0.0


def test_run_cross_trait_agent_uses_vnext_model_first_workflow(monkeypatch):
    bundles = [
        TraitBundle(
            bundle_id="bundle_a",
            canonical_label="same endpoint disease",
            bundle_type="binary",
            aliases=[],
            candidate_pgs_ids=["PGS001"],
            n_models=1,
        ),
        TraitBundle(
            bundle_id="bundle_b",
            canonical_label="mechanistic challenger",
            bundle_type="continuous",
            aliases=[],
            candidate_pgs_ids=["PGS002", "PGS003"],
            n_models=2,
        ),
        TraitBundle(
            bundle_id="bundle_c",
            canonical_label="generic metabolic trait",
            bundle_type="continuous",
            aliases=[],
            candidate_pgs_ids=["PGS010"],
            n_models=1,
        ),
        TraitBundle(
            bundle_id="bundle_d",
            canonical_label="late challenger",
            bundle_type="binary",
            aliases=[],
            candidate_pgs_ids=["PGS004"],
            n_models=1,
        ),
    ]
    dossier = CandidateBundleDossier(
        target=TargetTraitQuery(
            target_id="T001",
            target_code="T001",
            target_label="index target disease",
            aliases=["index target"],
        ),
        candidates=bundles,
    )

    class FakeToolbox:
        def __init__(self):
            self.calls: list[tuple[str, list[str], str]] = []

        def cross_trait_genetic_correlation_llm(self, *args, **kwargs):
            raise AssertionError("vNext workflow must not use LLM GC as the production path.")

        def cross_trait_genetic_correlation(self, target_trait, candidate_bundle_ids, response_format="screening"):
            self.calls.append(("gc", list(candidate_bundle_ids), response_format))
            rows = []
            for bundle_id in candidate_bundle_ids:
                rows.append(
                    {
                        "bundle_id": bundle_id,
                        "canonical_label": bundle_id,
                        "target_resolution": _resolution(target_trait, "gwas_atlas"),
                        "candidate_resolution": _resolution(bundle_id, "gwas_atlas"),
                        "pair_status": "resolved_pair_found",
                        "resolution_status": "resolved",
                        "pair_evidence_completeness": "complete",
                        "lookup_coverage": 1.0,
                        "expand_recommendation": "stop",
                        "rg": 0.35 if bundle_id in {"bundle_b", "bundle_d"} else 0.12,
                        "p_value": 0.01 if bundle_id in {"bundle_b", "bundle_d"} else 0.2,
                        "confidence": "High" if bundle_id in {"bundle_b", "bundle_d"} else "Low",
                        "supports": ["Resolved GC evidence."],
                        "against": [],
                        "uncertainties": [],
                    }
                )
            return {"target_trait": target_trait, "response_format": response_format, "results": rows}

        def cross_trait_heritability(self, target_trait, candidate_bundle_ids, ancestry="EUR", response_format="screening"):
            self.calls.append(("h2", list(candidate_bundle_ids), response_format))
            rows = []
            for bundle_id in candidate_bundle_ids:
                rows.append(
                    {
                        "bundle_id": bundle_id,
                        "canonical_label": bundle_id,
                        "ancestry": ancestry,
                        "target_profile": [{"trait_name": target_trait, "h2_obs": 0.10, "match_score": 99.0}],
                        "candidate_profile": [{"trait_name": bundle_id, "h2_obs": 0.08 if bundle_id == "bundle_b" else 0.03, "match_score": 99.0}],
                        "target_best_h2": 0.10,
                        "candidate_best_h2": 0.08 if bundle_id == "bundle_b" else 0.03,
                        "candidate_signal_capacity": 0.08 if bundle_id == "bundle_b" else 0.03,
                        "shared_signal_ceiling_proxy": 0.08 if bundle_id == "bundle_b" else 0.03,
                        "signal_capacity_score": 0.8 if bundle_id == "bundle_b" else 0.3,
                        "estimate_confidence": "High",
                        "ancestry_coverage": ["EUR"],
                        "resolution_status": "resolved",
                        "confidence_tier": "High",
                        "supports": ["Signal capacity retained."],
                        "against": [],
                        "uncertainties": [],
                    }
                )
            return {"target_trait": target_trait, "ancestry": ancestry, "response_format": response_format, "results": rows}

        def cross_trait_open_targets(self, target_trait, candidate_bundle_ids, response_format="evidence"):
            self.calls.append(("ot", list(candidate_bundle_ids), response_format))
            rows = []
            for bundle_id in candidate_bundle_ids:
                rows.append(
                    {
                        "bundle_id": bundle_id,
                        "canonical_label": bundle_id,
                        "target_resolution": _resolution(target_trait, "open_targets"),
                        "candidate_resolution": _resolution(bundle_id, "open_targets"),
                        "pair_status": "resolved_overlap",
                        "resolution_status": "resolved",
                        "weighted_shared_target_overlap_score": 0.9 if bundle_id == "bundle_b" else 0.4,
                        "shared_target_count": 2 if bundle_id == "bundle_b" else 1,
                        "genetic_overlap_score": 0.8 if bundle_id == "bundle_b" else 0.4,
                        "pathway_overlap_score": 0.6,
                        "phenotype_overlap_score": 0.3,
                        "ontology_overlap_score": 0.2,
                        "genericity_penalty": 0.1,
                        "confidence": "High" if bundle_id == "bundle_b" else "Moderate",
                        "supports": ["Mechanistic verification succeeded."],
                        "against": [],
                        "uncertainties": [],
                    }
                )
            return {"target_trait": target_trait, "response_format": response_format, "results": rows}

    monkeypatch.setattr(
        transfer_agent,
        "_call_search_plan_vnext",
        lambda target_summary, recall_cards, config: InitialSearchPlan(
            hypotheses=[
                {"hypothesis": f"h{i}", "rationale": "probe"} for i in range(6)
            ],
            probe_bundle_ids=["bundle_a", "bundle_b", "bundle_c"],
            rationale="Initial probe.",
        ),
    )
    round_calls = {"count": 0}

    def fake_probe_reflection(**kwargs):
        round_calls["count"] += 1
        if round_calls["count"] == 1:
            return ProbeRoundDecision(
                retain_bundle_ids=["bundle_b", "bundle_a"],
                challenger_bundle_ids=["bundle_d"],
                promote_to_ot_bundle_ids=["bundle_b"],
                stop=False,
                rationale="Keep bundle_b, inspect one challenger.",
            )
        return ProbeRoundDecision(
            retain_bundle_ids=["bundle_b", "bundle_d"],
            challenger_bundle_ids=[],
            promote_to_ot_bundle_ids=["bundle_d"],
            stop=True,
            rationale="Stop after challenger round.",
        )

    monkeypatch.setattr(transfer_agent, "_call_probe_reflection_vnext", fake_probe_reflection)

    def fake_bundle_posterior(**kwargs):
        return BundlePosteriorDecision(
            supporting_bundles=[
                SupportingBundleSelection(
                    bundle_id="bundle_b",
                    canonical_label="mechanistic challenger",
                    rank=1,
                    supports=["Strong GC + OT."],
                    against=[],
                    uncertainties=[],
                    confidence="High",
                    why_continue_or_stop="Continue to model tournament.",
                    tool_evidence=[
                        PerToolEvidence(
                            tool_name="genetic_correlation",
                            supports_selection=True,
                            key_evidence="Strong GC.",
                            confidence="High",
                        )
                    ],
                    utility_score=8.0,
                    transferability_prior_score=0.6,
                    phenotype_fidelity_score=0.8,
                ),
                SupportingBundleSelection(
                    bundle_id="bundle_d",
                    canonical_label="late challenger",
                    rank=2,
                    supports=["Late-round evidence survived."],
                    against=[],
                    uncertainties=[],
                    confidence="Moderate",
                    why_continue_or_stop="Keep one challenger.",
                    tool_evidence=[],
                    utility_score=6.0,
                    transferability_prior_score=0.4,
                    phenotype_fidelity_score=0.7,
                ),
            ],
            confidence="High",
            rationale="Bundle posterior selected two bundles.",
        )

    monkeypatch.setattr(transfer_agent, "_call_bundle_posterior_vnext", fake_bundle_posterior)
    monkeypatch.setattr(
        transfer_agent,
        "_hydrate_models_for_supporting_bundles_vnext",
        lambda dossier, supporting_bundles: (
            {"bundle_b": 2, "bundle_d": 1},
            [
                _stub_model("PGS002", "mechanistic challenger", pgs_only_auc=0.63, full_model_auc=0.69),
                _stub_model("PGS003", "mechanistic challenger", pgs_only_auc=0.67, full_model_auc=0.70),
                _stub_model("PGS004", "late challenger", pgs_only_auc=0.59, full_model_auc=0.62),
            ],
            {"PGS002": "bundle_b", "PGS003": "bundle_b", "PGS004": "bundle_d"},
        ),
    )

    def fake_local(**kwargs):
        supporting_bundle = kwargs["supporting_bundle"]
        if supporting_bundle.bundle_id == "bundle_b":
            return LocalChampionDecision(
                source_bundle_id="bundle_b",
                champions=[
                    PRSModelCandidate(
                        pgs_id="PGS003",
                        source_bundle_id="bundle_b",
                        source_cross_trait="mechanistic challenger",
                        rank=1,
                        selection_rationale="Best local model.",
                        cross_trait_evidence_rationale="Bundle_b won.",
                        model_quality_rationale="Cleaner PRS metrics.",
                        local_champion_rank=1,
                        bundle_rank=1,
                    )
                ],
                confidence="High",
                rationale="Pick PGS003.",
            )
        return LocalChampionDecision(
            source_bundle_id="bundle_d",
            champions=[
                PRSModelCandidate(
                    pgs_id="PGS004",
                    source_bundle_id="bundle_d",
                    source_cross_trait="late challenger",
                    rank=1,
                    selection_rationale="Only local model.",
                    cross_trait_evidence_rationale="Challenger survived.",
                    model_quality_rationale="Only remaining model.",
                    local_champion_rank=1,
                    bundle_rank=2,
                )
            ],
            confidence="Moderate",
            rationale="Pick PGS004.",
        )

    monkeypatch.setattr(transfer_agent, "_call_local_champion_vnext", fake_local)
    monkeypatch.setattr(
        transfer_agent,
        "_call_global_frontier_vnext",
        lambda champion_cards: transfer_agent.GlobalModelFrontierDecision(
            model_frontier=[
                PRSModelCandidate(
                    pgs_id="PGS003",
                    source_bundle_id="bundle_b",
                    source_cross_trait="mechanistic challenger",
                    rank=1,
                    selection_rationale="Global winner.",
                    cross_trait_evidence_rationale="Best bundle.",
                    model_quality_rationale="Best PRS-only signal.",
                    local_champion_rank=1,
                    bundle_rank=1,
                ),
                PRSModelCandidate(
                    pgs_id="PGS004",
                    source_bundle_id="bundle_d",
                    source_cross_trait="late challenger",
                    rank=2,
                    selection_rationale="Runner-up.",
                    cross_trait_evidence_rationale="Fallback challenger.",
                    model_quality_rationale="Reasonable model.",
                    local_champion_rank=1,
                    bundle_rank=2,
                ),
            ],
            primary_model_id="PGS003",
            confidence="High",
            rationale="Final tournament completed.",
        ),
    )

    result = transfer_agent.run_cross_trait_agent(
        dossier,
        condition="all-tools",
        toolbox=FakeToolbox(),
        benchmark_family="unified",
    )

    decision = result["decision"]
    assert decision["best_model_id"] == "PGS003"
    assert decision["best_bundle_id"] == "bundle_b"
    assert [model["pgs_id"] for model in decision["model_frontier"]] == ["PGS003", "PGS004"]
    assert [bundle["bundle_id"] for bundle in decision["supporting_bundles"]] == ["bundle_b", "bundle_d"]
    assert decision["search_trace"]["initial_probe_bundle_ids"] == ["bundle_a", "bundle_b", "bundle_c"]
    assert decision["search_trace"]["ot_verified_bundle_ids"] == ["bundle_b", "bundle_d"]
    assert decision["candidate_pgs_ids"] == ["PGS002", "PGS003", "PGS004"]
    assert decision["frontier_bundle_ids"] == ["bundle_b", "bundle_d"]
    assert decision["outcome"] == "MATCHED"
    assert [entry["name"] for entry in result["tool_trace"] if entry["name"] == "cross_trait_open_targets"] == [
        "cross_trait_open_targets"
    ]
    ot_call = next(entry for entry in result["tool_trace"] if entry["name"] == "cross_trait_open_targets")
    assert ot_call["args"]["candidate_bundle_ids"] == ["bundle_b", "bundle_d"]


def test_fallback_local_champion_prefers_cleaner_pgs_metrics():
    model_cards = [
        {
            "pgs_id": "PGS001",
            "source_bundle_id": "bundle_1",
            "source_cross_trait": "cross trait 1",
            "bundle_rank": 1,
            "method_family": "LDpred-family",
            "pgs_only_auc": 0.66,
            "pgs_only_r2": None,
            "full_model_auc": 0.68,
            "full_model_r2": None,
            "covariate_inflation_flag": False,
            "training_sample_n": 200000,
            "validation_sample_n": 10000,
            "quality_score": 2.1,
        },
        {
            "pgs_id": "PGS002",
            "source_bundle_id": "bundle_1",
            "source_cross_trait": "cross trait 1",
            "bundle_rank": 1,
            "method_family": "clumping-thresholding",
            "pgs_only_auc": 0.60,
            "pgs_only_r2": None,
            "full_model_auc": 0.71,
            "full_model_r2": None,
            "covariate_inflation_flag": True,
            "training_sample_n": 250000,
            "validation_sample_n": 12000,
            "quality_score": 1.2,
        },
    ]

    decision = transfer_agent._fallback_local_champion_vnext("bundle_1", model_cards, max_count=2)

    assert [champion.pgs_id for champion in decision.champions] == ["PGS001", "PGS002"]


def test_hit_at_percent_label_supports_decimal_percentiles():
    assert eval_mod._hit_at_percent_label(0.005) == "top_0_5pct"
    assert eval_mod._hit_at_percent_label(0.01) == "top_1pct"
    assert eval_mod._hit_at_percent_label(0.015) == "top_1_5pct"
    assert eval_mod._hit_at_percent_label(0.025) == "top_2_5pct"


def test_common_paths_support_run_id_and_ablation():
    full_path = transfer_common.condition_results_json(
        "all-tools",
        benchmark_family="unified",
        run_id="run42",
    )
    ablated_path = transfer_common.condition_results_json(
        "all-tools",
        benchmark_family="unified",
        run_id="run42",
        ablation="no_ot_verifier",
    )
    eval_path = transfer_common.evaluation_dir(
        "unified",
        run_id="run42",
        ablation="no_ot_verifier",
    )

    assert "all-tools__run42" in full_path.as_posix()
    assert "/ablation__no_ot_verifier/" in ablated_path.as_posix()
    assert ablated_path.name == "results.json"
    assert eval_path.name == "evaluation__run42"


def test_evaluate_end_to_end_condition_reports_new_metrics_and_stagewise_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setattr(
        eval_mod,
        "load_benchmark_target_selection",
        lambda benchmark_family="unified", selected_only=True: pd.DataFrame(
            [
                {
                    "input_icd": "A01",
                    "input_type": "A",
                    "target_source": "nontarget_pgs",
                    "input_ontology": "thyroid carcinoma",
                    "input_description": "Thyroid cancer",
                    "self_best_auc": None,
                    "selection_reason": "selected",
                    "selected": True,
                },
                {
                    "input_icd": "B01",
                    "input_type": "B",
                    "target_source": "rootcode_main_analysis",
                    "input_ontology": "asthma",
                    "input_description": "Asthma",
                    "self_best_auc": 0.52,
                    "selection_reason": "selected",
                    "selected": True,
                },
            ]
        ),
    )
    monkeypatch.setattr(
        eval_mod,
        "_load_auc_matrix",
        lambda target_source: pd.DataFrame(
            {
                "stub__PGS001": [0.61] if target_source == "rootcode_main_analysis" else [0.61],
                "stub__PGS002": [0.79] if target_source in {"nontarget_pgs", "extend_trait"} else [0.65],
                "stub__PGS003": [0.72] if target_source in {"nontarget_pgs", "extend_trait"} else [0.63],
            },
            index=["A01"] if target_source in {"nontarget_pgs", "extend_trait"} else ["B01"],
        ),
    )
    eval_calls = {}

    def fake_evaluation_dir(benchmark_family="unified", run_id=None, ablation=DEFAULT_TRANSFER_ABLATION):
        eval_calls["benchmark_family"] = benchmark_family
        eval_calls["run_id"] = run_id
        eval_calls["ablation"] = ablation
        return tmp_path / "evaluation"

    monkeypatch.setattr(eval_mod, "evaluation_dir", fake_evaluation_dir)

    results_path = tmp_path / "results.json"
    recommendations_path = tmp_path / "recommendations.json"
    results_path.write_text(
        json.dumps(
            [
                {
                    "target": {"target_id": "A01"},
                    "decision": {
                        "outcome": "MATCHED",
                        "best_bundle_id": "bundle_1",
                        "best_cross_trait": "thyroid carcinoma",
                        "best_model_id": "PGS003",
                        "candidate_pgs_ids": ["PGS002", "PGS003"],
                        "candidate_pgs_ids_union": ["PGS002", "PGS003"],
                        "model_frontier": [{"pgs_id": "PGS003"}],
                        "search_trace": {
                            "probed_bundle_ids": ["bundle_1", "bundle_2"],
                            "supporting_bundle_ids": ["bundle_1"],
                            "local_champion_ids": ["PGS003"],
                            "model_frontier_ids": ["PGS003"],
                            "model_budget_by_bundle": {"bundle_1": 2},
                        },
                        "evidence_state": {
                            "candidate_cards": [
                                {"bundle_id": "bundle_1", "candidate_pgs_ids": ["PGS002", "PGS003"], "phenotype_fidelity_score": 0.92},
                                {"bundle_id": "bundle_2", "candidate_pgs_ids": ["PGS001"], "phenotype_fidelity_score": 0.40},
                            ]
                        },
                    },
                },
                {
                    "target": {"target_id": "B01"},
                    "decision": {
                        "outcome": "NO_MATCH",
                        "best_bundle_id": None,
                        "best_cross_trait": None,
                        "candidate_pgs_ids": [],
                        "search_trace": {
                            "probed_bundle_ids": [],
                            "supporting_bundle_ids": [],
                            "local_champion_ids": [],
                            "model_frontier_ids": [],
                            "model_budget_by_bundle": {},
                        },
                        "evidence_state": {"candidate_cards": []},
                    },
                },
            ]
        )
    )
    recommendations_path.write_text(
        json.dumps(
            [
                {
                    "target": {"target_id": "A01"},
                    "transfer_decision": {"outcome": "MATCHED"},
                    "recommendation": {
                        "decision": {
                            "outcome": "DIRECT_SUB_OPTIMAL",
                            "best_model_id": "PGS003",
                            "confidence": "Moderate",
                            "rationale": "Selected",
                        },
                        "retrieval": {
                            "hydrated_model_count": 2,
                            "universe_matches_candidate_ids": True,
                            "missing_candidate_pgs_ids": [],
                        },
                    },
                },
                {
                    "target": {"target_id": "B01"},
                    "transfer_decision": {"outcome": "NO_MATCH"},
                    "recommendation": None,
                },
            ]
        )
    )

    summary = eval_mod.evaluate_end_to_end_condition(
        condition="all-tools",
        benchmark_family="unified",
        results_path=results_path,
        recommendations_path=recommendations_path,
    )

    assert summary["official_metrics"]["hit_at_percent"]["top_0_5pct"] == 0.0
    assert summary["official_metrics"]["hit_at_percent"]["top_2_5pct"] == 0.0
    assert summary["official_metrics"]["mean_gpr"] == 0.25
    assert summary["stagewise_diagnostics"]["oracle_in_probe_pool"] == 0.5
    assert summary["stagewise_diagnostics"]["oracle_in_supporting_bundles"] == 0.5
    assert summary["stagewise_diagnostics"]["oracle_in_model_frontier"] == 0.0
    assert summary["failure_label_counts"]["model_stage_ranking_error"] == 1
    assert eval_calls == {
        "benchmark_family": "unified",
        "run_id": None,
        "ablation": DEFAULT_TRANSFER_ABLATION,
    }

    detail_df = pd.read_csv(tmp_path / "evaluation" / "all-tools__end_to_end_eval_detail.csv")
    row_a01 = detail_df.loc[detail_df["target_id"] == "A01"].iloc[0]
    assert bool(row_a01["oracle_in_supporting_bundles"]) is True
    assert bool(row_a01["oracle_in_local_champions"]) is False
    assert bool(row_a01["local_champion_conversion"]) is False
    assert row_a01["failure_label"] == "model_stage_ranking_error"


def test_cmd_recommend_prefers_top_level_model_frontier(tmp_path, monkeypatch):
    results_path = tmp_path / "results.json"
    recommendations_path = tmp_path / "recommendations.json"
    results_path.write_text(
        json.dumps(
            [
                {
                    "target": {"target_id": "A01", "target_label": "target disease"},
                    "decision": {
                        "outcome": "MATCHED",
                        "best_cross_trait": "source trait",
                        "best_bundle_id": "bundle_1",
                        "best_model_id": "PGS003",
                        "candidate_pgs_ids": ["PGS002", "PGS003"],
                        "frontier_bundle_ids": ["bundle_1"],
                        "frontier_bundle_weights": {"bundle_1": 1.0},
                        "model_frontier": [{"pgs_id": "PGS003"}, {"pgs_id": "PGS002"}],
                        "search_trace": {"model_budget_by_bundle": {"bundle_1": 2}},
                    },
                }
            ]
        )
    )
    path_calls = {}

    def fake_results_json(
        condition,
        benchmark_family="unified",
        run_id=None,
        ablation=DEFAULT_TRANSFER_ABLATION,
    ):
        path_calls["results"] = {
            "condition": condition,
            "benchmark_family": benchmark_family,
            "run_id": run_id,
            "ablation": ablation,
        }
        return results_path

    def fake_recommendations_json(
        condition,
        benchmark_family="unified",
        run_id=None,
        ablation=DEFAULT_TRANSFER_ABLATION,
    ):
        path_calls["recommendations"] = {
            "condition": condition,
            "benchmark_family": benchmark_family,
            "run_id": run_id,
            "ablation": ablation,
        }
        return recommendations_path

    monkeypatch.setattr(run_batch, "condition_results_json", fake_results_json)
    monkeypatch.setattr(run_batch, "condition_recommendations_json", fake_recommendations_json)

    run_batch.cmd_recommend(
        argparse.Namespace(
            condition="all-tools",
            benchmark_family="unified",
            run_id="run42",
            ablation="no_ot_verifier",
        )
    )

    payload = json.loads(recommendations_path.read_text())
    assert payload[0]["recommendation"]["decision"]["best_model_id"] == "PGS003"
    assert payload[0]["recommendation"]["recommended_model_ids"] == ["PGS003", "PGS002"]
    assert path_calls["results"]["run_id"] == "run42"
    assert path_calls["results"]["ablation"] == "no_ot_verifier"
    assert path_calls["recommendations"]["run_id"] == "run42"
    assert path_calls["recommendations"]["ablation"] == "no_ot_verifier"


def test_cmd_offline_unified_wires_shared_run_id_and_ablation(monkeypatch):
    call_order: list[tuple[str, dict[str, object]]] = []

    def fake_prepare(args):
        call_order.append(
            (
                "prepare",
                {
                    "benchmark_family": args.benchmark_family,
                },
            )
        )

    def fake_run(args):
        call_order.append(
            (
                "run",
                {
                    "condition": args.condition,
                    "benchmark_family": args.benchmark_family,
                    "target_ids": args.target_ids,
                    "run_id": args.run_id,
                    "workers": args.workers,
                    "ablation": args.ablation,
                },
            )
        )

    def fake_recommend(args):
        call_order.append(
            (
                "recommend",
                {
                    "condition": args.condition,
                    "benchmark_family": args.benchmark_family,
                    "run_id": args.run_id,
                    "ablation": args.ablation,
                },
            )
        )

    def fake_evaluate(args):
        call_order.append(
            (
                "evaluate",
                {
                    "condition": args.condition,
                    "benchmark_family": args.benchmark_family,
                    "run_id": args.run_id,
                    "ablation": args.ablation,
                },
            )
        )

    monkeypatch.setattr(run_batch, "cmd_prepare_assets", fake_prepare)
    monkeypatch.setattr(run_batch, "cmd_run", fake_run)
    monkeypatch.setattr(run_batch, "cmd_recommend", fake_recommend)
    monkeypatch.setattr(run_batch, "cmd_evaluate_end_to_end", fake_evaluate)

    run_batch.cmd_offline_unified(
        argparse.Namespace(
            condition="all-tools",
            target_ids="A01,B01",
            run_id="20260421_120000",
            workers=6,
            ablation="no_h2",
            skip_prepare_assets=False,
        )
    )

    assert call_order == [
        ("prepare", {"benchmark_family": "unified"}),
        (
            "run",
            {
                "condition": "all-tools",
                "benchmark_family": "unified",
                "target_ids": "A01,B01",
                "run_id": "20260421_120000",
                "workers": 6,
                "ablation": "no_h2",
            },
        ),
        (
            "recommend",
            {
                "condition": "all-tools",
                "benchmark_family": "unified",
                "run_id": "20260421_120000",
                "ablation": "no_h2",
            },
        ),
        (
            "evaluate",
            {
                "condition": "all-tools",
                "benchmark_family": "unified",
                "run_id": "20260421_120000",
                "ablation": "no_h2",
            },
        ),
    ]
