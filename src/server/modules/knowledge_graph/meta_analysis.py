"""
Meta-Analysis Utilities for Knowledge Graph.
Implements inverse-variance weighted meta-analysis formula per sop.md.

Formula (from sop.md):
    theta_meta = sum(w_i * theta_i) / sum(w_i), where w_i = 1/SE_i^2
    SE_meta = 1 / sqrt(sum(w_i))
    Z_meta = theta_meta / SE_meta
    P_meta = 2 * Phi(-|Z_meta|)

Where theta represents either h^2 (for nodes) or r_g (for edges).
"""
import math
from typing import List, Dict, Any, Optional
from scipy import stats


def inverse_variance_meta_analysis(
    estimates: List[float],
    standard_errors: List[float]
) -> Dict[str, Any]:
    """
    Perform fixed-effect inverse-variance weighted meta-analysis.
    
    This function implements the aggregation strategy defined in sop.md Module 2:
    - Weights estimates by precision (1/SE^2)
    - Provides a single, consolidated estimate per Trait (node) or Trait-pair (edge)
    
    Args:
        estimates: List of effect estimates (h2 or rg values)
        standard_errors: List of corresponding standard errors
        
    Returns:
        Dictionary with:
            - theta_meta: Meta-analyzed estimate
            - se_meta: Standard error of meta-analyzed estimate
            - z_meta: Z-score
            - p_meta: Two-tailed P-value
            - n_valid: Number of valid estimates used
            
    Raises:
        ValueError: If estimates and standard_errors have different lengths
    """
    if len(estimates) != len(standard_errors):
        raise ValueError("estimates and standard_errors must have same length")
    
    # Filter valid pairs (SE > 0, no NaN)
    valid_pairs = []
    for est, se in zip(estimates, standard_errors):
        # Skip if either value is None
        if est is None or se is None:
            continue
        # Skip NaN values
        if math.isnan(est) or math.isnan(se):
            continue
        # Skip invalid SE (must be positive)
        if se <= 0:
            continue
        valid_pairs.append((est, se))
    
    n_valid = len(valid_pairs)
    
    if n_valid == 0:
        return {
            "theta_meta": None,
            "se_meta": None,
            "z_meta": None,
            "p_meta": None,
            "n_valid": 0
        }
    
    # Calculate weights: w_i = 1/SE_i^2
    weights = [1.0 / (se ** 2) for _, se in valid_pairs]
    sum_weights = sum(weights)
    
    # Meta-analyzed estimate: theta_meta = sum(w_i * theta_i) / sum(w_i)
    theta_meta = sum(w * est for (est, _), w in zip(valid_pairs, weights)) / sum_weights
    
    # Standard error: SE_meta = 1 / sqrt(sum(w_i))
    se_meta = 1.0 / math.sqrt(sum_weights)
    
    # Z-score: Z_meta = theta_meta / SE_meta
    z_meta = theta_meta / se_meta
    
    # P-value: P_meta = 2 * Phi(-|Z_meta|) (two-tailed)
    p_meta = 2 * stats.norm.sf(abs(z_meta))
    
    return {
        "theta_meta": theta_meta,
        "se_meta": se_meta,
        "z_meta": z_meta,
        "p_meta": p_meta,
        "n_valid": n_valid
    }
