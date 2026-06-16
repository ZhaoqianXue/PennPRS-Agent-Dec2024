from __future__ import annotations

from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    TargetTraitQuery,
    TraitBundle,
)
from experiments.contribution3.transfer.direct_baseline import (
    DirectNoHarnessSelection,
    SYSTEM_PROMPT,
    build_direct_recommendation_record,
    build_direct_result_record,
)


def _dossier() -> CandidateBundleDossier:
    return CandidateBundleDossier(
        target=TargetTraitQuery(
            target_id="T1",
            target_code="T1",
            target_label="Target disease",
            aliases=["target condition"],
        ),
        candidates=[
            TraitBundle(
                bundle_id="bundle_a",
                canonical_label="Source disease A",
                bundle_type="binary",
                aliases=["source a"],
                candidate_pgs_ids=["PGS000001"],
                n_models=1,
            ),
            TraitBundle(
                bundle_id="bundle_b",
                canonical_label="Source disease B",
                bundle_type="binary",
                aliases=["source b"],
                candidate_pgs_ids=["PGS000002"],
                n_models=1,
            ),
        ],
    )


def test_direct_baseline_normalizes_invalid_model_within_selected_bundle_only() -> None:
    """Strict no-harness baseline may normalize output format, not reasoning.

    If the LLM selects bundle_a but emits a model ID belonging to bundle_b, a
    harness could switch to bundle_b. The direct GPT-only baseline must not do
    that. It preserves the selected bundle and uses that bundle's first listed
    PGS ID so coverage is comparable without adding agent reasoning.
    """
    selection = DirectNoHarnessSelection(
        outcome="MATCHED",
        best_bundle_id="bundle_a",
        best_model_id="PGS000002",
        confidence="Moderate",
        rationale="Direct selection.",
    )

    result = build_direct_result_record(_dossier(), selection, condition="gpt-no-harness")
    decision = result["decision"]

    assert decision["outcome"] == "MATCHED"
    assert decision["best_bundle_id"] == "bundle_a"
    assert decision["best_model_id"] == "PGS000001"
    assert decision["candidate_pgs_ids"] == ["PGS000001"]
    assert decision["format_normalization_applied"] is True
    assert "does not belong" in decision["validation_error"]


def test_direct_baseline_valid_selection_writes_eval_compatible_recommendation() -> None:
    selection = DirectNoHarnessSelection(
        outcome="MATCHED",
        best_bundle_id="bundle_b",
        best_model_id="PGS000002",
        confidence="High",
        rationale="Best direct semantic match.",
    )

    result = build_direct_result_record(_dossier(), selection, condition="gpt-no-harness")
    recommendation = build_direct_recommendation_record(result, condition="gpt-no-harness")

    assert result["decision"]["outcome"] == "MATCHED"
    assert result["decision"]["best_cross_trait"] == "Source disease B"
    assert result["decision"]["candidate_pgs_ids"] == ["PGS000002"]
    assert recommendation["recommendation"]["matched_bundle_id"] == "bundle_b"
    assert recommendation["recommendation"]["decision"]["best_model_id"] == "PGS000002"


def test_direct_baseline_schema_is_forced_choice_not_abstention() -> None:
    """The GPT-only comparison baseline must produce one model per target.

    This keeps coverage comparable with the harness conditions while still
    removing agent harness engineering, tools, PRS Skills, retries, and staged
    evidence gathering.
    """
    schema_text = str(DirectNoHarnessSelection.model_json_schema())

    assert "NO_MATCH" not in schema_text
    assert "'type': 'null'" not in schema_text
    assert "NO_MATCH" not in SYSTEM_PROMPT
    assert "must select" in SYSTEM_PROMPT
