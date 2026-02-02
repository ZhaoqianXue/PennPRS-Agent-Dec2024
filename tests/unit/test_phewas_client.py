import pytest
from unittest.mock import Mock, patch
from src.server.core.phewas_client import PheWASClient
import requests

class TestPheWASClient:
    """Unit tests for PheWASClient."""

    @pytest.fixture
    def client(self):
        """Create a PheWASClient instance."""
        return PheWASClient()

    @patch("requests.Session.get")
    def test_get_outcomes(self, mock_get, client):
        """Test mapping EFO ID or trait name to ExPheWAS outcome ID."""
        # Mock response for /outcome
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "1", "label": "Crohn's Disease"},
            {"id": "EFO_0000384", "label": "Inflammatory Bowel Disease"},
            {"id": "3", "label": "Schizophrenia"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test search by trait name
        results = client.get_outcomes("Crohn")
        assert len(results) == 1
        assert results[0]["label"] == "Crohn's Disease"

        # Test search by EFO ID
        results = client.get_outcomes("EFO_0000384")
        assert len(results) == 1
        assert results[0]["id"] == "EFO_0000384"

        # Test case insensitivity
        results = client.get_outcomes("crohn")
        assert len(results) == 1

        # Test no match
        results = client.get_outcomes("NonExistent")
        assert len(results) == 0

    @patch("requests.Session.get")
    def test_get_outcome_results(self, mock_get, client):
        """Test getting gene-level associations for a phenotype."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"gene_id": "ENSG00000162594", "symbol": "IL23R", "p_value": 1e-10},
            {"gene_id": "ENSG00000096968", "symbol": "JAK2", "p_value": 1e-8}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        results = client.get_outcome_results("1")
        assert len(results) == 2
        assert results[0]["symbol"] == "IL23R"
        assert mock_get.called
        assert "/outcome/1/results" in mock_get.call_args[0][0]

    @patch("requests.Session.get")
    def test_get_gene_results(self, mock_get, client):
        """Test getting phenotype associations for a specific gene."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"outcome_id": "1", "label": "Crohn's Disease", "p_value": 1e-10},
            {"outcome_id": "2", "label": "Ulcerative Colitis", "p_value": 1e-5}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        results = client.get_gene_results("ENSG00000162594")
        assert len(results) == 2
        assert results[0]["label"] == "Crohn's Disease"
        assert "/gene/ENSG00000162594/results" in mock_get.call_args[0][0]

    @patch("requests.Session.get")
    def test_caching_logic(self, mock_get, client):
        """Test that the internal cache prevents duplicate requests."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "1", "label": "Test"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # First call should hit the API
        client.get_outcomes("Test")
        assert mock_get.call_count == 1

        # Second call with same endpoint (via get_outcomes) should use cache
        # Note: get_outcomes calls _get("/outcome")
        client.get_outcomes("Test")
        assert mock_get.call_count == 1  # Still 1

    @patch("requests.Session.get")
    def test_api_failure_handling(self, mock_get, client):
        """Test that API failures are handled gracefully."""
        mock_get.side_effect = requests.exceptions.HTTPError("API Down")
        
        # Test get_outcomes failure
        results = client.get_outcomes("Crohn")
        assert results == []

        # Test get_outcome_results failure
        results = client.get_outcome_results("1")
        assert results == []

        # Test get_gene_results failure
        results = client.get_gene_results("ENSG123")
        assert results == []
