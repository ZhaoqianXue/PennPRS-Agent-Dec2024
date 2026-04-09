import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from experiments.contribution3.transfer import agent as transfer_agent
from experiments.contribution3.transfer.common import (
    TraitBundle,
    CandidateBundleDossier,
    TargetTraitQuery,
    build_candidate_dossiers,
    build_target_queries,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    CandidateEvidenceCard,
    EvidenceState,
    JudgeFrontierSelection,
)
from experiments.contribution3.transfer.tools import CrossTraitToolbox
from src.server.core.tool_schemas import (
    DomainKnowledgeResult,
    PGSModelSummary,
    PublicationMetadata,
)
from src.server.modules.disease.recommendation_agent import Step1Decision


def _write_target_selection_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def _stub_model(model_id: str, trait: str) -> PGSModelSummary:
    return PGSModelSummary(
        id=model_id,
        trait_reported=trait,
        trait_efo=trait,
        method_name="LDpred2",
        variants_number=100,
        ancestry_distribution="EUR",
        publication=PublicationMetadata(title="Test", journal="Test Journal"),
        date_release="2020-01-01",
        samples_training="n=1000",
        performance_metrics={
            "auc": 0.61,
            "r2": None,
            "pgs_only_auc": 0.61,
            "pgs_only_r2": None,
            "full_model_auc": 0.68,
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
        covariates="age; sex",
        training_development_cohorts=["UKB"],
        validation_sample_size="n=500",
    )


def test_build_target_queries_reads_selected_targets_from_benchmark_family(tmp_path, monkeypatch):
    selection_path = tmp_path / "binary_to_binary" / "target_selection.csv"
    _write_target_selection_csv(
        selection_path,
        [
            {
                "input_icd": "A01",
                "input_ontology": "thyroid carcinoma",
                "input_description": "Thyroid cancer",
                "selected": True,
            },
            {
                "input_icd": "A02",
                "input_ontology": "",
                "input_description": "Unselected target",
                "selected": False,
            },
        ],
    )
    monkeypatch.setattr(
        "experiments.contribution3.transfer.common.benchmark_target_selection_csv",
        lambda benchmark_family="binary_to_binary": selection_path,
    )

    queries = build_target_queries(benchmark_family="binary_to_binary")

    assert len(queries) == 1
    assert queries[0].target_id == "A01"
    assert queries[0].target_label == "thyroid carcinoma"
    assert "Thyroid cancer" in queries[0].aliases


def test_build_candidate_dossiers_returns_non_empty_candidates(tmp_path, monkeypatch):
    selection_path = tmp_path / "binary_to_binary" / "target_selection.csv"
    _write_target_selection_csv(
        selection_path,
        [
            {
                "input_icd": "A01",
                "input_ontology": "thyroid carcinoma",
                "input_description": "Thyroid cancer",
                "selected": True,
            }
        ],
    )
    monkeypatch.setattr(
        "experiments.contribution3.transfer.common.benchmark_target_selection_csv",
        lambda benchmark_family="binary_to_binary": selection_path,
    )
    monkeypatch.setattr(
        "experiments.contribution3.transfer.common._resolve_overlap_bundles",
        lambda target, bundles: set(),
    )
    monkeypatch.setattr(
        "experiments.contribution3.transfer.common._resolve_gc_bundles",
        lambda target, bundles: set(),
    )

    bundles = [
        TraitBundle(
            bundle_id="efo_1",
            canonical_label="thyroid carcinoma",
            bundle_type="binary",
            aliases=["thyroid cancer"],
            candidate_pgs_ids=["PGS001"],
            n_models=1,
            source_efo_ids=["EFO_1"],
            source_mondo_ids=[],
        ),
        TraitBundle(
            bundle_id="efo_2",
            canonical_label="asthma",
            bundle_type="binary",
            aliases=["asthma"],
            candidate_pgs_ids=["PGS002"],
            n_models=1,
            source_efo_ids=["EFO_2"],
            source_mondo_ids=[],
        ),
    ]

    dossiers = build_candidate_dossiers(bundles, benchmark_family="binary_to_binary")

    assert len(dossiers) == 1
    assert len(dossiers[0].candidates) >= 1
    assert "efo_1" not in [candidate.bundle_id for candidate in dossiers[0].candidates]


def test_recommend_best_model_for_cross_trait_uses_exact_candidate_universe(monkeypatch):
    from experiments.contribution3.transfer import contribution2_adapter as adapter

    monkeypatch.setattr(
        adapter,
        "PGSCatalogClient",
        lambda: object(),
    )
    monkeypatch.setattr(
        adapter,
        "hydrate_pgs_model_summaries",
        lambda client, pgs_ids: [
            _stub_model("PGS002", "matched trait"),
            _stub_model("PGS001", "matched trait"),
        ],
    )
    monkeypatch.setattr(
        adapter,
        "prs_model_domain_knowledge",
        lambda query: DomainKnowledgeResult(
            query=query,
            full_document="domain knowledge",
            snippets=[],
            source_type="local",
        ),
    )
    monkeypatch.setattr(adapter, "_build_step1_chain", lambda: object())

    def fake_invoke(chain, context_payload, pgs_result):
        assert context_payload["target_trait"] == "matched trait"
        assert context_payload["original_target_trait"] == "original disease"
        assert [model.id for model in pgs_result.models] == ["PGS002", "PGS001"]
        return (
            Step1Decision(
                outcome="DIRECT_SUB_OPTIMAL",
                best_model_id="PGS001",
                confidence="Moderate",
                rationale="Selected from explicit whitelist",
            ),
            None,
        )

    monkeypatch.setattr(adapter, "_invoke_step1_chain", fake_invoke)

    result = adapter.recommend_best_model_for_cross_trait(
        original_target_trait="original disease",
        matched_cross_trait="matched trait",
        matched_bundle_id="bundle_1",
        candidate_pgs_ids=["PGS002", "PGS001", "PGS002"],
    )

    assert result["candidate_pgs_ids"] == ["PGS002", "PGS001"]
    assert result["retrieval"]["hydrated_model_ids"] == ["PGS002", "PGS001"]
    assert result["retrieval"]["universe_matches_candidate_ids"] is True
    assert result["decision"]["best_model_id"] == "PGS001"


def test_recommend_best_model_for_cross_trait_accepts_frontier_context(monkeypatch):
    from experiments.contribution3.transfer import contribution2_adapter as adapter

    monkeypatch.setattr(adapter, "PGSCatalogClient", lambda: object())
    monkeypatch.setattr(
        adapter,
        "hydrate_pgs_model_summaries",
        lambda client, pgs_ids: [_stub_model(model_id, "matched trait") for model_id in pgs_ids],
    )
    monkeypatch.setattr(
        adapter,
        "prs_model_domain_knowledge",
        lambda query: DomainKnowledgeResult(
            query=query,
            full_document="domain knowledge",
            snippets=[],
            source_type="local",
        ),
    )
    monkeypatch.setattr(adapter, "_build_step1_chain", lambda: object())

    captured: dict[str, object] = {}

    def fake_invoke(chain, context_payload, pgs_result):
        captured["context_payload"] = context_payload
        captured["model_ids"] = [model.id for model in pgs_result.models]
        return (
            Step1Decision(
                outcome="DIRECT_HIGH_QUALITY",
                best_model_id="PGS002",
                confidence="High",
                rationale="Weighted frontier kept the stronger model.",
            ),
            None,
        )

    monkeypatch.setattr(adapter, "_invoke_step1_chain", fake_invoke)

    result = adapter.recommend_best_model_for_cross_trait(
        original_target_trait="target disease",
        matched_cross_trait="matched trait",
        matched_bundle_id="bundle_primary",
        frontier_bundle_ids=["bundle_primary", "bundle_secondary"],
        frontier_bundle_weights={"bundle_primary": 0.7, "bundle_secondary": 0.3},
        candidate_pgs_ids_union=["PGS002", "PGS001", "PGS002"],
        bundle_evidence_tags={
            "bundle_primary": ["strong_gc", "ot_overlap"],
            "bundle_secondary": ["endophenotype_trait"],
        },
        evidence_state={"shortlist_bundle_ids": ["bundle_primary", "bundle_secondary"]},
    )

    context_payload = captured["context_payload"]
    assert context_payload["candidate_retrieval_mode"] == "weighted_frontier_candidate_pgs_ids"
    assert context_payload["frontier_bundle_ids"] == ["bundle_primary", "bundle_secondary"]
    assert context_payload["bundle_weights"]["bundle_primary"] == pytest.approx(0.7)
    assert context_payload["bundle_evidence_tags"]["bundle_secondary"] == ["endophenotype_trait"]
    assert context_payload["transfer_evidence_state"]["shortlist_bundle_ids"] == [
        "bundle_primary",
        "bundle_secondary",
    ]
    assert captured["model_ids"] == ["PGS002", "PGS001"]
    assert result["retrieval"]["frontier_bundle_count"] == 2
    assert result["frontier_bundle_weights"]["bundle_secondary"] == pytest.approx(0.3)
    assert result["decision"]["best_model_id"] == "PGS002"


def test_general_trait_archetype_classifier_only_penalizes_proxy():
    dossier = CandidateBundleDossier(
        target=TargetTraitQuery(
            target_id="J45",
            target_code="J45",
            target_label="asthma",
            aliases=["asthma disease"],
        ),
        candidates=[],
    )
    proxy_bundle = TraitBundle(
        bundle_id="proxy",
        canonical_label="family history of asthma",
        bundle_type="binary",
        aliases=[],
        candidate_pgs_ids=["PGS900"],
        n_models=1,
    )
    composite_bundle = TraitBundle(
        bundle_id="composite",
        canonical_label="metabolic syndrome",
        bundle_type="binary",
        aliases=[],
        candidate_pgs_ids=["PGS901"],
        n_models=1,
    )
    endophenotype_bundle = TraitBundle(
        bundle_id="endo",
        canonical_label="FEV1/FVC ratio",
        bundle_type="continuous",
        aliases=["lung function ratio"],
        candidate_pgs_ids=["PGS902"],
        n_models=1,
    )

    proxy_type = transfer_agent._candidate_archetype(dossier, proxy_bundle)
    composite_type = transfer_agent._candidate_archetype(dossier, composite_bundle)
    endo_type = transfer_agent._candidate_archetype(dossier, endophenotype_bundle)

    assert proxy_type == "administrative/exposure/treatment/family-history proxy"
    assert composite_type == "composite liability trait"
    assert endo_type == "mechanistic endophenotype / organ-function measurement"
    assert transfer_agent._phenotype_fidelity_score(dossier, proxy_bundle, proxy_type) < (
        transfer_agent._phenotype_fidelity_score(dossier, composite_bundle, composite_type)
    )
    assert transfer_agent._phenotype_fidelity_score(dossier, proxy_bundle, proxy_type) < (
        transfer_agent._phenotype_fidelity_score(dossier, endophenotype_bundle, endo_type)
    )


def test_finalize_frontier_decision_builds_weighted_union_candidate_universe():
    dossier = CandidateBundleDossier(
        target=TargetTraitQuery(
            target_id="E11",
            target_code="E11",
            target_label="type 2 diabetes",
            aliases=["T2D"],
        ),
        candidates=[
            TraitBundle(
                bundle_id="bundle_primary",
                canonical_label="metabolic syndrome",
                bundle_type="binary",
                aliases=[],
                candidate_pgs_ids=["PGS001", "PGS002"],
                n_models=2,
            ),
            TraitBundle(
                bundle_id="bundle_secondary",
                canonical_label="fasting glucose measurement",
                bundle_type="continuous",
                aliases=[],
                candidate_pgs_ids=["PGS002", "PGS003"],
                n_models=2,
            ),
        ],
    )
    evidence_state = EvidenceState(
        available_tools=["cross_trait_genetic_correlation", "cross_trait_open_targets"],
        shortlist_bundle_ids=["bundle_primary", "bundle_secondary"],
        target_summary={"target_label": "type 2 diabetes"},
        candidate_cards=[
            CandidateEvidenceCard(
                bundle_id="bundle_primary",
                canonical_label="metabolic syndrome",
                bundle_type="binary",
                candidate_pgs_ids=["PGS001", "PGS002"],
                n_models=2,
                archetype="composite liability trait",
                phenotype_fidelity="composite liability trait",
                phenotype_fidelity_score=0.74,
                cheap_rank_score=4.2,
                utility_score=6.8,
                evidence_tags=["significant_gc", "composite_liability_trait"],
            ),
            CandidateEvidenceCard(
                bundle_id="bundle_secondary",
                canonical_label="fasting glucose measurement",
                bundle_type="continuous",
                candidate_pgs_ids=["PGS002", "PGS003"],
                n_models=2,
                archetype="mechanistic endophenotype / organ-function measurement",
                phenotype_fidelity="mechanistic endophenotype / organ-function measurement",
                phenotype_fidelity_score=0.71,
                cheap_rank_score=3.9,
                utility_score=5.1,
                evidence_tags=["ot_overlap", "endophenotype_trait"],
            ),
        ],
    )
    judged = JudgeFrontierSelection(
        primary_bundle_id="bundle_primary",
        frontier_bundle_ids=["bundle_primary", "bundle_secondary"],
        confidence="Moderate",
        decision_mode="frontier_uncertain",
        rationale="Both bundles carry usable transfer evidence.",
        evidence_tags=["significant_gc", "ot_overlap"],
    )

    decision = transfer_agent._finalize_frontier_decision(dossier, evidence_state, judged)

    assert decision.primary_bundle_id == "bundle_primary"
    assert decision.frontier_bundle_ids == ["bundle_primary", "bundle_secondary"]
    assert decision.candidate_pgs_ids_union == ["PGS001", "PGS002", "PGS003"]
    assert decision.frontier_bundle_weights["bundle_primary"] > decision.frontier_bundle_weights["bundle_secondary"]
    assert set(decision.bundle_evidence_tags["bundle_secondary"]) == {
        "ot_overlap",
        "endophenotype_trait",
    }
    assert decision.outcome == "MATCHED"


def test_open_targets_shared_target_overlap_uses_weighted_datatype_support():
    toolbox = CrossTraitToolbox.__new__(CrossTraitToolbox)
    toolbox.ot_client = SimpleNamespace(
        get_target_pathways=lambda target_id: ["Pathway A", "Pathway B"],
        get_target_druggability=lambda target_id: "Druggable",
    )

    source_profile = {
        "associated_targets": [
            {
                "id": "ENSG0001",
                "approvedSymbol": "GENE1",
                "score": 0.8,
                "datatypeScores": [
                    {"id": "genetic_association", "score": 0.9},
                    {"id": "literature", "score": 0.2},
                ],
            }
        ]
    }
    candidate_profile = {
        "associated_targets": [
            {
                "id": "ENSG0001",
                "approvedSymbol": "GENE1",
                "score": 0.6,
                "datatypeScores": [
                    {"id": "genetic_association", "score": 0.8},
                    {"id": "clinical", "score": 0.5},
                ],
            }
        ]
    }

    shared_targets, shared_pathways, genetic_support_present = toolbox._shared_targets_from_profiles(
        source_profile,
        candidate_profile,
        "concise",
    )

    assert genetic_support_present is True
    assert shared_pathways == ["Pathway A", "Pathway B"]
    assert len(shared_targets) == 1
    assert shared_targets[0].symbol == "GENE1"
    assert shared_targets[0].weighted_overlap == pytest.approx(0.528, rel=1e-6)
    assert shared_targets[0].druggability == "Druggable"


def test_evaluate_end_to_end_condition_ranks_recommended_model(tmp_path, monkeypatch):
    from experiments.contribution3.transfer.eval import evaluate_end_to_end as eval_mod

    monkeypatch.setattr(
        eval_mod,
        "load_benchmark_target_selection",
        lambda benchmark_family="binary_to_binary", selected_only=True: pd.DataFrame(
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

    def fake_load_auc_matrix(target_source: str) -> pd.DataFrame:
        if target_source == "nontarget_pgs":
            return pd.DataFrame(
                {
                    "stub__PGS001": [0.61],
                    "stub__PGS002": [0.79],
                    "stub__PGS003": [0.72],
                },
                index=["A01"],
            )
        return pd.DataFrame(
            {
                "stub__PGS010": [0.65],
                "stub__PGS011": [0.63],
            },
            index=["B01"],
        )

    monkeypatch.setattr(eval_mod, "_load_auc_matrix", fake_load_auc_matrix)
    monkeypatch.setattr(
        eval_mod,
        "evaluation_dir",
        lambda benchmark_family="binary_to_binary": tmp_path / "evaluation",
    )

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
                        "candidate_pgs_ids": ["PGS002", "PGS003"],
                    },
                },
                {
                    "target": {"target_id": "B01"},
                    "decision": {
                        "outcome": "NO_MATCH",
                        "best_bundle_id": None,
                        "best_cross_trait": None,
                        "candidate_pgs_ids": [],
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
                    "transfer_decision": {
                        "outcome": "MATCHED",
                        "best_bundle_id": "bundle_1",
                        "best_cross_trait": "thyroid carcinoma",
                        "candidate_pgs_ids": ["PGS002", "PGS003"],
                    },
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
        benchmark_family="binary_to_binary",
        results_path=results_path,
        recommendations_path=recommendations_path,
    )

    assert summary["n_targets"] == 2
    assert summary["n_evaluated"] == 1
    assert summary["coverage"] == 0.5
    assert summary["official_metrics"]["mean_gpr"] == 0.25
    assert summary["conditional_mean_gpr"] == 0.5
    assert summary["official_metrics"]["hit_at_percent"]["top_5pct"] == 0.0
    assert summary["official_metrics"]["hit_at_percent"]["top_25pct"] == 0.0
    assert summary["official_metrics"]["mean_absolute_auc_regret"] == 0.07
    assert summary["by_input_type"]["A"]["official_metrics"]["mean_gpr"] == 0.5
    assert summary["by_input_type"]["B"]["official_metrics"]["mean_gpr"] == 0.0
    assert summary["mean_rank"] == 2.0
    assert summary["status_counts"]["evaluated"] == 1
    assert summary["status_counts"]["no_match"] == 1

    detail_df = pd.read_csv(tmp_path / "evaluation" / "all-tools__end_to_end_eval_detail.csv")
    row_a01 = detail_df.loc[detail_df["target_id"] == "A01"].iloc[0]
    row_b01 = detail_df.loc[detail_df["target_id"] == "B01"].iloc[0]
    assert row_a01["matched_bundle_id"] == "bundle_1"
    assert row_a01["selected_model_rank"] == 2
    assert row_a01["selected_model_gpr"] == 0.5
    assert row_a01["absolute_auc_regret"] == 0.07
    assert bool(row_a01["step1_universe_matches_bundle"]) is True
    assert pd.isna(row_b01["improves_over_self"])
    assert row_b01["status"] == "no_match"
