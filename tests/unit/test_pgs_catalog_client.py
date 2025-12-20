import unittest
from unittest.mock import patch, MagicMock
from src.core.pgs_catalog_client import PGSCatalogClient

class TestPGSCatalogClient(unittest.TestCase):
    def setUp(self):
        self.client = PGSCatalogClient()

    @patch('src.core.pgs_catalog_client.requests.get')
    def test_search_scores_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "PGS000001", "name": "Score 1"},
                {"id": "PGS000002", "name": "Score 2"}
            ]
        }
        mock_get.return_value = mock_response

        # Call method
        results = self.client.search_scores("Alzheimer")

        # Assert
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "PGS000001")
        mock_get.assert_called_once()

    @patch('src.core.pgs_catalog_client.requests.get')
    def test_get_score_metadata_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "PGS000001", "trait_reported": "Alzheimer's disease"}
        mock_get.return_value = mock_response

        # Call method
        metadata = self.client.get_score_metadata("PGS000001")

        # Assert
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["trait_reported"], "Alzheimer's disease")

if __name__ == '__main__':
    unittest.main()
