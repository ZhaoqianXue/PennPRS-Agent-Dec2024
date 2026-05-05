"""Round 4 — Pristine Stage 1 + separated runner-up generator + pairwise reranking.

Hypothesis (built on Round 1 win + Round 1/2/3 diagnoses):

- Round 1 (pairwise rerank on top-3) lifted Hit@1 +3 by re-ranking the LLM's
  own shortlist with a separated pairwise judge. But it had 4 H1 regressions:
  3 of them came not from the pairwise stage but from the schema-augmented
  Stage 1 prompt itself — adding `top_alternatives` to the schema subtly
  perturbed the primary pick on cholelithiasis, crohn's disease, and sleep
  apnea. Only 1 regression (otosclerosis) was a true pairwise overrule.
- Round 2 (Borda over k=5 samples at t=0.7) regressed Hit@1 –3.4pp: temperature
  diversity adds noise that hurts top-1 even with ranked voting.
- Round 3 (3-perspective ensemble at t=0) regressed Hit@1 –4.5pp: forced
  perspective decomposition produces 3 distinct picks whose Borda aggregation
  is dominated by candidates with consistent rank-2/rank-3 placements rather
  than the right rank-1.

Round 4 hypothesis: Round 1's pairwise stage is the load-bearing mechanism.
Preserving iterD-final's primary pick *bytewise* eliminates the 3
schema-perturbation regressions while keeping all 7 pairwise lifts. Net effect
should improve over Round 1 (which had +7 / –4 → +3) toward (+7 / –1 → +6).

Architecture:
  Stage 1A (PRISTINE): EXACT iterD-final prompt and schema. Emits
    {outcome, best_model_id, confidence, rationale}. No top_alternatives.
    Single-shot, t=0, seed=42. Result is the locked baseline pick.

  Stage 1B (RUNNER-UP GENERATOR): A separate LLM call that receives the same
    context PLUS Stage 1A's best_model_id, and is told to identify the two
    best-supported runners-up that are NOT Stage 1A's best. This isolates the
    schema-augmentation work from the primary pick. Single-shot, t=0, seed=42.

  Stage 2 (PAIRWISE JUDGE): Same as Round 1. For each pair of {Stage 1A best,
    alt1, alt2}, run an independent strict pairwise judge call. Borda count
    over the pairwise wins; tiebreak strictly prefers Stage 1A's best.

If Stage 1B returns fewer than 2 valid alternatives, the pairwise stage is
skipped and Stage 1A's pick is used directly (graceful degradation).

Distinct from Round 1: Round 1 fused Stage 1 with the runner-up generator into
one prompt (schema augmentation). Round 4 separates them, so the primary pick
is bytewise identical to iterD-final's prompt path.
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
from src.server.core.system_prompts import CO_SCIENTIST_STEP1_PROMPT


# ---------------------------------------------------------------------------
# Stage 1A — pristine iterD-final schema
# ---------------------------------------------------------------------------

class Step1Decision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


def _stage1a_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1Decision),
        },
    }


# ---------------------------------------------------------------------------
# Stage 1B — runner-up generator (NOT a re-pick)
# ---------------------------------------------------------------------------

class RunnerUpDecision(BaseModel):
    excluded_pgs_id: str
    runners_up: list[str]
    rationale: str


RUNNER_UP_SYSTEM_PROMPT = """# Identity & Persona
You are the runner-up generator for a PRS Co-scientist pipeline. The PRIMARY
candidate has already been chosen by a separate picker stage. Your job is NOT
to reconsider the primary pick — your job is to identify the two best-supported
RUNNERS-UP from the same visible candidate list.

# Task
Given the candidate list and the primary's pick (`excluded_pgs_id`), return
the two best-supported runners-up among the remaining candidates, ranked by
direct-match support strength.

# Decision Boundary
- excluded_pgs_id is fixed by the primary picker. You may not change it.
- runners_up must contain exactly two distinct PGS IDs from the visible
  candidate list, neither of which equals excluded_pgs_id.
- If only one runner-up is supportable, repeat that ID twice (the schema
  requires a stable two-element list).
- If no runner-up is supportable at all, return an empty list.

