"""
PGS/PennPRS metadata fetch service for Disease workflow.

Why this exists:
- `workflow.py` initializes an LLM at import time, which makes it hard to unit test.
- This module is intentionally LLM-free and network-call-free in tests (via mocking),
  so we can verify rate limiting / truncation logic deterministically.

All comments/strings are in English by project convention.
"""

from __future__ import annotations

import concurrent.futures
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from src.server.core.state import search_progress


DEFAULT_MAX_PGS_MODELS_FETCH = int(os.getenv("PGS_MAX_MODELS_FETCH", "40"))
# Increased default concurrent requests for faster fetching (was 20, now 50)
DEFAULT_PGS_FETCH_WORKERS = int(os.getenv("PGS_FETCH_MAX_WORKERS", "50"))

def _fetch_pgs_details_and_performance_concurrently(
    *,
    pgs_client: Any,
    pgs_ids: List[str],
    request_id: Optional[str],
    max_workers: int,
    progress_update_interval: int = 3,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Fetch PGS score details + performance concurrently using threads.

    Note:
    - This intentionally avoids the previously used `_fetch_models_async` helper, which was removed.
    - Keeping this logic local prevents backend reload crashes and ensures progress updates remain available.
    """
    details_map: Dict[str, Dict[str, Any]] = {}
    performance_map: Dict[str, List[Dict[str, Any]]] = {}

    total = len(pgs_ids)
    fetched_count = 0

    if request_id and request_id in search_progress:
        # Align with the CoScientist progress contract: step-1 reflects PGS model hydration.
        search_progress[request_id].update({
            "status": "running",
            "total": total,
            "fetched": 0,
            "current_action": "Fetching metadata...",
            "current_step": "step-1",
        })

    max_workers = max(1, int(max_workers))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_meta: Dict[concurrent.futures.Future, Tuple[str, str]] = {}

        for pgs_id in pgs_ids:
            future_to_meta[executor.submit(pgs_client.get_score_details, pgs_id)] = (pgs_id, "details")
            future_to_meta[executor.submit(pgs_client.get_score_performance, pgs_id)] = (pgs_id, "performance")

        for i, future in enumerate(concurrent.futures.as_completed(future_to_meta), start=1):
            pgs_id, req_type = future_to_meta[future]
            try:
                data = future.result()
            except Exception:
                # Best-effort: skip failed calls without failing the whole workflow.
                continue

            if req_type == "details":
                if data:
                    details_map[pgs_id] = data
                    fetched_count += 1

                    if request_id and request_id in search_progress:
                        # Throttle updates slightly to avoid overwhelming the client with writes.
                        if fetched_count == 1 or fetched_count % max(1, int(progress_update_interval)) == 0 or fetched_count == total:
                            search_progress[request_id].update({
                                "fetched": fetched_count,
                                "current_action": f"Fetching {pgs_id}...",
                                "current_step": "step-1",
                            })
            else:
                performance_map[pgs_id] = data or []

    if request_id and request_id in search_progress:
        # Set fetched to total to show all models have been processed
        # (regardless of success/failure, all models have been attempted)
        search_progress[request_id].update({
            "fetched": total,  # Use total attempted, not just successful
            "current_action": f"Completed fetching {total} models",
            "current_step": "step-1",
        })

    return details_map, performance_map


def fetch_pgs_and_pennprs_metadata(
    trait: str,
    *,
    pgs_client: Any,
    pennprs_client: Any,
    request_id: Optional[str] = None,
    max_pgs_models_fetch: int = DEFAULT_MAX_PGS_MODELS_FETCH,
    max_workers: int = DEFAULT_PGS_FETCH_WORKERS,
) -> Tuple[
    List[Dict[str, Any]],  # pgs_results (possibly truncated)
    Dict[str, Dict[str, Any]],  # pgs_details_map
    Dict[str, List[Dict[str, Any]]],  # pgs_performance_map
    List[Dict[str, Any]],  # penn_results
    int,  # pgs_total_found (before truncation)
]:
    """
    Fetch PGS model IDs (via trait search), then hydrate each with:
    - `/rest/score/{pgs_id}` (details)
    - `/rest/performance/search?pgs_id=...` (performance)

    Also fetch PennPRS public results for the same trait.
    """
    if request_id and request_id in search_progress:
        search_progress[request_id]["current_action"] = "Searching PGS Catalog..."

    t_start = time.time()
    pgs_results_all = pgs_client.search_scores(trait) or []
    print(f"[Timing] PGS Search (IDs): {time.time() - t_start:.4f}s")

    pgs_total_found = len(pgs_results_all)
    cap = max(0, int(max_pgs_models_fetch))
    pgs_results = pgs_results_all[:cap]

    t_penn = time.time()
    penn_results = pennprs_client.search_public_results(trait) or []
    print(f"[Timing] PennPRS Search: {time.time() - t_penn:.4f}s")

    # Extract PGS IDs
    pgs_ids = [res.get("id") for res in pgs_results if res.get("id")]
    
    # Hydrate PGS models concurrently (thread-based). This is reliable under reload and
    # doesn't depend on a removed async helper.
    pgs_details_map, pgs_performance_map = _fetch_pgs_details_and_performance_concurrently(
        pgs_client=pgs_client,
        pgs_ids=pgs_ids,
        request_id=request_id,
        max_workers=max_workers,
        progress_update_interval=3,
    )

    return pgs_results, pgs_details_map, pgs_performance_map, penn_results, pgs_total_found

