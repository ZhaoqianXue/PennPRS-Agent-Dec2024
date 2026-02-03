import sys
import os
import logging
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.pgs_catalog_client import PGSCatalogClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("RUN_REAL_API_TESTS") != "1":
    pytest.skip("Skipping real PGS Catalog API tests (set RUN_REAL_API_TESTS=1 to enable).", allow_module_level=True)

def test_real_pgs_search():
    """
    Test searching PGS Catalog with real API.
    """
    client = PGSCatalogClient()
    trait = "Alzheimer"
    
    results = client.search_scores(trait)
    
    assert results is not None, "PGS Catalog search returned None (possible API/network error)."
    assert isinstance(results, list), f"Expected list results, got {type(results)}"
    assert len(results) > 0, "No results found (trait yielded 0 results or API error)."

if __name__ == "__main__":
    # Allow running as a script for quick manual verification.
    test_real_pgs_search()