# Evaluation Reference Frame
Use the same evidence framework the primary picker used:
- candidate metadata returned by `prs_model_pgscatalog_search`
- optional `domain_knowledge` from `prs_model_domain_knowledge`
- if `domain_knowledge.full_document` is present, treat it as the authoritative
  field-level policy source

Compare runners-up across PRS-only AUC/R2 cleanliness, endpoint fidelity,
training scale, ancestry breadth, covariate cleanliness, packaging signals,
and heritability ceiling alignment when relevant. Do not invent missing
evidence.

# Output Requirements
Return one JSON object with exactly these fields:
{
  "excluded_pgs_id": "PGS00001",
  "runners_up": ["PGS00002", "PGS00003"],
  "rationale": "..."
}

# Output Discipline
- excluded_pgs_id must equal the primary picker's pick that was given to you.
- runners_up must each be present in the visible candidate list.
- runners_up must not include excluded_pgs_id.
- Do not include extra keys.
"""


def _runner_up_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "runner_up_decision",
            "strict": True,
            "schema": to_strict_json_schema(RunnerUpDecision),
        },
    }


def _runner_up_user_message(*, context_json: str, excluded_pgs_id: str) -> str:
    return (
        f"The primary picker selected excluded_pgs_id = '{excluded_pgs_id}'. "
        "Identify the two best-supported runners-up from the same visible candidate "
        "list (not including the excluded ID). Return exactly the schema-required "
        "JSON.\n\n"
        f"Context:\n{context_json}"
    )


# ---------------------------------------------------------------------------
# Stage 2 — pairwise judge (same as Round 1)
# ---------------------------------------------------------------------------

class PairwiseJudgment(BaseModel):
    winner_model_id: str
    confidence: str
    rationale: str


PAIRWISE_JUDGE_SYSTEM_PROMPT = """# Identity & Persona
You are a strict PRS quality judge. You compare exactly two PGS Catalog candidate
records for the same target trait, and you decide which one is better-supported
on the visible record fields.

# Task
Decide the winner of a head-to-head comparison between exactly two PGS candidates
for the target trait shown in the context. Output one JSON object with the winner's
PGS ID, your confidence, and a short rationale.

# Decision Boundary
- The winner must be one of the two candidate IDs explicitly given in the context.
- You may not introduce a third candidate, propose a tie, or refuse to choose.
- Your default is to pick a winner; declare confidence "Low" if the records are
  near-tied, but still emit a winner_model_id from the two given IDs.

# Evaluation Reference Frame
Use only evidence explicitly present in the context. Compare across:
- PRS-only AUC / R2 cleanliness (full-model AUC/R2 are not comparable PRS metrics)
- endpoint fidelity to the target trait (trait_reported, trait_efo, phenotyping_reported)
- training scale, validation breadth, ancestry breadth
- covariate-leakage and packaging signals (clinical risk calculators, family-history
  packages, biomarker / treatment / mediator adjustment, horizon-conditioned
  packaging, broad EHR phenotype summaries)
- heritability ceiling alignment when the trait-specific heritability section is present

If the optional `domain_knowledge.full_document` is present, treat it as the
authoritative field-level policy source; weigh its empirical patterns against
the candidate records.

Do not rank by method-name labels, publication age, "established" use, or
validation N alone unless the candidate records show why that signal matters
in this specific comparison.

# Output Requirements
Return one JSON object with exactly these fields:
{{
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}}

# Output Discipline
- winner_model_id must be one of the two candidate IDs given in the prompt.
- rationale must be grounded only in visible evidence and must reference both
  candidates (what the winner has and the loser lacks).
