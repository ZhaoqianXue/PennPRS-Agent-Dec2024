import unittest
from unittest.mock import patch, MagicMock
from src.server.core.pennprs_client import PennPRSClient

class TestPennPRSClient(unittest.TestCase):
    def setUp(self):
        self.client = PennPRSClient(email="test@example.com")

    @patch('src.server.core.pennprs_client.requests.post')
    def test_add_single_job_success(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"job_id": "12345", "status": "submitted"}
        mock_post.return_value = mock_response

        # Call method
        result = self.client.add_single_job(
            job_name="test_job",
            job_type="single",
            job_methods=["method1"],
            job_ensemble=False,
            traits_source=["source"],
            traits_detail=["detail"],
            traits_type=["type"],
            traits_name=["trait"],
            traits_population=["pop"],
            traits_col=[{"id": "1"}]
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["job_id"], "12345")
        mock_post.assert_called_once()
        
    @patch('src.server.core.pennprs_client.requests.get')
    def test_get_job_status_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "12345", "status": "completed"},
            {"id": "67890", "status": "running"}
        ]
        mock_get.return_value = mock_response

        # Call method
        status = self.client.get_job_status("12345")
        
        # Assert
        self.assertEqual(status, "completed")
        
    @patch('src.server.core.pennprs_client.requests.get')
    def test_download_results_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake zip content"
        mock_get.return_value = mock_response
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
             with patch('os.makedirs') as mock_makedirs:
                result_path = self.client.download_results("12345", output_dir="test_output")
                
                self.assertIsNotNone(result_path)
                self.assertIn("12345.zip", result_path)

if __name__ == '__main__':
    unittest.main()
