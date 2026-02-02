# tests/unit/test_prs_model_tools.py
"""
Unit tests for PRS Model Tools.
Implements TDD for sop.md L356-462 tool specifications.
"""
import pytest
from src.server.core.tool_schemas import PGSModelSummary, PerformanceLandscape
from src.server.core.tools.prs_model_tools import prs_model_performance_landscape


def _create_model(
    id: str, 
    auc: float = None, 
    r2: float = None
) -> PGSModelSummary:
    """Helper to create a PGSModelSummary for testing."""
    return PGSModelSummary(
        id=id,
        trait_reported="T2D",
        trait_efo="efo",
        method_name="LDpred2",
        variants_number=100,
        ancestry_distribution="EUR",
        publication="Pub",
        date_release="2020-01-01",
        samples_training="n=1000",
        performance_metrics={"auc": auc, "r2": r2},
        phenotyping_reported="T2D",
        covariates="age,sex",
        sampleset=None
    )


class TestPerformanceLandscape:
    """Test prs_model_performance_landscape tool."""
    
    def test_basic_calculation(self):
        """Test performance landscape calculation with basic input."""
        models = [
            _create_model("PGS001", auc=0.75, r2=0.15),
            _create_model("PGS002", auc=0.80, r2=0.20),
            _create_model("PGS003", auc=0.70, r2=0.10),
        ]
        
        result = prs_model_performance_landscape(models)
        
        assert isinstance(result, PerformanceLandscape)
        assert result.total_models == 3
        assert result.auc_distribution.min == 0.70
        assert result.auc_distribution.max == 0.80
        assert result.auc_distribution.median == 0.75
        assert result.top_performer.pgs_id == "PGS002"
        assert result.top_performer.auc == 0.80

    def test_with_missing_auc(self):
        """Test handling of models with missing AUC."""
        models = [
            _create_model("PGS001", auc=0.75, r2=0.15),
            _create_model("PGS002", auc=None, r2=0.20),  # Missing AUC
        ]
        
        result = prs_model_performance_landscape(models)
        
        assert result.auc_distribution.missing_count == 1
        assert result.auc_distribution.min == 0.75  # Only one AUC
        assert result.auc_distribution.max == 0.75

    def test_with_missing_r2(self):
        """Test handling of models with missing R2."""
        models = [
            _create_model("PGS001", auc=0.75, r2=None),  # Missing R2
            _create_model("PGS002", auc=0.80, r2=0.20),
        ]
        
        result = prs_model_performance_landscape(models)
        
        assert result.r2_distribution.missing_count == 1
        assert result.r2_distribution.min == 0.20

    def test_with_all_missing_metrics(self):
        """Test handling of models with both AUC and R2 missing."""
        models = [
            _create_model("PGS001", auc=0.75, r2=0.15),
            _create_model("PGS002", auc=None, r2=None),  # Both missing
        ]
        
        result = prs_model_performance_landscape(models)
        
        assert result.auc_distribution.missing_count == 1
        assert result.r2_distribution.missing_count == 1
        assert result.top_performer.pgs_id == "PGS001"

    def test_empty_input(self):
        """Test handling of empty model list."""
        result = prs_model_performance_landscape([])
        
        assert result.total_models == 0
        assert result.verdict_context == "No models available for analysis"
        assert result.top_performer.pgs_id == "N/A"

    def test_single_model(self):
        """Test handling of single model."""
        models = [_create_model("PGS001", auc=0.75, r2=0.15)]
        
        result = prs_model_performance_landscape(models)
        
        assert result.total_models == 1
        assert result.auc_distribution.min == 0.75
        assert result.auc_distribution.max == 0.75
        assert result.auc_distribution.median == 0.75
        assert result.top_performer.percentile_rank == 100.0

    def test_percentile_calculation(self):
        """Test that top performer percentile is calculated correctly."""
        # 5 models with ascending AUC
        models = [
            _create_model(f"PGS00{i}", auc=0.60 + i*0.05, r2=0.10 + i*0.02)
            for i in range(1, 6)
        ]
        
        result = prs_model_performance_landscape(models)
        
        # Top model is PGS005 with AUC = 0.60 + 5*0.05 = 0.85
        assert result.top_performer.pgs_id == "PGS005"
        assert result.top_performer.auc == 0.85
        # Should be at 100th percentile (best)
        assert result.top_performer.percentile_rank == 100.0

    def test_verdict_context_format(self):
        """Test that verdict context contains meaningful information."""
        models = [
            _create_model("PGS001", auc=0.70, r2=0.10),
            _create_model("PGS002", auc=0.90, r2=0.30),
        ]
        
        result = prs_model_performance_landscape(models)
        
        # Verdict should mention percentage above median
        assert "Top model" in result.verdict_context
        assert "%" in result.verdict_context

    def test_r2_only_models(self):
        """Test with models that only have R2, no AUC."""
        models = [
            _create_model("PGS001", auc=None, r2=0.15),
            _create_model("PGS002", auc=None, r2=0.25),
        ]
        
        result = prs_model_performance_landscape(models)
        
        # Should use R2 for top performer since no AUC
        assert result.auc_distribution.missing_count == 2
        assert result.top_performer.r2 == 0.25
        assert result.top_performer.auc is None
