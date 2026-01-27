import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.modules.genetic_correlation.models import GeneticCorrelationSource
from src.modules.genetic_correlation.gwas_atlas_client import GWASAtlasGCClient
from src.modules.genetic_correlation.gene_atlas_client import GeneAtlasClient

client = TestClient(app)

def test_clients_loading():
    """Test if both clients load data successfully."""
    print("\n--- Testing Data Loading ---")
    gwas_client = GWASAtlasGCClient()
    assert gwas_client._data is not None
    assert not gwas_client._data.empty
    print(f"GWAS Atlas: Loaded {len(gwas_client._data)} rows.")

    gene_client = GeneAtlasClient()
    assert gene_client._data is not None
    assert not gene_client._data.empty
    print(f"GeneAtlas: Loaded {len(gene_client._data)} rows.")

def test_gwas_atlas_search():
    """Test GWAS Atlas search (Source: GWAS_ATLAS)."""
    # Use a known ID. 1 is usually BMI or similar common trait.
    # Note: Using string "1" for strict ID test as router now takes str
    response = client.get("/api/genetic-correlation/1?source=gwas_atlas&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    assert data["results"][0]["source"] == GeneticCorrelationSource.GWAS_ATLAS
    print(f"\nGWAS Atlas Search (ID=1): Found {len(data['results'])} results.")

def test_gene_atlas_search():
    """Test GeneAtlas search (Source: GENE_ATLAS)."""
    # Use a known description search term that exists in the file, e.g. "Body" or "BMI"
    # Or use a known ID if we extracted one. '1070-0.0' (TV watching) was in the snippet.
    target_id = "1070-0.0" 
    response = client.get(f"/api/genetic-correlation/{target_id}?source=gene_atlas&limit=5")
    assert response.status_code == 200
    data = response.json()
    
    # If standard ID search returns nothing (exact match required), 
    # we might need to test the client's search method directly for loose header matching if API restricts.
    # But let's assume we use the ID we saw in the head command.
    if not data["results"]:
        pytest.fail(f"Detailed GeneAtlas search failed for known ID {target_id}")
    
    item = data["results"][0]
    assert item["source"] == GeneticCorrelationSource.GENE_ATLAS
    print(f"\nGeneAtlas Search (ID={target_id}): Found {len(data['results'])} results.")
    print(f"Example: {item['trait_1_name']} vs {item['trait_2_name']} (rg={item['rg']})")

def test_cross_source_routing():
    """Verify router rejects or handles mismatches."""
    # Sending a GeneAtlas ID to GWAS Atlas source should return empty or 404
    response = client.get("/api/genetic-correlation/1070-0.0?source=gwas_atlas")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 0
