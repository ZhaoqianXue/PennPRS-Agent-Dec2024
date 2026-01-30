import pandas as pd
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict
from src.server.core.config import get_data_path
from .models import GeneticCorrelationResult, GeneticCorrelationSource

logger = logging.getLogger(__name__)

# Default paths
# GC Data: ~1.4M rows, uncompressed TSV
DEFAULT_GC_DATA_PATH = "data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv"
# Metadata: To map IDs to names. Using the main Heritability module file
DEFAULT_METADATA_PATH = "data/heritability/gwas_atlas/gwas_atlas.tsv"

class GWASAtlasGCClient:
    """
    Client for querying pairwise genetic correlations from GWAS Atlas.
    Loads the data into memory on initialization (Singleton pattern recommended).
    """
    _instance = None
    _data: pd.DataFrame = None
    _id_map: Dict[int, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GWASAtlasGCClient, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load GC data and metadata map."""
        if self._data is not None:
            return

        # 1. Load Metadata for ID mapping
        try:
            full_meta_path = get_data_path(DEFAULT_METADATA_PATH)
            if full_meta_path.exists():
                logger.info(f"Loading GWAS Atlas metadata from {full_meta_path}")
                meta_df = pd.read_csv(full_meta_path, sep='\t', usecols=['uniqTrait', 'Trait'])
                # Create ID -> Name map. 'uniqTrait' in metadata corresponds to 'id1'/'id2' in GC file
                # Note: uniqTrait is mixed type in general, but for GC file linking it matches.
                # Let's ensure string to string mapping just in case, or int if strictly int.
                # The GC file IDs appear to be integers (1, 2, 3...).
                self._id_map = meta_df.set_index('uniqTrait')['Trait'].to_dict()
            else:
                logger.warning(f"Metadata file not found at {full_meta_path}. Trait names will be missing.")
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")

        # 2. Load GC Data
        try:
            full_data_path = get_data_path(DEFAULT_GC_DATA_PATH)
            logger.info(f"Loading Genetic Correlation data from {full_data_path}")
            
            if not full_data_path.exists():
                raise FileNotFoundError(f"GC Data file not found at {full_data_path}")

            # Load only necessary columns
            self._data = pd.read_csv(
                full_data_path, 
                sep='\t', 
                # compression='gzip', # Now uncompressed
                dtype={'id1': int, 'id2': int, 'rg': float, 'se': float, 'z': float, 'p': float}
            )
            logger.info(f"Loaded {len(self._data)} genetic correlation pairs.")
            
        except Exception as e:
            logger.error(f"Failed to load GC data: {e}")
            self._data = pd.DataFrame() # Empty fallback

    def get_correlations(self, trait_id: int, p_threshold: float = 0.05, limit: int = 100) -> List[GeneticCorrelationResult]:
        """
        Get all genetic correlations for a specific trait ID.
        Searches both id1 and id2 columns.
        """
        if self._data.empty:
            logger.warning("GWAS Atlas data is empty")
            return []

        # Filter: (id1 == trait_id) OR (id2 == trait_id)
        mask = (self._data['id1'] == trait_id) | (self._data['id2'] == trait_id)
        subset = self._data[mask].copy()

        logger.info(f"Search for ID {trait_id}: Found {len(subset)} raw matches")

        # Apply P-value threshold if requested
        if p_threshold:
            subset = subset[subset['p'] < p_threshold]
            logger.info(f"After P<{p_threshold}: {len(subset)} matches")

        # Sort by significance (p-value ascending) or magnitude of rg? Usually p-value is safer for 'top' hits
        subset = subset.sort_values(by='p', ascending=True).head(limit)

        results = []
        for _, row in subset.iterrows():
            # Identify which ID is the 'other' trait
            # Ensure safe integer comparison
            r_id1 = int(row['id1'])
            r_id2 = int(row['id2'])
            
            other_id = r_id2 if r_id1 == trait_id else r_id1
            
            # Map names
            t1_name = self._id_map.get(str(trait_id)) or self._id_map.get(trait_id)
            t2_name = self._id_map.get(str(other_id)) or self._id_map.get(other_id)

            results.append(GeneticCorrelationResult(
                id1=str(trait_id),
                id2=str(other_id),
                trait_1_name=str(t1_name) if t1_name else str(trait_id),
                trait_2_name=str(t2_name) if t2_name else str(other_id),
                rg=row['rg'],
                se=row['se'],
                z=row['z'],
                p=row['p'],
                source=GeneticCorrelationSource.GWAS_ATLAS
            ))
        
        logger.info(f"Returning {len(results)} results")
        return results

    def get_trait_name_by_id(self, trait_id: int) -> Optional[str]:
        """
        Get trait name for a given numeric GWAS Atlas ID.
        
        Args:
            trait_id: Numeric GWAS Atlas trait ID
            
        Returns:
            Trait name string, or None if not found
        """
        # Try both string and int keys since _id_map uses mixed types
        name = self._id_map.get(str(trait_id)) or self._id_map.get(trait_id)
        return str(name) if name else None
    
    def get_trait_id_by_name(self, trait_name: str) -> Optional[int]:
        """
        Get numeric GWAS Atlas ID for a given trait name.
        
        Args:
            trait_name: Trait name to look up
            
        Returns:
            Numeric trait ID, or None if not found
        """
        # Build reverse mapping if not exists
        if not hasattr(self, '_name_to_id_map') or not self._name_to_id_map:
            self._name_to_id_map = {}
            for id_key, name in self._id_map.items():
                # Normalize to lowercase for case-insensitive matching
                self._name_to_id_map[str(name).lower()] = id_key
        
        # Try exact match (case-insensitive)
        result = self._name_to_id_map.get(trait_name.lower())
        if result is not None:
            try:
                return int(result)
            except (ValueError, TypeError):
                return result
        return None

    def get_pair_correlation(self, id1: int, id2: int) -> Optional[GeneticCorrelationResult]:
        """
        Get correlation between two specific trait IDs.
        """
        if self._data.empty:
            return None

        # Search for the pair (order doesn't matter in logic, but file usually has id1 < id2 or similar)
        # We define a mask for both directions
        mask = ((self._data['id1'] == id1) & (self._data['id2'] == id2)) | \
               ((self._data['id1'] == id2) & (self._data['id2'] == id1))
        
        subset = self._data[mask]
        
        if subset.empty:
            return None
        
        row = subset.iloc[0]
        
        t1_name = self._id_map.get(str(id1)) or self._id_map.get(id1)
        t2_name = self._id_map.get(str(id2)) or self._id_map.get(id2)

        return GeneticCorrelationResult(
            id1=id1,
            id2=id2,
            trait_1_name=str(t1_name) if t1_name else str(id1),
            trait_2_name=str(t2_name) if t2_name else str(id2),
            rg=row['rg'],
            se=row['se'],
            z=row['z'],
            p=row['p'],
            source=GeneticCorrelationSource.GWAS_ATLAS
        )
