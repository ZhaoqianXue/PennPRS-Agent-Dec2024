"""
Data Models for Literature Mining Engine

Defines Pydantic models for:
- Paper metadata from PubMed
- Classification results
- Extracted data (PRS, h², rg)
- Validation results

All models are designed to be compatible with PGS Catalog schema
for seamless integration with existing frontend components.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class PaperCategory(str, Enum):
    """Categories for literature classification."""
    PRS_PERFORMANCE = "PRS_PERFORMANCE"
    HERITABILITY = "HERITABILITY"
    GENETIC_CORRELATION = "GENETIC_CORRELATION"
    NOT_RELEVANT = "NOT_RELEVANT"


class DataSource(str, Enum):
    """Data source identifiers."""
    PGS_CATALOG = "pgs_catalog"
    LITERATURE_MINING = "literature_mining"


class PRSMethod(str, Enum):
    """Common PRS methods."""
    PRS_CS = "PRS-CS"
    LDPRED2 = "LDpred2"
    CT = "C+T"  # Clumping and Thresholding
    LASSOSUM = "lassosum"
    SBLUP = "SBLUP"
    SBAYESR = "SBayesR"
    DBSLMM = "DBSLMM"
    MEGAPRS = "MegaPRS"
    PRSICE = "PRSice"
    OTHER = "other"


class HeritabilityMethod(str, Enum):
    """Common heritability estimation methods."""
    LDSC = "LDSC"
    GCTA = "GCTA"
    GREML = "GREML"
    BOLT_REML = "BOLT-REML"
    OTHER = "other"


class GeneticCorrelationMethod(str, Enum):
    """Common genetic correlation estimation methods."""
    LDSC = "LDSC"
    HDL = "HDL"
    GNOVA = "GNOVA"
    SUPERGNOVA = "SuperGNOVA"
    OTHER = "other"


class ValidationStatus(str, Enum):
    """Status after validation."""
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"
    DUPLICATE = "duplicate"


# ============================================================================
# Paper Metadata
# ============================================================================

class PaperMetadata(BaseModel):
    """Metadata for a paper from PubMed."""
    pmid: str = Field(..., description="PubMed ID")
    title: str = Field(..., description="Paper title")
    abstract: str = Field(default="", description="Paper abstract")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: str = Field(default="", description="Journal name")
    publication_date: Optional[date] = Field(default=None, description="Publication date")
    doi: Optional[str] = Field(default=None, description="DOI")
    keywords: List[str] = Field(default_factory=list, description="Keywords/MeSH terms")
    full_text_url: Optional[str] = Field(default=None, description="Link to full text if available")
    
    # Processing metadata
    retrieved_at: datetime = Field(default_factory=datetime.now, description="When the paper was retrieved")
    
    @property
    def pubmed_url(self) -> str:
        """Generate PubMed URL from PMID."""
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


# ============================================================================
# Classification Results
# ============================================================================

class CategoryScore(BaseModel):
    """Score for a single category."""
    category: PaperCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = Field(default=None)


class ClassificationResult(BaseModel):
    """Result of paper classification by the Classifier Agent."""
    pmid: str
    categories: List[CategoryScore] = Field(default_factory=list)
    primary_category: PaperCategory = Field(default=PaperCategory.NOT_RELEVANT)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    llm_reasoning: Optional[str] = Field(default=None, description="LLM's explanation")
    
    # Processing metadata
    classified_at: datetime = Field(default_factory=datetime.now)
    model_used: str = Field(default="gpt-4")
    
    @property
    def is_relevant(self) -> bool:
        """Check if paper is relevant for any extraction."""
        return self.primary_category != PaperCategory.NOT_RELEVANT
    
    @property
    def has_prs(self) -> bool:
        return any(c.category == PaperCategory.PRS_PERFORMANCE for c in self.categories if c.confidence > 0.5)
    
    @property
    def has_heritability(self) -> bool:
        return any(c.category == PaperCategory.HERITABILITY for c in self.categories if c.confidence > 0.5)
    
    @property
    def has_genetic_correlation(self) -> bool:
        return any(c.category == PaperCategory.GENETIC_CORRELATION for c in self.categories if c.confidence > 0.5)


# ============================================================================
# PRS Model Extraction
# ============================================================================

class PRSModelExtraction(BaseModel):
    """Extracted PRS model data from literature.
    
    Schema designed for compatibility with PGS Catalog,
    enabling unified display in ModelGrid component.
    """
    # Identifiers
    id: str = Field(default="", description="Generated ID (e.g., LIT-AD-2024-001)")
    source: DataSource = Field(default=DataSource.LITERATURE_MINING)
    pmid: str = Field(..., description="Source paper PMID")
    
    # Core model info
    name: Optional[str] = Field(default=None, description="Model name if provided")
    trait: str = Field(..., description="Target trait/disease")
    trait_efo: Optional[str] = Field(default=None, description="EFO ID if identifiable")
    
    # Performance metrics (at least one should be present)
    auc: Optional[float] = Field(default=None, ge=0.5, le=1.0, description="Area Under ROC Curve")
    r2: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Variance explained")
    c_index: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="C-statistic for survival")
    or_per_sd: Optional[float] = Field(default=None, description="Odds ratio per SD")
    
    # Model characteristics
    variants_number: Optional[int] = Field(default=None, ge=1, description="Number of variants")
    method: Optional[PRSMethod] = Field(default=None, description="PRS construction method")
    method_detail: Optional[str] = Field(default=None, description="Additional method details")
    
    # Population info
    sample_size: Optional[int] = Field(default=None, ge=1, description="Sample size")
    ancestry: Optional[str] = Field(default=None, description="Primary ancestry")
    ancestry_broad: Optional[str] = Field(default=None, description="Broad ancestry category")
    cohort: Optional[str] = Field(default=None, description="Cohort name(s)")
    
    # GWAS info
    gwas_id: Optional[str] = Field(default=None, description="GCST ID if available")
    gwas_source: Optional[str] = Field(default=None, description="Source of GWAS data")
    
    # Publication info
    publication: Optional[str] = Field(default=None, description="Citation string")
    publication_year: Optional[int] = Field(default=None)
    
    # Extraction metadata
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extracted_at: datetime = Field(default_factory=datetime.now)
    raw_text_snippet: Optional[str] = Field(default=None, description="Source text for traceability")
    
    @field_validator('auc', 'c_index', mode='before')
    @classmethod
    def validate_auc_range(cls, v):
        """AUC and C-index should be between 0.5 and 1.0 for valid discriminative models."""
        if v is not None and v < 0.5:
            return None  # Invalid value, likely a parsing error
        return v
    
    def generate_id(self, sequence: int = 1) -> str:
        """Generate a unique ID for this extraction."""
        trait_abbr = self.trait[:3].upper() if self.trait else "UNK"
        year = self.publication_year or datetime.now().year
        self.id = f"LIT-{trait_abbr}-{year}-{sequence:03d}"
        return self.id


# ============================================================================
# Heritability Extraction
# ============================================================================

class HeritabilityExtraction(BaseModel):
    """Extracted heritability (h²) estimate from literature."""
    # Identifiers
    id: str = Field(default="", description="Generated ID")
    source: DataSource = Field(default=DataSource.LITERATURE_MINING)
    pmid: str = Field(..., description="Source paper PMID")
    
    # Core data
    trait: str = Field(..., description="Target trait/disease")
    trait_efo: Optional[str] = Field(default=None, description="EFO ID if identifiable")
    h2: float = Field(..., ge=0.0, le=1.0, description="SNP-heritability estimate")
    se: Optional[float] = Field(default=None, ge=0.0, description="Standard error")
    
    # Method info
    method: Optional[HeritabilityMethod] = Field(default=None)
    method_detail: Optional[str] = Field(default=None)
    
    # Population info
    sample_size: Optional[int] = Field(default=None, ge=1)
    ancestry: Optional[str] = Field(default=None)
    
    # Publication info
    publication: Optional[str] = Field(default=None)
    publication_year: Optional[int] = Field(default=None)
    
    # Extraction metadata
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extracted_at: datetime = Field(default_factory=datetime.now)
    raw_text_snippet: Optional[str] = Field(default=None)
    
    @field_validator('h2', mode='before')
    @classmethod
    def validate_h2_range(cls, v):
        """h² must be between 0 and 1."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError(f"h² must be between 0 and 1, got {v}")
        return v


