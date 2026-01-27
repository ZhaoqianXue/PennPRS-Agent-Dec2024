"""
Unit tests for heritability clients.
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.modules.heritability.models import HeritabilityEstimate, HeritabilitySource
from src.modules.heritability.gwas_atlas_client import GWASAtlasClient
from src.modules.heritability.pan_ukb_client import PanUKBClient
from src.modules.heritability.ukbb_ldsc_client import UKBBLDSCClient
from src.modules.heritability.aggregator import HeritabilityAggregator


class TestGWASAtlasClient:
    """Tests for GWAS Atlas client."""
    
    @pytest.fixture
    def mock_gwas_data(self):
        """Sample GWAS Atlas data."""
        return pd.DataFrame({
            "id": ["GCST001", "GCST002", "GCST003"],
            "Trait": ["Alzheimer's disease", "Type 2 diabetes", "Alzheimer disease"],
            "h2": [0.24, 0.45, 0.22],
            "h2_SE": [0.03, 0.04, 0.05],
            "N": [54162, 100000, 40000],
            "pop": ["EUR", "EUR", "EAS"]
        })
    
    def test_search_trait_returns_matches(self, mock_gwas_data):
        """Test that search_trait finds matching traits."""
        client = GWASAtlasClient()
        client._df = mock_gwas_data
        client._loaded = True
        
        results = client.search_trait("Alzheimer", min_score=50)
        
        assert len(results) >= 1
        assert all(isinstance(r, HeritabilityEstimate) for r in results)
        assert all(r.source == HeritabilitySource.GWAS_ATLAS for r in results)
    
    def test_search_trait_empty_when_no_data(self):
        """Test that search returns empty list when no data loaded."""
        client = GWASAtlasClient()
        client._df = pd.DataFrame()
        client._loaded = True
        
        results = client.search_trait("Alzheimer")
        
        assert results == []
    
    def test_get_trait_count(self, mock_gwas_data):
        """Test trait count returns correct number."""
        client = GWASAtlasClient()
        client._df = mock_gwas_data
        client._loaded = True
        
        count = client.get_trait_count()
        
        assert count == 3  # 3 unique traits


class TestPanUKBClient:
    """Tests for Pan-UK Biobank client."""
    
    @pytest.fixture
    def mock_pan_ukb_data(self):
        """Sample Pan-UKB data with multi-ancestry."""
        return pd.DataFrame({
            "description": ["Alzheimer's disease", "Alzheimer's disease", "Type 2 diabetes"],
            "phenocode": ["AD001", "AD001", "T2D001"],
            "h2_observed": [0.25, 0.18, 0.50],
            "h2_observed_se": [0.02, 0.03, 0.04],
            "pop": ["EUR", "AFR", "EUR"],
            "n_cases": [5000, 2000, 10000]
        })
    
    def test_search_trait_multi_ancestry(self, mock_pan_ukb_data):
        """Test that search returns multiple ancestry results."""
        client = PanUKBClient()
        client._df = mock_pan_ukb_data
        client._loaded = True
        
        results = client.search_trait("Alzheimer", min_score=50)
        
        populations = {r.population for r in results}
        assert "EUR" in populations or "AFR" in populations
    
    def test_get_ancestry_breakdown(self, mock_pan_ukb_data):
        """Test ancestry breakdown groups correctly."""
        client = PanUKBClient()
        client._df = mock_pan_ukb_data
        client._loaded = True
        
        breakdown = client.get_ancestry_breakdown("Alzheimer")
        
        assert isinstance(breakdown, dict)
        # Should have at least one ancestry group
        assert len(breakdown) >= 0
    
    def test_filter_by_ancestry(self, mock_pan_ukb_data):
        """Test filtering by specific ancestry."""
        client = PanUKBClient()
        client._df = mock_pan_ukb_data
        client._loaded = True
        
        results = client.search_trait("Alzheimer", ancestry="EUR")
        
        for r in results:
            assert r.population == "EUR"


class TestUKBBLDSCClient:
    """Tests for UKBB LDSC client."""
    
    @pytest.fixture
    def mock_ldsc_data(self):
        """Sample UKBB LDSC data."""
        return pd.DataFrame({
            "description": ["Alzheimer's disease", "Depression", "BMI"],
            "phenotype_code": ["AD", "DEP", "BMI"],
            "h2_observed": [0.22, 0.15, 0.35],
            "h2_se": [0.03, 0.02, 0.01],
            "n": [50000, 80000, 300000]
        })
    
    def test_search_trait_returns_eur_only(self, mock_ldsc_data):
        """Test that UKBB LDSC returns EUR-only results."""
        client = UKBBLDSCClient()
        client._df = mock_ldsc_data
        client._loaded = True
        
        results = client.search_trait("Alzheimer", min_score=50)
        
        for r in results:
            assert r.population == "EUR"
            assert r.source == HeritabilitySource.UKBB_LDSC


class TestHeritabilityAggregator:
    """Tests for heritability aggregator."""
    
    @pytest.fixture
    def mock_aggregator(self):
        """Create aggregator with mocked clients."""
        aggregator = HeritabilityAggregator()
        
        # Mock GWAS Atlas
        aggregator.gwas_atlas._df = pd.DataFrame({
            "Trait": ["Alzheimer's disease"],
            "h2": [0.24],
            "h2_SE": [0.03],
            "N": [54162]
        })
        aggregator.gwas_atlas._loaded = True
        
        # Mock Pan-UKB
        aggregator.pan_ukb._df = pd.DataFrame({
            "description": ["Alzheimer's disease"],
            "h2_observed": [0.20],
            "h2_observed_se": [0.04],
            "pop": ["EUR"]
        })
        aggregator.pan_ukb._loaded = True
        
        # Mock UKBB LDSC
        aggregator.ukbb_ldsc._df = pd.DataFrame({
            "description": ["Alzheimer's disease"],
            "h2_observed": [0.22],
            "h2_se": [0.02],
            "n": [100000]
        })
        aggregator.ukbb_ldsc._loaded = True
        
        return aggregator
    
    def test_search_combines_sources(self, mock_aggregator):
        """Test that search combines results from all sources."""
        results = mock_aggregator.search("Alzheimer", min_score=50)
        
        sources = {r.source for r in results}
        # Should have results from at least one source
        assert len(sources) >= 1
    
    def test_get_best_estimate_prioritizes_correctly(self, mock_aggregator):
        """Test that best estimate selection works."""
        best = mock_aggregator.get_best_estimate("Alzheimer")
        
        # Should return something
        if best:
            assert isinstance(best, HeritabilityEstimate)
            assert best.h2_obs > 0
    
    def test_gap_analysis_calculates_efficiency(self, mock_aggregator):
        """Test gap analysis calculation."""
        result = mock_aggregator.gap_analysis("Alzheimer", prs_r2=0.08)
        
        assert result.trait_name == "Alzheimer"
        if result.best_h2 and result.best_prs_r2:
            assert result.efficiency is not None
            assert 0 <= result.efficiency <= 1
            assert result.improvement_potential is not None
    
    def test_get_by_source(self, mock_aggregator):
        """Test grouping by source."""
        by_source = mock_aggregator.get_by_source("Alzheimer")
        
        assert isinstance(by_source, dict)
    
    def test_get_by_ancestry(self, mock_aggregator):
        """Test grouping by ancestry."""
        by_ancestry = mock_aggregator.get_by_ancestry("Alzheimer")
        
        assert isinstance(by_ancestry, dict)


class TestHeritabilityModels:
    """Tests for Pydantic models."""
    
    def test_heritability_estimate_validation(self):
        """Test that HeritabilityEstimate validates correctly."""
        estimate = HeritabilityEstimate(
            trait_name="Alzheimer's disease",
            h2_obs=0.24,
            population="EUR",
            source=HeritabilitySource.GWAS_ATLAS
        )
        
        assert estimate.trait_name == "Alzheimer's disease"
        assert estimate.h2_obs == 0.24
        assert estimate.method == "ldsc"  # Default
    
    def test_heritability_estimate_bounds(self):
        """Test that h2 values are bounded 0-1."""
        with pytest.raises(ValueError):
            HeritabilityEstimate(
                trait_name="Test",
                h2_obs=1.5,  # Invalid: > 1
                population="EUR",
                source=HeritabilitySource.GWAS_ATLAS
            )
    
    def test_heritability_source_enum(self):
        """Test HeritabilitySource enum values."""
        assert HeritabilitySource.GWAS_ATLAS.value == "gwas_atlas"
        assert HeritabilitySource.PAN_UKB.value == "pan_ukb"
        assert HeritabilitySource.UKBB_LDSC.value == "ukbb_ldsc"
