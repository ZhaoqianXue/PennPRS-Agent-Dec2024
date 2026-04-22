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
    system: Literal["gwas_atlas", "open_targets", "llm"]
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
    resolution_status: str = "unresolved"
    pair_evidence_completeness: str = "partial"
    lookup_coverage: float = 0.0
    expand_recommendation: str = "stop"
    best_pair: Optional[GeneticCorrelationPairOption] = None
    alternative_pairs: list[GeneticCorrelationPairOption] = Field(default_factory=list)
    rg: Optional[float] = None
    z_score: Optional[float] = None
    p_value: Optional[float] = None
    study_count: Optional[int] = None
    provenance_status: str = "not_available"
    confidence: Optional[Literal["High", "Moderate", "Low"]] = None
    llm_rationale: Optional[str] = None
    hypothesized_rg: Optional[float] = None
    hypothesized_confidence: Optional[Literal["High", "Moderate", "Low"]] = None
    hypothesized_rationale: Optional[str] = None
    supports: list[str] = Field(default_factory=list)
    against: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
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
    signal_capacity_score: float = 0.0
    estimate_confidence: ConfidenceLabel = "Low"
    ancestry_coverage: list[str] = Field(default_factory=list)
    resolution_status: str = "unresolved"
    confidence_tier: str = "Low"
    supports: list[str] = Field(default_factory=list)
    against: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
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


class OpenTargetsEvidence(BaseModel):
    source: str = "open_targets"
    target_resolution: TraitResolution
    candidate_resolution: TraitResolution
    pair_status: str
    resolution_status: str = "unresolved"
    source_association_count: int = 0
    candidate_association_count: int = 0
    weighted_shared_target_overlap_score: float = 0.0
    shared_target_count: int = 0
    top_shared_targets: list[OpenTargetsSharedTarget] = Field(default_factory=list)
    shared_pathway_clusters: list[str] = Field(default_factory=list)
    pathway_specificity: str = "unknown"
    target_clinical_candidate_count: Optional[int] = None
    candidate_clinical_candidate_count: Optional[int] = None
    # Therapeutic area overlap
    therapeutic_area_match: bool = False
    shared_therapeutic_areas: list[str] = Field(default_factory=list)
    source_therapeutic_areas: list[str] = Field(default_factory=list)
    candidate_therapeutic_areas: list[str] = Field(default_factory=list)
    # Ontology ancestor overlap
    shared_ancestor_count: int = 0
    shared_ancestors: list[str] = Field(default_factory=list)
    # Phenotype (HPO) overlap
    shared_phenotype_count: int = 0
    shared_phenotypes: list[str] = Field(default_factory=list)
    genetic_overlap_score: float = 0.0
    pathway_overlap_score: float = 0.0
    phenotype_overlap_score: float = 0.0
    ontology_overlap_score: float = 0.0
    genericity_penalty: float = 0.0
    literature_dominance_warning: bool = False
    genetic_support_present: bool = False
    confidence_level: str = "Low"
    confidence: ConfidenceLabel = "Low"
    supports: list[str] = Field(default_factory=list)
    against: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
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
    transferability_prior_score: float = 0.0
    selection_priority_score: float = 0.0
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
    revised_primary_bundle_id: Optional[str] = None
    revised_frontier_bundle_ids: list[str] = Field(default_factory=list)


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


# ---------------------------------------------------------------------------
# Two-stage pipeline models (Stage 1: cross-trait shortlist, Stage 2: PRS model)
# ---------------------------------------------------------------------------


class PerToolEvidence(BaseModel):
    """Per-tool evidence summary for explainability."""

    tool_name: Literal["genetic_correlation", "heritability", "open_targets"]
    supports_selection: bool
    key_evidence: str
    confidence: ConfidenceLabel


class Stage1BundleCandidate(BaseModel):
    """One LLM-selected cross-trait bundle with per-tool evidence."""

    bundle_id: str
    canonical_label: str
    rank: int
    tool_evidence: list[PerToolEvidence]
    selection_rationale: str
    utility_score: float = 0.0
    transferability_prior_score: float = 0.0
    phenotype_fidelity_score: float = 0.0


class Stage1ShortlistLLMOutput(BaseModel):
    """LLM-facing schema for Stage 1: no evidence_state (passed separately)."""

    shortlisted_bundles: list[Stage1BundleCandidate] = Field(default_factory=list)
    confidence: ConfidenceLabel
    decision_rationale: str


