#!/usr/bin/env python3
"""
Build Heritability Ground Truth Dataset

Creates a validation dataset for testing the Heritability classifier with:
- Positive samples: Papers whose abstracts mention heritability estimates
- Negative samples: PRS papers from PGS Catalog (that don't mention heritability)

Output: data/validation/heritability_gold_standard.json

Usage:
    python scripts/build_heritability_ground_truth.py
"""

import sys
import os
import json
import csv
import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.literature.pubmed import PubMedClient
from modules.literature.entities import PaperMetadata

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Constants
# ============================================================================

# Target counts
TARGET_POSITIVE_SAMPLES = 100
TARGET_NEGATIVE_SAMPLES = 100

# PubMed search queries for heritability papers
HERITABILITY_SEARCH_QUERIES = [
    # Primary: Papers explicitly mentioning SNP heritability in abstract
    '("SNP heritability"[Title/Abstract] OR "SNP-heritability"[Title/Abstract])',
    # Secondary: LDSC heritability papers
    '("LD score regression"[Title/Abstract] AND heritability[Title/Abstract])',
    # Tertiary: GCTA heritability papers  
    '(GCTA[Title/Abstract] AND "heritability"[Title/Abstract] AND "h2"[Title/Abstract])',
]

# Keywords that indicate a paper reports heritability in abstract
HERITABILITY_KEYWORDS = [
    r'h[²2]\s*[=≈~]\s*\d',          # h² = 0.XX or h2 = 0.XX
    r'heritability\s*(?:was|of|is|=|:)\s*\d',  # heritability was 0.XX
    r'SNP[- ]heritability',          # SNP heritability or SNP-heritability
    r'h2\s*=\s*\d',                   # h2 = 0.XX
    r'heritability estimate',         # heritability estimate
    r'narrow-sense heritability',     # narrow-sense heritability
    r'LDSC.*heritab',                 # LDSC...heritability
    r'GCTA.*heritab',                 # GCTA...heritability
    r'GREML.*heritab',                # GREML...heritability
]

# Keywords that indicate a paper is likely NOT about heritability
NON_HERITABILITY_INDICATORS = [
    'polygenic risk score',
    'polygenic score',
    'genetic risk score',
    'PRS',
    'risk prediction',
    'predictive accuracy',
    'AUC',
    'C-statistic',
]


# ============================================================================
# Helper Functions
# ============================================================================

def has_heritability_in_abstract(abstract: str) -> Tuple[bool, List[str]]:
    """
    Check if abstract contains heritability-related content.
    
    Returns:
        Tuple of (is_heritability, matched_patterns)
    """
    if not abstract:
        return False, []
    
    abstract_lower = abstract.lower()
    matched = []
    
    for pattern in HERITABILITY_KEYWORDS:
        if re.search(pattern, abstract, re.IGNORECASE):
            matched.append(pattern)
    
    return len(matched) > 0, matched


def is_prs_paper_without_heritability(abstract: str) -> bool:
    """
    Check if a paper is primarily about PRS without heritability content.
    Good candidate for negative sample.
    """
    if not abstract:
        return False
    
    abstract_lower = abstract.lower()
    
    # Must have PRS indicators
    has_prs = any(kw.lower() in abstract_lower for kw in ['polygenic risk score', 'polygenic score', 'PRS', 'genetic risk score'])
    
    # Must NOT have heritability indicators
    has_herit, _ = has_heritability_in_abstract(abstract)
    
    return has_prs and not has_herit


def load_pgs_catalog_pmids() -> List[str]:
    """Load PMIDs from PGS Catalog publications."""
    csv_path = Path(__file__).parent.parent / "data" / "pgs_all_metadata" / "pgs_all_metadata_publications.csv"
    
    pmids = []
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pmid = row.get('PubMed ID (PMID)', '').strip()
                if pmid and pmid.isdigit():
                    pmids.append(pmid)
    
    logger.info(f"Loaded {len(pmids)} PMIDs from PGS Catalog publications")
    return pmids


# ============================================================================
# Main Dataset Building Functions
# ============================================================================

async def collect_positive_samples(client: PubMedClient, target_count: int) -> List[Dict[str, Any]]:
    """
    Collect positive samples (papers with heritability in abstract).
    
    Uses PubMed search to find papers that explicitly mention heritability.
    """
    logger.info(f"Collecting ~{target_count} positive samples (heritability papers)...")
    
    all_pmids = set()
    
    # Search using each query
    for query in HERITABILITY_SEARCH_QUERIES:
        try:
            result = client.search(
                query=query,
                max_results=100,
                date_from="2015/01/01",  # LDSC first published in 2015
                sort="relevance"
            )
            logger.info(f"Query '{query[:50]}...' returned {len(result.pmids)} results")
            all_pmids.update(result.pmids)
        except Exception as e:
            logger.error(f"Error searching with query '{query}': {e}")
    
    logger.info(f"Total unique PMIDs from searches: {len(all_pmids)}")
    
    # Fetch paper metadata
    pmid_list = list(all_pmids)[:200]  # Limit to avoid too many API calls
    papers = client.fetch_papers(pmid_list)
    logger.info(f"Fetched metadata for {len(papers)} papers")
    
    # Filter to papers that definitely have heritability in abstract
    positive_samples = []
    for paper in papers:
        has_herit, patterns = has_heritability_in_abstract(paper.abstract)
        if has_herit:
            # Convert date to string for JSON serialization
            pub_date = paper.publication_date
            if pub_date:
                pub_date_str = pub_date.isoformat() if hasattr(pub_date, 'isoformat') else str(pub_date)
            else:
                pub_date_str = None
            
            positive_samples.append({
                "pmid": paper.pmid,
                "title": paper.title,
                "abstract": paper.abstract,
                "publication_date": pub_date_str,
                "expected_classification": {
                    "is_heritability": True,
                    "confidence": "high"
                },
                "matched_patterns": patterns,
                "source": "pubmed_search",
                "validation_status": "auto_keyword_match"
            })
    
    logger.info(f"Filtered to {len(positive_samples)} papers with confirmed heritability keywords in abstract")
    
    # Limit to target count
    return positive_samples[:target_count]


