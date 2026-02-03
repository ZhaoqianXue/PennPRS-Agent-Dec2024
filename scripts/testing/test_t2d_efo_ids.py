#!/usr/bin/env python3
"""
Test script to find the correct EFO ID for Type 2 Diabetes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.server.core.opentargets_client import OpenTargetsClient


def test_t2d_efo_ids():
    """Search for Type 2 Diabetes EFO IDs."""
    client = OpenTargetsClient()
    
    print("=" * 80)
    print("Searching for Type 2 Diabetes EFO IDs")
    print("=" * 80)
    
    # Search for Type 2 Diabetes
    search_queries = [
        "Type 2 Diabetes",
        "Type 2 diabetes mellitus",
        "T2D",
        "T2DM"
    ]
    
    for query in search_queries:
        print(f"\n[Search] '{query}'")
        try:
            results = client.search_diseases(query, size=10)
            print(f"  Found {results.get('total', 0)} results")
            
            for i, hit in enumerate(results.get('hits', [])[:5], 1):
                print(f"  {i}. {hit.name} (ID: {hit.id})")
                
                # Test if this ID returns targets
                try:
                    targets = client.get_disease_targets(hit.id)
                    target_count = len(targets)
                    print(f"      → {target_count} associated targets")
                    if target_count > 0:
                        print(f"        Top targets: {', '.join([t.get('symbol', 'N/A') for t in targets[:5]])}")
                except Exception as e:
                    print(f"      → Error getting targets: {e}")
                    
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_t2d_efo_ids()
