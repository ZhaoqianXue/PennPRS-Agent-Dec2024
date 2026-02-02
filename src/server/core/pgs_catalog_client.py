import os
import random
import threading
import time
from typing import List, Dict, Any, Optional, Iterator

import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PGSCatalogClient:
    """
    Client for interacting with the PGS Catalog REST API.
    """
    BASE_URL = "https://www.pgscatalog.org/rest"
    DEFAULT_TIMEOUT_S = 30
    # Safety defaults to avoid PGS Catalog rate limits / pagination errors.
    MAX_PAGE_SIZE = int(os.getenv("PGS_CATALOG_MAX_PAGE_SIZE", "100"))
    MAX_RETRIES = int(os.getenv("PGS_CATALOG_MAX_RETRIES", "4"))
    MIN_REQUEST_INTERVAL_S = float(os.getenv("PGS_CATALOG_MIN_REQUEST_INTERVAL_S", "0.2"))
    BACKOFF_BASE_S = float(os.getenv("PGS_CATALOG_BACKOFF_BASE_S", "0.6"))
    BACKOFF_MAX_S = float(os.getenv("PGS_CATALOG_BACKOFF_MAX_S", "8.0"))
    JITTER_S = float(os.getenv("PGS_CATALOG_JITTER_S", "0.2"))

    def __init__(self):
        # Global throttle across threads for this client instance.
        self._throttle_lock = threading.Lock()
        self._next_allowed_time = 0.0

    def _throttle(self) -> None:
        """
        Simple client-side throttling to reduce 429s.
        Enforces a minimum spacing between HTTP requests across threads.
        """
        sleep_s = 0.0
        with self._throttle_lock:
            now = time.monotonic()
            if now < self._next_allowed_time:
                sleep_s = self._next_allowed_time - now
            # Update next allowed time (even if we didn't sleep).
            next_time = max(now, self._next_allowed_time) + max(self.MIN_REQUEST_INTERVAL_S, 0.0)
            self._next_allowed_time = next_time
        if sleep_s > 0:
            time.sleep(sleep_s)

    @staticmethod
    def _parse_retry_after_seconds(value: Optional[str]) -> Optional[float]:
        """
        Parse Retry-After header when it's in seconds.
        (We intentionally do not parse HTTP-date formats here.)
        """
        if not value:
            return None
        try:
            return float(value.strip())
        except Exception:
            return None

    def _request_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Issue a GET request to PGS Catalog with:
        - client-side throttling
        - retry with exponential backoff for 429 / 5xx / transient request failures

        Raises on final failure.
        """
        url = f"{self.BASE_URL}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(self.MAX_RETRIES + 1):
            # Throttle before each attempt to avoid bursting.
            self._throttle()

            try:
                resp = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT_S)

                # 429: respect Retry-After if present.
                if resp.status_code == 429:
                    retry_after = self._parse_retry_after_seconds(resp.headers.get("Retry-After"))
                    wait_s = retry_after if retry_after is not None else min(
                        self.BACKOFF_MAX_S,
                        self.BACKOFF_BASE_S * (2 ** attempt)
                    )
                    wait_s += random.uniform(0.0, self.JITTER_S)
                    logger.warning(
                        "PGS Catalog rate limited (429) for %s; sleeping %.2fs (attempt %d/%d)",
                        url, wait_s, attempt + 1, self.MAX_RETRIES + 1
                    )
                    time.sleep(wait_s)
                    continue

                # Retry on 5xx.
                if 500 <= resp.status_code < 600:
                    wait_s = min(self.BACKOFF_MAX_S, self.BACKOFF_BASE_S * (2 ** attempt))
                    wait_s += random.uniform(0.0, self.JITTER_S)
                    logger.warning(
                        "PGS Catalog server error (%d) for %s; sleeping %.2fs (attempt %d/%d)",
                        resp.status_code, url, wait_s, attempt + 1, self.MAX_RETRIES + 1
                    )
                    time.sleep(wait_s)
                    continue

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.RequestException as exc:
                last_exc = exc
                # Network/timeout/etc: retry with backoff.
                wait_s = min(self.BACKOFF_MAX_S, self.BACKOFF_BASE_S * (2 ** attempt))
                wait_s += random.uniform(0.0, self.JITTER_S)
                logger.warning(
                    "PGS Catalog request failed for %s (%s); sleeping %.2fs (attempt %d/%d)",
                    url, type(exc).__name__, wait_s, attempt + 1, self.MAX_RETRIES + 1
                )
                time.sleep(wait_s)
                continue

            except Exception as exc:
                last_exc = exc
                break

        if last_exc:
            raise last_exc
        raise RuntimeError(f"PGS Catalog request failed for {url}")

    def search_scores(self, trait: str) -> List[Dict[str, Any]]:
        """
        Search for scores in the PGS Catalog by trait.
        Since score/search doesn't support fuzzy trait matching well,
        we search for traits first, then collect associated PGS IDs.
        """
        try:
            # 1. Search for traits matching the term
            traits = self.search_traits(trait)

            # 2. Collect all associated PGS IDs
            t1 = time.time()
            pgs_ids = set()
            for t in traits:
                ids = t.get("associated_pgs_ids", [])
                pgs_ids.update(ids)
                # Also check child associated IDs if beneficial
                child_ids = t.get("child_associated_pgs_ids", [])
                pgs_ids.update(child_ids)
            print(f"[Timing] PGS ID Collection: {time.time() - t1:.4f}s (Count: {len(pgs_ids)})")

            # 3. Format as list of dicts with 'id'
            # We assume details will be fetched later to get the name
            # Limiting to top 50 to avoid performance issues
            unique_ids = sorted(list(pgs_ids))
            
            return [{"id": pid} for pid in unique_ids]



        except Exception as e:
            logger.error(f"Error searching PGS Catalog: {e}")
            return []

    def search_traits(self, term: str) -> List[Dict[str, Any]]:
        """
        Search for traits in the PGS Catalog via `/rest/trait/search`.

        Returns the raw `results[]` items so callers can extract:
        - `id` (typically EFO_* identifiers)
        - `label` / `trait` (if present)
        - `associated_pgs_ids` / `child_associated_pgs_ids`
        """
        try:
            t0 = time.time()
            data = self._request_json("/trait/search", params={"term": term})
            traits = data.get("results", []) or []
            print(f"[Timing] PGS Trait Search: {time.time() - t0:.4f}s")
            return traits
        except Exception as e:
            logger.error(f"Error searching PGS Catalog traits: {e}")
            return []


    def get_score_details(self, pgs_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific score ID.
        """
        try:
            return self._request_json(f"/score/{pgs_id}")
        except Exception as e:
            logger.error(f"Error getting PGS details for {pgs_id}: {e}")
            return {}

    def get_score_performance(self, pgs_id: str) -> List[Dict[str, Any]]:
        """
        Get performance metrics for a specific score ID.
        """
        try:
            data = self._request_json("/performance/search", params={"pgs_id": pgs_id})
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Error getting PGS performance for {pgs_id}: {e}")
            return []

    def list_scores_all(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List scores via the paginated `/rest/score/all` endpoint.

        Returns a dict with keys: size, count, next, previous, results.
        """
        try:
            safe_limit = min(int(limit), self.MAX_PAGE_SIZE)
            if safe_limit != int(limit):
                logger.warning("Clamping PGS score/all limit from %s to %s", limit, safe_limit)
            return self._request_json("/score/all", params={"limit": safe_limit, "offset": offset})
        except Exception as e:
            logger.error(f"Error listing PGS scores (all): {e}")
            return {"size": 0, "count": 0, "next": None, "previous": None, "results": []}

    def iter_all_scores(self, batch_size: int = 200, max_scores: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """
        Iterate all scores from `/rest/score/all` with offset pagination.

        Args:
            batch_size: page size to request
            max_scores: optional cap for safety/testing
        """
        offset = 0
        yielded = 0
        while True:
            page = self.list_scores_all(limit=batch_size, offset=offset)
            results = page.get("results", []) or []
            if not results:
                break
            for item in results:
                yield item
                yielded += 1
                if max_scores is not None and yielded >= max_scores:
                    return
            offset += batch_size

    def list_performance_all(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List performance records via the paginated `/rest/performance/all` endpoint.

        Returns a dict with keys: size, count, next, previous, results.
        """
        try:
            safe_limit = min(int(limit), self.MAX_PAGE_SIZE)
            if safe_limit != int(limit):
                logger.warning("Clamping PGS performance/all limit from %s to %s", limit, safe_limit)
            return self._request_json("/performance/all", params={"limit": safe_limit, "offset": offset})
        except Exception as e:
            logger.error(f"Error listing PGS performances (all): {e}")
            return {"size": 0, "count": 0, "next": None, "previous": None, "results": []}

    def iter_all_performances(
        self,
        batch_size: int = 200,
        max_records: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate all performance records from `/rest/performance/all` with offset pagination.

        Args:
            batch_size: page size to request
            max_records: optional cap for safety/testing
        """
        offset = 0
        yielded = 0
        while True:
            page = self.list_performance_all(limit=batch_size, offset=offset)
            results = page.get("results", []) or []
            if not results:
                break
            for item in results:
                yield item
                yielded += 1
                if max_records is not None and yielded >= max_records:
                    return
            offset += batch_size
