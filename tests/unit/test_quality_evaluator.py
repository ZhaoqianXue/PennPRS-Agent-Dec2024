"""
Unit Tests for Module 1: QualityEvaluator.
Implements specific test cases for Gold/Silver/Bronze tiers based on the proposal.
"""
import unittest
import sys
import os

# Add src to path if needed (though running from root usually works)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.server.core.quality_evaluator import QualityEvaluator, RecommendationGrade
except ImportError:
    # Allow test to be written before implementation exists (TDD Red Phase)
    QualityEvaluator = None
    RecommendationGrade = None

class TestQualityEvaluator(unittest.TestCase):
    def setUp(self):
        if QualityEvaluator is None:
            self.skipTest("QualityEvaluator not implemented yet")
        self.evaluator = QualityEvaluator()

    def test_gold_tier_perfect_model(self):
        """ Test Tier 1: Gold Criteria (High Sample, Recent, Polygenic, Good Metrics) """
        card = {
            "metrics": {"AUC": 0.75, "R2": 0.12},
            "sample_size": 60000,          # > 50k
            "num_variants": 1500000,       # > 1M (well above 100)
            "publication": {"date": "2021-06-15"} # >= 2020
        }
        result = self.evaluator.evaluate(card)
        self.assertEqual(result, RecommendationGrade.GOLD)

    def test_silver_tier_baseline(self):
        """ Test Tier 2: Silver Criteria (Medium Sample, Post-2018) """
        card = {
            "metrics": {"AUC": 0.60},      # Low AUC but present
            "sample_size": 20000,          # > 10k
            "num_variants": 80,            # > 50 (but < 100? No, Tier 2 requires > 50. Let's say 80 is fine for Silver).
                                           # Wait, proposal says > 50 is base.
                                           # Let's say 80 variants.
            "publication": {"date": "2019-01-01"} # >= 2018
        }
        result = self.evaluator.evaluate(card)
        self.assertEqual(result, RecommendationGrade.SILVER)

    def test_bronze_tier_old(self):
        """ Test Tier 3: Bronze (Old date) """
        card = {
            "metrics": {"AUC": 0.8},
            "sample_size": 100000,
            "num_variants": 200,
            "publication": {"date": "2015-01-01"} # < 2018
        }
        result = self.evaluator.evaluate(card)
        self.assertEqual(result, RecommendationGrade.BRONZE)

    def test_bronze_tier_oligogenic(self):
        """ Test Tier 3: Bronze (Too few variants) """
        card = {
            "metrics": {"AUC": 0.8},
            "sample_size": 100000,
            "num_variants": 10,           # < 50
            "publication": {"date": "2022-01-01"}
        }
        result = self.evaluator.evaluate(card)
        self.assertEqual(result, RecommendationGrade.BRONZE)

    def test_missing_data_defaults(self):
        """ Test Robustness: Handles missing fields gracefully """
        card = {} # Empty
        result = self.evaluator.evaluate(card)
        self.assertEqual(result, RecommendationGrade.BRONZE)

if __name__ == '__main__':
    unittest.main()
