from src.server.core.tool_schemas import RankedNeighbor
from src.server.modules.disease.local_graph_reranker import (
    rerank_neighbors_with_local_graph,
    select_neighbors_from_local_graph,
)


def test_local_graph_reranker_promotes_pgs_supported_neighbors():
    neighbors = [
        RankedNeighbor(
            trait_id="HighTransferNoPGS",
            domain="Test",
            rg_meta=0.8,
            rg_z_meta=4.0,
            h2_meta=0.6,
            transfer_score=0.30,
            n_correlations=5,
        ),
        RankedNeighbor(
            trait_id="ModerateTransferWithPGS",
            domain="Test",
            rg_meta=0.5,
            rg_z_meta=3.2,
            h2_meta=0.4,
            transfer_score=0.12,
            n_correlations=4,
        ),
    ]

    ranked = rerank_neighbors_with_local_graph(
        target_trait="Alzheimer disease",
        neighbors=neighbors,
        pgs_hit_counts={
            "HighTransferNoPGS": 0,
            "ModerateTransferWithPGS": 8,
        },
        similarity_fn=lambda _a, _b: 0.5,
        min_pgs_hits=1,
    )

    assert ranked[0]["trait_id"] == "ModerateTransferWithPGS"
    assert ranked[0]["passes_rules"] is True
    assert ranked[1]["passes_rules"] is False
    assert "insufficient_pgs_hits" in ranked[1]["rule_failures"]


def test_select_neighbors_uses_rule_passing_then_fallback():
    ranked_candidates = [
        {"trait_id": "A", "passes_rules": False},
        {"trait_id": "B", "passes_rules": True},
        {"trait_id": "C", "passes_rules": True},
    ]
    selected = select_neighbors_from_local_graph(ranked_candidates, top_n=2)
    assert selected == ["B", "C"]

    selected_fallback = select_neighbors_from_local_graph(
        [{"trait_id": "X", "passes_rules": False}, {"trait_id": "Y", "passes_rules": False}],
        top_n=1,
    )
    assert selected_fallback == ["X"]
