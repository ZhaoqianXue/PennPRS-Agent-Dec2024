#!/usr/bin/env python3
"""
Test script to check if EFO_0001360 exists and what it represents.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.server.core.opentargets_client import OpenTargetsClient


def test_efo_0001360():
    """Check EFO_0001360 details."""
    client = OpenTargetsClient()
    
    efo_id = "EFO_0001360"
    
    print("=" * 80)
    print(f"Testing EFO ID: {efo_id}")
    print("=" * 80)
    
    # Try to get disease details
    print(f"\n[1] Getting disease details for {efo_id}")
    try:
        details = client.get_disease_details(efo_id)
        if details:
            print(f"  ✓ Disease found:")
            print(f"    Name: {details.get('name', 'N/A')}")
            print(f"    ID: {details.get('id', 'N/A')}")
            print(f"    Description: {details.get('description', 'N/A')}")
        else:
            print(f"  ⚠ No details returned (disease may not exist in Open Targets)")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    # Try to get targets
    print(f"\n[2] Getting associated targets for {efo_id}")
    try:
        targets = client.get_disease_targets(efo_id)
        target_count = len(targets)
        print(f"  Target count: {target_count}")
        if target_count > 0:
            print(f"  Top 5 targets:")
            for i, target in enumerate(targets[:5], 1):
                print(f"    {i}. {target.get('symbol', 'N/A')} (score: {target.get('score', 'N/A')})")
        else:
            print(f"  ⚠ No targets found (EFO ID exists but has no target associations)")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    # Search for Type 2 Diabetes to see what IDs are returned
    print(f"\n[3] Searching for 'Type 2 diabetes mellitus' to see available IDs")
    try:
        results = client.search_diseases("Type 2 diabetes mellitus", size=10)
        print(f"  Found {results.get('total', 0)} results")
        print(f"  Top results with their IDs:")
        for i, hit in enumerate(results.get('hits', [])[:5], 1):
            print(f"    {i}. {hit.name}")
            print(f"       ID: {hit.id}")
            print(f"       Entity: {hit.entity}")
            if hit.id == efo_id:
                print(f"       ✓ This is the EFO ID we're testing!")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_efo_0001360()
