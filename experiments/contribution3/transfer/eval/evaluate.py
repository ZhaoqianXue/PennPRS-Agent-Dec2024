"""
Evaluate Cross-Disease Transfer results against C1 ground truth.

Compares:
  - Deterministic baseline (rg^2 * h2 ranking)
  - LLM conditions (rg-only, graph-no-dk, graph-with-dk)

Against ground truth from cross_list_report_merged.md / cross_list_summary_merged.csv.

Metrics:
  - Top-1 Hit Rate: does rank-1 match ground truth top output disease?
  - Top-K Hit Rate: does any of top-K match?
  - MRR: Mean Reciprocal Rank of ground truth top output disease
  - Transfer AUC: AUC of the recommended output disease's PGS model

Usage:
  python -m experiments.contribution3.transfer.eval.evaluate
  python -m experiments.contribution3.transfer.eval.evaluate --conditions rg-only,graph-with-dk
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

TRANSFER_DIR = Path(__file__).resolve().parents[1]
LOCAL_GRAPHS_DIR = TRANSFER_DIR / "runs" / "local_graphs"
LLM_RESULTS_DIR = TRANSFER_DIR / "runs" / "llm_results"
EVAL_DIR = TRANSFER_DIR / "runs" / "evaluation"

CROSS_LIST_CSV = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "runs"
    / "cross_list_summary_merged.csv"
)

CONDITIONS = ["rg-only", "graph-no-dk", "graph-with-dk"]


# ---------------------------------------------------------------------------
# Load ground truth
# ---------------------------------------------------------------------------
def load_ground_truth() -> pd.DataFrame:
    """Load cross-list ground truth: top output disease per input disease."""
    df = pd.read_csv(CROSS_LIST_CSV)
    # Only cross-list inputs (52 diseases)
    inputs = df[
        (df["n_cross_models_beating_self"] > 0) | (df["has_self_auc"] == False)  # noqa
    ].copy()
    return inputs


def normalize_disease_name(name: str) -> str:
    """Normalize disease name for comparison."""
    if not name:
        return ""
    return name.lower().strip()


def _stem(word: str) -> str:
    """Rough prefix extraction for disease name matching (first 5+ chars)."""
    # Return the first max(5, len-3) chars as a crude stem
    if len(word) <= 5:
        return word
    return word[: max(5, len(word) - 3)]


def disease_names_match(pred: str, truth: str) -> bool:
    """Check if predicted disease name matches ground truth (flexible matching).

    Ground truth top_output_disease is semicolon-separated list of ontology names.
    We check if any keyword overlap suggests a match.
    """
    pred_norm = normalize_disease_name(pred)
    truth_norm = normalize_disease_name(truth)

    if not pred_norm or not truth_norm:
        return False

    # Exact match
    if pred_norm == truth_norm:
        return True

    # Check if pred is contained in truth (truth may be "arthritis; connective tissue disease; ...")
    truth_parts = [t.strip() for t in truth_norm.split(";")]
    for part in truth_parts:
        if pred_norm == part:
            return True
        # Substring match for core disease name
        if pred_norm in part or part in pred_norm:
            return True

    stopwords = {"disease", "disorder", "the", "of", "and", "with", "based", "on"}

    # Keyword overlap (at least 2 significant words match)
    pred_words = set(pred_norm.split()) - stopwords
    truth_words = set(truth_norm.split()) - stopwords
    overlap = pred_words & truth_words
    if len(overlap) >= 2:
        return True

    # Stemmed keyword overlap (catches depression/depressive, etc.)
    pred_stems = {_stem(w) for w in pred_words}
    truth_stems = {_stem(w) for w in truth_words}
    stem_overlap = pred_stems & truth_stems
    if len(stem_overlap) >= 1 and len(pred_words) <= 2:
        # Single-concept prediction matching a truth part
        return True
    if len(stem_overlap) >= 2:
        return True

    return False


# ---------------------------------------------------------------------------
# Deterministic baseline
# ---------------------------------------------------------------------------
def get_deterministic_ranking(icd: str) -> List[Dict[str, Any]]:
    """Get deterministic ranking (rg^2 * h2) from local graph JSON."""
    json_path = LOCAL_GRAPHS_DIR / f"local_graph_{icd}.json"
    if not json_path.exists():
        return []

    with open(json_path) as f:
        graph = json.load(f)

    neighbors = graph.get("neighbors", [])
    if not neighbors:
        return []

    # Sort by transfer_score descending
    ranked = sorted(neighbors, key=lambda n: n.get("transfer_score", 0), reverse=True)
    return [
        {
            "rank": i + 1,
            "trait": n["trait_id"],
            "transfer_score": n.get("transfer_score", 0),
            "rg": n.get("rg_meta", 0),
            "h2": n.get("h2_meta", 0),
        }
        for i, n in enumerate(ranked)
    ]


# ---------------------------------------------------------------------------
# LLM results
# ---------------------------------------------------------------------------
def load_llm_results(condition: str) -> Dict[str, Any]:
    """Load parsed LLM results for a condition."""
    parsed_path = LLM_RESULTS_DIR / condition / "parsed_results.json"
    if not parsed_path.exists():
        return {}

    with open(parsed_path) as f:
        results = json.load(f)

    # Re-key by ICD
    by_icd = {}
    for key, val in results.items():
        icd = val.get("icd") or key.split("__", 1)[-1]
        by_icd[icd] = val
    return by_icd


def get_llm_ranking(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract ranked candidates from an LLM result."""
    if not result or result.get("error"):
        return []

    decision = result.get("decision", {})
    candidates = decision.get("ranked_candidates", [])
    return candidates


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(
    ranking: List[Dict[str, Any]],
    ground_truth_disease: str,
    k_values: List[int] = [1, 3, 5],
) -> Dict[str, Any]:
    """Compute evaluation metrics for a single disease."""
    if not ranking or not ground_truth_disease:
        return {
            f"hit@{k}": 0 for k in k_values
        } | {"mrr": 0.0, "first_hit_rank": None}

    # Find rank of ground truth
    first_hit_rank = None
    for item in ranking:
        trait = item.get("trait", "")
        rank = item.get("rank", 0)
        if disease_names_match(trait, ground_truth_disease):
            first_hit_rank = rank
            break

    metrics = {}
    for k in k_values:
        if first_hit_rank is not None and first_hit_rank <= k:
            metrics[f"hit@{k}"] = 1
        else:
            metrics[f"hit@{k}"] = 0

    metrics["mrr"] = 1.0 / first_hit_rank if first_hit_rank else 0.0
    metrics["first_hit_rank"] = first_hit_rank

    return metrics


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------
def evaluate(conditions: List[str]) -> pd.DataFrame:
    """Run evaluation across all conditions + deterministic baseline."""
    gt = load_ground_truth()

    # Only evaluate diseases that have neighbors (non-empty graph)
    diseases_with_graph = []
    for _, row in gt.iterrows():
        icd = row["input_icd"]
        json_path = LOCAL_GRAPHS_DIR / f"local_graph_{icd}.json"
        if json_path.exists():
            with open(json_path) as f:
                graph = json.load(f)
            if graph.get("neighbors"):
                diseases_with_graph.append(row)

    if not diseases_with_graph:
        print("No diseases with non-empty graphs found.")
        return pd.DataFrame()

    print(f"Evaluating {len(diseases_with_graph)} diseases with non-empty graphs")

    # Load LLM results for each condition
    llm_results = {}
    for cond in conditions:
        llm_results[cond] = load_llm_results(cond)
        n = len(llm_results[cond])
        print(f"  [{cond}] {n} LLM results loaded")

    # Compute metrics per disease per method
    all_rows = []
    for row_data in diseases_with_graph:
        icd = row_data["input_icd"]
        ontology = row_data["input_ontology"]
        gt_disease = row_data.get("top_output_disease", "")
        if pd.isna(gt_disease):
            gt_disease = ""

        result_row = {
            "icd": icd,
            "ontology": ontology,
            "ground_truth": gt_disease,
        }

        # Deterministic baseline
        det_ranking = get_deterministic_ranking(icd)
        det_metrics = compute_metrics(det_ranking, gt_disease)
        for k, v in det_metrics.items():
            result_row[f"deterministic_{k}"] = v
        if det_ranking:
            result_row["deterministic_top1"] = det_ranking[0]["trait"]

        # LLM conditions
        for cond in conditions:
            cond_key = cond.replace("-", "_")
            llm_data = llm_results[cond].get(icd, {})
            llm_ranking = get_llm_ranking(llm_data)
            llm_metrics = compute_metrics(llm_ranking, gt_disease)
            for k, v in llm_metrics.items():
                result_row[f"{cond_key}_{k}"] = v
            if llm_ranking:
                result_row[f"{cond_key}_top1"] = llm_ranking[0].get("trait", "")

        all_rows.append(result_row)

    df = pd.DataFrame(all_rows)
    return df


