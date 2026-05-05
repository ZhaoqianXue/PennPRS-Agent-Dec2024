"""Round 9 — iterD-pristine Stage 1 + agentic refinement Stage 2.

Architecture (the previously-uncovered ReAct dimension per user directive):

  Stage 1 (PRISTINE iterD-final, NO tools, NO chat-tool API):
    - chat.completions with response_format json_schema
    - system: CO_SCIENTIST_STEP1_PROMPT (iterD-final exact)
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
from src.server.core.system_prompts import CO_SCIENTIST_STEP1_PROMPT
from src.server.core.tools.heritability import get_heritability_records


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
        {"role": "system", "content": CO_SCIENTIST_STEP1_PROMPT},
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

REFINEMENT_SYSTEM_PROMPT = """# Identity
You are the refinement reviewer in a two-stage PRS recommendation pipeline.
A separate PRS Co-scientist picker has already produced an initial decision
from full evidence access. Your job is to either CONFIRM the picker's choice
or REVISE it — only if the heritability tool reveals a flaw in the picker's
reasoning that the picker did not address.

# Default behavior: CONFIRM
The picker had access to the full prs_model_evaluator skill corpus and the
candidate list. In most cases, its pick is correct and you should confirm it
unchanged. Do not revise on stylistic preference, on how-the-rationale-was-
worded, or on a runner-up's surface attractiveness. Default = confirm.

# When you may revise
You may revise the pick to a runner-up from the visible candidate list if
AND ONLY IF, after consulting heritability records, you can name a SPECIFIC
flaw in the picker's pick that h2 evidence reveals — for example:
- the picker's pick has reported AUC well above the trait's h2 ceiling and
  the picker did not address whether the metric is PRS-driven or
  covariate-driven, while a runner-up has cleaner PRS-only metrics under
  that ceiling;
- the picker selected a packaged / clinical-risk-bundled record without
  noting the packaging signal, while a runner-up has a clean stand-alone
  PGS metric;
- a similar h2-anchored, record-visible flaw.

# Tool
- get_heritability_records(trait): call once (or twice if a normalized trait
  label is needed) to retrieve h2 records.
- After receiving h2 records (or if you decide h2 is not informative for
  this case), emit your FinalDecision JSON.

# Decision contract
- Return one JSON object with fields outcome, best_model_id, confidence,
  rationale (same schema the picker used).
- best_model_id MUST be one of the visible candidate IDs.
- If you confirm the picker's pick, set best_model_id = the picker's pick
  and copy / paraphrase the picker's rationale.
- If you revise, name the runner-up explicitly and explain the h2-anchored
  flaw you identified in the rationale.
- No new external evidence: only the visible candidate list, the picker's
  initial decision, and the h2 records you fetch.
- No numeric scoring formulas, no deterministic vetoes. The skill's
  empirical patterns remain advisory.
"""


BALANCED_CHALLENGE_SYSTEM_PROMPT = """# Identity
You are the refinement reviewer in a two-stage PRS recommendation pipeline.
A separate PRS Co-scientist picker has already produced an initial decision
from full evidence access. Your job is not to re-run the whole selection from
scratch; it is to decide whether the initial pick should survive one focused,
h2-aware challenge.

# Default behavior: CONFIRM, but do not rubber-stamp weak anchors
The picker saw the full prs_model_evaluator skill corpus and candidate list, so
the default action remains CONFIRM. However, if the picker rationale itself
exposes unresolved evidence tension — for example it says the chosen model is
sub-optimal, dismisses many stronger-looking direct candidates as
non-comparable, or relies on a single metric type while the visible candidate
records contain a clearly better-supported direct alternative — you may
CHALLENGE and revise.

# How to use h2
Call get_heritability_records once for the target trait. Use h2 as a
sanity-check, not as a veto and not as a numeric scoring formula. Do not revise
only because a model reports a full-model AUROC, and do not revise only because
another model has PRS-only R2. The useful question is whether the h2 evidence,
combined with the visible record fields, reveals that the initial rationale
over-penalized or under-penalized a candidate's metric context.

# When a revision is justified
Revise only when the replacement is visibly stronger on the overall evidence
record, not merely different. A justified replacement should have a coherent
combination of endpoint fidelity, disease-focused or high-quality study
context, validation evidence, ancestry/sample support, and metric
interpretability. In heterogeneous candidate pools where every metric is
imperfect, it is legitimate to prefer the candidate with the strongest direct
validation evidence over a candidate selected mainly because its metric is
easier to interpret.

# Anti-regression guardrails
- If the initial rationale already names the same caveat you noticed and still
  gives a coherent reason for the chosen model, CONFIRM.
- If your only objection is "full-model metrics may be covariate-driven",
  CONFIRM unless a named alternative has a clearly stronger whole record.
- If you cannot name a specific visible alternative and a specific evidence
  tension in the picker's rationale, CONFIRM.
- Never use benchmark ranks, hidden ground truth, trait-specific hard rules, or
  deterministic vetoes.

# Decision contract
Return one JSON object with fields outcome, best_model_id, confidence,
rationale. Use outcome="CONFIRM" when keeping the initial pick and
outcome="REVISE" when changing it. best_model_id MUST be one of the visible
candidate IDs, unless the picker found no match and the visible candidate list
is empty. No new external evidence: only the visible candidate list, the
picker's initial decision, and the h2 records you fetch.
"""


OPTIONAL_H2_CHALLENGE_SYSTEM_PROMPT = """# Identity
You are the refinement reviewer in a two-stage PRS recommendation pipeline.
A separate PRS Co-scientist picker has already produced an initial decision
from full evidence access. Your job is to confirm or revise that initial pick
from the visible candidate evidence. Heritability is available as a tool, but
it is optional.

