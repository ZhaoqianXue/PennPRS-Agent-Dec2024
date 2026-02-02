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


class PGSSearchResult(BaseModel):
    """
    Result from prs_model_pgscatalog_search tool.
    Implements sop.md L369-387 output specification.
    """
    query_trait: str
    total_found: int
    after_filter: int
    models: List[PGSModelSummary]


class MetricDistribution(BaseModel):
    """Statistical distribution for a performance metric."""
    min: float
    max: float
    median: float
    p25: float
    p75: float
    missing_count: int


class TopPerformerSummary(BaseModel):
    """Summary of the top performing model."""
    pgs_id: str
    auc: Optional[float] = None
    r2: Optional[float] = None
    percentile_rank: float


class PerformanceLandscape(BaseModel):
    """
    Result from prs_model_performance_landscape tool.
    Implements sop.md L436-462 output specification.
    Token Budget: ~200 tokens.
    """
    total_models: int
    auc_distribution: MetricDistribution
    r2_distribution: MetricDistribution
    top_performer: TopPerformerSummary
    verdict_context: str


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
    mechanism_summary: str
    confidence_level: str  # High, Moderate, Low


# --- PennPRS Tools Schemas ---

class TrainingConfig(BaseModel):
    """
    Result from pennprs_train_model tool.
    Implements sop.md L572-594 output specification.
    Human-in-the-Loop: UI displays form, user submits.
    Token Budget: ~300 tokens.
    """
    # Pre-filled by Agent
    target_trait: str
    recommended_method: str  # e.g., "LDpred2", "PRS-CS"
    method_rationale: str  # Agent's reasoning for method choice
    
    # Form fields (editable by user)
    gwas_summary_stats: str  # URL or file path
    ld_reference: str  # e.g., "1000G EUR"
    ancestry: str  # Target population
    validation_cohort: Optional[str] = None  # Optional
    
    # Metadata
    agent_confidence: str  # "High", "Moderate", "Low"
    estimated_runtime: str  # e.g., "~2 hours"


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
