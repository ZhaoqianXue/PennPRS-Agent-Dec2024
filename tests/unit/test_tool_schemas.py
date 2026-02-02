# tests/unit/test_tool_schemas.py
"""
Unit tests for Module 3 Tool I/O Schemas.
Tests sop.md L352-622 output schema specifications.
"""
import pytest
from src.server.core.tool_schemas import (
    PGSSearchResult, PGSModelSummary,
    PerformanceLandscape, MetricDistribution,
    NeighborResult, RankedNeighbor,
    StudyPowerResult, CorrelationProvenance,
    MechanismValidation, SharedGene,
    TrainingConfig,
    ToolError
)


class TestPRSModelSchemas:
    """Test PRS Model Tool schemas."""
    
    def test_pgs_model_summary_schema(self):
        """Test PGSModelSummary can be instantiated with required fields."""
        summary = PGSModelSummary(
            id="PGS000025",
            trait_reported="Type 2 Diabetes",
            trait_efo="type 2 diabetes mellitus",
            method_name="LDpred2",
            variants_number=100000,
            ancestry_distribution="EUR (100%)",
            publication="Smith et al. 2020",
            date_release="2020-01-01",
            samples_training="n=50000",
            performance_metrics={"auc": 0.75, "r2": 0.15},
            phenotyping_reported="Type 2 Diabetes",
            covariates="age, sex, PC1-10",
            sampleset="UKB",
            training_development_cohorts=["UKB"]
        )
        assert summary.id == "PGS000025"
        assert summary.performance_metrics["auc"] == 0.75
        assert summary.trait_reported == "Type 2 Diabetes"

    def test_pgs_search_result_schema(self):
        """Test PGSSearchResult aggregates models correctly."""
        model = PGSModelSummary(
            id="PGS000001",
            trait_reported="T2D",
            trait_efo="efo",
            method_name="LDpred2",
            variants_number=100,
            ancestry_distribution="EUR",
            publication="Pub",
            date_release="2020-01-01",
            samples_training="n=1000",
            performance_metrics={"auc": 0.7, "r2": 0.1},
            phenotyping_reported="T2D",
            covariates="age",
            sampleset=None,
            training_development_cohorts=[]
        )
        result = PGSSearchResult(
            query_trait="Type 2 Diabetes",
            total_found=10,
            after_filter=5,
            models=[model]
        )
        assert result.total_found == 10
        assert result.after_filter == 5
        assert len(result.models) == 1

    def test_performance_landscape_schema(self):
        """Test PerformanceLandscape can be instantiated."""
        dist = MetricDistribution(
            min=0.5, max=0.85, median=0.7, p25=0.65, p75=0.78, missing_count=2
        )
        landscape = PerformanceLandscape(
            total_models=10,
            ancestry={"EUR": 10},
            sample_size=dist,
            auc=dist,
            r2=dist,
            variants=dist,
            training_development_cohorts={"UKB": 3},
            prs_methods={"LDpred2": 10}
        )
        assert landscape.total_models == 10
        assert landscape.auc.median == 0.7


class TestGeneticGraphSchemas:
    """Test Genetic Graph Tool schemas."""
    
    def test_neighbor_result_schema(self):
        """Test NeighborResult for genetic graph."""
        neighbor = RankedNeighbor(
            trait_id="Schizophrenia",
            domain="Psychiatric",
            rg_meta=0.6,
            rg_z_meta=5.2,
            h2_meta=0.8,
            transfer_score=0.288,  # 0.6^2 * 0.8
            n_correlations=3
        )
        result = NeighborResult(
            target_trait="Bipolar Disorder",
            target_h2_meta=0.7,
            neighbors=[neighbor]
        )
        assert len(result.neighbors) == 1
        assert result.neighbors[0].transfer_score == 0.288
        assert result.target_trait == "Bipolar Disorder"

    def test_study_power_result_schema(self):
        """Test StudyPowerResult for edge provenance."""
        prov = CorrelationProvenance(
            study1_id=123, study1_n=50000, study1_population="EUR", study1_pmid="12345678",
            study2_id=456, study2_n=40000, study2_population="EUR", study2_pmid="87654321",
            rg=0.65, se=0.05, p=1e-10
        )
        result = StudyPowerResult(
            source_trait="Crohn's disease",
            target_trait="Ulcerative colitis",
            rg_meta=0.56,
            n_correlations=2,
            correlations=[prov]
        )
        assert result.n_correlations == 2
        assert result.correlations[0].rg == 0.65
        assert result.source_trait == "Crohn's disease"

    def test_mechanism_validation_schema(self):
        """Test MechanismValidation for biological evidence."""
        gene = SharedGene(
            gene_symbol="IL23R",
            gene_id="ENSG00000162594",
            source_association=0.92,
            target_association=0.87,
            druggability="High",
            pathways=["IL-17 signaling"]
        )
        validation = MechanismValidation(
            source_trait="Crohn's disease",
            target_trait="Ulcerative colitis",
            shared_genes=[gene],
            shared_pathways=["Inflammatory bowel disease pathway"],
            mechanism_summary="Both share IL23R pathogenic pathway",
            confidence_level="High"
        )
        assert len(validation.shared_genes) == 1
        assert validation.confidence_level == "High"
        assert validation.shared_genes[0].gene_symbol == "IL23R"


class TestPennPRSSchemas:
    """Test PennPRS Tool schemas."""
    
    def test_training_config_schema(self):
        """Test TrainingConfig for PennPRS form."""
        config = TrainingConfig(
            target_trait="Type 2 Diabetes",
            recommended_method="LDpred2",
            method_rationale="Best for polygenic traits with large GWAS",
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
            validation_cohort="UKB",
            agent_confidence="High",
            estimated_runtime="~2 hours"
        )
        assert config.recommended_method == "LDpred2"
        assert config.agent_confidence == "High"
        assert config.job_ensemble is True
        assert "LDpred2" in config.job_methods

    def test_training_config_optional_cohort(self):
        """Test TrainingConfig with optional validation_cohort."""
        config = TrainingConfig(
            target_trait="CAD",
            recommended_method="PRS-CS",
            method_rationale="Good for sparse effects",
            job_name="CAD_001",
            job_type="single",
            job_methods=["PRS-CS"],
            job_ensemble=False,
            traits_source="public",
            traits_detail="GCST12345",
            traits_type="binary",
            traits_population="EUR",
            gwas_summary_stats="file.txt",
            ld_reference="1000G EUR",
            ancestry="EUR",
            validation_cohort=None,  # Optional
            agent_confidence="Moderate",
            estimated_runtime="~1 hour"
        )
        assert config.validation_cohort is None


class TestErrorSchema:
    """Test ToolError schema for error handling."""
    
    def test_tool_error_schema(self):
        """Test ToolError captures failure context."""
        error = ToolError(
            tool_name="genetic_graph_get_neighbors",
            error_type="TraitNotFound",
            error_message="Trait 'NonExistent' not found in Knowledge Graph",
            context={"trait_id": "NonExistent", "attempted_at": "2024-01-01"}
        )
        assert error.tool_name == "genetic_graph_get_neighbors"
        assert error.error_type == "TraitNotFound"
        assert "NonExistent" in error.context["trait_id"]

    def test_tool_error_default_context(self):
        """Test ToolError with empty context."""
        error = ToolError(
            tool_name="test_tool",
            error_type="GenericError",
            error_message="Something went wrong"
        )
        assert error.context == {}
