"""Replay pairwise Stage2 from a frozen double-stage run.

This analysis-only helper freezes the Stage1 carried-forward candidate universe
from a completed run and reruns only pairwise Stage2 comparisons on selected
traits. It is intended for low-cost Stage2 iteration without rerunning Stage1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.analysis.target10_hit1 import replay_stage2_from_run
from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr


FORBIDDEN_PROMPT_PATTERNS = (
    r"selection_proxy",
    r"first-pass proxy",
    r"mandatory first-pass",
    r"Select the rank-1",
    r"rank-1 proxy",
    r"proxy winner",
    r"external-validation performance",
    r"external validation shortlist",
    r"benchmark-selection",
    r"benchmark selection",
)


PERFORMANCE_FORWARD_PAIRWISE_SYSTEM_PROMPT = """# Identity & Persona
You are a PRS pairwise model-selection judge for within-phenotype
recommendation.
Choose which of two visible PGS Catalog candidates has stronger same-trait
predictive-performance support for the target trait and target ancestry.

# Decision Boundary
- winner_model_id must be exactly one of candidate_a_id or candidate_b_id.
- Candidate A/B labels and any upstream order are not evidence.
- Do not introduce another candidate, propose a tie, search externally, use PGS
  ID memory, use trait-specific priors, or use disease-category shortcuts.
- Use only visible candidate fields and skill_context.

# Selection Discipline
- Identify each candidate's strongest endpoint-compatible signal before
  choosing.
- Treat routine-adjusted performance rows as live predictive evidence. Routine
  covariates include age, sex, genotyping array/batch, site/center, assessment
  center, and ancestry PCs.
- Do not default to covariate-free PRS-only rows when the other candidate has
  visibly stronger direct-match support under routine adjustment, incremental
  genetic contribution, effect size, tail enrichment, case enrichment, or
  same-context sibling dominance.
- Family history, treatment, mediator, biomarker, horizon-conditioned, or broad
  clinical-risk packaging can weaken comparability. Routine adjustment alone is
  not a hard defect.
- Same-context near-clone rows are high-value evidence: if endpoint,
  cohort/sample context, ancestry, covariates, and metric family match, prefer
  the candidate with stronger same-context numeric evidence.
- Reject a stronger-looking row only for a concrete defect: endpoint mismatch,
  non-genetic clinical/family-history packaging, non-routine leakage, severe
  ancestry/context mismatch without compensating evidence, incompatible outcome
  horizon, or ambiguous row context that prevents comparison.

# Output Requirements
Return one JSON object with exactly these fields:
{
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}

# Output Discipline
- rationale must be grounded only in visible evidence and must reference both
  candidates.
