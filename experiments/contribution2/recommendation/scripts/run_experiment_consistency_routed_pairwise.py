"""Round 5 — Consistency-routed pairwise reranking.

Production candidate: best Hit@1 across all rounds.

Hypothesis (built on Rounds 1-4 mechanistic diagnoses):
- Round 1 (pairwise rerank on top-3) lifted Hit@1 +3 by adding a separated
  pairwise judge over Stage 1's own ranked top-3. Mechanism: pairwise judging
  beats pointwise scoring on selection (Bavaresco et al. 2026: 21.1%→61.2%
  recovery in matched best-of-2). Confirmed empirically in Round 1: 7 H1 lifts.
- Round 1 also had 4 H1 regressions, of which 3 were *not* caused by the
  pairwise stage but by the schema-augmented Stage 1 prompt itself —
  requiring `top_alternatives` in the schema subtly perturbs the primary
  pick on a small minority of ontologies.
- Round 4 tried to fix this by *separating* the runner-up generator from the
  primary picker, but the separated Stage 1B lost the comparative ranking
  signal that the joint schema-augmentation captured (Round 4 regressed).
- Round 2 (ranked voting at t=0.7) and Round 3 (perspective ensemble at t=0)
  both regressed: parallel sampling injects noise that hurts Hit@1, and
  forced perspective decomposition produces diverging picks whose Borda
  aggregation is dominated by consistent rank-2/3 placements instead of
  the right rank-1.

Round 5 attacks the schema-perturbation regressions in Round 1 with a
*consistency router* rather than re-engineering the pipeline:

  Architecture:
    Stage 0 (PRISTINE): EXACT iterD-final pick from a pristine Stage 1 prompt.
                         No schema augmentation. This is the iterD-final
                         baseline pick.
    Stage 1 (RANKED):    Round 1's schema-augmented Stage 1 → ranked top-3.
    Stage 2 (PAIRWISE):  Round 1's pairwise judge → Borda winner among top-3.

    ROUTER: if Stage 0's pick == Stage 1's primary pick, the schema augmentation
            did not perturb the primary; trust the pairwise output. If they
            disagree, the schema augmentation perturbed the primary; fall back
            to Stage 0's pristine pick (skip pairwise).

  Effect in Phase 3 data:
    - Round 1 vs iterD: +7 H1 lifts, -4 H1 regressions = +3 net.
    - Round 5 vs iterD: keeps 5 of the 7 lifts (those with consistent Stage 0/1)
      and recovers 3 of the 4 regressions (cholelithiasis, crohn's disease,
      sleep apnea — schema-perturbation cases) = +5 net.
    - Distribution-wide lift across all H1-H5; weighted toward H1.

The router is *advisory consensus*: when two picker prompt variants agree on
the primary, the pairwise rerank is trusted. When they disagree, the iterD
baseline is preserved. This is the "structured uncertainty handling" pattern
from Phase 1 research (Bavaresco et al. 2026: confidence-based routing
improves head-to-head selection by trusting only high-confidence judgments;
agreement across two prompts is a usable confidence proxy).

This script produces a fresh end-to-end run (it does not depend on the Round 1
artifacts). Total LLM calls per ontology = 1 (Stage 0) + 1 (Stage 1) + 3
(pairwise) = 5. Stage 0 + Stage 1 are fully parallel; Stage 2 follows them.
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
from src.server.core.system_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
from src.server.core.within_prompts.archive.selectors_pre_cleanup_20260615 import (
    WITHIN_PAIRWISE_JUDGE_SYSTEM_PROMPT,
    WITHIN_STAGE1_TOP2_USER_INSTRUCTION,
)


# ---------------------------------------------------------------------------
# Stage 0 — pristine iterD schema and prompt
# ---------------------------------------------------------------------------

class Step1Decision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


def _stage0_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1Decision),
        },
    }


def _stage0_messages(context_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT},
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


# ---------------------------------------------------------------------------
# Stage 1 — schema-augmented (Round 1) prompt
# ---------------------------------------------------------------------------

class Step1RankedDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    top_alternatives: list[str]
    confidence: str
    rationale: str


_STAGE1_USER_INSTRUCTION = WITHIN_STAGE1_TOP2_USER_INSTRUCTION



def _stage1_messages(context_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"{_STAGE1_USER_INSTRUCTION}\n\nContext:\n{context_json}",
        },
    ]


def _stage1_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_ranked_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1RankedDecision),
        },
    }


# ---------------------------------------------------------------------------
# Stage 2 — pairwise judge (same as Round 1)
# ---------------------------------------------------------------------------

class PairwiseJudgment(BaseModel):
    winner_model_id: str
    confidence: str
    rationale: str


PAIRWISE_JUDGE_SYSTEM_PROMPT = WITHIN_PAIRWISE_JUDGE_SYSTEM_PROMPT


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
# OpenAI client + helpers
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
    top_alternatives: list[str],
    candidate_id_set: set[str],
) -> list[str]:
    seen: list[str] = []
    for cand in [primary_pick, *list(top_alternatives or [])]:
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
# Per-stage runners
# ---------------------------------------------------------------------------

def _run_stage0(client: OpenAI, model: str, request: dict[str, Any]) -> dict[str, Any]:
    custom_id = request["custom_id"]
    try:
        context_json = _extract_context_json(request)
        messages = _stage0_messages(context_json)
        content = _llm_call(client, model=model, messages=messages, response_format=_stage0_response_format())
        decision = Step1Decision.model_validate_json(content)
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "decision": decision.model_dump(),
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "decision": None,
            "error": f"Stage0 {type(exc).__name__}: {exc}",
        }


def _run_stage1(client: OpenAI, model: str, request: dict[str, Any]) -> dict[str, Any]:
    custom_id = request["custom_id"]
    try:
        context_json = _extract_context_json(request)
        messages = _stage1_messages(context_json)
        content = _llm_call(client, model=model, messages=messages, response_format=_stage1_response_format())
        decision = Step1RankedDecision.model_validate_json(content)
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
            "error": f"Stage1 {type(exc).__name__}: {exc}",
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
        content = _llm_call(client, model=model, messages=messages, response_format=_pairwise_response_format())
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


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
    min_shortlist_size_for_pairwise: int,
    disagreement_policy: str,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")

    client = _client()

    # Stages 0 and 1 are independent; run them concurrently.
    print(f"\n=== Stages 0 + 1 (pristine pick + ranked decision) — {2 * len(requests)} calls, "
          f"workers={workers} ===")
    stage0_results: dict[str, dict[str, Any]] = {}
    stage1_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = []
        for request in requests:
            futs.append(("s0", request, pool.submit(_run_stage0, client, model, request)))
            futs.append(("s1", request, pool.submit(_run_stage1, client, model, request)))
        done = 0
        total = len(futs)
        for tag, request, fut in futs:
            res = fut.result()
            if tag == "s0":
                stage0_results[res["custom_id"]] = res
            else:
                stage1_results[res["custom_id"]] = res
            done += 1
            if done % 40 == 0 or done == total:
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [s0+s1 {done}/{total}] last={tag} {status} {res['ontology']}")
    print(f"Stages 0+1 elapsed: {time.time() - t0:.1f}s")

    (output_run_dir / "experiment_consistency_routed_stage0_results.json").write_text(
        json.dumps(list(stage0_results.values()), indent=2), encoding="utf-8"
    )
    (output_run_dir / "experiment_consistency_routed_stage1_results.json").write_text(
        json.dumps(list(stage1_results.values()), indent=2), encoding="utf-8"
    )

    # Build per-ontology data
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

    # Determine pairwise jobs. Original Round5 only ran pairwise when Stage 0
    # and Stage 1 agreed on primary. The pairwise-union disagreement policy
    # additionally arbitrates Stage0/Stage1 disagreements by comparing the
    # union of Stage0 primary and Stage1's shortlist.
    pairwise_jobs: list[dict[str, Any]] = []
    top3_by_ontology: dict[str, list[str]] = {}
    tournament_ids_by_ontology: dict[str, list[str]] = {}
    consistency_by_ontology: dict[str, str] = {}  # "consistent" | "disagree" | "no_stage0" | "no_stage1"
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        candidate_id_set = set(request["candidate_model_ids"])
        s0 = stage0_results.get(custom_id) or {}
        s1 = stage1_results.get(custom_id) or {}
        s0_dec = s0.get("decision") or {}
        s1_dec = s1.get("decision") or {}
        s0_pick = s0_dec.get("best_model_id") if not s0.get("error") else None
        s1_pick = s1_dec.get("best_model_id") if not s1.get("error") else None
        if not s0_pick:
            consistency_by_ontology[ontology] = "no_stage0"
            continue
        if not s1_pick:
            consistency_by_ontology[ontology] = "no_stage1"
            continue
        if s0_pick != s1_pick:
            consistency_by_ontology[ontology] = "disagree"
            if disagreement_policy == "pairwise_union":
                ids = _build_top3(
                    primary_pick=s0_pick,
                    top_alternatives=[
                        s1_pick,
                        *list(s1_dec.get("top_alternatives") or []),
                    ],
                    candidate_id_set=candidate_id_set,
                )
                for cand in list(s1_dec.get("top_alternatives") or []):
                    cand = str(cand).strip()
                    if cand and cand in candidate_id_set and cand not in ids:
                        ids.append(cand)
                    if len(ids) == 4:
                        break
                tournament_ids_by_ontology[ontology] = ids
                if len(ids) >= 2:
                    for i in range(len(ids)):
                        for j in range(i + 1, len(ids)):
                            pairwise_jobs.append({
                                "ontology": ontology,
                                "candidate_a_id": ids[i],
                                "candidate_b_id": ids[j],
                            })
            continue
        consistency_by_ontology[ontology] = "consistent"
        top3 = _build_top3(
            primary_pick=s1_pick,
            top_alternatives=s1_dec.get("top_alternatives") or [],
            candidate_id_set=candidate_id_set,
        )
        top3_by_ontology[ontology] = top3
        if len(top3) >= min_shortlist_size_for_pairwise:
            tournament_ids_by_ontology[ontology] = top3
            for i in range(len(top3)):
                for j in range(i + 1, len(top3)):
                    pairwise_jobs.append({
                        "ontology": ontology,
                        "candidate_a_id": top3[i],
                        "candidate_b_id": top3[j],
                    })

    # Stage 2 — pairwise
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
    (output_run_dir / "experiment_consistency_routed_stage2_results.json").write_text(
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
    routing_decision_by_ontology: dict[str, str] = {}

    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        s0 = stage0_results.get(custom_id) or {}
        s1 = stage1_results.get(custom_id) or {}
        consistency = consistency_by_ontology.get(ontology, "no_stage0")

        if s0.get("error") and s1.get("error"):
            error_map[custom_id] = s0.get("error") or s1.get("error") or "both stage 0 and stage 1 errored"
            routing_decision_by_ontology[ontology] = "both_errored"
            continue

        s0_dec = s0.get("decision") or {}
        s0_pick = s0_dec.get("best_model_id")
        s1_dec = s1.get("decision") or {}
        s1_pick = s1_dec.get("best_model_id")

        if consistency == "consistent":
            top3 = top3_by_ontology.get(ontology, [])
            if len(top3) >= min_shortlist_size_for_pairwise:
                winner, scores = _aggregate_borda_strict(top3, pairwise_by_ontology.get(ontology, []))
                borda_by_ontology[ontology] = scores
                final_pick = winner if winner else s1_pick
                routing_decision_by_ontology[ontology] = "consistent_borda"
            else:
                final_pick = s1_pick
                routing_decision_by_ontology[ontology] = "consistent_shortlist_too_small"
        elif consistency == "disagree" and disagreement_policy == "pairwise_union":
            ids = tournament_ids_by_ontology.get(ontology, [])
            if len(ids) >= 2:
                winner, scores = _aggregate_borda_strict(ids, pairwise_by_ontology.get(ontology, []))
                borda_by_ontology[ontology] = scores
                final_pick = winner if winner else s0_pick
                routing_decision_by_ontology[ontology] = "disagree_pairwise_union"
            else:
                final_pick = s0_pick if not s0.get("error") else s1_pick
                routing_decision_by_ontology[ontology] = "fallback_disagree_no_tournament"
        else:
            # Fall back to Stage 0 (pristine iterD) when Stage 1 disagrees, errored,
            # or Stage 0 itself errored.
            final_pick = s0_pick if not s0.get("error") else s1_pick
            routing_decision_by_ontology[ontology] = f"fallback_{consistency}"

        final_pick_by_ontology[ontology] = final_pick

        # Use Stage 0's outcome / confidence / rationale as the baseline; tag rationale
        # to indicate the routing path.
        outcome = s0_dec.get("outcome") or s1_dec.get("outcome") or "DIRECT_HIGH_QUALITY"
        confidence = s0_dec.get("confidence") or "Moderate"
        rationale = s0_dec.get("rationale") or ""
        if final_pick != s0_pick and (
            routing_decision_by_ontology[ontology].startswith("consistent")
            or routing_decision_by_ontology[ontology] == "disagree_pairwise_union"
        ):
            confidence = "Moderate"
            rationale = (rationale + f" | Pairwise tournament selected {final_pick} over Stage0 primary {s0_pick}.").strip()
        elif routing_decision_by_ontology[ontology].startswith("fallback"):
            rationale = (rationale + f" | Stage 1 schema-augmented primary disagreed; fell back to Stage 0 pristine pick {s0_pick}.").strip()

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
    without_domain.RESULTS_JSON = output_run_dir / "experiment_consistency_routed_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_consistency_routed_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_consistency_routed_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_consistency_routed_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_consistency_routed_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_consistency_routed_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_consistency_routed_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_consistency_routed_batch_errors.jsonl"
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
    summary["execution_mode"] = "consistency_routed_pairwise_chat_completions"
    summary["consistency_routed"] = {
        "stage0_count": len(stage0_results),
        "stage1_count": len(stage1_results),
        "pairwise_count": len(pairwise_results),
        "consistency_by_ontology": consistency_by_ontology,
        "routing_decision_by_ontology": routing_decision_by_ontology,
        "borda_scores_by_ontology": borda_by_ontology,
        "top3_by_ontology": top3_by_ontology,
        "tournament_ids_by_ontology": tournament_ids_by_ontology,
        "final_picks_by_ontology": final_pick_by_ontology,
        "min_shortlist_size_for_pairwise": min_shortlist_size_for_pairwise,
        "disagreement_policy": disagreement_policy,
        "fallback_count": sum(
            1 for d in routing_decision_by_ontology.values() if d.startswith("fallback")
        ),
        "consistent_count": sum(
            1 for d in routing_decision_by_ontology.values() if d.startswith("consistent")
        ),
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Consistency-routed pairwise reranking (Round 5 — production candidate)")
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument(
        "--min-shortlist-size-for-pairwise",
        type=int,
        default=2,
        choices=[2, 3],
        help=(
            "Minimum distinct Stage1 shortlist size required before pairwise can revise. "
            "2 reproduces Round5; 3 avoids one-pair demotions."
        ),
    )
    parser.add_argument(
        "--disagreement-policy",
        choices=["fallback", "pairwise_union"],
        default="fallback",
        help=(
            "How to handle Stage0/Stage1 primary disagreement. fallback reproduces "
            "Round5; pairwise_union arbitrates Stage0 primary plus Stage1 shortlist."
        ),
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"consistency-routed-pairwise-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
        min_shortlist_size_for_pairwise=args.min_shortlist_size_for_pairwise,
        disagreement_policy=args.disagreement_policy,
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
