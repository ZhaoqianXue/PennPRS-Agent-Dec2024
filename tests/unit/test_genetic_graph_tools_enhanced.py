import pytest
from unittest.mock import Mock, patch
from src.server.core.tool_schemas import MechanismValidation, ToolError, SharedGene
from src.server.core.tools.genetic_graph_tools import genetic_graph_validate_mechanism

class TestGeneticGraphToolsEnhanced:
    """Enhanced tests for genetic_graph_validate_mechanism with PheWAS integration."""

    @pytest.fixture
    def mock_ot_client(self):
        """Mock OpenTargetsClient."""
        client = Mock()
        # Mock responses for two diseases
        client.get_disease_targets.side_effect = [
            # Source targets (Crohn's)
            [
                {"id": "ENSG00000162594", "symbol": "IL23R", "score": 0.92},
                {"id": "ENSG00000096968", "symbol": "JAK2", "score": 0.85},
            ],
            # Target targets (Ulcerative Colitis)
            [
                {"id": "ENSG00000162594", "symbol": "IL23R", "score": 0.87},
                {"id": "ENSG00000096968", "symbol": "JAK2", "score": 0.80},
            ]
        ]
        client.get_target_druggability.return_value = "High"
        client.get_target_pathways.return_value = ["IL-17 signaling"]
        return client

    @pytest.fixture
    def mock_phewas_client(self):
        """Mock PheWASClient."""
        client = Mock()
        # Mock gene results for PheWAS
        # IL23R (ENSG00000162594) has significant PheWAS for "Crohn"
        # JAK2 (ENSG00000096968) does not have significant PheWAS matching keywords
        def get_gene_results_mock(gene_id):
            if gene_id == "ENSG00000162594":
                return [
                    {"label": "Crohn's disease", "p_value": 1e-12},
                    {"label": "Height", "p_value": 1e-20}
                ]
            elif gene_id == "ENSG00000096968":
                return [
                    {"label": "Red blood cell count", "p_value": 1e-30}
                ]
            return []
        
        client.get_gene_results.side_effect = get_gene_results_mock
        return client

    def test_validate_mechanism_with_phewas(self, mock_ot_client, mock_phewas_client):
        """Test mechanism validation including PheWAS evidence."""
        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_0000384",
            target_trait_efo="EFO_0000729",
            source_trait_name="Crohn's disease",
            target_trait_name="Ulcerative colitis",
            phewas_client=mock_phewas_client
        )

        assert isinstance(result, MechanismValidation)
        assert result.phewas_evidence_count == 1  # Only IL23R matched 'Crohn' keyword
        
        # Check SharedGene fields
        il23r = next(g for g in result.shared_genes if g.gene_symbol == "IL23R")
        assert il23r.phewas_p_value == 1e-12
        
        jak2 = next(g for g in result.shared_genes if g.gene_symbol == "JAK2")
        assert jak2.phewas_p_value is None

        # Check summary text
        assert "Further validated by PheWAS evidence for 1 gene(s)" in result.mechanism_summary

    def test_validate_mechanism_no_phewas_matches(self, mock_ot_client, mock_phewas_client):
        """Test mechanism validation when PheWAS results exist but don't match keywords."""
        # Change PheWAS mock to return non-matching traits
        mock_phewas_client.get_gene_results.side_effect = lambda gene_id: [
            {"label": "Unrelated Trait", "p_value": 1e-10}
        ]

        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_0000384",
            target_trait_efo="EFO_0000729",
            source_trait_name="Crohn's disease",
            target_trait_name="Ulcerative colitis",
            phewas_client=mock_phewas_client
        )

        assert result.phewas_evidence_count == 0
        assert "Further validated by PheWAS" not in result.mechanism_summary
        for gene in result.shared_genes:
            assert gene.phewas_p_value is None

    def test_validate_mechanism_phewas_api_failure(self, mock_ot_client, mock_phewas_client):
        """Test that PheWAS API failure doesn't crash the tool."""
        mock_phewas_client.get_gene_results.side_effect = Exception("PheWAS Down")

        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_0000384",
            target_trait_efo="EFO_0000729",
            source_trait_name="Crohn's disease",
            target_trait_name="Ulcerative colitis",
            phewas_client=mock_phewas_client
        )

        # Should still return Open Targets results
        assert isinstance(result, MechanismValidation)
        assert len(result.shared_genes) == 2
        assert result.phewas_evidence_count == 0

    def test_validate_mechanism_no_shared_genes(self, mock_ot_client):
        """Test case with no shared genes between traits."""
        mock_ot_client.get_disease_targets.side_effect = [
            [{"id": "ENSG1", "symbol": "GENE1", "score": 0.9}],
            [{"id": "ENSG2", "symbol": "GENE2", "score": 0.9}]
        ]

        result = genetic_graph_validate_mechanism(
            ot_client=mock_ot_client,
            source_trait_efo="EFO_1",
            target_trait_efo="EFO_2",
            source_trait_name="Trait 1",
            target_trait_name="Trait 2"
        )

        assert len(result.shared_genes) == 0
        assert result.confidence_level == "Low"
        assert "No shared genetic targets found" in result.mechanism_summary
