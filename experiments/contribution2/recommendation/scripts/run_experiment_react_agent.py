"""ReAct agent harness for c2 same-trait PGS selection.

Architecture (Round 1 of the c2 ReAct pivot):
  - True single-agent ReAct loop. The LLM autonomously decides when to read
    `prs_model_evaluator/SKILL.md` sections, when to call
    `get_heritability_records`, and when to terminate via
    `submit_recommendation`. No pre-fed 55K corpus, no pre-injected
    heritability section. Just-in-time evidence consultation.
  - 3 tools (intentionally minimal per Lance Martin "just enough agent"):
      1. read_skill_section(section_id)
      2. get_heritability_records(trait)
      3. submit_recommendation(best_model_id, confidence, rationale)
  - Section IDs are self-documenting and listed exhaustively in the tool
    description (per LangGraph: detailed tool descriptions yield ~25 % better
    selection accuracy).
  - LLM-decided termination via submit_recommendation; hard cap at
    `--max-iterations` to bound hallucinated-tool loops (LangGraph default 25;
    we use 12 — enough for several reads + h2 + submit).
  - Tool errors are returned as structured ToolMessage observations rather
    than raised, so the agent can self-correct (LangGraph anti-pattern fix:
    exception-based failure terminates the agent unhelpfully).
  - LLM: gpt-5.2 t=0 seed=42 (matches iterD-final).
  - Output schema-compatible with run_experiment_without_domain.py so that
    the existing summary / report / per-disease tooling consumes it
    unchanged.

Sources for design (all 2026):
  - Anthropic — Building Effective Agents
  - Anthropic — Effective Context Engineering for AI Agents
  - LangGraph TypeScript ReAct agent guide
  - Lance Martin — Agent Design (Jan 2026)
  - Composio — How to build tools for AI agents (a field guide)
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

# Register minimal_lift's wd patches so wd's manifests / paths align.
from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.tools.heritability import get_heritability_records


# ---------------------------------------------------------------------------
# Section addressing for the prs_model_evaluator skill (sealed)
# ---------------------------------------------------------------------------

SKILL_DIR = PROJECT_ROOT / "src" / "server" / "core" / "skills" / "prs_model_evaluator"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"
REFERENCE_DIR = SKILL_DIR / "reference"

# Section ID -> (file_path, one-line summary used in the tool description)
SECTION_INDEX: dict[str, tuple[Path, str]] = {
    "skill_overview": (
        SKILL_MD_PATH,
        "Procedural overview of how to evaluate PGS Catalog records: when to invoke, "
        "the seven-factor consideration list, role boundary, transfer caveat, "
        "table of contents to all reference sections.",
    ),
    "preamble": (
        REFERENCE_DIR / "00_preamble.md",
        "Cross-cutting empirical patterns and factor-importance rules.",
    ),
    "trait_labels": (
        REFERENCE_DIR / "01_trait_reported_trait_efo_phenotyping_reported.md",
        "Endpoint-fidelity rules across the three trait label fields "
        "(trait_reported, trait_efo, phenotyping_reported).",
    ),
    "performance_metrics": (
        REFERENCE_DIR / "02_performance_metrics_auc_performance_metrics_r2_covariates.md",
        "Comparable-metrics handling, the covariate-leakage / packaging catalogue, "
        "PRS-only AUC vs full-model AUC distinctions.",
    ),
    "validation_sample_size": (
        REFERENCE_DIR / "03_validation_sample_size.md",
        "When validation N is informative and when it isn't.",
    ),
    "training_cohorts_ancestry": (
        REFERENCE_DIR / "04_training_development_cohorts_samples_training_ancestry_distr.md",
        "Training-cohort, samples_training, and ancestry-transportability patterns.",
    ),
    "method_name": (
        REFERENCE_DIR / "05_method_name.md",
        "Method-family considerations.",
    ),
    "publication_context": (
        REFERENCE_DIR / "06_publication_title_publication_journal_date_release.md",
        "Publication-context weak signals (title, journal, release date).",
    ),
    "variants_number": (
        REFERENCE_DIR / "07_variants_number.md",
        "Variant-count considerations.",
    ),
    "cross_trait_transfer": (
        REFERENCE_DIR / "08_cross_trait_transfer_considerations.md",
        "Source-bundle plausibility and transferability heuristics.",
    ),
}

VALID_SECTION_IDS: list[str] = list(SECTION_INDEX.keys()) + ["decision_core", "all_references"]


def _read_skill_section(section_id: str) -> str:
    if section_id == "decision_core":
        # Balanced Skill entrypoint for c2 ReAct. This is still a sealed-skill
        # read: all content below is copied from SKILL.md / reference/*.md.
        # It prevents the agent from over-indexing on the performance_metrics
        # reference alone while still requiring explicit tool use.
        core_ids = [
            "skill_overview",
            "trait_labels",
            "performance_metrics",
            "validation_sample_size",
            "training_cohorts_ancestry",
            "publication_context",
        ]
        parts: list[str] = [
            "# decision_core\n\n"
            "Balanced c2 same-trait PGS-selection core. Use this as the default "
            "Skill entrypoint before finalizing a recommendation. It combines the "
            "sealed procedural overview with the reference sections that most often "
            "interact in same-trait PGS selection: endpoint fidelity, metric/covariate "
            "interpretation, validation sample size, training/ancestry context, and "
            "publication/study context.\n"
        ]
        for sid in core_ids:
            path, _ = SECTION_INDEX[sid]
            try:
                parts.append(f"\n\n# ============= skill section: {sid} =============\n\n"
                             + path.read_text(encoding="utf-8"))
            except Exception as exc:
                parts.append(f"\n\nERROR reading {sid}: {type(exc).__name__}: {exc}")
        return "".join(parts).strip()
    if section_id == "all_references":
        # Round 3 lever: return all 9 reference sections concatenated, mirroring
        # iterD-final's pre-fed corpus shape but only when the agent decides it
        # needs the full empirical-pattern catalog. Tests the hypothesis that
        # the section-fragmentation in Rounds 1-2 was the H1-regression cause.
        parts: list[str] = []
        for sid, (path, _) in SECTION_INDEX.items():
            if sid == "skill_overview":
                continue
            try:
                parts.append(f"\n\n# ============= reference: {sid} =============\n\n"
                             + path.read_text(encoding="utf-8"))
            except Exception as exc:
                parts.append(f"\n\nERROR reading {sid}: {type(exc).__name__}: {exc}")
        return "".join(parts).strip()
    if section_id not in SECTION_INDEX:
        return (
            f"ERROR: unknown section_id '{section_id}'. Valid section_ids are: "
            f"{', '.join(VALID_SECTION_IDS)}."
        )
    path, _ = SECTION_INDEX[section_id]
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"ERROR reading section_id '{section_id}': {type(exc).__name__}: {exc}"


def _get_heritability_records_safe(trait: str, *, format_like_iterd: bool = False) -> str:
    """Wrap heritability tool call into a JSON observation. Errors return as
    descriptive observations rather than exceptions (LangGraph anti-pattern fix).

    Round 8 lever: `format_like_iterd=True` returns the EXACT iterD-final
    `_format_heritability_section` markdown layout (best record + sanity-check
    usage rules + top 3 matches), reproducing the framing the iterD-final
    runner pre-feeds in `domain_knowledge.full_document`. This isolates whether
    the gap between Round 7 (raw records) and iterD-final is the tool-observation
    formatting (per Anthropic context engineering: tool observations should be
    in the exact shape the model expects, not raw API dumps).
    """
    try:
        records = get_heritability_records(trait, ancestry="EUR")
        if format_like_iterd:
            from experiments.contribution2.recommendation.scripts.run_experiment_minimal_lift import (
                _format_heritability_section,
            )
            return _format_heritability_section(trait, records or [])
        if not records:
            return json.dumps({
                "trait": trait,
                "ancestry_filter": "EUR",
                "n_records": 0,
                "records": [],
                "interpretation_guidance": (
                    "No matching local h2 records were returned. Do not infer "
                    "h2-based conclusions; rely on the Skill guidance and visible "
                    "candidate records."
                ),
            })
        return json.dumps({
            "trait": trait,
            "ancestry_filter": "EUR",
            "n_records": len(records),
            "interpretation_guidance": (
                "These are raw local h2 records. Use them only as an advisory "
                "sanity-check for PRS-comparable R2 and possible covariate-driven "
                "full-model metrics. Do not rank candidates by h2, do not treat low "
                "h2 as a veto, and do not revise solely because one candidate has "
                "PRS-only R2/AUC while another has full-model metrics. Prefer the "
                "whole evidence record: endpoint fidelity, study context, validation "
                "support, ancestry/sample context, and metric interpretability."
            ),
            "records": records,
        })
    except Exception as exc:
        return json.dumps({
            "trait": trait,
            "error": f"{type(exc).__name__}: {exc}",
        })


# ---------------------------------------------------------------------------
# Tool schemas (OpenAI tool-calling format)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# JSON-schema terminal output (Round 5+ lever: avoid the structured-tool-call
# output bias by emitting the final pick via response_format json_schema on
# the model's terminal turn — matches iterD-final's output channel exactly).
# ---------------------------------------------------------------------------

class FinalDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


def _final_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "final_decision",
            "strict": True,
            "schema": to_strict_json_schema(FinalDecision),
        },
    }


def _tool_schemas() -> list[dict[str, Any]]:
    skill_section_summary_lines = "\n".join(
        f"  - '{sid}': {summary}"
        for sid, (_, summary) in SECTION_INDEX.items()
    )
    return [
        {
            "type": "function",
            "function": {
                "name": "read_skill_section",
                "description": (
                    "Tool to read one section of the prs_model_evaluator Agent Skill "
                    "(empirical patterns for evaluating PGS Catalog records). "
                    "Use when you need policy guidance on a specific evaluation dimension "
                    "before judging the candidate list. Each call returns the full markdown "
                    "of one section. Valid section_id values:\n"
                    f"{skill_section_summary_lines}\n"
                    "  - 'decision_core': balanced same-trait PGS-selection core "
                    "bundle copied from the sealed Skill. It includes the procedural "
                    "overview plus trait-label, performance/covariate, validation-N, "
                    "training/ancestry, and publication-context references. Prefer "
                    "this as the first Skill read when you need an integrated decision "
                    "framework rather than a narrow metric-only lookup.\n"
                    "  - 'all_references': returns ALL 9 reference sections concatenated "
                    "(~55K chars). Use when the candidate cluster is not trivially decided "
                    "by one or two evaluation dimensions and you want the full empirical-"
                    "pattern catalog for an integrated comparison.\n"
                    "Returns the section markdown (or an ERROR string if section_id is "
                    "unknown — in that case retry with a valid section_id from the list above)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "section_id": {
                            "type": "string",
                            "enum": VALID_SECTION_IDS,
                            "description": "The skill section to read. Must be one of the listed enum values.",
                        }
                    },
                    "required": ["section_id"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_heritability_records",
                "description": (
                    "Tool to look up local heritability (h2) records for the target trait. "
                    "Use h2 as an advisory sanity-check for performance interpretation, not "
                    "as a candidate ranking score, formula, or veto. It is most useful when "
                    "interpreting PRS-comparable R2 (PGS-only or covariates-regressed-out) "
                    "against a plausible trait heritability ceiling, and as background when "
                    "a very high full-model AUROC may be covariate-driven. Returns up to ~20 "
                    "raw matching EUR records from the local aggregator; the tool itself does "
                    "not select a best estimate or apply source-priority tiers. Each record "
                    "contains trait_name, h2 (observed), h2_liability, h2_se, h2_z, n_samples, "
                    "source, ancestry, match_score. If no records match, returns an empty "
                    "list — do not infer h2-based conclusions; fall back to the skill and "
                    "candidate evidence."
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
        },
        {
            "type": "function",
            "function": {
                "name": "submit_recommendation",
                "description": (
                    "Tool to submit your final PGS selection and END the agent loop. "
                    "Call this exactly once when you have gathered enough evidence to decide. "
                    "best_model_id MUST be one of the candidate PGS IDs from the user message; "
                    "you may not invent IDs not present in the candidate list. "
                    "outcome must be one of: 'DIRECT_HIGH_QUALITY', 'DIRECT_SUB_OPTIMAL', "
                    "'NO_MATCH_FOUND'. confidence must be one of 'High', 'Moderate', 'Low'. "
                    "rationale should be 1-3 sentences grounded only in visible evidence "
                    "(candidate records, sections you read, heritability records you fetched)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "outcome": {
                            "type": "string",
                            "enum": ["DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"],
                            "description": "Direct-match outcome label.",
                        },
                        "best_model_id": {
                            "type": "string",
                            "description": "PGS ID drawn from the visible candidate list. Use null only if outcome is NO_MATCH_FOUND.",
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["High", "Moderate", "Low"],
                            "description": "Your confidence in this pick.",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "1-3 sentence rationale grounded in visible evidence.",
                        },
                    },
                    "required": ["outcome", "best_model_id", "confidence", "rationale"],
                    "additionalProperties": False,
                },
            },
        },
    ]


# ---------------------------------------------------------------------------
# System + initial user prompts
# ---------------------------------------------------------------------------

# Round 2 (active): the procedural overview of the prs_model_evaluator skill
# is embedded in the system prompt as the agent's anchor framework. Reference
# sections + heritability remain on-demand. This is the Anthropic-textbook
# "progressive disclosure" pattern (skill metadata pre-loaded, deeper material
# loaded just-in-time via tools). Round 1 cold-start (no pre-load) regressed
# -9.5pp on H1 because the agent did not know the procedural framework existed
# and consulted only ~1.5 references on average.
def _build_system_prompt(json_schema_terminal: bool = False) -> str:
    skill_overview = SKILL_MD_PATH.read_text(encoding="utf-8")
    if json_schema_terminal:
        terminal_section = (
            "# Termination contract (this run uses JSON-schema terminal output)\n"
            "- Tool catalog: read_skill_section, get_heritability_records (only).\n"
            "- When you have gathered enough evidence, STOP calling tools and emit\n"
            "  a single JSON object with the schema:\n"
            "  {\"outcome\": \"DIRECT_HIGH_QUALITY|DIRECT_SUB_OPTIMAL|NO_MATCH_FOUND\",\n"
            "   \"best_model_id\": \"PGS00...\" or null,\n"
            "   \"confidence\": \"High|Moderate|Low\",\n"
            "   \"rationale\": \"...\"}\n"
            "- best_model_id MUST be one of the visible candidate IDs. Use null only\n"
            "  when outcome=NO_MATCH_FOUND.\n"
            "- The harness terminates the loop the first time you emit the JSON.\n"
        )
    else:
        terminal_section = (
            "# Termination contract (this run uses tool-call terminal output)\n"
            "- Tool catalog: read_skill_section, get_heritability_records,\n"
            "  submit_recommendation. Call submit_recommendation exactly once to end.\n"
        )
    return f"""# Identity
