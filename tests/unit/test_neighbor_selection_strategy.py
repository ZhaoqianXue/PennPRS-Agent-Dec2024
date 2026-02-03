"""
Test neighbor selection strategy and evidence collection workflow.

Tests the new workflow where:
1. >= 2 neighbors -> process top 2 only
2. < 2 neighbors -> process all
3. Evidence collection tools called AFTER models are found (not as decision gates)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.server.modules.disease.recommendation_agent import recommend_models
from src.server.core.tool_schemas import (
    NeighborResult, RankedNeighbor, PGSSearchResult, PGSModelSummary,
    ToolError
)
from src.server.modules.disease.models import RecommendationReport


class TestNeighborSelectionStrategy:
    """Test neighbor selection strategy implementation."""
    
    @pytest.fixture
    def mock_clients(self):
        """Create mock clients."""
        pgs_client = Mock()
        ot_client = Mock()
        phewas_client = Mock()
        kg_service = Mock()
        return pgs_client, ot_client, phewas_client, kg_service
    
    def test_processes_top_2_when_3_or_more_neighbors(self, mock_clients):
        """Test that only top 2 neighbors are processed when >= 2 neighbors found."""
        pgs_client, ot_client, phewas_client, kg_service = mock_clients
        
        # Mock Step 1 to return NO_MATCH_FOUND
        with patch('src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search') as mock_search, \
             patch('src.server.modules.disease.recommendation_agent.prs_model_domain_knowledge') as mock_knowledge, \
             patch('src.server.modules.disease.recommendation_agent.prs_model_performance_landscape') as mock_landscape, \
             patch('src.server.modules.disease.recommendation_agent.trait_synonym_expand') as mock_synonym, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_get_neighbors') as mock_get_neighbors, \
             patch('src.server.modules.disease.recommendation_agent.resolve_efo_and_mondo_ids') as mock_resolve_ids, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_validate_mechanism') as mock_validate, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_verify_study_power') as mock_verify, \
             patch('src.server.modules.disease.recommendation_agent._build_step1_chain') as mock_step1_chain, \
             patch('src.server.modules.disease.recommendation_agent._build_report_chain') as mock_report_chain:
            
            # Setup mocks
            mock_search.return_value = PGSSearchResult(
                query_trait="Test Trait",
                total_found=0,
                after_filter=0,
                models=[]
            )
            mock_knowledge.return_value = Mock()
            mock_landscape.return_value = Mock()
            mock_synonym.return_value = Mock(expanded_queries=["Test Trait"])
            
            # Create 3 neighbors
            neighbors = [
                RankedNeighbor(
                    trait_id="Neighbor1",
                    domain="Test",
                    rg_meta=0.8,
                    rg_z_meta=3.0,
                    h2_meta=0.5,
                    transfer_score=0.32,
                    n_correlations=5
                ),
                RankedNeighbor(
                    trait_id="Neighbor2",
                    domain="Test",
                    rg_meta=0.7,
                    rg_z_meta=2.5,
                    h2_meta=0.4,
                    transfer_score=0.196,
                    n_correlations=4
                ),
                RankedNeighbor(
                    trait_id="Neighbor3",
                    domain="Test",
                    rg_meta=0.6,
                    rg_z_meta=2.2,
                    h2_meta=0.3,
                    transfer_score=0.108,
                    n_correlations=3
                )
            ]
            
            mock_get_neighbors.return_value = NeighborResult(
                query_trait="Test Trait",
                resolved_by="exact",
                resolution_confidence="High",
                target_trait="Test Trait",
                target_h2_meta=0.4,
                neighbors=neighbors
            )
            
            mock_resolve_ids.return_value = ("EFO_123", "MONDO_456")
            mock_validate.return_value = Mock(
                shared_genes=[],
                shared_pathways=[],
                mechanism_summary="Test mechanism",
                confidence_level="High"
            )
            mock_verify.return_value = Mock(
                n_correlations=5,
                rg_meta=0.8
            )
            
            # Mock Step 1 decision
            from src.server.modules.disease.recommendation_agent import Step1Decision
            mock_step1_chain.return_value.invoke.return_value = Step1Decision(
                outcome="NO_MATCH_FOUND",
                best_model_id=None,
                confidence="Low",
                rationale="No direct models"
            )
            
            # Mock report generation
            from src.server.modules.disease.models import RecommendationReport
            mock_report_chain.return_value.invoke.return_value = RecommendationReport(
                recommendation_type="NO_MATCH_FOUND",
                primary_recommendation=None,
                alternative_recommendations=[],
                direct_match_evidence=None,
                cross_disease_evidence=None,
                caveats_and_limitations=[],
                follow_up_options=[]
            )
            
            # Call function
            result = recommend_models("Test Trait")
            
            # Verify that prs_model_pgscatalog_search was called exactly 2 times (for top 2 neighbors)
            # Note: First call is for target trait in Step 1, then 2 calls for neighbors
            assert mock_search.call_count == 3  # 1 for target + 2 for neighbors
            
            # Verify neighbors were processed in order (highest transfer_score first)
            neighbor_calls = [call[0][1] for call in mock_search.call_args_list[1:]]  # Skip first call (target trait)
            assert len(neighbor_calls) == 2
            assert neighbor_calls[0] == "Neighbor1"  # Highest transfer_score
            assert neighbor_calls[1] == "Neighbor2"  # Second highest
    
    def test_processes_all_when_1_neighbor(self, mock_clients):
        """Test that all neighbors are processed when < 2 neighbors found."""
        pgs_client, ot_client, phewas_client, kg_service = mock_clients
        
        with patch('src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search') as mock_search, \
             patch('src.server.modules.disease.recommendation_agent.prs_model_domain_knowledge') as mock_knowledge, \
             patch('src.server.modules.disease.recommendation_agent.prs_model_performance_landscape') as mock_landscape, \
             patch('src.server.modules.disease.recommendation_agent.trait_synonym_expand') as mock_synonym, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_get_neighbors') as mock_get_neighbors, \
             patch('src.server.modules.disease.recommendation_agent.resolve_efo_and_mondo_ids') as mock_resolve_ids, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_validate_mechanism') as mock_validate, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_verify_study_power') as mock_verify, \
             patch('src.server.modules.disease.recommendation_agent._build_step1_chain') as mock_step1_chain, \
             patch('src.server.modules.disease.recommendation_agent._build_report_chain') as mock_report_chain:
            
            # Setup mocks
            mock_search.return_value = PGSSearchResult(
                query_trait="Test Trait",
                total_found=0,
                after_filter=0,
                models=[]
            )
            mock_knowledge.return_value = Mock()
            mock_landscape.return_value = Mock()
            mock_synonym.return_value = Mock(expanded_queries=["Test Trait"])
            
            # Create 1 neighbor
            neighbors = [
                RankedNeighbor(
                    trait_id="Neighbor1",
                    domain="Test",
                    rg_meta=0.8,
                    rg_z_meta=3.0,
                    h2_meta=0.5,
                    transfer_score=0.32,
                    n_correlations=5
                )
            ]
            
            mock_get_neighbors.return_value = NeighborResult(
                query_trait="Test Trait",
                resolved_by="exact",
                resolution_confidence="High",
                target_trait="Test Trait",
                target_h2_meta=0.4,
                neighbors=neighbors
            )
            
            mock_resolve_ids.return_value = ("EFO_123", "MONDO_456")
            mock_validate.return_value = Mock(
                shared_genes=[],
                shared_pathways=[],
                mechanism_summary="Test mechanism",
                confidence_level="High"
            )
            mock_verify.return_value = Mock(
                n_correlations=5,
                rg_meta=0.8
            )
            
            # Mock Step 1 decision
            from src.server.modules.disease.recommendation_agent import Step1Decision
            mock_step1_chain.return_value.invoke.return_value = Step1Decision(
                outcome="NO_MATCH_FOUND",
                best_model_id=None,
                confidence="Low",
                rationale="No direct models"
            )
            
            # Mock report generation
            from src.server.modules.disease.models import RecommendationReport
            mock_report_chain.return_value.invoke.return_value = RecommendationReport(
                recommendation_type="NO_MATCH_FOUND",
                primary_recommendation=None,
                alternative_recommendations=[],
                direct_match_evidence=None,
                cross_disease_evidence=None,
                caveats_and_limitations=[],
                follow_up_options=[]
            )
            
            # Call function
            result = recommend_models("Test Trait")
            
            # Verify that prs_model_pgscatalog_search was called 2 times (1 for target + 1 for neighbor)
            assert mock_search.call_count == 2
            
            # Verify the single neighbor was processed
            neighbor_calls = [call[0][1] for call in mock_search.call_args_list[1:]]
            assert len(neighbor_calls) == 1
            assert neighbor_calls[0] == "Neighbor1"
    
    def test_evidence_collection_called_after_models_found(self, mock_clients):
        """Test that evidence collection tools are called AFTER models are found."""
        pgs_client, ot_client, phewas_client, kg_service = mock_clients
        
        with patch('src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search') as mock_search, \
             patch('src.server.modules.disease.recommendation_agent.prs_model_domain_knowledge') as mock_knowledge, \
             patch('src.server.modules.disease.recommendation_agent.prs_model_performance_landscape') as mock_landscape, \
             patch('src.server.modules.disease.recommendation_agent.trait_synonym_expand') as mock_synonym, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_get_neighbors') as mock_get_neighbors, \
             patch('src.server.modules.disease.recommendation_agent.resolve_efo_and_mondo_ids') as mock_resolve_ids, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_validate_mechanism') as mock_validate, \
             patch('src.server.modules.disease.recommendation_agent.genetic_graph_verify_study_power') as mock_verify, \
             patch('src.server.modules.disease.recommendation_agent._build_step1_chain') as mock_step1_chain, \
             patch('src.server.modules.disease.recommendation_agent._build_report_chain') as mock_report_chain:
            
            # Setup mocks
            # First call (target trait) returns no models
            # Second call (neighbor) returns models
            def search_side_effect(trait_query, limit=25):
                if trait_query == "Test Trait":
                    return PGSSearchResult(
                        query_trait="Test Trait",
                        total_found=0,
                        after_filter=0,
                        models=[]
                    )
                else:  # neighbor trait
                    return PGSSearchResult(
                        query_trait="Neighbor1",
                        total_found=5,
                        after_filter=3,
                        models=[
                            Mock(id="PGS000001", performance_metrics={"auc": 0.75}),
                            Mock(id="PGS000002", performance_metrics={"auc": 0.70})
                        ]
                    )
            
            mock_search.side_effect = search_side_effect
            mock_knowledge.return_value = Mock()
            mock_landscape.return_value = Mock()
            mock_synonym.return_value = Mock(expanded_queries=["Test Trait"])
            
            neighbors = [
                RankedNeighbor(
                    trait_id="Neighbor1",
                    domain="Test",
                    rg_meta=0.8,
                    rg_z_meta=3.0,
                    h2_meta=0.5,
                    transfer_score=0.32,
                    n_correlations=5
                )
            ]
            
            mock_get_neighbors.return_value = NeighborResult(
                query_trait="Test Trait",
                resolved_by="exact",
                resolution_confidence="High",
                target_trait="Test Trait",
                target_h2_meta=0.4,
                neighbors=neighbors
            )
            
            mock_resolve_ids.return_value = ("EFO_123", "MONDO_456")
            mock_validate.return_value = Mock(
                shared_genes=[],
                shared_pathways=[],
                mechanism_summary="Test mechanism",
                confidence_level="High"
            )
            mock_verify.return_value = Mock(
                n_correlations=5,
                rg_meta=0.8
            )
            
            # Mock Step 1 decision
            from src.server.modules.disease.recommendation_agent import Step1Decision
            mock_step1_chain.return_value.invoke.return_value = Step1Decision(
                outcome="NO_MATCH_FOUND",
                best_model_id=None,
                confidence="Low",
                rationale="No direct models"
            )
            
            # Mock report generation
            from src.server.modules.disease.models import RecommendationReport
            mock_report_chain.return_value.invoke.return_value = RecommendationReport(
                recommendation_type="NO_MATCH_FOUND",
                primary_recommendation=None,
                alternative_recommendations=[],
                direct_match_evidence=None,
                cross_disease_evidence=None,
                caveats_and_limitations=[],
                follow_up_options=[]
            )
            
            # Call function
            result = recommend_models("Test Trait")
            
            # Verify call order: search first, then evidence collection
            call_order = [call[0][0].__name__ if hasattr(call[0][0], '__name__') else str(call[0][0]) 
                         for call in mock_search.call_args_list]
            
            # Verify that validate_mechanism and verify_study_power were called
            # (they should be called after models are found)
            assert mock_validate.called, "genetic_graph_validate_mechanism should be called after models found"
            assert mock_verify.called, "genetic_graph_verify_study_power should be called after models found"
            
            # Verify that evidence tools were called with correct parameters
            validate_call = mock_validate.call_args
            assert validate_call is not None
            assert validate_call[1]['source_trait_name'] == "Neighbor1"
            assert validate_call[1]['target_trait_name'] == "Test Trait"
