# tests/integration/test_trait_synonym_expansion_real.py
"""
Integration tests for Trait Synonym Expansion feature using REAL APIs.

These tests use real API calls to validate the trait synonym expansion feature
works correctly in production-like scenarios.

Run with: RUN_REAL_API_TESTS=1 pytest tests/integration/test_trait_synonym_expansion_real.py -v -s
"""
import sys
import os
import logging
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

from src.server.core.tools.trait_tools import trait_synonym_expand
from src.server.core.tool_schemas import ToolError
from src.server.core.trait_synonym_expander import TraitExpansionResult
from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

if os.getenv("RUN_REAL_API_TESTS") != "1":
    pytest.skip("Skipping real API tests (set RUN_REAL_API_TESTS=1 to enable).", allow_module_level=True)


def test_breast_cancer_synonym_expansion_and_search():
    """Test synonym expansion and PGS search for 'Breast cancer'."""
    print("\n" + "="*80)
    print("TEST 1: Breast cancer - Synonym Expansion and PGS Search")
    print("="*80)
    
    trait = "Breast cancer"
    
    # Step 1: Synonym Expansion
    print(f"\n[Step 1] Expanding synonyms for '{trait}'...")
    expansion_result = trait_synonym_expand(trait)
    
    assert isinstance(expansion_result, (TraitExpansionResult, ToolError)), \
        f"Expected TraitExpansionResult or ToolError, got {type(expansion_result)}"
    
    if isinstance(expansion_result, ToolError):
        pytest.fail(f"trait_synonym_expand returned error: {expansion_result.error_message}")
    
    print(f"✓ Expanded to {len(expansion_result.expanded_queries)} queries")
    print(f"  Expanded queries: {expansion_result.expanded_queries}")
    print(f"  Found {len(expansion_result.synonyms)} synonyms")
    for syn in expansion_result.synonyms[:5]:  # Show first 5
        print(f"    - {syn.synonym} ({syn.relationship}, {syn.confidence})")
    
    # Verify expansion worked
    assert expansion_result.original_query == trait
    assert len(expansion_result.expanded_queries) > 1, "Should expand to multiple queries"
    assert trait in expansion_result.expanded_queries, "Original query should be in expanded list"
    
    # Check for medical synonyms
    synonym_texts = [s.synonym.lower() for s in expansion_result.synonyms]
    has_medical_synonym = any(
        "neoplasm" in text or "carcinoma" in text or "malignant" in text
        for text in synonym_texts
    )
    assert has_medical_synonym, "Should include medical terminology synonyms"
    print("✓ Medical synonyms found")
    
    # Step 2: PGS Search with expanded queries
    print(f"\n[Step 2] Searching PGS Catalog with {len(expansion_result.expanded_queries)} expanded queries...")
    pgs_client = PGSCatalogClient()
    
    all_models = []
    seen_model_ids = set()
    queries_searched = 0
    
    for i, query in enumerate(expansion_result.expanded_queries, 1):
        print(f"  [{i}/{len(expansion_result.expanded_queries)}] Searching: '{query}'...", end=" ", flush=True)
        result = prs_model_pgscatalog_search(pgs_client, query, limit=25)
        
        if isinstance(result, ToolError):
            print(f"✗ Error: {result.error_message}")
            continue
        
        queries_searched += 1
        models_found = len(result.models)
        print(f"✓ Found {models_found} models")
        
        # Merge results, deduplicating by model ID
        for model in result.models:
            if model.id not in seen_model_ids:
                all_models.append(model)
                seen_model_ids.add(model.id)
    
    print(f"\n[Step 3] Results Summary:")
    print(f"  Queries searched: {queries_searched}/{len(expansion_result.expanded_queries)}")
    print(f"  Total unique models found: {len(all_models)}")
    print(f"  Models deduplicated: {len(seen_model_ids)} unique IDs")
    
    # Verify we found models
    assert len(all_models) > 0, "Should find at least one model with expanded queries"
    assert len(all_models) == len(seen_model_ids), "Models should be deduplicated"
    
    print(f"\n✓ Test PASSED: Found {len(all_models)} unique models for '{trait}'")
    print("="*80 + "\n")


def test_type_2_diabetes_synonym_expansion_and_search():
    """Test synonym expansion and PGS search for 'Type 2 Diabetes'."""
    print("\n" + "="*80)
    print("TEST 2: Type 2 Diabetes - Synonym Expansion and PGS Search")
    print("="*80)
    
    trait = "Type 2 Diabetes"
    
    # Step 1: Synonym Expansion
    print(f"\n[Step 1] Expanding synonyms for '{trait}'...")
    expansion_result = trait_synonym_expand(trait)
    
    assert isinstance(expansion_result, (TraitExpansionResult, ToolError)), \
        f"Expected TraitExpansionResult or ToolError, got {type(expansion_result)}"
    
    if isinstance(expansion_result, ToolError):
        pytest.fail(f"trait_synonym_expand returned error: {expansion_result.error_message}")
    
    print(f"✓ Expanded to {len(expansion_result.expanded_queries)} queries")
    print(f"  Expanded queries: {expansion_result.expanded_queries}")
    print(f"  Found {len(expansion_result.synonyms)} synonyms")
    for syn in expansion_result.synonyms[:5]:  # Show first 5
        print(f"    - {syn.synonym} ({syn.relationship}, {syn.confidence})")
    
    # Verify expansion worked
    assert expansion_result.original_query == trait
    assert len(expansion_result.expanded_queries) > 1, "Should expand to multiple queries"
    assert trait in expansion_result.expanded_queries, "Original query should be in expanded list"
    
    # Check for common abbreviations
    synonym_texts = [s.synonym.lower() for s in expansion_result.synonyms]
    has_abbreviation = any(
        "t2d" in text or "t2dm" in text or "niddm" in text
        for text in synonym_texts
    )
    assert has_abbreviation, "Should include common abbreviations"
    print("✓ Common abbreviations found")
    
    # Step 2: PGS Search with expanded queries
    print(f"\n[Step 2] Searching PGS Catalog with {len(expansion_result.expanded_queries)} expanded queries...")
    pgs_client = PGSCatalogClient()
    
    all_models = []
    seen_model_ids = set()
    queries_searched = 0
    
    for i, query in enumerate(expansion_result.expanded_queries, 1):
        print(f"  [{i}/{len(expansion_result.expanded_queries)}] Searching: '{query}'...", end=" ", flush=True)
        result = prs_model_pgscatalog_search(pgs_client, query, limit=25)
        
        if isinstance(result, ToolError):
            print(f"✗ Error: {result.error_message}")
            continue
        
        queries_searched += 1
        models_found = len(result.models)
        print(f"✓ Found {models_found} models")
        
        # Merge results, deduplicating by model ID
        for model in result.models:
            if model.id not in seen_model_ids:
                all_models.append(model)
                seen_model_ids.add(model.id)
    
    print(f"\n[Step 3] Results Summary:")
    print(f"  Queries searched: {queries_searched}/{len(expansion_result.expanded_queries)}")
    print(f"  Total unique models found: {len(all_models)}")
    print(f"  Models deduplicated: {len(seen_model_ids)} unique IDs")
    
    # Verify we found models
    assert len(all_models) > 0, "Should find at least one model with expanded queries"
    assert len(all_models) == len(seen_model_ids), "Models should be deduplicated"
    
    print(f"\n✓ Test PASSED: Found {len(all_models)} unique models for '{trait}'")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Allow running as a script for quick manual verification
    pytest.main([__file__, "-v", "-s"])
