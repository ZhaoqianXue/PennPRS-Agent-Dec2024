from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ConfidenceLabel = Literal["High", "Moderate", "Low"]
DecisionMode = Literal["single_confident", "frontier_uncertain", "abstain_only_if_no_valid_bundle"]


class TraitResolutionHit(BaseModel):
    id: str
    label: str
    score: float
    source: str


class TraitResolution(BaseModel):
    query: str
    system: Literal["gwas_atlas", "open_targets"]
    best_id: Optional[str] = None
    best_label: Optional[str] = None
    matched_text: Optional[str] = None
    confidence: Literal["High", "Moderate", "Low", "Unresolved"] = "Unresolved"
    alternatives: list[TraitResolutionHit] = Field(default_factory=list)
    unavailable_reason: Optional[str] = None


class GeneticCorrelationPairOption(BaseModel):
    target_trait_id: Optional[int] = None
    target_trait_label: Optional[str] = None
    candidate_trait_id: Optional[int] = None
    candidate_trait_label: Optional[str] = None
    score: float = 0.0


class GeneticCorrelationEvidence(BaseModel):
    source: str = "gwas_atlas"
    target_resolution: TraitResolution
    candidate_resolution: TraitResolution
    pair_status: str
    best_pair: Optional[GeneticCorrelationPairOption] = None
    alternative_pairs: list[GeneticCorrelationPairOption] = Field(default_factory=list)
    rg: Optional[float] = None
    z_score: Optional[float] = None
    p_value: Optional[float] = None
    study_count: Optional[int] = None
    provenance_status: str = "not_available"
    evidence_strength: str = "Unavailable"
    unavailable_reason: Optional[str] = None


class HeritabilityDatum(BaseModel):
    trait_name: str
    trait_id: Optional[str] = None
    h2_obs: Optional[float] = None
    h2_obs_se: Optional[float] = None
    population: Optional[str] = None
    source: Optional[str] = None
    n_samples: Optional[int] = None
    method: Optional[str] = None
    h2_z: Optional[float] = None
    match_score: float = 0.0


class HeritabilityEvidence(BaseModel):
    source: str = "aggregated"
    ancestry: str = "EUR"
    target_profile: list[HeritabilityDatum] = Field(default_factory=list)
    candidate_profile: list[HeritabilityDatum] = Field(default_factory=list)
    target_best_h2: Optional[float] = None
    candidate_best_h2: Optional[float] = None
    candidate_signal_capacity: Optional[float] = None
    shared_signal_ceiling_proxy: Optional[float] = None
    confidence_tier: str = "Low"
    unavailable_reason: Optional[str] = None


class OpenTargetsSharedTarget(BaseModel):
    target_id: str
    symbol: str
    source_score: float
    candidate_score: float
    min_score: float
    weighted_overlap: float
    source_datatype_scores: dict[str, float] = Field(default_factory=dict)
    candidate_datatype_scores: dict[str, float] = Field(default_factory=dict)
    pathways: list[str] = Field(default_factory=list)
    druggability: str = "Unknown"


class OpenTargetsEvidence(BaseModel):
    source: str = "open_targets"
    target_resolution: TraitResolution
    candidate_resolution: TraitResolution
    pair_status: str
    source_association_count: int = 0
    candidate_association_count: int = 0
    weighted_shared_target_overlap_score: float = 0.0
    shared_target_count: int = 0
    top_shared_targets: list[OpenTargetsSharedTarget] = Field(default_factory=list)
    top_source_targets: list[dict[str, Any]] = Field(default_factory=list)
    top_candidate_targets: list[dict[str, Any]] = Field(default_factory=list)
    shared_pathway_clusters: list[str] = Field(default_factory=list)
    pathway_specificity: str = "unknown"
    target_clinical_candidate_count: Optional[int] = None
    candidate_clinical_candidate_count: Optional[int] = None
    literature_dominance_warning: bool = False
    genetic_support_present: bool = False
    confidence_level: str = "Low"
    mechanism_summary: Optional[str] = None
    unavailable_reason: Optional[str] = None


