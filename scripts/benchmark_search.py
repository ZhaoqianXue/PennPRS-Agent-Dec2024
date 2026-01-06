import time
import json
from src.core.pennprs_client import PennPRSClient
from src.core.pgs_catalog_client import PGSCatalogClient
import concurrent.futures

def benchmark_search(trait):
    print(f"=== Benchmarking search for: {trait} ===")
    
    pgs_client = PGSCatalogClient()
    penn_client = PennPRSClient()
    
    start_total = time.time()
    
    # 1. Search PGS Catalog
    start = time.time()
    pgs_results = pgs_client.search_scores(trait)
    end = time.time()
    print(f"PGS search_scores took: {end - start:.2f}s (Found {len(pgs_results)} results)")
    
    # 2. Search PennPRS Public Results
    start = time.time()
    penn_results = penn_client.search_public_results(trait)
    end = time.time()
    print(f"PennPRS search_public_results took: {end - start:.2f}s (Found {len(penn_results)} results)")
    
    # 3. Parallel Fetch details for PGS Catalog
    start = time.time()
    pgs_details_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {
            executor.submit(pgs_client.get_score_details, res.get('id')): res.get('id') 
            for res in pgs_results
        }
        for future in concurrent.futures.as_completed(future_to_id):
            pid = future_to_id[future]
            try:
                data = future.result()
                pgs_details_map[pid] = data
            except Exception as exc:
                print(f'{pid} generated an exception: {exc}')
    end = time.time()
    print(f"PGS get_score_details (Parallel 10 workers) took: {end - start:.2f}s")
    
    # 4. Formatting and Sorting (Simplified for benchmark)
    start = time.time()
    model_cards = []
    # (Omitted full formatting for brevity, focusing on the core logic)
    for res in pgs_results:
        pid = res.get('id')
        details = pgs_details_map.get(pid, {})
        model_cards.append({"id": pid, "source": "PGS", "metrics": details.get("metrics", {})})
    for res in penn_results:
        model_cards.append({"id": res.get('id'), "source": "PennPRS", "metrics": res.get('metrics', {})})
        
    def get_sort_auc(card):
        metrics = card.get("metrics", {})
        return metrics.get("AUC") or 0
    
    model_cards.sort(key=get_sort_auc, reverse=True)
    end = time.time()
    print(f"Formatting and Sorting took: {end - start:.4f}s")
    
    end_total = time.time()
    print(f"Total time: {end_total - start_total:.2f}s")
    print("=========================================\n")
    return model_cards

if __name__ == "__main__":
    benchmark_search("Alzheimer's disease")
    benchmark_search("Type 2 Diabetes")
