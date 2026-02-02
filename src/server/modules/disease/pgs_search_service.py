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
DEFAULT_PGS_FETCH_WORKERS = int(os.getenv("PGS_FETCH_MAX_WORKERS", "4"))


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

    if request_id and request_id in search_progress:
        # Progress reflects actual hydration work (capped PGS list).
        search_progress[request_id]["total"] = len(pgs_results) + len(penn_results)
        search_progress[request_id]["status"] = "running"
        search_progress[request_id]["current_action"] = "Fetching metadata..."

    pgs_details_map: Dict[str, Dict[str, Any]] = {}
    pgs_performance_map: Dict[str, List[Dict[str, Any]]] = {}
    fetched_count = 0

    workers = max(1, int(max_workers))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_req: Dict[concurrent.futures.Future, Tuple[str, str]] = {}
        for res in pgs_results:
            pid = res.get("id")
            if not pid:
                continue
            future_to_req[executor.submit(pgs_client.get_score_details, pid)] = (pid, "details")
            future_to_req[executor.submit(pgs_client.get_score_performance, pid)] = (pid, "performance")

        for future in concurrent.futures.as_completed(future_to_req):
            pid, req_type = future_to_req[future]
            try:
                data = future.result()
                if req_type == "details":
                    pgs_details_map[pid] = data or {}
                    fetched_count += 1
                    if request_id and request_id in search_progress:
                        search_progress[request_id]["fetched"] = fetched_count
                        search_progress[request_id]["current_action"] = f"Fetching {pid}..."
                else:
                    pgs_performance_map[pid] = data or []
            except Exception:
                # Individual failures should not crash the workflow.
                continue

    return pgs_results, pgs_details_map, pgs_performance_map, penn_results, pgs_total_found

