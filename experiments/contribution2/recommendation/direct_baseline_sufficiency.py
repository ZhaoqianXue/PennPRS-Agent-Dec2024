"""Binary direct-baseline sufficiency adjudicator for Contribution 2.

This module belongs to the c2 same-trait harness. It runs after the retained
Stage 2 evaluator has selected the final same-trait PGS and before any top-level
PennPRS Agent workflow is allowed to call the c3 transfer harness.
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional

from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel


class DirectBaselineSufficiencyDecision(BaseModel):
    accept_direct_baseline: bool
    rationale: str


SUFFICIENCY_SYSTEM_PROMPT = """# Identity & Role
You are the Contribution 2 direct-baseline sufficiency adjudicator inside the
PennPRS same-trait PGS-selection harness.

# Task
The c2 harness has already selected one final same-trait PGS candidate. Decide
whether that direct same-trait baseline is strong enough to terminate the
top-level PennPRS Agent workflow without cross-trait transfer.

# Decision Boundary
- Output a binary decision only.
- `accept_direct_baseline=true` means the final same-trait PGS is sufficiently
  well supported by visible same-trait evidence, so the top-level workflow should
  stop.
- `accept_direct_baseline=false` means the same-trait baseline is missing, weak,
  conflicted, or too uncertain, so the top-level workflow should escalate to
  cross-trait transfer.
- Do not choose a new PGS.
- Do not reason about cross-trait source selection.
- Respect the c2 retained evaluator contract: a full c2 Stage 2
  `DIRECT_HIGH_QUALITY` winner with High/Moderate confidence is sufficient, and
  a retained `DIRECT_SUB_OPTIMAL` or lower-confidence winner is not sufficient.
- Direct-only same-trait retrieval without the retained c2 Stage 2 evaluator is
  weaker evidence and should terminate only when support is unusually clear.
- Do not use hidden benchmark labels, held-out AUCs, target-route labels, trait
  categories, ICD rules, whitelists, blacklists, or case-specific shortcuts.
- Do not invent thresholds or missing evidence.

# Evidence Frame
Use only production-visible evidence in the input context:
- c2 Stage 1 decision and shortlist, if present
- c2 Stage 2 final same-trait evaluator output, if present
- selected PGS Catalog candidate metadata
- visible same-trait shortlist candidate metadata
- c2 domain-knowledge / PRS model evaluator guidance, if present

Weigh endpoint fit, comparable PRS evidence, covariate/package risk,
validation/training context, ancestry context, method/model record, and internal
conflicts. The guidance is advisory, not a deterministic score sheet.

