import os
from unittest.mock import Mock, patch

import pytest

from src.server.core.tool_schemas import PGSModelSummary, PGSSearchResult
from src.server.modules.disease.recommendation_agent import Step1Decision, recommend_models


def _one_model_result() -> PGSSearchResult:
    model = PGSModelSummary(
        id="PGS000001",
        trait_reported="Test Trait",
        trait_efo="test trait",
        method_name="LDpred2",
        variants_number=1000,
        ancestry_distribution="GWAS: EUR (100%) | EVAL: EUR (100%)",
        publication={"title": "Test publication", "journal": "Test Journal"},
        date_release="2024-01-01",
        samples_training="n=100000",
        performance_metrics={"auc": 0.7, "r2": 0.05},
        phenotyping_reported="Test Trait",
        covariates="age, sex",
        training_development_cohorts=["UKB"],
        validation_sample_size="n=5000",
    )
    return PGSSearchResult(
        query_trait="Test Trait",
        total_found=1,
        after_filter=1,
        models=[model],
    )


@patch.dict(
    os.environ,
    {
        "PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE": "1",
        "PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION": "0",
        "PENNPRS_CONTRIB2_STRICT_LLM_ONLY": "1",
    },
    clear=False,
)
def test_strict_llm_only_raises_when_step1_chain_fails():
    with patch("src.server.modules.disease.recommendation_agent.PGSCatalogClient", return_value=Mock()), \
         patch("src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search", return_value=_one_model_result()), \
         patch("src.server.modules.disease.recommendation_agent._build_step1_chain") as mock_step1_chain:

        mock_step1_chain.return_value.invoke.side_effect = ValueError("step1 exploded")

        with pytest.raises(RuntimeError, match="Step 1 decision failed in strict LLM-only mode"):
            recommend_models("Test Trait")


@patch.dict(
    os.environ,
    {
        "PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE": "1",
        "PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION": "0",
        "PENNPRS_CONTRIB2_STRICT_LLM_ONLY": "1",
    },
    clear=False,
)
def test_strict_llm_only_raises_when_report_generation_fails():
    with patch("src.server.modules.disease.recommendation_agent.PGSCatalogClient", return_value=Mock()), \
         patch("src.server.modules.disease.recommendation_agent.prs_model_pgscatalog_search", return_value=_one_model_result()), \
         patch("src.server.modules.disease.recommendation_agent._build_step1_chain") as mock_step1_chain, \
         patch("src.server.modules.disease.recommendation_agent._build_report_chain") as mock_report_chain:

        mock_step1_chain.return_value.invoke.return_value = Step1Decision(
            outcome="DIRECT_HIGH_QUALITY",
            best_model_id="PGS000001",
            top_alternatives=[],
            confidence="Moderate",
            rationale="Choose the direct model.",
        )
        mock_report_chain.return_value.invoke.side_effect = ValueError("report exploded")

        with pytest.raises(RuntimeError, match="Report generation failed in strict LLM-only mode"):
            recommend_models("Test Trait")
