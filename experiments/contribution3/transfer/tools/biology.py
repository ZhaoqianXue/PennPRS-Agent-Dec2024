"""Biology-aware retrieval tool — Stage 1 Scout candidate augmentation.

This tool is **retrieval augmentation**, not ranking. It identifies
candidate bundles in a target's bundle universe that are biologically
related to the target trait but that a lexical similarity filter may
have missed (e.g., shared genetic architecture, pleiotropy, comorbidity
without keyword overlap). The Scout stage merges these IDs additively
into its probe pool; the helper does NOT reorder existing IDs.

Tool contract:
- INPUT: target trait label/aliases, the bundle universe to choose from,
  and a one-line `reason` from Scout (why augmentation was requested).
- OUTPUT: `BiologyRetrievalResult` — typed Pydantic model containing
  validated suggestions (filtered against the universe), the LLM's
  rationale, and observability counters (`n_suggestions_total` /
  `n_suggestions_kept` / `skipped_reason`) so callers can audit whether
  the LLM contributed real signal or returned empty.

Architecture:
- Single LLM call (P8a-style; reverted 2026-04-24 from a 3-axis variant
  P9 that diluted Judge focus on K42/K02). Pure LLM-driven, no external
  KBs — biomedical reasoning comes from the LLM's parametric knowledge,
  per the project's no-external-DB constraint.
- Output filter: bundle_ids absent from the input universe are dropped
  silently. The harness can rely on the typed result without re-checking.

Performance contract (verified by ablation on v10 80-target benchmark):
- Disabling this tool drops top_0.5% from 20→16 (-4 hits) and top_2.5%
  from 42→32 (-10 hits) on the unified benchmark — the tool is a
  load-bearing contributor and should not be removed without a verified
  replacement of equivalent value.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

from experiments.contribution3.transfer.schemas import (
    BiologyRetrievalResponse,
    BiologyRetrievalResult,
    BiologySuggestion,
)
from src.server.core.llm_config import get_llm

logger = logging.getLogger(__name__)


# Same prompt as P8a — kept verbatim. Behavior is part of the v10
# performance contract; do not edit without an A/B benchmark.
_BIOLOGY_RETRIEVAL_SYSTEM_PROMPT = """\
You are a biomedical knowledge retriever. The user provides a target trait \
and a universe of candidate bundle labels. Your job is to identify bundles \
in the universe that are biologically related to the target but that a \
lexical similarity filter may have missed — e.g., because they share \
genetic architecture or disease mechanism without sharing keywords.

HARD CONSTRAINTS
- You MUST only return bundle IDs that appear in the provided universe.
- You MUST NOT reference specific ICD codes, disease family names, or
  category-specific rules. Keep your reasoning trait-agnostic.
- Return at most 15 suggestions.
- For each suggestion, give a one-sentence biological rationale citing a \
  shared pathway, pleiotropy, or comorbidity — not a lexical overlap.

You ARE augmenting candidate retrieval only. Another LLM call later will \
rank candidates; do not attempt ranking here.
"""


@lru_cache(maxsize=1)
def _build_biology_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=_BIOLOGY_RETRIEVAL_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template("{request_json}"),
        ]
    )
    structured = llm.with_structured_output(
        BiologyRetrievalResponse, method="function_calling"
    )
    return prompt | structured


def biology_retrieve_related_bundles(
    *,
    target_label: str,
    target_aliases: list[str] | None,
    bundle_universe: list[dict[str, Any]],
    reason: str = "",
) -> BiologyRetrievalResult:
    """Identify universe bundles biologically related to the target trait.

    Args:
        target_label: Canonical label of the target trait (e.g. "stroke").
        target_aliases: Up to 10 aliases for the target. Truncated by the
            tool to control prompt size.
        bundle_universe: List of {bundle_id, canonical_label, aliases}
            dicts that the LLM is allowed to pick from. The tool filters
            output strictly against this universe.
        reason: One-line rationale from Scout for why augmentation was
            requested. Passed to the LLM verbatim so it can target gaps.

    Returns:
        BiologyRetrievalResult with validated suggestions, LLM rationale,
        and observability counters. Always returns a result object — never
        raises. If the LLM call errors or inputs are degenerate, the
        result has empty `suggestions` and a populated `skipped_reason`.
    """
    target_label = str(target_label or "").strip()
    if not target_label:
        return BiologyRetrievalResult(
            suggestions=[], rationale="", skipped_reason="empty_target"
        )
    if not bundle_universe:
        return BiologyRetrievalResult(
            suggestions=[], rationale="", skipped_reason="empty_universe"
        )
    known_ids = {b.get("bundle_id") for b in bundle_universe if b.get("bundle_id")}

    request = {
        "target_trait": target_label,
        "target_aliases": list(target_aliases or [])[:10],
        "reason_for_augmentation": reason,
        "bundle_universe": [
            {
                "bundle_id": b.get("bundle_id"),
                "canonical_label": b.get("canonical_label"),
                "aliases": list(b.get("aliases") or [])[:4],
            }
            for b in bundle_universe
        ],
    }

    try:
        raw: BiologyRetrievalResponse = _build_biology_chain().invoke(
            {"request_json": json.dumps(request, ensure_ascii=False)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Biology retrieval LLM call failed: %s", exc)
        return BiologyRetrievalResult(
            suggestions=[], rationale="", skipped_reason=f"llm_error:{exc}"
        )

    n_total = len(raw.suggestions)
    kept = [s for s in raw.suggestions if s.bundle_id in known_ids]
    return BiologyRetrievalResult(
        suggestions=[
            BiologySuggestion(
                bundle_id=s.bundle_id,
                suggestion_rationale=s.suggestion_rationale,
            )
            for s in kept
        ],
        rationale=raw.rationale,
        n_suggestions_total=n_total,
        n_suggestions_kept=len(kept),
        skipped_reason=None,
    )


