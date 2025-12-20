

# Add src to path
import sys
import os
sys.path.append(os.getcwd())
from src.core.pgs_catalog_client import PGSCatalogClient

def main():
    query = "alzheimer's" # Use exact query from user
    print(f"Testing PGSCatalogClient search for '{query}'...")
    
    client = PGSCatalogClient()
    results = client.search_scores(query)
    
    print(f"Found {len(results)} matches:")
    for res in results:
        print(f"- {res.get('id')}: {res.get('name')}")

if __name__ == "__main__":
    main()
