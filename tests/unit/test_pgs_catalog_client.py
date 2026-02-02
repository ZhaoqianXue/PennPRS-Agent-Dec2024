import unittest
from unittest.mock import patch, MagicMock
from src.server.core.pgs_catalog_client import PGSCatalogClient

class TestPGSCatalogClient(unittest.TestCase):
    def setUp(self):
        self.client = PGSCatalogClient()

    @patch('src.server.core.pgs_catalog_client.requests.get')
    def test_search_scores_success(self, mock_get):
        """Test search_scores correctly handles the trait-then-id search flow."""
        # 1. Mock response for trait search
        mock_trait_response = MagicMock()
        mock_trait_response.status_code = 200
        mock_trait_response.json.return_value = {
            "results": [
                {
                    "id": "EFO_0000001", 
                    "associated_pgs_ids": ["PGS000001"],
                    "child_associated_pgs_ids": ["PGS000002"]
                }
            ]
        }
        
        mock_get.return_value = mock_trait_response

        # Call method
        results = self.client.search_scores("Alzheimer")

        # Assert
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "PGS000001")
        self.assertEqual(results[1]["id"], "PGS000002")
        mock_get.assert_called_once()

    @patch('src.server.core.pgs_catalog_client.requests.get')
    def test_get_score_details_success(self, mock_get):
        """Test fetching score details."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "PGS000001", "trait_reported": "Alzheimer's disease"}
        mock_get.return_value = mock_response

        # Call method
        details = self.client.get_score_details("PGS000001")

        # Assert
        self.assertIsNotNone(details)
        self.assertEqual(details["trait_reported"], "Alzheimer's disease")

    @patch('src.server.core.pgs_catalog_client.requests.get')
    def test_get_score_performance_success(self, mock_get):
        """Test fetching score performance results."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"score_id": "PGS000001", "effect_sizes": [{"name_short": "AUC", "estimate": 0.8}]}
            ]
        }
        mock_get.return_value = mock_response

        # Call method
        performance = self.client.get_score_performance("PGS000001")

        # Assert
        self.assertEqual(len(performance), 1)
        self.assertEqual(performance[0]["score_id"], "PGS000001")

if __name__ == '__main__':
    unittest.main()
