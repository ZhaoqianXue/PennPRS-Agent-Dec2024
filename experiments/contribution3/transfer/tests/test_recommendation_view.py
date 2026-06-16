"""Contract for the reworked within-phenotype recommendation skill view.

`load_recommendation_view()` is the production within (contribution2) read
path that replaced the retired `load_c2_view()` byte-equality contract. It
returns the `prs-model-recommendation` skill's SKILL.md procedural overview
(frontmatter stripped) followed by its single merged
`references/pgs_evidence_appraisal.md` corpus.

This test pins the NEW contract that the retired byte-equality tests no longer
describe:
  - the view is non-empty and includes BOTH the SKILL.md procedure (fixing the
    prior gap where within never read its own SKILL.md) AND the corpus;
  - it speaks the current single-record PGS schema vocabulary used by the
    production within candidate records; and
  - it does NOT leak cross-trait transfer content (that now lives in the
    sibling prs-model-transfer skill).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.server.core.tools.prs_model_evaluator_skill import (
    RECOMMENDATION_CORPUS_PATH,
    RECOMMENDATION_SKILL_MD_PATH,
    load_recommendation_view,
)


def test_recommendation_view_is_non_empty() -> None:
    view = load_recommendation_view()
    assert view and view.strip(), "load_recommendation_view() returned empty"


def test_recommendation_view_includes_skill_md_procedure_and_corpus() -> None:
    """The within view must include BOTH the SKILL.md procedure and the separated corpus."""
    view = load_recommendation_view()
    # SKILL.md procedural overview markers.
    assert "PGS Model Recommendation" in view, "within-phenotype SKILL.md body missing from view"
    assert "Boundary: this skill supplies same-trait PRS evidence judgment" in view
    assert "Runtime orchestration, candidate-universe boundaries, output" in view
    assert "within-trait" in view
    assert "same-trait" in view
    # Merged corpus markers.
    assert "PGS Evidence Appraisal" in view, "appraisal corpus missing from view"
    assert "endpoint-fidelity field" in view, "corpus section content missing from view"


def test_recommendation_view_uses_new_single_record_schema_vocabulary() -> None:
    view = load_recommendation_view()
    for token in (
        "predicted_trait",
        "performance_metrics",
        "classification_metrics",
        "other_metrics",
        "effect_sizes",
        "evaluation_samples",
        "source_of_variant_associations_gwas",
        "score_development_training",
        "development_method",
        "pgs_source",
    ):
        assert token in view, f"new-schema token {token!r} missing from within view"


def test_recommendation_view_documents_reference_boundary_contract() -> None:
    view = load_recommendation_view()
    assert "`references/pgs_evidence_appraisal.md` is the field-level appraisal reference" in view
    assert "read only when more detail is needed for a field-level comparison" in view


def test_recommendation_view_excludes_cross_trait_transfer_content() -> None:
    """Cross-trait transfer reasoning now lives in prs-model-transfer; the
    within view must not carry it (the legacy concat pulled in section 08)."""
    view = load_recommendation_view()
    for transfer_marker in (
        "Cross-trait transfer considerations",
        "Bundle universe",
        "Open Targets",
        "n_models",
        "canonical_label",
        "cross-bundle",
    ):
        assert transfer_marker not in view, (
            f"cross-trait transfer marker {transfer_marker!r} leaked into the "
            "within recommendation view"
        )


def test_recommendation_skill_files_exist() -> None:
    assert RECOMMENDATION_SKILL_MD_PATH.exists(), "within SKILL.md missing"
    assert RECOMMENDATION_CORPUS_PATH.exists(), "within appraisal corpus missing"
