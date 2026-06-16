from __future__ import annotations

import pytest

from experiments.contribution3.cross_optimized.leak_guard import assert_no_leakage, scan_payload


def test_leak_guard_allows_metadata_payload() -> None:
    payload = {
        "target": {"target_id": "X01", "label": "Example trait"},
        "candidate_bundles": [
            {
                "bundle_id": "efo_1",
                "canonical_label": "Example source",
                "candidate_pgs_ids": ["PGS000001"],
                "retrieval_lanes": ["lexical_or_ontology"],
            }
        ],
    }
    assert scan_payload(payload) == []


def test_leak_guard_rejects_eval_fields() -> None:
    payload = {"target_id": "X01", "benchmark_top_model_id": "PGS999999"}
    with pytest.raises(ValueError, match="Potential Contribution1 AUC leakage"):
        assert_no_leakage(payload)


def test_leak_guard_rejects_eval_values() -> None:
    payload = {"note": "read prs_adjauc_matrix_binary_combined_rootcode.csv before choosing"}
    with pytest.raises(ValueError, match="Potential Contribution1 AUC leakage"):
        assert_no_leakage(payload)
