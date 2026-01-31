"""
Unit Tests for Meta-Analysis utility functions.
Tests the inverse-variance weighted meta-analysis formula per sop.md.
"""
import pytest
import math


def test_meta_analysis_single_estimate():
    """Single estimate should return the same value."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    estimates = [0.5]
    standard_errors = [0.1]
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["theta_meta"] == pytest.approx(0.5, rel=1e-6)
    assert result["se_meta"] == pytest.approx(0.1, rel=1e-6)
    assert result["n_valid"] == 1


def test_meta_analysis_two_estimates():
    """Two estimates should be weighted by inverse variance."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    # Estimate 1: theta=0.4, se=0.1 -> weight = 1/0.01 = 100
    # Estimate 2: theta=0.6, se=0.2 -> weight = 1/0.04 = 25
    # theta_meta = (100*0.4 + 25*0.6) / (100 + 25) = (40 + 15) / 125 = 0.44
    # se_meta = 1/sqrt(125) = 0.0894
    estimates = [0.4, 0.6]
    standard_errors = [0.1, 0.2]
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["theta_meta"] == pytest.approx(0.44, rel=1e-3)
    assert result["se_meta"] == pytest.approx(1/math.sqrt(125), rel=1e-3)
    assert result["z_meta"] == pytest.approx(0.44 / (1/math.sqrt(125)), rel=1e-3)
    assert result["n_valid"] == 2


def test_meta_analysis_empty_input():
    """Empty input should return None values."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    result = inverse_variance_meta_analysis([], [])
    
    assert result["theta_meta"] is None
    assert result["se_meta"] is None
    assert result["n_valid"] == 0


def test_meta_analysis_skips_invalid_se():
    """Should skip estimates with zero or negative SE."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    estimates = [0.5, 0.6, 0.7]
    standard_errors = [0.1, 0.0, -0.1]  # Only first is valid
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["theta_meta"] == pytest.approx(0.5, rel=1e-6)
    assert result["n_valid"] == 1


def test_meta_analysis_skips_nan_values():
    """Should skip NaN estimates and SEs."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    estimates = [0.5, float('nan'), 0.6]
    standard_errors = [0.1, 0.1, float('nan')]
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    # Only first estimate (0.5, 0.1) is valid
    assert result["theta_meta"] == pytest.approx(0.5, rel=1e-6)
    assert result["n_valid"] == 1


def test_meta_analysis_p_value_calculation():
    """Test that P-value is correctly calculated from Z-score."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    # Large Z -> small p
    estimates = [0.5]
    standard_errors = [0.05]  # Z = 10
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["z_meta"] == pytest.approx(10.0, rel=1e-3)
    assert result["p_meta"] < 1e-10  # Very small p-value
