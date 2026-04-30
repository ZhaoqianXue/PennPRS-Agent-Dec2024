"""Two-view contract for the prs-model-evaluator Anthropic Agent Skill.

The skill folder at `src/server/core/skills/prs_model_evaluator/` is
the **single source of truth** for the PRS-model-evaluator domain
knowledge. Both contribution2 and contribution3 read from this same
folder, but through different view APIs (`load_c2_view` and
`load_c3_view`) that compose its files differently.

The user-facing contract this test file enforces:

1. **c2 view = byte-equal current `prs_model_domain_knowledge.md`.**
   `load_c2_view()` returns content identical to the legacy canonical
   `.md` file, computed by concatenating `reference/*.md` in
   filename-sort order.

2. **c2 view is frozen against c3-only edits.**
   - Editing `SKILL.md` does NOT change `load_c2_view()` output.
   - Adding files under `overrides_c3/` does NOT change
     `load_c2_view()` output.
   - Only edits to `reference/*.md` change `load_c2_view()`, and any
     such edit must be mirrored to the legacy canonical `.md` (the
     existing test_skill_c2_compat_sync test guarantees this).

3. **c3 view inherits SKILL.md and overrides_c3, plus opt-in
   reference selections.**

4. **The two views are partly the same and partly different**, exactly
   as the user articulated:
   - Both can ground out in `reference/*.md` content.
   - c3 view also gets `SKILL.md` (procedural overview) and
     `overrides_c3/*` (c3-only tunings).
   - c2 view gets the full reference set in canonical concat order;
     c3 view gets only opt-in subsets.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.server.core.tools.prs_model_evaluator_skill import (
    LEGACY_C2_CORPUS_PATH,
    OVERRIDES_C3_DIR,
    SKILL_DIR,
    SKILL_MD_PATH,
    load_c2_view,
    load_c3_view,
)


# ---------------------------------------------------------------------------
# Same-folder, different-content
# ---------------------------------------------------------------------------

def test_both_views_read_from_the_same_skill_folder() -> None:
    """Both views ground out in the same portable skill folder. This is
    what 'contribution2 和 contribution3 读到的都是同一个skill/文件夹'
    means: SKILL_DIR is the single source of truth.

    The c3-private overrides directory lives OUTSIDE the skill folder
    (at experiments/contribution3/transfer/skill_overrides/) so the
    skill folder remains portable to other consumers. The c3 loader
    composes the portable skill with c3-private overrides at load
    time."""
    assert SKILL_DIR.exists()
    assert SKILL_DIR.name == "prs_model_evaluator"
    # SKILL.md and reference/ live INSIDE the portable skill folder.
    assert SKILL_MD_PATH.parent == SKILL_DIR
    assert (SKILL_DIR / "reference").exists()
    # Overrides live OUTSIDE the skill folder (consumer-private).
    assert OVERRIDES_C3_DIR.parent != SKILL_DIR, (
        "overrides_c3 should live outside the portable skill folder; "
        "having it inside makes the skill folder consumer-specific."
    )


def test_two_views_produce_different_content() -> None:
    """The two views, called on the same folder, return different text.
    This is what '获取到的却是不同的内容（部分相同但部分不同）' means."""
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg_on = ToolAblationConfig(enable_pgs_quality_skill=True, enable_skill=False)
    c2_text = load_c2_view()
    c3_text = load_c3_view("pick", cfg=cfg_on).primary_section
    assert c2_text, "c2 view returned empty"
    assert c3_text, "c3 view returned empty"
    assert c2_text != c3_text, (
        "two views returned identical content — the architecture is "
        "broken. They must differ: c3 view should include SKILL.md "
        "procedural overview; c2 view should not."
    )


def test_c2_view_does_not_include_skill_md_body() -> None:
    """c2 view content must NOT include any of SKILL.md's authored
    procedural overview (those are c3-tunable text that should never
    leak into c2's view)."""
    c2_text = load_c2_view()
    skill_md_body_marker = "# PRS Model Evaluator"
    skill_md_section = "Anthropic Agent Skill"
    assert skill_md_body_marker not in c2_text, (
        "c2 view leaked SKILL.md body (header marker found) — "
        "load_c2_view must only concat reference/*.md"
    )
    assert skill_md_section not in c2_text, (
        "c2 view leaked SKILL.md body (Anthropic Agent Skill phrase found)"
    )


def test_c3_view_does_not_bulk_load_reference_at_any_stage() -> None:
    """The c3 view must never bulk-load the full reference/*.md
    catalogue (9 files). Iteration measurements showed bulk-loading
    at PICK biased the LLM toward by-the-book endpoint-fidelity
    choices.

    Focused per-stage opt-ins (1-2 reference files) are allowed —
    they're how c3 layers specific guidance from the corpus without
    flooding the prompt."""
    from experiments.contribution3.transfer.agent import ToolAblationConfig
    cfg_on = ToolAblationConfig(enable_pgs_quality_skill=True, enable_skill=False)
    MAX_REFERENCE_SECTIONS_PER_STAGE = 3
    for stage in ("pick", "reconcile", "critic"):
        result = load_c3_view(stage, cfg=cfg_on)
        assert result.procedural_overview, f"c3 view missing SKILL.md body at {stage}"
        assert len(result.reference_sections) <= MAX_REFERENCE_SECTIONS_PER_STAGE, (
            f"c3 view at {stage!r} loaded {len(result.reference_sections)} "
            f"reference sections; cap is {MAX_REFERENCE_SECTIONS_PER_STAGE}. "
            "Bulk-loading the catalogue was measured to harm performance."
        )


# ---------------------------------------------------------------------------
# c2 view byte-equality (the load-bearing guarantee)
# ---------------------------------------------------------------------------

def test_c2_view_byte_equals_legacy_canonical_corpus() -> None:
    """`load_c2_view()` returns content **byte-equal** to the legacy
    canonical `prs_model_domain_knowledge.md`.

    This is the contract that lets contribution2 migrate from reading
    the .md to reading via this loader without any behavioural change:
    the function returns exactly the bytes c2's existing parsing
    expects.
    """
    canonical = LEGACY_C2_CORPUS_PATH.read_text(encoding="utf-8")
    view = load_c2_view()
    if view != canonical:
        import hashlib
        first_diff = next(
            (i for i, (a, b) in enumerate(zip(canonical, view)) if a != b),
            min(len(canonical), len(view)),
        )
        raise AssertionError(
            f"load_c2_view() does NOT byte-equal the legacy canonical .md.\n"
            f"  canonical sha256: {hashlib.sha256(canonical.encode()).hexdigest()}\n"
            f"  view      sha256: {hashlib.sha256(view.encode()).hexdigest()}\n"
            f"  canonical len: {len(canonical)}, view len: {len(view)}\n"
            f"  first diff byte index: {first_diff}\n"
            "Fix: align reference/*.md with the canonical .md."
        )


# ---------------------------------------------------------------------------
# Frozen-against-c3-edits invariant
# ---------------------------------------------------------------------------

def test_c2_view_unchanged_when_skill_md_is_edited(tmp_path) -> None:
    """If a c3-only tuning edits SKILL.md, `load_c2_view()` MUST return
    the exact same bytes. This is the safety guarantee that c3
    iterations cannot break c2."""
    original_text = SKILL_MD_PATH.read_text(encoding="utf-8")
    sentinel_addition = "\n\n## c3-only experimental section\n\nSentinel for invariant test.\n"

    c2_before = load_c2_view()
    try:
        SKILL_MD_PATH.write_text(original_text + sentinel_addition, encoding="utf-8")
        c2_after = load_c2_view()
        assert c2_before == c2_after, (
            "load_c2_view() output changed when SKILL.md was edited — "
            "the c3/c2 isolation contract is broken. The c2 view must "
            "depend ONLY on reference/*.md."
        )
    finally:
        SKILL_MD_PATH.write_text(original_text, encoding="utf-8")


def test_c2_view_unchanged_when_overrides_c3_is_added(tmp_path) -> None:
    """If a c3-only tuning adds a file under overrides_c3/,
    `load_c2_view()` MUST return the exact same bytes."""
    sentinel_path = OVERRIDES_C3_DIR / "_test_c2_isolation_sentinel.md"

    c2_before = load_c2_view()
    try:
        sentinel_path.write_text(
            "# c3-only experimental override\n\nSentinel.\n", encoding="utf-8"
        )
        c2_after = load_c2_view()
        assert c2_before == c2_after, (
            "load_c2_view() output changed when an overrides_c3/ file "
            "was added — the c3/c2 isolation contract is broken. The c2 "
            "view must depend ONLY on reference/*.md, never on overrides_c3."
        )
    finally:
        if sentinel_path.exists():
            sentinel_path.unlink()


# ---------------------------------------------------------------------------
# Migration-readiness check
# ---------------------------------------------------------------------------

def test_c2_view_is_drop_in_for_c2_legacy_md_read() -> None:
    """When c2 migrates, its read path swaps from `open(c2_md)` to
    `load_c2_view()`. Asserting drop-in equivalence here means the
    migration is a 1-line code change with zero downstream parsing
    risk."""
    from src.server.core.tools import prs_model_tools as c2_tools

    c2_legacy_md_text = Path(c2_tools.KNOWLEDGE_BASE_PATH).read_text(encoding="utf-8")
    c2_view_text = load_c2_view()
    assert c2_legacy_md_text == c2_view_text, (
        "load_c2_view() is not a drop-in replacement for c2's current "
        ".md read. Migration would change c2 behaviour."
    )


# ---------------------------------------------------------------------------
# Worked example: how c3 modifies "shared" content without touching c2
# ---------------------------------------------------------------------------
#
# The architecture forbids editing reference/*.md from c3 alone (the
# c2-compat sync test would fail). To "modify shared content for c3
# only", the supported pattern is omit+add:
#   1) Author the c3-specific replacement in skill_overrides/.
#   2) Configure STAGE_TO_REFERENCE_FILES to OMIT the canonical
#      reference file for that stage (so c3 stops loading it).
#   3) Configure STAGE_TO_OVERRIDE_FILES to INCLUDE the replacement.
# c2 view still reads concat(reference/*.md), so its content is
# unchanged.

def test_c3_can_modify_shared_section_via_omit_and_add_without_touching_c2(tmp_path) -> None:
    """End-to-end demonstration of the omit+add pattern.

    Scenario: contribution3 wants to soften the endpoint-fidelity
    rules in Section 1 for the PICK stage, without changing what
    contribution2 sees. The supported way to do this is:

      - DO NOT edit reference/01_*.md (would break the c2 sync test).
      - Author a replacement file under skill_overrides/.
      - Adjust the loader's STAGE_TO_REFERENCE_FILES to omit Section 1.
      - Adjust STAGE_TO_OVERRIDE_FILES to include the replacement.

    Result: the PICK c3 view contains the replacement instead of the
    canonical Section 1; the c2 view is byte-identical to the
    canonical .md before and after.
    """
    import src.server.core.tools.prs_model_evaluator_skill as central
    from experiments.contribution3.transfer.agent import ToolAblationConfig

    # The canonical Section 1 reference filename (numerically prefixed
    # by the splitter; the test discovers it generically rather than
    # hard-coding the slug).
    canonical_section_1 = next(
        f for f in central.list_reference_files() if f.startswith("01_")
    )
    replacement_filename = "_test_pick_endpoint_fidelity_replacement.md"
    replacement_path = central.OVERRIDES_C3_DIR / replacement_filename
    replacement_body = (
        "## (c3-only replacement for endpoint-fidelity rules)\n\n"
        "For cross-trait transfer, treat endpoint fidelity to the source "
        "trait as one signal among several rather than the dominant "
        "criterion. Polygenic signal strength and validation breadth "
        "are first-class signals.\n"
    )

    cfg_on = ToolAblationConfig(enable_pgs_quality_skill=True, enable_skill=False)
    original_ref_files = central.STAGE_TO_REFERENCE_FILES.copy()
    original_override_files = central.STAGE_TO_OVERRIDE_FILES.copy()
    canonical_md_before = LEGACY_C2_CORPUS_PATH.read_text(encoding="utf-8")
    c2_view_before = load_c2_view()

    try:
        # 1) c3 authors the replacement under skill_overrides/.
        replacement_path.write_text(replacement_body, encoding="utf-8")

        # 2) c3 omits canonical Section 1 from PICK and 3) opts in to
        # the replacement instead.
        central.STAGE_TO_REFERENCE_FILES = {
            **original_ref_files,
            "pick": tuple(  # all reference files EXCEPT Section 1
                f for f in central.list_reference_files()
                if f != canonical_section_1
            ),
        }
        central.STAGE_TO_OVERRIDE_FILES = {
            **original_override_files,
            "pick": (replacement_filename,),
        }

        # c3 view at PICK now contains the replacement, NOT the canonical Section 1.
        result = load_c3_view("pick", cfg=cfg_on)
        c3_pick_text = result.primary_section
        assert "(c3-only replacement for endpoint-fidelity rules)" in c3_pick_text, (
            "c3 view did not pick up the replacement override file"
        )
        # Canonical Section 1 has its own distinctive heading; assert it
        # is absent from the c3 view.
        canonical_section_1_text = (
            central.REFERENCE_DIR / canonical_section_1
        ).read_text(encoding="utf-8")
        canonical_first_heading_line = next(
            (ln for ln in canonical_section_1_text.splitlines() if ln.startswith("## ")),
            "",
        )
        assert canonical_first_heading_line, "test setup error"
        assert canonical_first_heading_line not in c3_pick_text, (
            "c3 view still contains the canonical Section 1 heading after "
            "it was supposed to be omitted via STAGE_TO_REFERENCE_FILES"
        )

        # c2 view must be byte-identical to before — neither the
        # SKILL.md edit nor the override addition nor the loader-map
        # change can move it.
        c2_view_after = load_c2_view()
        assert c2_view_after == c2_view_before, (
            "c2 view changed when c3 used the omit+add pattern. The "
            "pattern is broken — c3 must be able to layer overrides "
            "without disturbing c2."
        )
        # And the canonical .md on disk is also untouched (we only
        # modified loader state and skill_overrides/, never reference/).
        canonical_md_after = LEGACY_C2_CORPUS_PATH.read_text(encoding="utf-8")
        assert canonical_md_after == canonical_md_before, (
            "the canonical .md file changed during a c3-only override "
            "experiment — the omit+add pattern must never touch the "
            "canonical corpus on disk"
        )
    finally:
        # Restore loader state and clean up the override file.
        central.STAGE_TO_REFERENCE_FILES = original_ref_files
        central.STAGE_TO_OVERRIDE_FILES = original_override_files
        if replacement_path.exists():
            replacement_path.unlink()
