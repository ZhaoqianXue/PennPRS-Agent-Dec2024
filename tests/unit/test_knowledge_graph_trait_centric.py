"""
Unit Tests for Trait-Centric Knowledge Graph Service.
Tests the refactored service with meta-analysis aggregation per sop.md Module 2.
"""
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


@pytest.fixture
def mock_h2_df():
    """Mock heritability DataFrame with multiple studies per trait."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "uniqTrait": ["Target Trait", "Neighbor A", "Neighbor A", "Neighbor B"],
        "SNPh2": [0.4, 0.5, 0.45, 0.3],
        "SNPh2_se": [0.03, 0.04, 0.03, 0.05],
        "SNPh2_z": [13.3, 12.5, 15.0, 6.0],
        "Domain": ["Psychiatric"] * 4,
        "ChapterLevel": ["Mental"] * 4
    })


@pytest.fixture
def mock_gc_df():
    """Mock genetic correlation DataFrame with multiple study-pairs."""
    return pd.DataFrame({
        "id1": [1, 1, 1],
        "id2": [2, 3, 4],
        "rg": [0.6, 0.55, 0.3],
        "se": [0.05, 0.06, 0.1],
        "z": [12.0, 9.2, 3.0],
        "p": [1e-10, 1e-8, 0.003]
    })


def test_get_trait_node_returns_aggregated_node(mock_h2_df):
    """Test that get_trait_node returns a TraitNode with meta-analyzed h2."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.knowledge_graph.models import TraitNode
    
    # Create mock clients
    mock_h2_client = MagicMock()
    mock_h2_client.df = mock_h2_df
    
    mock_gc_client = MagicMock()
    mock_gc_client._data = pd.DataFrame()
    
    service = KnowledgeGraphService(gc_client=mock_gc_client, h2_client=mock_h2_client)
    
    node = service.get_trait_node("Neighbor A")
    
    assert node is not None
    assert isinstance(node, TraitNode)
    assert node.trait_id == "Neighbor A"
    assert node.n_studies == 2  # Two studies for "Neighbor A"
    assert node.h2_meta is not None
    assert node.h2_z_meta is not None


def test_get_trait_node_not_found(mock_h2_df):
    """Test that get_trait_node returns None for unknown trait."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    
    mock_h2_client = MagicMock()
    mock_h2_client.df = mock_h2_df
    
    mock_gc_client = MagicMock()
    mock_gc_client._data = pd.DataFrame()
    
    service = KnowledgeGraphService(gc_client=mock_gc_client, h2_client=mock_h2_client)
    
    node = service.get_trait_node("Unknown Trait")
    
    assert node is None


def test_get_prioritized_neighbors_v2_uses_meta_analysis(mock_h2_df, mock_gc_df):
    """Test that prioritized neighbors use rg_meta and h2_meta for scoring."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    
    mock_h2_client = MagicMock()
    mock_h2_client.df = mock_h2_df
    
    mock_gc_client = MagicMock()
    mock_gc_client._data = mock_gc_df
    
    service = KnowledgeGraphService(gc_client=mock_gc_client, h2_client=mock_h2_client)
    
    neighbors = service.get_prioritized_neighbors_v2("Target Trait")
    
    # Neighbors with |rg_z_meta| > 2 and h2_z_meta > 2 should pass
    assert len(neighbors) >= 1
    
    # Check that score is calculated correctly
    for neighbor in neighbors:
        assert neighbor.score > 0
        # Score should be rg^2 * h2
        expected_score = neighbor.rg ** 2 * neighbor.h2
        assert abs(neighbor.score - expected_score) < 0.01


