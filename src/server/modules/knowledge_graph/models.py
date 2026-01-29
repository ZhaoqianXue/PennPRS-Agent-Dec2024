"""
Data Models for Knowledge Graph (Module 2).
Matches shared/contracts/api.ts for backend usage.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class KnowledgeGraphNode(BaseModel):
    """ Represents a Trait Node """
    id: str = Field(..., description="EFO ID or Trait Name")
    label: str = Field(..., description="Display Name")
    h2: Optional[float] = Field(None, description="Heritability")

class GeneticCorrelationEdge(BaseModel):
    """ Represents a relationship edge """
    source: str = Field(..., description="Source Trait ID")
    target: str = Field(..., description="Target Trait ID")
    rg: float = Field(..., description="Genetic Correlation Coefficient")
    p_value: float = Field(..., description="Significance P-value")
    se: Optional[float] = Field(None, description="Standard Error")

class KnowledgeGraphResult(BaseModel):
    """ Response model for graph queries """
    nodes: List[KnowledgeGraphNode] = Field(default_factory=list)
    edges: List[GeneticCorrelationEdge] = Field(default_factory=list)
