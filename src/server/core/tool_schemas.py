# src/server/core/tool_schemas.py
"""
Tool I/O Schemas for Module 3 Tools.
Implements sop.md L352-622 Output Schema specifications.

Schema Design Principles:
- [Agent + UI] fields only for LLM context efficiency
- Structured error objects for Error Trace Retention
- Pydantic v2 for strict validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# --- PRS Model Tools Schemas ---

class PGSModelSummary(BaseModel):
    """
    Summary of a PGS model with [Agent + UI] fields only.
    Implements sop.md L371-387 schema.
    """
    id: str = Field(..., description="Unique Model ID (e.g., PGS000025)")
    trait_reported: str = Field(..., description="Original reported trait")
    trait_efo: str = Field(..., description="EFO Ontology mapping")
    method_name: str = Field(..., description="Algorithm used (e.g., LDpred2)")
    variants_number: int = Field(..., description="Count of variants in model")
    ancestry_distribution: str = Field(..., description="Ancestry breakdown")
    publication: str = Field(..., description="Publication metadata")
    date_release: str = Field(..., description="Date the score was released")
    samples_training: str = Field(..., description="Samples used for training")
    performance_metrics: Dict[str, Optional[float]] = Field(
        ..., description="Metrics (auc, r2, etc.)"
    )
    phenotyping_reported: str = Field(..., description="Phenotype description in validation")
    covariates: str = Field(..., description="Covariates used in validation")
    sampleset: Optional[str] = Field(None, description="Sample set used for validation")
    training_development_cohorts: List[str] = Field(
        default_factory=list,
        description="Union of cohort short names from training/development-related samples"
    )


class PGSSearchResult(BaseModel):
    """
    Result from prs_model_pgscatalog_search tool.
    Implements sop.md L369-387 output specification.
    """
    query_trait: str
    total_found: int
    after_filter: int
    models: List[PGSModelSummary]


class KnowledgeSnippet(BaseModel):
    """A snippet from domain knowledge search."""
    source: str = Field(..., description="Source file or URL")
    section: str = Field(..., description="Section heading")
    content: str = Field(..., description="Relevant content snippet")
    relevance_score: float = Field(0.0, description="Relevance to query (0-1)")


class DomainKnowledgeResult(BaseModel):
    """
    Result from prs_model_domain_knowledge tool.
    Implements sop.md L394-428 output specification.
    Token Budget: ~300 tokens.
    """
    query: str
    snippets: List[KnowledgeSnippet]
    source_type: str = Field("local", description="'local' or 'web'")



class MetricDistribution(BaseModel):
    """Statistical distribution for a numeric metric."""
    min: float
    max: float
    median: float
    p25: float
    p75: float
    missing_count: int


class PerformanceLandscape(BaseModel):
    """
    Result from prs_model_performance_landscape tool.
    Implements sop.md L436-462 output specification.
    Token Budget: ~200 tokens.
    """
    total_models: int
    ancestry: Dict[str, int] = Field(default_factory=dict, description="Counts by ancestry code (best-effort parse)")
    sample_size: MetricDistribution
    auc: MetricDistribution
    r2: MetricDistribution
    variants: MetricDistribution
    training_development_cohorts: Dict[str, int] = Field(default_factory=dict, description="Counts by cohort short name")
    prs_methods: Dict[str, int] = Field(default_factory=dict, description="Counts by PRS method name")


# --- Genetic Graph Tools Schemas ---

class RankedNeighbor(BaseModel):
    """
    A genetically correlated trait with ranking score.
    Implements sop.md L478-493 schema.
    
    NOTE: h2_se_meta, rg_se_meta, rg_p_meta intentionally omitted for token efficiency.
    Use genetic_graph_verify_study_power for detailed provenance if needed.
    """
    trait_id: str = Field(..., description="Trait canonical name")
    domain: str = Field(..., description="Trait domain (e.g., Psychiatric)")
    rg_meta: float = Field(..., description="Meta-analyzed genetic correlation")
    rg_z_meta: float = Field(..., description="Z-score of rg")
    h2_meta: float = Field(..., description="Neighbor's meta-analyzed heritability")
    transfer_score: float = Field(..., description="rg^2 * h2 score")
    n_correlations: int = Field(..., description="Number of study-pairs aggregated")


class NeighborResult(BaseModel):
    """
    Result from genetic_graph_get_neighbors tool.
    Implements sop.md L476-495 output specification.
    Token Budget: ~100 tokens per neighbor; max 10 neighbors.
    """
    # Optional resolution metadata for robust trait matching.
    # These fields allow the agent/UI to understand when a user query was mapped
    # onto a canonical Knowledge Graph trait ID.
    query_trait: Optional[str] = Field(
        default=None,
        description="Original user query trait string (if resolved/mapped)"
    )
    resolved_by: Optional[str] = Field(
        default=None,
        description="Resolution method used: exact | alias | none"
    )
    resolution_confidence: Optional[str] = Field(
        default=None,
        description="Resolution confidence: High | Moderate | Low"
    )
    target_trait: str
    target_h2_meta: float
    neighbors: List[RankedNeighbor]


class CorrelationProvenance(BaseModel):
    """
    Detailed provenance for a single correlation measurement.
    Implements sop.md L510-528 schema.
    """
    study1_id: int
    study1_n: int
    study1_population: str
    study1_pmid: str
    study2_id: int
    study2_n: int
    study2_population: str
    study2_pmid: str
    rg: float
    se: float
    p: float


class StudyPowerResult(BaseModel):
    """
    Result from genetic_graph_verify_study_power tool.
    Implements sop.md L500-530 output specification.
    JIT Loading: Only called for deep quality control.
    Token Budget: ~300 tokens.
    """
    source_trait: str
    target_trait: str
    rg_meta: float
    n_correlations: int
    correlations: List[CorrelationProvenance]


class SharedGene(BaseModel):
    """
    A gene shared between two traits.
    Implements sop.md L549-558 schema.
    """
    gene_symbol: str = Field(..., description="e.g., IL23R")
    gene_id: str = Field(..., description="ENSG ID")
    source_association: float = Field(..., description="Disease A association score")
    target_association: float = Field(..., description="Disease B association score")
    phewas_p_value: Optional[float] = Field(None, description="Significance of gene-phenotype association from PheWAS")
    druggability: str = Field(..., description="High, Medium, Low")
    pathways: List[str] = Field(default_factory=list)


class MechanismValidation(BaseModel):
    """
    Result from genetic_graph_validate_mechanism tool.
    Implements sop.md L534-560 output specification.
    JIT Loading: Only called to justify cross-disease model transfer.
    Token Budget: ~500 tokens.
    """
    source_trait: str
    target_trait: str
    shared_genes: List[SharedGene]
    shared_pathways: List[str]
    phewas_evidence_count: int = Field(0, description="Number of shared genes validated by PheWAS")
    mechanism_summary: str
    confidence_level: str  # High, Moderate, Low


# --- PennPRS Tools Schemas ---

class TrainingConfig(BaseModel):
    """
    Configuration for PennPRS training job.
    Implements sop.md L572-594 output specification.
    Human-in-the-Loop: UI displays form, user submits.
    Token Budget: ~300 tokens.
    
    Based on PennPRSClient.add_single_job parameters.
    """
    # Pre-filled by Agent
    target_trait: str = Field(..., description="Disease/trait name")
    recommended_method: str = Field(..., description="e.g., 'LDpred2', 'PRS-CS'")
    method_rationale: str = Field(..., description="Agent's reasoning for method choice")
    
    # PennPRS API fields
    job_name: str = Field(..., description="Unique job identifier")
    job_type: str = Field("single", description="'single' or 'multiple'")
    job_methods: List[str] = Field(..., description="Methods to use: LDpred2, PRS-CS, Lassosum2, CT-pseudo")
    job_ensemble: bool = Field(False, description="Whether to ensemble multiple methods")
    
    # Trait configuration
    traits_source: str = Field("public", description="'public' (GCST ID) or 'user' (uploaded file)")
    traits_detail: str = Field(..., description="GCST ID or 'FILE:filename'")
    traits_type: str = Field(..., description="'binary' or 'continuous'")
    traits_population: str = Field(..., description="Target population: EUR, EAS, AFR, etc.")
    
    # GWAS data
    gwas_summary_stats: str = Field(..., description="GCST ID or file path")
    ld_reference: str = Field("1000G EUR", description="LD reference panel")
    ancestry: str = Field(..., description="Target ancestry for validation")
    
    # Parameters
    para_dict: Dict[str, Any] = Field(default_factory=dict, description="Method-specific parameters")
    
    # Metadata
    agent_confidence: str = Field(..., description="'High', 'Moderate', 'Low'")
    estimated_runtime: str = Field("~2 hours", description="Estimated job duration")
    
    # Optional
    validation_cohort: Optional[str] = Field(None, description="Validation cohort name")


class JobSubmissionResult(BaseModel):
    """
    Result from pennprs_train_model tool after successful submission.
    """
    success: bool
    job_id: Optional[str] = None
    job_name: str
    status: str  # "submitted", "pending", "error"
    message: str
    config: TrainingConfig  # The configuration that was submitted


# --- Trait Synonym Tools Schemas ---

class TraitSynonym(BaseModel):
    """A synonym or alternative name for a trait."""
    synonym: str = Field(..., description="Alternative name or synonym for the trait")
    relationship: str = Field(..., description="Relationship type: exact_synonym, broader_term, narrower_term, related_term, icd10_code, efo_id, or other")
    confidence: str = Field(..., description="Confidence level: High, Moderate, or Low")
    rationale: Optional[str] = Field(None, description="Brief explanation of why this is a synonym")


class TraitSynonymResult(BaseModel):
    """
    Result from trait_synonym_expand tool.
    Provides synonyms and alternative names for a trait query.
    Token Budget: ~200 tokens.
    """
    original_query: str
    expanded_queries: List[str] = Field(..., description="List of expanded query terms including original")
    synonyms: List[TraitSynonym] = Field(..., description="List of identified synonyms with metadata")
    method: str = Field(..., description="Expansion method: llm, cache, or none")
    confidence: str = Field(..., description="Overall confidence: High, Moderate, or Low")


# --- Error Schema ---

class ToolError(BaseModel):
    """
    Structured error for tool failures.
    Supports Error Trace Retention (sop.md L609).
    Failed tool calls remain in history with error details for Agent learning.
    """
    tool_name: str
    error_type: str
    error_message: str
    context: Dict[str, Any] = Field(default_factory=dict)
