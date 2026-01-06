
import sys
import os
import json
sys.path.append(os.getcwd())

from src.core.pennprs_client import PennPRSClient

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_deep_fetch():
    client = PennPRSClient()
    mid = "GCST90032275"
    print(f"Testing deep fetch for {mid}...")
    
    res = client.get_deep_metadata(mid)
    
    print("Result:")
    print(json.dumps(res, indent=2))
    
    if res.get("deep_fetch_status") == "success":
        print("PASS: Deep fetch successful.")
        if res.get("h2"):
             print(f"PASS: Found H2: {res.get('h2')}")
        else:
             print("WARN: H2 not found (might be missing in specific file).")
             
        if res.get("num_variants"):
             print(f"PASS: Found Variants: {res.get('num_variants')}")
        else:
             print("WARN: Variants not found.")
    else:
        print("FAIL: Deep fetch failed.")

if __name__ == "__main__":
    verify_deep_fetch()
