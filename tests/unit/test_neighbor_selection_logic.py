"""
Test local-graph neighbor selection logic.
"""

from src.server.modules.disease.local_graph_reranker import select_neighbors_from_local_graph


def test_select_neighbors_prefers_rule_passing_candidates():
    ranked = [
        {"trait_id": "N1", "passes_rules": True, "local_graph_score": 0.9},
        {"trait_id": "N2", "passes_rules": True, "local_graph_score": 0.8},
        {"trait_id": "N3", "passes_rules": False, "local_graph_score": 0.99},
    ]
    selected = select_neighbors_from_local_graph(ranked, top_n=2)
    assert selected == ["N1", "N2"]


def test_select_neighbors_falls_back_when_no_rule_passing_candidate():
    ranked = [
        {"trait_id": "N1", "passes_rules": False, "local_graph_score": 0.9},
        {"trait_id": "N2", "passes_rules": False, "local_graph_score": 0.8},
    ]
    selected = select_neighbors_from_local_graph(ranked, top_n=1)
    assert selected == ["N1"]
