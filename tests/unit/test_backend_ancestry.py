
import sys
import os
import json
import logging

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mock llm_config to avoid complex dependency if needed, or rely on real one
# Assuming we can just import the module
try:
    from src.modules.disease.trait_classifier import classify_trait, _fallback_classification
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_ancestry_inference():
    test_cases = [
        {
            "trait": "Type 2 diabetes", 
            "sample_info": "433,540 East Asian ancestry individuals",
            "expected_ancestry": "EAS"
        },
        {
            "trait": "Breast cancer", 
            "sample_info": "15,000 African American individuals",
            "expected_ancestry": "AFR"
        },
        {
            "trait": "Height", 
            "sample_info": "Something with no race info",
            "expected_ancestry": "EUR" # Default fallback
        },
        {
             "trait": "Schizophrenia",
             "sample_info": "European ancestry",
             "expected_ancestry": "EUR"
        }
    ]

    print("--- Testing Backend Ancestry Inference ---")
    for case in test_cases:
        print(f"\nTesting: Trait='{case['trait']}', Info='{case['sample_info']}'")
        
        # 1. Test Fallback Logic directly (deterministically checks heuristic)
        fallback_res = _fallback_classification(case['trait'], case['sample_info'])
        print(f"Fallback Result: {fallback_res['ancestry']} (Reason: {fallback_res['reasoning']})")
        
        # 2. Test Main Logic (might use LLM)
        # Note: If LLM is not configured in this test env, it might fail or use fallback.
        # We catch exceptions to be safe.
        try:
            main_res = classify_trait(case['trait'], case['sample_info'])
            print(f"Main Result: {main_res['ancestry']} (Reason: {main_res['reasoning']})")
            
            if main_res['ancestry'] == case['expected_ancestry']:
                print("✅ PASS")
            else:
                print(f"❌ FAIL (Expected {case['expected_ancestry']})")
                
        except Exception as e:
            print(f"⚠️ Main Logic Failed (LLM issue?): {e}")

if __name__ == "__main__":
    test_ancestry_inference()
