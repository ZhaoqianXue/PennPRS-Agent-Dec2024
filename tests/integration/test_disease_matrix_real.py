import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient


# This test suite is intentionally gated because it performs real online calls:
# - OpenAI (LLM calls)
# - External scientific APIs (PGS Catalog, Open Targets, ExPheWAS, etc.)
if os.getenv("RUN_REAL_DISEASE_MATRIX_TESTS") != "1":
    pytest.skip(
        "Skipping real disease-matrix tests (set RUN_REAL_DISEASE_MATRIX_TESTS=1 to enable).",
        allow_module_level=True,
    )


load_dotenv()


def _client() -> TestClient:
    # Import inside function so .env is loaded before app import.
    from src.server.main import app

    return TestClient(app)


# SOP disease categories (sop.md line 13):
# - cancer
# - mental diseases
# - neurodegenerative diseases
# - heart diseases
DISEASE_MATRIX: list[tuple[str, str]] = [
    # Cancer
    ("cancer", "Breast cancer"),
    ("cancer", "Prostate cancer"),
    ("cancer", "Colorectal cancer"),
    # Mental diseases
    ("mental", "Schizophrenia"),
    ("mental", "Major depressive disorder"),
    ("mental", "Bipolar disorder"),
    # Neurodegenerative diseases
    ("neurodegenerative", "Alzheimer's disease"),
    ("neurodegenerative", "Parkinson's disease"),
    ("neurodegenerative", "Amyotrophic lateral sclerosis"),
    # Heart diseases
    ("heart", "Coronary artery disease"),
    ("heart", "Atrial fibrillation"),
    ("heart", "Myocardial infarction"),
]


@pytest.mark.parametrize("category,trait", DISEASE_MATRIX)
def test_recommend_endpoint_real_disease_matrix(category: str, trait: str):
    """
    Per-disease smoke test against `/agent/recommend`.

    Assertions focus on:
    - endpoint stability (HTTP 200)
    - response schema presence (frontend contract)
    - follow-up training option required by SOP
    - no obvious secret leakage
    """
    client = _client()

    resp = client.post("/agent/recommend", json={"trait": trait})
    assert resp.status_code == 200, f"category={category} trait={trait} status={resp.status_code} body={resp.text}"

    data = resp.json()
    assert isinstance(data, dict)

    # Contract fields (shared/contracts/api.ts)
    assert "recommendation_type" in data
    assert "follow_up_options" in data

    assert data["recommendation_type"] in {
        "DIRECT_HIGH_QUALITY",
        "DIRECT_SUB_OPTIMAL",
        "CROSS_DISEASE",
        "NO_MATCH_FOUND",
    }

    follow_ups = data["follow_up_options"]
    assert isinstance(follow_ups, list)
    assert len(follow_ups) >= 1

    # SOP requires always offering training option.
    assert any(
        isinstance(opt, dict) and opt.get("action") == "TRIGGER_PENNPRS_CONFIG"
        for opt in follow_ups
    ), f"Missing training follow-up option for category={category} trait={trait}"

    # Basic secret leak check (should never show API keys in outputs).
    serialized = str(data)
    assert "sk-" not in serialized


@pytest.mark.parametrize(
    "category,trait",
    [
        ("cancer", "Breast cancer"),
        ("mental", "Schizophrenia"),
        ("neurodegenerative", "Alzheimer's disease"),
        ("heart", "Coronary artery disease"),
    ],
)
def test_invoke_endpoint_real_one_per_category(category: str, trait: str):
    """
    One-per-category smoke test against `/agent/invoke` (frontend primary chat endpoint).
    """
    client = _client()

    message = f"Find PRS models for {trait} and summarize the best options."
    resp = client.post("/agent/invoke", json={"message": message})
    assert resp.status_code == 200, f"category={category} trait={trait} status={resp.status_code} body={resp.text}"

    data = resp.json()
    assert isinstance(data, dict)
    assert "response" in data
    assert "full_state" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0

