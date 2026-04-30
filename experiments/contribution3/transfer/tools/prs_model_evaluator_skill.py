"""c3-side re-export shim for the prs-model-evaluator skill loader.

The actual loader logic lives at
`src/server/core/tools/prs_model_evaluator_skill.py` (the central
loader), which exposes both the c2 view and the c3 view of the same
skill folder.

This c3-side shim keeps the existing import path
`experiments.contribution3.transfer.tools.prs_model_evaluator_skill`
working unchanged for `agent.py` and the c3 tests, while delegating
to the single source of truth.
"""
from __future__ import annotations

# Re-export the c3-view function under its historical name so existing
# c3 callers (`from experiments.contribution3.transfer.tools import
# prs_model_evaluator_skill`) keep working.
from src.server.core.tools.prs_model_evaluator_skill import (
    load_c3_view as prs_model_evaluator_skill,
    # Re-export everything c3 callers / tests reference.
    LEGACY_C2_CORPUS_PATH as SOURCE_CORPUS_PATH,  # historical alias for the c2 corpus path
    OVERRIDES_C3_DIR,
    PROJECT_ROOT,
    PgsModelEvaluatorResult,
    PgsSkillStage,
    REFERENCE_DIR,
    SKILL_DIR,
    SKILL_MD_PATH,
    STAGE_TO_OVERRIDE_FILES,
    STAGE_TO_REFERENCE_FILES,
    list_override_files,
    list_reference_files,
)

__all__ = [
    "PgsModelEvaluatorResult",
    "PgsSkillStage",
    "prs_model_evaluator_skill",  # = load_c3_view
    "STAGE_TO_REFERENCE_FILES",
    "STAGE_TO_OVERRIDE_FILES",
    "list_reference_files",
    "list_override_files",
    "SKILL_DIR",
    "SKILL_MD_PATH",
    "REFERENCE_DIR",
    "OVERRIDES_C3_DIR",
    "SOURCE_CORPUS_PATH",
    "PROJECT_ROOT",
]
