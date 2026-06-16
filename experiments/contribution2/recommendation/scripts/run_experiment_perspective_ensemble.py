"""Round 3 — Multi-perspective ensemble (Borda over 3 specialized prompts at t=0).

Hypothesis (Phase 1 + Round 1/2 grounded):
- A single picker prompt has to balance many evaluation dimensions (PRS-only
  metrics, training scale, ancestry breadth, covariate leakage, endpoint
  fidelity, heritability ceiling) and risks over-weighting one dimension.
- Round 2 confirmed that injecting diversity via TEMPERATURE hurts Hit@1
  (–3.4pp at k=5, t=0.7) — the noise dominates the runner-up signal.
- Round 1 confirmed that careful aggregation of multiple ranked outputs (its
  pairwise-on-top-3 stage) does lift Hit@1 (+3 vs iterD-final).
- Phase 1 (Anthropic harness paper, Bavaresco et al. 2026): structured
  perspectives applied to the same evidence outperform a single broad-judgment
  pass; Borda voting captures the consensus across perspectives.

Round 3 attacks the same signal with a structurally distinct mechanism: hold
the temperature at 0 (deterministic), and inject diversity via PROMPT FRAMING.
Three specialized Stage 1 prompts each over-weight a distinct subset of
evaluation dimensions; each emits a ranked top-3 over the SAME visible
candidate list and the SAME context (heritability + SKILL.md + corpus). Borda
aggregation across the three perspective rankings concentrates on candidates
strong on MULTIPLE dimensions, while still respecting the "no scoring formulas
/ no deterministic vetoes" constraint (the LLMs do the judging; Borda just
aggregates votes).

Distinct from prior failures:
- iterE (decision-protocol prose addition): added more text inside ONE prompt;
  Round 3 splits across THREE prompts so each is *narrower*, not broader.
- iterF/G + Round 2 (parallel sampling at non-zero temperature): noise.
  Round 3 is t=0 — every prompt is deterministic.
- pev-with-skill (TRIAGE/PICK/CRITIC): sequential refinement chain that
  over-revised. Round 3 is parallel + symmetric, not a refinement loop.
- Round 1 (pairwise judge): adds a separate Stage 2 LLM stage. Round 3 has
  NO Stage 2 — the aggregator is pure code.

Three perspectives:
  PERSPECTIVE_A — "PRS-only metric cleanliness + endpoint fidelity"
  PERSPECTIVE_B — "polygenic signal scale + transferability"
  PERSPECTIVE_C — "covariate cleanliness + packaging + heritability ceiling"

Each perspective inherits the system prompt's identity / persona / decision
boundary, but its instructions tell it to weigh ONE subset of factors more
heavily — without ever assigning numeric weights or deterministic vetoes,
preserving the LLM-led contract.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from collections import Counter
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
    WITHIN_PERSPECTIVE_A_FOCUS,
    WITHIN_PERSPECTIVE_B_FOCUS,
    WITHIN_PERSPECTIVE_C_FOCUS,
    WITHIN_PERSPECTIVE_USER_INSTRUCTION,
    build_within_perspective_prompt,
)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class Step1RankedDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    top_alternatives: list[str]
    confidence: str
    rationale: str


# ---------------------------------------------------------------------------
# Three perspective system prompts.
# Each preserves the iterD-final base prompt and appends a "Perspective" stanza
# that focuses on a subset of evaluation dimensions. The constraint set
# (no numeric scoring, no vetoes, no trait-specific rules) is restated.
# ---------------------------------------------------------------------------


def _perspective_prompt(focus_block: str) -> str:
    return build_within_perspective_prompt(
        base_prompt=WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        focus_block=focus_block,
    )


PERSPECTIVE_A_FOCUS = WITHIN_PERSPECTIVE_A_FOCUS
PERSPECTIVE_B_FOCUS = WITHIN_PERSPECTIVE_B_FOCUS
PERSPECTIVE_C_FOCUS = WITHIN_PERSPECTIVE_C_FOCUS
_USER_INSTRUCTION = WITHIN_PERSPECTIVE_USER_INSTRUCTION


PERSPECTIVES: list[tuple[str, str]] = [
    ("perspective_A_prs_only_cleanliness_and_endpoint_fidelity", PERSPECTIVE_A_FOCUS),
    ("perspective_B_polygenic_signal_scale_and_transferability", PERSPECTIVE_B_FOCUS),
    ("perspective_C_covariate_packaging_and_heritability_ceiling", PERSPECTIVE_C_FOCUS),
]


def _stage1_messages(perspective_focus: str, context_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": _perspective_prompt(perspective_focus)},
        {
            "role": "user",
            "content": f"{_USER_INSTRUCTION}\n\nContext:\n{context_json}",
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
# Borda
# ---------------------------------------------------------------------------

RANK_POINTS = [3, 2, 1]


def _ranked_list_from_decision(decision: dict[str, Any], candidate_id_set: set[str]) -> list[str]:
    seen: list[str] = []
    best = decision.get("best_model_id")
    if best:
        best = str(best).strip()
    alts = decision.get("top_alternatives") or []
    for cand in [best, *list(alts)]:
        if not cand:
            continue
        cand = str(cand).strip()
        if cand and cand in candidate_id_set and cand not in seen:
            seen.append(cand)
        if len(seen) == 3:
            break
    return seen


def _borda_aggregate(
    sample_rankings: list[list[str]],
) -> tuple[Optional[str], dict[str, float], list[tuple[str, int]]]:
    scores: dict[str, float] = {}
    top1_counts: Counter[str] = Counter()
    first_seen_index: dict[str, int] = {}
    for sample_idx, ranking in enumerate(sample_rankings):
        for rank_idx, pgs_id in enumerate(ranking[: len(RANK_POINTS)]):
            pts = RANK_POINTS[rank_idx]
            scores[pgs_id] = scores.get(pgs_id, 0.0) + float(pts)
            if rank_idx == 0:
                top1_counts[pgs_id] += 1
            if pgs_id not in first_seen_index:
                first_seen_index[pgs_id] = (sample_idx * 10) + rank_idx
    if not scores:
        return None, {}, []
    ranked = sorted(
        scores.keys(),
        key=lambda pid: (
            -scores[pid],
            -top1_counts.get(pid, 0),
            first_seen_index.get(pid, 1_000_000),
        ),
    )
    return ranked[0], scores, top1_counts.most_common()


# ---------------------------------------------------------------------------
# OpenAI client + sample
# ---------------------------------------------------------------------------

def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _sample(
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


def _run_one_perspective(
    client: OpenAI,
    *,
    model: str,
    request: dict[str, Any],
    perspective_id: str,
    perspective_focus: str,
) -> dict[str, Any]:
    custom_id = request["custom_id"]
    body = request["request"]["body"]
    user_messages = body["messages"]
    original_user = user_messages[1]["content"]
    marker = "Context:\n"
    idx = original_user.find(marker)
    if idx < 0:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "perspective_id": perspective_id,
            "decision": None,
            "error": "Context marker not found",
        }
    context_json = original_user[idx + len(marker):]
    messages = _stage1_messages(perspective_focus, context_json)
    try:
        content = _sample(
            client,
            model=model,
            messages=messages,
            response_format=_stage1_response_format(),
        )
        decision = Step1RankedDecision.model_validate_json(content)
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "perspective_id": perspective_id,
            "decision": decision.model_dump(),
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "perspective_id": perspective_id,
            "decision": None,
            "error": f"perspective {type(exc).__name__}: {exc}",
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
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")
    print(f"Perspectives: {[pid for pid, _ in PERSPECTIVES]}")

    client = _client()

    jobs = []
    for request in requests:
        for perspective_id, perspective_focus in PERSPECTIVES:
            jobs.append({
                "request": request,
                "perspective_id": perspective_id,
                "perspective_focus": perspective_focus,
            })
    print(f"\n=== Sampling — {len(jobs)} calls (workers={workers}) ===")
    sample_results: list[dict[str, Any]] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_one_perspective,
                client,
                model=model,
                request=job["request"],
                perspective_id=job["perspective_id"],
                perspective_focus=job["perspective_focus"],
            ): job
            for job in jobs
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            sample_results.append(res)
            done += 1
            if done % 50 == 0 or done == len(jobs):
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [perspective {done}/{len(jobs)}] last={status} "
                      f"{res['ontology']} {res['perspective_id']}")
    print(f"Sampling elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_perspective_ensemble_samples.json").write_text(
        json.dumps(sample_results, indent=2), encoding="utf-8"
    )

    # Group by ontology and aggregate
    by_request: dict[str, list[dict[str, Any]]] = {}
    for res in sample_results:
        by_request.setdefault(res["custom_id"], []).append(res)

    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    aggregation_meta: dict[str, dict[str, Any]] = {}

    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        candidate_id_set = set(request["candidate_model_ids"])
        # Stable order: A, B, C
        recs_by_id = {r["perspective_id"]: r for r in by_request.get(custom_id, [])}
        sample_rankings: list[list[str]] = []
        sample_decisions: list[dict[str, Any]] = []
        last_error: Optional[str] = None
        for pid, _ in PERSPECTIVES:
            rec = recs_by_id.get(pid)
            if rec is None:
                last_error = f"missing perspective {pid}"
                continue
            if rec.get("error"):
                last_error = rec["error"]
                continue
            decision = rec.get("decision") or {}
            ranking = _ranked_list_from_decision(decision, candidate_id_set)
            sample_rankings.append(ranking)
            sample_decisions.append(decision)

        if not sample_rankings:
            error_map[custom_id] = last_error or "no valid perspectives"
            aggregation_meta[ontology] = {
                "borda_scores": {},
                "perspective_rankings": [],
                "winner": None,
                "n_valid_perspectives": 0,
            }
            continue

        winner, scores, top1_counts = _borda_aggregate(sample_rankings)

        # Choose representative outcome / confidence / rationale from the
        # perspective whose top-1 == winner (else the first perspective's).
        chosen_decision: Optional[dict[str, Any]] = None
        for decision, ranking in zip(sample_decisions, sample_rankings):
            if ranking and ranking[0] == winner:
                chosen_decision = decision
                break
        if chosen_decision is None and sample_decisions:
            chosen_decision = sample_decisions[0]

        outcome = (chosen_decision or {}).get("outcome") or "DIRECT_HIGH_QUALITY"
        confidence = (chosen_decision or {}).get("confidence") or "Moderate"
        rationale = (chosen_decision or {}).get("rationale") or ""
        first_top1 = sample_rankings[0][0] if sample_rankings[0] else None
        if winner != first_top1:
            confidence = "Moderate"
            rationale = (rationale + f" | Borda re-rank promoted {winner} via cross-perspective consensus.").strip()

        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": outcome,
                "best_model_id": winner,
                "confidence": confidence,
                "rationale": rationale,
            }],
            "error": None,
        }
        aggregation_meta[ontology] = {
            "borda_scores": scores,
            "perspective_rankings": [
                {"perspective_id": pid, "ranking": ranking}
                for (pid, _), ranking in zip(PERSPECTIVES, sample_rankings)
            ],
            "top1_counts": top1_counts,
            "winner": winner,
            "n_valid_perspectives": len(sample_rankings),
        }

    # Wire output paths
    without_domain.RESULTS_JSON = output_run_dir / "experiment_perspective_ensemble_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_perspective_ensemble_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_perspective_ensemble_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_perspective_ensemble_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_perspective_ensemble_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_perspective_ensemble_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_perspective_ensemble_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_perspective_ensemble_batch_errors.jsonl"
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
    summary["execution_mode"] = "perspective_ensemble_chat_completions"
    summary["perspective_ensemble"] = {
        "perspectives": [pid for pid, _ in PERSPECTIVES],
        "rank_points": RANK_POINTS,
        "aggregation_by_ontology": aggregation_meta,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Perspective ensemble (Round 3)")
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
    run_dir_name = f"perspective-ensemble-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
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
