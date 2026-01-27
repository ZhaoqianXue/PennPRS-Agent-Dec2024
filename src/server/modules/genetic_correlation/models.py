from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class GeneticCorrelationSource(str, Enum):
    GWAS_ATLAS = "gwas_atlas"
    GENE_ATLAS = "gene_atlas"
    OTHER = "other"

class GeneticCorrelationResult(BaseModel):
    id1: str = Field(..., description="ID of the query trait")
    id2: str = Field(..., description="ID of the correlated trait")
    trait_1_name: Optional[str] = Field(None, description="Name of the query trait")
    trait_2_name: Optional[str] = Field(None, description="Name of the correlated trait")
    rg: float = Field(..., description="Genetic correlation coefficient")
    se: float = Field(..., description="Standard error of rg")
    z: float = Field(..., description="Z-score")
    p: float = Field(..., description="P-value")
    source: GeneticCorrelationSource = Field(..., description="Data source")

class GeneticCorrelationResponse(BaseModel):
    query_trait: str = Field(..., description="The trait being queried")
    results: List[GeneticCorrelationResult] = Field(default_factory=list, description="List of correlations found")
    total_found: int = Field(..., description="Total number of correlations found")
