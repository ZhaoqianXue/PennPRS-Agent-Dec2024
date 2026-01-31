"""
Unit Tests for Edge Aggregator.
Tests grouping Study-pair correlations by Trait-pair and applying meta-analysis for rg.
"""
import pytest
import pandas as pd


def test_aggregate_edges_by_trait_pair():
    """Test aggregating multiple study-pair edges into one trait-pair edge."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    # Create mock GC dataframe: 2 study-pairs between same trait-pair
    gc_data = pd.DataFrame({
        "id1": [9, 10],   # Both map to Trait A
        "id2": [5, 5],    # Both map to Trait B
        "rg": [0.5, 0.55],
        "se": [0.1, 0.08],
        "z": [5.0, 6.875],
        "p": [1e-6, 1e-10]
    })
    
    # ID to Trait mapping
    id_to_trait = {9: "Trait A", 10: "Trait A", 5: "Trait B"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    result = aggregator.get_aggregated_edge("Trait A", "Trait B")
    
    assert result is not None
    assert result.source_trait == "Trait A"
    assert result.target_trait == "Trait B"
    assert result.n_correlations == 2
    assert len(result.correlations) == 2
    assert result.rg_meta is not None  # Meta-analyzed value
    assert result.rg_z_meta is not None


def test_aggregate_edges_reverse_lookup():
    """Test that edge lookup works regardless of source/target order."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [1],
        "id2": [2],
        "rg": [0.6],
        "se": [0.1],
        "z": [6.0],
        "p": [1e-8]
    })
    
    id_to_trait = {1: "Trait A", 2: "Trait B"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    # Lookup in both directions should return the same edge
    result_ab = aggregator.get_aggregated_edge("Trait A", "Trait B")
    result_ba = aggregator.get_aggregated_edge("Trait B", "Trait A")
    
    assert result_ab is not None
    assert result_ba is not None
    assert result_ab.rg_meta == result_ba.rg_meta


def test_aggregate_edges_excludes_self_loops():
    """Test that edges between studies of the same trait are excluded."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [9, 10],
        "id2": [10, 11],  # id 9,10,11 all map to same trait
        "rg": [0.9, 0.95],
        "se": [0.02, 0.03],
        "z": [45, 31],
        "p": [0, 0]
    })
    
    id_to_trait = {9: "Trait A", 10: "Trait A", 11: "Trait A"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    # Should return None (self-loop)
    result = aggregator.get_aggregated_edge("Trait A", "Trait A")
    
    assert result is None


def test_get_neighbors_for_trait():
    """Test getting all neighbor traits for a given trait."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [1, 1, 2],
        "id2": [2, 3, 3],
        "rg": [0.5, 0.6, 0.7],
        "se": [0.1, 0.1, 0.1],
        "z": [5, 6, 7],
        "p": [1e-5, 1e-7, 1e-9]
    })
    
    id_to_trait = {1: "Trait A", 2: "Trait B", 3: "Trait C"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    neighbors = aggregator.get_neighbor_traits("Trait A")
    
    assert len(neighbors) == 2
    assert "Trait B" in neighbors
    assert "Trait C" in neighbors


def test_edge_not_found():
    """Test that None is returned for non-existent edge."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [1],
        "id2": [2],
        "rg": [0.5],
        "se": [0.1],
        "z": [5],
        "p": [1e-5]
    })
    
    id_to_trait = {1: "Trait A", 2: "Trait B", 3: "Trait C"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    result = aggregator.get_aggregated_edge("Trait A", "Trait C")
    
    assert result is None


def test_edge_with_unmapped_ids():
    """Test that edges with unmapped IDs are skipped."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [1, 999],  # 999 not in mapping
        "id2": [2, 2],
        "rg": [0.5, 0.6],
        "se": [0.1, 0.1],
        "z": [5, 6],
        "p": [1e-5, 1e-6]
    })
    
    id_to_trait = {1: "Trait A", 2: "Trait B"}  # 999 not mapped
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    result = aggregator.get_aggregated_edge("Trait A", "Trait B")
    
    # Should only include the first edge (999 is unmapped)
    assert result is not None
    assert result.n_correlations == 1
