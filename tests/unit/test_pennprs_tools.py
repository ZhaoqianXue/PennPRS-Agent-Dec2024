# tests/unit/test_pennprs_tools.py
"""
Unit tests for PennPRS Tools.
Implements TDD for sop.md L564-594 tool specifications.
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.server.core.tool_schemas import (
    TrainingConfig, JobSubmissionResult, ToolError
)
from src.server.core.tools.pennprs_tools import pennprs_train_model, generate_training_config


class TestGenerateTrainingConfig:
    """Test generate_training_config function."""
    
    def test_generates_config_for_t2d(self):
        """Test config generation for Type 2 Diabetes."""
        config = generate_training_config(
            target_trait="Type 2 Diabetes",
            gwas_id="GCST90014023",
            ancestry="EUR",
            trait_type="binary"
        )
        
        assert isinstance(config, TrainingConfig)
        assert config.target_trait == "Type 2 Diabetes"
        assert config.ancestry == "EUR"
        assert config.traits_type == "binary"
        assert len(config.job_methods) > 0
        assert config.recommended_method in config.job_methods

    def test_recommends_ldpred2_for_polygenic(self):
        """Test tool recommends LDpred2 for polygenic traits."""
        config = generate_training_config(
            target_trait="Schizophrenia",
            gwas_id="GCST90001234",
            ancestry="EUR",
            trait_type="binary",
            sample_size=100000
        )
        
        # LDpred2 should be recommended for large polygenic GWAS
        assert "LDpred2" in config.job_methods
        
    def test_recommends_prscs_for_very_large_gwas(self):
        """Test tool recommends PRS-CS for very large GWAS."""
        config = generate_training_config(
            target_trait="Height",
            gwas_id="GCST90099999",
            ancestry="EUR",
            trait_type="continuous",
            sample_size=500000
        )
        
        assert "PRS-CS" in config.job_methods

    def test_handles_non_eur_ancestry(self):
        """Test config adapts for non-EUR ancestry."""
        config = generate_training_config(
            target_trait="Type 2 Diabetes",
            gwas_id="GCST90014024",
            ancestry="EAS",
            trait_type="binary"
        )
        
        assert config.ancestry == "EAS"
        assert config.traits_population == "EAS"
        # LD reference should mention EAS
        assert "EAS" in config.ld_reference or "1000G" in config.ld_reference

    def test_generates_unique_job_name(self):
        """Test generates unique job name."""
        config1 = generate_training_config(
            target_trait="Trait A",
            gwas_id="GCST1",
            ancestry="EUR",
            trait_type="binary"
        )
        config2 = generate_training_config(
            target_trait="Trait A",
            gwas_id="GCST1",
            ancestry="EUR",
            trait_type="binary"
        )
        
        # Job names should be unique (include timestamp or UUID)
        assert config1.job_name != config2.job_name or "Trait A" in config1.job_name


class TestSubmitJob:
    """Test pennprs_train_model tool."""
    
    @pytest.fixture
    def mock_pennprs_client(self):
        """Create mock PennPRS client."""
        client = Mock()
        client.add_single_job.return_value = {
            "jobId": "job_12345",
            "status": "submitted",
            "message": "Job submitted successfully"
        }
        return client
    
    @pytest.fixture
    def sample_config(self):
        """Create sample training config."""
        return TrainingConfig(
            target_trait="Type 2 Diabetes",
            recommended_method="LDpred2",
            method_rationale="Recommended for polygenic traits with moderate heritability",
            job_name="T2D_20260202_001",
            job_type="single",
            job_methods=["LDpred2", "PRS-CS"],
            job_ensemble=True,
            traits_source="public",
            traits_detail="GCST90014023",
            traits_type="binary",
            traits_population="EUR",
            gwas_summary_stats="GCST90014023",
            ld_reference="1000G EUR",
            ancestry="EUR",
            agent_confidence="High",
            estimated_runtime="~2 hours"
        )

    def test_submits_job_successfully(self, mock_pennprs_client, sample_config):
        """Test successful job submission."""
        result = pennprs_train_model(
            pennprs_client=mock_pennprs_client,
            config=sample_config
        )
        
        assert isinstance(result, JobSubmissionResult)
        assert result.success is True
        assert result.job_id == "job_12345"
        assert result.status == "submitted"
        mock_pennprs_client.add_single_job.assert_called_once()

    def test_returns_error_on_api_failure(self, sample_config):
        """Test error handling when API fails."""
        failing_client = Mock()
        failing_client.add_single_job.return_value = None
        
        result = pennprs_train_model(
            pennprs_client=failing_client,
            config=sample_config
        )
        
        assert isinstance(result, ToolError)
        assert result.tool_name == "pennprs_train_model"
        assert result.error_type == "SubmissionFailed"

    def test_passes_correct_parameters(self, mock_pennprs_client, sample_config):
        """Test correct parameters are passed to API."""
        pennprs_train_model(
            pennprs_client=mock_pennprs_client,
            config=sample_config
        )
        
        # Verify the call parameters
        call_kwargs = mock_pennprs_client.add_single_job.call_args
        
        # Check key parameters were passed
        assert call_kwargs[1]["job_name"] == "T2D_20260202_001"
        assert "LDpred2" in call_kwargs[1]["job_methods"]
        assert call_kwargs[1]["job_ensemble"] == True

    def test_handles_exception(self, sample_config):
        """Test exception handling."""
        failing_client = Mock()
        failing_client.add_single_job.side_effect = ConnectionError("Network error")
        
        result = pennprs_train_model(
            pennprs_client=failing_client,
            config=sample_config
        )
        
        assert isinstance(result, ToolError)
        assert "Network error" in result.error_message
