"""Replay an analysis-only Stage2 verifier from a frozen double-stage run.

This helper is for low-cost Stage2 iteration. It does not rerun Stage1. It
freezes the carried-forward candidate universe from a completed run, shows the
current Stage2 decision as non-binding context, and asks an independent LLM
verifier to choose a final winner from the same carried set.
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

from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.analysis.target10_hit1 import replay_stage2_from_run
from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
from src.server.core.within_prompts.selectors import _selection_record_digest


class CandidateVerifierAudit(BaseModel):
    pgs_id: str
    strongest_visible_signal: str
    hard_defect_if_rejected: str
    support_or_rejection: str
    final_status: str


class VerifierJudgment(BaseModel):
    candidate_audits: list[CandidateVerifierAudit]
    ranked_model_ids: list[str]
    winner_model_id: str
    strongest_runner_up: str
    confidence: str
    rationale: str


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


VERIFIER_SYSTEM_PROMPT = """# Identity & Persona
You are an independent PRS final-selection verifier for within-phenotype
recommendation.
You audit a prior Stage2 decision, but you are not bound by it.
Your job is to choose the single candidate best supported by visible same-trait
evidence from the fixed carried-forward candidate set.

# Decision Boundary
- winner_model_id must be one of `ranked_candidate_ids`.
- `ranked_candidate_ids` defines the allowed universe only; its order is not
  evidence.
- The prior Stage2 decision is non-binding context, not a default, not a rank,
  and not authority.
- Do not introduce candidates, use benchmark labels, use PGS ID memory, use
  trait-specific priors, or use disease-category shortcuts.

# Evidence Reference Frame
Use only visible candidate fields, neutral digest fields, provided skill_context,
and the prior Stage2 rationale as an audit object.
Raw `candidates` remains the source of truth for selection-relevant details.

# Verification Discipline
- Produce a candidate audit for every ID in `ranked_candidate_ids` before
  choosing. Do not skip candidates because another near-clone or cleaner
  narrative looks plausible.
- For each candidate audit, identify that candidate's strongest visible
  endpoint-compatible genetic-signal row or effect/tail row, not an average
  impression of the record.
- If a candidate is rejected, state the hard defect if one exists. If no hard
  defect exists, say "none" and reject only if the winner has stronger
  whole-record support.
- First identify the strongest challenger to the prior winner from the full
  carried set.
- Re-read that challenger's strongest endpoint-compatible genetic-signal row:
  PRS-only discrimination, incremental/covariate-regressed signal, partial-r,
  effect-size, tail enrichment, case enrichment, or same-context numeric
  evidence.
- If the prior rationale rejected that challenger mainly for soft stability
  reasons, audit whether those reasons are decisive. Soft stability concerns
  include smaller N, single-cohort support, sparse/framework origin, fewer
  external cohorts, OR-only/HR-only/partial-r-only reporting, unfamiliar method
  labels, or less publication narrative.
- Soft stability concerns break close ties; they should not defeat a materially
  stronger endpoint-compatible genetic signal unless there is a concrete hard
  defect.
- Hard defects include endpoint mismatch, non-genetic or family-history/clinical
  risk packaging, non-routine covariate/mediator/treatment leakage, severe
  target-ancestry mismatch without compensating evidence, incompatible outcome
  horizon, or missing/ambiguous row context that prevents comparison.
- Same-context near-clone rows are high-value evidence. If candidates share the
  same endpoint, cohort, ancestry/sample context, covariates, and metric family,
  prefer the candidate with stronger same-context numeric rows unless another
  candidate has a clearly stronger compatible signal family.
- Do not switch away from a prior winner just for novelty. Switch only when a
  challenger has stronger visible whole-record support after this audit.

# Output Requirements
Return one JSON object with exactly these fields:
{
  "candidate_audits": [
    {
      "pgs_id": "PGS000XXX",
      "strongest_visible_signal": "...",
      "hard_defect_if_rejected": "...",
      "support_or_rejection": "...",
      "final_status": "winner | runner_up | rejected"
    }
  ],
  "ranked_model_ids": ["PGS000XXX", "PGS000YYY"],
  "winner_model_id": "PGS000XXX",
  "strongest_runner_up": "PGS000YYY",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}

# Output Discipline
- `ranked_model_ids` must list every candidate in `ranked_candidate_ids` exactly
  once when possible, ordered from best-supported to least-supported by your
  visible-evidence appraisal.
