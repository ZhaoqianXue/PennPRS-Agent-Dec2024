import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.pgs_catalog_client import PGSCatalogClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_pgs_search():
    """
    Test searching PGS Catalog with real API.
    """
    client = PGSCatalogClient()
    trait = "Alzheimer"
    print(f"Searching for trait: {trait}...")
    
    results = client.search_scores(trait)
    
    if results:
        print(f"✅ Found {len(results)} results.")
        # Print first one
        first = results[0]
        print(f"Sample Result: ID={first.get('id')}, Name={first.get('name')}")
        return True
    else:
        print("⚠️ No results found or API error. (Or trait yielded 0 results)")
        return False

if __name__ == "__main__":
    success = test_real_pgs_search()
    if not success:
        sys.exit(1)
