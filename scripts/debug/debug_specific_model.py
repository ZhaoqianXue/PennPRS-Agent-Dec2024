
import sys
import os
import requests
import json

# Add src to path
sys.path.append(os.getcwd())
from src.core.pgs_catalog_client import PGSCatalogClient

def main():
    client = PGSCatalogClient()
    pid = "PGS000945" # The one with 0.98 AUC
    
    print(f"--- Deep Dive {pid} ---")
    
    # 1. Get Score Info
    score_url = f"https://www.pgscatalog.org/rest/score/{pid}"
    s_resp = requests.get(score_url).json()
    print(f"Name: {s_resp.get('name')}")
    print(f"Trait Reported: {s_resp.get('trait_reported')}")
    
    # 2. Get Performance Records
    perf_url = "https://www.pgscatalog.org/rest/performance/search"
    p_resp = requests.get(perf_url, params={"pgs_id": pid}).json()
    results = p_resp.get("results", [])
    
    print(f"Performance Records: {len(results)}")
    
    for i, res in enumerate(results):
        print(f"\n[Record {i+1}]")
        print(f"  Sample Set: {res.get('sampleset', {}).get('name_short')}")
        print(f"  Sample Size: {res.get('sampleset', {}).get('number_samples')}")
        print(f"  Ancestry: {res.get('sampleset', {}).get('ancestry_broad')}")
        print(f"  Comments: {res.get('performance_comments')}")
        
        pm = res.get("performance_metrics", {})
        
        # Check AUC specifically
        class_acc = pm.get("class_acc", [])
        for ca in class_acc:
             print(f"  -> Class Metric: {ca.get('name_short')} = {ca.get('estimate')} (Type: {ca.get('name_long')})")

        # Check Other Metrics (Where PGS R2 might be)
        others = pm.get("othermetrics", [])
        for o in others:
            print(f"  -> Other Metric: {o.get('name_short')} = {o.get('estimate')} (Type: {o.get('name_long')})")

if __name__ == "__main__":
    main()
