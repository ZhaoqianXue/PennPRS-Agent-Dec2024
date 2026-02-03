#!/usr/bin/env python3
"""
Debug script to check trait resolution and neighbor lookup for cancer traits.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.server.modules.knowledge_graph.service import KnowledgeGraphService
from src.server.modules.genetic_correlation.gwas_atlas_client import GWASAtlasGCClient
from src.server.modules.heritability.gwas_atlas_client import GWASAtlasClient

def main():
    print("Initializing KnowledgeGraphService...")
    kg_service = KnowledgeGraphService()
    
    # Test trait: Breast cancer
    query_trait = "Breast cancer"
    print(f"\n{'='*80}")
    print(f"Testing trait resolution for: '{query_trait}'")
    print(f"{'='*80}\n")
    
    # Step 1: Check trait resolution
    print("Step 1: Resolving trait ID...")
    resolution = kg_service.resolve_trait_id(query_trait)
    print(f"  Resolution result:")
    print(f"    resolved_trait_id: {resolution.get('resolved_trait_id')}")
    print(f"    method: {resolution.get('method')}")
    print(f"    confidence: {resolution.get('confidence')}")
    print(f"    rationale: {resolution.get('rationale')}")
    
    candidates = resolution.get('candidates', [])
    print(f"\n  Top candidates:")
    for i, cand in enumerate(candidates[:5], 1):
        print(f"    {i}. {cand.get('trait_id')} (score: {cand.get('score')}, domain: {cand.get('domain')})")
    
    resolved_trait = resolution.get('resolved_trait_id')
    if not resolved_trait:
        print("\n  ERROR: Could not resolve trait!")
        return
    
    # Step 2: Check if trait node exists
    print(f"\nStep 2: Checking trait node for '{resolved_trait}'...")
    trait_node = kg_service.get_trait_node(resolved_trait)
    if trait_node:
        print(f"  ✓ Trait node found:")
        print(f"    h2_meta: {trait_node.h2_meta}")
        print(f"    h2_z_meta: {trait_node.h2_z_meta}")
        print(f"    n_studies: {trait_node.n_studies}")
        print(f"    domain: {trait_node.domain}")
    else:
        print(f"  ✗ Trait node NOT found!")
        return
    
    # Step 3: Check edge aggregator's neighbor lookup
    print(f"\nStep 3: Checking edge aggregator...")
    if not kg_service._ensure_aggregators():
        print("  ✗ Aggregators not initialized!")
        return
    
    edge_agg = kg_service._edge_aggregator
    if edge_agg:
        neighbor_traits = edge_agg.get_neighbor_traits(resolved_trait)
        print(f"  Found {len(neighbor_traits)} neighbor traits")
        if neighbor_traits:
            print(f"  First 10 neighbors:")
            for i, neighbor in enumerate(neighbor_traits[:10], 1):
                print(f"    {i}. {neighbor}")
        else:
            print(f"  ✗ No neighbors found!")
            
            # Debug: Check what traits are in the edge aggregator
            print(f"\n  Debugging edge aggregator...")
            print(f"    Total trait pairs: {len(edge_agg.get_all_trait_pairs())}")
            
            # Check if resolved_trait is in the neighbor dict
            if hasattr(edge_agg, '_trait_neighbors'):
                all_traits_with_neighbors = list(edge_agg._trait_neighbors.keys())
                print(f"    Traits with neighbors: {len(all_traits_with_neighbors)}")
                
                # Check for similar trait names
                print(f"\n    Searching for similar trait names...")
                query_lower = resolved_trait.lower()
                matches = [t for t in all_traits_with_neighbors if 'breast' in t.lower() or 'cancer' in t.lower()]
                print(f"    Found {len(matches)} traits containing 'breast' or 'cancer':")
                for match in matches[:10]:
                    neighbor_count = len(edge_agg._trait_neighbors.get(match, set()))
                    print(f"      - {match} ({neighbor_count} neighbors)")
    
    # Step 4: Check get_prioritized_neighbors_v2
    print(f"\nStep 4: Calling get_prioritized_neighbors_v2('{resolved_trait}')...")
    neighbors = kg_service.get_prioritized_neighbors_v2(
        trait_id=resolved_trait,
        rg_z_threshold=2.0,
        h2_z_threshold=2.0
    )
    print(f"  Found {len(neighbors)} prioritized neighbors")
    if neighbors:
        print(f"  Top 5 neighbors:")
        for i, n in enumerate(neighbors[:5], 1):
            print(f"    {i}. {n.trait_id}")
            print(f"       rg_meta={n.rg:.4f}, rg_z={n.rg_z}, h2_meta={n.h2:.4f}, score={n.score:.4f}")
    else:
        print(f"  ✗ No prioritized neighbors found!")
        
        # Try with lower thresholds
        print(f"\n  Trying with lower thresholds (rg_z=1.0, h2_z=1.0)...")
        neighbors_low = kg_service.get_prioritized_neighbors_v2(
            trait_id=resolved_trait,
            rg_z_threshold=1.0,
            h2_z_threshold=1.0
        )
        print(f"  Found {len(neighbors_low)} neighbors with lower thresholds")
        if neighbors_low:
            print(f"  Top 5 neighbors:")
            for i, n in enumerate(neighbors_low[:5], 1):
                print(f"    {i}. {n.trait_id}")
                print(f"       rg_meta={n.rg:.4f}, rg_z={n.rg_z}, h2_meta={n.h2:.4f}, h2_z={n.h2_z_meta if hasattr(n, 'h2_z_meta') else 'N/A'}")
    
    # Step 5: Check ID mapping
    print(f"\nStep 5: Checking ID to trait mapping...")
    if kg_service._id_to_trait:
        # Find breast cancer related IDs
        breast_ids = []
        for study_id, trait_name in kg_service._id_to_trait.items():
            if 'breast' in str(trait_name).lower() or 'cancer' in str(trait_name).lower():
                breast_ids.append((study_id, trait_name))
        
        print(f"  Found {len(breast_ids)} breast cancer related study IDs:")
        for study_id, trait_name in breast_ids[:10]:
            print(f"    ID {study_id}: {trait_name}")
            
            # Check if this ID has neighbors in GC file
            if edge_agg:
                neighbor_traits_for_id = edge_agg.get_neighbor_traits(trait_name)
                print(f"      -> {len(neighbor_traits_for_id)} neighbors")
    
    print(f"\n{'='*80}")
    print("Debug complete!")

if __name__ == "__main__":
    main()