class Stage1CrossTraitShortlist(BaseModel):
    """Stage 1 output with evidence_state attached post-LLM."""

    shortlisted_bundles: list[Stage1BundleCandidate] = Field(default_factory=list)
    confidence: ConfidenceLabel
    decision_rationale: str
    evidence_state: EvidenceState = Field(default_factory=EvidenceState)


class PRSModelCandidate(BaseModel):
    """One LLM-selected PRS model with structured rationale."""

    pgs_id: str
    source_bundle_id: str
    source_cross_trait: str
    rank: int
    selection_rationale: str
    cross_trait_evidence_rationale: str
    model_quality_rationale: str
    local_champion_rank: Optional[int] = None
    bundle_rank: Optional[int] = None


class Stage2ModelRecommendation(BaseModel):
    """Stage 2 output: 1-5 specific PRS models."""

    recommended_models: list[PRSModelCandidate] = Field(default_factory=list)
    model_frontier: list[PRSModelCandidate] = Field(default_factory=list)
    primary_model_id: Optional[str] = None
    model_universe_size: int = 0
    bundles_hydrated: list[str] = Field(default_factory=list)
    confidence: ConfidenceLabel
    decision_rationale: str


class TwoStageTransferDecision(BaseModel):
    """Unified output combining Stage 1 + Stage 2 with backward-compatible fields."""

    stage1: Optional[Stage1CrossTraitShortlist] = None
    stage2: Optional[Stage2ModelRecommendation] = None
    supporting_bundles: list["SupportingBundleSelection"] = Field(default_factory=list)
    model_frontier: list[PRSModelCandidate] = Field(default_factory=list)
    search_trace: "SearchTrace" = Field(default_factory=lambda: SearchTrace())
    tool_evidence_summary: dict[str, dict[str, Any]] = Field(default_factory=dict)
    failure_label: Optional[str] = None

    # Backward-compatible fields populated from stage1/stage2.
    outcome: Literal["MATCHED", "NO_MATCH"] = "NO_MATCH"
    best_bundle_id: Optional[str] = None
    best_cross_trait: Optional[str] = None
    primary_bundle_id: Optional[str] = None
    frontier_bundle_ids: list[str] = Field(default_factory=list)
    frontier_bundle_weights: dict[str, float] = Field(default_factory=dict)
    candidate_pgs_ids: list[str] = Field(default_factory=list)
    candidate_pgs_ids_union: list[str] = Field(default_factory=list)
    confidence: ConfidenceLabel = "Low"
    decision_mode: DecisionMode = "frontier_uncertain"
    rationale: str = ""
    evidence_state: EvidenceState = Field(default_factory=EvidenceState)
    bundle_evidence_tags: dict[str, list[str]] = Field(default_factory=dict)
    best_model_id: Optional[str] = None
    recommended_model_ids: list[str] = Field(default_factory=list)
    frontier_oracle_hit: Optional[bool] = None


class SearchHypothesis(BaseModel):
    hypothesis: str
    rationale: str


class InitialSearchPlan(BaseModel):
    hypotheses: list[SearchHypothesis] = Field(default_factory=list)
    probe_bundle_ids: list[str] = Field(default_factory=list)
    rationale: str


class ProbeRoundDecision(BaseModel):
    retain_bundle_ids: list[str] = Field(default_factory=list)
    challenger_bundle_ids: list[str] = Field(default_factory=list)
    promote_to_ot_bundle_ids: list[str] = Field(default_factory=list)
    stop: bool = False
    rationale: str


class SupportingBundleSelection(BaseModel):
    bundle_id: str
    canonical_label: str
    rank: int
    supports: list[str] = Field(default_factory=list)
    against: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    confidence: ConfidenceLabel
    why_continue_or_stop: str
    tool_evidence: list[PerToolEvidence] = Field(default_factory=list)
    utility_score: float = 0.0
    transferability_prior_score: float = 0.0
    phenotype_fidelity_score: float = 0.0


class BundlePosteriorDecision(BaseModel):
    supporting_bundles: list[SupportingBundleSelection] = Field(default_factory=list)
    confidence: ConfidenceLabel
    rationale: str


