#!/usr/bin/env python3
"""
Analyze breast cancer traits in heritability file and their GC pairs.
Excludes proxy traits (family history, screening, etc.)
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict

def main():
    # Load heritability metadata
    h2_file = Path("data/heritability/gwas_atlas/gwas_atlas.tsv")
    print(f"Loading heritability data from {h2_file}...")
    h2_df = pd.read_csv(h2_file, sep='\t', usecols=['id', 'uniqTrait', 'Trait', 'Domain'])
    
    # Find breast cancer related traits (excluding proxy traits)
    print("\n" + "="*80)
    print("Step 1: Finding non-proxy breast cancer traits")
    print("="*80)
    
    breast_cancer_studies = []
    for _, row in h2_df.iterrows():
        trait = str(row['uniqTrait']) if pd.notna(row['uniqTrait']) else ''
        trait_display = str(row['Trait']) if pd.notna(row['Trait']) else ''
        study_id = int(row['id']) if pd.notna(row['id']) else None
        
        if study_id is None:
            continue
        
        # Check if it's breast cancer related
        is_breast_cancer = 'breast' in trait.lower() and 'cancer' in trait.lower()
        
        # Check if it's a proxy trait
        proxy_keywords = ['family', 'history', 'maternal', 'paternal', 'sibling', 'siblings', 
                         'screening', 'mammogram', 'father', 'mother']
        is_proxy = any(kw in trait.lower() for kw in proxy_keywords)
        
        # Check domain
        domain = str(row.get('Domain', '')).lower()
        is_neoplasm = domain == 'neoplasms'
        
        if is_breast_cancer and not is_proxy:
            breast_cancer_studies.append({
                'study_id': study_id,
                'uniqTrait': trait,
                'Trait': trait_display,
                'Domain': domain
            })
    
    print(f"\nFound {len(breast_cancer_studies)} non-proxy breast cancer studies:")
    print("-" * 80)
    for study in breast_cancer_studies:
        print(f"ID {study['study_id']:4d}: {study['uniqTrait']}")
        print(f"         Display: {study['Trait']}")
        print(f"         Domain: {study['Domain']}")
        print()
    
    # Build ID to trait mapping for all studies
    print("="*80)
    print("Step 2: Building ID to trait mapping")
    print("="*80)
    id_to_trait = {}
    for _, row in h2_df.iterrows():
        study_id = int(row['id']) if pd.notna(row['id']) else None
        trait = str(row['uniqTrait']) if pd.notna(row['uniqTrait']) else None
        if study_id is not None and trait is not None:
            id_to_trait[study_id] = trait
    
    print(f"Total study IDs mapped: {len(id_to_trait)}")
    
    # Get breast cancer study IDs
    bc_study_ids = [s['study_id'] for s in breast_cancer_studies]
    print(f"Breast cancer study IDs: {bc_study_ids}")
    
    # Load GC file and find pairs
    gc_file = Path("data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv")
    print("\n" + "="*80)
    print("Step 3: Finding GC pairs for breast cancer studies")
    print("="*80)
    
    gc_pairs = []
    chunk_size = 100000
    
    print("Scanning GC file...")
    for chunk in pd.read_csv(gc_file, sep='\t', chunksize=chunk_size, dtype={'id1': int, 'id2': int}):
        for bc_id in bc_study_ids:
            mask = (chunk['id1'] == bc_id) | (chunk['id2'] == bc_id)
            matching_rows = chunk[mask]
            
            if not matching_rows.empty:
                for _, row in matching_rows.iterrows():
                    other_id = int(row['id2']) if row['id1'] == bc_id else int(row['id1'])
                    other_trait = id_to_trait.get(other_id, f'ID_{other_id}')
                    
                    gc_pairs.append({
                        'breast_cancer_id': bc_id,
                        'breast_cancer_trait': id_to_trait.get(bc_id, f'ID_{bc_id}'),
                        'other_id': other_id,
                        'other_trait': other_trait,
                        'rg': row['rg'],
                        'se': row['se'],
                        'z': row['z'],
                        'p': row['p']
                    })
    
    print(f"\nFound {len(gc_pairs)} GC pairs involving breast cancer studies")
    
    # Group by breast cancer trait
    print("\n" + "="*80)
    print("Step 4: GC pairs grouped by breast cancer trait")
    print("="*80)
    
    pairs_by_trait = defaultdict(list)
    for pair in gc_pairs:
        pairs_by_trait[pair['breast_cancer_trait']].append(pair)
    
    for bc_trait, pairs in pairs_by_trait.items():
        print(f"\n{bc_trait} (Study ID: {pairs[0]['breast_cancer_id']})")
        print(f"  Total pairs: {len(pairs)}")
        
        # Show unique other traits
        other_traits = set(p['other_trait'] for p in pairs)
        print(f"  Unique correlated traits: {len(other_traits)}")
        
        # Show top 10 most significant pairs
        sorted_pairs = sorted(pairs, key=lambda x: abs(x['z']), reverse=True)[:10]
        print(f"\n  Top 10 most significant correlations:")
        for i, p in enumerate(sorted_pairs, 1):
            print(f"    {i}. {p['other_trait']} (ID: {p['other_id']})")
            print(f"       rg={p['rg']:.4f}, z={p['z']:.2f}, p={p['p']:.6f}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("Step 5: Summary Statistics")
    print("="*80)
    
    all_other_traits = set()
    for pair in gc_pairs:
        all_other_traits.add(pair['other_trait'])
    
    print(f"\nTotal unique traits correlated with breast cancer studies: {len(all_other_traits)}")
    print(f"Total GC pairs: {len(gc_pairs)}")
    
    # Check which breast cancer traits have GC data
    print(f"\nBreast cancer traits with GC data:")
    for bc_trait, pairs in pairs_by_trait.items():
        study_id = pairs[0]['breast_cancer_id']
        print(f"  ✓ {bc_trait} (ID {study_id}): {len(pairs)} pairs")
    
    # Check which don't have GC data
    bc_traits_without_gc = []
    for study in breast_cancer_studies:
        if study['study_id'] not in [p['breast_cancer_id'] for p in gc_pairs]:
            bc_traits_without_gc.append(study)
    
    if bc_traits_without_gc:
        print(f"\nBreast cancer traits WITHOUT GC data:")
        for study in bc_traits_without_gc:
            print(f"  ✗ {study['uniqTrait']} (ID {study['study_id']})")

if __name__ == "__main__":
    main()