You are a PRS Co-scientist running as a single-agent ReAct loop. Your task is
to recommend exactly one polygenic-score (PGS) candidate from a fixed visible
candidate list for a fixed target trait, grounded only in visible evidence.

{terminal_section}

# Anchor framework (always available — read this first, do NOT re-fetch via tools)
The procedural overview from the prs_model_evaluator Agent Skill is reproduced
below verbatim. It is your default evaluation framework. The reference sections
listed in its table of contents are loaded on-demand via read_skill_section.

<skill_overview>
{skill_overview}
</skill_overview>

# Tool catalog (3 tools)
- read_skill_section(section_id): on-demand access to one of the 9 reference
  sections of the prs_model_evaluator skill (table of contents above). Use
  when the candidate comparison hinges on a specific evaluation dimension
  whose detail catalog the procedural overview defers to a reference file.
- get_heritability_records(trait): on-demand h2 lookup for the target trait.
  Use BEFORE deciding whenever you intend to weigh reported AUC / R^2 — the
  trait's heritability ceiling is the single most useful sanity-check for
  whether a candidate's metric is PRS-driven or covariate-driven, and the
  procedural overview's "Sanity-check usage" rules are designed around it.
- submit_recommendation(...): your terminal action. Call this exactly once
  to record your final pick and end the loop.

