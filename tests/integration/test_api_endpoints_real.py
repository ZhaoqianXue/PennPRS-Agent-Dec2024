import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient


# These tests are intentionally gated because they perform real online calls:
# - OpenAI (LLM calls)
# - External scientific APIs (PGS Catalog, Open Targets, etc.)
if os.getenv("RUN_REAL_E2E_TESTS") != "1":
    pytest.skip(
        "Skipping real endpoint tests (set RUN_REAL_E2E_TESTS=1 to enable).",
        allow_module_level=True,
    )


load_dotenv()


def _client() -> TestClient:
    # Import inside function so .env is loaded before app import.
    from src.server.main import app

    return TestClient(app)


def test_root_healthcheck():
    client = _client()
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "message" in data


def test_classify_trait_endpoint_real_openai():
    client = _client()

    payloads = [
        {
            "trait_name": "Type 2 diabetes",
            "sample_info": "100,000 European ancestry individuals",
        },
        {
            "trait_name": "LDL cholesterol levels",
            "sample_info": "300,000 European ancestry individuals",
        },
        {
            "trait_name": "Alzheimer's disease or family history",
            "sample_info": "321,047 European ancestry individuals",
        },
    ]

    for p in payloads:
        resp = client.post("/agent/classify_trait", json=p)
        assert resp.status_code == 200
        data = resp.json()

        assert set(data.keys()) == {"trait_type", "ancestry", "confidence", "reasoning"}
        assert data["trait_type"] in {"Binary", "Continuous"}
        assert data["ancestry"] in {"EUR", "AFR", "EAS", "SAS", "AMR"}
        assert data["confidence"] in {"high", "medium", "low"}
        assert isinstance(data["reasoning"], str)
        assert len(data["reasoning"]) > 0


def test_recommend_models_endpoint_smoke():
    client = _client()

    resp = client.post("/agent/recommend", json={"trait": "Alzheimer's disease"})
    assert resp.status_code == 200
    data = resp.json()

    # Schema smoke checks (do not assert exact content to avoid flaky failures).
    assert isinstance(data, dict)
    assert "recommendation_type" in data
    assert "follow_up_options" in data
    assert isinstance(data["follow_up_options"], list)
    assert len(data["follow_up_options"]) >= 1

