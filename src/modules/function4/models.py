from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

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

class Function4State(BaseModel):
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
