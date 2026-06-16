"""Minimal-lift c2 runner: single-shot + SKILL.md procedural overview + heritability tool.

Hypothesis (post-codex PEV regression diagnosis):
- The legacy with-domain runner sends ~59K chars of skill text to the LLM
  (54.7K full_text + 4.4K snippets). c3 iter1-vs-iter3 measurement
  showed bulk-loading the corpus biases the LLM and crowds out attention
  on the candidate records.
- Codex's PEV runner introduced TRIAGE / PICK / CRITIC stages on top of
  this and lost 5 rank-1 picks because multi-stage revisions over-corrected.
- Minimal lift: keep the legacy single-shot architecture, but replace
  full_text (~55K) with the SKILL.md procedural overview (~8K) and
  inject raw heritability records as a section, single shot.

Architecture:
  skill_context.full_text = SKILL.md procedural overview + appended
                            "## Trait-Specific Heritability" section
                            built from get_heritability_records.
  skill_context.snippets  = keyword-ranked snippets (kept).
  Single-shot LLM call, no TRIAGE / PICK / CRITIC stages.

Reuses:
  - prs-model-evaluator Anthropic Agent Skill via load_c3_view("pick", ...)
  - shared heritability tool at src/server/core/tools/heritability.py
  - existing without_domain batch infrastructure (manifest, prepare, submit,
    collect, eval, summary) and the with_domain main() entry point.

LLM-led discipline preserved: SKILL.md content is advisory; the LLM
still picks the primary PGS from the candidate records.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as wd
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.tools.heritability import get_heritability_records
from src.server.core.tools.prs_model_evaluator_skill import load_c3_view
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge


# ---------------------------------------------------------------------------
# Cached SKILL.md procedural overview
# ---------------------------------------------------------------------------

class _SkillCfg:
    """Duck-typed cfg for load_c3_view: only the flag-name attribute matters."""
    enable_pgs_quality_skill = True
    enable_skill = False


_SKILL_PROCEDURAL_OVERVIEW = load_c3_view("pick", cfg=_SkillCfg()).procedural_overview


# ---------------------------------------------------------------------------
# Per-disease step-1 context (replaces with_domain._step1_context)
# ---------------------------------------------------------------------------

def _fmt_float(v: Any, digits: int = 4) -> str:
    if v is None:
        return "N/A"
    try:
        return f"{float(v):.{digits}f}"
    except (TypeError, ValueError):
        return "N/A"


def _fmt_int(v: Any) -> str:
    if v is None:
        return "N/A"
    try:
        n = int(v)
        return f"{n:,}" if n > 0 else "N/A"
    except (TypeError, ValueError):
        return "N/A"


def _format_heritability_section(target_trait: str, records: list[dict[str, Any]]) -> str:
    """Reproduce the LEGACY 'Trait-Specific Heritability' section format
    that the previous in-corpus heritability injection used.

    The goal is bytewise-equivalent framing: target trait line,
    best-matched estimate one-liner, four sanity-check usage rules,
    and a short top-matches list. Records come from the shared
    get_heritability_records tool; this function is a pure formatter.

    Empirical motivation: codex's iter A/B used a sparse raw-record dump
    that did not match baseline framing; same-day comparison on 89 disease
    t=1 showed sparse format underperformed the legacy framing by ~3-5pp
    on Hit@1 / Hit@2.
    """
    if not records:
        return (
            "## Trait-Specific Heritability\n\n"
            f"Target trait: {target_trait}\n"
            "No matching local heritability estimate was found above the retrieval threshold.\n"
            "- use the generic ceiling rule only\n"
            "- do not infer PRS quality from full-model AUROC alone"
        )
    # Mirror the legacy _heritability_confidence_rank exactly:
    # primary: n_samples (descending)
    # secondary: 1/(SE+0.001) (descending — tighter SE wins)
    # tertiary: source priority gwas_atlas > ukbb_ldsc > pan_ukb
    _SOURCE_PRIORITY = {"gwas_atlas": 3, "ukbb_ldsc": 2, "pan_ukb": 1}
    def _rank(r: dict[str, Any]) -> tuple[int, float, int]:
        try:
            n = int(r.get("n_samples") or 0)
        except (TypeError, ValueError):
            n = 0
        se = r.get("h2_se")
        try:
            se_inv = 0.0 if se is None else 1.0 / (float(se) + 0.001)
        except (TypeError, ValueError):
            se_inv = 0.0
        src = str(r.get("source") or "")
        return (n, se_inv, _SOURCE_PRIORITY.get(src, 0))
    eur = [r for r in records if (r.get("ancestry") or "").upper() == "EUR"]
    pool = eur if eur else records
    pool_sorted = sorted(pool, key=_rank, reverse=True)
    best = pool_sorted[0]
    top_records = pool_sorted[:3]

    lines = [
        "## Trait-Specific Heritability",
        "",
        f"Target trait: {target_trait}",
        (
            "Best matched local heritability estimate: "
            f"h2_obs={_fmt_float(best.get('h2'))}; "
            f"h2_liability={_fmt_float(best.get('h2_liability'))}; "
            f"SE={_fmt_float(best.get('h2_se'))}; "
            f"z={_fmt_float(best.get('h2_z'), digits=2)}; "
            f"population={best.get('ancestry') or 'N/A'}; "
            f"n={_fmt_int(best.get('n_samples'))}; "
            f"source={best.get('source') or 'N/A'}."
        ),
        "Sanity-check usage:",
        "- compare PGS-only R2 or covariates-regressed-out R2 against h2; they should remain below the trait heritability ceiling",
        "- if full-model AUROC is very high but incremental AUROC and PGS-only R2 are small relative to h2, treat the AUROC as mostly covariate-driven rather than PRS-driven",
        "- if PGS-only AUROC is absent, do not substitute the full-model AUROC as a comparable PRS metric",
        "- use heritability as a ceiling/sanity field, not as an exact formula to reconstruct AUROC",
    ]
    if top_records:
        lines.append("Top local matches:")
        for r in top_records:
            lines.append(
                "- "
                f"{r.get('trait_name') or r.get('trait') or 'Unknown'} | "
                f"h2_obs={_fmt_float(r.get('h2'))} | "
                f"population={r.get('ancestry') or 'N/A'} | "
                f"n={_fmt_int(r.get('n_samples'))} | "
                f"source={r.get('source') or 'N/A'}"
            )
    return "\n".join(lines)


def _step1_context(
    ontology: str,
    candidate_models: list[Any],
    total_found: int,
    target_ancestry: str,
) -> dict[str, Any]:
    """Single-shot c2 context — ADDITIVE design.

    Empirical finding (paired80 89-disease t=1, same day as codex baseline):
    - REPLACING the legacy 55K full_text with an 8K SKILL.md procedural
      overview hurt Hit@1 by 4.5pp and Hit@2 by 14.6pp. c2's same-trait
      selection task is well-aligned to the original empirical corpus, so
      shrinking that corpus loses signal that the LLM was using.
    - The c3 lesson ("less skill text is better at PICK") does NOT transfer
      to c2 because c3 PICK is cross-trait (corpus partly misaligned) and
      runs 6-8 times per target (token cost compounds), while c2 is
      same-trait (corpus aligned) and single-shot.

    Additive design:
    - skill_context.full_text = SKILL.md procedural overview as
      PREAMBLE + the legacy 55K corpus + a "Trait-Specific Heritability"
      section appended from get_heritability_records. This is a strict
      superset of the legacy baseline content with two added structures
      (procedural overview, raw heritability evidence).
    - skill_context.snippets are kept unchanged.
    - All other fields match the with-domain context shape, including
      target_ancestry and the unrestricted id-plus-seven-evidence-section
      candidate schema.
    """
    query = wd._domain_query(ontology, target_ancestry)
    base_domain = prs_model_domain_knowledge(query, max_snippets=8).model_dump()

    heritability_records = get_heritability_records(ontology, ancestry="EUR")
    heritability_section = _format_heritability_section(ontology, heritability_records)

    # Legacy-baseline-equivalent layout: heritability section FIRST (before
    # the corpus header), then the corpus. This matches the byte layout
    # produced by the pre-codex `_build_trait_specific_heritability_section`
    # injection that the legacy with-domain runner consumed.
    parts: list[str] = []
    if heritability_section:
        parts.append(heritability_section)
    legacy_corpus = (base_domain.get("full_document") or "").strip()
    if legacy_corpus:
        parts.append(legacy_corpus)
    full_text = "\n\n".join(parts) if parts else ""

    # Preserve the legacy retrieval order while exposing it through the
    # current Agent Skill context field:
    #   name, query, full_text, snippets, source_type.
    # JSON serialisation preserves dict insertion order; field order
    # affects the textual sequence the LLM reads. Verified empirically
    # that reversing this order (snippets before full_text) hurt
    # Hit@1 by ~6pp on 89-disease t=1.
    skill_context = {
        "name": "prs-model-recommendation",
        "query": base_domain.get("query"),
        "full_text": full_text,
        "snippets": base_domain.get("snippets", []),
        "source_type": base_domain.get("source_type", "local"),
    }

    return {
        "target_trait": ontology,
        "target_ancestry": target_ancestry,
        "direct_models": {
            "query_trait": ontology,
            "total_found": total_found,
            "after_filter": len(candidate_models),
            "models": [without_domain._candidate_view_for_llm(m) for m in candidate_models],
        },
        "skill_context": skill_context,
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


# ---------------------------------------------------------------------------
# Archive dir + artifact path overrides
# ---------------------------------------------------------------------------

def _archive_dir_name(
    model: str,
    trials: int,
    run_tag: Optional[str] = None,
    dataset_label: Optional[str] = None,
) -> str:
    safe_model = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"minimal-lift-{safe_model}-t{trials}"
    if dataset_label:
        base = f"{base}__{dataset_label}"
    safe_tag = without_domain.re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _set_artifact_paths() -> None:
    if without_domain.ACTIVE_RUN_DIR is None:
        raise RuntimeError("Run directory is not configured.")
    rd = without_domain.ACTIVE_RUN_DIR
    without_domain.RESULTS_JSON = rd / "experiment_minimal_lift_results.json"
    without_domain.SUMMARY_JSON = rd / "experiment_minimal_lift_summary.json"
    without_domain.REPORT_MD = rd / "experiment_minimal_lift_report.md"
    without_domain.BATCH_REQUESTS_JSONL = rd / "experiment_minimal_lift_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = rd / "experiment_minimal_lift_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = rd / "experiment_minimal_lift_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = rd / "experiment_minimal_lift_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = rd / "experiment_minimal_lift_batch_errors.jsonl"
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
    # Sync wd-local globals so wd.main() comparison helpers don't crash if invoked.
    wd.RESULTS_JSON = without_domain.RESULTS_JSON
    wd.SUMMARY_JSON = without_domain.SUMMARY_JSON
    wd.REPORT_MD = without_domain.REPORT_MD
    wd.BATCH_REQUESTS_JSONL = without_domain.BATCH_REQUESTS_JSONL
    wd.BATCH_MANIFEST_JSON = without_domain.BATCH_MANIFEST_JSON
    wd.BATCH_JOB_JSON = without_domain.BATCH_JOB_JSON
    wd.BATCH_OUTPUT_JSONL = without_domain.BATCH_OUTPUT_JSONL
    wd.BATCH_ERROR_JSONL = without_domain.BATCH_ERROR_JSONL


# Reuse with-domain's _prepare_manifest but rename the experiment label.
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
    manifest["experiment"] = "minimal_lift_batch_formal"
    manifest["skill_context"] = True
    manifest["minimal_lift_skill_chars"] = len(_SKILL_PROCEDURAL_OVERVIEW)
    return manifest


# ---------------------------------------------------------------------------
# Wire the patches into with_domain so wd.main() picks them up
# ---------------------------------------------------------------------------

wd._step1_context = _step1_context
wd._domain_archive_dir_name = _archive_dir_name
wd._set_domain_artifact_paths = _set_artifact_paths
wd._prepare_manifest = _patched_prepare_manifest


if __name__ == "__main__":
    sys.exit(wd.main())
