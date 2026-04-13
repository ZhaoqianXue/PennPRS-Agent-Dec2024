from __future__ import annotations

import argparse
import json
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
    load_benchmark_target_selection,
    load_trait_bundle_index,
)


ROOTCODE_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "aou_binary"
    / "prs_adjauc_matrix_binary_combined_rootcode.csv"
)
NONTARGET_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "aou_extend_trait"
    / "prs_adjauc_matrix_binary_extend_qc.csv"
)


def _load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"results.json not found: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"Expected list-shaped results.json: {path}")
    return data


def _clean_text(raw: Any) -> str:
    if raw is None:
        return ""
    text = str(raw).strip()
    return "" if not text or text.lower() == "nan" else text


def _normalize_target_source(raw: Any) -> str:
    source = _clean_text(raw)
    return "extend_trait" if source in ("nontarget_pgs", "extend_trait") else "rootcode_main_analysis"


def _col_to_pgs_id(col: str) -> str:
    text = str(col).strip()
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


def _matrix_path(target_source: str) -> Path:
    return NONTARGET_AUC_MATRIX if target_source in ("nontarget_pgs", "extend_trait") else ROOTCODE_AUC_MATRIX


@lru_cache(maxsize=2)
def _load_auc_matrix(target_source: str) -> pd.DataFrame:
    path = _matrix_path(target_source)
    if not path.exists():
        raise FileNotFoundError(f"AUC matrix not found: {path}")
    matrix = pd.read_csv(path, index_col=0)
    matrix.columns = [_col_to_pgs_id(col) for col in matrix.columns]
    return matrix


@lru_cache(maxsize=1)
def _bundle_metadata() -> tuple[dict[str, list[str]], dict[str, str]]:
    bundles = load_trait_bundle_index()
    bundle_pgs_ids = {
        bundle.bundle_id: list(dict.fromkeys(bundle.candidate_pgs_ids))
        for bundle in bundles
    }
    bundle_labels = {
        bundle.bundle_id: bundle.canonical_label
        for bundle in bundles
    }
    return bundle_pgs_ids, bundle_labels


def _competition_ranks(auc_by_bundle: dict[str, float]) -> dict[str, int]:
    ranked_bundle_ids = sorted(
        auc_by_bundle,
        key=lambda bundle_id: (-auc_by_bundle[bundle_id], bundle_id),
    )
    ranks: dict[str, int] = {}
    previous_auc: float | None = None
    current_rank = 0
    for idx, bundle_id in enumerate(ranked_bundle_ids, start=1):
        auc = auc_by_bundle[bundle_id]
        if previous_auc is None or auc != previous_auc:
            current_rank = idx
            previous_auc = auc
        ranks[bundle_id] = current_rank
    return ranks


def _bundle_ranks_for_target(target_code: str, target_source: str) -> tuple[dict[str, int], set[str]]:
    matrix = _load_auc_matrix(target_source)
    if target_code not in matrix.index:
        raise KeyError(f"Target {target_code} not found in {target_source} AUC matrix.")

    bundle_pgs_ids, _ = _bundle_metadata()
    auc_row = matrix.loc[target_code]
    auc_by_pgs = {
        str(pgs_id): float(value)
        for pgs_id, value in auc_row.items()
        if pd.notna(value)
    }

    auc_by_bundle: dict[str, float] = {}
    unavailable_bundle_ids: set[str] = set()
    for bundle_id, pgs_ids in bundle_pgs_ids.items():
        values = [auc_by_pgs[pgs_id] for pgs_id in pgs_ids if pgs_id in auc_by_pgs]
        if values:
            auc_by_bundle[bundle_id] = max(values)
        else:
            unavailable_bundle_ids.add(bundle_id)

    return _competition_ranks(auc_by_bundle), unavailable_bundle_ids


def _target_lookup(benchmark_family: str) -> dict[str, dict[str, str]]:
    df = load_benchmark_target_selection(benchmark_family=benchmark_family, selected_only=True)
    lookup: dict[str, dict[str, str]] = {}
    for _, row in df.iterrows():
        target_id = str(row.get("input_icd") or "").strip()
        if not target_id:
            continue
        lookup[target_id] = {
            "target_id": target_id,
            "target_label": _clean_text(row.get("input_ontology"))
            or _clean_text(row.get("input_description"))
            or target_id,
            "target_source": _normalize_target_source(row.get("target_source")),
        }
    return lookup


def _results_by_target(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str((row.get("target") or {}).get("target_id") or "").strip(): row
        for row in results
        if (row.get("target") or {}).get("target_id")
    }


def _decision(row: dict[str, Any] | None) -> dict[str, Any]:
    return (row or {}).get("decision") or {}


def _best_bundle_id(row: dict[str, Any] | None) -> str | None:
    decision = _decision(row)
    if decision.get("outcome") != "MATCHED":
        return None
    bundle_id = str(decision.get("best_bundle_id") or "").strip()
    return bundle_id or None


def _shortlist_ids(row: dict[str, Any] | None) -> list[str]:
    decision = _decision(row)
    evidence_state = decision.get("evidence_state") or {}
    cards = evidence_state.get("candidate_cards") or []
    ids = [str(card.get("bundle_id") or "").strip() for card in cards if card.get("bundle_id")]
    if ids:
        return list(dict.fromkeys(ids))
    return [
        str(bundle_id).strip()
        for bundle_id in (evidence_state.get("shortlist_bundle_ids") or [])
        if str(bundle_id).strip()
    ]


