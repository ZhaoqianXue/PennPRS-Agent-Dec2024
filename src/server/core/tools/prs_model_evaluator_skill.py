"""prs-model-evaluator Anthropic Agent Skill — central loader with two views.

The skill folder lives at `src/server/core/skills/prs_model_evaluator/`
and is the **single source of truth** for the PRS-model-evaluator
domain knowledge. Both contribution2 and contribution3 read from
**this same folder**, but through different view APIs that compose its
files differently.

Two view APIs:

- `load_c2_view()` — returns content **byte-equal to the current
  `src/server/core/knowledge/prs_model_domain_knowledge.md`**, computed
  by concatenating `reference/*.md` in filename order. This view is
  **frozen against c3-only edits**: changes to `SKILL.md` or to files
  under `overrides_c3/` never affect this output. Only edits to
  `reference/*.md` change this view, and any such edit must be
  mirrored to the canonical `.md` (CI sync test enforces).

- `load_c3_view(stage, cfg)` — returns the c3 transfer-pipeline view:
  SKILL.md procedural overview (always) plus opt-in
  `reference/*.md` and `overrides_c3/*.md` files per stage. This view
  is **tunable**: changes to SKILL.md or new files in overrides_c3/
  reshape it without touching c2.

How the two views share content vs. diverge:

| asset                          | c2 view | c3 view                |
|--------------------------------|---------|------------------------|
| `reference/*.md` (full set)    | always  | only opt-in filenames  |
| `SKILL.md` body                | never   | always                 |
| `SKILL.md` frontmatter         | never   | as metadata            |
| `overrides_c3/*.md`            | never   | only opt-in filenames  |

So the two views are partly the same (both ground out in `reference/`
content) and partly different (c3 also gets SKILL.md and overrides_c3;
c2 gets the full reference set in canonical concat order).

c2 migration path:

Today, c2's `prs_model_domain_knowledge(query, max_snippets=8)` in
`src/server/core/tools/prs_model_tools.py` reads the legacy `.md`
directly. To migrate c2 to the skill, swap the file read for a call to
`load_c2_view()`. The output bytes are identical, so c2's downstream
parsing (`_parse_markdown_sections`, snippet selection, etc.) keeps
working without further change. The `prs_model_domain_knowledge.md`
file can then be removed, with the sync test continuing to guarantee
byte-equality between the historical canonical content and what
`load_c2_view()` now produces.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    # Type-only import; runtime uses duck-typing on cfg attributes so this
    # central loader does not depend on c3's agent module at import time.
    from experiments.contribution3.transfer.agent import ToolAblationConfig


# ---------------------------------------------------------------------------
# Skill-folder paths (single source of truth)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Canonical, portable skill folder. Contains SKILL.md + reference/ only.
# No consumer-specific subdirectories — the folder is self-contained and
# could be copied to another project unchanged. Anthropic Skills standard.
SKILL_DIR = PROJECT_ROOT / "src" / "server" / "core" / "skills" / "prs_model_evaluator"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"
REFERENCE_DIR = SKILL_DIR / "reference"

# contribution3-private overrides directory, OUTSIDE the skill folder.
# Files here are layered on top of the portable skill at load time by
# `load_c3_view`, but they are never part of the canonical skill and
# never visible to `load_c2_view`. Keeping this directory outside the
# skill folder is what makes the skill folder portable.
OVERRIDES_C3_DIR = (
    PROJECT_ROOT / "experiments" / "contribution3" / "transfer" / "skill_overrides"
)

# Legacy canonical corpus path. c2 reads this today; the c2-compat sync
# test asserts it is byte-equal to load_c2_view() so c2 can migrate to
# the skill folder without behaviour change. After c2 migrates, this
# path can be removed (and the sync test rewritten to track only the
# canonical historical content).
LEGACY_C2_CORPUS_PATH = (
    PROJECT_ROOT / "src" / "server" / "core" / "knowledge" / "prs_model_domain_knowledge.md"
)


# ---------------------------------------------------------------------------
# c3 view types
# ---------------------------------------------------------------------------

PgsSkillStage = Literal["pgs_triage", "pick", "reconcile", "critic"]


# Per-stage Level-3 reference selection for the c3 view.
#
# Iteration history (paired80, vs best baseline skilltask_final2):
# - iter1: ALL of (00, 01, 02, 04, 05, 07, 08) at PICK -> top_0.5%=0.275
#   (-5pp), mean_gpr 0.8238. Bulk-loading the corpus biased PICK
#   toward by-the-book endpoint-fidelity choices.
# - iter3: () at PICK (SKILL.md only) -> top_0.5%=0.2666 (-5.84pp) but
#   mean_gpr 0.8562 ABOVE baseline best (+1.1pp).
#   Best aggregate-quality result so far.
# - iter5: ("08_cross_trait_transfer_considerations.md",) at PICK ->
#   top_0.5%=0.25 (worse than iter3), mean_gpr 0.8146 (worse).
#   Section 8 added text without helping primary selection; broke
#   PICK's records-driven judgment.
#
# CONCLUSION: SKILL.md-only at every stage is the local optimum
# across 5 iterations. Any content opt-in measured worse than empty.
# Production setting holds at ().
STAGE_TO_REFERENCE_FILES: dict[PgsSkillStage, tuple[str, ...]] = {
    "pgs_triage": (),
    "pick":       (),
    "reconcile":  (),
    "critic":     (),
}

# Per-stage c3-only override selection. Files listed here live under
# experiments/contribution3/transfer/skill_overrides/ and are never
# read by load_c2_view, so they are safe for c3-only experiments.
#
# Iteration history:
# - iter4: ("pick_transfer_decision_aids.md",) at PICK -> WORSE than
#   iter3 (mean_gpr 0.8198, top_0.5% 0.25). The hand-crafted
#   prescriptive override over-corrected: oracle_in_model_frontier
#   dropped from iter3's 0.2625 to 0.2375, indicating PICK was being
#   pushed away from endpoint-faithful candidates even when those
#   were the right pick. The override file is retained on disk as
#   a documented experiment but is no longer wired in.
# - iter5: () at every stage (rolled back to no overrides).
STAGE_TO_OVERRIDE_FILES: dict[PgsSkillStage, tuple[str, ...]] = {
    "pgs_triage": (),
    "pick":       (),
    "reconcile":  (),
    "critic":     (),
}


class PgsModelEvaluatorResult(BaseModel):
    """c3-view output: SKILL.md procedural overview (always when enabled)
    plus the per-stage opt-in reference and override sections.

    `procedural_overview` is the SKILL.md body without frontmatter
    (Levels 1+2 — always loaded when the skill is enabled).
    `reference_sections` is the ordered selection from `reference/*.md`
    (Level 3, opt-in via STAGE_TO_REFERENCE_FILES).
    `override_sections` is the ordered selection from
    `overrides_c3/*.md` (Level 3, opt-in via STAGE_TO_OVERRIDE_FILES,
    c3-only — never read by load_c2_view).
    """

    stage: str
    enabled: bool = Field(
        description="False when ToolAblationConfig.enable_pgs_quality_skill is False; "
                    "in that case the other fields are empty strings / lists."
    )
    frontmatter_description: str = ""
    procedural_overview: str = Field(
        default="",
        description="SKILL.md body without YAML frontmatter. Always loaded "
                    "when the skill is enabled.",
    )
    reference_sections: List[str] = Field(
        default_factory=list,
        description="Selected reference/*.md bodies for this stage, in the "
                    "order specified by STAGE_TO_REFERENCE_FILES. Empty by "
                    "default (Anthropic-style progressive disclosure).",
    )
    override_sections: List[str] = Field(
        default_factory=list,
        description="Selected overrides_c3/*.md bodies for this stage, in the "
                    "order specified by STAGE_TO_OVERRIDE_FILES. Never read by "
                    "contribution2. Empty by default.",
    )

    @property
    def primary_section(self) -> str:
        """Concatenated text the prompt builder injects into the LLM context.
        Order: procedural overview → reference sections → override sections."""
        if not self.enabled:
            return ""
        parts: list[str] = []
        if self.procedural_overview.strip():
            parts.append(self.procedural_overview.strip())
        for section in self.reference_sections:
            if section.strip():
                parts.append(section.strip())
        for section in self.override_sections:
            if section.strip():
                parts.append(section.strip())
        return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Shared helpers (used by both views)
# ---------------------------------------------------------------------------

def _split_yaml_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body) from a markdown file with YAML frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    frontmatter: dict[str, str] = {}
    body_start_idx: Optional[int] = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start_idx = idx + 1
            break
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    if body_start_idx is None:
        return {}, text
    body = "\n".join(lines[body_start_idx:]).lstrip("\n")
    return frontmatter, body


def _load_skill_md() -> tuple[dict[str, str], str]:
    """Read SKILL.md once. Empty result if the file is missing."""
    if not SKILL_MD_PATH.exists():
        return {}, ""
    return _split_yaml_frontmatter(SKILL_MD_PATH.read_text(encoding="utf-8"))


def _load_files_from_dir(base_dir: Path, filenames: tuple[str, ...]) -> List[str]:
    """Read each named file from `base_dir` and return contents in order.
    Missing files are silently skipped (forgiving — caught by tests)."""
    out: List[str] = []
    for name in filenames:
        path = base_dir / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            out.append(text)
    return out


def list_reference_files() -> List[str]:
    """Filenames under reference/, sorted. Used by the c2 view AND by the
    sync test that asserts byte-equality with the legacy canonical .md."""
    if not REFERENCE_DIR.exists():
        return []
    return sorted(p.name for p in REFERENCE_DIR.iterdir() if p.suffix == ".md")


def list_override_files() -> List[str]:
    """Filenames under overrides_c3/, sorted (excluding README)."""
    if not OVERRIDES_C3_DIR.exists():
        return []
    return sorted(
        p.name for p in OVERRIDES_C3_DIR.iterdir()
        if p.suffix == ".md" and p.name != "README.md"
    )


# ---------------------------------------------------------------------------
# c2 view — byte-equal to current prs_model_domain_knowledge.md
# ---------------------------------------------------------------------------

def load_c2_view() -> str:
    """Return content **byte-equal** to the legacy
    `prs_model_domain_knowledge.md` file by concatenating
    `reference/*.md` in filename-sort order.

    This view is **frozen against c3-only edits**:
    - Edits to SKILL.md never affect this output.
    - Edits to overrides_c3/* never affect this output.
    - Only edits to reference/*.md change this view, and any such edit
      must be mirrored to the legacy canonical .md (the c2-compat sync
      test will fail until they are aligned).

    Used by:
    - The c2-compat sync test, today, to verify the invariant.
    - contribution2's `prs_model_domain_knowledge(query, ...)` after
      migration: the legacy file read swaps to a call to this function;
      output bytes are identical, so downstream parsing is unchanged.
    """
    files = list_reference_files()
    if not files:
        # Skill folder is broken; return empty rather than raising so
        # the test layer surfaces the diagnostic rather than the runtime.
        return ""
    return "".join(
        (REFERENCE_DIR / fname).read_text(encoding="utf-8") for fname in files
    )


# ---------------------------------------------------------------------------
# c3 view — stage-aware progressive disclosure for the transfer pipeline
# ---------------------------------------------------------------------------

def load_c3_view(
    stage: PgsSkillStage,
    cfg: Optional["ToolAblationConfig"] = None,
) -> PgsModelEvaluatorResult:
    """Stage-aware c3 view of the prs-model-evaluator skill.

    Returns the SKILL.md procedural overview (Levels 1+2, always when
    enabled) plus the stage-specific opt-in reference and override
    sections (Level 3). Default per-stage maps are empty, so the
    routine return is "SKILL.md only" — true Anthropic-style
    progressive disclosure.

    When the cfg disables the skill, returns a disabled result so the
    caller can omit the corresponding context field entirely
    (strict-ablation contract).

    Args:
        stage: Pipeline stage. Determines which reference and override
            files are loaded.
        cfg: ToolAblationConfig; the skill is enabled when
            `cfg.enable_pgs_quality_skill is True` (defaults to False
            when cfg is None).

    Returns:
        PgsModelEvaluatorResult.
    """
    enabled = bool(cfg is not None and getattr(cfg, "enable_pgs_quality_skill", False))
    if not enabled:
        return PgsModelEvaluatorResult(stage=stage, enabled=False)

    reference_filenames = STAGE_TO_REFERENCE_FILES.get(stage, ())
    override_filenames = STAGE_TO_OVERRIDE_FILES.get(stage, ())

    frontmatter, skill_body = _load_skill_md()
    if not skill_body:
        return PgsModelEvaluatorResult(stage=stage, enabled=False)

    reference_sections = _load_files_from_dir(REFERENCE_DIR, reference_filenames)
    override_sections = _load_files_from_dir(OVERRIDES_C3_DIR, override_filenames)

    return PgsModelEvaluatorResult(
        stage=stage,
        enabled=True,
        frontmatter_description=frontmatter.get("description", ""),
        procedural_overview=skill_body,
        reference_sections=reference_sections,
        override_sections=override_sections,
    )
