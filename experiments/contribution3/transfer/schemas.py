"""Pydantic output schemas for the LLM-led cross-trait transfer agent.

All decision-bearing schemas intentionally OMIT the following fields (any
appearance is a CI failure; see REFACTOR_PLAN.md §6):
    archetype, phenotype_fidelity_score, utility_score,
    selection_priority_score, transferability_prior_score,
    cheap_rank_score, evidence_tags, rank_by_*, weighted_overlap,
    confidence_level, confidence_tier, genetic_support_present.

Only the LLM may populate `rank`, `confidence`, and `rationale`. The harness
may only (a) drop invalid IDs (tagged `harness:drop_invalid_id`) and
(b) tag each field's source in `ProvenanceLog`.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ConfidenceLabel = Literal["High", "Moderate", "Low"]


# ---------------------------------------------------------------------------
# Gather (Stage 2): LLM directive per ReAct round
# ---------------------------------------------------------------------------

class ToolCall(BaseModel):
    tool: Literal[
        "get_open_targets_overlap",
    ]
    args: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tool", mode="before")
    @classmethod
    def _normalize_tool_name(cls, value: Any) -> Any:
        text = str(value or "").strip()
        if "." in text:
            text = text.rsplit(".", 1)[-1]
        return text


class RoundDirective(BaseModel):
    """One LLM turn inside the Gather ReAct loop."""

    tool_calls: list[ToolCall] = Field(default_factory=list)
    bundle_notes: dict[str, str] = Field(
        default_factory=dict,
        description="Free-text observations per bundle_id, authored by the LLM.",
    )
    done: bool = Field(
        False,
        description="If True, LLM halts the Gather loop; otherwise another round runs.",
    )
    rationale: str = ""


# ---------------------------------------------------------------------------
# Scout (Stage 1)
# ---------------------------------------------------------------------------

class ScoutDirective(BaseModel):
    """Stage 1 output: which bundles enter the Gather probe pool."""

    probe_bundle_ids: list[str]
    invoke_biology_retrieval: bool = Field(
        False,
        description="If True, the harness will run biology_retrieve_related_bundles "
        "and append those IDs to probe_bundle_ids (retrieval augmentation only).",
    )
    biology_retrieval_reason: str = Field(
        "",
        description="One-line rationale for needing biology retrieval — passed to the helper.",
    )
    used_biology_retrieval: bool = False  # populated by the harness after helper runs
    rationale: str = ""

    @field_validator("probe_bundle_ids", mode="before")
    @classmethod
    def _filter_probe_bundle_ids(cls, value: Any) -> list[str]:
        """Drop malformed LLM list items instead of failing the whole Scout call."""
        if not isinstance(value, list):
            return []
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    out.append(text)
            elif isinstance(item, (int, float)) and not isinstance(item, bool):
                out.append(str(item))
        return out


class BiologySuggestion(BaseModel):
    """One LLM-proposed biology-related bundle. The bundle_id is filtered
    against the input universe by the tool; LLM-emitted IDs not in the
    universe are dropped."""

    bundle_id: str
    suggestion_rationale: str


class BiologyRetrievalResponse(BaseModel):
    """Raw LLM structured output of the biology-retrieval call."""

    suggestions: list[BiologySuggestion]
    rationale: str = ""


class BiologyRetrievalResult(BaseModel):
    """Public tool output of `biology_retrieve_related_bundles`.

    Wraps the raw LLM response with:
    - id-validity filtering already applied (only bundle_ids in input universe)
    - observability fields (n_total / n_kept / skipped_reason) so callers
      can distinguish empty-output cases (LLM proposed 0 vs LLM proposed
      many but all invalid vs LLM call errored).
    """

    suggestions: list[BiologySuggestion] = Field(default_factory=list)
    rationale: str = ""
    n_suggestions_total: int = Field(
        0,
        description="Number of suggestions the LLM emitted before universe filtering.",
    )
    n_suggestions_kept: int = Field(
        0,
        description="Number of suggestions retained after filtering to known bundle_ids.",
    )
    skipped_reason: str | None = Field(
        None,
        description=(
            "Set when the tool returned without a real LLM call: "
            "'empty_target' / 'empty_universe' / 'llm_error:<msg>'. "
            "None when the call succeeded normally."
        ),
    )


# ---------------------------------------------------------------------------
# Judge (Stage 3)
# ---------------------------------------------------------------------------

class RankedBundle(BaseModel):
    bundle_id: str
    rank: int = Field(ge=1)
    confidence: ConfidenceLabel
    rationale: str
    evidence_cited: list[str] = Field(
        default_factory=list,
        description="Dot-paths into EvidenceRegistry keys justifying this rank.",
    )


class BundleRanking(BaseModel):
    ranked_bundles: list[RankedBundle]
    k_chosen_for_picker: int = Field(
        ge=1,
        description="How many top-ranked bundles feed Stage 4 (Pick).",
    )
    rationale: str = ""


# ---------------------------------------------------------------------------
# Pick (Stage 4)
# ---------------------------------------------------------------------------

class FrontierModel(BaseModel):
    pgs_id: str
    bundle_id: str
    rank: int = Field(ge=1)
    confidence: ConfidenceLabel
    rationale: str


class ModelFrontier(BaseModel):
    frontier: list[FrontierModel]
    primary_pgs_id: str
    rationale: str = ""


# ---------------------------------------------------------------------------
# Pick — PGS Triage sub-call (when a bundle has many candidate PGS IDs)
# ---------------------------------------------------------------------------

class PGSTriageSelection(BaseModel):
    """LLM picks a small subset of PGS IDs to fully describe.

    This is retrieval, not ranking — the selection returns IDs worth
    deeper inspection. The Picker then fully hydrates and ranks them.
    """

    selected_pgs_ids: list[str]
    rationale: str = ""


# ---------------------------------------------------------------------------
# Global Primary Reconciliation — cross-bundle final primary pick
# ---------------------------------------------------------------------------

class GlobalPrimaryDecision(BaseModel):
    """Cross-bundle reconciliation: the LLM sees aggregated PGS candidates
    from ALL Pick bundles (not just rank-1) and chooses the single best
    primary plus an ordered frontier across bundles.

    This is ranking across the Pick output, not a new retrieval.
    """

    primary_pgs_id: str
    ordered_frontier_pgs_ids: list[str]
    rationale: str = ""


# ---------------------------------------------------------------------------
# Critic (Stage 5)
# ---------------------------------------------------------------------------

class CritiqueDecision(BaseModel):
    kept: bool = Field(
        description="If True, the pre-critic frontier is accepted unchanged.",
    )
    revised_frontier: Optional[list[FrontierModel]] = None
    revised_primary_pgs_id: Optional[str] = None
    rationale: str = ""


# ---------------------------------------------------------------------------
# Sentinel — forbidden fields are validated by a separate lint test, not
# enforced at runtime here. Keeping the list as a constant so the lint test
# has a single source of truth.
# ---------------------------------------------------------------------------

FORBIDDEN_SCHEMA_FIELDS: tuple[str, ...] = (
    "archetype",
    "phenotype_fidelity_score",
    "utility_score",
    "selection_priority_score",
    "transferability_prior_score",
    "cheap_rank_score",
    "evidence_tags",
    "weighted_overlap",
    "confidence_level",
    "confidence_tier",
    "genetic_support_present",
)
