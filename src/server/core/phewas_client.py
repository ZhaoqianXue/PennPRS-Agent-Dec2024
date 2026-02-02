"""
ExPheWAS API Client

This module provides a client for the ExPheWAS API, enabling programmatic access 
to phenome-wide association study results from the UK Biobank.

API Root: https://exphewas.statgen.org/v1/api
Documentation: https://exphewas.statgen.org/v1/docs/api
"""

import requests
import logging
import json
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PheWASClient:
    """
    Client for interacting with the ExPheWAS API (v1).
    
    Provides methods to query outcomes, gene-level associations for phenotypes,
    and phenotype associations for specific genes.
    """
    
    BASE_URL = "https://exphewas.statgen.org/v1/api"
    
    def __init__(self, base_url: str = BASE_URL):
        """
        Initialize the PheWAS client.
        
        Args:
            base_url: The root URL of the ExPheWAS API.
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json"
        })
        self._cache = {}  # Basic in-memory cache

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: int = 60) -> Any:
        """
        Execute a GET request and return the JSON response with basic caching.
        
        Args:
            endpoint: The API endpoint path.
            params: Optional query parameters.
            timeout: Request timeout in seconds.
            
        Returns:
            The parsed JSON response.
            
        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        # Create a cache key from endpoint and sorted parameters
        cache_key = f"{endpoint}:{json.dumps(params, sort_keys=True) if params else ''}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            self._cache[cache_key] = data
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error occurred: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during the request: {e}")
            raise

    def get_outcomes(self, query: str) -> List[Dict[str, Any]]:
        """
        Map an EFO ID or trait name to an ExPheWAS outcome ID.
        
        Args:
            query: The search string (e.g., "Crohn", "EFO_0000384").
            
        Returns:
            A list of matching outcome dictionaries.
        """
        # GET /outcome returns a list of all outcomes.
        # We filter locally as the server-side 'q' parameter doesn't seem to filter.
        try:
            outcomes = self._get("/outcome")
            if not outcomes:
                return []
                
            query_lower = query.lower()
            results = [
                outcome for outcome in outcomes
                if query_lower in outcome.get("label", "").lower() or 
                   query_lower in str(outcome.get("id", "")).lower()
            ]
            
            logger.info(f"Found {len(results)} outcomes matching '{query}'")
            return results
        except Exception as e:
            logger.error(f"Failed to fetch outcomes: {e}")
            return []

    def get_outcome_results(self, outcome_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get gene-level associations for a specific phenotype.
        
        Args:
            outcome_id: The ExPheWAS outcome identifier.
            limit: Maximum number of results to return.
            
        Returns:
            A list of gene association statistics.
        """
        endpoint = f"/outcome/{outcome_id}/results"
        try:
            results = self._get(endpoint)
            if not isinstance(results, list):
                logger.warning(f"Unexpected response format for outcome results: {type(results)}")
                return []
                
            return results[:limit]
        except Exception as e:
            logger.error(f"Failed to fetch results for outcome {outcome_id}: {e}")
            return []

    def get_gene_results(self, ensembl_id: str) -> List[Dict[str, Any]]:
        """
        Get all phenotypes associated with a specific gene.
        
        Args:
            ensembl_id: The Ensembl gene ID (e.g., 'ENSG00000130203').
            
        Returns:
            A list of phenotype association statistics for the gene.
        """
        endpoint = f"/gene/{ensembl_id}/results"
        try:
            results = self._get(endpoint)
            if not isinstance(results, list):
                logger.warning(f"Unexpected response format for gene results: {type(results)}")
                return []
            return results
        except Exception as e:
            logger.error(f"Failed to fetch results for gene {ensembl_id}: {e}")
            return []
