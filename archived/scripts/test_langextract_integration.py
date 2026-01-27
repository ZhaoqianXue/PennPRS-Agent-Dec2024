import sys
import os
import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from src.modules.literature.information_extractor import PRSExtractor
from src.modules.literature.entities import PaperMetadata

def test_integration():
    print("Testing LangExtract Integration in PRSExtractor...")
    
    # 1. Setup Dummy Paper
    full_text = """
    This study evaluates the performance of a Polygenic Risk Score (PRS) for Alzheimer's Disease.
    We used the LDpred2 method.
    The resulting AUC was 0.85 in the validation cohort.
    The collected sample size was 5000 individuals of European ancestry.
    """
    
    paper = PaperMetadata(
        pmid="12345678",
        title="Test Paper",
        abstract="Abstract...",
        full_text=full_text,
        publication_date=datetime.date(2023, 1, 1),
        journal="Nature Genetics"
    )
    
    # 2. Simulate LLM Response
    # This structure must match what the Extractor expects (PRS_EXTRACTION_SCHEMA)
    response_data = {
        "extractions": [
            {
                "trait": "Alzheimer's Disease",
                "performance_metrics": {
                    "auc": 0.85,
                    "r2": None,
                    "c_index": None,
                    "or_per_sd": None
                },
                "model_characteristics": {
                    "method": "LDpred2",
                    "variants_number": None,
                    "method_detail": None
                },
                "population": {
                    "sample_size": 5000,
                    "ancestry": "European",
                    "cohort": None
                },
                "extraction_metadata": {
                    "confidence": 0.9,
                    "source_text": "The resulting AUC was 0.85 in the validation cohort."
                }
            }
        ]
    }
    
    # 3. Instantiate Extractor
    extractor = PRSExtractor()
    
    # 4. Call _parse_response directly
    results = extractor._parse_response(paper, response_data)
    
    # 5. Verify Results
    print(f"Parsed {len(results)} results.")
    
    if len(results) > 0:
        result = results[0]
        print(f"Extracted AUC: {result.auc}")
        print(f"Extracted Raw Text Snippet: '{result.raw_text_snippet}'")
        print(f"Generated Evidence HTML: {result.evidence_html}")
        
        # Assertions
        assert result.auc == 0.85
        assert result.raw_text_snippet == "The resulting AUC was 0.85 in the validation cohort."
        assert '<mark class="highlight">The resulting AUC was 0.85 in the validation cohort.</mark>' in result.evidence_html
        
        print("\nSUCCESS: Evidence HTML was generated correctly via integration!")
    else:
        print("\nFAILURE: No results parsed.")

if __name__ == "__main__":
    test_integration()
