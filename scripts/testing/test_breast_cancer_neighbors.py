#!/usr/bin/env python3
"""
Simple test to check why breast cancer has no neighbors.
"""
import sys
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.server.core.config import get_data_path

def main():
    # Load metadata
    meta_file = get_data_path("data/heritability/gwas_atlas/gwas_atlas.tsv")
    print(f"Loading metadata from {meta_file}...")
    meta_df = pd.read_csv(meta_file, sep='\t', usecols=['id', 'uniqTrait', 'Trait'])
    
    # Build ID to trait mapping
    id_to_trait = {}
    for _, row in meta_df.iterrows():
        study_id = int(row['id']) if pd.notna(row['id']) else None
        trait = str(row['uniqTrait']) if pd.notna(row['uniqTrait']) else None
        if study_id is not None and trait is not None:
            id_to_trait[study_id] = trait
    
    print(f"Loaded {len(id_to_trait)} ID mappings")
    
    # Find breast cancer traits
    breast_traits = set()
    for _, row in meta_df.iterrows():
        trait = str(row['uniqTrait']) if pd.notna(row['uniqTrait']) else ""
        if 'breast' in trait.lower() and 'cancer' in trait.lower():
            breast_traits.add(trait)
    
    print(f"\nFound {len(breast_traits)} breast cancer traits:")
    for trait in sorted(breast_traits):
        print(f"  - {trait}")
    
    # Load GC file
    gc_file = get_data_path("data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv")
    print(f"\nLoading GC file from {gc_file}...")
    
    # Check which breast cancer IDs are in GC file
    breast_ids_in_gc = set()
    chunk_size = 100000
    
    for chunk in pd.read_csv(gc_file, sep='\t', chunksize=chunk_size, dtype={'id1': int, 'id2': int}):
        for bc_trait in breast_traits:
            # Find IDs for this trait
            trait_ids = [sid for sid, t in id_to_trait.items() if t == bc_trait]
            for tid in trait_ids:
                mask = (chunk['id1'] == tid) | (chunk['id2'] == tid)
                if mask.any():
                    breast_ids_in_gc.add(tid)
    
    print(f"\nBreast cancer study IDs found in GC file: {sorted(breast_ids_in_gc)}")
    
    # For each breast cancer trait, check how many neighbors it has
    print(f"\n{'='*80}")
    print("Checking neighbors for each breast cancer trait:")
    print(f"{'='*80}\n")
    
    for bc_trait in sorted(breast_traits):
        trait_ids = [sid for sid, t in id_to_trait.items() if t == bc_trait]
        print(f"Trait: {bc_trait}")
        print(f"  Study IDs: {trait_ids}")
        
        # Count neighbors in GC file
        neighbor_traits = set()
        neighbor_count = 0
        
        for chunk in pd.read_csv(gc_file, sep='\t', chunksize=chunk_size, dtype={'id1': int, 'id2': int}):
            for tid in trait_ids:
                mask = (chunk['id1'] == tid) | (chunk['id2'] == tid)
                matching_rows = chunk[mask]
                if not matching_rows.empty:
                    for _, row in matching_rows.iterrows():
                        other_id = int(row['id2']) if row['id1'] == tid else int(row['id1'])
                        other_trait = id_to_trait.get(other_id)
                        if other_trait and other_trait != bc_trait:
                            neighbor_traits.add(other_trait)
                            neighbor_count += 1
        
        print(f"  Neighbors found: {len(neighbor_traits)} unique traits, {neighbor_count} total edges")
        if neighbor_traits:
            print(f"  Sample neighbors: {list(neighbor_traits)[:5]}")
        print()

if __name__ == "__main__":
    main()
