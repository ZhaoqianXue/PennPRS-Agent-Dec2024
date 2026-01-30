"""
Unit Tests for Module 2 Enhanced: KnowledgeGraphService.
Tests for:
1. Node Heritability integration
2. Weighted Scoring (rg^2 * h2)
3. ID Mapping
"""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.knowledge_graph.models import (
        KnowledgeGraphResult, 
        KnowledgeGraphNode, 
        GeneticCorrelationEdge,
        PrioritizedNeighbor
    )
    from src.server.modules.genetic_correlation.models import GeneticCorrelationResult, GeneticCorrelationSource
    from src.server.modules.heritability.models import HeritabilityEstimate, HeritabilitySource
except ImportError as e:
    # TDD Red Phase: Some classes may not exist yet
    print(f"Import warning: {e}")
    KnowledgeGraphService = None
    PrioritizedNeighbor = None


class TestKnowledgeGraphEnhancements(unittest.TestCase):
    """Test enhanced KnowledgeGraph functionality per sop.md Module 2 spec."""
    
    def setUp(self):
        if KnowledgeGraphService is None:
            self.skipTest("KnowledgeGraphService not implemented yet")
        
        # Mock the GC client
        self.mock_gc_client = MagicMock()
        
        # Mock the heritability client
        self.mock_h2_client = MagicMock()
        
        # Create service with both clients injected
        self.service = KnowledgeGraphService(
            gc_client=self.mock_gc_client,
            h2_client=self.mock_h2_client
        )
    
    # ============ Phase 2: Node Heritability Tests ============
    
    def test_get_neighbors_populates_h2_from_heritability_client(self):
        """
        Test that get_neighbors queries heritability client and populates h2 attribute.
        Addresses: "Node Heritability: Heritability ($h^2$) attributes are currently None"
        """
        # Arrange: Mock GC result
        mock_gc_result = MagicMock()
        mock_gc_result.id2 = "123"
        mock_gc_result.trait_2_name = "Type 2 Diabetes"
        mock_gc_result.rg = 0.5
        mock_gc_result.p = 0.001
        mock_gc_result.se = 0.05
        
        self.mock_gc_client.get_correlations.return_value = [mock_gc_result]
        
        # Mock heritability result
        mock_h2_estimate = MagicMock(spec=HeritabilityEstimate)
        mock_h2_estimate.h2_obs = 0.42
        self.mock_h2_client.search_trait.return_value = [mock_h2_estimate]
        
        # Act
        result = self.service.get_neighbors("456")
        
        # Assert: h2 should be populated
        self.assertEqual(len(result.nodes), 1)
        node = result.nodes[0]
        self.assertEqual(node.h2, 0.42)
        
        # Verify heritability client was called with trait name
        self.mock_h2_client.search_trait.assert_called_with("Type 2 Diabetes", limit=1)
    
    def test_get_neighbors_h2_none_when_heritability_not_found(self):
        """
        Test that h2 is None when heritability client returns no results.
        """
        # Arrange
        mock_gc_result = MagicMock()
        mock_gc_result.id2 = "789"
        mock_gc_result.trait_2_name = "Unknown Trait"
        mock_gc_result.rg = 0.3
        mock_gc_result.p = 0.01
        mock_gc_result.se = 0.1
        
        self.mock_gc_client.get_correlations.return_value = [mock_gc_result]
        self.mock_h2_client.search_trait.return_value = []  # No h2 found
        
        # Act
        result = self.service.get_neighbors("100")
        
        # Assert
        self.assertEqual(len(result.nodes), 1)
        self.assertIsNone(result.nodes[0].h2)
    
    # ============ Phase 3: Weighted Scoring Tests ============
    
    def test_get_prioritized_neighbors_returns_scored_list(self):
        """
        Test ranking neighbors by weighted score: rg^2 * h2.
        Addresses: "Weighted Scoring: Ranking neighbors by rg^2 * h2 is not yet implemented"
        """
        if PrioritizedNeighbor is None:
            self.skipTest("PrioritizedNeighbor model not implemented yet")
        
        # Arrange: Two neighbors with different rg and h2
        mock_gc_1 = MagicMock()
        mock_gc_1.id2 = "101"
        mock_gc_1.trait_2_name = "Trait A"
        mock_gc_1.rg = 0.5  # rg^2 = 0.25
        mock_gc_1.p = 0.001
        mock_gc_1.se = 0.05
        
        mock_gc_2 = MagicMock()
        mock_gc_2.id2 = "102"
        mock_gc_2.trait_2_name = "Trait B"
        mock_gc_2.rg = 0.8  # rg^2 = 0.64
        mock_gc_2.p = 0.002
        mock_gc_2.se = 0.06
        
        self.mock_gc_client.get_correlations.return_value = [mock_gc_1, mock_gc_2]
        
        # Mock heritability: Trait A has h2=0.6, Trait B has h2=0.3
        def h2_side_effect(trait_name, limit=1):
            h2_map = {"Trait A": 0.6, "Trait B": 0.3}
            if trait_name in h2_map:
                mock_est = MagicMock(spec=HeritabilityEstimate)
                mock_est.h2_obs = h2_map[trait_name]
                return [mock_est]
            return []
        
        self.mock_h2_client.search_trait.side_effect = h2_side_effect
        
        # Expected scores:
        # Trait A: 0.5^2 * 0.6 = 0.25 * 0.6 = 0.15
        # Trait B: 0.8^2 * 0.3 = 0.64 * 0.3 = 0.192
        # Trait B should rank higher
        
        # Act
        result = self.service.get_prioritized_neighbors("999")
        
        # Assert: Should return list sorted by score descending
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].trait_id, "102")  # Trait B first (score=0.192)
        self.assertEqual(result[1].trait_id, "101")  # Trait A second (score=0.15)
        self.assertAlmostEqual(result[0].score, 0.192, places=3)
        self.assertAlmostEqual(result[1].score, 0.15, places=3)
    
    def test_get_prioritized_neighbors_excludes_nodes_without_h2(self):
        """
        Test that nodes without h2 are excluded from prioritized results.
        """
        if PrioritizedNeighbor is None:
            self.skipTest("PrioritizedNeighbor model not implemented yet")
        
        # Arrange
        mock_gc_1 = MagicMock()
        mock_gc_1.id2 = "201"
        mock_gc_1.trait_2_name = "Trait With H2"
        mock_gc_1.rg = 0.7
        mock_gc_1.p = 0.001
        mock_gc_1.se = 0.05
        
        mock_gc_2 = MagicMock()
        mock_gc_2.id2 = "202"
        mock_gc_2.trait_2_name = "Trait Without H2"
        mock_gc_2.rg = 0.9
        mock_gc_2.p = 0.002
        mock_gc_2.se = 0.03
        
        self.mock_gc_client.get_correlations.return_value = [mock_gc_1, mock_gc_2]
        
        def h2_side_effect(trait_name, limit=1):
            if trait_name == "Trait With H2":
                mock_est = MagicMock(spec=HeritabilityEstimate)
                mock_est.h2_obs = 0.5
                return [mock_est]
            return []  # No h2 for "Trait Without H2"
        
        self.mock_h2_client.search_trait.side_effect = h2_side_effect
        
        # Act
        result = self.service.get_prioritized_neighbors("888")
        
        # Assert: Only trait with h2 should be in results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].trait_id, "201")


