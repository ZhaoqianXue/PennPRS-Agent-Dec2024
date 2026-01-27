#!/usr/bin/env python3
"""
Test classifier accuracy using PGS Catalog publications.

All 756 publications in PGS Catalog should theoretically be classified as 
PRS_PERFORMANCE since they contain PRS-related data.

This tests the classifier's recall rate on known PRS papers.
"""

import sys
import os
import json
import time
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_pgs_catalog_publications() -> List[str]:
    """
    Fetch all publication PMIDs from PGS Catalog API.
    
    API endpoint: https://www.pgscatalog.org/rest/publication/all
    """
    print("📥 Fetching publications from PGS Catalog API...")
    
    all_pmids = []
    url = "https://www.pgscatalog.org/rest/publication/all"
    
    try:
        # PGS Catalog API is paginated
        next_url = url
        page = 1
        
        while next_url:
            print(f"   Fetching page {page}...", end=" ")
            response = requests.get(next_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            for pub in results:
                pmid = pub.get("PMID")
                if pmid:
                    all_pmids.append(str(pmid))
            
            print(f"got {len(results)} publications")
            
            next_url = data.get("next")
            page += 1
            
            # Small delay to be nice to the API
            time.sleep(0.1)
        
        print(f"\n   Total PMIDs: {len(all_pmids)}")
        return all_pmids
        
    except Exception as e:
        print(f"\n❌ Error fetching from PGS Catalog: {e}")
        return []


def fetch_paper_metadata(pmids: List[str], batch_size: int = 100) -> List[Any]:
    """
    Fetch paper metadata from PubMed for given PMIDs.
    """
    from src.modules.literature.pubmed import PubMedClient
    
    pubmed = PubMedClient()
    all_papers = []
    
    print(f"\n📄 Fetching metadata from PubMed for {len(pmids)} papers...")
    
    # Fetch in batches
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        print(f"   Batch {i//batch_size + 1}/{(len(pmids)-1)//batch_size + 1}: fetching {len(batch)} papers...")
        
        papers = pubmed.fetch_papers(batch)
        all_papers.extend(papers)
        
        # Small delay
        time.sleep(0.5)
    
    print(f"   Total papers fetched: {len(all_papers)}")
    return all_papers


def run_classification_test(papers: List[Any]) -> Dict[str, Any]:
    """
    Run the classifier on all papers and calculate accuracy.
    """
    from src.modules.literature.paper_classifier import PaperClassifier
    from src.modules.literature.entities import PaperCategory
    
    classifier = PaperClassifier()
    
    print(f"\n🚀 Classifying {len(papers)} papers with parallel threads...")
    print(f"   (This may take a minute...)")
    
    start = time.perf_counter()
    
    # Progress tracking
    classified = [0]
    def progress(current, total):
        if current % 50 == 0 or current == total:
            elapsed = time.perf_counter() - start
            rate = current / elapsed if elapsed > 0 else 0
            remaining = (total - current) / rate if rate > 0 else 0
            print(f"   Progress: {current}/{total} ({current/total*100:.1f}%) - {rate:.1f} papers/sec - ETA: {remaining:.0f}s")
    
    results = classifier.classify_batch(papers, progress_callback=progress)
    
    end = time.perf_counter()
    total_time_s = end - start
    
    # Calculate statistics
    categories = {}
    prs_correct = 0
    prs_with_multi = 0  # Papers that have PRS as one of their categories
    confidences = []
    errors = []
    
    for result in results:
        cat = result.primary_category.value
        categories[cat] = categories.get(cat, 0) + 1
        
        if cat == "PRS_PERFORMANCE":
            prs_correct += 1
            confidences.append(result.overall_confidence)
        
        # Check if PRS is in any of the categories (multi-label)
        for cat_score in result.categories:
            if cat_score.category == PaperCategory.PRS_PERFORMANCE:
                prs_with_multi += 1
                break
        
        # Track errors
        if result.overall_confidence == 0.0 and "error" in result.llm_reasoning.lower():
            errors.append(result.pmid)
    
    # Calculate metrics
    total = len(results)
    accuracy = prs_correct / total if total > 0 else 0
    recall_multi = prs_with_multi / total if total > 0 else 0
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        "total_papers": total,
        "total_time_s": total_time_s,
        "time_per_paper_ms": (total_time_s * 1000) / total if total > 0 else 0,
        "papers_per_second": total / total_time_s if total_time_s > 0 else 0,
        "categories": categories,
        "prs_primary": prs_correct,
        "prs_any_category": prs_with_multi,
        "accuracy_primary": accuracy,
        "accuracy_multi_label": recall_multi,
        "avg_prs_confidence": avg_confidence,
        "errors_count": len(errors),
        "error_pmids": errors[:10],  # First 10 errors
        "results": results
    }


