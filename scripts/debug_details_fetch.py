#!/usr/bin/env python3
"""
Debug script to check if PGS models really don't have details or if it's a code issue.
Tests actual API responses for details and performance endpoints.
"""

import sys
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.server.core.pgs_catalog_client import PGSCatalogClient

PGS_CATALOG_BASE_URL = "https://www.pgscatalog.org/rest"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)


async def fetch_details_direct(session: aiohttp.ClientSession, pgs_id: str) -> Tuple[str, Dict, int]:
    """Fetch details directly and return status code."""
    url = f"{PGS_CATALOG_BASE_URL}/score/{pgs_id}"
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
            status = resp.status
            if status == 200:
                data = await resp.json()
                return (pgs_id, data, status)
            else:
                text = await resp.text()
                return (pgs_id, {"error": f"HTTP {status}", "response": text[:200]}, status)
    except Exception as e:
        return (pgs_id, {"error": str(e)}, 0)


async def fetch_performance_direct(session: aiohttp.ClientSession, pgs_id: str) -> Tuple[str, Dict, int]:
    """Fetch performance directly and return status code."""
    url = f"{PGS_CATALOG_BASE_URL}/performance/search"
    params = {"pgs_id": pgs_id}
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as resp:
            status = resp.status
            if status == 200:
                data = await resp.json()
                return (pgs_id, data, status)
            else:
                text = await resp.text()
                return (pgs_id, {"error": f"HTTP {status}", "response": text[:200]}, status)
    except Exception as e:
        return (pgs_id, {"error": str(e)}, 0)


