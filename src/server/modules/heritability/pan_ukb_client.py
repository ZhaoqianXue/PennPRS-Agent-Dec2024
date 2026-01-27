"""
Pan-UK Biobank client for multi-ancestry heritability data.

Data source: https://pan.ukbb.broadinstitute.org/downloads
Heritability manifest: https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/h2_manifest.tsv.bgz
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from thefuzz import fuzz, process

from src.server.core.config import get_data_path
from src.server.modules.heritability.models import HeritabilityEstimate, HeritabilitySource, Population

logger = logging.getLogger(__name__)


# Pan-UKB ancestry codes
PAN_UKB_ANCESTRIES = {
    "EUR": Population.EUR,
    "AFR": Population.AFR,
    "AMR": Population.AMR,
    "CSA": Population.CSA,
    "EAS": Population.EAS,
    "MID": Population.MID,
}


class PanUKBClient:
    """
    Client for querying Pan-UK Biobank heritability data.
    
    Pan-UKB provides multi-ancestry GWAS results for 7,228 phenotypes
    across 6 continental ancestry groups.
    """
    
    DEFAULT_DATA_PATH = "data/heritability/pan_ukb/pan_ukb_h2.tsv"
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize the Pan-UKB client.
        
        Args:
            data_path: Path to the heritability manifest file.
        """
        self.data_path = data_path or get_data_path(self.DEFAULT_DATA_PATH)
        self._df: Optional[pd.DataFrame] = None
        self._loaded = False
    
    def _load_data(self) -> None:
        """Load the Pan-UKB heritability manifest."""
        if self._loaded:
            return
            
        if not self.data_path.exists():
            logger.warning(f"Pan-UKB data file not found: {self.data_path}")
            self._df = pd.DataFrame()
            self._loaded = True
            return
        
        try:
            # Handle both .bgz and .tsv formats
            if str(self.data_path).endswith('.bgz'):
                self._df = pd.read_csv(self.data_path, sep='\t', compression='gzip')
            else:
                self._df = pd.read_csv(self.data_path, sep='\t')
            
            self._df.columns = self._df.columns.str.strip()
            logger.info(f"Loaded Pan-UKB data: {len(self._df)} records")
            self._loaded = True
            
        except Exception as e:
            logger.error(f"Error loading Pan-UKB data: {e}")
            self._df = pd.DataFrame()
            self._loaded = True
    
    @property
    def df(self) -> pd.DataFrame:
        """Get the loaded DataFrame."""
        if not self._loaded:
            self._load_data()
        return self._df
    
    def search_trait(
        self,
        trait: str,
        ancestry: Optional[str] = None,
        min_score: int = 60,
        limit: int = 50
    ) -> list[HeritabilityEstimate]:
        """
        Search for heritability estimates by trait name.
        
        Args:
            trait: Trait name to search for
            ancestry: Filter by specific ancestry (EUR, AFR, etc.)
            min_score: Minimum fuzzy match score
            limit: Maximum results
            
        Returns:
            List of HeritabilityEstimate objects
        """
        if self.df.empty:
            return []
        
        # Pan-UKB uses phenocode as the trait identifier
        trait_col = self._find_column(['phenocode', 'description', 'phenotype', 'trait', 'pheno_name'])
        if trait_col is None:
            logger.error(f"No trait column found. Columns: {self.df.columns.tolist()}")
            return []
        
        # Fuzzy match
        all_traits = self.df[trait_col].dropna().unique().tolist()
        # Convert to strings for fuzzy matching
        all_traits = [str(t) for t in all_traits]
        matches = process.extract(trait, all_traits, scorer=fuzz.token_set_ratio, limit=limit)
        
        results = []
        for match_trait, score in matches:
            if score < min_score:
                continue
                
            trait_rows = self.df[self.df[trait_col].astype(str) == match_trait]
            
            # Filter by ancestry if specified (Pan-UKB uses 'pop' column)
            pop_col = self._find_column(['pop', 'ancestry', 'population'])
            if ancestry and pop_col:
                trait_rows = trait_rows[trait_rows[pop_col] == ancestry]
            
            for _, row in trait_rows.iterrows():
                try:
                    # Pan-UKB actual columns: estimates.ldsc.h2_observed, etc.
                    h2_obs = self._get_float(row, [
                        'estimates.final.h2_observed',
                        'estimates.ldsc.h2_observed', 
                        'h2_observed', 'h2_obs', 'h2'
                    ])
                    if h2_obs is None:
                        continue
                    
                    population = "EUR"
                    if pop_col and pd.notna(row.get(pop_col)):
                        population = str(row[pop_col])
                    
                    estimate = HeritabilityEstimate(
                        trait_name=str(match_trait),
                        trait_id=self._get_str(row, ['phenocode', 'trait_id', 'pheno']),
                        h2_obs=h2_obs,
                        h2_obs_se=self._get_float(row, [
                            'estimates.final.h2_observed_se',
                            'estimates.ldsc.h2_observed_se',
                            'h2_observed_se', 'h2_obs_se', 'h2_se'
                        ]),
                        h2_liability=self._get_float(row, [
                            'estimates.final.h2_liability',
                            'estimates.ldsc.h2_liability',
                            'h2_liability', 'h2_lia'
                        ]),
                        h2_liability_se=self._get_float(row, [
                            'estimates.final.h2_liability_se',
                            'estimates.ldsc.h2_liability_se'
                        ]),
                        population=population,
                        source=HeritabilitySource.PAN_UKB,
                        n_samples=self._get_int(row, ['n_cases', 'N', 'n_samples', 'N_ancestry_QC_pass']),
                        method="ldsc",
                        h2_z=self._get_float(row, [
                            'estimates.final.h2_z',
                            'estimates.ldsc.h2_z',
                            'h2_z', 'z_h2'
                        ])
                    )
                    results.append(estimate)
                    
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue
        
        return results
    
    def get_ancestry_breakdown(self, trait: str) -> dict[str, list[HeritabilityEstimate]]:
        """
        Get heritability estimates grouped by ancestry.
        
        Args:
            trait: Trait name to search
            
        Returns:
            Dict mapping ancestry code to list of estimates
        """
        all_results = self.search_trait(trait, min_score=70)
        
        breakdown: dict[str, list[HeritabilityEstimate]] = {}
        for est in all_results:
            if est.population not in breakdown:
                breakdown[est.population] = []
            breakdown[est.population].append(est)
        
        return breakdown
    
    def _find_column(self, candidates: list[str]) -> Optional[str]:
        """Find the first matching column from candidates."""
        for col in candidates:
            if col in self.df.columns:
                return col
        return None
    
    def _get_float(self, row: pd.Series, columns: list[str]) -> Optional[float]:
        """Try to get a float value from multiple possible column names."""
        for col in columns:
            if col in row.index:
                val = row[col]
                if pd.notna(val):
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        continue
        return None
    
    def _get_int(self, row: pd.Series, columns: list[str]) -> Optional[int]:
        """Try to get an int value from multiple possible column names."""
        for col in columns:
            if col in row.index:
                val = row[col]
                if pd.notna(val):
                    try:
                        return int(float(val))
                    except (ValueError, TypeError):
                        continue
        return None
    
    def _get_str(self, row: pd.Series, columns: list[str]) -> Optional[str]:
        """Try to get a string value from multiple possible column names."""
        for col in columns:
            if col in row.index:
                val = row[col]
                if pd.notna(val):
                    return str(val)
        return None
    
    def get_available_ancestries(self) -> list[str]:
        """Get list of available ancestry codes."""
        pop_col = self._find_column(['pop', 'ancestry', 'population'])
        if pop_col and not self.df.empty:
            return self.df[pop_col].dropna().unique().tolist()
        return list(PAN_UKB_ANCESTRIES.keys())
