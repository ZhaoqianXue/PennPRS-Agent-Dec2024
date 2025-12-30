
from src.core.omicspred_client import OmicsPredClient
import json

def test_search():
    client = OmicsPredClient()
    
    print("\n--- Test 1: Gene Search (COL1A1) ---")
    results_gene = client.search_scores_general("COL1A1")
    print(f"Found {len(results_gene)} scores for 'COL1A1'")
    if len(results_gene) > 0:
        print("Sample result name:", results_gene[0]['name'])
        print("Sample result ID:", results_gene[0]['id'])
        print(f"Gene Info: {results_gene[0].get('genes')}")

    print("\n--- Test 2: Protein Search (Collagen alpha-1(I) chain) ---")
    results_protein = client.search_scores_general("Collagen alpha-1(I) chain")
    print(f"Found {len(results_protein)} scores for 'Collagen alpha-1(I) chain'")
    
    print("\n--- Test 3: Platform Filter (Olink) ---")
    results_platform = client.get_scores_by_platform("Olink", max_results=5)
    print(f"Found {len(results_platform)} scores for platform 'Olink'")
    if len(results_platform) > 0:
        print("First Olink result platform:", results_platform[0]['platform']['name'])

    print("\n--- Test 4: Detail Fetch ---")
    if len(results_gene) > 0:
        score_id = results_gene[0]['id']
        details = client.get_score_details(score_id)
        print(f"Successfully fetched details for {score_id}")
        formatted = client.format_score_for_ui(details)
        print("Formatted Data Keys:", formatted.keys())

if __name__ == "__main__":
    test_search()
