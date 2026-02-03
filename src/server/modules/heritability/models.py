"""
Heritability data models for PennGene Agent.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class HeritabilitySource(str, Enum):
    """Data sources for heritability estimates."""
    GWAS_ATLAS = "gwas_atlas"
    PAN_UKB = "pan_ukb"
    UKBB_LDSC = "ukbb_ldsc"


class Population(str, Enum):
    """Ancestry/population codes."""
    EUR = "EUR"
    AFR = "AFR"
    EAS = "EAS"
    AMR = "AMR"
    CSA = "CSA"
    MID = "MID"
    MIXED = "MIXED"


class HeritabilityEstimate(BaseModel):
    """A single heritability estimate from one source."""
    trait_name: str = Field(..., description="Name of the trait")
    trait_id: Optional[str] = Field(None, description="Standardized trait ID (EFO/MONDO)")
    h2_obs: float = Field(..., ge=0, le=1, description="Observed scale heritability")
    h2_obs_se: Optional[float] = Field(None, ge=0, description="Standard error of h2_obs")
    h2_liability: Optional[float] = Field(None, ge=0, le=1, description="Liability scale h2 (binary traits)")
    h2_liability_se: Optional[float] = Field(None, ge=0, description="SE of liability scale h2")
    population: str = Field(..., description="Population/ancestry code")
    source: HeritabilitySource = Field(..., description="Data source")
    n_samples: Optional[int] = Field(None, ge=0, description="Sample size")
    method: str = Field("ldsc", description="Estimation method")
    h2_z: Optional[float] = Field(None, description="Z-score for heritability estimate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "trait_name": "Alzheimer's disease",
                "trait_id": "EFO_0000249",
                "h2_obs": 0.24,
                "h2_obs_se": 0.03,
                "h2_liability": 0.58,
                "population": "EUR",
                "source": "gwas_atlas",
                "n_samples": 54162,
                "method": "ldsc"
            }
        }


class HeritabilitySearchResponse(BaseModel):
    """Response for heritability search endpoint."""
    query: str
    total_results: int
    estimates: List[HeritabilityEstimate]


class HeritabilityByAncestry(BaseModel):
    """Heritability grouped by ancestry."""
    trait_name: str
    ancestry_breakdown: Dict[str, List[HeritabilityEstimate]]


class GapAnalysisResult(BaseModel):
    """Result of PRS efficiency (R²/h²) analysis."""
    trait_name: str
    best_h2: Optional[float] = Field(None, description="Best heritability estimate")
    best_h2_source: Optional[str] = None
    best_prs_r2: Optional[float] = Field(None, description="Best PRS R² from PGS Catalog")
    best_prs_id: Optional[str] = None
    efficiency: Optional[float] = Field(None, description="R²/h² ratio (0-1)")
    improvement_potential: Optional[float] = Field(None, description="1 - efficiency")
    interpretation: Optional[str] = None
