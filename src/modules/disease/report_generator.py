from typing import Dict, Any, List
from src.modules.disease.models import Report
import datetime
import os

def extract_features(file_path: str, model_id: str, trait: str) -> Report:
    """
    Mock feature extraction from a result file (e.g., zip).
    In production, this would unzip the file and parse the weights/variants.
    """
    """
    Mock feature extraction from a result file (e.g., zip).
    In production, this would unzip the file and parse the weights/variants.
    """
    from src.core.pgs_catalog_client import PGSCatalogClient
    pgs_client = PGSCatalogClient()
    
    num_variants = 0
    method = "Unknown"
    metrics = {}
    
    if model_id.startswith("PGS"):
        details = pgs_client.get_score_details(model_id)
        num_variants = details.get("num_variants", 0)
        method = details.get("method", "Unknown")
        metrics = details.get("metrics", {})
    
    return Report(
        model_id=model_id,
        trait=trait,
        method=method,
        ancestry="EUR", # Still hardcoded unless we fetch it from details
        num_variants=num_variants,
        top_variants=["rs429358 (APOE)", "rs7412 (APOE)"], # Kept as placeholder since real variants require big file download
        performance_metrics=metrics,
        download_path=file_path,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

def generate_report_markdown(report: Report) -> str:
    """
    Generate a markdown report string from the Report object.
    """
    md = f"""# PRS Model Report: {report.model_id}

## Overview
- **Trait**: {report.trait}
- **Method**: {report.method}
- **Ancestry**: {report.ancestry}
- **Created At**: {report.created_at}

## Model Features
- **Total Variants**: {report.num_variants:,}
- **Top Significant Variants**:
"""
    for v in report.top_variants:
        md += f"  - {v}\n"

    md += f"""
## Performance Metrics
- **R² Score**: {report.performance_metrics.get('R2')}
- **AUC**: {report.performance_metrics.get('AUC')}

## Downloads
- [Download Model Files]({report.download_path})

---
> [!TIP]
> This model is ready for downstream analysis. You can proceed to **Benchmarking** or **Proteomics Integration (PennPRS-Protein)**.
"""
    return md
