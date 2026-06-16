from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.data_contract import clean_text


def _performance(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("performance")
    return value if isinstance(value, dict) else {}


def _stage_b_support(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("stage_b_support")
    return value if isinstance(value, dict) else {}


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _source_bundle_id(record: dict[str, Any]) -> str:
    source_bundles = record.get("source_bundles") or []
    if source_bundles and isinstance(source_bundles[0], dict):
        bundle_id = clean_text(source_bundles[0].get("bundle_id"))
        if bundle_id:
            return bundle_id
    support = record.get("stage_b_support") or {}
    source_ids = support.get("source_bundle_ids") or []
    if source_ids:
        return clean_text(source_ids[0])
    mapped_ids = [clean_text(value) for value in record.get("mapped_trait_ids") or [] if clean_text(value)]
    return "|".join(mapped_ids[:2])


def _load_stage_c_request_records(path: Path) -> dict[str, dict[str, Any]]:
    contexts: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            custom_id = clean_text(row.get("custom_id"))
            parts = custom_id.split("__")
            target_id = parts[1] if len(parts) >= 2 else ""
            payload = json.loads(row["body"]["input"][1]["content"])
            target = payload.get("target") or {}
            target_id = clean_text(target.get("target_id")) or target_id
            records: list[dict[str, Any]] = []
            seen: set[str] = set()
            for record in payload.get("frontier_pgs_records") or []:
                pgs_id = clean_text(record.get("pgs_id"))
                if not pgs_id or pgs_id in seen:
                    continue
                seen.add(pgs_id)
                records.append(record)
            if target_id and records:
                contexts[target_id] = {"target": target, "records": records}
    return contexts


def _record_count_key(record: dict[str, Any]) -> tuple[float, float, str]:
    perf = _performance(record)
    return (
        _number(perf.get("performance_record_count")),
        _number(perf.get("best_auc")),
        clean_text(record.get("pgs_id")),
    )


def _record_count(record: dict[str, Any]) -> float:
    return _number(_performance(record).get("performance_record_count"))


def _frontier_votes(record: dict[str, Any]) -> float:
    return _number(_stage_b_support(record).get("frontier_votes"))


def _frontier_vote_record_count_key(record: dict[str, Any]) -> tuple[float, float, float, str]:
    perf = _performance(record)
    return (
        _frontier_votes(record),
        _record_count(record),
        _number(perf.get("best_auc")),
        clean_text(record.get("pgs_id")),
    )


def _minmax_norm(value: float, values: list[float]) -> float:
    low = min(values)
    high = max(values)
    if high <= low:
        return 0.0
    return (value - low) / (high - low)


def _load_prediction_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("predictions", data.get("results", []))
    if not isinstance(data, list):
        raise ValueError(f"Prediction file must contain a list: {path}")
    return [row for row in data if isinstance(row, dict)]


def _load_vote_counts(paths: list[Path], *, frontier_limit: int = 12) -> dict[tuple[str, str], float]:
    counts: dict[tuple[str, str], float] = {}
    for path in paths:
        for row in _load_prediction_rows(path):
            target_id = clean_text(row.get("target_id"))
            primary_id = clean_text(row.get("primary_pgs_id"))
            ordered_ids: list[str] = []
            if primary_id:
                ordered_ids.append(primary_id)
            ordered_ids.extend(clean_text(value) for value in row.get("frontier_pgs_ids") or [])
            seen: list[str] = []
            for pgs_id in ordered_ids:
                if pgs_id and pgs_id not in seen:
                    seen.append(pgs_id)
                if len(seen) >= frontier_limit:
                    break
            for pgs_id in seen:
                counts[(target_id, pgs_id)] = counts.get((target_id, pgs_id), 0.0) + 1.0
    return counts


def _record_count_vote_guard_record(
    records: list[dict[str, Any]],
    *,
    base_top_n: int = 6,
    challenge_top_n: int = 7,
    min_record_margin: float = 1.0,
    min_frontier_vote_delta: float = -1.0,
) -> dict[str, Any]:
    base_records = records[:base_top_n]
    challenge_records = records[:challenge_top_n]
    base_record = max(base_records, key=_record_count_key)
    challenge_record = max(challenge_records, key=_record_count_key)
    frontier_vote_delta = _frontier_votes(challenge_record) - _frontier_votes(base_record)
    if (
        clean_text(challenge_record.get("pgs_id")) != clean_text(base_record.get("pgs_id"))
        and _record_count(challenge_record) - _record_count(base_record) >= min_record_margin
        and frontier_vote_delta >= min_frontier_vote_delta
    ):
        return challenge_record
    return base_record


def _frontier_ids(
    *,
    primary_record: dict[str, Any],
    preferred_records: list[dict[str, Any]],
    fallback_records: list[dict[str, Any]],
    limit: int = 12,
) -> list[str]:
    frontier: list[str] = []
    for record in [primary_record, *preferred_records, *fallback_records]:
        pgs_id = clean_text(record.get("pgs_id"))
        if pgs_id and pgs_id not in frontier:
            frontier.append(pgs_id)
        if len(frontier) >= limit:
            break
    return frontier


def build_record_count_policy_predictions(
    *,
    candidate_request_path: Path,
    outpath: Path,
    top_n: int = 6,
) -> list[dict[str, Any]]:
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    contexts = _load_stage_c_request_records(candidate_request_path)
    predictions: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        candidate_records = context["records"][:top_n]
        primary_record = max(candidate_records, key=_record_count_key)
        primary_id = clean_text(primary_record.get("pgs_id"))
        frontier = _frontier_ids(
            primary_record=primary_record,
            preferred_records=candidate_records,
            fallback_records=context["records"][top_n:12],
        )
        perf = _performance(primary_record)
        predictions.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": _source_bundle_id(primary_record),
                "frontier_pgs_ids": frontier,
                "issues": [],
                "rationale": (
                    f"Deterministic metadata policy: choose the top-{top_n} candidate "
                    "with highest PGS Catalog performance_record_count; tie-break by "
                    "best_auc, then pgs_id. "
                    f"selected_record_count={perf.get('performance_record_count')}."
                ),
            }
        )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def build_record_count_window_policy_predictions(
    *,
    candidate_request_path: Path,
    outpath: Path,
    base_top_n: int = 6,
    challenge_top_n: int = 7,
    min_record_margin: float = 1.0,
) -> list[dict[str, Any]]:
    if base_top_n <= 0:
        raise ValueError("base_top_n must be positive.")
    if challenge_top_n < base_top_n:
        raise ValueError("challenge_top_n must be greater than or equal to base_top_n.")
    contexts = _load_stage_c_request_records(candidate_request_path)
    predictions: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        records = context["records"]
        base_records = records[:base_top_n]
        challenge_records = records[:challenge_top_n]
        base_record = max(base_records, key=_record_count_key)
        challenge_record = max(challenge_records, key=_record_count_key)
        base_count = _record_count(base_record)
        challenge_count = _record_count(challenge_record)
        switched = (
            clean_text(challenge_record.get("pgs_id")) != clean_text(base_record.get("pgs_id"))
            and challenge_count - base_count >= min_record_margin
        )
        primary_record = challenge_record if switched else base_record
        primary_id = clean_text(primary_record.get("pgs_id"))
        frontier = _frontier_ids(
            primary_record=primary_record,
            preferred_records=[base_record, *base_records],
            fallback_records=[*challenge_records, *records[challenge_top_n:12]],
        )
        perf = _performance(primary_record)
        predictions.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": _source_bundle_id(primary_record),
                "frontier_pgs_ids": frontier,
                "issues": [],
                "rationale": (
                    "Deterministic metadata window policy: choose the top-"
                    f"{base_top_n} record-count winner unless the top-{challenge_top_n} "
                    "record-count winner is outside the base window and exceeds the base "
                    f"winner by at least {min_record_margin:g} performance records. "
                    "Tie-break by best_auc, then pgs_id. "
                    f"base_record_count={base_count:g}; selected_record_count="
                    f"{_number(perf.get('performance_record_count')):g}; switched={switched}."
                ),
            }
        )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def build_frontier_vote_window_policy_predictions(
    *,
    candidate_request_path: Path,
    outpath: Path,
    base_top_n: int = 6,
    challenge_top_n: int = 7,
    min_record_margin: float = 1.0,
) -> list[dict[str, Any]]:
    if base_top_n <= 0:
        raise ValueError("base_top_n must be positive.")
    if challenge_top_n < base_top_n:
        raise ValueError("challenge_top_n must be greater than or equal to base_top_n.")
    contexts = _load_stage_c_request_records(candidate_request_path)
    predictions: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        records = context["records"]
        base_records = records[:base_top_n]
        challenge_records = records[:challenge_top_n]
        base_record = max(base_records, key=_record_count_key)
        challenge_record = max(challenge_records, key=_frontier_vote_record_count_key)
        base_count = _record_count(base_record)
        challenge_count = _record_count(challenge_record)
        switched = (
            clean_text(challenge_record.get("pgs_id")) != clean_text(base_record.get("pgs_id"))
            and challenge_count - base_count >= min_record_margin
        )
        primary_record = challenge_record if switched else base_record
        primary_id = clean_text(primary_record.get("pgs_id"))
        frontier = _frontier_ids(
            primary_record=primary_record,
            preferred_records=[base_record, *base_records],
            fallback_records=[*challenge_records, *records[challenge_top_n:12]],
        )
        perf = _performance(primary_record)
        predictions.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": _source_bundle_id(primary_record),
                "frontier_pgs_ids": frontier,
                "issues": [],
                "rationale": (
                    "Deterministic frontier-vote window policy: choose the top-"
                    f"{base_top_n} record-count winner unless the top-{challenge_top_n} "
                    "frontier-vote winner exceeds the base winner by at least "
                    f"{min_record_margin:g} performance records. Candidate tie-breaks "
                    "by record_count, best_auc, then pgs_id. "
                    f"base_record_count={base_count:g}; selected_record_count="
                    f"{_number(perf.get('performance_record_count')):g}; "
                    f"selected_frontier_votes={_frontier_votes(primary_record):g}; "
                    f"switched={switched}."
                ),
            }
        )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def build_record_count_vote_guard_window_policy_predictions(
    *,
    candidate_request_path: Path,
    outpath: Path,
    base_top_n: int = 6,
    challenge_top_n: int = 7,
    min_record_margin: float = 1.0,
    min_frontier_vote_delta: float = -1.0,
) -> list[dict[str, Any]]:
    if base_top_n <= 0:
        raise ValueError("base_top_n must be positive.")
    if challenge_top_n < base_top_n:
        raise ValueError("challenge_top_n must be greater than or equal to base_top_n.")
    contexts = _load_stage_c_request_records(candidate_request_path)
    predictions: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        records = context["records"]
        base_records = records[:base_top_n]
        challenge_records = records[:challenge_top_n]
        base_record = max(base_records, key=_record_count_key)
        challenge_record = max(challenge_records, key=_record_count_key)
        base_count = _record_count(base_record)
        challenge_count = _record_count(challenge_record)
        frontier_vote_delta = _frontier_votes(challenge_record) - _frontier_votes(base_record)
        switched = (
            clean_text(challenge_record.get("pgs_id")) != clean_text(base_record.get("pgs_id"))
            and challenge_count - base_count >= min_record_margin
            and frontier_vote_delta >= min_frontier_vote_delta
        )
        primary_record = challenge_record if switched else base_record
        primary_id = clean_text(primary_record.get("pgs_id"))
        frontier = _frontier_ids(
            primary_record=primary_record,
            preferred_records=[base_record, *base_records],
            fallback_records=[*challenge_records, *records[challenge_top_n:12]],
        )
        perf = _performance(primary_record)
        predictions.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": _source_bundle_id(primary_record),
                "frontier_pgs_ids": frontier,
                "issues": [],
                "rationale": (
                    "Deterministic record-count vote-guard window policy: choose the "
                    f"top-{base_top_n} record-count winner unless the top-{challenge_top_n} "
                    "record-count winner exceeds the base winner by at least "
                    f"{min_record_margin:g} performance records and has frontier_votes "
                    f"delta >= {min_frontier_vote_delta:g}. Tie-break by best_auc, then pgs_id. "
                    f"base_record_count={base_count:g}; selected_record_count="
                    f"{_number(perf.get('performance_record_count')):g}; "
                    f"frontier_vote_delta={frontier_vote_delta:g}; switched={switched}."
                ),
            }
        )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def build_llm_count_ensemble_policy_predictions(
    *,
    candidate_request_path: Path,
    vote_prediction_paths: list[Path],
    outpath: Path,
    top_n: int = 7,
    llm_count_weight: float = 0.5,
    vote_frontier_limit: int = 12,
) -> list[dict[str, Any]]:
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    if not vote_prediction_paths:
        raise ValueError("vote_prediction_paths must not be empty.")
    contexts = _load_stage_c_request_records(candidate_request_path)
    vote_counts = _load_vote_counts(vote_prediction_paths, frontier_limit=vote_frontier_limit)
    predictions: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        candidate_records = context["records"][:top_n]
        rec_values = [math.log1p(max(0.0, _record_count(record))) for record in candidate_records]
        vote_values = [
            vote_counts.get((target_id, clean_text(record.get("pgs_id"))), 0.0)
            for record in candidate_records
        ]
        vote_guard_record = _record_count_vote_guard_record(context["records"])
        vote_guard_id = clean_text(vote_guard_record.get("pgs_id"))
        scored_records: list[tuple[float, dict[str, Any], float, float]] = []
        for idx, record in enumerate(candidate_records):
            pgs_id = clean_text(record.get("pgs_id"))
            rec_norm = _minmax_norm(rec_values[idx], rec_values)
            vote_norm = _minmax_norm(vote_values[idx], vote_values)
            score = rec_norm + (llm_count_weight * vote_norm)
            if pgs_id == vote_guard_id:
                score += 1e-7
            score += 1e-9 * rec_values[idx] + 1e-11 * (1 / (idx + 1))
            scored_records.append((score, record, rec_norm, vote_norm))
        best_score, primary_record, selected_rec_norm, selected_vote_norm = max(scored_records, key=lambda item: item[0])
        primary_id = clean_text(primary_record.get("pgs_id"))
        frontier = _frontier_ids(
            primary_record=primary_record,
            preferred_records=candidate_records,
            fallback_records=context["records"][top_n:12],
        )
        predictions.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": _source_bundle_id(primary_record),
                "frontier_pgs_ids": frontier,
                "issues": [],
                "rationale": (
                    "Deterministic LLM-count ensemble policy: within the top-"
                    f"{top_n} candidate window, score each PGS by minmax(log1p("
                    "performance_record_count)) + "
                    f"{llm_count_weight:g} * minmax(number of supplied LLM frontiers "
                    f"containing the PGS within top-{vote_frontier_limit}). "
                    "Tie-break by the record-count vote-guard policy, then record_count, "
                    f"then candidate order. selected_score={best_score:.6g}; "
                    f"selected_record_count_norm={selected_rec_norm:.6g}; "
                    f"selected_llm_count_norm={selected_vote_norm:.6g}; "
                    f"vote_file_count={len(vote_prediction_paths)}."
                ),
            }
        )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic metadata-policy predictions.")
    parser.add_argument("--candidate-request", type=Path, required=True)
    parser.add_argument(
        "--policy",
        choices=[
            "record_count",
            "record_count_window",
            "frontier_vote_window",
            "record_count_vote_guard_window",
            "llm_count_ensemble",
        ],
        default="record_count",
    )
    parser.add_argument("--top-n", type=int, default=6)
    parser.add_argument("--base-top-n", type=int, default=6)
    parser.add_argument("--challenge-top-n", type=int, default=7)
    parser.add_argument("--min-record-margin", type=float, default=1.0)
    parser.add_argument("--min-frontier-vote-delta", type=float, default=-1.0)
    parser.add_argument("--vote-predictions", type=Path, nargs="*", default=[])
    parser.add_argument("--llm-count-weight", type=float, default=0.5)
    parser.add_argument("--vote-frontier-limit", type=int, default=12)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.policy == "record_count_window":
        predictions = build_record_count_window_policy_predictions(
            candidate_request_path=args.candidate_request,
            base_top_n=args.base_top_n,
            challenge_top_n=args.challenge_top_n,
            min_record_margin=args.min_record_margin,
            outpath=args.out,
        )
    elif args.policy == "frontier_vote_window":
        predictions = build_frontier_vote_window_policy_predictions(
            candidate_request_path=args.candidate_request,
            base_top_n=args.base_top_n,
            challenge_top_n=args.challenge_top_n,
            min_record_margin=args.min_record_margin,
            outpath=args.out,
        )
    elif args.policy == "record_count_vote_guard_window":
        predictions = build_record_count_vote_guard_window_policy_predictions(
            candidate_request_path=args.candidate_request,
            base_top_n=args.base_top_n,
            challenge_top_n=args.challenge_top_n,
            min_record_margin=args.min_record_margin,
            min_frontier_vote_delta=args.min_frontier_vote_delta,
            outpath=args.out,
        )
    elif args.policy == "llm_count_ensemble":
        predictions = build_llm_count_ensemble_policy_predictions(
            candidate_request_path=args.candidate_request,
            vote_prediction_paths=args.vote_predictions,
            top_n=args.top_n,
            llm_count_weight=args.llm_count_weight,
            vote_frontier_limit=args.vote_frontier_limit,
            outpath=args.out,
        )
    else:
        predictions = build_record_count_policy_predictions(
            candidate_request_path=args.candidate_request,
            top_n=args.top_n,
            outpath=args.out,
        )
    print(f"Wrote {len(predictions)} metadata-policy predictions -> {args.out}")


if __name__ == "__main__":
    main()
