"""Replay custom Stage2 prompt variants from a frozen double-stage run.

This analysis-only helper freezes the Stage1 carried-forward candidate universe
and tests alternative LLM-led Stage2 wording without rerunning Stage1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.analysis.target10_hit1 import replay_stage2_from_run
from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
from src.server.core.within_prompts.selectors import _selection_record_digest


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


PERFORMANCE_FORWARD_SYSTEM_PROMPT = """# Identity & Persona
You are a PRS model-selection judge for within-phenotype recommendation.
You choose the carried-forward PGS Catalog candidate with the strongest visible
same-trait predictive-performance support for the target trait and target
ancestry.

# Decision Boundary
- winner_model_id must be one of `ranked_candidate_ids`.
- `ranked_candidate_ids` defines the allowed candidate universe only; its order
  is not evidence.
- Do not introduce another candidate, propose a tie, search externally, use PGS
  ID memory, use trait-specific priors, or use disease-category shortcuts.
- Use only visible candidate fields, neutral digest fields, and skill_context.

# Evidence Frame
Raw `candidates` is the source of truth. `selection_record_digest` is only a
compact neutral map of endpoint labels, method, variant count, performance
records, covariates, evaluation samples, and metric buckets.

# Selection Discipline
- Audit every carried candidate's strongest endpoint-compatible signal before
  finalizing.
- Treat routine-adjusted performance rows as live predictive evidence. Routine
  covariates include age, sex, genotyping array/batch, site/center, assessment
  center, and ancestry PCs.
- Do not default to covariate-free PRS-only rows when another direct-match
  candidate has visibly stronger endpoint-compatible support under routine
  adjustment, incremental genetic contribution, effect size, tail enrichment,
  case enrichment, or same-context sibling dominance.
- Family history, treatment, mediator, biomarker, horizon-conditioned, or broad
  clinical-risk packaging can weaken comparability. Routine adjustment alone is
  not a hard defect.
- Compare each candidate's best compatible signal row before using validation
  breadth, publication polish, method labels, variant count, or record count as
  tie-breaks.
- Same-context near-clone rows are high-value evidence. If candidates share
  endpoint, cohort/sample context, ancestry, covariates, and metric family,
  prefer the candidate with stronger same-context numeric evidence.
- When metric families differ, decide which signal is most relevant to selecting
  a disease-risk PRS: discrimination, incremental/covariate-regressed signal,
  effect size, risk-tail enrichment, case enrichment, calibration-like evidence,
  and target-ancestry support can each carry the choice.
- Do not average away a candidate's strongest credible signal across weaker
  secondary rows.
- Reject a stronger-looking row only for a concrete defect: endpoint mismatch,
  non-genetic clinical/family-history packaging, non-routine leakage, severe
  ancestry/context mismatch without compensating evidence, incompatible outcome
  horizon, or ambiguous row context that prevents comparison.

# Output Requirements
Return one JSON object with exactly these fields:
{
  "ranked_model_ids": ["PGS000XXX", "PGS000YYY"],
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}

# Output Discipline
- `ranked_model_ids` must list every candidate in `ranked_candidate_ids` exactly
  once when possible, ordered from best-supported to least-supported by your
  visible-evidence appraisal.
- winner_model_id must equal the first ID in ranked_model_ids.
- `rationale` must cite visible evidence and compare the winner with the
  strongest runner-up.
- Do not expose raw chain-of-thought; provide concise evidence summaries only.
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