# ============================================================================
# Genetic Correlation Extraction
# ============================================================================

class GeneticCorrelationExtraction(BaseModel):
    """Extracted genetic correlation (rg) data from literature."""
    # Identifiers
    id: str = Field(default="", description="Generated ID")
    source: DataSource = Field(default=DataSource.LITERATURE_MINING)
    pmid: str = Field(..., description="Source paper PMID")
    
    # Core data
    trait1: str = Field(..., description="First trait")
    trait1_efo: Optional[str] = Field(default=None)
    trait2: str = Field(..., description="Second trait")
    trait2_efo: Optional[str] = Field(default=None)
    rg: float = Field(..., ge=-1.0, le=1.0, description="Genetic correlation")
    se: Optional[float] = Field(default=None, ge=0.0, description="Standard error")
    p_value: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Method info
    method: Optional[GeneticCorrelationMethod] = Field(default=None)
    method_detail: Optional[str] = Field(default=None)
    
    # Population info
    sample_size: Optional[int] = Field(default=None, ge=1)
    ancestry: Optional[str] = Field(default=None)
    
    # Publication info
    publication: Optional[str] = Field(default=None)
    publication_year: Optional[int] = Field(default=None)
    
    # Extraction metadata
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extracted_at: datetime = Field(default_factory=datetime.now)
    raw_text_snippet: Optional[str] = Field(default=None)
    
    @field_validator('rg', mode='before')
    @classmethod
    def validate_rg_range(cls, v):
        """rg must be between -1 and 1."""
        if v is not None and (v < -1 or v > 1):
            raise ValueError(f"rg must be between -1 and 1, got {v}")
        return v


