"""
Comprehensive Test Suite for Agentic Study Classifier

Tests various study types from the GWAS Catalog to ensure the classifier works correctly:
- Binary (case/control) studies
- Continuous (individuals) studies
- Family history / Proxy studies (should be Continuous)
- Different ancestries (EUR, EAS, AFR, AMR, SAS)
- Edge cases

Run with: python test_agentic_classifier.py
"""

from dotenv import load_dotenv
load_dotenv()

import time
import sys
from collections import defaultdict

from src.modules.function4.agentic_study_classifier import classify_trait_from_study


# ============================================================================
# Test Cases - Selected from gwas_catalog.tsv
# Format: (study_id, expected_type, expected_ancestry, description)
# ============================================================================

TEST_CASES = [
    # ==========================================================================
    # BINARY (Case/Control) Studies
    # ==========================================================================
    ("GCST009979", "Binary", "EUR", "Major depressive disorder (29,475 cases, 63,482 controls)"),
    ("GCST009980", "Binary", "EUR", "Major depressive disorder in trauma exposed individuals"),
    ("GCST006956", "Binary", "EUR", "Erectile dysfunction (6,175 cases, 217,630 controls)"),
    ("GCST006091", "Binary", "EAS", "Freckles - Japanese ancestry (7,148 cases, 4,034 controls)"),
    ("GCST010681", "Binary", "EUR", "Type 1 diabetes (9,266 cases, 15,574 controls)"),
    ("GCST90013429", "Binary", "EUR", "Amyotrophic lateral sclerosis (22,040 cases, 62,644 controls)"),
    ("GCST011888", "Binary", "EUR", "Sporadic miscarriage (49,996 cases, 174,109 controls)"),
    ("GCST010118", "Binary", "EAS", "Type 2 diabetes - East Asian (77,418 cases, 356,122 controls)"),
    ("GCST90000255", "Binary", "EUR", "Severe COVID-19 infection (1,610 cases, 2,205 controls)"),
    ("GCST006810", "Binary", "EUR", "Self-reported risk-taking behaviour (113,882 cases)"),
    
    # ==========================================================================
    # CONTINUOUS (Individuals) Studies - Quantitative Traits
    # ==========================================================================
    ("GCST007429", "Continuous", "EUR", "Lung function FVC (321,047 individuals)"),
    ("GCST007432", "Continuous", "EUR", "FEV1 (321,047 individuals)"),
    ("GCST006250", "Continuous", "EUR", "Intelligence (269,867 individuals)"),
    ("GCST008592", "Continuous", "AMR", "HDL cholesterol levels - Hispanic/Latino (11,103 individuals)"),
    ("GCST008591", "Continuous", "AMR", "Triglyceride levels - Hispanic/Latino (11,103 individuals)"),
    ("GCST90002224", "Continuous", "AMR", "Height - Peruvian (3,134 individuals)"),
    ("GCST90002316", "Continuous", "EUR", "Lymphocyte count - European (524,923 individuals)"),
    ("GCST90002317", "Continuous", "EAS", "Lymphocyte count - East Asian (89,266 individuals)"),
    ("GCST90002373", "Continuous", "AFR", "White blood cell count - African (15,061 individuals)"),
    ("GCST90002319", "Continuous", "SAS", "Lymphocyte count - South Asian (8,163 individuals)"),
    ("GCST90002310", "Continuous", "EUR", "Hemoglobin concentration (563,946 individuals)"),
    ("GCST90000287", "Continuous", "EUR", "Myocardial fractal dimension (18,096 individuals)"),
    
    # ==========================================================================
    # CONTINUOUS - Family History / Proxy Studies (CRITICAL EDGE CASE)
    # ==========================================================================
    ("GCST90012877", "Continuous", "EUR", "Alzheimer's disease OR family history (472,868 individuals) - PROXY"),
    ("GCST90012878", "Continuous", "EUR", "Family history of Alzheimer's disease (408,942 individuals) - PROXY"),
    
    # ==========================================================================
    # CONTINUOUS - Biomarker Levels
    # ==========================================================================
    ("GCST90012102", "Continuous", "EUR", "Bioavailable testosterone levels - women"),
    ("GCST90012103", "Continuous", "EUR", "Bioavailable testosterone levels - men"),
]


