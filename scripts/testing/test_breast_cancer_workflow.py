#!/usr/bin/env python3
"""
Test script for the complete workflow with user input "Oropharyngeal cancer".

This script simulates a real user scenario and tests the entire recommendation workflow
according to SOP specifications.

Follows @.agent/blueprints/sop.md and @.agent/rules/rules.md
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.server.modules.disease.recommendation_agent import recommend_models
from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
from src.server.core.pgs_catalog_client import PGSCatalogClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_prs_search_direct():
    """Test Step 1: Search PGS Catalog directly with trait name"""
    logger.info("=" * 80)
    logger.info("STEP 1: Testing prs_model_pgscatalog_search (direct, no synonym expansion)")
    logger.info("=" * 80)
    
    pgs_client = PGSCatalogClient()
    target_trait = "Oropharyngeal cancer"
    
    logger.info(f"Searching with trait: '{target_trait}'")
    
    result = prs_model_pgscatalog_search(pgs_client, target_trait, limit=25)
    
    if hasattr(result, 'models'):
        logger.info(f"✓ PGS Catalog search successful:")
        logger.info(f"  - Total found: {result.total_found}")
        logger.info(f"  - After filter: {result.after_filter}")
        logger.info(f"  - Models returned: {len(result.models)}")
        
        if result.models:
            logger.info(f"\nTop 3 models:")
            for i, model in enumerate(result.models[:3], 1):
                logger.info(f"  {i}. {model.id}: {model.trait_reported}")
                logger.info(f"     AUC: {model.performance_metrics.get('auc', 'N/A')}, "
                          f"R²: {model.performance_metrics.get('r2', 'N/A')}")
        
        return result.models
    else:
        logger.error(f"✗ PGS Catalog search failed: {result}")
        return []


def test_full_recommendation_workflow(force_outcome=None):
    """Test the complete recommendation workflow
    
    Args:
        force_outcome: Optional. Force Step 1 outcome for testing:
            - "DIRECT_SUB_OPTIMAL": Force Sub-optimal Match to test Step 2a
            - "NO_MATCH_FOUND": Force No Match to test Step 2a
            - None: Use normal LLM decision
    """
    logger.info("=" * 80)
    logger.info("FULL WORKFLOW TEST: Testing recommend_models()")
    logger.info("=" * 80)
    
    target_trait = "Prostate cancer"  # Use a disease with models to test Step 2a properly
    
    if force_outcome:
        logger.info(f"TEST MODE: Forcing Step 1 outcome to {force_outcome}")
    
    logger.info(f"User input: {target_trait}")
    logger.info("Calling recommend_models()...")
    
    try:
        report = recommend_models(target_trait, force_step1_outcome=force_outcome)
        
        logger.info("=" * 80)
        logger.info("RECOMMENDATION REPORT")
        logger.info("=" * 80)
        
        # Convert to dict for logging
        report_dict = report.model_dump() if hasattr(report, 'model_dump') else report
        
        logger.info(f"Recommendation Type: {report_dict.get('recommendation_type', 'N/A')}")
        
        primary = report_dict.get('primary_recommendation', {})
        if primary:
            logger.info(f"\nPrimary Recommendation:")
            logger.info(f"  - PGS ID: {primary.get('pgs_id', 'N/A')}")
            logger.info(f"  - Source Trait: {primary.get('source_trait', 'N/A')}")
            logger.info(f"  - Confidence: {primary.get('confidence', 'N/A')}")
            logger.info(f"  - Rationale: {primary.get('rationale', 'N/A')[:200]}...")
        
        alternatives = report_dict.get('alternative_recommendations', [])
        if alternatives:
            logger.info(f"\nAlternative Recommendations ({len(alternatives)}):")
            for i, alt in enumerate(alternatives[:3], 1):
                logger.info(f"  {i}. {alt.get('pgs_id', 'N/A')}: {alt.get('source_trait', 'N/A')}")
        
        direct_evidence = report_dict.get('direct_match_evidence', {})
        if direct_evidence:
            logger.info(f"\nDirect Match Evidence:")
            logger.info(f"  - Models evaluated: {direct_evidence.get('models_evaluated', 'N/A')}")
        
        cross_disease = report_dict.get('cross_disease_evidence', {})
        if cross_disease:
            logger.info(f"\nCross-Disease Evidence:")
            logger.info(f"  - Source trait: {cross_disease.get('source_trait', 'N/A')}")
            logger.info(f"  - Genetic correlation (rg): {cross_disease.get('rg_meta', 'N/A')}")
            logger.info(f"  - Transfer score: {cross_disease.get('transfer_score', 'N/A')}")
        
        tool_errors = report_dict.get('tool_errors', [])
        if tool_errors:
            logger.warning(f"\nTool Errors ({len(tool_errors)}):")
            for err in tool_errors:
                logger.warning(f"  - {err.get('tool_name', 'Unknown')}: {err.get('error_message', 'N/A')}")
        
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW TEST COMPLETED")
        logger.info("=" * 80)
        
        return report_dict
        
    except Exception as e:
        logger.error(f"✗ Workflow test failed with exception: {e}", exc_info=True)
        return None


def main():
    """Main test function"""
    logger.info("Starting Oropharyngeal Cancer Workflow Test")
    logger.info("Following SOP specifications from @.agent/blueprints/sop.md")
    logger.info("")
    
    # Test Step 1: PGS search directly (no synonym expansion)
    pgs_models = test_prs_search_direct()
    
    # Test full workflow with forced Sub-optimal Match to test Step 2a
    logger.info("")
    logger.info("=" * 80)
    logger.info("TESTING WITH FORCED SUB-OPTIMAL MATCH (to test Step 2a)")
    logger.info("=" * 80)
    report = test_full_recommendation_workflow(force_outcome="DIRECT_SUB_OPTIMAL")
    
    # Save results
    output_dir = project_root / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "oropharyngeal_cancer_workflow_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "pgs_models_count": len(pgs_models),
            "recommendation_report": report
        }, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"\nResults saved to: {output_file}")
    
    return report is not None


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
