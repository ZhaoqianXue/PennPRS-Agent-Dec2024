#!/usr/bin/env python3
"""
Test Heritability Classifier Accuracy

Runs the Paper Classifier against the Heritability Ground Truth dataset
and calculates performance metrics (Recall, Precision, F1, Accuracy).

Output: Console report + data/test_results/heritability_classifier_test_*.json

Usage:
    python scripts/test_heritability_classifier.py
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.literature.paper_classifier import PaperClassifier
from modules.literature.entities import PaperMetadata

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_ground_truth() -> Dict[str, Any]:
    """Load the heritability ground truth dataset."""
    gt_path = Path(__file__).parent.parent / "data" / "validation" / "heritability_gold_standard.json"
    
    if not gt_path.exists():
        raise FileNotFoundError(
            f"Ground truth file not found: {gt_path}\n"
            "Please run build_heritability_ground_truth.py first."
        )
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def prepare_papers(ground_truth: Dict[str, Any]) -> Tuple[List[PaperMetadata], Dict[str, bool]]:
    """
    Prepare papers and expected labels from ground truth.
    
    Returns:
        Tuple of (papers, expected_labels)
        where expected_labels maps PMID to expected is_heritability value
    """
    papers = []
    expected_labels = {}
    
    # Process positive samples
    for sample in ground_truth.get("positive_samples", []):
        paper = PaperMetadata(
            pmid=sample["pmid"],
            title=sample["title"],
            abstract=sample["abstract"],
            publication_date=sample.get("publication_date")
        )
        papers.append(paper)
        expected_labels[sample["pmid"]] = True
    
    # Process negative samples
    for sample in ground_truth.get("negative_samples", []):
        paper = PaperMetadata(
            pmid=sample["pmid"],
            title=sample["title"],
            abstract=sample["abstract"],
            publication_date=sample.get("publication_date")
        )
        papers.append(paper)
        expected_labels[sample["pmid"]] = False
    
    return papers, expected_labels


def calculate_metrics(predictions: Dict[str, bool], expected: Dict[str, bool]) -> Dict[str, float]:
    """
    Calculate classification metrics.
    
    Returns:
        Dict with TP, TN, FP, FN, Recall, Precision, F1, Accuracy, Specificity
    """
    tp = tn = fp = fn = 0
    
    for pmid, expected_value in expected.items():
        predicted_value = predictions.get(pmid, False)
        
        if expected_value and predicted_value:
            tp += 1
        elif not expected_value and not predicted_value:
            tn += 1
        elif not expected_value and predicted_value:
            fp += 1
        elif expected_value and not predicted_value:
            fn += 1
    
    # Calculate metrics (handle division by zero)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "specificity": round(specificity, 4),
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4)
    }


async def run_classifier_test():
    """Main function to run the classifier test."""
    logger.info("=" * 70)
    logger.info("Heritability Classifier Accuracy Test")
    logger.info("=" * 70)
    
    # Load ground truth
    logger.info("Loading ground truth dataset...")
    ground_truth = load_ground_truth()
    
    n_positive = len(ground_truth.get("positive_samples", []))
    n_negative = len(ground_truth.get("negative_samples", []))
    logger.info(f"Ground truth: {n_positive} positive, {n_negative} negative samples")
    
    # Prepare papers and expected labels
    papers, expected_labels = prepare_papers(ground_truth)
    logger.info(f"Prepared {len(papers)} papers for classification")
    
    # Initialize classifier
    classifier = PaperClassifier()
    logger.info(f"Using model: {classifier.model_name}")
    
    # Run classification with progress callback
    def progress_callback(completed: int, total: int):
        if completed % 20 == 0 or completed == total:
            logger.info(f"Progress: {completed}/{total} ({100*completed/total:.1f}%)")
    
    logger.info("Starting classification...")
    start_time = datetime.now()
    
    results = classifier.classify_batch(papers, progress_callback=progress_callback)
    
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Classification completed in {elapsed:.1f} seconds")
    
    # Extract predictions
    predictions = {}
    detailed_results = []
    
    for result in results:
        pmid = result.pmid
        # Get has_heritability from the classification result (it's a property method)
        is_heritability = result.has_heritability
        
        # Get heritability confidence from categories
        herit_confidence = 0.0
        from modules.literature.entities import PaperCategory
        for cat in result.categories:
            if cat.category == PaperCategory.HERITABILITY:
                herit_confidence = cat.confidence
                break
        
        predictions[pmid] = is_heritability
        
        expected = expected_labels.get(pmid, None)
        is_correct = (is_heritability == expected) if expected is not None else None
        
        detailed_results.append({
            "pmid": pmid,
            "expected_is_heritability": expected,
            "predicted_is_heritability": is_heritability,
            "heritability_confidence": round(herit_confidence, 3) if herit_confidence else 0.0,
            "is_correct": is_correct,
            "reasoning": result.llm_reasoning or "",
            "primary_category": result.primary_category.value if result.primary_category else "unknown"
        })
    
    # Calculate metrics
    metrics = calculate_metrics(predictions, expected_labels)
    
    # Identify failures for analysis
    false_negatives = [r for r in detailed_results if r["expected_is_heritability"] == True and r["predicted_is_heritability"] == False]
    false_positives = [r for r in detailed_results if r["expected_is_heritability"] == False and r["predicted_is_heritability"] == True]
    
    # Print results
    logger.info("\n" + "=" * 70)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total papers tested: {len(papers)}")
    logger.info(f"  - Positive samples (expected h²=True): {n_positive}")
    logger.info(f"  - Negative samples (expected h²=False): {n_negative}")
    logger.info("")
    logger.info("Confusion Matrix:")
    logger.info(f"  True Positives:  {metrics['true_positives']}")
    logger.info(f"  True Negatives:  {metrics['true_negatives']}")
    logger.info(f"  False Positives: {metrics['false_positives']}")
    logger.info(f"  False Negatives: {metrics['false_negatives']}")
    logger.info("")
    logger.info("Performance Metrics:")
    logger.info(f"  Recall (Sensitivity):    {metrics['recall']:.2%}")
    logger.info(f"  Precision:               {metrics['precision']:.2%}")
    logger.info(f"  Specificity:             {metrics['specificity']:.2%}")
    logger.info(f"  Accuracy:                {metrics['accuracy']:.2%}")
    logger.info(f"  F1 Score:                {metrics['f1_score']:.4f}")
    
    if false_negatives:
        logger.info("\n" + "-" * 70)
        logger.info(f"FALSE NEGATIVES ({len(false_negatives)} papers missed h²):")
        for fn in false_negatives[:5]:  # Show first 5
            logger.info(f"  PMID:{fn['pmid']} - Conf:{fn['heritability_confidence']}")
    
    if false_positives:
        logger.info("\n" + "-" * 70)
        logger.info(f"FALSE POSITIVES ({len(false_positives)} papers incorrectly classified as h²):")
        for fp in false_positives[:5]:  # Show first 5
            logger.info(f"  PMID:{fp['pmid']} - Conf:{fp['heritability_confidence']}")
    
    # Save detailed results
    output_dir = Path(__file__).parent.parent / "data" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"heritability_classifier_test_{timestamp}.json"
    
    test_report = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "model": classifier.model_name,
            "elapsed_seconds": round(elapsed, 2),
            "ground_truth_version": ground_truth.get("metadata", {}).get("version", "unknown")
        },
        "summary": {
            "total_papers": len(papers),
            "positive_samples": n_positive,
            "negative_samples": n_negative
        },
        "metrics": metrics,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "detailed_results": detailed_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\nDetailed results saved to: {output_file}")
    logger.info("=" * 70)
    
    return test_report


if __name__ == "__main__":
    asyncio.run(run_classifier_test())