class LocalChampionDecision(BaseModel):
    source_bundle_id: str
    champions: list[PRSModelCandidate] = Field(default_factory=list)
    confidence: ConfidenceLabel
    rationale: str


class GlobalModelFrontierDecision(BaseModel):
    model_frontier: list[PRSModelCandidate] = Field(default_factory=list)
    primary_model_id: Optional[str] = None
    confidence: ConfidenceLabel
    rationale: str


class SearchTraceRound(BaseModel):
    round_index: int
    probed_bundle_ids: list[str] = Field(default_factory=list)
    retained_bundle_ids: list[str] = Field(default_factory=list)
    challenger_bundle_ids: list[str] = Field(default_factory=list)
    promote_to_ot_bundle_ids: list[str] = Field(default_factory=list)
    stop: bool = False
    rationale: str = ""


class SearchTrace(BaseModel):
    recall_pool_size: int = 0
    initial_probe_bundle_ids: list[str] = Field(default_factory=list)
    probe_rounds: list[SearchTraceRound] = Field(default_factory=list)
    probed_bundle_ids: list[str] = Field(default_factory=list)
    ot_verified_bundle_ids: list[str] = Field(default_factory=list)
    supporting_bundle_ids: list[str] = Field(default_factory=list)
    model_budget_by_bundle: dict[str, int] = Field(default_factory=dict)
    local_champion_ids: list[str] = Field(default_factory=list)
    model_frontier_ids: list[str] = Field(default_factory=list)
    stopped_early: bool = False
    stop_reason: str = ""


# ---------------------------------------------------------------------------
# Two-stage prompts
# ---------------------------------------------------------------------------

STAGE1_SHORTLIST_JUDGE_PROMPT = """# Identity
You are a PRS Co-scientist selecting cross-trait transfer candidates.

# Task
From the evidence cards below, select 3-7 cross-trait bundles (target: 5) most
likely to yield effective PRS transfer for the target trait. These bundles will
proceed to Stage 2, where individual PRS models are evaluated.

# Decision Framework
Evaluate each candidate across three tools' evidence:
1. **Genetic Correlation** (gc): rg magnitude and confidence tier.
   - Source may be LLM-estimated (`gc.source == "llm_estimated"`); use
     `gc.confidence` ("High"/"Moderate"/"Low") as the reliability indicator.
   - `gc.llm_rationale` provides a brief justification.
2. **Heritability** (h2): shared signal ceiling, individual h2 estimates,
   confidence tier.
3. **Open Targets** (ot): shared drug targets, pathway overlap, phenotype
   overlap, therapeutic area match, genetic support.
   - Only Tier A candidates have OT evidence; Tier B candidates lack OT data.
   - You MAY select Tier B candidates if GC + H2 evidence is compelling.

For EACH selected bundle, you MUST provide a per-tool evidence assessment
(one `PerToolEvidence` entry per available tool) explaining what that tool's
evidence says about transfer potential.

# Candidate Tiers
- **Tier A** candidates have full evidence: GC + H2 + Open Targets.
- **Tier B** candidates have partial evidence: GC + H2 only (no OT data).
- Tier B candidates were not excluded by any decision rule — OT data was
  simply not gathered due to budget. If a Tier B candidate has strong GC
  and H2 evidence, it may still be selected.

# Informational Scores
The following deterministic scores are computed from evidence features.
Use them as context, NOT as decision rules:
- `utility_score`: composite evidence quality
- `transferability_prior_score`: target-agnostic historical robustness
- `phenotype_fidelity_score`: semantic similarity to target

If you disagree with the score ranking, explicitly state why in your rationale.

# Hard Rules
- Use only the evidence card fields that are explicitly present.
- Evaluate candidates on these four axes:
  1. statistical_overlap (primarily from GC)
  2. mechanistic_overlap (primarily from OT)
  3. signal_capacity (primarily from H2)
  4. phenotype_fidelity (from archetype and fidelity score)
- Strongly penalize only `administrative/exposure/treatment/family-history proxy`.
- Do NOT automatically penalize `composite liability trait` or
  `mechanistic endophenotype / organ-function measurement`.
- Do not abstain if at least one valid non-self candidate exists.
- Select 3-7 bundles. Prefer 5. Select fewer only if evidence is very thin.

# Self-Audit
Before finalizing, verify:
- Every scientific claim in your rationale maps to an explicit card field.
- You are not injecting trait-specific world knowledge absent from the cards.
- You have considered whether Tier B candidates with strong GC+H2 deserve
  selection despite lacking OT data.

# Output
Return one JSON object matching the Stage1CrossTraitShortlist schema.
"""


