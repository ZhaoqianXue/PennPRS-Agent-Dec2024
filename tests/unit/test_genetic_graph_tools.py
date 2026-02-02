# tests/unit/test_genetic_graph_tools.py
"""
Unit tests for Genetic Graph Tools.
Implements TDD for sop.md L464-562 tool specifications.
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.server.core.tool_schemas import (
    StudyPowerResult, CorrelationProvenance, 
    NeighborResult, RankedNeighbor, ToolError
)
from src.server.core.tools.genetic_graph_tools import (
    genetic_graph_verify_study_power,
    genetic_graph_get_neighbors
)


class TestVerifyStudyPower:
    """Test genetic_graph_verify_study_power tool."""
    
    @pytest.fixture
    def mock_kg_service(self):
        """Create mock KnowledgeGraphService with edge provenance."""
        service = Mock()
        service.get_edge_provenance.return_value = StudyPowerResult(
            source_trait="Schizophrenia",
            target_trait="Bipolar disorder",
            rg_meta=0.65,
            n_correlations=2,
            correlations=[
                CorrelationProvenance(
                    study1_id=123, study1_n=50000, study1_population="EUR", study1_pmid="12345",
                    study2_id=456, study2_n=40000, study2_population="EUR", study2_pmid="67890",
                    rg=0.60, se=0.05, p=1e-8
                ),
                CorrelationProvenance(
                    study1_id=789, study1_n=30000, study1_population="EAS", study1_pmid="11111",
                    study2_id=101, study2_n=25000, study2_population="EAS", study2_pmid="22222",
                    rg=0.70, se=0.06, p=1e-7
                )
            ]
        )
        return service

    def test_returns_study_power_result(self, mock_kg_service):
        """Test tool wrapper calls service and returns result."""
        result = genetic_graph_verify_study_power(
            mock_kg_service,
            source_trait="Schizophrenia",
            target_trait="Bipolar disorder"
        )
        
        assert isinstance(result, StudyPowerResult)
        assert result.source_trait == "Schizophrenia"
        assert result.n_correlations == 2
        mock_kg_service.get_edge_provenance.assert_called_once_with(
            source_trait="Schizophrenia",
            target_trait="Bipolar disorder"
        )

    def test_returns_tool_error_when_edge_not_found(self):
        """Test tool returns ToolError when edge not found."""
        service = Mock()
        service.get_edge_provenance.return_value = None
        
        result = genetic_graph_verify_study_power(
            service,
            source_trait="NonExistent",
            target_trait="AlsoNonExistent"
        )
        
        assert isinstance(result, ToolError)
        assert result.tool_name == "genetic_graph_verify_study_power"
        assert result.error_type == "EdgeNotFound"
        assert "NonExistent" in result.error_message

    def test_handles_service_exception(self):
        """Test tool catches and wraps exceptions."""
        service = Mock()
        service.get_edge_provenance.side_effect = ConnectionError("Network failed")
        
        result = genetic_graph_verify_study_power(
            service,
            source_trait="Trait1",
            target_trait="Trait2"
        )
        
        assert isinstance(result, ToolError)
        assert result.error_type == "ConnectionError"
        assert "Network failed" in result.error_message


class TestGetNeighbors:
    """Test genetic_graph_get_neighbors tool."""
    
    @pytest.fixture
    def mock_kg_service_with_neighbors(self):
        """Create mock KnowledgeGraphService with prioritized neighbors."""
        from src.server.modules.knowledge_graph.models import PrioritizedNeighbor, TraitNode
        
        service = Mock()
        
        # Mock get_prioritized_neighbors_v2 return
        neighbor1 = Mock()
        neighbor1.trait_id = "Type 2 Diabetes"
        neighbor1.trait_name = "Type 2 Diabetes" 
        neighbor1.rg = 0.45
        neighbor1.h2 = 0.6
        neighbor1.score = 0.1215  # 0.45^2 * 0.6
        neighbor1.p_value = 1e-10
        
        neighbor2 = Mock()
        neighbor2.trait_id = "Obesity"
        neighbor2.trait_name = "Obesity"
        neighbor2.rg = 0.35
        neighbor2.h2 = 0.5
        neighbor2.score = 0.0613  # 0.35^2 * 0.5
        neighbor2.p_value = 1e-8
        
        service.get_prioritized_neighbors_v2.return_value = [neighbor1, neighbor2]
        
        # Mock get_trait_node for target h2
        target_node = Mock()
        target_node.h2_meta = 0.55
        target_node.domain = "Metabolic"
        service.get_trait_node.return_value = target_node
        
        return service

    def test_returns_neighbor_result(self, mock_kg_service_with_neighbors):
        """Test tool returns properly formatted NeighborResult."""
        result = genetic_graph_get_neighbors(
            mock_kg_service_with_neighbors,
            trait_id="Coronary Artery Disease"
        )
        
        assert isinstance(result, NeighborResult)
        assert result.target_trait == "Coronary Artery Disease"
        assert result.target_h2_meta == 0.55
        assert len(result.neighbors) == 2

    def test_neighbors_have_correct_fields(self, mock_kg_service_with_neighbors):
        """Test each RankedNeighbor has all required fields."""
        result = genetic_graph_get_neighbors(
            mock_kg_service_with_neighbors,
            trait_id="CAD"
        )
        
        neighbor = result.neighbors[0]
        assert isinstance(neighbor, RankedNeighbor)
        assert hasattr(neighbor, 'trait_id')
        assert hasattr(neighbor, 'domain')
        assert hasattr(neighbor, 'rg_meta')
        assert hasattr(neighbor, 'rg_z_meta')
        assert hasattr(neighbor, 'h2_meta')
        assert hasattr(neighbor, 'transfer_score')
        assert hasattr(neighbor, 'n_correlations')

    def test_returns_tool_error_when_trait_not_found(self):
        """Test tool returns ToolError when trait not in graph."""
        service = Mock()
        service.get_prioritized_neighbors_v2.return_value = None
        
        result = genetic_graph_get_neighbors(
            service,
            trait_id="NonExistentTrait"
        )
        
        assert isinstance(result, ToolError)
        assert result.tool_name == "genetic_graph_get_neighbors"
        assert result.error_type == "TraitNotFound"

    def test_respects_limit_parameter(self, mock_kg_service_with_neighbors):
        """Test that limit parameter restricts neighbor count."""
        result = genetic_graph_get_neighbors(
            mock_kg_service_with_neighbors,
            trait_id="CAD",
            limit=1
        )
        
        # Should return at most 1 neighbor
        assert len(result.neighbors) <= 1


class TestValidateMechanism:
    """Test genetic_graph_validate_mechanism tool."""
    
    def test_returns_mechanism_validation(self):
        """Test tool returns MechanismValidation with shared genes."""
        from src.server.core.tools.genetic_graph_tools import genetic_graph_validate_mechanism
        from src.server.core.tool_schemas import MechanismValidation
        from unittest.mock import Mock, patch
        
        # Mock the Open Targets client
        mock_ot_client = Mock()
        
        # Mock responses for two diseases
        mock_ot_client.get_disease_targets.side_effect = [
            # Crohn's disease targets
            [
                {"id": "ENSG00000162594", "symbol": "IL23R", "score": 0.92},
                {"id": "ENSG00000096968", "symbol": "JAK2", "score": 0.85},
                {"id": "ENSG00000117020", "symbol": "AKT3", "score": 0.75},
            ],
            # UC targets
            [
                {"id": "ENSG00000162594", "symbol": "IL23R", "score": 0.87},
                {"id": "ENSG00000096968", "symbol": "JAK2", "score": 0.80},
                {"id": "ENSG00000140105", "symbol": "WARS", "score": 0.70},
            ]
        ]
        
        # Mock druggability
        mock_ot_client.get_target_druggability.return_value = "High"
        mock_ot_client.get_target_pathways.return_value = ["IL-17 signaling"]
        
        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_0000384",  # Crohn's
            target_trait_efo="EFO_0000729",  # UC
            source_trait_name="Crohn's disease",
            target_trait_name="Ulcerative colitis"
        )
        
        assert isinstance(result, MechanismValidation)
        assert result.source_trait == "Crohn's disease"
        assert result.target_trait == "Ulcerative colitis"
        assert len(result.shared_genes) >= 1  # At least IL23R and JAK2
        
        # Check shared genes include expected
        gene_symbols = [g.gene_symbol for g in result.shared_genes]
        assert "IL23R" in gene_symbols
        assert "JAK2" in gene_symbols

    def test_returns_tool_error_on_api_failure(self):
        """Test tool returns ToolError when API fails."""
        from src.server.core.tools.genetic_graph_tools import genetic_graph_validate_mechanism
        from src.server.core.tool_schemas import ToolError
        from unittest.mock import Mock
        
        mock_ot_client = Mock()
        mock_ot_client.get_disease_targets.side_effect = ConnectionError("API unavailable")
        
        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_0000384",
            target_trait_efo="EFO_0000729",
            source_trait_name="Crohn's disease",
            target_trait_name="Ulcerative colitis"
        )
        
        assert isinstance(result, ToolError)
        assert result.tool_name == "genetic_graph_validate_mechanism"

    def test_handles_no_shared_genes(self):
        """Test tool handles case when no genes are shared."""
        from src.server.core.tools.genetic_graph_tools import genetic_graph_validate_mechanism
        from src.server.core.tool_schemas import MechanismValidation
        from unittest.mock import Mock
        
        mock_ot_client = Mock()
        mock_ot_client.get_disease_targets.side_effect = [
            [{"id": "ENSG00000001", "symbol": "GENE_A", "score": 0.9}],
            [{"id": "ENSG00000002", "symbol": "GENE_B", "score": 0.9}],
        ]
        
        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_0001",
            target_trait_efo="EFO_0002",
            source_trait_name="Disease A",
            target_trait_name="Disease B"
        )
        
        assert isinstance(result, MechanismValidation)
        assert len(result.shared_genes) == 0
        assert result.confidence_level == "Low"
