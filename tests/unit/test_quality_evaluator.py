"""
Unit Tests for Module 1: QualityEvaluator.
Verifies metric extraction from raw metadata.
"""
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.server.core.quality_evaluator import QualityEvaluator

class TestQualityEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = QualityEvaluator()

    def test_extract_metrics_full(self):
        """ Test extracting metrics from a complete model card """
        card = {
            "metrics": {"AUC": 0.75, "R2": 0.12},
            "sample_size": 60000,
            "num_variants": 1500000,
            "publication": {"date": "2021-06-15"}
        }
        metrics = self.evaluator.extract_metrics(card)
        self.assertEqual(metrics.auc, 0.75)
        self.assertEqual(metrics.r2, 0.12)
        self.assertEqual(metrics.sample_size, 60000)
        self.assertEqual(metrics.num_variants, 1500000)
        self.assertEqual(metrics.publication_year, 2021)
        self.assertTrue(metrics.is_polygenic)

    def test_extract_metrics_minimal(self):
        """ Test extraction with minimal information """
        card = {
            "num_variants": 10
        }
        metrics = self.evaluator.extract_metrics(card)
        self.assertEqual(metrics.num_variants, 10)
        self.assertFalse(metrics.is_polygenic)
        self.assertIsNone(metrics.auc)

    def test_empty_card(self):
        """ Test extraction from an empty card """
        card = {}
        metrics = self.evaluator.extract_metrics(card)
        self.assertIsNone(metrics.publication_year)
        self.assertFalse(metrics.is_polygenic)

if __name__ == '__main__':
    unittest.main()
