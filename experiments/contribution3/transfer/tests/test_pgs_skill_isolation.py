"""Strict-ablation + general-trait isolation tests for prs_model_evaluator skill.

Two contracts under test:

1. Strict ablation: when `enable_pgs_quality_skill=False`, no PICK /
   GLOBAL_PRIMARY / CRITIC prompt or skill output references the skill or
   its `pgs_quality_guidance` field.

2. Trait-agnostic discipline: the SKILL.md and the slices the loader
   returns must not name any specific ICD code, disease family, or trait
   category. The skill must generalize to any trait (project policy).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.contribution3.transfer.agent import ToolAblationConfig
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    make_critic_prompt,
    make_gather_prompt,
    make_global_primary_prompt,
    make_judge_prompt,
    make_pgs_triage_prompt,
    make_pick_prompt,
    make_scout_prompt,
)
from experiments.contribution3.transfer.tools import prs_model_evaluator_skill


PGS_SKILL_OFF_CFG = ToolAblationConfig(
    enable_h2=False, enable_ot=False, enable_gc_batch=False,
    enable_biology=False, enable_skill=False,
    enable_pgs_quality_skill=False,
)
PGS_SKILL_ON_CFG = ToolAblationConfig(
    enable_h2=False, enable_ot=False, enable_gc_batch=False,
    enable_biology=False, enable_skill=False,
    enable_pgs_quality_skill=True,
)

PGS_SKILL_PROMPT_TERMS = (
    "pgs_quality_guidance",
    "pgs quality skill",
    "prs_model_evaluator",
    "prs-model-evaluator",
)


def _assert_no_pgs_skill_terms(text: str) -> None:
    lowered = text.lower()
    leaked = [term for term in PGS_SKILL_PROMPT_TERMS if term in lowered]
    assert leaked == [], f"prompt leaked pgs-skill terms while disabled: {leaked}"


def test_pgs_skill_off_omits_block_everywhere() -> None:
    """Strict ablation: with the skill off, no prompt anywhere names the
    skill or its context field."""
    for factory in (
        make_scout_prompt, make_gather_prompt, make_judge_prompt,
        make_pgs_triage_prompt, make_pick_prompt,
        make_global_primary_prompt, make_critic_prompt,
    ):
        _assert_no_pgs_skill_terms(factory(PGS_SKILL_OFF_CFG))


def test_pgs_skill_on_injects_block_at_active_stages_only() -> None:
    """The skill is injected at the within-bundle PGS-selection stages
    (PGS_TRIAGE, PICK) and nowhere else.

    Active stages — they handle PGS-quality decisions within a fixed
    bundle:
      - PGS_TRIAGE (iter8): keeps the surviving ~15-candidate set
        diverse and quality-balanced for downstream PICK.
      - PICK (iter3): picks the within-bundle primary.

    Excluded stages — different decision layer:
      - SCOUT / GATHER / JUDGE: bundle-level decisions, not PGS quality.
      - GLOBAL_PRIMARY_RECONCILIATION / CRITIC: iter0 paired80
        measurement showed skill at these cross-bundle stages caused
        bundle-level regressions (LLM switched primaries to bundles
        whose source-trait endpoints looked cleaner but transferred
        worse)."""
    for factory in (make_pgs_triage_prompt, make_pick_prompt):
        text = factory(PGS_SKILL_ON_CFG)
        assert "pgs_quality_guidance" in text, (
            f"{factory.__name__} must advertise pgs_quality_guidance"
        )
    for factory in (
        make_scout_prompt, make_gather_prompt, make_judge_prompt,
        make_global_primary_prompt, make_critic_prompt,
    ):
        _assert_no_pgs_skill_terms(factory(PGS_SKILL_ON_CFG))


def test_pgs_skill_loader_disabled_when_cfg_off() -> None:
    """Loader output is empty when the cfg disables the skill."""
    for stage in ("pgs_triage", "pick", "reconcile", "critic"):
        result = prs_model_evaluator_skill(stage, cfg=PGS_SKILL_OFF_CFG)
        assert result.enabled is False
        assert result.primary_section == ""
        assert result.procedural_overview == ""
        assert result.reference_sections == []


def test_pgs_skill_loader_enabled_when_cfg_on() -> None:
    """When enabled, loader returns a non-empty procedural overview.
    Reference sections are EMPTY BY DEFAULT under the Anthropic-style
    progressive-disclosure contract — the loader's default per-stage
    map opts no Level-3 files in. Stage-specific opt-in is tested
    separately."""
    for stage in ("pgs_triage", "pick", "reconcile", "critic"):
        result = prs_model_evaluator_skill(stage, cfg=PGS_SKILL_ON_CFG)
        assert result.enabled is True
        # Level 1+2 always loaded
        assert result.procedural_overview.strip(), f"empty SKILL.md body for {stage}"
        assert result.frontmatter_description.strip(), f"empty frontmatter desc for {stage}"
        # primary_section concatenates overview + (empty) reference + (empty) override
        assert result.procedural_overview.strip() in result.primary_section


def test_pgs_skill_loader_progressive_disclosure_is_disciplined() -> None:
    """Anthropic-style progressive disclosure: stages opt in to Level-3
    content only with deliberate justification.

    For reference/*.md (Level-3, byte-equal mirror of the canonical c2
    corpus): a stage may opt in to specific filenames. The test
    rejects bulk-loading the full catalogue (which iter1 measured to
    bias the LLM toward by-the-book endpoint-fidelity choices) and
    requires that any opted-in filename points to a real file.

    For overrides (Level-3, c3-private content): same discipline —
    opt-ins allowed, must point to real files under skill_overrides/.

    This catches typos, stale references, and accidental over-loading
    while letting deliberate experiments through."""
    from src.server.core.tools.prs_model_evaluator_skill import (
        STAGE_TO_REFERENCE_FILES,
        STAGE_TO_OVERRIDE_FILES,
        OVERRIDES_C3_DIR,
        REFERENCE_DIR,
    )
    # Hard cap on per-stage reference opt-ins. The full catalogue is 9
    # files; iter1 loaded 7 and measured a regression. A small focused
    # selection (1-2 files) is the iteration sweet spot. Raising this
    # cap requires evidence in a paired80 measurement.
    MAX_REFERENCE_OPTINS_PER_STAGE = 3
    for stage in ("pick", "reconcile", "critic"):
        ref_files = STAGE_TO_REFERENCE_FILES[stage]
        assert len(ref_files) <= MAX_REFERENCE_OPTINS_PER_STAGE, (
            f"stage {stage!r} opts in to {len(ref_files)} reference files "
            f"({list(ref_files)}); the discipline cap is "
            f"{MAX_REFERENCE_OPTINS_PER_STAGE}. Bulk-loading the full "
            "catalogue was measured to harm performance (iter1)."
        )
        for ref_filename in ref_files:
            ref_path = REFERENCE_DIR / ref_filename
            assert ref_path.exists(), (
                f"stage {stage!r} opts in to reference {ref_filename!r} "
                f"but the file does not exist at {ref_path}."
            )
        for override_filename in STAGE_TO_OVERRIDE_FILES[stage]:
            override_path = OVERRIDES_C3_DIR / override_filename
            assert override_path.exists(), (
                f"stage {stage!r} opts in to override {override_filename!r} "
                f"but the file does not exist at {override_path}. Check the "
                "filename or create the file."
            )


def test_pgs_skill_loader_can_opt_in_to_reference_files() -> None:
    """Mechanism check: when the per-stage map opts in to a reference
    filename, the loader actually returns its content. Patches the
    CENTRAL loader (the c3 shim re-exports a snapshot, not the live
    map, so patching the shim has no effect on the underlying
    function's behaviour)."""
    import src.server.core.tools.prs_model_evaluator_skill as central
    original = central.STAGE_TO_REFERENCE_FILES.copy()
    try:
        # Pick a small known file from the source corpus split.
        central.STAGE_TO_REFERENCE_FILES = {
            **original,
            "pick": ("00_preamble.md",),
        }
        result = central.load_c3_view("pick", cfg=PGS_SKILL_ON_CFG)
        assert result.enabled is True
        assert len(result.reference_sections) == 1
        # The preamble starts with the canonical corpus title.
        assert "PRS Model Domain Knowledge" in result.reference_sections[0]
    finally:
        central.STAGE_TO_REFERENCE_FILES = original


def test_pgs_skill_loader_disabled_when_cfg_none() -> None:
    """Default-safe: with cfg=None the loader treats the skill as off so
    no opt-in caller accidentally enables it."""
    for stage in ("pick", "reconcile", "critic"):
        result = prs_model_evaluator_skill(stage, cfg=None)
        assert result.enabled is False
        assert result.primary_section == ""


# ---------------------------------------------------------------------------
# Trait-agnostic discipline
# ---------------------------------------------------------------------------
#
# Project policy: c3 must not INTRODUCE trait-specific hardcoding (special
# casing, whitelists, blacklists, ICD predicates) into the skill or its
# call sites. Inherited illustrative-example wording in the shared source
# corpus (`src/server/core/knowledge/prs_model_domain_knowledge.md`,
# unchanged from contribution2 use) is out of scope here — c2 has long
# consumed those examples without issue, and modifying the source corpus
# is forbidden by the "do not affect contribution2" constraint.
#
# Boundary enforced by these tests:
#  - SKILL.md (newly authored for c3): MUST be fully trait-agnostic — no
#    ICD codes, no disease family names, no organ-system rules. The
#    procedural overview must read as "given any candidate PGS records,
#    apply this procedure".
#  - Source-corpus slices: must not introduce *new* ICD-shaped predicates
#    (the original .md has none); illustrative disease-family wording
#    inherited from c2 is permitted because we cannot modify it.
#
# What is FORBIDDEN anywhere c3 touches: rule predicates of the form
# "IF target == X THEN ...", trait-blocklists or trait-whitelists, any
# stage helper that special-cases a specific disease.

ICD_CODE_RE = re.compile(r"\b[A-TV-Z][0-9]{2}(?:\.[0-9])?\b")  # e.g. C50, E11, I25.5

SKILL_MD_PATH = (
    REPO_ROOT
    / "src" / "server" / "core" / "skills"
    / "prs_model_evaluator" / "SKILL.md"
)


def _read_skill_md_only() -> str:
    """Return SKILL.md body (frontmatter + procedural overview), excluding
    the inherited source-corpus slices."""
    return SKILL_MD_PATH.read_text(encoding="utf-8").lower()


def test_skill_md_is_fully_trait_agnostic() -> None:
    """SKILL.md is the new authored entry point. It must read as a
    trait-agnostic procedural overview — no specific disease, ICD code,
    or organ-system named in any rule or example."""
    text = _read_skill_md_only()

    # No ICD-code predicates in the new authored content.
    icd_hits = sorted(set(ICD_CODE_RE.findall(text)))
    assert icd_hits == [], f"SKILL.md contains ICD-code tokens: {icd_hits}"

    # No specific disease / organ-system names in the new authored content.
    # This list is the policy's "anything you might be tempted to special
    # case" set, kept tight intentionally so violations stand out.
    forbidden_in_skill_md = (
        "diabetes",
        "cancer",
        "cardiovascular",
        "alzheimer",
        "schizophrenia",
        "psoriasis",
        "asthma",
        "hypertension",
        "hyperlipidemia",
        "depression",
        "obesity",
        "lung",
        "breast",
        "prostate",
        "colorectal",
    )
    leaked = [name for name in forbidden_in_skill_md if name in text]
    assert leaked == [], (
        f"SKILL.md (newly authored for c3) names specific disease families: "
        f"{leaked}. Rephrase as a covariate / endpoint / packaging category "
        "that generalises. The shared source corpus is exempt; SKILL.md is not."
    )


PORTABILITY_FORBIDDEN_TERMS = (
    # Project-internal contribution / module names — break portability of
    # the skill folder. SKILL.md should describe the skill itself, not
    # the projects that consume it.
    "contribution2",
    "contribution3",
    # Standalone "c2" / "c3" abbreviations — same reason.
    " c2 ",
    " c3 ",
    " c2.",
    " c3.",
    " c2,",
    " c3,",
    # Experiment-tracking names — time-sensitive, against Anthropic best
    # practices (skills must not include time-sensitive info).
    "iter0",
    "iter1",
    "iter2",
    "iter3",
    "paired80",
    "paired20",
    "skilltask_final",
    # Project-specific cohort / dataset names.
    "AoU",
    "All of Us",
    # Internal repo file paths in narrative — break portability across
    # repos.
    "src/server/core/tools",
    "experiments/contribution3",
    "experiments/contribution2",
)


def test_skill_md_is_portable() -> None:
    """SKILL.md should describe the skill itself, not the projects that
    consume it. Per Anthropic's "Skill authoring best practices",
    skills are portable across tools and platforms — putting
    consumer-specific narrative (project names, module abbreviations,
    experiment tracking, internal file paths) into SKILL.md breaks that
    portability and bloats the description that gets injected into the
    system prompt.

    Consumer-specific documentation (loader contracts, migration paths,
    project-specific overrides) belongs in the consumer's code/docs,
    not in SKILL.md.
    """
    text = SKILL_MD_PATH.read_text(encoding="utf-8")
    leaked = []
    # Pad text with spaces so " c2 " etc. matches at the very edges too.
    padded = " " + text + " "
    for term in PORTABILITY_FORBIDDEN_TERMS:
        if term in padded:
            leaked.append(term)
    assert leaked == [], (
        f"SKILL.md leaks consumer-specific terms that break portability: {leaked}. "
        "Move project-specific narrative (loader contracts, migration paths, "
        "experiment names, internal file paths) out of SKILL.md and into the "
        "consumer's code/docs. SKILL.md should describe the skill itself only."
    )


def test_skill_folder_does_not_contain_consumer_specific_subdirs() -> None:
    """The skill folder should be portable to other projects unchanged.
    Consumer-specific subdirectories (e.g. an "overrides_<consumer>"
    folder) telegraph which project the skill is bound to and break
    that portability. Such overrides belong in the consumer's own
    project tree, layered on top of the portable skill at load time."""
    from src.server.core.tools.prs_model_evaluator_skill import SKILL_DIR
    children = sorted(p.name for p in SKILL_DIR.iterdir() if p.is_dir())
    allowed = {"reference", "scripts"}  # Anthropic standard: SKILL.md + reference/ + scripts/
    consumer_specific = [c for c in children if c not in allowed]
    assert consumer_specific == [], (
        f"skill folder contains consumer-specific subdirectories: "
        f"{consumer_specific}. Anthropic skills should be portable; "
        f"only standard subdirs ({sorted(allowed)}) belong in the skill "
        f"folder. Move consumer-specific content to the consumer's tree."
    )


def test_loader_output_does_not_introduce_new_icd_predicates() -> None:
    """The stage-aware loader must not introduce ICD-code-shaped tokens
    that are not already in the source corpus. (Pre-existing illustrative
    wording inherited from contribution2's shared corpus is exempt; we
    test for net new tokens.)"""
    source_corpus = (
        REPO_ROOT
        / "src" / "server" / "core" / "knowledge"
        / "prs_model_domain_knowledge.md"
    ).read_text(encoding="utf-8").lower()
    source_icd_tokens = set(ICD_CODE_RE.findall(source_corpus))

    parts: list[str] = []
    for stage in ("pick", "reconcile", "critic"):
        parts.append(prs_model_evaluator_skill(stage, cfg=PGS_SKILL_ON_CFG).primary_section)
    loader_text = "\n\n".join(parts).lower()
    loader_icd_tokens = set(ICD_CODE_RE.findall(loader_text))
    introduced = sorted(loader_icd_tokens - source_icd_tokens)
    assert introduced == [], (
        f"Loader introduced new ICD-shaped tokens not in source corpus: {introduced}. "
        "The loader must be a transparent slicer; it cannot add new trait-specific "
        "predicates."
    )
