"""
Function 3: Proteomics PRS Models
Data models for protein genetic scores.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ProteinScore(BaseModel):
    """
    Represents a protein genetic score from OmicsPred.
    """
    id: str  # OPGS ID
    name: str
    protein_name: Optional[str] = None
    gene_name: Optional[str] = None
    uniprot_id: Optional[str] = None
    platform: Optional[str] = None  # Olink, Somalogic, etc.
    tissue: Optional[str] = None
    cohort: Optional[str] = None
    ancestry: str = "EUR"
    method: str = "Genetic Score"
    num_variants: int = 0
    sample_size: int = 0
    source: str = "OmicsPred"
    download_url: Optional[str] = None
    
    # Metrics
    r2: Optional[float] = None
    heritability: Optional[float] = None
    effect_size: Optional[float] = None
    p_value: Optional[float] = None
    
    # Publication
    pmid: Optional[str] = None
    doi: Optional[str] = None


class ProteinSearchResult(BaseModel):
    """
    Search result from OmicsPred.
    """
    total_count: int
    results: List[ProteinScore]
    query: Optional[str] = None
    platform: Optional[str] = None


class ProteinAgentRequest(BaseModel):
    """
    Request to the protein agent.
    """
    message: str
    request_id: Optional[str] = None
    platform: Optional[str] = None  # Optional platform filter
