from __future__ import annotations

import argparse
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (
    BENCHMARK_FAMILIES,
    DEFAULT_BENCHMARK_FAMILY,
    condition_recommendations_json,
    condition_results_json,
    evaluation_dir,
    load_benchmark_target_selection,
)


ROOTCODE_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "aou_icd_260217"
    / "prs_adjauc_matrix_260217_rootcode.csv"
)
NONTARGET_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "aou_nontarget_pgs"
    / "prs_adjauc_matrix_notarget_pgs_qc.csv"
)
HIT_AT_PCTS = (0.05, 0.10, 0.15, 0.20, 0.25)


def _load_json(path: Path) -> Any:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _clean_text(raw: Any) -> str:
    if raw is None:
        return ""
    text = str(raw).strip()
    return "" if not text or text.lower() == "nan" else text


def _normalize_target_source(raw: Any) -> str:
    source = _clean_text(raw)
    return "nontarget_pgs" if source == "nontarget_pgs" else "rootcode_main_analysis"


def _col_to_pgs_id(col: str) -> str:
    text = str(col).strip()
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


@lru_cache(maxsize=2)
def _load_auc_matrix(target_source: str) -> pd.DataFrame:
    path = NONTARGET_AUC_MATRIX if target_source == "nontarget_pgs" else ROOTCODE_AUC_MATRIX
    if not path.exists():
        raise FileNotFoundError(f"AUC matrix not found: {path}")
    return pd.read_csv(path, index_col=0)