class CandidateEvidenceCard(BaseModel):
    bundle_id: str
    canonical_label: str
    bundle_type: str
    candidate_pgs_ids: list[str] = Field(default_factory=list)
    n_models: int = 0
    archetype: str
    phenotype_fidelity: str
    phenotype_fidelity_score: float
    lexical_match_score: int = 0
    shared_token_count: int = 0
    cheap_rank_score: float = 0.0
    utility_score: float = 0.0
    evidence_tags: list[str] = Field(default_factory=list)
    gc: Optional[GeneticCorrelationEvidence] = None
    h2: Optional[HeritabilityEvidence] = None
    open_targets: Optional[OpenTargetsEvidence] = None


class EvidenceState(BaseModel):
    available_tools: list[str] = Field(default_factory=list)
    shortlist_bundle_ids: list[str] = Field(default_factory=list)
    target_summary: dict[str, Any] = Field(default_factory=dict)
    candidate_cards: list[CandidateEvidenceCard] = Field(default_factory=list)


class JudgeFrontierSelection(BaseModel):
    primary_bundle_id: Optional[str] = None
    frontier_bundle_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLabel
    decision_mode: DecisionMode
    rationale: str
    evidence_tags: list[str] = Field(default_factory=list)


class VerifiedSelection(BaseModel):
    confidence: ConfidenceLabel
    decision_mode: DecisionMode
    rationale: str
    evidence_tags: list[str] = Field(default_factory=list)
    supported: bool = True
    issues: list[str] = Field(default_factory=list)


class CrossTraitTransferFrontierDecision(BaseModel):
    primary_bundle_id: Optional[str] = None
    frontier_bundle_ids: list[str] = Field(default_factory=list)
    frontier_bundle_weights: dict[str, float] = Field(default_factory=dict)
    candidate_pgs_ids_union: list[str] = Field(default_factory=list)
    confidence: ConfidenceLabel
    decision_mode: DecisionMode
    rationale: str
    evidence_state: EvidenceState
    bundle_evidence_tags: dict[str, list[str]] = Field(default_factory=dict)
    frontier_oracle_hit: Optional[bool] = None

    # Compatibility fields for existing batch/eval pipeline.
    outcome: Literal["MATCHED", "NO_MATCH"] = "NO_MATCH"
    best_bundle_id: Optional[str] = None
    best_cross_trait: Optional[str] = None
    candidate_pgs_ids: list[str] = Field(default_factory=list)


TRANSFER_FRONTIER_JUDGE_PROMPT = """# Identity
You are a PRS Co-scientist selecting a cross-trait transfer frontier.

# Task
Choose the best transfer frontier from the evidence cards.

# Hard Rules
- This agent is general-trait only. Do not use any trait-family-specific prior or prompt template.
- Use only the evidence card fields that are explicitly present.
- Evaluate candidates only on these four axes:
  1. statistical_overlap
  2. mechanistic_overlap
  3. signal_capacity
  4. phenotype_fidelity
- Strongly penalize only `administrative/exposure/treatment/family-history proxy`.
- Do NOT automatically penalize `composite liability trait` or `mechanistic endophenotype / organ-function measurement`.
- Do not abstain if at least one valid non-self candidate exists.
- `single_confident` requires a clearly best candidate with evidence closure on either significant GC or clearly supported Open Targets overlap.
- Otherwise prefer `frontier_uncertain` and keep up to 3 bundles.

# Selection Guidance
- Read all evidence cards before deciding.
- Treat `utility_score` as a hint, not a rule.
- Prefer explanations that can be mapped to explicit evidence fields.
- If the top card has missing GC and weak OT but remains best on phenotype fidelity, lower confidence.
- If a composite or endophenotype candidate has strong GC or mechanistic support, it can outrank a same-family disease candidate.

# Output
Return one JSON object only.
"""


TRANSFER_FRONTIER_VERIFY_PROMPT = """# Identity
You are a verifier for cross-trait transfer decisions.

# Task
Audit the proposed frontier selection against the evidence cards.

# Rules
- Keep the selected frontier fixed unless it contains an invalid bundle id.
- Rewrite the rationale so every scientific claim is grounded in explicit card fields.
- Lower confidence when the rationale overclaims.
- Never inject trait-specific world knowledge that is absent from the evidence cards.
- Evidence tags must be a subset of tags visible in the selected cards.

# Output
Return one JSON object only.
"""
