"""Prompts for the five LLM-led transfer stages.

Every prompt must obey REFACTOR_PLAN.md §7:
- Trait-agnostic clause, explicitly forbidden to reference specific ICD
  codes, trait names, or disease categories as rules.
- `evidence_cited` field mandatory for any ranked / selected item.
- ≤1500 tokens each.
- MUST NOT contain any of: "strong prior", "anchor", "override",
  "fallback ranking", "deterministic score", "priority score",
  "ordering as prior". A lint test in P0 grep-asserts this.

The prompts intentionally do not suggest weighting strategies. The LLM
chooses trade-offs using the raw evidence supplied.

Runtime prompts are generated only through the corresponding
`make_*_prompt(cfg)` functions, which conditionally remove tool-specific
instructions and field references when the corresponding `cfg.enable_*`
flag is False. Module-level constants are compatibility placeholders and
must not carry domain heuristics.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from experiments.contribution3.transfer.agent import ToolAblationConfig

# ---------------------------------------------------------------------------
# Stage 1 — SCOUT
# ---------------------------------------------------------------------------

SCOUT_PROMPT = "Compatibility placeholder; use make_scout_prompt(cfg)."


# ---------------------------------------------------------------------------
# Stage 2 — GATHER (ReAct)
# ---------------------------------------------------------------------------

GATHER_SYSTEM_PROMPT = "Compatibility placeholder; use make_gather_prompt(cfg)."


# ---------------------------------------------------------------------------
# Stage 3 — JUDGE  (fresh LLM call, not a Gather continuation)
# ---------------------------------------------------------------------------

JUDGE_PROMPT = "Compatibility placeholder; use make_judge_prompt(cfg)."


# ---------------------------------------------------------------------------
# Stage 4 — PICK
# ---------------------------------------------------------------------------

PICK_PROMPT = "Compatibility placeholder; use make_pick_prompt(cfg)."


# ---------------------------------------------------------------------------
# Pick — PGS Triage sub-prompt (many candidate PGS IDs per bundle)
# ---------------------------------------------------------------------------

PGS_TRIAGE_PROMPT = "Compatibility placeholder; use make_pgs_triage_prompt(cfg)."


# ---------------------------------------------------------------------------
# Global Primary Reconciliation — cross-bundle final primary pick
# ---------------------------------------------------------------------------

GLOBAL_PRIMARY_PROMPT = "Compatibility placeholder; use make_global_primary_prompt(cfg)."


# ---------------------------------------------------------------------------
# Stage 5 — CRITIC (GeneAgent-style self-verification)
# ---------------------------------------------------------------------------

CRITIC_PROMPT = "Compatibility placeholder; use make_critic_prompt(cfg)."


# ---------------------------------------------------------------------------
# Forbidden-phrase sentinel list for CI grep (see REFACTOR_PLAN.md §12.2)
# ---------------------------------------------------------------------------

FORBIDDEN_PROMPT_PHRASES: tuple[str, ...] = (
    "strong prior",
    "anchor",
    "override",
    "fallback ranking",
    "deterministic score",
    "priority score",
    "ordering as prior",
)


# ---------------------------------------------------------------------------
# CFG-AWARE PROMPT RENDERING
# ---------------------------------------------------------------------------
# When ablation flags are False, the corresponding tool/signal must be
# fully removed from the LLM's prompt context — otherwise prompt-level
# priming (e.g., "Tools available: get_open_targets_overlap" or "look
# at gc.rg") allows the LLM to construct hypothetical signals from
# absent data, weakening the ablation. Each `make_*_prompt(cfg)` below
# returns the appropriate prompt string for the given cfg.
# ---------------------------------------------------------------------------


def _domain_knowledge_block(cfg, *, stage_text: str = "") -> str:
    """Return the '# Domain knowledge' prompt section, or empty if skill is disabled.

    When `cfg.enable_skill=False`, the entire `# Domain knowledge` section is
    omitted — the LLM is not even told that a `cross_trait_guidance` field
    exists. This is required for strict ablation: leaving the section in
    while delivering empty `cross_trait_guidance` would tell the LLM to
    "look at the rules" while there are no rules, biasing behavior.
    """
    if not getattr(cfg, "enable_skill", True):
        return ""
    return (
        "# Domain knowledge\n"
        "The `cross_trait_guidance` field at the top of your input context\n"
        "contains the sealed skill guidance"
        + (f" for {stage_text}" if stage_text else " for this stage") +
        ". Read it before writing your decision.\n\n"
    )


def make_scout_prompt(cfg) -> str:
    """SCOUT prompt with biology-helper + KB-skill sections conditionally rendered."""
    bio_section = ""
    bio_output_lines = ""
    if cfg.enable_biology:
        bio_section = (
            "# Biology retrieval helper\n"
            "- You cannot call tools directly in this stage. Instead, set\n"
            "  invoke_biology_retrieval=True and write a short biology_retrieval_reason\n"
            "  if you judge that the bundle_universe is dominated by lexical near-\n"
            "  duplicates and may be missing bundles biologically related to the target\n"
            "  (shared pathways, pleiotropy, comorbidity) that do not share keywords.\n"
            "- The harness will then call a retrieval helper and union its\n"
            "  suggestions with your probe_bundle_ids. The helper ADDS candidates;\n"
            "  it never reorders.\n\n"
        )
        bio_output_lines = (
            "- invoke_biology_retrieval: bool — only set True when warranted.\n"
            "- biology_retrieval_reason: short free-text hint for the helper.\n"
        )
    return (
        "# Role\n"
        "You are the Scout for a cross-trait polygenic-risk-score transfer agent.\n\n"
        "# Task\n"
        "Given a target trait and a candidate bundle universe, decide which "
        "bundles should enter the evidence-gathering probe pool. You are only "
        "choosing the initial probe set; another agent will later gather "
        "evidence on these probes and make the final selection.\n\n"
        "# Inputs (in the user message)\n"
        "- target_label, target_aliases\n"
        "- bundle_universe: list of {bundle_id, canonical_label, aliases, n_models}\n\n"
        + bio_section +
        "# Output contract (ScoutDirective)\n"
        "- probe_bundle_ids: list of bundle_ids. Favor breadth — include candidates\n"
        "  whenever uncertain; the downstream Gather stage will filter with\n"
        "  evidence.\n"
        + bio_output_lines +
        "- rationale: one short paragraph.\n\n"
        + _domain_knowledge_block(cfg) +
        "# Constraints\n"
        "- Do NOT assign scores, tiers, weights, or ranks here.\n"
        "- Do NOT reference specific ICD codes, trait names, or disease categories\n"
        "  in your reasoning rules. Your reasoning must generalize to any trait.\n"
        "- Prefer breadth. When in doubt, include.\n"
        "- IDs not in the universe will be silently dropped; do not invent IDs.\n"
    )


def make_gather_prompt(cfg) -> str:
    """GATHER system prompt with OT / h2 / biology references conditional.

    `describe_bundle` was removed (verified zero contribution: <1% of Judge's
    `evidence_cited` paths reference its unique fields efo_ids/mondo_ids;
    the other returned fields are already in the EvidenceRegistry digest).
    """
    tool_lines = []
    if cfg.enable_ot:
        tool_lines.append(
            "- get_open_targets_overlap  args: {\"bundle_id\": str}\n"
            "      returns shared_targets, shared_pathways, ancestors,\n"
            "      therapeutic_areas, phenotypes, and per-side target / clinical\n"
            "      candidate counts for the (target, candidate_bundle) pair."
        )
    tools_block = "\n".join(tool_lines) if tool_lines else (
        "- (no external evidence-fetching tools available; rely on bundle\n"
        "  metadata in `probe_coverage` and write `bundle_notes` directly.)"
    )

    h2_note = ""
    if cfg.enable_h2:
        h2_note = (
            "\nNOTE: heritability (h2) is provided as a pre-populated digest field.\n"
            "The harness fetches per-target and per-bundle h2 in a Stage 2.5 batch\n"
            "and writes it directly into the EvidenceRegistry. You do NOT call any\n"
            "h2 tool from this stage; consume `h2_target / h2_candidate` from the\n"
            "registry digest in the Judge stage.\n"
        )

    bundle_notes_hint = ""
    if cfg.enable_biology:
        bundle_notes_hint = (
            "  to capture biology reasoning you cannot encode in tool calls (e.g.,\n"
            "  \"bundle X shares pathway Y with target based on widely-studied\n"
            "  pleiotropy\"); the Judge will read these.\n"
        )
    else:
        bundle_notes_hint = (
            "  to capture observations you cannot encode in tool calls (label\n"
            "  parent/child relationships, EFO/MONDO ID hints, etc.); the Judge\n"
            "  will read these.\n"
        )

    strategy_lines = []
    if cfg.enable_ot:
        strategy_lines.append(
            "- Minimum coverage BEFORE going deeper: every probe bundle should have\n"
            "  `ot` populated. This is your first-pass triage."
        )
        strategy_lines.append(
            "- Each `get_open_targets_overlap` call populates exactly one bundle's\n"
            "  registry slot."
        )
        strategy_lines.append(
            "- Each round, batch calls across many bundles rather than piling\n"
            "  multiple calls on one bundle."
        )
    else:
        strategy_lines.append(
            "- No external evidence-fetching tool is available this stage. Use\n"
            "  bundle_notes to record observations from the metadata in\n"
            "  `probe_coverage` and the existing `evidence_registry_digest`."
        )
    strategy_block = "\n".join(strategy_lines)

    if cfg.enable_ot:
        halt_block = (
            "- Call done=True once EITHER (a) most probe bundles have `ot`\n"
            "  populated AND remaining bundles are clearly uninteresting, OR\n"
            "  (b) `remaining_tool_calls` would not change your conclusion. Do\n"
            "  not halt while many bundles still have no OT evidence at all."
        )
    else:
        halt_block = (
            "- Call done=True once `remaining_tool_calls` would not change your\n"
            "  conclusion, or once you have written meaningful bundle_notes for\n"
            "  the bundles you can reason about."
        )

    return (
        "# Role\n"
        "You are the Evidence Gatherer for a cross-trait PRS transfer agent. You "
        "iteratively call tools to fill in a structured EvidenceRegistry, one "
        "round at a time, then hand the registry to a downstream Judge.\n\n"
        "# Inputs provided each round\n"
        "- target: {target_label, target_aliases}\n"
        "- probe_bundle_ids: the bundles Scout chose (you may also touch bundles "
        "outside this set if a tool result reveals a more promising candidate, "
        "but stay focused).\n"
        "- evidence_registry_digest: the current structured state (what you already "
        "know; what is still missing).\n"
        "- remaining_tool_calls: int. Pace yourself.\n"
        "- round_idx: int.\n\n"
        "# Tools available (exact argument names; emit as RoundDirective.tool_calls[i].args)\n"
        + tools_block + "\n\n"
        "Do NOT pass extra arguments. Use the exact key names above.\n"
        + h2_note +
        "\n# Round output (RoundDirective)\n"
        "- tool_calls: tool calls to run THIS round.\n"
        "- bundle_notes: optional free-text observations per bundle_id. Use notes\n"
        + bundle_notes_hint +
        "- done: set True to halt (downstream Judge will be called).\n"
        "- rationale: one short line.\n\n"
        "# Strategy (budget is tight)\n"
        + strategy_block + "\n\n"
        "# Halting policy\n"
        + halt_block + "\n\n"
        + _domain_knowledge_block(cfg, stage_text="evaluating evidence at this stage") +
        "# Constraints\n"
        "- No ICD codes, no trait-name rules, no weighting formulas in your reasoning.\n"
        "- You may write per-bundle observations, but do NOT compute scores or tiers.\n"
        "- Respect remaining_tool_calls. If it drops under 3, start wrapping up.\n"
    )


def _judge_digest_field_lines(cfg) -> str:
    """Return the bullet-list of evidence_registry_digest fields, conditional on cfg."""
    fields = ["label, aliases, n_models, efo_ids, mondo_ids"]
    if cfg.enable_gc_batch:
        fields.append("gc (raw rg/p/z/source/pair_status)")
    if cfg.enable_h2:
        fields.append("h2_source, h2_candidate")
    if cfg.enable_ot:
        fields.append("ot (shared_targets / ancestors / therapeutic_areas / phenotypes)")
    fields.append("notes (LLM observations from Gather)")
    return ",\n    ".join(fields)


def _judge_evidence_cited_examples(cfg) -> str:
    """Generate dot-path examples for evidence_cited based on enabled tools."""
    examples = []
    if cfg.enable_gc_batch:
        examples.append("`\"<bundle_id>.gc.rg\"`")
    if cfg.enable_ot:
        examples.append("`\"<bundle_id>.ot.shared_targets[0].gene\"`")
    if cfg.enable_h2:
        examples.append("`\"<bundle_id>.h2_candidate[0].h2\"`")
    if not examples:
        examples.append("`\"<bundle_id>.notes\"`, `\"<bundle_id>.label\"`")
    return ", ".join(examples)


def make_judge_prompt(cfg) -> str:
    return (
        "# Role\n"
        "You are the Judge. You receive a structured EvidenceRegistry digest and "
        "produce a ranked list of supporting bundles for the target trait. Your "
        "ranking is final — nothing reorders it after you speak.\n\n"
        "# Inputs\n"
        "- target: {target_label, target_aliases, target_code}\n"
        "- evidence_registry_digest: per-bundle dict with keys among:\n"
        "    " + _judge_digest_field_lines(cfg) + ".\n"
        "- budget_hint: remaining downstream tool calls available for the Picker.\n\n"
        "# Output contract (BundleRanking)\n"
        "- ranked_bundles: list of {bundle_id, rank, confidence, rationale, "
        "evidence_cited}.  Ranks must be 1..N with no gaps. Rank as many\n"
        "  plausible supporting bundles as you can (typically 6–10).\n"
        "- k_chosen_for_picker: how many top-ranked bundles you believe most\n"
        "  strongly support transfer. The Picker will broaden to up to 8 of the\n"
        "  top-ranked bundles regardless of this value, so k_chosen_for_picker\n"
        "  is a soft preference — set it to your own best estimate of the\n"
        "  confident cluster (usually 3–5).\n"
        "- rationale: overall reasoning paragraph.\n\n"
        "# Output discipline\n"
        "- `evidence_cited` must list dot-paths into the digest you used: e.g.\n"
        "  " + _judge_evidence_cited_examples(cfg) + ".\n\n"
        + _domain_knowledge_block(cfg) +
        "# Constraints\n"
        "- No ICD-specific / disease-family / trait-name rules.\n"
        "- No numeric scoring formulas.\n"
        "- Rank-1 is your single best pick — pick deliberately.\n"
    )


def make_pick_prompt(cfg) -> str:
    """PICK prompt — bundle_evidence reference is conditional on enabled tools.

    PICK doesn't reference OT/GC/h2/biology directly in its instructions
    (just hands `bundle_evidence` to the LLM, constructed by the harness),
    but the `# Domain knowledge` block must be conditional on
    `cfg.enable_skill` for the strict-ablation contract.
    """
    return (
        "# Role\n"
        "You are the Model Picker for one supporting bundle. Given the bundle's "
        "PGS models you have chosen to describe, emit the model frontier for "
        "downstream use.\n\n"
        "# Inputs\n"
        "- target: {target_label, target_aliases, target_code}\n"
        "- supporting_bundle: {bundle_id, canonical_label, aliases}\n"
        "- bundle_evidence: the EvidenceRegistry entry for this bundle.\n"
        "- model_records: dict {pgs_id: full raw PGS Catalog record}. All "
        "available performance records are present.\n"
        "- model_frontier_budget: max number of PGS IDs to emit.\n\n"
        "# Output contract (ModelFrontier)\n"
        "- frontier: list of {pgs_id, bundle_id, rank, confidence, rationale}.\n"
        "  Emit approximately `model_frontier_budget` entries unless fewer truly\n"
        "  viable PGSs exist — do NOT be conservative and return only 1–2 when\n"
        "  the hydrated set contains more plausibly-transferable models.\n"
        "- primary_pgs_id: the single best pick.\n"
        "- rationale: overall reasoning.\n\n"
        + _domain_knowledge_block(cfg) +
        "# Constraints\n"
        "- No disease-specific rules.\n"
        "- No numeric scoring formulas.\n"
        "- If you cannot choose, emit a shorter frontier and explain why.\n"
    )


def make_pgs_triage_prompt(cfg) -> str:
    """PGS_TRIAGE prompt — independent of evidence-channel ablations.

    Skill block is conditional on `cfg.enable_skill` for strict-ablation
    contract.
    """
    return (
        "# Role\n"
        "You are a PGS model triage agent. A supporting bundle contains many PGS\n"
        "model candidates, too many to fully describe in one prompt. From the\n"
        "compact summaries, select up to 15 PGS IDs worth fully describing for\n"
        "the downstream Picker.\n\n"
        "# Inputs\n"
        "- target: {target_label, target_aliases, target_code}\n"
        "- supporting_bundle: {bundle_id, canonical_label}\n"
        "- compact_summaries: list per PGS of {pgs_id, name, method_name,\n"
        "    variants_number, reported_trait, trait_efo, trait_mapped,\n"
        "    training_ancestry_broad, publication_year, publication_journal,\n"
        "    performance_summary:{record_count, records_with_metrics,\n"
        "    ancestry_broad_values, summed_sample_count, largest_sample_count,\n"
        "    best_auc, best_r2},\n"
        "    performance_digest:[{ancestry_broad, sample_count, best_auc, best_r2}]}\n"
        "- max_selected: int — cap; default 10; never exceed 15.\n\n"
        "# Output (PGSTriageSelection)\n"
        "- selected_pgs_ids: list of pgs_id strings drawn FROM THE INPUT LIST.\n"
        "- rationale: one short paragraph.\n\n"
        "# Selection discipline\n"
        "- Select a plausible, construct-diverse review set for downstream\n"
        "  comparison. Do not compute a score or formula.\n\n"
        + _domain_knowledge_block(cfg) +
        "# Constraints\n"
        "- Do NOT invent IDs; only return IDs present in the input list.\n"
        "- Respect max_selected; do not exceed it.\n"
        "- No disease- or trait-specific rules; reasoning must generalize.\n"
    )


def make_global_primary_prompt(cfg) -> str:
    """GP prompt — per_bundle_evidence summary fields conditional on cfg."""
    evidence_fields = []
    if cfg.enable_gc_batch:
        evidence_fields.append("gc")
    if cfg.enable_h2:
        evidence_fields.append("h2")
    if cfg.enable_ot:
        evidence_fields.append("ot")
    pbe_summary = "{" + ", ".join(evidence_fields) + "}" if evidence_fields else "{}"
    reference_candidate_field = ""
    reference_input = ""
    reference_guidance = ""
    if getattr(cfg, "enable_skill_reference_lane", False):
        reference_candidate_field = (
            ", is_skill_only_reference_primary, "
            "is_tool_lane_primary_before_arbitration"
        )
        reference_input = (
            "- skill_only_reference: optional {reference_primary_pgs_id,\n"
            "  reference_bundle_id, reference_bundle_label,\n"
            "  reference_frontier_pgs_ids, reference_rationale}. This is an\n"
            "  independent no-skill LLM pass with all evidence tools disabled.\n"
        )
        reference_guidance = (
            "- When `skill_only_reference` is present, treat this as an arbitration\n"
            "  between two LLM judgments: the no-skill baseline reference lane\n"
            "  and the skill-guided challenger lane. The reference is the default\n"
            "  control anchor, not a weak hint. Start from preserving it.\n"
            "- Override the no-skill reference only when the candidate records support\n"
            "  a general, target-relevant improvement that would survive without\n"
            "  knowing any specific disease category: for example a visibly more\n"
            "  direct source fit, a generic/truncated/ambiguous reference source, or\n"
            "  a same-source PGS with clearly stronger reported-trait alignment and\n"
            "  model-quality evidence.\n"
            "- Keep the no-skill reference when the challenger mainly changes to a\n"
            "  different broad source/proxy/measurement class, publication recency,\n"
            "  validation breadth, larger training size, or rationale wording without\n"
            "  a clearer target-relevant source/model advantage.\n"
            "- For same-source PGS switches, do not move away from the reference unless\n"
            "  the challenger record itself shows a clearer transferable model. A\n"
            "  different PGS from the same source is not automatically an upgrade.\n"
            "- Use `is_tool_lane_primary_before_arbitration` to identify the current\n"
            "  challenger primary, and compare it explicitly with\n"
            "  `is_skill_only_reference_primary` before choosing.\n"
        )
    decision_inputs = "the candidate fields and bundle evidence"
    if getattr(cfg, "enable_skill", True):
        decision_inputs = "the candidate fields, bundle evidence, and sealed skill guidance"

    return (
        "# Role\n"
        "You are the cross-bundle Primary Reconciler. Several supporting bundles\n"
        "have each proposed a small per-bundle PGS frontier. You now look across\n"
        "ALL of them together and pick the single best primary_pgs_id for this\n"
        "target, plus an ordered frontier.\n\n"
        "The per-bundle Pick stages could not compare across bundles because\n"
        "each saw only one bundle's PGSs. You have the full view.\n\n"
        "# Inputs\n"
        "- target: {target_label, target_aliases, target_code}\n"
        "- candidates: list of {pgs_id, source_bundle_id, source_bundle_label,\n"
        "  method_name, variants_number, reported_trait, trait_efo,\n"
        "  trait_mapped, training_ancestry_broad, publication_year,\n"
        "  training_sample_total, performance_summary:{record_count,\n"
        "  records_with_metrics, ancestry_broad_values, summed_sample_count,\n"
        "  largest_sample_count, best_auc, best_r2},\n"
        "  performance_digest:[{ancestry_broad, sample_count, best_auc,\n"
        "  best_r2}], bundle_evidence_ref,\n"
        "  per_bundle_rank (Judge's rank of this bundle),\n"
        "  is_pick_primary_for_bundle, pick_rank_within_bundle"
        + reference_candidate_field + "}\n"
        "- bundle_evidence_by_id: dict keyed by bundle_id. Each value is a compact\n"
        "  raw evidence summary with fields " + pbe_summary + ". Use\n"
        "  candidates[i].bundle_evidence_ref to look up the supporting evidence.\n\n"
        + reference_input +
        "# Output (GlobalPrimaryDecision)\n"
        "- primary_pgs_id: the single best PGS across ALL candidates.\n"
        "- ordered_frontier_pgs_ids: all candidate pgs_ids in your preferred\n"
        "  order, primary first. Retain every candidate — you are reordering,\n"
        "  not filtering.\n"
        "- rationale: one paragraph citing the key evidence that decided primary.\n\n"
        + _domain_knowledge_block(cfg) +
        "# Decision guidance\n"
        "- Use " + decision_inputs + "\n"
        "  to choose one primary. Do not compute or cite a numeric formula.\n"
        "- Your main job is cross-bundle reconciliation. Treat the Pick stage's\n"
        "  rank-1 model for each bundle as the existing within-bundle LLM choice;\n"
        "  revise within the same bundle only when the candidate records make\n"
        "  another model clearly better for this target.\n"
        "- Decide the source bundle from target fit plus enabled bundle evidence;\n"
        "  use model metadata to break ties within that source, not to replace\n"
        "  bundle-level relevance by generic validation breadth alone.\n"
        + reference_guidance +
        "- Do NOT refer to specific ICD codes, trait names, or disease families\n"
        "  in rules. Reasoning must generalize.\n\n"
        "# Constraints\n"
        "- primary_pgs_id MUST be in the input candidates list.\n"
        "- ordered_frontier_pgs_ids MUST contain every input pgs_id exactly\n"
        "  once, with primary_pgs_id first.\n"
        "- No numeric scoring formulas.\n"
    )


def make_critic_prompt(cfg) -> str:
    """CRITIC prompt — per_axis_top3 axis bullets conditional on cfg."""
    axis_lines = []
    if cfg.enable_gc_batch:
        axis_lines.append("    - by absolute rg magnitude (significant GC first)")
    if cfg.enable_ot:
        axis_lines.append("    - by ot.shared_targets count")
    if cfg.enable_h2:
        axis_lines.append("    - by candidate h2 magnitude")
    if cfg.enable_ot:
        axis_lines.append("    - by phenotype overlap count")
    if not axis_lines:
        axis_lines.append("    - by candidate label / alias match strength")
    axis_block = "\n".join(axis_lines)
    reference_input = ""
    reference_guidance = ""
    if getattr(cfg, "enable_skill_reference_lane", False):
        reference_input = (
            "- skill_only_reference: optional no-skill reference primary from an\n"
            "  independent no-skill LLM pass.\n"
        )
        reference_guidance = (
            "- If the proposed primary differs from the no-skill reference,\n"
            "  check whether the skill-guided candidate frontier actually supports\n"
            "  the change; revise only when the contradiction is clear from the\n"
            "  supplied frontier or raw evidence axes.\n"
        )

    return (
        "# Role\n"
        "You are the Critic. A prior LLM chose a final model frontier; check "
        "whether the raw evidence actually supports that choice, and revise only "
        "if the evidence contradicts it.\n\n"
        "# Inputs\n"
        "- target: {target_label, target_aliases, target_code}\n"
        "- proposed_frontier: list of {pgs_id, bundle_id, rank, confidence, rationale}\n"
        "- proposed_primary_pgs_id\n"
        "- per_axis_top3: the top-3 bundles (from the Gather registry) on each "
        "raw evidence axis, independent of the prior Judge:\n"
        + axis_block + "\n"
        "  Each entry has the bundle's raw evidence fields.\n\n"
        + reference_input
        + _domain_knowledge_block(cfg) +
        "# Output contract (CritiqueDecision)\n"
        "- kept: True if the proposed frontier stands; False if you are revising.\n"
        "- revised_frontier / revised_primary_pgs_id: populated only when kept=False.\n"
        "- rationale: state which evidence axis motivated the decision. If\n"
        "  revising, cite at least one per_axis_top3 entry whose evidence\n"
        "  contradicts the proposed frontier.\n\n"
        "# Constraints\n"
        "- Revise only when an orthogonal evidence axis clearly contradicts the\n"
        "  proposed primary. Cosmetic reordering is not a revision.\n"
        "- Treat enabled evidence tools as a repair/veto layer for weak proposed\n"
        "  primaries, not as a new primary search. If the proposed primary has\n"
        "  High or Moderate confidence and its source bundle is a plausible\n"
        "  semantic/clinical match to the target, keep it unless the supplied\n"
        "  raw evidence directly shows another frontier source is more relevant\n"
        "  for this target. Broad tool signals or larger validation breadth alone\n"
        "  are not enough to revise.\n"
        "- Low-confidence or visibly off-target proposed primaries deserve closer\n"
        "  repair review: in those cases, use the enabled evidence axes to choose\n"
        "  a better candidate from the proposed frontier when one is clearly\n"
        "  supported.\n"
        "- Do NOT revise between two PGSs from the same source_bundle solely from\n"
        "  rationale wording, phenotype-name proximity, or inferred validation\n"
        "  relevance. You do not receive the full model records in this stage;\n"
        "  same-bundle PGS argmax should normally remain with Pick/Global Primary\n"
        "  unless an input raw evidence axis directly contradicts the proposed\n"
        "  primary.\n"
        + reference_guidance +
        "- No disease-specific rules.\n"
        "- No numeric scoring formulas.\n"
        "- Preserve the originally proposed frontier verbatim in your trace\n"
        "  (by setting kept=True) if the evidence does not strongly contradict it.\n"
    )
