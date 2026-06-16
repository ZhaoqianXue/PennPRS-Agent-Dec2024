from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from experiments.contribution3.cross_optimized.data_contract import clean_text
from experiments.contribution3.cross_optimized.paths import TARGET_SELECTION_CSV, matrix_path_for_target_source
from experiments.contribution3.cross_optimized.retrieve.source_retriever import col_to_pgs_id


HIT_AT_PCTS = (0.005, 0.01, 0.025, 0.05, 0.10, 0.25)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(predictions: Path, manifest: Path) -> None:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    expected = clean_text(data.get("predictions_sha256"))
    actual = sha256_file(predictions)
    if expected != actual:
        raise ValueError(f"Frozen prediction hash mismatch: expected {expected}, got {actual}")


def load_predictions(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("predictions", data.get("results", []))
    if not isinstance(data, list):
        raise ValueError("Prediction JSON must be a list or contain a predictions/results list.")
    return data


def target_lookup(path: Path = TARGET_SELECTION_CSV) -> dict[str, dict[str, Any]]:
    df = pd.read_csv(path)
    lookup: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        target_id = clean_text(row.get("input_icd"))
        if not target_id:
            continue
        lookup[target_id] = {
            "target_id": target_id,
            "input_type": clean_text(row.get("input_type")),
            "target_source": clean_text(row.get("target_source")),
            "target_label": clean_text(row.get("input_ontology")) or clean_text(row.get("input_description")),
            "target_description": clean_text(row.get("input_description")),
        }
    return lookup


@lru_cache(maxsize=4)
def load_matrix(target_source: str) -> pd.DataFrame:
    path = matrix_path_for_target_source(target_source)
    if not path.exists():
        raise FileNotFoundError(f"AUC matrix not found: {path}")
    return pd.read_csv(path, index_col=0)


def full_matrix_ranking(target_id: str, target_source: str) -> tuple[list[str], dict[str, float], dict[str, float]]:
    matrix = load_matrix(target_source)
    if target_id not in matrix.index:
        raise KeyError(f"Target {target_id} not found in matrix for source {target_source}.")
    auc_row = matrix.loc[target_id]
    auc_by_id = {
        col_to_pgs_id(col): float(value)
        for col, value in auc_row.items()
        if pd.notna(value)
    }
    ranked_ids = sorted(auc_by_id, key=lambda pgs_id: (-auc_by_id[pgs_id], pgs_id))
    rank_map: dict[str, float] = {}
    start_idx = 0
    while start_idx < len(ranked_ids):
        current_auc = auc_by_id[ranked_ids[start_idx]]
        end_idx = start_idx
        while end_idx + 1 < len(ranked_ids) and auc_by_id[ranked_ids[end_idx + 1]] == current_auc:
            end_idx += 1
        avg_rank = ((start_idx + 1) + (end_idx + 1)) / 2
        for idx in range(start_idx, end_idx + 1):
            rank_map[ranked_ids[idx]] = avg_rank
        start_idx = end_idx + 1
    return ranked_ids, rank_map, auc_by_id


def global_percentile_rank(rank: float | None, candidate_count: int) -> float | None:
    if rank is None or candidate_count <= 1:
        return None
    return 1 - ((rank - 1) / (candidate_count - 1))


def hit_at(rank: float | None, candidate_count: int, pct: float) -> bool:
    if rank is None or candidate_count <= 0:
        return False
    return rank <= max(1, math.ceil(candidate_count * pct))


def _prediction_pgs_id(row: dict[str, Any]) -> str:
    return (
        clean_text(row.get("primary_pgs_id"))
        or clean_text(row.get("recommended_model_id"))
        or clean_text(row.get("best_model_id"))
    )


def evaluate_predictions(predictions: list[dict[str, Any]], targets: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    detail: list[dict[str, Any]] = []
    for row in predictions:
        target_id = clean_text(row.get("target_id"))
        pgs_id = _prediction_pgs_id(row)
        meta = targets.get(target_id)
        status = "evaluated"
        selected_rank = None
        selected_auc = None
        selected_gpr = None
        top_pgs_id = None
        top_auc = None
        candidate_count = None
        try:
            if meta is None:
                raise KeyError("target_not_found")
            ranked_ids, rank_map, auc_by_id = full_matrix_ranking(target_id, meta["target_source"])
            candidate_count = len(ranked_ids)
            top_pgs_id = ranked_ids[0] if ranked_ids else None
            top_auc = auc_by_id.get(top_pgs_id) if top_pgs_id else None
            if not pgs_id:
                status = "missing_prediction"
            elif pgs_id not in rank_map:
                status = "pgs_not_in_matrix"
            else:
                selected_rank = rank_map[pgs_id]
                selected_auc = auc_by_id[pgs_id]
                selected_gpr = global_percentile_rank(selected_rank, candidate_count)
        except Exception as exc:
            status = f"matrix_error:{exc.__class__.__name__}"
        detail.append(
            {
                "target_id": target_id,
                "input_type": meta.get("input_type") if meta else None,
                "target_source": meta.get("target_source") if meta else None,
                "target_label": meta.get("target_label") if meta else None,
                "primary_pgs_id": pgs_id,
                "source_bundle_id": clean_text(row.get("source_bundle_id")),
                "status": status,
                "candidate_count": candidate_count,
                "selected_model_auc": selected_auc,
                "selected_model_rank": selected_rank,
                "selected_model_gpr": selected_gpr,
                "benchmark_top_model_id": top_pgs_id,
                "benchmark_top_model_auc": top_auc,
                "absolute_auc_regret": (
                    round(top_auc - selected_auc, 6)
                    if top_auc is not None and selected_auc is not None
                    else None
                ),
                **{
                    f"hit_top_{str(pct * 100).replace('.', '_')}pct": hit_at(selected_rank, candidate_count or 0, pct)
                    for pct in HIT_AT_PCTS
                },
            }
        )

    evaluated = [row for row in detail if row["status"] == "evaluated"]
    summary = {
        "schema_version": "cross_optimized.eval_summary.v1",
        "n_predictions": len(predictions),
        "n_evaluated": len(evaluated),
        "mean_gpr": (
            round(sum(float(row["selected_model_gpr"]) for row in evaluated) / len(evaluated), 6)
            if evaluated
            else None
        ),
        "mean_absolute_auc_regret": (
            round(sum(float(row["absolute_auc_regret"]) for row in evaluated) / len(evaluated), 6)
            if evaluated
            else None
        ),
        "hit_at": {
            f"top_{str(pct * 100).replace('.', '_')}pct": (
                round(
                    sum(1 for row in evaluated if row[f"hit_top_{str(pct * 100).replace('.', '_')}pct"])
                    / len(evaluated),
                    6,
                )
                if evaluated
                else None
            )
            for pct in HIT_AT_PCTS
        },
        "status_counts": {
            status: sum(1 for row in detail if row["status"] == status)
            for status in sorted({row["status"] for row in detail})
        },
    }
    return detail, summary


def write_detail(detail: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    if not detail:
        outpath.write_text("", encoding="utf-8")
        return
    with outpath.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(detail[0].keys()))
        writer.writeheader()
        writer.writerows(detail)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen cross-optimized predictions.")
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    parser.add_argument("--detail-out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    args = parser.parse_args()

    verify_manifest(args.predictions, args.manifest)
    predictions = load_predictions(args.predictions)
    detail, summary = evaluate_predictions(predictions, target_lookup(args.targets))
    write_detail(detail, args.detail_out)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
