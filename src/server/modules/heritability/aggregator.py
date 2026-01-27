"""
Heritability aggregator combining multiple data sources.
"""
import logging
from typing import Optional

from src.server.modules.heritability.models import (
    HeritabilityEstimate,
    HeritabilitySource,
    GapAnalysisResult
)
from src.server.modules.heritability.gwas_atlas_client import GWASAtlasClient
from src.server.modules.heritability.pan_ukb_client import PanUKBClient
from src.server.modules.heritability.ukbb_ldsc_client import UKBBLDSCClient

logger = logging.getLogger(__name__)


class HeritabilityAggregator:
    """
    Aggregates heritability data from multiple sources.
    
    Provides unified search across GWAS Atlas, Pan-UK Biobank, and UKBB LDSC.
    """
    
    def __init__(self):
        """Initialize all data source clients."""
        self.gwas_atlas = GWASAtlasClient()
        self.pan_ukb = PanUKBClient()
        self.ukbb_ldsc = UKBBLDSCClient()
    
    def search(
        self,
        trait: str,
        sources: Optional[list[HeritabilitySource]] = None,
        ancestry: Optional[str] = None,
        min_score: int = 60,
        limit: int = 100
    ) -> list[HeritabilityEstimate]:
        """
        Search for heritability estimates across all sources.
        
        Args:
            trait: Trait name to search
            sources: Limit to specific sources (None = all)
            ancestry: Filter by ancestry code
            min_score: Minimum fuzzy match score
            limit: Maximum results per source
            
        Returns:
            Combined list of HeritabilityEstimate objects
        """
        results: list[HeritabilityEstimate] = []
        
        # Default to all sources
        if sources is None:
            sources = list(HeritabilitySource)
        
        try:
            if HeritabilitySource.GWAS_ATLAS in sources:
                gwas_results = self.gwas_atlas.search_trait(
                    trait, min_score=min_score, limit=limit
                )
                if ancestry:
                    gwas_results = [r for r in gwas_results if r.population == ancestry]
                results.extend(gwas_results)
        except Exception as e:
            logger.error(f"GWAS Atlas search failed: {e}")
        
        try:
            if HeritabilitySource.PAN_UKB in sources:
                pan_results = self.pan_ukb.search_trait(
                    trait, ancestry=ancestry, min_score=min_score, limit=limit
                )
                results.extend(pan_results)
        except Exception as e:
            logger.error(f"Pan-UKB search failed: {e}")
        
        try:
            if HeritabilitySource.UKBB_LDSC in sources:
                ldsc_results = self.ukbb_ldsc.search_trait(
                    trait, min_score=min_score, limit=limit
                )
                if ancestry:
                    ldsc_results = [r for r in ldsc_results if r.population == ancestry]
                results.extend(ldsc_results)
        except Exception as e:
            logger.error(f"UKBB LDSC search failed: {e}")
        
        return results
    
    def get_best_estimate(
        self,
        trait: str,
        ancestry: str = "EUR"
    ) -> Optional[HeritabilityEstimate]:
        """
        Get the highest-confidence heritability estimate.
        
        Selection criteria (in order):
        1. Higher sample size
        2. Lower standard error  
        3. Source priority: GWAS Atlas > UKBB LDSC > Pan-UKB
        
        Args:
            trait: Trait name
            ancestry: Target ancestry
            
        Returns:
            Best HeritabilityEstimate or None
        """
        all_results = self.search(trait, ancestry=ancestry, min_score=70)
        
        if not all_results:
            return None
        
        # Sort by confidence criteria
        def confidence_score(est: HeritabilityEstimate) -> tuple:
            n_samples = est.n_samples or 0
            se_inv = 1.0 / (est.h2_obs_se + 0.001) if est.h2_obs_se else 0
            source_priority = {
                HeritabilitySource.GWAS_ATLAS: 3,
                HeritabilitySource.UKBB_LDSC: 2,
                HeritabilitySource.PAN_UKB: 1
            }
            return (n_samples, se_inv, source_priority.get(est.source, 0))
        
        all_results.sort(key=confidence_score, reverse=True)
        return all_results[0]
    
    def get_by_source(self, trait: str) -> dict[str, list[HeritabilityEstimate]]:
        """Group heritability estimates by data source."""
        all_results = self.search(trait)
        
        by_source: dict[str, list[HeritabilityEstimate]] = {}
        for est in all_results:
            source_name = est.source.value
            if source_name not in by_source:
                by_source[source_name] = []
            by_source[source_name].append(est)
        
        return by_source
    
    def get_by_ancestry(self, trait: str) -> dict[str, list[HeritabilityEstimate]]:
        """Group heritability estimates by ancestry."""
        all_results = self.search(trait)
        
        by_ancestry: dict[str, list[HeritabilityEstimate]] = {}
        for est in all_results:
            if est.population not in by_ancestry:
                by_ancestry[est.population] = []
            by_ancestry[est.population].append(est)
        
        return by_ancestry
    
    def gap_analysis(
        self,
        trait: str,
        prs_r2: Optional[float] = None,
        prs_id: Optional[str] = None
    ) -> GapAnalysisResult:
        """
        Calculate PRS efficiency (R²/h²) and improvement potential.
        
        Args:
            trait: Trait name
            prs_r2: Best PRS R² (if known)
            prs_id: PRS ID (if known)
            
        Returns:
            GapAnalysisResult with efficiency and interpretation
        """
        best_h2 = self.get_best_estimate(trait)
        
        result = GapAnalysisResult(
            trait_name=trait,
            best_h2=best_h2.h2_obs if best_h2 else None,
            best_h2_source=best_h2.source.value if best_h2 else None,
            best_prs_r2=prs_r2,
            best_prs_id=prs_id
        )
        
        if best_h2 and prs_r2 and best_h2.h2_obs > 0:
            efficiency = prs_r2 / best_h2.h2_obs
            result.efficiency = min(efficiency, 1.0)  # Cap at 100%
            result.improvement_potential = 1.0 - result.efficiency
            
            # Generate interpretation
            if efficiency >= 0.8:
                result.interpretation = (
                    f"Excellent: PRS captures {efficiency*100:.0f}% of heritability. "
                    "Near theoretical maximum."
                )
            elif efficiency >= 0.5:
                result.interpretation = (
                    f"Good: PRS captures {efficiency*100:.0f}% of heritability. "
                    f"{result.improvement_potential*100:.0f}% improvement possible."
                )
            elif efficiency >= 0.25:
                result.interpretation = (
                    f"Moderate: PRS captures {efficiency*100:.0f}% of heritability. "
                    "Consider larger GWAS or multi-trait approaches."
                )
            else:
                result.interpretation = (
                    f"Low: PRS captures only {efficiency*100:.0f}% of heritability. "
                    "Significant room for improvement via larger GWAS."
                )
        elif best_h2:
            result.interpretation = (
                f"Heritability h² = {best_h2.h2_obs:.2f} from {best_h2.source.value}. "
                "No PRS R² provided for gap analysis."
            )
        else:
            result.interpretation = "No heritability data found for this trait."
        
        return result
