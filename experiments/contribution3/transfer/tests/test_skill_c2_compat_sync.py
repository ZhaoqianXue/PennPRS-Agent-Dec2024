"""c2 ↔ skill content invariant.

The contribution2 single-shot pipeline reads the canonical PRS-model
domain-knowledge corpus from
`src/server/core/knowledge/prs_model_domain_knowledge.md`.

The contribution3 transfer pipeline reads the same corpus via the
prs_model_evaluator Anthropic Agent Skill folder at
`src/server/core/skills/prs_model_evaluator/`. The skill folder
contains `SKILL.md` (procedural overview) plus a `reference/` directory
that mirrors the canonical corpus split into per-section files.

This test enforces the **load-bearing invariant**:

    concat(sorted(reference/*.md), in filename order) == prs_model_domain_knowledge.md

If this invariant holds, then any content the c3 loader serves from
`reference/*.md` is **byte-equal** to what c2 reads. Future c3 tunings
that should NOT affect c2 must therefore go into `overrides_c3/`
instead of editing `reference/`. If a tuning genuinely needs to change
the shared corpus, both the canonical .md and the reference files must
be edited together (this test will fail until they are aligned).

Without this test, c2 and c3 could silently diverge.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

# RETIRED 2026-06 (kept for traceability, not deleted). This file enforced the
# byte-equality invariant between the legacy canonical corpus
# (prs_model_domain_knowledge.md) and the concatenated
# prs_model_evaluator/reference/*.md. Production within (contribution2) has
# migrated to the reworked prs-model-recommendation skill via
# load_recommendation_view(), whose content is DELIBERATELY not byte-equal to
# the legacy corpus, so this invariant no longer describes the running system.
# The replacement contract lives in test_recommendation_view.py.
pytestmark = pytest.mark.skip(
    reason="legacy c2 byte-equality contract retired; production within now "
    "reads the prs-model-recommendation skill (load_recommendation_view). "
    "Kept for traceability; see test_recommendation_view.py."
)

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.contribution3.transfer.tools.prs_model_evaluator_skill import (
    REFERENCE_DIR,
    SOURCE_CORPUS_PATH,
    list_reference_files,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reference_concat_byte_equals_canonical_corpus() -> None:
    """The hard invariant: c2's canonical .md is byte-equal to the
    in-order concatenation of the skill's reference files.

    If this fails, the most common causes are:
    - Someone edited `prs_model_domain_knowledge.md` without updating
      `reference/*.md` (or vice versa).
    - A new section was added to the canonical corpus and no
      corresponding `reference/NN_*.md` file was created.
    - A reference filename was renamed and the resulting filename-sort
      order changed the section ordering.

    To repair: regenerate reference files from the canonical corpus
    (see scripts/split_corpus.py if present, or the splitter inline in
    git history for the initial creation), or align the canonical .md
    to the concatenated reference content.
    """
    assert SOURCE_CORPUS_PATH.exists(), (
        f"canonical corpus missing at {SOURCE_CORPUS_PATH} — c2 reads from here"
    )
    assert REFERENCE_DIR.exists(), (
        f"reference dir missing at {REFERENCE_DIR} — skill is broken"
    )
    files = list_reference_files()
    assert files, "no reference files found — skill is broken"

    canonical = _read(SOURCE_CORPUS_PATH)
    concat = "".join(_read(REFERENCE_DIR / fname) for fname in files)

    if concat != canonical:
        # Surface a diff hint that's actually useful when this fails.
        canonical_sha = hashlib.sha256(canonical.encode()).hexdigest()
        concat_sha = hashlib.sha256(concat.encode()).hexdigest()
        # Find first differing byte for a useful pointer.
        first_diff = next(
            (i for i, (a, b) in enumerate(zip(canonical, concat)) if a != b),
            min(len(canonical), len(concat)),
        )
        raise AssertionError(
            f"c2 ↔ skill content invariant BROKEN.\n"
            f"  canonical corpus: {SOURCE_CORPUS_PATH}\n"
            f"    sha256={canonical_sha}  len={len(canonical)}\n"
            f"  concatenated reference: {len(files)} files\n"
            f"    sha256={concat_sha}  len={len(concat)}\n"
            f"  first byte difference at index {first_diff}\n"
            f"  files in concat order: {files}\n"
            f"\nFix: align the two views. Either regenerate reference/ from "
            f"the canonical corpus or align the canonical .md to the "
            f"concatenated reference content."
        )


def test_reference_filename_sort_is_explicit() -> None:
    """The concat order is filename sort. Names should start with a
    zero-padded 2-digit prefix to make the order obvious in `ls`."""
    files = list_reference_files()
    for fname in files:
        prefix = fname[:2]
        assert prefix.isdigit() and len(prefix) == 2, (
            f"reference file {fname!r} should start with a 2-digit zero-padded "
            f"prefix to make filename sort order explicit"
        )


def test_canonical_corpus_path_is_what_c2_reads() -> None:
    """Belt-and-braces: confirm the path the skill loader documents as
    'canonical' is identical to the path c2's tool function actually
    reads. If c2's path ever moves, this test points at the divergence
    immediately."""
    from src.server.core.tools import prs_model_tools as c2_tools

    c2_path = Path(c2_tools.KNOWLEDGE_BASE_PATH).resolve()
    skill_loader_canonical_path = SOURCE_CORPUS_PATH.resolve()
    assert c2_path == skill_loader_canonical_path, (
        f"c2's KB path ({c2_path}) and the skill loader's canonical "
        f"path ({skill_loader_canonical_path}) have diverged. The c2 ↔ "
        f"skill sync test must be updated to point at the new c2 path "
        f"(or c2 should be re-pointed back)."
    )
