"""
OmicsPred API Client for PennPRS-Protein functionality.
Provides access to proteomics genetic scores from https://www.omicspred.org/
"""

import requests
from typing import List, Dict, Any, Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OmicsPredClient:
    """
    Client for interacting with the OmicsPred REST API.
    Documentation: https://rest.omicspred.org/
    """
    BASE_URL = "https://rest.omicspred.org"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def search_scores(
        self, 
        query: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 250,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for genetic scores in OmicsPred.
        
        Args:
            query: Optional search query (protein name, gene symbol, etc.)
            platform: Optional platform filter ('Olink', 'Somalogic')
            limit: Maximum results per page (max 500, default 250)
            offset: Pagination offset
            
        Returns:
            List of score dictionaries
        """
        try:
            url = f"{self.BASE_URL}/api/score/search"
            params = {
                "limit": min(limit, 500),
                "offset": offset
            }
            
            if platform:
                params["platform"] = platform
                
            t0 = time.time()
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            print(f"[Timing] OmicsPred Score Search: {time.time() - t0:.4f}s (Count: {len(results)})")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching OmicsPred scores: {e}")
            return []
    
    def search_scores_by_protein(self, protein_query: str) -> List[Dict[str, Any]]:
        """
        Search for genetic scores associated with a specific protein.
        
        Args:
            protein_query: Protein name, gene symbol, or UniProt ID
            
        Returns:
            List of score dictionaries
        """
        try:
            # First try direct protein search
            url = f"{self.BASE_URL}/api/score/search/protein/{protein_query}"
            
            t0 = time.time()
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                print(f"[Timing] OmicsPred Protein Search '{protein_query}': {time.time() - t0:.4f}s (Count: {len(results)})")
                return results
            
            # Fallback: Search using protein/search endpoint with gene parameter
            url = f"{self.BASE_URL}/api/protein/search"
            response = self.session.get(url, params={"gene": protein_query}, timeout=30)
            
            if response.status_code == 200:
                protein_data = response.json()
                protein_results = protein_data.get("results", [])
                
                # Collect all score IDs from matching proteins
                all_scores = []
                for protein in protein_results:
                    scores = protein.get("associated_scores", [])
                    all_scores.extend(scores)
                
                print(f"[Timing] OmicsPred Gene Search '{protein_query}': {time.time() - t0:.4f}s (Scores: {len(all_scores)})")
                return all_scores
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching OmicsPred by protein '{protein_query}': {e}")
            return []
    
    def get_score_details(self, score_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific score ID.
        
        Args:
            score_id: OPGS score ID (e.g., OPGS000001)
            
        Returns:
            Score details dictionary
        """
        try:
            url = f"{self.BASE_URL}/api/score/{score_id}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting OmicsPred details for {score_id}: {e}")
            return {}
    
    def get_protein_details(self, protein_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific protein.
        
        Args:
            protein_id: Protein ID (gene symbol or UniProt ID)
            
        Returns:
            Protein details dictionary
        """
        try:
            url = f"{self.BASE_URL}/api/protein/{protein_id}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting protein details for {protein_id}: {e}")
            return {}
    
    def get_gene_scores(self, gene_query: str) -> List[Dict[str, Any]]:
        """
        Get all genetic scores for a specific gene.
        Supports both Ensembl IDs (ENSG...) and gene symbols (COL1A1).
        
        Args:
            gene_query: Gene Ensembl ID or symbol (e.g., ENSG00000108821 or COL1A1)
            
        Returns:
            List of score dictionaries associated with this gene
        """
        try:
            t0 = time.time()
            
            # Try gene endpoint first
            url = f"{self.BASE_URL}/api/gene/{gene_query}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # The gene endpoint returns gene info with associated scores
                scores = data.get("associated_scores", [])
                if not scores:
                    # Try getting scores from 'scores' key
                    scores = data.get("scores", [])
                print(f"[Timing] OmicsPred Gene '{gene_query}': {time.time() - t0:.4f}s (Count: {len(scores)})")
                return scores
            
            # Fallback: Search using protein endpoint with gene filter
            url = f"{self.BASE_URL}/api/protein/search"
            response = self.session.get(url, params={"gene": gene_query}, timeout=30)
            
            if response.status_code == 200:
                protein_data = response.json()
                protein_results = protein_data.get("results", [])
                
                all_scores = []
                for protein in protein_results:
                    scores = protein.get("associated_scores", [])
                    all_scores.extend(scores)
                
                print(f"[Timing] OmicsPred Gene Search (fallback) '{gene_query}': {time.time() - t0:.4f}s (Scores: {len(all_scores)})")
                return all_scores
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting gene scores for '{gene_query}': {e}")
            return []

    
    def list_platforms(self) -> List[Dict[str, Any]]:
        """
        List available omics platforms (Olink, Somalogic, etc.).
        
        Returns:
            List of platform dictionaries
        """
        try:
            url = f"{self.BASE_URL}/api/platform"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Error listing OmicsPred platforms: {e}")
            return []
    
    def get_scores_by_platform(self, platform: str, max_results: int = 10000) -> List[Dict[str, Any]]:
        """
        Get all scores for a specific platform with parallel pagination support.
        Includes robust retry logic and deduplication.
        
        Args:
            platform: Platform name ('Olink', 'Somalogic')
            max_results: Maximum results to fetch
            
        Returns:
            List of score dictionaries
        """
        import concurrent.futures
        import math
        import time
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Setup a dedicated session for parallel requests with retries
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,  # wait 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        all_results = []
        seen_ids = set()  # Deduplication
        page_size = 500
        
        try:
            t0 = time.time()
            
            # 1. Fetch first page to get metadata (count)
            url = f"{self.BASE_URL}/api/proteomics/{platform}"
            # Use max page size to minimize requests
            params = {"limit": page_size, "offset": 0}
            
            # Initial request with retry
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            for res in results:
                sid = res.get("id")
                if sid and sid not in seen_ids:
                    seen_ids.add(sid)
                    all_results.append(res)
            
            total_count = data.get("count", 0)
            print(f"[Metadata] Platform '{platform}' reports count: {total_count}")
            
            # If we already have enough, return
            if len(all_results) >= total_count or len(all_results) >= max_results:
                return all_results[:max_results]
                
            # 2. Parallel fetch for remaining pages
            needed = min(total_count, max_results) - len(results) # rough estimate
            # Recalculate pages needed based on total
            num_pages = math.ceil(total_count / page_size)
            
            offsets = [i * page_size for i in range(1, num_pages)]
            
            # Limit concurrency to avoid 500 errors
            max_workers = 5 
            print(f"[Parallel] Spawning {len(offsets)} tasks (workers={max_workers}) for '{platform}'")
            
            def fetch_page(offset):
                # Inner manual retry for extra safety
                for attempt in range(3):
                    try:
                        p_response = session.get(
                            f"{self.BASE_URL}/api/proteomics/{platform}", 
                            params={"limit": page_size, "offset": offset},
                            timeout=60
                        )
                        p_response.raise_for_status()
                        return p_response.json().get("results", [])
                    except Exception as ex:
                        if attempt == 2:
                            logger.error(f"Failed to fetch {platform} offset {offset} after 3 attempts: {ex}")
                            return []
                        time.sleep(1 * (attempt + 1))
                return []

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_offset = {executor.submit(fetch_page, o): o for o in offsets}
                
                for future in concurrent.futures.as_completed(future_to_offset):
                    page_results = future.result()
                    for res in page_results:
                        sid = res.get("id")
                        # Some APIs return duplicates across pages if data updates, so we dedup
                        if sid and sid not in seen_ids:
                            seen_ids.add(sid)
                            all_results.append(res)

            print(f"[Timing] OmicsPred Platform '{platform}': {time.time() - t0:.4f}s (Total Unique: {len(all_results)}, Reported: {total_count})")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error getting scores for platform '{platform}': {e}")
            return all_results

    def search_scores_general(self, term: str, limit: int = 5000) -> List[Dict[str, Any]]:
        """
        General search across all OmicsPred data.
        Uses multiple endpoints to find matching scores.
        
        Args:
            term: Search term (protein name, gene, etc.)
            limit: Maximum results
            
        Returns:
            List of formatted score dictionaries for UI consumption
        """
        import concurrent.futures
        
        all_results = []
        seen_ids = set()
        
        try:
            t0 = time.time()
            
            # Strategy 1: Direct protein/gene search
            protein_scores = self.search_scores_by_protein(term)
            for score in protein_scores:
                sid = score.get("opgs_id") or score.get("id")
                if sid and sid not in seen_ids:
                    seen_ids.add(sid)
                    all_results.append(score)
            
            # Strategy 2: If no results, try listing some scores and filtering
            if not all_results:
                # Try from both major platforms - fetch ALL to ensure we don't miss matches
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(self.get_scores_by_platform, "Olink", 10000),
                        executor.submit(self.get_scores_by_platform, "Somalogic", 10000)
                    ]
                    
                    term_lower = term.lower()
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            scores = future.result()
                            for score in scores:
                                # Extract gene name from genes array safely
                                genes = score.get("genes", [])
                                gene_name = ""
                                gene_desc = ""
                                
                                if genes:
                                    first_gene = genes[0]
                                    gene_name = first_gene.get("name", "").lower()
                                    # Safe access to descriptions list
                                    descriptions = first_gene.get("descriptions", [])
                                    if descriptions and len(descriptions) > 0:
                                        gene_desc = (descriptions[0] or "").lower()
                                
                                # Match on gene name or description
                                if (term_lower in gene_name or 
                                    term_lower in gene_desc or
                                    gene_name.startswith(term_lower)):
                                    sid = score.get("id")
                                    if sid and sid not in seen_ids:
                                        seen_ids.add(sid)
                                        all_results.append(score)
                        except Exception as exc:
                            logger.error(f"Platform search generated exception: {exc}")
            
            print(f"[Timing] OmicsPred General Search '{term}': {time.time() - t0:.4f}s (Total: {len(all_results)})")
            
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in general OmicsPred search for '{term}': {e}")
            return []
    def format_score_for_ui(self, score: Dict[str, Any], details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format an OmicsPred score for frontend consumption.
        Preserves all original data structures for detailed modal display.
        
        Args:
            score: Raw score data from API
            details: Optional detailed score data
            
        Returns:
            Formatted dictionary with both summary and full data
        """
        # Merge score and details if provided
        data = {**score, **(details or {})}
        
        # Extract score ID
        score_id = data.get("id") or "Unknown"
        
        # Extract gene info - preserve full array
        genes = data.get("genes", [])
        gene_info = genes[0] if genes else {}
        gene_name = gene_info.get("name", "")
        gene_description = gene_info.get("descriptions", [""])[0] if gene_info.get("descriptions") else ""
        gene_ensembl_id = gene_info.get("external_id", "")
        
        # Extract protein info - preserve full array
        proteins = data.get("proteins", [])
        protein_info = proteins[0] if proteins else {}
        protein_name = protein_info.get("name", "") or gene_description
        uniprot_id = protein_info.get("external_id", "")
        protein_synonyms = protein_info.get("synonyms", [])
        protein_descriptions = protein_info.get("descriptions", [])
        
        # Display name prioritization
        display_name = protein_name or gene_description or gene_name or score_id
        
        # Extract metrics summary from performance_data
        perf_data = data.get("performance_data", {})
        metrics = {}
        
        # Find training R2
        train_r2 = None
        train_rho = None
        for key, val in perf_data.items():
            if isinstance(val, dict) and "estimate" in val:
                estimate = val.get("estimate")
                if "R2" in key and "training" in key.lower():
                    train_r2 = round(estimate, 4) if estimate else None
                    metrics["R2"] = train_r2
                elif "Rho" in key and "training" in key.lower():
                    train_rho = round(estimate, 3) if estimate else None
                    metrics["Rho"] = train_rho
        
        # Extract ancestry information - preserve full structure
        ancestry_data = data.get("ancestry", {})
        dev_ancestry = ancestry_data.get("dev", {})
        eval_ancestry = ancestry_data.get("eval", {})
        dev_count = dev_ancestry.get("count", 0)
        eval_count = eval_ancestry.get("count", 0)
        
        # Get primary ancestry code
        dev_anc = dev_ancestry.get("anc", {})
        ancestry_code = "EUR"  # Default
        if dev_anc:
            largest = max(dev_anc.items(), key=lambda x: x[1].get("dist", 0) if isinstance(x[1], dict) else 0)
            ancestry_code = largest[0]
        
        # Extract publication info - preserve full structure
        pub_data = data.get("publication", {})
        publication = None
        if pub_data:
            publication = {
                "id": pub_data.get("id"),
                "citation": f"{pub_data.get('firstauthor', 'Unknown')} et al. ({pub_data.get('date_publication', '')[:4] if pub_data.get('date_publication') else ''}) {pub_data.get('journal', '')}",
                "doi": pub_data.get("doi", ""),
                "pmid": pub_data.get("pmid"),
                "title": pub_data.get("title"),
                "date": pub_data.get("date_publication"),
                "journal": pub_data.get("journal"),
                "firstauthor": pub_data.get("firstauthor")
            }
        
        # Build formatted response with full data preservation
        return {
            # === Summary Fields (for cards) ===
            "id": score_id,
            "name": display_name,
            "trait": display_name,
            "ancestry": ancestry_code,
            "method": "Omic Genetic Score",
            "metrics": metrics,
            "num_variants": data.get("variants_number") or 0,
            "publication": publication,
            "sample_size": dev_count,
            "source": "OmicsPred",
            "download_url": f"https://www.omicspred.org/score/{score_id}",
            
            # === OmicsPred-Specific Fields ===
            "protein_name": protein_name,
            "gene_name": gene_name,
            "gene_ensembl_id": gene_ensembl_id,
            "uniprot_id": uniprot_id,
            "protein_synonyms": protein_synonyms,
            "protein_description": protein_descriptions[0] if protein_descriptions else "",
            
            # Platform / Dataset
            "platform": data.get("platform_version") or "Unknown",
            "dataset_name": data.get("dataset_name"),
            "dataset_id": data.get("dataset_id"),
            
            # Development Ancestry details
            "dev_sample_size": dev_count,
            "eval_sample_size": eval_count,
            "ancestry_dev": dev_ancestry,
            "ancestry_eval": eval_ancestry,
            
            # Full performance data for detail modal
            "performance_data": perf_data,
            
            # Full arrays for deep detail
            "genes": genes,
            "proteins": proteins,
            
            # Type marker
            "trait_type": "Protein Expression",
        }

