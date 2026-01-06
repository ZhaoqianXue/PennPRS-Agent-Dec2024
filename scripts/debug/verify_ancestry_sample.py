
import sys
import os
import requests
import json

# Add src to path
sys.path.append(os.getcwd())
try:
    from src.core.pgs_catalog_client import PGSCatalogClient
except ImportError:
    pass

def main():
    pgs_id = "PGS000945"
    
    # 1. Fetch Raw API Data to see "Ground Truth"
    print(f"--- Fetching Raw Metadata for {pgs_id} ---")
    raw_resp = requests.get(f"https://www.pgscatalog.org/rest/score/{pgs_id}")
    raw_data = raw_resp.json()
    
    print("\n[Raw] Ancestry Distribution:")
    print(json.dumps(raw_data.get("ancestry_distribution", {}), indent=2))
    
    print("\n[Raw] Samples Training:")
    print(json.dumps(raw_data.get("samples_training", []), indent=2))
    
    print("\n[Raw] Samples Variants:")
    print(json.dumps(raw_data.get("samples_variants", []), indent=2))

    # 2. Check Client Extraction
    print(f"\n--- Checking Client Extraction for {pgs_id} ---")
    client = PGSCatalogClient()
    details = client.get_score_details(pgs_id)
    
    print(f"Client 'ancestry_distribution':")
    print(json.dumps(details.get("ancestry_distribution", {}), indent=2))
    
    print(f"Client 'sample_size': {details.get('sample_size')}")
    print(f"Client 'ancestry' (string summary): {details.get('ancestry')}")

if __name__ == "__main__":
    main()