def _user_message(
    *,
    target_trait: str,
    target_ancestry: str | None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: dict[str, Any],
) -> str:
    selection_digest = _selection_record_digest(
        target_trait=target_trait,
        target_ancestry=target_ancestry,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
    )
    payload = {
        "target_trait": target_trait,
        "target_ancestry": target_ancestry,
        "ranked_candidate_ids": ranked_candidate_ids,
        "candidates": [
            candidate_summaries.get(pgs_id, {"pgs_id": pgs_id, "missing": True})
            for pgs_id in ranked_candidate_ids
        ],
        "selection_record_digest": selection_digest,
        "skill_context": skill_context or {},
    }
    return (
        "Choose the final best-supported direct-match PRS candidate from the "
        "carried-forward universe. ranked_candidate_ids order is not evidence. "
        "Use raw candidates as the source of truth and the neutral digest only as "
        "a compact evidence map.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _inspect_messages(
    *,
    stage1_rows: list[dict[str, Any]],
    stage2_rows: list[dict[str, Any]],
    stage2_candidate_order: str,
    stage2_candidate_order_seed: str,
) -> dict[str, Any]:
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    forbidden_hits: list[dict[str, str]] = []
    for stage2_row in stage2_rows:
        ontology = stage2_row["ontology"]
        context, candidate_summaries = _candidate_map(stage1_by_ontology[ontology])
        ranked_candidate_ids = replay_stage2_from_run._order_stage2_candidate_ids(
            ontology=ontology,
            ranked_candidate_ids=list(stage2_row.get("ranked_candidate_ids") or []),
            candidate_order=stage2_candidate_order,
            candidate_order_seed=stage2_candidate_order_seed,
        )
        joined = "\n\n".join([
            PERFORMANCE_FORWARD_SYSTEM_PROMPT,
            _user_message(
                target_trait=ontology,
                target_ancestry=context.get("target_ancestry"),
                ranked_candidate_ids=ranked_candidate_ids,
                candidate_summaries=candidate_summaries,
                skill_context=context.get("skill_context") or {},
            ),
        ])
        for pattern in FORBIDDEN_PROMPT_PATTERNS:
            if re.search(pattern, joined, re.I):
                forbidden_hits.append({"ontology": ontology, "pattern": pattern})
    return {
        "request_count": len(stage2_rows),
        "forbidden_prompt_hits": forbidden_hits,
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "passed": not forbidden_hits,
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
) -> dict[str, Any]:
    stage1_rows = _load_json(run_dir / "experiment_pairwise_rerank_stage1_results.json")
    source_stage2_rows = replay_stage2_from_run._filter_stage2_rows(
        _load_json(run_dir / "experiment_pairwise_rerank_stage2_results.json"),
        selected_ontologies,
    )
    result_rows = _load_json(run_dir / "experiment_pairwise_rerank_results.json")
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    result_by_ontology = {row["ontology"]: row for row in result_rows}

    output_dir.mkdir(parents=True, exist_ok=True)
    inspection = _inspect_messages(
        stage1_rows=stage1_rows,
        stage2_rows=source_stage2_rows,
        stage2_candidate_order=stage2_candidate_order,
        stage2_candidate_order_seed=stage2_candidate_order_seed,
    )
    (output_dir / "stage2_prompt_variant_request_inspection.json").write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not inspection["passed"]:
        raise SystemExit(f"Prompt-variant request inspection failed; see {output_dir}")

    client = pr._client()
    pr._reset_usage_records()
    started = time.time()
    replay_rows: list[dict[str, Any]] = []

    def submit(stage2_row: dict[str, Any]) -> dict[str, Any]:
        ontology = stage2_row["ontology"]
        context, candidate_summaries = _candidate_map(stage1_by_ontology[ontology])
        ranked_candidate_ids = replay_stage2_from_run._order_stage2_candidate_ids(
            ontology=ontology,
            ranked_candidate_ids=list(stage2_row.get("ranked_candidate_ids") or []),
            candidate_order=stage2_candidate_order,
            candidate_order_seed=stage2_candidate_order_seed,
        )
        try:
            content = pr._llm_call(
                client,
                model=model,
                messages=[
                    {"role": "system", "content": PERFORMANCE_FORWARD_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": _user_message(
                            target_trait=ontology,
                            target_ancestry=context.get("target_ancestry"),
                            ranked_candidate_ids=ranked_candidate_ids,
                            candidate_summaries=candidate_summaries,
                            skill_context=context.get("skill_context") or {},
                        ),
                    },
                ],
                response_format=pr._topk_response_format(),
                stage="stage2_prompt_variant",
                custom_id=ontology,
            )
            verdict = pr.TopKJudgment.model_validate_json(content)
            allowed = set(ranked_candidate_ids)
            valid_ranked: list[str] = []
            for pgs_id in verdict.ranked_model_ids:
                pgs_id = str(pgs_id).strip()
                if pgs_id in allowed and pgs_id not in valid_ranked:
                    valid_ranked.append(pgs_id)
            for pgs_id in ranked_candidate_ids:
                if pgs_id not in valid_ranked:
                    valid_ranked.append(pgs_id)
            winner = verdict.winner_model_id.strip()
            error = None
            if winner not in allowed:
                error = f"winner '{winner}' not in carried set"
                winner = None
            elif valid_ranked and winner != valid_ranked[0]:
                error = "winner_model_id does not match first ranked_model_ids entry"
                winner = None
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "ranked_model_ids": valid_ranked,
                "winner_model_id": winner,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": error,
            }
        except Exception as exc:
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "ranked_model_ids": [],
                "winner_model_id": None,
                "confidence": None,
                "rationale": None,
                "error": f"PromptVariant {type(exc).__name__}: {exc}",
            }

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(submit, row): row["ontology"] for row in source_stage2_rows}
        for future in as_completed(futures):
            replay_rows.append(future.result())

    ontology_order = [row["ontology"] for row in source_stage2_rows]
    replay_rows.sort(key=lambda row: ontology_order.index(row["ontology"]))

    report_rows = []
    hit1 = hit5 = top1_carried = top5_carried = 0
    for row in replay_rows:
        ontology = row["ontology"]
        ranked_ids = list(row.get("ranked_candidate_ids") or [])
        ranks = _rank_map(result_by_ontology[ontology])
        winner = row.get("winner_model_id")
        winner_rank = ranks.get(winner)
        best_carried = min(
            ((pgs_id, ranks.get(pgs_id)) for pgs_id in ranked_ids),
            key=lambda item: item[1] if item[1] is not None else 10**9,
        )
        row_top1_carried = best_carried[1] == 1
        row_top5_carried = best_carried[1] is not None and best_carried[1] <= 5
        row_hit1 = winner_rank == 1
        row_hit5 = winner_rank is not None and winner_rank <= 5
        top1_carried += int(row_top1_carried)
        top5_carried += int(row_top5_carried)
        hit1 += int(row_hit1)
        hit5 += int(row_hit5)
        report_rows.append({
            "ontology": ontology,
            "carried_size": len(ranked_ids),
            "top1_carried": row_top1_carried,
            "top5_carried": row_top5_carried,
            "best_carried_id": best_carried[0],
            "best_carried_rank": best_carried[1],
            "winner_model_id": winner,
            "winner_rank": winner_rank,
            "hit1": row_hit1,
            "hit5": row_hit5,
            "error": row.get("error"),
            "rationale": row.get("rationale"),
            "ranked_candidate_ids": ranked_ids,
        })

    summary = {
        "run_type": "stage2_prompt_variant_replay_from_frozen_double_stage_run",
        "prompt_variant": "performance_forward",
        "source_run_dir": str(run_dir),
        "model": model,
        "selected_ontologies": sorted(selected_ontologies) if selected_ontologies else None,
        "stage1_frozen": True,
        "stage1_calls": 0,
        "stage2_calls": len(replay_rows),
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "elapsed_seconds": round(time.time() - started, 1),
        "aggregate": {
            "hit1": f"{hit1}/{len(replay_rows)}",
            "hit5": f"{hit5}/{len(replay_rows)}",
            "top1_carried": f"{top1_carried}/{len(replay_rows)}",
            "top5_carried": f"{top5_carried}/{len(replay_rows)}",
        },
        "cost": pr._summarize_usage_cost(model),
        "inspection": inspection,
        "rows": report_rows,
    }
    (output_dir / "stage2_prompt_variant_results.json").write_text(
        json.dumps(replay_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_prompt_variant_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_prompt_variant_usage_records.json").write_text(
        json.dumps(list(pr._USAGE_RECORDS), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--workers", type=int, default=4)
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
    args = parser.parse_args()

    selected_ontologies = replay_stage2_from_run._load_selected_ontologies(
        ontology_values=args.ontology,
        ontologies_file=args.ontologies_file,
    )
    source_stage2_rows = replay_stage2_from_run._filter_stage2_rows(
        _load_json(args.run_dir / "experiment_pairwise_rerank_stage2_results.json"),
        selected_ontologies,
    )
    if args.inspect_only:
        inspection = _inspect_messages(
            stage1_rows=_load_json(args.run_dir / "experiment_pairwise_rerank_stage1_results.json"),
            stage2_rows=source_stage2_rows,
            stage2_candidate_order=args.stage2_candidate_order,
            stage2_candidate_order_seed=args.stage2_candidate_order_seed,
        )
        inspection["selected_ontologies"] = (
            sorted(selected_ontologies) if selected_ontologies else None
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "stage2_prompt_variant_request_inspection.json").write_text(
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
    )
    print(json.dumps(summary["aggregate"], indent=2, ensure_ascii=False))
    if summary.get("cost"):
        print(json.dumps(summary["cost"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
