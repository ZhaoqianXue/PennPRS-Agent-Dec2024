#!/usr/bin/env python3
"""
Test script to compare the number of targets returned by Open Targets API
when using EFO IDs vs MONDO IDs for the same diseases.

Tests diseases:
- Breast cancer
- Type 2 Diabetes (T2D)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.server.core.opentargets_client import OpenTargetsClient


def test_efo_vs_mondo_targets():
    """Compare targets returned for EFO vs MONDO IDs."""
    client = OpenTargetsClient()
    
    # Test cases: (disease_name, efo_id, mondo_id)
    test_cases = [
        ("Breast cancer", "EFO_0000305", "MONDO_0007254"),  # Breast cancer
        ("Type 2 Diabetes", "EFO_0001360", "MONDO_0005148"),  # Type 2 diabetes mellitus
    ]
    
    print("=" * 80)
    print("Comparing EFO vs MONDO IDs for Open Targets API")
    print("=" * 80)
    
    for disease_name, efo_id, mondo_id in test_cases:
        print(f"\n{'='*80}")
        print(f"Disease: {disease_name}")
        print(f"{'='*80}")
        
        # Test with EFO ID
        print(f"\n[EFO ID] {efo_id}")
        try:
            efo_targets = client.get_disease_targets(efo_id)
            efo_count = len(efo_targets)
            print(f"  ✓ Success: Found {efo_count} associated targets")
            if efo_count > 0:
                print(f"  Example targets (top 5):")
                for i, target in enumerate(efo_targets[:5], 1):
                    print(f"    {i}. {target.get('symbol', 'N/A')} (score: {target.get('score', 'N/A')})")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")
            efo_count = 0
            efo_targets = []
        
        # Test with MONDO ID
        print(f"\n[MONDO ID] {mondo_id}")
        try:
            mondo_targets = client.get_disease_targets(mondo_id)
            mondo_count = len(mondo_targets)
            print(f"  ✓ Success: Found {mondo_count} associated targets")
            if mondo_count > 0:
                print(f"  Example targets (top 5):")
                for i, target in enumerate(mondo_targets[:5], 1):
                    print(f"    {i}. {target.get('symbol', 'N/A')} (score: {target.get('score', 'N/A')})")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")
            mondo_count = 0
            mondo_targets = []
        
        # Compare results
        print(f"\n[Comparison]")
        print(f"  EFO ID targets:   {efo_count}")
        print(f"  MONDO ID targets: {mondo_count}")
        
        if efo_count == mondo_count:
            print(f"  ✓ Same number of targets ({efo_count})")
        else:
            print(f"  ⚠ Different number of targets (difference: {abs(efo_count - mondo_count)})")
        
        # Compare target sets if both succeeded
        if efo_count > 0 and mondo_count > 0:
            efo_symbols = {t.get('symbol') for t in efo_targets if t.get('symbol')}
            mondo_symbols = {t.get('symbol') for t in mondo_targets if t.get('symbol')}
            
            common_symbols = efo_symbols & mondo_symbols
            efo_only = efo_symbols - mondo_symbols
            mondo_only = mondo_symbols - efo_symbols
            
            print(f"\n  Target overlap analysis:")
            print(f"    Common targets:     {len(common_symbols)}")
            print(f"    EFO-only targets:   {len(efo_only)}")
            print(f"    MONDO-only targets: {len(mondo_only)}")
            
            if len(common_symbols) > 0:
                print(f"\n    Common targets (top 10): {', '.join(list(common_symbols)[:10])}")
            if len(efo_only) > 0:
                print(f"\n    EFO-only targets (top 10): {', '.join(list(efo_only)[:10])}")
            if len(mondo_only) > 0:
                print(f"\n    MONDO-only targets (top 10): {', '.join(list(mondo_only)[:10])}")
            
            # Calculate overlap percentage
            total_unique = len(efo_symbols | mondo_symbols)
            if total_unique > 0:
                overlap_pct = (len(common_symbols) / total_unique) * 100
                print(f"\n    Overlap percentage: {overlap_pct:.1f}%")
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("If EFO and MONDO IDs return the same number of targets and")
    print("high overlap, they are likely equivalent or very similar.")
    print("If they differ significantly, they may represent different")
    print("disease concepts or have different annotation coverage.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_efo_vs_mondo_targets()
