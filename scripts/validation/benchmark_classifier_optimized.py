#!/usr/bin/env python3
"""
Optimized Classifier Performance Test

This script tests various optimization strategies for the paper classifier:
1. Rule-based classifier (no LLM)
2. Cheaper/faster models (gpt-4o-mini)
3. Batch processing
4. Async parallel processing
5. Prompt size reduction

Usage:
    python scripts/benchmark_classifier_optimized.py
"""

import sys
import os
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Configure logging (less verbose)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_test_papers(num_papers: int = 5, disease: str = "Alzheimer's Disease"):
    """Fetch test papers from PubMed."""
    from src.modules.literature.pubmed import PubMedClient
    
    pubmed = PubMedClient()
    search_result = pubmed.search_prs_papers(disease, max_results=num_papers)
    papers = pubmed.fetch_papers(search_result.pmids[:num_papers])
    return papers


# ============================================================================
# Strategy 1: Rule-based Classifier (No LLM)
# ============================================================================

def benchmark_rule_based(papers):
    """Benchmark the rule-based classifier (no LLM calls)."""
    from src.modules.literature.paper_classifier import RuleBasedClassifier
    
    classifier = RuleBasedClassifier()
    
    start = time.perf_counter()
    results = []
    for paper in papers:
        result = classifier.classify(paper)
        results.append(result)
    end = time.perf_counter()
    
    total_ms = (end - start) * 1000
    avg_ms = total_ms / len(papers)
    
    return {
        "strategy": "Rule-based (No LLM)",
        "total_ms": total_ms,
        "avg_ms_per_paper": avg_ms,
        "papers": len(papers),
        "categories": {r.primary_category.value: 1 for r in results}
    }


# ============================================================================
# Strategy 2: Different LLM Models
# ============================================================================

def benchmark_model(papers, model_name: str):
    """Benchmark classification with a specific model."""
    from openai import OpenAI
    from src.modules.literature.prompts import get_prompt, format_user_prompt
    from src.modules.literature.schemas import PAPER_CLASSIFICATION_SCHEMA
    
    client = OpenAI()
    
    developer_prompt = get_prompt("classification", "developer")
    schema_json = json.dumps(PAPER_CLASSIFICATION_SCHEMA["json_schema"]["schema"], indent=2)
    
    start = time.perf_counter()
    results = []
    
    for paper in papers:
        user_prompt = format_user_prompt(
            "classification",
            pmid=paper.pmid,
            title=paper.title,
            abstract=paper.abstract[:4000] if paper.abstract else "(No abstract available)",
            journal=paper.journal or "Unknown",
            year=paper.publication_date.year if paper.publication_date else "Unknown"
        )
        
        messages = [
            {"role": "system", "content": developer_prompt},
            {"role": "user", "content": user_prompt + f"\n\nYou must output valid JSON strictly following this schema:\n```json\n{schema_json}\n```"}
        ]
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            results.append({
                "pmid": paper.pmid,
                "category": data.get("primary_category", "NOT_RELEVANT"),
                "success": True
            })
        except Exception as e:
            results.append({
                "pmid": paper.pmid,
                "category": "ERROR",
                "success": False,
                "error": str(e)
            })
    
    end = time.perf_counter()
    total_ms = (end - start) * 1000
    
    return {
        "strategy": f"Model: {model_name}",
        "total_ms": total_ms,
        "avg_ms_per_paper": total_ms / len(papers),
        "papers": len(papers),
        "success_rate": sum(1 for r in results if r["success"]) / len(results)
    }


# ============================================================================
# Strategy 3: Simplified Prompt (Reduced Token Count)
# ============================================================================

SIMPLIFIED_DEVELOPER_PROMPT = """You are a biomedical literature classifier. Classify papers into:

1. PRS_PERFORMANCE - Papers with polygenic risk score metrics (AUC, R², OR/HR per SD)
2. HERITABILITY - Papers with SNP-heritability (h²) estimates
3. GENETIC_CORRELATION - Papers with genetic correlation (rg) between traits
4. NOT_RELEVANT - No extractable genetic data

Return JSON with:
- classifications: array of {category, confidence (0-1), reasoning}
- primary_category: main category
- overall_reasoning: brief explanation"""

SIMPLIFIED_USER_TEMPLATE = """PMID: {pmid}
Title: {title}
Abstract: {abstract}

Classify this paper."""

SIMPLIFIED_SCHEMA = {
    "type": "object",
    "properties": {
        "primary_category": {"type": "string", "enum": ["PRS_PERFORMANCE", "HERITABILITY", "GENETIC_CORRELATION", "NOT_RELEVANT"]},
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "confidence": {"type": "number"},
                    "reasoning": {"type": "string"}
                }
            }
        },
        "overall_reasoning": {"type": "string"}
    },
    "required": ["primary_category", "classifications"]
}


