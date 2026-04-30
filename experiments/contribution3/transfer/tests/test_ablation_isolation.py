from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.contribution3.transfer.agent import ToolAblationConfig
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    make_critic_prompt,
    make_gather_prompt,
    make_global_primary_prompt,
    make_judge_prompt,
    make_pgs_triage_prompt,
    make_pick_prompt,
    make_scout_prompt,
)
from experiments.contribution3.transfer.tools.cross_trait_domain_knowledge import (
    cross_trait_domain_knowledge,
)


NO_ALL_NO_SKILL_CFG = ToolAblationConfig(
    enable_h2=False,
    enable_ot=False,
    enable_gc_batch=False,
    enable_biology=False,
    enable_skill=False,
)

SKILL_ONLY_CFG = ToolAblationConfig(
    enable_h2=False,
    enable_ot=False,
    enable_gc_batch=False,
    enable_biology=False,
    enable_skill=True,
)

DISABLED_TOOL_TERMS = (
    "get_open_targets_overlap",
    "open targets",
    "shared_targets",
    "ot.",
    "gc.",
    "genetic correlation",
    "candidate h2",
    "h2_candidate",
    "heritability",
    "biology retrieval",
    "invoke_biology_retrieval",
)

DISABLED_SKILL_TERMS = (
    "cross_trait_guidance",
    "sealed skill",
    "domain knowledge",
    "skill_only_reference",
    "skill-only reference",
)


def _assert_no_disabled_tool_terms(text: str) -> None:
    lowered = text.lower()
    leaked = [term for term in DISABLED_TOOL_TERMS if term in lowered]
    assert leaked == []


def _assert_no_disabled_skill_terms(text: str) -> None:
    lowered = text.lower()
    leaked = [term for term in DISABLED_SKILL_TERMS if term in lowered]
    assert leaked == []


def test_no_all_tools_prompts_do_not_name_disabled_tools_or_skill() -> None:
    for factory in (
        make_scout_prompt,
        make_gather_prompt,
        make_judge_prompt,
        make_pick_prompt,
        make_pgs_triage_prompt,
        make_global_primary_prompt,
        make_critic_prompt,
    ):
        text = factory(NO_ALL_NO_SKILL_CFG)
        _assert_no_disabled_tool_terms(text)
        _assert_no_disabled_skill_terms(text)


def test_skill_only_prompts_do_not_name_disabled_tools() -> None:
    for factory in (
        make_scout_prompt,
        make_gather_prompt,
        make_judge_prompt,
        make_pick_prompt,
        make_pgs_triage_prompt,
        make_global_primary_prompt,
        make_critic_prompt,
    ):
        _assert_no_disabled_tool_terms(factory(SKILL_ONLY_CFG))


def test_skill_only_skill_text_filters_disabled_tool_terms() -> None:
    for stage in (
        "scout",
        "gather",
        "judge",
        "pick",
        "pgs_triage",
        "global_primary",
        "critic",
    ):
        result = cross_trait_domain_knowledge(stage=stage, query="target_trait: example", cfg=SKILL_ONLY_CFG)
        _assert_no_disabled_tool_terms(result.primary_section)


def test_no_all_tools_disables_skill_entirely() -> None:
    assert NO_ALL_NO_SKILL_CFG.enable_skill is False
    result = cross_trait_domain_knowledge(stage="judge", query="target_trait: example", cfg=NO_ALL_NO_SKILL_CFG)
    assert result.primary_section == ""
    assert result.full_document == ""
    assert result.snippets == []


def test_skill_only_keeps_skill_enabled() -> None:
    assert SKILL_ONLY_CFG.enable_skill is True
    result = cross_trait_domain_knowledge(stage="judge", query="target_trait: example", cfg=SKILL_ONLY_CFG)
    assert result.primary_section.strip()