- Do not expose raw chain-of-thought.
- Do not include extra keys.
"""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_map(stage1_row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    context = json.loads(stage1_row["context_json"])
    models = context.get("direct_models", {}).get("models") or []
    return context, {str(model.get("id")): model for model in models if model.get("id")}


def _rank_map(result_row: dict[str, Any]) -> dict[str, int]:
    return {pgs_id: idx + 1 for idx, pgs_id in enumerate(result_row.get("benchmark_ranked_ids") or [])}


def _pair_jobs_for_rows(
    *,
    stage1_rows: list[dict[str, Any]],
    stage2_rows: list[dict[str, Any]],
    stage2_candidate_order: str,
    stage2_candidate_order_seed: str,
    pair_source: str,
) -> list[dict[str, Any]]:
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    jobs: list[dict[str, Any]] = []
    for stage2_row in stage2_rows:
        ontology = stage2_row["ontology"]
        context, candidate_summaries = _candidate_map(stage1_by_ontology[ontology])
        ranked_candidate_ids = replay_stage2_from_run._order_stage2_candidate_ids(
            ontology=ontology,
            ranked_candidate_ids=list(stage2_row.get("ranked_candidate_ids") or []),
            candidate_order=stage2_candidate_order,
            candidate_order_seed=stage2_candidate_order_seed,
        )
        pairs: list[tuple[str, str]] = []
        if pair_source == "all_pairs":
            for i in range(len(ranked_candidate_ids)):
                for j in range(i + 1, len(ranked_candidate_ids)):
                    pairs.append((ranked_candidate_ids[i], ranked_candidate_ids[j]))
        elif pair_source == "stage1_vs_stage2":
            stage1_best = (stage1_by_ontology[ontology].get("decision") or {}).get("best_model_id")
            stage2_winner = stage2_row.get("winner_model_id")
            if (
                stage1_best
                and stage2_winner
                and stage1_best != stage2_winner
                and stage1_best in candidate_summaries
                and stage2_winner in candidate_summaries
            ):
                pairs.append((stage1_best, stage2_winner))
        else:
            raise ValueError(f"Unsupported pair_source: {pair_source}")
        for candidate_a_id, candidate_b_id in pairs:
            jobs.append({
                "ontology": ontology,
                "target_ancestry": context.get("target_ancestry"),
                "skill_context": context.get("skill_context") or {},
                "ranked_candidate_ids": ranked_candidate_ids,
                "candidate_a_id": candidate_a_id,
                "candidate_b_id": candidate_b_id,
                "candidate_a_summary": candidate_summaries.get(candidate_a_id, {}),
                "candidate_b_summary": candidate_summaries.get(candidate_b_id, {}),
            })
    return jobs


def _inspect_messages(
    *,
    stage1_rows: list[dict[str, Any]],
    stage2_rows: list[dict[str, Any]],
    stage2_candidate_order: str,
    stage2_candidate_order_seed: str,
    pair_source: str,
    pairwise_prompt: str,
) -> dict[str, Any]:
    jobs = _pair_jobs_for_rows(
        stage1_rows=stage1_rows,
        stage2_rows=stage2_rows,
        stage2_candidate_order=stage2_candidate_order,
        stage2_candidate_order_seed=stage2_candidate_order_seed,
        pair_source=pair_source,
    )
    forbidden_hits: list[dict[str, str]] = []
    universe_mismatches: list[dict[str, Any]] = []
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    for stage2_row in stage2_rows:
        ontology = stage2_row["ontology"]
        stage1_row = stage1_by_ontology[ontology]
        context, candidate_summaries = _candidate_map(stage1_row)
        decision = stage1_row.get("decision") or {}
        carried = pr._select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=set(candidate_summaries),
            top_k=None,
        )
        ranked_candidate_ids = replay_stage2_from_run._order_stage2_candidate_ids(
            ontology=ontology,
            ranked_candidate_ids=list(stage2_row.get("ranked_candidate_ids") or []),
            candidate_order=stage2_candidate_order,
            candidate_order_seed=stage2_candidate_order_seed,
        )
        if set(carried) != set(ranked_candidate_ids):
            universe_mismatches.append({
                "ontology": ontology,
                "from_stage1_decision": carried,
                "from_stage2_artifact": list(stage2_row.get("ranked_candidate_ids") or []),
                "llm_visible_stage2_order": ranked_candidate_ids,
            })
    for job in jobs:
        if pairwise_prompt == "performance_forward":
            messages = [
                {"role": "system", "content": PERFORMANCE_FORWARD_PAIRWISE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": pr._build_pairwise_user_message(
                        target_trait=job["ontology"],
                        target_ancestry=job["target_ancestry"],
                        candidate_a_id=job["candidate_a_id"],
                        candidate_b_id=job["candidate_b_id"],
                        candidate_a_summary=job["candidate_a_summary"],
                        candidate_b_summary=job["candidate_b_summary"],
                        skill_context=job["skill_context"],
                    ),
                },
            ]
        else:
            messages = pr._pairwise_messages_for_arm(
                target_trait=job["ontology"],
                target_ancestry=job["target_ancestry"],
                candidate_a_id=job["candidate_a_id"],
                candidate_b_id=job["candidate_b_id"],
                candidate_a_summary=job["candidate_a_summary"],
                candidate_b_summary=job["candidate_b_summary"],
                skill_context=job["skill_context"],
                objective="support",
                general_biomedical_llm=False,
            )
        joined = "\n\n".join(message["content"] for message in messages)
        for pattern in FORBIDDEN_PROMPT_PATTERNS:
            if re.search(pattern, joined, re.I):
                forbidden_hits.append({
                    "ontology": job["ontology"],
                    "pair": f"{job['candidate_a_id']}::{job['candidate_b_id']}",
                    "pattern": pattern,
                })
    return {
        "request_count": len(jobs),
        "forbidden_prompt_hits": forbidden_hits,
        "stage2_universe_mismatches": universe_mismatches,
        "stage2_universe_equals_stage1_carried_forward": not universe_mismatches,
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "pair_source": pair_source,
        "pairwise_prompt": pairwise_prompt,
        "passed": not forbidden_hits and not universe_mismatches,
    }


def _run_replay(
    *,
    run_dir: Path,
    output_dir: Path,
    model: str,
    workers: int,
    selected_ontologies: set[str] | None,
    stage2_candidate_order: str,
    stage2_candidate_order_seed: str,
    pair_source: str,
    pairwise_prompt: str,
) -> dict[str, Any]:
    stage1_rows = _load_json(run_dir / "experiment_pairwise_rerank_stage1_results.json")
    source_stage2_rows = replay_stage2_from_run._filter_stage2_rows(
        _load_json(run_dir / "experiment_pairwise_rerank_stage2_results.json"),
        selected_ontologies,
    )
    result_rows = _load_json(run_dir / "experiment_pairwise_rerank_results.json")
    result_by_ontology = {row["ontology"]: row for row in result_rows}
    output_dir.mkdir(parents=True, exist_ok=True)
    inspection = _inspect_messages(
        stage1_rows=stage1_rows,
        stage2_rows=source_stage2_rows,
        stage2_candidate_order=stage2_candidate_order,
        stage2_candidate_order_seed=stage2_candidate_order_seed,
        pair_source=pair_source,
        pairwise_prompt=pairwise_prompt,
    )
    (output_dir / "stage2_pairwise_request_inspection.json").write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not inspection["passed"]:
        raise SystemExit(f"Pairwise request inspection failed; see {output_dir}")

    jobs = _pair_jobs_for_rows(
        stage1_rows=stage1_rows,
        stage2_rows=source_stage2_rows,
        stage2_candidate_order=stage2_candidate_order,
        stage2_candidate_order_seed=stage2_candidate_order_seed,
        pair_source=pair_source,
    )
    client = pr._client()
    pr._reset_usage_records()
    started = time.time()
    pairwise_rows: list[dict[str, Any]] = []

    def submit(job: dict[str, Any]) -> dict[str, Any]:
        if pairwise_prompt == "performance_forward":
            try:
                content = pr._llm_call(
                    client,
                    model=model,
                    messages=[
                        {"role": "system", "content": PERFORMANCE_FORWARD_PAIRWISE_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": pr._build_pairwise_user_message(
                                target_trait=job["ontology"],
                                target_ancestry=job["target_ancestry"],
                                candidate_a_id=job["candidate_a_id"],
                                candidate_b_id=job["candidate_b_id"],
                                candidate_a_summary=job["candidate_a_summary"],
                                candidate_b_summary=job["candidate_b_summary"],
                                skill_context=job["skill_context"],
                            ),
                        },
                    ],
                    response_format=pr._pairwise_response_format(),
                    stage="stage2_pairwise_performance_forward",
                    custom_id=f"{job['ontology']}::{job['candidate_a_id']}::{job['candidate_b_id']}",
                )
                verdict = pr.PairwiseJudgment.model_validate_json(content)
                winner = verdict.winner_model_id.strip()
                if winner not in {job["candidate_a_id"], job["candidate_b_id"]}:
                    return {
                        "ontology": job["ontology"],
                        "candidate_a_id": job["candidate_a_id"],
                        "candidate_b_id": job["candidate_b_id"],
                        "winner_model_id": None,
                        "confidence": verdict.confidence,
                        "rationale": verdict.rationale,
                        "error": f"winner '{winner}' not in pair",
                    }
                return {
                    "ontology": job["ontology"],
                    "candidate_a_id": job["candidate_a_id"],
                    "candidate_b_id": job["candidate_b_id"],
                    "winner_model_id": winner,
                    "confidence": verdict.confidence,
                    "rationale": verdict.rationale,
                    "error": None,
                }
            except Exception as exc:
                return {
                    "ontology": job["ontology"],
                    "candidate_a_id": job["candidate_a_id"],
                    "candidate_b_id": job["candidate_b_id"],
                    "winner_model_id": None,
                    "confidence": None,
                    "rationale": None,
                    "error": f"Stage2PerformancePairwise {type(exc).__name__}: {exc}",
                }
        return pr._run_stage2_for_pair(
            client,
            model,
            ontology=job["ontology"],
            candidate_a_id=job["candidate_a_id"],
            candidate_b_id=job["candidate_b_id"],
            candidate_a_summary=job["candidate_a_summary"],
            candidate_b_summary=job["candidate_b_summary"],
            target_ancestry=job["target_ancestry"],
            skill_context=job["skill_context"],
            objective="support",
            general_biomedical_llm=False,
        )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(submit, job): job for job in jobs}
        for future in as_completed(futures):
            pairwise_rows.append(future.result())

    pairs_by_ontology: dict[str, list[dict[str, Any]]] = defaultdict(list)
    order_by_ontology: dict[str, list[str]] = {}
    source_stage2_by_ontology = {row["ontology"]: row for row in source_stage2_rows}
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    for job in jobs:
        order_by_ontology[job["ontology"]] = job["ranked_candidate_ids"]
    for row in pairwise_rows:
        pairs_by_ontology[row["ontology"]].append(row)

    report_rows = []
    hit1 = hit5 = top1_carried = top5_carried = 0
    for ontology in [row["ontology"] for row in source_stage2_rows]:
        ranked_ids = order_by_ontology.get(
            ontology,
            replay_stage2_from_run._order_stage2_candidate_ids(
                ontology=ontology,
                ranked_candidate_ids=list(source_stage2_by_ontology[ontology].get("ranked_candidate_ids") or []),
                candidate_order=stage2_candidate_order,
                candidate_order_seed=stage2_candidate_order_seed,
            ),
        )
        if pair_source == "stage1_vs_stage2":
            pair_rows = pairs_by_ontology.get(ontology, [])
            if pair_rows:
                winner = pair_rows[0].get("winner_model_id")
                scores = {winner: 1} if winner else {}
            else:
                winner = source_stage2_by_ontology[ontology].get("winner_model_id")
                scores = {}
        else:
            winner, scores = pr._aggregate_borda(ranked_ids, pairs_by_ontology.get(ontology, []))
        ranks = _rank_map(result_by_ontology[ontology])
        winner_rank = ranks.get(winner)
        best_carried = min(
            ((pgs_id, ranks.get(pgs_id)) for pgs_id in ranked_ids),
            key=lambda item: item[1] if item[1] is not None else 10**9,
        )
        row_hit1 = winner_rank == 1
        row_hit5 = winner_rank is not None and winner_rank <= 5
        row_top1_carried = best_carried[1] == 1
        row_top5_carried = best_carried[1] is not None and best_carried[1] <= 5
        hit1 += int(row_hit1)
        hit5 += int(row_hit5)
        top1_carried += int(row_top1_carried)
        top5_carried += int(row_top5_carried)
        report_rows.append({
            "ontology": ontology,
            "carried_size": len(ranked_ids),
            "pair_count": len(pairs_by_ontology.get(ontology, [])),
            "top1_carried": row_top1_carried,
            "top5_carried": row_top5_carried,
            "best_carried_id": best_carried[0],
            "best_carried_rank": best_carried[1],
            "winner_model_id": winner,
            "winner_rank": winner_rank,
            "hit1": row_hit1,
            "hit5": row_hit5,
            "scores": scores,
            "ranked_candidate_ids": ranked_ids,
        })

    summary = {
        "run_type": "stage2_pairwise_replay_from_frozen_double_stage_run",
        "source_run_dir": str(run_dir),
        "model": model,
        "selected_ontologies": sorted(selected_ontologies) if selected_ontologies else None,
        "stage1_frozen": True,
        "stage1_calls": 0,
        "stage2_pairwise_calls": len(pairwise_rows),
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "pair_source": pair_source,
        "pairwise_prompt": pairwise_prompt,
        "elapsed_seconds": round(time.time() - started, 1),
        "aggregate": {
            "hit1": f"{hit1}/{len(report_rows)}",
            "hit5": f"{hit5}/{len(report_rows)}",
            "top1_carried": f"{top1_carried}/{len(report_rows)}",
            "top5_carried": f"{top5_carried}/{len(report_rows)}",
        },
        "cost": pr._summarize_usage_cost(model),
        "inspection": inspection,
        "rows": report_rows,
    }
    (output_dir / "stage2_pairwise_results.json").write_text(
        json.dumps(pairwise_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_pairwise_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_pairwise_usage_records.json").write_text(
        json.dumps(list(pr._USAGE_RECORDS), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--ontology", action="append", default=None)
    parser.add_argument("--ontologies-file", type=Path, default=None)
    parser.add_argument(
        "--stage2-candidate-order",
        choices=replay_stage2_from_run.STAGE2_CANDIDATE_ORDER_CHOICES,
        default="stable_hash_shuffle",
    )
    parser.add_argument(
        "--stage2-candidate-order-seed",
        default=replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
    )
    parser.add_argument(
        "--pair-source",
        choices=("all_pairs", "stage1_vs_stage2"),
        default="all_pairs",
    )
    parser.add_argument(
        "--pairwise-prompt",
        choices=("current", "performance_forward"),
        default="current",
    )
    args = parser.parse_args()

    selected_ontologies = replay_stage2_from_run._load_selected_ontologies(
        ontology_values=args.ontology,
        ontologies_file=args.ontologies_file,
    )
    stage1_rows = _load_json(args.run_dir / "experiment_pairwise_rerank_stage1_results.json")
    source_stage2_rows = replay_stage2_from_run._filter_stage2_rows(
        _load_json(args.run_dir / "experiment_pairwise_rerank_stage2_results.json"),
        selected_ontologies,
    )
    if args.inspect_only:
        inspection = _inspect_messages(
            stage1_rows=stage1_rows,
            stage2_rows=source_stage2_rows,
            stage2_candidate_order=args.stage2_candidate_order,
            stage2_candidate_order_seed=args.stage2_candidate_order_seed,
            pair_source=args.pair_source,
            pairwise_prompt=args.pairwise_prompt,
        )
        inspection["selected_ontologies"] = (
            sorted(selected_ontologies) if selected_ontologies else None
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "stage2_pairwise_request_inspection.json").write_text(
            json.dumps(inspection, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(inspection, indent=2, ensure_ascii=False))
        if not inspection["passed"]:
            raise SystemExit(1)
        return

    summary = _run_replay(
        run_dir=args.run_dir,
        output_dir=args.output_dir,
        model=args.model,
        workers=args.workers,
        selected_ontologies=selected_ontologies,
        stage2_candidate_order=args.stage2_candidate_order,
        stage2_candidate_order_seed=args.stage2_candidate_order_seed,
        pair_source=args.pair_source,
        pairwise_prompt=args.pairwise_prompt,
    )
    print(json.dumps(summary["aggregate"], indent=2, ensure_ascii=False))
    if summary.get("cost"):
        print(json.dumps(summary["cost"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
