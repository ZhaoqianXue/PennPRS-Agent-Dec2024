"""
Core Logic for Module 1: PRS Quality Evaluation.
Implements the 'Tier 1/2/3' logic defined in 'proposal.md'.
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RecommendationGrade(str, Enum):
    """ Matches shared/contracts/api.ts """
    GOLD = 'GOLD'      # Tier 1
    SILVER = 'SILVER'  # Tier 2
    BRONZE = 'BRONZE'  # Tier 3

class QualityMetrics(BaseModel):
    """ Matches shared/contracts/api.ts """
    auc: Optional[float] = None
    r2: Optional[float] = None
    sample_size: Optional[int] = None
    num_variants: Optional[int] = None
    publication_year: Optional[int] = None
    is_polygenic: bool = False

class QualityEvaluator:
    """ Evaluates raw model data against Quality Thresholds. """
    
    def evaluate(self, model_card: Dict[str, Any]) -> RecommendationGrade:
        """
        Determines the quality tier (GOLD/SILVER/BRONZE) for a given model.
        Args:
            model_card: Dictionary containing raw metadata from PGS Catalog/PennPRS.
        Returns:
            RecommendationGrade Enum.
        """
        # Extract fields safely
        metrics = model_card.get('metrics', {})
        auc = float(metrics.get("AUC") or 0)
        r2 = float(metrics.get("R2") or 0)
        
        # 'sample_size' might be top-level or nested
        try:
            sample_size = int(model_card.get('sample_size') or 0)
        except (ValueError, TypeError):
            sample_size = 0
        
        # 'publication' -> {"date": "2021-01-01"}
        pub_date = model_card.get('publication', {}).get('date', "")
        try:
            year = int(pub_date.split("-")[0]) if pub_date else 0
        except (ValueError, IndexError):
            year = 0
            
        # 'num_variants' -> Integer
        try: 
            num_variants = int(model_card.get('num_variants') or 0)
        except (ValueError, TypeError):
            num_variants = 0
        
        # Logic Implementation
        
        # Tier 1 (Gold) Criteria
        is_polygenic = num_variants > 100
        is_recent = year >= 2020
        is_large = sample_size > 50000
        has_good_metrics = (auc > 0.65) or (r2 > 0.05) 
        
        if is_polygenic and is_recent and is_large and has_good_metrics:
            return RecommendationGrade.GOLD
            
        # Tier 2 (Silver) Criteria (Baseline)
        is_polygenic_base = num_variants > 50 # Proposal says > 50
        is_recent_base = year >= 2018
        is_medium = sample_size > 10000
        
        if is_polygenic_base and is_recent_base and is_medium:
            return RecommendationGrade.SILVER
            
        # Default Bronze (Legacy/Warning)
        return RecommendationGrade.BRONZE
