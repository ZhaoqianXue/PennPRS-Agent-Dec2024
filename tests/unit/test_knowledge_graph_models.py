"""
Unit Tests for Module 2: Knowledge Graph Models.
Tests the new Trait-Centric data models with Meta-Analysis fields.
"""
import pytest
from pydantic import ValidationError


def test_trait_node_has_meta_analyzed_fields():
    """Test that TraitNode model includes h2_meta, h2_se_meta, h2_z_meta, n_studies, studies."""
    from src.server.modules.knowledge_graph.models import TraitNode
    
    node = TraitNode(
        trait_id="Schizophrenia",
        domain="Psychiatric",
        chapter_level="Mental Disorders",
        h2_meta=0.45,
        h2_se_meta=0.03,
        h2_z_meta=15.0,
        n_studies=4,
        studies=[
            {"study_id": 9, "pmid": "21926974", "n": 21856, "snp_h2": 0.55, "snp_h2_se": 0.04}
        ]
    )
    
    assert node.trait_id == "Schizophrenia"
    assert node.h2_meta == 0.45
    assert node.h2_z_meta == 15.0
    assert node.n_studies == 4
    assert len(node.studies) == 1


def test_genetic_correlation_edge_has_meta_analyzed_fields():
    """Test that GeneticCorrelationEdgeMeta model includes rg_meta, rg_se_meta, rg_z_meta, rg_p_meta."""
    from src.server.modules.knowledge_graph.models import GeneticCorrelationEdgeMeta
    
    edge = GeneticCorrelationEdgeMeta(
        source_trait="Schizophrenia",
        target_trait="Bipolar disorder",
        rg_meta=0.68,
        rg_se_meta=0.04,
        rg_z_meta=17.0,
        rg_p_meta=1e-30,
        n_correlations=12,
        correlations=[
            {"source_study_id": 9, "target_study_id": 5, "rg": 0.65, "se": 0.05, "p": 0.001}
        ]
    )
    
    assert edge.source_trait == "Schizophrenia"
    assert edge.rg_meta == 0.68
    assert edge.rg_z_meta == 17.0
    assert edge.n_correlations == 12


def test_trait_centric_graph_result():
    """Test TraitCentricGraphResult container model."""
    from src.server.modules.knowledge_graph.models import (
        TraitNode, GeneticCorrelationEdgeMeta, TraitCentricGraphResult
    )
    
    node = TraitNode(trait_id="Test", n_studies=1, studies=[])
    edge = GeneticCorrelationEdgeMeta(
        source_trait="A", target_trait="B", rg_meta=0.5, n_correlations=1, correlations=[]
    )
    
    result = TraitCentricGraphResult(nodes=[node], edges=[edge])
    
    assert len(result.nodes) == 1
    assert len(result.edges) == 1
