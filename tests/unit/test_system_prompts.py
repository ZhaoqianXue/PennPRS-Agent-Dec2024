import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_system_prompts_export_co_scientist_prompts():
    from src.server.core.system_prompts import (
        CO_SCIENTIST_STEP1_PROMPT,
        CO_SCIENTIST_STEP1_NATIVE_PROMPT,
        CO_SCIENTIST_REPORT_PROMPT
    )

    assert "Your task is to evaluate direct-match PRS candidates for the target trait" in CO_SCIENTIST_STEP1_PROMPT
    assert "This decision concerns direct-match assessment for the target trait only." in CO_SCIENTIST_STEP1_PROMPT
    assert CO_SCIENTIST_STEP1_NATIVE_PROMPT == CO_SCIENTIST_STEP1_PROMPT
    assert "If `domain_knowledge` is present, incorporate it as additional evidence." in CO_SCIENTIST_STEP1_PROMPT
    assert "do not use arbitrary or mechanical ID-based tie-breaking" in CO_SCIENTIST_STEP1_PROMPT
    assert "select the candidate supported by the broadest set of mutually consistent visible evidence" in CO_SCIENTIST_STEP1_PROMPT
    assert "do not let a single salient fact dominate the decision" in CO_SCIENTIST_STEP1_PROMPT
    assert "use the lexicographically smallest valid `PGS ID` as the deterministic tie-break" not in CO_SCIENTIST_STEP1_PROMPT
    assert "# Confidence Semantics" in CO_SCIENTIST_STEP1_PROMPT
    assert "Native GPT Constraint" not in CO_SCIENTIST_STEP1_PROMPT
    assert "Step 1 Evidence Priorities" not in CO_SCIENTIST_STEP1_PROMPT
    assert "Step 1: Direct Match Assessment" not in CO_SCIENTIST_STEP1_PROMPT
    assert "# Query Protocol" not in CO_SCIENTIST_STEP1_PROMPT
    assert "# Tool Orchestration Protocol" not in CO_SCIENTIST_STEP1_PROMPT
    assert "Output Schema" not in CO_SCIENTIST_STEP1_PROMPT
    assert "Output Schema" in CO_SCIENTIST_REPORT_PROMPT


def test_system_prompts_export_study_classifier_prompt():
    from src.server.core.system_prompts import STUDY_CLASSIFIER_SYSTEM_PROMPT

    assert "GWAS" in STUDY_CLASSIFIER_SYSTEM_PROMPT
