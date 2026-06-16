from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.batch.prompts import (
    STAGE_C_SCHEMA,
    dumps_compact,
    response_json_schema,
    static_system_prompt,
)
from experiments.contribution3.cross_optimized.data_contract import clean_text, compact_text
from experiments.contribution3.cross_optimized.leak_guard import assert_no_leakage


DEFAULT_MODEL = "gpt-5.4-nano"


def _unique_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        clean_value = clean_text(value)
        if not clean_value or clean_value in seen:
            continue
        seen.add(clean_value)
        out.append(clean_value)
    return out


def _load_stage_c_request_contexts(paths: list[Path]) -> tuple[list[str], dict[str, dict[str, Any]]]:
    target_order: list[str] = []
    contexts: dict[str, dict[str, Any]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                body = row.get("body") or {}
                inputs = body.get("input") or []
                if len(inputs) < 2 or not isinstance(inputs[1].get("content"), str):
                    continue
                payload = json.loads(inputs[1]["content"])
                target = payload.get("target") or {}
                target_id = clean_text(target.get("target_id"))
                if not target_id:
                    continue
                context = contexts.setdefault(
                    target_id,
                    {
                        "target": target,
                        "chunk_predictions": payload.get("chunk_predictions") or [],
                        "records_by_pgs": {},
                    },
                )
                if target_id not in target_order:
                    target_order.append(target_id)
                records_by_pgs = context["records_by_pgs"]
                for record in payload.get("frontier_pgs_records") or []:
                    if not isinstance(record, dict):
                        continue
                    pgs_id = clean_text(record.get("pgs_id"))
                    if pgs_id and pgs_id not in records_by_pgs:
                        records_by_pgs[pgs_id] = record
    return target_order, contexts


def _load_prediction_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("predictions", data) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError(f"Prediction file must contain a list or predictions list: {path}")
    return [row for row in rows if isinstance(row, dict)]


def _prediction_ids(row: dict[str, Any], *, frontier_limit: int) -> list[str]:
    ids = [clean_text(row.get("primary_pgs_id"))]
    ids.extend(clean_text(value) for value in (row.get("frontier_pgs_ids") or [])[:frontier_limit])
    return _unique_preserve(ids)


def _prediction_ids_by_target(
    prediction_paths: list[Path],
    *,
    frontier_limit_per_prediction: int,
) -> dict[str, list[str]]:
    by_target: dict[str, list[str]] = {}
    for path in prediction_paths:
        for row in _load_prediction_rows(path):
            target_id = clean_text(row.get("target_id"))
            if not target_id:
                continue
            ids = by_target.setdefault(target_id, [])
            ids.extend(_prediction_ids(row, frontier_limit=frontier_limit_per_prediction))
            by_target[target_id] = _unique_preserve(ids)
    return by_target


def _first_prediction_by_target(prediction_path: Path) -> dict[str, dict[str, Any]]:
    by_target: dict[str, dict[str, Any]] = {}
    for row in _load_prediction_rows(prediction_path):
        target_id = clean_text(row.get("target_id"))
        if target_id and target_id not in by_target:
            by_target[target_id] = row
    return by_target


def _compact_anchor_decision(row: dict[str, Any], *, max_frontier_ids: int) -> dict[str, Any]:
    return {
        "primary_pgs_id": clean_text(row.get("primary_pgs_id")),
        "source_bundle_id": clean_text(row.get("source_bundle_id")),
        "frontier_pgs_ids": _unique_preserve(
            [clean_text(value) for value in (row.get("frontier_pgs_ids") or [])[:max_frontier_ids]]
        ),
        "issues": [
            compact_text(value, 180)
            for value in (row.get("issues") or [])[:4]
            if compact_text(value, 180)
        ],
        "rationale": compact_text(row.get("rationale"), 520),
    }


def _response_body(*, model: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": model,
        "input": [
            {"role": "system", "content": static_system_prompt("stage_c")},
            {"role": "user", "content": dumps_compact(payload)},
        ],
        "reasoning": {"effort": "low"},
        "text": {
            "format": response_json_schema(
                "cross_stage_d_candidate_panel",
                STAGE_C_SCHEMA,
            )
        },
        "max_output_tokens": 1000,
    }


def build_anchor_challenger_shortlist_lines(
    *,
    record_source_request_paths: list[Path],
    anchor_prediction_path: Path,
    model: str = DEFAULT_MODEL,
    max_candidates: int = 6,
    max_frontier_ids: int = 3,
) -> list[dict[str, Any]]:
    if not record_source_request_paths:
        raise ValueError("record_source_request_paths must not be empty.")
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive.")
    if max_frontier_ids < 0:
        raise ValueError("max_frontier_ids must not be negative.")

    target_order, contexts = _load_stage_c_request_contexts(record_source_request_paths)
    anchors_by_target = _first_prediction_by_target(anchor_prediction_path)

    lines: list[dict[str, Any]] = []
    for target_id in target_order:
        context = contexts[target_id]
        anchor_row = anchors_by_target.get(target_id)
        if not anchor_row:
            continue
        records_by_pgs = context["records_by_pgs"]
        anchor_decision = _compact_anchor_decision(
            anchor_row,
            max_frontier_ids=max_frontier_ids,
        )
        anchor_ids = _unique_preserve(
            [
                anchor_decision["primary_pgs_id"],
                *anchor_decision["frontier_pgs_ids"],
            ]
        )

        candidate_records: list[dict[str, Any]] = []
        missing_ids: list[str] = []
        seen: set[str] = set()
        for pgs_id in anchor_ids:
            record = records_by_pgs.get(pgs_id)
            if record is None:
                missing_ids.append(pgs_id)
                continue
            candidate_records.append(record)
            seen.add(pgs_id)
            if len(candidate_records) >= max_candidates:
                break
        if len(candidate_records) < max_candidates:
            for pgs_id, record in records_by_pgs.items():
                if pgs_id in seen:
                    continue
                candidate_records.append(record)
                seen.add(pgs_id)
                if len(candidate_records) >= max_candidates:
                    break
        if not candidate_records:
            continue

        payload = {
            "schema_version": "cross_optimized.stage_c.anchor_challenger_shortlist.v1",
            "target": context["target"],
            "anchor_decision": anchor_decision,
            "frontier_pgs_records": candidate_records,
            "instruction": (
                "Return a compact Stage C shortlist decision. Choose primary_pgs_id "
                "only from frontier_pgs_records.pgs_id, put the selected primary "
                "first in frontier_pgs_ids, and keep only plausible alternatives. "
                "Treat anchor_decision as one visible LLM argument to audit, not "
                "authority. Candidate presence and order are context only, not a "
                "vote, score, rank, threshold, or rule. First critique whether the "
                "anchor source bridge and PGS evidence remain coherent from the "
                "provided records. A challenger can replace the anchor when its "
                "source bridge and visible PGS evidence give a stronger transfer "
                "case under the skill. Preserve uncertainty in issues. Do not "
                "introduce new PGS IDs."
            ),
            "candidate_supply_note": {
                "source": "anchor_challenger_high_recall_shortlist",
                "anchor_prediction_path": str(anchor_prediction_path),
                "max_candidates": max_candidates,
                "max_frontier_ids": max_frontier_ids,
                "anchor_primary_present": anchor_decision["primary_pgs_id"] in records_by_pgs,
                "missing_anchor_ids": missing_ids[:12],
            },
        }
        row = {
            "custom_id": f"stageCAnchorChallengerShortlist__{target_id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": _response_body(model=model, payload=payload),
        }
        assert_no_leakage(row, root=row["custom_id"])
        lines.append(row)
    return lines


def build_llm_union_panel_lines(
    *,
    record_source_request_paths: list[Path],
    prediction_paths: list[Path],
    model: str = DEFAULT_MODEL,
    frontier_limit_per_prediction: int = 3,
    max_candidates: int = 8,
) -> list[dict[str, Any]]:
    if not record_source_request_paths:
        raise ValueError("record_source_request_paths must not be empty.")
    if not prediction_paths:
        raise ValueError("prediction_paths must not be empty.")
    if frontier_limit_per_prediction <= 0:
        raise ValueError("frontier_limit_per_prediction must be positive.")
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive.")

    target_order, contexts = _load_stage_c_request_contexts(record_source_request_paths)
    candidate_ids_by_target = _prediction_ids_by_target(
        prediction_paths,
        frontier_limit_per_prediction=frontier_limit_per_prediction,
    )

    lines: list[dict[str, Any]] = []
    for target_id in target_order:
        context = contexts[target_id]
        records_by_pgs = context["records_by_pgs"]
        candidate_records: list[dict[str, Any]] = []
        missing_ids: list[str] = []
        for pgs_id in candidate_ids_by_target.get(target_id, []):
            record = records_by_pgs.get(pgs_id)
            if record is None:
                missing_ids.append(pgs_id)
                continue
            candidate_records.append(record)
            if len(candidate_records) >= max_candidates:
                break
        if not candidate_records:
            continue
        payload = {
            "schema_version": "cross_optimized.stage_c.llm_union_candidate_panel.v1",
            "target": context["target"],
            "chunk_predictions": context["chunk_predictions"],
            "frontier_pgs_records": candidate_records,
            "instruction": (
                "Choose the final primary PGS only from frontier_pgs_records.pgs_id. "
                "This panel is supplied from current LLM lane primary/frontier outputs. "
                "Candidate presence is context only, not a vote, score, rank, threshold, "
                "or authority. Reconcile source fit, endpoint fit, method, ancestry, "
                "and visible PGS evidence. Do not introduce new PGS IDs."
            ),
            "candidate_supply_note": {
                "source": "current_llm_lane_union",
                "prediction_file_count": len(prediction_paths),
                "frontier_limit_per_prediction": frontier_limit_per_prediction,
                "max_candidates": max_candidates,
                "missing_candidate_ids": missing_ids[:12],
            },
        }
        row = {
            "custom_id": f"stageCllmUnionPanel__{target_id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": _response_body(model=model, payload=payload),
        }
        assert_no_leakage(row, root=row["custom_id"])
        lines.append(row)
    return lines


def build_frontier_compression_lines(
    *,
    record_source_request_paths: list[Path],
    model: str = DEFAULT_MODEL,
    max_candidates: int = 4,
    target_frontier_size: int = 2,
) -> list[dict[str, Any]]:
    if not record_source_request_paths:
        raise ValueError("record_source_request_paths must not be empty.")
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive.")
    if target_frontier_size <= 0:
        raise ValueError("target_frontier_size must be positive.")

    target_order, contexts = _load_stage_c_request_contexts(record_source_request_paths)
    lines: list[dict[str, Any]] = []
    for target_id in target_order:
        context = contexts[target_id]
        candidate_records = list(context["records_by_pgs"].values())[:max_candidates]
        if not candidate_records:
            continue
        payload = {
            "schema_version": "cross_optimized.stage_c.frontier_compression.v1",
            "target": context["target"],
            "chunk_predictions": context["chunk_predictions"],
            "frontier_pgs_records": candidate_records,
            "instruction": (
                "Compress this high-recall panel into a low-noise Stage C decision. "
                "Choose primary_pgs_id only from frontier_pgs_records.pgs_id and return "
                f"no more than {target_frontier_size} frontier_pgs_ids with the primary first. "
                "Review every candidate with the same source-then-model checklist: source "
                "bridge to the target, endpoint fit, visible PGS evidence, method context, "
                "and ancestry portability. Candidate order is context only, not evidence. "
                "Do not overcorrect toward later candidates; later position is also not "
                "evidence. Candidate presence is not a count, score, threshold, or authority. "
                "Do not introduce new PGS IDs."
            ),
            "candidate_supply_note": {
                "source": "llm_frontier_compression",
                "max_candidates": max_candidates,
                "target_frontier_size": target_frontier_size,
            },
        }
        row = {
            "custom_id": f"stageCFrontierCompression__{target_id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": _response_body(model=model, payload=payload),
        }
        assert_no_leakage(row, root=row["custom_id"])
        lines.append(row)
    return lines


def _records_for_prediction_groups(
    *,
    records_by_pgs: dict[str, dict[str, Any]],
    prediction_id_groups: list[list[str]],
    max_candidates: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    candidate_records: list[dict[str, Any]] = []
    missing_ids: list[str] = []
    seen: set[str] = set()
    for ids in prediction_id_groups:
        for pgs_id in ids:
            if not pgs_id or pgs_id in seen:
                continue
            seen.add(pgs_id)
            record = records_by_pgs.get(pgs_id)
            if record is None:
                missing_ids.append(pgs_id)
                continue
            candidate_records.append(record)
            if len(candidate_records) >= max_candidates:
                return candidate_records, missing_ids
    return candidate_records, missing_ids


def _record_source_keys(record: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for value in record.get("mapped_trait_ids") or []:
        key = clean_text(value).lower()
        if key:
            keys.add(key)

    support = record.get("stage_b_support") or {}
    for value in support.get("source_bundle_ids") or []:
        key = clean_text(value).lower()
        if key:
            keys.add(key)

    for source_bundle in record.get("source_bundles") or []:
        if not isinstance(source_bundle, dict):
            continue
        key = clean_text(source_bundle.get("bundle_id")).lower()
        if key:
            keys.add(key)
    return keys


def _keep_source_equivalent_challengers(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(records) <= 1:
        return records
    anchor_keys = _record_source_keys(records[0])
    if not anchor_keys:
        return records[:1]
    return [records[0]] + [
        record for record in records[1:] if anchor_keys & _record_source_keys(record)
    ]


def build_anchor_advisor_panel_lines(
    *,
    record_source_request_paths: list[Path],
    anchor_prediction_paths: list[Path],
    advisor_prediction_paths: list[Path],
    model: str = DEFAULT_MODEL,
    anchor_frontier_limit_per_prediction: int = 1,
    advisor_frontier_limit_per_prediction: int = 0,
    max_candidates: int = 4,
    source_equivalent_challengers_only: bool = False,
) -> list[dict[str, Any]]:
    if not record_source_request_paths:
        raise ValueError("record_source_request_paths must not be empty.")
    if not anchor_prediction_paths:
        raise ValueError("anchor_prediction_paths must not be empty.")
    if not advisor_prediction_paths:
        raise ValueError("advisor_prediction_paths must not be empty.")
    if anchor_frontier_limit_per_prediction < 0:
        raise ValueError("anchor_frontier_limit_per_prediction must not be negative.")
    if advisor_frontier_limit_per_prediction < 0:
        raise ValueError("advisor_frontier_limit_per_prediction must not be negative.")
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive.")

    target_order, contexts = _load_stage_c_request_contexts(record_source_request_paths)
    anchor_ids_by_target = _prediction_ids_by_target(
        anchor_prediction_paths,
        frontier_limit_per_prediction=anchor_frontier_limit_per_prediction,
    )
    advisor_ids_by_target = _prediction_ids_by_target(
        advisor_prediction_paths,
        frontier_limit_per_prediction=advisor_frontier_limit_per_prediction,
    )

    lines: list[dict[str, Any]] = []
    for target_id in target_order:
        context = contexts[target_id]
        candidate_records, missing_ids = _records_for_prediction_groups(
            records_by_pgs=context["records_by_pgs"],
            prediction_id_groups=[
                anchor_ids_by_target.get(target_id, []),
                advisor_ids_by_target.get(target_id, []),
            ],
            max_candidates=max_candidates,
        )
        if source_equivalent_challengers_only:
            candidate_records = _keep_source_equivalent_challengers(candidate_records)
        if not candidate_records:
            continue
        payload = {
            "schema_version": "cross_optimized.stage_c.anchor_advisor_candidate_panel.v1",
            "target": context["target"],
            "chunk_predictions": context["chunk_predictions"],
            "frontier_pgs_records": candidate_records,
            "instruction": (
                "Choose the final primary PGS only from frontier_pgs_records.pgs_id. "
                "This compact panel is supplied from prior LLM anchor outputs and "
                "non-decision advisor-surfaced candidates. Candidate presence and "
                "provenance are review context only, not a vote, score, rank, "
                "threshold, or authority. Reconcile source fit, endpoint fit, "
                "method, ancestry, and visible PGS evidence. Do not introduce new PGS IDs."
            ),
            "candidate_supply_note": {
                "source": "current_llm_anchor_and_nondecision_advisor_union",
                "anchor_prediction_file_count": len(anchor_prediction_paths),
                "advisor_prediction_file_count": len(advisor_prediction_paths),
                "anchor_frontier_limit_per_prediction": anchor_frontier_limit_per_prediction,
                "advisor_frontier_limit_per_prediction": advisor_frontier_limit_per_prediction,
                "max_candidates": max_candidates,
                "source_equivalent_challengers_only": source_equivalent_challengers_only,
                "missing_candidate_ids": missing_ids[:12],
            },
        }
        row = {
            "custom_id": f"stageCAnchorAdvisorPanel__{target_id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": _response_body(model=model, payload=payload),
        }
        assert_no_leakage(row, root=row["custom_id"])
        lines.append(row)
    return lines


def write_jsonl(lines: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build LLM-led Stage D candidate panels.")
    parser.add_argument("--record-source-request", type=Path, nargs="+", required=True)
    parser.add_argument("--prediction", type=Path, nargs="+", required=True)
    parser.add_argument("--advisor-prediction", type=Path, nargs="*", default=[])
    parser.add_argument("--anchor-challenger-shortlist", action="store_true")
    parser.add_argument("--frontier-limit-per-prediction", type=int, default=3)
    parser.add_argument("--advisor-frontier-limit-per-prediction", type=int, default=0)
    parser.add_argument("--shortlist-frontier-ids", type=int, default=3)
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--source-equivalent-challengers-only", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.anchor_challenger_shortlist:
        if len(args.prediction) != 1:
            raise ValueError("--anchor-challenger-shortlist requires exactly one --prediction file.")
        lines = build_anchor_challenger_shortlist_lines(
            record_source_request_paths=args.record_source_request,
            anchor_prediction_path=args.prediction[0],
            model=args.model,
            max_candidates=args.max_candidates,
            max_frontier_ids=args.shortlist_frontier_ids,
        )
    elif args.advisor_prediction:
        lines = build_anchor_advisor_panel_lines(
            record_source_request_paths=args.record_source_request,
            anchor_prediction_paths=args.prediction,
            advisor_prediction_paths=args.advisor_prediction,
            model=args.model,
            anchor_frontier_limit_per_prediction=args.frontier_limit_per_prediction,
            advisor_frontier_limit_per_prediction=args.advisor_frontier_limit_per_prediction,
            max_candidates=args.max_candidates,
            source_equivalent_challengers_only=args.source_equivalent_challengers_only,
        )
    else:
        lines = build_llm_union_panel_lines(
            record_source_request_paths=args.record_source_request,
            prediction_paths=args.prediction,
            model=args.model,
            frontier_limit_per_prediction=args.frontier_limit_per_prediction,
            max_candidates=args.max_candidates,
        )
    write_jsonl(lines, args.out)
    print(f"Wrote {len(lines)} LLM-union candidate panel requests -> {args.out}")


if __name__ == "__main__":
    main()
