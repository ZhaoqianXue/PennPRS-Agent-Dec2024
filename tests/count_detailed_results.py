
import sys
import os
import concurrent.futures
import time

# Add src to path
sys.path.append(os.getcwd())

from src.core.pgs_catalog_client import PGSCatalogClient
from src.core.pennprs_client import PennPRSClient

def main():
    pgs_client = PGSCatalogClient()
    penn_client = PennPRSClient()
    
    query = "alzheimer's"
    print(f"--- Searching for '{query}' ---")
    
    # 1. Search PGS Catalog (Full Index)
    print("Scanning PGS Catalog (this may take a moment)...")
    pgs_matches = pgs_client.search_scores(query)
    print(f"PGS Catalog Matches: {len(pgs_matches)}")
    
    # 2. Fetch Details for ALL PGS Matches
    print(f"Fetching details for {len(pgs_matches)} models to check data richness...")
    
    detailed_count = 0
    has_metrics = 0
    has_variants = 0
    has_ancestry = 0
    
    # Helper to fetch
    def fetch_one(mid):
        try:
            return pgs_client.get_score_details(mid)
        except:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_one, m['id']): m['id'] for m in pgs_matches}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            mid = futures[future]
            details = future.result()
            
            if details:
                # Criteria for "Detailed"
                # - Has Metrics (Performance)
                # - OR Has Variants/Genetic Info
                # - OR Has Ancestry
                
                m = details.get("metrics", {})
                v = details.get("num_variants", 0)
                a = details.get("ancestry_distribution", {})
                
                if m: has_metrics += 1
                if v > 0: has_variants += 1
                if a and a.get("dist"): has_ancestry += 1
                
                if m or v > 0 or (a and a.get("dist")):
                    detailed_count += 1
            
            if (i+1) % 10 == 0:
                print(f"Processed {i+1}/{len(pgs_matches)}...")

    print("\n--- PGS Catalog Stats ---")
    print(f"Total Models Found: {len(pgs_matches)}")
    print(f"Models with Detailed Data: {detailed_count}")
    print(f"  - With Performance Metrics: {has_metrics}")
    print(f"  - With Variant Counts: {has_variants}")
    print(f"  - With Ancestry Dist: {has_ancestry}")

    # 3. Search PennPRS
    print("\nScanning PennPRS Public Results...")
    penn_matches = penn_client.search_public_results(query)
    
    # PennPRS "Deep Scan" is on-demand, so we check if they are capable of deep scan (have download link)
    penn_capable = len([m for m in penn_matches if m.get("download_link")])
    
    print("--- PennPRS Stats ---")
    print(f"Total Models Found: {len(penn_matches)}")
    print(f"Models Capable of Deep Scan (Detailed): {penn_capable}")
    
    # Summary
    print("\n=== FINAL SUMMARY ===")
    print(f"Total Unique Models: {len(pgs_matches) + len(penn_matches)}")
    print(f"Rich Data Available for: {detailed_count + penn_capable}")

if __name__ == "__main__":
    main()
