"""
GWAS Atlas client for heritability data.

Data source: https://atlas.ctglab.nl/traitDB
Download: gwasATLAS_v20191115.txt.gz
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, List, Dict
from thefuzz import fuzz, process

from src.server.core.config import get_data_path
from src.server.modules.heritability.models import HeritabilityEstimate, HeritabilitySource

logger = logging.getLogger(__name__)


class GWASAtlasClient:
    """
    Client for querying GWAS Atlas heritability data.
    
    Uses pre-downloaded flat file from GWAS Atlas containing SNP heritability
    estimates computed via LD score regression.
    """
    
    DEFAULT_DATA_PATH = "data/heritability/gwas_atlas/gwas_atlas.tsv"
    
    # Expected columns in the GWAS Atlas file
    REQUIRED_COLUMNS = ["id", "Trait", "h2", "h2_SE"]
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize the GWAS Atlas client.
        
        Args:
            data_path: Path to the GWAS Atlas TSV file. If None, uses default.
        """
        self.data_path = data_path or get_data_path(self.DEFAULT_DATA_PATH)
        self._df: Optional[pd.DataFrame] = None
        self._loaded = False
    
    def _load_data(self) -> None:
        """Load the GWAS Atlas data file."""
        if self._loaded:
            return
            
        if not self.data_path.exists():
            logger.warning(f"GWAS Atlas data file not found: {self.data_path}")
            self._df = pd.DataFrame()
            self._loaded = True
            return
        
        try:
            # Try to load the file - handle both TSV and gzipped formats
            if str(self.data_path).endswith('.gz'):
                self._df = pd.read_csv(self.data_path, sep='\t', compression='gzip')
            else:
                self._df = pd.read_csv(self.data_path, sep='\t')
            
            # Normalize column names
            self._df.columns = self._df.columns.str.strip()
            
            logger.info(f"Loaded GWAS Atlas data: {len(self._df)} records")
            self._loaded = True
            
        except Exception as e:
            logger.error(f"Error loading GWAS Atlas data: {e}")
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
    ) -> List[HeritabilityEstimate]:
        """
        Search for heritability estimates by trait name.
        
        Args:
            trait: Trait name to search for (fuzzy matching)
            min_score: Minimum fuzzy match score (0-100)
            limit: Maximum number of results
            
        Returns:
            List of HeritabilityEstimate objects
        """
        if self.df.empty:
            return []
        
        # GWAS Atlas uses 'Trait' and 'uniqTrait' columns
        trait_col = None
        for col in ['Trait', 'uniqTrait', 'trait', 'TRAIT', 'trait_name']:
            if col in self.df.columns:
                trait_col = col
                break
        
        if trait_col is None:
            logger.error(f"No trait column found. Columns: {self.df.columns.tolist()}")
            return []
        
        # Fuzzy match traits
        all_traits = self.df[trait_col].dropna().unique().tolist()
        # Convert to strings for matching
        all_traits = [str(t) for t in all_traits]
        matches = process.extract(trait, all_traits, scorer=fuzz.token_set_ratio, limit=limit)
        
        results = []
        for match_trait, score in matches:
            if score < min_score:
                continue
                
            # Get rows matching this trait
            trait_rows = self.df[self.df[trait_col].astype(str) == match_trait]
            
            for _, row in trait_rows.iterrows():
                try:
                    # GWAS Atlas actual columns: SNPh2, SNPh2_se, SNPh2_z
                    h2_obs = self._get_float(row, ['SNPh2', 'h2', 'h2_obs', 'snp_h2'])
                    if h2_obs is None:
                        continue
                    
                    h2_se = self._get_float(row, ['SNPh2_se', 'h2_SE', 'h2_obs_se', 'snp_h2_se', 'se'])
                    h2_liability = self._get_float(row, ['SNPh2_l', 'h2_liability', 'h2_lia'])
                    n_samples = self._get_int(row, ['N', 'n', 'sample_size', 'Neff'])
                    h2_z = self._get_float(row, ['SNPh2_z', 'h2_Z', 'z', 'zscore'])
                    
                    # Get population (GWAS Atlas has Population column)
                    population = self._get_str(row, ['Population', 'pop', 'population', 'ancestry']) or "EUR"
                    # Extract first population if it's multi-ancestry (e.g., "EUR+EAS")
                    if '+' in population:
                        population = population.split('+')[0]
                    
                    estimate = HeritabilityEstimate(
                        trait_name=str(match_trait),
                        trait_id=self._get_str(row, ['id', 'trait_id', 'efo_id']),
                        h2_obs=h2_obs,
                        h2_obs_se=h2_se,
                        h2_liability=h2_liability,
                        population=population,
                        source=HeritabilitySource.GWAS_ATLAS,
                        n_samples=n_samples,
                        method="ldsc",
                        h2_z=h2_z
                    )
                    results.append(estimate)
                    
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue
        
        return results
    
    def _get_float(self, row: pd.Series, columns: List[str]) -> Optional[float]:
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
    
    def _get_int(self, row: pd.Series, columns: List[str]) -> Optional[int]:
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
    
    def _get_str(self, row: pd.Series, columns: List[str]) -> Optional[str]:
        """Try to get a string value from multiple possible column names."""
        for col in columns:
            if col in row.index:
                val = row[col]
                if pd.notna(val):
                    return str(val)
        return None
    
    def get_all_traits(self) -> List[str]:
        """Get all available trait names."""
        if self.df.empty:
            return []
        
        for col in ['Trait', 'trait', 'TRAIT', 'trait_name']:
            if col in self.df.columns:
                return self.df[col].dropna().unique().tolist()
        return []
    
    def get_trait_count(self) -> int:
        """Get the number of unique traits."""
        return len(self.get_all_traits())
