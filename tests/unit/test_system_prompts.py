import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_system_prompts_export_co_scientist_prompts():
    from src.server.core.system_prompts import (
        CO_SCIENTIST_STEP1_PROMPT,
        CO_SCIENTIST_REPORT_PROMPT
    )

    assert "Step 1: Direct Match Assessment" in CO_SCIENTIST_STEP1_PROMPT
    assert "Output Schema" not in CO_SCIENTIST_STEP1_PROMPT
    assert "Output Schema" in CO_SCIENTIST_REPORT_PROMPT


def test_system_prompts_export_study_classifier_prompt():
    from src.server.core.system_prompts import STUDY_CLASSIFIER_SYSTEM_PROMPT

    assert "GWAS" in STUDY_CLASSIFIER_SYSTEM_PROMPT