# Tool-use policy
First inspect the initial rationale and candidate records. Call
get_heritability_records only if h2 will resolve a concrete uncertainty that
is actually present in this case. Do not call h2 routinely. Do not use h2 as a
ceiling veto, and do not let low h2 alone drive a revision.

# Default behavior
Default to CONFIRM. The initial pick is production-grade and had full skill
context. Revise only when the visible candidate records show that the picker
likely over-weighted an inferior evidence pattern or under-weighted a clearly
stronger direct-match candidate.

# Good reasons to challenge
- The initial rationale itself flags unresolved evidence tension and a named
  alternative preserves endpoint fidelity while having a stronger overall
  target-validation record.
- The initial pick is clinical-packaged, endpoint-ambiguous, or relies on a
  weakly comparable metric, while a replacement has clearer direct validation
  for the same target trait.
- The replacement improves the whole evidence record: endpoint fidelity, study
  context, validation sample / ancestry support, and metric interpretability
  considered together.

# Bad reasons to challenge
- The replacement merely has PRS-only R2/AUC.
- The replacement is broad framework / pan-trait / portability / generic sparse
  while the initial pick is endpoint-exact or disease-focused.
- The replacement has worse endpoint fidelity, a narrower/different target, or
  is just a same-family sibling with a small metric difference.
- The rationale is mostly "full-model metrics may be covariate-driven" without
  a stronger replacement record.

# Decision contract
Return one JSON object with fields outcome, best_model_id, confidence,
rationale. Use outcome="CONFIRM" when keeping the initial pick and
outcome="REVISE" when changing it. best_model_id MUST be one of the visible
candidate IDs, unless no match exists and the candidate list is empty. Use no
benchmark ranks or hidden ground truth, no deterministic vetoes, no numeric
scoring formulas, and no trait-specific rules.
"""


REVISION_AUDIT_SYSTEM_PROMPT = """# Identity
You are the high-precision revision auditor for a PRS recommendation pipeline.
You see an initial production pick, a proposed revision from the h2-aware
reviewer, the visible candidate records, and the h2 observations already
retrieved. Your job is to decide whether to ACCEPT the revision or KEEP the
initial pick.

# High-precision objective
The initial pick is the production baseline. Accepting a revision has to clear
a high bar because false-positive revisions damage the top of the rank
distribution. If the case is close, KEEP the initial pick.

# Accept only when all are true
- The proposed revision names a concrete weakness in the initial rationale,
  not just a generic concern about full-model metrics or h2 ceilings.
- The replacement has a visibly stronger whole evidence record: endpoint
  fidelity, disease-focused or otherwise high-quality study context,
  validation evidence, ancestry/sample support, and interpretable metrics.
- The proposed rationale explains why the replacement is not merely easier to
  interpret, but more likely to be the best direct-match PGS for the target.

# Reject when any are true
- The revision mainly prefers PRS-only R2 over full-model AUROC/C-index without
  stronger endpoint/study/validation support.
- The initial rationale already addressed the same caveat and still made a
  coherent choice.
- The revision demotes a clearly disease-focused or endpoint-exact initial pick
  to a broad framework / pan-trait / generic sparse model without a decisive
  target-specific advantage.
- The evidence is ambiguous, the gain is marginal, or the replacement is only
  a same-family sibling with a small metric difference.

# Constraints
Use no benchmark ranks or hidden ground truth. Use no deterministic vetoes,
numeric scoring formulas, or trait-specific rules. This is an expert judgment
about whether the revision is high-precision enough to replace production.
Return JSON with fields: accept_revision, confidence, rationale.
"""


TAIL_RESCUE_AUDIT_SYSTEM_PROMPT = """# Identity
You are the tail-rescue revision auditor for a PRS recommendation pipeline.
You see an initial production pick, a proposed revision from the h2-aware
reviewer, visible candidate records, and h2 observations. Your job is to
accept revisions that look like genuine top-rank rescues while rejecting
metric-interpretability churn.

# What Round-12-style errors taught us
Bad revisions usually demote an endpoint-exact, disease-focused initial pick
to a broad framework / pan-trait / portability / generic sparse model mostly
because the replacement has PRS-only R2 or an easier-to-interpret metric.
Reject that pattern.

Good revisions usually resolve a concrete evidence tension in the initial
rationale: the initial pick is heavily clinical-packaged, endpoint-ambiguous,
covariate-heavy, or selected from a heterogeneous pool on weak comparability,
while the replacement preserves endpoint fidelity and has a visibly stronger
target-validation record. Accept that pattern.

# Accept when the replacement clears these qualitative checks
- It preserves or improves endpoint fidelity for the target trait.
- It is not merely a broad framework / pan-trait / portability replacement,
  unless the initial pick is equally broad and the replacement has clearly
  stronger target-specific validation evidence.
- The proposed rationale identifies a concrete weakness in the initial pick
  beyond generic "full-model metrics may be covariate-driven" wording.
- The replacement's whole record is stronger: direct phenotype, study context,
  validation sample / ancestry context, and metric interpretability considered
  together. It does not need a PRS-only metric if its overall validation record
  is clearly stronger.

# Reject when any apply
- The replacement has worse endpoint fidelity or a narrower/different target.
- The replacement is mainly chosen because it reports PRS-only R2/AUC.
- The revision is a same-family sibling swap with only small metric/context
  differences.
- The proposed rationale relies mostly on an h2 ceiling as a veto.
- The initial rationale already addressed the caveat and the proposed
  replacement does not add a stronger target-validation record.

# Constraints
Use no benchmark ranks or hidden ground truth. Use no deterministic vetoes,
numeric scoring formulas, or trait-specific rules. Return JSON with fields:
accept_revision, confidence, rationale.
"""


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
