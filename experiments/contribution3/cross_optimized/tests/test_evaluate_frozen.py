from __future__ import annotations

from experiments.contribution3.cross_optimized.eval import evaluate_frozen


def test_evaluate_summary_reports_full_hit_grid(monkeypatch) -> None:
    def fake_ranking(target_id: str, target_source: str):
        ranked = [f"PGS{i:06d}" for i in range(1, 101)]
        auc = {pgs_id: 1.0 - idx / 1000 for idx, pgs_id in enumerate(ranked)}
        rank_map = {pgs_id: idx + 1 for idx, pgs_id in enumerate(ranked)}
        return ranked, rank_map, auc

    monkeypatch.setattr(evaluate_frozen, "full_matrix_ranking", fake_ranking)

    detail, summary = evaluate_frozen.evaluate_predictions(
        [{"target_id": "X01", "primary_pgs_id": "PGS000004"}],
        {"X01": {"target_source": "extend_trait", "input_type": "A", "target_label": "Target"}},
    )

    assert list(summary["hit_at"]) == [
        "top_0_5pct",
        "top_1_0pct",
        "top_2_5pct",
        "top_5_0pct",
        "top_10_0pct",
        "top_25_0pct",
    ]
    assert summary["hit_at"]["top_2_5pct"] == 0.0
    assert summary["hit_at"]["top_5_0pct"] == 1.0
    assert detail[0]["hit_top_25_0pct"] is True
