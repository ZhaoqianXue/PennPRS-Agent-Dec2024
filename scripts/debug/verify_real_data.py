import sys
import os
sys.path.append(os.getcwd())

from src.modules.function4.workflow import _fetch_formatted_models
from src.modules.function4.report_generator import extract_features
import time

def test_real_data():
    trait = "Alzheimer's disease"
    print(f"Searching for {trait} (No Limit, Parallel Fetch)...")
    
    start = time.time()
    model_cards, pgs_results, penn_results = _fetch_formatted_models(trait)
    end = time.time()
    
    print(f"Search completed in {end - start:.2f} seconds.")
    print(f"Total Models Found: {len(model_cards)}")
    
    # Check limits
    if len(model_cards) <= 20:
        print("WARNING: Model count <= 20. Could be correct, or limit still exists.")
    else:
        print("PASS: Model count > 20.")
        
    # Check Metrics in Grid
    print("\n--- Top 5 Models in Grid ---")
    for m in model_cards[:5]:
        print(f"ID: {m['id']}, Method: {m['method']}, Metrics: {m['metrics']}, Variants (Grid): {m.get('num_variants')}")
        
    # Verify exact variants for known ID
    # PGS000025 should have 19 variants
    target = next((m for m in model_cards if m['id'] == 'PGS000025'), None)
    if target:
        print(f"\nTarget Check PGS000025:")
        print(f"  Grid Variants: {target.get('num_variants')}")
        if target.get('num_variants') == 19:
            print("  PASS: Correct Variant Count (19)")
        else:
            print(f"  FAIL: Expected 19, got {target.get('num_variants')}")
            
    # Check Report Generation (Real Data)
    print("\n--- Report Generation Test (PGS000025) ---")
    report = extract_features("dummy/path", "PGS000025", trait)
    print(f"Report Variants: {report.num_variants}")
    print(f"Report Metrics: {report.performance_metrics}")
    
    if report.num_variants == 19:
        print("PASS: Report Generation uses real data.")
    else:
        print("FAIL: Report Generation mocked/wrong.")

if __name__ == "__main__":
    test_real_data()
