#!/usr/bin/env python3
"""
Test script to verify concurrent fetching performance and error handling.
Tests the increased worker count (10) and reduced interval (0.1s) settings.
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search

def test_concurrent_fetch():
    """Test concurrent fetching with new settings (10 workers, 0.1s interval)."""
    print("=" * 60)
    print("Testing Concurrent Fetch Performance")
    print("=" * 60)
    print(f"Workers: {os.getenv('PGS_FETCH_MAX_WORKERS', '10')}")
    print(f"Request Interval: {os.getenv('PGS_CATALOG_MIN_REQUEST_INTERVAL_S', '0.1')}s")
    print()
    
    client = PGSCatalogClient()
    
    # Test with a common trait that should return multiple models
    test_trait = "Type 2 Diabetes"
    print(f"Testing trait: {test_trait}")
    print()
    
    # Step 1: Search for models
    print("Step 1: Searching for models...")
    start_time = time.time()
    search_results = client.search_scores(test_trait)
    search_time = time.time() - start_time
    print(f"Found {len(search_results)} models in {search_time:.2f}s")
    
    if len(search_results) == 0:
        print("ERROR: No models found. Cannot test concurrent fetching.")
        return False
    
    # Limit to first 20 models for testing
    test_models = search_results[:20]
    print(f"Testing with {len(test_models)} models")
    print()
    
    # Step 2: Test concurrent fetching with prs_model_pgscatalog_search
    print("Step 2: Testing concurrent fetch with prs_model_pgscatalog_search...")
    start_time = time.time()
    
    try:
        result = prs_model_pgscatalog_search(
            client, 
            test_trait, 
            limit=len(test_models),
            request_id="test-concurrent-fetch"
        )
        fetch_time = time.time() - start_time
        
        print(f"✓ Successfully fetched {len(result.models)} models")
        print(f"✓ Total time: {fetch_time:.2f}s")
        print(f"✓ Average time per model: {fetch_time / len(test_models):.3f}s")
        print()
        
        # Check for errors
        if len(result.models) == 0:
            print("WARNING: No models returned after filtering")
            return False
        
        print("✓ Test passed: No errors detected")
        return True
        
    except Exception as e:
        fetch_time = time.time() - start_time
        print(f"✗ ERROR after {fetch_time:.2f}s: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_limiting():
    """Test if we're hitting rate limits with new settings."""
    print("=" * 60)
    print("Testing Rate Limiting")
    print("=" * 60)
    
    client = PGSCatalogClient()
    
    # Test rapid requests
    test_ids = ["PGS000001", "PGS000002", "PGS000003", "PGS000004", "PGS000005"]
    error_count = 0
    success_count = 0
    
    print(f"Making {len(test_ids)} rapid requests...")
    start_time = time.time()
    
    for pgs_id in test_ids:
        try:
            details = client.get_score_details(pgs_id)
            if details:
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            print(f"  Error fetching {pgs_id}: {type(e).__name__}")
    
    elapsed = time.time() - start_time
    print(f"✓ Success: {success_count}/{len(test_ids)}")
    print(f"✗ Errors: {error_count}/{len(test_ids)}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Average: {elapsed / len(test_ids):.3f}s per request")
    
    if error_count > len(test_ids) / 2:
        print("WARNING: High error rate detected. May be hitting rate limits.")
        return False
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PGS Catalog Concurrent Fetch Test")
    print("=" * 60 + "\n")
    
    # Test 1: Concurrent fetching
    test1_passed = test_concurrent_fetch()
    print()
    
    # Test 2: Rate limiting
    test2_passed = test_rate_limiting()
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Concurrent Fetch Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Rate Limiting Test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed. New settings appear safe.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Consider adjusting settings.")
        sys.exit(1)
