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
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

_ORIGINAL_PREPARE_MANIFEST = without_domain._prepare_manifest
_ORIGINAL_STEP1_MESSAGES = without_domain._step1_messages

RECOMMENDATION_RUNS = Path(__file__).parent.parent / "runs"
DOCS_DIR = Path(__file__).parent.parent / "docs"
CONTRIB1_RESULT_DIR = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "aou_icd_260217"
CHILDCODE_AUC_MATRIX = CONTRIB1_RESULT_DIR / "prs_adjauc_matrix_260217_childrencode.csv"
ROOTCODE_AUC_MATRIX = CONTRIB1_RESULT_DIR / "prs_adjauc_matrix_260217_rootcode.csv"

RESULTS_JSON = Path()
SUMMARY_JSON = Path()
REPORT_MD = Path()

BATCH_REQUESTS_JSONL = Path()
BATCH_MANIFEST_JSON = Path()
BATCH_JOB_JSON = Path()
BATCH_OUTPUT_JSONL = Path()
BATCH_ERROR_JSONL = Path()

COMPARISON_REPORT_MD = Path()
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_WITHOUT_DOMAIN_BATCH_CALIBRATION_DIR = RECOMMENDATION_RUNS / "without-domain-gpt-5.2-t10"

FIELD_ROWS: list[tuple[str, str]] = [
    ("Selected PGS ID", "agent_input"),
    ("AoU benchmark rank", "benchmark_only"),
    ("AoU benchmark AUC", "benchmark_only"),
    ("Hit@1", "benchmark_only"),
    ("Hit@2", "benchmark_only"),
    ("Hit@3", "benchmark_only"),
    ("Hit@4", "benchmark_only"),
    ("Hit@5", "benchmark_only"),
    ("Selection frequency", "benchmark_only"),
    ("trait_reported", "agent_input"),
    ("trait_efo", "agent_input"),
    ("phenotyping_reported", "agent_input"),
    ("method_name", "agent_input"),
    ("performance_metrics.selected_performance_id", "agent_input"),
    ("performance_metrics.selected_validation_ancestry", "agent_input"),
    ("performance_metrics.record_count", "agent_input"),
    ("performance_metrics.auc", "agent_input"),
    ("performance_metrics.r2", "agent_input"),
    ("performance_metrics.full_model_auc", "agent_input"),
    ("performance_metrics.full_model_r2", "agent_input"),
    ("performance_metrics.incremental_auc", "agent_input"),
    ("performance_metrics.classification_metrics", "agent_input"),
    ("performance_metrics.other_metrics", "agent_input"),
    ("performance_metrics.effect_sizes", "agent_input"),
    ("validation_sample_size", "agent_input"),
    ("samples_training", "agent_input"),
    ("ancestry_distribution", "agent_input"),
    ("training_development_cohorts", "agent_input"),
    ("publication.title", "agent_input"),
    ("publication.journal", "agent_input"),
    ("date_release", "agent_input"),
    ("variants_number", "agent_input"),
    ("covariates", "agent_input"),
]


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


def _comparison_doc_path() -> Path:
    return without_domain._doc_path("with_vs_without_domain_per_disease_comparison")


def _default_without_domain_summary_path(model: str, trials: int, run_tag: Optional[str]) -> Path:
    run_dir = RECOMMENDATION_RUNS / without_domain._archive_dir_name(
        model,
        trials,
        run_tag=run_tag,
        dataset_label=without_domain.ACTIVE_BENCHMARK_LABEL,
    )
    return run_dir / "experiment_without_domain_summary.json"


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


def _domain_archive_dir_name(
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
    dataset_label: Optional[str] = None,
) -> str:
    safe_model = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"with-domain-{safe_model}-t{trials}"
    if dataset_label:
        base = f"{base}__{dataset_label}"
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
        f"target_trait: {ontology}; PRS clinical thresholds AUC R2 heritability ceiling sanity-check must-pass gates "
        "phenotype alignment endpoint specificity external transfer reliability "
        "ancestry compatibility ranking features penalties method priors "
        "validation sample size tie-break time-to-event horizon-specific "
        "incident case-control dominant subtype PGS-only no-covariates incremental AUROC "
        "snpnet biobank transportability"
    )


def _step1_context(
    ontology: str,
    candidate_models: list[Any],
    total_found: int,
    landscape: dict[str, Any],
) -> dict[str, Any]:
    query = _domain_query(ontology)
    domain = prs_model_domain_knowledge(query, max_snippets=8).model_dump()
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
    return _ORIGINAL_STEP1_MESSAGES(context_json)


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