def _build_full_matrix_ranking(
    target_code: str,
    target_source: str,
) -> tuple[list[str], dict[str, float], dict[str, float]]:
    matrix = _load_auc_matrix(target_source)
    if target_code not in matrix.index:
        raise KeyError(f"Target {target_code} not found in {target_source} AUC matrix.")
    auc_row = matrix.loc[target_code]
    auc_by_id = {
        _col_to_pgs_id(col): float(value)
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
        start_rank = start_idx + 1
        end_rank = end_idx + 1
        average_rank = (start_rank + end_rank) / 2
        for idx in range(start_idx, end_idx + 1):
            rank_map[ranked_ids[idx]] = average_rank
        start_idx = end_idx + 1

    return ranked_ids, rank_map, auc_by_id


def _global_percentile_rank(rank: float | None, candidate_count: int) -> float | None:
    if rank is None or candidate_count <= 1 or rank < 1 or rank > candidate_count:
        return None
    return 1 - ((rank - 1) / (candidate_count - 1))


def _rank_fraction(rank: float | None, candidate_count: int) -> float | None:
    if rank is None or candidate_count <= 0 or rank < 1 or rank > candidate_count:
        return None
    return rank / candidate_count


def _hit_at_percent_label(percent: float) -> str:
    return f"top_{int(percent * 100)}pct"


def _is_top_percent_hit(rank: float | None, candidate_count: int | None, percent: float) -> bool:
    if rank is None or candidate_count is None or candidate_count <= 0:
        return False
    threshold = max(1, math.ceil(candidate_count * percent))
    return rank <= threshold


def _safe_float(raw: Any) -> float | None:
    try:
        if raw is None or pd.isna(raw):
            return None
        return float(raw)
    except Exception:
        return None


def _selected_target_lookup(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> dict[str, dict[str, Any]]:
    df = load_benchmark_target_selection(benchmark_family=benchmark_family, selected_only=True).copy()
    lookup: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        target_id = str(row["input_icd"]).strip()
        lookup[target_id] = {
            "target_id": target_id,
            "input_type": _clean_text(row.get("input_type")),
            "target_source": _normalize_target_source(row.get("target_source")),
            "target_ontology": _clean_text(row.get("input_ontology")),
            "target_description": _clean_text(row.get("input_description")),
            "self_best_auc": row.get("self_best_auc"),
            "selection_reason": _clean_text(row.get("selection_reason")),
        }
    return lookup


def _build_detail_rows(
    condition: str,
    benchmark_family: str,
    results: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_lookup = _selected_target_lookup(benchmark_family=benchmark_family)
    results_by_target = {
        str((row.get("target") or {}).get("target_id") or "").strip(): row
        for row in results
        if (row.get("target") or {}).get("target_id")
    }
    recommendations_by_target = {
        str((row.get("target") or {}).get("target_id") or "").strip(): row
        for row in recommendations
        if (row.get("target") or {}).get("target_id")
    }

    detail_rows: list[dict[str, Any]] = []
    for target_id, meta in target_lookup.items():
        result_row = results_by_target.get(target_id) or {}
        recommendation_row = recommendations_by_target.get(target_id) or {}
        decision = result_row.get("decision") or recommendation_row.get("transfer_decision") or {}
        recommendation = recommendation_row.get("recommendation") or {}
        retrieval = recommendation.get("retrieval") or {}
        recommendation_decision = recommendation.get("decision") or {}
        recommended_model_id = _clean_text(recommendation_decision.get("best_model_id")) or None
        self_best_auc = _safe_float(meta["self_best_auc"])

        candidate_count = None
        selected_rank = None
        selected_auc = None
        top_model_id = None
        top_model_auc = None
        absolute_auc_regret = None
        auc_gain_over_self = None
        improves_over_self = None
        selected_gpr = None
        rank_fraction = None
        status = "missing_result"

        try:
            ranked_ids, rank_map, auc_by_id = _build_full_matrix_ranking(
                target_code=target_id,
                target_source=meta["target_source"],
            )
            candidate_count = len(ranked_ids)
            top_model_id = ranked_ids[0] if ranked_ids else None
            top_model_auc = auc_by_id.get(top_model_id) if top_model_id else None

            if not result_row:
                status = "missing_result"
            elif decision.get("outcome") != "MATCHED":
                status = "no_match"
            elif not recommendation_row:
                status = "awaiting_recommendation"
            elif not recommended_model_id:
                status = "no_model_selected"
            elif recommended_model_id not in rank_map:
                status = "model_not_in_full_matrix"
            else:
                selected_rank = rank_map[recommended_model_id]
                selected_auc = auc_by_id[recommended_model_id]
                absolute_auc_regret = (
                    round(top_model_auc - selected_auc, 6)
                    if top_model_auc is not None and selected_auc is not None
                    else None
                )
                auc_gain_over_self = (
                    round(selected_auc - self_best_auc, 6)
                    if self_best_auc is not None and selected_auc is not None
                    else None
                )
                improves_over_self = (
                    auc_gain_over_self > 0 if auc_gain_over_self is not None else None
                )
                selected_gpr = _global_percentile_rank(selected_rank, candidate_count)
                rank_fraction = _rank_fraction(selected_rank, candidate_count)
                status = "evaluated"
        except Exception as exc:  # pragma: no cover - defensive reporting
            status = f"matrix_error:{exc.__class__.__name__}"

        detail_rows.append(
            {
                "benchmark_family": benchmark_family,
                "condition": condition,
                "target_id": target_id,
                "input_type": meta["input_type"],
                "target_source": meta["target_source"],
                "target_ontology": meta["target_ontology"],
                "target_description": meta["target_description"],
                "selection_reason": meta["selection_reason"],
                "self_best_auc": meta["self_best_auc"],
                "transfer_outcome": decision.get("outcome"),
                "matched_bundle_id": decision.get("best_bundle_id"),
                "matched_cross_trait": decision.get("best_cross_trait"),
                "candidate_pgs_id_count": len(decision.get("candidate_pgs_ids") or []),
                "recommended_model_id": recommended_model_id,
                "step1_model_universe_count": retrieval.get("hydrated_model_count"),
                "step1_universe_matches_bundle": retrieval.get("universe_matches_candidate_ids"),
                "step1_missing_candidate_pgs_count": len(
                    retrieval.get("missing_candidate_pgs_ids") or []
                ),
                "candidate_count": candidate_count,
                "selected_model_auc": selected_auc,
                "selected_model_rank": selected_rank,
                "selected_model_rank_fraction": rank_fraction,
                "selected_model_gpr": selected_gpr,
                "benchmark_top_model_id": top_model_id,
                "benchmark_top_model_auc": top_model_auc,
                "absolute_auc_regret": absolute_auc_regret,
                "auc_gain_over_self": auc_gain_over_self,
                "improves_over_self": improves_over_self,
                "status": status,
                "has_result": bool(result_row),
                "has_recommendation": bool(recommendation_row),
            }
        )

    return detail_rows


def _mean_or_none(values: list[float | None], *, digits: int) -> float | None:
    clean_values = [float(value) for value in values if value is not None and not pd.isna(value)]
    if not clean_values:
        return None
    return round(sum(clean_values) / len(clean_values), digits)


def _compute_subset_official_metrics(subset: pd.DataFrame) -> dict[str, Any]:
    if subset.empty:
        return {
            "mean_gpr": None,
            "hit_at_percent": {
                _hit_at_percent_label(percent): None for percent in HIT_AT_PCTS
            },
            "mean_absolute_auc_regret": None,
        }

    total_targets = int(len(subset))
    evaluated = subset.loc[subset["status"] == "evaluated"].copy()
    all_target_gpr = subset["selected_model_gpr"].apply(
        lambda value: float(value) if pd.notna(value) else 0.0
    )

    hit_at_percent = {}
    for percent in HIT_AT_PCTS:
        hits = int(
            sum(
                _is_top_percent_hit(
                    rank=row.selected_model_rank,
                    candidate_count=row.candidate_count,
                    percent=percent,
                )
                for row in subset.itertuples()
            )
        )
        hit_at_percent[_hit_at_percent_label(percent)] = round(hits / total_targets, 4)

    return {
        "mean_gpr": round(float(all_target_gpr.mean()), 4),
        "hit_at_percent": hit_at_percent,
        "mean_absolute_auc_regret": (
            round(float(evaluated["absolute_auc_regret"].mean()), 6) if not evaluated.empty else None
        ),
    }


def _summarize_rows(detail_df: pd.DataFrame) -> dict[str, Any]:
    if detail_df.empty:
        return {}

    evaluated_mask = detail_df["status"] == "evaluated"
    evaluated = detail_df.loc[evaluated_mask].copy()

    universe_match_rate = None
    if "step1_universe_matches_bundle" in detail_df:
        universe_flags = detail_df["step1_universe_matches_bundle"].apply(
            lambda value: bool(value) if pd.notna(value) else False
        )
        universe_match_rate = round(float(universe_flags.mean()), 4)

    summary: dict[str, Any] = {
        "benchmark_family": str(detail_df["benchmark_family"].iloc[0]),
        "condition": str(detail_df["condition"].iloc[0]),
        "n_targets": int(len(detail_df)),
        "n_results": int(detail_df["has_result"].sum()),
        "n_recommendations": int(detail_df["has_recommendation"].sum()),
        "n_evaluated": int(evaluated_mask.sum()),
        "coverage": round(float(evaluated_mask.mean()), 4),
        "no_match_rate": round(float((detail_df["transfer_outcome"] == "NO_MATCH").mean()), 4),
        "mean_rank": float(evaluated["selected_model_rank"].mean()) if not evaluated.empty else None,
        "mean_rank_fraction": (
            float(evaluated["selected_model_rank_fraction"].mean()) if not evaluated.empty else None
        ),
        "conditional_mean_gpr": (
            float(evaluated["selected_model_gpr"].mean()) if not evaluated.empty else None
        ),
        "mean_selected_auc": float(evaluated["selected_model_auc"].mean()) if not evaluated.empty else None,
        "conditional_mean_absolute_auc_regret": (
            float(evaluated["absolute_auc_regret"].mean()) if not evaluated.empty else None
        ),
        "step1_universe_match_rate": universe_match_rate,
        "status_counts": detail_df["status"].value_counts(dropna=False).to_dict(),
        "by_input_type": {},
    }

    for input_type, subset in detail_df.groupby("input_type", dropna=False):
        label = _clean_text(input_type) or "UNKNOWN"
        evaluated_subset = subset[subset["status"] == "evaluated"]
        summary["by_input_type"][label] = {
            "n_targets": int(len(subset)),
            "n_evaluated": int((subset["status"] == "evaluated").sum()),
            "coverage": round(float((subset["status"] == "evaluated").mean()), 4),
            "no_match_rate": round(float((subset["transfer_outcome"] == "NO_MATCH").mean()), 4),
            "official_metrics": _compute_subset_official_metrics(subset),
            "mean_rank": (
                float(evaluated_subset["selected_model_rank"].mean())
                if not evaluated_subset.empty
                else None
            ),
            "mean_rank_fraction": (
                float(evaluated_subset["selected_model_rank_fraction"].mean())
                if not evaluated_subset.empty
                else None
            ),
            "conditional_mean_gpr": (
                float(evaluated_subset["selected_model_gpr"].mean())
                if not evaluated_subset.empty
                else None
            ),
        }

    macro_labels = [label for label in ("A", "B") if label in summary["by_input_type"]]
    if not macro_labels:
        macro_labels = list(summary["by_input_type"].keys())

    summary["official_metrics"] = {
        "mean_gpr": _mean_or_none(
            [
                summary["by_input_type"][label]["official_metrics"]["mean_gpr"]
                for label in macro_labels
            ],
            digits=4,
        ),
        "hit_at_percent": {
            _hit_at_percent_label(percent): _mean_or_none(
                [
                    summary["by_input_type"][label]["official_metrics"]["hit_at_percent"][
                        _hit_at_percent_label(percent)
                    ]
                    for label in macro_labels
                ],
                digits=4,
            )
            for percent in HIT_AT_PCTS
        },
        "mean_absolute_auc_regret": _mean_or_none(
            [
                summary["by_input_type"][label]["official_metrics"]["mean_absolute_auc_regret"]
                for label in macro_labels
            ],
            digits=6,
        ),
    }

    return summary


def evaluate_end_to_end_condition(
    condition: str,
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
    *,
    results_path: Path | None = None,
    recommendations_path: Path | None = None,
) -> dict[str, Any]:
    results_path = results_path or condition_results_json(
        condition=condition,
        benchmark_family=benchmark_family,
    )
    recommendations_path = recommendations_path or condition_recommendations_json(
        condition=condition,
        benchmark_family=benchmark_family,
    )

    results = _load_json(results_path)
    recommendations = _load_json(recommendations_path)
    detail_rows = _build_detail_rows(
        condition=condition,
        benchmark_family=benchmark_family,
        results=results,
        recommendations=recommendations,
    )
    detail_df = pd.DataFrame(detail_rows)
    summary = _summarize_rows(detail_df)

    out_dir = evaluation_dir(benchmark_family)
    out_dir.mkdir(parents=True, exist_ok=True)
    detail_path = out_dir / f"{condition}__end_to_end_eval_detail.csv"
    summary_path = out_dir / f"{condition}__end_to_end_eval_summary.json"
    detail_df.to_csv(detail_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Wrote end-to-end detail -> {detail_path}")
    print(f"Wrote end-to-end summary -> {summary_path}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate Cross-Trait Transfer + PRS Recommendation end-to-end on the full "
            "Contribution1 AUC matrix with GPR / Hit@Top% / Absolute AUC Regret metrics."
        )
    )
    parser.add_argument(
        "--condition",
        default="all-tools",
        help="Transfer condition to evaluate.",
    )
    parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default=DEFAULT_BENCHMARK_FAMILY,
        help="Benchmark target family to evaluate.",
    )
    parser.add_argument(
        "--results-path",
        default="",
        help="Optional explicit path to transfer results.json.",
    )
    parser.add_argument(
        "--recommendations-path",
        default="",
        help="Optional explicit path to contribution2_recommendations.json.",
    )
    args = parser.parse_args()

    evaluate_end_to_end_condition(
        condition=args.condition,
        benchmark_family=args.benchmark_family,
        results_path=Path(args.results_path) if args.results_path else None,
        recommendations_path=Path(args.recommendations_path) if args.recommendations_path else None,
    )


if __name__ == "__main__":
    main()
