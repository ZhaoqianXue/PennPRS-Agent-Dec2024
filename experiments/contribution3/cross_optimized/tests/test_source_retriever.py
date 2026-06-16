from __future__ import annotations

from experiments.contribution3.cross_optimized.data_contract import CompactBundleRecord, TargetRecord
from experiments.contribution3.cross_optimized.retrieve.source_retriever import (
    _position_coverage_ids,
    retrieve_bundles,
)


def test_retriever_filters_self_like_and_non_evaluable_pgs() -> None:
    target = TargetRecord(
        target_id="X01",
        input_type="A",
        target_source="extend_trait",
        label="Example disease",
        aliases=["Example disease"],
    )
    bundles = [
        CompactBundleRecord(
            bundle_id="self",
            canonical_label="Example disease",
            bundle_type="binary",
            aliases=["Example disease"],
            candidate_pgs_ids=["PGS000001"],
            n_models=1,
        ),
        CompactBundleRecord(
            bundle_id="proxy",
            canonical_label="Example biomarker level",
            bundle_type="continuous",
            aliases=["Example biomarker"],
            candidate_pgs_ids=["PGS000002", "PGS000003"],
            n_models=2,
        ),
        CompactBundleRecord(
            bundle_id="broad",
            canonical_label="Broad source",
            bundle_type="binary",
            aliases=["Broad source"],
            candidate_pgs_ids=["PGS000004"],
            n_models=1,
        ),
    ]

    retrieved = retrieve_bundles(
        target=target,
        bundles=bundles,
        evaluable_pgs_ids={"PGS000002", "PGS000004"},
        fallback_binary=10,
        fallback_continuous=10,
    )

    by_id = {row.bundle.bundle_id: row for row in retrieved}
    assert "self" not in by_id
    assert by_id["proxy"].candidate_pgs_ids == ["PGS000002"]
    assert by_id["broad"].candidate_pgs_ids == ["PGS000004"]
    assert all("score" not in row.to_prompt_dict() for row in retrieved)


def test_retriever_promotes_breadth_floor_ahead_of_lexical_tail() -> None:
    target = TargetRecord(
        target_id="X01",
        input_type="A",
        target_source="extend_trait",
        label="Target condition",
        aliases=["Target condition"],
    )
    bundles = [
        CompactBundleRecord(
            bundle_id="lexical_head",
            canonical_label="Target condition related",
            bundle_type="binary",
            aliases=["Target condition related"],
            candidate_pgs_ids=["PGS000001"],
            n_models=1,
        ),
        CompactBundleRecord(
            bundle_id="lexical_tail",
            canonical_label="Target condition adjacent",
            bundle_type="binary",
            aliases=["Target condition adjacent"],
            candidate_pgs_ids=["PGS000002"],
            n_models=1,
        ),
        CompactBundleRecord(
            bundle_id="generalist",
            canonical_label="Broad quantitative source",
            bundle_type="continuous",
            aliases=["Broad quantitative source"],
            candidate_pgs_ids=["PGS000003", "PGS000004", "PGS000005"],
            n_models=3,
        ),
    ]

    retrieved = retrieve_bundles(
        target=target,
        bundles=bundles,
        evaluable_pgs_ids={"PGS000001", "PGS000002", "PGS000003", "PGS000004", "PGS000005"},
        lexical_front_cap=1,
        breadth_front_count=2,
        fallback_binary=10,
        fallback_continuous=10,
    )

    assert [row.bundle.bundle_id for row in retrieved[:3]] == [
        "lexical_head",
        "generalist",
        "lexical_tail",
    ]


def test_position_coverage_ids_samples_middle_dossier_regions() -> None:
    bundle_ids = [f"bundle_{idx:03d}" for idx in range(1, 601)]

    covered = _position_coverage_ids(bundle_ids, max_ids=40)

    assert "bundle_214" in covered
    assert "bundle_250" in covered
    assert "bundle_347" in covered