def run_tests():
    """Run all test cases and report results."""
    
    print("=" * 80)
    print("🧪 AGENTIC STUDY CLASSIFIER - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Total test cases: {len(TEST_CASES)}")
    print()
    
    results = {
        "passed": [],
        "failed": [],
        "errors": []
    }
    
    ancestry_stats = defaultdict(lambda: {"passed": 0, "failed": 0})
    type_stats = defaultdict(lambda: {"passed": 0, "failed": 0})
    
    total_time = 0
    times = []
    
    for i, (study_id, expected_type, expected_ancestry, description) in enumerate(TEST_CASES, 1):
        print(f"[{i:02d}/{len(TEST_CASES)}] Testing {study_id}...")
        
        try:
            t_start = time.time()
            result = classify_trait_from_study(study_id)
            elapsed = time.time() - t_start
            total_time += elapsed
            times.append(elapsed)
            
            actual_type = result.get("trait_type", "Unknown")
            actual_ancestry = result.get("ancestry", "Unknown")
            sample_size = result.get("sample_size", 0)
            confidence = result.get("confidence", "Unknown")
            
            type_match = actual_type == expected_type
            ancestry_match = actual_ancestry == expected_ancestry
            
            if type_match and ancestry_match:
                results["passed"].append({
                    "study_id": study_id,
                    "description": description,
                    "time": elapsed,
                    "sample_size": sample_size
                })
                ancestry_stats[expected_ancestry]["passed"] += 1
                type_stats[expected_type]["passed"] += 1
                print(f"       ✅ PASS | {actual_type} | {actual_ancestry} | N={sample_size:,} | {elapsed:.2f}s")
            else:
                failure_reason = []
                if not type_match:
                    failure_reason.append(f"Type: got {actual_type}, expected {expected_type}")
                if not ancestry_match:
                    failure_reason.append(f"Ancestry: got {actual_ancestry}, expected {expected_ancestry}")
                
                results["failed"].append({
                    "study_id": study_id,
                    "description": description,
                    "expected": (expected_type, expected_ancestry),
                    "actual": (actual_type, actual_ancestry),
                    "reason": "; ".join(failure_reason),
                    "reasoning": result.get("reasoning", "")
                })
                ancestry_stats[expected_ancestry]["failed"] += 1
                type_stats[expected_type]["failed"] += 1
                print(f"       ❌ FAIL | {' | '.join(failure_reason)}")
                print(f"       Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
                
        except Exception as e:
            results["errors"].append({
                "study_id": study_id,
                "description": description,
                "error": str(e)
            })
            print(f"       ⚠️  ERROR | {str(e)[:60]}...")
    
    # =========================================================================
    # Summary Report
    # =========================================================================
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = len(results["passed"])
    failed = len(results["failed"])
    errors = len(results["errors"])
    total = len(TEST_CASES)
    
    print(f"\n✅ Passed: {passed}/{total} ({100*passed/total:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({100*failed/total:.1f}%)")
    print(f"⚠️  Errors: {errors}/{total} ({100*errors/total:.1f}%)")
    
    print(f"\n⏱️  Performance:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per study: {total_time/total:.2f}s")
    if times:
        print(f"   Fastest: {min(times):.2f}s")
        print(f"   Slowest: {max(times):.2f}s")
    
    print(f"\n📈 By Trait Type:")
    for trait_type, stats in sorted(type_stats.items()):
        total_type = stats["passed"] + stats["failed"]
        pct = 100 * stats["passed"] / total_type if total_type > 0 else 0
        print(f"   {trait_type}: {stats['passed']}/{total_type} passed ({pct:.0f}%)")
    
    print(f"\n🌍 By Ancestry:")
    for ancestry, stats in sorted(ancestry_stats.items()):
        total_anc = stats["passed"] + stats["failed"]
        pct = 100 * stats["passed"] / total_anc if total_anc > 0 else 0
        print(f"   {ancestry}: {stats['passed']}/{total_anc} passed ({pct:.0f}%)")
    
    if results["failed"]:
        print(f"\n❌ FAILED TESTS DETAILS:")
        print("-" * 60)
        for fail in results["failed"]:
            print(f"   {fail['study_id']}: {fail['description']}")
            print(f"      Expected: {fail['expected']}")
            print(f"      Actual: {fail['actual']}")
            print(f"      Reason: {fail['reason']}")
            print()
    
    if results["errors"]:
        print(f"\n⚠️  ERRORS:")
        print("-" * 60)
        for err in results["errors"]:
            print(f"   {err['study_id']}: {err['error']}")
    
    print()
    print("=" * 80)
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed + errors} TEST(S) NEED ATTENTION")
    print("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
