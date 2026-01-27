"""
FastAPI router for heritability endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.modules.heritability.models import (
    HeritabilityEstimate,
    HeritabilitySearchResponse,
    HeritabilityByAncestry,
    GapAnalysisResult,
    HeritabilitySource
)
from src.modules.heritability.aggregator import HeritabilityAggregator

router = APIRouter(prefix="/api/heritability", tags=["heritability"])

# Singleton aggregator instance
_aggregator: Optional[HeritabilityAggregator] = None


def get_aggregator() -> HeritabilityAggregator:
    """Get or create the heritability aggregator singleton."""
    global _aggregator
    if _aggregator is None:
        _aggregator = HeritabilityAggregator()
    return _aggregator


@router.get("/{trait}", response_model=HeritabilitySearchResponse)
async def get_heritability(
    trait: str,
    source: Optional[HeritabilitySource] = Query(None, description="Filter by data source"),
    ancestry: Optional[str] = Query(None, description="Filter by ancestry (EUR, AFR, etc.)"),
    min_score: int = Query(60, ge=0, le=100, description="Minimum fuzzy match score")
) -> HeritabilitySearchResponse:
    """
    Search for heritability estimates for a trait.
    
    Queries GWAS Atlas, Pan-UK Biobank, and UKBB LDSC databases.
    Uses fuzzy matching to find relevant traits.
    """
    aggregator = get_aggregator()
    
    sources = [source] if source else None
    results = aggregator.search(
        trait=trait,
        sources=sources,
        ancestry=ancestry,
        min_score=min_score
    )
    
    return HeritabilitySearchResponse(
        query=trait,
        total_results=len(results),
        estimates=results
    )


@router.get("/{trait}/ancestry", response_model=HeritabilityByAncestry)
async def get_heritability_by_ancestry(
    trait: str,
    min_score: int = Query(60, ge=0, le=100, description="Minimum fuzzy match score")
) -> HeritabilityByAncestry:
    """
    Get heritability estimates grouped by ancestry.
    
    Useful for comparing heritability across populations.
    """
    aggregator = get_aggregator()
    breakdown = aggregator.get_by_ancestry(trait)
    
    return HeritabilityByAncestry(
        trait_name=trait,
        ancestry_breakdown=breakdown
    )


@router.get("/{trait}/sources")
async def get_heritability_by_source(
    trait: str,
    min_score: int = Query(60, ge=0, le=100)
) -> dict:
    """
    Get heritability estimates grouped by data source.
    
    Shows which databases have data for this trait.
    """
    aggregator = get_aggregator()
    by_source = aggregator.get_by_source(trait)
    
    return {
        "trait_name": trait,
        "sources": {
            source: [est.model_dump() for est in estimates]
            for source, estimates in by_source.items()
        },
        "source_counts": {source: len(estimates) for source, estimates in by_source.items()}
    }


@router.get("/{trait}/best")
async def get_best_heritability(
    trait: str,
    ancestry: str = Query("EUR", description="Target ancestry")
) -> dict:
    """
    Get the highest-confidence heritability estimate for a trait.
    
    Selection based on sample size, standard error, and source priority.
    """
    aggregator = get_aggregator()
    best = aggregator.get_best_estimate(trait, ancestry=ancestry)
    
    if not best:
        raise HTTPException(status_code=404, detail=f"No heritability data found for '{trait}'")
    
    return {
        "trait_name": trait,
        "ancestry": ancestry,
        "best_estimate": best.model_dump()
    }


@router.get("/gap-analysis/{trait}", response_model=GapAnalysisResult)
async def get_gap_analysis(
    trait: str,
    prs_r2: Optional[float] = Query(None, ge=0, le=1, description="PRS R² value"),
    prs_id: Optional[str] = Query(None, description="PRS ID from PGS Catalog")
) -> GapAnalysisResult:
    """
    Calculate PRS efficiency (R²/h²) and improvement potential.
    
    Compares the best available PRS performance against heritability ceiling.
    """
    aggregator = get_aggregator()
    return aggregator.gap_analysis(trait, prs_r2=prs_r2, prs_id=prs_id)


@router.get("/sources/available")
async def get_available_sources() -> dict:
    """List available heritability data sources and their statistics."""
    aggregator = get_aggregator()
    
    return {
        "sources": [
            {
                "id": "gwas_atlas",
                "name": "GWAS Atlas",
                "url": "https://atlas.ctglab.nl/traitDB",
                "trait_count": aggregator.gwas_atlas.get_trait_count(),
                "description": "3,302 traits from 4,756 GWAS with LD score regression"
            },
            {
                "id": "pan_ukb",
                "name": "Pan-UK Biobank",
                "url": "https://pan.ukbb.broadinstitute.org/",
                "ancestries": aggregator.pan_ukb.get_available_ancestries(),
                "description": "Multi-ancestry GWAS for 7,228 phenotypes"
            },
            {
                "id": "ukbb_ldsc",
                "name": "UKBB LDSC (Neale Lab)",
                "url": "https://nealelab.github.io/UKBB_ldsc/",
                "trait_count": len(aggregator.ukbb_ldsc.get_all_traits()),
                "description": "2,419 UK Biobank phenotypes (European ancestry)"
            }
        ]
    }
