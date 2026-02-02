# src/server/core/tools/genetic_graph_tools.py
"""
Genetic Graph Tools for Module 3.
Implements sop.md L464-562 tool specifications.
"""
from typing import Union, Optional, List
import logging
from src.server.core.tool_schemas import (
    StudyPowerResult, NeighborResult, RankedNeighbor, ToolError,
    MechanismValidation, SharedGene
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
            domain = neighbor_node.domain if neighbor_node else "Unknown"
            
            neighbor = RankedNeighbor(
                trait_id=n.trait_id,
                domain=domain or "Unknown",
                rg_meta=n.rg,
                rg_z_meta=n.rg_z or 0.0,
                h2_meta=n.h2,
                transfer_score=n.score,
                n_correlations=n.n_correlations
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


def genetic_graph_validate_mechanism(
    ot_client,  # OpenTargetsClient interface
    source_trait_efo: str,
    target_trait_efo: str,
    source_trait_name: str,
    target_trait_name: str,
    top_n_genes: int = 50,
    phewas_client = None
) -> Union[MechanismValidation, ToolError]:
    """
    Validate biological mechanism between two traits via Open Targets and PheWAS.
    
    Implements sop.md L532-560 specification.
    JIT Loading: Only called when Agent needs to justify cross-disease transfer.
    Token Budget: ~500 tokens.
    
    This tool acts as a "biological translator" - converting statistical
    correlation (rg) into causal biological logic via shared gene targets.
    
    Args:
        ot_client: Open Targets client with get_disease_targets method
        source_trait_efo: Source trait EFO ID (e.g., "EFO_0000384")
        target_trait_efo: Target trait EFO ID (e.g., "EFO_0000729")
        source_trait_name: Human-readable source trait name
        target_trait_name: Human-readable target trait name
        top_n_genes: Number of top genes to compare (default 50)
        phewas_client: Optional ExPheWAS client for cross-validation
        
    Returns:
        MechanismValidation with shared genes and pathways, or ToolError
    """
    try:
        # Fetch associated targets for both diseases
        source_targets = ot_client.get_disease_targets(source_trait_efo)
        target_targets = ot_client.get_disease_targets(target_trait_efo)
        
        # Build lookup maps
        source_map = {t["id"]: t for t in source_targets[:top_n_genes]}
        target_map = {t["id"]: t for t in target_targets[:top_n_genes]}
        
        # Find intersection
        shared_gene_ids = set(source_map.keys()) & set(target_map.keys())
        
        # Build SharedGene list
        shared_genes = []
        all_pathways = set()
        phewas_evidence_count = 0
        
        for gene_id in shared_gene_ids:
            source_info = source_map[gene_id]
            target_info = target_map[gene_id]
            
            # Get druggability and pathways (may require additional API calls)
            try:
                druggability = ot_client.get_target_druggability(gene_id)
            except Exception:
                druggability = "Unknown"
            
            try:
                pathways = ot_client.get_target_pathways(gene_id)
            except Exception:
                pathways = []
            
            all_pathways.update(pathways)
            
            shared_gene = SharedGene(
                gene_symbol=source_info.get("symbol", "Unknown"),
                gene_id=gene_id,
                source_association=source_info.get("score", 0.0),
                target_association=target_info.get("score", 0.0),
                druggability=druggability,
                pathways=pathways
            )
            
            # Cross-validate with PheWAS if client provided
            if phewas_client:
                try:
                    phewas_results = phewas_client.get_gene_results(gene_id)
                    significant_p = None
                    
                    # Match traits by keyword
                    src_kw = source_trait_name.lower().split()
                    tgt_kw = target_trait_name.lower().split()
                    
                    for res in phewas_results:
                        # ExPheWAS API often uses 'p_value' and 'outcome_label' or similar
                        p_val = res.get("p_value") or res.get("p-value") or res.get("pval")
                        label = (res.get("outcome_label") or res.get("label") or 
                                res.get("trait") or res.get("phenotype") or "")
                        label_lower = str(label).lower()
                        
                        if p_val is not None and p_val < 0.05:
                            # Check if label matches source or target trait keywords
                            matches_src = any(kw in label_lower for kw in src_kw if len(kw) > 3)
                            matches_tgt = any(kw in label_lower for kw in tgt_kw if len(kw) > 3)
                            
                            if matches_src or matches_tgt:
                                significant_p = min(significant_p, p_val) if significant_p else p_val
                    
                    if significant_p is not None:
                        shared_gene.phewas_p_value = significant_p
                        phewas_evidence_count += 1
                        
                except Exception as e:
                    # Log error but continue validation
                    logging.getLogger(__name__).warning(f"PheWAS validation failed for {gene_id}: {e}")
            
            shared_genes.append(shared_gene)
        
        # Sort by combined association score
        shared_genes.sort(
            key=lambda g: g.source_association + g.target_association, 
            reverse=True
        )
        
        # Determine confidence level based on shared gene count
        if len(shared_genes) >= 5:
            confidence = "High"
        elif len(shared_genes) >= 2:
            confidence = "Moderate"
        else:
            confidence = "Low"
        
        # Generate mechanism summary
        if shared_genes:
            top_gene = shared_genes[0].gene_symbol
            summary = f"Both traits share {len(shared_genes)} gene(s). Top: {top_gene}."
            if all_pathways:
                summary += f" Pathways: {', '.join(list(all_pathways)[:3])}"
            if phewas_evidence_count > 0:
                summary += f" Further validated by PheWAS evidence for {phewas_evidence_count} gene(s)."
        else:
            summary = "No shared genetic targets found in top-ranked associations."
        
        return MechanismValidation(
            source_trait=source_trait_name,
            target_trait=target_trait_name,
            shared_genes=shared_genes,
            shared_pathways=list(all_pathways),
            phewas_evidence_count=phewas_evidence_count,
            mechanism_summary=summary,
            confidence_level=confidence
        )
        
    except Exception as e:
        return ToolError(
            tool_name="genetic_graph_validate_mechanism",
            error_type=type(e).__name__,
            error_message=str(e),
            context={
                "source_efo": source_trait_efo,
                "target_efo": target_trait_efo
            }
        )

