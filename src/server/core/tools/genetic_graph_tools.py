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

logger = logging.getLogger(__name__)


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
        query_trait = trait_id
        resolved_by: Optional[str] = None
        resolution_confidence: Optional[str] = None
        resolved_trait: Optional[str] = None

        # Step 1: Try trait resolution first for free-form user inputs
        resolution = None
        if hasattr(kg_service, "resolve_trait_id"):
            try:
                resolution = kg_service.resolve_trait_id(query_trait)
            except Exception:
                resolution = None

        # Detect if query is a proxy trait (family history, etc.)
        query_norm_tokens = set(kg_service._normalize_trait_text(query_trait).split()) if hasattr(kg_service, "_normalize_trait_text") else set()
        query_is_proxy = any(t in query_norm_tokens for t in {"family", "history", "paternal", "maternal", "father", "mother", "sibling", "siblings"})
        
        # Collect all candidate traits to try
        candidates_to_try = []
        proxy_candidates = []  # Separate proxy traits for fallback only if query is proxy
        if isinstance(resolution, dict):
            resolved_trait = resolution.get("resolved_trait_id")
            resolved_by = resolution.get("method")
            resolution_confidence = resolution.get("confidence")
            
            # Add resolved trait as first candidate
            if resolved_trait and isinstance(resolved_trait, str):
                # Check if resolved trait is a proxy
                trait_tokens = set(kg_service._normalize_trait_text(resolved_trait).split()) if hasattr(kg_service, "_normalize_trait_text") else set()
                is_proxy = any(t in trait_tokens for t in {"family", "history", "paternal", "maternal", "father", "mother", "sibling", "siblings"})
                
                if is_proxy and not query_is_proxy:
                    # Don't use proxy traits unless query is also proxy
                    proxy_candidates.append(resolved_trait)
                else:
                    candidates_to_try.append(resolved_trait)
            
            # Add other candidates, separating proxy from non-proxy
            candidates = resolution.get("candidates", [])
            for cand in candidates:
                cand_trait = cand.get("trait_id") if isinstance(cand, dict) else None
                if not cand_trait or cand_trait in candidates_to_try:
                    continue
                
                # Check if candidate is a proxy trait
                trait_tokens = set(kg_service._normalize_trait_text(cand_trait).split()) if hasattr(kg_service, "_normalize_trait_text") else set()
                is_proxy = any(t in trait_tokens for t in {"family", "history", "paternal", "maternal", "father", "mother", "sibling", "siblings"})
                
                if is_proxy and not query_is_proxy:
                    # Don't use proxy traits unless query is also proxy
                    if cand_trait not in proxy_candidates:
                        proxy_candidates.append(cand_trait)
                else:
                    candidates_to_try.append(cand_trait)
        
        # If no resolution, try query as-is
        if not candidates_to_try:
            candidates_to_try = [query_trait]

        # Step 2: Try each non-proxy candidate until we find one with neighbors
        target_node = None
        prioritized_neighbors = None
        final_trait_id = None
        
        for candidate_trait in candidates_to_try:
            # Get target trait node to verify trait exists
            target_node = kg_service.get_trait_node(candidate_trait)
            if target_node is None:
                continue
            
            # Get prioritized neighbors
            prioritized_neighbors = kg_service.get_prioritized_neighbors_v2(
                trait_id=candidate_trait,
                rg_z_threshold=rg_z_threshold,
                h2_z_threshold=h2_z_threshold
            )
            
            # If we found neighbors, use this trait
            if prioritized_neighbors and len(prioritized_neighbors) > 0:
                final_trait_id = candidate_trait
                resolved_by = resolved_by or "exact_match"
                resolution_confidence = resolution_confidence or "High"
                break
        
        # Step 2b: Only try proxy candidates if query is also proxy AND no non-proxy candidates worked
        if final_trait_id is None and query_is_proxy and proxy_candidates:
            for candidate_trait in proxy_candidates:
                target_node = kg_service.get_trait_node(candidate_trait)
                if target_node is None:
                    continue
                
                prioritized_neighbors = kg_service.get_prioritized_neighbors_v2(
                    trait_id=candidate_trait,
                    rg_z_threshold=rg_z_threshold,
                    h2_z_threshold=h2_z_threshold
                )
                
                if prioritized_neighbors and len(prioritized_neighbors) > 0:
                    final_trait_id = candidate_trait
                    if candidate_trait not in candidates_to_try:
                        resolved_by = resolved_by or "proxy_fallback"
                        resolution_confidence = "Low"
                    break
        
        # Handle case where no trait with neighbors was found
        # Return empty NeighborResult instead of ToolError for graceful handling
        if final_trait_id is None:
            # Determine the resolved trait (if any) for metadata
            resolved_trait_for_meta = candidates_to_try[0] if candidates_to_try else query_trait
            target_node = kg_service.get_trait_node(resolved_trait_for_meta)
            target_h2_val = target_node.h2_meta if target_node else None
            target_h2 = float(target_h2_val) if isinstance(target_h2_val, (int, float)) else 0.0
            
            return NeighborResult(
                query_trait=query_trait if resolved_by or (candidates_to_try and candidates_to_try[0] != query_trait) else None,
                resolved_by=resolved_by,
                resolution_confidence=resolution_confidence,
                target_trait=resolved_trait_for_meta,
                target_h2_meta=target_h2,
                neighbors=[]  # Empty list - no neighbors found
            )
        
        trait_id = final_trait_id
        # Ensure schema stability: NeighborResult.target_h2_meta is a float.
        # Some traits exist in the KG but have missing meta-analyzed h2 (None).
        target_h2_val = target_node.h2_meta if target_node else None
        target_h2 = float(target_h2_val) if isinstance(target_h2_val, (int, float)) else 0.0
        
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
            query_trait=query_trait if resolved_by or trait_id != query_trait else None,
            resolved_by=resolved_by,
            resolution_confidence=resolution_confidence,
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
    phewas_client = None,
    source_trait_mondo: Optional[str] = None,
    target_trait_mondo: Optional[str] = None
) -> Union[MechanismValidation, ToolError]:
    """
    Validate biological mechanism between two traits via Open Targets and PheWAS.
    
    Implements sop.md L532-560 specification.
    JIT Loading: Only called when Agent needs to justify cross-disease transfer.
    Token Budget: ~500 tokens.
    
    This tool acts as a "biological translator" - converting statistical
    correlation (rg) into causal biological logic via shared gene targets.
    
    **Strategy**: Tries both EFO and MONDO IDs (if provided) and merges results
    to maximize coverage, as different IDs may have different target associations.
    
    Args:
        ot_client: Open Targets client with get_disease_targets method
        source_trait_efo: Source trait EFO ID (e.g., "EFO_0000384")
        target_trait_efo: Target trait EFO ID (e.g., "EFO_0000729")
        source_trait_name: Human-readable source trait name
        target_trait_name: Human-readable target trait name
        top_n_genes: Number of top genes to compare (default 50)
        phewas_client: Optional ExPheWAS client for cross-validation
        source_trait_mondo: Optional MONDO ID for source trait (e.g., "MONDO_0005148")
        target_trait_mondo: Optional MONDO ID for target trait (e.g., "MONDO_0007254")
        
    Returns:
        MechanismValidation with shared genes and pathways, or ToolError
    """
    try:
        # Try EFO IDs first, then MONDO IDs if provided, and merge results
        source_targets_list = []
        target_targets_list = []
        
        # Fetch targets for source trait
        if source_trait_efo and source_trait_efo.strip():
            try:
                efo_targets = ot_client.get_disease_targets(source_trait_efo)
                if efo_targets:
                    source_targets_list.append(("EFO", efo_targets))
            except Exception:
                pass  # EFO ID may not exist or have no data
        
        if source_trait_mondo and source_trait_mondo.strip():
            try:
                mondo_targets = ot_client.get_disease_targets(source_trait_mondo)
                if mondo_targets:
                    source_targets_list.append(("MONDO", mondo_targets))
            except Exception:
                pass  # MONDO ID may not exist or have no data
        
        # Fetch targets for target trait
        if target_trait_efo and target_trait_efo.strip():
            try:
                efo_targets = ot_client.get_disease_targets(target_trait_efo)
                if efo_targets:
                    target_targets_list.append(("EFO", efo_targets))
            except Exception:
                pass  # EFO ID may not exist or have no data
        
        if target_trait_mondo and target_trait_mondo.strip():
            try:
                mondo_targets = ot_client.get_disease_targets(target_trait_mondo)
                if mondo_targets:
                    target_targets_list.append(("MONDO", mondo_targets))
            except Exception:
                pass  # MONDO ID may not exist or have no data
        
        # Merge targets: deduplicate by gene ID, keep highest score
        source_targets_map = {}  # gene_id -> (target_info, source_type)
        for source_type, targets in source_targets_list:
            for target in targets:
                gene_id = target.get("id")
                if gene_id:
                    existing = source_targets_map.get(gene_id)
                    if not existing or target.get("score", 0.0) > existing[0].get("score", 0.0):
                        source_targets_map[gene_id] = (target, source_type)
        
        target_targets_map = {}  # gene_id -> (target_info, source_type)
        for source_type, targets in target_targets_list:
            for target in targets:
                gene_id = target.get("id")
                if gene_id:
                    existing = target_targets_map.get(gene_id)
                    if not existing or target.get("score", 0.0) > existing[0].get("score", 0.0):
                        target_targets_map[gene_id] = (target, source_type)
        
        # Convert back to lists (keeping only target_info, not source_type)
        source_targets = [info for info, _ in source_targets_map.values()]
        target_targets = [info for info, _ in target_targets_map.values()]
        
        if not source_targets or not target_targets:
            return ToolError(
                tool_name="genetic_graph_validate_mechanism",
                error_type="NoTargetsFound",
                error_message=f"No targets found for source trait '{source_trait_name}' (EFO: {source_trait_efo}, MONDO: {source_trait_mondo}) or target trait '{target_trait_name}' (EFO: {target_trait_efo}, MONDO: {target_trait_mondo})",
                context={
                    "source_trait_efo": source_trait_efo,
                    "source_trait_mondo": source_trait_mondo,
                    "target_trait_efo": target_trait_efo,
                    "target_trait_mondo": target_trait_mondo,
                    "source_targets_count": len(source_targets),
                    "target_targets_count": len(target_targets)
                }
            )
        
        # Sort targets by score (descending) and take top N
        source_targets_sorted = sorted(source_targets, key=lambda t: t.get("score", 0.0), reverse=True)
        target_targets_sorted = sorted(target_targets, key=lambda t: t.get("score", 0.0), reverse=True)
        
        # Build lookup maps
        source_map = {t["id"]: t for t in source_targets_sorted[:top_n_genes]}
        target_map = {t["id"]: t for t in target_targets_sorted[:top_n_genes]}
        
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
                    logger.warning(f"PheWAS validation failed for {gene_id}: {e}")
            
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
                "source_trait_efo": source_trait_efo,
                "source_trait_mondo": source_trait_mondo,
                "target_trait_efo": target_trait_efo,
                "target_trait_mondo": target_trait_mondo
            }
        )
