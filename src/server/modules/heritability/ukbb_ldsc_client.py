"""
UKBB LDSC client for heritability data from Neale Lab.

Data source: https://nealelab.github.io/UKBB_ldsc/
European-ancestry focused LDSC heritability estimates.
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from thefuzz import fuzz, process

from src.server.core.config import get_data_path
from src.server.modules.heritability.models import HeritabilityEstimate, HeritabilitySource

logger = logging.getLogger(__name__)


class UKBBLDSCClient:
    """
    Client for querying UKBB LDSC heritability data from Neale Lab.
    
    Provides high-quality LD score regression heritability estimates
    for 2,419 UK Biobank phenotypes (primarily European ancestry).
    """
    
    DEFAULT_DATA_PATH = "data/heritability/ukbb_ldsc/ukbb_ldsc.tsv"
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize the UKBB LDSC client.
        
        Args:
            data_path: Path to the UKBB LDSC data file.
        """
        self.data_path = data_path or get_data_path(self.DEFAULT_DATA_PATH)
        self._df: Optional[pd.DataFrame] = None
        self._loaded = False
    
    def _load_data(self) -> None:
        """Load the UKBB LDSC data file."""
        if self._loaded:
            return
            
        if not self.data_path.exists():
            logger.warning(f"UKBB LDSC data file not found: {self.data_path}")
            self._df = pd.DataFrame()
            self._loaded = True
            return
        
        try:
            if str(self.data_path).endswith('.gz'):
                self._df = pd.read_csv(self.data_path, sep='\t', compression='gzip')
            else:
                self._df = pd.read_csv(self.data_path, sep='\t')
            
            self._df.columns = self._df.columns.str.strip()
            logger.info(f"Loaded UKBB LDSC data: {len(self._df)} records")
            self._loaded = True
            
        except Exception as e:
            logger.error(f"Error loading UKBB LDSC data: {e}")
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
        min_score: int = 60,
        limit: int = 50
    ) -> list[HeritabilityEstimate]:
        """
        Search for heritability estimates by trait name.
        
        Args:
            trait: Trait name to search for
            min_score: Minimum fuzzy match score
            limit: Maximum results
            
        Returns:
            List of HeritabilityEstimate objects
        """
        if self.df.empty:
            return []
        
        # UKBB LDSC uses 'description' column for trait names
        trait_col = self._find_column(['description', 'phenotype', 'Phenotype', 'trait'])
        if trait_col is None:
            logger.error(f"No trait column found. Columns: {self.df.columns.tolist()}")
            return []
        
        # Fuzzy match
        all_traits = self.df[trait_col].dropna().unique().tolist()
        # Convert to strings for matching
        all_traits = [str(t) for t in all_traits]
        matches = process.extract(trait, all_traits, scorer=fuzz.token_set_ratio, limit=limit)
        
        results = []
        for match_trait, score in matches:
            if score < min_score:
                continue
                
            trait_rows = self.df[self.df[trait_col].astype(str) == match_trait]
            
            for _, row in trait_rows.iterrows():
                try:
                    # UKBB LDSC actual columns: h2_observed, h2_observed_se, etc.
                    h2_obs = self._get_float(row, ['h2_observed', 'h2_obs', 'h2', 'h2_snp'])
                    if h2_obs is None:
                        continue
                    
                    estimate = HeritabilityEstimate(
                        trait_name=str(match_trait),
                        trait_id=self._get_str(row, ['phenotype', 'phenotype_code', 'pheno_id', 'code']),
                        h2_obs=h2_obs,
                        h2_obs_se=self._get_float(row, ['h2_observed_se', 'h2_se', 'se']),
                        h2_liability=self._get_float(row, ['h2_liability']),
                        population="EUR",  # UKBB LDSC is primarily European
                        source=HeritabilitySource.UKBB_LDSC,
                        n_samples=self._get_int(row, ['n', 'N', 'sample_size', 'n_cases']),
                        method="ldsc",
                        h2_z=self._get_float(row, ['h2_z', 'z'])
                    )
                    results.append(estimate)
                    
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue
        
        return results
    
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
    
    def get_all_traits(self) -> list[str]:
        """Get all available trait names."""
        if self.df.empty:
            return []
        
        trait_col = self._find_column(['description', 'phenotype', 'Phenotype', 'trait'])
        if trait_col:
            return self.df[trait_col].dropna().unique().tolist()
        return []
