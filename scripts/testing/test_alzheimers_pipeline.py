#!/usr/bin/env python3
"""
Test script to run the Literature Mining Pipeline on 12 Alzheimer's disease papers.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path to allow imports from src
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from src.modules.literature.pipeline import mine_literature, WorkflowState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    disease_name = "Alzheimer's Disease"
    paper_count = 12
    
    print(f"Starting literature mining test for '{disease_name}'...")
    print(f"Target paper count: {paper_count}")
    
    # Run the pipeline
    try:
        result: WorkflowState = mine_literature(
            disease=disease_name,
            max_papers=paper_count,
            search_type="all"  # Search for all types (PRS, h2, rg)
        )
        
        # Print summary of results
        print("\n" + "="*50)
        print("LITERATURE MINING RESULTS SUMMARY")
        print("="*50)
        
        print(f"Status: {result.status}")
        
        valid_prs = result.valid_prs_models
        valid_h2 = result.valid_heritability
        valid_rg = result.valid_genetic_correlations
        
        print(f"\n✅ Valid Extractions Found:")
        print(f"  - PRS Models: {len(valid_prs)}")
        print(f"  - Heritability Estimates: {len(valid_h2)}")
        print(f"  - Genetic Correlations: {len(valid_rg)}")
        
        if valid_prs:
            print(f"\nSample PRS Model (First):")
            print(f"  Model ID: {valid_prs[0].id}")
            print(f"  PMID: {valid_prs[0].pmid}")
            print(f"  AUC: {valid_prs[0].auc}")
            print(f"  Sample Size: {valid_prs[0].sample_size}")
            
        print("\n" + "="*50)
        
        if result.errors:
            print("\nErrors encountered:")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