# Output
Return exactly one JSON object with:
{
  "accept_direct_baseline": true,
  "rationale": "One concise evidence-grounded sentence."
}
"""


def adjudicate_direct_baseline_sufficiency(
    *,
    target_trait: str,
    same_trait_result: dict[str, Any],
    stage1_decision: Optional[dict[str, Any]] = None,
    stage2_decision: Optional[dict[str, Any]] = None,
    candidate_summaries: Optional[list[dict[str, Any]]] = None,
    domain_knowledge: Optional[dict[str, Any]] = None,
    model: Optional[str] = None,
    use_llm: bool = True,
) -> DirectBaselineSufficiencyDecision:
    """Return the c2 binary decision that controls whether c3 may run.

    `use_llm=False` is the stable cached-demo path. It preserves the c2 decision
    contract without calling an external model, and it remains deliberately
    conservative for missing or low-confidence matches.
    """
    fallback = _fallback_from_c2_contract(same_trait_result)
    contract_decision = _deterministic_harness_contract(same_trait_result)
    if contract_decision is not None:
        return contract_decision
    if not use_llm or not os.getenv("OPENAI_API_KEY"):
        return fallback

    context = {
        "target_trait": target_trait,
        "same_trait_result": _strip_internal_fields(same_trait_result),
        "stage1_decision": stage1_decision or {},
        "stage2_decision": stage2_decision or {},
        "candidate_summaries": candidate_summaries or [],
        "domain_knowledge": domain_knowledge or {},
        "instruction": (
            "Decide whether the final c2 same-trait baseline is sufficient to "
            "stop the top-level workflow. Return only the binary schema."
        ),
    }

    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model=model or os.getenv("OPENAI_MODEL") or "gpt-5.2",
            messages=[
                {"role": "system", "content": SUFFICIENCY_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": "Context:\n"
                    + json.dumps(context, ensure_ascii=False, separators=(",", ":")),
                },
            ],
            response_format=_response_format(),
            temperature=0,
            seed=42,
        )
        content = response.choices[0].message.content
    except Exception:
        return fallback
    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        )
    try:
        decision = DirectBaselineSufficiencyDecision.model_validate_json(content or "")
    except Exception:
        return fallback
    if not _has_usable_same_trait_candidate(same_trait_result):
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=False,
            rationale=(
                "No usable same-trait PGS was selected, so the direct baseline "
                "cannot terminate the workflow."
            ),
        )
    if same_trait_result.get("match_kind") == "candidate_label_fuzzy":
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=False,
            rationale=(
                "The same-trait match was established only through a low-confidence "
                "candidate-label fallback, so transfer evidence should be evaluated."
            ),
        )
    return decision


def _response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "direct_baseline_sufficiency_decision",
            "strict": True,
            "schema": to_strict_json_schema(DirectBaselineSufficiencyDecision),
        },
    }


def _fallback_from_c2_contract(
    same_trait_result: dict[str, Any],
) -> DirectBaselineSufficiencyDecision:
    if not _has_usable_same_trait_candidate(same_trait_result):
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=False,
            rationale=(
                "C2 did not establish a usable same-trait PGS baseline, so the "
                "workflow should escalate to transfer."
            ),
        )
    if same_trait_result.get("match_kind") == "candidate_label_fuzzy":
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=False,
            rationale=(
                "C2 matched the baseline only through a low-confidence candidate "
                "label fallback, so the baseline is not sufficient to stop."
            ),
        )
    rec_type = same_trait_result.get("recommendation_type")
    confidence = same_trait_result.get("confidence")
    accepted = rec_type == "DIRECT_HIGH_QUALITY" and confidence in {"High", "Moderate"}
    if accepted:
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=True,
            rationale=(
                "C2 accepted the retained same-trait winner as a direct high-quality "
                "baseline with at least moderate confidence."
            ),
        )
    return DirectBaselineSufficiencyDecision(
        accept_direct_baseline=False,
        rationale=(
            "C2 selected a same-trait baseline, but its retained outcome or "
            "confidence was not strong enough to stop before transfer review."
        ),
    )


def _deterministic_harness_contract(
    same_trait_result: dict[str, Any],
) -> Optional[DirectBaselineSufficiencyDecision]:
    """Apply non-negotiable c2 harness routing constraints before LLM review."""
    if not _has_usable_same_trait_candidate(same_trait_result):
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=False,
            rationale=(
                "C2 did not establish a usable same-trait PGS baseline, so the "
                "workflow should escalate to transfer."
            ),
        )
    if same_trait_result.get("match_kind") == "candidate_label_fuzzy":
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=False,
            rationale=(
                "C2 matched the baseline only through a low-confidence candidate "
                "label fallback, so the baseline is not sufficient to stop."
            ),
        )

    rec_type = same_trait_result.get("recommendation_type")
    confidence = same_trait_result.get("confidence")
    execution_mode = str(same_trait_result.get("execution_mode") or "")

    if execution_mode == "live_direct_only_same_trait":
        if rec_type != "DIRECT_HIGH_QUALITY" or confidence != "High":
            return DirectBaselineSufficiencyDecision(
                accept_direct_baseline=False,
                rationale=(
                    "The direct-only same-trait pass did not provide high-confidence "
                    "direct-baseline evidence, so the workflow should escalate to transfer."
                ),
            )
        return None

    if rec_type == "DIRECT_HIGH_QUALITY" and confidence in {"High", "Moderate"}:
        return DirectBaselineSufficiencyDecision(
            accept_direct_baseline=True,
            rationale=(
                "The retained C2 same-trait evaluator accepted the final winner as "
                "a direct high-quality baseline with at least moderate confidence."
            ),
        )
    return DirectBaselineSufficiencyDecision(
        accept_direct_baseline=False,
        rationale=(
            "The retained C2 same-trait evaluator did not classify the final winner "
            "as a high-quality direct baseline, so transfer evidence should be evaluated."
        ),
    )


def _has_usable_same_trait_candidate(same_trait_result: dict[str, Any]) -> bool:
    return same_trait_result.get("status") == "found" and bool(same_trait_result.get("pgs_id"))


def _strip_internal_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if not str(key).startswith("_")
    }
