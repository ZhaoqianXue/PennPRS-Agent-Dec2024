"""c2 evidence-bootstrap harness: production-equivalent Skill + h2 wrapper.

This runner is intentionally close to `run_experiment_minimal_lift.py`.
The point is not to invent a new decision workflow; it is to repackage the
existing same-trait PGS-selection task as an explicit harness-engineering
artifact while preserving the evidence shape that made iterD-final work.

Architecture:
  - EvidenceBootstrap calls the two c2 evidence capabilities:
      1. read_skill_section("full_c2_reference")
      2. get_heritability_records(target_trait)
  - The harness formats those observations into the same Step 1 context shape
    consumed by the existing production batch infrastructure.
  - The LLM still makes the PGS choice in one JSON-schema call. The harness
    does not score, rank, veto, or substitute candidate IDs.

This is a workflow harness, not a ReAct experiment. It is the lowest-risk
bridge from c2's fixed workflow into the 2026 "agent = model + harness"
framing before adding optional agentic refinement.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as wd
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from experiments.contribution2.recommendation.scripts.run_experiment_minimal_lift import (
    _format_heritability_section,
)
from src.server.core.tools.heritability import get_heritability_records
from src.server.core.tools.prs_model_evaluator_skill import REFERENCE_DIR, SKILL_DIR, load_c2_view
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge


SKILL_VIEW = os.getenv("C2_HARNESS_SKILL_VIEW", "full_c2_reference").strip() or "full_c2_reference"


def read_skill_section(section_name: str) -> str:
    """Harness-facing Skill reader for c2's production-equivalent corpus.

    The allowed ReAct tool name is `read_skill_section`; this bootstrap harness
    uses the same conceptual interface, but deterministically requests a c2
    Skill view so evidence is not fragmented. The returned text is assembled
    only from the sealed prs_model_evaluator SKILL.md / reference/*.md files.
    """
    if section_name == "full_c2_reference":
        return load_c2_view()
    if section_name == "same_trait_reference":
        return "".join(
            path.read_text(encoding="utf-8")
            for path in sorted(REFERENCE_DIR.glob("*.md"))
            if not path.name.startswith("08_cross_trait_transfer")
        )
    if section_name == "skill_overview_same_trait_reference":
        parts = [
            (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"),
            read_skill_section("same_trait_reference"),
        ]
        return "\n\n".join(part.strip() for part in parts if part.strip())
    if section_name == "skill_overview_full_c2_reference":
        parts = [
            (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"),
            read_skill_section("full_c2_reference"),
        ]
        return "\n\n".join(part.strip() for part in parts if part.strip())
    if section_name != "full_c2_reference":
        return (
            f"ERROR: unknown c2 harness skill section {section_name!r}. "
            "Valid section_names: full_c2_reference, same_trait_reference, "
            "skill_overview_same_trait_reference, skill_overview_full_c2_reference."
        )
    return load_c2_view()


def _step1_context(
    ontology: str,
    candidate_models: list[Any],
    total_found: int,
) -> dict[str, Any]:
    """Build the production-equivalent Step 1 context via harness tools."""
    query = wd._domain_query(ontology)
    base_domain = prs_model_domain_knowledge(query, max_snippets=8).model_dump()

    skill_reference = read_skill_section(SKILL_VIEW).strip()
    if skill_reference.startswith("ERROR:"):
        raise ValueError(skill_reference)
    heritability_records = get_heritability_records(ontology, ancestry="EUR")
    heritability_section = _format_heritability_section(ontology, heritability_records)

    parts: list[str] = []
    if heritability_section:
        parts.append(heritability_section)
    if skill_reference:
        parts.append(skill_reference)
    full_document = "\n\n".join(parts) if parts else ""

    return {
        "target_trait": ontology,
        "direct_models": {
            "query_trait": ontology,
            "total_found": total_found,
            "after_filter": len(candidate_models),
            "models": [without_domain._summarize_model_for_llm(m) for m in candidate_models],
        },
        "domain_knowledge": {
            "query": base_domain.get("query"),
            "full_document": full_document,
            "snippets": base_domain.get("snippets", []),
            "source_type": base_domain.get("source_type", "local"),
        },
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


def _archive_dir_name(
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
    dataset_label: Optional[str] = None,
) -> str:
    safe_model = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"agent-harness-lift-{safe_model}-t{trials}"
    if dataset_label:
        base = f"{base}__{dataset_label}"
    safe_tag = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _set_artifact_paths() -> None:
    if without_domain.ACTIVE_RUN_DIR is None:
        raise RuntimeError("Run directory is not configured.")
    rd = without_domain.ACTIVE_RUN_DIR
    without_domain.RESULTS_JSON = rd / "experiment_agent_harness_lift_results.json"
    without_domain.SUMMARY_JSON = rd / "experiment_agent_harness_lift_summary.json"
    without_domain.REPORT_MD = rd / "experiment_agent_harness_lift_report.md"
    without_domain.BATCH_REQUESTS_JSONL = rd / "experiment_agent_harness_lift_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = rd / "experiment_agent_harness_lift_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = rd / "experiment_agent_harness_lift_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = rd / "experiment_agent_harness_lift_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = rd / "experiment_agent_harness_lift_batch_errors.jsonl"
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
    wd.RESULTS_JSON = without_domain.RESULTS_JSON
    wd.SUMMARY_JSON = without_domain.SUMMARY_JSON
    wd.REPORT_MD = without_domain.REPORT_MD
    wd.BATCH_REQUESTS_JSONL = without_domain.BATCH_REQUESTS_JSONL
    wd.BATCH_MANIFEST_JSON = without_domain.BATCH_MANIFEST_JSON
    wd.BATCH_JOB_JSON = without_domain.BATCH_JOB_JSON
    wd.BATCH_OUTPUT_JSONL = without_domain.BATCH_OUTPUT_JSONL
    wd.BATCH_ERROR_JSONL = without_domain.BATCH_ERROR_JSONL


_ORIGINAL_PREPARE_MANIFEST = wd._prepare_manifest


def _patched_prepare_manifest(
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
    manifest["experiment"] = "agent_harness_lift"
    manifest["domain_knowledge"] = True
    manifest["harness_engineering"] = {
        "type": "evidence_bootstrap_workflow_harness",
        "skill_tool": f"read_skill_section({SKILL_VIEW})",
        "heritability_tool": "get_heritability_records",
        "candidate_selection": "single LLM JSON-schema Step1",
        "no_harness_scoring": True,
    }
    return manifest


wd._step1_context = _step1_context
wd._domain_archive_dir_name = _archive_dir_name
wd._set_domain_artifact_paths = _set_artifact_paths
wd._prepare_manifest = _patched_prepare_manifest


if __name__ == "__main__":
    sys.exit(wd.main())
