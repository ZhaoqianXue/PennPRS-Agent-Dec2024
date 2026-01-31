"""
Trait Aggregator for Knowledge Graph.
Groups Studies by uniqTrait and applies meta-analysis to create TraitNodes.

Per sop.md Module 2:
- Node Aggregation: Group Studies by `uniqTrait`, apply inverse-variance weighted meta-analysis for h^2.
- Primary Key: trait_id (uniqTrait)
- Provenance: All Studies retained in `studies` array
"""
import pandas as pd
import logging
from typing import Optional, List, Dict, Any

from src.server.modules.knowledge_graph.models import TraitNode
from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis

logger = logging.getLogger(__name__)


class TraitAggregator:
    """
    Aggregates Study-level data by Trait (uniqTrait).
    Creates TraitNode objects with meta-analyzed h2 and full study provenance.
    """
    
    def __init__(self, h2_df: pd.DataFrame):
        """
        Initialize with heritability DataFrame.
        
        Args:
            h2_df: DataFrame with columns including 'uniqTrait', 'SNPh2', 'SNPh2_se', etc.
        """
        self._df = h2_df
        self._trait_groups: Dict[str, pd.DataFrame] = {}
        self._id_to_trait: Dict[int, str] = {}
        self._preprocess()
    
    def _preprocess(self):
        """Group studies by uniqTrait and build ID mapping."""
        if self._df.empty:
            self._trait_groups = {}
            self._id_to_trait = {}
            return
        
        if 'uniqTrait' not in self._df.columns:
            logger.warning("'uniqTrait' column not found in DataFrame")
            self._trait_groups = {}
            self._id_to_trait = {}
            return
        
        # Group by uniqTrait
        self._trait_groups = {
            str(name): group for name, group in self._df.groupby('uniqTrait')
        }
        
        # Build ID -> Trait mapping
        if 'id' in self._df.columns:
            for _, row in self._df.iterrows():
                study_id = int(row['id']) if pd.notna(row['id']) else None
                trait = str(row['uniqTrait']) if pd.notna(row['uniqTrait']) else None
                if study_id is not None and trait is not None:
                    self._id_to_trait[study_id] = trait
    
    def get_all_trait_ids(self) -> List[str]:
        """Get list of all unique trait IDs (canonical names)."""
        return list(self._trait_groups.keys())
    
    def get_study_ids_for_trait(self, trait_id: str) -> List[int]:
        """Get list of study IDs for a given trait."""
        if trait_id not in self._trait_groups:
            return []
        
        group = self._trait_groups[trait_id]
        if 'id' not in group.columns:
            return []
        
        return [int(sid) for sid in group['id'].dropna().tolist()]
    
    def get_id_to_trait_map(self) -> Dict[int, str]:
        """Get mapping from study ID to trait name."""
        return self._id_to_trait.copy()
    
    def get_trait_node(self, trait_id: str) -> Optional[TraitNode]:
        """
        Get aggregated TraitNode for a given trait ID.
        
        Applies inverse-variance weighted meta-analysis per sop.md:
        - h2_meta = sum(w_i * h2_i) / sum(w_i), where w_i = 1/SE_i^2
        
        Args:
            trait_id: Trait canonical name (uniqTrait)
            
        Returns:
            TraitNode with meta-analyzed h2 and study provenance, or None if not found
        """
        if trait_id not in self._trait_groups:
            return None
        
        group = self._trait_groups[trait_id]
        
        # Extract h2 estimates and SEs
        estimates = []
        ses = []
        
        if 'SNPh2' in group.columns and 'SNPh2_se' in group.columns:
            for _, row in group.iterrows():
                h2 = row.get('SNPh2')
                se = row.get('SNPh2_se')
                if pd.notna(h2) and pd.notna(se):
                    estimates.append(float(h2))
                    ses.append(float(se))
        
        # Apply meta-analysis
        if estimates and ses:
            meta_result = inverse_variance_meta_analysis(estimates, ses)
        else:
            meta_result = {"theta_meta": None, "se_meta": None, "z_meta": None, "n_valid": 0}
        
        # Build study provenance
        studies = []
        for _, row in group.iterrows():
            study = {
                "study_id": int(row['id']) if pd.notna(row.get('id')) else None,
            }
            # Add optional fields if present
            if 'PMID' in row.index and pd.notna(row.get('PMID')):
                study["pmid"] = str(row['PMID'])
            if 'N' in row.index and pd.notna(row.get('N')):
                study["n"] = int(row['N'])
            if 'SNPh2' in row.index and pd.notna(row.get('SNPh2')):
                study["snp_h2"] = float(row['SNPh2'])
            if 'SNPh2_se' in row.index and pd.notna(row.get('SNPh2_se')):
                study["snp_h2_se"] = float(row['SNPh2_se'])
            if 'SNPh2_z' in row.index and pd.notna(row.get('SNPh2_z')):
                study["snp_h2_z"] = float(row['SNPh2_z'])
            if 'Population' in row.index and pd.notna(row.get('Population')):
                study["population"] = str(row['Population'])
            if 'Consortium' in row.index and pd.notna(row.get('Consortium')):
                study["consortium"] = str(row['Consortium'])
            if 'Year' in row.index and pd.notna(row.get('Year')):
                study["year"] = int(row['Year'])
            
            studies.append(study)
        
        # Get domain and chapter from first row
        first_row = group.iloc[0]
        domain = None
        chapter = None
        
        if 'Domain' in first_row.index and pd.notna(first_row.get('Domain')):
            domain = str(first_row['Domain'])
        if 'ChapterLevel' in first_row.index and pd.notna(first_row.get('ChapterLevel')):
            chapter = str(first_row['ChapterLevel'])
        
        return TraitNode(
            trait_id=trait_id,
            domain=domain,
            chapter_level=chapter,
            h2_meta=meta_result["theta_meta"],
            h2_se_meta=meta_result["se_meta"],
            h2_z_meta=meta_result["z_meta"],
            n_studies=len(studies),
            studies=studies
        )