def _rank_or_na(bundle_id: str | None, ranks: dict[str, int]) -> int | None:
    if not bundle_id:
        return None
    return ranks.get(bundle_id)


def _format_rank(rank: int | None) -> str:
    if rank is None or pd.isna(rank):
        return "na"
    return str(int(rank))


def _oracle_from_shortlist(shortlist_ids: list[str], ranks: dict[str, int]) -> tuple[str | None, int | None, int]:
    evaluable_ids = [bundle_id for bundle_id in shortlist_ids if bundle_id in ranks]
    unavailable_count = len(shortlist_ids) - len(evaluable_ids)
    if not evaluable_ids:
        return None, None, unavailable_count
    oracle_bundle_id = min(evaluable_ids, key=lambda bundle_id: ranks[bundle_id])
    return oracle_bundle_id, ranks[oracle_bundle_id], unavailable_count


def compare_bundle_ranks(
    *,
    benchmark_family: str,
    previous_results_path: Path,
    latest_results_path: Path,
) -> pd.DataFrame:
    target_lookup = _target_lookup(benchmark_family)
    previous_by_target = _results_by_target(_load_json(previous_results_path))
    latest_by_target = _results_by_target(_load_json(latest_results_path))
    _, bundle_labels = _bundle_metadata()

    rows: list[dict[str, Any]] = []
    for target_id, meta in target_lookup.items():
        previous_row = previous_by_target.get(target_id)
        latest_row = latest_by_target.get(target_id)
        previous_bundle_id = _best_bundle_id(previous_row)
        latest_bundle_id = _best_bundle_id(latest_row)
        if previous_bundle_id is None and latest_bundle_id is None:
            continue

        ranks, _ = _bundle_ranks_for_target(target_id, meta["target_source"])
        latest_oracle_id, latest_oracle_rank, latest_unavailable = _oracle_from_shortlist(
            _shortlist_ids(latest_row),
            ranks,
        )
        previous_oracle_id, previous_oracle_rank, previous_unavailable = _oracle_from_shortlist(
            _shortlist_ids(previous_row),
            ranks,
        )
        previous_rank = _rank_or_na(previous_bundle_id, ranks)
        latest_rank = _rank_or_na(latest_bundle_id, ranks)

        rows.append(
            {
                "benchmark_family": benchmark_family,
                "target_id": target_id,
                "target_label": meta["target_label"],
                "target_source": meta["target_source"],
                "oracle_bundle_id": latest_oracle_id,
                "oracle_bundle_label": bundle_labels.get(latest_oracle_id or "", ""),
                "oracle_rank": latest_oracle_rank,
                "previous_oracle_rank": previous_oracle_rank,
                "previous_bundle_id": previous_bundle_id,
                "previous_bundle_label": bundle_labels.get(previous_bundle_id or "", ""),
                "previous_selected_rank": previous_rank,
                "latest_bundle_id": latest_bundle_id,
                "latest_bundle_label": bundle_labels.get(latest_bundle_id or "", ""),
                "latest_selected_rank": latest_rank,
                "previous_gap_to_latest_oracle": (
                    previous_rank - latest_oracle_rank
                    if previous_rank is not None and latest_oracle_rank is not None
                    else None
                ),
                "latest_gap_to_oracle": (
                    latest_rank - latest_oracle_rank
                    if latest_rank is not None and latest_oracle_rank is not None
                    else None
                ),
                "rank_delta_previous_minus_latest": (
                    previous_rank - latest_rank
                    if previous_rank is not None and latest_rank is not None
                    else None
                ),
                "latest_shortlist_unavailable_bundle_count": latest_unavailable,
                "previous_shortlist_unavailable_bundle_count": previous_unavailable,
                "previous_oracle_bundle_id": previous_oracle_id,
                "previous_oracle_bundle_label": bundle_labels.get(previous_oracle_id or "", ""),
            }
        )
    return pd.DataFrame(rows)


def _print_markdown(df: pd.DataFrame) -> None:
    columns = [
        "target_id",
        "oracle_rank",
        "previous_selected_rank",
        "latest_selected_rank",
        "rank_delta_previous_minus_latest",
    ]
    print("| target_id | oracle_rank | previous_selected_rank | latest_selected_rank | delta(prev-latest) |")
    print("|---|---:|---:|---:|---:|")
    for row in df[columns].itertuples(index=False):
        print(
            "| "
            + " | ".join(
                [
                    str(row.target_id),
                    _format_rank(row.oracle_rank),
                    _format_rank(row.previous_selected_rank),
                    _format_rank(row.latest_selected_rank),
                    _format_rank(row.rank_delta_previous_minus_latest),
                ]
            )
            + " |"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare bundle-level cross-trait transfer ranks between two results.json files."
    )
    parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default=DEFAULT_BENCHMARK_FAMILY,
    )
    parser.add_argument("--previous-results-path", required=True)
    parser.add_argument("--latest-results-path", required=True)
    parser.add_argument(
        "--out-csv",
        default="",
        help="Optional output CSV path. Defaults to bundle_rank_comparison.csv next to latest results.json.",
    )
    args = parser.parse_args()

    latest_results_path = Path(args.latest_results_path)
    out_csv = Path(args.out_csv) if args.out_csv else latest_results_path.parent / "bundle_rank_comparison.csv"
    df = compare_bundle_ranks(
        benchmark_family=args.benchmark_family,
        previous_results_path=Path(args.previous_results_path),
        latest_results_path=latest_results_path,
    )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Wrote bundle rank comparison -> {out_csv}")
    _print_markdown(df)


if __name__ == "__main__":
    main()