# ============================================================================
# Extraction Result (Aggregate)
# ============================================================================

class ExtractionResult(BaseModel):
    """Aggregate result from all extractor agents for a single paper."""
    pmid: str
    paper: Optional[PaperMetadata] = None
    classification: Optional[ClassificationResult] = None
    
    # Extracted data
    prs_models: List[PRSModelExtraction] = Field(default_factory=list)
    heritability_estimates: List[HeritabilityExtraction] = Field(default_factory=list)
    genetic_correlations: List[GeneticCorrelationExtraction] = Field(default_factory=list)
    
    # Status
    status: str = Field(default="pending")  # pending, processing, completed, failed
    error_message: Optional[str] = Field(default=None)
    
    # Timing
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    @property
    def total_extractions(self) -> int:
        return len(self.prs_models) + len(self.heritability_estimates) + len(self.genetic_correlations)
    
    @property
    def processing_time_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# ============================================================================
# Validation Result
# ============================================================================

class ValidationIssue(BaseModel):
    """A single validation issue."""
    field: str
    issue_type: str  # "range_error", "missing_required", "duplicate", "format_error"
    message: str
    severity: Literal["error", "warning", "info"] = "error"


class ValidationResult(BaseModel):
    """Result from the Validator Agent."""
    extraction_id: str
    extraction_type: Literal["prs", "heritability", "genetic_correlation"]
    status: ValidationStatus
    
    issues: List[ValidationIssue] = Field(default_factory=list)
    is_duplicate: bool = Field(default=False)
    duplicate_of: Optional[str] = Field(default=None, description="ID of existing duplicate")
    
    # If valid, the cleaned/normalized data
    validated_data: Optional[Dict[str, Any]] = Field(default=None)
    
    validated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)


# ============================================================================
# Workflow State
# ============================================================================

class WorkflowState(BaseModel):
    """State for the LangGraph workflow."""
    # Input
    query: str = Field(default="", description="Search query")
    disease: Optional[str] = Field(default=None)
    max_papers: int = Field(default=50)
    
    # Papers to process
    papers: List[PaperMetadata] = Field(default_factory=list)
    current_paper_index: int = Field(default=0)
    
    # Results
    classifications: List[ClassificationResult] = Field(default_factory=list)
    extractions: List[ExtractionResult] = Field(default_factory=list)
    validations: List[ValidationResult] = Field(default_factory=list)
    
    # Aggregated valid results
    valid_prs_models: List[PRSModelExtraction] = Field(default_factory=list)
    valid_heritability: List[HeritabilityExtraction] = Field(default_factory=list)
    valid_genetic_correlations: List[GeneticCorrelationExtraction] = Field(default_factory=list)
    
    # Status tracking
    status: str = Field(default="initialized")  # initialized, searching, classifying, extracting, validating, completed, failed
    errors: List[str] = Field(default_factory=list)
    
    # Timing
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    @property
    def current_paper(self) -> Optional[PaperMetadata]:
        if 0 <= self.current_paper_index < len(self.papers):
            return self.papers[self.current_paper_index]
        return None
    
    @property
    def progress_percentage(self) -> float:
        if not self.papers:
            return 0.0
        return (self.current_paper_index / len(self.papers)) * 100