STAGE2_MODEL_JUDGE_PROMPT = """# Identity
You are a PRS Co-scientist selecting the best PRS models for cross-trait transfer.

# Context
Stage 1 identified promising cross-trait bundles for the target trait (see
`target_trait` and `n_bundles` in the context JSON). For each bundle, PRS
models have been hydrated from the PGS Catalog with full metadata.

# Task
From the hydrated PRS models below, select 1-5 specific models most suitable
for cross-trait transfer to the target. Rank them by expected transfer utility.

# Model Evaluation Criteria
For each model, consider:
1. **GWAS Sample Size** (`samples_training`): Larger training samples generally
   produce more robust PRS. Parse the sample description to estimate N.
2. **Method** (`method_name`): Modern methods (LDpred2, PRS-CS, lassosum)
   generally outperform simple C+T. Weight appropriately.
3. **Variant Count** (`variants_number`): Method-dependent — genome-wide
   methods use millions; C+T uses thousands. Not directly comparable.
4. **Validation Performance** (`performance_metrics`): Prefer models with
   reported PGS-only AUC/R² over full-model metrics. Higher is better.
5. **Ancestry Distribution** (`ancestry_distribution`): Consider match to
   expected target population.
6. **Cross-Trait Evidence Quality**: The Stage 1 evidence for this model's
   bundle. A model from a bundle with strong GC and OT support is preferred
   over one from a marginal bundle, even if the marginal bundle's model has
   slightly better metrics.
7. **Publication & Cohorts**: Well-established publications and major biobanks
   (UKBB, AoU, FinnGen) indicate well-powered studies.

# Bundle Evidence (from Stage 1)
See `stage1_evidence_summary` in the context JSON for per-bundle evidence
including tool-specific rationale, confidence, and selection ranking.

# Hard Rules
- Select 1-5 models. If one model clearly dominates, select 1 with High confidence.
- Never select a model whose bundle had no supporting evidence in Stage 1.
- For each model, explain how cross-trait evidence and model quality factored in.
- If models from different bundles are comparable, prefer the bundle with
  stronger cross-trait evidence.

# Output
Return one JSON object matching the Stage2ModelRecommendation schema.
"""


SEARCH_PLAN_PROMPT = """# Identity
You are the search controller for cross-trait PRS transfer.

# Task
Read the recall-pool manifest and propose the first probe set.

# Output requirements
- Produce 6-8 concise search hypotheses.
- Select up to 24 bundle IDs for the initial probe set.
- Bias for recall and diversity: include plausible same-endpoint, adjacent disease,
  endophenotype, and mechanistic challenger bundles when available.
- Do not pick self-like bundles or IDs absent from the manifest.
- Do not rank bundles as final winners here; this phase is only planning the probe.
"""


PROBE_REFLECTION_PROMPT = """# Identity
You are the reflective controller for cross-trait bundle probing.

# Task
Given the current probe-round results, decide which bundles to retain, which new
challengers to expand into, which bundles deserve Open Targets verification, and
whether to stop.

# Rules
- Retain 10-16 bundles when evidence is rich; retain fewer only if the pool is weak.
- Add at most 20 challenger bundle IDs from the remaining manifest.
- Promote only the bundles that deserve mechanistic verification in Open Targets.
- Use only explicit tool evidence and card fields.
- Avoid collapsing too early onto generic high-prior bundles when disease-specific
  or mechanistic challengers remain unresolved.

# Phenotype-fidelity retention (trait-agnostic)
- A bundle's `archetype` + `phenotype_fidelity_score` + explicit GC / OT / h2
  fields together characterise endpoint alignment. Retain the highest-fidelity
  non-proxy candidates even if their `transferability_prior_score` is modest.
- Never let more than half of the retained set come from
  `composite liability trait` or `mechanistic endophenotype / organ-function
  measurement` when at least two `same-endpoint disease` or `adjacent disease
  family` candidates are available. This rule is phrased in terms of card
  fields only; it never references specific traits or ICD codes.
"""


