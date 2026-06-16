from __future__ import annotations

from experiments.contribution2.recommendation.direct_baseline_sufficiency import (
    adjudicate_direct_baseline_sufficiency,
)
from src.server.modules.pennprs_agent import service


def test_cached_transfer_missing_artifact_returns_warning(monkeypatch, tmp_path):
    missing_result = tmp_path / "missing_results.json"
    missing_eval = tmp_path / "missing_eval_summary.json"
    monkeypatch.setattr(service, "C3_RESULT_PATH", missing_result)
    monkeypatch.setattr(service, "C3_EVAL_SUMMARY_PATH", missing_eval)

    warnings: list[str] = []
    errors: list[str] = []
    artifacts: list[dict[str, str]] = []

    result = service._load_cached_transfer(
        "bipolar disorder",
        warnings,
        errors,
        artifacts,
    )

    assert result is None
    assert errors == []
    assert len(artifacts) == 2
    assert "Cached transfer artifact unavailable" in warnings[0]
    assert str(missing_result) in warnings[0]


def test_cached_recommendation_survives_missing_transfer_artifact(monkeypatch, tmp_path):
    missing_result = tmp_path / "missing_results.json"
    monkeypatch.setattr(service, "C3_RESULT_PATH", missing_result)

    response = service.recommend("bipolar disorder", mode="cached")

    assert response.errors == []
    assert response.final_recommendation.recommendation_source == "same_trait"
    assert any(
        "Cached transfer artifact unavailable" in warning
        for warning in response.warnings
    )


def test_cached_same_trait_assessment_is_binary_and_production_visible():
    response = service.recommend("breast carcinoma", mode="cached")

    assessment = response.same_trait_quality_assessment.model_dump()
    assert set(assessment) == {"accept_direct_baseline", "rationale"}
    assert assessment["accept_direct_baseline"] is True

    evidence = response.same_trait_result.get("selected_model_evidence") or {}
    assert "cached_benchmark_rank" not in evidence
    assert "cached_benchmark_auc" not in evidence
    assert "_sufficiency_context" not in response.same_trait_result


def test_transfer_recommendation_exposes_source_trait_model_previews():
    response = service.recommend("late-onset Alzheimer's disease", mode="cached")

    if not service.C3_RESULT_PATH.exists():
        assert response.final_recommendation.recommendation_source == "same_trait"
        assert response.transfer_result is None
        assert any("Cached transfer artifact unavailable" in warning for warning in response.warnings)
        return

    transfer = response.transfer_result or {}
    previews = transfer.get("model_previews") or []

    assert response.final_recommendation.recommendation_source == "cross_trait_transfer"
    assert transfer.get("source_trait") == "dementia"
    assert previews
    assert previews[0]["id"] == "PGS000945"
    assert "dementia" in previews[0]["trait"].lower()


def test_sufficiency_gate_respects_c2_retained_contract():
    direct_high = adjudicate_direct_baseline_sufficiency(
        target_trait="example trait",
        same_trait_result={
            "status": "found",
            "execution_mode": "live_one_row_production_runner",
            "match_kind": "canonical_exact",
            "recommendation_type": "DIRECT_HIGH_QUALITY",
            "confidence": "Moderate",
            "pgs_id": "PGS000001",
        },
        use_llm=False,
    )
    direct_suboptimal = adjudicate_direct_baseline_sufficiency(
        target_trait="example trait",
        same_trait_result={
            "status": "found",
            "execution_mode": "live_one_row_production_runner",
            "match_kind": "canonical_exact",
            "recommendation_type": "DIRECT_SUB_OPTIMAL",
            "confidence": "Moderate",
            "pgs_id": "PGS000002",
        },
        use_llm=False,
    )

    assert direct_high.accept_direct_baseline is True
    assert direct_suboptimal.accept_direct_baseline is False


def test_direct_only_moderate_baseline_escalates():
    decision = adjudicate_direct_baseline_sufficiency(
        target_trait="example trait",
        same_trait_result={
            "status": "found",
            "execution_mode": "live_direct_only_same_trait",
            "match_kind": "live_direct_only",
            "recommendation_type": "DIRECT_HIGH_QUALITY",
            "confidence": "Moderate",
            "pgs_id": "PGS000003",
        },
        use_llm=False,
    )

    assert decision.accept_direct_baseline is False
