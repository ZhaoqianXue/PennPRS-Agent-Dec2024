import sys
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    def test_search_traits_success(self, mock_get):
        """Test search_traits returns raw trait results."""
        mock_trait_response = MagicMock()
        mock_trait_response.status_code = 200
        mock_trait_response.json.return_value = {
            "results": [
                {
                    "id": "EFO_0000001",
                    "label": "Example Trait",
                    "associated_pgs_ids": ["PGS000001"],
                    "child_associated_pgs_ids": ["PGS000002"]
                }
            ]
        }
        mock_get.return_value = mock_trait_response

        traits = self.client.search_traits("Example")

        self.assertEqual(len(traits), 1)
        self.assertEqual(traits[0]["id"], "EFO_0000001")
        self.assertEqual(traits[0]["label"], "Example Trait")
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
        mock_response.headers = {}
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

    @patch("src.server.core.pgs_catalog_client.time.sleep")
    @patch("src.server.core.pgs_catalog_client.random.uniform", return_value=0.0)
    @patch('src.server.core.pgs_catalog_client.requests.get')
    def test_retries_on_429_then_succeeds(self, mock_get, _mock_jitter, mock_sleep):
        """Test 429 rate limit triggers a retry and eventually succeeds."""
        r429 = MagicMock()
        r429.status_code = 429
        r429.headers = {"Retry-After": "0"}

        r200 = MagicMock()
        r200.status_code = 200
        r200.headers = {}
        r200.json.return_value = {"results": [{"id": "EFO_0000001"}]}

        mock_get.side_effect = [r429, r200]

        out = self.client.search_traits("Example")
        self.assertEqual(len(out), 1)
        self.assertEqual(mock_get.call_count, 2)
        self.assertGreaterEqual(mock_sleep.call_count, 1)

    @patch('src.server.core.pgs_catalog_client.requests.get')
    def test_list_performance_all_clamps_limit(self, mock_get):
        """Test performance/all limit is clamped to avoid 400."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"size": 0, "count": 0, "next": None, "previous": None, "results": []}
        mock_get.return_value = mock_response

        self.client.list_performance_all(limit=500, offset=0)
        self.assertTrue(mock_get.called)
        params = mock_get.call_args.kwargs.get("params") or {}
        self.assertEqual(params.get("limit"), self.client.MAX_PAGE_SIZE)

if __name__ == '__main__':
    unittest.main()
