"""
Edge Aggregator for Knowledge Graph.
Groups Study-pair correlations by Trait-pair and applies meta-analysis for rg.

Per sop.md Module 2:
- Edge Aggregation: Group edges by (source_trait, target_trait), apply inverse-variance weighted meta-analysis for r_g.
- Self-loops: Edges between studies of the same trait are excluded.
- Provenance: All Study-pair correlations retained in `correlations` array.
"""
import pandas as pd
import logging
from typing import Optional, List, Dict, Set, Tuple
from collections import defaultdict

from src.server.modules.knowledge_graph.models import GeneticCorrelationEdgeMeta
from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis

logger = logging.getLogger(__name__)


class EdgeAggregator:
    """
    Aggregates Study-pair correlations by Trait-pair.
    Creates GeneticCorrelationEdgeMeta objects with meta-analyzed rg and full provenance.
    """
    
    def __init__(self, gc_df: pd.DataFrame, id_to_trait_map: Dict[int, str]):
        """
        Initialize with genetic correlation DataFrame and ID mapping.
        
        Args:
            gc_df: DataFrame with columns 'id1', 'id2', 'rg', 'se', 'z', 'p'
            id_to_trait_map: Mapping from study ID to trait name
        """
        self._df = gc_df
        self._id_to_trait = id_to_trait_map
        self._trait_pair_edges: Dict[Tuple[str, str], List[pd.Series]] = defaultdict(list)
        self._trait_neighbors: Dict[str, Set[str]] = defaultdict(set)
        self._preprocess()
    
    def _normalize_pair(self, trait1: str, trait2: str) -> Tuple[str, str]:
        """Normalize trait pair to consistent order (alphabetically)."""
        return (trait1, trait2) if trait1 <= trait2 else (trait2, trait1)
    
    def _preprocess(self):
        """Group study-pair edges by trait-pair, excluding self-loops."""
        if self._df.empty:
            return
        
        for _, row in self._df.iterrows():
            id1 = int(row['id1']) if pd.notna(row.get('id1')) else None
            id2 = int(row['id2']) if pd.notna(row.get('id2')) else None
            
            if id1 is None or id2 is None:
                continue
            
            trait1 = self._id_to_trait.get(id1)
            trait2 = self._id_to_trait.get(id2)
            
            if trait1 is None or trait2 is None:
                continue
            
            # Exclude self-loops (edges between studies of the same trait)
            if trait1 == trait2:
                continue
            
            pair_key = self._normalize_pair(trait1, trait2)
            self._trait_pair_edges[pair_key].append(row)
            
            # Track neighbors
            self._trait_neighbors[trait1].add(trait2)
            self._trait_neighbors[trait2].add(trait1)
    
    def get_neighbor_traits(self, trait_id: str) -> List[str]:
        """Get list of neighbor traits for a given trait."""
        return list(self._trait_neighbors.get(trait_id, set()))
    
    def get_all_trait_pairs(self) -> List[Tuple[str, str]]:
        """Get list of all unique trait pairs with edges."""
        return list(self._trait_pair_edges.keys())
    
    def get_aggregated_edge(
        self, 
        source_trait: str, 
        target_trait: str
    ) -> Optional[GeneticCorrelationEdgeMeta]:
        """
        Get aggregated edge between two traits.
        
        Applies inverse-variance weighted meta-analysis per sop.md:
        - rg_meta = sum(w_i * rg_i) / sum(w_i), where w_i = 1/SE_i^2
        
        Args:
            source_trait: Source trait canonical name
            target_trait: Target trait canonical name
            
        Returns:
            GeneticCorrelationEdgeMeta with meta-analyzed rg, or None if not found
        """
        # Exclude self-loops
        if source_trait == target_trait:
            return None
        
        pair_key = self._normalize_pair(source_trait, target_trait)
        
        if pair_key not in self._trait_pair_edges:
            return None
        
        rows = self._trait_pair_edges[pair_key]
        
        # Extract rg estimates and SEs
        estimates = []
        ses = []
        
        for row in rows:
            rg = row.get('rg')
            se = row.get('se')
            if pd.notna(rg) and pd.notna(se):
                estimates.append(float(rg))
                ses.append(float(se))
        
        if not estimates or not ses:
            return None
        
        # Apply meta-analysis
        meta_result = inverse_variance_meta_analysis(estimates, ses)
        
        if meta_result["theta_meta"] is None:
            return None
        
        # Build correlation provenance
        correlations = []
        for row in rows:
            corr = {
                "source_study_id": int(row['id1']) if pd.notna(row.get('id1')) else None,
                "target_study_id": int(row['id2']) if pd.notna(row.get('id2')) else None,
            }
            if pd.notna(row.get('rg')):
                corr["rg"] = float(row['rg'])
            if pd.notna(row.get('se')):
                corr["se"] = float(row['se'])
            if pd.notna(row.get('z')):
                corr["z"] = float(row['z'])
            if pd.notna(row.get('p')):
                corr["p"] = float(row['p'])
            
            correlations.append(corr)
        
        return GeneticCorrelationEdgeMeta(
            source_trait=source_trait,
            target_trait=target_trait,
            rg_meta=meta_result["theta_meta"],
            rg_se_meta=meta_result["se_meta"],
            rg_z_meta=meta_result["z_meta"],
            rg_p_meta=meta_result["p_meta"],
            n_correlations=len(correlations),
            correlations=correlations
        )
