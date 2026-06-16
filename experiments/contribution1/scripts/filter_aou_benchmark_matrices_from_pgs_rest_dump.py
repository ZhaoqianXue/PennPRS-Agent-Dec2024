"""Regenerate no-AoU benchmark matrices from the PGS Catalog REST dump.

This script treats ``data/pgs_all_metadata/pgs_full_rest_dump.jsonl`` as a
read-only source of truth for PGS Catalog cohort metadata. It rewrites only the
benchmark matrix CSVs under ``experiments/contribution1/result/legacy_no_aou_pgs``
by removing PGS columns whose full REST record mentions All of Us/AoU.

It intentionally does not update rank matrices, metadata tables, recommendation
outputs, figure data, or evaluation summaries.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PGS_REST_DUMP = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_full_rest_dump.jsonl"
SOURCE_ROOT = PROJECT_ROOT / "Genetic_Agent" / "result"
OUT_ROOT = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "legacy_no_aou_pgs"

AOU_PATTERN = re.compile(r"\b(all\s*of\s*us|allofus|aou)\b", re.IGNORECASE)
PGS_ID_PATTERN = re.compile(r"PGS\d{6}")


@dataclass(frozen=True)
class MatrixSpec:
    dataset: str
    filename: str

    @property
    def source_path(self) -> Path:
        return SOURCE_ROOT / self.dataset / self.filename

    @property
    def output_path(self) -> Path:
        return OUT_ROOT / self.dataset / self.filename


MATRIX_SPECS = [
    MatrixSpec("aou_binary", "prs_adjauc_matrix_binary_combined_rootcode.csv"),
    MatrixSpec("aou_binary", "prs_adjauc_matrix_binary_combined_rootcode_qc.csv"),
    MatrixSpec("aou_binary", "prs_adjauc_matrix_binary_combined_childrencode.csv"),
    MatrixSpec("aou_binary", "prs_adjauc_matrix_binary_combined_childrencode_qc.csv"),
    MatrixSpec("aou_extend_trait", "prs_adjauc_matrix_binary_extend.csv"),
    MatrixSpec("aou_extend_trait", "prs_adjauc_matrix_binary_extend_qc.csv"),
    MatrixSpec("aou_continuous", "prs_incrementalr2_matrix_260225_loinccode.csv"),
    MatrixSpec("aou_continuous", "prs_incrementalr2_matrix_260225_loinccode_qc.csv"),
]


def _iter_string_values(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _iter_string_values(child, child_path)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            yield from _iter_string_values(child, f"{path}[{idx}]")
    elif isinstance(value, str):
        yield path, value


def _pgs_id_from_column(column: str) -> str:
    text = str(column).strip()
    if text == "trait":
        return ""
    if "__" in text:
        text = text.rsplit("__", 1)[-1]
    text = text.replace("_hmPOS_GRCh38", "")
    match = PGS_ID_PATTERN.search(text)
    return match.group(0) if match else ""


def load_aou_overlap_pgs_ids() -> tuple[set[str], dict[str, list[dict[str, str]]], set[str]]:
    all_pgs_ids: set[str] = set()
    excluded_pgs_ids: set[str] = set()
    matches_by_pgs: dict[str, list[dict[str, str]]] = {}

    with PGS_REST_DUMP.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            record = json.loads(line)
            pgs_id = str(record.get("pgs_id") or record.get("score", {}).get("id") or "").strip()
            if not pgs_id:
                raise ValueError(f"Missing pgs_id on line {line_number}")
            all_pgs_ids.add(pgs_id)

            matches: list[dict[str, str]] = []
            for path, text in _iter_string_values(record):
                match = AOU_PATTERN.search(text)
                if not match:
                    continue
                matches.append(
                    {
                        "field_path": path,
                        "matched_text": text,
                    }
                )

            if matches:
                excluded_pgs_ids.add(pgs_id)
                matches_by_pgs[pgs_id] = matches

    return excluded_pgs_ids, matches_by_pgs, all_pgs_ids


def filter_matrix(spec: MatrixSpec, excluded_pgs_ids: set[str], all_pgs_ids: set[str]) -> dict[str, Any]:
    if not spec.source_path.exists():
        raise FileNotFoundError(f"Source matrix not found: {spec.source_path}")

    matrix = pd.read_csv(spec.source_path)
    trait_col = matrix.columns[0]

    removed_columns: list[str] = []
    missing_from_dump: list[str] = []
    pgs_columns_before = 0
    non_pgs_columns_preserved: list[str] = []
    keep_columns = [trait_col]

    for column in matrix.columns[1:]:
        pgs_id = _pgs_id_from_column(column)
        if not pgs_id:
            keep_columns.append(column)
            non_pgs_columns_preserved.append(column)
            continue
        pgs_columns_before += 1
        if pgs_id in excluded_pgs_ids:
            removed_columns.append(column)
            continue
        if pgs_id not in all_pgs_ids:
            missing_from_dump.append(column)
            continue
        keep_columns.append(column)

    filtered = matrix.loc[:, keep_columns]
    spec.output_path.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(spec.output_path, index=False)

    return {
        "dataset": spec.dataset,
        "filename": spec.filename,
        "source": str(spec.source_path.relative_to(PROJECT_ROOT)),
        "output": str(spec.output_path.relative_to(PROJECT_ROOT)),
        "rows": int(filtered.shape[0]),
        "pgs_columns_before": pgs_columns_before,
        "pgs_columns_after": pgs_columns_before - len(removed_columns) - len(missing_from_dump),
        "non_pgs_columns_preserved": non_pgs_columns_preserved,
        "aou_overlap_pgs_columns_removed": len(removed_columns),
        "pgs_columns_missing_from_dump_removed": len(missing_from_dump),
        "removed_pgs_ids": sorted({_pgs_id_from_column(column) for column in removed_columns}),
        "missing_from_dump_pgs_ids": sorted({_pgs_id_from_column(column) for column in missing_from_dump}),
    }


def write_exclusion_report(
    matches_by_pgs: dict[str, list[dict[str, str]]],
    used_excluded_ids: set[str],
) -> None:
    report_path = OUT_ROOT / "aou_overlap_exclusion_report.tsv"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["pgs_id", "field_path", "matched_text"],
            delimiter="\t",
        )
        writer.writeheader()
        for pgs_id in sorted(used_excluded_ids):
            for match in matches_by_pgs.get(pgs_id, []):
                writer.writerow(
                    {
                        "pgs_id": pgs_id,
                        "field_path": match["field_path"],
                        "matched_text": match["matched_text"],
                    }
                )


def main() -> None:
    excluded_pgs_ids, matches_by_pgs, all_pgs_ids = load_aou_overlap_pgs_ids()
    stats = [filter_matrix(spec, excluded_pgs_ids, all_pgs_ids) for spec in MATRIX_SPECS]

    used_excluded_ids = {
        pgs_id
        for item in stats
        for pgs_id in item["removed_pgs_ids"]
    }
    write_exclusion_report(matches_by_pgs, used_excluded_ids)

    manifest = {
        "purpose": "Regenerate legacy no-AoU benchmark matrix CSVs by filtering PGS columns whose PGS Catalog REST metadata mentions All of Us/AoU.",
        "pgs_rest_dump": str(PGS_REST_DUMP.relative_to(PROJECT_ROOT)),
        "source_root": str(SOURCE_ROOT.relative_to(PROJECT_ROOT)),
        "output_root": str(OUT_ROOT.relative_to(PROJECT_ROOT)),
        "total_pgs_ids_in_rest_dump": len(all_pgs_ids),
        "total_aou_overlap_pgs_ids_in_rest_dump": len(excluded_pgs_ids),
        "aou_overlap_pgs_ids_used_by_matrices": len(used_excluded_ids),
        "matrices": stats,
        "untouched_outputs": [
            "rank matrices",
            "self-rank matrices",
            "metadata tables",
            "model-ranking summaries",
            "figure data",
            "recommendation/evaluation summaries",
        ],
    }
    manifest_path = OUT_ROOT / "matrix_filter_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "total_pgs_ids_in_rest_dump": len(all_pgs_ids),
                "total_aou_overlap_pgs_ids_in_rest_dump": len(excluded_pgs_ids),
                "aou_overlap_pgs_ids_used_by_matrices": len(used_excluded_ids),
                "matrix_outputs": [
                    {
                        "output": item["output"],
                        "pgs_columns_before": item["pgs_columns_before"],
                        "pgs_columns_after": item["pgs_columns_after"],
                        "aou_overlap_pgs_columns_removed": item[
                            "aou_overlap_pgs_columns_removed"
                        ],
                    }
                    for item in stats
                ],
                "manifest": str(manifest_path.relative_to(PROJECT_ROOT)),
                "exclusion_report": str(
                    (OUT_ROOT / "aou_overlap_exclusion_report.tsv").relative_to(PROJECT_ROOT)
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