def _normalize_ontology_key(text: str) -> str:
    return (text or "").strip().lower()


def _load_aou_auc_lookup() -> dict[str, dict[str, float]]:
    if not without_domain.UNION_CSV.exists():
        raise FileNotFoundError(f"Union CSV not found: {without_domain.UNION_CSV}")
    if not CHILDCODE_AUC_MATRIX.exists():
        raise FileNotFoundError(f"Child-code AUC matrix not found: {CHILDCODE_AUC_MATRIX}")
    if not ROOTCODE_AUC_MATRIX.exists():
        raise FileNotFoundError(f"Root-code AUC matrix not found: {ROOTCODE_AUC_MATRIX}")

    union_df = pd.read_csv(without_domain.UNION_CSV)
    child_matrix = pd.read_csv(CHILDCODE_AUC_MATRIX)
    root_matrix = pd.read_csv(ROOTCODE_AUC_MATRIX)

    lookup: dict[str, dict[str, float]] = {}
    child_row_map = child_matrix.set_index("trait")
    root_row_map = root_matrix.set_index("trait")

    for _, row in union_df.iterrows():
        ontology = str(row.get("Ontology", "")).strip()
        icd = str(row.get("ICD", "")).strip()
        source = str(row.get("Source", "")).strip().lower()
        if not ontology or not icd:
            continue

        matrix = child_row_map if source in {"childrencode", "both"} else root_row_map
        if icd not in matrix.index:
            continue

        auc_row = matrix.loc[icd]
        if isinstance(auc_row, pd.DataFrame):
            auc_row = auc_row.iloc[0]

        ontology_key = _normalize_ontology_key(ontology)
        per_model: dict[str, float] = {}
        for column, value in auc_row.items():
            if column == "trait" or pd.isna(value):
                continue
            pgs_id = str(column).replace("_hmPOS_GRCh38", "")
            try:
                per_model[pgs_id] = float(value)
            except (TypeError, ValueError):
                continue
        lookup[ontology_key] = per_model

    return lookup


def _model_map(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(model.get("id")): model
        for model in (row.get("candidate_models_visible_to_llm") or [])
        if model.get("id")
    }


def _get_nested_field(model: Optional[dict[str, Any]], field: str) -> Any:
    if not model:
        return None
    if field == "Selected PGS ID":
        return model.get("id")
    if "." not in field:
        return model.get(field)
    value: Any = model
    for part in field.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _collapse_whitespace(text: str) -> str:
    return " ".join((text or "").split())


def _format_doc_value(value: Any, field: str) -> str:
    if value is None or value == "":
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "N/A"
        return _collapse_whitespace(" ".join(str(v) for v in value))
    if isinstance(value, dict):
        return _collapse_whitespace(json.dumps(value, sort_keys=True))

    text = str(value)
    text = text.replace("|", " / ").replace("\n", " ")
    text = _collapse_whitespace(text)
    return text or "N/A"


def _benchmark_rank_label(selected_id: Optional[str], row: dict[str, Any]) -> str:
    if not selected_id:
        return "N/A"
    ranked_ids = row.get("benchmark_ranked_ids") or []
    try:
        rank = ranked_ids.index(selected_id) + 1
        return f"{rank}/{len(ranked_ids)}"
    except ValueError:
        return "N/A"


def _benchmark_auc_value(
    ontology: str,
    selected_id: Optional[str],
    auc_lookup: dict[str, dict[str, float]],
) -> str:
    if not selected_id:
        return "N/A"
    value = auc_lookup.get(_normalize_ontology_key(ontology), {}).get(selected_id)
    if value is None:
        return "N/A"
    return f"{value:.4f}"


def _hit_at_k_label(selected_id: Optional[str], row: dict[str, Any], k: int) -> str:
    return without_domain._hit_at_k_label(selected_id, row, k)


def _build_comparison_doc_value(
    field: str,
    ontology: str,
    selected_id: Optional[str],
    row: dict[str, Any],
    model_map: dict[str, dict[str, Any]],
    auc_lookup: dict[str, dict[str, float]],
    selection_label: str,
) -> str:
    if field == "Selected PGS ID":
        return selected_id or "N/A"
    if field == "AoU benchmark rank":
        return _benchmark_rank_label(selected_id, row)
    if field == "AoU benchmark AUC":
        return _benchmark_auc_value(ontology, selected_id, auc_lookup)
    hit_k = without_domain._hit_at_k_field(field)
    if hit_k is not None:
        return _hit_at_k_label(selected_id, row, hit_k)
    if field == "Selection frequency":
        return selection_label

    model = model_map.get(selected_id or "")
    return _format_doc_value(_get_nested_field(model, field), field)