- `candidate_audits` must include every candidate in `ranked_candidate_ids`
  exactly once when possible.
- winner_model_id must equal the first ID in ranked_model_ids.
- `rationale` must cite visible evidence and compare the winner with the
  strongest runner-up.
- Do not expose raw chain-of-thought; provide concise evidence summaries only.
- Do not include extra keys.
"""


INDEPENDENT_AUDIT_SYSTEM_PROMPT = """# Identity & Persona
You are an independent PRS final-selection judge for within-phenotype
recommendation.
Your job is to choose the single candidate best supported by visible same-trait
evidence from the fixed carried-forward candidate set.

# Decision Boundary
- winner_model_id must be one of `ranked_candidate_ids`.
- `ranked_candidate_ids` defines the allowed universe only; its order is not
  evidence.
- Do not introduce candidates, use benchmark labels, use PGS ID memory, use
  trait-specific priors, or use disease-category shortcuts.

# Evidence Reference Frame
Use only visible candidate fields, neutral digest fields, and provided
skill_context.
Raw `candidates` remains the source of truth for selection-relevant details.

# Audit Discipline
- Produce a candidate audit for every ID in `ranked_candidate_ids` before
  choosing. Do not skip candidates because another candidate has a cleaner
  narrative or more familiar metric family.
- For each candidate, identify its strongest visible endpoint-compatible
  genetic-signal row or effect/tail row.
- If a candidate is rejected, state the hard defect if one exists. If no hard
  defect exists, say "none" and reject only if the winner has stronger
  whole-record support.
- A candidate with routine covariates only, such as age, sex, genotyping array,
  site/center, assessment center, and ancestry PCs, remains live evidence. Do
  not dismiss it merely because the row is covariate-adjusted or reported as a
  full/incremental model.
- Family history, treatment, mediator, biomarker, or broad clinical-risk
  packaging can weaken comparability. Routine adjustment alone is not a hard
  defect.
- When PRS-only discrimination is modest, sparse, or near-tied across candidates,
  a materially stronger endpoint-compatible routine-adjusted row, incremental
  genetic contribution, partial-r, effect-size, tail enrichment, case
  enrichment, or same-context sibling advantage can carry the selection.
- Validation breadth and larger sample size are support, not automatic vetoes
  against a candidate whose strongest compatible genetic-signal row is visibly
  stronger.
- Same-context near-clone rows are high-value evidence. If candidates share the
  same endpoint, cohort, ancestry/sample context, covariates, and metric family,
  prefer the candidate with stronger same-context numeric rows unless another
  candidate has a clearly stronger compatible signal family.
- Do not average away a candidate's strongest credible genetic-signal evidence
  across weaker secondary rows.
- Do not switch to a high-signal challenger if its endpoint is mismatched, its
  signal is mainly non-genetic clinical packaging, or its performance context is
  too ambiguous to compare.

# Output Requirements
Return one JSON object with exactly these fields:
{
  "candidate_audits": [
    {
      "pgs_id": "PGS000XXX",
      "strongest_visible_signal": "...",
      "hard_defect_if_rejected": "...",
      "support_or_rejection": "...",
      "final_status": "winner | runner_up | rejected"
    }
  ],
  "ranked_model_ids": ["PGS000XXX", "PGS000YYY"],
  "winner_model_id": "PGS000XXX",
  "strongest_runner_up": "PGS000YYY",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}

# Output Discipline
- `ranked_model_ids` must list every candidate in `ranked_candidate_ids` exactly
  once when possible, ordered from best-supported to least-supported by your
  visible-evidence appraisal.
- `candidate_audits` must include every candidate in `ranked_candidate_ids`
  exactly once when possible.
- winner_model_id must equal the first ID in ranked_model_ids.
- `rationale` must cite visible evidence and compare the winner with the
  strongest runner-up.
