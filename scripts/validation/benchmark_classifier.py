#!/usr/bin/env python3
"""
Classifier Performance Benchmark

This script benchmarks the paper classifier to identify performance bottlenecks.
It measures time spent in each stage:
1. Prompt preparation
2. LLM API call
3. Response parsing
4. Result processing

Usage:
    python scripts/benchmark_classifier.py
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

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


@dataclass
class TimingResult:
    """Timing result for a single classification."""
    pmid: str
    title: str
    
    # Stage timings (in seconds)
    prompt_preparation_ms: float = 0.0
    api_call_ms: float = 0.0
    response_parsing_ms: float = 0.0
    total_ms: float = 0.0
    
    # Result info
    primary_category: str = ""
    confidence: float = 0.0
    success: bool = True
    error: str = ""
    
    # Token counts (estimated)
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class BenchmarkSummary:
    """Summary of benchmark results."""
    timestamp: str = ""
    model_name: str = ""
    num_papers: int = 0
    
    # Aggregate timings (ms)
    total_time_ms: float = 0.0
    avg_time_per_paper_ms: float = 0.0
    
    # Stage breakdown (ms)
    avg_prompt_preparation_ms: float = 0.0
    avg_api_call_ms: float = 0.0
    avg_response_parsing_ms: float = 0.0
    
    # Stage percentages
    prompt_preparation_pct: float = 0.0
    api_call_pct: float = 0.0
    response_parsing_pct: float = 0.0
    
    # Success rate
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    
    # Category distribution
    categories: Dict[str, int] = field(default_factory=dict)
    
    # Individual results
    results: List[TimingResult] = field(default_factory=list)


class InstrumentedPaperClassifier:
    """
    Instrumented version of PaperClassifier that tracks timing for each stage.
    """
    
    def __init__(self):
        self._client = None
        self._model_name = None
        self._config = None
        
    @property
    def client(self):
        if self._client is None:
            try:
                from src.core.llm_config import get_config
                from openai import OpenAI
                self._config = get_config("literature_classifier")
                self._model_name = self._config.model
                self._client = OpenAI()
                logger.info(f"Using model: {self._model_name}")
            except ImportError as e:
                logger.warning(f"Could not import llm_config: {e}. Using default.")
                from openai import OpenAI
                self._client = OpenAI()
                self._model_name = "gpt-4o-mini"
        return self._client
    
    @property
    def model_name(self) -> str:
        if self._model_name is None:
            _ = self.client
        return self._model_name or "unknown"
    
    def classify_with_timing(self, paper) -> TimingResult:
        """
        Classify a paper and return detailed timing information.
        """
        from src.modules.literature.prompts import get_prompt, format_user_prompt
        from src.modules.literature.schemas import PAPER_CLASSIFICATION_SCHEMA
        from src.modules.literature.entities import PaperCategory
        
        timing = TimingResult(
            pmid=paper.pmid,
            title=paper.title[:80] + "..." if len(paper.title) > 80 else paper.title
        )
        
        total_start = time.perf_counter()
        
        try:
            # ============================================
            # Stage 1: Prompt Preparation
            # ============================================
            prompt_start = time.perf_counter()
            
            developer_prompt = get_prompt("classification", "developer")
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
                {"role": "user", "content": user_prompt}
            ]
            
            # Add schema instructions
            schema_json = json.dumps(PAPER_CLASSIFICATION_SCHEMA["json_schema"]["schema"], indent=2)
            prompt_suffix = f"\n\nYou must output valid JSON strictly following this schema:\n```json\n{schema_json}\n```"
            messages[-1]["content"] += prompt_suffix
            
            prompt_end = time.perf_counter()
            timing.prompt_preparation_ms = (prompt_end - prompt_start) * 1000
            
            # Estimate input tokens (rough: ~4 chars per token)
            total_input_text = developer_prompt + user_prompt + prompt_suffix
            timing.input_tokens = len(total_input_text) // 4
            
            # ============================================
            # Stage 2: API Call
            # ============================================
            api_start = time.perf_counter()
            
            response = self.client.responses.create(
                model=self.model_name,
                input=messages
            )
            
            api_end = time.perf_counter()
            timing.api_call_ms = (api_end - api_start) * 1000
            
            # ============================================
            # Stage 3: Response Parsing
            # ============================================
            parse_start = time.perf_counter()
            
            # Extract content from response
            content = ""
            if hasattr(response, 'output'):
                if isinstance(response.output, list):
                    for block in response.output:
                        if hasattr(block, 'type') and block.type == 'message':
                            if hasattr(block, 'content') and isinstance(block.content, list):
                                for msg_part in block.content:
                                    if hasattr(msg_part, 'type') and msg_part.type == 'output_text':
                                        content = msg_part.text
                                        break
                            if content:
                                break
                else:
                    content = str(response.output)
            
            # Estimate output tokens
            timing.output_tokens = len(content) // 4
            
            # Parse JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            data = json.loads(content.strip())
            
            # Extract classification result
            primary_category = data.get("primary_category", "NOT_RELEVANT")
            
            # Get confidence from classifications
            overall_confidence = 0.0
            for cls in data.get("classifications", []):
                if cls.get("category") == primary_category:
                    overall_confidence = float(cls.get("confidence", 0.5))
                    break
            
            parse_end = time.perf_counter()
            timing.response_parsing_ms = (parse_end - parse_start) * 1000
            
            # Set result info
            timing.primary_category = primary_category
            timing.confidence = overall_confidence
            timing.success = True
            
        except Exception as e:
            timing.success = False
            timing.error = str(e)
            timing.primary_category = "ERROR"
            logger.error(f"Error classifying paper {paper.pmid}: {e}")
        
        total_end = time.perf_counter()
        timing.total_ms = (total_end - total_start) * 1000
        
        return timing


def run_benchmark(num_papers: int = 5, disease: str = "Alzheimer's Disease") -> BenchmarkSummary:
    """
    Run the classifier benchmark.
    
    Args:
        num_papers: Number of papers to classify
        disease: Disease to search for
    
    Returns:
        BenchmarkSummary with all timing information
    """
    from src.modules.literature.pubmed import PubMedClient
    
    summary = BenchmarkSummary(
        timestamp=datetime.now().isoformat(),
        num_papers=num_papers
    )
    
    print("=" * 70)
    print("📊 PAPER CLASSIFIER PERFORMANCE BENCHMARK")
    print("=" * 70)
    
    # Initialize components
    print("\n1️⃣ Initializing components...")
    pubmed = PubMedClient()
    classifier = InstrumentedPaperClassifier()
    summary.model_name = classifier.model_name
    print(f"   Model: {summary.model_name}")
    
    # Search for papers
    print(f"\n2️⃣ Searching for {num_papers} papers on '{disease}'...")
    search_start = time.perf_counter()
    search_result = pubmed.search_prs_papers(disease, max_results=num_papers)
    papers = pubmed.fetch_papers(search_result.pmids[:num_papers])
    search_time = (time.perf_counter() - search_start) * 1000
    print(f"   Found {len(papers)} papers in {search_time:.2f}ms")
    
    # Classify papers
    print(f"\n3️⃣ Classifying {len(papers)} papers...")
    print("-" * 70)
    
    results = []
    for i, paper in enumerate(papers):
        print(f"\n   [{i+1}/{len(papers)}] PMID: {paper.pmid}")
        print(f"   Title: {paper.title[:60]}...")
        
        timing = classifier.classify_with_timing(paper)
        results.append(timing)
        
        if timing.success:
            print(f"   ✅ Result: {timing.primary_category} (conf: {timing.confidence:.2f})")
        else:
            print(f"   ❌ Error: {timing.error[:50]}...")
        
        print(f"   ⏱️  Timing breakdown:")
        print(f"      - Prompt preparation: {timing.prompt_preparation_ms:7.2f}ms ({timing.prompt_preparation_ms/timing.total_ms*100:5.1f}%)")
        print(f"      - API call:           {timing.api_call_ms:7.2f}ms ({timing.api_call_ms/timing.total_ms*100:5.1f}%)")
        print(f"      - Response parsing:   {timing.response_parsing_ms:7.2f}ms ({timing.response_parsing_ms/timing.total_ms*100:5.1f}%)")
        print(f"      - TOTAL:              {timing.total_ms:7.2f}ms")
        print(f"   📊 Tokens: ~{timing.input_tokens} input, ~{timing.output_tokens} output")
    
    # Calculate summary statistics
    print("\n" + "=" * 70)
    print("📈 BENCHMARK SUMMARY")
    print("=" * 70)
    
    summary.results = results
    summary.num_papers = len(results)
    
    successful = [r for r in results if r.success]
    summary.success_count = len(successful)
    summary.failure_count = len(results) - len(successful)
    summary.success_rate = len(successful) / len(results) if results else 0
    
    if successful:
        summary.total_time_ms = sum(r.total_ms for r in successful)
        summary.avg_time_per_paper_ms = summary.total_time_ms / len(successful)
        
        summary.avg_prompt_preparation_ms = sum(r.prompt_preparation_ms for r in successful) / len(successful)
        summary.avg_api_call_ms = sum(r.api_call_ms for r in successful) / len(successful)
        summary.avg_response_parsing_ms = sum(r.response_parsing_ms for r in successful) / len(successful)
        
        total_avg = summary.avg_prompt_preparation_ms + summary.avg_api_call_ms + summary.avg_response_parsing_ms
        if total_avg > 0:
            summary.prompt_preparation_pct = (summary.avg_prompt_preparation_ms / total_avg) * 100
            summary.api_call_pct = (summary.avg_api_call_ms / total_avg) * 100
            summary.response_parsing_pct = (summary.avg_response_parsing_ms / total_avg) * 100
        
        # Category distribution
        for r in results:
            cat = r.primary_category
            summary.categories[cat] = summary.categories.get(cat, 0) + 1
    
    print(f"\n📋 Papers processed: {summary.num_papers}")
    print(f"✅ Success rate: {summary.success_rate*100:.1f}% ({summary.success_count}/{summary.num_papers})")
    print(f"🤖 Model: {summary.model_name}")
    
    print(f"\n⏱️  AVERAGE TIMING PER PAPER:")
    print(f"   {'Stage':<25} {'Time (ms)':>12} {'Percentage':>12}")
    print(f"   {'-'*25} {'-'*12} {'-'*12}")
    print(f"   {'Prompt preparation':<25} {summary.avg_prompt_preparation_ms:>10.2f}ms {summary.prompt_preparation_pct:>10.1f}%")
    print(f"   {'API call':<25} {summary.avg_api_call_ms:>10.2f}ms {summary.api_call_pct:>10.1f}%")
    print(f"   {'Response parsing':<25} {summary.avg_response_parsing_ms:>10.2f}ms {summary.response_parsing_pct:>10.1f}%")
    print(f"   {'-'*25} {'-'*12} {'-'*12}")
    print(f"   {'TOTAL':<25} {summary.avg_time_per_paper_ms:>10.2f}ms {'100.0%':>12}")
    
    print(f"\n📊 CATEGORY DISTRIBUTION:")
    for cat, count in sorted(summary.categories.items(), key=lambda x: -x[1]):
        pct = count / summary.num_papers * 100
        bar = "█" * int(pct / 5)
        print(f"   {cat:<25} {count:>3} ({pct:5.1f}%) {bar}")
    
    print(f"\n⚡ PERFORMANCE INSIGHTS:")
    if summary.api_call_pct > 90:
        print(f"   🔴 API call dominates ({summary.api_call_pct:.1f}%) - Consider:")
        print(f"      - Batch processing multiple papers per API call")
        print(f"      - Using a faster model (e.g., gpt-4o-mini)")
        print(f"      - Reducing prompt size")
    elif summary.api_call_pct > 70:
        print(f"   🟡 API call is main bottleneck ({summary.api_call_pct:.1f}%)")
        print(f"      - Consider async/parallel processing for multiple papers")
    else:
        print(f"   🟢 Well-balanced timing distribution")
    
    if summary.avg_time_per_paper_ms > 5000:
        print(f"   🔴 Slow classification ({summary.avg_time_per_paper_ms/1000:.1f}s per paper)")
        print(f"      - For 100 papers: ~{summary.avg_time_per_paper_ms * 100 / 60000:.1f} minutes")
    elif summary.avg_time_per_paper_ms > 2000:
        print(f"   🟡 Moderate speed ({summary.avg_time_per_paper_ms/1000:.1f}s per paper)")
    else:
        print(f"   🟢 Good speed ({summary.avg_time_per_paper_ms/1000:.1f}s per paper)")
    
    # Save results
    output_dir = project_root / "data" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"classifier_benchmark_{timestamp}.json"
    
    # Convert to serializable format
    output_data = {
        "timestamp": summary.timestamp,
        "model_name": summary.model_name,
        "num_papers": summary.num_papers,
        "total_time_ms": summary.total_time_ms,
        "avg_time_per_paper_ms": summary.avg_time_per_paper_ms,
        "timing_breakdown": {
            "avg_prompt_preparation_ms": summary.avg_prompt_preparation_ms,
            "avg_api_call_ms": summary.avg_api_call_ms,
            "avg_response_parsing_ms": summary.avg_response_parsing_ms,
        },
        "timing_percentages": {
            "prompt_preparation_pct": summary.prompt_preparation_pct,
            "api_call_pct": summary.api_call_pct,
            "response_parsing_pct": summary.response_parsing_pct,
        },
        "success_rate": summary.success_rate,
        "categories": summary.categories,
        "individual_results": [
            {
                "pmid": r.pmid,
                "title": r.title,
                "prompt_preparation_ms": r.prompt_preparation_ms,
                "api_call_ms": r.api_call_ms,
                "response_parsing_ms": r.response_parsing_ms,
                "total_ms": r.total_ms,
                "primary_category": r.primary_category,
                "confidence": r.confidence,
                "success": r.success,
                "error": r.error,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
            }
            for r in results
        ]
    }
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("=" * 70)
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark the paper classifier performance")
    parser.add_argument("-n", "--num-papers", type=int, default=5, help="Number of papers to classify")
    parser.add_argument("-d", "--disease", type=str, default="Alzheimer's Disease", help="Disease to search for")
    
    args = parser.parse_args()
    
    run_benchmark(num_papers=args.num_papers, disease=args.disease)
