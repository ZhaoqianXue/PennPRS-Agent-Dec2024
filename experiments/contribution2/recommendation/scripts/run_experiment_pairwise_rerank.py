"""Synchronous ranked-decision plus final-selection runner for within-trait PGS selection.

Hypothesis (Phase 1 + Phase 3 grounded):
- Phase 1, Anthropic harness paper: a stock LLM is a poor evaluator of its own
  work; "Separating the agent doing the work from the agent judging it proves
  to be a strong lever".
- Phase 1, Bavaresco et al. 2026 (LLM-judge BoN paper): in matched best-of-2
  audits, pairwise judging raises selection-recovery from 21.1% → 61.2% versus
  pointwise scoring, because pointwise tie rates near 67% force random tiebreaks.
- Phase 3, iterD-final 89-disease t=1: 36 of 59 H1 misses are still inside H5,
  meaning the right candidate is in the LLM's reachable shortlist but Stage 1
  fails to discriminate the AUC-best within a tight cluster.
- Distinct from prior failures: not multi-trial sampling (iterF/G majority vote
  failed at t=0/0.3); not extra decision-protocol prose (iterE failed); not
  open-ended TRIAGE/PICK/CRITIC (pev-with-skill over-revised). The final
  selector can only choose among the ranked candidates the first call carried
  forward, never introduce an out-of-pool candidate.

Architecture:
  Stage 1: same iterD-final context (SKILL.md procedural overview + 55K corpus +
           heritability section), same within-stage-1 shortlist system prompt,
           but the schema is augmented to also emit `top_alternatives` as an
           evidence-supported, non-repeating runner-up list after `best_model_id`.
           Single-shot, t=0, seed=42 — preserves iterD-final pick on the easy 30 cases.
  Stage 2: Either pairwise-judge calls over the carried-forward set, or one
           holistic judge/ranker call, depending on --evaluator.
  Aggregate: Pairwise mode uses Borda count over pairwise wins; holistic modes
           directly return the Stage 2 winner.

If Stage 1 emits too few valid candidates for Stage 2, the Stage 1 best_model_id
is used directly (graceful degradation).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401 — registers patches into wd
from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as wd
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.within_prompts import (
    WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
    WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
    WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    build_within_stage1_user_instruction,
    build_within_topk_user_message,
    objective_block as within_objective_block,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

STAGE1_MAX_CARRIED_CANDIDATES = 10
STAGE1_MAX_TOP_ALTERNATIVES = STAGE1_MAX_CARRIED_CANDIDATES - 1
STAGE2_CANDIDATE_ORDER_SOURCE = "source"
STAGE2_CANDIDATE_ORDER_SEED = "pennprs-stage2-carried-order-v1"


def _archived_surface_error(name: str) -> ValueError:
    return ValueError(
        f"{name} is archived and is not part of the active retained-result prompt surface; "
        "use topk_judge double-stage or fullpool_judge single-stage with support objective."
    )


class Step1RankedDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    top_alternatives: list[str] = Field(max_length=STAGE1_MAX_TOP_ALTERNATIVES)
    confidence: str
    rationale: str


class Stage1CandidateAudit(BaseModel):
    pgs_id: str
    shortlist_status: str
    endpoint_fit: str
    ancestry_fit: str
    metric_signal: str
    validation_signal: str
    risk_signal: str
    missing_or_ambiguous_evidence: str


class Stage1ShortlistAuditJudgment(BaseModel):
    candidate_audits: list[Stage1CandidateAudit]
    shortlist_model_ids: list[str]
    excluded_model_ids: list[str]
    best_model_id: Optional[str] = None
    strongest_excluded_competitor: Optional[str] = None
    shortlist_deciding_factors: list[str]
    non_deciding_factors: list[str]
    uncertainty_drivers: list[str]
    confidence: str
    rationale: str


class PairwiseJudgment(BaseModel):
    winner_model_id: str
    confidence: str
    rationale: str


class TopKJudgment(BaseModel):
    ranked_model_ids: list[str]
    winner_model_id: str
    confidence: str
    rationale: str


class TopKRankingJudgment(BaseModel):
    ranked_model_ids: list[str]
    confidence: str
    rationale: str


class CandidateAudit(BaseModel):
    pgs_id: str
    endpoint_fit: str
    metric_signal: str
    validation_signal: str
    risk_signal: str
    benchmark_rank_signal: str


class AuditedTopKJudgment(BaseModel):
    candidate_audits: list[CandidateAudit]
    ranked_model_ids: list[str]
    winner_model_id: str
    strongest_runner_up: str
    deciding_factors: list[str]
    non_deciding_factors: list[str]
    uncertainty_drivers: list[str]
    confidence: str
    rationale: str


# ---------------------------------------------------------------------------
# Stage 1 — modified single-shot that also emits top alternatives
# ---------------------------------------------------------------------------

def _objective_block(objective: str) -> str:
    return within_objective_block(objective)


def _stage1_user_instruction(top_k: int, *, objective: str) -> str:
    return build_within_stage1_user_instruction(top_k, objective=objective)

def _stage1_messages(context_json: str, *, top_k: int, objective: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"{_stage1_user_instruction(top_k, objective=objective)}\n{context_json}",
        },
    ]


def _json_payload_from_user_message(user_message: str) -> str | None:
    for marker in ("Input JSON:\n", "Context:\n"):
        idx = user_message.find(marker)
        if idx >= 0:
            return user_message[idx + len(marker):]
    return None


def _general_biomedical_context_json(context_json: str) -> str:
    try:
        ctx = json.loads(context_json)
    except Exception:
        return context_json
    for key in ["skill_context", "domain_knowledge", "todo_recitation_path", "todo_recitation"]:
        ctx.pop(key, None)
    return json.dumps(ctx, separators=(",", ":"), ensure_ascii=False)


def _general_biomedical_stage1_messages(context_json: str, *, top_k: int) -> list[dict[str, str]]:
    del context_json, top_k
    raise _archived_surface_error("general_biomedical_stage1")


def _stage1_messages_for_arm(
    context_json: str,
    *,
    top_k: int,
    objective: str,
    general_biomedical_llm: bool,
) -> list[dict[str, str]]:
    if general_biomedical_llm:
        raise _archived_surface_error("general_biomedical_stage1")
    return _stage1_messages(context_json, top_k=top_k, objective=objective)


def _stage1_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_ranked_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1RankedDecision),
        },
    }


def _build_stage1_audit_user_message(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    candidate_summaries: dict[str, dict[str, Any]] | list[dict[str, Any]],
    stage1_decision: dict[str, Any],
    skill_context: Optional[dict[str, Any]] = None,
) -> str:
    del target_trait, target_ancestry, candidate_summaries, stage1_decision, skill_context
    raise _archived_surface_error("stage1_audit")


def _stage1_audit_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "stage1_shortlist_audit_judgment",
            "strict": True,
            "schema": to_strict_json_schema(Stage1ShortlistAuditJudgment),
        },
    }


# ---------------------------------------------------------------------------
# Stage 2 — pairwise judge
# ---------------------------------------------------------------------------

def _build_pairwise_user_message(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    skill_context: Optional[dict[str, Any]] = None,
) -> str:
    del (
        target_trait,
        target_ancestry,
        candidate_a_id,
        candidate_b_id,
        candidate_a_summary,
        candidate_b_summary,
        skill_context,
    )
    raise _archived_surface_error("pairwise_judge")


def _pairwise_messages_for_arm(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool,
) -> list[dict[str, str]]:
    del (
        target_trait,
        target_ancestry,
        candidate_a_id,
        candidate_b_id,
        candidate_a_summary,
        candidate_b_summary,
        skill_context,
        objective,
        general_biomedical_llm,
    )
    raise _archived_surface_error("pairwise_judge")


def _pairwise_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "pairwise_judgment",
            "strict": True,
            "schema": to_strict_json_schema(PairwiseJudgment),
        },
    }


def _build_topk_user_message(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: Optional[dict[str, Any]] = None,
) -> str:
    return build_within_topk_user_message(
        target_trait=target_trait,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        skill_context=skill_context,
    )


def _topk_messages_for_arm(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool,
) -> list[dict[str, str]]:
    if general_biomedical_llm:
        raise _archived_surface_error("general_biomedical_topk_selector")

    user_message = _build_topk_user_message(
        target_trait=target_trait,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        skill_context=skill_context,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def _topk_ranker_messages_for_arm(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool,
) -> list[dict[str, str]]:
    del (
        target_trait,
        target_ancestry,
        ranked_candidate_ids,
        candidate_summaries,
        skill_context,
        objective,
        general_biomedical_llm,
    )
    raise _archived_surface_error("topk_ranker")


def _fullpool_messages_for_arm(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool,
) -> list[dict[str, str]]:
    if general_biomedical_llm:
        raise _archived_surface_error("general_biomedical_fullpool")

    user_message = _build_topk_user_message(
        target_trait=target_trait,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        skill_context=skill_context,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def _build_stage2_audit_user_message(
    *,
    target_trait: str,
    target_ancestry: Optional[str] = None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: Optional[dict[str, Any]] = None,
    frozen_winner_model_id: str,
    stage2_decision: Optional[dict[str, Any]] = None,
) -> str:
    del (
        target_trait,
        target_ancestry,
        ranked_candidate_ids,
        candidate_summaries,
        skill_context,
        frozen_winner_model_id,
        stage2_decision,
    )
    raise _archived_surface_error("stage2_audit")


def _topk_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "topk_judgment",
            "strict": True,
            "schema": to_strict_json_schema(TopKJudgment),
        },
    }


def _topk_audit_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "audited_topk_judgment",
            "strict": True,
            "schema": to_strict_json_schema(AuditedTopKJudgment),
        },
    }


def _run_stage2_for_topk_audit(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    target_ancestry: Optional[str] = None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: Optional[dict[str, Any]] = None,
    frozen_winner_model_id: str,
    stage2_decision: Optional[dict[str, Any]] = None,
    objective: str,
) -> dict[str, Any]:
    del (
        client,
        model,
        ontology,
        target_ancestry,
        ranked_candidate_ids,
        candidate_summaries,
        skill_context,
        frozen_winner_model_id,
        stage2_decision,
        objective,
    )
    raise _archived_surface_error("stage2_audit")


def _run_stage1_audit_trace(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    target_ancestry: Optional[str],
    candidate_summaries: dict[str, dict[str, Any]],
    stage1_decision: dict[str, Any],
    skill_context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    del client, model, ontology, target_ancestry, candidate_summaries, stage1_decision, skill_context
    raise _archived_surface_error("stage1_audit")


def _topk_ranking_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "topk_ranking_judgment",
            "strict": True,
            "schema": to_strict_json_schema(TopKRankingJudgment),
        },
    }


def _run_stage2_for_topk_ranker(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    target_ancestry: Optional[str] = None,
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool = False,
) -> dict[str, Any]:
    messages = _topk_ranker_messages_for_arm(
        target_trait=ontology,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        skill_context=skill_context,
        objective=objective,
        general_biomedical_llm=general_biomedical_llm,
    )
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_ranking_response_format(),
            stage="stage2_topk_ranker",
            custom_id=ontology,
        )
        verdict = TopKRankingJudgment.model_validate_json(content)
        valid_ids: list[str] = []
        allowed = set(ranked_candidate_ids)
        for pgs_id in verdict.ranked_model_ids:
            pgs_id = str(pgs_id).strip()
            if pgs_id in allowed and pgs_id not in valid_ids:
                valid_ids.append(pgs_id)
        for pgs_id in ranked_candidate_ids:
            if pgs_id not in valid_ids:
                valid_ids.append(pgs_id)
        winner = valid_ids[0] if valid_ids else None
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "ranked_model_ids": valid_ids,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None if winner else "empty ranked_model_ids",
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "ranked_model_ids": [],
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"TopKRanker Stage2 {type(exc).__name__}: {exc}",
        }


def _run_stage2_for_topk(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    target_ancestry: Optional[str] = None,
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool = False,
) -> dict[str, Any]:
    messages = _topk_messages_for_arm(
        target_trait=ontology,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        skill_context=skill_context,
        objective=objective,
        general_biomedical_llm=general_biomedical_llm,
    )
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_response_format(),
            stage="stage2_topk_judge",
            custom_id=ontology,
        )
        verdict = TopKJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        allowed = set(ranked_candidate_ids)
        valid_ranked: list[str] = []
        for pgs_id in verdict.ranked_model_ids:
            pgs_id = str(pgs_id).strip()
            if pgs_id in allowed and pgs_id not in valid_ranked:
                valid_ranked.append(pgs_id)
        for pgs_id in ranked_candidate_ids:
            if pgs_id not in valid_ranked:
                valid_ranked.append(pgs_id)
        if winner not in allowed:
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "ranked_model_ids": valid_ranked,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in shortlist",
            }
        if valid_ranked and winner != valid_ranked[0]:
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "ranked_model_ids": valid_ranked,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": "winner_model_id does not match first ranked_model_ids entry",
            }
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "ranked_model_ids": valid_ranked,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"TopK Stage2 {type(exc).__name__}: {exc}",
        }


def _run_stage2_for_fullpool(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    target_ancestry: Optional[str] = None,
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool = False,
    usage_stage: str = "stage2_fullpool_judge",
) -> dict[str, Any]:
    messages = _fullpool_messages_for_arm(
        target_trait=ontology,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        skill_context=skill_context,
        objective=objective,
        general_biomedical_llm=general_biomedical_llm,
    )
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_response_format(),
            stage=usage_stage,
            custom_id=ontology,
        )
        verdict = TopKJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in set(ranked_candidate_ids):
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in full pool",
            }
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"FullPool Stage2 {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

_USAGE_LOCK = Lock()
_USAGE_RECORDS: list[dict[str, Any]] = []


def _reset_usage_records() -> None:
    with _USAGE_LOCK:
        _USAGE_RECORDS.clear()


def _record_usage(*, stage: str, custom_id: str, model: str, usage: Any) -> None:
    if usage is None:
        return
    payload = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage)
    with _USAGE_LOCK:
        _USAGE_RECORDS.append({
            "stage": stage,
            "custom_id": custom_id,
            "model": model,
            "usage": payload,
        })


def _summarize_usage_cost(model: str) -> Optional[dict[str, Any]]:
    pricing_key, pricing = without_domain._pricing_for_model(
        model,
        without_domain.STANDARD_PRICING_PER_MILLION_USD,
    )
    if pricing is None:
        return None
    with _USAGE_LOCK:
        records = list(_USAGE_RECORDS)
    input_tokens = 0
    cached_tokens = 0
    output_tokens = 0
    total_tokens = 0
    stage_counts: dict[str, int] = {}
    stage_usage: dict[str, dict[str, int]] = {}
    for record in records:
        usage = record.get("usage") or {}
        stage = str(record.get("stage") or "unknown")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        stage_block = stage_usage.setdefault(stage, {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        in_tok = without_domain._safe_int(usage.get("prompt_tokens") or usage.get("input_tokens"))
        out_tok = without_domain._safe_int(usage.get("completion_tokens") or usage.get("output_tokens"))
        tot_tok = without_domain._safe_int(usage.get("total_tokens"))
        details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
        cached = without_domain._safe_int(details.get("cached_tokens"))
        input_tokens += in_tok
        cached_tokens += cached
        output_tokens += out_tok
        total_tokens += tot_tok
        stage_block["input_tokens"] += in_tok
        stage_block["cached_input_tokens"] += cached
        stage_block["output_tokens"] += out_tok
        stage_block["total_tokens"] += tot_tok
    uncached_input_tokens = max(input_tokens - cached_tokens, 0)
    uncached_input_cost = uncached_input_tokens / 1_000_000 * pricing["input"]
    cached_input_cost = cached_tokens / 1_000_000 * pricing["cached_input"]
    output_cost = output_tokens / 1_000_000 * pricing["output"]
    total_cost = uncached_input_cost + cached_input_cost + output_cost
    return {
        "model_pricing_key": pricing_key or model,
        "token_usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
        "stage_call_counts": stage_counts,
        "stage_token_usage": stage_usage,
        "pricing_per_million_tokens_usd": {
            "input": pricing["input"],
            "cached_input": pricing["cached_input"],
            "output": pricing["output"],
        },
        "method": "exact_chat_completion_usage_times_official_standard_tier_prices",
        "estimated_cost_breakdown_usd": {
            "uncached_input": round(uncached_input_cost, 4),
            "cached_input": round(cached_input_cost, 4),
            "output": round(output_cost, 4),
        },
        "estimated_total_cost_usd": round(total_cost, 4),
    }


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _llm_call(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    response_format: dict[str, Any],
    stage: str,
    custom_id: str,
) -> str:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
    }
    # Match disease_workflow defaults from gpt-5.2 config (temperature=0, seed=42)
    body["temperature"] = 0
    body["seed"] = 42
    response = client.chat.completions.create(**body)
    _record_usage(stage=stage, custom_id=custom_id, model=model, usage=response.usage)
    choice = response.choices[0]
    content = choice.message.content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts).strip()
    return (content or "").strip()


def _run_stage1_for_request(
    client: OpenAI,
    model: str,
    request: dict[str, Any],
    top_k: int,
    objective: str,
    general_biomedical_llm: bool = False,
) -> dict[str, Any]:
    """Execute Stage 1 for a single batch-request entry. Reuses the prepared
    context_json from the existing manifest (no re-fetch of candidates).
    """
    custom_id = request["custom_id"]
    body = request["request"]["body"]
    user_messages = body["messages"]
    # The original user message is index 1; replace its instruction-prefix with
    # the ranked-decision instruction while preserving the JSON payload.
    original_user = user_messages[1]["content"]
    raw_context_json = _json_payload_from_user_message(original_user)
    if raw_context_json is None:
        raise RuntimeError(f"{custom_id}: could not locate input JSON marker in original user message")
    context_json = (
        _general_biomedical_context_json(raw_context_json)
        if general_biomedical_llm else _context_json_with_skill_context(raw_context_json)
    )
    messages = _stage1_messages_for_arm(
        context_json,
        top_k=top_k,
        objective=objective,
        general_biomedical_llm=general_biomedical_llm,
    )
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_stage1_response_format(),
            stage="stage1",
            custom_id=custom_id,
        )
        decision = Step1RankedDecision.model_validate_json(content)
        _select_ranked_candidates(
            best_model_id=decision.best_model_id,
            top_alternatives=decision.top_alternatives,
            candidate_id_set={str(pgs_id) for pgs_id in request.get("candidate_model_ids") or []},
            top_k=None,
        )
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "decision": decision.model_dump(),
            "context_json": context_json,
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "decision": None,
            "context_json": None,
            "error": f"Stage1 {type(exc).__name__}: {exc}",
        }


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """ontology -> { pgs_id -> candidate_summary }"""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for row in disease_metadata:
        ontology = row["ontology"]
        out[ontology] = {}
        for summary in row.get("candidate_models_visible_to_llm") or []:
            pgs_id = summary.get("pgs_id") or summary.get("id")
            if pgs_id:
                out[ontology][pgs_id] = summary
    return out


def _run_stage2_for_pair(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    target_ancestry: Optional[str] = None,
    skill_context: Optional[dict[str, Any]] = None,
    objective: str,
    general_biomedical_llm: bool = False,
) -> dict[str, Any]:
    messages = _pairwise_messages_for_arm(
        target_trait=ontology,
        target_ancestry=target_ancestry,
        candidate_a_id=candidate_a_id,
        candidate_b_id=candidate_b_id,
        candidate_a_summary=candidate_a_summary,
        candidate_b_summary=candidate_b_summary,
        skill_context=skill_context,
        objective=objective,
        general_biomedical_llm=general_biomedical_llm,
    )
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_pairwise_response_format(),
            stage="stage2_pairwise",
            custom_id=f"{ontology}::{candidate_a_id}::{candidate_b_id}",
        )
        verdict = PairwiseJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in {candidate_a_id, candidate_b_id}:
            return {
                "ontology": ontology,
                "candidate_a_id": candidate_a_id,
                "candidate_b_id": candidate_b_id,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in pair",
            }
        return {
            "ontology": ontology,
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"Stage2 {type(exc).__name__}: {exc}",
        }


def _select_ranked_candidates(
    *,
    best_model_id: Optional[str],
    top_alternatives: list[str],
    candidate_id_set: set[str],
    top_k: Optional[int] = None,
) -> list[str]:
    """Return the candidates the model ranked in contention, in Stage 1 order
    (deduplicated, candidate-set-valid, best_model_id first).

    With ``top_k=None`` (the production default), the carried-forward set is the
    model's valid Stage-1 shortlist, machine-validated against the 2-10 prompt
    contract. This is a boundary check, not a proxy ranker or benchmark aid.
    An explicit integer ``top_k`` is honoured only for legacy ablations that opt
    into a count.
    """
    seen: list[str] = []
    for cand in [best_model_id, *list(top_alternatives or [])]:
        if not cand:
            continue
        cand = str(cand).strip()
        if cand and cand in candidate_id_set and cand not in seen:
            seen.append(cand)
        if top_k is None and len(seen) > STAGE1_MAX_CARRIED_CANDIDATES:
            raise ValueError(
                f"Stage1 carried set exceeds {STAGE1_MAX_CARRIED_CANDIDATES}: "
                f"{len(seen)} valid candidates"
            )
        if top_k is not None and len(seen) >= top_k:
            break
    return seen


def _order_stage2_candidate_ids_for_llm(
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_order_seed: str = STAGE2_CANDIDATE_ORDER_SEED,
) -> list[str]:
    """Return the same carried candidate universe in the configured visible order."""
    ids = [pgs_id for pgs_id in ranked_candidate_ids if pgs_id]
    if STAGE2_CANDIDATE_ORDER_SOURCE == "source":
        return ids
    if STAGE2_CANDIDATE_ORDER_SOURCE != "stable_hash_shuffle":
        raise ValueError(f"Unsupported Stage2 candidate order: {STAGE2_CANDIDATE_ORDER_SOURCE}")
    return sorted(
        ids,
        key=lambda pgs_id: (
            hashlib.sha256(
                f"{candidate_order_seed}\0{ontology}\0{pgs_id}".encode("utf-8")
            ).hexdigest(),
            pgs_id,
        ),
    )


def _candidate_range_metadata(*, evaluator: str, top_k: Optional[int]) -> dict[str, Any]:
    """Describe the candidate range carried into final selection.

    This separates a true full-pool selector from an evidence-determined
    carry-forward set and from explicit fixed-count legacy ablations.
    """
    if top_k is not None:
        return {
            "top_k": top_k,
            "candidate_range": "fixed_count",
            "candidate_range_basis": "explicit_legacy_ablation_count",
            "engineering_limit": "fixed count requested by --top-k; not the production evidence-bound path",
        }
    if evaluator == "fullpool_judge":
        return {
            "top_k": "all",
            "candidate_range": "candidate_pool_universe",
            "candidate_range_basis": "all candidate_model_ids from the prepared manifest are sent to final selection",
            "engineering_limit": (
                "bounded only by the model/API context window and request-size limits; "
                "the runner applies no additional candidate-count cap"
            ),
        }
    return {
        "top_k": "all",
        "candidate_range": "evidence_determined",
        "candidate_range_basis": (
            "the final selector receives the valid ranked candidates emitted by the first call"
        ),
        "engineering_limit": (
            "bounded by the first call's evidence-determined output, machine-validated at "
            f"{STAGE1_MAX_CARRIED_CANDIDATES} carried candidates, and by model/API context-window limits"
        ),
    }


def _aggregate_borda(
    ranked_candidates: list[str],
    pairwise_results: list[dict[str, Any]],
) -> tuple[Optional[str], dict[str, int]]:
    """Win-count aggregation among Stage 1 ranked candidates from pairwise results.

    scores: dict pgs_id -> wins (each pairwise win = 1). Tiebreak: Stage 1 order
    (Stage 1 best_model_id wins ties)."""
    scores: dict[str, int] = {pgs_id: 0 for pgs_id in ranked_candidates}
    for result in pairwise_results:
        winner = result.get("winner_model_id")
        if winner and winner in scores:
            scores[winner] = scores.get(winner, 0) + 1
    if not scores:
        return None, scores
    # Sort by (wins desc, top3 index asc)
    order = {pgs_id: idx for idx, pgs_id in enumerate(ranked_candidates)}
    ranked = sorted(scores.keys(), key=lambda pid: (-scores[pid], order.get(pid, len(ranked_candidates))))
    return ranked[0], scores


def _enabled_audit_stages(emit_audit_trace: bool, audit_stages: str) -> set[str]:
    if not emit_audit_trace:
        return set()
    if audit_stages == "both":
        return {"stage1", "stage2"}
    if audit_stages in {"stage1", "stage2"}:
        return {audit_stages}
    raise ValueError(f"Unknown audit_stages: {audit_stages}")


def _target_ancestry_from_context_json(context_json: Optional[str]) -> Optional[str]:
    if not context_json:
        return None
    try:
        value = json.loads(context_json).get("target_ancestry")
    except Exception:
        return None
    return str(value).strip() if value else None


def _skill_context_from_context(ctx: dict[str, Any]) -> dict[str, Any]:
    skill_context = ctx.get("skill_context")
    if isinstance(skill_context, dict):
        return skill_context
    legacy = ctx.get("domain_knowledge")
    if not isinstance(legacy, dict):
        return {}
    return {
        "name": "prs-model-recommendation",
        "query": legacy.get("query", ""),
        "full_text": legacy.get("full_text", legacy.get("full_document", "")),
        "snippets": legacy.get("snippets", []),
        "source_type": legacy.get("source_type", "legacy_context"),
    }


def _context_json_with_skill_context(context_json: str) -> str:
    try:
        ctx = json.loads(context_json)
    except Exception:
        return context_json
    if "skill_context" not in ctx:
        skill_context = _skill_context_from_context(ctx)
        if skill_context:
            ctx["skill_context"] = skill_context
        ctx.pop("domain_knowledge", None)
    return json.dumps(ctx, separators=(",", ":"), ensure_ascii=False)


def _manifest_uses_general_biomedical_llm(manifest: dict[str, Any]) -> bool:
    if manifest.get("prompt_only_no_skill") is True:
        return False
    if manifest.get("skill_context") is False:
        return True
    if manifest.get("experiment") == "without_domain_batch_formal":
        return True
    return False


def _ensure_not_general_biomedical_rerank_manifest(manifest: dict[str, Any]) -> None:
    if _manifest_uses_general_biomedical_llm(manifest):
        raise ValueError(
            "general biomedical LLM prompt surfaces are archived from this runner. "
            "Use a retained PRS Agent manifest, or a prompt-only/no-skill manifest "
            "with prompt_only_no_skill=true."
        )


def _skill_context_and_target_ancestry_from_requests(
    requests: list[dict[str, Any]],
    *,
    general_biomedical_llm: bool,
) -> tuple[dict[str, dict[str, Any]], dict[str, Optional[str]]]:
    skill_context_by_ontology: dict[str, dict[str, Any]] = {}
    target_ancestry_by_ontology: dict[str, Optional[str]] = {}
    for request in requests:
        ontology = request["ontology"]
        if ontology in skill_context_by_ontology:
            continue
        body = request["request"]["body"]
        original_user = body["messages"][1]["content"]
        raw_context_json = _json_payload_from_user_message(original_user)
        if raw_context_json is None:
            skill_context_by_ontology[ontology] = {}
            target_ancestry_by_ontology[ontology] = None
            continue
        try:
            ctx = json.loads(raw_context_json)
        except Exception:
            skill_context_by_ontology[ontology] = {}
            target_ancestry_by_ontology[ontology] = None
            continue
        skill_context_by_ontology[ontology] = (
            {} if general_biomedical_llm else _skill_context_from_context(ctx)
        )
        value = ctx.get("target_ancestry")
        target_ancestry_by_ontology[ontology] = str(value).strip() if value else None
    return skill_context_by_ontology, target_ancestry_by_ontology


def _write_usage_records(output_run_dir: Path) -> None:
    with _USAGE_LOCK:
        usage_records = list(_USAGE_RECORDS)
    (output_run_dir / "experiment_pairwise_rerank_usage_records.json").write_text(
        json.dumps(usage_records, indent=2),
        encoding="utf-8",
    )


def _run_single_stage_fullpool_pipeline(
    *,
    client: OpenAI,
    manifest: dict[str, Any],
    requests: list[dict[str, Any]],
    output_run_dir: Path,
    model: str,
    workers: int,
    objective: str,
    stage1_objective: str,
    general_biomedical_llm: bool,
) -> dict[str, Any]:
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    skill_context_by_ontology, target_ancestry_by_ontology = _skill_context_and_target_ancestry_from_requests(
        requests,
        general_biomedical_llm=general_biomedical_llm,
    )
    ranked_candidates_by_ontology = {
        request["ontology"]: list(request["candidate_model_ids"])
        for request in requests
    }
    benchmark_top1_positions_by_ontology = {
        request["ontology"]: request.get("benchmark_top1_position_in_candidate_order")
        for request in requests
    }
    candidate_order_matches_benchmark_count = sum(
        1 for request in requests
        if request.get("candidate_order_matches_benchmark_order") is True
    )

    jobs = [
        {
            "ontology": request["ontology"],
            "ranked_candidate_ids": list(request["candidate_model_ids"]),
        }
        for request in requests
        if len(request["candidate_model_ids"]) >= 2
    ]

    print(f"\n=== Single-stage full-pool selector — {len(jobs)} calls, workers={workers} ===")
    fullpool_results: list[dict[str, Any]] = []
    t0 = time.time()

    def _run_one(job: dict[str, Any]) -> dict[str, Any]:
        ontology = job["ontology"]
        return _run_stage2_for_fullpool(
            client,
            model,
            ontology=ontology,
            ranked_candidate_ids=job["ranked_candidate_ids"],
            candidate_summaries=candidate_summary_by_ontology.get(ontology, {}),
            target_ancestry=target_ancestry_by_ontology.get(ontology),
            skill_context=skill_context_by_ontology.get(ontology, {}),
            objective=objective,
            general_biomedical_llm=general_biomedical_llm,
            usage_stage="single_stage_fullpool_judge",
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_one, job): job for job in jobs}
        done = 0
        for future in as_completed(futures):
            res = future.result()
            fullpool_results.append(res)
            done += 1
            status = "ok" if res["error"] is None else "ERR"
            print(f"  [fullpool {done}/{len(jobs)}] {status} {res['ontology']} -> {res.get('winner_model_id')}")
    print(f"Single-stage full-pool elapsed: {time.time() - t0:.1f}s")

    fullpool_results_path = output_run_dir / "experiment_pairwise_rerank_fullpool_results.json"
    fullpool_results_path.write_text(json.dumps(fullpool_results, indent=2), encoding="utf-8")

    fullpool_by_ontology = {res["ontology"]: res for res in fullpool_results}
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        result = fullpool_by_ontology.get(ontology) or {}
        if result.get("error"):
            error_map[custom_id] = result["error"]
            continue
        final_pick = result.get("winner_model_id")
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": "DIRECT_HIGH_QUALITY" if final_pick else "NO_MATCH_FOUND",
                "best_model_id": final_pick,
                "confidence": result.get("confidence") or "Moderate",
                "rationale": result.get("rationale") or "",
            }],
            "error": None,
        }

    without_domain.RESULTS_JSON = output_run_dir / "experiment_pairwise_rerank_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_pairwise_rerank_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_pairwise_rerank_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_pairwise_rerank_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_pairwise_rerank_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_errors.jsonl"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
    without_domain._configure_benchmark_sources(
        union_csv=manifest.get("union_csv"),
        ground_truth_dir=manifest.get("ground_truth_dir"),
    )

    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    candidate_range = _candidate_range_metadata(evaluator="fullpool_judge", top_k=None)
    summary["execution_mode"] = "single_stage_fullpool_chat_completions"
    summary["pairwise_rerank"] = {
        "evaluator": "fullpool_judge",
        "execution_architecture": "single_stage_fullpool",
        "legacy_two_stage_fullpool": False,
        "prompt_profile": "general_biomedical_llm" if general_biomedical_llm else "prs_agent_specialist",
        "objective": objective,
        "stage1_objective": stage1_objective,
        "stage1_count": 0,
        "stage2_count": 0,
        "single_stage_count": len(fullpool_results),
        "fullpool_count": len(fullpool_results),
        **candidate_range,
        "borda_revised_count": 0,
        "ontologies_with_invalid_ranked_alternatives": sum(
            1 for ids in ranked_candidates_by_ontology.values() if len(ids) < 2
        ),
        "borda_scores_by_ontology": {},
        "ranked_candidates_by_ontology": ranked_candidates_by_ontology,
        "top3_by_ontology": {
            ontology: ranked_candidates[:3]
            for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
        },
        "candidate_order_source": manifest.get("candidate_order") or (
            requests[0].get("candidate_order_source") if requests else None
        ),
        "candidate_order_seed": manifest.get("candidate_order_seed") or (
            requests[0].get("candidate_order_seed") if requests else None
        ),
        "candidate_order_matches_benchmark_count": candidate_order_matches_benchmark_count,
        "benchmark_top1_positions_by_ontology": benchmark_top1_positions_by_ontology,
        "audit_trace": {
            "enabled": False,
            "stages": [],
            "non_interventional": True,
        },
        "fullpool_results_path": str(fullpool_results_path),
    }
    cost = _summarize_usage_cost(model)
    if cost:
        summary["cost"] = cost
    _write_usage_records(output_run_dir)

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def _run_audit_trace(
    *,
    client: OpenAI,
    model: str,
    workers: int,
    enabled_stages: set[str],
    requests: list[dict[str, Any]],
    stage1_results: dict[str, dict[str, Any]],
    ranked_candidates_by_ontology: dict[str, list[str]],
    candidate_summary_by_ontology: dict[str, dict[str, dict[str, Any]]],
    skill_context_by_ontology: dict[str, dict[str, Any]],
    target_ancestry_by_ontology: dict[str, Optional[str]],
    final_pick_by_ontology: dict[str, Optional[str]],
    stage1_decision_by_ontology: dict[str, dict[str, Any]],
    topk_by_ontology: dict[str, dict[str, Any]],
    objective: str,
) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "non_interventional": True,
        "enabled_stages": sorted(enabled_stages),
        "stage1": [],
        "stage2": [],
    }
    if not enabled_stages:
        return trace

    if "stage1" in enabled_stages:
        stage1_jobs: list[dict[str, Any]] = []
        for request in requests:
            ontology = request["ontology"]
            stage1_jobs.append({
                "ontology": ontology,
                "target_ancestry": _target_ancestry_from_context_json(
                    (stage1_results.get(request["custom_id"]) or {}).get("context_json")
                ),
                "candidate_summaries": candidate_summary_by_ontology.get(ontology, {}),
                "stage1_decision": stage1_decision_by_ontology.get(ontology, {}),
                "skill_context": skill_context_by_ontology.get(ontology, {}),
            })
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(
                    _run_stage1_audit_trace,
                    client,
                    model,
                    ontology=job["ontology"],
                    target_ancestry=job["target_ancestry"],
                    candidate_summaries=job["candidate_summaries"],
                    stage1_decision=job["stage1_decision"],
                    skill_context=job["skill_context"],
                ): job
                for job in stage1_jobs
            }
            for future in as_completed(futures):
                trace["stage1"].append(future.result())

    if "stage2" in enabled_stages:
        stage2_jobs: list[dict[str, Any]] = []
        for ontology, ranked_candidate_ids in ranked_candidates_by_ontology.items():
            frozen_winner = final_pick_by_ontology.get(ontology)
            if not frozen_winner or len(ranked_candidate_ids) < 2:
                continue
            stage2_jobs.append({
                "ontology": ontology,
                "target_ancestry": target_ancestry_by_ontology.get(ontology),
                "ranked_candidate_ids": ranked_candidate_ids,
                "candidate_summaries": candidate_summary_by_ontology.get(ontology, {}),
                "skill_context": skill_context_by_ontology.get(ontology, {}),
                "frozen_winner_model_id": frozen_winner,
                "stage2_decision": topk_by_ontology.get(ontology) or {
                    "winner_model_id": frozen_winner,
                    "source": "pairwise_or_stage1_fallback",
                },
            })
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(
                    _run_stage2_for_topk_audit,
                    client,
                    model,
                    ontology=job["ontology"],
                    target_ancestry=job["target_ancestry"],
                    ranked_candidate_ids=job["ranked_candidate_ids"],
                    candidate_summaries=job["candidate_summaries"],
                    skill_context=job["skill_context"],
                    frozen_winner_model_id=job["frozen_winner_model_id"],
                    stage2_decision=job["stage2_decision"],
                    objective=objective,
                ): job
                for job in stage2_jobs
            }
            for future in as_completed(futures):
                trace["stage2"].append(future.result())

    return trace


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
    top_k: Optional[int] = None,
    evaluator: str,
    objective: str,
    stage1_objective: str,
    emit_audit_trace: bool = False,
    audit_stages: str = "both",
    legacy_two_stage_fullpool: bool = False,
) -> dict[str, Any]:
    if evaluator not in {"topk_judge", "fullpool_judge"}:
        raise _archived_surface_error(evaluator)
    if objective != "support" or stage1_objective != "support":
        raise _archived_surface_error("non_support_objective")
    if emit_audit_trace:
        raise _archived_surface_error("audit_trace")
    if legacy_two_stage_fullpool:
        raise _archived_surface_error("legacy_two_stage_fullpool")

    output_run_dir.mkdir(parents=True, exist_ok=True)
    _reset_usage_records()
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    general_biomedical_llm = _manifest_uses_general_biomedical_llm(manifest)
    if general_biomedical_llm:
        raise _archived_surface_error("general_biomedical_llm")
    single_stage_fullpool = evaluator == "fullpool_judge" and not legacy_two_stage_fullpool
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")
    print(
        "Prompt profile: "
        + ("general_biomedical_llm" if general_biomedical_llm else "prs_agent_specialist")
    )

    client = _client()

    if single_stage_fullpool:
        return _run_single_stage_fullpool_pipeline(
            client=client,
            manifest=manifest,
            requests=requests,
            output_run_dir=output_run_dir,
            model=model,
            workers=workers,
            objective=objective,
            stage1_objective=stage1_objective,
            general_biomedical_llm=general_biomedical_llm,
        )

    # Stage 1
    print(f"\n=== Stage 1 (ranked decision) — {len(requests)} requests, workers={workers} ===")
    stage1_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_stage1_for_request,
                client,
                model,
                request,
                top_k,
                stage1_objective,
                general_biomedical_llm,
            ): request
            for request in requests
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            stage1_results[res["custom_id"]] = res
            done += 1
            status = "ok" if res["error"] is None else "ERR"
            print(f"  [stage1 {done}/{len(requests)}] {status} {res['ontology']}")
    print(f"Stage 1 elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pairwise_rerank_stage1_results.json").write_text(
        json.dumps(list(stage1_results.values()), indent=2), encoding="utf-8"
    )

    # Build pairwise jobs from Stage 1 outputs
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    skill_context_by_ontology: dict[str, dict[str, Any]] = {}
    target_ancestry_by_ontology: dict[str, Optional[str]] = {}
    for request in requests:
        ontology = request["ontology"]
        if ontology in skill_context_by_ontology:
            continue
        # Extract skill_context from the original Stage 1 context JSON. Older
        # manifests are normalized by _skill_context_from_context.
        body = request["request"]["body"]
        original_user = body["messages"][1]["content"]
        raw_context_json = _json_payload_from_user_message(original_user)
        if raw_context_json is not None:
            try:
                ctx = json.loads(raw_context_json)
                skill_context_by_ontology[ontology] = (
                    {} if general_biomedical_llm else _skill_context_from_context(ctx)
                )
                value = ctx.get("target_ancestry")
                target_ancestry_by_ontology[ontology] = str(value).strip() if value else None
            except Exception:
                skill_context_by_ontology[ontology] = {}
                target_ancestry_by_ontology[ontology] = None
        else:
            skill_context_by_ontology[ontology] = {}
            target_ancestry_by_ontology[ontology] = None

    pairwise_jobs: list[dict[str, Any]] = []
    topk_jobs: list[dict[str, Any]] = []
    ranked_candidates_by_ontology: dict[str, list[str]] = {}
    stage1_decision_by_ontology: dict[str, dict[str, Any]] = {}
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        candidate_id_set = set(request["candidate_model_ids"])
        s1 = stage1_results.get(custom_id) or {}
        decision = s1.get("decision") or {}
        stage1_decision_by_ontology[ontology] = decision
        carried_candidates = _select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=candidate_id_set,
            top_k=top_k,
        )
        ranked_candidates = _order_stage2_candidate_ids_for_llm(
            ontology=ontology,
            ranked_candidate_ids=carried_candidates,
        )
        ranked_candidates_by_ontology[ontology] = ranked_candidates
        if evaluator == "fullpool_judge":
            ranked_candidates = list(request["candidate_model_ids"])
            ranked_candidates_by_ontology[ontology] = ranked_candidates
        if len(ranked_candidates) < 2:
            continue
        if evaluator == "pairwise":
            for i in range(len(ranked_candidates)):
                for j in range(i + 1, len(ranked_candidates)):
                    pairwise_jobs.append({
                        "ontology": ontology,
                        "candidate_a_id": ranked_candidates[i],
                        "candidate_b_id": ranked_candidates[j],
                    })
        elif evaluator in {"topk_judge", "topk_ranker", "fullpool_judge"}:
            topk_jobs.append({
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidates,
            })
        else:
            raise ValueError(f"Unknown evaluator: {evaluator}")

    pairwise_results: list[dict[str, Any]] = []
    topk_results: list[dict[str, Any]] = []
    t0 = time.time()

    def _run_one_pair(job: dict[str, Any]) -> dict[str, Any]:
        ontology = job["ontology"]
        a_id = job["candidate_a_id"]
        b_id = job["candidate_b_id"]
        cand_summaries = candidate_summary_by_ontology.get(ontology, {})
        return _run_stage2_for_pair(
            client,
            model,
            ontology=ontology,
            candidate_a_id=a_id,
            candidate_b_id=b_id,
            candidate_a_summary=cand_summaries.get(a_id, {"pgs_id": a_id, "missing": True}),
            candidate_b_summary=cand_summaries.get(b_id, {"pgs_id": b_id, "missing": True}),
            target_ancestry=target_ancestry_by_ontology.get(ontology),
            skill_context=skill_context_by_ontology.get(ontology, {}),
            objective=objective,
            general_biomedical_llm=general_biomedical_llm,
        )

    def _run_one_topk(job: dict[str, Any]) -> dict[str, Any]:
        ontology = job["ontology"]
        kwargs = {
            "client": client,
            "model": model,
            "ontology": ontology,
            "ranked_candidate_ids": job["ranked_candidate_ids"],
            "candidate_summaries": candidate_summary_by_ontology.get(ontology, {}),
            "target_ancestry": target_ancestry_by_ontology.get(ontology),
            "skill_context": skill_context_by_ontology.get(ontology, {}),
            "objective": objective,
            "general_biomedical_llm": general_biomedical_llm,
        }
        if evaluator == "topk_ranker":
            return _run_stage2_for_topk_ranker(**kwargs)
        if evaluator == "fullpool_judge":
            return _run_stage2_for_fullpool(**kwargs)
        return _run_stage2_for_topk(**kwargs)

    if evaluator == "pairwise":
        print(f"\n=== Stage 2 (pairwise) — {len(pairwise_jobs)} pair calls, workers={workers} ===")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_one_pair, job): job for job in pairwise_jobs}
            done = 0
            for future in as_completed(futures):
                res = future.result()
                pairwise_results.append(res)
                done += 1
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage2 {done}/{len(pairwise_jobs)}] {status} {res['ontology']} "
                      f"{res['candidate_a_id']} vs {res['candidate_b_id']} -> {res.get('winner_model_id')}")
    else:
        label = {
            "topk_ranker": "top-k ranker",
            "fullpool_judge": "full-pool judge",
        }.get(evaluator, "top-k judge")
        print(f"\n=== Stage 2 ({label}) — {len(topk_jobs)} shortlist calls, workers={workers} ===")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_one_topk, job): job for job in topk_jobs}
            done = 0
            for future in as_completed(futures):
                res = future.result()
                topk_results.append(res)
                done += 1
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage2 {done}/{len(topk_jobs)}] {status} {res['ontology']} "
                      f"-> {res.get('winner_model_id')}")
    print(f"Stage 2 elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pairwise_rerank_stage2_results.json").write_text(
        json.dumps(pairwise_results if evaluator == "pairwise" else topk_results, indent=2),
        encoding="utf-8"
    )

    # Aggregate via Borda
    pairwise_by_ontology: dict[str, list[dict[str, Any]]] = {}
    for res in pairwise_results:
        pairwise_by_ontology.setdefault(res["ontology"], []).append(res)

    final_pick_by_ontology: dict[str, Optional[str]] = {}
    borda_by_ontology: dict[str, dict[str, int]] = {}
    topk_by_ontology = {res["ontology"]: res for res in topk_results}
    for ontology, ranked_candidates in ranked_candidates_by_ontology.items():
        if len(ranked_candidates) < 2:
            stage1_pick = stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            final_pick_by_ontology[ontology] = stage1_pick
            borda_by_ontology[ontology] = {}
            continue
        if evaluator == "pairwise":
            winner, scores = _aggregate_borda(ranked_candidates, pairwise_by_ontology.get(ontology, []))
            final_pick_by_ontology[ontology] = winner
            borda_by_ontology[ontology] = scores
        else:
            topk_result = topk_by_ontology.get(ontology) or {}
            final_pick_by_ontology[ontology] = topk_result.get("winner_model_id") or ranked_candidates[0]
            borda_by_ontology[ontology] = {}

    enabled_audit_stages = _enabled_audit_stages(emit_audit_trace, audit_stages)
    audit_trace_path: Optional[Path] = None
    audit_trace_summary: dict[str, Any] = {
        "enabled": bool(enabled_audit_stages),
        "stages": sorted(enabled_audit_stages),
        "non_interventional": True,
    }
    if enabled_audit_stages:
        print(f"\n=== Audit trace (non-interventional) — stages={sorted(enabled_audit_stages)} ===")
        audit_trace = _run_audit_trace(
            client=client,
            model=model,
            workers=workers,
            enabled_stages=enabled_audit_stages,
            requests=requests,
            stage1_results=stage1_results,
            ranked_candidates_by_ontology=ranked_candidates_by_ontology,
            candidate_summary_by_ontology=candidate_summary_by_ontology,
            skill_context_by_ontology=skill_context_by_ontology,
            target_ancestry_by_ontology=target_ancestry_by_ontology,
            final_pick_by_ontology=final_pick_by_ontology,
            stage1_decision_by_ontology=stage1_decision_by_ontology,
            topk_by_ontology=topk_by_ontology,
            objective=objective,
        )
        audit_trace_path = output_run_dir / "experiment_pairwise_rerank_audit_trace.json"
        audit_trace_path.write_text(json.dumps(audit_trace, indent=2), encoding="utf-8")
        audit_trace_summary["path"] = str(audit_trace_path)
        audit_trace_summary["stage1_count"] = len(audit_trace.get("stage1") or [])
        audit_trace_summary["stage2_count"] = len(audit_trace.get("stage2") or [])

    # Build per-disease rows in the existing summary format. We need to feed
    # _build_summary_and_results-compatible parsed_outputs that produce a single
    # "trial" (trial=1) carrying the FINAL Borda-winner pick.
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        s1 = stage1_results.get(custom_id) or {}
        if s1.get("error"):
            error_map[custom_id] = s1["error"]
            continue
        final_pick = final_pick_by_ontology.get(ontology)
        decision = s1.get("decision") or {}
        # Reuse Stage 1's outcome / confidence labels if its best is the final pick;
        # otherwise mark as Borda-revised with the same outcome but Moderate confidence.
        outcome = decision.get("outcome") or "DIRECT_HIGH_QUALITY"
        confidence = decision.get("confidence") or "Moderate"
        rationale = decision.get("rationale") or ""
        if final_pick != decision.get("best_model_id"):
            confidence = "Moderate"
            rationale = (rationale + " | Borda re-rank promoted runner-up to primary.").strip()
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": outcome,
                "best_model_id": final_pick,
                "confidence": confidence,
                "rationale": rationale,
            }],
            "error": None,
        }

    # Wire the summary builder. To prevent NameError on without_domain global paths
    # we set them explicitly to point at our run directory.
    without_domain.RESULTS_JSON = output_run_dir / "experiment_pairwise_rerank_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_pairwise_rerank_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_pairwise_rerank_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_pairwise_rerank_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_pairwise_rerank_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_errors.jsonl"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
    # Configure benchmark sources to match the manifest
    union_csv = manifest.get("union_csv")
    ground_truth_dir = manifest.get("ground_truth_dir")
    without_domain._configure_benchmark_sources(
        union_csv=union_csv,
        ground_truth_dir=ground_truth_dir,
    )

    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    candidate_range = _candidate_range_metadata(evaluator=evaluator, top_k=top_k)
    summary["execution_mode"] = "pairwise_rerank_chat_completions"
    summary["pairwise_rerank"] = {
        "evaluator": evaluator,
        "execution_architecture": (
            "legacy_two_stage_fullpool"
            if evaluator == "fullpool_judge"
            else "two_stage_rerank"
        ),
        "legacy_two_stage_fullpool": evaluator == "fullpool_judge",
        "prompt_profile": "general_biomedical_llm" if general_biomedical_llm else "prs_agent_specialist",
        "objective": objective,
        "stage1_objective": stage1_objective,
        "stage1_count": len(stage1_results),
        "stage2_count": len(pairwise_results) if evaluator == "pairwise" else len(topk_results),
        "stage2_candidate_order_source": (
            STAGE2_CANDIDATE_ORDER_SOURCE if evaluator != "fullpool_judge" else None
        ),
        "stage2_candidate_order_seed": (
            STAGE2_CANDIDATE_ORDER_SEED if evaluator != "fullpool_judge" else None
        ),
        **candidate_range,
        "borda_revised_count": sum(
            1
            for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
            if (
                len(ranked_candidates) >= 2
                and final_pick_by_ontology.get(ontology) is not None
                and final_pick_by_ontology.get(ontology)
                    != stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            )
        ),
        "ontologies_with_invalid_ranked_alternatives": sum(
            1 for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
            if len(ranked_candidates) < 2
        ),
        "borda_scores_by_ontology": borda_by_ontology,
        "ranked_candidates_by_ontology": ranked_candidates_by_ontology,
        "top3_by_ontology": {
            ontology: ranked_candidates[:3]
            for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
        },
        "audit_trace": audit_trace_summary,
    }
    cost = _summarize_usage_cost(model)
    if cost:
        summary["cost"] = cost
    _write_usage_records(output_run_dir)

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def _parse_top_k(value: str) -> Optional[int]:
    """Map --top-k to None (production evidence-bound mode) or a positive
    integer (legacy fixed-count ablations)."""
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"", "all", "none", "0", "-1"}:
        return None
    parsed = int(text)
    return None if parsed <= 0 else parsed


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronous two-stage reranking for within-trait PGS selection")
    parser.add_argument("--manifest", type=str, required=True,
                        help="Path to an existing iterD-style batch manifest JSON")
    parser.add_argument("--run-tag", type=str, required=True,
                        help="Run tag suffix appended to the output run directory name")
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--top-k", type=_parse_top_k, default=None,
                        help="Candidate-set cap for Stage 2. Default 'all': the carried-forward set is "
                             "what the model ranked in contention, evidence-determined and validated "
                             f"at {STAGE1_MAX_CARRIED_CANDIDATES} carried candidates. An integer opts "
                             "a legacy ablation back into a fixed count.")
    parser.add_argument("--evaluator", choices=["topk_judge", "fullpool_judge"], default="topk_judge",
                        help="Retained evaluator: PRS Agent double-stage topk_judge or prompt-only/no-skill single-stage fullpool_judge.")
    parser.add_argument("--objective", choices=["support"], default="support",
                        help="Retained production objective framing.")
    parser.add_argument("--stage1-objective", choices=["support"],
                        default="support",
                        help="Retained Stage 1 shortlist objective.")
    parser.add_argument("--emit-audit-trace", action="store_true",
                        help="Archived; not available in the retained production prompt surface.")
    parser.add_argument("--audit-stages", choices=["stage1", "stage2", "both"], default="both",
                        help="Audit stages to emit when --emit-audit-trace is set.")
    parser.add_argument("--legacy-two-stage-fullpool", action="store_true",
                        help="Archived; not available in the retained production prompt surface.")
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    union_csv = manifest.get("union_csv")
    if union_csv:
        dataset_label = without_domain._dataset_label_from_union_path(Path(union_csv))
    else:
        dataset_label = f"{len(manifest.get('disease_metadata') or [])}disease"

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"pairwise-rerank-{args.model}-t1__{dataset_label}__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
        top_k=args.top_k,
        evaluator=args.evaluator,
        objective=args.objective,
        stage1_objective=args.stage1_objective,
        emit_audit_trace=args.emit_audit_trace,
        audit_stages=args.audit_stages,
        legacy_two_stage_fullpool=args.legacy_two_stage_fullpool,
    )
    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, "
              f"accuracy={v.get('accuracy')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