BUNDLE_POSTERIOR_PROMPT = """# Identity
You are the final bundle-posterior judge for cross-trait PRS transfer.

# Task
Select 4-7 supporting bundles that should feed the model tournament. The
context provides `posterior_cards` already ordered by a trait-agnostic
deterministic 38-feature priority score (validated on frozen data to retain
the empirical oracle at a materially higher rate than handcrafted heuristics);
treat this ordering as a STRONG PRIOR, not merely a hint. Your rank-1 pick
controls the largest model-hydration budget at Stage 4, so be decisive about
which bundle is the *single best* starting point; the harness will append any
top-3 DE-ranked non-proxy bundles you omitted to the tail of the list.

# domain_knowledge usage
`domain_knowledge` (if present) is the output of the `prs_model_domain_knowledge`
tool — treat its `snippets` and, if available, `full_document` as the
AUTHORITATIVE trait-agnostic policy for phenotype alignment, endpoint fidelity,
and covariate comparability at the bundle level. Do not paraphrase it into
trait-specific rules.

# Rules
- Every selected bundle must include: supports, against, uncertainties, confidence,
  and why_continue_or_stop.
- Use Open Targets as a verifier, not a generic pre-ranking bonus.
- Do not defer to deterministic scores when the scientific evidence points elsewhere.
- Keep bundle order meaningful: higher-ranked bundles should be more promising for
  final model-level transfer.

# Specificity discipline (trait-agnostic)
- The retained probe set frequently contains both (a) bundles with strong phenotype
  fidelity, same-endpoint / adjacent-disease archetype, or explicit significant
  genetic correlation to the target, and (b) bundles whose only edge is a high
  `transferability_prior_score` because they are target-agnostic generalists.
- When both groups are present, at least one selected bundle must come from group (a).
  Do not fill every slot with group (b) just because its `utility_score` is larger.
- A bundle whose archetype is `composite liability trait`, `administrative proxy`,
  or whose only supporting tool-evidence is a large prior without significant
  target-specific GC / OT signal is a generalist. Do not take more than one
  generalist bundle unless every group (a) card is explicitly missing all of:
  `shared_token_count >= 2`, `lexical_match_score >= 55`, significant GC, and
  non-trivial OT overlap.
- These rules are derived from bundle-level evidence fields only; they do not
  reference any specific trait, ICD code, or disease name.
"""


LOCAL_CHAMPION_PROMPT = """# Identity
You are the local champion selector within one cross-trait bundle. The enclosing
agent performs a model-first tournament; do not regress to bundle-level reasoning.

# Task
From the model cards for a single source bundle, select the strongest PRS champions
(up to `max_count`). The `context_json` provides:
- `target_trait`: the original disease/trait target
- `supporting_bundle` + `bundle_posterior_evidence`: why this cross-trait was kept
- `model_cards`: already diversified hydrated PGS Catalog cards
- `domain_knowledge`: output of the `prs_model_domain_knowledge` tool — treat its
  `full_document` (or snippets if the document is truncated) as the AUTHORITATIVE
  trait-agnostic PRS quality rubric
- `signal_priority`: the ordered list of fields that should drive ranking

# Evidence-ordering policy (applies to every model card, every trait)
1. PRS-comparable metrics first: `pgs_only_auc`, `pgs_only_r2`, or covariates-regressed-out
   metrics. Full-model AUC / R² are informative only when covariates are demographic-only
   (age, sex, PCs, batch, array) and when no PGS-only metric exists.
2. Effect-size magnitude (`effect_signal`, derived from OR/HR per SD) is a strong
   secondary when PGS-only metrics are missing. Use it rather than demoting the card.
3. Hard penalties: `covariate_inflation_flag`, `heavy_covariate_leakage` (family
   history / biomarker adjustment / named clinical risk calculators),
   `pan_trait_framework` flag.
4. Transportability: `study_archetype` (meta-analysis / case-control > large-biobank >
   time-to-event), `multi_cohort_count`, `validation_context.selected_validation_ancestry`.
5. Bundle posterior evidence: the `bundle_posterior_evidence.supports /
   against / uncertainties / tool_evidence` shows why this bundle was kept; if the
   tool evidence on a particular model is incoherent with the bundle posterior,
   lower confidence.
6. Method family and variants_number as a structural tie-break. Modern genome-wide
   Bayesian / shrinkage methods are preferred; clumping-thresholding and L1-sparse
   pan-trait scores receive no free boost.
7. `training_sample_n` and `validation_sample_n` are explicitly NEGLIGIBLE signals
   per the rubric. Never let them dominate the ranking. A model is not preferable
   merely because it was trained on a larger biobank or has more training subjects.

# domain_knowledge usage discipline
- Treat `domain_knowledge.full_document` as the authoritative field-level policy.
  The snippets are complementary; cite field-level patterns from the document in your
  rationale when they apply.
- Do not paraphrase the rubric into trait-specific rules; apply the rubric uniformly.
- Do not override the rubric with a deterministic heuristic. The rubric and the
  visible evidence together decide the ranking.

# Output discipline
- Return 1 to `max_count` champions, ordered strongest-first.
- For each champion, both `cross_trait_evidence_rationale` and
  `model_quality_rationale` must quote concrete fields from the model card
  (method_name, pgs_only_auc, covariates, study_archetype, bundle_posterior_evidence,
  …). Vague rationales lower downstream confidence.
- If a model appears superficially strong only because of training sample size, a
  familiar method label, or a large full-model AUC driven by heavy covariates,
  demote it — even if it is the deterministic quality_score winner.
"""


