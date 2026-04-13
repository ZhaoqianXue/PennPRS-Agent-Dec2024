from __future__ import annotations

import argparse
import json
import statistics
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
    CandidateBundleDossier,
    TargetTraitQuery,
    TraitBundle,
    is_self_like_bundle,
    load_benchmark_target_selection,
    load_candidate_dossiers,
    load_trait_bundle_index,
    target_dossiers_json,
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


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(path.read_text())


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


@lru_cache(maxsize=2)
def _load_auc_matrix(target_source: str) -> pd.DataFrame:
    path = NONTARGET_AUC_MATRIX if target_source in ("nontarget_pgs", "extend_trait") else ROOTCODE_AUC_MATRIX
    if not path.exists():
        raise FileNotFoundError(f"AUC matrix not found: {path}")
    matrix = pd.read_csv(path, index_col=0)
    matrix.columns = [_col_to_pgs_id(col) for col in matrix.columns]
    return matrix


@lru_cache(maxsize=1)
def _bundle_lookup() -> dict[str, TraitBundle]:
    return {bundle.bundle_id: bundle for bundle in load_trait_bundle_index()}


def _competition_ranks(auc_by_bundle: dict[str, float]) -> dict[str, int]:
    ranked_bundle_ids = sorted(
        auc_by_bundle,
        key=lambda bundle_id: (-auc_by_bundle[bundle_id], bundle_id),
    )
    ranks: dict[str, int] = {}
    current_rank = 0
    previous_auc: float | None = None
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

    auc_row = matrix.loc[target_code]
    auc_by_pgs = {
        str(pgs_id): float(value)
        for pgs_id, value in auc_row.items()
        if pd.notna(value)
    }

    auc_by_bundle: dict[str, float] = {}
    unavailable_bundle_ids: set[str] = set()
    for bundle_id, bundle in _bundle_lookup().items():
        values = [auc_by_pgs[pgs_id] for pgs_id in bundle.candidate_pgs_ids if pgs_id in auc_by_pgs]
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


def _dossiers_by_target(dossiers: list[CandidateBundleDossier]) -> dict[str, CandidateBundleDossier]:
    return {dossier.target.target_id: dossier for dossier in dossiers}


def _decision(row: dict[str, Any] | None) -> dict[str, Any]:
    return (row or {}).get("decision") or {}


def _selected_bundle_id(row: dict[str, Any] | None) -> str | None:
    decision = _decision(row)
    bundle_id = str(
        decision.get("primary_bundle_id")
        or decision.get("best_bundle_id")
        or ""
    ).strip()
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


def _best_rank(bundle_ids: list[str], ranks: dict[str, int]) -> int | None:
    evaluable = [bundle_id for bundle_id in bundle_ids if bundle_id in ranks]
    if not evaluable:
        return None
    return min(ranks[bundle_id] for bundle_id in evaluable)


def _oracle_bundle(
    target: TargetTraitQuery,
    ranks: dict[str, int],
) -> tuple[str | None, int | None]:
    candidates: list[tuple[str, int]] = []
    for bundle_id, rank in ranks.items():
        bundle = _bundle_lookup().get(bundle_id)
        if bundle is None or is_self_like_bundle(target, bundle):
            continue
        candidates.append((bundle_id, rank))
    if not candidates:
        return None, None
    bundle_id, rank = min(candidates, key=lambda item: (item[1], item[0]))
    return bundle_id, rank


def build_shortlist_recall_rows(
    *,
    benchmark_family: str,
    results_path: Path,
    candidate_dossiers_path: Path | None = None,
) -> list[dict[str, Any]]:
    results = _load_json(results_path)
    if not isinstance(results, list):
        raise ValueError(f"Expected list-shaped results JSON: {results_path}")

    dossiers_path = candidate_dossiers_path or target_dossiers_json(benchmark_family)
    dossiers = load_candidate_dossiers(dossiers_path)
    dossiers_by_target = _dossiers_by_target(dossiers)
    target_lookup = _target_lookup(benchmark_family)
    results_by_target = _results_by_target(results)
    bundle_labels = {bundle_id: bundle.canonical_label for bundle_id, bundle in _bundle_lookup().items()}

    rows: list[dict[str, Any]] = []
    for target_id, meta in target_lookup.items():
        dossier = dossiers_by_target.get(target_id)
        result_row = results_by_target.get(target_id)
        if dossier is None:
            rows.append(
                {
                    "benchmark_family": benchmark_family,
                    "target_id": target_id,
                    "target_label": meta["target_label"],
                    "target_source": meta["target_source"],
                    "status": "missing_candidate_dossier",
                }
            )
            continue

        ranks, _ = _bundle_ranks_for_target(target_id, meta["target_source"])
        oracle_id, oracle_rank = _oracle_bundle(dossier.target, ranks)
        dossier_ids = [bundle.bundle_id for bundle in dossier.candidates]
        shortlist_ids = _shortlist_ids(result_row)
        selected_id = _selected_bundle_id(result_row)
        shortlist_unavailable_count = sum(1 for bundle_id in shortlist_ids if bundle_id not in ranks)

        rows.append(
            {
                "benchmark_family": benchmark_family,
                "target_id": target_id,
                "target_label": meta["target_label"],
                "target_source": meta["target_source"],
                "transfer_eligible_global_oracle_bundle_id": oracle_id,
                "transfer_eligible_global_oracle_label": bundle_labels.get(oracle_id or "", ""),
                "transfer_eligible_global_oracle_rank": oracle_rank,
                "oracle_in_candidate_dossier": bool(oracle_id and oracle_id in dossier_ids),
                "oracle_in_shortlist": bool(oracle_id and oracle_id in shortlist_ids),
                "candidate_dossier_best_rank": _best_rank(dossier_ids, ranks),
                "shortlist_best_rank": _best_rank(shortlist_ids, ranks),
                "shortlist_size": len(shortlist_ids),
                "shortlist_unavailable_count": shortlist_unavailable_count,
                "selected_bundle_id": selected_id,
                "selected_bundle_label": bundle_labels.get(selected_id or "", ""),
                "selected_bundle_rank": ranks.get(selected_id) if selected_id else None,
                "status": "ok" if result_row else "missing_result",
            }
        )
    return rows


