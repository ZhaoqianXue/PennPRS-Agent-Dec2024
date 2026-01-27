
import sys
import os
import json
sys.path.append(os.getcwd())
from src.core.pgs_catalog_client import PGSCatalogClient

def main():
    client = PGSCatalogClient()
    pgs_id = "PGS000945"
    print(f"Fetching complete details for {pgs_id}...")
    
    data = client.get_score_details(pgs_id)
    
    print("\n" + "="*40)
    print(f"DATA AUDIT REPORT: {pgs_id}")
    print("="*40)
    
    print(f"[1] Metadata")
    print(f"  - PGS Name: {data.get('pgs_name')}")
    print(f"  - Reported Trait: {data.get('trait_reported')}")
    print(f"  - Mapped Traits: {[t['label'] + ' (' + t['id'] + ')' for t in data.get('mapped_traits', [])]}")
    print(f"  - Variants (Count): {data.get('num_variants')}")
    print(f"  - Genome Build: {data.get('variants_genomebuild')}")
    print(f"  - Method: {data.get('method')} (Params: {data.get('params')})")
    print(f"  - Weight Type: {data.get('weight_type')}")
    print(f"  - License: {data.get('license')}")
    
    # 2. Publication
    pub = data.get("publication", {})
    print(f"\n[2] Publication")
    print(f"  - Citation: {pub.get('citation')}")
    print(f"  - DOI: {pub.get('doi')}")
    
    # 3. Development Samples
    print(f"\n[3] Support (Training Data)")
    print(f"  - Sample Size: {data.get('sample_size'):,}")
    print(f"  - Ancestry: {data.get('ancestry')}")
    
    # 4. Performance Metrics (Detailed)
    perf = data.get("performance_detailed", [])
    print(f"\n[4] Performance Metrics ({len(perf)} Records)")
    
    print(f"{'ID':<10} | {'Ancestry':<20} | {'Cohorts':<10} | {'N':<8} | {'AUC [95% CI]':<22} | {'R2 (Full)':<10}")
    print("-" * 100)
    
    for p in perf:
        p_id = p.get("ppm_id")
        anc = p.get("ancestry") or "N/A"
        coh = p.get("cohorts") or "NR"
        n = p.get("sample_size") or 0
        auc = p.get("auc")
        r2 = p.get("r2") or 0
        
        # Format AUC with CI
        if auc:
            auc_str = f"{auc:.4f}"
            if p.get("auc_ci_lower") and p.get("auc_ci_upper"):
                auc_str += f" [{p.get('auc_ci_lower'):.3f}-{p.get('auc_ci_upper'):.3f}]"
        else:
            auc_str = "N/A"
            
        print(f"{p_id:<10} | {anc:<20} | {coh:<10} | {n:<8,} | {auc_str:<22} | {r2:<10.4f}")

if __name__ == "__main__":
    main()
