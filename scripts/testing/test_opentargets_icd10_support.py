#!/usr/bin/env python3
"""
Test script to verify whether Open Targets Platform API supports ICD-10 codes.

This script tests if we can query Open Targets API using ICD-10 codes directly,
or if we must use EFO/MONDO IDs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.server.core.opentargets_client import OpenTargetsClient


def test_icd10_code_direct_query():
    """Test if Open Targets API accepts ICD-10 codes directly."""
    client = OpenTargetsClient()
    
    # Test cases: ICD-10 codes for common diseases
    test_cases = [
        ("C50", "Breast cancer (ICD-10: C50)"),
        ("E11", "Type 2 Diabetes (ICD-10: E11)"),
        ("I25", "Chronic ischemic heart disease (ICD-10: I25)"),
    ]
    
    print("=" * 80)
    print("Testing Open Targets API with ICD-10 codes")
    print("=" * 80)
    
    for icd10_code, description in test_cases:
        print(f"\n[Test] {description}")
        print(f"  Attempting to query with ICD-10 code: {icd10_code}")
        
        try:
            # Try to get disease targets using ICD-10 code
            targets = client.get_disease_targets(icd10_code)
            
            if targets:
                print(f"  ✓ SUCCESS: API accepted ICD-10 code '{icd10_code}'")
                print(f"    Found {len(targets)} associated targets")
                if len(targets) > 0:
                    print(f"    Example target: {targets[0].get('symbol', 'N/A')}")
            else:
                print(f"  ⚠ WARNING: API accepted '{icd10_code}' but returned no targets")
                print(f"    This might mean:")
                print(f"    1. The code is valid but has no associated targets")
                print(f"    2. The code needs to be mapped to EFO first")
                
        except Exception as e:
            print(f"  ✗ FAILED: API rejected ICD-10 code '{icd10_code}'")
            print(f"    Error: {type(e).__name__}: {e}")
            print(f"    This suggests ICD-10 codes are NOT directly supported")
    
    print("\n" + "=" * 80)
    print("Testing with EFO ID for comparison")
    print("=" * 80)
    
    # Test with a known EFO ID for comparison
    efo_id = "EFO_0000305"  # Breast cancer EFO ID
    print(f"\n[Control Test] Using EFO ID: {efo_id}")
    try:
        targets = client.get_disease_targets(efo_id)
        print(f"  ✓ SUCCESS: API accepted EFO ID '{efo_id}'")
        print(f"    Found {len(targets)} associated targets")
        if len(targets) > 0:
            print(f"    Example target: {targets[0].get('symbol', 'N/A')}")
    except Exception as e:
        print(f"  ✗ FAILED: Unexpected error with EFO ID")
        print(f"    Error: {type(e).__name__}: {e}")


def test_search_with_icd10():
    """Test if search API can find diseases using ICD-10 codes."""
    client = OpenTargetsClient()
    
    print("\n" + "=" * 80)
    print("Testing Open Targets Search API with ICD-10 codes")
    print("=" * 80)
    
    test_codes = ["C50", "E11", "I25"]
    
    for icd10_code in test_codes:
        print(f"\n[Search Test] Searching for: '{icd10_code}'")
        try:
            results = client.search_diseases(icd10_code, size=5)
            print(f"  Total results: {results.get('total', 0)}")
            
            if results.get('total', 0) > 0:
                print(f"  ✓ Found {len(results.get('hits', []))} disease matches")
                for i, hit in enumerate(results.get('hits', [])[:3], 1):
                    print(f"    {i}. {hit.name} (ID: {hit.id})")
            else:
                print(f"  ⚠ No results found for ICD-10 code '{icd10_code}'")
                print(f"    This suggests search doesn't recognize ICD-10 codes")
                
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Open Targets API ICD-10 Support Verification")
    print("=" * 80)
    print("\nThis script tests whether Open Targets Platform API supports")
    print("ICD-10 codes directly, or requires EFO/MONDO IDs.\n")
    
    test_icd10_code_direct_query()
    test_search_with_icd10()
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("Based on the test results above:")
    print("- If ICD-10 codes are accepted: API supports ICD-10")
    print("- If ICD-10 codes are rejected: API requires EFO/MONDO IDs")
    print("- If search finds results: ICD-10 might be searchable but not queryable")
    print("=" * 80 + "\n")
