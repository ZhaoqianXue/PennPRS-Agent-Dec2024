import pandas as pd
import logging
import os
from pathlib import Path
from typing import List, Optional
from src.server.core.config import get_data_path
from .models import GeneticCorrelationResult, GeneticCorrelationSource

logger = logging.getLogger(__name__)

# Default path
DEFAULT_DATA_PATH = "data/genetic_correlation/gene_atlas/gene_atlas_gc.tsv"

class GeneAtlasClient:
    """
    Client for querying pairwise genetic correlations from GeneAtlas.
    Loads the data into memory on initialization.
    """
    _instance = None
    _data: pd.DataFrame = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeneAtlasClient, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load GeneAtlas GC data."""
        if self._data is not None:
            return

        try:
            full_data_path = get_data_path(DEFAULT_DATA_PATH)
            logger.info(f"Loading GeneAtlas data from {full_data_path}")
            
            if not full_data_path.exists():
                raise FileNotFoundError(f"GeneAtlas Data file not found at {full_data_path}")

            # Load the file
            # Columns: Phenotype_1_ID, Phenotype_1_desc, Phenotype_1_h2, Phenotype_2_ID, Phenotype_2_desc, Phenotype_2_h2, r_y, r_g, r_e, cov_y, cov_g, cov_e
            self._data = pd.read_csv(full_data_path, sep='\t')
            
            # Helper column for searching (lowercase description)
            self._data['t1_desc_lower'] = self._data['Phenotype_1_desc'].fillna('').str.lower()
            self._data['t2_desc_lower'] = self._data['Phenotype_2_desc'].fillna('').str.lower()
            
            logger.info(f"Loaded {len(self._data)} GeneAtlas correlation pairs.")
            
        except Exception as e:
            logger.error(f"Failed to load GeneAtlas data: {e}")
            self._data = pd.DataFrame()

    def search_correlations(self, trait_name: str, limit: int = 50) -> List[GeneticCorrelationResult]:
        """
        Search for correlations by trait name (substring match).
        """
        if self._data.empty:
            return []

        query = trait_name.lower()
        
        # Filter rows where either description matches
        mask = (self._data['t1_desc_lower'].str.contains(query, na=False)) | \
               (self._data['t2_desc_lower'].str.contains(query, na=False))
        
        subset = self._data[mask].head(limit)
        
        results = []
        for _, row in subset.iterrows():
            # Determine which is the query trait match to order result cleanly?
            # Or just return as is.
            
            # Map to model
            # Note: GeneAtlas file does not strictly provide SE/P/Z for rg in this file version.
            # We set them to 0.0 or None as placeholders.
            results.append(GeneticCorrelationResult(
                id1=str(row['Phenotype_1_ID']), # Model expects int, but IDs might be string? Model said int.
                id2=str(row['Phenotype_2_ID']), # Updated model strictly typed? Let's check model.
                trait_1_name=row['Phenotype_1_desc'],
                trait_2_name=row['Phenotype_2_desc'],
                rg=float(row['r_g']) if pd.notnull(row['r_g']) else 0.0,
                se=0.0, # Not available
                z=0.0,  # Not available
                p=1.0,  # Not available, default to non-significant
                source=GeneticCorrelationSource.GENE_ATLAS
            ))
            
        return results

    def get_correlations_by_id(self, trait_id: str, limit: int = 50) -> List[GeneticCorrelationResult]:
        """
        Get correlations by exact ID match.
        """
        if self._data.empty:
            return []

        # IDs in file are likely strings like "1070-0.0"
        mask = (self._data['Phenotype_1_ID'].astype(str) == str(trait_id)) | \
               (self._data['Phenotype_2_ID'].astype(str) == str(trait_id))
        
        subset = self._data[mask].head(limit)
        
        results = []
        for _, row in subset.iterrows():
            results.append(GeneticCorrelationResult(
                id1=str(row['Phenotype_1_ID']), 
                id2=str(row['Phenotype_2_ID']),
                trait_1_name=row['Phenotype_1_desc'],
                trait_2_name=row['Phenotype_2_desc'],
                rg=float(row['r_g']) if pd.notnull(row['r_g']) else 0.0,
                se=0.0,
                z=0.0,
                p=1.0,
                source=GeneticCorrelationSource.GENE_ATLAS
            ))
        return results
