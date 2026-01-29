"""
Core Logic for Module 2: Knowledge Graph Service.
Implements the Genetic Correlation Traversal logic defined in 'proposal.md'.
"""
from typing import List, Optional, Union
from src.server.modules.genetic_correlation.gwas_atlas_client import GWASAtlasGCClient
from src.server.modules.knowledge_graph.models import KnowledgeGraphResult, KnowledgeGraphNode, GeneticCorrelationEdge

class KnowledgeGraphService:
    def __init__(self, client: Optional[GWASAtlasGCClient] = None):
        # Use dependency injection standard or singleton default
        self.client = client or GWASAtlasGCClient()

    def get_neighbors(self, trait_id: Union[str, int], p_threshold: float = 0.05) -> KnowledgeGraphResult:
        """
        Query genetic neighbors for a given trait.
        Args:
            trait_id: Source Trait ID (e.g. EFO_00001 or numeric ID)
            p_threshold: Significance cutoff (Default 0.05)
        """
        
        # Note: GWASAtlasGCClient typically expects integer ID.
        # If passed string, we pass it through (assuming client handles it or it's a mock).
        # In future phases, EFO -> Atlas ID mapping logic should be added here.
        
        # The client.get_correlations returns List[GeneticCorrelationResult]
        raw_results = self.client.get_correlations(trait_id, p_threshold=p_threshold)
        
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
                # Use getattr or .get depending on if it's object or dict
                # The model says GeneticCorrelationResult is a Pydantic model (object)
                label = getattr(res, 'trait_2_name', "Unknown")
                
                node = KnowledgeGraphNode(
                    id=node_id,
                    label=str(label),
                    h2=None 
                )
                nodes.append(node)
                seen_nodes.add(node_id)
                
        return KnowledgeGraphResult(nodes=nodes, edges=edges)
