import os

import pytest
from dotenv import load_dotenv


# Real online LLM tests only.
if os.getenv("RUN_REAL_LLM_TESTS") != "1":
    pytest.skip(
        "Skipping real Step1 ablation tests (set RUN_REAL_LLM_TESTS=1 to enable).",
        allow_module_level=True,
    )

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    pytest.skip(
        "OPENAI_API_KEY not configured for real Step1 ablation tests.",
        allow_module_level=True,
    )

from src.server.core.agent_artifacts import stable_json_dumps
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
from src.server.modules.disease.recommendation_agent import _build_step1_chain


def _step1_context(domain_knowledge_payload):
    return {
        "target_trait": "Synthetic neurodegenerative disease",
        "direct_models": {
            "query_trait": "Synthetic neurodegenerative disease",
            "total_found": 2,
            "after_filter": 2,
            "top_models": [
                {
                    "id": "PGS_SYNTH_001",
                    "trait_reported": "Synthetic neurodegenerative disease",
                    "trait_efo": "EFO_SYNTH",
                    "method_name": "PRS-CS-auto",
                    "variants_number": 800000,
                    "ancestry_distribution": "DEV: EUR (100%) | EVAL: EUR (100%)",
                    "samples_training": "n=350000",
                    "performance_metrics": {"auc": 0.72, "r2": 0.10},
                    "phenotyping_reported": "Clinical diagnosis",
                    "covariates": "age, sex, PCs",
                },
                {
                    "id": "PGS_SYNTH_002",
                    "trait_reported": "Family history of synthetic disease",
                    "trait_efo": "EFO_SYNTH_PROXY",
                    "method_name": "C+T",
                    "variants_number": 150000,
                    "ancestry_distribution": "DEV: EUR (100%) | EVAL: EUR (100%)",
                    "samples_training": "n=120000",
                    "performance_metrics": {"auc": 0.75, "r2": 0.03},
                    "phenotyping_reported": "Family history proxy",
                    "covariates": "age, sex",
                },
            ],
        },
        "performance_landscape": {
            "total_models": 1000,
            "auc": {"min": 0.51, "max": 0.84, "median": 0.67, "p25": 0.61, "p75": 0.73, "missing_count": 0},
            "r2": {"min": 0.01, "max": 0.20, "median": 0.06, "p25": 0.03, "p75": 0.09, "missing_count": 0},
            "sample_size": {"min": 5000, "max": 900000, "median": 110000, "p25": 40000, "p75": 260000, "missing_count": 0},
            "variants": {"min": 50, "max": 1400000, "median": 230000, "p25": 40000, "p75": 580000, "missing_count": 0},
            "ancestry": {"EUR": 700, "EAS": 120, "AFR": 80},
            "training_development_cohorts": {"UKB": 300},
            "prs_methods": {"PRS-CS-auto": 200, "LDpred2-auto": 150, "C+T": 120},
        },
        "domain_knowledge": domain_knowledge_payload,
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


def test_step1_chain_real_with_structured_domain_knowledge():
    chain = _build_step1_chain(use_native_prompt=False)
    domain = prs_model_domain_knowledge(
        "clinical thresholds must-pass gates penalties method priors ancestry phenotype"
    ).model_dump()
    result = chain.invoke({"context_json": stable_json_dumps(_step1_context(domain))})

    assert result.outcome in {"DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"}
    assert result.confidence in {"High", "Moderate", "Low"}
    assert isinstance(result.rationale, str)
    assert len(result.rationale.strip()) > 0


def test_step1_chain_real_without_domain_knowledge_ablation():
    chain = _build_step1_chain(use_native_prompt=True)
    domain_disabled = {"query": "", "snippets": [], "source_type": "disabled_by_ablation"}
    result = chain.invoke({"context_json": stable_json_dumps(_step1_context(domain_disabled))})

    assert result.outcome in {"DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"}
    assert result.confidence in {"High", "Moderate", "Low"}
    assert isinstance(result.rationale, str)
    assert len(result.rationale.strip()) > 0
