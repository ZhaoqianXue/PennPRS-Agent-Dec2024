
import sys
import os
import json
import asyncio

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pgs_catalog_client import PGSCatalogClient

async def main():
    client = PGSCatalogClient()
    pgs_id = "PGS000945"
    
    print(f"Fetching details for {pgs_id}...")
    try:
        data = client.get_score_details(pgs_id)
        
        # Define the expected keys based on what the Frontend uses
        frontend_keys = [
            "id", "name", "trait_reported", "mapped_traits", 
            "pgs_name", "variants_genomebuild", "num_variants", 
            "method", "params", "weight_type", 
            "performance_detailed", 
            "publication", "license", "ancestry_distribution"
        ]
        
        print("\n--- Data Availability Check ---")
        for key in frontend_keys:
            val = data.get(key)
            status = "✅ Present" if val else "❌ MISSING/EMPTY"
            if isinstance(val, list) and len(val) == 0:
                status = "⚠️ Empty List"
            print(f"{key}: {status}")
            
        print("\n--- Detailed Performance Structure Check ---")
        perf = data.get("performance_detailed", [])
        if not perf:
            print("❌ No performance_detailed records found!")
        else:
            print(f"Found {len(perf)} records. Checking first record structure:")
            first = perf[0]
            expected_perf_keys = ["ancestry", "cohorts", "sample_size", "auc", "auc_ci_lower", "auc_ci_upper", "r2"]
            for k in expected_perf_keys:
                print(f"  - {k}: {first.get(k)} ({type(first.get(k))})")

        print("\n--- Ancestry Distribution Check ---")
        dist = data.get("ancestry_distribution", {})
        if not dist or "dist" not in dist:
             print("❌ Invalid ancestry_distribution structure")
        else:
             print(f"✅ Distribution found with {len(dist['dist'])} items")

        # Save to file for manual inspection if needed
        with open("tests/frontend_payload_dump.json", "w") as f:
            json.dump(data, f, indent=2)
        print("\nDump saved to tests/frontend_payload_dump.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
