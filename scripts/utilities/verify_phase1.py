"""
Verification Script for Phase 1.
Validates Module 1 (Quality) and Module 2 (Knowledge Graph) APIs.
"""
import sys
import os
from unittest.mock import MagicMock

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    from src.server.core.quality_evaluator import QualityEvaluator, RecommendationGrade
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.genetic_correlation.models import GeneticCorrelationResult, GeneticCorrelationSource
except ImportError as e:
    print(f"FAILED to import Phase 1 Modules: {e}")
    sys.exit(1)

def verify_module_1():
    print("\n--- Verifying Module 1: Quality Evaluator ---")
    evaluator = QualityEvaluator()
    
    # 1. Gold Case
    card_gold = {
        "metrics": {"AUC": 0.75, "R2": 0.12},
        "sample_size": 100000,
        "num_variants": 200,
        "publication": {"date": "2021-06-15"}
    }
    result_gold = evaluator.evaluate(card_gold)
    grade = result_gold.grade
    print(f"Gold Case Grade: {grade} (Expected: GOLD)")
    print(f"Reasoning: {result_gold.reasoning}")
    assert grade == RecommendationGrade.GOLD, "Failed Gold Case"
    assert len(result_gold.reasoning) > 0, "Missing reasoning for Gold"
    
    # 2. Bronze Case
    card_bronze = {
        "metrics": {"AUC": 0.5},
        "sample_size": 2000,
        "num_variants": 20,
        "publication": {"date": "2015-01-01"}
    }
    result_bronze = evaluator.evaluate(card_bronze)
    grade_b = result_bronze.grade
    print(f"Bronze Case Grade: {grade_b} (Expected: BRONZE)")
    print(f"Reasoning: {result_bronze.reasoning}")
    assert grade_b == RecommendationGrade.BRONZE, "Failed Bronze Case"
    assert len(result_bronze.reasoning) > 0, "Missing reasoning for Bronze"
    print("Module 1 Passed.")

def verify_module_2():
    print("\n--- Verifying Module 2: Knowledge Graph ---")
    
    # Mock Client
    mock_client = MagicMock()
    # Mock return value (Object with attributes)
    res1 = MagicMock()
    res1.id2 = "EFO_TEST"
    res1.trait_2_name = "Test Disease"
    res1.rg = 0.8
    res1.p = 0.0001
    mock_client.get_correlations.return_value = [res1]
    
    service = KnowledgeGraphService(client=mock_client)
    
    # Query
    print("Querying neighbors for 'EFO_Query'...")
    graph = service.get_neighbors("EFO_Query")
    
    print(f"Nodes Found: {len(graph.nodes)}")
    print(f"Edges Found: {len(graph.edges)}")
    
    if len(graph.edges) > 0:
        print(f"Edge 1: Source={graph.edges[0].source} Target={graph.edges[0].target} rg={graph.edges[0].rg}")
        assert graph.edges[0].rg == 0.8
        print("Module 2 Passed.")
    else:
        print("Module 2 Failed (No edges returned)")
        sys.exit(1)

if __name__ == "__main__":
    verify_module_1()
    verify_module_2()
    print("\nPhase 1 verification successful.")
