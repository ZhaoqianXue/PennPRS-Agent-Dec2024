"""Round 2 — Ranked Voting (Borda) over k=5 samples emitting top-3 rankings.

Hypothesis (Phase 1 + Round 1 grounded):
- Phase 1, Wang & Lou 2025 (Ranked Voting Self-Consistency): ranked-voting
  beats majority-voting on selection tasks by 4.95% on lightweight models and
  2.68%–3.51% on 7B–9B class models. The mechanism: each sample emits a ranked
  list, and Borda count aggregates across samples — runner-up positions encode
  information that majority-on-top-1 throws away.
- Phase 3, iterF (3 trials majority @ t=0): –4.1pp vs iterD-final.
- Phase 3, iterG (5 trials majority @ t=0.3): –3.6pp vs iterD-final.
- Round 1 diagnosis: Stage 1's top-3 frequently contains the right candidate;
  the real signal lives in the rank-2 and rank-3 positions, not just the top-1.
  Round 1 captured that signal via pairwise judging, with 21 Borda-revisions
  yielding 7 lifts and 4 regressions for net +3.

Round 2 attacks the same signal with a *different* pattern class. Instead of a
separated pairwise judge, we draw k=5 independent ranked-top-3 samples at t=0.7
(matching the Wang & Lou paper) from the same Stage 1 prompt and aggregate via
Borda count: each sample contributes 3 / 2 / 1 points to its top-1 / top-2 /
top-3 candidates. Final pick = max Borda; tiebreak prefers the modal top-1.

Why this is distinct from iterF/G:
- iterF/G voted on single picks (`best_model_id`), so at low temperature the
  votes degenerate (5 identical answers → one vote = one answer). At t=0 there
  was no diversity. At t=0.3 there was some diversity but the vote couldn't
  use the runner-up signal.
- Ranked voting at t=0.7 (a) injects enough diversity for samples to disagree,
  (b) aggregates the disagreement via Borda which captures consistent runner-up
  consensus, (c) does not depend on a separate evaluator stage.

Why this is distinct from Round 1:
- Round 1 = single Stage 1 sample + separate pairwise judge stage.
- Round 2 = k parallel Stage 1 samples + deterministic Borda aggregation.
- No Stage 2 LLM; the aggregator is pure code.

Total LLM calls per ontology = 5 (vs 1 in iterD-final, 4 in Round 1).
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
    WITHIN_STAGE1_TOP2_USER_INSTRUCTION,
)


# ---------------------------------------------------------------------------
# Schema (Stage 1 ranked decision; matches Round 1's schema)
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
# Borda aggregator — points by rank position
# ---------------------------------------------------------------------------

# Each sample contributes points: rank-1 = 3, rank-2 = 2, rank-3 = 1
RANK_POINTS = [3, 2, 1]


def _ranked_list_from_decision(decision: dict[str, Any], candidate_id_set: set[str]) -> list[str]:
    """Return up to 3 distinct, candidate-set-valid PGS IDs in
    [best, alt1, alt2] order (deduplicated, preserving first occurrence)."""
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
    """Aggregate k ranked top-3 lists via Borda count.
    Returns (winner, scores, sorted_top1_counts).

    Tiebreak rule:
      1. Highest Borda score wins.
      2. If tied, the candidate with the most rank-1 votes wins.
      3. If still tied, fall back to the candidate that appeared earliest in
         the first sample's ranking (deterministic stable order).
    """
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
    temperature: float,
    seed: int,
) -> str:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
        "temperature": temperature,
        "seed": seed,
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


def _run_single_sample(
    client: OpenAI,
    *,
    model: str,
    request: dict[str, Any],
    temperature: float,
    seed: int,
    sample_idx: int,
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
            "sample_idx": sample_idx,
            "decision": None,
            "error": "Context marker not found in original user message",
        }
    context_json = original_user[idx + len(marker):]
    messages = _stage1_messages(context_json)
    try:
        content = _sample(
            client,
            model=model,
            messages=messages,
            response_format=_stage1_response_format(),
            temperature=temperature,
            seed=seed,
        )
        decision = Step1RankedDecision.model_validate_json(content)
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "sample_idx": sample_idx,
            "decision": decision.model_dump(),
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "sample_idx": sample_idx,
            "decision": None,
            "error": f"sample {type(exc).__name__}: {exc}",
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
    n_samples: int,
    temperature: float,
    base_seed: int,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")
    print(f"Sampling: n={n_samples}, t={temperature}, seed={base_seed}..{base_seed + n_samples - 1}")

    client = _client()

    # Generate the (request, sample_idx, seed) job list
    jobs = []
    for request in requests:
        for s_idx in range(n_samples):
            jobs.append({
                "request": request,
                "sample_idx": s_idx,
                "seed": base_seed + s_idx,
            })
    print(f"\n=== Sampling — {len(jobs)} calls (workers={workers}) ===")
    sample_results: list[dict[str, Any]] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_single_sample,
                client,
                model=model,
                request=job["request"],
                temperature=temperature,
                seed=job["seed"],
                sample_idx=job["sample_idx"],
            ): job
            for job in jobs
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            sample_results.append(res)
            done += 1
            status = "ok" if res["error"] is None else "ERR"
            if done % 50 == 0 or done == len(jobs):
                print(f"  [sample {done}/{len(jobs)}] last={status} {res['ontology']} #{res['sample_idx']}")
    print(f"Sampling elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_ranked_voting_samples.json").write_text(
        json.dumps(sample_results, indent=2), encoding="utf-8"
    )

    # Aggregate per ontology via Borda
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
        sample_recs = sorted(by_request.get(custom_id, []), key=lambda r: r["sample_idx"])
        sample_rankings: list[list[str]] = []
        sample_decisions: list[dict[str, Any]] = []
        any_error: Optional[str] = None
        for rec in sample_recs:
            if rec.get("error"):
                any_error = rec["error"]
                continue
            decision = rec.get("decision") or {}
            ranking = _ranked_list_from_decision(decision, candidate_id_set)
            sample_rankings.append(ranking)
            sample_decisions.append(decision)

        if not sample_rankings:
            error_map[custom_id] = any_error or "No valid samples"
            aggregation_meta[ontology] = {
                "borda_scores": {},
                "sample_rankings": [],
                "winner": None,
                "n_valid_samples": 0,
            }
            continue

        winner, scores, top1_counts = _borda_aggregate(sample_rankings)

        # Choose representative outcome / confidence / rationale from the sample
        # whose top-1 == winner (preferring the FIRST one for stability).
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
        # If winner does NOT match the first sample's top-1, mark Borda re-rank.
        first_top1 = sample_rankings[0][0] if sample_rankings[0] else None
        if winner != first_top1:
            confidence = "Moderate"
            rationale = (rationale + f" | Borda re-rank promoted {winner} from runner-up positions.").strip()

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
            "sample_rankings": sample_rankings,
            "top1_counts": top1_counts,
            "winner": winner,
            "n_valid_samples": len(sample_rankings),
        }

    # Wire output paths
    without_domain.RESULTS_JSON = output_run_dir / "experiment_ranked_voting_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_ranked_voting_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_ranked_voting_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_ranked_voting_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_ranked_voting_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_ranked_voting_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_ranked_voting_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_ranked_voting_batch_errors.jsonl"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
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
    summary["execution_mode"] = "ranked_voting_chat_completions"
    summary["ranked_voting"] = {
        "n_samples_per_ontology": n_samples,
        "temperature": temperature,
        "rank_points": RANK_POINTS,
        "aggregation_by_ontology": aggregation_meta,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Ranked voting (Borda) over k samples (Round 2)")
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--n-samples", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--base-seed", type=int, default=42)
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"ranked-voting-{args.model}-t{args.n_samples}__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
        n_samples=args.n_samples,
        temperature=args.temperature,
        base_seed=args.base_seed,
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
