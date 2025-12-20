
import sys
import os
import json
sys.path.append(os.getcwd())

from src.core.pennprs_client import PennPRSClient

# Disable SSL warnings for the test
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_extraction():
    client = PennPRSClient()
    trait = "CAG-349" # From previous debug; specific enough to get the item we saw
    
    print(f"Searching public results for '{trait}'...")
    results = client.search_public_results(trait)
    
    if not results:
        print("No results found. Trying broad search.")
        results = client.search_public_results("stool") # Broad term from the previous item
        
    if results:
        print(f"Found {len(results)} results.")
        first = results[0]
        print(json.dumps(first, indent=2))
        
        # Verify specific fields
        if first.get("sample_size") and isinstance(first.get("sample_size"), int):
            print("PASS: Sample Size is an int.")
        else:
            print(f"FAIL: Sample Size is {type(first.get('sample_size'))} - {first.get('sample_size')}")
            
        if first.get("publication") and "citation" in first.get("publication"):
            print(f"PASS: Publication found: {first['publication']['citation']}")
        else:
             print("FAIL: Publication missing.")
    else:
        print("No results found to verify.")

if __name__ == "__main__":
    verify_extraction()
