"""
Unit Tests for Module 2: KnowledgeGraphService.
Tests the graph traversal logic using mocked GWAS Atlas client.
"""
import unittest
import sys
import os
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.knowledge_graph.models import KnowledgeGraphResult, GeneticCorrelationEdge
    # We also need GeneticCorrelationResult from genetic_correlation module for mocking
    from src.server.modules.genetic_correlation.models import GeneticCorrelationResult, GeneticCorrelationSource
except ImportError:
    # TDD Red Phase: Service doesn't exist yet
    KnowledgeGraphService = None
    KnowledgeGraphResult = None
    GeneticCorrelationResult = None
    GeneticCorrelationSource = None

class TestKnowledgeGraphService(unittest.TestCase):
    def setUp(self):
        if KnowledgeGraphService is None:
            self.skipTest("KnowledgeGraphService not implemented yet")
        
        # Mock the underlying client (GWASAtlasGCClient)
        self.mock_client = MagicMock()
        self.service = KnowledgeGraphService(client=self.mock_client)

    def test_get_neighbors_significant(self):
        """ Test basic traversal: Query Trait -> Get Significant Neighbors """
        # Mock GeneticCorrelationResult object
        mock_res1 = MagicMock()
        mock_res1.id2 = "EFO_00002"
        mock_res1.trait_2_name = "Disease B"
        mock_res1.rg = 0.6
        mock_res1.p = 0.001
        
        mock_res2 = MagicMock()
        mock_res2.id2 = "EFO_00003" 
        mock_res2.trait_2_name = "Disease C"
        mock_res2.rg = 0.1 # Weak correlation (No longer filtered by threshold)
        mock_res2.p = 0.20 # Insignificant (Above default 0.05)
        
        self.mock_client.get_correlations.return_value = [mock_res1, mock_res2]
        
        # Act: Get neighbors for EFO_00001
        # Default thresholds: p < 0.05
        result = self.service.get_neighbors("EFO_00001")
        
        # Assert
        # Should only return Disease B (Significant)
        self.assertEqual(len(result.edges), 1)
        edge = result.edges[0]
        self.assertEqual(edge.target, "EFO_00002")
        self.assertEqual(edge.rg, 0.6)
        
        # Verify call
        self.mock_client.get_correlations.assert_called_with("EFO_00001", p_threshold=0.05)

if __name__ == '__main__':
    unittest.main()
