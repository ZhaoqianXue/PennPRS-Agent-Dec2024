#!/usr/bin/env python3
"""
Test trait resolution for "Breast cancer" to see all candidates.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.server.modules.knowledge_graph.service import KnowledgeGraphService

def main():
    print("="*80)
    print("Testing trait resolution for 'Breast cancer'")
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
    
    # Call resolve_trait_id
    print("Calling resolve_trait_id...")
    resolution = kg_service.resolve_trait_id(query_trait, max_candidates=20)
    
    print()
    print("="*80)
    print("Resolution Results:")
    print("="*80)
    print()
    
    print(f"Resolved trait ID: {resolution.get('resolved_trait_id')}")
    print(f"Method: {resolution.get('method')}")
    print(f"Confidence: {resolution.get('confidence')}")
    print(f"Rationale: {resolution.get('rationale')}")
    print()
    
    candidates = resolution.get('candidates', [])
    print(f"Total candidates: {len(candidates)}")
    print()
    
    if candidates:
        print("All candidates:")
        print("-" * 80)
        for i, cand in enumerate(candidates, 1):
            trait_id = cand.get('trait_id', 'N/A')
            score = cand.get('score', 'N/A')
            domain = cand.get('domain', 'N/A')
            neoplasm_like = cand.get('neoplasm_like', False)
            proxy_like = cand.get('proxy_like', False)
            
            print(f"{i}. {trait_id}")
            print(f"   Score: {score}, Domain: {domain}")
            print(f"   Neoplasm-like: {neoplasm_like}, Proxy-like: {proxy_like}")
            print()
    
    # Check which candidates have neighbors
    print("="*80)
    print("Checking which candidates have neighbors in GC file:")
    print("="*80)
    print()
    
    if not kg_service._ensure_aggregators():
        print("❌ Aggregators not initialized")
        return
    
    edge_agg = kg_service._edge_aggregator
    if edge_agg:
        for i, cand in enumerate(candidates[:10], 1):
            trait_id = cand.get('trait_id')
            if trait_id:
                neighbors = edge_agg.get_neighbor_traits(trait_id)
                has_neighbors = len(neighbors) > 0
                status = "✓" if has_neighbors else "✗"
                print(f"{status} {trait_id}: {len(neighbors)} neighbors")

if __name__ == "__main__":
    main()
