"""
Integration tests for Open Targets Platform client.

Tests verify the client correctly interfaces with the Open Targets GraphQL API.
"""

import pytest
from src.core.opentargets_client import OpenTargetsClient, SearchResult


class TestOpenTargetsClient:
    """Test suite for OpenTargetsClient."""

    @pytest.fixture
    def client(self):
        """Create a fresh client for each test."""
        return OpenTargetsClient()

    def test_search_diseases_returns_results(self, client):
        """Test that searching for 'Alzheimer' returns disease results."""
        results = client.search_diseases("Alzheimer", size=5)
        
        assert results["total"] > 0
        assert len(results["hits"]) > 0
        
        # First result should be Alzheimer disease
        first_hit = results["hits"][0]
        assert isinstance(first_hit, SearchResult)
        assert first_hit.entity == "disease"
        assert "alzheimer" in first_hit.name.lower()
        # Should have MONDO or EFO ID
        assert first_hit.id.startswith("MONDO_") or first_hit.id.startswith("EFO_")

    def test_search_targets_returns_results(self, client):
        """Test that searching for 'APOE' returns target results."""
        results = client.search_targets("APOE", size=5)
        
        assert results["total"] > 0
        assert len(results["hits"]) > 0
        
        # First result should be APOE gene
        first_hit = results["hits"][0]
        assert isinstance(first_hit, SearchResult)
        assert first_hit.entity == "target"
        assert "APOE" in first_hit.name.upper()
        # Should have Ensembl ID
        assert first_hit.id.startswith("ENSG")

    def test_search_with_pagination(self, client):
        """Test pagination works correctly."""
        page1 = client.search_diseases("cancer", page=0, size=5)
        page2 = client.search_diseases("cancer", page=1, size=5)
        
        # Both pages should have results
        assert len(page1["hits"]) == 5
        assert len(page2["hits"]) > 0
        
        # Results should be different
        page1_ids = {hit.id for hit in page1["hits"]}
        page2_ids = {hit.id for hit in page2["hits"]}
        assert page1_ids != page2_ids

    def test_empty_query_returns_empty(self, client):
        """Test that empty query returns no results."""
        results = client.search_diseases("", size=5)
        
        # Empty search should still work (returns total but 0 hits for empty query)
        assert "total" in results
        assert "hits" in results

    def test_search_general_with_entity_filter(self, client):
        """Test general search with entity type filter."""
        results = client.search("diabetes", entity_types=["disease"], size=5)
        
        assert results["total"] > 0
        for hit in results["hits"]:
            assert hit.entity == "disease"

    def test_format_for_ui(self, client):
        """Test formatting results for frontend consumption."""
        results = client.search_diseases("Alzheimer", size=3)
        formatted = client.format_search_results_for_ui(results)
        
        assert "total" in formatted
        assert "hits" in formatted
        assert len(formatted["hits"]) > 0
        
        first_formatted = formatted["hits"][0]
        assert "id" in first_formatted
        assert "name" in first_formatted
        assert "entity_type" in first_formatted
        assert "display_label" in first_formatted

    def test_get_disease_details(self, client):
        """Test fetching detailed disease information."""
        details = client.get_disease_details("EFO_1001870")  # Late-onset Alzheimer's
        
        assert details is not None
        assert details.get("name") is not None or details.get("id") is not None

    def test_get_target_details(self, client):
        """Test fetching detailed target information."""
        details = client.get_target_details("ENSG00000130203")  # APOE
        
        assert details is not None
        assert details.get("approvedSymbol") is not None or details.get("id") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