# Loop discipline
- Inspect the candidate list first. Then consult the anchor framework above to
  decide which dimensions matter for the specific candidate cluster.
- read_skill_section: invoke for any dimension where the procedural overview
  defers detail to a reference file (e.g. covariate-leakage / packaging
  catalog lives in the performance_metrics reference; endpoint-fidelity rules
  live in the trait_labels reference).
- get_heritability_records: invoke whenever AUC/R^2 interpretation is in play.
- Hard budget: 12 tool calls. Always end with submit_recommendation.

# Decision contract (carried over from c2 production)
- Direct-match assessment for the named target trait only. Do not expand to
  cross-disease reasoning. Outcome labels:
  - DIRECT_HIGH_QUALITY: at least one direct-match candidate is the
    best-supported choice from the visible evidence without major unresolved
    conflict.
  - DIRECT_SUB_OPTIMAL: direct-match candidates are present but the evidence
    is limited, conflicted, or insufficient.
  - NO_MATCH_FOUND: no direct-match candidates are present.
- best_model_id must be exactly one of the visible candidate IDs.
- Compare candidates on PRS-only metric cleanliness, endpoint fidelity,
  training scale, ancestry breadth, covariate cleanliness, packaging signals,
  heritability ceiling alignment when relevant.
- Do not assign numeric weights, scoring formulas, or deterministic vetoes.
  Empirical patterns from the skill are advisory.
