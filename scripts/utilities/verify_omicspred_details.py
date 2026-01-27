
import time
import requests
import json
from src.core.omicspred_client import OmicsPredClient

def verify_single_score_fields():
    print("\n[1] Verifying Data Fields for OPGS000890...")
    client = OmicsPredClient()
    
    # Force API fetch
    t0 = time.time()
    details = client.get_score_details("OPGS000890")
    t_fetch = time.time() - t0
    
    print(f"Details keys: {details.keys()}")
    if 'dataset' in details:
        print(f"Dataset keys: {details['dataset'].keys()}")
    if 'dataset_info' in details:
        print(f"Dataset Info keys: {details['dataset_info'].keys()}")
        print(f"Train Cohorts: {details['dataset_info'].get('train_cohorts')}")
    
    formatted = client.format_score_for_ui(details)
    
    # Checklist based on user screenshot
    checklist = {
        "Score Information": {
            "Score Name": formatted.get("name"),
            "Publication": formatted.get("publication"),
            "Platform": formatted.get("platform"),
            "Tissue": details.get("tissue", {}).get("label"),
            "Dataset": formatted.get("dataset_name"),
            "Method Name": formatted.get("method"),
            "Reported Trait": details.get("trait_reported"),
            "Number of Variants": formatted.get("num_variants"),
            "Genome Build": details.get("variants_genomebuild"),
            "Terms & Licenses": details.get("license")
        },
        "Linked Annotations": {
            "Gene": formatted.get("genes"),
            "Protein": formatted.get("proteins"),
            # Pathways might be missing
        },
        "Evaluations (CRITICAL)": {
            "Ancestry Distribution": formatted.get("ancestry_dev"),
            "Evaluation Table (R2, Rho)": formatted.get("metrics")
        }
    }

    print(json.dumps(checklist, indent=2, default=str))
    
    # Check for R2 specifically
    r2 = formatted.get("metrics", {}).get("R2")
    print(f"\n[!] R2 Value: {r2}")
    if r2 is None or r2 == "N/A":
        print("    -> R2/Performance data is MISSING from API response.")
    else:
        print("    -> R2/Performance data FOUND.")

    return t_fetch

def test_batch_performance():
    print("\n[2] Testing Batch Performance (18 items)...")
    client = OmicsPredClient()
    
    # Search first
    results = client.search_scores_general("COL1A1")
    count = len(results)
    print(f"    Found {count} scores.")
    
    times = []
    success = 0
    
    for item in results:
        sid = item['id']
        t0 = time.time()
        det = client.get_score_details(sid)
        dur = time.time() - t0
        times.append(dur)
        if det: success += 1
        print(f"    Fetched {sid}: {dur:.3f}s")
        
    avg = sum(times) / len(times) if times else 0
    print(f"\n    Success Rate: {success}/{count}")
    print(f"    Average Time: {avg:.3f}s")
    print(f"    Total Time: {sum(times):.3f}s")

if __name__ == "__main__":
    verify_single_score_fields()
    test_batch_performance()