def _write_per_disease_comparison_doc(
    domain_summary: dict[str, Any],
    without_domain_summary_path: Path,
) -> Optional[Path]:
    if not without_domain_summary_path.exists():
        return None

    without_domain_summary = json.loads(without_domain_summary_path.read_text(encoding="utf-8"))
    output_path = _comparison_doc_path()
    without_domain._ensure_summary_hit_metrics(domain_summary)
    without_domain._ensure_summary_hit_metrics(without_domain_summary)
    auc_lookup = _load_aou_auc_lookup()
    domain_nrs = without_domain._compute_nrs_metrics(domain_summary)
    without_domain_nrs = without_domain._compute_nrs_metrics(without_domain_summary)
    domain_rows = {row["ontology"]: row for row in domain_summary["per_disease"]}
    without_domain_rows = {row["ontology"]: row for row in without_domain_summary["per_disease"]}
    per_disease_rows = without_domain._sort_disease_rows(domain_summary["per_disease"])

    lines = [
        "# With Domain Knowledge vs Without Domain Knowledge: Per-Disease Comparison",
        "",
        "## Scope",
        "",
        "This report is a disease-by-disease comparison built from the latest with-domain and without-domain experiment summaries and the underlying AoU benchmark matrices.",
        "",
        "Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).",
        "",
        "Each disease table includes benchmark-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models), followed by the current with-domain, without-domain, and baseline selections.",
        "Rows `Hit@1`..`Hit@5` use eligible-only denominators; diseases with fewer than `k` evaluated models are marked `N/A` for `Hit@k`.",
        "",
        "## High-Level Outcome",
        "",
        *[
            (
                f"- With Domain Knowledge `Hit@{k}`: `{domain_summary['modal_hit_at_k'][str(k)]['hits']}/"
                f"{domain_summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(domain_summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {domain_summary['trial_hit_at_k'][str(k)]['hits']}/"
                f"{domain_summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(domain_summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        *[
            (
                f"- Without Domain Knowledge `Hit@{k}`: `{without_domain_summary['modal_hit_at_k'][str(k)]['hits']}/"
                f"{without_domain_summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(without_domain_summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {without_domain_summary['trial_hit_at_k'][str(k)]['hits']}/"
                f"{without_domain_summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(without_domain_summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        *[
            (
                f"- Baseline `Hit@{k}`: `{domain_summary['baseline']['hit_at_k'][str(k)]['hits']}/"
                f"{domain_summary['baseline']['hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(domain_summary['baseline']['hit_at_k'][str(k)]['accuracy'] or 0.0)}` "
                f"(coverage `{domain_summary['baseline']['hit_at_k'][str(k)]['available']}/"
                f"{domain_summary['baseline']['hit_at_k'][str(k)]['eligible']}`)"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        "",
        "## Normalized Ranking Score (NRS)",
        "",
        "- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.",
        "- Formula: `NRS = (M - r) / (M - 1)`, with `r = 1` as best and `r = M` as worst.",
        "- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.",
        (
            f"- With Domain Knowledge: "
            f"`mean NRS = {without_domain._format_score(domain_nrs['modal_mean_nrs'])}` "
            f"({domain_nrs['modal_count']} modal selections); "
            f"`trial mean NRS = {without_domain._format_score(domain_nrs['trial_mean_nrs'])}` "
            f"({domain_nrs['trial_count']} trials)"
        ),
        (
            f"- Without Domain Knowledge: "
            f"`mean NRS = {without_domain._format_score(without_domain_nrs['modal_mean_nrs'])}` "
            f"({without_domain_nrs['modal_count']} modal selections); "
            f"`trial mean NRS = {without_domain._format_score(without_domain_nrs['trial_mean_nrs'])}` "
            f"({without_domain_nrs['trial_count']} trials)"
        ),
        "",
        "## Per-Disease Tables",
        "",
    ]

    for row in per_disease_rows:
        ontology = row["ontology"]
        domain_row = domain_rows[ontology]
        without_row = without_domain_rows[ontology]
        models = _model_map(domain_row)
        benchmark_columns = without_domain._benchmark_columns(row)
        with_id = domain_row.get("modal_recommendation")
        without_id = without_row.get("modal_recommendation")
        baseline_id = (domain_row.get("baseline") or {}).get("pgs_id")

        header = ["Field"] + [label for label, _, _ in benchmark_columns] + ["With Domain Knowledge", "Without Domain Knowledge", "Baseline", "Field Type"]
        separator = ["---"] * len(header)

        lines.extend([
            f"### {ontology}",
            "",
            f"Candidate pool: `{row['n_models']}` models. Eligible `Hit@k`: `{without_domain._format_eligible_ks(row.get('eligible_at_k') or {})}`.",
            "",
            "",
            f"| {' | '.join(header)} |",
            f"| {' | '.join(separator)} |",
        ])

        for field, field_type in FIELD_ROWS:
            values = [field]
            for _, benchmark_id, selection_label in benchmark_columns:
                values.append(
                    _build_comparison_doc_value(
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
                _build_comparison_doc_value(
                    field=field,
                    ontology=ontology,
                    selected_id=with_id,
                    row=domain_row,
                    model_map=models,
                    auc_lookup=auc_lookup,
                    selection_label=f"{domain_row.get('modal_recommendation_count', 0)}/{domain_summary['trials_per_ontology']} trials",
                )
            )
            values.append(
                _build_comparison_doc_value(
                    field=field,
                    ontology=ontology,
                    selected_id=without_id,
                    row=without_row,
                    model_map=models,
                    auc_lookup=auc_lookup,
                    selection_label=f"{without_row.get('modal_recommendation_count', 0)}/{without_domain_summary['trials_per_ontology']} trials",
                )
            )
            values.append(
                _build_comparison_doc_value(
                    field=field,
                    ontology=ontology,
                    selected_id=baseline_id,
                    row=domain_row,
                    model_map=models,
                    auc_lookup=auc_lookup,
                    selection_label="Rule-based baseline",
                )
            )
            values.append("Agent Input" if field_type == "agent_input" else "Benchmark Only")
            lines.append(f"| {' | '.join(values)} |")

        lines.extend(["", ""])

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    without_domain._write_without_domain_per_disease_doc(without_domain_summary)
    return output_path


def _write_report(summary: dict[str, Any], without_domain_summary_path: Path) -> None:
    without_domain._ensure_summary_hit_metrics(summary)
    total_ontologies = summary["total_ontologies"]
    total_trials = summary["diagnostics"]["total_trials"]
    without_domain_summary = json.loads(without_domain_summary_path.read_text(encoding="utf-8"))
    without_domain._ensure_summary_hit_metrics(without_domain_summary)
    nrs = without_domain._compute_nrs_metrics(summary)
    without_domain_nrs = without_domain._compute_nrs_metrics(without_domain_summary)
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
        *[
            (
                f"- **With Domain Modal Hit@{k}**: {summary['modal_hit_at_k'][str(k)]['hits']}/"
                f"{summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}; "
                f"`trial_hits = {summary['trial_hit_at_k'][str(k)]['hits']}/"
                f"{summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        *[
            (
                f"- **Without Domain Modal Hit@{k}**: {without_domain_summary['modal_hit_at_k'][str(k)]['hits']}/"
                f"{without_domain_summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(without_domain_summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}; "
                f"`trial_hits = {without_domain_summary['trial_hit_at_k'][str(k)]['hits']}/"
                f"{without_domain_summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(without_domain_summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        "",
        "## Normalized Ranking Score (NRS)",
        "",
        "- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.",
        "- Formula: `NRS = (M - r) / (M - 1)`, with `r = 1` as best and `r = M` as worst.",
        "- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.",
        (
            f"- With Domain Knowledge: `mean NRS = {without_domain._format_score(nrs['modal_mean_nrs'])}` "
            f"({nrs['modal_count']} modal selections); "
            f"`trial mean NRS = {without_domain._format_score(nrs['trial_mean_nrs'])}` "
            f"({nrs['trial_count']} trials)"
        ),
        (
            f"- Without Domain Knowledge: `mean NRS = {without_domain._format_score(without_domain_nrs['modal_mean_nrs'])}` "
            f"({without_domain_nrs['modal_count']} modal selections); "
            f"`trial mean NRS = {without_domain._format_score(without_domain_nrs['trial_mean_nrs'])}` "
            f"({without_domain_nrs['trial_count']} trials)"
        ),
        "",
        "## Experiment Setup",
        "",
        "- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_domain_knowledge + prs_model_performance_landscape",
        "- **Domain Knowledge**: Enabled (local curated knowledge base)",
        "- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us",
        "- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking; diseases with fewer than `k` evaluated models are excluded from the `Hit@k` denominator",
        "- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`",
        "- **Without Domain Knowledge reference**: compare against `without-domain-gpt-5.2-t10` under the same 30-disease / 10-trial protocol",
        "",
        "## Results by Disease",
        "",
        "All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.",
        "They are **not** PGS Catalog reported-AUC ranks.",
        "",
        "| Ontology | N Models | Eligible Ks | Trial Hit@1..5 | With Domain Knowledge Hit@1..5 | With Domain Knowledge | Without Domain Knowledge Hit@1..5 | Without Domain Knowledge |",
        "|----------|----------|-------------|---------------|----------------------------------|-----------------------|-------------------------------------|--------------------------|",
    ]

    for row in per_disease_rows:
        without_domain_row = without_domain_rows[row["ontology"]]
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | {without_domain._format_eligible_ks(row.get('eligible_at_k') or {})} | "
            f"{without_domain._format_rate_vector(row.get('trial_hit_rates_at_k') or {})} | "
            f"{without_domain._format_hit_vector(row.get('modal_recommendation_hit_at_k') or {})} | {_format_models(row.get('recommended_model_counts') or [])} | "
            f"{without_domain._format_hit_vector(without_domain_row.get('modal_recommendation_hit_at_k') or {})} | {_format_models(without_domain_row.get('recommended_model_counts') or [])} |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def _write_comparison_report(domain_summary: dict[str, Any], without_domain_summary_path: Path) -> Optional[Path]:
    if not without_domain_summary_path.exists():
        return None

    without_domain_summary = json.loads(without_domain_summary_path.read_text(encoding="utf-8"))
    without_domain._ensure_summary_hit_metrics(domain_summary)
    without_domain._ensure_summary_hit_metrics(without_domain_summary)
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
            f"{domain_summary['modal_hit_at_k']['1']['hits']}/{domain_summary['modal_hit_at_k']['1']['eligible']} = "
            f"{without_domain._format_percent(domain_summary['modal_hit_at_k']['1']['accuracy'] or 0.0)}; "
            f"`trial_hits = {domain_summary['trial_hit_at_k']['1']['hits']}/{domain_summary['trial_hit_at_k']['1']['eligible']} = {without_domain._format_percent(domain_summary['trial_hit_at_k']['1']['accuracy'] or 0.0)}`"
        ),
        (
            f"- **Without Domain Knowledge**: "
            f"{without_domain_summary['modal_hit_at_k']['1']['hits']}/{without_domain_summary['modal_hit_at_k']['1']['eligible']} = "
            f"{without_domain._format_percent(without_domain_summary['modal_hit_at_k']['1']['accuracy'] or 0.0)}; "
            f"`trial_hits = {without_domain_summary['trial_hit_at_k']['1']['hits']}/{without_domain_summary['trial_hit_at_k']['1']['eligible']} = {without_domain._format_percent(without_domain_summary['trial_hit_at_k']['1']['accuracy'] or 0.0)}`"
        ),
        (
            f"- **Baseline**: "
            f"{domain_summary['baseline']['hits']}/{domain_summary['total_ontologies']} = "
            f"{without_domain._format_percent(domain_summary['baseline']['accuracy'])}"
        ),
        "",
        "## Results by Disease",
        "",
        "| Ontology | N Models | Eligible Ks | Baseline Hit@1..5 | Baseline Models | Without Domain Knowledge Hit@1..5 | Without Domain Knowledge | With Domain Knowledge Hit@1..5 | With Domain Knowledge |",
        "|----------|----------|-------------|-------------------|-----------------|-------------------------------------|--------------------------|----------------------------------|-----------------------|",
    ]

    for row in per_disease_rows:
        domain_row = domain_rows[row["ontology"]]
        without_domain_row = without_domain_rows[row["ontology"]]
        baseline = domain_row.get("baseline") or {}
        baseline_id = baseline.get("pgs_id")
        baseline_rank_label = baseline.get("rank_label") or "-"
        baseline_text = f"{baseline_id} (AUC rank {baseline_rank_label})" if baseline_id else "-"
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | {without_domain._format_eligible_ks(row.get('eligible_at_k') or {})} | "
            f"{without_domain._format_hit_vector(domain_row.get('baseline_hit_at_k') or {})} | "
            f"{baseline_text} | "
            f"{without_domain._format_hit_vector(without_domain_row.get('modal_recommendation_hit_at_k') or {})} | "
            f"{_format_models(without_domain_row.get('recommended_model_counts') or [])} | "
            f"{without_domain._format_hit_vector(domain_row.get('modal_recommendation_hit_at_k') or {})} | "
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
    per_disease_doc_path = _write_per_disease_comparison_doc(summary, without_domain_summary_path)
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
    if per_disease_doc_path:
        print(f"Per-disease doc: {per_disease_doc_path}")
    else:
        print(f"Per-disease doc: skipped (without-domain summary not found at {without_domain_summary_path})")
    print(f"Archive: {archive_dir}")
    return summary


def _regenerate_baseline(
    without_domain_summary_path: Path,
    with_run_dir: Path,
) -> None:
    """Recompute tiered baseline in both summaries and regenerate per-disease docs."""
    # Load and recompute without-domain summary
    if not without_domain_summary_path.exists():
        print(f"ERROR: Without-domain summary not found: {without_domain_summary_path}")
        return
    without_summary = json.loads(without_domain_summary_path.read_text(encoding="utf-8"))
    without_domain._recompute_baseline_in_summary(without_summary)
    without_domain_summary_path.write_text(
        json.dumps(without_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Updated without-domain summary: {without_domain_summary_path}")

    # Write without-domain per-disease doc
    without_doc = without_domain._write_without_domain_per_disease_doc(without_summary)
    print(f"Wrote without-domain doc: {without_doc}")

    # Load and recompute with-domain summary
    with_summary_path = with_run_dir / "experiment_with_domain_summary.json"
    if not with_summary_path.exists():
        print(f"WARNING: With-domain summary not found: {with_summary_path}")
        print("Skipping with_vs_without_domain_per_disease_comparison.md")
        return
    with_summary = json.loads(with_summary_path.read_text(encoding="utf-8"))
    without_domain._recompute_baseline_in_summary(with_summary)
    with_summary_path.write_text(
        json.dumps(with_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Updated with-domain summary: {with_summary_path}")

    # Write with_vs_without per-disease doc
    comparison_doc = _write_per_disease_comparison_doc(with_summary, without_domain_summary_path)
    if comparison_doc:
        print(f"Wrote comparison doc: {comparison_doc}")


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
    per_disease_doc_path = _write_per_disease_comparison_doc(summary, without_domain_summary_path)
    if comparison_path:
        print(f"Comparison Report: {comparison_path}")
    else:
        print(f"Comparison Report: skipped (without-domain summary not found at {without_domain_summary_path})")
    if per_disease_doc_path:
        print(f"Per-disease doc: {per_disease_doc_path}")
    else:
        print(f"Per-disease doc: skipped (without-domain summary not found at {without_domain_summary_path})")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Contribution2 Experiment 2: With Domain Knowledge batch evaluation"
    )
    parser.add_argument(
        "--mode",
        choices=["prepare", "prepare-submit", "status", "collect", "archive-current", "quick-eval", "regenerate-baseline"],
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
    parser.add_argument(
        "--without-domain-summary",
        type=str,
        default=None,
        help="Optional path to the without-domain summary JSON used for comparison report generation. Defaults to the matching without-domain run for the same disease list.",
    )
    parser.add_argument(
        "--with-run-dir",
        type=str,
        default=None,
        help="For regenerate-baseline: path to with-domain run dir (default: runs/with-domain-gpt-5.2-t10)",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    ontology_filter = without_domain._load_ontology_filter(args.ontology, args.ontologies_file)
    without_domain._configure_benchmark_sources(
        union_csv=args.union_csv,
        ground_truth_dir=args.ground_truth_dir,
    )
    _configure_without_domain_module(model=args.model, trials=args.trials, run_tag=args.run_tag)
    without_domain_summary_path = (
        Path(args.without_domain_summary)
        if args.without_domain_summary
        else _default_without_domain_summary_path(args.model, args.trials, args.run_tag)
    )

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
        elif args.mode == "regenerate-baseline":
            _regenerate_baseline(
                without_domain_summary_path=without_domain_summary_path,
                with_run_dir=(
                    Path(args.with_run_dir)
                    if args.with_run_dir
                    else RECOMMENDATION_RUNS
                    / _domain_archive_dir_name(
                        args.model,
                        args.trials,
                        run_tag=args.run_tag,
                        dataset_label=without_domain.ACTIVE_BENCHMARK_LABEL,
                    )
                ),
            )
        else:
            raise ValueError(f"Unsupported mode: {args.mode}")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