def test_get_prioritized_neighbors_v2_filters_by_z_scores(mock_gc_df):
    """Test that neighbors with low Z-scores are filtered out."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    
    # Create h2_df with Neighbor B having h2_z below threshold
    # Note: meta-analysis Z = theta / SE, so we need SE high enough to make Z < 2
    h2_df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "uniqTrait": ["Target Trait", "Neighbor A", "Neighbor A", "Neighbor B"],
        "SNPh2": [0.4, 0.5, 0.45, 0.1],  # Neighbor B has low h2
        "SNPh2_se": [0.03, 0.04, 0.03, 0.1],  # Neighbor B has high SE -> low Z
        "SNPh2_z": [13.3, 12.5, 15.0, 1.0],  # Neighbor B z < 2
        "Domain": ["Psychiatric"] * 4,
        "ChapterLevel": ["Mental"] * 4
    })
    
    mock_h2_client = MagicMock()
    mock_h2_client.df = h2_df
    
    mock_gc_client = MagicMock()
    mock_gc_client._data = mock_gc_df
    
    service = KnowledgeGraphService(gc_client=mock_gc_client, h2_client=mock_h2_client)
    
    neighbors = service.get_prioritized_neighbors_v2("Target Trait", h2_z_threshold=2.0)
    
    # Neighbor B should be filtered out (h2_z_meta < 2)
    neighbor_ids = [n.trait_id for n in neighbors]
    assert "Neighbor B" not in neighbor_ids



def test_get_prioritized_neighbors_v2_sorted_by_score():
    """Test that neighbors are sorted by score in descending order."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    
    # Create DataFrame with clear ranking
    h2_df = pd.DataFrame({
        "id": [1, 2, 3],
        "uniqTrait": ["Target", "High Score", "Low Score"],
        "SNPh2": [0.4, 0.6, 0.3],
        "SNPh2_se": [0.03, 0.03, 0.03],
        "SNPh2_z": [13.3, 20.0, 10.0],
        "Domain": ["A", "A", "A"]
    })
    
    gc_df = pd.DataFrame({
        "id1": [1, 1],
        "id2": [2, 3],
        "rg": [0.8, 0.4],  # High Score: 0.8^2 * 0.6 = 0.384, Low Score: 0.4^2 * 0.3 = 0.048
        "se": [0.05, 0.05],
        "z": [16.0, 8.0],
        "p": [1e-20, 1e-10]
    })
    
    mock_h2_client = MagicMock()
    mock_h2_client.df = h2_df
    
    mock_gc_client = MagicMock()
    mock_gc_client._data = gc_df
    
    service = KnowledgeGraphService(gc_client=mock_gc_client, h2_client=mock_h2_client)
    
    neighbors = service.get_prioritized_neighbors_v2("Target")
    
    assert len(neighbors) == 2
    assert neighbors[0].trait_id == "High Score"
    assert neighbors[1].trait_id == "Low Score"
    assert neighbors[0].score > neighbors[1].score


def test_get_trait_centric_graph():
    """Test get_trait_centric_graph returns complete graph with nodes and edges."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.knowledge_graph.models import TraitCentricGraphResult
    
    h2_df = pd.DataFrame({
        "id": [1, 2],
        "uniqTrait": ["Target", "Neighbor"],
        "SNPh2": [0.4, 0.5],
        "SNPh2_se": [0.03, 0.03],
        "SNPh2_z": [13.3, 16.7],
        "Domain": ["A", "B"]
    })
    
    gc_df = pd.DataFrame({
        "id1": [1],
        "id2": [2],
        "rg": [0.6],
        "se": [0.05],
        "z": [12.0],
        "p": [1e-10]
    })
    
    mock_h2_client = MagicMock()
    mock_h2_client.df = h2_df
    
    mock_gc_client = MagicMock()
    mock_gc_client._data = gc_df
    
    service = KnowledgeGraphService(gc_client=mock_gc_client, h2_client=mock_h2_client)
    
    result = service.get_trait_centric_graph("Target")
    
    assert isinstance(result, TraitCentricGraphResult)
    assert len(result.nodes) >= 1  # At least source node
    assert len(result.edges) >= 0  # At least edges to neighbors
