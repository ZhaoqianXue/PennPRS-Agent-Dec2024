"""Round 9 — iterD-pristine Stage 1 + agentic refinement Stage 2.

Architecture (the previously-uncovered ReAct dimension per user directive):

  Stage 1 (PRISTINE iterD-final, NO tools, NO chat-tool API):
    - chat.completions with response_format json_schema
    - system: WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT (iterD-final exact)
    - user: iterD-mirror context with full_document = SKILL.md + all 9
            references (and optional heritability section, mirroring iterD)
    - output: Step1Decision = {outcome, best_model_id, confidence, rationale}
    - This stage REPLICATES iterD-final's evidence-shape and decision-channel
      via chat.completions surface, giving us an iterD-equivalent floor.

  Stage 2 (AGENTIC REFINEMENT — challenge or confirm):
    - chat.completions with response_format json_schema (FinalDecision schema)
    - tools: [get_heritability_records] only (per user directive)
    - system: refinement-specific instructions — DEFAULT IS TO CONFIRM the
              initial pick; revise only if h2 evidence reveals a flaw the
              picker may have missed.
    - user: same iterD-mirror context + the initial decision from Stage 1
    - LLM-decided termination: agent emits FinalDecision when ready
    - hard-cap: max 6 iterations (1 read of h2 + 1 emit is the typical case)

  Distinct from rounds 1-8:
    - Rounds 1-5 cold-start ReAct: agent had to discover both *what* skill
      sections to read and *which* candidate to pick. D1 confirmed gpt-5.2
      systematically under-fetches.
    - Rounds 6-8 inline-skill ReAct: agent had full priming but ALSO had to
      make the initial pick from scratch in a multi-turn chat. D7 confirmed
      a residual ~3.4pp cost from this multi-turn cost vs single-shot.
    - Round 9 SEPARATES priming + initial pick (Stage 1, pristine single-shot)
      from the refinement decision (Stage 2). Stage 2 inherits an iterD-grade
      anchor and only adds an h2-grounded challenge layer. The agentic surface
      is bounded to "challenge or confirm", not "make a pick from scratch".

  Round 9 success path:
    - Stage 1 alone is iterD-equivalent → H1 floor ≈ 0.3371.
    - Stage 2 occasionally revises a wrong pick to a better runner-up via h2
      sanity-check → +N hits.
    - Need net +3 hits (above iterD) for N=1 ≥ 0.3671 gate.

LLM: gpt-5.2, temperature=0, seed=42 (matches iterD-final).
N=1 gate first; N=2 confirm only if N=1 ≥ 0.3671 (per user efficiency patch).

Output: schema-compatible with run_experiment_without_domain.py — written to
runs/react-refinement-... and consumable by per-disease tooling unchanged.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from experiments.contribution2.recommendation.scripts.run_experiment_minimal_lift import (
    _format_heritability_section,
)
from src.server.core.system_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
from src.server.core.tools.heritability import get_heritability_records
from src.server.core.within_prompts.archive.audits_pre_cleanup_20260615 import (
    WITHIN_REVISION_AUDIT_SYSTEM_PROMPT,
    WITHIN_TAIL_RESCUE_AUDIT_SYSTEM_PROMPT,
)
from src.server.core.within_prompts.archive.selectors_pre_cleanup_20260615 import (
    WITHIN_BALANCED_CHALLENGE_SYSTEM_PROMPT,
    WITHIN_OPTIONAL_H2_CHALLENGE_SYSTEM_PROMPT,
    WITHIN_REFINEMENT_SYSTEM_PROMPT,
)


# ---------------------------------------------------------------------------
# Skill assembly (same as react_agent.py)
# ---------------------------------------------------------------------------

SKILL_DIR = PROJECT_ROOT / "src" / "server" / "core" / "skills" / "prs_model_evaluator"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"
REFERENCE_DIR = SKILL_DIR / "reference"

REFERENCE_FILES = [
    "00_preamble.md",
    "01_trait_reported_trait_efo_phenotyping_reported.md",
    "02_performance_metrics_auc_performance_metrics_r2_covariates.md",
    "03_validation_sample_size.md",
    "04_training_development_cohorts_samples_training_ancestry_distr.md",
    "05_method_name.md",
    "06_publication_title_publication_journal_date_release.md",
    "07_variants_number.md",
    "08_cross_trait_transfer_considerations.md",
]


def _build_full_skill_corpus() -> str:
    parts: list[str] = [SKILL_MD_PATH.read_text(encoding="utf-8")]
    for fname in REFERENCE_FILES:
        path = REFERENCE_DIR / fname
        try:
            parts.append(f"\n\n# ============= reference: {fname} =============\n\n"
                         + path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return "".join(parts)


_FULL_SKILL_CORPUS = _build_full_skill_corpus()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class Step1Decision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


class FinalDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


class RevisionAuditDecision(BaseModel):
    accept_revision: bool
    confidence: str
    rationale: str


def _stage1_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1Decision),
        },
    }


def _final_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "final_decision",
            "strict": True,
            "schema": to_strict_json_schema(FinalDecision),
        },
    }


def _revision_audit_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "revision_audit_decision",
            "strict": True,
            "schema": to_strict_json_schema(RevisionAuditDecision),
        },
    }


# ---------------------------------------------------------------------------
# h2 tool (the only LLM-callable tool in Stage 2)
# ---------------------------------------------------------------------------

def _h2_tool_schema() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_heritability_records",
            "description": (
                "Tool to look up local heritability (h2) records for the target trait. "
                "Use when reviewing the picker's initial decision: the trait's h2 "
                "ceiling is the single most useful sanity-check for whether a "
                "candidate's reported AUC is PRS-driven or covariate-driven, and the "
                "procedural overview's Sanity-check usage rules apply. Returns up to "
                "~20 records ranked by source / sample size, restricted to EUR. "
                "Each record has trait_name, h2 (observed), h2_liability, h2_se, "
                "h2_z, n_samples, source, ancestry, match_score. If no records "
                "match, returns an empty list."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "trait": {
                        "type": "string",
                        "description": "The target trait name (free text). Pass the trait verbatim from the user message.",
                    }
                },
                "required": ["trait"],
                "additionalProperties": False,
            },
        },
    }


def _h2_call_safe(trait: str) -> str:
    try:
        records = get_heritability_records(trait, ancestry="EUR")
        return _format_heritability_section(trait, records or [])
    except Exception as exc:
        return json.dumps({"trait": trait, "error": f"{type(exc).__name__}: {exc}"})


# ---------------------------------------------------------------------------
# Stage 1 — pristine iterD single-shot via chat.completions
# ---------------------------------------------------------------------------

def _stage1_user_message(target_trait: str, candidate_models: list[dict[str, Any]]) -> str:
    payload = {
        "target_trait": target_trait,
        "direct_models": {
            "query_trait": target_trait,
            "total_found": len(candidate_models),
            "after_filter": len(candidate_models),
            "models": candidate_models,
        },
        "domain_knowledge": {
            "query": target_trait,
            "full_document": _FULL_SKILL_CORPUS,
            "snippets": [],
            "source_type": "local",
        },
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }
    return (
        "Perform direct-match assessment only. Use the context JSON below to "
        "select the best supported direct-match candidate and return exactly "
        "one JSON object with fields: outcome, best_model_id, confidence, "
        "rationale.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _run_stage1(
    client: OpenAI,
    *,
    model: str,
    target_trait: str,
    candidate_models: list[dict[str, Any]],
    temperature: float,
    seed: int,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT},
        {"role": "user", "content": _stage1_user_message(target_trait, candidate_models)},
    ]
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
        "response_format": _stage1_response_format(),
    }
    response = client.chat.completions.create(**body)
    content = response.choices[0].message.content
    if isinstance(content, list):
        content = "".join(item.get("text", "") for item in content if isinstance(item, dict))
    decision = Step1Decision.model_validate_json((content or "").strip())
    return decision.model_dump()


# ---------------------------------------------------------------------------
# Stage 2 — agentic refinement (challenge or confirm)
# ---------------------------------------------------------------------------

REFINEMENT_SYSTEM_PROMPT = WITHIN_REFINEMENT_SYSTEM_PROMPT



BALANCED_CHALLENGE_SYSTEM_PROMPT = WITHIN_BALANCED_CHALLENGE_SYSTEM_PROMPT



OPTIONAL_H2_CHALLENGE_SYSTEM_PROMPT = WITHIN_OPTIONAL_H2_CHALLENGE_SYSTEM_PROMPT



REVISION_AUDIT_SYSTEM_PROMPT = WITHIN_REVISION_AUDIT_SYSTEM_PROMPT



TAIL_RESCUE_AUDIT_SYSTEM_PROMPT = WITHIN_TAIL_RESCUE_AUDIT_SYSTEM_PROMPT



def _revision_audit_system_prompt(mode: str) -> str:
    if mode == "high_precision":
        return REVISION_AUDIT_SYSTEM_PROMPT
    if mode == "tail_rescue":
        return TAIL_RESCUE_AUDIT_SYSTEM_PROMPT
    raise ValueError(f"Unknown revision audit mode: {mode}")


def _refinement_system_prompt(mode: str) -> str:
    if mode == "balanced_challenge":
        return BALANCED_CHALLENGE_SYSTEM_PROMPT
    if mode == "optional_h2_challenge":
        return OPTIONAL_H2_CHALLENGE_SYSTEM_PROMPT
    if mode != "default":
        raise ValueError(f"Unknown refinement mode: {mode}")
    return REFINEMENT_SYSTEM_PROMPT


def _stage2_user_message(
    target_trait: str,
    candidate_models: list[dict[str, Any]],
    initial_decision: dict[str, Any],
) -> str:
    payload = {
        "target_trait": target_trait,
        "direct_models": {
            "query_trait": target_trait,
            "total_found": len(candidate_models),
            "after_filter": len(candidate_models),
            "models": candidate_models,
        },
        "domain_knowledge": {
            "query": target_trait,
            "full_document": _FULL_SKILL_CORPUS,
            "snippets": [],
            "source_type": "local",
        },
        "initial_decision_from_picker": initial_decision,
    }
    return (
        "Review the picker's initial decision. Default action: CONFIRM. You "
        "may call get_heritability_records exactly when h2 evidence is needed "
        "to validate or challenge the picker's choice. After h2 (or if h2 is "
        "not needed for this case), emit your FinalDecision JSON.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _run_stage2(
    client: OpenAI,
    *,
    model: str,
    target_trait: str,
    candidate_models: list[dict[str, Any]],
    initial_decision: dict[str, Any],
    temperature: float,
    seed: int,
    max_iterations: int,
    refinement_mode: str,
) -> dict[str, Any]:
    candidate_id_set = {str(m.get("id")) for m in candidate_models if m.get("id")}
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": _refinement_system_prompt(refinement_mode)},
        {"role": "user", "content": _stage2_user_message(target_trait, candidate_models, initial_decision)},
    ]
    tools = [_h2_tool_schema()]
    tool_call_log: list[dict[str, Any]] = []
    last_error: Optional[str] = None
    final_decision: Optional[dict[str, Any]] = None

    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                seed=seed,
                response_format=_final_response_format(),
            )
        except Exception as exc:
            last_error = f"Stage2 LLM call iter={iteration}: {type(exc).__name__}: {exc}"
            break

        choice = response.choices[0]
        msg = choice.message
        assistant_msg: dict[str, Any] = {"role": "assistant"}
        if msg.content:
            assistant_msg["content"] = msg.content if isinstance(msg.content, str) else str(msg.content)
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)
        tool_calls = assistant_msg.get("tool_calls") or []

        if not tool_calls:
            content = assistant_msg.get("content") or ""
            try:
                parsed = FinalDecision.model_validate_json(content).model_dump()
            except Exception as exc:
                last_error = f"Stage2 JSON parse failed iter={iteration}: {type(exc).__name__}: {exc}"
                tool_call_log.append({
                    "iteration": iteration,
                    "kind": "json_parse_error",
                    "content_preview": content[:200],
                })
                break
            if parsed.get("outcome") == "NO_MATCH_FOUND":
                parsed["best_model_id"] = None
            else:
                bid = parsed.get("best_model_id")
                if not bid or str(bid).strip() not in candidate_id_set:
                    last_error = f"Stage2 best_model_id '{bid}' not in candidate list."
                    tool_call_log.append({
                        "iteration": iteration,
                        "kind": "invalid_pick",
                        "content_preview": content[:200],
                    })
                    break
            final_decision = parsed
            tool_call_log.append({
                "iteration": iteration,
                "kind": "json_terminal",
                "content_preview": content[:200],
            })
            break

        for tc in tool_calls:
            fn = tc["function"]
            name = fn["name"]
            args = fn.get("arguments", "{}")
            if name != "get_heritability_records":
                obs = f"ERROR: unknown tool '{name}'."
            else:
                try:
                    parsed_args = json.loads(args) if args else {}
                except Exception as exc:
                    obs = f"ERROR parsing arguments: {type(exc).__name__}: {exc}"
                else:
                    trait_arg = str(parsed_args.get("trait") or target_trait).strip()
                    obs = _h2_call_safe(trait_arg)
            tool_call_log.append({
                "iteration": iteration,
                "tool_name": name,
                "arguments": args,
                "observation_preview": obs[:200],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": obs,
            })

    return {
        "decision": final_decision,
        "tool_call_log": tool_call_log,
        "iterations_used": len(tool_call_log),
        "error": last_error,
    }


def _run_revision_audit(
    client: OpenAI,
    *,
    model: str,
    target_trait: str,
    candidate_models: list[dict[str, Any]],
    initial_decision: dict[str, Any],
    proposed_decision: dict[str, Any],
    tool_call_log: list[dict[str, Any]],
    temperature: float,
    seed: int,
    revision_audit_mode: str,
) -> dict[str, Any]:
    h2_observations = [
        {
            "arguments": entry.get("arguments"),
            "observation_preview": entry.get("observation_preview"),
        }
        for entry in tool_call_log
        if entry.get("tool_name") == "get_heritability_records"
    ]
    payload = {
        "target_trait": target_trait,
        "direct_models": {
            "query_trait": target_trait,
            "total_found": len(candidate_models),
            "after_filter": len(candidate_models),
            "models": candidate_models,
        },
        "initial_decision_from_picker": initial_decision,
        "proposed_revision_from_reviewer": proposed_decision,
        "h2_observations": h2_observations,
    }
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _revision_audit_system_prompt(revision_audit_mode)},
            {
                "role": "user",
                "content": (
                    "Audit the proposed revision. Accept it only if it clears "
                    "the high-precision bar; otherwise keep the initial pick.\n\n"
                    f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
                ),
            },
        ],
        temperature=temperature,
        seed=seed,
        response_format=_revision_audit_response_format(),
    )
    content = response.choices[0].message.content
    if isinstance(content, list):
        content = "".join(item.get("text", "") for item in content if isinstance(item, dict))
    parsed = RevisionAuditDecision.model_validate_json((content or "").strip()).model_dump()
    return parsed


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in disease_metadata:
        out[row["ontology"]] = list(row.get("candidate_models_visible_to_llm") or [])
    return out


def _run_one_request(
    client: OpenAI,
    *,
    model: str,
    request: dict[str, Any],
    candidate_summary_by_ontology: dict[str, list[dict[str, Any]]],
    temperature: float,
    seed: int,
    max_iterations: int,
    refinement_mode: str,
    revision_audit_mode: str,
    stage1_prefill_by_ontology: Optional[dict[str, dict[str, Any]]] = None,
) -> dict[str, Any]:
    custom_id = request["custom_id"]
    ontology = request["ontology"]
    candidate_models = candidate_summary_by_ontology.get(ontology, [])
    try:
        if stage1_prefill_by_ontology is not None and ontology in stage1_prefill_by_ontology:
            initial_decision = stage1_prefill_by_ontology[ontology]
        else:
            initial_decision = _run_stage1(
                client,
                model=model,
                target_trait=ontology,
                candidate_models=candidate_models,
                temperature=temperature,
                seed=seed,
            )
        # Validate Stage 1 best_model_id. If invalid, skip Stage 2 and return.
        candidate_id_set = {str(m.get("id")) for m in candidate_models if m.get("id")}
        s1_pick = initial_decision.get("best_model_id")
        if s1_pick is not None and str(s1_pick).strip() not in candidate_id_set:
            return {
                "custom_id": custom_id,
                "ontology": ontology,
                "initial_decision": initial_decision,
                "final_decision": initial_decision,
                "tool_call_log": [],
                "stage2_used": False,
                "error": f"Stage1 best_model_id '{s1_pick}' not in candidate list",
            }

        stage2_result = _run_stage2(
            client,
            model=model,
            target_trait=ontology,
            candidate_models=candidate_models,
            initial_decision=initial_decision,
            temperature=temperature,
            seed=seed,
            max_iterations=max_iterations,
            refinement_mode=refinement_mode,
        )
        final_decision = stage2_result["decision"]
        if final_decision is None:
            # Stage 2 failed; fall back to Stage 1's decision.
            return {
                "custom_id": custom_id,
                "ontology": ontology,
                "initial_decision": initial_decision,
                "final_decision": initial_decision,
                "tool_call_log": stage2_result["tool_call_log"],
                "iterations_used": stage2_result["iterations_used"],
                "stage2_used": True,
                "stage2_failed": True,
                "error": stage2_result.get("error") or "Stage2 produced no decision; fallback to Stage1",
            }

        revision_audit: Optional[dict[str, Any]] = None
        if (
            revision_audit_mode != "none"
            and final_decision.get("best_model_id") != initial_decision.get("best_model_id")
        ):
            try:
                revision_audit = _run_revision_audit(
                    client,
                    model=model,
                    target_trait=ontology,
                    candidate_models=candidate_models,
                    initial_decision=initial_decision,
                    proposed_decision=final_decision,
                    tool_call_log=stage2_result["tool_call_log"],
                    temperature=temperature,
                    seed=seed,
                    revision_audit_mode=revision_audit_mode,
                )
            except Exception as exc:
                revision_audit = {
                    "accept_revision": False,
                    "confidence": "Low",
                    "rationale": f"Revision audit failed: {type(exc).__name__}: {exc}",
                }
            if not revision_audit.get("accept_revision"):
                final_decision = dict(initial_decision)
                final_decision["rationale"] = (
                    f"{initial_decision.get('rationale', '')}\n\n"
                    f"Revision audit rejected proposed revision: {revision_audit.get('rationale', '')}"
                ).strip()

        return {
            "custom_id": custom_id,
            "ontology": ontology,
            "initial_decision": initial_decision,
            "final_decision": final_decision,
            "revision_audit": revision_audit,
            "tool_call_log": stage2_result["tool_call_log"],
            "iterations_used": stage2_result["iterations_used"],
            "stage2_used": True,
            "stage2_failed": False,
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": ontology,
            "initial_decision": None,
            "final_decision": None,
            "tool_call_log": [],
            "stage2_used": False,
            "error": f"orchestration {type(exc).__name__}: {exc}",
        }


def _build_stage1_prefill_from_iterd(
    iterd_summary_path: Path,
    iterd_results_path: Optional[Path] = None,
) -> dict[str, dict[str, Any]]:
    """Round 10/11 lever: pre-fill Stage 1's initial_decision from a previously
    recorded iterD-final summary. Eliminates the chat.completions vs Batch API
    surface noise (~10-15 / 89 picks differ on the same prompt) so Stage 2's
    agentic refinement is anchored at the iterD H1 floor (0.3371) rather than
    iterD-via-chat.completions floor (~0.3034).

    Round 11 lever (iterd_results_path): also load iterD's actual per-trial
    rationale and outcome / confidence, so Stage 2 sees the picker's real
    reasoning — not a placeholder. Round 10 N=1 with empty rationale showed
    Stage 2 over-revised (14 revisions, net -6 H1) because the critic had
    nothing to anchor on. Round 11 hypothesis: a real anchor restores the
    "default = confirm" discipline.
    """
    summary = json.loads(iterd_summary_path.read_text(encoding="utf-8"))
    rationale_by_ontology: dict[str, dict[str, Any]] = {}
    if iterd_results_path is not None and iterd_results_path.exists():
        results = json.loads(iterd_results_path.read_text(encoding="utf-8"))
        for row in results:
            o = row.get("ontology")
            if o and row.get("trial") == 1:
                rationale_by_ontology[o] = {
                    "outcome": row.get("recommendation_type") or "DIRECT_HIGH_QUALITY",
                    "confidence": row.get("recommendation_confidence") or "Moderate",
                    "rationale": row.get("rationale") or "",
                }

    out: dict[str, dict[str, Any]] = {}
    for pd in summary.get("per_disease") or []:
        ontology = pd.get("ontology")
        pick = pd.get("modal_recommendation")
        meta = rationale_by_ontology.get(ontology, {})
        outcome = meta.get("outcome") or ("DIRECT_HIGH_QUALITY" if pick else "NO_MATCH_FOUND")
        confidence = meta.get("confidence") or "Moderate"
        rationale = meta.get("rationale") or "(initial pick pre-filled from iterD-final recorded summary)"
        out[ontology] = {
            "outcome": outcome,
            "best_model_id": pick,
            "confidence": confidence,
            "rationale": rationale,
        }
    return out


def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
    temperature: float,
    seed: int,
    max_iterations: int,
    refinement_mode: str,
    revision_audit_mode: str,
    stage1_prefill_summary: Optional[Path] = None,
    stage1_prefill_results: Optional[Path] = None,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])

    stage1_prefill_by_ontology: Optional[dict[str, dict[str, Any]]] = None
    if stage1_prefill_summary is not None:
        stage1_prefill_by_ontology = _build_stage1_prefill_from_iterd(
            stage1_prefill_summary,
            stage1_prefill_results,
        )
        print(f"Stage 1 PREFILL loaded from {stage1_prefill_summary} "
              f"({len(stage1_prefill_by_ontology)} ontologies)")
        if stage1_prefill_results is not None:
            print(f"Stage 1 PREFILL rationales loaded from {stage1_prefill_results}")

    client = _client()

    print(f"\n=== Round 9 — Stage1 (iterD pristine) + Stage2 (agentic refinement) "
          f"— {len(requests)} ontologies, workers={workers}, max_iters={max_iterations} ===")
    results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_one_request,
                client,
                model=model,
                request=request,
                candidate_summary_by_ontology=candidate_summary_by_ontology,
                temperature=temperature,
                seed=seed,
                max_iterations=max_iterations,
                refinement_mode=refinement_mode,
                revision_audit_mode=revision_audit_mode,
                stage1_prefill_by_ontology=stage1_prefill_by_ontology,
            ): request
            for request in requests
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            results[res["custom_id"]] = res
            done += 1
            if done % 20 == 0 or done == len(requests):
                status = "ok" if res["error"] is None else "ERR"
                init_pick = (res.get("initial_decision") or {}).get("best_model_id")
                final_pick = (res.get("final_decision") or {}).get("best_model_id")
                revised = init_pick != final_pick
                rev_marker = "REV" if revised else "ok"
                print(f"  [{done}/{len(requests)}] {status} {res['ontology']} "
                      f"({rev_marker}: {init_pick} -> {final_pick})")
    print(f"Elapsed: {time.time() - t0:.1f}s")

    (output_run_dir / "experiment_react_refinement_full_results.json").write_text(
        json.dumps(list(results.values()), indent=2), encoding="utf-8"
    )

    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    revised_count = 0
    proposed_revision_count = 0
    audit_accepted_count = 0
    audit_rejected_count = 0
    stage2_failed_count = 0
    h2_call_count = 0
    for request in requests:
        custom_id = request["custom_id"]
        res = results.get(custom_id) or {}
        if res.get("error") and res.get("final_decision") is None:
            error_map[custom_id] = res["error"]
            continue
        decision = res.get("final_decision") or res.get("initial_decision")
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [decision],
            "error": None,
        }
        init_pick = (res.get("initial_decision") or {}).get("best_model_id")
        final_pick = (res.get("final_decision") or {}).get("best_model_id")
        if init_pick != final_pick:
            revised_count += 1
        audit = res.get("revision_audit")
        if audit is not None:
            proposed_revision_count += 1
            if audit.get("accept_revision"):
                audit_accepted_count += 1
            else:
                audit_rejected_count += 1
        if res.get("stage2_failed"):
            stage2_failed_count += 1
        for entry in res.get("tool_call_log") or []:
            if entry.get("tool_name") == "get_heritability_records":
                h2_call_count += 1

    without_domain.RESULTS_JSON = output_run_dir / "experiment_react_refinement_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_react_refinement_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_react_refinement_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_react_refinement_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_react_refinement_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_react_refinement_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_react_refinement_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_react_refinement_batch_errors.jsonl"
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
    summary["execution_mode"] = "react_refinement_chat_completions"
    summary["react_refinement"] = {
        "total_ontologies": len(requests),
        "stage2_revised_count": revised_count,
        "stage2_proposed_revision_count": proposed_revision_count,
        "revision_audit_accepted_count": audit_accepted_count,
        "revision_audit_rejected_count": audit_rejected_count,
        "stage2_failed_count": stage2_failed_count,
        "h2_call_count": h2_call_count,
        "refinement_mode": refinement_mode,
        "revision_audit_mode": revision_audit_mode,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Round 9 — iterD Stage1 + agentic refinement Stage2")
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-iterations", type=int, default=6)
    parser.add_argument("--refinement-mode", choices=["default", "balanced_challenge", "optional_h2_challenge"],
                        default="default",
                        help="Stage 2 reviewer prompt family. 'default' is the "
                        "Round 9-11 conservative h2-flaw reviewer. "
                        "'balanced_challenge' is the Round 12 reviewer that treats "
                        "h2 as a sanity-check rather than a metric veto and allows "
                        "revision when the initial rationale exposes unresolved "
                        "evidence tension.")
    parser.add_argument("--revision-audit-mode", choices=["none", "high_precision", "tail_rescue"],
                        default="none",
                        help="Optional Round 13 high-precision audit for proposed "
                        "Stage 2 revisions. 'none' keeps Stage 2 as-is. "
                        "'high_precision' asks a second same-agent audit call to "
                        "accept or reject only proposed revisions, falling back to "
                        "the production initial pick when rejected. 'tail_rescue' "
                        "is the Round 14 audit tuned from Round 12/13 diagnostics "
                        "to preserve genuine tail rescues while rejecting "
                        "metric-interpretability churn.")
    parser.add_argument("--stage1-prefill-summary", type=str, default=None,
                        help="Round 10 lever: path to a recorded iterD-final summary "
                        "JSON. When provided, Stage 1's initial_decision is pre-filled "
                        "from per_disease[*].modal_recommendation (no Stage 1 LLM call). "
                        "This anchors Stage 2 at iterD's H1 floor (0.3371) and isolates "
                        "the agentic refinement layer's true lift.")
    parser.add_argument("--stage1-prefill-results", type=str, default=None,
                        help="Round 11 lever: optional path to the matching iterD-final "
                        "experiment_minimal_lift_results.json. When provided alongside "
                        "--stage1-prefill-summary, Stage 2 sees the recorded picker "
                        "rationale / confidence instead of an empty placeholder.")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"react-refinement-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
        temperature=args.temperature,
        seed=args.seed,
        max_iterations=args.max_iterations,
        refinement_mode=args.refinement_mode,
        revision_audit_mode=args.revision_audit_mode,
        stage1_prefill_summary=Path(args.stage1_prefill_summary) if args.stage1_prefill_summary else None,
        stage1_prefill_results=Path(args.stage1_prefill_results) if args.stage1_prefill_results else None,
    )
    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, "
              f"accuracy={v.get('accuracy')}")
    rr = summary.get("react_refinement") or {}
    print(f"\nrefinement meta: revised={rr.get('stage2_revised_count')}, "
          f"stage2_failed={rr.get('stage2_failed_count')}, h2_calls={rr.get('h2_call_count')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
