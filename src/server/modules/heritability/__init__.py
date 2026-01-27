"""
Heritability module for PennGene Agent.
"""
from src.server.modules.heritability.models import (
    HeritabilityEstimate,
    HeritabilitySearchResponse,
    HeritabilityByAncestry,
    GapAnalysisResult,
    HeritabilitySource,
    Population
)

__all__ = [
    "HeritabilityEstimate",
    "HeritabilitySearchResponse", 
    "HeritabilityByAncestry",
    "GapAnalysisResult",
    "HeritabilitySource",
    "Population"
]
