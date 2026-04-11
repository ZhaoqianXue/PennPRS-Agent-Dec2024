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


def test_cross_trait_agent_fetches_detailed_evidence_for_full_shortlist(monkeypatch):
    bundles = [
        TraitBundle(
            bundle_id=f"bundle_{idx}",
            canonical_label=f"candidate trait {idx}",
            bundle_type="binary",
            aliases=[f"candidate alias {idx}"],
            candidate_pgs_ids=[f"PGS{idx:03d}"],
            n_models=idx + 1,
        )
        for idx in range(6)
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
        def __init__(self, bundle_lookup):
            self.bundle_lookup = bundle_lookup
            self.calls = []

        @staticmethod
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

        def _record(self, name: str, candidate_bundle_ids: list[str], response_format: str, ancestry: str | None = None) -> None:
            self.calls.append(
                {
                    "name": name,
                    "candidate_bundle_ids": list(candidate_bundle_ids),
                    "response_format": response_format,
                    "ancestry": ancestry,
                }
            )

        def cross_trait_genetic_correlation(
            self,
            target_trait: str,
            candidate_bundle_ids: list[str],
            response_format: str = "concise",
        ) -> dict:
            self._record("cross_trait_genetic_correlation", candidate_bundle_ids, response_format)
            rows = []
            for offset, bundle_id in enumerate(candidate_bundle_ids):
                bundle = self.bundle_lookup[bundle_id]
                row = {
                    "bundle_id": bundle_id,
                    "canonical_label": bundle.canonical_label,
                    "target_resolution": self._resolution(target_trait, "gwas_atlas"),
                    "candidate_resolution": self._resolution(bundle.canonical_label, "gwas_atlas"),
                    "pair_status": "resolved_pair_found",
                    "rg": round(0.08 + offset * 0.01, 4),
                    "z_score": 1.0,
                    "p_value": 0.2,
                    "provenance_status": "lookup_only",
                    "evidence_strength": "Weak",
                }
                if response_format == "detailed":
                    row["alternative_pairs"] = [
                        {
                            "target_trait_id": 10,
                            "target_trait_label": target_trait,
                            "candidate_trait_id": 20 + offset,
                            "candidate_trait_label": bundle.canonical_label,
                            "score": 180.0,
                        }
                    ]
                rows.append(row)
            return {"target_trait": target_trait, "response_format": response_format, "results": rows}

        def cross_trait_heritability(
            self,
            target_trait: str,
            candidate_bundle_ids: list[str],
            ancestry: str = "EUR",
            response_format: str = "concise",
        ) -> dict:
            self._record("cross_trait_heritability", candidate_bundle_ids, response_format, ancestry)
            rows = []
            for offset, bundle_id in enumerate(candidate_bundle_ids):
                bundle = self.bundle_lookup[bundle_id]
                rows.append(
                    {
                        "bundle_id": bundle_id,
                        "canonical_label": bundle.canonical_label,
                        "ancestry": ancestry,
                        "target_profile": [
                            {"trait_name": target_trait, "h2_obs": 0.02, "match_score": 99.0},
                            {"trait_name": f"{target_trait} alternate", "h2_obs": 0.018, "match_score": 88.0},
                        ],
                        "candidate_profile": [
                            {"trait_name": bundle.canonical_label, "h2_obs": 0.01 + offset * 0.001, "match_score": 99.0},
                            {"trait_name": f"{bundle.canonical_label} alternate", "h2_obs": 0.008, "match_score": 87.0},
                        ],
                        "target_best_h2": 0.02,
                        "candidate_best_h2": 0.01 + offset * 0.001,
                        "candidate_signal_capacity": 0.01 + offset * 0.001,
                        "shared_signal_ceiling_proxy": 0.01,
                        "confidence_tier": "High",
                    }
                )
            return {
                "target_trait": target_trait,
                "ancestry": ancestry,
                "response_format": response_format,
                "results": rows,
            }

        def cross_trait_open_targets(
            self,
            target_trait: str,
            candidate_bundle_ids: list[str],
            response_format: str = "concise",
        ) -> dict:
            self._record("cross_trait_open_targets", candidate_bundle_ids, response_format)
            rows = []
            for offset, bundle_id in enumerate(candidate_bundle_ids):
                bundle = self.bundle_lookup[bundle_id]
                rows.append(
                    {
                        "bundle_id": bundle_id,
                        "canonical_label": bundle.canonical_label,
                        "target_resolution": self._resolution(target_trait, "open_targets"),
                        "candidate_resolution": self._resolution(bundle.canonical_label, "open_targets"),
                        "pair_status": "resolved_overlap",
                        "source_association_count": 12,
                        "candidate_association_count": 10,
                        "weighted_shared_target_overlap_score": 0.3 + offset * 0.01,
                        "shared_target_count": 1,
                        "top_shared_targets": [
                            {
                                "target_id": f"ENSG{offset:04d}",
                                "symbol": f"GENE{offset}",
                                "source_score": 0.8,
                                "candidate_score": 0.7,
                                "min_score": 0.7,
                                "weighted_overlap": 0.3,
                                "source_datatype_scores": {"genetic_association": 0.5},
                                "candidate_datatype_scores": {"genetic_association": 0.4},
                                "pathways": ["Pathway A", "Pathway B"],
                            }
                        ],
                        "shared_pathway_clusters": ["Pathway A", "Pathway B"],
                        "therapeutic_area_match": True,
                        "shared_therapeutic_areas": ["immune system disease"],
                        "source_therapeutic_areas": ["immune system disease"],
                        "candidate_therapeutic_areas": ["immune system disease"],
                        "shared_ancestor_count": 2,
                        "shared_ancestors": ["autoimmune disease", "immune system disease"],
                        "shared_phenotype_count": 3,
                        "shared_phenotypes": ["Fever", "Fatigue", "Weight loss"],
                        "phenotype_overlap_score": 0.12,
                        "genetic_support_present": True,
                        "confidence_level": "Moderate",
                        "mechanism_summary": "Synthetic detailed overlap.",
                    }
                )
            return {"target_trait": target_trait, "response_format": response_format, "results": rows}

    fake_toolbox = FakeToolbox({bundle.bundle_id: bundle for bundle in bundles})

    def fake_judge(evidence_state, default_frontier_ids, default_mode):
        return JudgeFrontierSelection(
            primary_bundle_id=default_frontier_ids[0],
            frontier_bundle_ids=default_frontier_ids,
            confidence="Moderate",
            decision_mode=default_mode,
            rationale="Synthetic judge selection.",
            evidence_tags=[],
        )

    def fake_verify(evidence_state, proposed, selected_cards):
        visible_tags = sorted({tag for card in selected_cards for tag in card.evidence_tags})
        return transfer_agent.VerifiedSelection(
            confidence=proposed.confidence,
            decision_mode=proposed.decision_mode,
            rationale=proposed.rationale,
            evidence_tags=visible_tags,
            supported=True,
            issues=[],
        )

    monkeypatch.setattr(transfer_agent, "_judge_frontier", fake_judge)
    monkeypatch.setattr(transfer_agent, "_verify_selection", fake_verify)

    result = transfer_agent.run_cross_trait_agent(
        dossier,
        condition="all-tools",
        toolbox=fake_toolbox,
        benchmark_family="binary_to_continuous",
    )

    all_candidate_ids = [bundle.bundle_id for bundle in bundles]
    detailed_calls = [
        call
        for call in fake_toolbox.calls
        if call["response_format"] == "detailed"
    ]
    concise_h2_ot_calls = [
        call
        for call in fake_toolbox.calls
        if call["name"] in {"cross_trait_heritability", "cross_trait_open_targets"}
        and call["response_format"] == "concise"
    ]

    assert fake_toolbox.calls[0] == {
        "name": "cross_trait_genetic_correlation",
        "candidate_bundle_ids": all_candidate_ids,
        "response_format": "concise",
        "ancestry": None,
    }
    assert [call["name"] for call in fake_toolbox.calls] == [
        "cross_trait_genetic_correlation",
        "cross_trait_genetic_correlation",
        "cross_trait_heritability",
        "cross_trait_open_targets",
    ]
    assert concise_h2_ot_calls == []
    assert len(detailed_calls) == 3

    detailed_gc_call = detailed_calls[0]
    shortlist_ids = detailed_gc_call["candidate_bundle_ids"]
    assert len(shortlist_ids) == len(all_candidate_ids)
    assert set(shortlist_ids) == set(all_candidate_ids)
    assert all(call["candidate_bundle_ids"] == shortlist_ids for call in detailed_calls)
    assert all(len(call["candidate_bundle_ids"]) != 3 for call in detailed_calls)

    trace = result["tool_trace"]
    assert trace[0]["phase"] == "candidate_prescreen"
    assert trace[0]["args"]["response_format"] == "concise"
    assert [entry["phase"] for entry in trace[1:]] == ["shortlist_detailed"] * 3
    assert [entry["args"]["response_format"] for entry in trace[1:]] == ["detailed"] * 3

    evidence_state = result["decision"]["evidence_state"]
    candidate_cards = evidence_state["candidate_cards"]
    assert set(evidence_state["shortlist_bundle_ids"]) == set(shortlist_ids)
    assert {card["bundle_id"] for card in candidate_cards} == set(shortlist_ids)
    for card in candidate_cards:
        assert card["gc"]["alternative_pairs"]
        assert len(card["h2"]["candidate_profile"]) == 2
        assert card["open_targets"]["therapeutic_area_match"] is True


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

    decision = transfer_agent._finalize_frontier_decision(
        dossier,
        evidence_state,
        judged,
        config=transfer_agent.DEFAULT_CONFIG,
    )

    assert decision.primary_bundle_id == "bundle_primary"
    assert decision.frontier_bundle_ids == ["bundle_primary", "bundle_secondary"]
    assert decision.candidate_pgs_ids_union == ["PGS001", "PGS002", "PGS003"]
    assert decision.frontier_bundle_weights["bundle_primary"] > decision.frontier_bundle_weights["bundle_secondary"]
    assert set(decision.bundle_evidence_tags["bundle_secondary"]) == {
        "ot_overlap",
        "endophenotype_trait",
    }
    assert decision.outcome == "MATCHED"


def test_finalize_frontier_decision_stabilizes_primary_with_model_support(monkeypatch):
    dossier = CandidateBundleDossier(
        target=TargetTraitQuery(
            target_id="T1",
            target_code="T1",
            target_label="target disease",
        ),
        candidates=[
            TraitBundle(
                bundle_id="sparse_high_utility",
                canonical_label="sparse candidate",
                bundle_type="binary",
                aliases=[],
                candidate_pgs_ids=["PGS001"],
                n_models=1,
            ),
            TraitBundle(
                bundle_id="supported_near_tie",
                canonical_label="supported candidate",
                bundle_type="binary",
                aliases=[],
                candidate_pgs_ids=["PGS010", "PGS011"],
                n_models=80,
            ),
        ],
    )
    evidence_state = EvidenceState(
        available_tools=["cross_trait_genetic_correlation"],
        shortlist_bundle_ids=["sparse_high_utility", "supported_near_tie"],
        target_summary={"target_label": "target disease"},
        candidate_cards=[
            CandidateEvidenceCard(
                bundle_id="sparse_high_utility",
                canonical_label="sparse candidate",
                bundle_type="binary",
                candidate_pgs_ids=["PGS001"],
                n_models=1,
                archetype="adjacent disease family",
                phenotype_fidelity="adjacent disease family",
                phenotype_fidelity_score=0.76,
                cheap_rank_score=3.0,
                utility_score=6.2,
                evidence_tags=["significant_gc"],
            ),
            CandidateEvidenceCard(
                bundle_id="supported_near_tie",
                canonical_label="supported candidate",
                bundle_type="binary",
                candidate_pgs_ids=["PGS010", "PGS011"],
                n_models=80,
                archetype="adjacent disease family",
                phenotype_fidelity="adjacent disease family",
                phenotype_fidelity_score=0.76,
                cheap_rank_score=2.9,
                utility_score=5.9,
                evidence_tags=["significant_gc"],
            ),
        ],
    )
    judged = JudgeFrontierSelection(
        primary_bundle_id="sparse_high_utility",
        frontier_bundle_ids=["sparse_high_utility", "supported_near_tie"],
        confidence="Moderate",
        decision_mode="frontier_uncertain",
        rationale="Both frontier bundles have usable support.",
        evidence_tags=["significant_gc"],
    )

    def fake_verify(evidence_state, proposed, selected_cards):
        return transfer_agent.VerifiedSelection(
            confidence=proposed.confidence,
            decision_mode=proposed.decision_mode,
            rationale=proposed.rationale,
            evidence_tags=proposed.evidence_tags,
            supported=True,
            issues=[],
        )

    monkeypatch.setattr(transfer_agent, "_verify_selection", fake_verify)

    decision = transfer_agent._finalize_frontier_decision(
        dossier,
        evidence_state,
        judged,
        config=transfer_agent.DEFAULT_CONFIG,
    )

    assert decision.primary_bundle_id == "supported_near_tie"
    assert decision.best_bundle_id == "supported_near_tie"
    assert decision.frontier_bundle_ids[0] == "supported_near_tie"
    assert decision.candidate_pgs_ids_union == ["PGS010", "PGS011", "PGS001"]


def test_open_targets_shared_target_overlap_uses_weighted_datatype_support():
    toolbox = CrossTraitToolbox.__new__(CrossTraitToolbox)
    toolbox.ot_client = SimpleNamespace(
        get_target_pathways=lambda target_id: ["Pathway A", "Pathway B"],
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
    assert shared_targets[0].weighted_overlap == pytest.approx(0.63, rel=1e-6)


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
