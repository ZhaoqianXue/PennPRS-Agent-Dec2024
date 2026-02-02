# src/server/core/tools/prs_model_tools.py
"""
PRS Model Tools for Module 3.
Implements sop.md L356-462 tool specifications.
"""
from typing import List, Optional, Dict, Any
from statistics import median, quantiles
from src.server.core.tool_schemas import (
    PGSModelSummary, PGSSearchResult,
    PerformanceLandscape, MetricDistribution, TopPerformerSummary,
    ToolError
)


def prs_model_pgscatalog_search(
    client,  # PGSCatalogClient
    trait_query: str,
    limit: int = 10
) -> PGSSearchResult:
    """
    Search for trait-specific PRS models and retrieve [Agent + UI] metadata.
    
    Implements sop.md L359-392 specification.
    Hard-coded Filter: Remove models where AUC and R2 are both null.
    Token Budget: ~500 tokens per model; max 10 models.
    
    Args:
        client: PGSCatalogClient instance
        trait_query: User's target trait (e.g., "Type 2 Diabetes")
        limit: Max models to return (default 10)
        
    Returns:
        PGSSearchResult with filtered models
    """
    # 1. Search for scores
    search_results = client.search_scores(trait_query)
    total_found = len(search_results)
    
    models = []
    
    # 2. Fetch details and performance for each score
    for res in search_results:
        if len(models) >= limit:
            break
            
        pgs_id = res['id']
        
        # Get metadata and performance
        details = client.get_score_details(pgs_id)
        performance = client.get_score_performance(pgs_id)
        
        if not details:
            continue
            
        # Extract performance metrics
        auc = None
        r2 = None
        
        # PGS Catalog performance search returns a list of results, each with effect_sizes
        for p in performance:
            for es in p.get("effect_sizes", []):
                name = es.get("name_short", "").upper()
                estimate = es.get("estimate")
                if name == "AUC" and estimate is not None:
                    auc = float(estimate)
                elif (name == "R²" or name == "R2") and estimate is not None:
                    r2 = float(estimate)
        
        # Hard-coded Filter: Remove models where both are null
        if auc is None and r2 is None:
            continue
            
        # Map to [Agent + UI] fields
        summary = PGSModelSummary(
            id=pgs_id,
            trait_reported=details.get("trait_reported", "Unknown"),
            trait_efo=", ".join([t.get("label", "") for t in details.get("trait_efo", [])]),
            method_name=details.get("method_name", "Unknown"),
            variants_number=details.get("variants_number", 0),
            ancestry_distribution=_format_ancestry(details.get("ancestry_distribution", {})),
            publication=details.get("publication", {}).get("title", "Unknown"),
            date_release=details.get("date_release", "Unknown"),
            samples_training=_format_samples(details.get("samples_training", [])),
            performance_metrics={"auc": auc, "r2": r2},
            phenotyping_reported=performance[0].get("phenotyping_reported", "Unknown") if performance else "Unknown",
            covariates=performance[0].get("covariates", "Unknown") if performance else "Unknown",
            sampleset=performance[0].get("sampleset", {}).get("name", "Unknown") if performance else "Unknown"
        )
        models.append(summary)
        
    return PGSSearchResult(
        query_trait=trait_query,
        total_found=total_found,
        after_filter=len(models),
        models=models
    )


def _format_ancestry(dist: Dict[str, Any]) -> str:
    """Format ancestry distribution for LLM context."""
    if not dist:
        return "Unknown"
    
    parts = []
    for stage in ["gwas", "dev", "eval"]:
        if stage in dist:
            stage_parts = []
            for anc, weight in dist[stage].items():
                stage_parts.append(f"{anc} ({weight*100:.0f}%)")
            parts.append(f"{stage.upper()}: {', '.join(stage_parts)}")
            
    return " | ".join(parts) if parts else "Unknown"


def _format_samples(samples: List[Dict[str, Any]]) -> str:
    """Format training samples for LLM context."""
    if not samples:
        return "N/A"
    
    total_n = sum(s.get("sample_number", 0) for s in samples)
    return f"n={total_n:,}"


