
import requests
import json
import logging

def dump_pgs_data(pgs_id):
    print(f"=== AUDIT REPORT FOR {pgs_id} ===\n")
    
    # 1. Score Metadata Endpoint
    meta_url = f"https://www.pgscatalog.org/rest/score/{pgs_id}"
    print(f"[Endpoint 1] {meta_url}")
    try:
        resp = requests.get(meta_url)
        data = resp.json()
        print("--- FULL METADATA PAYLOAD ---")
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error fetching metadata: {e}")

    print("\n" + "="*50 + "\n")

    # 2. Performance Endpoint
    perf_url = f"https://www.pgscatalog.org/rest/performance/search?pgs_id={pgs_id}"
    print(f"[Endpoint 2] {perf_url}")
    try:
        resp = requests.get(perf_url)
        data = resp.json()
        results = data.get("results", [])
        print(f"Found {len(results)} Performance Records.")
        
        for idx, res in enumerate(results):
            print(f"\n[Record #{idx+1} - ID: {res.get('id')}]")
            
            # Metrics
            print("  > performance_metrics:")
            metrics = res.get("performance_metrics", {})
            print(json.dumps(metrics, indent=4))
            
            # Sampleset
            print("  > sampleset:")
            print(json.dumps(res.get("sampleset"), indent=4))
            
            # Covariates
            print(f"  > covariates: {res.get('covariates')}")
            print(f"  > performance_comments: {res.get('performance_comments')}")

    except Exception as e:
        print(f"Error fetching performance: {e}")

if __name__ == "__main__":
    dump_pgs_data("PGS000945")
