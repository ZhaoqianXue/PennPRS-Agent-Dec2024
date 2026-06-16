from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.batch.prompts import (
    STAGE_A_SCHEMA,
    STAGE_B_SCHEMA,
    STAGE_C_SCHEMA,
    dumps_compact,
    response_json_schema,
    static_system_prompt,
)
from experiments.contribution3.cross_optimized.data_contract import CompactBundleRecord, clean_text, compact_text
from experiments.contribution3.cross_optimized.leak_guard import assert_no_leakage
from experiments.contribution3.cross_optimized.paths import DEFAULT_COMPACT_CATALOG_JSON, RUNS_DIR, TARGET_SELECTION_CSV
from experiments.contribution3.cross_optimized.retrieve.source_retriever import (
    bundles_from_catalog,
    load_compact_catalog,
    load_targets,
    retrieve_bundles,
    source_universe_pgs_ids,
)


DEFAULT_MODEL = "gpt-5.4-nano"


def _batch_line(custom_id: str, body: dict[str, Any]) -> dict[str, Any]:
    assert_no_leakage(body, root=custom_id)
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": body,
    }


def _response_body(
    *,
    model: str,
    stage: str,
    user_payload: dict[str, Any],
    schema_name: str,
    schema: dict[str, Any],
    max_output_tokens: int,
    reasoning_effort: str = "low",
) -> dict[str, Any]:
    return {
        "model": model,
        "input": [
            {"role": "system", "content": static_system_prompt(stage)},
            {"role": "user", "content": dumps_compact(user_payload)},
        ],
        "reasoning": {"effort": reasoning_effort},
        "text": {"format": response_json_schema(schema_name, schema)},
        "max_output_tokens": max_output_tokens,
    }


