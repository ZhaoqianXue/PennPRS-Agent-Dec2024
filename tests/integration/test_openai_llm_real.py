import os

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# These tests are intentionally gated because they perform real online calls to OpenAI.
if os.getenv("RUN_REAL_LLM_TESTS") != "1":
    pytest.skip(
        "Skipping real OpenAI LLM tests (set RUN_REAL_LLM_TESTS=1 to enable).",
        allow_module_level=True,
    )


load_dotenv()


class PingResponse(BaseModel):
    """Structured response schema for a minimal OpenAI call."""

    answer: str = Field(description="Must be exactly 'pong'.")


def test_openai_basic_chat_completion():
    """
    Smoke test: verify we can make a real ChatCompletions call via LangChain.
    """
    from src.core.llm_config import get_llm

    llm = get_llm("default")
    msg = llm.invoke("Reply with exactly one word: pong")

    assert hasattr(msg, "content")
    assert msg.content.strip().lower() == "pong"


def test_openai_structured_output_json_schema():
    """
    Smoke test: verify strict JSON Schema structured output works end-to-end.
    """
    from src.core.llm_config import get_llm

    llm = get_llm("agentic_classifier")
    structured = llm.with_structured_output(PingResponse, method="json_schema", strict=True)

    result = structured.invoke("Return {\"answer\":\"pong\"} with answer exactly 'pong'.")
    assert isinstance(result, PingResponse)
    assert result.answer.strip().lower() == "pong"

