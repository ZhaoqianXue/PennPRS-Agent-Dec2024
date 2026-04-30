"""Cached LangChain structured-output chain builders for the 7 stages.

Chains are now cfg-aware — each `make_*_chain(cfg)` returns a chain
whose system prompt is rendered with tool-specific sections removed
when the corresponding `cfg.enable_*` flag is False. This is essential
for strict ablation studies: when a tool is disabled, the LLM must
neither see it in the "Tools available" list nor see the corresponding
field in any digest description, otherwise prompt-level priming lets
the LLM construct hypothetical signals from absent data.

Chain caching is keyed on the cfg's hashable signature so that running
the same cfg multiple times reuses the same compiled chain. Switching
ablations within one process spins up a new chain on first use and
caches it for reuse.

Skill text is delivered only through the JSON `cross_trait_guidance`
field in `context_json`. Prompt files contain procedural instructions;
empirical heuristics live in the sealed skill file.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from experiments.contribution3.transfer.prompts.transfer_prompt import (
    make_critic_prompt,
    make_gather_prompt,
    make_global_primary_prompt,
    make_judge_prompt,
    make_pgs_triage_prompt,
    make_pick_prompt,
    make_scout_prompt,
)
from experiments.contribution3.transfer.schemas import (
    BundleRanking,
    CritiqueDecision,
    GlobalPrimaryDecision,
    ModelFrontier,
    PGSTriageSelection,
    RoundDirective,
    ScoutDirective,
)
from src.server.core.llm_config import get_llm


def _build_chain(system_prompt: str, output_model):
    """Build a structured-output chain with literal system prompt.

    We avoid LangChain's variable substitution on the system string
    (prompts contain documentation-style `{field_name}` tokens that are
    not template variables). The human message uses `{context_json}`
    which IS the only templated variable.
    """
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            HumanMessagePromptTemplate.from_template("{context_json}"),
        ]
    )
    return prompt | llm.with_structured_output(output_model, method="function_calling")


def _build_chain_with_prefix(base_system_prompt: str, output_model):
    """Build a chain whose system message has a per-call prefix injected."""
    llm = get_llm("disease_workflow")
    system_template = (
        "{{ system_prefix }}\n\n"
        "---\n\n"
        + base_system_prompt
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                system_template, template_format="jinja2"
            ),
            HumanMessagePromptTemplate.from_template(
                "{{ context_json }}", template_format="jinja2"
            ),
        ]
    )
    return prompt | llm.with_structured_output(output_model, method="function_calling")


# ---------------------------------------------------------------------------
# CFG-AWARE CHAIN FACTORIES
# ---------------------------------------------------------------------------
# Each factory accepts a `ToolAblationConfig` and returns the chain whose
# system prompt has tool-specific sections stripped when the corresponding
# enable_* flag is False. Caching uses the cfg's hashable tuple as key.
#
# To preserve backward compatibility, the bare factories `scout_chain()`,
# etc., default to `ToolAblationConfig()` (the current "full" baseline).


def _cfg_key(cfg) -> tuple:
    return (
        cfg.enable_h2,
        cfg.enable_ot,
        cfg.enable_gc_batch,
        cfg.enable_biology,
        cfg.enable_skill,
        cfg.enable_skill_reference_lane,
    )


@lru_cache(maxsize=16)
def _scout_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_scout_prompt(cfg), ScoutDirective)


@lru_cache(maxsize=16)
def _gather_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_gather_prompt(cfg), RoundDirective)


@lru_cache(maxsize=16)
def _judge_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_judge_prompt(cfg), BundleRanking)


@lru_cache(maxsize=16)
def _pick_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_pick_prompt(cfg), ModelFrontier)


@lru_cache(maxsize=16)
def _pgs_triage_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_pgs_triage_prompt(cfg), PGSTriageSelection)


@lru_cache(maxsize=16)
def _global_primary_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_global_primary_prompt(cfg), GlobalPrimaryDecision)


@lru_cache(maxsize=16)
def _critic_chain_for_key(key: tuple):
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg = ToolAblationConfig(*key)
    return _build_chain(make_critic_prompt(cfg), CritiqueDecision)


def scout_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _scout_chain_for_key(_cfg_key(cfg))


def gather_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _gather_chain_for_key(_cfg_key(cfg))


def judge_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _judge_chain_for_key(_cfg_key(cfg))


def pick_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _pick_chain_for_key(_cfg_key(cfg))


def pgs_triage_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _pgs_triage_chain_for_key(_cfg_key(cfg))


def global_primary_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _global_primary_chain_for_key(_cfg_key(cfg))


def critic_chain(cfg=None):
    if cfg is None:
        from experiments.contribution3.transfer.agent import ToolAblationConfig
        cfg = ToolAblationConfig()
    return _critic_chain_for_key(_cfg_key(cfg))
