
import sys
import os
import json
sys.path.append(os.getcwd())

from src.core.pgs_catalog_client import PGSCatalogClient

def debug_metrics():
    client = PGSCatalogClient()
    ids = ["PGS000026"]
    
    print(f"Debugging Metrics for: {ids}")
    
    for mid in ids:
        print(f"\n--- Fetching {mid} ---")
        try:
            details = client.get_score_details(mid)
            print("Extracted Details:", json.dumps(details, indent=2))
            
            print(f"Sample Size: {details.get('sample_size')}")
            print(f"Publication: {details.get('publication')}")
            
            # Also dump raw performance response
            import requests
            perf_url = f"{client.BASE_URL}/performance/search"
            resp = requests.get(perf_url, params={"pgs_id": mid})
            if resp.status_code == 200:
                print(f"\n--- RAW PERFORMANCE for {mid} ---")
                print(json.dumps(resp.json(), indent=2))
            else:
                print(f"Failed to fetch performance: {resp.status_code}")
             
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_metrics()
