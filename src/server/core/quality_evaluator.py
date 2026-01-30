"""
Core Logic for Module 1: PRS Quality Evaluation.
Extracts quantitative metrics from raw metadata to be used by the LLM for dynamic quality assessment.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class QualityMetrics(BaseModel):
    """ Matches shared/contracts/api.ts """
    auc: Optional[float] = None
    r2: Optional[float] = None
    sample_size: Optional[int] = None
    num_variants: Optional[int] = None
    publication_year: Optional[int] = None
    is_polygenic: bool = False

class QualityEvaluator:
    """ Evaluates raw model data and extracts Quality Metrics. """
    
    def extract_metrics(self, model_card: Dict[str, Any]) -> QualityMetrics:
        """
        Extracts structured metrics from raw metadata.
        Args:
            model_card: Dictionary containing raw metadata from PGS Catalog/PennPRS.
        Returns:
            QualityMetrics object.
        """
        # Extract metrics (AUC, R2)
        metrics_raw = model_card.get('metrics', {})
        auc = float(metrics_raw.get("AUC") or 0) if metrics_raw.get("AUC") is not None else None
        r2 = float(metrics_raw.get("R2") or 0) if metrics_raw.get("R2") is not None else None
        
        # Sample size
        try:
            sample_size = int(model_card.get('sample_size') or 0)
        except (ValueError, TypeError):
            sample_size = None
        
        # Publication year
        pub_date = model_card.get('publication', {}).get('date', "")
        try:
            year = int(pub_date.split("-")[0]) if pub_date else None
        except (ValueError, IndexError):
            year = None
            
        # Number of variants
        try: 
            num_variants = int(model_card.get('num_variants') or 0)
        except (ValueError, TypeError):
            num_variants = None
        
        is_polygenic = (num_variants > 100) if num_variants is not None else False
        
        return QualityMetrics(
            auc=auc,
            r2=r2,
            sample_size=sample_size,
            num_variants=num_variants,
            publication_year=year,
            is_polygenic=is_polygenic
        )
