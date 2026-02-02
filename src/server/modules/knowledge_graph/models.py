"""
Data Models for Knowledge Graph (Module 2).
Implements Trait-Centric schema with Meta-Analysis aggregation per sop.md.

New Models (Trait-Centric):
- TraitNode: Represents a Trait with meta-analyzed h2 and study provenance
- GeneticCorrelationEdgeMeta: Represents an edge with meta-analyzed rg
- TraitCentricGraphResult: Container for trait-centric graph queries

Legacy Models (preserved for backward compatibility):
- KnowledgeGraphNode, GeneticCorrelationEdge, KnowledgeGraphResult, PrioritizedNeighbor
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# NEW TRAIT-CENTRIC MODELS (per sop.md Module 2 spec)
# =============================================================================

class StudyProvenance(BaseModel):
    """Individual study data for provenance tracking."""
    study_id: int = Field(..., description="GWAS Atlas numeric ID")
    pmid: Optional[str] = Field(None, description="PubMed Identifier")
    year: Optional[int] = Field(None, description="Publication year")
    population: Optional[str] = Field(None, description="Ancestry")
    n: Optional[int] = Field(None, description="Sample size")
    snp_h2: Optional[float] = Field(None, description="SNP heritability estimate")
    snp_h2_se: Optional[float] = Field(None, description="SE of h2")
    snp_h2_z: Optional[float] = Field(None, description="Z-score of h2")
    consortium: Optional[str] = Field(None, description="Research consortium")


class TraitNode(BaseModel):
    """
    Represents a Trait Node with meta-analyzed heritability.
    
    Each Trait has exactly ONE node, aggregating ALL Study information.
    Per sop.md: Node Schema (Traits) with h2_meta, h2_se_meta, h2_z_meta, n_studies, studies.
    """
    trait_id: str = Field(..., description="Canonical trait name (uniqTrait). Primary Key.")
    domain: Optional[str] = Field(None, description="Top-level category (e.g., Psychiatric)")
    chapter_level: Optional[str] = Field(None, description="ICD-10 chapter classification")
    h2_meta: Optional[float] = Field(None, description="Meta-analyzed h2 (inverse-variance weighted)")
    h2_se_meta: Optional[float] = Field(None, description="SE of meta-analyzed h2")
    h2_z_meta: Optional[float] = Field(None, description="Z-score of meta-analyzed h2")
    n_studies: int = Field(0, description="Number of Studies aggregated")
    studies: List[Dict[str, Any]] = Field(default_factory=list, description="All Studies for provenance")


class CorrelationProvenance(BaseModel):
    """Individual study-pair correlation for provenance tracking."""
    source_study_id: int = Field(..., description="Source study GWAS Atlas ID")
    target_study_id: int = Field(..., description="Target study GWAS Atlas ID")
    rg: float = Field(..., description="Genetic correlation coefficient")
    se: Optional[float] = Field(None, description="Standard error")
    z: Optional[float] = Field(None, description="Z-score")
    p: Optional[float] = Field(None, description="P-value")


class GeneticCorrelationEdgeMeta(BaseModel):
    """
    Represents a Genetic Correlation Edge with meta-analyzed rg.
    
    Each Trait-pair has exactly ONE edge, aggregating ALL Study-pair correlations.
    Per sop.md: Edge Schema with rg_meta, rg_se_meta, rg_z_meta, rg_p_meta, n_correlations, correlations.
    """
    source_trait: str = Field(..., description="Source trait canonical name")
    target_trait: str = Field(..., description="Target trait canonical name")
    rg_meta: float = Field(..., description="Meta-analyzed rg (inverse-variance weighted)")
    rg_se_meta: Optional[float] = Field(None, description="SE of meta-analyzed rg")
    rg_z_meta: Optional[float] = Field(None, description="Z-score of meta-analyzed rg")
    rg_p_meta: Optional[float] = Field(None, description="P-value of meta-analyzed rg")
    n_correlations: int = Field(0, description="Number of Study-pair correlations aggregated")
    correlations: List[Dict[str, Any]] = Field(default_factory=list, description="All correlations for provenance")


class TraitCentricGraphResult(BaseModel):
    """Response model for trait-centric graph queries."""
    nodes: List[TraitNode] = Field(default_factory=list)
    edges: List[GeneticCorrelationEdgeMeta] = Field(default_factory=list)


# =============================================================================
# LEGACY MODELS (preserved for backward compatibility)
# =============================================================================

class KnowledgeGraphNode(BaseModel):
    """Represents a Trait Node (Legacy)."""
    id: str = Field(..., description="EFO ID or Trait Name")
    label: str = Field(..., description="Display Name")
    h2: Optional[float] = Field(None, description="Heritability")


class GeneticCorrelationEdge(BaseModel):
    """Represents a relationship edge (Legacy)."""
    source: str = Field(..., description="Source Trait ID")
    target: str = Field(..., description="Target Trait ID")
    rg: float = Field(..., description="Genetic Correlation Coefficient")
    p_value: float = Field(..., description="Significance P-value")
    se: Optional[float] = Field(None, description="Standard Error")


class KnowledgeGraphResult(BaseModel):
    """Response model for graph queries (Legacy)."""
    nodes: List[KnowledgeGraphNode] = Field(default_factory=list)
    edges: List[GeneticCorrelationEdge] = Field(default_factory=list)


class PrioritizedNeighbor(BaseModel):
    """
    Represents a neighbor trait with weighted score for prioritization.
    Score = rg^2 * h2 (genetic correlation squared times heritability)
    """
    trait_id: str = Field(..., description="Trait ID (GWAS Atlas numeric ID)")
    trait_name: str = Field(..., description="Trait display name")
    rg: float = Field(..., description="Genetic correlation coefficient")
    h2: float = Field(..., description="Heritability of the correlated trait")
    score: float = Field(..., description="Weighted score: rg^2 * h2")
    p_value: float = Field(..., description="Significance P-value of genetic correlation")
    rg_z: Optional[float] = Field(None, description="Z-score of genetic correlation")
    n_correlations: int = Field(1, description="Number of correlations aggregated")