def main():
    print("=" * 70)
    print("🧪 PGS CATALOG CLASSIFIER ACCURACY TEST")
    print("=" * 70)
    print("\nThis test uses all publications from PGS Catalog as ground truth.")
    print("These papers should all be classified as PRS_PERFORMANCE.\n")
    
    # Step 1: Fetch PMIDs from PGS Catalog
    pmids = fetch_pgs_catalog_publications()
    
    if not pmids:
        print("❌ Failed to fetch PMIDs from PGS Catalog")
        return
    
    # Step 2: Fetch paper metadata from PubMed
    papers = fetch_paper_metadata(pmids)
    
    if not papers:
        print("❌ Failed to fetch paper metadata from PubMed")
        return
    
    # Step 3: Run classification
    results = run_classification_test(papers)
    
    # Step 4: Print results
    print("\n" + "=" * 70)
    print("📊 CLASSIFICATION RESULTS")
    print("=" * 70)
    
    print(f"\n📋 Summary:")
    print(f"   Total papers tested: {results['total_papers']}")
    print(f"   Total time: {results['total_time_s']:.2f}s ({results['total_time_s']/60:.2f} minutes)")
    print(f"   Speed: {results['time_per_paper_ms']:.2f}ms per paper ({results['papers_per_second']:.1f} papers/sec)")
    
    print(f"\n📈 Accuracy (Primary Category = PRS_PERFORMANCE):")
    print(f"   Correct: {results['prs_primary']}/{results['total_papers']}")
    print(f"   Accuracy: {results['accuracy_primary']*100:.2f}%")
    print(f"   Average confidence: {results['avg_prs_confidence']:.2f}")
    
    print(f"\n📈 Recall (PRS_PERFORMANCE in any category):")
    print(f"   Detected: {results['prs_any_category']}/{results['total_papers']}")
    print(f"   Recall: {results['accuracy_multi_label']*100:.2f}%")
    
    print(f"\n📊 Category Distribution:")
    for cat, count in sorted(results['categories'].items(), key=lambda x: -x[1]):
        pct = count / results['total_papers'] * 100
        bar = "█" * int(pct / 2)
        print(f"   {cat:<25} {count:>4} ({pct:5.1f}%) {bar}")
    
    if results['errors_count'] > 0:
        print(f"\n⚠️ Errors: {results['errors_count']} papers had parsing errors")
        print(f"   Sample error PMIDs: {results['error_pmids']}")
    
    # Save detailed results
    output_dir = project_root / "data" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"pgs_catalog_accuracy_test_{timestamp}.json"
    
    # Prepare serializable results
    output_data = {
        "timestamp": timestamp,
        "total_papers": results['total_papers'],
        "total_time_s": results['total_time_s'],
        "time_per_paper_ms": results['time_per_paper_ms'],
        "papers_per_second": results['papers_per_second'],
        "accuracy_primary": results['accuracy_primary'],
        "accuracy_multi_label": results['accuracy_multi_label'],
        "avg_prs_confidence": results['avg_prs_confidence'],
        "categories": results['categories'],
        "errors_count": results['errors_count'],
        "detailed_results": [
            {
                "pmid": r.pmid,
                "primary_category": r.primary_category.value,
                "confidence": r.overall_confidence,
                "categories": [
                    {"category": c.category.value, "confidence": c.confidence}
                    for c in r.categories
                ]
            }
            for r in results['results']
        ]
    }
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
