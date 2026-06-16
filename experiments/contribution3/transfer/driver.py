"""Batch-compatible entry point for the LLM-led transfer agent.

Preserves the old `run_cross_trait_agent(dossier, condition=..., toolbox=...,
benchmark_family=..., ablation=..., stop_after=...)` signature so that
`experiments/contribution3/transfer/batch/run_batch.py` needs only a
one-line import change.

The `condition`, `toolbox`, `benchmark_family`, and `ablation` arguments
are accepted for API compatibility. In the LLM-led architecture the
toolbox is built internally from the dossier, and `condition`/`ablation`
map onto the tool-call budget only — decisions stay entirely with the
LLM.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Literal, Optional

from experiments.contribution3.transfer.agent import (
    ToolAblationConfig,
    run_transfer_agent,
)
from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    DEFAULT_TRANSFER_ABLATION,
    LEGACY_FULL_ABLATION,
    filter_dossier_to_benchmark_universe,
    normalize_transfer_ablation,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Legacy-compatible enums & helpers consumed by batch/run_batch.py
# ---------------------------------------------------------------------------

CONDITION_TOOLS: dict[str, list[str]] = {
    "gpt-only": [],
    "dossier-only": [],
    "all-tools": [
        "get_heritability",
        "get_open_targets_overlap",
    ],
}

TRANSFER_ABLATIONS: tuple[str, ...] = (
    # Paper-facing C3 result: tuned Harness Only V1.
    DEFAULT_TRANSFER_ABLATION,
    # Formal comparator for the V1 result.
    "no_all_tools",
    # Legacy top-level label retained for archived full-tool runs only.
    LEGACY_FULL_ABLATION,
    "no_critic",
    "all_evidence_tools",
    # Archived evidence-tool ablations.
    "add_h2_tool",
    "add_ot_tool",
    "add_gc_tool",
    "add_biology_tool",
    "add_h2_ot_tools",
    "add_h2_gc_tools",
    "add_h2_biology_tools",
    "add_ot_gc_tools",
    "add_ot_biology_tools",
    "add_gc_biology_tools",
    "add_h2_ot_gc_tools",
    "add_h2_ot_biology_tools",
    "add_h2_gc_biology_tools",
    "add_ot_gc_biology_tools",
    "no_h2_tool",
    "no_ot_tool",
    "no_gc_tool",
    "no_biology_tool",
)


# ---------------------------------------------------------------------------
# Ablation label → ToolAblationConfig
# ---------------------------------------------------------------------------

_TOOL_ABLATION_CONFIGS: dict[str, ToolAblationConfig] = {
    # Paper-facing C3 result: tuned Harness Only V1.
    # Reactivates the existing breadth_floor safety net under no-OT
    # conditions by allowing high-n_models probed bundles to qualify
    # without OT overlap. Trait-agnostic, harness-common, no PRS skill text.
    DEFAULT_TRANSFER_ABLATION: ToolAblationConfig(
        enable_h2=False, enable_ot=False, enable_gc_batch=False, enable_biology=False,
        enable_breadth_floor_no_ot_fallback=True,
        enable_dossier_coverage_floor=True,
    ),
    # Formal comparator for V1.
    "no_all_tools": ToolAblationConfig(
        enable_h2=False, enable_ot=False, enable_gc_batch=False, enable_biology=False,
    ),
    # Legacy full-tool labels.
    LEGACY_FULL_ABLATION: ToolAblationConfig(enable_h2=True, enable_ot=True, enable_gc_batch=True, enable_biology=True),
    "no_critic":               ToolAblationConfig(),
    "all_evidence_tools":      ToolAblationConfig(enable_h2=True, enable_ot=True, enable_gc_batch=True, enable_biology=True),
    # Archived additive tool conditions over no_all_tools.
    "add_h2_tool":             ToolAblationConfig(enable_h2=True,  enable_ot=False, enable_gc_batch=False, enable_biology=False),
    "add_ot_tool":             ToolAblationConfig(enable_h2=False, enable_ot=True,  enable_gc_batch=False, enable_biology=False),
    "add_gc_tool":             ToolAblationConfig(enable_h2=False, enable_ot=False, enable_gc_batch=True,  enable_biology=False),
    "add_biology_tool":        ToolAblationConfig(enable_h2=False, enable_ot=False, enable_gc_batch=False, enable_biology=True),
    "add_h2_ot_tools":         ToolAblationConfig(enable_h2=True,  enable_ot=True,  enable_gc_batch=False, enable_biology=False),
    "add_h2_gc_tools":         ToolAblationConfig(enable_h2=True,  enable_ot=False, enable_gc_batch=True,  enable_biology=False),
    "add_h2_biology_tools":    ToolAblationConfig(enable_h2=True,  enable_ot=False, enable_gc_batch=False, enable_biology=True),
    "add_ot_gc_tools":         ToolAblationConfig(enable_h2=False, enable_ot=True,  enable_gc_batch=True,  enable_biology=False),
    "add_ot_biology_tools":    ToolAblationConfig(enable_h2=False, enable_ot=True,  enable_gc_batch=False, enable_biology=True),
    "add_gc_biology_tools":    ToolAblationConfig(enable_h2=False, enable_ot=False, enable_gc_batch=True,  enable_biology=True),
    "add_h2_ot_gc_tools":      ToolAblationConfig(enable_h2=True,  enable_ot=True,  enable_gc_batch=True,  enable_biology=False),
    "add_h2_ot_biology_tools": ToolAblationConfig(enable_h2=True,  enable_ot=True,  enable_gc_batch=False, enable_biology=True),
    "add_h2_gc_biology_tools": ToolAblationConfig(enable_h2=True,  enable_ot=False, enable_gc_batch=True,  enable_biology=True),
    "add_ot_gc_biology_tools": ToolAblationConfig(enable_h2=False, enable_ot=True,  enable_gc_batch=True,  enable_biology=True),
    "no_h2_tool":              ToolAblationConfig(enable_h2=False, enable_ot=False, enable_gc_batch=True, enable_biology=False),
    "no_ot_tool":              ToolAblationConfig(enable_h2=True, enable_ot=False, enable_gc_batch=True, enable_biology=False),
    "no_gc_tool":              ToolAblationConfig(enable_h2=True, enable_ot=False, enable_gc_batch=False, enable_biology=False),
    "no_biology_tool":         ToolAblationConfig(enable_h2=True, enable_ot=False, enable_gc_batch=True, enable_biology=False),
}

def _tool_ablation_for_label(label: str) -> ToolAblationConfig:
    return _TOOL_ABLATION_CONFIGS.get(label, ToolAblationConfig())


def _budget_for_condition(condition: str) -> int:
    """Tool-call budget by condition — observability knob only.

    All conditions run the same LLM-led architecture. `gpt-only` gets a
    tiny budget (the LLM must rely on its prior); `all-tools` gets the
    full 40-call budget.
    """
    if condition == "gpt-only":
        return 0
    if condition == "dossier-only":
        return 0
    return 40  # all-tools


def run_cross_trait_agent(
    dossier: CandidateBundleDossier,
    condition: Literal["gpt-only", "dossier-only", "all-tools"],
    bundles: Optional[Iterable[Any]] = None,
    toolbox: Optional[Any] = None,
    max_steps: int = 8,
    enable_semantic_backstop: bool = True,
    enable_forced_match: bool = True,
    benchmark_family: str = "unified",
    ablation: str = DEFAULT_TRANSFER_ABLATION,
    stop_after: Optional[Literal["bundle_posterior"]] = None,
) -> dict[str, Any]:
    """Preserve the old entrypoint signature; delegate to the LLM-led agent.

    Accepted-but-ignored legacy knobs: `bundles`, `toolbox`,
    `enable_semantic_backstop`, `enable_forced_match`. They were wiring
    for the deleted v-prev architecture and carry no decision semantics.
    """
    del bundles, toolbox, enable_semantic_backstop, enable_forced_match
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    ablation_label = normalize_transfer_ablation(ablation)
    if ablation_label not in TRANSFER_ABLATIONS:
        raise ValueError(
            f"Unsupported ablation: {ablation}. Expected one of {TRANSFER_ABLATIONS}"
        )

    max_tool_calls = _budget_for_condition(condition)
    enable_critic = ablation_label != "no_critic"
    max_gather_rounds = max(1, int(max_steps))
    tool_ablation = _tool_ablation_for_label(ablation_label)
    dossier = filter_dossier_to_benchmark_universe(
        dossier,
        benchmark_family=benchmark_family,
    )

    return run_transfer_agent(
        dossier=dossier,
        max_tool_calls=max_tool_calls,
        max_gather_rounds=max_gather_rounds,
        enable_critic=enable_critic,
        stop_after=stop_after,
        benchmark_family=benchmark_family,
        tool_ablation=tool_ablation,
    )


# ---------------------------------------------------------------------------
# Output persistence
# ---------------------------------------------------------------------------

def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    """Serialize agent results to JSON on disk."""
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str))