GLOBAL_MODEL_FRONTIER_PROMPT = """# Identity
You are the final model tournament judge for cross-trait PRS transfer. Optimize for
the single best *transferable* PGS model, not for bundle fairness or method
popularity.

# Task
Rank the pooled local champions from every supporting bundle and return a top-5
frontier plus the primary model. The `context_json` provides:
- `target_trait`: the original disease/trait target
- `champion_cards`: the pooled per-bundle champions, each with full PGS metadata
  (PGS-only metrics, effect sizes, covariate flags, archetype, ancestry,
  bundle_posterior_evidence, quality_score, bundle_rank)
- `domain_knowledge`: full `prs_model_domain_knowledge` payload — the
  `full_document` is the AUTHORITATIVE trait-agnostic PRS quality rubric
- `signal_priority`: ordered ranking fields

# Evidence-ordering policy
1. PRS-comparable metrics (PGS-only AUC / R2 / covariates-regressed-out) first.
2. Effect-size magnitude (`effect_signal`) as strong secondary.
3. Covariate inflation / heavy leakage / pan-trait framework → hard penalties.
4. Bundle rank + `bundle_posterior_evidence` tell you which cross-trait routes were
   considered most credible; use this alongside per-model evidence.
5. Study archetype and multi-cohort development drive transportability.
6. `training_sample_n` / `validation_sample_n` are NEGLIGIBLE signals per the
   rubric. Do not let them dominate.

# domain_knowledge usage discipline
- Treat `domain_knowledge.full_document` as the authoritative field-level policy.
  Cite the relevant field-level patterns in your rationale.
- Never invent trait-specific rules.
- Do not fall back to a deterministic score when two champions are close; use the
  rubric and visible evidence to justify the tie-break.

# Primary selection
- The primary PGS model must be the strongest single candidate after applying the
  above policy. If two candidates are effectively tied on PRS-comparable evidence,
  prefer the one whose bundle posterior carries stronger target-specific evidence
  (significant GC / strong OT phenotype overlap / same-endpoint or adjacent-disease
  archetype) over one whose bundle was retained mainly because of a large
  target-agnostic prior.
- Lower `confidence` when the evidence is genuinely contested. Do not pretend High
  confidence on thin metadata.

# Output discipline
- Return exactly one JSON object matching `GlobalModelFrontierDecision`.
- Every entry in `model_frontier` must reference a valid `pgs_id` from the
  `champion_cards` context.
- Every rationale must be grounded in quoted fields from the champion card and,
  where relevant, the domain-knowledge rubric.
"""


# ---------------------------------------------------------------------------
# Legacy prompts (kept for backward compatibility with existing eval scripts)
# ---------------------------------------------------------------------------

