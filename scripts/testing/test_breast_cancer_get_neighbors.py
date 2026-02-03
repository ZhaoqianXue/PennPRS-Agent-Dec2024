#!/usr/bin/env python3
"""
Test genetic_graph_get_neighbors for "Breast cancer" query.
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.server.core.tools.genetic_graph_tools import genetic_graph_get_neighbors
from src.server.modules.knowledge_graph.service import KnowledgeGraphService

def main():
    print("="*80)
    print("Testing genetic_graph_get_neighbors for 'Breast cancer'")
    print("="*80)
    print()
    
    # Initialize KnowledgeGraphService
    print("Initializing KnowledgeGraphService...")
    kg_service = KnowledgeGraphService()
    print("KnowledgeGraphService ready.\n")
    
    # Test query
    query_trait = "Breast cancer"
    print(f"Query trait: '{query_trait}'")
    print()
    
    # Call genetic_graph_get_neighbors
    print("Calling genetic_graph_get_neighbors...")
    result = genetic_graph_get_neighbors(
        kg_service=kg_service,
        trait_id=query_trait,
        rg_z_threshold=2.0,
        h2_z_threshold=2.0,
        limit=10
    )
    
    print()
    print("="*80)
    print("Results:")
    print("="*80)
    print()
    
    # Check if it's an error
    if hasattr(result, 'error_type'):
        print(f"❌ Error: {result.error_type}")
        print(f"   Message: {result.error_message}")
        print()
        if hasattr(result, 'context'):
            print("Context:")
            print(json.dumps(result.context, indent=2, ensure_ascii=False))
    else:
        # Success case
        print(f"✅ Success!")
        print()
        print(f"Query trait: {result.query_trait or 'N/A'}")
        print(f"Resolved by: {result.resolved_by or 'N/A'}")
        print(f"Resolution confidence: {result.resolution_confidence or 'N/A'}")
        print(f"Target trait: {result.target_trait}")
        print(f"Target h2_meta: {result.target_h2_meta}")
        print(f"Number of neighbors: {len(result.neighbors)}")
        print()
        
        if result.neighbors:
            print("Neighbors:")
            print("-" * 80)
            for i, neighbor in enumerate(result.neighbors, 1):
                print(f"{i}. {neighbor.trait_id}")
                print(f"   Domain: {neighbor.domain}")
                print(f"   rg_meta: {neighbor.rg_meta:.4f}")
                print(f"   rg_z_meta: {neighbor.rg_z_meta:.4f}")
                print(f"   h2_meta: {neighbor.h2_meta:.4f}")
                print(f"   transfer_score: {neighbor.transfer_score:.4f}")
                print(f"   n_correlations: {neighbor.n_correlations}")
                print()
        else:
            print("⚠️  No neighbors found (may be filtered by thresholds)")
            print()
            print("Trying with lower thresholds (rg_z=1.0, h2_z=1.0)...")
            result_low = genetic_graph_get_neighbors(
                kg_service=kg_service,
                trait_id=query_trait,
                rg_z_threshold=1.0,
                h2_z_threshold=1.0,
                limit=10
            )
            
            if hasattr(result_low, 'error_type'):
                print(f"❌ Still error with lower thresholds: {result_low.error_type}")
            elif result_low.neighbors:
                print(f"✅ Found {len(result_low.neighbors)} neighbors with lower thresholds:")
                for i, neighbor in enumerate(result_low.neighbors[:5], 1):
                    print(f"   {i}. {neighbor.trait_id} (rg_z={neighbor.rg_z_meta:.2f}, h2_z={neighbor.h2_meta:.4f})")
            else:
                print("⚠️  Still no neighbors found even with lower thresholds")

if __name__ == "__main__":
    main()
