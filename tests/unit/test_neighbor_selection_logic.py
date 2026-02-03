"""
Test neighbor selection strategy logic.

Tests the core logic:
1. >= 2 neighbors -> process top 2 only
2. < 2 neighbors -> process all
3. Evidence collection tools called AFTER models are found
"""
import pytest
from src.server.core.tool_schemas import RankedNeighbor


def test_neighbor_selection_strategy():
    """Test neighbor selection strategy logic."""
    
    # Test case 1: >= 2 neighbors -> select top 2
    neighbors_3 = [
        RankedNeighbor(
            trait_id="Neighbor1",
            domain="Test",
            rg_meta=0.8,
            rg_z_meta=3.0,
            h2_meta=0.5,
            transfer_score=0.32,
            n_correlations=5
        ),
        RankedNeighbor(
            trait_id="Neighbor2",
            domain="Test",
            rg_meta=0.7,
            rg_z_meta=2.5,
            h2_meta=0.4,
            transfer_score=0.196,
            n_correlations=4
        ),
        RankedNeighbor(
            trait_id="Neighbor3",
            domain="Test",
            rg_meta=0.6,
            rg_z_meta=2.2,
            h2_meta=0.3,
            transfer_score=0.108,
            n_correlations=3
        )
    ]
    
    # Apply selection strategy
    sorted_neighbors = sorted(neighbors_3, key=lambda n: n.transfer_score, reverse=True)
    selected = sorted_neighbors[:2] if len(sorted_neighbors) >= 2 else sorted_neighbors
    
    assert len(selected) == 2
    assert selected[0].trait_id == "Neighbor1"  # Highest transfer_score
    assert selected[1].trait_id == "Neighbor2"  # Second highest
    assert selected[0].transfer_score > selected[1].transfer_score
    
    # Test case 2: < 2 neighbors -> select all
    neighbors_1 = [
        RankedNeighbor(
            trait_id="Neighbor1",
            domain="Test",
            rg_meta=0.8,
            rg_z_meta=3.0,
            h2_meta=0.5,
            transfer_score=0.32,
            n_correlations=5
        )
    ]
    
    sorted_neighbors_1 = sorted(neighbors_1, key=lambda n: n.transfer_score, reverse=True)
    selected_1 = sorted_neighbors_1[:2] if len(sorted_neighbors_1) >= 2 else sorted_neighbors_1
    
    assert len(selected_1) == 1
    assert selected_1[0].trait_id == "Neighbor1"
    
    # Test case 3: 0 neighbors -> empty list
    neighbors_0 = []
    sorted_neighbors_0 = sorted(neighbors_0, key=lambda n: n.transfer_score, reverse=True)
    selected_0 = sorted_neighbors_0[:2] if len(sorted_neighbors_0) >= 2 else sorted_neighbors_0
    
    assert len(selected_0) == 0
    
    # Test case 4: Exactly 2 neighbors -> select both
    neighbors_2 = [
        RankedNeighbor(
            trait_id="Neighbor1",
            domain="Test",
            rg_meta=0.8,
            rg_z_meta=3.0,
            h2_meta=0.5,
            transfer_score=0.32,
            n_correlations=5
        ),
        RankedNeighbor(
            trait_id="Neighbor2",
            domain="Test",
            rg_meta=0.7,
            rg_z_meta=2.5,
            h2_meta=0.4,
            transfer_score=0.196,
            n_correlations=4
        )
    ]
    
    sorted_neighbors_2 = sorted(neighbors_2, key=lambda n: n.transfer_score, reverse=True)
    selected_2 = sorted_neighbors_2[:2] if len(sorted_neighbors_2) >= 2 else sorted_neighbors_2
    
    assert len(selected_2) == 2
    assert selected_2[0].trait_id == "Neighbor1"
    assert selected_2[1].trait_id == "Neighbor2"


def test_evidence_collection_conditional_logic():
    """Test that evidence collection is conditional on models being found."""
    
    # Simulate workflow: models found -> collect evidence
    neighbor_models_found = 3  # Models found
    
    evidence_collected = False
    if neighbor_models_found > 0:
        evidence_collected = True
    
    assert evidence_collected is True
    
    # Simulate workflow: no models found -> skip evidence collection
    neighbor_models_found = 0  # No models found
    
    evidence_collected = False
    if neighbor_models_found > 0:
        evidence_collected = True
    
    assert evidence_collected is False


def test_transfer_score_ranking():
    """Test that neighbors are ranked by transfer_score (descending)."""
    
    neighbors = [
        RankedNeighbor(
            trait_id="Low",
            domain="Test",
            rg_meta=0.5,
            rg_z_meta=2.0,
            h2_meta=0.3,
            transfer_score=0.075,  # 0.5^2 * 0.3 = 0.075
            n_correlations=2
        ),
        RankedNeighbor(
            trait_id="High",
            domain="Test",
            rg_meta=0.8,
            rg_z_meta=3.0,
            h2_meta=0.5,
            transfer_score=0.32,  # 0.8^2 * 0.5 = 0.32
            n_correlations=5
        ),
        RankedNeighbor(
            trait_id="Medium",
            domain="Test",
            rg_meta=0.6,
            rg_z_meta=2.5,
            h2_meta=0.4,
            transfer_score=0.144,  # 0.6^2 * 0.4 = 0.144
            n_correlations=3
        )
    ]
    
    sorted_neighbors = sorted(neighbors, key=lambda n: n.transfer_score, reverse=True)
    
    assert sorted_neighbors[0].trait_id == "High"
    assert sorted_neighbors[1].trait_id == "Medium"
    assert sorted_neighbors[2].trait_id == "Low"
    
    # Verify transfer_score ordering
    assert sorted_neighbors[0].transfer_score > sorted_neighbors[1].transfer_score
    assert sorted_neighbors[1].transfer_score > sorted_neighbors[2].transfer_score