TRANSFER_FRONTIER_JUDGE_PROMPT = """# Identity
You are a PRS Co-scientist selecting a cross-trait transfer frontier.

# Task
Choose the best transfer frontier from the evidence cards.

# Hard Rules
- This agent is general-trait only. Do not use any trait-family-specific prior or prompt template.
- Use only the evidence card fields that are explicitly present.
- Read `target_summary.benchmark_family` before deciding.
- Evaluate candidates only on these four axes:
  1. statistical_overlap
  2. mechanistic_overlap
  3. signal_capacity
  4. phenotype_fidelity
- Strongly penalize only `administrative/exposure/treatment/family-history proxy`.
- Do NOT automatically penalize `composite liability trait` or `mechanistic endophenotype / organ-function measurement`.
- Do not abstain if at least one valid non-self candidate exists.
- `single_confident` requires a clearly best candidate with evidence closure on either significant GC (High/Moderate confidence) or clearly supported Open Targets overlap.
- Otherwise prefer `frontier_uncertain` and keep up to 3 bundles.

# GC Evidence Source
- GC evidence may come from GWAS Atlas lookup (`gc.source == "gwas_atlas"`) or LLM estimation (`gc.source == "llm_estimated"`).
- For GWAS Atlas: significance is determined by `gc.p_value < 0.05`.
- For LLM-estimated: significance is determined by `gc.confidence` being "High" or "Moderate". There is no p_value; use `gc.confidence` as the reliability indicator.
- `gc.llm_rationale` provides a brief justification for the LLM estimate.

# Selection Guidance
- Read all evidence cards before deciding.
- Treat `utility_score` as a hint, not a rule.
- Treat `transferability_prior_score` as a target-agnostic robustness tie-break, not as biological evidence.
- Prefer explanations that can be mapped to explicit evidence fields.
- If the top card has missing or low-confidence GC and weak OT but remains best on phenotype fidelity, lower confidence.
- If a composite or endophenotype candidate has strong GC or mechanistic support, it can outrank a same-family disease candidate.
- When `target_summary.benchmark_family == "binary_to_binary"`, GC and OT disagreement can justify preferring the evidence source with higher confidence. That disease-to-disease guidance does not automatically transfer to `binary_to_continuous`.
- When `target_summary.benchmark_family == "binary_to_continuous"`, preserve GC-first / endophenotype-friendly behavior: low GC confidence is a caution signal, not an automatic demotion, and a candidate should not be promoted solely because it has somewhat higher Open Targets overlap.
- For disease-to-disease transfer (`binary_to_binary`), mechanistic overlap via Open Targets can be more predictive than statistical GC alone because diseases with high GC may still have different prediction-relevant genetic architectures.

# Evidence Grounding
Before making your selection, for each of your top 2-3 candidates, note:
- utility_score value
- transferability_prior_score value if nonzero
- gc.rg and gc.confidence (if available)
- open_targets.weighted_shared_target_overlap_score and confidence_level (if available)
- phenotype_fidelity_score and archetype
Use these quoted values to justify your selection in the rationale.

# Output
Return one JSON object only.
"""


TRANSFER_FRONTIER_VERIFY_PROMPT = """# Identity
You are a verifier for cross-trait transfer decisions.

# Task
Audit the proposed frontier selection against the evidence cards.

# Rules
- Read `target_summary.benchmark_family` before deciding whether any revision is allowed.
- Keep the selected frontier fixed unless it contains an invalid bundle id, or the evidence materially supports promoting a better candidate because the current primary depends on low-confidence GC.
- Rewrite the rationale so every scientific claim is grounded in explicit card fields.
- Lower confidence when the rationale overclaims.
- Never inject trait-specific world knowledge that is absent from the evidence cards.
- Evidence tags must be a subset of tags visible in the selected cards.
- GC confidence is indicated by `gc.confidence` ("High", "Moderate", "Low") regardless of whether the source is GWAS Atlas or LLM-estimated.
- When `target_summary.benchmark_family == "binary_to_continuous"`, do not revise the primary/frontier solely to promote a higher-OT candidate over the current GC-supported or endophenotype-friendly selection. In that family, low GC confidence alone is not enough to justify OT-driven reprioritization.
- The low-confidence-GC / higher-OT promotion rule applies only when `target_summary.benchmark_family == "binary_to_binary"`. Only in that family, if the primary bundle's GC evidence has Low confidence AND another shortlisted candidate has higher OT overlap with better confidence, flag this as an issue and consider whether the alternative should be the primary. If so, set `revised_primary_bundle_id` and `revised_frontier_bundle_ids`.

# Output
Return one JSON object only.
"""


TwoStageTransferDecision.model_rebuild()