def print_summary(df: pd.DataFrame, conditions: List[str]) -> str:
    """Print summary metrics across all methods."""
    lines = []
    lines.append("=" * 80)
    lines.append("Cross-Disease Transfer Evaluation Summary")
    lines.append(f"Diseases evaluated: {len(df)}")
    lines.append("=" * 80)
    lines.append("")

    methods = ["deterministic"] + [c.replace("-", "_") for c in conditions]

    header = f"{'Method':25s} {'Hit@1':>8s} {'Hit@3':>8s} {'Hit@5':>8s} {'MRR':>8s}"
    lines.append(header)
    lines.append("-" * len(header))

    for method in methods:
        hit1_col = f"{method}_hit@1"
        hit3_col = f"{method}_hit@3"
        hit5_col = f"{method}_hit@5"
        mrr_col = f"{method}_mrr"

        if hit1_col not in df.columns:
            continue

        hit1 = df[hit1_col].mean()
        hit3 = df[hit3_col].mean()
        hit5 = df[hit5_col].mean()
        mrr = df[mrr_col].mean()

        lines.append(
            f"{method:25s} {hit1:8.3f} {hit3:8.3f} {hit5:8.3f} {mrr:8.3f}"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Evaluate C3 transfer results")
    parser.add_argument(
        "--conditions",
        type=str,
        default=",".join(CONDITIONS),
        help="Comma-separated conditions to evaluate",
    )
    args = parser.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",")]

    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    df = evaluate(conditions)

    if df.empty:
        print("No results to evaluate.")
        return

    # Save detailed results
    detail_path = EVAL_DIR / "evaluation_detail.csv"
    df.to_csv(detail_path, index=False)
    print(f"Detailed results saved to {detail_path}")

    # Print and save summary
    summary = print_summary(df, conditions)
    print(summary)

    summary_path = EVAL_DIR / "evaluation_summary.txt"
    summary_path.write_text(summary)
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
