"""
Open Targets Platform GraphQL Client

This module provides a client for querying the Open Targets Platform GraphQL API,
implementing search functionality identical to https://platform.opentargets.org

API Endpoint: https://api.platform.opentargets.org/api/v4/graphql
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Open Targets Platform GraphQL API endpoint
OPENTARGETS_API_URL = "https://api.platform.opentargets.org/api/v4/graphql"


# GraphQL query for search - FULL VERSION matching Open Targets Platform
SEARCH_QUERY = """
query SearchQuery($queryString: String!, $page: Pagination!, $entityNames: [String!]) {
  search(queryString: $queryString, page: $page, entityNames: $entityNames) {
    total
    hits {
      id
      name
      entity
      description
      score
      highlights
    }
  }
}
"""

# GraphQL query for disease details
DISEASE_QUERY = """
query DiseaseQuery($efoId: String!) {
  disease(efoId: $efoId) {
    id
    name
    description
  }
}
"""

# GraphQL query for target details
TARGET_QUERY = """
query TargetQuery($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    id
    approvedSymbol
    approvedName
    biotype
    proteinIds {
      id
      source
    }
    functionDescriptions
    synonyms {
      label
      source
    }
  }
}
"""

# GraphQL query for study details - for enriching GWAS study results
STUDY_QUERY = """
query StudyQuery($studyId: String!) {
  study(studyId: $studyId) {
    id
    traitFromSource
    studyType
    nSamples
    nCases
    hasSumstats
  }
}
"""


@dataclass
class SearchResult:
    """Represents a single search result from Open Targets - FULL VERSION."""
    id: str
    name: str
    entity: str  # 'disease', 'target', or 'drug'
    description: Optional[str] = None
    score: Optional[float] = None  # Relevance score from Open Targets
    highlights: Optional[List[str]] = None  # Highlighted text snippets


class OpenTargetsClient:
    """
    Client for Open Targets Platform GraphQL API.
    
    Provides identical search functionality to the Open Targets Platform website,
    with methods for searching diseases, targets (genes/proteins), and drugs.
    """
    
    def __init__(self, api_url: str = OPENTARGETS_API_URL):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self._cache = {}  # Cache for GraphQL responses

    def _execute_query(self, query: str, variables: Dict[str, Any], timeout: int = 8) -> Dict[str, Any]:
        """Execute a GraphQL query and return the response data with caching."""
        # Create a cache key from query and variables
        import json
        cache_key = f"{query}:{json.dumps(variables, sort_keys=True)}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        payload = {
            "query": query,
            "variables": variables
        }
        
        response = self.session.post(self.api_url, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        
        if "errors" in result:
            error_messages = [e.get("message", str(e)) for e in result["errors"]]
            raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
        
        data = result.get("data", {})
        self._cache[cache_key] = data
        return data
    
    def search(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        page: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search Open Targets Platform for entities matching the query.
        
        Args:
            query: Search query string
            entity_types: Optional list of entity types to filter ('disease', 'target', 'drug')
            page: Page index for pagination (0-indexed)
            size: Number of results per page
            
        Returns:
            Dict with 'total' count and 'hits' list of SearchResult objects
        """
        variables = {
            "queryString": query,
            "page": {"index": page, "size": size}
        }
        
        if entity_types:
            variables["entityNames"] = entity_types
        
        data = self._execute_query(SEARCH_QUERY, variables)
        search_data = data.get("search", {})
        
        # Convert hits to SearchResult objects - FULL VERSION with score and highlights
        hits = []
        for hit in search_data.get("hits", []):
            hits.append(SearchResult(
                id=hit.get("id", ""),
                name=hit.get("name", ""),
                entity=hit.get("entity", ""),
                description=hit.get("description"),
                score=hit.get("score"),
                highlights=hit.get("highlights")
            ))
        
        return {
            "total": search_data.get("total", 0),
            "hits": hits
        }
    
    def full_search(
        self,
        query: str,
        page: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        FULL SEARCH - Search ALL entity types without restrictions.
        This is the "Premium/Full" (full version) matching Open Targets Platform exactly.
        
        Returns diseases, targets (genes/proteins), AND drugs together,
        sorted by relevance score.
        
        Args:
            query: Search query string
            page: Page index for pagination
            size: Number of results per page
            
        Returns:
            Dict with 'total' count and 'hits' list of ALL entity types
        """
        # No entity_types filter = search ALL types
        return self.search(query, entity_types=None, page=page, size=size)
    
    def grouped_search(
        self,
        query: str,
        size: int = 25  # Reduced for speed - only need 3 per category
    ) -> Dict[str, Any]:
        """
        GROUPED SEARCH - Returns results organized by entity type for autocomplete UI.
        Mimics the Open Targets Platform autocomplete dropdown EXACTLY with sections:
        - topHit: The single best matching result
        - targets: Gene/protein results (ENSG IDs) - 3 items
        - diseases: Disease results (MONDO/EFO IDs) - 3 items
        - drugs: Drug results (CHEMBL IDs) - 3 items
        - studies: GWAS study results (GCST IDs) with trait names - 3 items
        - variants: Variant results - 3 items (if any)
        
        Args:
            query: Search query string
            size: Total results to fetch for grouping
            
        Returns:
            Dict with 'topHit', 'targets', 'diseases', 'drugs', 'studies', 'variants' sections
        """
        results = self.full_search(query, page=0, size=size)
        hits = results.get("hits", [])
        
        if not hits:
            return {
                "total": 0,
                "topHit": None,
                "targets": [],
                "diseases": [],
                "drugs": [],
                "studies": [],
                "variants": []
            }
        
        # Top hit is the first result (highest score)
        top_hit = hits[0]
        
        # Group remaining results by entity type - include variant
        grouped = {
            "target": [],
            "disease": [],
            "drug": [],
            "study": [],
            "variant": []
        }
        
        for hit in hits:
            entity_type = hit.entity
            if entity_type in grouped:
                grouped[entity_type].append(hit)
        
        # Limit to 3 items per section like Open Targets
        limited_studies = grouped["study"][:3]
        
        # Enrich studies with traitFromSource - PARALLEL for speed
        enriched_studies = []
        if limited_studies:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def fetch_study(study):
                study_details = self._get_study_details(study.id)
                if study_details:
                    return {
                        "id": study.id,
                        "name": study_details.get("traitFromSource") or study.name,
                        "entity": "study",
                        "description": study.description,
                        "score": study.score,
                        "highlights": study.highlights,
                        "study_type": study_details.get("studyType"),
                        "n_samples": study_details.get("nSamples"),
                        "n_cases": study_details.get("nCases")
                    }
                return study
            
            # Parallel fetch - 3x faster
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(fetch_study, s): i for i, s in enumerate(limited_studies)}
                results_map = {}
                for future in as_completed(futures):
                    idx = futures[future]
                    results_map[idx] = future.result()
                
                # Maintain order
                enriched_studies = [results_map[i] for i in range(len(limited_studies))]
        
        return {
            "total": results.get("total", 0),
            "topHit": top_hit,
            "targets": grouped["target"][:3],
            "diseases": grouped["disease"][:3],
            "drugs": grouped["drug"][:3],
            "studies": enriched_studies,
            "variants": grouped["variant"][:3]
        }
    
    def _get_study_details(self, study_id: str) -> Optional[Dict[str, Any]]:
        """Fetch study details including traitFromSource."""
        try:
            variables = {"studyId": study_id}
            data = self._execute_query(STUDY_QUERY, variables)
            return data.get("study", {})
        except Exception:
            return None
    
    def search_diseases(
        self,
        query: str,
        page: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search for diseases/phenotypes matching the query.
        
        Args:
            query: Disease name or partial name to search
            page: Page index for pagination
            size: Number of results per page
            
        Returns:
            Dict with 'total' count and 'hits' list of disease SearchResults
        """
        return self.search(query, entity_types=["disease"], page=page, size=size)
    
    def search_targets(
        self,
        query: str,
        page: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search for targets (genes/proteins) matching the query.
        
        Args:
            query: Gene symbol, protein name, or Ensembl ID to search
            page: Page index for pagination
            size: Number of results per page
            
        Returns:
            Dict with 'total' count and 'hits' list of target SearchResults
        """
        return self.search(query, entity_types=["target"], page=page, size=size)
    
    def get_disease_details(self, disease_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a disease.
        
        Args:
            disease_id: Disease ID (e.g., 'MONDO_0004975', 'EFO_0000249')
            
        Returns:
            Dict with full disease details
        """
        variables = {"efoId": disease_id}
        data = self._execute_query(DISEASE_QUERY, variables)
        return data.get("disease", {})
    
    def get_target_details(self, ensembl_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a target (gene/protein).
        
        Args:
            ensembl_id: Ensembl gene ID (e.g., 'ENSG00000130203')
            
        Returns:
            Dict with full target details
        """
        variables = {"ensemblId": ensembl_id}
        data = self._execute_query(TARGET_QUERY, variables)
        return data.get("target", {})
    
    def format_search_result_for_ui(self, result: SearchResult) -> Dict[str, Any]:
        """
        Format a search result for frontend display - FULL VERSION.
        
        Returns a dict matching the frontend's expected format with all fields.
        """
        return {
            "id": result.id,
            "name": result.name,
            "entity_type": result.entity,
            "description": result.description or "",
            "score": result.score,
            "highlights": result.highlights or [],
            "display_label": f"{result.name} ({result.id})"
        }
    
    def format_search_results_for_ui(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format search results for frontend display - FULL VERSION.
        """
        return {
            "total": results["total"],
            "hits": [self.format_search_result_for_ui(hit) for hit in results["hits"]]
        }
    
    def format_grouped_search_for_ui(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format grouped search results for frontend display.
        Returns structure matching Open Targets autocomplete UI EXACTLY.
        """
        def format_item(item):
            # Handle both SearchResult objects and enriched dict (studies)
            if isinstance(item, dict):
                return {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "entity_type": item.get("entity", ""),
                    "description": item.get("description", ""),
                    "score": item.get("score"),
                    "highlights": item.get("highlights", []),
                    "display_label": f"{item.get('name', '')} ({item.get('id', '')})",
                    # Study-specific fields
                    "study_type": item.get("study_type"),
                    "n_samples": item.get("n_samples"),
                    "n_cases": item.get("n_cases")
                }
            else:
                return self.format_search_result_for_ui(item)
        
        def format_list(items):
            return [format_item(h) for h in items]
        
        return {
            "total": results.get("total", 0),
            "topHit": self.format_search_result_for_ui(results["topHit"]) if results.get("topHit") else None,
            "targets": format_list(results.get("targets", [])),
            "diseases": format_list(results.get("diseases", [])),
            "drugs": format_list(results.get("drugs", [])),
            "studies": format_list(results.get("studies", [])),
            "variants": format_list(results.get("variants", []))
        }

