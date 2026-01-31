"""
Unit Tests for Trait Aggregator.
Tests grouping Studies by uniqTrait and applying meta-analysis for h2.
"""
import pytest
import pandas as pd


def test_aggregate_heritability_by_trait():
    """Test aggregating multiple studies for the same trait."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    # Create mock heritability dataframe with 3 studies for "Schizophrenia"
    h2_data = pd.DataFrame({
        "id": [9, 10, 11],
        "uniqTrait": ["Schizophrenia", "Schizophrenia", "Schizophrenia"],
        "Domain": ["Psychiatric", "Psychiatric", "Psychiatric"],
        "ChapterLevel": ["Mental", "Mental", "Mental"],
        "PMID": ["111", "222", "333"],
        "N": [10000, 20000, 30000],
        "SNPh2": [0.5, 0.45, 0.48],
        "SNPh2_se": [0.05, 0.04, 0.03],
        "SNPh2_z": [10.0, 11.25, 16.0]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    result = aggregator.get_trait_node("Schizophrenia")
    
    assert result is not None
    assert result.trait_id == "Schizophrenia"
    assert result.n_studies == 3
    assert len(result.studies) == 3
    assert result.h2_meta is not None
    assert result.h2_z_meta is not None
    assert result.domain == "Psychiatric"


def test_aggregate_heritability_trait_not_found():
    """Test that None is returned for unknown trait."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    h2_data = pd.DataFrame({
        "id": [1],
        "uniqTrait": ["Diabetes"],
        "SNPh2": [0.3],
        "SNPh2_se": [0.05]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    result = aggregator.get_trait_node("Unknown Trait")
    
    assert result is None


def test_get_all_trait_ids():
    """Test getting list of all unique trait IDs."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    h2_data = pd.DataFrame({
        "id": [1, 2, 3],
        "uniqTrait": ["Trait A", "Trait A", "Trait B"],
        "SNPh2": [0.3, 0.4, 0.5],
        "SNPh2_se": [0.05, 0.06, 0.07]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    traits = aggregator.get_all_trait_ids()
    
    assert len(traits) == 2
    assert "Trait A" in traits
    assert "Trait B" in traits


def test_get_study_ids_for_trait():
    """Test getting list of study IDs for a given trait."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    h2_data = pd.DataFrame({
        "id": [1, 2, 3],
        "uniqTrait": ["Trait A", "Trait A", "Trait B"],
        "SNPh2": [0.3, 0.4, 0.5],
        "SNPh2_se": [0.05, 0.06, 0.07]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    study_ids = aggregator.get_study_ids_for_trait("Trait A")
    
    assert len(study_ids) == 2
    assert 1 in study_ids
    assert 2 in study_ids


def test_build_id_to_trait_map():
    """Test building study ID to trait name mapping."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    h2_data = pd.DataFrame({
        "id": [1, 2, 3],
        "uniqTrait": ["Trait A", "Trait A", "Trait B"],
        "SNPh2": [0.3, 0.4, 0.5],
        "SNPh2_se": [0.05, 0.06, 0.07]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    id_map = aggregator.get_id_to_trait_map()
    
    assert id_map[1] == "Trait A"
    assert id_map[2] == "Trait A"
    assert id_map[3] == "Trait B"


def test_trait_aggregator_handles_missing_columns():
    """Test graceful handling of missing optional columns."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    # Minimal dataframe without Domain, ChapterLevel, etc.
    h2_data = pd.DataFrame({
        "id": [1],
        "uniqTrait": ["Trait A"],
        "SNPh2": [0.3],
        "SNPh2_se": [0.05]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    result = aggregator.get_trait_node("Trait A")
    
    assert result is not None
    assert result.trait_id == "Trait A"
    assert result.domain is None  # Missing column handled gracefully