class TestIDMapping(unittest.TestCase):
    """Test ID mapping between EFO IDs and GWAS Atlas Numeric IDs."""
    
    def setUp(self):
        # We'll test this through the GWASAtlasGCClient
        try:
            from src.server.modules.genetic_correlation.gwas_atlas_client import GWASAtlasGCClient
            self.client_class = GWASAtlasGCClient
        except ImportError:
            self.skipTest("GWASAtlasGCClient not available")
    
    def test_get_trait_name_by_id(self):
        """Test forward lookup: numeric ID -> trait name."""
        # This uses the existing _id_map internally
        # The method should be publicly accessible
        client = self.client_class()
        
        # Check method exists
        self.assertTrue(hasattr(client, 'get_trait_name_by_id'))
        
        # If data is loaded, test actual lookup
        if client._id_map:
            first_id = next(iter(client._id_map.keys()))
            expected_name = client._id_map[first_id]
            result = client.get_trait_name_by_id(first_id)
            self.assertEqual(result, expected_name)
    
    def test_get_trait_id_by_name(self):
        """Test reverse lookup: trait name -> numeric ID."""
        client = self.client_class()
        
        # Check method exists
        self.assertTrue(hasattr(client, 'get_trait_id_by_name'))
        
        # If data is loaded, test actual lookup
        if client._id_map:
            first_id = next(iter(client._id_map.keys()))
            trait_name = client._id_map[first_id]
            result = client.get_trait_id_by_name(trait_name)
            # Should return the ID (could be int or str depending on implementation)
            self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
