
import sys
import os
import requests
import json

# Add src to path
sys.path.append(os.getcwd())
from src.core.pgs_catalog_client import PGSCatalogClient

def main():
    client = PGSCatalogClient()
    query = "alzheimer's"
    print(f"--- Auditing High AUC Models for '{query}' ---")
    
    # 1. Search
    print("Searching PGS Catalog...")
    results = client.search_scores(query)
    print(f"Total models found: {len(results)}")
    
    high_auc_models = []
    
    # 2. Check each model's details
    print("Fetching details to identify models with AUC > 0.9...")
    for res in results:
        mid = res.get('id')
        try:
            details = client.get_score_details(mid)
            metrics = details.get("metrics", {})
            auc = metrics.get("AUC")
            
            if auc and auc > 0.9:
                high_auc_models.append({
                    "id": mid,
                    "name": res.get("name"),
                    "auc": auc,
                    "metrics": metrics
                })
        except Exception as e:
            pass

    # 3. Deep Dive into High AUC Models
    if not high_auc_models:
        print("\n[OK] No models found with AUC > 0.9. The highest values likely just reflect good performance.")
    else:
        print(f"\n[!] Found {len(high_auc_models)} models with AUC > 0.9. Investigating...")
        
        for m in high_auc_models:
            print(f"\n=== Model {m['id']} ({m['name']}) ===")
            print(f"Display AUC: {m['auc']}")
            
            # Fetch RAW performance data to show user the source
            perf_url = "https://www.pgscatalog.org/rest/performance/search"
            resp = requests.get(perf_url, params={"pgs_id": m['id']})
            raw_data = resp.json().get("results", [])
            
            print(f"Raw API Performance Records: {len(raw_data)}")
            for i, rec in enumerate(raw_data):
                pm = rec.get("performance_metrics", {})
                
                # Check Class Accuracy (AUC often hid here)
                class_acc = pm.get("class_acc", [])
                for ca in class_acc:
                    if "AUC" in ca.get("name_short", ""):
                        print(f"  - Record {i+1} Source: AUC = {ca.get('estimate')} (95% CI: {ca.get('ci95_lo')}-{ca.get('ci95_up')})")
                        print(f"    - Sample Set: {rec.get('sampleset', {}).get('name', 'Unknown')}")
                        print(f"    - Covariates used: {rec.get('covariates')}")
                        print(f"    - Comments: {rec.get('performance_comments')}")
                
                # Check Other Metrics
                others = pm.get("othermetrics", [])
                for o in others:
                     if "AUC" in o.get("name_short", ""):
                        print(f"  - Record {i+1} Source: {o.get('name_short')} = {o.get('estimate')}")

    print("\n--- Audit Complete ---")

if __name__ == "__main__":
    main()
