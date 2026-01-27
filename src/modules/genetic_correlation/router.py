from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import GeneticCorrelationResponse, GeneticCorrelationResult, GeneticCorrelationSource
from .gwas_atlas_client import GWASAtlasGCClient
from .gene_atlas_client import GeneAtlasClient

router = APIRouter(
    prefix="/api/genetic-correlation",
    tags=["Genetic Correlation"]
)

# Initialize clients
gwas_atlas_client = GWASAtlasGCClient()
gene_atlas_client = GeneAtlasClient()

@router.get("/{trait_id}", response_model=GeneticCorrelationResponse)
async def get_genetic_correlations(
    trait_id: str,
    source: GeneticCorrelationSource = Query(GeneticCorrelationSource.GWAS_ATLAS, description="Data source to query"),
    limit: int = Query(50, description="Max number of results to return")
):
    """
    Get top genetic correlations for a specific trait ID.
    """
    results = []
    
    # Int conversion helper for GWAS Atlas (which expects ints)
    def clean_id(tid):
        try:
            return int(float(tid))
        except:
            return tid

    if source == GeneticCorrelationSource.GWAS_ATLAS:
        # GWAS Atlas uses integer IDs
        try:
            int_id = clean_id(trait_id)
            if isinstance(int_id, int):
                results = gwas_atlas_client.get_correlations(int_id, limit=limit)
        except ValueError:
            results = [] # Invalid ID format for this source
            
    elif source == GeneticCorrelationSource.GENE_ATLAS:
        # GeneAtlas uses string IDs (e.g. "1070-0.0")
        results = gene_atlas_client.get_correlations_by_id(str(trait_id), limit=limit)
        # If no results by ID, try searching by name? 
        # The previous 'trait_id' in endpoint implies ID, but user might pass name?
        # Let's keep it strict ID for now.
    
    # Try to resolve trait name from results
    trait_name = str(trait_id)
    if results:
        first = results[0]
        # Logic to pick the query trait name vs the partner name
        # If id1 matches query, trait_1_name is the query name.
        if str(first.id1) == str(trait_id) or str(first.id1) == str(clean_id(trait_id)):
            trait_name = first.trait_1_name or str(trait_id)
        else:
            trait_name = first.trait_2_name or str(trait_id)

    return GeneticCorrelationResponse(
        query_trait=trait_name,
        total_found=len(results),
        results=results
    )

@router.get("/pair/{id1}/{id2}", response_model=GeneticCorrelationResult)
async def get_pair_correlation(
    id1: str, 
    id2: str,
    source: GeneticCorrelationSource = Query(GeneticCorrelationSource.GWAS_ATLAS, description="Data source")
):
    """
    Get the genetic correlation between two specific traits.
    """
    result = None
    
    def clean_id(tid):
        try:
            return int(float(tid))
        except:
            return tid

    if source == GeneticCorrelationSource.GWAS_ATLAS:
        try:
            i1 = clean_id(id1)
            i2 = clean_id(id2)
            if isinstance(i1, int) and isinstance(i2, int):
                result = gwas_atlas_client.get_pair_correlation(i1, i2)
        except:
            pass
            
    elif source == GeneticCorrelationSource.GENE_ATLAS:
        result = gene_atlas_client.get_pair_correlation(str(id1), str(id2))

    if not result:
        # Fallback for GeneAtlas if I didn't verify get_pair_correlation exists in client
        # I should add it to client.
        raise HTTPException(status_code=404, detail=f"No genetic correlation found between {id1} and {id2} in {source}")
    
    return result
