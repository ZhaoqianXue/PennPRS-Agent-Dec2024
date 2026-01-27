"""
OmicsPred API Client (Local Data Version) for PennPRS-Protein functionality.
Provides access to proteomics genetic scores from local TSV database.
"""

import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import time
import os
from pathlib import Path
from src.server.core.config import get_data_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_PATH = "data/omicspred/omicspred_scores_full.tsv"

class OmicsPredClient:
    """
    Client for querying the local OmicsPred dataset.
    Replaces remote API calls with local pandas operations.
    """
    
    def __init__(self):
        self.df = None
        self._data_loaded = False
    
    def load_data(self):
        """Lazy load the dataset into memory."""
        if self._data_loaded:
            return

        try:
            full_data_path = get_data_path(DATA_PATH)
            if not full_data_path.exists():
                logger.error(f"Data file not found at {full_data_path}")
                self.df = pd.DataFrame() # Empty fallback
                return

            t0 = time.time()
            # Dtypes optimization for speed
            self.df = pd.read_csv(full_data_path, sep='\t', dtype=str).fillna("")
            self._data_loaded = True
            print(f"[System] Loaded {len(self.df)} OmicsPred records in {time.time() - t0:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load OmicsPred data: {e}")
            self.df = pd.DataFrame()

    def _row_to_api_format(self, row: pd.Series) -> Dict[str, Any]:
        """Convert a flat dataframe row back to the nested API structure."""
        
        # Reconstruct Genes list
        genes = []
        g_names = str(row.get('genes_names', '')).split('|')
        g_ids = str(row.get('genes_external_ids', '')).split('|')
        
        for i, name in enumerate(g_names):
            if name:
                 genes.append({
                     "name": name,
                     "external_id": g_ids[i] if i < len(g_ids) else ""
                 })
        
        # Reconstruct Proteins list
        proteins = []
        p_names = str(row.get('proteins_names', '')).split('|')
        p_ids = str(row.get('proteins_external_ids', '')).split('|')
        
        for i, name in enumerate(p_names):
            if name:
                proteins.append({
                    "name": name,
                    "external_id": p_ids[i] if i < len(p_ids) else ""
                })

        # Publication
        publication = {
            "id": row.get('pub_id'),
            "title": row.get('pub_title'),
            "journal": row.get('pub_journal'),
            "doi": row.get('pub_doi'),
            "pmid": row.get('pub_pmid'),
            "date": row.get('pub_date'), # Key: date (matches UI)
            # "firstauthor" missing in TSV schema currently but implied
        }

        # Platform
        platform = {
            "name": row.get('platform_name'),
            "full_name": row.get('platform_full_name'),
            "technic": row.get('platform_technic'),
            "version": row.get('platform_name') # Simplified
        }

        # Dataset (Study)
        dataset_info = {
            "id": row.get('dataset_id'),
            "train_n": row.get('study_train_n'),
            "train_cohorts": str(row.get('study_train_cohorts', '')).split('|'),
            "train_ancestries": str(row.get('study_train_ancestries', '')).split('|'),
        }

        return {
            "id": row.get('id'),
            "opgs_id": row.get('id'), # Alias
            "name": row.get('name'),
            "trait_reported": row.get('trait_reported'),
            "trait_reported_id": row.get('trait_reported_id'),
            "method_name": row.get('method_name'),
            "variants_number": row.get('variants_number'),
            "variants_genomebuild": row.get('variants_genomebuild'),
            
            "genes": genes,
            "proteins": proteins,
            "publication": publication,
            "platform": platform,
            "dataset_info": dataset_info,
            
            # Flat fields for easier access
            "platform_version": row.get('platform_name'),
            "dataset_id": row.get('dataset_id'),
            "study_train_cohorts": row.get('study_train_cohorts'),
            "dataset_name": row.get('study_train_cohorts'), # Approx mapping
            
            # Ancestry (mock structure to match API expectations)
            "ancestry": {
                "dev": {
                    "count": row.get('study_train_n'),
                    "anc": { an: {} for an in dataset_info["train_ancestries"] if an }
                },
                "eval": {
                    "count": row.get('study_valid_n'),
                    "anc": { an: {} for an in str(row.get('study_valid_ancestries', '')).split('|') if an }
                }
            },
            
            "performance_data": {} # R2 metrics not in TSV
        }

    def search_scores_general(self, term: str, limit: int = 5000) -> List[Dict[str, Any]]:
        """
        General search across local OmicsPred data.
        """
        self.load_data()
        if self.df.empty:
            return []

        term_lower = term.lower().strip()
        t0 = time.time()
        
        # Vectorized string search on relevant columns
        # Case-insensitive contains using regex=False for simple substring matching
        mask = (
            self.df['trait_reported'].str.lower().str.contains(term_lower, regex=False, na=False) |
            self.df['genes_names'].str.lower().str.contains(term_lower, regex=False, na=False) |
            self.df['genes_external_ids'].str.lower().str.contains(term_lower, regex=False, na=False) |
            self.df['proteins_names'].str.lower().str.contains(term_lower, regex=False, na=False) |
            self.df['proteins_external_ids'].str.lower().str.contains(term_lower, regex=False, na=False) |
            self.df['id'].str.lower().str.contains(term_lower, regex=False, na=False)
        )
        
        matches = self.df[mask].copy()
        
        # Sort by sample size if possible (casted to float/int)
        try:
            matches['study_train_n_numeric'] = pd.to_numeric(matches['study_train_n'], errors='coerce').fillna(0)
            matches = matches.sort_values('study_train_n_numeric', ascending=False)
        except:
            pass

        results = [self._row_to_api_format(row) for _, row in matches.head(limit).iterrows()]
        
        print(f"[Timing] Local Search '{term}': {time.time() - t0:.4f}s (Matches: {len(results)})")
        return results

    def get_scores_by_platform(self, platform: str, max_results: int = 10000) -> List[Dict[str, Any]]:
        self.load_data()
        if self.df.empty: return []

        term_lower = platform.lower().strip()
        mask = self.df['platform_name'].str.lower().str.contains(term_lower, na=False)
        matches = self.df[mask].head(max_results)
        
        return [self._row_to_api_format(row) for _, row in matches.iterrows()]

    def search_scores_by_protein(self, protein_query: str) -> List[Dict[str, Any]]:
        # Redirect to general search
        return self.search_scores_general(protein_query)

    def get_gene_scores(self, gene_query: str) -> List[Dict[str, Any]]:
        # Redirect to general search
        return self.search_scores_general(gene_query)

    def get_score_details(self, score_id: str) -> Dict[str, Any]:
        """
        Fetch detailed score information from external OmicsPred APIs.
        1. Metadata from public API.
        2. Performance metrics from private API (reverse-engineered).
        """
        # 1. Fetch Metadata
        meta_url = f"https://rest.omicspred.org/api/score/{score_id}"
        meta_data = {}
        try:
            resp = requests.get(meta_url, timeout=10)
            if resp.status_code == 200:
                meta_data = resp.json()
            else:
                logger.warning(f"Metadata API request failed: {resp.status_code}")
                # Fallback to local
                meta_data = self._get_local_details(score_id)
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            meta_data = self._get_local_details(score_id)

        if not meta_data:
            return {}

        # 2. Fetch Performance Data (R2, Rho)
        # Found via browser inspection: https://rest-private-dot-sl925-phpc-1.nw.r.appspot.com/api/performance/search
        perf_url = f"https://rest-private-dot-sl925-phpc-1.nw.r.appspot.com/api/performance/search?opgs_id={score_id}"
        try:
            p_resp = requests.get(perf_url, timeout=10)
            if p_resp.status_code == 200:
                p_data = p_resp.json()
                meta_data['performance_raw'] = p_data.get('results', [])
            else:
                logger.warning(f"Performance API request failed: {p_resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching performance data: {e}")

        return meta_data

    def _get_local_details(self, score_id: str) -> Dict[str, Any]:
        """Fallback to local DB if API fails."""
        self.load_data()
        if self.df is not None and not self.df.empty:
            matches = self.df[self.df['id'] == score_id]
            if not matches.empty:
                return self._row_to_api_format(matches.iloc[0])
        return {}

    def list_platforms(self) -> List[Dict[str, Any]]:
        self.load_data()
        if self.df is None or self.df.empty: return []
        
        platforms = self.df['platform_name'].unique()
        return [{"name": p} for p in platforms if p]

    def format_score_for_ui(self, score: Dict[str, Any], details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format a score dictionary for UI consumption.
        TRANSFORMS raw API performance list into the dict format expected by ProteinDetailModal.
        """
        data = {**score, **(details or {})}
        
        # Safety checks for lists
        genes = data.get('genes', [])
        proteins = data.get('proteins', [])
        
        gene_name = genes[0]['name'] if genes else ""
        protein_name = proteins[0]['name'] if proteins else None # Strict: None if no protein annotation
        
        # Normalize Publication Data (Ensure 'date' field is present for UI)
        publication = data.get('publication')
        if publication and isinstance(publication, dict):
            if not publication.get('date') and publication.get('date_publication'):
                publication['date'] = publication.get('date_publication')
            # Ensure date is a string for .split('-') in frontend
            if publication.get('date'):
                publication['date'] = str(publication['date'])
        
        # Process Performance Data
        # Goal: Transform list of cohort results into dict: "Cohort_Metric": { estimate: val }
        # And extract max R2/Rho for summary
        
        perf_raw = data.get('performance_raw', [])
        performance_data = {} # The formatted dict for UI
        max_r2 = None
        max_rho = None
        
        if perf_raw:
            for item in perf_raw:
                cohort = item.get('cohort_label', 'Unknown')
                # stage = item.get('evaluation_type', '') # e.g. Training, External Validation
                
                metrics_list = item.get('performance_metrics', [])
                for m in metrics_list:
                    m_name = m.get('name_short', '') # R2, Rho
                    val = m.get('estimate')
                    
                    if val is not None:
                        # Build key e.g., "INTERVAL_R2" or "INTERVAL_Training_R2"
                        # ProteinDetailModal splits by '_' -> Cohort is first part.
                        # We'll use "Cohort_Metric" pattern.
                        # Note: ProteinDetailModal logic: `key.split('_')`. `cohortName = parts[0]`. `metricType = parts.slice(1)`
                        # If we have "INTERVAL_R2", cohort=INTERVAL, metric=R2. valid.
                        
                        key = f"{cohort}_{m_name}"
                        performance_data[key] = { "estimate": val }
                        
                        # Summary Metrics (try to get Training first, or Max)
                        if m_name == 'R2':
                            if max_r2 is None or val > max_r2: max_r2 = val
                        if m_name == 'Rho':
                            if max_rho is None or val > max_rho: max_rho = val

        # Populate summary metrics
        metrics = {
            "R2": max_r2, 
            "Rho": max_rho
        }
        
        # Handle ancestry count safely
        try:
            sample_size = int(float(data.get("ancestry", {}).get("dev", {}).get("count", 0)))
        except:
            sample_size = 0

        # Construct Dataset Name & Cohorts
        train_cohorts = data.get("dataset_info", {}).get("train_cohorts", [])
        if not train_cohorts and "study_train_cohorts" in data:
            raw_c = data.get("study_train_cohorts", "")
            if isinstance(raw_c, str):
                train_cohorts = [c.strip() for c in raw_c.split('|') if c.strip()]
        
        # Fallback 3: Extract from performance evaluations (common for API results)
        if not train_cohorts and perf_raw:
            train_cohorts = list(set([item.get('cohort_label') for item in perf_raw if item.get('cohort_label')]))

        dev_cohorts_str = ", ".join(train_cohorts) if train_cohorts else ""

        dataset_name = data.get("dataset_name")
        if not dataset_name:
             if not train_cohorts and "ancestry" in data:
                 dataset_name = data.get("dataset_id", "")
             else:
                 dataset_name = " / ".join(train_cohorts) if train_cohorts else data.get("dataset_id", "Unknown")

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "trait": data.get("trait_reported"), # Use raw trait reported
            "ancestry": "Multi-ancestry" if len(data.get("ancestry", {}).get("dev", {}).get("anc", {})) > 1 else "EUR",
            "method": data.get("method_name"),
            "metrics": metrics,
            "num_variants": data.get("variants_number"),
            "publication": data.get("publication"),
            "sample_size": sample_size,
            "source": f"OmicsPred ({'API' if perf_raw else 'Local'})",
            "download_url": f"https://www.omicspred.org/score/{data.get('id')}",
            
            "protein_name": protein_name,
            "gene_name": gene_name,
            "platform": data.get("platform", {}).get("name"),
            "dataset_name": dataset_name,
            "dataset_id": data.get("dataset_id"),
            "dev_cohorts": dev_cohorts_str,
            "tissue": data.get("tissue", {}).get("label") or data.get("tissue_label"),
            "tissue_id": data.get("tissue", {}).get("id") or data.get("tissue_id"),
            "genome_build": data.get("variants_genomebuild"),
            "license": data.get("license"),
            
            # Pass transform perf data (Legacy dict for summaries if needed)
            "performance_data": performance_data,
            # Pass RAW list for detailed table
            "evaluations": perf_raw,
            
            "genes": genes,
            "proteins": proteins,
            "ancestry_dev": data.get("ancestry", {}).get("dev", {}),
            "ancestry_eval": data.get("ancestry", {}).get("eval", {}),
            "trait_type": "Protein Expression",
            
            "uniprot_id": proteins[0].get("external_id") if proteins else None,
            "protein_description": "; ".join(proteins[0].get("descriptions", [])) if proteins else None
        }


