#!/usr/bin/env python3
"""
Detailed test script to measure async optimization performance.
Tests only the PGS model fetching part, not the full recommendation workflow.
"""

import sys
import time
import asyncio
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search

def test_async_fetch():
    """Test async fetching performance."""
    print("=" * 80)
    print("Detailed Async Fetch Performance Test")
    print("=" * 80)
    
    client = PGSCatalogClient()
    test_trait = "breast cancer"
    
    print(f"\n[1] Searching for models: {test_trait}")
    search_start = time.time()
    search_results = client.search_scores(test_trait)
    search_time = time.time() - search_start
    print(f"    Found {len(search_results)} models in {search_time:.2f}s")
    
    if len(search_results) == 0:
        print("ERROR: No models found")
        return
    
    pgs_ids = [res["id"] for res in search_results]
    print(f"\n[2] Testing async fetch for {len(pgs_ids)} models")
    print(f"    PGS IDs: {pgs_ids[:5]}..." if len(pgs_ids) > 5 else f"    PGS IDs: {pgs_ids}")
    
    # Test the async fetch function
    fetch_start = time.time()
    try:
        result = prs_model_pgscatalog_search(
            client,
            test_trait,
            limit=len(pgs_ids),
            request_id="test-async-detailed"
        )
        fetch_time = time.time() - fetch_start
        
        print(f"\n[3] Fetch completed!")
        print(f"    Total fetch time: {fetch_time:.2f}s")
        print(f"    Models returned: {len(result.models)}")
        print(f"    Average time per model: {fetch_time / len(pgs_ids):.3f}s")
        
        # Performance analysis
        print(f"\n[4] Performance Analysis:")
        if fetch_time < 5:
            print(f"    🚀 Excellent! (< 5s)")
        elif fetch_time < 10:
            print(f"    ✅ Good (< 10s)")
        elif fetch_time < 20:
            print(f"    ⚠️  Acceptable (< 20s)")
        else:
            print(f"    ❌ Needs improvement (> 20s)")
        
        # Breakdown
        print(f"\n[5] Time Breakdown:")
        print(f"    Search time: {search_time:.2f}s ({search_time/fetch_time*100:.1f}%)")
        print(f"    Fetch time: {fetch_time:.2f}s ({fetch_time/fetch_time*100:.1f}%)")
        
        return True
        
    except Exception as e:
        fetch_time = time.time() - fetch_start
        print(f"\n[ERROR] Fetch failed after {fetch_time:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_async_fetch()
    sys.exit(0 if success else 1)
