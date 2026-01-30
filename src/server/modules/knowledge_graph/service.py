"""
Core Logic for Module 2: Knowledge Graph Service.
Implements the Genetic Correlation Traversal logic defined in 'sop.md'.

Features:
- Dynamic Graph Construction (Nodes/Edges)
- Node Heritability Integration
- Weighted Scoring (rg^2 * h2)
"""
from typing import List, Optional, Union
from src.server.modules.genetic_correlation.gwas_atlas_client import GWASAtlasGCClient
from src.server.modules.heritability.gwas_atlas_client import GWASAtlasClient as HeritabilityClient
from src.server.modules.heritability.models import HeritabilityEstimate
from src.server.modules.knowledge_graph.models import (
    KnowledgeGraphResult, 
    KnowledgeGraphNode, 
    GeneticCorrelationEdge,
    PrioritizedNeighbor
)

import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    Service for querying and traversing the Genetic Architecture Graph.
    
    The Knowledge Graph is implemented as a Virtual/Dynamic Graph,
    constructed on-demand from local GWAS Atlas data.
    """
    
    def __init__(
        self, 
        gc_client: Optional[GWASAtlasGCClient] = None,
        h2_client: Optional[HeritabilityClient] = None,
        # Legacy parameter for backward compatibility
        client: Optional[GWASAtlasGCClient] = None
    ):
        """
        Initialize the Knowledge Graph Service.
        
        Args:
            gc_client: Genetic Correlation client (GWAS Atlas)
            h2_client: Heritability client (GWAS Atlas)
            client: Legacy parameter, alias for gc_client
        """
        # Support both new and legacy parameter names
        self.gc_client = gc_client or client or GWASAtlasGCClient()
        self.h2_client = h2_client or HeritabilityClient()

    def _get_heritability(self, trait_name: str) -> Optional[HeritabilityEstimate]:
        """
        Query heritability for a trait by name.
        
        Args:
            trait_name: Name of the trait to look up
            
        Returns:
            HeritabilityEstimate object or None if not found
        """
        try:
            results = self.h2_client.search_trait(trait_name, limit=1)
            if results:
                return results[0]
        except Exception as e:
            logger.warning(f"Failed to get heritability for '{trait_name}': {e}")
        return None

    def get_neighbors(
        self, 
        trait_id: Union[str, int], 
        p_threshold: float = 0.05,
        include_h2: bool = True
    ) -> KnowledgeGraphResult:
        """
        Query genetic neighbors for a given trait.
        
        Args:
            trait_id: Source Trait ID (e.g. EFO_00001 or numeric ID)
            p_threshold: Significance cutoff (Default 0.05)
            include_h2: Whether to populate heritability for each node
            
        Returns:
            KnowledgeGraphResult with nodes and edges
        """
        # Get genetic correlations from GWAS Atlas
        raw_results = self.gc_client.get_correlations(trait_id, p_threshold=p_threshold)
        
        edges = []
        nodes = []
        seen_nodes = set()
        
        for res in raw_results:
            # Create Edge
            edge = GeneticCorrelationEdge(
                source=str(trait_id),
                target=str(res.id2),
                rg=res.rg,
                p_value=res.p,
                se=res.se
            )
            edges.append(edge)
            
            # Create Node (Target)
            node_id = str(res.id2)
            if node_id not in seen_nodes:
                label = getattr(res, 'trait_2_name', "Unknown")
                
                # Query heritability if requested
                h2_value = None
                if include_h2 and label and label != "Unknown":
                    est = self._get_heritability(str(label))
                    if est:
                        h2_value = est.h2_obs
                
                node = KnowledgeGraphNode(
                    id=node_id,
                    label=str(label),
                    h2=h2_value
                )
                nodes.append(node)
                seen_nodes.add(node_id)
                
        return KnowledgeGraphResult(nodes=nodes, edges=edges)

    def get_prioritized_neighbors(
        self,
        trait_id: Union[str, int],
        p_threshold: float = 0.05
    ) -> List[PrioritizedNeighbor]:
        """
        Get neighbors ranked by weighted score: rg^2 * h2.
        
        This method prioritizes proxy traits that are both:
        1. Highly correlated with the target (high rg)
        2. Biologically viable for PRS transfer (significant h2)
        
        Args:
            trait_id: Source Trait ID
            p_threshold: Significance cutoff (Default 0.05)
            
        Returns:
            List of PrioritizedNeighbor sorted by score descending.
            Nodes without significant h2 (Z > 2) are excluded.
        """
        # Get genetic correlations
        raw_results = self.gc_client.get_correlations(trait_id, p_threshold=p_threshold)
        
        prioritized = []
        
        for res in raw_results:
            trait_name = getattr(res, 'trait_2_name', None)
            if not trait_name or trait_name == "Unknown":
                continue
            
            # Get heritability for the neighbor
            est = self._get_heritability(str(trait_name))
            if est is None:
                continue

            # Filter: Heritability Validity (Z > 2)
            # If Z is missing, we conservatively check if h2_obs > 0 and se is small, 
            # but usually Z is present. If Z is None, skip to be safe? 
            # Or use h2_obs > 0? Standard is Z > 2.
            if est.h2_z is None or est.h2_z <= 2.0:
                 continue
            
            h2_value = est.h2_obs
            
            # Calculate weighted score: rg^2 * h2
            rg_squared = res.rg ** 2
            score = rg_squared * h2_value
            
            neighbor = PrioritizedNeighbor(
                trait_id=str(res.id2),
                trait_name=str(trait_name),
                rg=res.rg,
                h2=h2_value,
                score=score,
                p_value=res.p
            )
            prioritized.append(neighbor)
        
        # Sort by score descending
        prioritized.sort(key=lambda x: x.score, reverse=True)
        
        return prioritized