- If multiple candidates are near-tied on the visible evidence, lower
  confidence rather than picking arbitrarily.
"""


SYSTEM_PROMPT_TOOL = _build_system_prompt(json_schema_terminal=False)
SYSTEM_PROMPT_JSON = _build_system_prompt(json_schema_terminal=True)


def _build_full_skill_corpus() -> str:
    """Reproduce the iterD-final pre-fed evidence shape: SKILL.md procedural
    overview + all 9 reference sections concatenated. Matches the byte layout
    of iterD's `domain_knowledge.full_document` field as closely as possible.
    """
    parts: list[str] = [SKILL_MD_PATH.read_text(encoding="utf-8")]
    for sid, (path, _) in SECTION_INDEX.items():
        if sid == "skill_overview":
            continue
        try:
            parts.append(f"\n\n# ============= reference: {sid} =============\n\n"
                         + path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return "".join(parts)


def _initial_user_message(
    target_trait: str,
    candidate_models: list[dict[str, Any]],
    *,
    json_schema_terminal: bool = False,
    iterd_mirror: bool = False,
    inline_full_skill: bool = False,
) -> str:
    """Build the initial user message.

    inline_full_skill=True (Round 6 production design per user directive):
        Embed the full SKILL.md + reference catalog into the user message's
        `domain_knowledge.full_document` field — bytewise compatible with
        iterD-final's pre-fed evidence shape. This is the priming that
        Rounds 1-3 confirmed is load-bearing: when given a choice, gpt-5.2
        systematically under-fetches skill sections (Round 3 picked the
        all_references option 0 / 89 times). Pre-fed priming bypasses that
        under-fetch failure mode entirely.

    iterd_mirror=True alone (without inline_full_skill): mirrors iterD's
        context structure but does not pre-feed the corpus.
    """
    if inline_full_skill:
        # Production Round 6/7 shape: iterD-equivalent context structure + the
        # FULL skill corpus in domain_knowledge.full_document. Tools are still
        # available for the agent's autonomy lever (h2).
        # Round 7 lever (force_h2_first): in Round 6 the agent never invoked
        # get_heritability_records (0 / 89). iterD-final pre-feeds a formatted
        # heritability section in addition to the corpus, so dropping the h2
        # call drops a load-bearing piece of evidence. Round 7 instructs the
        # agent to call h2 first; the agent then autonomously decides whether
        # to revise its initial reading and when to terminate.
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
                "full_document": _build_full_skill_corpus(),
                "snippets": [],
                "source_type": "local",
            },
            "todo_recitation_path": "N/A",
            "todo_recitation": "",
        }
        h2_clause = (
            "First, call get_heritability_records(trait) for the target trait — the "
            "trait-specific heritability records are NOT in your context and the "
            "procedural overview's Sanity-check usage rules require them to interpret "
            "candidate AUC / R^2 against the heritability ceiling. After receiving the "
            "h2 records, integrate them with the candidate list and SKILL guidance, "
            "then emit your final JSON decision. You may call get_heritability_records "
            "more than once (e.g. with a normalized trait label) if the first call "
            "returns no records. You may also emit the JSON directly without further "
            "tool calls once you have enough evidence.\n\n"
        )
        return (
            "Perform direct-match assessment only. Use the context JSON below to "
            "select the best supported direct-match candidate and return exactly "
            "one JSON object with fields: outcome, best_model_id, confidence, "
            "rationale.\n\n"
            f"{h2_clause}"
            f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
        )
    if iterd_mirror:
        payload = {
            "target_trait": target_trait,
            "direct_models": {
                "query_trait": target_trait,
                "total_found": len(candidate_models),
                "after_filter": len(candidate_models),
                "models": candidate_models,
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
    payload = {
        "target_trait": target_trait,
        "candidate_models": candidate_models,
    }
    terminal_clause = (
        "then emit the final JSON object" if json_schema_terminal
        else "then call submit_recommendation"
    )
    return (
        "Recommend the best PGS for the target trait below. The candidate list is "
        f"fixed. Inspect candidates first; consult skill sections and heritability "
        f"records on demand; {terminal_clause}.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


# ---------------------------------------------------------------------------
# OpenAI client + ReAct loop
# ---------------------------------------------------------------------------

def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _llm_call(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    temperature: float,
    seed: int,
    response_format: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    if response_format is not None:
        body["response_format"] = response_format
    response = client.chat.completions.create(**body)
    choice = response.choices[0]
    msg = choice.message
    out: dict[str, Any] = {"role": "assistant"}
    if msg.content:
        out["content"] = msg.content if isinstance(msg.content, str) else str(msg.content)
    if msg.tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
    return out


def _execute_tool(
    *,
    name: str,
    arguments: str,
    target_trait: str,
    candidate_id_set: set[str],
    format_h2_like_iterd: bool = False,
) -> tuple[str, Optional[dict[str, Any]]]:
    """Execute one tool call. Returns (observation_str, submitted_decision_or_None).

    When the tool is submit_recommendation, `submitted_decision` is the parsed
    decision dict (and the agent loop should terminate). Otherwise, the
    observation is a string to feed back as a ToolMessage.
    """
    try:
        args = json.loads(arguments) if arguments else {}
    except Exception as exc:
        return (f"ERROR parsing tool arguments: {type(exc).__name__}: {exc}", None)

    if name == "read_skill_section":
        section_id = str(args.get("section_id") or "").strip()
        return (_read_skill_section(section_id), None)

    if name == "get_heritability_records":
        trait = str(args.get("trait") or target_trait).strip()
        return (_get_heritability_records_safe(trait, format_like_iterd=format_h2_like_iterd), None)

    if name == "submit_recommendation":
        outcome = str(args.get("outcome") or "").strip()
        best_model_id = args.get("best_model_id")
        if best_model_id is not None:
            best_model_id = str(best_model_id).strip()
        confidence = str(args.get("confidence") or "Moderate").strip()
        rationale = str(args.get("rationale") or "").strip()
        # Validate
        if outcome not in {"DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"}:
            return (
                f"ERROR: outcome '{outcome}' invalid. Must be one of "
                "'DIRECT_HIGH_QUALITY', 'DIRECT_SUB_OPTIMAL', 'NO_MATCH_FOUND'.",
                None,
            )
        if outcome == "NO_MATCH_FOUND":
            best_model_id = None
        else:
            if not best_model_id or best_model_id not in candidate_id_set:
                return (
                    f"ERROR: best_model_id '{best_model_id}' is not present in the visible "
                    f"candidate list. Pick one of: {sorted(candidate_id_set)}.",
                    None,
                )
        if confidence not in {"High", "Moderate", "Low"}:
            confidence = "Moderate"
        decision = {
            "outcome": outcome,
            "best_model_id": best_model_id,
            "confidence": confidence,
            "rationale": rationale,
        }
        return (
            f"Recommendation submitted: {json.dumps(decision)}",
            decision,
        )

    return (f"ERROR: unknown tool '{name}'.", None)


def _run_react_loop(
    client: OpenAI,
    *,
    model: str,
    target_trait: str,
    candidate_models: list[dict[str, Any]],
    max_iterations: int,
    temperature: float,
    seed: int,
    preload_all_references: bool = False,
    preload_heritability: bool = False,
    json_schema_terminal: bool = False,
    iterd_mirror: bool = False,
    inline_full_skill: bool = False,
    h2_only_tool_surface: bool = False,
    format_h2_like_iterd: bool = False,
) -> dict[str, Any]:
    """Run a single-agent ReAct loop for one ontology. Returns a dict with
    keys: decision (the parsed submit_recommendation), tool_call_log, error.

    Round 4 lever: when preload_all_references=True, a synthetic
    `read_skill_section('all_references')` observation is appended BEFORE the
    first LLM call. This matches iterD-final's evidence shape (full reference
    catalog available from turn 0) and tests whether section-fragmentation in
    Rounds 1-3 was the H1-regression cause. Round 3 confirmed the agent never
    chose all_references when offered as an option — code-level injection is
    the only way to test the hypothesis on equal footing.

    Round 4 lever (h2 preload): same idea for heritability records.
    """
    candidate_id_set = {str(m.get("id")) for m in candidate_models if m.get("id")}
    if iterd_mirror or inline_full_skill:
        # Use iterD-final's exact CO_SCIENTIST_STEP1_PROMPT system prompt;
        # tools are still available but the user-message framing matches iterD.
        from src.server.core.system_prompts import CO_SCIENTIST_STEP1_PROMPT
        sys_prompt = CO_SCIENTIST_STEP1_PROMPT
    else:
        sys_prompt = SYSTEM_PROMPT_JSON if json_schema_terminal else SYSTEM_PROMPT_TOOL
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": _initial_user_message(
            target_trait, candidate_models,
            json_schema_terminal=json_schema_terminal,
            iterd_mirror=iterd_mirror,
            inline_full_skill=inline_full_skill,
        )},
    ]
    tool_call_log: list[dict[str, Any]] = []
    submitted_decision: Optional[dict[str, Any]] = None
    last_error: Optional[str] = None

    if preload_all_references:
        # Synthesize a faux "assistant tool call + tool observation" turn so
        # the agent observes the corpus as if it had asked for it.
        synthetic_call_id = "preload_all_references_0001"
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": synthetic_call_id,
                "type": "function",
                "function": {
                    "name": "read_skill_section",
                    "arguments": json.dumps({"section_id": "all_references"}),
                },
            }],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": synthetic_call_id,
            "content": _read_skill_section("all_references"),
        })
        tool_call_log.append({
            "iteration": -1,
            "tool_name": "read_skill_section",
            "arguments": json.dumps({"section_id": "all_references"}),
            "observation_preview": "[preloaded by harness]",
            "preloaded": True,
        })

    if preload_heritability:
        synthetic_call_id = "preload_heritability_0001"
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": synthetic_call_id,
                "type": "function",
                "function": {
                    "name": "get_heritability_records",
                    "arguments": json.dumps({"trait": target_trait}),
                },
            }],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": synthetic_call_id,
            "content": _get_heritability_records_safe(target_trait, format_like_iterd=format_h2_like_iterd),
        })
        tool_call_log.append({
            "iteration": -1,
            "tool_name": "get_heritability_records",
            "arguments": json.dumps({"trait": target_trait}),
            "observation_preview": "[preloaded by harness]",
            "preloaded": True,
        })

    # Tool list & response_format depend on terminal mode.
    # In json_schema_terminal mode, submit_recommendation is removed and the
    # final assistant turn emits a JSON object via response_format.
    # h2_only_tool_surface (Round 6 production lever per user directive):
    # restrict the tool surface to ONLY get_heritability_records — the agent's
    # one autonomy lever after seeing the iterD-equivalent priming.
    base_tools = _tool_schemas()
    if json_schema_terminal:
        base_tools = [t for t in base_tools if t["function"]["name"] != "submit_recommendation"]
    if h2_only_tool_surface:
        base_tools = [t for t in base_tools if t["function"]["name"] == "get_heritability_records"]
    full_tools = base_tools

    for iteration in range(max_iterations):
        try:
            # response_format only applies on the model's terminal turn (when
            # the model decides not to tool-call). It is always supplied in
            # json_schema_terminal mode; OpenAI honors it only when the model
            # produces content rather than tool_calls.
            rf = _final_response_format() if json_schema_terminal else None
            assistant_msg = _llm_call(
                client,
                model=model,
                messages=messages,
                tools=full_tools,
                temperature=temperature,
                seed=seed,
                response_format=rf,
            )
        except Exception as exc:
            last_error = f"LLM call iter={iteration}: {type(exc).__name__}: {exc}"
            break

        # Append assistant message
        messages.append(assistant_msg)
        tool_calls = assistant_msg.get("tool_calls") or []
        if not tool_calls:
            content = assistant_msg.get("content") or ""
            if json_schema_terminal:
                # Terminal turn: parse content as JSON and treat it as the decision.
                try:
                    parsed = FinalDecision.model_validate_json(content).model_dump()
                except Exception as exc:
                    last_error = f"Final JSON parse failed: {type(exc).__name__}: {exc}"
                    tool_call_log.append({
                        "iteration": iteration,
                        "kind": "json_parse_error",
                        "content_preview": content[:200],
                    })
                    break
                # Validate against candidate list
                if parsed.get("outcome") == "NO_MATCH_FOUND":
                    parsed["best_model_id"] = None
                else:
                    bid = parsed.get("best_model_id")
                    if not bid or str(bid).strip() not in candidate_id_set:
                        last_error = (
                            f"Final best_model_id '{bid}' not in candidate list."
                        )
                        tool_call_log.append({
                            "iteration": iteration,
                            "kind": "invalid_best_model_id",
                            "content_preview": content[:200],
                        })
                        break
                submitted_decision = parsed
                tool_call_log.append({
                    "iteration": iteration,
                    "kind": "json_terminal",
                    "content_preview": content[:200],
                })
                break
            # Agent emitted final text without calling submit_recommendation.
            # That's a contract violation — give it one corrective nudge and continue.
            tool_call_log.append({
                "iteration": iteration,
                "kind": "no_tool_call",
                "content_preview": content[:200],
            })
            messages.append({
                "role": "user",
                "content": (
                    "You did not call any tool. To end the loop you MUST call "
                    "submit_recommendation with a valid best_model_id from the visible "
                    "candidate list. Do not output free-form text instead."
                ),
            })
            continue

        # Execute each tool call in order; append a ToolMessage for each.
        for tc in tool_calls:
            fn = tc["function"]
            name = fn["name"]
            args = fn.get("arguments", "{}")
            observation, decision = _execute_tool(
                name=name,
                arguments=args,
                target_trait=target_trait,
                candidate_id_set=candidate_id_set,
                format_h2_like_iterd=format_h2_like_iterd,
            )
            tool_call_log.append({
                "iteration": iteration,
                "tool_name": name,
                "arguments": args,
                "observation_preview": observation[:200],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": observation,
            })
            if decision is not None:
                submitted_decision = decision
                break
        if submitted_decision is not None:
            break

    return {
        "decision": submitted_decision,
        "tool_call_log": tool_call_log,
        "error": last_error,
        "iterations_used": len(tool_call_log),
        "max_iterations": max_iterations,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _run_one_request(
    client: OpenAI,
    *,
    model: str,
    request: dict[str, Any],
    candidate_summary_by_ontology: dict[str, list[dict[str, Any]]],
    max_iterations: int,
    temperature: float,
    seed: int,
    preload_all_references: bool = False,
    preload_heritability: bool = False,
    json_schema_terminal: bool = False,
    iterd_mirror: bool = False,
    inline_full_skill: bool = False,
    h2_only_tool_surface: bool = False,
    format_h2_like_iterd: bool = False,
) -> dict[str, Any]:
    custom_id = request["custom_id"]
    ontology = request["ontology"]
    candidate_models = candidate_summary_by_ontology.get(ontology, [])
    try:
        result = _run_react_loop(
            client,
            model=model,
            target_trait=ontology,
            candidate_models=candidate_models,
            max_iterations=max_iterations,
            temperature=temperature,
            seed=seed,
            preload_all_references=preload_all_references,
            preload_heritability=preload_heritability,
            json_schema_terminal=json_schema_terminal,
            iterd_mirror=iterd_mirror,
            inline_full_skill=inline_full_skill,
            h2_only_tool_surface=h2_only_tool_surface,
            format_h2_like_iterd=format_h2_like_iterd,
        )
        decision = result["decision"]
        if decision is None:
            return {
                "custom_id": custom_id,
                "ontology": ontology,
                "decision": None,
                "tool_call_log": result["tool_call_log"],
                "iterations_used": result["iterations_used"],
                "error": result.get("error") or "Agent did not call submit_recommendation within budget",
            }
        return {
            "custom_id": custom_id,
            "ontology": ontology,
            "decision": decision,
            "tool_call_log": result["tool_call_log"],
            "iterations_used": result["iterations_used"],
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": ontology,
            "decision": None,
            "tool_call_log": [],
            "iterations_used": 0,
            "error": f"orchestration {type(exc).__name__}: {exc}",
        }


def _candidate_summary_lookup(
    disease_metadata: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in disease_metadata:
        out[row["ontology"]] = list(row.get("candidate_models_visible_to_llm") or [])
    return out


def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
    max_iterations: int,
    temperature: float,
    seed: int,
    preload_all_references: bool = False,
    preload_heritability: bool = False,
    json_schema_terminal: bool = False,
    iterd_mirror: bool = False,
    inline_full_skill: bool = False,
    h2_only_tool_surface: bool = False,
    format_h2_like_iterd: bool = False,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])

    client = _client()

    print(f"\n=== ReAct loop — {len(requests)} ontologies, workers={workers}, "
          f"max_iters={max_iterations}, preload_all_references={preload_all_references}, "
          f"preload_heritability={preload_heritability}, "
          f"json_schema_terminal={json_schema_terminal}, "
          f"iterd_mirror={iterd_mirror}, inline_full_skill={inline_full_skill}, "
          f"h2_only_tool_surface={h2_only_tool_surface} ===")
    react_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_one_request,
                client,
                model=model,
                request=request,
                candidate_summary_by_ontology=candidate_summary_by_ontology,
                max_iterations=max_iterations,
                temperature=temperature,
                seed=seed,
                preload_all_references=preload_all_references,
                preload_heritability=preload_heritability,
                json_schema_terminal=json_schema_terminal,
                iterd_mirror=iterd_mirror,
                inline_full_skill=inline_full_skill,
                h2_only_tool_surface=h2_only_tool_surface,
                format_h2_like_iterd=format_h2_like_iterd,
            ): request
            for request in requests
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            react_results[res["custom_id"]] = res
            done += 1
            status = "ok" if res["error"] is None else "ERR"
            iters = res.get("iterations_used", 0)
            if done % 20 == 0 or done == len(requests):
                print(f"  [react {done}/{len(requests)}] last={status} {res['ontology']} iters={iters}")
    print(f"ReAct elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_react_agent_results.json").write_text(
        json.dumps(list(react_results.values()), indent=2), encoding="utf-8"
    )

    # Build parsed_outputs in the format _build_summary_and_results expects.
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in requests:
        custom_id = request["custom_id"]
        res = react_results.get(custom_id) or {}
        if res.get("error") and res.get("decision") is None:
            error_map[custom_id] = res["error"]
            continue
        decision = res["decision"]
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [decision],
            "error": None,
        }

    # Wire output paths
    without_domain.RESULTS_JSON = output_run_dir / "experiment_react_agent_trial_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_react_agent_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_react_agent_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_react_agent_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_react_agent_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_react_agent_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_react_agent_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_react_agent_batch_errors.jsonl"
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
    summary["execution_mode"] = "react_agent_chat_completions"

    # Tool-call distribution
    iterations_distribution: dict[str, int] = {}
    tool_use_counts: dict[str, int] = {"read_skill_section": 0, "get_heritability_records": 0,
                                        "submit_recommendation": 0, "no_tool_call": 0}
    section_read_counts: dict[str, int] = {sid: 0 for sid in VALID_SECTION_IDS}
    no_decision_count = 0
    for res in react_results.values():
        iters = res.get("iterations_used", 0)
        bucket = str(min(iters, 12))
        iterations_distribution[bucket] = iterations_distribution.get(bucket, 0) + 1
        if res.get("decision") is None:
            no_decision_count += 1
        for entry in res.get("tool_call_log") or []:
            kind = entry.get("tool_name") or entry.get("kind") or ""
            tool_use_counts[kind] = tool_use_counts.get(kind, 0) + 1
            if entry.get("tool_name") == "read_skill_section":
                args = entry.get("arguments") or "{}"
                try:
                    parsed = json.loads(args)
                    sid = parsed.get("section_id")
                    if sid in section_read_counts:
                        section_read_counts[sid] += 1
                except Exception:
                    pass

    summary["react_agent"] = {
        "max_iterations": max_iterations,
        "temperature": temperature,
        "seed": seed,
        "iterations_distribution": iterations_distribution,
        "tool_use_counts": tool_use_counts,
        "section_read_counts": section_read_counts,
        "no_decision_count": no_decision_count,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="ReAct agent harness for c2 same-trait PGS selection")
    parser.add_argument("--manifest", type=str, required=True, help="iterD-style manifest path")
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--max-iterations", type=int, default=12)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--preload-all-references", action="store_true",
                        help="Round 4+ lever: pre-inject all_references read at turn 0.")
    parser.add_argument("--preload-heritability", action="store_true",
                        help="Round 4+ lever: pre-inject heritability records at turn 0.")
    parser.add_argument("--json-schema-terminal", action="store_true",
                        help="Round 5+ lever: drop submit_recommendation tool, emit final "
                        "decision via response_format json_schema (matches iterD-final's "
                        "output channel).")
    parser.add_argument("--iterd-mirror", action="store_true",
                        help="Round 6 lever: mirror iterD-final's exact context structure "
                        "and user-message wording.")
    parser.add_argument("--inline-full-skill", action="store_true",
                        help="Round 6 production lever: pre-feed the FULL SKILL.md + "
                        "reference catalog into the user message's domain_knowledge."
                        "full_document field — bytewise compatible with iterD-final's "
                        "evidence shape, addressing the LLM-systematically-under-fetches "
                        "failure mode observed in Rounds 1-3.")
    parser.add_argument("--h2-only-tool-surface", action="store_true",
                        help="Round 6 production lever: restrict the agent's tool surface "
                        "to ONLY get_heritability_records (drop read_skill_section). "
                        "Pairs with --inline-full-skill: skill is pre-fed, h2 is the one "
                        "autonomous agentic lever.")
    parser.add_argument("--format-h2-like-iterd", action="store_true",
                        help="Round 8 lever: shape h2 tool observations as iterD-final's "
                        "_format_heritability_section markdown (best record + sanity-check "
                        "usage rules + top 3 matches), instead of raw JSON records.")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"react-agent-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
        max_iterations=args.max_iterations,
        temperature=args.temperature,
        seed=args.seed,
        preload_all_references=args.preload_all_references,
        preload_heritability=args.preload_heritability,
        json_schema_terminal=args.json_schema_terminal,
        iterd_mirror=args.iterd_mirror,
        inline_full_skill=args.inline_full_skill,
        h2_only_tool_surface=args.h2_only_tool_surface,
        format_h2_like_iterd=args.format_h2_like_iterd,
    )
    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, "
              f"accuracy={v.get('accuracy')}")
    ra = summary.get("react_agent") or {}
    print(f"\nReAct meta:")
    print(f"  iterations_distribution: {ra.get('iterations_distribution')}")
    print(f"  tool_use_counts: {ra.get('tool_use_counts')}")
    print(f"  section_read_counts: {ra.get('section_read_counts')}")
    print(f"  no_decision_count: {ra.get('no_decision_count')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