def prs_model_performance_landscape(models: List[PGSModelSummary]) -> PerformanceLandscape:
    """
    Calculate statistical distributions across all retrieved candidate models.
    
    Implements sop.md L430-462 specification.
    Token Budget: ~200 tokens.
    
    Args:
        models: Filtered models from prs_model_pgscatalog_search
        
    Returns:
        PerformanceLandscape with distributions and top performer
    """
    if not models:
        return PerformanceLandscape(
            total_models=0,
            auc_distribution=MetricDistribution(
                min=0, max=0, median=0, p25=0, p75=0, missing_count=0
            ),
            r2_distribution=MetricDistribution(
                min=0, max=0, median=0, p25=0, p75=0, missing_count=0
            ),
            top_performer=TopPerformerSummary(pgs_id="N/A", auc=None, r2=None, percentile_rank=0),
            verdict_context="No models available for analysis"
        )
    
    # Extract metrics, handling None values
    auc_values: List[tuple] = []  # (id, auc)
    r2_values: List[tuple] = []   # (id, r2)
    auc_missing = 0
    r2_missing = 0
    
    for m in models:
        auc = m.performance_metrics.get("auc")
        r2 = m.performance_metrics.get("r2")
        
        if auc is not None:
            auc_values.append((m.id, auc))
        else:
            auc_missing += 1
            
        if r2 is not None:
            r2_values.append((m.id, r2))
        else:
            r2_missing += 1
    
    # Calculate distributions
    auc_distribution = _calculate_distribution([v for _, v in auc_values], auc_missing)
    r2_distribution = _calculate_distribution([v for _, v in r2_values], r2_missing)
    
    # Find top performer (by AUC, fallback to R2)
    top_performer = _find_top_performer(auc_values, r2_values)
    
    # Generate verdict context
    verdict = _generate_verdict(auc_values, auc_distribution)
    
    return PerformanceLandscape(
        total_models=len(models),
        auc_distribution=auc_distribution,
        r2_distribution=r2_distribution,
        top_performer=top_performer,
        verdict_context=verdict
    )


def _calculate_distribution(values: List[float], missing_count: int) -> MetricDistribution:
    """Calculate statistical distribution for a list of values."""
    if not values:
        return MetricDistribution(
            min=0, max=0, median=0, p25=0, p75=0, missing_count=missing_count
        )
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    if n >= 4:
        # Use quantiles for 4+ values
        q = quantiles(sorted_vals, n=4)
        p25, med, p75 = q[0], q[1], q[2]
    elif n >= 2:
        med = median(sorted_vals)
        p25 = sorted_vals[0]
        p75 = sorted_vals[-1]
    else:
        # Single value
        med = sorted_vals[0]
        p25 = p75 = med
    
    return MetricDistribution(
        min=min(sorted_vals),
        max=max(sorted_vals),
        median=med,
        p25=p25,
        p75=p75,
        missing_count=missing_count
    )


def _find_top_performer(
    auc_values: List[tuple], 
    r2_values: List[tuple]
) -> TopPerformerSummary:
    """Find the top performing model by AUC (preferred) or R2."""
    if auc_values:
        # Find best by AUC
        top_id, top_auc = max(auc_values, key=lambda x: x[1])
        # Find corresponding R2
        r2_map = dict(r2_values)
        top_r2 = r2_map.get(top_id)
        # Calculate percentile (percentage of models at or below this AUC)
        all_aucs = [v for _, v in auc_values]
        rank = sum(1 for v in all_aucs if v <= top_auc) / len(all_aucs) * 100
    elif r2_values:
        # Fallback to R2 if no AUC data
        top_id, top_r2 = max(r2_values, key=lambda x: x[1])
        top_auc = None
        all_r2s = [v for _, v in r2_values]
        rank = sum(1 for v in all_r2s if v <= top_r2) / len(all_r2s) * 100
    else:
        return TopPerformerSummary(pgs_id="N/A", auc=None, r2=None, percentile_rank=0)
    
    return TopPerformerSummary(
        pgs_id=top_id,
        auc=top_auc,
        r2=top_r2,
        percentile_rank=rank
    )


