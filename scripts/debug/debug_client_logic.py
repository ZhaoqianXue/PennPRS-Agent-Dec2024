
import sys
import os
import requests
import json

def main():
    pgs_id = "PGS000945"
    BASE_URL = "https://www.pgscatalog.org/rest"
    perf_url = f"{BASE_URL}/performance/search"
    
    print(f"Fetching performance for {pgs_id}...")
    resp = requests.get(perf_url, params={"pgs_id": pgs_id})
    data = resp.json()
    results = data.get("results", [])
    print(f"Results count: {len(results)}")
    
    r2_values = []
    auc_values = []
    pgs_only_r2 = []
    pgs_only_auc = []
    
    for i, res in enumerate(results):
        print(f"\n--- Processing Record {i+1} ---")
        perf = res.get("performance_metrics", {})
        
        # 2. Other Metrics logic
        others = perf.get("othermetrics", [])
        for m in others:
            name_raw = m.get("name_short", "")
            name = name_raw.lower().replace("²", "2")
            estimate = m.get("estimate")
            
            print(f"  [Metric] Raw: '{name_raw}' -> Norm: '{name}' | Val: {estimate}")
            
            if estimate is None:
                continue
                
            if "no covariates" in name:
                if "r2" in name or "r-squared" in name:
                    pgs_only_r2.append(estimate)
                    print("    -> Added to PGS_R2")
                if "auc" in name or "roc" in name:
                    pgs_only_auc.append(estimate)
                    print("    -> Added to PGS_AUC")
                    
            if "r2" in name or "r-squared" in name:
                r2_values.append(estimate)
                print("    -> Added to R2")
            if "auc" in name or "c-index" in name or "roc" in name:
                auc_values.append(estimate)
                print("    -> Added to AUC")
                
        # 3. Class Acc logic
        class_acc = perf.get("class_acc", [])
        for m in class_acc:
             name = m.get("name_short", "").lower()
             est = m.get("estimate")
             print(f"  [Class Acc] {name} | Val: {est}")
             if "auc" in name or "roc" in name:
                auc_values.append(est)
                print("    -> Added to AUC")

    print("\n--- Summary ---")
    print(f"R2 Values: {r2_values}")
    if r2_values: print(f"Max R2: {max(r2_values)}")
    
    print(f"PGS R2 Values: {pgs_only_r2}")
    if pgs_only_r2: print(f"Max PGS R2: {max(pgs_only_r2)}")

if __name__ == "__main__":
    main()