def benchmark_simplified_prompt(papers, model_name: str = "gpt-4o-mini"):
    """Benchmark with simplified prompt (fewer tokens)."""
    from openai import OpenAI
    
    client = OpenAI()
    
    start = time.perf_counter()
    results = []
    
    for paper in papers:
        user_prompt = SIMPLIFIED_USER_TEMPLATE.format(
            pmid=paper.pmid,
            title=paper.title,
            abstract=paper.abstract[:2000] if paper.abstract else "(No abstract)"
        )
        
        messages = [
            {"role": "system", "content": SIMPLIFIED_DEVELOPER_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            results.append({
                "pmid": paper.pmid,
                "category": data.get("primary_category", "NOT_RELEVANT"),
                "success": True
            })
        except Exception as e:
            results.append({
                "pmid": paper.pmid,
                "category": "ERROR",
                "success": False
            })
    
    end = time.perf_counter()
    total_ms = (end - start) * 1000
    
    return {
        "strategy": f"Simplified Prompt + {model_name}",
        "total_ms": total_ms,
        "avg_ms_per_paper": total_ms / len(papers),
        "papers": len(papers),
        "success_rate": sum(1 for r in results if r["success"]) / len(results)
    }


# ============================================================================
# Strategy 4: Parallel Processing
# ============================================================================

def classify_single_paper(args):
    """Classify a single paper (for parallel execution)."""
    paper, model_name = args
    from openai import OpenAI
    
    client = OpenAI()
    
    user_prompt = SIMPLIFIED_USER_TEMPLATE.format(
        pmid=paper.pmid,
        title=paper.title,
        abstract=paper.abstract[:2000] if paper.abstract else "(No abstract)"
    )
    
    messages = [
        {"role": "system", "content": SIMPLIFIED_DEVELOPER_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=500
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return {
            "pmid": paper.pmid,
            "category": data.get("primary_category", "NOT_RELEVANT"),
            "success": True,
            "time_ms": (time.perf_counter() - start) * 1000
        }
    except Exception as e:
        return {
            "pmid": paper.pmid,
            "category": "ERROR",
            "success": False,
            "time_ms": (time.perf_counter() - start) * 1000
        }


def benchmark_parallel(papers, model_name: str = "gpt-4o-mini", max_workers: int = 3):
    """Benchmark with parallel processing."""
    
    start = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        args = [(paper, model_name) for paper in papers]
        results = list(executor.map(classify_single_paper, args))
    
    end = time.perf_counter()
    total_ms = (end - start) * 1000
    
    return {
        "strategy": f"Parallel ({max_workers} workers) + {model_name}",
        "total_ms": total_ms,
        "avg_ms_per_paper": total_ms / len(papers),
        "papers": len(papers),
        "success_rate": sum(1 for r in results if r["success"]) / len(results),
        "individual_times_ms": [r["time_ms"] for r in results]
    }


# ============================================================================
# Strategy 5: Batch API (if available)
# ============================================================================

def benchmark_batch_prompt(papers, model_name: str = "gpt-4o-mini"):
    """
    Benchmark with batching multiple papers in a single prompt.
    This reduces API call overhead but may affect quality.
    """
    from openai import OpenAI
    
    client = OpenAI()
    
    # Create a batch prompt with all papers
    papers_text = ""
    for i, paper in enumerate(papers):
        papers_text += f"""
Paper {i+1}:
- PMID: {paper.pmid}
- Title: {paper.title}
- Abstract: {(paper.abstract or 'N/A')[:1000]}
"""
    
    batch_prompt = f"""Classify the following {len(papers)} papers. For each paper, determine if it contains:
- PRS_PERFORMANCE: PRS model metrics (AUC, R², OR/HR per SD)
- HERITABILITY: SNP-heritability estimates (h²)
- GENETIC_CORRELATION: Genetic correlations (rg)
- NOT_RELEVANT: No extractable genetic data

{papers_text}

Return a JSON object with a "classifications" array, one entry per paper in order:
{{"classifications": [{{"pmid": "...", "primary_category": "...", "confidence": 0.X}}, ...]}}"""
    
    start = time.perf_counter()
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a biomedical literature classifier. Return valid JSON."},
                {"role": "user", "content": batch_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        success = True
        results = data.get("classifications", [])
    except Exception as e:
        success = False
        results = []
    
    end = time.perf_counter()
    total_ms = (end - start) * 1000
    
    return {
        "strategy": f"Batch (all papers in 1 call) + {model_name}",
        "total_ms": total_ms,
        "avg_ms_per_paper": total_ms / len(papers),
        "papers": len(papers),
        "success": success,
        "results_count": len(results)
    }


# ============================================================================
# Main Benchmark Runner
# ============================================================================

def run_all_benchmarks():
    print("=" * 70)
    print("🚀 CLASSIFIER OPTIMIZATION BENCHMARK")
    print("=" * 70)
    
    # Get test papers
    print("\n📄 Fetching test papers...")
    papers = get_test_papers(num_papers=3)
    print(f"   Got {len(papers)} papers")
    
    results = []
    
    # Strategy 1: Rule-based (baseline - fastest possible)
    print("\n" + "-" * 70)
    print("1️⃣ Testing Rule-based Classifier (No LLM)...")
    rule_result = benchmark_rule_based(papers)
    results.append(rule_result)
    print(f"   ⏱️ Total: {rule_result['total_ms']:.2f}ms")
    print(f"   ⏱️ Per paper: {rule_result['avg_ms_per_paper']:.2f}ms")
    
    # Strategy 2: gpt-4o-mini (faster model)
    print("\n" + "-" * 70)
    print("2️⃣ Testing gpt-4o-mini (faster model)...")
    gpt4o_mini_result = benchmark_model(papers, "gpt-4o-mini")
    results.append(gpt4o_mini_result)
    print(f"   ⏱️ Total: {gpt4o_mini_result['total_ms']:.2f}ms")
    print(f"   ⏱️ Per paper: {gpt4o_mini_result['avg_ms_per_paper']:.2f}ms")
    print(f"   ✅ Success rate: {gpt4o_mini_result['success_rate']*100:.1f}%")
    
    # Strategy 3: Simplified prompt
    print("\n" + "-" * 70)
    print("3️⃣ Testing Simplified Prompt + gpt-4o-mini...")
    simplified_result = benchmark_simplified_prompt(papers, "gpt-4o-mini")
    results.append(simplified_result)
    print(f"   ⏱️ Total: {simplified_result['total_ms']:.2f}ms")
    print(f"   ⏱️ Per paper: {simplified_result['avg_ms_per_paper']:.2f}ms")
    print(f"   ✅ Success rate: {simplified_result['success_rate']*100:.1f}%")
    
    # Strategy 4: Parallel processing
    print("\n" + "-" * 70)
    print("4️⃣ Testing Parallel Processing (3 workers)...")
    parallel_result = benchmark_parallel(papers, "gpt-4o-mini", max_workers=3)
    results.append(parallel_result)
    print(f"   ⏱️ Total: {parallel_result['total_ms']:.2f}ms")
    print(f"   ⏱️ Per paper: {parallel_result['avg_ms_per_paper']:.2f}ms (wall clock)")
    print(f"   ✅ Success rate: {parallel_result['success_rate']*100:.1f}%")
    
    # Strategy 5: Batch processing
    print("\n" + "-" * 70)
    print("5️⃣ Testing Batch Processing (all papers in 1 call)...")
    batch_result = benchmark_batch_prompt(papers, "gpt-4o-mini")
    results.append(batch_result)
    print(f"   ⏱️ Total: {batch_result['total_ms']:.2f}ms")
    print(f"   ⏱️ Per paper: {batch_result['avg_ms_per_paper']:.2f}ms")
    print(f"   ✅ Success: {batch_result['success']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 BENCHMARK COMPARISON")
    print("=" * 70)
    
    # Sort by total time
    sorted_results = sorted(results, key=lambda x: x['total_ms'])
    
    baseline_time = 24242  # From previous benchmark (gpt-5-nano)
    
    print(f"\n{'Strategy':<45} {'Total (ms)':>12} {'Per Paper':>12} {'Speedup':>10}")
    print("-" * 85)
    
    for r in sorted_results:
        speedup = baseline_time / r['avg_ms_per_paper'] if r['avg_ms_per_paper'] > 0 else 0
        print(f"{r['strategy']:<45} {r['total_ms']:>10.1f}ms {r['avg_ms_per_paper']:>10.1f}ms {speedup:>9.1f}x")
    
    print("-" * 85)
    print(f"{'BASELINE (gpt-5-nano)':<45} {'72728.0ms':>12} {'24242.0ms':>12} {'1.0x':>10}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)
    
    fastest_llm = min([r for r in results if 'gpt' in r['strategy'].lower()], key=lambda x: x['avg_ms_per_paper'])
    
    print(f"""
🏆 Best LLM Strategy: {fastest_llm['strategy']}
   - {fastest_llm['avg_ms_per_paper']:.1f}ms per paper
   - {baseline_time / fastest_llm['avg_ms_per_paper']:.1f}x faster than baseline

📋 Optimization Recommendations:
1. ✅ Switch from gpt-5-nano to gpt-4o-mini (faster model)
2. ✅ Use simplified prompt (fewer input tokens)
3. ✅ Use parallel processing for multiple papers
4. ✅ Consider batch processing for bulk classification
5. 🔧 For highest speed: use Rule-based pre-filter → LLM only for uncertain cases

📈 Expected Performance Improvements:
   - Current: ~24s per paper (gpt-5-nano)
   - Optimized: ~{fastest_llm['avg_ms_per_paper']/1000:.1f}s per paper (gpt-4o-mini + optimizations)
   - Speedup: {baseline_time / fastest_llm['avg_ms_per_paper']:.0f}x faster
   
   For 100 papers:
   - Current: ~40 minutes
   - Optimized: ~{fastest_llm['avg_ms_per_paper'] * 100 / 60000:.1f} minutes (or less with parallelism)
""")
    
    # Save results
    output_dir = project_root / "data" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"optimization_benchmark_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "baseline_avg_ms": baseline_time,
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    run_all_benchmarks()
