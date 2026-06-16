import os
from unittest.mock import Mock, patch

from src.server.core.tool_schemas import NeighborResult, RankedNeighbor, PGSSearchResult
from src.server.modules.disease.models import RecommendationReport
from src.server.modules.disease.recommendation_agent import Step1Decision, recommend_models


def _make_neighbors() -> NeighborResult:
    return NeighborResult(
        query_trait="Test Trait",
        resolved_by="exact",
        resolution_confidence="High",
        target_trait="Test Trait",
        target_h2_meta=0.4,
        neighbors=[
            RankedNeighbor(
                trait_id="Neighbor1",
                domain="Neuro",
                rg_meta=0.8,
                rg_z_meta=3.0,
                h2_meta=0.5,
                transfer_score=0.30,
                n_correlations=5,
            ),
            RankedNeighbor(
                trait_id="Neighbor2",
                domain="Neuro",
                rg_meta=0.6,
                rg_z_meta=2.6,
                h2_meta=0.4,
                transfer_score=0.20,
                n_correlations=4,
            ),
        ],
    )


def _empty_report() -> RecommendationReport:
    return RecommendationReport(
        recommendation_type="NO_MATCH_FOUND",
        primary_recommendation=None,
        alternative_recommendations=[],
        direct_match_evidence=None,
        cross_disease_evidence=None,
        caveats_and_limitations=[],
        follow_up_options=[],
    )


def test_recommendation_agent_uses_local_graph_selected_neighbors():
    mock_pgs_client = Mock()
    mock_pgs_client.search_scores.side_effect = lambda trait: [{"id": "PGS"}] if trait == "Neighbor2" else []
    mock_pgs_client.search_traits.return_value = []
    mock_pgs_client.get_score_details.return_value = {}

    with patch.dict(os.environ, {"PENNPRS_CONTRIB2_EVALUATED_PGS_JSON": ""}, clear=False), \
         patch("src.server.modules.disease.recommendation_agent.PGSCatalogClient", return_value=mock_pgs_client), \
         patch("src.server.modules.disease.recommendation_agent.OpenTargetsClient", return_value=Mock()), \
         patch("src.server.modules.disease.recommendation_agent.PheWASClient", return_value=Mock()), \
         patch("src.server.modules.disease.recommendation_agent.KnowledgeGraphService", return_value=Mock()), \
         patch("src.server.modules.disease.recommendation_agent.prs_model_domain_knowledge", return_value=Mock(model_dump=lambda: {})), \
         patch("src.server.modules.disease.recommendation_agent.trait_synonym_expand", return_value=Mock(expanded_queries=["Test Trait"])), \
         patch("src.server.modules.disease.recommendation_agent.genetic_graph_get_neighbors", return_value=_make_neighbors()), \
         patch("src.server.modules.disease.recommendation_agent.resolve_efo_and_mondo_ids", return_value=("EFO_1", "MONDO_1")), \
         patch("src.server.modules.disease.recommendation_agent.genetic_graph_validate_mechanism", return_value=Mock(
             shared_genes=[],
             shared_pathways=[],
             mechanism_summary="ok",
             confidence_level="High",
             phewas_evidence_count=0,
         )), \
         patch("src.server.modules.disease.recommendation_agent.genetic_graph_verify_study_power", return_value=Mock(
             n_correlations=5,
             rg_meta=0.6,
         )), \
         patch("src.server.modules.disease.recommendation_agent.rerank_neighbors_with_local_graph", return_value=[
             {"trait_id": "Neighbor2", "passes_rules": True, "local_graph_score": 0.9, "local_graph_rank": 1, "pgs_hit_count": 1},
             {"trait_id": "Neighbor1", "passes_rules": False, "local_graph_score": 0.4, "local_graph_rank": 2, "pgs_hit_count": 0},
         ]), \
         patch("src.server.modules.disease.recommendation_agent.select_neighbors_from_local_graph", return_value=["Neighbor2"]), \
         patch("src.server.modules.disease.recommendation_agent._build_step1_chain") as mock_step1_chain, \
         patch("src.server.modules.disease.recommendation_agent._build_report_chain") as mock_report_chain, \
         patch("src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search") as mock_search:

        def _search_side_effect(_client, trait_query, request_id=None, **kwargs):
            if trait_query == "Test Trait":
                return PGSSearchResult(query_trait=trait_query, total_found=0, after_filter=0, models=[])
            return PGSSearchResult(query_trait=trait_query, total_found=3, after_filter=1, models=[])

        mock_search.side_effect = _search_side_effect
        mock_step1_chain.return_value.invoke.return_value = Step1Decision(
            outcome="NO_MATCH_FOUND",
            best_model_id=None,
            top_alternatives=[],
            confidence="Low",
            rationale="No direct models.",
        )
        mock_report_chain.return_value.invoke.return_value = _empty_report()

        recommend_models("Test Trait")

        trait_calls = [c.args[1] for c in mock_search.call_args_list]
        assert trait_calls == ["Test Trait", "Neighbor2"]


def test_step1_disable_domain_knowledge_skips_tool_call():
    env = {
        "PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE": "1",
        "PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION": "0",
    }
    with patch.dict(os.environ, env, clear=False), \
         patch("src.server.modules.disease.recommendation_agent.prs_model_domain_knowledge") as mock_domain_tool, \
         patch("src.server.modules.disease.recommendation_agent._build_step1_chain") as mock_step1_chain, \
         patch("src.server.modules.disease.recommendation_agent._build_report_chain") as mock_report_chain, \
         patch("src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search", return_value=PGSSearchResult(
             query_trait="Test Trait",
             total_found=1,
             after_filter=0,
             models=[],
         )):

        mock_step1_chain.return_value.invoke.return_value = Step1Decision(
            outcome="DIRECT_HIGH_QUALITY",
            best_model_id=None,
            top_alternatives=[],
            confidence="Low",
            rationale="Forced test path.",
        )
        mock_report_chain.return_value.invoke.return_value = RecommendationReport(
            recommendation_type="DIRECT_HIGH_QUALITY",
            primary_recommendation=None,
            alternative_recommendations=[],
            direct_match_evidence=None,
            cross_disease_evidence=None,
            caveats_and_limitations=[],
            follow_up_options=[],
        )

        recommend_models("Test Trait")
        assert mock_domain_tool.call_count == 0
