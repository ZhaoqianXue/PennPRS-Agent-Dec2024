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

        # IMPORTANT PERFORMANCE NOTE:
        # The GC dataset is ~1.4M rows. Storing every row's pd.Series in memory per trait-pair
        # is extremely slow and memory-heavy. For neighbor ranking we only need aggregated
        # (rg_meta, rg_se_meta, rg_z_meta, rg_p_meta, n_correlations), not full provenance.
        # Provenance is handled separately by KnowledgeGraphService.get_edge_provenance.
        self._trait_pair_meta: Dict[Tuple[str, str], Dict[str, float]] = {}
        self._trait_neighbors: Dict[str, Set[str]] = defaultdict(set)
        self._preprocess()
    
    def _normalize_pair(self, trait1: str, trait2: str) -> Tuple[str, str]:
        """Normalize trait pair to consistent order (alphabetically)."""
        return (trait1, trait2) if trait1 <= trait2 else (trait2, trait1)
    
    def _preprocess(self):
        """
        Aggregate study-pair edges by trait-pair, excluding self-loops.

        This is intentionally implemented as a single pass over the DataFrame using
        itertuples() to avoid pandas iterrows() overhead and to avoid storing full rows.
        """
        if self._df.empty:
            return

        # Accumulate inverse-variance meta-analysis sufficient statistics per trait-pair.
        # For each pair: sum_w = Σ(1/se^2), sum_w_theta = Σ(rg/se^2), n = count_valid
        pair_stats: Dict[Tuple[str, str], List[float]] = {}

        for row in self._df.itertuples(index=False):
            id1 = getattr(row, "id1", None)
            id2 = getattr(row, "id2", None)
            rg = getattr(row, "rg", None)
            se = getattr(row, "se", None)

            if id1 is None or id2 is None or rg is None or se is None:
                continue
            if pd.isna(id1) or pd.isna(id2) or pd.isna(rg) or pd.isna(se):
                continue

            try:
                id1_i = int(id1)
                id2_i = int(id2)
                rg_f = float(rg)
                se_f = float(se)
            except Exception:
                continue

            if se_f <= 0:
                continue

            trait1 = self._id_to_trait.get(id1_i)
            trait2 = self._id_to_trait.get(id2_i)
            if not trait1 or not trait2:
                continue

            # Exclude self-loops (edges between studies of the same trait)
            if trait1 == trait2:
                continue

            pair_key = self._normalize_pair(trait1, trait2)

            # Track neighbors (for fast adjacency lookup).
            self._trait_neighbors[trait1].add(trait2)
            self._trait_neighbors[trait2].add(trait1)

            w = 1.0 / (se_f ** 2)
            stats = pair_stats.get(pair_key)
            if stats is None:
                # [sum_w, sum_w_theta, n_valid]
                pair_stats[pair_key] = [w, w * rg_f, 1.0]
            else:
                stats[0] += w
                stats[1] += (w * rg_f)
                stats[2] += 1.0

        # Finalize meta-analysis metrics.
        import math
        for pair_key, (sum_w, sum_w_theta, n_valid_f) in pair_stats.items():
            if sum_w <= 0:
                continue
            theta_meta = sum_w_theta / sum_w
            se_meta = 1.0 / math.sqrt(sum_w)
            z_meta = theta_meta / se_meta if se_meta > 0 else None
            p_meta = math.erfc(abs(z_meta) / math.sqrt(2.0)) if z_meta is not None else None
            self._trait_pair_meta[pair_key] = {
                "rg_meta": theta_meta,
                "rg_se_meta": se_meta,
                "rg_z_meta": z_meta if z_meta is not None else 0.0,
                "rg_p_meta": p_meta if p_meta is not None else 1.0,
                "n_correlations": int(n_valid_f),
            }
    
    def get_neighbor_traits(self, trait_id: str) -> List[str]:
        """Get list of neighbor traits for a given trait."""
        return list(self._trait_neighbors.get(trait_id, set()))
    
    def get_all_trait_pairs(self) -> List[Tuple[str, str]]:
        """Get list of all unique trait pairs with edges."""
        return list(self._trait_pair_meta.keys())
    
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

        meta = self._trait_pair_meta.get(pair_key)
        if not meta:
            return None

        return GeneticCorrelationEdgeMeta(
            source_trait=source_trait,
            target_trait=target_trait,
            rg_meta=float(meta["rg_meta"]),
            rg_se_meta=float(meta["rg_se_meta"]) if meta.get("rg_se_meta") is not None else None,
            rg_z_meta=float(meta["rg_z_meta"]) if meta.get("rg_z_meta") is not None else None,
            rg_p_meta=float(meta["rg_p_meta"]) if meta.get("rg_p_meta") is not None else None,
            n_correlations=int(meta.get("n_correlations") or 0),
            correlations=[]
        )
