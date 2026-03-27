"""
Domain Knowledge Ablation Experiment runner.

For each ablation variant (a copy of prs_model_domain_knowledge.md with one
## section removed), this script runs the same Contribution2 with-domain
experiment pipeline, routing outputs to experiments/contribution2/ablation/runs/.

It reuses the existing with-domain / without-domain batch infrastructure via
monkey-patching, overriding only the knowledge_file path used by
prs_model_domain_knowledge().

Usage:
    # Run a single variant
    python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
        --variant no-section5 --mode prepare-submit --trials 10

    # Run all variants sequentially (each submits its own batch job)
    python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
        --all --mode prepare-submit --trials 10

    # Check status for a variant
    python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
        --variant no-section5 --mode status

    # Collect results for all completed variants
    python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
        --all --mode collect
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

ABLATION_DIR = Path(__file__).resolve().parent.parent
VARIANTS_DIR = ABLATION_DIR / "variants"
ABLATION_RUNS_DIR = ABLATION_DIR / "runs"
MANIFEST_JSON = VARIANTS_DIR / "manifest.json"

# Import the recommendation experiment modules
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as with_domain
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

DEFAULT_MODEL = "gpt-5.2"
RECOMMENDATION_RUNS = with_domain.RECOMMENDATION_RUNS


def _load_variant_manifest() -> list[dict[str, Any]]:
    if not MANIFEST_JSON.exists():
        raise FileNotFoundError(
            f"Variant manifest not found: {MANIFEST_JSON}. "
            "Run generate_ablation_variants.py first."
        )
    return json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))


def _variant_knowledge_file(variant_id: str) -> Path:
    return VARIANTS_DIR / f"{variant_id}.md"


def _ablation_archive_dir_name(
    variant_id: str,
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
    dataset_label: Optional[str] = None,
) -> str:
    import re as _re
    safe_model = _re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"ablation-{variant_id}__{safe_model}-t{trials}"
    if dataset_label:
        base = f"{base}__{dataset_label}"
    safe_tag = _re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _make_step1_context(knowledge_file: str):
    """Create a _step1_context function that uses the specified knowledge file."""
    def _step1_context(
        ontology: str,
        candidate_models: list[Any],
        total_found: int,
    ) -> dict[str, Any]:
        query = with_domain._domain_query(ontology)
        domain = prs_model_domain_knowledge(
            query, knowledge_file=knowledge_file, max_snippets=8
        ).model_dump()
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
            "domain_knowledge": domain,
            "todo_recitation_path": "N/A",
            "todo_recitation": "",
        }
    return _step1_context


def _configure_for_variant(
    variant_id: str,
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
) -> Path:
    """Configure the without_domain module for an ablation variant run."""
    knowledge_file = _variant_knowledge_file(variant_id)
    if not knowledge_file.exists():
        raise FileNotFoundError(
            f"Variant knowledge file not found: {knowledge_file}. "
            "Run generate_ablation_variants.py first."
        )

    # Enable domain knowledge
    os.environ["PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"] = "0"
    os.environ["PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"] = "0"
    os.environ["PENNPRS_CONTRIB2_STRICT_LLM_ONLY"] = "1"

    # Override model name
    without_domain._model_name = lambda: model  # type: ignore[assignment]

    # Override archive dir name to route to ablation runs dir
    dataset_label = without_domain.ACTIVE_BENCHMARK_LABEL

    def _archive_dir_name_override(
        m: str,
        t: int,
        run_tag: Optional[str] = None,
        dataset_label: Optional[str] = None,
    ) -> str:
        return _ablation_archive_dir_name(
            variant_id,
            m,
            t,
            run_tag=run_tag,
            dataset_label=dataset_label,
        )

    without_domain._archive_dir_name = _archive_dir_name_override  # type: ignore[assignment]

    # Override RECOMMENDATION_RUNS to point to ablation runs dir
    without_domain.RECOMMENDATION_RUNS = ABLATION_RUNS_DIR

    # Override step1 context and messages
    without_domain._step1_context = _make_step1_context(str(knowledge_file))  # type: ignore[assignment]
    without_domain._step1_messages = with_domain._ORIGINAL_STEP1_MESSAGES  # type: ignore[assignment]

    # Override prepare_manifest to tag as ablation
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
        manifest["experiment"] = f"ablation_{variant_id}"
        manifest["domain_knowledge"] = True
        manifest["ablation_variant"] = variant_id
        manifest["knowledge_file"] = str(knowledge_file)
        manifest["model"] = model
        return manifest

    without_domain._prepare_manifest = _prepare_manifest_override  # type: ignore[assignment]

    # Set run paths
    without_domain._set_run_paths(trials=trials, model=model, run_tag=run_tag)

    # Override artifact filenames to use ablation prefix
    run_dir = without_domain.ACTIVE_RUN_DIR
    without_domain.RESULTS_JSON = run_dir / "experiment_ablation_results.json"
    without_domain.SUMMARY_JSON = run_dir / "experiment_ablation_summary.json"
    without_domain.REPORT_MD = run_dir / "experiment_ablation_report.md"
    without_domain.BATCH_REQUESTS_JSONL = run_dir / "experiment_ablation_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = run_dir / "experiment_ablation_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = run_dir / "experiment_ablation_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = run_dir / "experiment_ablation_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = run_dir / "experiment_ablation_batch_errors.jsonl"
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

    # Sync with_domain path references
    with_domain.RESULTS_JSON = without_domain.RESULTS_JSON
    with_domain.SUMMARY_JSON = without_domain.SUMMARY_JSON
    with_domain.REPORT_MD = without_domain.REPORT_MD
    with_domain.BATCH_REQUESTS_JSONL = without_domain.BATCH_REQUESTS_JSONL
    with_domain.BATCH_MANIFEST_JSON = without_domain.BATCH_MANIFEST_JSON
    with_domain.BATCH_JOB_JSON = without_domain.BATCH_JOB_JSON
    with_domain.BATCH_OUTPUT_JSONL = without_domain.BATCH_OUTPUT_JSONL
    with_domain.BATCH_ERROR_JSONL = without_domain.BATCH_ERROR_JSONL

    print(f"Configured ablation variant: {variant_id}")
    print(f"  Knowledge file: {knowledge_file}")
    print(f"  Run directory:  {run_dir}")
    return run_dir


def _build_summary_and_results(
    manifest: dict[str, Any],
    parsed_outputs: dict[str, dict[str, Any]],
    error_map: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trial_results, summary = without_domain._build_summary_and_results(
        manifest, parsed_outputs, error_map
    )
    summary["experiment"] = manifest.get("experiment", "ablation")
    summary["domain_knowledge"] = True
    summary["ablation_variant"] = manifest.get("ablation_variant", "unknown")
    summary["knowledge_file"] = manifest.get("knowledge_file", "unknown")
    summary["model"] = manifest.get("model", DEFAULT_MODEL)
    return trial_results, summary


def _submit_batch(variant_id: str) -> dict[str, Any]:
    """Submit a batch job for the configured variant."""
    batch_requests = without_domain.BATCH_REQUESTS_JSONL
    batch_manifest = without_domain.BATCH_MANIFEST_JSON
    batch_job_json = without_domain.BATCH_JOB_JSON

    if not batch_requests.exists():
        raise FileNotFoundError(f"Batch requests not found: {batch_requests}")
    if not batch_manifest.exists():
        raise FileNotFoundError(f"Batch manifest not found: {batch_manifest}")

    client = without_domain._client()
    with batch_requests.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "experiment": f"contribution2_ablation_{variant_id}",
            "manifest_file": batch_manifest.name,
        },
    )
    job = {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "request_file": str(batch_requests),
        "manifest_file": str(batch_manifest),
        "status": batch.status,
        "batch": batch.model_dump(),
    }
    without_domain._write_json(batch_job_json, job)
    print(f"Uploaded batch input file: {uploaded.id}")
    print(f"Created batch job: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Saved job metadata: {batch_job_json}")
    return job


def _status(batch_id: Optional[str]) -> dict[str, Any]:
    batch_job_json = without_domain.BATCH_JOB_JSON
    if batch_id:
        job = {"batch_id": batch_id}
    else:
        if not batch_job_json.exists():
            raise FileNotFoundError(
                f"Batch job file not found: {batch_job_json}. "
                "Run with --mode prepare-submit first."
            )
        job = without_domain._load_json(batch_job_json)

    client = without_domain._client()
    batch = client.batches.retrieve(job["batch_id"])
    payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
    }
    print(json.dumps(payload, indent=2))
    return payload


def _collect(variant_id: str, batch_id: Optional[str]) -> dict[str, Any]:
    batch_manifest = without_domain.BATCH_MANIFEST_JSON
    batch_job_json = without_domain.BATCH_JOB_JSON

    if not batch_manifest.exists():
        raise FileNotFoundError(
            f"Batch manifest not found: {batch_manifest}. "
            "Run with --mode prepare or --mode prepare-submit first."
        )

    manifest = without_domain._load_json(batch_manifest)
    job = without_domain._load_job(batch_id=batch_id)
    client = without_domain._client()
    batch = client.batches.retrieve(job["batch_id"])

    if batch.status != "completed":
        raise RuntimeError(
            f"Batch {batch.id} is not completed yet (status={batch.status}). "
            "Run --mode status and retry later."
        )
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
    trial_results, summary = _build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["cost"] = without_domain._estimate_batch_cost(batch.model_dump())

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    _write_ablation_report(summary)
    archive_dir = without_domain._archive_current_outputs(summary=summary)

    job_payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
        "batch": batch.model_dump(),
        "manifest_file": str(batch_manifest),
        "output_jsonl_file": str(without_domain.BATCH_OUTPUT_JSONL),
        "error_jsonl_file": str(without_domain.BATCH_ERROR_JSONL) if batch.error_file_id else None,
    }
    without_domain._write_json(batch_job_json, job_payload)

    print(f"Collected batch output: {without_domain.BATCH_OUTPUT_JSONL}")
    if batch.error_file_id:
        print(f"Collected batch errors: {without_domain.BATCH_ERROR_JSONL}")
    print(f"Results: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    print(f"Report:  {without_domain.REPORT_MD}")
    print(f"Archive: {archive_dir}")
    return summary


def _write_ablation_report(summary: dict[str, Any]) -> None:
    """Write a minimal Markdown report for a single ablation variant."""
    variant_id = summary.get("ablation_variant", "unknown")
    knowledge_file = summary.get("knowledge_file", "unknown")
    model = summary.get("model", "unknown")

    lines: list[str] = []
    lines.append(f"# Ablation Experiment Report: {variant_id}")
    lines.append("")
    lines.append("## Experiment Setup")
    lines.append("")
    lines.append(f"- **Ablation variant**: `{variant_id}`")
    lines.append(f"- **Knowledge file**: `{knowledge_file}`")
    lines.append(f"- **Model**: {model}")
    lines.append(f"- **Domain Knowledge**: Enabled (ablated variant)")
    lines.append("")

    # Overall metrics — actual summary uses modal_hit_at_k / trial_hit_at_k / nrs
    modal_hit = summary.get("modal_hit_at_k", {})
    trial_hit = summary.get("trial_hit_at_k", {})
    nrs_obj = summary.get("nrs", {})

    lines.append("## Overall Results")
    lines.append("")
    lines.append("| Metric | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |")
    lines.append("|--------|-------|-------|-------|-------|-------|")

    def _fmt_pct(v: Any) -> str:
        if v is None:
            return "N/A"
        return f"{float(v) * 100:.1f}%"

    modal_row = "| Modal Hit Rate |"
    trial_row = "| Trial Hit Rate |"
    for k in range(1, 6):
        modal_acc = modal_hit.get(str(k), {}).get("accuracy")
        trial_acc = trial_hit.get(str(k), {}).get("accuracy")
        modal_row += f" {_fmt_pct(modal_acc)} |"
        trial_row += f" {_fmt_pct(trial_acc)} |"
    lines.append(modal_row)
    lines.append(trial_row)
    lines.append("")
    modal_nrs = nrs_obj.get("modal_mean_nrs")
    if modal_nrs is not None:
        lines.append(f"**Normalized Ranking Score (NRS)**: {float(modal_nrs):.4f}")
        lines.append("")

    # Per-disease summary — per_disease is a list of dicts with "ontology" key
    per_disease = summary.get("per_disease", [])
    if per_disease:
        lines.append("## Per-Disease Results")
        lines.append("")
        lines.append("| Disease | Modal PGS ID | Selection Freq | Hit@1 | Hit@3 | Hit@5 |")
        lines.append("|---------|-------------|----------------|-------|-------|-------|")
        for entry in sorted(per_disease, key=lambda e: e.get("ontology", "")):
            ontology = entry.get("ontology", "N/A")
            modal_id = entry.get("modal_recommendation", "N/A")
            modal_count = entry.get("modal_recommendation_count", 0)
            total_trials = summary.get("trials_per_ontology", 10)
            freq = f"{modal_count}/{total_trials}"
            modal_hits = entry.get("modal_recommendation_hit_at_k", {})
            h1 = "Y" if modal_hits.get("1") else "N"
            h3 = "Y" if modal_hits.get("3") else "N"
            h5 = "Y" if modal_hits.get("5") else "N"
            lines.append(f"| {ontology} | {modal_id} | {freq} | {h1} | {h3} | {h5} |")
        lines.append("")

    # Cost
    cost = summary.get("cost", {})
    if cost:
        lines.append("## Cost")
        lines.append("")
        total = cost.get("total_cost_usd")
        if total is not None:
            lines.append(f"- **Total cost**: ${float(total):.4f}")
        lines.append("")

    report_md = without_domain.REPORT_MD
    report_md.write_text("\n".join(lines), encoding="utf-8")


def _run_variant(
    variant_id: str,
    mode: str,
    model: str,
    trials: int,
    limit: Optional[int],
    batch_id: Optional[str],
    refresh_cache: bool,
    ontology_filter: Optional[set[str]],
    run_tag: Optional[str],
) -> int:
    """Execute one mode for one variant. Returns 0 on success, 1 on error."""
    print(f"\n{'='*60}")
    print(f"ABLATION VARIANT: {variant_id}")
    print(f"MODE: {mode}")
    print(f"{'='*60}")

    try:
        _configure_for_variant(
            variant_id=variant_id,
            model=model,
            trials=trials,
            run_tag=run_tag,
        )

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
            _submit_batch(variant_id)
        elif mode == "status":
            _status(batch_id=batch_id)
        elif mode == "collect":
            _collect(variant_id=variant_id, batch_id=batch_id)
        else:
            print(f"ERROR: unsupported mode: {mode}")
            return 1

    except Exception as exc:
        print(f"ERROR [{variant_id}]: {type(exc).__name__}: {exc}")
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Domain Knowledge Ablation Experiment runner"
    )
    parser.add_argument(
        "--variant",
        type=str,
        default=None,
        help="Variant ID to run (e.g. no-section5). Required unless --all is set.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all variants from the manifest sequentially.",
    )
    parser.add_argument(
        "--mode",
        choices=["prepare", "prepare-submit", "status", "collect"],
        default="prepare-submit",
        help="Batch workflow step (default: prepare-submit)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Prepare only the first N ontologies for debugging")
    parser.add_argument("--trials", type=int, default=10, help="Number of repeated trials per ontology (default: 10)")
    parser.add_argument("--batch-id", type=str, default=None, help="Optional batch ID override for status/collect")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"OpenAI model (default: {DEFAULT_MODEL})")
    parser.add_argument("--ontology", action="append", default=None, help="Run only the specified ontology (repeatable)")
    parser.add_argument("--ontologies-file", type=str, default=None, help="Path to a newline-delimited ontology filter file")
    parser.add_argument("--run-tag", type=str, default=None, help="Optional tag appended to the run directory name")
    parser.add_argument(
        "--union-csv",
        type=str,
        default=str(without_domain.DEFAULT_UNION_CSV),
        help="Disease union CSV (default: frozen 30-disease union).",
    )
    parser.add_argument(
        "--ground-truth-dir",
        type=str,
        default=None,
        help="Ground-truth directory produced by generate_evaluated_pgs_list.py.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore experiment-local prepare cache and refetch candidate metadata",
    )
    args = parser.parse_args()

    if not args.variant and not args.all:
        parser.error("Either --variant or --all is required.")
    if args.variant and args.all:
        parser.error("--variant and --all are mutually exclusive.")

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    # Configure benchmark sources (shared across all variants)
    ontology_filter = without_domain._load_ontology_filter(args.ontology, args.ontologies_file)
    without_domain._configure_benchmark_sources(
        union_csv=args.union_csv,
        ground_truth_dir=args.ground_truth_dir,
    )

    # Determine which variants to run
    if args.all:
        manifest_entries = _load_variant_manifest()
        variant_ids = [entry["variant_id"] for entry in manifest_entries]
    else:
        variant_ids = [args.variant]
        # Validate variant exists
        kf = _variant_knowledge_file(args.variant)
        if not kf.exists():
            print(f"ERROR: Variant file not found: {kf}")
            print(f"Available variants: {[f.stem for f in sorted(VARIANTS_DIR.glob('*.md'))]}")
            return 1

    results: list[tuple[str, int]] = []
    for variant_id in variant_ids:
        rc = _run_variant(
            variant_id=variant_id,
            mode=args.mode,
            model=args.model,
            trials=args.trials,
            limit=args.limit,
            batch_id=args.batch_id,
            refresh_cache=args.refresh_cache,
            ontology_filter=ontology_filter,
            run_tag=args.run_tag,
        )
        results.append((variant_id, rc))

    # Summary
    if len(results) > 1:
        print(f"\n{'='*60}")
        print("ABLATION BATCH SUMMARY")
        print(f"{'='*60}")
        for variant_id, rc in results:
            status = "OK" if rc == 0 else "FAILED"
            print(f"  {variant_id}: {status}")
        failed = sum(1 for _, rc in results if rc != 0)
        print(f"\nTotal: {len(results)} variants, {len(results) - failed} OK, {failed} failed")

    return 1 if any(rc != 0 for _, rc in results) else 0


if __name__ == "__main__":
    sys.exit(main())
