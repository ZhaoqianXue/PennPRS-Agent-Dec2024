from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing import Literal

class TraitColumn(BaseModel):
    id: str = Field(..., description="ID of the trait/dataset")
    SNP: str = ""
    CHR: str = ""
    BETA: str = ""
    SE: str = ""
    P: str = ""
    A1: str = ""
    A2: str = ""
    MAF: str = ""
    N: str = ""
    NEFF: str = ""
    NCASE: str = ""
    NCONTROL: str = ""

class JobConfiguration(BaseModel):
    job_name: str
    job_type: str = "single"
    job_methods: List[str] = ["C+T-pseudo", "lassosum2-pseudo", "LDpred2-pseudo"]
    job_ensemble: bool = True
    traits_source: List[str] = ["Query Data"]
    traits_detail: List[str] = ["GWAS Catalog"]
    traits_type: List[str] = ["Continuous"]
    traits_name: List[str]
    traits_population: List[str] = ["EUR"]
    traits_col: List[TraitColumn]
    para_dict: Optional[Dict[str, Any]] = None

class Report(BaseModel):
    model_id: str
    trait: str
    method: str
    ancestry: str
    num_variants: int
    top_variants: List[str]
    performance_metrics: Dict[str, float]
    download_path: str
    created_at: str


class PrimaryRecommendation(BaseModel):
    pgs_id: Optional[str] = Field(default=None, description="PGS model identifier")
    source_trait: Optional[str] = Field(default=None, description="Source trait for cross-disease transfer")
    confidence: Literal["High", "Moderate", "Low"] = Field(..., description="Confidence level")
    rationale: str = Field(..., description="Evidence-backed rationale")


class DirectMatchEvidence(BaseModel):
    models_evaluated: int = Field(..., description="Number of models assessed")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Global performance landscape")
    clinical_benchmarks: List[str] = Field(default_factory=list, description="Clinical benchmarks or guidelines")


class CrossDiseaseModelSummary(BaseModel):
    models_found: int = Field(..., description="Number of models found for source trait")
    best_model_id: Optional[str] = Field(default=None, description="Best model ID among source trait models")
    best_model_auc: Optional[float] = Field(default=None, description="Best model AUC")


class CrossDiseaseEvidence(BaseModel):
    source_trait: str = Field(..., description="Neighbor trait used for transfer")
    rg_meta: Optional[float] = Field(default=None, description="Meta-analyzed genetic correlation")
    transfer_score: Optional[float] = Field(default=None, description="Transfer viability score")
    related_traits_evaluated: List[str] = Field(default_factory=list, description="Traits evaluated for transfer")
    shared_genes: List[str] = Field(default_factory=list, description="Shared genes supporting mechanism")
    biological_rationale: Optional[str] = Field(default=None, description="Mechanism summary")
    source_trait_models: Optional[CrossDiseaseModelSummary] = Field(default=None, description="Source trait model summary")


class StudyPowerSummary(BaseModel):
    n_correlations: int = Field(..., description="Number of study-pair correlations aggregated")
    rg_meta: Optional[float] = Field(default=None, description="Meta-analyzed genetic correlation")


class GeneticGraphEvidence(BaseModel):
    neighbor_trait: str = Field(..., description="Genetically correlated trait")
    rg_meta: Optional[float] = Field(default=None, description="Meta-analyzed genetic correlation")
    transfer_score: Optional[float] = Field(default=None, description="Transfer viability score")
    neighbor_models_found: int = Field(default=0, description="Number of PRS models found for neighbor trait")
    neighbor_best_model_id: Optional[str] = Field(default=None, description="Best neighbor model ID")
    neighbor_best_model_auc: Optional[float] = Field(default=None, description="Best neighbor model AUC")
    mechanism_confidence: Optional[str] = Field(default=None, description="Mechanism confidence")
    mechanism_summary: Optional[str] = Field(default=None, description="Mechanism summary")
    shared_genes: List[str] = Field(default_factory=list, description="Top shared genes (if available)")
    study_power: Optional[StudyPowerSummary] = Field(default=None, description="Study power summary")


class FollowUpOption(BaseModel):
    label: str = Field(..., description="UI action label")
    action: str = Field(..., description="UI action identifier")
    context: str = Field(..., description="Additional context for the action")


class RecommendationReport(BaseModel):
    recommendation_type: Literal[
        "DIRECT_HIGH_QUALITY",
        "DIRECT_SUB_OPTIMAL",
        "CROSS_DISEASE",
        "NO_MATCH_FOUND"
    ]
    primary_recommendation: Optional[PrimaryRecommendation] = None
    alternative_recommendations: List[PrimaryRecommendation] = Field(default_factory=list)
    direct_match_evidence: Optional[DirectMatchEvidence] = None
    cross_disease_evidence: Optional[CrossDiseaseEvidence] = None
    genetic_graph_evidence: List[GeneticGraphEvidence] = Field(default_factory=list)
    genetic_graph_ran: bool = Field(default=False, description="Whether genetic graph tools were executed")
    genetic_graph_neighbors: List[str] = Field(default_factory=list, description="Neighbor traits returned by genetic_graph_get_neighbors")
    genetic_graph_errors: List[str] = Field(default_factory=list, description="Errors from genetic graph tools, if any")
    caveats_and_limitations: List[str] = Field(default_factory=list)
    follow_up_options: List[FollowUpOption] = Field(default_factory=list)

class DiseaseState(BaseModel):
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    step: str = Field(default="start", description="Current step in the workflow")
    user_intent: Optional[str] = None
    selected_trait: Optional[str] = None # Renamed from selected_phenotype for consistency
    selected_model_id: Optional[str] = None
    use_existing_model: Optional[bool] = None
    job_config: Optional[JobConfiguration] = None
    job_id: Optional[str] = None
    job_status: Optional[str] = None
    result_path: Optional[str] = None
    report_data: Optional[Report] = None