def _generate_verdict(
    auc_values: List[tuple], 
    auc_distribution: MetricDistribution
) -> str:
    """Generate a human-readable verdict context."""
    if not auc_values:
        return "Performance data limited - no AUC metrics available"
    
    best_auc = max(v for _, v in auc_values)
    median_auc = auc_distribution.median
    
    if median_auc > 0:
        pct_above = ((best_auc - median_auc) / median_auc * 100)
        if pct_above > 0:
            return f"Top model is +{pct_above:.0f}% above median AUC"
        elif pct_above < 0:
            return f"Top model is {abs(pct_above):.0f}% below median AUC"
        else:
            return "Top model matches median AUC"
    else:
        return "Median AUC is zero - check data quality"


# --- Domain Knowledge Tool ---

# Default path to knowledge base
import os
KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "knowledge", "prs_model_domain_knowledge.md"
)


def prs_model_domain_knowledge(
    query: str,
    knowledge_file: Optional[str] = None,
    max_snippets: int = 5
):
    """
    Search domain knowledge for PRS model selection guidance.
    
    Implements sop.md L394-428 specification.
    Currently uses local file retrieval; will upgrade to web search.
    Token Budget: ~300 tokens.
    
    Args:
        query: Search query (e.g., "LDpred2 best for", "ancestry considerations")
        knowledge_file: Optional path to knowledge base file
        max_snippets: Maximum snippets to return (default 5)
        
    Returns:
        DomainKnowledgeResult with relevant snippets
    """
    from src.server.core.tool_schemas import DomainKnowledgeResult, KnowledgeSnippet
    
    kb_path = knowledge_file or KNOWLEDGE_BASE_PATH
    
    # Load knowledge base
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return DomainKnowledgeResult(
            query=query,
            snippets=[],
            source_type="local"
        )
    
    # Parse into sections
    sections = _parse_markdown_sections(content)
    
    # Score and rank sections by relevance
    query_terms = query.lower().split()
    scored_sections = []
    
    for section_title, section_content in sections:
        score = _calculate_relevance(query_terms, section_title, section_content)
        if score > 0:
            scored_sections.append((section_title, section_content, score))
    
    # Sort by score descending
    scored_sections.sort(key=lambda x: x[2], reverse=True)
    
    # Build snippets
    snippets = []
    for title, content_text, score in scored_sections[:max_snippets]:
        # Truncate content to reasonable length
        truncated = content_text[:500] + "..." if len(content_text) > 500 else content_text
        
        snippet = KnowledgeSnippet(
            source="prs_model_domain_knowledge.md",
            section=title,
            content=truncated,
            relevance_score=min(score / 10.0, 1.0)  # Normalize to 0-1
        )
        snippets.append(snippet)
    
    return DomainKnowledgeResult(
        query=query,
        snippets=snippets,
        source_type="local"
    )


def _parse_markdown_sections(content: str) -> List[tuple]:
    """
    Parse markdown content into sections.
    
    Returns:
        List of (section_title, section_content) tuples
    """
    import re
    
    sections = []
    current_title = "Introduction"
    current_content = []
    
    for line in content.split('\n'):
        # Check for headers (##, ###)
        header_match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if header_match:
            # Save previous section
            if current_content:
                sections.append((current_title, '\n'.join(current_content).strip()))
            current_title = header_match.group(2)
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections.append((current_title, '\n'.join(current_content).strip()))
    
    return sections


def _calculate_relevance(query_terms: List[str], title: str, content: str) -> float:
    """
    Calculate relevance score between query and section.
    
    Simple keyword matching - can be upgraded to embeddings later.
    """
    combined = (title + " " + content).lower()
    
    score = 0.0
    for term in query_terms:
        if term in combined:
            # Higher weight for title matches
            if term in title.lower():
                score += 3.0
            else:
                score += 1.0
            
            # Bonus for multiple occurrences
            count = combined.count(term)
            if count > 1:
                score += min(count * 0.2, 2.0)
    
    return score

