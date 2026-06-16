"""Public within-phenotype PRS prompt surface for retained formal arms."""

from .selectors import (
    WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
    WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
    WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    build_within_stage1_user_instruction,
    build_within_topk_user_message,
    objective_block,
)

__all__ = [
    "WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT",
    "WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT",
    "WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT",
    "build_within_stage1_user_instruction",
    "build_within_topk_user_message",
    "objective_block",
]
