"""Contribution2 PEV harness with the shared prs-model-evaluator skill.

This runner keeps Contribution2's evaluation universe and Hit@k summary code,
but replaces the single Step-1 LLM call with a c2-specific
plan -> execute -> verify harness:

  1. TRIAGE: review the full candidate pool and identify candidates needing
     close comparison.
  2. PICK: select the primary PGS using the full candidate records, the
     triage notes, shared skill guidance, and raw h2 evidence.
  3. CRITIC: verify the pick and revise only when the LLM judges a visible
     contradiction or better-supported alternative.

The harness is trait-agnostic and LLM-led. It does not use AoU benchmark ranks,
hardcoded weights, deterministic scoring formulas, or fixed vetoes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as c2_eval
from src.server.core.llm_config import get_config
from src.server.core.tools.heritability import get_heritability_records
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
from src.server.core.tools.prs_model_evaluator_skill import load_c3_view

RECOMMENDATION_RUNS = Path(__file__).parent.parent / "runs"
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_UNION_CSV = c2_eval.CURRENT_UNION_CSV
DEFAULT_GROUND_TRUTH_DIR = (
    RECOMMENDATION_RUNS / "ground-truth__selected_diseases_contribution2_current_union"
)


class PEVTriageDecision(BaseModel):
    shortlist_ids: list[str] = Field(
        description="Candidate IDs that deserve close comparison downstream."
    )
    watchlist_ids: list[str] = Field(
        description="Plausible alternatives or candidates with unresolved evidence."
    )
    rationale: str
    uncertainty: str


class PEVPickDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    runner_up_ids: list[str]
    confidence: str
    rationale: str


class PEVCriticDecision(BaseModel):
    keep_legacy_proposal: bool
    final_outcome: str
    final_best_model_id: Optional[str] = None
    revised: bool
    confidence: str
    verification_notes: str


class PEVConflictDecision(BaseModel):
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


def _safe_model_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", (text or "unknown")).strip("-")


def _archive_dir_name(model: str, trials: int, run_tag: Optional[str]) -> str:
    base = f"pev-with-skill-{_safe_model_name(model)}-t{trials}"
    if c2_eval.ACTIVE_BENCHMARK_LABEL:
        base = f"{base}__{c2_eval.ACTIVE_BENCHMARK_LABEL}"
    safe_tag = _safe_model_name(run_tag or "")
    return f"{base}__{safe_tag}" if safe_tag else base


def _run_paths(model: str, trials: int, run_tag: Optional[str]) -> dict[str, Path]:
    run_dir = RECOMMENDATION_RUNS / _archive_dir_name(model, trials, run_tag)
    run_dir.mkdir(parents=True, exist_ok=True)
    return {
        "run_dir": run_dir,
        "manifest": run_dir / "experiment_pev_with_skill_manifest.json",
        "results": run_dir / "experiment_pev_with_skill_results.json",
        "summary": run_dir / "experiment_pev_with_skill_summary.json",
        "traces": run_dir / "experiment_pev_with_skill_traces.json",
        "report": run_dir / "experiment_pev_with_skill_report.md",
    }


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _json_response_format(schema_model: type[BaseModel], name: str) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": True,
            "schema": to_strict_json_schema(schema_model),
        },
    }


def _chat_json(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    schema_model: type[BaseModel],
    schema_name: str,
) -> BaseModel:
    config = get_config("disease_workflow")
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": _json_response_format(schema_model, schema_name),
    }
    if config.temperature is not None:
        body["temperature"] = config.temperature
    if config.max_tokens:
        body["max_tokens"] = config.max_tokens
    if config.seed is not None:
        body["seed"] = config.seed
    response = client.chat.completions.create(**body)
    content = c2_eval._extract_message_content(response.choices[0].message.content)
    return schema_model.model_validate_json(content)


def _skill_guidance(stage: str) -> str:
    cfg = SimpleNamespace(enable_pgs_quality_skill=True)
    return load_c3_view(stage, cfg=cfg).primary_section


def _candidate_context(disease_info: dict[str, Any]) -> list[dict[str, Any]]:
    return list(disease_info.get("candidate_models_visible_to_llm") or [])


def _candidate_ids(disease_info: dict[str, Any]) -> list[str]:
    return [str(pgs_id) for pgs_id in (disease_info.get("candidate_model_ids") or [])]


def _evidence_context(ontology: str) -> dict[str, Any]:
    return {
        "heritability_records": get_heritability_records(
            trait_label=ontology,
            ancestry="EUR",
            min_score=70,
            limit=20,
        ),
        "h2_usage_boundary": (
            "Raw h2 records are advisory ceiling/context evidence. Do not rank by "
            "h2 alone, do not calculate fixed efficiency scores, and do not discard "
            "a direct, well-supported PGS solely because h2 is missing."
        ),
    }


def _domain_query(ontology: str) -> str:
    return (
        f"target_trait: {ontology}; PRS clinical thresholds AUC R2 heritability ceiling sanity-check must-pass gates "
        "phenotype alignment endpoint specificity external transfer reliability "
        "ancestry compatibility ranking features penalties method priors "
        "validation sample size tie-break time-to-event horizon-specific "
        "incident case-control dominant subtype PGS-only no-covariates incremental AUROC "
        "snpnet biobank transportability"
    )


def _legacy_proposal_context(
    ontology: str,
    disease_info: dict[str, Any],
) -> dict[str, Any]:
    return {
        "target_trait": ontology,
        "direct_models": {
            "query_trait": ontology,
            "total_found": disease_info.get("total_found"),
            "after_filter": len(_candidate_context(disease_info)),
            "models": _candidate_context(disease_info),
        },
        "domain_knowledge": prs_model_domain_knowledge(
            _domain_query(ontology),
            max_snippets=8,
        ).model_dump(),
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


def _legacy_proposal(
    client: OpenAI,
    *,
    model: str,
    ontology: str,
    disease_info: dict[str, Any],
) -> c2_eval.Step1Decision:
    context_json = json.dumps(
        _legacy_proposal_context(ontology, disease_info),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    decision = _chat_json(
        client,
        model=model,
        messages=c2_eval._step1_messages(context_json),
        schema_model=c2_eval.Step1Decision,
        schema_name="step1_decision",
    )
    assert isinstance(decision, c2_eval.Step1Decision)
    return decision


def _system_prompt(stage: str) -> str:
    return (
        "You are the Contribution2 PRS recommendation PEV harness, "
        f"stage={stage}. Compare candidate PGS Catalog records for one fixed "
        "target trait. Use only visible context. Stay trait-agnostic: do not "
        "special-case diseases, ICD codes, organ systems, or disease families. "
        "Stay LLM-led: do not apply hardcoded weights, ranking formulas, "
        "numeric thresholds, or deterministic vetoes. The skill and tool outputs "
        "are advisory evidence; weigh them case-by-case. For Contribution2 "
        "direct-match selection, do not turn metric cleanliness into an implicit "
        "veto: PRS-only metrics are cleaner when available, but full-model "
        "AUC/C-index/R2, OR/HR, validation scale, endpoint alignment, and method "
        "context can still be meaningful predictive evidence when the visible "
        "covariates are conventional or similarly packaged across candidates. "
        "A cleaner but visibly weaker sibling is not automatically preferable "
        "to a strong direct-endpoint candidate with less perfectly separated "
        "metric reporting."
    )


def _triage(
    client: OpenAI,
    *,
    model: str,
    ontology: str,
    disease_info: dict[str, Any],
    evidence: dict[str, Any],
) -> PEVTriageDecision:
    context = {
        "target_trait": ontology,
        "candidate_count": len(_candidate_ids(disease_info)),
        "candidate_ids": _candidate_ids(disease_info),
        "candidate_models": _candidate_context(disease_info),
        "pgs_quality_guidance": _skill_guidance("pgs_triage"),
        "evidence": evidence,
    }
    messages = [
        {"role": "system", "content": _system_prompt("TRIAGE")},
        {
            "role": "user",
            "content": (
                "Plan the downstream PGS comparison. Identify candidates that "
                "deserve close comparison, including strong candidates, plausible "
                "near-ties, and candidates with evidence that could mislead a "
                "single-shot picker. This is not a filter: downstream PICK may "
                "still choose any candidate in the full list. Preserve candidates "
                "with strong direct-endpoint predictive evidence even when their "
                "metrics are not perfectly PRS-only, and preserve cleaner-metric "
                "alternatives for head-to-head comparison. Return JSON only.\n\n"
                f"Context:\n{json.dumps(context, ensure_ascii=False, separators=(',', ':'))}"
            ),
        },
    ]
    return _chat_json(
        client,
        model=model,
        messages=messages,
        schema_model=PEVTriageDecision,
        schema_name="c2_pev_triage_decision",
    )


def _pick(
    client: OpenAI,
    *,
    model: str,
    ontology: str,
    disease_info: dict[str, Any],
    evidence: dict[str, Any],
    triage: PEVTriageDecision,
    proposal: c2_eval.Step1Decision,
) -> PEVPickDecision:
    context = {
        "target_trait": ontology,
        "candidate_ids": _candidate_ids(disease_info),
        "candidate_models": _candidate_context(disease_info),
        "legacy_with_domain_proposal": proposal.model_dump(),
        "triage_notes": triage.model_dump(),
        "pgs_quality_guidance": _skill_guidance("pick"),
        "evidence": evidence,
    }
    messages = [
        {"role": "system", "content": _system_prompt("PICK")},
        {
            "role": "user",
            "content": (
                "Select the best-supported direct-match PGS for the target trait. "
                "Inspect the full candidate list, not only the triage shortlist. "
                "This PICK stage is a stress test of legacy_with_domain_proposal, "
                "not a from-scratch reranking exercise. Keep the legacy proposal "
                "when it remains defensible from the visible records. Revise only "
                "when a different candidate is clearly better-supported across "
                "multiple independent visible axes; if the legacy proposal and an "
                "alternative are both defensible, keep the legacy proposal. Do not "
                "revise away merely because an alternative has cleaner PRS-only "
                "AUC/R2; the alternative must also be at least comparably direct "
                "on endpoint and stronger on the visible predictive evidence as a "
                "whole. "
                "Weigh metric comparability without treating missing PRS-only "
                "AUC/R2 as a deterministic penalty. When a direct-endpoint "
                "candidate has stronger visible discrimination/effect evidence "
                "and ordinary covariate packaging, compare that predictive signal "
                "against cleaner but weaker alternatives case-by-case. "
                "Use outcome labels DIRECT_HIGH_QUALITY, DIRECT_SUB_OPTIMAL, or "
                "NO_MATCH_FOUND. The selected best_model_id must be one candidate "
                "from candidate_ids, or null if no candidate is supportable. "
                "Return JSON only.\n\n"
                f"Context:\n{json.dumps(context, ensure_ascii=False, separators=(',', ':'))}"
            ),
        },
    ]
    return _chat_json(
        client,
        model=model,
        messages=messages,
        schema_model=PEVPickDecision,
        schema_name="c2_pev_pick_decision",
    )


def _critic(
    client: OpenAI,
    *,
    model: str,
    ontology: str,
    disease_info: dict[str, Any],
    evidence: dict[str, Any],
    triage: PEVTriageDecision,
    proposal: c2_eval.Step1Decision,
    pick: PEVPickDecision,
) -> PEVCriticDecision:
    context = {
        "target_trait": ontology,
        "candidate_ids": _candidate_ids(disease_info),
        "candidate_models": _candidate_context(disease_info),
        "legacy_with_domain_proposal": proposal.model_dump(),
        "triage_notes": triage.model_dump(),
        "proposed_pick": pick.model_dump(),
        "pgs_quality_guidance": _skill_guidance("critic"),
        "evidence": evidence,
    }
    messages = [
        {"role": "system", "content": _system_prompt("CRITIC")},
        {
            "role": "user",
            "content": (
                "Verify the proposed PGS pick against the visible records, skill "
                "guidance, and raw evidence. The critic's job is to catch clear "
                "mistakes, not to re-rank close calls. Keep the pick if it is "
                "defensible. Also check whether the original "
                "legacy_with_domain_proposal is defensible; if the proposal and "
                "the proposed_pick are both defensible, revise back to the legacy "
                "proposal and set keep_legacy_proposal=true. Set "
                "keep_legacy_proposal=false only when the legacy proposal is not "
                "defensible or a different candidate is clearly better-supported "
                "by the visible evidence. "
                "Revise only if your LLM judgment finds a concrete visible "
                "contradiction or a better-supported visible alternative. Do not "
                "revise from a fixed rule list, and do not revise merely because "
                "another candidate has cleaner PRS-only reporting if the legacy "
                "proposal or proposed pick has direct-endpoint alignment, strong "
                "visible OR/HR/AUC/C-index/R2 or validation evidence, and no "
                "visible severe packaging problem. Return JSON only.\n\n"
                f"Context:\n{json.dumps(context, ensure_ascii=False, separators=(',', ':'))}"
            ),
        },
    ]
    return _chat_json(
        client,
        model=model,
        messages=messages,
        schema_model=PEVCriticDecision,
        schema_name="c2_pev_critic_decision",
    )


def _decision_from_pev(
    *,
    candidate_ids: set[str],
    triage: PEVTriageDecision,
    proposal: c2_eval.Step1Decision,
    pick: PEVPickDecision,
    critic: PEVCriticDecision,
) -> dict[str, Any]:
    if critic.keep_legacy_proposal and proposal.best_model_id in candidate_ids:
        selected = proposal.best_model_id
        outcome = proposal.outcome
        confidence = critic.confidence or proposal.confidence
    else:
        selected = critic.final_best_model_id
        outcome = critic.final_outcome or pick.outcome
        confidence = critic.confidence or pick.confidence
    notes = critic.verification_notes

    if selected not in candidate_ids:
        selected = pick.best_model_id if pick.best_model_id in candidate_ids else None
        if selected is None and proposal.best_model_id in candidate_ids:
            selected = proposal.best_model_id
        notes = (
            f"{notes} Validity repair: critic returned an ID outside the candidate "
            "set, so the harness retained the pick-stage candidate if valid, "
            "falling back to the legacy proposal if needed."
        )
    if selected is None:
        outcome = "NO_MATCH_FOUND"

    return {
        "outcome": outcome,
        "best_model_id": selected,
        "confidence": confidence,
        "rationale": (
            f"TRIAGE: {triage.rationale} Uncertainty: {triage.uncertainty} "
            f"LEGACY_PROPOSAL: {proposal.rationale} PICK: {pick.rationale} "
            f"CRITIC: {notes}"
        ),
    }


def _run_request(
    request: dict[str, Any],
    disease_info: dict[str, Any],
    *,
    model: str,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    custom_id = request["custom_id"]
    ontology = request["ontology"]
    client = _client()
    evidence = _evidence_context(ontology)
    candidate_ids = set(_candidate_ids(disease_info))
    decisions: list[dict[str, Any]] = []
    trace_trials: list[dict[str, Any]] = []

    for trial_offset in range(request["trials"]):
        trial = request["trial_start"] + trial_offset
        proposal = _legacy_proposal(
            client,
            model=model,
            ontology=ontology,
            disease_info=disease_info,
        )
        triage = _triage(
            client,
            model=model,
            ontology=ontology,
            disease_info=disease_info,
            evidence=evidence,
        )
        pick = _pick(
            client,
            model=model,
            ontology=ontology,
            disease_info=disease_info,
            evidence=evidence,
            triage=triage,
            proposal=proposal,
        )
        critic = _critic(
            client,
            model=model,
            ontology=ontology,
            disease_info=disease_info,
            evidence=evidence,
            triage=triage,
            proposal=proposal,
            pick=pick,
        )
        decision = _decision_from_pev(
            candidate_ids=candidate_ids,
            triage=triage,
            proposal=proposal,
            pick=pick,
            critic=critic,
        )
        decisions.append(decision)
        trace_trials.append({
            "trial": trial,
            "legacy_proposal": proposal.model_dump(),
            "triage": triage.model_dump(),
            "pick": pick.model_dump(),
            "critic": critic.model_dump(),
            "final_decision": decision,
        })

    return (
        custom_id,
        {"custom_id": custom_id, "decisions": decisions, "error": None},
        {
            "custom_id": custom_id,
            "ontology": ontology,
            "evidence": evidence,
            "trials": trace_trials,
        },
    )


def _resolve_conflicts(
    *,
    manifest: dict[str, Any],
    parsed_outputs: dict[str, dict[str, Any]],
    traces: dict[str, dict[str, Any]],
    model: str,
) -> None:
    if int(manifest.get("trials_per_ontology") or 1) <= 1:
        return
    requests_by_ontology: dict[str, list[dict[str, Any]]] = {}
    for request in manifest.get("requests") or []:
        requests_by_ontology.setdefault(request["ontology"], []).append(request)

    disease_index = {row["ontology"]: row for row in manifest["disease_metadata"]}
    client = _client()
    for ontology, requests in requests_by_ontology.items():
        trial_decisions: list[dict[str, Any]] = []
        for request in requests:
            parsed = parsed_outputs.get(request["custom_id"]) or {}
            trial_decisions.extend(parsed.get("decisions") or [])
        valid_ids = {
            d.get("best_model_id")
            for d in trial_decisions
            if d.get("best_model_id") in set(_candidate_ids(disease_index[ontology]))
        }
        if len(valid_ids) <= 1:
            continue
        context = {
            "target_trait": ontology,
            "candidate_ids": _candidate_ids(disease_index[ontology]),
            "candidate_models": _candidate_context(disease_index[ontology]),
            "trial_decisions": trial_decisions,
            "pgs_quality_guidance": _skill_guidance("critic"),
            "evidence": _evidence_context(ontology),
        }
        messages = [
            {"role": "system", "content": _system_prompt("CROSS_TRIAL_RESOLUTION")},
            {
                "role": "user",
                "content": (
                    "Multiple PEV trials disagreed. Resolve the disagreement by "
                    "LLM judgment over the visible candidate records and trial "
                    "rationales. Do not use modal voting as a rule. Return JSON only.\n\n"
                    f"Context:\n{json.dumps(context, ensure_ascii=False, separators=(',', ':'))}"
                ),
            },
        ]
        resolved = _chat_json(
            client,
            model=model,
            messages=messages,
            schema_model=PEVConflictDecision,
            schema_name="c2_pev_conflict_decision",
        )
        if resolved.best_model_id not in set(_candidate_ids(disease_index[ontology])):
            continue
        for request in requests:
            parsed = parsed_outputs.get(request["custom_id"]) or {}
            for decision in parsed.get("decisions") or []:
                decision["best_model_id"] = resolved.best_model_id
                decision["confidence"] = resolved.confidence
                decision["rationale"] = (
                    f"{decision.get('rationale', '')} CROSS_TRIAL_RESOLUTION: "
                    f"{resolved.rationale}"
                )
            trace = traces.get(request["custom_id"])
            if trace is not None:
                trace["cross_trial_resolution"] = resolved.model_dump()


def _write_report(summary: dict[str, Any], path: Path) -> None:
    c2_eval._ensure_summary_hit_metrics(summary)
    lines = [
        "# Contribution2 PEV With prs-model-evaluator Skill",
        "",
        f"- Diseases: {summary['total_ontologies']}",
        f"- Trials per disease: {summary['trials_per_ontology']}",
        f"- Model: {summary['model']}",
        f"- Union CSV: `{summary.get('union_csv')}`",
        "",
        "## Hit@k",
        "",
    ]
    for k in c2_eval.BENCHMARK_HIT_KS:
        payload = summary["modal_hit_at_k"][str(k)]
        lines.append(
            f"- Hit@{k}: {payload['hits']}/{payload['eligible']} = "
            f"{c2_eval._format_percent(payload['accuracy'] or 0.0)}"
        )
    nrs = summary.get("nrs") or {}
    lines.extend([
        "",
        "## Rank",
        "",
        f"- Modal mean NRS: {c2_eval._format_score(nrs.get('modal_mean_nrs'))}",
        "",
        "## Harness",
        "",
        "- TRIAGE, PICK, and CRITIC each consume the shared prs-model-evaluator skill.",
        "- Raw heritability records are exposed as advisory evidence, not embedded in the skill text.",
        "- The final JSON is converted to the existing Contribution2 Step1Decision shape for evaluation.",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def _prepare_manifest(
    *,
    model: str,
    trials: int,
    run_tag: Optional[str],
    union_csv: str,
    ground_truth_dir: Optional[str],
    limit: Optional[int],
    refresh_cache: bool,
    ontology_filter: Optional[set[str]],
) -> dict[str, Any]:
    os.environ["OPENAI_MODEL"] = model
    c2_eval.ACTIVE_RUN_TAG = run_tag
    c2_eval._configure_benchmark_sources(
        union_csv=union_csv,
        ground_truth_dir=ground_truth_dir,
    )
    manifest = c2_eval._prepare_manifest(
        limit=limit,
        trials=trials,
        refresh_cache=refresh_cache,
        ontology_filter=ontology_filter,
    )
    manifest["experiment"] = "pev_with_skill"
    manifest["domain_knowledge"] = True
    manifest["pgs_quality_skill"] = True
    manifest["heritability_tool"] = True
    manifest["model"] = model
    return manifest


def _run_pev(
    *,
    manifest: dict[str, Any],
    model: str,
    workers: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, str]]:
    disease_index = {row["ontology"]: row for row in manifest["disease_metadata"]}
    parsed_outputs: dict[str, dict[str, Any]] = {}
    traces: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {
            executor.submit(
                _run_request,
                request,
                disease_index[request["ontology"]],
                model=model,
            ): request
            for request in manifest["requests"]
        }
        total = len(future_map)
        for index, future in enumerate(as_completed(future_map), start=1):
            request = future_map[future]
            custom_id = request["custom_id"]
            ontology = request["ontology"]
            print(f"[pev {index}/{total}] {ontology}", flush=True)
            try:
                out_custom_id, parsed, trace = future.result()
                parsed_outputs[out_custom_id] = parsed
                traces[out_custom_id] = trace
            except Exception as exc:  # noqa: BLE001
                error_map[custom_id] = f"PEV failed: {type(exc).__name__}: {exc}"

    _resolve_conflicts(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        traces=traces,
        model=model,
    )
    return parsed_outputs, traces, error_map


def _print_hit_metrics(summary: dict[str, Any]) -> None:
    for k in c2_eval.BENCHMARK_HIT_KS:
        payload = summary["modal_hit_at_k"][str(k)]
        print(
            f"Hit@{k}: {payload['hits']}/{payload['eligible']} = "
            f"{payload['accuracy']:.4f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Contribution2 PEV harness with prs-model-evaluator skill"
    )
    parser.add_argument(
        "--mode",
        choices=["prepare", "run"],
        default="run",
        help="prepare writes the manifest only; run prepares and evaluates",
    )
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--ontology", action="append", default=None)
    parser.add_argument("--ontologies-file", type=str, default=None)
    parser.add_argument("--run-tag", type=str, default=None)
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--union-csv", type=str, default=str(DEFAULT_UNION_CSV))
    parser.add_argument("--ground-truth-dir", type=str, default=str(DEFAULT_GROUND_TRUTH_DIR))
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY") and args.mode == "run":
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1
    if args.trials <= 0:
        print("ERROR: --trials must be positive.")
        return 1

    ontology_filter = c2_eval._load_ontology_filter(args.ontology, args.ontologies_file)
    manifest = _prepare_manifest(
        model=args.model,
        trials=args.trials,
        run_tag=args.run_tag,
        union_csv=args.union_csv,
        ground_truth_dir=args.ground_truth_dir,
        limit=args.limit,
        refresh_cache=args.refresh_cache,
        ontology_filter=ontology_filter,
    )
    paths = _run_paths(args.model, args.trials, args.run_tag)
    c2_eval._write_json(paths["manifest"], manifest)
    print(f"Manifest: {paths['manifest']}")

    if args.mode == "prepare":
        return 0

    parsed_outputs, traces, error_map = _run_pev(
        manifest=manifest,
        model=args.model,
        workers=args.workers,
    )
    trial_results, summary = c2_eval._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["experiment"] = "pev_with_skill"
    summary["domain_knowledge"] = True
    summary["pgs_quality_skill"] = True
    summary["heritability_tool"] = True
    summary["execution_mode"] = "pev_chat_completions"

    c2_eval._write_json(paths["results"], trial_results)
    c2_eval._write_json(paths["summary"], summary)
    c2_eval._write_json(paths["traces"], traces)
    _write_report(summary, paths["report"])

    print(f"Results: {paths['results']}")
    print(f"Summary: {paths['summary']}")
    print(f"Traces:  {paths['traces']}")
    print(f"Report:  {paths['report']}")
    _print_hit_metrics(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