async def collect_negative_samples(client: PubMedClient, target_count: int) -> List[Dict[str, Any]]:
    """
    Collect negative samples (papers without heritability in abstract).
    
    Uses PGS Catalog publications as source - these are PRS papers,
    most of which don't report heritability in their abstracts.
    """
    logger.info(f"Collecting ~{target_count} negative samples (non-heritability papers)...")
    
    # Load PGS Catalog PMIDs
    pgs_pmids = load_pgs_catalog_pmids()
    
    if not pgs_pmids:
        logger.error("No PMIDs found from PGS Catalog!")
        return []
    
    # Sample more than needed to account for filtering
    sample_size = min(len(pgs_pmids), target_count * 2)
    import random
    random.seed(42)  # Reproducible sampling
    sampled_pmids = random.sample(pgs_pmids, sample_size)
    
    # Fetch paper metadata
    papers = client.fetch_papers(sampled_pmids)
    logger.info(f"Fetched metadata for {len(papers)} PGS Catalog papers")
    
    # Filter to papers that don't mention heritability
    negative_samples = []
    skipped_has_heritability = 0
    
    for paper in papers:
        has_herit, _ = has_heritability_in_abstract(paper.abstract)
        
        if has_herit:
            skipped_has_heritability += 1
            continue
        
        # Convert date to string for JSON serialization
        pub_date = paper.publication_date
        if pub_date:
            pub_date_str = pub_date.isoformat() if hasattr(pub_date, 'isoformat') else str(pub_date)
        else:
            pub_date_str = None
        
        negative_samples.append({
            "pmid": paper.pmid,
            "title": paper.title,
            "abstract": paper.abstract,
            "publication_date": pub_date_str,
            "expected_classification": {
                "is_heritability": False,
                "confidence": "high"
            },
            "reason": "PGS Catalog paper without heritability keywords in abstract",
            "source": "pgs_catalog",
            "validation_status": "auto_keyword_absence"
        })
    
    logger.info(f"Filtered to {len(negative_samples)} papers without heritability keywords")
    logger.info(f"Skipped {skipped_has_heritability} papers that mentioned heritability")
    
    # Limit to target count
    return negative_samples[:target_count]


async def build_ground_truth_dataset():
    """Main function to build the ground truth dataset."""
    logger.info("=" * 60)
    logger.info("Building Heritability Ground Truth Dataset")
    logger.info("=" * 60)
    
    output_dir = Path(__file__).parent.parent / "data" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "heritability_gold_standard.json"
    
    # Initialize PubMed client
    client = PubMedClient()
    
    try:
        # Collect positive samples
        positive_samples = await collect_positive_samples(client, TARGET_POSITIVE_SAMPLES)
        
        # Collect negative samples
        negative_samples = await collect_negative_samples(client, TARGET_NEGATIVE_SAMPLES)
        
        # Build final dataset
        dataset = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Ground truth dataset for validating Heritability classifier",
                "positive_sample_source": "PubMed search for heritability keywords in abstract",
                "negative_sample_source": "PGS Catalog publications without heritability keywords",
                "total_positive": len(positive_samples),
                "total_negative": len(negative_samples),
                "total_papers": len(positive_samples) + len(negative_samples)
            },
            "positive_samples": positive_samples,
            "negative_samples": negative_samples
        }
        
        # Save dataset
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info("=" * 60)
        logger.info("Dataset Build Complete!")
        logger.info("=" * 60)
        logger.info(f"Output file: {output_file}")
        logger.info(f"Positive samples: {len(positive_samples)}")
        logger.info(f"Negative samples: {len(negative_samples)}")
        logger.info(f"Total papers: {len(positive_samples) + len(negative_samples)}")
        
        # Print sample statistics
        if positive_samples:
            logger.info("\nSample positive paper:")
            sample = positive_samples[0]
            logger.info(f"  PMID: {sample['pmid']}")
            logger.info(f"  Title: {sample['title'][:80]}...")
            logger.info(f"  Patterns: {sample.get('matched_patterns', [])}")
        
        if negative_samples:
            logger.info("\nSample negative paper:")
            sample = negative_samples[0]
            logger.info(f"  PMID: {sample['pmid']}")
            logger.info(f"  Title: {sample['title'][:80]}...")
        
        return dataset
        
    finally:
        client.close()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    asyncio.run(build_ground_truth_dataset())
