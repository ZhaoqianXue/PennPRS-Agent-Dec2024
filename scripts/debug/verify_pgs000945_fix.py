
import sys
import os
import json

# Add src to path
sys.path.append(os.getcwd())
try:
    from src.core.pgs_catalog_client import PGSCatalogClient
except ImportError:
    # Use mocks if needed, but here we want real integration
    # ensure dependencies installed
    pass

def main():
    client = PGSCatalogClient()
    pid = "PGS000945"
    print(f"--- Verifying Data Extraction for {pid} ---")
    
    details = client.get_score_details(pid)
    metrics = details.get("metrics", {})
    
    print("Extracted Metrics:")
    print(json.dumps(metrics, indent=2))
    
    perf = details.get("performance_detailed", [])
    print(f"\nDetailed Records Found: {len(perf)}")
    print(json.dumps(perf, indent=2))

    # Validation
    if len(perf) > 0:
        print("\n[SUCCESS] Detailed performance records extracted.")
    else:
        print("\n[FAIL] No detailed records.")

if __name__ == "__main__":
    main()
