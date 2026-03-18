"""
Contribution2 Experiment 1: Prompt-Only Baseline batch evaluation.

This runner reuses the search-only batch workflow but strips all metadata from
direct-match candidates so Step 1 sees only candidate PGS IDs (no trait,
method, performance, or other fields) plus the fixed system prompt.  The LLM
must rely on parametric knowledge to choose among the candidates.
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

_ORIGINAL_PREPARE_MANIFEST = without_domain._prepare_manifest

RESULTS_JSON = Path()
SUMMARY_JSON = Path()
REPORT_MD = Path()

BATCH_REQUESTS_JSONL = Path()
BATCH_MANIFEST_JSON = Path()
BATCH_JOB_JSON = Path()
BATCH_OUTPUT_JSONL = Path()
BATCH_ERROR_JSONL = Path()


def _sync_paths_from_without_domain() -> None:
    global RESULTS_JSON, SUMMARY_JSON, REPORT_MD
    global BATCH_REQUESTS_JSONL, BATCH_MANIFEST_JSON, BATCH_JOB_JSON
    global BATCH_OUTPUT_JSONL, BATCH_ERROR_JSONL

    RESULTS_JSON = without_domain.RESULTS_JSON
    SUMMARY_JSON = without_domain.SUMMARY_JSON
    REPORT_MD = without_domain.REPORT_MD
    BATCH_REQUESTS_JSONL = without_domain.BATCH_REQUESTS_JSONL
    BATCH_MANIFEST_JSON = without_domain.BATCH_MANIFEST_JSON
    BATCH_JOB_JSON = without_domain.BATCH_JOB_JSON
    BATCH_OUTPUT_JSONL = without_domain.BATCH_OUTPUT_JSONL
    BATCH_ERROR_JSONL = without_domain.BATCH_ERROR_JSONL


def _set_prompt_artifact_paths() -> None:
    if without_domain.ACTIVE_RUN_DIR is None:
        raise RuntimeError("Without-domain run directory is not configured.")

    run_dir = without_domain.ACTIVE_RUN_DIR
    without_domain.RESULTS_JSON = run_dir / "experiment_prompt_only_results.json"
    without_domain.SUMMARY_JSON = run_dir / "experiment_prompt_only_summary.json"
    without_domain.REPORT_MD = run_dir / "experiment_prompt_only_report.md"
    without_domain.BATCH_REQUESTS_JSONL = run_dir / "experiment_prompt_only_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = run_dir / "experiment_prompt_only_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = run_dir / "experiment_prompt_only_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = run_dir / "experiment_prompt_only_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = run_dir / "experiment_prompt_only_batch_errors.jsonl"
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
    ]
    _sync_paths_from_without_domain()


def _prompt_archive_dir_name(
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
    dataset_label: Optional[str] = None,
) -> str:
    safe_model = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"prompt-only-{safe_model}-t{trials}"
    if dataset_label:
        base = f"{base}__{dataset_label}"
    safe_tag = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _configure_without_domain_module(model: Optional[str], trials: int, run_tag: Optional[str] = None) -> None:
    os.environ["PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"] = "1"
    os.environ["PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"] = "0"
    os.environ["PENNPRS_CONTRIB2_STRICT_LLM_ONLY"] = "1"

    if model is not None:
        without_domain._model_name = lambda: model  # type: ignore[assignment]
    without_domain._archive_dir_name = _prompt_archive_dir_name  # type: ignore[assignment]
    without_domain._prepare_manifest = _prepare_manifest  # type: ignore[assignment]
    without_domain._step1_context = _step1_context  # type: ignore[assignment]
    without_domain._write_report = _write_report  # type: ignore[assignment]
    without_domain._write_without_domain_per_disease_doc = _write_prompt_only_per_disease_doc  # type: ignore[assignment]
    without_domain._set_run_paths(trials=trials, model=model, run_tag=run_tag)
    _set_prompt_artifact_paths()


def _doc_path(stem: str) -> Path:
    label = without_domain.ACTIVE_BENCHMARK_LABEL or "30disease"
    return without_domain.DOCS_DIR / f"{stem}__{label}.md"


def _step1_context(
    ontology: str,
    candidate_models: list[Any],
    total_found: int,
) -> dict[str, Any]:
    return {
        "target_trait": ontology,
        "direct_models": {
            "query_trait": ontology,
            "total_found": total_found,
            "after_filter": len(candidate_models),
            "models": [{"id": getattr(m, "id", None)} for m in candidate_models],
        },
        "domain_knowledge": {
            "query": "",
            "snippets": [],
            "source_type": "disabled_by_prompt_only",
        },
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


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
    manifest["experiment"] = "prompt_only_batch_formal"
    manifest["prompt_only"] = True
    manifest["domain_knowledge"] = False
    manifest["model"] = without_domain._model_name()
    return manifest


def _write_prompt_only_per_disease_doc(summary: dict[str, Any]) -> Path:
    without_domain._ensure_summary_hit_metrics(summary)
    auc_lookup = without_domain._load_aou_auc_lookup()
    per_disease_rows = without_domain._sort_disease_rows(summary["per_disease"])
    output_path = _doc_path("prompt_only_per_disease_comparison")
    rank_fraction = without_domain._compute_rank_metric_summary(summary, without_domain._rank_fraction)
    reverse_rank_fraction = without_domain._compute_rank_metric_summary(summary, without_domain._reverse_rank_fraction)
    nrs = summary.get("nrs") or without_domain._compute_nrs_metrics(summary)

    lines = [
        f"# {without_domain.PROMPT_ONLY_LABEL}: Per-Disease Comparison",
        "",
        "## Scope",
        "",
        f"This report is a disease-by-disease comparison built from the {without_domain.PROMPT_ONLY_LABEL.lower()} experiment summary and the underlying AoU benchmark matrices.",
        "",
        "Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).",
        "",
        "Each disease table includes the benchmark top-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models).",
        "Rows `Hit@1`..`Hit@5` are evaluated over the full disease/trial set; when a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models for that disease.",
        "",
        "## High-Level Outcome",
        "",
        *[
            (
                f"- {without_domain.PROMPT_ONLY_LABEL} `Hit@{k}`: "
                f"`{summary['modal_hit_at_k'][str(k)]['hits']}/{summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {summary['trial_hit_at_k'][str(k)]['hits']}/{summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        "",
        *without_domain._rank_metric_section_lines(
            title="Rank Fraction (r / M)",
            metric_display="r / M",
            formula_text="r / M",
            scale_lines=[
                "- Scale: smaller is better.",
                "- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.",
            ],
            metrics_by_label=[(without_domain.PROMPT_ONLY_LABEL, rank_fraction)],
        ),
        *without_domain._rank_metric_section_lines(
            title="Reverse Rank Fraction ((M - r) / M)",
            metric_display="(M - r) / M",
            formula_text="(M - r) / M",
            scale_lines=[
                "- Scale: `0.0` means bottom-ranked; larger is better.",
                "- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.",
            ],
            metrics_by_label=[(without_domain.PROMPT_ONLY_LABEL, reverse_rank_fraction)],
        ),
        *without_domain._rank_metric_section_lines(
            title="Normalized Ranking Score (NRS)",
            metric_display="NRS",
            formula_text="NRS = (M - r) / (M - 1)",
            scale_lines=[
                "- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.",
            ],
            metrics_by_label=[(without_domain.PROMPT_ONLY_LABEL, nrs)],
        ),
        "",
        "## Per-Disease Tables",
        "",
    ]

    for row in per_disease_rows:
        ontology = row["ontology"]
        models = without_domain._model_map(row)
        benchmark_columns = without_domain._benchmark_columns(row)
        prompt_id = row.get("modal_recommendation")

        header = ["Field"] + [label for label, _, _ in benchmark_columns] + [without_domain.PROMPT_ONLY_LABEL, "Field Type"]
        separator = ["---"] * len(header)

        lines.extend([
            f"### {ontology}",
            "",
            f"Candidate pool: `{row['n_models']}` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.",
            "",
            "",
            f"| {' | '.join(header)} |",
            f"| {' | '.join(separator)} |",
        ])

        for field, field_type in without_domain.FIELD_ROWS:
            values = [field]
            for _, benchmark_id, selection_label in benchmark_columns:
                values.append(
                    without_domain._build_per_disease_doc_value(
                        field=field,
                        ontology=ontology,
                        selected_id=benchmark_id,
                        row=row,
                        model_map=models,
                        auc_lookup=auc_lookup,
                        selection_label=selection_label,
                    )
                )
            values.append(
                without_domain._build_per_disease_doc_value(
                    field=field,
                    ontology=ontology,
                    selected_id=prompt_id,
                    row=row,
                    model_map=models,
                    auc_lookup=auc_lookup,
                    selection_label=f"{row.get('modal_recommendation_count', 0)}/{summary['trials_per_ontology']} trials",
                )
            )
            values.append("Agent Input" if field_type == "agent_input" else "Benchmark Only")
            lines.append(f"| {' | '.join(values)} |")

        lines.extend(["", ""])

    without_domain.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _write_report(summary: dict[str, Any]) -> None:
    without_domain._ensure_summary_hit_metrics(summary)
    total_ontologies = summary["total_ontologies"]
    total_trials = summary["diagnostics"]["total_trials"]
    rank_fraction = without_domain._compute_rank_metric_summary(summary, without_domain._rank_fraction)
    reverse_rank_fraction = without_domain._compute_rank_metric_summary(summary, without_domain._reverse_rank_fraction)
    nrs = summary.get("nrs") or without_domain._compute_nrs_metrics(summary)
    cost = summary.get("cost") or {}
    token_usage = cost.get("token_usage") or {}
    cost_breakdown = cost.get("estimated_cost_breakdown_usd") or {}
    per_disease_rows = without_domain._sort_disease_rows(summary["per_disease"])

    lines = [
        f"# Contribution2 Experiment 1: {without_domain.PROMPT_ONLY_LABEL}",
        "",
        "## Summary",
        "",
        f"- **Diseases**: {total_ontologies}",
        f"- **Trials per disease**: {summary['trials_per_ontology']}",
        f"- **Total trials**: {total_trials}",
        f"- **Model**: {summary['model']}",
        f"- **Valid output rate**: {summary['diagnostics']['valid_outputs']}/{total_trials} = {without_domain._format_percent(summary['diagnostics']['valid_output_rate'])}",
        (
            f"- **Estimated API cost**: {without_domain._format_currency(cost.get('estimated_total_cost_usd', 0.0))} "
            f"(uncached input {token_usage.get('uncached_input_tokens', 0):,} tokens = "
            f"{without_domain._format_currency(cost_breakdown.get('uncached_input', 0.0))}; "
            f"cached input {token_usage.get('cached_input_tokens', 0):,} tokens = "
            f"{without_domain._format_currency(cost_breakdown.get('cached_input', 0.0))}; "
            f"output {token_usage.get('output_tokens', 0):,} tokens = "
            f"{without_domain._format_currency(cost_breakdown.get('output', 0.0))})"
        ),
        "",
        "## High-Level Outcome",
        "",
        *[
            (
                f"- {without_domain.PROMPT_ONLY_LABEL} `Hit@{k}`: `{summary['modal_hit_at_k'][str(k)]['hits']}/"
                f"{summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {summary['trial_hit_at_k'][str(k)]['hits']}/"
                f"{summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        "",
        *without_domain._percentile_hit_section_lines([
            (without_domain.PROMPT_ONLY_LABEL, summary["modal_percentile_hit"], summary["trial_percentile_hit"]),
        ]),
        *without_domain._rank_metric_section_lines(
            title="Rank Fraction (r / M)",
            metric_display="r / M",
            formula_text="r / M",
            scale_lines=[
                "- Scale: smaller is better.",
                "- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.",
            ],
            metrics_by_label=[(without_domain.PROMPT_ONLY_LABEL, rank_fraction)],
        ),
        *without_domain._rank_metric_section_lines(
            title="Reverse Rank Fraction ((M - r) / M)",
            metric_display="(M - r) / M",
            formula_text="(M - r) / M",
            scale_lines=[
                "- Scale: `0.0` means bottom-ranked; larger is better.",
                "- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.",
            ],
            metrics_by_label=[(without_domain.PROMPT_ONLY_LABEL, reverse_rank_fraction)],
        ),
        *without_domain._rank_metric_section_lines(
            title="Normalized Ranking Score (NRS)",
            metric_display="NRS",
            formula_text="NRS = (M - r) / (M - 1)",
            scale_lines=[
                "- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.",
            ],
            metrics_by_label=[(without_domain.PROMPT_ONLY_LABEL, nrs)],
        ),
        "",
        "## Experiment Setup",
        "",
        "- **Step 1 tools**: none (candidate PGS IDs visible, all metadata stripped)",
        "- **Domain Knowledge**: Disabled",
        "- **Candidate pool visibility to LLM**: ID-only (no trait, method, performance, or other metadata)",
        "- **Candidate pool for evaluation**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us",
        "- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking using the full disease/trial denominator; if a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models",
        "- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`",
        "",
        "## Results by Disease",
        "",
        "All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.",
        "They are **not** PGS Catalog reported-AUC ranks.",
        "",
        f"| Ontology | N Models | Trial Hit@1..5 | {without_domain.PROMPT_ONLY_LABEL} Hit@1..5 | {without_domain.PROMPT_ONLY_LABEL} |",
        "|----------|----------|---------------|------------------------------|------------------------|",
    ]

    for row in per_disease_rows:
        recommendation_models = "<br>".join(
            f"{item['pgs_id']} (AUC rank {item['rank_label']}): x{item['count']}"
            for item in (row.get("recommended_model_counts") or [])
        ) or "-"
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | "
            f"{without_domain._format_rate_vector(row.get('trial_hit_rates_at_k') or {})} | "
            f"{without_domain._format_hit_vector(row.get('modal_recommendation_hit_at_k') or {})} | "
            f"{recommendation_models} |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def _submit_batch() -> dict[str, Any]:
    if not BATCH_REQUESTS_JSONL.exists():
        raise FileNotFoundError(f"Batch requests not found: {BATCH_REQUESTS_JSONL}")
    if not BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(f"Batch manifest not found: {BATCH_MANIFEST_JSON}")

    client = without_domain._client()
    with BATCH_REQUESTS_JSONL.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "experiment": "contribution2_prompt_only",
            "manifest_file": BATCH_MANIFEST_JSON.name,
        },
    )
    job = {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "request_file": str(BATCH_REQUESTS_JSONL),
        "manifest_file": str(BATCH_MANIFEST_JSON),
        "status": batch.status,
        "batch": batch.model_dump(),
    }
    without_domain._write_json(BATCH_JOB_JSON, job)
    print(f"Uploaded batch input file: {uploaded.id}")
    print(f"Created batch job: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Saved job metadata: {BATCH_JOB_JSON}")
    return job


def _status(batch_id: Optional[str]) -> dict[str, Any]:
    job = without_domain._load_job(batch_id=batch_id)
    client = without_domain._client()
    batch = client.batches.retrieve(job["batch_id"])
    payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
        "batch": batch.model_dump(),
    }
    without_domain._write_json(BATCH_JOB_JSON, payload)
    print(json.dumps(payload, indent=2))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Contribution2 Experiment 1: {without_domain.PROMPT_ONLY_LABEL} batch evaluation"
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
    parser.add_argument("--model", type=str, default="gpt-5.2", help="OpenAI model for this experiment (default: gpt-5.2)")
    parser.add_argument("--ontology", action="append", default=None, help="Run only the specified ontology (repeatable)")
    parser.add_argument("--ontologies-file", type=str, default=None, help="Path to a newline-delimited ontology filter file")
    parser.add_argument("--run-tag", type=str, default=None, help="Optional tag appended to the run directory name")
    parser.add_argument(
        "--union-csv",
        type=str,
        default=str(without_domain.DEFAULT_UNION_CSV),
        help="Disease union CSV used for evaluation (default: frozen 30-disease union).",
    )
    parser.add_argument(
        "--ground-truth-dir",
        type=str,
        default=None,
        help="Ground-truth directory produced by generate_evaluated_pgs_list.py. Defaults to a path derived from --union-csv.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore experiment-local prepare cache and refetch candidate metadata",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    if args.model:
        os.environ["OPENAI_MODEL"] = args.model

    ontology_filter = without_domain._load_ontology_filter(args.ontology, args.ontologies_file)
    without_domain._configure_benchmark_sources(union_csv=args.union_csv, ground_truth_dir=args.ground_truth_dir)
    _configure_without_domain_module(model=args.model, trials=args.trials, run_tag=args.run_tag)

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
            _submit_batch()
        elif args.mode == "status":
            _status(batch_id=args.batch_id)
        elif args.mode == "collect":
            without_domain._collect(batch_id=args.batch_id)
        elif args.mode == "archive-current":
            without_domain._archive_current_outputs()
        elif args.mode == "quick-eval":
            without_domain._quick_eval()
        else:
            raise ValueError(f"Unsupported mode: {args.mode}")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
