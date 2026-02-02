import pytest
from unittest.mock import MagicMock

from src.server.core.state import search_progress
from src.server.modules.disease.pgs_search_service import fetch_pgs_and_pennprs_metadata


def test_fetch_metadata_caps_pgs_hydration(monkeypatch):
    """Ensure we do not hydrate an unbounded number of PGS IDs."""
    pgs_client = MagicMock()
    penn_client = MagicMock()

    pgs_client.search_scores.return_value = [{"id": f"PGS{i:06d}"} for i in range(100)]
    pgs_client.get_score_details.return_value = {"ok": True}
    pgs_client.get_score_performance.return_value = []

    penn_client.search_public_results.return_value = []

    pgs_results, details_map, perf_map, penn_results, total_found = fetch_pgs_and_pennprs_metadata(
        "Type 2 diabetes",
        pgs_client=pgs_client,
        pennprs_client=penn_client,
        max_pgs_models_fetch=10,
        max_workers=2,
    )

    assert total_found == 100
    assert len(pgs_results) == 10
    assert pgs_client.get_score_details.call_count == 10
    assert pgs_client.get_score_performance.call_count == 10
    assert len(details_map) == 10
    assert isinstance(perf_map, dict)
    assert penn_results == []


def test_fetch_metadata_updates_progress_total():
    """Ensure progress totals reflect capped PGS hydration work."""
    pgs_client = MagicMock()
    penn_client = MagicMock()

    pgs_client.search_scores.return_value = [{"id": f"PGS{i:06d}"} for i in range(25)]
    pgs_client.get_score_details.return_value = {}
    pgs_client.get_score_performance.return_value = []
    penn_client.search_public_results.return_value = [{"id": "GCST000001"}]

    request_id = "req-test-123"
    search_progress[request_id] = {"status": "starting", "total": 0, "fetched": 0, "current_action": ""}

    pgs_results, _, _, penn_results, _ = fetch_pgs_and_pennprs_metadata(
        "Asthma",
        pgs_client=pgs_client,
        pennprs_client=penn_client,
        request_id=request_id,
        max_pgs_models_fetch=5,
        max_workers=1,
    )

    assert len(pgs_results) == 5
    assert len(penn_results) == 1
    assert search_progress[request_id]["total"] == 6