def build_stage_a_lines(
    *,
    catalog_path: Path = DEFAULT_COMPACT_CATALOG_JSON,
    targets_path: Path = TARGET_SELECTION_CSV,
    model: str = DEFAULT_MODEL,
    prompt_candidate_cap: int = 160,
    max_dossier_bundles: int = 600,
    target_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    catalog = load_compact_catalog(catalog_path)
    bundles = bundles_from_catalog(catalog)
    targets = load_targets(targets_path)
    if target_ids:
        targets = [target for target in targets if target.target_id in target_ids]
    lines: list[dict[str, Any]] = []
    for target in targets:
        retrieved = retrieve_bundles(target=target, bundles=bundles, max_bundles=max_dossier_bundles)
        prompt_bundles = [bundle.to_prompt_dict() for bundle in retrieved[:prompt_candidate_cap]]
        payload = {
            "schema_version": "cross_optimized.stage_a.v1",
            "target": target.to_prompt_dict(),
            "candidate_bundle_count_full": len(retrieved),
            "candidate_bundle_count_prompt": len(prompt_bundles),
            "candidate_bundles": prompt_bundles,
            "instruction": "Select source bundles only from candidate_bundles. Preserve uncertainty in frontier_bundle_ids.",
        }
        body = _response_body(
            model=model,
            stage="stage_a",
            user_payload=payload,
            schema_name="cross_stage_a_source_shortlist",
            schema=STAGE_A_SCHEMA,
            max_output_tokens=1200,
        )
        lines.append(_batch_line(f"stageA__{target.target_id}", body))
    return lines


def _load_stage_a_selection(path: Path) -> dict[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "selections" in data:
        data = data["selections"]
    if isinstance(data, dict):
        return {
            str(target_id): [clean_text(v) for v in values if clean_text(v)]
            for target_id, values in data.items()
        }
    selections: dict[str, list[str]] = {}
    for row in data:
        target_id = clean_text(row.get("target_id"))
        bundle_ids = row.get("bundle_ids") or row.get("selected_bundle_ids") or row.get("frontier_bundle_ids") or []
        if target_id:
            selections[target_id] = [clean_text(v) for v in bundle_ids if clean_text(v)]
    return selections


def _pgs_lookup(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {clean_text(row.get("pgs_id")): row for row in catalog.get("pgs_records") or [] if clean_text(row.get("pgs_id"))}


def _bundle_lookup(bundles: list[CompactBundleRecord]) -> dict[str, CompactBundleRecord]:
    return {bundle.bundle_id: bundle for bundle in bundles}


def _unique_preserve_ids(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _canonicalize_bundle_id(
    bundle_id: str,
    bundle_lookup: dict[str, CompactBundleRecord],
) -> str | None:
    if bundle_id in bundle_lookup:
        return bundle_id
    match = re.fullmatch(r"([A-Za-z]+)_(\d+)", bundle_id)
    if not match:
        return None
    prefix, numeric = match.group(1).lower(), int(match.group(2))
    candidates = [
        candidate_id
        for candidate_id in bundle_lookup
        if (candidate_match := re.fullmatch(r"([A-Za-z]+)_(\d+)", candidate_id))
        and candidate_match.group(1).lower() == prefix
        and int(candidate_match.group(2)) == numeric
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def _method_quality(method: str, details: str) -> int:
    text = f"{method} {details}".lower()
    if "prs-csx" in text or "prscsx" in text:
        return 7
    if "prs-cs" in text or "prscs" in text:
        return 6
    if "ldpred" in text or "sbayes" in text:
        return 5
    if "lassosum" in text:
        return 4
    if "prsice" in text or "pruning" in text or "threshold" in text or "p+t" in text:
        return 3
    if "gwas hit" in text:
        return 1
    return 2


def _ancestry_signal(row: dict[str, Any]) -> int:
    text = " ".join(
        clean_text(row.get(key))
        for key in ("ancestry_evaluation", "ancestry_training", "ancestry_gwas")
    ).lower()
    signal = 0
    if "multi-ancestry" in text or "including european" in text:
        signal += 3
    signal += text.count("|")
    if "european" in text:
        signal += 1
    if "african" in text:
        signal += 1
    if "asian" in text or "east asian" in text or "south asian" in text:
        signal += 1
    if "hispanic" in text or "latin" in text:
        signal += 1
    return signal


def _performance_dict(row: dict[str, Any]) -> dict[str, Any]:
    performance = row.get("performance")
    return performance if isinstance(performance, dict) else {}


def _performance_float(row: dict[str, Any], key: str) -> float:
    value = _performance_dict(row).get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _performance_int(row: dict[str, Any], key: str) -> int:
    value = _performance_dict(row).get(key)
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _compact_performance_prompt(performance: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in (
        "performance_record_count",
        "sample_set_count",
        "evaluation_sample_max",
        "evaluation_sample_total",
        "best_auc",
        "best_r2",
        "best_hr",
        "best_or",
        "best_abs_beta",
        "evaluation_ancestry",
    ):
        value = performance.get(key)
        if value in (None, "", 0, [], {}):
            continue
        out[key] = value
    return out


def _compact_pgs_prompt_row(row: dict[str, Any]) -> dict[str, Any]:
    prompt_row: dict[str, Any] = {
        "pgs_id": clean_text(row.get("pgs_id")),
        "reported_trait": compact_text(row.get("reported_trait"), 120),
        "mapped_trait_labels": [clean_text(v) for v in (row.get("mapped_trait_labels") or [])[:3] if clean_text(v)],
        "mapped_trait_ids": [clean_text(v) for v in (row.get("mapped_trait_ids") or [])[:3] if clean_text(v)],
        "method": compact_text(row.get("method"), 80),
        "method_details": compact_text(row.get("method_details"), 80),
        "variant_count": row.get("variant_count"),
        "ancestry_gwas": compact_text(row.get("ancestry_gwas"), 80),
        "ancestry_training": compact_text(row.get("ancestry_training"), 80),
        "ancestry_evaluation": compact_text(row.get("ancestry_evaluation"), 80),
        "release_date": clean_text(row.get("release_date")),
    }
    performance = _compact_performance_prompt(_performance_dict(row))
    if performance:
        prompt_row["performance"] = performance
    return {key: value for key, value in prompt_row.items() if value not in (None, "", [], {})}


def _pgs_to_bundle_ids(bundles: list[CompactBundleRecord]) -> dict[str, list[str]]:
    lookup: dict[str, list[str]] = {}
    for bundle in bundles:
        for pgs_id in bundle.candidate_pgs_ids:
            clean_id = clean_text(pgs_id)
            if clean_id:
                lookup.setdefault(clean_id, []).append(bundle.bundle_id)
    return lookup


def _pgs_to_bundle_summaries(bundles: list[CompactBundleRecord]) -> dict[str, list[dict[str, Any]]]:
    lookup: dict[str, list[dict[str, Any]]] = {}
    for bundle in bundles:
        summary = {
            "bundle_id": bundle.bundle_id,
            "canonical_label": bundle.canonical_label,
            "aliases": [clean_text(value) for value in (bundle.aliases or [])[:3] if clean_text(value)],
        }
        summary = {key: value for key, value in summary.items() if value not in (None, "", [], {})}
        for pgs_id in bundle.candidate_pgs_ids:
            clean_id = clean_text(pgs_id)
            if clean_id:
                lookup.setdefault(clean_id, []).append(summary)
    return lookup


def _stage_b_support_by_pgs(
    rows: list[dict[str, Any]],
    pgs_to_bundle_ids: dict[str, list[str]],
) -> dict[str, dict[str, Any]]:
    working: dict[str, dict[str, Any]] = {}
    for row in rows:
        primary_id = clean_text(row.get("primary_pgs_id"))
        frontier_ids = [clean_text(value) for value in row.get("frontier_pgs_ids") or [] if clean_text(value)]
        frontier_set = set(frontier_ids)
        chunk_id = clean_text(row.get("chunk_id"))
        confidence = clean_text(row.get("confidence")) or "unknown"
        source_bundle_id = clean_text(row.get("source_bundle_id"))
        for pgs_id in _unique_preserve_ids([primary_id, *frontier_ids]):
            entry = working.setdefault(
                pgs_id,
                {
                    "primary_votes": 0,
                    "frontier_votes": 0,
                    "chunk_ids": set(),
                    "confidence_counts": {},
                    "source_bundle_ids": set(),
                },
            )
            if pgs_id == primary_id:
                entry["primary_votes"] += 1
                if source_bundle_id:
                    entry["source_bundle_ids"].add(source_bundle_id)
            if pgs_id in frontier_set:
                entry["frontier_votes"] += 1
            if chunk_id:
                entry["chunk_ids"].add(chunk_id)
            entry["confidence_counts"][confidence] = entry["confidence_counts"].get(confidence, 0) + 1
            for bundle_id in pgs_to_bundle_ids.get(pgs_id, []):
                entry["source_bundle_ids"].add(bundle_id)

    support: dict[str, dict[str, Any]] = {}
    for pgs_id, entry in working.items():
        support[pgs_id] = {
            "primary_votes": entry["primary_votes"],
            "frontier_votes": entry["frontier_votes"],
            "chunk_count": len(entry["chunk_ids"]),
            "confidence_counts": {
                key: entry["confidence_counts"][key]
                for key in sorted(entry["confidence_counts"])
            },
            "source_bundle_ids": sorted(entry["source_bundle_ids"])[:8],
        }
    return support


def _stage_b_support_sort_key(pgs_id: str, support_by_pgs: dict[str, dict[str, Any]]) -> tuple[Any, ...]:
    support = support_by_pgs.get(pgs_id) or {}
    confidence_counts = support.get("confidence_counts") or {}
    confidence_score = (
        3 * int(confidence_counts.get("high") or 0)
        + 2 * int(confidence_counts.get("moderate") or 0)
        + int(confidence_counts.get("low") or 0)
    )
    return (
        -int(support.get("primary_votes") or 0),
        -int(support.get("frontier_votes") or 0),
        -confidence_score,
        -int(support.get("chunk_count") or 0),
        pgs_id,
    )


def _stage_c_frontier_records(
    rows: list[dict[str, Any]],
    pgs_lookup: dict[str, dict[str, Any]],
    pgs_to_bundle_ids: dict[str, list[str]],
    pgs_to_bundle_summaries: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    support_by_pgs = _stage_b_support_by_pgs(rows, pgs_to_bundle_ids)
    frontier_ids = _unique_preserve_ids(
        [
            clean_text(value)
            for row in rows
            for value in [row.get("primary_pgs_id"), *(row.get("frontier_pgs_ids") or [])]
            if clean_text(value)
        ]
    )
    frontier_ids = sorted(frontier_ids, key=lambda pgs_id: _stage_b_support_sort_key(pgs_id, support_by_pgs))
    frontier_records = []
    for pgs_id in frontier_ids:
        if pgs_id not in pgs_lookup:
            continue
        prompt_row = _compact_pgs_prompt_row(pgs_lookup[pgs_id])
        source_bundles = pgs_to_bundle_summaries.get(pgs_id) or []
        if source_bundles:
            prompt_row["source_bundles"] = source_bundles[:6]
        prompt_row["stage_b_support"] = support_by_pgs.get(pgs_id) or {}
        frontier_records.append(prompt_row)
    return frontier_records


def _performance_sort_key(row: dict[str, Any]) -> tuple[float, ...] | tuple[Any, ...]:
    return (
        -_performance_float(row, "best_auc"),
        -_performance_float(row, "best_r2"),
        -_performance_int(row, "performance_record_count"),
        -_performance_int(row, "evaluation_sample_max"),
        -_performance_int(row, "evaluation_sample_total"),
        -_performance_float(row, "best_or"),
        -_performance_float(row, "best_hr"),
        -_performance_float(row, "best_abs_beta"),
        clean_text(row.get("pgs_id")),
    )


def _release_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        clean_text(row.get("release_date")),
        clean_text(row.get("pgs_id")),
    )


def _interleave_row_lanes(lanes: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    total = sum(len(lane) for lane in lanes)
    while len(out) < total:
        progressed = False
        for lane in lanes:
            for row in lane:
                pgs_id = clean_text(row.get("pgs_id"))
                if not pgs_id or pgs_id in seen:
                    continue
                seen.add(pgs_id)
                out.append(row)
                progressed = True
                break
        if not progressed:
            break
    return out


def _unique_rows_from_sequences(sequences: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for sequence in sequences:
        for row in sequence:
            pgs_id = clean_text(row.get("pgs_id"))
            if not pgs_id or pgs_id in seen:
                continue
            seen.add(pgs_id)
            out.append(row)
    return out


def _coverage_lane_pgs_rows(
    *,
    candidate_pgs_ids: list[str],
    pgs_lookup: dict[str, dict[str, Any]],
    evaluable_pgs_ids: set[str],
) -> list[dict[str, Any]]:
    ordered_rows = [
        pgs_lookup[pgs_id]
        for pgs_id in candidate_pgs_ids
        if pgs_id in pgs_lookup and (not evaluable_pgs_ids or pgs_id in evaluable_pgs_ids)
    ]
    if not ordered_rows:
        return []
    n = len(ordered_rows)
    indices: list[int] = []

    def add_index(index: int) -> None:
        if 0 <= index < n and index not in indices:
            indices.append(index)

    # Quantile centers first: this protects large bundles from being reduced
    # to only the first few PGS IDs or only high-method siblings.
    centers = [int(round((n - 1) * fraction)) for fraction in (0.03, 0.08, 0.12, 0.25, 0.32, 0.50, 0.67, 0.80, 0.91)]
    for center in centers:
        add_index(center)
    for center in centers:
        add_index(center - 1)
        add_index(center + 1)

    for index in range(min(n, 24)):
        add_index(index)

    for index in range(n):
        add_index(index)

    return [ordered_rows[index] for index in indices]


def _quality_sorted_pgs_rows(
    *,
    candidate_pgs_ids: list[str],
    pgs_lookup: dict[str, dict[str, Any]],
    evaluable_pgs_ids: set[str],
) -> list[dict[str, Any]]:
    rows = [
        pgs_lookup[pgs_id]
        for pgs_id in candidate_pgs_ids
        if pgs_id in pgs_lookup and (not evaluable_pgs_ids or pgs_id in evaluable_pgs_ids)
    ]
    quality_lane = sorted(
        rows,
        key=lambda row: (
            -_method_quality(clean_text(row.get("method")), clean_text(row.get("method_details"))),
            -_ancestry_signal(row),
            -(int(row.get("variant_count") or 0)),
            clean_text(row.get("pgs_id")),
        ),
    )
    performance_lane = sorted(rows, key=_performance_sort_key)
    recency_lane = sorted(rows, key=_release_sort_key, reverse=True)
    variant_lane = sorted(
        rows,
        key=lambda row: (-(int(row.get("variant_count") or 0)), clean_text(row.get("pgs_id"))),
    )
    coverage_lane = _coverage_lane_pgs_rows(
        candidate_pgs_ids=candidate_pgs_ids,
        pgs_lookup=pgs_lookup,
        evaluable_pgs_ids=evaluable_pgs_ids,
    )
    return _unique_rows_from_sequences(
        [
            quality_lane[:1],
            performance_lane[:1],
            quality_lane[1:12],
            coverage_lane[:18],
            performance_lane[1:8],
            coverage_lane[18:],
            quality_lane[12:],
            performance_lane[8:],
            recency_lane,
            variant_lane,
        ]
    )


def build_stage_b_lines(
    *,
    stage_a_selection_path: Path,
    catalog_path: Path = DEFAULT_COMPACT_CATALOG_JSON,
    targets_path: Path = TARGET_SELECTION_CSV,
    model: str = DEFAULT_MODEL,
    pgs_per_bundle_cap: int = 32,
    retrieval_floor_count: int = 24,
    bundle_chunk_size: int | None = None,
    target_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    catalog = load_compact_catalog(catalog_path)
    bundles = bundles_from_catalog(catalog)
    bundle_lookup = _bundle_lookup(bundles)
    pgs_lookup = _pgs_lookup(catalog)
    targets = {target.target_id: target for target in load_targets(targets_path)}
    selections = _load_stage_a_selection(stage_a_selection_path)
    if target_ids:
        selections = {target_id: values for target_id, values in selections.items() if target_id in target_ids}

    lines: list[dict[str, Any]] = []
    for target_id, bundle_ids in selections.items():
        target = targets.get(target_id)
        if target is None:
            continue
        source_bundles = []
        evaluable_pgs_ids = source_universe_pgs_ids(target.target_source)
        floor_bundle_ids: list[str] = []
        if retrieval_floor_count > 0:
            floor_bundle_ids = [
                row.bundle.bundle_id
                for row in retrieve_bundles(
                    target=target,
                    bundles=bundles,
                    evaluable_pgs_ids=evaluable_pgs_ids,
                    max_bundles=retrieval_floor_count,
                )
            ]
        seen_canonical_bundle_ids: set[str] = set()
        for raw_bundle_id in _unique_preserve_ids(bundle_ids + floor_bundle_ids):
            bundle_id = _canonicalize_bundle_id(raw_bundle_id, bundle_lookup)
            if bundle_id is None:
                continue
            if bundle_id in seen_canonical_bundle_ids:
                continue
            seen_canonical_bundle_ids.add(bundle_id)
            bundle = bundle_lookup.get(bundle_id)
            if bundle is None:
                continue
            pgs_rows = _quality_sorted_pgs_rows(
                candidate_pgs_ids=bundle.candidate_pgs_ids,
                pgs_lookup=pgs_lookup,
                evaluable_pgs_ids=evaluable_pgs_ids,
            )[:pgs_per_bundle_cap]
            if not pgs_rows:
                continue
            source_bundles.append(
                {
                    "bundle": bundle.to_prompt_dict(candidate_pgs_ids=[row["pgs_id"] for row in pgs_rows]),
                    "pgs_records": [_compact_pgs_prompt_row(row) for row in pgs_rows],
                }
            )
        chunks = [source_bundles]
        if bundle_chunk_size and bundle_chunk_size > 0:
            chunks = [
                source_bundles[index : index + bundle_chunk_size]
                for index in range(0, len(source_bundles), bundle_chunk_size)
            ]
        for chunk_idx, source_chunk in enumerate(chunks):
            payload = {
                "schema_version": "cross_optimized.stage_b.v1",
                "target": target.to_prompt_dict(),
                "source_bundles": source_chunk,
                "bundle_chunk": {
                    "chunk_index": chunk_idx,
                    "chunk_count": len(chunks),
                    "chunk_size": len(source_chunk),
                    "full_source_bundle_count": len(source_bundles),
                },
                "instruction": (
                    "Select a provisional primary PGS only from source_bundles.pgs_records. "
                    "Optimize chunk-local recall for Stage C: when enough candidates are present, "
                    "return 8-12 diverse frontier_pgs_ids spanning plausible source axes, methods, "
                    "and visible performance signals. Keep rationale <=120 words and cite only terse "
                    "field paths in evidence_cited."
                ),
            }
            body = _response_body(
                model=model,
                stage="stage_b",
                user_payload=payload,
                schema_name="cross_stage_b_pgs_pick",
                schema=STAGE_B_SCHEMA,
                max_output_tokens=2400,
            )
            custom_id = f"stageB__{target_id}"
            if bundle_chunk_size and bundle_chunk_size > 0:
                custom_id = f"{custom_id}__chunk{chunk_idx:02d}"
            lines.append(_batch_line(custom_id, body))
    return lines


def build_stage_c_group_lines(
    *,
    proposals_path: Path,
    catalog_path: Path = DEFAULT_COMPACT_CATALOG_JSON,
    targets_path: Path = TARGET_SELECTION_CSV,
    model: str = DEFAULT_MODEL,
    group_size: int = 48,
) -> list[dict[str, Any]]:
    if group_size <= 0:
        raise ValueError("group_size must be positive.")
    data = json.loads(proposals_path.read_text(encoding="utf-8"))
    proposals = data.get("predictions", data) if isinstance(data, dict) else data
    catalog = load_compact_catalog(catalog_path)
    pgs_lookup = _pgs_lookup(catalog)
    bundles = bundles_from_catalog(catalog)
    pgs_to_bundle_ids = _pgs_to_bundle_ids(bundles)
    pgs_to_bundle_summaries = _pgs_to_bundle_summaries(bundles)
    targets = {target.target_id: target for target in load_targets(targets_path)}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in proposals:
        target_id = clean_text(row.get("target_id"))
        if target_id:
            grouped.setdefault(target_id, []).append(row)

    lines: list[dict[str, Any]] = []
    for target_id, rows in grouped.items():
        target = targets.get(target_id)
        if target is None:
            continue
        frontier_records = _stage_c_frontier_records(
            rows,
            pgs_lookup,
            pgs_to_bundle_ids,
            pgs_to_bundle_summaries,
        )
        groups = [
            frontier_records[index : index + group_size]
            for index in range(0, len(frontier_records), group_size)
        ]
        for group_idx, group_records in enumerate(groups):
            payload = {
                "schema_version": "cross_optimized.stage_c_group.v1",
                "target": target.to_prompt_dict(),
                "candidate_group": {
                    "group_index": group_idx,
                    "group_count": len(groups),
                    "group_size": len(group_records),
                    "full_frontier_record_count": len(frontier_records),
                },
                "frontier_pgs_records": group_records,
                "instruction": (
                    "This is a tournament group, not the final global decision. "
                    "Choose a provisional primary from this group and return 10-12 "
                    "diverse finalist frontier_pgs_ids when enough candidates are present. "
                    "Do not over-weight stage_b_support; reconcile it with target fit, "
                    "source-trait fit, method, ancestry, and visible performance metadata. "
                    "Keep direct or construct-adjacent candidates in the frontier even when "
                    "their support count is low."
                ),
            }
            body = _response_body(
                model=model,
                stage="stage_c",
                user_payload=payload,
                schema_name="cross_stage_c_group_tournament",
                schema=STAGE_C_SCHEMA,
                max_output_tokens=1600,
            )
            lines.append(_batch_line(f"stageCgroup__{target_id}__group{group_idx:02d}", body))
    return lines


def build_stage_c_lines(
    *,
    proposals_path: Path,
    catalog_path: Path = DEFAULT_COMPACT_CATALOG_JSON,
    targets_path: Path = TARGET_SELECTION_CSV,
    model: str = DEFAULT_MODEL,
) -> list[dict[str, Any]]:
    data = json.loads(proposals_path.read_text(encoding="utf-8"))
    proposals = data.get("predictions", data) if isinstance(data, dict) else data
    catalog = load_compact_catalog(catalog_path)
    pgs_lookup = _pgs_lookup(catalog)
    bundles = bundles_from_catalog(catalog)
    bundle_lookup = _bundle_lookup(bundles)
    pgs_to_bundle_ids = _pgs_to_bundle_ids(bundles)
    pgs_to_bundle_summaries = _pgs_to_bundle_summaries(bundles)
    targets = {target.target_id: target for target in load_targets(targets_path)}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in proposals:
        target_id = clean_text(row.get("target_id"))
        if target_id:
            grouped.setdefault(target_id, []).append(row)
    lines: list[dict[str, Any]] = []
    for target_id, rows in grouped.items():
        target = targets.get(target_id)
        if target is None:
            continue
        frontier_records = _stage_c_frontier_records(
            rows,
            pgs_lookup,
            pgs_to_bundle_ids,
            pgs_to_bundle_summaries,
        )
        chunk_predictions = []
        for row in rows:
            source_bundle_id = clean_text(row.get("source_bundle_id"))
            bundle = bundle_lookup.get(source_bundle_id)
            chunk_predictions.append(
                {
                    "chunk_id": clean_text(row.get("chunk_id")),
                    "primary_pgs_id": clean_text(row.get("primary_pgs_id")),
                    "source_bundle_id": source_bundle_id,
                    "source_bundle": bundle.to_prompt_dict(candidate_pgs_ids=[]) if bundle else {},
                    "frontier_pgs_ids": [
                        clean_text(value) for value in row.get("frontier_pgs_ids") or [] if clean_text(value)
                    ],
                    "confidence": clean_text(row.get("confidence")),
                    "rationale": compact_text(row.get("rationale"), 500),
                    "evidence_cited": [
                        clean_text(value) for value in row.get("evidence_cited") or [] if clean_text(value)
                    ][:12],
                }
            )
        payload = {
            "schema_version": "cross_optimized.stage_c.v1",
            "target": target.to_prompt_dict(),
            "chunk_predictions": chunk_predictions,
            "frontier_pgs_records": frontier_records,
            "instruction": (
                "Choose the final primary PGS only from frontier_pgs_records.pgs_id. "
                "Use stage_b_support as aggregate harness evidence, then reconcile it "
                "with endpoint fit, method, ancestry, and visible performance metadata. "
                "Do not introduce new PGS IDs."
            ),
        }
        body = _response_body(
            model=model,
            stage="stage_c",
            user_payload=payload,
            schema_name="cross_stage_c_verifier",
            schema=STAGE_C_SCHEMA,
            max_output_tokens=1000,
        )
        lines.append(_batch_line(f"stageC__{target_id}", body))
    return lines


def _load_prediction_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("predictions", data) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError(f"Prediction file must contain a list or predictions list: {path}")
    return [row for row in rows if isinstance(row, dict)]


def _draft_decision_by_target(path: Path) -> dict[str, dict[str, Any]]:
    drafts: dict[str, dict[str, Any]] = {}
    for row in _load_prediction_rows(path):
        target_id = clean_text(row.get("target_id"))
        if not target_id:
            continue
        drafts[target_id] = {
            "primary_pgs_id": clean_text(row.get("primary_pgs_id")),
            "source_bundle_id": clean_text(row.get("source_bundle_id")),
            "frontier_pgs_ids": [
                clean_text(value) for value in row.get("frontier_pgs_ids") or [] if clean_text(value)
            ][:12],
            "issues": [compact_text(value, 160) for value in row.get("issues") or [] if clean_text(value)][:4],
            "rationale": compact_text(row.get("rationale"), 420),
        }
    return drafts


def _llm_frontier_evidence_by_pgs(
    *,
    prediction_paths: list[Path],
    frontier_limit: int,
    include_rationales: bool = False,
    rationale_char_limit: int = 220,
    max_rationales_per_candidate: int = 3,
    lane_labels_by_stem: dict[str, str] | None = None,
    lane_prefix: str = "lane",
) -> dict[str, dict[str, dict[str, Any]]]:
    evidence: dict[str, dict[str, dict[str, Any]]] = {}
    for index, path in enumerate(prediction_paths, start=1):
        lane_name = (lane_labels_by_stem or {}).get(path.stem, f"{lane_prefix}_{index:02d}")
        for row in _load_prediction_rows(path):
            target_id = clean_text(row.get("target_id"))
            if not target_id:
                continue
            primary_id = clean_text(row.get("primary_pgs_id"))
            frontier_ids = [
                clean_text(value)
                for value in row.get("frontier_pgs_ids") or []
                if clean_text(value)
            ][:frontier_limit]
            for pgs_id in _unique_preserve_ids([primary_id, *frontier_ids]):
                entry = evidence.setdefault(target_id, {}).setdefault(
                    pgs_id,
                    {"frontier_count": 0, "primary_count": 0, "included_by": [], "primary_by": []},
                )
                if lane_name not in entry["included_by"]:
                    entry["frontier_count"] += 1
                    entry["included_by"].append(lane_name)
                if pgs_id == primary_id and lane_name not in entry["primary_by"]:
                    entry["primary_count"] += 1
                    entry["primary_by"].append(lane_name)
                    if include_rationales:
                        primary_rationales = entry.setdefault("primary_rationales", [])
                    if include_rationales and len(primary_rationales) < max_rationales_per_candidate:
                        rationale = compact_text(row.get("rationale"), rationale_char_limit)
                        if rationale:
                            primary_rationales.append(
                                {
                                    "lane": lane_name,
                                    "source_bundle_id": clean_text(row.get("source_bundle_id")),
                                    "rationale": rationale,
                                }
                            )
    return evidence


def _agent_visible_lane_labels(prediction_paths: list[Path], prefix: str) -> dict[str, str]:
    return {path.stem: f"{prefix}_{index:02d}" for index, path in enumerate(prediction_paths, start=1)}


def _empty_llm_frontier_evidence() -> dict[str, Any]:
    return {"frontier_count": 0, "primary_count": 0, "included_by": [], "primary_by": []}


def _order_stage_d_cards(cards: list[dict[str, Any]], candidate_order: str) -> list[dict[str, Any]]:
    if candidate_order == "input":
        return cards
    if candidate_order == "reverse_input":
        return list(reversed(cards))
    if candidate_order == "pgs_id":
        return sorted(cards, key=lambda card: clean_text(card.get("pgs_id")))
    raise ValueError(f"Unsupported candidate_order: {candidate_order}")


def _load_optional_json(path: Path | None) -> Any:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _lookup_tool_evidence(tool_data: Any, target_id: str, pgs_id: str) -> Any:
    if not tool_data:
        return None
    if isinstance(tool_data, dict):
        for key in (f"{target_id}|{pgs_id}", f"{target_id}::{pgs_id}", f"{target_id}__{pgs_id}"):
            if key in tool_data:
                return tool_data[key]
        target_block = tool_data.get(target_id)
        if isinstance(target_block, dict):
            return target_block.get(pgs_id)
    return None


def _stage_d_candidate_card(
    *,
    record: dict[str, Any],
    llm_evidence: dict[str, Any],
    advisory_evidence: dict[str, Any],
    open_targets_evidence: Any,
    genetic_correlation_evidence: Any,
    pairwise_review_evidence: Any = None,
    include_llm_provenance: bool = True,
    performance_mode: str = "full",
) -> dict[str, Any]:
    if performance_mode not in {"full", "source_only"}:
        raise ValueError(f"Unsupported performance_mode: {performance_mode}")
    card: dict[str, Any] = {}
    for key in (
        "pgs_id",
        "reported_trait",
        "mapped_trait_labels",
        "mapped_trait_ids",
        "source_bundles",
        "method",
        "method_details",
        "variant_count",
        "ancestry_gwas",
        "ancestry_training",
        "ancestry_evaluation",
        "release_date",
        "stage_b_support",
    ):
        value = record.get(key)
        if value not in (None, "", [], {}):
            card[key] = value
    if performance_mode == "full":
        value = record.get("performance")
        if value not in (None, "", [], {}):
            card["performance"] = value
    if include_llm_provenance:
        card["llm_frontier_evidence"] = llm_evidence
        if advisory_evidence not in (None, "", [], {}):
            card["non_decision_advisory_evidence"] = advisory_evidence
    if open_targets_evidence not in (None, "", [], {}):
        card["open_targets_overlap"] = open_targets_evidence
    if genetic_correlation_evidence not in (None, "", [], {}):
        card["genetic_correlation_evidence"] = genetic_correlation_evidence
    if pairwise_review_evidence not in (None, "", [], {}):
        card["pairwise_review_evidence"] = pairwise_review_evidence
    return card


def _stage_d_instruction(
    prompt_mode: str,
    anchor_lane: str,
    *,
    omit_llm_provenance: bool = False,
) -> str:
    base = (
        "Choose primary_pgs_id only from candidate_evidence_cards. Priority order is "
        "LLM Harness > Skill > Tools. You are the final decision maker: do not apply "
        "a numeric formula or defer to any single metadata field, vote count, or tool "
        "field. No specific-trait, ICD, disease-category, whitelist, blacklist, or "
        "case-by-case rule is allowed."
    )
    if prompt_mode == "anchor_precision":
        return (
            f"{base} This is an anchor review reconciler. Treat anchor_lane="
            f"{anchor_lane or 'none'} as the baseline LLM final lane inside llm_frontier_evidence; "
            "preserve the anchor lane primary when its source axis is coherent. Switch only when "
            "the cross-transfer skill gives a generalizable, source-axis-level reason that the "
            "anchor is likely a broad proxy, wrong endpoint, or weak within-axis model. Do not "
            "switch solely because another candidate has broader validation, larger record counts, "
            "more variants, newer release date, or tool overlap. When switching, explain why that "
            "improves the target-transfer case rather than only metadata breadth."
        )
    if prompt_mode == "anchor_evidence_burden_review":
        return (
            f"{base} This is an anchor evidence-burden reconciler. Treat anchor_lane="
            f"{anchor_lane or 'none'} as a strong LLM-harness prior, but not an automatic winner. "
            "The purpose is to review expanded-recall challengers without over-switching to a "
            "closer-looking label whose PGS evidence is sparse or weak. First reconstruct the "
            "best LLM-readable case for the anchor primary from llm_frontier_evidence and visible "
            "PGS metadata. Then audit each challenger. Switch away from the anchor only when the "
            "challenger has two independent LLM-readable reasons: a coherent source-axis bridge "
            "that is not merely lexical closeness, and materially stronger visible PGS evidence "
            "such as endpoint-useful raw performance, evaluation record "
            "depth, ancestry portability, method context, or PRS-only evidence. do not switch "
            "merely because the challenger has a closer-looking label, a narrower disease name, "
            "more generic validation, more variants, newer release date, broader source category, "
            "or more frontier appearances. Also do not keep the anchor by inertia: if its source "
            "bridge is broad/generic, wrong-direction, or visibly weak and the challenger satisfies "
            "both burden reasons, choose the challenger. Explain the anchor case, the strongest challenger case, and "
            "why the switch burden was or was not met."
        )
    if prompt_mode == "anchor_challenger_gate_review":
        return (
            f"{base} This is an anchor-challenger gate reconciler. Treat anchor_lane="
            f"{anchor_lane or 'none'} and the candidate with LLM primary provenance as an "
            "LLM-harness prior, not an automatic winner. The expanded candidates are review "
            "challengers, not advisor authorities. First reconstruct the strongest target-transfer "
            "case for the anchor from its source-axis bridge, endpoint fit, visible PGS evidence, "
            "ancestry/method context, and any LLM rationale fields. Then audit each challenger "
            "against that case. A switch requires a coherent source-axis bridge plus materially "
            "stronger visible PGS evidence, or a source-equivalent model case whose endpoint, "
            "PRS-only, effect-size, evaluation-context, ancestry, or method evidence is stronger "
            "than the anchor's. Keep the anchor when challengers mainly offer lexical closeness, "
            "metadata scale, larger samples, more records, newer release, broader validation, "
            "candidate position, advisor provenance, or generic source plausibility without a "
            "better transfer argument. This is not a formula, threshold, vote, rank, source-category "
            "rule, whitelist, blacklist, or case-specific exception. Explain the anchor case, "
            "the best challenger case, and the final LLM-led decision."
        )
    if prompt_mode == "anchor_switch_audit_review":
        return (
            f"{base} This is an anchor switch-audit reconciler. The candidate set should contain "
            "the anchor_lane primary and a primary proposed by a later LLM review. The proposed "
            "switch is a claim to audit, not evidence of correctness, and the anchor is a "
            "serious LLM-harness prior, not an automatic winner. do not use a revert rule, a "
            "switch rule, a vote count, a threshold, or a numeric formula. Compare the anchor "
            "case and the switch case from their LLM rationales, source-axis bridge, endpoint "
            "specificity, visible PRS evidence, ancestry/method context, and target-transfer "
            "plausibility. Keep the anchor when the switch case mainly relies on a closer-looking "
            "label, narrower disease name, generic source category, or directionally plausible "
            "but weaker PGS evidence. Choose the switch when the anchor is broad, downstream, "
            "wrong-direction, or visibly weak, and the switch case has a coherent source bridge "
            "plus materially stronger or more endpoint-useful visible PGS evidence. Explain the anchor case, the "
            "switch case, and the final LLM-led reason without using a hard revert or switch rule."
        )
    if prompt_mode == "source_axis_champion":
        return (
            f"{base} This is a source-axis champion reconciler. First identify the best source "
            "axis using the cross-transfer skill; then select the best PGS within that axis. "
            "Use LLM-harness agreement to break close source-axis ties, not to override a clearly "
            "better endpoint/source axis. Prefer specific, coherent, evidence-supported source "
            "bridges over broad, generic, or merely well-validated proxy traits. Explain any disagreement with "
            "the strongest LLM-harness primary lane."
        )
    if prompt_mode == "source_axis_consensus_guard":
        return (
            f"{base} This is a source-axis consensus guard reconciler. First identify the best "
            "source axis using the cross-transfer skill; then compare the source-axis champion "
            f"against anchor_lane={anchor_lane or 'none'}. Strong multi-lane LLM primary agreement "
            "for an anchor is high-priority harness evidence when the anchor source axis is "
            "coherent, but it is not a threshold or formula. Switch away from such an anchor only "
            "when the challenger has a clearer source-axis/endpoint bridge or clearly stronger "
            "within-source PGS evidence. When LLM primary agreement is weak, split, or attached "
            "to a broad proxy source, be willing to choose the source-axis champion. Explain the "
            "anchor-vs-champion comparison and the reason the selected candidate is better "
            "supported for target transfer."
        )
    if prompt_mode == "challenger_audit":
        return (
            f"{base} This is a challenger audit reconciler. Treat anchor_lane="
            f"{anchor_lane or 'none'} as the prior LLM final lane, but do not keep it by inertia. "
            "Audit every non-anchor candidate that appears in multiple LLM frontiers, has Stage B "
            "frontier support, or has stronger visible PGS evidence. Counts and record metadata "
            "are review triggers, not decision rules: do not convert counts into a formula, and "
            "do not select a challenger unless the cross-transfer skill supports its source axis "
            "and endpoint fit. Conversely, if a challenger has coherent source-axis fit plus "
            "stronger visible PGS evidence than the anchor, prefer the challenger even when it was "
            "not the most common primary lane. Explain the best challenger-vs-anchor comparison."
        )
    if prompt_mode == "metadata_challenger_review":
        return (
            f"{base} This is a metadata challenger review reconciler. Treat anchor_lane="
            f"{anchor_lane or 'none'} as the prior LLM final lane. The non-LLM metadata advisor "
            "is not a judge; it is only a cheap review trigger derived from visible candidate "
            "metadata and prior frontiers. Do not select an advised candidate because it was "
            "advised, because it has larger record counts, or because it has broader validation. "
            "Use the advisor to decide which challenger deserves careful LLM review, then apply "
            "the cross-transfer skill: source-axis fit, endpoint fit, within-source PGS evidence, "
            "and target-transfer plausibility. LLM Harness and Skill remain higher priority than the "
            "advisor. Explain why the selected primary beats both the anchor and the strongest "
            "advised challenger."
        )
    if prompt_mode == "robust_evidence_review":
        return (
            f"{base} This is a robust evidence review reconciler. First compare source-axis and "
            "endpoint fit. If one candidate has a clearly direct, specific, and coherent source "
            "axis, keep that as the leading reason. If all leading candidates are indirect "
            "proxies, construct-adjacent, upstream, downstream, or similarly uncertain, then "
            "give more attention to visible PGS evidence: actual evaluation records, evaluation "
            "sample sizes, ancestry breadth, method context, raw PRS performance descriptions, "
            "and whether the endpoint is PRS-only rather than covariate-heavy. Do not convert "
            "validation breadth, record counts, variant counts, release dates, or LLM frontier "
            "counts into a formula. A stronger PGS evidence profile can beat a slightly closer "
            "but weak source only when the selected source remains biologically or construct "
            "coherent for cross-transfer. Explain the source-fit tier first, then the PGS "
            "evidence comparison."
        )
    if prompt_mode == "early_tail_robust_review":
        return (
            f"{base} This is a robust source-evidence review reconciler. Start by assigning each "
            "candidate to a source-fit tier: direct/specific, construct-adjacent, upstream or "
            "downstream proxy, broad comorbidity proxy, or weak/distant. Prefer the highest "
            "source-fit tier, but when several leading candidates are indirect or similarly "
            "coherent, use visible PGS evidence to decide which one is more likely to be an "
            "effective target-transfer primary: endpoint specificity, PRS-only validation signal, evaluation "
            "sample size, ancestry breadth, method context, and raw performance descriptions. "
            "Do not convert validation breadth, record counts, variant counts, release dates, "
            "or LLM frontier counts into a formula. Do not select a broad proxy merely because "
            "it is robust; it must remain a coherent cross-transfer source. Explain the selected "
            "source-fit tier and why it is better supported for target transfer than the "
            "nearest alternatives."
        )
    if prompt_mode == "tiered_tail_precision_review":
        return (
            f"{base} This is a tiered source-evidence reconciler. Internally assign each "
            "candidate to a qualitative source-fit tier relative to the target: direct/specific, "
            "measurement or mechanistic proxy, construct-adjacent, upstream/downstream proxy, "
            "broad comorbidity/generalist proxy, or weak/distant. These tiers are LLM judgments "
            "from the provided text, not disease-category rules or formulas. Select from the "
            "highest defensible source-fit tier unless its visible PGS evidence is clearly sparse "
            "or weak and the next tier still has a coherent transfer bridge plus materially "
            "stronger PRS evidence. Within the selected tier, choose the best PGS using endpoint "
            "specificity, PRS-only validation signal when visible, evaluation records and sample "
            "sizes, ancestry breadth, method context, and raw performance descriptions. Use "
            "LLM frontier agreement to identify candidates and break close qualitative ties, not "
            "as a count rule. Do not switch to a lower-tier broad proxy solely because it has "
            "larger record counts, more variants, newer release date, broader validation, tool "
            "overlap, or more frontier appearances. Explain the selected source-fit tier, the "
            "nearest same-tier alternative, and why any stronger-metadata lower-tier alternative "
            "does not beat the selected primary for target transfer."
        )
    if prompt_mode == "rationale_grounded_review":
        return (
            f"{base} This is a rationale-grounded LLM harness reconciler. Use the upstream "
            "LLM primary_rationales inside llm_frontier_evidence as high-priority harness "
            "evidence, because they explain why independent LLM lanes selected their primaries. "
            "Do not treat rationale count, primary count, frontier count, or rationale wording "
            "as a formula or as hidden performance evidence. First build the strongest qualitative "
            "case for each candidate with LLM primary rationales, then compare those cases "
            "against the best non-primary challenger using the cross-transfer skill. Prefer "
            "the candidate whose LLM rationales and visible PGS metadata jointly support a "
            "specific, coherent source bridge for the target. Switch away "
            "from a rationale-supported primary only when another candidate has a clearer "
            "source-axis bridge or materially stronger PRS evidence while remaining coherent "
            "for transfer. Penalize broad, generic, comorbidity-only, or purely high-metadata "
            "proxies when the rationales do not establish a bridge to the target. Explain the "
            "decisive rationale-vs-challenger comparison."
        )
    if prompt_mode == "order_debiased_review":
        return (
            f"{base} This is an order-debiased reconciler. Candidate card order is "
            "a harness presentation detail, not priority evidence; candidate_order may be "
            "input, reversed, or otherwise arbitrary. Counter input-order anchoring by first "
            "auditing the later-position cards and any low-primary-count candidate with a "
            "coherent source bridge or visibly strong PGS evidence. Then compare those "
            "challengers against the strongest LLM-harness primary candidates using the "
            "cross-transfer skill. Do not "
            "keep the first card by inertia, and do not switch to a later card because of "
            "position alone. LLM frontier agreement is harness evidence, not a vote formula; "
            "record counts, validation breadth, variant counts, tool overlap, and release date "
            "are tie-break evidence only after source-axis and endpoint fit are coherent. "
            "Explain the best later-card challenger versus the selected primary."
        )
    if prompt_mode == "advisor_duel_review":
        return (
            f"{base} This is a two-candidate advisor-duel reconciler. The candidate set should "
            "contain the current LLM-anchor primary and a non-decision metadata-advisor "
            "challenger. Treat the LLM anchor as a serious prior from the harness, but not as "
            "an automatic winner. Treat non_decision_advisory_evidence only as the reason a "
            "challenger was brought to review; it is not a rule, rank, vote, or authority. "
            "Decide the duel with the cross-transfer skill: source-axis coherence, endpoint "
            "specificity, visible PRS evidence, ancestry/method context, and target-transfer "
            "plausibility. Prefer the anchor when the challenger is only broader, larger, newer, "
            "or more validated without a clearer transfer bridge. Switch to the challenger when "
            "it has a comparably coherent or clearer source-axis bridge plus materially stronger "
            "visible PGS evidence. Explain the anchor-vs-challenger "
            "comparison, and explicitly reject any numeric formula or advisor deference."
        )
    if prompt_mode == "advisor_duel_precision_switch":
        return (
            f"{base} This is a symmetric two-candidate review duel. The candidate set "
            "should contain an LLM-anchor primary and a non-decision metadata-advisor challenger, "
            "but neither candidate is the default winner. Treat non_decision_advisory_evidence "
            "only as the reason a challenger was surfaced, not as authority. Compare the two candidates symmetrically using "
            "the cross-transfer skill: source-axis coherence, endpoint specificity, visible PRS "
            "evidence, ancestry/method context, and target-transfer plausibility. If both candidates "
            "have coherent transfer bridges, prefer the one with stronger visible PGS evidence "
            "even if it is not the LLM anchor. Keep the anchor only when "
            "the challenger is broader, generic, weakly bridged, or relies mainly on metadata "
            "scale. Do not use a formula, threshold, vote count, or advisor deference. Explain "
            "the symmetric anchor-vs-challenger comparison."
        )
    if prompt_mode == "advisor_challenge_first_review":
        return (
            f"{base} This is an advisor challenge-first reconciler. The candidate set should "
            "contain an LLM-anchor primary and a non-decision metadata-advisor challenger. "
            "Start by steelman the advisor-surfaced candidate first: ask whether it has a "
            "coherent source-axis bridge, endpoint specificity, and materially stronger visible "
            "PRS evidence. Then audit the LLM anchor as the strongest "
            "alternative. This ordering is not advisor deference: non_decision_advisory_evidence "
            "is only a review trigger, not a rule, rank, vote, score, threshold, or authority. "
            "Choose the advisor-surfaced "
            "candidate when its source bridge is at least comparably coherent and its visible "
            "PGS evidence is materially stronger or more endpoint-useful. Keep the anchor when "
            "the advisor is broad, generic, weakly bridged, covariate-heavy, or mainly larger, "
            "newer, or more validated without a target-coherent transfer bridge. Explain the "
            "advisor steelman, the anchor rebuttal, and the LLM-led reason for the final choice."
        )
    if prompt_mode == "advisor_panel_review":
        return (
            f"{base} This is an advisor-panel reconciler. The candidate set should contain the "
            "current LLM-anchor primary plus one or more candidates surfaced by cheap "
            "non-decision advisors. non_decision_advisory_evidence explains why a candidate was "
            "brought into the panel; it is not a ranking, vote, score, threshold, or authority. "
            "Review the LLM anchor and all surfaced advisors with the cross-transfer skill: "
            "source-axis coherence, endpoint specificity, visible PRS evidence, ancestry/method "
            "context, and target-transfer plausibility. Prefer the anchor when advisors mainly offer broader validation, metadata "
            "scale, newer release date, or generic proxy coverage without a clearer transfer "
            "bridge. Switch to an advisor-surfaced candidate only when it has a comparably "
            "coherent or clearer source bridge plus materially stronger visible PGS evidence for "
            "target transfer. If advisors disagree, do not average them; decide which "
            "qualitative case is strongest under LLM Harness > Skill > Tools. Explain the "
            "selected primary against the strongest losing anchor/advisor alternatives."
        )
    if prompt_mode == "advisor_source_aware_panel_review":
        return (
            f"{base} This is an advisor-source-aware panel reconciler. The candidate set should "
            "contain the current LLM-led primary plus candidates surfaced by one or more cheap "
            "non-decision advisors. Multiple advisor sources for the same candidate are "
            "corroboration triggers, not votes, weights, ranks, thresholds, or authority. Use "
            "them to decide which challengers deserve careful review, but never select from "
            "advisor agreement alone. First compare source-axis bridge quality: direct/specific, "
            "measurement or mechanistic proxy, construct-adjacent, upstream/downstream proxy, "
            "broad comorbidity/generalist proxy, or weak/distant. These are qualitative LLM "
            "judgments from the provided text, not trait-category rules. Then compare visible "
            "PGS evidence inside only the candidates whose source bridge remains coherent: "
            "endpoint specificity, raw PRS performance descriptions, evaluation records and "
            "sample sizes, ancestry breadth, method context, and whether evidence appears "
            "PRS-only rather than covariate-heavy. Prefer the current LLM-led primary when advisor candidates "
            "are mainly broader, larger, newer, or generic proxies. Switch to an advisor-surfaced "
            "candidate when the bridge is at least comparably coherent and visible PGS evidence "
            "is materially stronger for target transfer. Explain the source tier and the "
            "decisive PGS-evidence comparison against the strongest losing alternative."
        )
    if prompt_mode == "harness_convergence_guard_review":
        return (
            f"{base} This is a harness-convergence guard reconciler. The candidate set may contain "
            "candidates surfaced by several independent LLM-led lanes and later LLM review passes. "
            "Treat repeated LLM convergence on the same candidate or source axis as high-priority "
            "harness evidence, because it can reveal a stable qualitative judgment across prompts. "
            "Do not turn that convergence into a vote, count threshold, score, rank, formula, or "
            "automatic winner. First reconstruct the strongest qualitative case for the converged "
            "LLM candidate or source axis using only the visible card fields and LLM frontier or "
            "advisor evidence. Then use the cross-transfer skill to falsify that case: ask whether "
            "the converged source bridge is broad, generic, weak, wrong-direction, or supported "
            "mainly by metadata scale. Keep the converged LLM candidate when its source bridge is "
            "coherent and no challenger has both a clearer target-transfer bridge and materially "
            "stronger visible PGS evidence. Switch only when the challenger has an independently "
            "coherent bridge plus stronger endpoint-useful PRS evidence, or when the converged "
            "case visibly fails the source-bridge audit. Explain the converged case, the strongest "
            "challenger, and why the final LLM-led choice is not a mechanical agreement rule."
        )
    if prompt_mode == "same_source_model_audit_review":
        return (
            f"{base} This is a same-source model audit reconciler. Use it when the LLM "
            "anchor and a non-decision advisor-surfaced challenger share the same source "
            "axis, mapped construct, or source bundle. In that setting, source fit no "
            "longer decides the model choice; compare the PGS models themselves. "
            "non_decision_advisory_evidence is a review trigger only, not a rank, vote, "
            "threshold, or authority. Reconstruct the best model-level case for each "
            "candidate using endpoint definition, method context, ancestry context, raw "
            "performance descriptions, evaluation records and sample context, release "
            "context, and variant count only in method context. Do not treat any single "
            "headline metric as universal across endpoints; AUC, R2, odds ratios, hazard "
            "ratios, record counts, and sample counts can be informative but not universal "
            "across endpoints. Switch from the LLM anchor when the challenger is "
            "source-equivalent and has the stronger model-level transfer case, or when "
            "the anchor's model evidence is visibly thinner. Keep the anchor when the "
            "challenger mainly offers metadata scale without endpoint, method, ancestry, "
            "or performance support. If candidates do not share a source axis, return to "
            "source bridge first. Explain the source-equivalence check and the decisive "
            "model-level comparison."
        )
    if prompt_mode == "source_equivalent_model_challenger_review":
        return (
            f"{base} This is a source-equivalent model challenger reconciler. First ask "
            "whether the LLM anchor and advisor-surfaced challenger share the same mapped "
            "construct, source bundle, or near-equivalent source axis. If they do, lane "
            "convergence is weaker evidence than usual because the disagreement is mostly "
            "model-level, not source-axis-level. Do not select the advisor-surfaced model by "
            "rule, count, rank, threshold, or authority; it remains only a review trigger. "
            "Compare the models as alternative implementations for the same source axis. "
            "A larger best_auc, best_r2, sample count, or ancestry breadth is useful context "
            "but not a universal transfer ordering, because those fields can reflect endpoint, "
            "cohort, or reporting differences. Give serious weight to model-level signals that "
            "may transfer differently across related endpoints: method family, polygenic coverage "
            "in method context, endpoint definition, odds or hazard estimates when relevant, "
            "evaluation record depth, release context, and whether the model looks over-specialized "
            "to the anchor endpoint. Switch when the challenger has a credible source-equivalent "
            "model case that the anchor's headline metrics do not settle. Keep the anchor when "
            "the challenger mainly offers scale, novelty, or advisor provenance without a "
            "stronger model-level argument. If the source axes are not equivalent, return to "
            "source bridge first. Explain the source-equivalence check and why the final LLM-led "
            "model choice is not a metadata rule."
        )
    if prompt_mode == "same_source_metric_calibrated_review":
        return (
            f"{base} This is a same-source metric-calibrated reconciler. Use it when the "
            "candidate set contains source-equivalent PGS alternatives. Candidate provenance "
            "is review context only: llm_frontier_evidence and non_decision_advisory_evidence "
            "explain why candidates are present, not which candidate should win. First confirm "
            "whether the leading candidates share a source axis, mapped construct, or source "
            "bundle. If they do, compare PGS model evidence rather than source fit. Headline "
            "metrics are not automatically comparable: a larger best_auc, best_r2, sample "
            "count, validation count, ancestry set, release date, or variant count can reflect "
            "endpoint definition, cohort construction, covariate use, reporting choices, or "
            "source-endpoint specialization. Do not select by formula, larger metric, anchor "
            "status, advisor status, lane count, or metadata scale. Decide which model has the "
            "stronger target-portable PRS signal from endpoint definition, method family, "
            "PRS-only versus covariate-heavy evidence when visible, odds/hazard/beta estimates "
            "when relevant, evaluation record context, ancestry context, release context, and "
            "over-specialization risk. A smaller-headline model can beat a larger-headline model "
            "when its evidence is more endpoint-relevant or more clearly PRS-based; a larger-headline "
            "model can still win when its evidence is comparable and well supported. Explain the "
            "source-equivalence check, metric comparability, and final LLM-led model choice."
        )
    if prompt_mode == "binary_effect_calibrated_review":
        return (
            f"{base} This is a binary/time-to-event effect-calibrated reconciler. Use it when "
            "the target or leading candidates are clinical diagnoses, binary phenotypes, "
            "case-control endpoints, time-to-event endpoints, or liability-like outcomes; "
            "it is not a formula. "
            "Candidate provenance is review context only; it is not priority evidence. First "
            "compare source-axis coherence and endpoint fit. Among coherent candidates, calibrate "
            "metrics by endpoint type: odds ratios, hazard ratios, or beta estimates can be "
            "serious risk-separation evidence, while AUC and R2 can be informative but not "
            "universal. Do not select by formula, larger metric, anchor status, advisor status, "
            "lane count, sample count, record count, source category, or release date. Ask whether "
            "each metric is aligned with the target endpoint and whether it appears to describe "
            "PRS signal rather than a covariate-heavy full model. A candidate with visible "
            "effect-size evidence can beat a candidate with larger AUC or R2 when both source "
            "bridges are coherent and the effect-size evidence is more endpoint-relevant or more "
            "clearly PRS-based. A larger-AUC/R2 candidate can still win when those metrics are "
            "comparable and better supported. This is no disease-specific rule; explain the "
            "source bridge, endpoint-metric calibration, and final LLM-led model choice."
        )
    if prompt_mode == "evidence_only_early_tail_panel_review":
        if omit_llm_provenance:
            return (
                f"{base} This is a symmetric PGS-evidence panel reconciler. Candidate cards are "
                "shown without lane or advisor provenance, so do not infer importance from why a "
                "candidate appears in the panel. Do not preserve an incumbent, do not favor an "
                "advisor, and do not count appearances across prior passes. Decide as if the "
                "candidate cards were presented symmetrically. First compare source-axis bridge "
                "quality using only provided target and candidate text: direct/specific, "
                "measurement or mechanistic proxy, construct-adjacent, upstream/downstream proxy, "
                "broad comorbidity/generalist proxy, or weak/distant. These are qualitative LLM "
                "judgments, not disease-category rules. Then compare visible PGS evidence among "
                "candidates with coherent bridges: endpoint specificity, raw PRS performance "
                "descriptions, evaluation records and sample sizes, ancestry breadth, method "
                "context, and whether evidence appears PRS-only rather than covariate-heavy. A "
                "candidate with a slightly less direct but still coherent bridge can win when its "
                "visible PGS evidence is materially stronger for target transfer. Explain the "
                "source bridge and PGS-evidence tradeoff, not provenance."
            )
        return (
            f"{base} This is an evidence-only panel reconciler. Candidate provenance "
            "is not priority evidence: llm_frontier_evidence and non_decision_advisory_evidence "
            "only explain why a candidate appears in the small panel. do not preserve an incumbent, "
            "do not favor an advisor, and do not count lane or advisor appearances. Decide as if "
            "the candidate cards were presented symmetrically. First compare source-axis bridge "
            "quality using only provided target and candidate text: direct/specific, measurement "
            "or mechanistic proxy, construct-adjacent, upstream/downstream proxy, broad "
            "comorbidity/generalist proxy, or weak/distant. These are qualitative LLM judgments, "
            "not disease-category rules. Then compare visible PGS evidence among candidates with "
            "coherent bridges: endpoint specificity, raw PRS performance descriptions, evaluation "
            "records and sample sizes, ancestry breadth, method context, and whether evidence "
            "appears PRS-only rather than covariate-heavy. A candidate with a slightly less direct but still coherent "
            "bridge can win when its visible PGS evidence is materially stronger for target "
            "transfer. Explain the source bridge and PGS-evidence tradeoff, not provenance."
        )
    if prompt_mode == "extreme_tail_evidence_panel_review":
        return (
            f"{base} This is an evidence panel reconciler. Candidate provenance "
            "is context only: llm_frontier_evidence and non_decision_advisory_evidence identify "
            "which candidates need review, not which candidate should win. source fit is a coherence "
            "gate, not an automatic winner: discard weak "
            "or distant bridges, but among candidates with coherent bridges, allow materially "
            "stronger visible PGS evidence to beat a closer-looking label. Compare endpoint "
            "specificity, PRS-only versus covariate-heavy signals, raw performance descriptions, "
            "evaluation record breadth, sample context, ancestry portability, method context, "
            "and endpoint relevance. do not use "
            "a numeric formula, vote count, threshold, trait category rule, source whitelist, "
            "or advisor agreement as the decision. Explain why the winner is better supported "
            "for target transfer than the strongest losing candidate."
        )
    if prompt_mode == "expanded_evidence_shortlist_review":
        return (
            f"{base} This is an expanded evidence shortlist reconciler. The panel is larger "
            "because candidate recall is being increased with provided Stage C frontier records; "
            "candidate provenance is context only, not priority evidence. Start with source-axis "
            "triage: identify which candidates have a coherent direct, measurement, mechanistic, "
            "construct-adjacent, upstream, downstream, or specific proxy bridge to the target, "
            "and set aside weak, distant, overly broad, or generic bridges even when their PGS "
            "metadata looks strong. This triage is a qualitative LLM judgment from the provided "
            "text, not a disease-category rule. Among candidates that pass the coherence gate, "
            "compare endpoint specificity, raw PRS performance descriptions, evaluation records "
            "and sample context, ancestry portability, method context, and evidence that the PGS "
            "has target-relevant predictive support. do not use candidate position, vote count, advisor "
            "agreement, record count, variant count, source category, or any numeric formula as "
            "the decision. Explain the winning source bridge and the decisive PGS-evidence "
            "comparison against the strongest coherent loser."
        )
    if prompt_mode == "coherent_evidence_decisive_review":
        return (
            f"{base} This is a coherent-evidence decisive reconciler. Candidate provenance is "
            "context only: llm_frontier_evidence and non_decision_advisory_evidence explain why "
            "a candidate is present, not which candidate should win. First exclude only candidates "
            "whose source bridge to the target is weak, distant, or generic without a record-visible "
            "bridge. For the remaining coherent candidates, do not automatically choose the closest "
            "label or most disease-specific source. Decide which PGS is most likely to provide a "
            "strong transportable PRS signal for the target by comparing endpoint specificity, raw "
            "PRS performance descriptions, evaluation records and sample context, ancestry "
            "portability, method context, and whether the evidence is PRS-relevant rather than "
            "covariate-heavy. A less direct but still coherent source can beat a closer-looking "
            "candidate when its visible PGS evidence is materially stronger. Conversely, a broad "
            "or generic source cannot win from metadata scale alone; it must have a coherent "
            "target-transfer bridge. Do not use candidate position, vote count, advisor agreement, "
            "record count, variant count, source category, tool overlap, or any numeric formula as "
            "the decision. Explain the coherent source bridge, the decisive PGS-evidence comparison, "
            "and why the strongest closer-looking loser does not beat the selected primary."
        )
    if prompt_mode == "bridge_calibrated_evidence_review":
        return (
            f"{base} This is a bridge-calibrated evidence reconciler. Candidate provenance is "
            "context only: llm_frontier_evidence and non_decision_advisory_evidence explain why "
            "a candidate is present, not which candidate should win. First identify candidates "
            "with a coherent source bridge to the target: direct construct, core measurement, "
            "mechanistic pathway, construct-adjacent condition, upstream driver, or downstream "
            "consequence. Set aside weak, distant, generic, or merely comorbid sources unless "
            "the card text supplies a concrete bridge. Among candidates with coherent bridges, "
            "do not let small differences in label closeness automatically beat materially "
            "stronger visible PGS evidence. Measurement and biomarker sources can be strong "
            "when they represent a core target construct; diagnosis labels can be weak when "
            "they are sparse, covariate-heavy, overly broad, or only superficially related. "
            "Compare endpoint specificity, raw PRS performance descriptions, evaluation "
            "records and sample context, ancestry portability, method context, and whether "
            "the evidence supports PRS transfer rather than only metadata scale. Do not use "
            "candidate order, vote count, advisor agreement, record count, variant count, "
            "source category, tool overlap, or any numeric formula as the decision. Explain "
            "the winning bridge and why the strongest loser is less convincing."
        )
    if prompt_mode == "llm_lane_panel_review":
        return (
            f"{base} This is an LLM-lane panel reconciler. The candidate set should contain "
            "primaries from independent LLM-led final lanes. llm_frontier_evidence tells you "
            "which lanes kept a candidate in scope or made it primary; it is not a majority "
            "vote, threshold, rank, or formula. First reconstruct the strongest lane-level "
            "qualitative case for each candidate from its source axis, endpoint fit, visible "
            "PRS evidence, ancestry/method context, and target-transfer plausibility. Then "
            "choose the candidate with the strongest lane-level qualitative case under "
            "LLM Harness > Skill > Tools. Do not average lanes, obey the most common primary, "
            "or preserve any lane by inertia. Switch away "
            "from a lane primary only when another lane's candidate has a clearer transfer "
            "bridge or materially stronger visible PGS evidence while remaining coherent for "
            "the target. Explain the selected primary against the strongest losing LLM-lane "
            "alternative."
        )
    if prompt_mode == "llm_early_tail_tiebreak_review":
        return (
            f"{base} This is an LLM lane tie-break reconciler. The candidate set should "
            "contain only candidates produced by conflicting LLM-led final lanes for the same "
            "target. llm_frontier_evidence identifies the lane provenance; it is not a lane "
            "vote, average, threshold, or merge rule. Your task is to choose the candidate with "
            "the strongest target-transfer case, not the candidate with the most lane mentions. "
            "First compare source-axis bridge quality for each candidate using the cross-transfer "
            "skill. Then compare visible PGS evidence only among candidates with coherent bridges: "
            "endpoint specificity, raw PRS performance descriptions, evaluation records and "
            "sample sizes, ancestry breadth, method context, and whether evidence appears PRS-only "
            "rather than covariate-heavy. If one lane candidate has "
            "a closer source bridge but thin PGS evidence and the other has a slightly less direct "
            "yet still coherent bridge with materially stronger PGS evidence, choose the stronger "
            "target-transfer case. Explain the decisive bridge-vs-PGS evidence tradeoff."
        )
    if prompt_mode == "order_perturbation_tiebreak_review":
        return (
            f"{base} This is an order-perturbation tiebreak reconciler for presentation-sensitive "
            "disagreement between LLM-led lanes that saw the same evidence in different candidate "
            "orders. The disagreement is a reason to audit carefully, not evidence that either "
            "lane is correct. do not prefer the original-order lane or the reverse-order lane, "
            "and do not use input order, lane order, candidate position, lane count, vote count, "
            "thresholds, or any merge rule as the decision. Use upstream primary_rationales only "
            "to reconstruct each lane's qualitative case, then judge the candidates symmetrically "
            "with the cross-transfer skill. First compare source-axis bridge quality and endpoint "
            "fit. Then compare visible PGS evidence only among candidates with coherent bridges: "
            "raw PRS performance descriptions, evaluation record depth, sample context, ancestry "
            "portability, method context, and whether the signal appears PRS-only rather than "
            "covariate-heavy. "
            "A closer-looking source with thin PGS evidence can lose to a slightly less direct "
            "but coherent source with materially stronger visible PGS evidence; a broad proxy with "
            "strong metadata still loses if its bridge is weak or generic. Explain why the final "
            "choice is robust to the order perturbation."
        )
    if prompt_mode == "advisor_contradiction_falsification_review":
        return (
            f"{base} This is an advisor contradiction falsification reconciler. The candidate set "
            "should contain a current LLM-led primary plus one or more candidates surfaced by a "
            "cheap non-decision advisor. The advisor explains why a challenger deserves review; "
            "it is not authority, not a rank, not a vote, not a threshold, and not a merge rule. "
            "falsify both cases before deciding. First ask whether the current LLM primary relies "
            "on a broad biomarker, generic comorbidity, weak endpoint, or plausible-but-thin "
            "source bridge. Then ask whether the advisor-surfaced challenger has an independently "
            "coherent source-axis bridge, endpoint fit, and materially stronger visible PGS "
            "evidence. Do not keep the current primary by inertia, and "
            "do not switch because of metadata scale alone. A challenger can beat the current "
            "LLM primary only when it passes both burdens: coherent transfer bridge and stronger "
            "or more endpoint-useful PRS evidence. The current primary wins when the challenger "
            "is mainly larger, newer, broader, more validated, or advisor-surfaced without a "
            "clearer bridge. "
            "Explain the falsification of the losing case and the LLM-led reason for the winner."
        )
    if prompt_mode == "pairwise_adjudicated_review":
        return (
            f"{base} This is a head-to-head adjudication reconciler. pairwise_review_evidence "
            "contains auxiliary LLM arguments from comparing candidate pairs; it is not authority, "
            "not a tally, not a majority decision, and not a rule. First form an independent "
            "case for each candidate from its card: source bridge, endpoint fit, visible PGS "
            "evidence, ancestry/method context, and target-transfer plausibility. Then use the "
            "head-to-head reviews only to find overlooked strengths, contradictions, or weak "
            "claims in those independent cases. Do not select a candidate because it has more "
            "favorable reviews; a candidate can still win when its card-level transfer case is "
            "stronger. Explain the decisive card-level reason and any important head-to-head "
            "conflict."
        )
    if prompt_mode == "signal_literate_review":
        return (
            f"{base} This is a signal-literate reconciler. First set aside candidates whose "
            "source bridge is weak, distant, generic, or unsupported by the provided record. "
            "For the remaining coherent candidates, do not let a closer-looking source label "
            "automatically beat materially stronger PRS evidence. Compare whether the candidate "
            "has endpoint-useful validation, raw PGS performance descriptions, evaluation record "
            "depth, sample context, ancestry portability, method context, and signs that the "
            "signal is PRS-relevant rather than covariate-heavy. A measurement, construct-adjacent, "
            "upstream, or downstream source can win when its bridge is concrete and its PRS "
            "evidence is stronger; a label-like diagnosis can lose when its PRS evidence is "
            "sparse, narrow, or less portable. Do not use candidate order, lane appearances, "
            "record counts, variant counts, source category, tool overlap, or any numeric formula "
            "as the decision. Explain the selected coherent bridge and why the strongest "
            "label-closer or metadata-strong loser does not beat it."
        )
    if prompt_mode == "source_model_symmetric_review":
        return (
            f"{base} This is a symmetric source-then-model reconciler. Review every candidate "
            "from the card text rather than from candidate order, lane provenance, advisor "
            "provenance, incumbent status, or metadata scale. Step one is source-axis bridge: "
            "decide whether each candidate has a coherent direct, measurement, mechanistic, "
            "construct-adjacent, upstream, downstream, or specific proxy bridge to the target. "
            "Weak, distant, overly broad, or generic bridges should not win from larger metadata "
            "alone. Step two is model evidence among candidates with coherent or similarly "
            "defensible bridges: compare endpoint definition, raw PRS performance descriptions, "
            "evaluation records and sample context, ancestry portability, method context, and "
            "whether the visible signal appears PRS-relevant rather than covariate-heavy. A "
            "closer-looking source can lose when its model evidence is sparse or poorly aligned; "
            "a less direct source can win when its bridge remains coherent and its model evidence "
            "is materially stronger. This is not a formula, rank, threshold, vote, source-category "
            "rule, whitelist, blacklist, or case-specific exception. Explain the winning source "
            "bridge, the decisive model evidence, and why the strongest loser does not beat it."
        )
    if prompt_mode == "structured_source_model_review":
        return (
            f"{base} This is a structured source-model review. Review every candidate with the "
            "same qualitative checklist before choosing: source bridge to the target, endpoint "
            "fit, model evidence, ancestry and method portability, and whether visible "
            "performance evidence appears PRS-relevant rather than covariate-heavy. Candidate "
            "order is not evidence, but do not overcorrect toward later cards; later position "
            "is also not evidence. First separate candidates with weak, distant, generic, or "
            "unsupported source bridges from candidates with coherent direct, measurement, "
            "mechanistic, construct-adjacent, upstream, downstream, or specific proxy bridges. "
            "Then compare model evidence only among candidates whose source bridge remains "
            "coherent or similarly defensible. A closer-looking label can lose when its model "
            "evidence is sparse or poorly aligned; a less direct source can win when its bridge "
            "is coherent and its visible model evidence is materially stronger. Do not use "
            "candidate position, lane count, vote count, record count, variant count, source "
            "category, tool overlap, whitelist, blacklist, or any numeric formula as the "
            "decision. Explain the selected candidate against the strongest losing candidate "
            "using the same source-then-model checklist."
        )
    if prompt_mode == "same_source_effect_size_audit_review":
        return (
            f"{base} This is a same-source effect-size audit reconciler. First identify whether "
            "the leading candidates share a source axis, mapped construct, source bundle, or "
            "near-equivalent source trait. When they do, source fit is no longer the deciding "
            "axis; audit model evidence directly. For clinical, binary, case-control, "
            "time-to-event, or liability-like endpoints, odds ratios, hazard ratios, beta "
            "estimates, and similar effect-size fields can be first-class evidence of risk "
            "separation. AUC and R2 remain useful, but do not assume they dominate effect-size "
            "evidence across different endpoints, cohorts, covariate adjustment choices, or "
            "reporting conventions. This is not a formula. Do not choose by formula, threshold, larger metric, sample "
            "count, record count, release date, variant count, candidate order, provenance, "
            "source category, whitelist, blacklist, or trait-specific exception. Ask which "
            "same-source model has the stronger target-portable PRS signal from endpoint "
            "definition, PRS-only versus covariate-heavy evidence when visible, effect-size "
            "fields when relevant, evaluation record context, ancestry context, method context, "
            "and over-specialization risk. If the leading candidates are not source-equivalent, "
            "fall back to source-axis bridge first, then model evidence. Explain the source "
            "equivalence check, the metric comparability audit, and the final LLM-led choice."
        )
    if prompt_mode == "source_axis_precision":
        return (
            f"{base} This is a source-axis review reconciler. First identify the most "
            "specific, coherent source axis using the cross-transfer skill; then choose the best "
            "PGS inside that axis. Do not select a broad proxy that is merely well validated "
            "when a more specific, coherent, target-relevant source axis is available. Use "
            "LLM-harness agreement as primary evidence when source-axis fit is close; "
            "use method, endpoint, ancestry, and visible performance metadata only to resolve close "
            "within-axis or close-source decisions. Explain why the selected source axis is more "
            "target-relevant than the nearest alternatives."
        )
    if prompt_mode == "source_axis_blinded_review":
        return (
            f"{base} This is a source-axis blinded reconciler. First identify the most "
            "specific, coherent source axis using the cross-transfer skill from the visible "
            "target, reported trait, mapped trait, source-bundle, endpoint, method, ancestry, "
            "and release/context fields. Visible PGS performance fields are intentionally "
            "omitted in this pass to reduce cross-source metric anchoring; do not infer weak "
            "model evidence from that omission. Choose the best PGS inside the selected source "
            "axis using endpoint fit, method context, ancestry context, and source-bundle "
            "specificity. Do not select a broad proxy merely because it looks more general, "
            "newer, larger, or familiar. This is not a formula, rank, threshold, vote, "
            "source-category rule, whitelist, blacklist, or case-specific exception. Explain "
            "the winning source bridge and why the strongest alternative source does not beat it."
        )
    return (
        f"{base} Use broad LLM-harness agreement first, then the cross-transfer skill for "
        "source-trait and endpoint fit, then raw tool evidence as a weak auxiliary signal. "
        "Explain conflicts between LLM frontier agreement and biological or metadata evidence."
    )


AGENT_VISIBLE_REVIEW_MODES = {
    "anchor_precision": "anchor_review",
    "anchor_evidence_burden_review": "anchor_evidence_burden_review",
    "anchor_challenger_gate_review": "anchor_challenger_gate_review",
    "anchor_switch_audit_review": "anchor_switch_audit_review",
    "source_axis_champion": "source_axis_champion",
    "source_axis_consensus_guard": "source_axis_consensus_guard",
    "challenger_audit": "challenger_audit",
    "metadata_challenger_review": "metadata_challenger_review",
    "robust_evidence_review": "robust_evidence_review",
    "early_tail_robust_review": "robust_source_evidence_review",
    "tiered_tail_precision_review": "tiered_source_evidence_review",
    "rationale_grounded_review": "rationale_grounded_review",
    "order_debiased_review": "order_debiased_review",
    "advisor_duel_review": "advisor_duel_review",
    "advisor_duel_precision_switch": "advisor_duel_symmetric_review",
    "advisor_challenge_first_review": "advisor_challenge_first_review",
    "advisor_panel_review": "advisor_panel_review",
    "advisor_source_aware_panel_review": "advisor_source_aware_panel_review",
    "harness_convergence_guard_review": "harness_convergence_guard_review",
    "same_source_model_audit_review": "same_source_model_audit_review",
    "source_equivalent_model_challenger_review": "source_equivalent_model_challenger_review",
    "same_source_metric_calibrated_review": "same_source_metric_calibrated_review",
    "binary_effect_calibrated_review": "binary_effect_calibrated_review",
    "evidence_only_early_tail_panel_review": "evidence_only_panel_review",
    "extreme_tail_evidence_panel_review": "evidence_panel_review",
    "expanded_evidence_shortlist_review": "expanded_evidence_shortlist_review",
    "coherent_evidence_decisive_review": "coherent_evidence_decisive_review",
    "bridge_calibrated_evidence_review": "bridge_calibrated_evidence_review",
    "llm_lane_panel_review": "llm_lane_panel_review",
    "llm_early_tail_tiebreak_review": "llm_lane_tiebreak_review",
    "order_perturbation_tiebreak_review": "order_perturbation_tiebreak_review",
    "advisor_contradiction_falsification_review": "advisor_contradiction_falsification_review",
    "pairwise_adjudicated_review": "pairwise_adjudicated_review",
    "signal_literate_review": "signal_literate_review",
    "source_model_symmetric_review": "source_model_symmetric_review",
    "structured_source_model_review": "structured_source_model_review",
    "same_source_effect_size_audit_review": "same_source_effect_size_audit_review",
    "source_axis_precision": "source_axis_review",
    "source_axis_blinded_review": "source_axis_blinded_review",
}


def _agent_visible_review_mode(prompt_mode: str) -> str:
    return AGENT_VISIBLE_REVIEW_MODES.get(prompt_mode, "general_reconciliation_review")


def build_stage_d_evidence_lines(
    *,
    candidate_request_path: Path,
    vote_prediction_paths: list[Path],
    advisor_prediction_paths: list[Path] | None = None,
    model: str = DEFAULT_MODEL,
    top_n: int = 7,
    vote_frontier_limit: int = 12,
    open_targets_evidence_path: Path | None = None,
    genetic_correlation_evidence_path: Path | None = None,
    pairwise_review_evidence_path: Path | None = None,
    prompt_mode: str = "balanced",
    anchor_lane: str = "",
    reasoning_effort: str = "low",
    candidate_order: str = "input",
    include_vote_rationales: bool = False,
    vote_rationale_char_limit: int = 220,
    max_rationales_per_candidate: int = 3,
    max_output_tokens: int = 1200,
    omit_llm_provenance: bool = False,
    performance_mode: str = "full",
) -> list[dict[str, Any]]:
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    if vote_frontier_limit <= 0:
        raise ValueError("vote_frontier_limit must be positive.")
    if max_output_tokens <= 0:
        raise ValueError("max_output_tokens must be positive.")
    if performance_mode not in {"full", "source_only"}:
        raise ValueError("performance_mode must be one of: full, source_only.")

    vote_lane_labels = _agent_visible_lane_labels(vote_prediction_paths, "llm_lane")
    advisor_lane_labels = _agent_visible_lane_labels(advisor_prediction_paths or [], "advisor_lane")
    visible_anchor_lane = vote_lane_labels.get(anchor_lane, "anchor_lane" if anchor_lane else "")

    vote_evidence = _llm_frontier_evidence_by_pgs(
        prediction_paths=vote_prediction_paths,
        frontier_limit=vote_frontier_limit,
        include_rationales=include_vote_rationales,
        rationale_char_limit=vote_rationale_char_limit,
        max_rationales_per_candidate=max_rationales_per_candidate,
        lane_labels_by_stem=vote_lane_labels,
        lane_prefix="llm_lane",
    )
    advisory_evidence = _llm_frontier_evidence_by_pgs(
        prediction_paths=advisor_prediction_paths or [],
        frontier_limit=vote_frontier_limit,
        lane_labels_by_stem=advisor_lane_labels,
        lane_prefix="advisor_lane",
    )
    open_targets_data = _load_optional_json(open_targets_evidence_path)
    genetic_correlation_data = _load_optional_json(genetic_correlation_evidence_path)
    pairwise_review_data = _load_optional_json(pairwise_review_evidence_path)
    if isinstance(pairwise_review_data, dict) and "evidence" in pairwise_review_data:
        pairwise_review_data = pairwise_review_data.get("evidence") or {}

    lines: list[dict[str, Any]] = []
    with candidate_request_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if not raw_line.strip():
                continue
            request_line = json.loads(raw_line)
            inputs = ((request_line.get("body") or {}).get("input") or [])
            if len(inputs) < 2 or not isinstance(inputs[1].get("content"), str):
                continue
            candidate_payload = json.loads(inputs[1]["content"])
            target = candidate_payload.get("target") or {}
            target_id = clean_text(target.get("target_id"))
            if not target_id:
                continue
            cards = []
            for record in (candidate_payload.get("frontier_pgs_records") or [])[:top_n]:
                if not isinstance(record, dict):
                    continue
                pgs_id = clean_text(record.get("pgs_id"))
                if not pgs_id:
                    continue
                cards.append(
                    _stage_d_candidate_card(
                        record=record,
                        llm_evidence=vote_evidence.get(target_id, {}).get(pgs_id)
                        or _empty_llm_frontier_evidence(),
                        advisory_evidence=advisory_evidence.get(target_id, {}).get(pgs_id)
                        or {},
                        open_targets_evidence=_lookup_tool_evidence(open_targets_data, target_id, pgs_id),
                        genetic_correlation_evidence=_lookup_tool_evidence(
                            genetic_correlation_data,
                            target_id,
                            pgs_id,
                        ),
                        pairwise_review_evidence=_lookup_tool_evidence(
                            pairwise_review_data,
                            target_id,
                            pgs_id,
                        ),
                        include_llm_provenance=not omit_llm_provenance,
                        performance_mode=performance_mode,
                    )
                )
            if not cards:
                continue
            cards = _order_stage_d_cards(cards, candidate_order)
            harness_policy = {
                "prompt_mode": _agent_visible_review_mode(prompt_mode),
                "anchor_lane": visible_anchor_lane,
                "candidate_order": candidate_order,
            }
            if performance_mode != "full":
                harness_policy["performance_mode"] = performance_mode
            payload = {
                "schema_version": "cross_optimized.stage_d_evidence.v1",
                "target": target,
                "decision_authority": "llm_final",
                "harness_policy": harness_policy,
                "candidate_evidence_cards": cards,
                "tool_policy": {
                    "open_targets": "Raw overlap evidence when available; use only as one biological clue.",
                    "genetic_correlation": "Raw literature or genetic-correlation evidence when available; use only as one biological clue.",
                },
                "harness_evidence_policy": {
                    "pairwise_reviews": (
                        "Auxiliary LLM head-to-head arguments when available; use only to audit candidate cases, "
                        "not as authority or a selection rule."
                    )
                },
                "instruction": _stage_d_instruction(
                    prompt_mode,
                    visible_anchor_lane,
                    omit_llm_provenance=omit_llm_provenance,
                ),
            }
            if omit_llm_provenance:
                payload["harness_policy"]["llm_provenance"] = "omitted_from_candidate_cards"
            body = _response_body(
                model=model,
                stage="stage_c",
                user_payload=payload,
                schema_name="cross_stage_d_llm_evidence_reconciler",
                schema=STAGE_C_SCHEMA,
                max_output_tokens=max_output_tokens,
                reasoning_effort=reasoning_effort,
            )
            lines.append(_batch_line(f"stageD__{target_id}", body))
    return lines


def _stage_d_audit_instruction(audit_mode: str) -> str:
    base = (
        "Choose primary_pgs_id only from candidate_evidence_cards. You are auditing "
        "a draft_decision from an earlier LLM pass in the same harness. The draft is "
        "not authority, not a vote, and not a target-specific answer. "
        "Use it only as a compact argument to critique. Re-evaluate candidate cards "
        "symmetrically under the cross-transfer skill: source bridge first, then "
        "endpoint fit, PRS evidence, method context, ancestry context, and visible "
        "performance descriptions. Do not use candidate order, vote count, metadata "
        "scale, source category, tool overlap, or any numeric formula as the decision. "
        "Set accepted=true when you return a final primary; use issues to record "
        "uncertainty or draft disagreements."
    )
    if audit_mode == "standard":
        return (
            f"{base} Keep the draft only if its bridge and PGS evidence withstand "
            "the strongest alternative. Switch only when another candidate has a "
            "clearer transfer bridge or materially stronger PGS evidence under an "
            "equally coherent bridge. Explain the selected primary against the "
            "strongest losing candidate."
        )
    if audit_mode == "conservative_switch":
        return (
            f"{base} Start by reconstructing the best case for the draft and the "
            "best case for the strongest alternative. Preserve the draft when the "
            "comparison is ambiguous, when the alternative wins on only one axis, "
            "or when the alternative's bridge is broader, more generic, or mainly "
            "metadata-driven. Switch only when the alternative is at least coherent "
            "on source bridge and clearly stronger on the decisive PGS evidence, or "
            "when the draft's source bridge is visibly weak while the alternative "
            "has a concrete bridge. Do not switch merely because an alternative has "
            "a larger model, newer release, broader validation, or closer-looking "
            "label without a better transfer argument. Explain why the final primary "
            "beats the strongest losing candidate."
        )
    if audit_mode == "dual_draft_adjudication":
        return (
            f"{base} You are given draft_decision and comparison_draft_decision "
            "from two earlier LLM passes in the same harness. Neither draft is "
            "authority. Treat them as two compact arguments to audit against the "
            "candidate cards. When the drafts agree, verify the shared primary but "
            "do not preserve it by inertia if the cards reveal a stronger transfer "
            "case. When the drafts disagree, compare the best source-bridge and "
            "best PGS-evidence argument for each draft primary, then decide the "
            "final primary from candidate_evidence_cards. A switch must be justified "
            "by a better transfer argument, not by draft identity, candidate order, "
            "agreement count, metadata scale, source category, tool overlap, or any "
            "numeric formula. Explain the final primary against the strongest losing "
            "draft or candidate."
        )
    raise ValueError(f"Unsupported audit_mode: {audit_mode}")


def build_stage_d_audit_lines(
    *,
    candidate_request_path: Path,
    draft_prediction_path: Path,
    comparison_draft_prediction_path: Path | None = None,
    vote_prediction_paths: list[Path],
    model: str = DEFAULT_MODEL,
    top_n: int = 8,
    vote_frontier_limit: int = 12,
    reasoning_effort: str = "low",
    candidate_order: str = "pgs_id",
    audit_mode: str = "standard",
    max_output_tokens: int = 1200,
    include_vote_rationales: bool = False,
    vote_rationale_char_limit: int = 180,
    max_rationales_per_candidate: int = 2,
) -> list[dict[str, Any]]:
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    if vote_frontier_limit <= 0:
        raise ValueError("vote_frontier_limit must be positive.")
    if max_output_tokens <= 0:
        raise ValueError("max_output_tokens must be positive.")

    drafts = _draft_decision_by_target(draft_prediction_path)
    comparison_drafts = (
        _draft_decision_by_target(comparison_draft_prediction_path)
        if comparison_draft_prediction_path is not None
        else {}
    )
    vote_lane_labels = _agent_visible_lane_labels(vote_prediction_paths, "llm_lane")
    vote_evidence = _llm_frontier_evidence_by_pgs(
        prediction_paths=vote_prediction_paths,
        frontier_limit=vote_frontier_limit,
        include_rationales=include_vote_rationales,
        rationale_char_limit=vote_rationale_char_limit,
        max_rationales_per_candidate=max_rationales_per_candidate,
        lane_labels_by_stem=vote_lane_labels,
        lane_prefix="llm_lane",
    )
    instruction = _stage_d_audit_instruction(audit_mode)

    lines: list[dict[str, Any]] = []
    with candidate_request_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if not raw_line.strip():
                continue
            request_line = json.loads(raw_line)
            inputs = ((request_line.get("body") or {}).get("input") or [])
            if len(inputs) < 2 or not isinstance(inputs[1].get("content"), str):
                continue
            candidate_payload = json.loads(inputs[1]["content"])
            target = candidate_payload.get("target") or {}
            target_id = clean_text(target.get("target_id"))
            if not target_id:
                continue
            cards = []
            for record in (candidate_payload.get("frontier_pgs_records") or [])[:top_n]:
                if not isinstance(record, dict):
                    continue
                pgs_id = clean_text(record.get("pgs_id"))
                if not pgs_id:
                    continue
                cards.append(
                    _stage_d_candidate_card(
                        record=record,
                        llm_evidence=vote_evidence.get(target_id, {}).get(pgs_id)
                        or _empty_llm_frontier_evidence(),
                        advisory_evidence={},
                        open_targets_evidence=None,
                        genetic_correlation_evidence=None,
                    )
                )
            if not cards:
                continue
            cards = _order_stage_d_cards(cards, candidate_order)
            payload = {
                "schema_version": "cross_optimized.stage_d_audit.v1",
                "target": target,
                "decision_authority": "llm_final",
                "harness_policy": {
                    "prompt_mode": audit_mode,
                    "candidate_order": candidate_order,
                },
                "draft_decision": drafts.get(target_id) or {},
                "comparison_draft_decision": comparison_drafts.get(target_id) or {},
                "candidate_evidence_cards": cards,
                "instruction": instruction,
            }
            body = _response_body(
                model=model,
                stage="stage_c",
                user_payload=payload,
                schema_name="cross_stage_d_llm_draft_audit",
                schema=STAGE_C_SCHEMA,
                max_output_tokens=max_output_tokens,
                reasoning_effort=reasoning_effort,
            )
            lines.append(_batch_line(f"stageD__{target_id}", body))
    return lines


def write_jsonl(lines: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build cross-optimized Batch API JSONL request files.")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--catalog", type=Path, default=DEFAULT_COMPACT_CATALOG_JSON)
    common.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    common.add_argument("--model", default=DEFAULT_MODEL)
    common.add_argument("--out", type=Path, required=True)

    stage_a = sub.add_parser("stage-a", parents=[common])
    stage_a.add_argument("--prompt-candidate-cap", type=int, default=160)
    stage_a.add_argument("--max-dossier-bundles", type=int, default=600)
    stage_a.add_argument("--target-id", action="append", default=[])

    stage_b = sub.add_parser("stage-b", parents=[common])
    stage_b.add_argument("--stage-a-selection", type=Path, required=True)
    stage_b.add_argument("--pgs-per-bundle-cap", type=int, default=32)
    stage_b.add_argument("--retrieval-floor-count", type=int, default=24)
    stage_b.add_argument("--bundle-chunk-size", type=int)
    stage_b.add_argument("--target-id", action="append", default=[])

    stage_c = sub.add_parser("stage-c")
    stage_c.add_argument("--proposals", type=Path, required=True)
    stage_c.add_argument("--catalog", type=Path, default=DEFAULT_COMPACT_CATALOG_JSON)
    stage_c.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    stage_c.add_argument("--model", default=DEFAULT_MODEL)
    stage_c.add_argument("--out", type=Path, required=True)

    stage_c_groups = sub.add_parser("stage-c-groups")
    stage_c_groups.add_argument("--proposals", type=Path, required=True)
    stage_c_groups.add_argument("--catalog", type=Path, default=DEFAULT_COMPACT_CATALOG_JSON)
    stage_c_groups.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    stage_c_groups.add_argument("--model", default=DEFAULT_MODEL)
    stage_c_groups.add_argument("--group-size", type=int, default=48)
    stage_c_groups.add_argument("--out", type=Path, required=True)

    stage_d_evidence = sub.add_parser("stage-d-evidence")
    stage_d_evidence.add_argument("--candidate-request", type=Path, required=True)
    stage_d_evidence.add_argument("--vote-predictions", type=Path, nargs="+", required=True)
    stage_d_evidence.add_argument("--advisor-predictions", type=Path, nargs="*", default=[])
    stage_d_evidence.add_argument("--model", default=DEFAULT_MODEL)
    stage_d_evidence.add_argument("--top-n", type=int, default=7)
    stage_d_evidence.add_argument("--vote-frontier-limit", type=int, default=12)
    stage_d_evidence.add_argument("--open-targets-evidence", type=Path)
    stage_d_evidence.add_argument("--genetic-correlation-evidence", type=Path)
    stage_d_evidence.add_argument("--pairwise-review-evidence", type=Path)
    stage_d_evidence.add_argument("--prompt-mode", default="balanced")
    stage_d_evidence.add_argument("--anchor-lane", default="")
    stage_d_evidence.add_argument("--reasoning-effort", default="low")
    stage_d_evidence.add_argument("--candidate-order", default="input", choices=["input", "reverse_input", "pgs_id"])
    stage_d_evidence.add_argument("--include-vote-rationales", action="store_true")
    stage_d_evidence.add_argument("--vote-rationale-char-limit", type=int, default=220)
    stage_d_evidence.add_argument("--max-rationales-per-candidate", type=int, default=3)
    stage_d_evidence.add_argument("--max-output-tokens", type=int, default=1200)
    stage_d_evidence.add_argument("--omit-llm-provenance", action="store_true")
    stage_d_evidence.add_argument("--performance-mode", default="full", choices=["full", "source_only"])
    stage_d_evidence.add_argument("--out", type=Path, required=True)

    stage_d_audit = sub.add_parser("stage-d-audit")
    stage_d_audit.add_argument("--candidate-request", type=Path, required=True)
    stage_d_audit.add_argument("--draft-predictions", type=Path, required=True)
    stage_d_audit.add_argument("--comparison-draft-predictions", type=Path)
    stage_d_audit.add_argument("--vote-predictions", type=Path, nargs="+", required=True)
    stage_d_audit.add_argument("--model", default=DEFAULT_MODEL)
    stage_d_audit.add_argument("--top-n", type=int, default=8)
    stage_d_audit.add_argument("--vote-frontier-limit", type=int, default=12)
    stage_d_audit.add_argument("--reasoning-effort", default="low")
    stage_d_audit.add_argument("--candidate-order", default="pgs_id", choices=["input", "reverse_input", "pgs_id"])
    stage_d_audit.add_argument(
        "--audit-mode",
        default="standard",
        choices=["standard", "conservative_switch", "dual_draft_adjudication"],
    )
    stage_d_audit.add_argument("--max-output-tokens", type=int, default=1200)
    stage_d_audit.add_argument("--include-vote-rationales", action="store_true")
    stage_d_audit.add_argument("--vote-rationale-char-limit", type=int, default=180)
    stage_d_audit.add_argument("--max-rationales-per-candidate", type=int, default=2)
    stage_d_audit.add_argument("--out", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "stage-a":
        lines = build_stage_a_lines(
            catalog_path=args.catalog,
            targets_path=args.targets,
            model=args.model,
            prompt_candidate_cap=args.prompt_candidate_cap,
            max_dossier_bundles=args.max_dossier_bundles,
            target_ids=set(args.target_id) if args.target_id else None,
        )
    elif args.command == "stage-b":
        lines = build_stage_b_lines(
            stage_a_selection_path=args.stage_a_selection,
            catalog_path=args.catalog,
            targets_path=args.targets,
            model=args.model,
            pgs_per_bundle_cap=args.pgs_per_bundle_cap,
            retrieval_floor_count=args.retrieval_floor_count,
            bundle_chunk_size=args.bundle_chunk_size,
            target_ids=set(args.target_id) if args.target_id else None,
        )
    elif args.command == "stage-c":
        lines = build_stage_c_lines(
            proposals_path=args.proposals,
            catalog_path=args.catalog,
            targets_path=args.targets,
            model=args.model,
        )
    elif args.command == "stage-c-groups":
        lines = build_stage_c_group_lines(
            proposals_path=args.proposals,
            catalog_path=args.catalog,
            targets_path=args.targets,
            model=args.model,
            group_size=args.group_size,
        )
    elif args.command == "stage-d-evidence":
        lines = build_stage_d_evidence_lines(
            candidate_request_path=args.candidate_request,
            vote_prediction_paths=args.vote_predictions,
            advisor_prediction_paths=args.advisor_predictions,
            model=args.model,
            top_n=args.top_n,
            vote_frontier_limit=args.vote_frontier_limit,
            open_targets_evidence_path=args.open_targets_evidence,
            genetic_correlation_evidence_path=args.genetic_correlation_evidence,
            pairwise_review_evidence_path=args.pairwise_review_evidence,
            prompt_mode=args.prompt_mode,
            anchor_lane=args.anchor_lane,
            reasoning_effort=args.reasoning_effort,
            candidate_order=args.candidate_order,
            include_vote_rationales=args.include_vote_rationales,
            vote_rationale_char_limit=args.vote_rationale_char_limit,
            max_rationales_per_candidate=args.max_rationales_per_candidate,
            max_output_tokens=args.max_output_tokens,
            omit_llm_provenance=args.omit_llm_provenance,
            performance_mode=args.performance_mode,
        )
    else:
        lines = build_stage_d_audit_lines(
            candidate_request_path=args.candidate_request,
            draft_prediction_path=args.draft_predictions,
            comparison_draft_prediction_path=args.comparison_draft_predictions,
            vote_prediction_paths=args.vote_predictions,
            model=args.model,
            top_n=args.top_n,
            vote_frontier_limit=args.vote_frontier_limit,
            reasoning_effort=args.reasoning_effort,
            candidate_order=args.candidate_order,
            audit_mode=args.audit_mode,
            max_output_tokens=args.max_output_tokens,
            include_vote_rationales=args.include_vote_rationales,
            vote_rationale_char_limit=args.vote_rationale_char_limit,
            max_rationales_per_candidate=args.max_rationales_per_candidate,
        )

    write_jsonl(lines, args.out)
    print(f"Wrote {len(lines)} batch requests -> {args.out}")


if __name__ == "__main__":
    main()
