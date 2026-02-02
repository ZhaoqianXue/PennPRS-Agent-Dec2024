import requests
from typing import List, Dict, Any, Optional, Iterator
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PGSCatalogClient:
    """
    Client for interacting with the PGS Catalog REST API.
    """
    BASE_URL = "https://www.pgscatalog.org/rest"
    DEFAULT_TIMEOUT_S = 30

    def search_scores(self, trait: str) -> List[Dict[str, Any]]:
        """
        Search for scores in the PGS Catalog by trait.
        Since score/search doesn't support fuzzy trait matching well,
        we search for traits first, then collect associated PGS IDs.
        """
        try:
            # 1. Search for traits matching the term
            t0 = time.time()
            url = f"{self.BASE_URL}/trait/search"
            response = requests.get(url, params={"term": trait}, timeout=self.DEFAULT_TIMEOUT_S)
            response.raise_for_status()
            data = response.json()
            traits = data.get("results", [])
            print(f"[Timing] PGS Trait Search: {time.time() - t0:.4f}s")

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


    def get_score_details(self, pgs_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific score ID.
        """
        try:
            url = f"{self.BASE_URL}/score/{pgs_id}"
            response = requests.get(url, timeout=self.DEFAULT_TIMEOUT_S)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting PGS details for {pgs_id}: {e}")
            return {}

    def get_score_performance(self, pgs_id: str) -> List[Dict[str, Any]]:
        """
        Get performance metrics for a specific score ID.
        """
        try:
            url = f"{self.BASE_URL}/performance/search"
            response = requests.get(url, params={"pgs_id": pgs_id}, timeout=self.DEFAULT_TIMEOUT_S)
            response.raise_for_status()
            data = response.json()
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
            url = f"{self.BASE_URL}/score/all"
            response = requests.get(
                url,
                params={"limit": limit, "offset": offset},
                timeout=self.DEFAULT_TIMEOUT_S
            )
            response.raise_for_status()
            return response.json()
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
            url = f"{self.BASE_URL}/performance/all"
            response = requests.get(
                url,
                params={"limit": limit, "offset": offset},
                timeout=self.DEFAULT_TIMEOUT_S
            )
            response.raise_for_status()
            return response.json()
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