async def test_pgs_ids(pgs_ids: List[str], sample_size: int = 20):
    """Test a sample of PGS IDs to see what's actually returned."""
    print("=" * 80)
    print(f"Testing {min(sample_size, len(pgs_ids))} PGS IDs for Details and Performance")
    print("=" * 80)
    
    test_ids = pgs_ids[:sample_size]
    
    connector = aiohttp.TCPConnector(limit=20, limit_per_host=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Fetch details
        print(f"\n[1] Fetching Details for {len(test_ids)} models...")
        details_tasks = [fetch_details_direct(session, pgs_id) for pgs_id in test_ids]
        details_results = await asyncio.gather(*details_tasks)
        
        # Fetch performance
        print(f"[2] Fetching Performance for {len(test_ids)} models...")
        performance_tasks = [fetch_performance_direct(session, pgs_id) for pgs_id in test_ids]
        performance_results = await asyncio.gather(*performance_tasks)
    
    # Analyze results
    print("\n" + "=" * 80)
    print("Results Analysis")
    print("=" * 80)
    
    details_stats = {
        "success": 0,
        "empty": 0,
        "error": 0,
        "http_200_empty": 0,
        "http_error": 0
    }
    
    performance_stats = {
        "success": 0,
        "empty": 0,
        "error": 0,
        "http_200_empty": 0,
        "http_error": 0
    }
    
    print("\n[Details Results]")
    print("-" * 80)
    for pgs_id, data, status in details_results:
        if status == 200:
            if data and isinstance(data, dict) and len(data) > 0:
                details_stats["success"] += 1
                print(f"✓ {pgs_id}: Success (has data)")
            else:
                details_stats["empty"] += 1
                details_stats["http_200_empty"] += 1
                print(f"✗ {pgs_id}: HTTP 200 but empty data: {data}")
        elif status > 0:
            details_stats["error"] += 1
            details_stats["http_error"] += 1
            error_msg = data.get("error", "Unknown") if isinstance(data, dict) else str(data)
            print(f"✗ {pgs_id}: HTTP {status} - {error_msg}")
        else:
            details_stats["error"] += 1
            error_msg = data.get("error", "Unknown") if isinstance(data, dict) else str(data)
            print(f"✗ {pgs_id}: Exception - {error_msg}")
    
    print("\n[Performance Results]")
    print("-" * 80)
    for pgs_id, data, status in performance_results:
        if status == 200:
            # Check if it's a list or dict with results
            if isinstance(data, list):
                has_data = len(data) > 0
            elif isinstance(data, dict):
                results = data.get("results", [])
                has_data = len(results) > 0 if isinstance(results, list) else bool(results)
            else:
                has_data = bool(data)
            
            if has_data:
                performance_stats["success"] += 1
                print(f"✓ {pgs_id}: Success (has data)")
            else:
                performance_stats["empty"] += 1
                performance_stats["http_200_empty"] += 1
                print(f"○ {pgs_id}: HTTP 200 but empty list/dict")
        elif status > 0:
            performance_stats["error"] += 1
            performance_stats["http_error"] += 1
            error_msg = data.get("error", "Unknown") if isinstance(data, dict) else str(data)
            print(f"✗ {pgs_id}: HTTP {status} - {error_msg}")
        else:
            performance_stats["error"] += 1
            error_msg = data.get("error", "Unknown") if isinstance(data, dict) else str(data)
            print(f"✗ {pgs_id}: Exception - {error_msg}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    print(f"\n[Details]")
    print(f"  Success (has data): {details_stats['success']}/{len(test_ids)}")
    print(f"  HTTP 200 but empty: {details_stats['http_200_empty']}/{len(test_ids)}")
    print(f"  HTTP errors: {details_stats['http_error']}/{len(test_ids)}")
    print(f"  Other errors: {details_stats['error'] - details_stats['http_error']}/{len(test_ids)}")
    
    print(f"\n[Performance]")
    print(f"  Success (has data): {performance_stats['success']}/{len(test_ids)}")
    print(f"  HTTP 200 but empty: {performance_stats['http_200_empty']}/{len(test_ids)}")
    print(f"  HTTP errors: {performance_stats['http_error']}/{len(test_ids)}")
    print(f"  Other errors: {performance_stats['error'] - performance_stats['http_error']}/{len(test_ids)}")
    
    # Check code logic
    print("\n" + "=" * 80)
    print("Code Logic Check")
    print("=" * 80)
    
    print("\n[Current Code Logic]")
    print("  Details: if data:  # Only store non-empty details")
    print("  Performance: data or []  # Always store (even if empty)")
    
    print("\n[Issue Analysis]")
    if details_stats["http_200_empty"] > 0:
        print(f"  ⚠️  Found {details_stats['http_200_empty']} models with HTTP 200 but empty details")
        print("     This is expected - some models may not have details in the catalog")
    if details_stats["http_error"] > 0:
        print(f"  ⚠️  Found {details_stats['http_error']} models with HTTP errors")
        print("     These might be retryable or indicate API issues")
    
    # Test with sync client for comparison
    print("\n" + "=" * 80)
    print("Comparison: Sync Client Test")
    print("=" * 80)
    
    client = PGSCatalogClient()
    sync_success = 0
    sync_empty = 0
    sync_error = 0
    
    print(f"\nTesting first 5 IDs with sync client...")
    for pgs_id in test_ids[:5]:
        try:
            details = client.get_score_details(pgs_id)
            if details and isinstance(details, dict) and len(details) > 0:
                sync_success += 1
                print(f"✓ {pgs_id}: Success (sync)")
            else:
                sync_empty += 1
                print(f"✗ {pgs_id}: Empty (sync)")
        except Exception as e:
            sync_error += 1
            print(f"✗ {pgs_id}: Error (sync) - {type(e).__name__}: {e}")
    
    print(f"\nSync client results: {sync_success} success, {sync_empty} empty, {sync_error} errors")
    
    return details_stats, performance_stats


def main():
    """Main function."""
    print("\n" + "=" * 80)
    print("PGS Details Fetch Debug Tool")
    print("=" * 80)
    
    # Get PGS IDs from a test search
    print("\n[0] Searching for 'breast cancer' models...")
    client = PGSCatalogClient()
    search_results = client.search_scores("breast cancer")
    pgs_ids = [res["id"] for res in search_results]
    
    print(f"Found {len(pgs_ids)} models")
    print(f"Sample IDs: {pgs_ids[:10]}")
    
    if len(pgs_ids) == 0:
        print("ERROR: No models found")
        return
    
    # Test with async
    print(f"\n[Testing with async code...]")
    asyncio.run(test_pgs_ids(pgs_ids, sample_size=20))
    
    print("\n" + "=" * 80)
    print("Debug Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
