"""Contract for the unrestricted 7-section PGS schema builder.

The builder emits the same top-level sections for every PGS, but preserves all
multi-record source blocks instead of selecting one representative record.
"""

import pytest

from src.server.core.tools.pgs_single_record import build_single_record, load_rest_dump

SECTIONS = [
    "id",
    "predicted_trait",
    "development_method",
    "variants",
    "pgs_source",
    "source_of_variant_associations_gwas",
    "score_development_training",
    "performance_metrics",
]


def test_build_pgs003725_preserves_all_performance_records():
    """PGS003725 has 11 PGS Catalog performance records; none should be hidden."""
    dump = load_rest_dump()
    got = build_single_record("PGS003725")

    assert got is not None
    assert list(got.keys()) == SECTIONS
    assert isinstance(got["performance_metrics"], list)
    assert len(got["performance_metrics"]) == len(dump["PGS003725"]["performance"]) == 11
    assert got["performance_metrics"][0]["performance_id"] == "PPM018419"
    assert got["performance_metrics"][-1]["performance_id"] == "PPM023041"
    assert len(got["performance_metrics"][-1]["evaluation_samples"]) == 4


def test_seven_section_schema_shape():
    dump = load_rest_dump()
    rec = build_single_record("PGS003725")
    assert list(rec.keys()) == SECTIONS
    assert isinstance(rec["source_of_variant_associations_gwas"], list)
    assert isinstance(rec["score_development_training"], list)
    perf = rec["performance_metrics"][0]
    assert "metrics" not in perf
    assert set(perf.keys()) == {
        "performance_id",
        "phenotyping_reported",
        "covariates",
        "effect_sizes",
        "classification_metrics",
        "other_metrics",
        "evaluation_samples",
    }
    source_metrics = dump["PGS003725"]["performance"][0]["performance_metrics"]
    assert len(perf["effect_sizes"]) == len(source_metrics["effect_sizes"])
    assert perf["classification_metrics"] == source_metrics["class_acc"] == []
    assert perf["other_metrics"] == source_metrics["othermetrics"] == []
    assert {entry["metric_name"] for entry in perf["effect_sizes"]} == {"HR", "OR"}
    assert all("name_short" not in entry for entry in perf["effect_sizes"])
    assert all("name_long" not in entry for entry in perf["effect_sizes"])
    es = rec["performance_metrics"][0]["evaluation_samples"][0]
    assert set(es["sample_numbers"].keys()) == {"individuals", "cases", "controls"}


def test_metric_entries_keep_short_names_only():
    """Metric buckets should stay compact and avoid duplicating long labels."""
    rec = build_single_record("PGS000013")

    metric_entries = []
    for perf in rec["performance_metrics"]:
        metric_entries.extend(perf["effect_sizes"])
        metric_entries.extend(perf["classification_metrics"])
        metric_entries.extend(perf["other_metrics"])

    assert any(perf["classification_metrics"] for perf in rec["performance_metrics"])
    assert any(perf["other_metrics"] for perf in rec["performance_metrics"])
    assert metric_entries
    assert all("metric_name" in entry for entry in metric_entries)
    assert all("name_short" not in entry for entry in metric_entries)
    assert all("name_long" not in entry for entry in metric_entries)


def test_build_preserves_all_training_blocks_when_present():
    """A model with multiple training blocks should expose every block, not train[0]."""
    dump = load_rest_dump()
    rec = build_single_record("PGS005329")

    assert rec is not None
    assert len(dump["PGS005329"]["score"]["samples_training"]) > 1
    assert len(rec["score_development_training"]) == len(dump["PGS005329"]["score"]["samples_training"])


def test_unknown_pgs_returns_none():
    assert build_single_record("PGS000000000") is None


def test_builds_for_a_sample_of_diverse_candidates():
    """Spot-check that a metric-rich and a sparse candidate both build into the
    full schema (no crashes, all fixed sections present)."""
    dump = load_rest_dump()
    sample = [pid for pid in ("PGS000013", "PGS001306", "PGS003725") if pid in dump]
    assert sample, "expected at least one sample PGS present in the dump"
    for pid in sample:
        rec = build_single_record(pid)
        assert rec is not None and list(rec.keys()) == SECTIONS
        assert rec["development_method"]["method_name"] is not None
