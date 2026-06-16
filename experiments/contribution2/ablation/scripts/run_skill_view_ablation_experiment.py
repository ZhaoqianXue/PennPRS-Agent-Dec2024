"""Run c2 PRS Model Skill-view ablations with OpenAI Batch.

This runner differs from the older domain-knowledge ablation runner:

- It ablates the packaged `prs_model_evaluator` Skill view directly.
- It uses the same-trait Skill view: SKILL.md overview plus reference/00-07.
- It always excludes reference/08_cross_trait_transfer_considerations.md.
- It clears `domain_knowledge.snippets` so removed Skill sections cannot leak
  back through snippets.
- The `no-skill` arm keeps the heritability evidence wrapper but removes the
  PRS Model Skill text.

Each arm is a separate batch job. By default the runner uses the updated
82-disease union and filters it to the frozen M>5 50-disease subset.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as with_domain
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from experiments.contribution2.recommendation.scripts.run_experiment_minimal_lift import (
    _format_heritability_section,
)
from src.server.core.tools.heritability import get_heritability_records
from src.server.core.tools.prs_model_evaluator_skill import REFERENCE_DIR, SKILL_DIR


ABLATION_DIR = Path(__file__).resolve().parent.parent
ABLATION_RUNS_DIR = ABLATION_DIR / "runs"
FILTERS_DIR = ABLATION_DIR / "filters"

DEFAULT_MODEL = "gpt-5.2"
DEFAULT_UNION_CSV = (
    PROJECT_ROOT
    / "experiments/contribution2/disease_selection/runs/"
    / "selected_diseases_contribution2_current_union__82disease.csv"
)
DEFAULT_GROUND_TRUTH_DIR = (
    PROJECT_ROOT
    / "experiments/contribution2/recommendation/runs/"
    / "ground-truth__selected_diseases_contribution2_current_union__82disease"
)
DEFAULT_ONTOLOGIES_FILE = FILTERS_DIR / "current82_Mgt5_50disease.txt"

SAME_TRAIT_REFERENCE_FILES = (
    "00_preamble.md",
    "01_trait_reported_trait_efo_phenotyping_reported.md",
    "02_performance_metrics_auc_performance_metrics_r2_covariates.md",
    "03_validation_sample_size.md",
    "04_training_development_cohorts_samples_training_ancestry_distr.md",
    "05_method_name.md",
    "06_publication_title_publication_journal_date_release.md",
    "07_variants_number.md",
)

ARM_TO_REMOVED_FILE: dict[str, Optional[str]] = {
    "skill-only-no-harness": None,
    "no-section1-trait-endpoint": "01_trait_reported_trait_efo_phenotyping_reported.md",
    "no-section2-performance-covariates": "02_performance_metrics_auc_performance_metrics_r2_covariates.md",
    "no-section3-validation-sample-size": "03_validation_sample_size.md",
    "no-section4-training-cohorts-ancestry": "04_training_development_cohorts_samples_training_ancestry_distr.md",
    "no-section5-method-name": "05_method_name.md",
    "no-section6-publication": "06_publication_title_publication_journal_date_release.md",
    "no-section7-variants-number": "07_variants_number.md",
    "no-skill": None,
}

ARM_LABELS = {
    "skill-only-no-harness": "Skill-only / no harness",
    "no-section1-trait-endpoint": "S1: trait / endpoint",
    "no-section2-performance-covariates": "S2: performance / covariates",
    "no-section3-validation-sample-size": "S3: validation_sample_size",
    "no-section4-training-cohorts-ancestry": "S4: training_cohorts / ancestry",
    "no-section5-method-name": "S5: method_name",
    "no-section6-publication": "S6: publication",
    "no-section7-variants-number": "S7: variants_number",
    "no-skill": "No PRS Model Skill",
}


def _split_yaml_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    frontmatter: dict[str, str] = {}
    body_start: Optional[int] = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = idx + 1
            break
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    if body_start is None:
        return {}, text
    return frontmatter, "\n".join(lines[body_start:]).lstrip("\n")


def _load_skill_overview() -> str:
    path = SKILL_DIR / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill overview not found: {path}")
    _, body = _split_yaml_frontmatter(path.read_text(encoding="utf-8"))
    body = _strip_cross_trait_overview(body)
    return body.strip()


def _strip_cross_trait_overview(body: str) -> str:
    """Return the same-trait-only Skill overview used by within-phenotype runs."""
    start = body.find("## Cross-trait transfer caveat")
    if start != -1:
        end = body.find("\n## Reference files", start)
        if end == -1:
            body = body[:start]
        else:
            body = body[:start].rstrip() + "\n" + body[end:].lstrip("\n")

    lines = []
    for line in body.splitlines():
        if "08_cross_trait_transfer_considerations.md" in line:
            continue
        lines.append(line)
    return "\n".join(lines)


def _load_reference_file(filename: str) -> str:
    path = REFERENCE_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Skill reference file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def _included_reference_files(arm: str) -> list[str]:
    if arm == "no-skill":
        return []
    removed = ARM_TO_REMOVED_FILE[arm]
    return [name for name in SAME_TRAIT_REFERENCE_FILES if name != removed]


def _skill_text_for_arm(arm: str) -> str:
    if arm == "no-skill":
        return ""
    parts = [_load_skill_overview()]
    parts.extend(_load_reference_file(name) for name in _included_reference_files(arm))
    return "\n\n".join(part.strip() for part in parts if part.strip())


def _arm_metadata(arm: str) -> dict[str, Any]:
    included = _included_reference_files(arm)
    return {
        "arm": arm,
        "label": ARM_LABELS[arm],
        "skill_enabled": arm != "no-skill",
        "skill_overview_included": arm != "no-skill",
        "heritability_included": True,
        "removed_reference_file": ARM_TO_REMOVED_FILE[arm],
        "included_reference_files": included,
        "excluded_reference_files": [
            name for name in sorted(p.name for p in REFERENCE_DIR.glob("*.md"))
            if name not in included
        ],
        "snippets_cleared": True,
    }


def _ablation_archive_dir_name(
    arm: str,
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
    dataset_label: Optional[str] = None,
) -> str:
    safe_model = re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"skill-view-{arm}__{safe_model}-t{trials}"
    if dataset_label:
        base = f"{base}__{dataset_label}"
    safe_tag = re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _make_step1_context(arm: str):
    def _step1_context(
        ontology: str,
        candidate_models: list[Any],
        total_found: int,
    ) -> dict[str, Any]:
        query = with_domain._domain_query(ontology)
        heritability_records = get_heritability_records(ontology, ancestry="EUR")
        heritability_section = _format_heritability_section(ontology, heritability_records)
        skill_text = _skill_text_for_arm(arm)

        full_document_parts = []
        if heritability_section:
            full_document_parts.append(heritability_section)
        if skill_text:
            full_document_parts.append(skill_text)

        return {
            "target_trait": ontology,
            "direct_models": {
                "query_trait": ontology,
                "total_found": total_found,
                "after_filter": len(candidate_models),
                "models": [
                    without_domain._summarize_model_for_llm(model)
                    for model in candidate_models
                ],
            },
            "domain_knowledge": {
                "query": query,
                "full_document": "\n\n".join(full_document_parts),
                "snippets": [],
                "source_type": "skill_view_ablation",
            },
            "todo_recitation_path": "N/A",
            "todo_recitation": "",
        }

    return _step1_context


def _configure_for_arm(
    arm: str,
    model: str,
    trials: int,
    run_tag: Optional[str],
) -> Path:
    if arm not in ARM_TO_REMOVED_FILE:
        raise ValueError(f"Unknown arm: {arm}")

    os.environ["PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"] = "0"
    os.environ["PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"] = "0"
    os.environ["PENNPRS_CONTRIB2_STRICT_LLM_ONLY"] = "1"

    without_domain._model_name = lambda: model  # type: ignore[assignment]
    without_domain.RECOMMENDATION_RUNS = ABLATION_RUNS_DIR

    def _archive_dir_name_override(
        run_model: str,
        run_trials: int,
        run_tag: Optional[str] = None,
        dataset_label: Optional[str] = None,
    ) -> str:
        return _ablation_archive_dir_name(
            arm,
            run_model,
            run_trials,
            run_tag=run_tag,
            dataset_label=dataset_label,
        )

    without_domain._archive_dir_name = _archive_dir_name_override  # type: ignore[assignment]
    without_domain._step1_context = _make_step1_context(arm)  # type: ignore[assignment]
    without_domain._step1_messages = with_domain._ORIGINAL_STEP1_MESSAGES  # type: ignore[assignment]

    original_prepare_manifest = with_domain._ORIGINAL_PREPARE_MANIFEST

    def _prepare_manifest_override(
        limit: Optional[int],
        trials: int,
        refresh_cache: bool = False,
        ontology_filter: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        manifest = original_prepare_manifest(
            limit=limit,
            trials=trials,
            refresh_cache=refresh_cache,
            ontology_filter=ontology_filter,
        )
        manifest["experiment"] = f"skill_view_ablation_{arm}"
        manifest["domain_knowledge"] = True
        manifest["model"] = model
        manifest["skill_view_ablation"] = _arm_metadata(arm)
        return manifest

    without_domain._prepare_manifest = _prepare_manifest_override  # type: ignore[assignment]

    without_domain._set_run_paths(trials=trials, model=model, run_tag=run_tag)
    run_dir = without_domain.ACTIVE_RUN_DIR
    if run_dir is None:
        raise RuntimeError("Run directory was not configured.")

    without_domain.RESULTS_JSON = run_dir / "experiment_skill_view_ablation_results.json"
    without_domain.SUMMARY_JSON = run_dir / "experiment_skill_view_ablation_summary.json"
    without_domain.REPORT_MD = run_dir / "experiment_skill_view_ablation_report.md"
    without_domain.BATCH_REQUESTS_JSONL = run_dir / "experiment_skill_view_ablation_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = run_dir / "experiment_skill_view_ablation_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = run_dir / "experiment_skill_view_ablation_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = run_dir / "experiment_skill_view_ablation_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = run_dir / "experiment_skill_view_ablation_batch_errors.jsonl"
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

    return run_dir


def _submit_batch(arm: str) -> dict[str, Any]:
    if not without_domain.BATCH_REQUESTS_JSONL.exists():
        raise FileNotFoundError(f"Batch requests not found: {without_domain.BATCH_REQUESTS_JSONL}")
    if not without_domain.BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(f"Batch manifest not found: {without_domain.BATCH_MANIFEST_JSON}")

    client = without_domain._client()
    with without_domain.BATCH_REQUESTS_JSONL.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "experiment": f"skill_view_ablation_{arm}",
            "manifest_file": without_domain.BATCH_MANIFEST_JSON.name,
        },
    )
    job = {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "request_file": str(without_domain.BATCH_REQUESTS_JSONL),
        "manifest_file": str(without_domain.BATCH_MANIFEST_JSON),
        "status": batch.status,
        "batch": batch.model_dump(),
    }
    without_domain._write_json(without_domain.BATCH_JOB_JSON, job)
    print(f"Uploaded batch input file: {uploaded.id}")
    print(f"Created batch job: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Saved job metadata: {without_domain.BATCH_JOB_JSON}")
    return job


def _status(batch_id: Optional[str]) -> dict[str, Any]:
    if batch_id:
        job = {"batch_id": batch_id}
    else:
        if not without_domain.BATCH_JOB_JSON.exists():
            raise FileNotFoundError(
                f"Batch job file not found: {without_domain.BATCH_JOB_JSON}."
            )
        job = without_domain._load_json(without_domain.BATCH_JOB_JSON)

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
    without_domain._write_json(without_domain.BATCH_JOB_JSON, payload)
    print(json.dumps(payload, indent=2))
    return payload


def _build_summary_and_results(
    arm: str,
    manifest: dict[str, Any],
    parsed_outputs: dict[str, dict[str, Any]],
    error_map: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trial_results, summary = without_domain._build_summary_and_results(
        manifest,
        parsed_outputs,
        error_map,
    )
    summary["experiment"] = f"skill_view_ablation_{arm}"
    summary["domain_knowledge"] = True
    summary["model"] = manifest.get("model", DEFAULT_MODEL)
    summary["skill_view_ablation"] = manifest.get("skill_view_ablation", _arm_metadata(arm))
    return trial_results, summary


def _write_report(summary: dict[str, Any]) -> None:
    arm = summary.get("skill_view_ablation", {}).get("arm", "unknown")
    label = summary.get("skill_view_ablation", {}).get("label", arm)
    modal_hit = summary.get("modal_hit_at_k", {})
    trial_hit = summary.get("trial_hit_at_k", {})
    nrs = summary.get("nrs", {})
    cost = summary.get("cost", {})

    lines = [
        f"# Skill-view Ablation Report: {arm}",
        "",
        "## Setup",
        "",
        f"- **Arm**: `{arm}`",
        f"- **Label**: {label}",
        f"- **Model**: {summary.get('model', 'unknown')}",
        f"- **Total ontologies**: {summary.get('total_ontologies', 'unknown')}",
        f"- **Trials per ontology**: {summary.get('trials_per_ontology', 'unknown')}",
        f"- **Union CSV**: `{summary.get('union_csv', 'unknown')}`",
        f"- **Ground truth dir**: `{summary.get('ground_truth_dir', 'unknown')}`",
        "",
        "## Results",
        "",
        "| Metric | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    def _pct(obj: dict[str, Any], k: int) -> str:
        acc = obj.get(str(k), {}).get("accuracy")
        if acc is None:
            return "N/A"
        return f"{float(acc) * 100:.1f}%"

    lines.append("| Modal | " + " | ".join(_pct(modal_hit, k) for k in range(1, 6)) + " |")
    lines.append("| Trial | " + " | ".join(_pct(trial_hit, k) for k in range(1, 6)) + " |")
    if nrs.get("modal_mean_nrs") is not None:
        lines.extend(["", f"**Modal NRS**: {float(nrs['modal_mean_nrs']):.4f}"])
    if cost.get("estimated_total_cost_usd") is not None:
        lines.extend(["", f"**Batch cost**: ${float(cost['estimated_total_cost_usd']):.4f}"])
    lines.append("")

    without_domain.REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def _collect(arm: str, batch_id: Optional[str]) -> dict[str, Any]:
    if not without_domain.BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(
            f"Batch manifest not found: {without_domain.BATCH_MANIFEST_JSON}."
        )

    manifest = without_domain._load_json(without_domain.BATCH_MANIFEST_JSON)
    job = without_domain._load_job(batch_id=batch_id)
    client = without_domain._client()
    batch = client.batches.retrieve(job["batch_id"])

    if batch.status != "completed":
        raise RuntimeError(f"Batch {batch.id} is not completed yet (status={batch.status}).")
    if not batch.output_file_id:
        raise RuntimeError(f"Batch {batch.id} completed without output_file_id.")

    raw_output_jsonl = client.files.retrieve_content(batch.output_file_id)
    without_domain.BATCH_OUTPUT_JSONL.write_text(raw_output_jsonl, encoding="utf-8")

    raw_error_jsonl = ""
    if batch.error_file_id:
        raw_error_jsonl = client.files.retrieve_content(batch.error_file_id)
        without_domain.BATCH_ERROR_JSONL.write_text(raw_error_jsonl, encoding="utf-8")

    parsed_outputs: dict[str, dict[str, Any]] = {}
    for line in raw_output_jsonl.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        parsed = without_domain._parse_batch_output_line(record)
        parsed_outputs[parsed["custom_id"]] = parsed

    error_map = without_domain._parse_error_file(raw_error_jsonl) if raw_error_jsonl else {}
    trial_results, summary = _build_summary_and_results(arm, manifest, parsed_outputs, error_map)
    summary["cost"] = without_domain._estimate_batch_cost(batch.model_dump())

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    _write_report(summary)
    archive_dir = without_domain._archive_current_outputs(summary=summary)

    job_payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
        "batch": batch.model_dump(),
        "manifest_file": str(without_domain.BATCH_MANIFEST_JSON),
        "output_jsonl_file": str(without_domain.BATCH_OUTPUT_JSONL),
        "error_jsonl_file": str(without_domain.BATCH_ERROR_JSONL) if batch.error_file_id else None,
    }
    without_domain._write_json(without_domain.BATCH_JOB_JSON, job_payload)

    print(f"Collected batch output: {without_domain.BATCH_OUTPUT_JSONL}")
    print(f"Results: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    print(f"Report:  {without_domain.REPORT_MD}")
    print(f"Archive: {archive_dir}")
    return summary


def _run_arm(
    arm: str,
    mode: str,
    model: str,
    trials: int,
    limit: Optional[int],
    batch_id: Optional[str],
    refresh_cache: bool,
    ontology_filter: Optional[set[str]],
    run_tag: Optional[str],
) -> int:
    print(f"\n{'=' * 72}")
    print(f"SKILL-VIEW ABLATION ARM: {arm}")
    print(f"MODE: {mode}")
    print(f"{'=' * 72}")

    try:
        run_dir = _configure_for_arm(arm, model=model, trials=trials, run_tag=run_tag)
        print(f"Run directory: {run_dir}")
        print(f"Arm metadata: {json.dumps(_arm_metadata(arm), indent=2)}")

        if mode == "prepare":
            without_domain._prepare(
                limit=limit,
                trials=trials,
                refresh_cache=refresh_cache,
                ontology_filter=ontology_filter,
            )
        elif mode == "prepare-submit":
            without_domain._prepare(
                limit=limit,
                trials=trials,
                refresh_cache=refresh_cache,
                ontology_filter=ontology_filter,
            )
            _submit_batch(arm)
        elif mode == "status":
            _status(batch_id=batch_id)
        elif mode == "collect":
            _collect(arm=arm, batch_id=batch_id)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
    except Exception as exc:
        print(f"ERROR [{arm}]: {type(exc).__name__}: {exc}")
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run packaged PRS Model Skill-view ablations")
    parser.add_argument("--arm", type=str, default=None, help="Ablation arm to run")
    parser.add_argument("--all", action="store_true", help="Run all arms")
    parser.add_argument(
        "--mode",
        choices=["prepare", "prepare-submit", "status", "collect"],
        default="prepare-submit",
    )
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-id", type=str, default=None)
    parser.add_argument("--ontology", action="append", default=None)
    parser.add_argument("--ontologies-file", type=str, default=str(DEFAULT_ONTOLOGIES_FILE))
    parser.add_argument("--run-tag", type=str, default=None)
    parser.add_argument("--union-csv", type=str, default=str(DEFAULT_UNION_CSV))
    parser.add_argument("--ground-truth-dir", type=str, default=str(DEFAULT_GROUND_TRUTH_DIR))
    parser.add_argument("--refresh-cache", action="store_true")
    args = parser.parse_args()

    if not args.arm and not args.all:
        parser.error("Either --arm or --all is required.")
    if args.arm and args.all:
        parser.error("--arm and --all are mutually exclusive.")
    if args.arm and args.arm not in ARM_TO_REMOVED_FILE:
        parser.error(f"Unknown --arm {args.arm!r}. Valid arms: {sorted(ARM_TO_REMOVED_FILE)}")
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    ontology_filter = without_domain._load_ontology_filter(args.ontology, args.ontologies_file)
    without_domain._configure_benchmark_sources(
        union_csv=args.union_csv,
        ground_truth_dir=args.ground_truth_dir,
    )

    arms = list(ARM_TO_REMOVED_FILE) if args.all else [args.arm]
    results: list[tuple[str, int]] = []
    for arm in arms:
        rc = _run_arm(
            arm=arm,
            mode=args.mode,
            model=args.model,
            trials=args.trials,
            limit=args.limit,
            batch_id=args.batch_id,
            refresh_cache=args.refresh_cache,
            ontology_filter=ontology_filter,
            run_tag=args.run_tag,
        )
        results.append((arm, rc))

    if len(results) > 1:
        print(f"\n{'=' * 72}")
        print("SKILL-VIEW ABLATION SUMMARY")
        print(f"{'=' * 72}")
        for arm, rc in results:
            print(f"  {arm}: {'OK' if rc == 0 else 'FAILED'}")

    return 1 if any(rc != 0 for _, rc in results) else 0


if __name__ == "__main__":
    sys.exit(main())
