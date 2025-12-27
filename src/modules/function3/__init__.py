"""
Function 3: Proteomics PRS Models
"""

from .workflow import app as protein_workflow_app
from .models import ProteinScore, ProteinSearchResult, ProteinAgentRequest

__all__ = [
    "protein_workflow_app",
    "ProteinScore",
    "ProteinSearchResult", 
    "ProteinAgentRequest"
]