- Do not include extra keys.
"""


def _pairwise_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "pairwise_judgment",
            "strict": True,
            "schema": to_strict_json_schema(PairwiseJudgment),
        },
    }


def _pairwise_user_message(
    *,
    target_trait: str,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    domain_knowledge: dict[str, Any],
) -> str:
    payload = {
        "target_trait": target_trait,
        "comparison": {
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "candidate_a": candidate_a_summary,
            "candidate_b": candidate_b_summary,
        },
        "domain_knowledge": domain_knowledge,
    }
    return (
        "Decide the winner of the head-to-head comparison below. winner_model_id "
        "must be exactly one of candidate_a_id or candidate_b_id.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


# ---------------------------------------------------------------------------
# Helpers
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
    messages: list[dict[str, str]],
    response_format: dict[str, Any],
) -> str:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
        "temperature": 0,
        "seed": 42,
    }
    response = client.chat.completions.create(**body)
    choice = response.choices[0]
    content = choice.message.content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts).strip()
    return (content or "").strip()


def _extract_context_json(request: dict[str, Any]) -> str:
    body = request["request"]["body"]
    user_messages = body["messages"]
    original_user = user_messages[1]["content"]
    marker = "Context:\n"
    idx = original_user.find(marker)
    if idx < 0:
        raise RuntimeError("Context marker not found")
    return original_user[idx + len(marker):]


def _stage1a_messages(context_json: str) -> list[dict[str, str]]:
    """EXACT iterD-final messages — produced from the same body."""
    return [
        {"role": "system", "content": CO_SCIENTIST_STEP1_PROMPT},
        {
            "role": "user",
            "content": (
                "Perform direct-match assessment only. Use the context JSON below to "
                "select the best supported direct-match candidate and return exactly "
                "one JSON object with fields: outcome, best_model_id, confidence, "
                f"rationale.\n\nContext:\n{context_json}"
            ),
        },
    ]


def _run_stage1a(client: OpenAI, model: str, request: dict[str, Any]) -> dict[str, Any]:
    custom_id = request["custom_id"]
    try:
        context_json = _extract_context_json(request)
        messages = _stage1a_messages(context_json)
        content = _llm_call(
            client, model=model, messages=messages,
            response_format=_stage1a_response_format(),
        )
        decision = Step1Decision.model_validate_json(content)
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "context_json": context_json,
            "decision": decision.model_dump(),
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "context_json": None,
            "decision": None,
            "error": f"Stage1A {type(exc).__name__}: {exc}",
        }


def _run_stage1b(
    client: OpenAI,
    model: str,
    *,
    custom_id: str,
    ontology: str,
    context_json: str,
    excluded_pgs_id: str,
) -> dict[str, Any]:
    try:
        user_msg = _runner_up_user_message(context_json=context_json, excluded_pgs_id=excluded_pgs_id)
        messages = [
            {"role": "system", "content": RUNNER_UP_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        content = _llm_call(
            client, model=model, messages=messages,
            response_format=_runner_up_response_format(),
        )
        decision = RunnerUpDecision.model_validate_json(content)
        return {
            "custom_id": custom_id,
            "ontology": ontology,
            "decision": decision.model_dump(),
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": ontology,
            "decision": None,
            "error": f"Stage1B {type(exc).__name__}: {exc}",
        }


def _run_pairwise(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    domain_knowledge: dict[str, Any],
) -> dict[str, Any]:
    try:
        user_msg = _pairwise_user_message(
            target_trait=ontology,
            candidate_a_id=candidate_a_id,
            candidate_b_id=candidate_b_id,
            candidate_a_summary=candidate_a_summary,
            candidate_b_summary=candidate_b_summary,
            domain_knowledge=domain_knowledge,
        )
        messages = [
            {"role": "system", "content": PAIRWISE_JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        content = _llm_call(
            client, model=model, messages=messages,
            response_format=_pairwise_response_format(),
        )
        verdict = PairwiseJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        valid = winner in {candidate_a_id, candidate_b_id}
        return {
            "ontology": ontology,
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "winner_model_id": winner if valid else None,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None if valid else f"winner '{winner}' not in pair",
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"Pairwise {type(exc).__name__}: {exc}",
        }


def _candidate_summary_lookup(
    disease_metadata: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for row in disease_metadata:
        ontology = row["ontology"]
        out[ontology] = {}
        for summary in row.get("candidate_models_visible_to_llm") or []:
            pgs_id = summary.get("pgs_id") or summary.get("id")
            if pgs_id:
                out[ontology][pgs_id] = summary
    return out


def _build_top3(
    *,
    primary_pick: Optional[str],
    runners_up: list[str],
    candidate_id_set: set[str],
) -> list[str]:
    seen: list[str] = []
    for cand in [primary_pick, *list(runners_up or [])]:
        if not cand:
            continue
        cand = str(cand).strip()
        if cand and cand in candidate_id_set and cand not in seen:
            seen.append(cand)
        if len(seen) == 3:
            break
    return seen


def _aggregate_borda_strict(
    top3: list[str],
    pairwise_results: list[dict[str, Any]],
) -> tuple[Optional[str], dict[str, int]]:
    """Borda-count among top-3. Tiebreak: top3 order (Stage 1A's best wins ties)."""
    if not top3:
        return None, {}
    scores: dict[str, int] = {pgs_id: 0 for pgs_id in top3}
    for result in pairwise_results:
        winner = result.get("winner_model_id")
        if winner and winner in scores:
            scores[winner] = scores.get(winner, 0) + 1
    order = {pgs_id: idx for idx, pgs_id in enumerate(top3)}
    ranked = sorted(scores.keys(), key=lambda pid: (-scores[pid], order.get(pid, len(top3))))
    return ranked[0], scores


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")

    client = _client()

    # Stage 1A — pristine iterD-final picks
    print(f"\n=== Stage 1A (pristine iterD pick) — {len(requests)} requests, workers={workers} ===")
    stage1a_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_stage1a, client, model, request): request for request in requests}
        done = 0
        for future in as_completed(futures):
            res = future.result()
            stage1a_results[res["custom_id"]] = res
            done += 1
            if done % 20 == 0 or done == len(requests):
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage1A {done}/{len(requests)}] last={status} {res['ontology']}")
    print(f"Stage 1A elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pristine_pairwise_stage1a_results.json").write_text(
        json.dumps(list(stage1a_results.values()), indent=2), encoding="utf-8"
    )

    # Stage 1B — runner-up generator
    stage1b_jobs = []
    for request in requests:
        custom_id = request["custom_id"]
        s1a = stage1a_results.get(custom_id) or {}
        if s1a.get("error"):
            continue
        decision = s1a.get("decision") or {}
        primary_pick = decision.get("best_model_id")
        if not primary_pick:
            continue
        stage1b_jobs.append({
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "context_json": s1a["context_json"],
            "excluded_pgs_id": primary_pick,
        })

    print(f"\n=== Stage 1B (runner-up generator) — {len(stage1b_jobs)} requests, workers={workers} ===")
    stage1b_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_stage1b,
                client, model,
                custom_id=job["custom_id"],
                ontology=job["ontology"],
                context_json=job["context_json"],
                excluded_pgs_id=job["excluded_pgs_id"],
            ): job
            for job in stage1b_jobs
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            stage1b_results[res["custom_id"]] = res
            done += 1
            if done % 20 == 0 or done == len(stage1b_jobs):
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage1B {done}/{len(stage1b_jobs)}] last={status} {res['ontology']}")
    print(f"Stage 1B elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pristine_pairwise_stage1b_results.json").write_text(
        json.dumps(list(stage1b_results.values()), indent=2), encoding="utf-8"
    )

    # Build top-3 per ontology
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    domain_by_ontology: dict[str, dict[str, Any]] = {}
    for request in requests:
        ontology = request["ontology"]
        if ontology in domain_by_ontology:
            continue
        try:
            ctx = json.loads(_extract_context_json(request))
            domain_by_ontology[ontology] = ctx.get("domain_knowledge") or {}
        except Exception:
            domain_by_ontology[ontology] = {}

    top3_by_ontology: dict[str, list[str]] = {}
    pairwise_jobs: list[dict[str, Any]] = []
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        candidate_id_set = set(request["candidate_model_ids"])
        s1a = stage1a_results.get(custom_id) or {}
        primary = (s1a.get("decision") or {}).get("best_model_id")
        s1b = stage1b_results.get(custom_id) or {}
        runners = ((s1b.get("decision") or {}).get("runners_up") or [])
        top3 = _build_top3(
            primary_pick=primary,
            runners_up=runners,
            candidate_id_set=candidate_id_set,
        )
        top3_by_ontology[ontology] = top3
        if len(top3) < 2:
            continue
        for i in range(len(top3)):
            for j in range(i + 1, len(top3)):
                pairwise_jobs.append({
                    "ontology": ontology,
                    "candidate_a_id": top3[i],
                    "candidate_b_id": top3[j],
                })

    # Stage 2 — pairwise judge
    print(f"\n=== Stage 2 (pairwise) — {len(pairwise_jobs)} pair calls, workers={workers} ===")
    pairwise_results: list[dict[str, Any]] = []
    t0 = time.time()

    def _run_one(job: dict[str, Any]) -> dict[str, Any]:
        ontology = job["ontology"]
        a = job["candidate_a_id"]
        b = job["candidate_b_id"]
        cands = candidate_summary_by_ontology.get(ontology, {})
        return _run_pairwise(
            client, model,
            ontology=ontology,
            candidate_a_id=a,
            candidate_b_id=b,
            candidate_a_summary=cands.get(a, {"pgs_id": a}),
            candidate_b_summary=cands.get(b, {"pgs_id": b}),
            domain_knowledge=domain_by_ontology.get(ontology, {}),
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_one, job): job for job in pairwise_jobs}
        done = 0
        for future in as_completed(futures):
            res = future.result()
            pairwise_results.append(res)
            done += 1
            if done % 30 == 0 or done == len(pairwise_jobs):
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage2 {done}/{len(pairwise_jobs)}] last={status} {res['ontology']}")
    print(f"Stage 2 elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pristine_pairwise_stage2_results.json").write_text(
        json.dumps(pairwise_results, indent=2), encoding="utf-8"
    )

    # Aggregate via Borda
    pairwise_by_ontology: dict[str, list[dict[str, Any]]] = {}
    for res in pairwise_results:
        pairwise_by_ontology.setdefault(res["ontology"], []).append(res)

    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    final_pick_by_ontology: dict[str, Optional[str]] = {}
    borda_by_ontology: dict[str, dict[str, int]] = {}
    revised_count = 0

    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        s1a = stage1a_results.get(custom_id) or {}
        if s1a.get("error"):
            error_map[custom_id] = s1a["error"]
            continue
        primary_decision = s1a.get("decision") or {}
        primary_pick = primary_decision.get("best_model_id")
        top3 = top3_by_ontology.get(ontology, [])

        if len(top3) < 2:
            # Cannot pairwise rerank — use Stage 1A pick directly
            final_pick = primary_pick
        else:
            winner, scores = _aggregate_borda_strict(top3, pairwise_by_ontology.get(ontology, []))
            borda_by_ontology[ontology] = scores
            final_pick = winner if winner else primary_pick

        if final_pick != primary_pick and primary_pick is not None and final_pick is not None:
            revised_count += 1

        final_pick_by_ontology[ontology] = final_pick

        outcome = primary_decision.get("outcome") or "DIRECT_HIGH_QUALITY"
        confidence = primary_decision.get("confidence") or "Moderate"
        rationale = primary_decision.get("rationale") or ""
        if final_pick != primary_pick:
            confidence = "Moderate"
            rationale = (rationale + f" | Pairwise rerank promoted runner-up {final_pick} over primary {primary_pick}.").strip()

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

    # Wire output paths
    without_domain.RESULTS_JSON = output_run_dir / "experiment_pristine_pairwise_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_pristine_pairwise_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_pristine_pairwise_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_pristine_pairwise_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_pristine_pairwise_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_pristine_pairwise_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_pristine_pairwise_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_pristine_pairwise_batch_errors.jsonl"
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
    summary["execution_mode"] = "pristine_pairwise_chat_completions"
    summary["pristine_pairwise"] = {
        "stage1a_count": len(stage1a_results),
        "stage1b_count": len(stage1b_results),
        "pairwise_count": len(pairwise_results),
        "borda_revised_count": revised_count,
        "ontologies_with_invalid_top3": sum(
            1 for ontology, top3 in top3_by_ontology.items() if len(top3) < 2
        ),
        "borda_scores_by_ontology": borda_by_ontology,
        "top3_by_ontology": top3_by_ontology,
        "final_picks_by_ontology": final_pick_by_ontology,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Pristine Stage1 + pairwise reranking (Round 4)")
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"pristine-pairwise-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
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