def summarize_shortlist_recall(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_rows = [row for row in rows if row.get("status") in {"ok", "missing_result"}]
    total = len(ok_rows)
    shortlist_best_ranks = [
        int(row["shortlist_best_rank"])
        for row in ok_rows
        if row.get("shortlist_best_rank") is not None and not pd.isna(row.get("shortlist_best_rank"))
    ]

    def count_true(key: str) -> int:
        return sum(1 for row in ok_rows if bool(row.get(key)))

    def coverage_at(limit: int) -> int:
        return sum(
            1
            for row in ok_rows
            if row.get("shortlist_best_rank") is not None and int(row["shortlist_best_rank"]) <= limit
        )

    return {
        "target_count": total,
        "candidate_dossier_oracle_recall": {
            "count": count_true("oracle_in_candidate_dossier"),
            "total": total,
            "rate": round(count_true("oracle_in_candidate_dossier") / total, 4) if total else None,
        },
        "shortlist_oracle_recall": {
            "count": count_true("oracle_in_shortlist"),
            "total": total,
            "rate": round(count_true("oracle_in_shortlist") / total, 4) if total else None,
        },
        "shortlist_best_rank_median": (
            statistics.median(shortlist_best_ranks) if shortlist_best_ranks else None
        ),
        "shortlist_best_rank_mean": (
            round(sum(shortlist_best_ranks) / len(shortlist_best_ranks), 4)
            if shortlist_best_ranks
            else None
        ),
        "shortlist_rank_le_5": {
            "count": coverage_at(5),
            "total": total,
            "rate": round(coverage_at(5) / total, 4) if total else None,
        },
        "shortlist_rank_le_10": {
            "count": coverage_at(10),
            "total": total,
            "rate": round(coverage_at(10) / total, 4) if total else None,
        },
        "shortlist_unavailable_total": int(
            sum(int(row.get("shortlist_unavailable_count") or 0) for row in ok_rows)
        ),
    }


def _print_summary(summary: dict[str, Any]) -> None:
    candidate = summary["candidate_dossier_oracle_recall"]
    shortlist = summary["shortlist_oracle_recall"]
    rank5 = summary["shortlist_rank_le_5"]
    rank10 = summary["shortlist_rank_le_10"]
    print(
        "candidate dossier oracle recall: "
        f"{candidate['count']}/{candidate['total']} ({candidate['rate']})"
    )
    print(
        "shortlist oracle recall: "
        f"{shortlist['count']}/{shortlist['total']} ({shortlist['rate']})"
    )
    print(
        "shortlist best rank: "
        f"median={summary['shortlist_best_rank_median']} "
        f"mean={summary['shortlist_best_rank_mean']}"
    )
    print(f"shortlist rank<=5 coverage: {rank5['count']}/{rank5['total']} ({rank5['rate']})")
    print(f"shortlist rank<=10 coverage: {rank10['count']}/{rank10['total']} ({rank10['rate']})")
    print(f"shortlist unavailable total: {summary['shortlist_unavailable_total']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate transfer-eligible global-oracle recall for candidate dossiers and shortlists."
    )
    parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default=DEFAULT_BENCHMARK_FAMILY,
    )
    parser.add_argument("--results-path", required=True)
    parser.add_argument(
        "--candidate-dossiers-path",
        default="",
        help="Optional candidate_dossiers.json path. Defaults to the benchmark-family run directory.",
    )
    parser.add_argument(
        "--out-csv",
        default="",
        help="Optional per-target CSV path. Defaults to shortlist_recall.csv next to results.json.",
    )
    parser.add_argument(
        "--out-json",
        default="",
        help="Optional summary JSON path. Defaults to shortlist_recall_summary.json next to results.json.",
    )
    args = parser.parse_args()

    results_path = Path(args.results_path)
    rows = build_shortlist_recall_rows(
        benchmark_family=args.benchmark_family,
        results_path=results_path,
        candidate_dossiers_path=(
            Path(args.candidate_dossiers_path)
            if args.candidate_dossiers_path
            else None
        ),
    )
    summary = summarize_shortlist_recall(rows)

    out_csv = Path(args.out_csv) if args.out_csv else results_path.parent / "shortlist_recall.csv"
    out_json = Path(args.out_json) if args.out_json else results_path.parent / "shortlist_recall_summary.json"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    print(f"Wrote per-target shortlist recall -> {out_csv}")
    print(f"Wrote shortlist recall summary -> {out_json}")
    _print_summary(summary)


if __name__ == "__main__":
    main()
