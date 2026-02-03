#!/usr/bin/env python3
"""
Test trait synonym expansion functionality.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.server.core.trait_synonym_expander import get_trait_expander
from src.server.core.tools.genetic_graph_tools import genetic_graph_get_neighbors
from src.server.modules.knowledge_graph.service import KnowledgeGraphService

def main():
    print("="*80)
    print("Testing Trait Synonym Expansion")
    print("="*80)
    print()
    
    # Test 1: Synonym expansion
    print("Test 1: Synonym Expansion")
    print("-"*80)
    expander = get_trait_expander()
    
    test_queries = ["Breast cancer", "Malignant neoplasm of breast"]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = expander.expand_trait_query(query, max_synonyms=10)
        print(f"  Method: {result.method}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Expanded queries ({len(result.expanded_queries)}):")
        for i, exp_query in enumerate(result.expanded_queries, 1):
            print(f"    {i}. {exp_query}")
        print(f"  Synonyms ({len(result.synonyms)}):")
        for i, syn in enumerate(result.synonyms[:5], 1):
            print(f"    {i}. {syn.synonym} ({syn.relationship}, {syn.confidence})")
    
    # Test 2: genetic_graph_get_neighbors with expansion
    print("\n" + "="*80)
    print("Test 2: genetic_graph_get_neighbors with Synonym Expansion")
    print("="*80)
    print()
    
    kg_service = KnowledgeGraphService()
    
    query = "Breast cancer"
    print(f"Query: '{query}'")
    print()
    
    # With expansion
    print("With synonym expansion:")
    result_expanded = genetic_graph_get_neighbors(
        kg_service=kg_service,
        trait_id=query,
        rg_z_threshold=2.0,
        h2_z_threshold=2.0,
        limit=10,
        use_synonym_expansion=True
    )
    
    if hasattr(result_expanded, 'error_type'):
        print(f"  ❌ Error: {result_expanded.error_type}")
        print(f"     {result_expanded.error_message}")
    else:
        print(f"  ✅ Success!")
        print(f"     Target trait: {result_expanded.target_trait}")
        print(f"     Neighbors found: {len(result_expanded.neighbors)}")
        if result_expanded.neighbors:
            print(f"     Top 5 neighbors:")
            for i, neighbor in enumerate(result_expanded.neighbors[:5], 1):
                print(f"       {i}. {neighbor.trait_id}")
    
    print()
    
    # Without expansion (for comparison)
    print("Without synonym expansion:")
    result_no_expansion = genetic_graph_get_neighbors(
        kg_service=kg_service,
        trait_id=query,
        rg_z_threshold=2.0,
        h2_z_threshold=2.0,
        limit=10,
        use_synonym_expansion=False
    )
    
    if hasattr(result_no_expansion, 'error_type'):
        print(f"  ❌ Error: {result_no_expansion.error_type}")
        print(f"     {result_no_expansion.error_message}")
    else:
        print(f"  ✅ Success!")
        print(f"     Target trait: {result_no_expansion.target_trait}")
        print(f"     Neighbors found: {len(result_no_expansion.neighbors)}")
        if result_no_expansion.neighbors:
            print(f"     Top 5 neighbors:")
            for i, neighbor in enumerate(result_no_expansion.neighbors[:5], 1):
                print(f"       {i}. {neighbor.trait_id}")
    
    print("\n" + "="*80)
    print("Test complete!")

if __name__ == "__main__":
    main()
