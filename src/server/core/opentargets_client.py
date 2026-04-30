"""
Open Targets Platform GraphQL Client

This module provides a client for querying the Open Targets Platform GraphQL API,
implementing search functionality identical to https://platform.opentargets.org

API Endpoint: https://api.platform.opentargets.org/api/v4/graphql
"""

import json
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Open Targets Platform GraphQL API endpoint
OPENTARGETS_API_URL = "https://api.platform.opentargets.org/api/v4/graphql"

logger = logging.getLogger(__name__)


class OpenTargetsRequestError(RuntimeError):
    """
    Error raised when Open Targets GraphQL request fails.

    This is intentionally lightweight (no external deps) and provides enough context
    to debug transient upstream failures without crashing the whole workflow.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        variables: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
        self.errors = errors
        self.variables = variables


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

# GraphQL query for disease associated targets
ASSOCIATED_TARGETS_QUERY = """
query DiseaseAssociatedTargets($efoId: String!) {
  disease(efoId: $efoId) {
    associatedTargets {
      rows {
        target {
          id
          approvedSymbol
        }
        score
      }
    }
  }
}
"""

DISEASE_TARGET_PROFILE_QUERY = """
query DiseaseTargetProfile($efoId: String!, $page: Pagination!) {
  disease(efoId: $efoId) {
    id
    name
    therapeuticAreas {
      id
      name
    }
    ancestors
    associatedTargets(page: $page) {
      rows {
        score
        datatypeScores {
          id
          score
        }
        target {
          id
          approvedSymbol
          approvedName
        }
      }
    }
    drugAndClinicalCandidates {
      count
    }
  }
}
"""

# GraphQL query for disease phenotypes (HPO annotations)
DISEASE_PHENOTYPES_QUERY = """
query DiseasePhenotypes($efoId: String!, $page: Pagination!) {
  disease(efoId: $efoId) {
    phenotypes(page: $page) {
      count
      rows {
        phenotypeHPO {
          id
          name
        }
        evidence {
          frequencyHPO {
            label
          }
        }
      }
    }
  }
}
"""

# GraphQL query for target tractability (druggability)
TARGET_TRACTABILITY_QUERY = """
query TargetTractability($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    tractability {
      label
      modality
      value
    }
  }
}
"""

# GraphQL query for target pathways
TARGET_PATHWAYS_QUERY = """
query TargetPathways($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    pathways {
      pathway
      pathwayId
    }
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
        adapter = HTTPAdapter(pool_connections=64, pool_maxsize=64)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self._cache = {}  # Cache for GraphQL responses

    def _execute_query(self, query: str, variables: Dict[str, Any], timeout: int = 15) -> Dict[str, Any]:
        """Execute a GraphQL query and return the response data with caching."""
        # Create a cache key from query and variables
        cache_key = f"{query}:{json.dumps(variables, sort_keys=True)}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        payload = {
            "query": query,
            "variables": variables
        }

        # Small retry for transient upstream issues (e.g., "Internal server error").
        # Keep it conservative to avoid slowing down the workflow.
        max_attempts = 2
        last_exc: Optional[Exception] = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.post(self.api_url, json=payload, timeout=timeout)
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < max_attempts:
                    time.sleep(0.25 * attempt)
                    continue
                raise OpenTargetsRequestError(
                    f"Open Targets request failed after {attempt} attempts: {exc}",
                    variables=variables,
                ) from exc

            status_code = response.status_code
            response_text = (response.text or "")[:2000]

            # HTTP-level failures.
            if status_code >= 400:
                err = OpenTargetsRequestError(
                    f"Open Targets HTTP error: status_code={status_code}",
                    status_code=status_code,
                    response_text=response_text,
                    variables=variables,
                )
                if attempt < max_attempts and status_code in (429, 500, 502, 503, 504):
                    last_exc = err
                    time.sleep(0.25 * attempt)
                    continue
                raise err

            # GraphQL-level failures.
            try:
                result = response.json()
            except ValueError as exc:
                err = OpenTargetsRequestError(
                    "Open Targets returned non-JSON response",
                    status_code=status_code,
                    response_text=response_text,
                    variables=variables,
                )
                if attempt < max_attempts:
                    last_exc = err
                    time.sleep(0.25 * attempt)
                    continue
                raise err from exc

            gql_errors = result.get("errors") if isinstance(result, dict) else None
            if gql_errors:
                error_messages = [e.get("message", str(e)) for e in gql_errors if isinstance(e, dict)]
                message = "; ".join(error_messages) if error_messages else str(gql_errors)
                err = OpenTargetsRequestError(
                    f"Open Targets GraphQL errors: {message}",
                    status_code=status_code,
                    response_text=response_text,
                    errors=gql_errors if isinstance(gql_errors, list) else None,
                    variables=variables,
                )
                # Retry only for common transient upstream failures.
                if attempt < max_attempts and any("internal server error" in (m or "").lower() for m in error_messages):
                    last_exc = err
                    time.sleep(0.25 * attempt)
                    continue
                raise err

            data = result.get("data", {}) if isinstance(result, dict) else {}
            self._cache[cache_key] = data
            return data

        # Should never happen, but keep mypy/runtime safe.
        if last_exc:
            raise last_exc
        raise OpenTargetsRequestError("Open Targets query failed with unknown error", variables=variables)
    
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
    
    def get_disease_targets(self, efo_id: str) -> List[Dict[str, Any]]:
        """
        Get targets associated with a disease.
        
        Args:
            efo_id: Disease ID (e.g., 'EFO_0000384')
            
        Returns:
            List of associated targets with symbols and scores
        """
        variables = {"efoId": efo_id}
        data = self._execute_query(ASSOCIATED_TARGETS_QUERY, variables)
        disease_data = data.get("disease", {})
        if not disease_data:
            return []
        
        rows = disease_data.get("associatedTargets", {}).get("rows", [])
        results = []
        for row in rows:
            target = row.get("target", {})
            results.append({
                "id": target.get("id"),
                "symbol": target.get("approvedSymbol"),
                "score": row.get("score")
            })
        return results

    def get_disease_target_profile(
        self,
        efo_id: str,
        *,
        page_index: int = 0,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Fetch a richer disease profile for transfer reasoning.

        Returns associated target rows with datatype score breakdowns plus a
        disease-level clinical/drug candidate count.
        """
        variables = {
            "efoId": efo_id,
            "page": {"index": page_index, "size": page_size},
        }
        data = self._execute_query(DISEASE_TARGET_PROFILE_QUERY, variables)
        disease = data.get("disease") or {}
        if not disease:
            return {
                "id": efo_id,
                "name": None,
                "associated_targets": [],
                "clinical_candidate_count": None,
                "therapeutic_areas": [],
                "ancestors": [],
            }

        rows = disease.get("associatedTargets", {}).get("rows", []) or []
        associated_targets: List[Dict[str, Any]] = []
        for row in rows:
            target = row.get("target") or {}
            associated_targets.append(
                {
                    "id": target.get("id"),
                    "approvedSymbol": target.get("approvedSymbol"),
                    "approvedName": target.get("approvedName"),
                    "score": row.get("score"),
                    "datatypeScores": row.get("datatypeScores") or [],
                }
            )

        therapeutic_areas = [
            {"id": ta.get("id"), "name": ta.get("name")}
            for ta in (disease.get("therapeuticAreas") or [])
            if ta.get("id")
        ]
        ancestors = []
        for anc in disease.get("ancestors") or []:
            if isinstance(anc, dict):
                anc_id = anc.get("id")
                if anc_id:
                    ancestors.append({"id": anc_id, "name": anc.get("name") or anc_id})
            elif anc:
                anc_id = str(anc)
                ancestors.append({"id": anc_id, "name": anc_id})

        return {
            "id": disease.get("id"),
            "name": disease.get("name"),
            "associated_targets": associated_targets,
            "clinical_candidate_count": (disease.get("drugAndClinicalCandidates") or {}).get("count"),
            "therapeutic_areas": therapeutic_areas,
            "ancestors": ancestors,
        }

    def get_disease_phenotypes(
        self,
        efo_id: str,
        *,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fetch HPO phenotype annotations for a disease.

        Returns a list of dicts with 'hpo_id', 'hpo_name', and optional
        'frequency' label.
        """
        variables = {
            "efoId": efo_id,
            "page": {"index": 0, "size": page_size},
        }
        data = self._execute_query(DISEASE_PHENOTYPES_QUERY, variables)
        disease = data.get("disease") or {}
        phenotypes_block = disease.get("phenotypes") or {}
        rows = phenotypes_block.get("rows") or []
        results: List[Dict[str, Any]] = []
        for row in rows:
            hpo = row.get("phenotypeHPO") or {}
            hpo_id = hpo.get("id")
            if not hpo_id:
                continue
            evidence = row.get("evidence") or {}
            freq_hpo = evidence.get("frequencyHPO") or {}
            results.append({
                "hpo_id": hpo_id,
                "hpo_name": hpo.get("name") or "",
                "frequency": freq_hpo.get("label"),
            })
        return results

    def get_target_druggability(self, ensembl_id: str) -> str:
        """
        Get tractability (druggability) assessment for a target.
        
        Args:
            ensembl_id: Ensembl gene ID
            
        Returns:
            String description of druggability (e.g., 'High', 'Medium', 'Low')
        """
        variables = {"ensemblId": ensembl_id}
        data = self._execute_query(TARGET_TRACTABILITY_QUERY, variables)
        target_data = data.get("target", {})
        if not target_data:
            return "Unknown"
        
        tractability = target_data.get("tractability", [])
        # Simple heuristic: if any modality has 'value' true for high-level categories
        # This can be refined based on specific needs
        high_confidence = False
        medium_confidence = False
        
        for item in tractability:
            if item.get("value") is True:
                label = item.get("label", "").lower()
                if "clinical" in label or "approved" in label:
                    high_confidence = True
                elif "discovery" in label or "pre-clinical" in label:
                    medium_confidence = True
        
        if high_confidence:
            return "High"
        if medium_confidence:
            return "Medium"
        return "Low"

    def get_target_pathways(self, ensembl_id: str) -> List[str]:
        """
        Get pathways associated with a target.
        
        Args:
            ensembl_id: Ensembl gene ID
            
        Returns:
            List of pathway names
        """
        variables = {"ensemblId": ensembl_id}
        data = self._execute_query(TARGET_PATHWAYS_QUERY, variables)
        target_data = data.get("target", {})
        if not target_data:
            return []
        
        pathways = target_data.get("pathways", [])
        return [p.get("pathway") for p in pathways if p.get("pathway")]

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
