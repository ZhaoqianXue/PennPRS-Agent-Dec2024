# src/server/core/tools/prs_model_tools.py
"""
PRS Model Tools for Module 3.
Implements sop.md L356-462 tool specifications.
"""
from typing import List, Optional
from statistics import median, quantiles
from src.server.core.tool_schemas import (
    PGSModelSummary, PGSSearchResult,
    PerformanceLandscape, MetricDistribution, TopPerformerSummary,
    ToolError
)


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
