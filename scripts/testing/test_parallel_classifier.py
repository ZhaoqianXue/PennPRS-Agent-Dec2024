#!/usr/bin/env python3
"""
Test the optimized parallel classifier with gpt-4.1-nano model.

Compares:
1. Sequential classification (1 thread)
2. Parallel classification (max threads)
"""

import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    from src.modules.literature.pubmed import PubMedClient
    from src.modules.literature.paper_classifier import PaperClassifier
    from src.core.llm_config import get_config
    
    NUM_PAPERS = 6  # Test with 6 papers
    
    print("=" * 70)
    print("🚀 PARALLEL CLASSIFIER PERFORMANCE TEST")
    print("=" * 70)
    
    # Check model configuration
    config = get_config("literature_classifier")
    print(f"\n📋 Configuration:")
    print(f"   Model: {config.model}")
    print(f"   Temperature: {config.temperature}")
    print(f"   Timeout: {config.timeout}s")
    
    # Fetch test papers
    print(f"\n📄 Fetching {NUM_PAPERS} test papers...")
    pubmed = PubMedClient()
    search_result = pubmed.search_prs_papers("Alzheimer's Disease", max_results=NUM_PAPERS)
    papers = pubmed.fetch_papers(search_result.pmids[:NUM_PAPERS])
    print(f"   Got {len(papers)} papers")
    
    classifier = PaperClassifier()
    
    # =========================================================================
    # Test 1: Sequential (1 worker)
    # =========================================================================
    print("\n" + "-" * 70)
    print("1️⃣ SEQUENTIAL CLASSIFICATION (1 worker)")
    print("-" * 70)
    
    def progress_seq(current, total):
        print(f"   Progress: {current}/{total}")
    
    start_seq = time.perf_counter()
    results_seq = classifier.classify_batch(papers, progress_callback=progress_seq, max_workers=1)
    end_seq = time.perf_counter()
    
    time_seq_ms = (end_seq - start_seq) * 1000
    time_seq_per_paper = time_seq_ms / len(papers)
    
    print(f"\n   ⏱️  Total time: {time_seq_ms:.2f}ms ({time_seq_ms/1000:.2f}s)")
    print(f"   ⏱️  Per paper: {time_seq_per_paper:.2f}ms ({time_seq_per_paper/1000:.2f}s)")
    
    # =========================================================================
    # Test 2: Parallel (max workers)
    # =========================================================================
    print("\n" + "-" * 70)
    
    # Determine max workers
    cpu_count = os.cpu_count() or 4
    max_workers = min(cpu_count * 2, len(papers), 10)
    
    print(f"2️⃣ PARALLEL CLASSIFICATION ({max_workers} workers)")
    print("-" * 70)
    
    def progress_par(current, total):
        print(f"   Progress: {current}/{total}")
    
    start_par = time.perf_counter()
    results_par = classifier.classify_batch(papers, progress_callback=progress_par, max_workers=max_workers)
    end_par = time.perf_counter()
    
    time_par_ms = (end_par - start_par) * 1000
    time_par_per_paper = time_par_ms / len(papers)
    
    print(f"\n   ⏱️  Total time: {time_par_ms:.2f}ms ({time_par_ms/1000:.2f}s)")
    print(f"   ⏱️  Per paper (wall clock): {time_par_per_paper:.2f}ms ({time_par_per_paper/1000:.2f}s)")
    
    # =========================================================================
    # Comparison
    # =========================================================================
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 70)
    
    speedup = time_seq_ms / time_par_ms if time_par_ms > 0 else 0
    
    print(f"\n{'Method':<35} {'Total Time':>15} {'Per Paper':>15} {'Speedup':>10}")
    print("-" * 80)
    print(f"{'Sequential (1 worker)':<35} {time_seq_ms/1000:>13.2f}s {time_seq_per_paper/1000:>13.2f}s {'1.0x':>10}")
    print(f"{'Parallel (' + str(max_workers) + ' workers)':<35} {time_par_ms/1000:>13.2f}s {time_par_per_paper/1000:>13.2f}s {speedup:>9.1f}x")
    print("-" * 80)
    
    # Baseline comparison (gpt-5-nano was 24.2s per paper)
    baseline_per_paper_ms = 24242
    speedup_vs_baseline = baseline_per_paper_ms / time_par_per_paper if time_par_per_paper > 0 else 0
    
    print(f"\n📈 VS BASELINE (gpt-5-nano sequential):")
    print(f"   Baseline: 24.2s per paper")
    print(f"   Optimized: {time_par_per_paper/1000:.2f}s per paper")
    print(f"   Total speedup: {speedup_vs_baseline:.1f}x faster")
    
    # Results validation
    print("\n" + "=" * 70)
    print("📋 CLASSIFICATION RESULTS")
    print("=" * 70)
    
    categories = {}
    for r in results_par:
        cat = r.primary_category.value
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n{'PMID':<12} {'Category':<25} {'Confidence':>10}")
    print("-" * 50)
    for r in results_par:
        print(f"{r.pmid:<12} {r.primary_category.value:<25} {r.overall_confidence:>10.2f}")
    
    print(f"\n📊 Category Distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        pct = count / len(results_par) * 100
        bar = "█" * int(pct / 5)
        print(f"   {cat:<25} {count:>3} ({pct:5.1f}%) {bar}")
    
    # Projection for 100 papers
    print("\n" + "=" * 70)
    print("⚡ PERFORMANCE PROJECTIONS")
    print("=" * 70)
    
    papers_100_baseline = baseline_per_paper_ms * 100 / 60000  # minutes
    papers_100_optimized = time_par_per_paper * 100 / 60000  # minutes
    
    print(f"\n   For 100 papers:")
    print(f"   - Baseline (gpt-5-nano, sequential): {papers_100_baseline:.1f} minutes")
    print(f"   - Optimized (gpt-4.1-nano, parallel): {papers_100_optimized:.1f} minutes")
    print(f"   - Time saved: {papers_100_baseline - papers_100_optimized:.1f} minutes")
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
