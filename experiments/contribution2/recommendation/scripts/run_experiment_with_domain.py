"""
Contribution2 Experiment 2: With Domain Knowledge batch evaluation.

This runner reuses the no-domain batch workflow but enables local
`prs_model_domain_knowledge` retrieval for Step 1 and emits an additional
comparison report against the archived without-domain GPT-5.2 results.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

_ORIGINAL_PREPARE_MANIFEST = without_domain._prepare_manifest

RECOMMENDATION_RUNS = Path(__file__).parent.parent / "runs"

RESULTS_JSON = Path()
SUMMARY_JSON = Path()
REPORT_MD = Path()

BATCH_REQUESTS_JSONL = Path()
BATCH_MANIFEST_JSON = Path()
BATCH_JOB_JSON = Path()
BATCH_OUTPUT_JSONL = Path()
BATCH_ERROR_JSONL = Path()

COMPARISON_REPORT_MD = Path()
DEFAULT_WITHOUT_DOMAIN_SUMMARY_JSON = (
    RECOMMENDATION_RUNS
    / "without-domain-gpt-5.2-t10"
    / "experiment_without_domain_summary.json"
)
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_WITHOUT_DOMAIN_BATCH_CALIBRATION_DIR = RECOMMENDATION_RUNS / "without-domain-gpt-5.2-t10"


def _sync_paths_from_without_domain() -> None:
    global RESULTS_JSON, SUMMARY_JSON, REPORT_MD
    global BATCH_REQUESTS_JSONL, BATCH_MANIFEST_JSON, BATCH_JOB_JSON
    global BATCH_OUTPUT_JSONL, BATCH_ERROR_JSONL, COMPARISON_REPORT_MD

    RESULTS_JSON = without_domain.RESULTS_JSON
    SUMMARY_JSON = without_domain.SUMMARY_JSON
    REPORT_MD = without_domain.REPORT_MD
    BATCH_REQUESTS_JSONL = without_domain.BATCH_REQUESTS_JSONL
    BATCH_MANIFEST_JSON = without_domain.BATCH_MANIFEST_JSON
    BATCH_JOB_JSON = without_domain.BATCH_JOB_JSON
    BATCH_OUTPUT_JSONL = without_domain.BATCH_OUTPUT_JSONL
    BATCH_ERROR_JSONL = without_domain.BATCH_ERROR_JSONL
    if without_domain.ACTIVE_RUN_DIR is None:
        raise RuntimeError("Without-domain run directory is not configured.")
    COMPARISON_REPORT_MD = without_domain.ACTIVE_RUN_DIR / "experiment_with_vs_without_domain_report.md"


def _set_domain_artifact_paths() -> None:
    if without_domain.ACTIVE_RUN_DIR is None:
        raise RuntimeError("Without-domain run directory is not configured.")

    run_dir = without_domain.ACTIVE_RUN_DIR
    without_domain.RESULTS_JSON = run_dir / "experiment_with_domain_results.json"
    without_domain.SUMMARY_JSON = run_dir / "experiment_with_domain_summary.json"
    without_domain.REPORT_MD = run_dir / "experiment_with_domain_report.md"
    without_domain.BATCH_REQUESTS_JSONL = run_dir / "experiment_with_domain_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = run_dir / "experiment_with_domain_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = run_dir / "experiment_with_domain_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = run_dir / "experiment_with_domain_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = run_dir / "experiment_with_domain_batch_errors.jsonl"
    without_domain.ARCHIVE_ARTIFACTS = [
        without_domain.TOP_K_JSON,
        without_domain.EVALUATED_JSON,
        without_domain.BATCH_JOB_JSON,
        without_domain.BATCH_MANIFEST_JSON,
        without_domain.BATCH_OUTPUT_JSONL,
        without_domain.BATCH_ERROR_JSONL,
        without_domain.BATCH_REQUESTS_JSONL,
        without_domain.REPORT_MD,
        without_domain.RESULTS_JSON,
        without_domain.SUMMARY_JSON,
        run_dir / "experiment_with_vs_without_domain_report.md",
    ]
    _sync_paths_from_without_domain()


def _domain_archive_dir_name(model: str, trials: int, run_tag: Optional[str] = None) -> str:
    safe_model = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"with-domain-{safe_model}-t{trials}"
    safe_tag = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _configure_without_domain_module(model: str, trials: int, run_tag: Optional[str] = None) -> None:
    os.environ["PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"] = "0"
    os.environ["PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"] = "0"
    os.environ["PENNPRS_CONTRIB2_STRICT_LLM_ONLY"] = "1"

    without_domain._model_name = lambda: model  # type: ignore[assignment]
    without_domain._archive_dir_name = _domain_archive_dir_name  # type: ignore[assignment]
    without_domain._prepare_manifest = _prepare_manifest  # type: ignore[assignment]
    without_domain._step1_context = _step1_context  # type: ignore[assignment]
    without_domain._step1_messages = _step1_messages  # type: ignore[assignment]
    without_domain._set_run_paths(trials=trials, model=model, run_tag=run_tag)
    _set_domain_artifact_paths()


def _domain_query(ontology: str) -> str:
    return (
        f"target_trait: {ontology}; PRS clinical thresholds AUC R2 must-pass gates "
        "phenotype alignment endpoint specificity external transfer reliability "
        "ancestry compatibility ranking features penalties method priors "
        "validation sample size tie-break time-to-event horizon-specific "
        "incident case-control dominant subtype snpnet biobank transportability"
    )


def _step1_context(
    ontology: str,
    candidate_models: list[Any],
    total_found: int,
    landscape: dict[str, Any],
) -> dict[str, Any]:
    query = _domain_query(ontology)
    domain = prs_model_domain_knowledge(query, max_snippets=5).model_dump()
    return {
        "target_trait": ontology,
        "direct_models": {
            "query_trait": ontology,
            "total_found": total_found,
            "after_filter": len(candidate_models),
            "models": [without_domain._summarize_model_for_llm(model) for model in candidate_models],
        },
        "performance_landscape": landscape,
        "domain_knowledge": domain,
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


def _step1_messages(context_json: str) -> list[dict[str, str]]:
    return without_domain._step1_messages(context_json)


def _prepare_manifest(
    limit: Optional[int],
    trials: int,
    refresh_cache: bool = False,
    ontology_filter: Optional[set[str]] = None,
) -> dict[str, Any]:
    manifest = _ORIGINAL_PREPARE_MANIFEST(
        limit=limit,
        trials=trials,
        refresh_cache=refresh_cache,
        ontology_filter=ontology_filter,
    )
    manifest["experiment"] = "with_domain_batch_formal"
    manifest["domain_knowledge"] = True
    manifest["model"] = without_domain._model_name()
    return manifest


def _build_summary_and_results(
    manifest: dict[str, Any],
    parsed_outputs: dict[str, dict[str, Any]],
    error_map: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trial_results, summary = without_domain._build_summary_and_results(manifest, parsed_outputs, error_map)
    summary["experiment"] = "with_domain_batch_formal"
    summary["domain_knowledge"] = True
    summary["model"] = manifest["model"]
    return trial_results, summary


def _format_models(items: list[dict[str, Any]]) -> str:
    return "<br>".join(
        f"{item['pgs_id']} (AUC rank {item['rank_label']}): x{item['count']}"
        for item in (items or [])
    ) or "-"


def _write_report(summary: dict[str, Any], without_domain_summary_path: Path) -> None:
    total_ontologies = summary["total_ontologies"]
    total_trials = summary["diagnostics"]["total_trials"]
    recommended_hits = summary["majority_vote_hits"]
    recommended_accuracy = summary["majority_vote_accuracy"]
    without_domain_summary = json.loads(without_domain_summary_path.read_text(encoding="utf-8"))
    without_domain_hits = without_domain_summary["majority_vote_hits"]
    without_domain_accuracy = without_domain_summary["majority_vote_accuracy"]
    cost = summary.get("cost") or {}
    token_usage = cost.get("token_usage") or {}
    cost_breakdown = cost.get("estimated_cost_breakdown_usd") or {}
    per_disease_rows = without_domain._sort_disease_rows(summary["per_disease"])
    without_domain_rows = {row["ontology"]: row for row in without_domain_summary["per_disease"]}

    lines = [
        "# Contribution2 Experiment 2: With Domain Knowledge",
        "",
        "## Summary",
        "",
        f"- **Diseases**: {total_ontologies}",
        f"- **Trials per disease**: {summary['trials_per_ontology']}",
        f"- **Total trials**: {total_trials}",
        f"- **Model**: {summary['model']}",
        (
            f"- **Estimated API cost**: {without_domain._format_currency(cost.get('estimated_total_cost_usd', 0.0))} "
            f"(uncached input {token_usage.get('uncached_input_tokens', 0):,} tokens = "
            f"{without_domain._format_currency(cost_breakdown.get('uncached_input', 0.0))}; "
            f"cached input {token_usage.get('cached_input_tokens', 0):,} tokens = "
            f"{without_domain._format_currency(cost_breakdown.get('cached_input', 0.0))}; "
            f"output {token_usage.get('output_tokens', 0):,} tokens = "
            f"{without_domain._format_currency(cost_breakdown.get('output', 0.0))})"
        ),
        f"- **Overall Recommended Model Accuracy**: {recommended_hits}/{total_ontologies} = {without_domain._format_percent(recommended_accuracy)}",
        (
            f"- **Without Domain Knowledge**: "
            f"{without_domain_hits}/{total_ontologies} = {without_domain._format_percent(without_domain_accuracy)}"
        ),
        "",
        "## Experiment Setup",
        "",
        "- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_domain_knowledge + prs_model_performance_landscape",
        "- **Domain Knowledge**: Enabled (local curated knowledge base)",
        "- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us",
        "- **Success rule**: a run is successful iff the recommended `PGS ID` belongs to that disease's `Target_TopK` set",
        "- **Without Domain Knowledge reference**: compare against `without-domain-gpt-5.2-t10` under the same 30-disease / 10-trial protocol",
        "",
        "## Results by Disease",
        "",
        "All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.",
        "They are **not** PGS Catalog reported-AUC ranks.",
        "",
        "| Ontology | N Models | Target_TopK | Trial Hits | With Domain Knowledge Hits Target | With Domain Knowledge | Without Domain Knowledge Hits Target | Without Domain Knowledge |",
        "|----------|----------|-------------|------------|-----------------------------------|-----------------------|--------------------------------------|--------------------------|",
    ]

    for row in per_disease_rows:
        recommended_hit = "Yes" if row["modal_recommendation_in_target_topk"] else "No"
        without_domain_row = without_domain_rows[row["ontology"]]
        without_domain_hit = "Yes" if without_domain_row["modal_recommendation_in_target_topk"] else "No"
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | {row['target_topk']} | "
            f"{row['trial_hits']}/{summary['trials_per_ontology']} | "
            f"{recommended_hit} | {_format_models(row.get('recommended_model_counts') or [])} | "
            f"{without_domain_hit} | {_format_models(without_domain_row.get('recommended_model_counts') or [])} |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def _write_comparison_report(domain_summary: dict[str, Any], without_domain_summary_path: Path) -> Optional[Path]:
    if not without_domain_summary_path.exists():
        return None

    without_domain_summary = json.loads(without_domain_summary_path.read_text(encoding="utf-8"))
    domain_rows = {row["ontology"]: row for row in domain_summary["per_disease"]}
    without_domain_rows = {row["ontology"]: row for row in without_domain_summary["per_disease"]}
    per_disease_rows = without_domain._sort_disease_rows(domain_summary["per_disease"])

    lines = [
        "# Contribution2 Experiment 2: With Domain Knowledge vs Without Domain Knowledge vs Baseline",
        "",
        "## Summary",
        "",
        f"- **Model**: {domain_summary['model']}",
        (
            f"- **With Domain Knowledge**: "
            f"{domain_summary['majority_vote_hits']}/{domain_summary['total_ontologies']} = "
            f"{without_domain._format_percent(domain_summary['majority_vote_accuracy'])}"
        ),
        (
            f"- **Without Domain Knowledge**: "
            f"{without_domain_summary['majority_vote_hits']}/{without_domain_summary['total_ontologies']} = "
            f"{without_domain._format_percent(without_domain_summary['majority_vote_accuracy'])}"
        ),
        (
            f"- **Baseline**: "
            f"{domain_summary['baseline']['hits']}/{domain_summary['total_ontologies']} = "
            f"{without_domain._format_percent(domain_summary['baseline']['accuracy'])}"
        ),
        "",
        "## Results by Disease",
        "",
        "| Ontology | N Models | Target_TopK | Baseline Hits Target | Baseline Models | Without Domain Knowledge Hits Target | Without Domain Knowledge | With Domain Knowledge Hits Target | With Domain Knowledge |",
        "|----------|----------|-------------|----------------------|-----------------|--------------------------------------|--------------------------|-----------------------------------|-----------------------|",
    ]

    for row in per_disease_rows:
        domain_row = domain_rows[row["ontology"]]
        without_domain_row = without_domain_rows[row["ontology"]]
        baseline = domain_row.get("baseline") or {}
        baseline_id = baseline.get("pgs_id")
        baseline_rank_label = baseline.get("rank_label") or "-"
        baseline_text = f"{baseline_id} (AUC rank {baseline_rank_label})" if baseline_id else "-"
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | {row['target_topk']} | "
            f"{'Yes' if domain_row['baseline_in_target_topk'] else 'No'} | "
            f"{baseline_text} | "
            f"{'Yes' if without_domain_row['modal_recommendation_in_target_topk'] else 'No'} | "
            f"{_format_models(without_domain_row.get('recommended_model_counts') or [])} | "
            f"{'Yes' if domain_row['modal_recommendation_in_target_topk'] else 'No'} | "
            f"{_format_models(domain_row.get('recommended_model_counts') or [])} |"
        )

    COMPARISON_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return COMPARISON_REPORT_MD


def _collect(batch_id: Optional[str], without_domain_summary_path: Path) -> dict[str, Any]:
    if not BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(
            f"Batch manifest not found: {BATCH_MANIFEST_JSON}. Run with --mode prepare or --mode prepare-submit first."
        )
    manifest = without_domain._load_json(BATCH_MANIFEST_JSON)
    job = without_domain._load_job(batch_id=batch_id)
    client = without_domain._client()
    batch = client.batches.retrieve(job["batch_id"])

    if batch.status != "completed":
        raise RuntimeError(
            f"Batch {batch.id} is not completed yet (status={batch.status}). Run --mode status and retry later."
        )
    if not batch.output_file_id:
        raise RuntimeError(f"Batch {batch.id} completed without output_file_id.")

    raw_output_jsonl = client.files.retrieve_content(batch.output_file_id)
    BATCH_OUTPUT_JSONL.write_text(raw_output_jsonl, encoding="utf-8")

    raw_error_jsonl = ""
    if batch.error_file_id:
        raw_error_jsonl = client.files.retrieve_content(batch.error_file_id)
        BATCH_ERROR_JSONL.write_text(raw_error_jsonl, encoding="utf-8")

    parsed_outputs: dict[str, dict[str, Any]] = {}
    for line in raw_output_jsonl.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        parsed = without_domain._parse_batch_output_line(record)
        parsed_outputs[parsed["custom_id"]] = parsed

    error_map = without_domain._parse_error_file(raw_error_jsonl) if raw_error_jsonl else {}
    trial_results, summary = _build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["cost"] = without_domain._estimate_batch_cost(batch.model_dump())

    without_domain._write_json(RESULTS_JSON, trial_results)
    without_domain._write_json(SUMMARY_JSON, summary)
    _write_report(summary, without_domain_summary_path)
    comparison_path = _write_comparison_report(summary, without_domain_summary_path)
    archive_dir = without_domain._archive_current_outputs(summary=summary)

    job_payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
        "batch": batch.model_dump(),
        "manifest_file": str(BATCH_MANIFEST_JSON),
        "output_jsonl_file": str(BATCH_OUTPUT_JSONL),
        "error_jsonl_file": str(BATCH_ERROR_JSONL) if batch.error_file_id else None,
    }
    without_domain._write_json(BATCH_JOB_JSON, job_payload)

    print(f"Collected batch output: {BATCH_OUTPUT_JSONL}")
    if batch.error_file_id:
        print(f"Collected batch errors: {BATCH_ERROR_JSONL}")
    print(f"Results: {RESULTS_JSON}")
    print(f"Summary: {SUMMARY_JSON}")
    print(f"Report:  {REPORT_MD}")
    if comparison_path:
        print(f"Comparison Report: {comparison_path}")
    else:
        print(f"Comparison Report: skipped (without-domain summary not found at {without_domain_summary_path})")
    print(f"Archive: {archive_dir}")
    return summary


def _quick_eval(without_domain_summary_path: Path) -> dict[str, Any]:
    summary = without_domain._quick_eval()
    summary["experiment"] = "with_domain_formal"
    summary["domain_knowledge"] = True
    summary["batch_mode"] = False
    summary["cost"] = without_domain._estimate_quick_eval_cost_from_artifacts(
        manifest=without_domain._load_json(BATCH_MANIFEST_JSON),
        trial_results=without_domain._load_json(RESULTS_JSON),
        model_name=summary["model"],
        calibration_run_dir=DEFAULT_WITHOUT_DOMAIN_BATCH_CALIBRATION_DIR,
    )
    without_domain._write_json(SUMMARY_JSON, summary)
    _write_report(summary, without_domain_summary_path)
    comparison_path = _write_comparison_report(summary, without_domain_summary_path)
    if comparison_path:
        print(f"Comparison Report: {comparison_path}")
    else:
        print(f"Comparison Report: skipped (without-domain summary not found at {without_domain_summary_path})")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Contribution2 Experiment 2: With Domain Knowledge batch evaluation"
    )
    parser.add_argument(
        "--mode",
        choices=["prepare", "prepare-submit", "status", "collect", "archive-current", "quick-eval"],
        default="prepare-submit",
        help="Batch workflow step (default: prepare-submit)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Prepare only the first N ontologies for debugging")
    parser.add_argument("--trials", type=int, default=10, help="Number of repeated trials per ontology (default: 10)")
    parser.add_argument("--batch-id", type=str, default=None, help="Optional batch ID override for status/collect")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="OpenAI model for this experiment (default: gpt-5.2)")
    parser.add_argument("--ontology", action="append", default=None, help="Run only the specified ontology (repeatable)")
    parser.add_argument("--ontologies-file", type=str, default=None, help="Path to a newline-delimited ontology filter file")
    parser.add_argument("--run-tag", type=str, default=None, help="Optional tag appended to the run directory name")
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore experiment-local prepare cache and refetch candidate metadata",
    )
    parser.add_argument(
        "--without-domain-summary",
        type=str,
        default=str(DEFAULT_WITHOUT_DOMAIN_SUMMARY_JSON),
        help="Path to the without-domain summary JSON used for comparison report generation",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    ontology_filter = without_domain._load_ontology_filter(args.ontology, args.ontologies_file)
    _configure_without_domain_module(model=args.model, trials=args.trials, run_tag=args.run_tag)
    without_domain_summary_path = Path(args.without_domain_summary)

    try:
        if args.mode == "prepare":
            without_domain._prepare(
                limit=args.limit,
                trials=args.trials,
                refresh_cache=args.refresh_cache,
                ontology_filter=ontology_filter,
            )
        elif args.mode == "prepare-submit":
            without_domain._prepare(
                limit=args.limit,
                trials=args.trials,
                refresh_cache=args.refresh_cache,
                ontology_filter=ontology_filter,
            )
            without_domain._submit_batch()
        elif args.mode == "status":
            without_domain._status(batch_id=args.batch_id)
        elif args.mode == "collect":
            _collect(batch_id=args.batch_id, without_domain_summary_path=without_domain_summary_path)
        elif args.mode == "archive-current":
            without_domain._archive_current_outputs()
        elif args.mode == "quick-eval":
            _quick_eval(without_domain_summary_path=without_domain_summary_path)
        else:
            raise ValueError(f"Unsupported mode: {args.mode}")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