- Do not expose raw chain-of-thought; provide concise evidence summaries only.
- Do not include extra keys.
"""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _verifier_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "stage2_verifier_judgment",
            "strict": True,
            "schema": to_strict_json_schema(VerifierJudgment),
        },
    }


def _candidate_map(stage1_row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    context = json.loads(stage1_row["context_json"])
    models = context.get("direct_models", {}).get("models") or []
    return context, {str(model.get("id")): model for model in models if model.get("id")}


def _rank_map(result_row: dict[str, Any]) -> dict[str, int]:
    return {pgs_id: idx + 1 for idx, pgs_id in enumerate(result_row.get("benchmark_ranked_ids") or [])}


def _verifier_user_message(
    *,
    target_trait: str,
    target_ancestry: str | None,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    skill_context: dict[str, Any],
    prior_stage2_decision: dict[str, Any] | None,
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
    if prior_stage2_decision is not None:
        payload["prior_stage2_decision"] = {
            "winner_model_id": prior_stage2_decision.get("winner_model_id"),
            "confidence": prior_stage2_decision.get("confidence"),
            "rationale": prior_stage2_decision.get("rationale"),
        }
        task_prefix = (
            "Audit the prior Stage2 decision and choose the final best-supported "
            "direct-match candidate from the same carried-forward universe. The prior "
            "decision is non-binding context; ranked_candidate_ids order is not "
            "evidence."
        )
    else:
        task_prefix = (
            "Choose the final best-supported direct-match candidate from this "
            "carried-forward universe. ranked_candidate_ids order is not evidence."
        )
    return (
        f"{task_prefix} Use raw candidates as the source of truth and the neutral "
        "selection_record_digest only as a compact map of visible schema fields.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _inspect_messages(
    *,
    stage1_rows: list[dict[str, Any]],
    stage2_rows: list[dict[str, Any]],
    independent: bool = False,
    stage2_candidate_order: str = "source",
    stage2_candidate_order_seed: str = replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
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
        user_message = _verifier_user_message(
            target_trait=ontology,
            target_ancestry=context.get("target_ancestry"),
            ranked_candidate_ids=ranked_candidate_ids,
            candidate_summaries=candidate_summaries,
            skill_context=context.get("skill_context") or {},
            prior_stage2_decision=None if independent else stage2_row,
        )
        system_prompt = INDEPENDENT_AUDIT_SYSTEM_PROMPT if independent else VERIFIER_SYSTEM_PROMPT
        joined = f"{system_prompt}\n\n{user_message}"
        for pattern in FORBIDDEN_PROMPT_PATTERNS:
            if re.search(pattern, joined, re.I):
                forbidden_hits.append({"ontology": ontology, "pattern": pattern})
    return {
        "request_count": len(stage2_rows),
        "forbidden_prompt_hits": forbidden_hits,
        "independent": independent,
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
    independent: bool,
    stage2_candidate_order: str,
    stage2_candidate_order_seed: str,
) -> dict[str, Any]:
    stage1_rows = _load_json(run_dir / "experiment_pairwise_rerank_stage1_results.json")
    source_stage2_rows = _load_json(run_dir / "experiment_pairwise_rerank_stage2_results.json")
    source_stage2_rows = replay_stage2_from_run._filter_stage2_rows(
        source_stage2_rows,
        selected_ontologies,
    )
    result_rows = _load_json(run_dir / "experiment_pairwise_rerank_results.json")
    stage1_by_ontology = {row["ontology"]: row for row in stage1_rows}
    result_by_ontology = {row["ontology"]: row for row in result_rows}

    output_dir.mkdir(parents=True, exist_ok=True)
    inspection = _inspect_messages(
        stage1_rows=stage1_rows,
        stage2_rows=source_stage2_rows,
        independent=independent,
        stage2_candidate_order=stage2_candidate_order,
        stage2_candidate_order_seed=stage2_candidate_order_seed,
    )
    (output_dir / "stage2_verifier_request_inspection.json").write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not inspection["passed"]:
        raise SystemExit(f"Verifier request inspection failed; see {output_dir}")

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
        system_prompt = INDEPENDENT_AUDIT_SYSTEM_PROMPT if independent else VERIFIER_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": _verifier_user_message(
                    target_trait=ontology,
                    target_ancestry=context.get("target_ancestry"),
                    ranked_candidate_ids=ranked_candidate_ids,
                    candidate_summaries=candidate_summaries,
                    skill_context=context.get("skill_context") or {},
                    prior_stage2_decision=None if independent else stage2_row,
                ),
            },
        ]
        try:
            content = pr._llm_call(
                client,
                model=model,
                messages=messages,
                response_format=_verifier_response_format(),
                stage="stage2_verifier",
                custom_id=ontology,
            )
            verdict = VerifierJudgment.model_validate_json(content)
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
                "prior_winner_model_id": stage2_row.get("winner_model_id"),
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
                "prior_winner_model_id": stage2_row.get("winner_model_id"),
                "error": f"Verifier {type(exc).__name__}: {exc}",
            }

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(submit, row): row["ontology"] for row in source_stage2_rows}
        for future in as_completed(futures):
            replay_rows.append(future.result())

    ontology_order = [row["ontology"] for row in source_stage2_rows]
    replay_rows.sort(key=lambda row: ontology_order.index(row["ontology"]))

    report_rows = []
    hit1 = hit5 = prior_hit1 = prior_hit5 = changed = 0
    for row in replay_rows:
        ontology = row["ontology"]
        ranks = _rank_map(result_by_ontology[ontology])
        winner = row.get("winner_model_id")
        prior_winner = row.get("prior_winner_model_id")
        winner_rank = ranks.get(winner)
        prior_rank = ranks.get(prior_winner)
        row_hit1 = winner_rank == 1
        row_hit5 = winner_rank is not None and winner_rank <= 5
        row_prior_hit1 = prior_rank == 1
        row_prior_hit5 = prior_rank is not None and prior_rank <= 5
        hit1 += int(row_hit1)
        hit5 += int(row_hit5)
        prior_hit1 += int(row_prior_hit1)
        prior_hit5 += int(row_prior_hit5)
        changed += int(winner != prior_winner)
        report_rows.append({
            "ontology": ontology,
            "prior_winner_model_id": prior_winner,
            "prior_winner_rank": prior_rank,
            "winner_model_id": winner,
            "winner_rank": winner_rank,
            "changed_from_prior": winner != prior_winner,
            "prior_hit1": row_prior_hit1,
            "prior_hit5": row_prior_hit5,
            "hit1": row_hit1,
            "hit5": row_hit5,
            "error": row.get("error"),
            "rationale": row.get("rationale"),
            "ranked_candidate_ids": row.get("ranked_candidate_ids"),
        })

    summary = {
        "run_type": "stage2_verifier_replay_from_frozen_double_stage_run",
        "source_run_dir": str(run_dir),
        "model": model,
        "selected_ontologies": sorted(selected_ontologies) if selected_ontologies else None,
        "stage1_frozen": True,
        "stage1_calls": 0,
        "stage2_verifier_calls": len(replay_rows),
        "independent": independent,
        "stage2_candidate_order": stage2_candidate_order,
        "stage2_candidate_order_seed": stage2_candidate_order_seed,
        "elapsed_seconds": round(time.time() - started, 1),
        "aggregate": {
            "prior_hit1": f"{prior_hit1}/{len(replay_rows)}",
            "prior_hit5": f"{prior_hit5}/{len(replay_rows)}",
            "hit1": f"{hit1}/{len(replay_rows)}",
            "hit5": f"{hit5}/{len(replay_rows)}",
            "changed_from_prior": f"{changed}/{len(replay_rows)}",
        },
        "cost": pr._summarize_usage_cost(model),
        "inspection": inspection,
        "rows": report_rows,
    }
    (output_dir / "stage2_verifier_results.json").write_text(
        json.dumps(replay_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_verifier_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "stage2_verifier_usage_records.json").write_text(
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
    parser.add_argument(
        "--independent",
        action="store_true",
        help="Do not expose the prior Stage2 decision; run as an independent audit judge.",
    )
    parser.add_argument(
        "--stage2-candidate-order",
        choices=replay_stage2_from_run.STAGE2_CANDIDATE_ORDER_CHOICES,
        default="source",
        help="Analysis-only LLM-visible order for frozen carried Stage2 candidates.",
    )
    parser.add_argument(
        "--stage2-candidate-order-seed",
        default=replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
        help="Seed string for analysis-only stable_hash_shuffle Stage2 candidate ordering.",
    )
    parser.add_argument("--ontology", action="append", default=None)
    parser.add_argument("--ontologies-file", type=Path, default=None)
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
            independent=args.independent,
            stage2_candidate_order=args.stage2_candidate_order,
            stage2_candidate_order_seed=args.stage2_candidate_order_seed,
        )
        inspection["selected_ontologies"] = (
            sorted(selected_ontologies) if selected_ontologies else None
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "stage2_verifier_request_inspection.json").write_text(
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
        independent=args.independent,
        stage2_candidate_order=args.stage2_candidate_order,
        stage2_candidate_order_seed=args.stage2_candidate_order_seed,
    )
    print(json.dumps(summary["aggregate"], indent=2, ensure_ascii=False))
    if summary.get("cost"):
        print(json.dumps(summary["cost"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
