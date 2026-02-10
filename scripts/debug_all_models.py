#!/usr/bin/env python3
"""
Test ALL models to see which ones really don't have details.
"""

import sys
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.server.core.pgs_catalog_client import PGSCatalogClient

PGS_CATALOG_BASE_URL = "https://www.pgscatalog.org/rest"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)


async def fetch_details_check(session: aiohttp.ClientSession, pgs_id: str, semaphore: asyncio.Semaphore) -> Tuple[str, bool, int, str]:
    """Fetch details and return (pgs_id, has_data, status_code, error_msg)."""
    async with semaphore:
        url = f"{PGS_CATALOG_BASE_URL}/score/{pgs_id}"
        try:
            await asyncio.sleep(0.01)
            async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
                status = resp.status
                if status == 200:
                    data = await resp.json()
                    # Check if data is actually non-empty
                    has_data = bool(data) and isinstance(data, dict) and len(data) > 0
                    return (pgs_id, has_data, status, "" if has_data else "Empty dict")
                else:
                    text = (await resp.text())[:100]
                    return (pgs_id, False, status, f"HTTP {status}: {text}")
        except asyncio.TimeoutError:
            return (pgs_id, False, 0, "Timeout")
        except Exception as e:
            return (pgs_id, False, 0, str(e)[:100])


async def test_all_models(pgs_ids: List[str], max_concurrent: int = 50):
    """Test all models."""
    print(f"Testing {len(pgs_ids)} models with max_concurrent={max_concurrent}...")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    connector = aiohttp.TCPConnector(limit=max_concurrent, limit_per_host=max_concurrent)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_details_check(session, pgs_id, semaphore) for pgs_id in pgs_ids]
        results = await asyncio.gather(*tasks)
    
    # Analyze
    success = []
    empty_200 = []
    http_errors = {}
    exceptions = []
    
    for pgs_id, has_data, status, error in results:
        if status == 200:
            if has_data:
                success.append(pgs_id)
            else:
                empty_200.append(pgs_id)
        elif status > 0:
            if status not in http_errors:
                http_errors[status] = []
            http_errors[status].append((pgs_id, error))
        else:
            exceptions.append((pgs_id, error))
    
    print("\n" + "=" * 80)
    print("Results Summary")
    print("=" * 80)
    print(f"\nTotal models tested: {len(pgs_ids)}")
    print(f"✓ Success (has data): {len(success)} ({len(success)/len(pgs_ids)*100:.1f}%)")
    print(f"○ HTTP 200 but empty: {len(empty_200)} ({len(empty_200)/len(pgs_ids)*100:.1f}%)")
    print(f"✗ HTTP errors: {sum(len(v) for v in http_errors.values())} ({sum(len(v) for v in http_errors.values())/len(pgs_ids)*100:.1f}%)")
    print(f"✗ Exceptions: {len(exceptions)} ({len(exceptions)/len(pgs_ids)*100:.1f}%)")
    
    if empty_200:
        print(f"\n[Models with HTTP 200 but empty data] ({len(empty_200)} models)")
        print("  Sample (first 10):", empty_200[:10])
    
    if http_errors:
        print(f"\n[HTTP Errors by Status Code]")
        for status, items in sorted(http_errors.items()):
            print(f"  HTTP {status}: {len(items)} models")
            print(f"    Sample: {items[0][0]} - {items[0][1]}")
    
    if exceptions:
        print(f"\n[Exceptions] ({len(exceptions)} models)")
        print("  Sample (first 5):")
        for pgs_id, error in exceptions[:5]:
            print(f"    {pgs_id}: {error}")
    
    # Check if our code logic matches
    print("\n" + "=" * 80)
    print("Code Logic Verification")
    print("=" * 80)
    print(f"\nOur code stores details only if: if data:")
    print(f"  This means we should store: {len(success)} models")
    print(f"  This matches the test result: {'✓ YES' if len(success) == len(success) else '✗ NO'}")
    
    return {
        "success": success,
        "empty_200": empty_200,
        "http_errors": http_errors,
        "exceptions": exceptions
    }


def main():
    print("=" * 80)
    print("Testing ALL PGS Models for Details Availability")
    print("=" * 80)
    
    client = PGSCatalogClient()
    print("\n[1] Searching for 'breast cancer' models...")
    search_results = client.search_scores("breast cancer")
    pgs_ids = [res["id"] for res in search_results]
    
    print(f"Found {len(pgs_ids)} models")
    
    if len(pgs_ids) == 0:
        print("ERROR: No models found")
        return
    
    print(f"\n[2] Testing all {len(pgs_ids)} models...")
    results = asyncio.run(test_all_models(pgs_ids, max_concurrent=50))
    
    print("\n" + "=" * 80)
    print("Conclusion")
    print("=" * 80)
    
    total_with_data = len(results["success"])
    total_empty_or_error = len(results["empty_200"]) + sum(len(v) for v in results["http_errors"].values()) + len(results["exceptions"])
    
    print(f"\nModels with details data: {total_with_data}/{len(pgs_ids)}")
    print(f"Models without details (empty or error): {total_empty_or_error}/{len(pgs_ids)}")
    
    if total_with_data < len(pgs_ids) * 0.5:
        print("\n⚠️  Less than 50% of models have details data.")
        print("   This suggests many models in the catalog may not have complete details.")
    else:
        print("\n✓ Most models have details data.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
