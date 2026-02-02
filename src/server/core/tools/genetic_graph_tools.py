# src/server/core/tools/genetic_graph_tools.py
"""
Genetic Graph Tools for Module 3.
Implements sop.md L464-562 tool specifications.
"""
from typing import Union, Optional
from src.server.core.tool_schemas import (
    StudyPowerResult, NeighborResult, RankedNeighbor, ToolError
)


def genetic_graph_verify_study_power(
    kg_service,  # KnowledgeGraphService
    source_trait: str,
    target_trait: str
) -> Union[StudyPowerResult, ToolError]:
    """
    Fetch detailed study-pair provenance for a genetic correlation edge.
    
    Implements sop.md L497-530 specification.
    JIT Loading: Only called when Agent needs deep quality control.
    Token Budget: ~300 tokens.
    
    Args:
        kg_service: KnowledgeGraphService instance
        source_trait: Source trait canonical name
        target_trait: Target trait canonical name
        
    Returns:
        StudyPowerResult with provenance, or ToolError if edge not found
    """
    try:
        result = kg_service.get_edge_provenance(
            source_trait=source_trait,
            target_trait=target_trait
        )
        
        if result is None:
            return ToolError(
                tool_name="genetic_graph_verify_study_power",
                error_type="EdgeNotFound",
                error_message=f"No genetic correlation edge found between '{source_trait}' and '{target_trait}'",
                context={"source_trait": source_trait, "target_trait": target_trait}
            )
        
        return result
        
    except Exception as e:
        return ToolError(
            tool_name="genetic_graph_verify_study_power",
            error_type=type(e).__name__,
            error_message=str(e),
            context={"source_trait": source_trait, "target_trait": target_trait}
        )


def genetic_graph_get_neighbors(
    kg_service,  # KnowledgeGraphService
    trait_id: str,
    rg_z_threshold: float = 2.0,
    h2_z_threshold: float = 2.0,
    limit: int = 10
) -> Union[NeighborResult, ToolError]:
    """
    Get pre-ranked genetically correlated traits.
    
    Implements sop.md L464-495 specification.
    Auto-sorted by rg^2 * h2 (descending).
    Token Budget: ~100 tokens per neighbor.
    
    Args:
        kg_service: KnowledgeGraphService instance
        trait_id: Target trait canonical name
        rg_z_threshold: Minimum |rg_z_meta| (default 2.0)
        h2_z_threshold: Minimum h2_z_meta (default 2.0)
        limit: Maximum neighbors to return (default 10)
        
    Returns:
        NeighborResult with ranked neighbors, or ToolError on failure
    """
    try:
        # Call existing v2 method
        prioritized_neighbors = kg_service.get_prioritized_neighbors_v2(
            trait_id=trait_id,
            rg_z_threshold=rg_z_threshold,
            h2_z_threshold=h2_z_threshold
        )
        
        if prioritized_neighbors is None:
            return ToolError(
                tool_name="genetic_graph_get_neighbors",
                error_type="TraitNotFound",
                error_message=f"Trait '{trait_id}' not found in Knowledge Graph",
                context={"trait_id": trait_id}
            )
        
        # Get target trait h2 from node
        target_node = kg_service.get_trait_node(trait_id)
        target_h2 = target_node.h2_meta if target_node else 0.0
        
        # Convert to tool output schema
        neighbors = []
        for n in prioritized_neighbors[:limit]:
            # Get domain from trait node if available
            neighbor_node = kg_service.get_trait_node(n.trait_id)
            domain = getattr(neighbor_node, 'domain', 'Unknown') if neighbor_node else 'Unknown'
            
            # Calculate rg_z_meta estimate (if not directly available)
            # For PrioritizedNeighbor from v2, we don't have z directly stored
            # We'll estimate or pass 0 for now - proper implementation would track this
            rg_z_meta = 0.0  # Placeholder - full implementation would track this
            
            # n_correlations would come from the edge aggregator
            n_correlations = 1  # Placeholder
            
            neighbor = RankedNeighbor(
                trait_id=n.trait_id,
                domain=domain or "Unknown",
                rg_meta=n.rg,
                rg_z_meta=rg_z_meta,
                h2_meta=n.h2,
                transfer_score=n.score,
                n_correlations=n_correlations
            )
            neighbors.append(neighbor)
        
        return NeighborResult(
            target_trait=trait_id,
            target_h2_meta=target_h2,
            neighbors=neighbors
        )
        
    except Exception as e:
        return ToolError(
            tool_name="genetic_graph_get_neighbors",
            error_type=type(e).__name__,
            error_message=str(e),
            context={"trait_id": trait_id}
        )
