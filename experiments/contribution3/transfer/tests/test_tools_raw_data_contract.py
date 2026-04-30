"""P1 gate: every tool returns raw data only (no derived tiers/scores).

These tests do NOT hit the network for GC / OT (those are data-dependent
and slow); they use `describe_pgs_model` which reads from the on-disk
PGS Catalog cache (`data/pgs_catalog_cache/pgs_catalog_cache.pkl`).

The contract this file enforces (grep-assert on the JSON serialisation):

  Forbidden keys anywhere in any tool's output:
    tier, confidence_level, confidence_tier, weighted_overlap,
    genetic_support_present, archetype, utility_score,
    selection_priority_score, phenotype_fidelity_score, evidence_tags,
    primary_performance, selected_performance_record.

Run with:  pytest experiments/contribution3/transfer/tests/test_tools_raw_data_contract.py -q
"""
from __future__ import annotations

import json
import re

import pytest

from experiments.contribution3.transfer.common import (
    load_candidate_dossiers,
    target_dossiers_json,
)
from experiments.contribution3.transfer.tools import (
    describe_pgs_model,
)
from experiments.contribution3.transfer.tools.ot import get_open_targets_overlap

# Keys banned anywhere in tool output (recursively).
FORBIDDEN_OUTPUT_KEYS = {
    "tier",
    "confidence_level",
    "confidence_tier",
    "weighted_overlap",
    "genetic_support_present",
    "archetype",
    "utility_score",
    "selection_priority_score",
    "phenotype_fidelity_score",
    "evidence_tags",
    "primary_performance",
    "selected_performance_record",
    "transferability_prior_score",
    "cheap_rank_score",
}


def _collect_keys(obj, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(str(k))
            _collect_keys(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_keys(item, out)


def _assert_no_forbidden_keys(obj, tool_name: str) -> None:
    keys: set[str] = set()
    _collect_keys(obj, keys)
    overlap = keys & FORBIDDEN_OUTPUT_KEYS
    assert not overlap, (
        f"[{tool_name}] produced forbidden key(s) {overlap}. "
        f"All keys: {sorted(keys)[:50]}"
    )


@pytest.fixture(scope="module")
def dossiers():
    return load_candidate_dossiers(target_dossiers_json("unified"))


@pytest.fixture(scope="module")
def first_dossier(dossiers):
    return dossiers[0]


@pytest.fixture(scope="module")
def hand_picked_bundles(first_dossier):
    """Three arbitrary bundles from the dossier — structural test only."""
    assert len(first_dossier.candidates) >= 3
    return first_dossier.candidates[:3]


# ---------------------------------------------------------------------------
# describe_pgs_model — uses cached PGS Catalog if available; all records preserved
# ---------------------------------------------------------------------------

def test_describe_pgs_model_preserves_all_performance_records(hand_picked_bundles):
    """The LLM must see every performance record, not a pre-selected 'primary'."""
    # Pick the first PGS from the first bundle that has any candidate PGS IDs.
    for bundle in hand_picked_bundles:
        if bundle.candidate_pgs_ids:
            pgs_id = bundle.candidate_pgs_ids[0]
            break
    else:
        pytest.skip("No hand-picked bundle has any candidate_pgs_ids")

    result = describe_pgs_model(pgs_id=pgs_id)
    _assert_no_forbidden_keys(result, "describe_pgs_model")

    # Core raw fields must be present.
    assert result.get("pgs_id"), f"missing pgs_id for {pgs_id}"
    assert "performance_records" in result
    perf = result["performance_records"]
    assert isinstance(perf, list)
    # If the cache has this score, we expect >= 1 record; else empty is OK.
    # Either way, there must be no "selected" / "representative" shortcut.
    payload = json.dumps(result, default=str)
    assert "representative_performance" not in payload
    assert '"selected_performance_record"' not in payload


def test_describe_pgs_model_handles_invalid_id():
    result = describe_pgs_model(pgs_id="")
    assert result == {"error": "empty_pgs_id"}


# ---------------------------------------------------------------------------
# get_open_targets_overlap — structural contract
# ---------------------------------------------------------------------------

def test_ot_output_shape_with_empty_input():
    result = get_open_targets_overlap("", "")
    _assert_no_forbidden_keys(result, "get_open_targets_overlap")
    assert "shared_targets" in result
    assert "shared_pathways" in result
    assert "ancestors" in result
    assert "phenotypes" in result
    assert "therapeutic_areas" in result
    # Forbidden derived fields must not appear anywhere.
    payload = json.dumps(result, default=str)
    assert "weighted_overlap" not in payload
    assert "genetic_support_present" not in payload


# ---------------------------------------------------------------------------
# get_heritability — structural contract
# ---------------------------------------------------------------------------

def test_h2_output_is_unsorted_list_of_raw_records():
    from experiments.contribution3.transfer.tools.h2 import get_heritability

    result = get_heritability("", ancestry="EUR")
    assert isinstance(result, list)
    # Empty label returns an empty list by contract.
    assert result == []


def test_h2_output_returns_unpriorized_records():
    """With a likely-resolvable trait, every record must carry raw fields
    and NO pre-computed tier / priority field."""
    from experiments.contribution3.transfer.tools.h2 import get_heritability

    # Try a common trait string; the aggregator may or may not find rows
    # depending on local data availability. Either way, test contract holds.
    result = get_heritability("height", ancestry="EUR")
    assert isinstance(result, list)
    for record in result:
        _assert_no_forbidden_keys(record, "get_heritability")
        # Each record must expose raw fields, not a pre-picked "best" signal.
        keys = set(record.keys())
        forbidden = {"tier", "priority", "is_best", "selected", "rank"}
        assert not (keys & forbidden), f"forbidden priority/tier keys: {keys & forbidden}"
