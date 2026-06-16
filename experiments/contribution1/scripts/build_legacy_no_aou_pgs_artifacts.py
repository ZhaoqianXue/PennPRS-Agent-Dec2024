"""Build Contribution1 artifacts with the legacy target universe and no-AoU PGS set.

The intended Contribution1 refresh removes PGS models whose training/evaluation
cohorts include All of Us. It should not change the disease/trait target rows
used by Contribution2/Contribution3. This script preserves the legacy rows from
`Genetic_Agent` and filters only PGS columns using the allowed PGS IDs observed
in `Genetic_Agent copy`.

Outputs:
  experiments/contribution1/result/legacy_no_aou_pgs/
    aou_binary/
    aou_extend_trait/
    aou_continuous/
    manifest.json
"""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LEGACY_SOURCE_ROOT = PROJECT_ROOT / "Genetic_Agent" / "result"
COPY_SOURCE_ROOT = PROJECT_ROOT / "Genetic_Agent copy" / "result"
OUT_ROOT = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "legacy_no_aou_pgs"


def _pgs_id_from_column(column: str) -> str:
    text = str(column).strip()
    if text == "trait":
        return ""
    if "__" in text:
        text = text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


def _matrix_pgs_ids(path: Path) -> set[str]:
    header = pd.read_csv(path, nrows=0)
    return {_pgs_id_from_column(col) for col in header.columns[1:] if _pgs_id_from_column(col)}


def _parse_pgs_ids(raw: Any) -> list[str]:
    if raw is None or pd.isna(raw):
        return []
    try:
        value = ast.literal_eval(str(raw))
    except (SyntaxError, ValueError):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _filter_matrix_csv(src: Path, dst: Path, allowed_pgs_ids: set[str]) -> dict[str, int]:
    df = pd.read_csv(src)
    trait_col = df.columns[0]
    keep_columns = [trait_col] + [
        col for col in df.columns[1:] if _pgs_id_from_column(col) in allowed_pgs_ids
    ]
    filtered = df.loc[:, keep_columns]
    dst.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(dst, index=False)
    return {
        "rows": int(filtered.shape[0]),
        "pgs_columns_before": int(df.shape[1] - 1),
        "pgs_columns_after": int(filtered.shape[1] - 1),
        "pgs_columns_removed": int((df.shape[1] - 1) - (filtered.shape[1] - 1)),
    }


def _filter_rank_csv(src: Path, dst: Path, allowed_pgs_ids: set[str]) -> dict[str, int]:
    df = pd.read_csv(src)
    trait_col = df.columns[0]
    rows: list[dict[str, Any]] = []
    max_rank = 0
    for _, row in df.iterrows():
        values = [
            str(value).strip()
            for value in row.iloc[1:].tolist()
            if pd.notna(value) and str(value).strip()
        ]
        kept = [value for value in values if _pgs_id_from_column(value) in allowed_pgs_ids]
        max_rank = max(max_rank, len(kept))
        rows.append({trait_col: row[trait_col], "__kept": kept})

    out_rows: list[dict[str, Any]] = []
    for row in rows:
        kept = row.pop("__kept")
        out = {trait_col: row[trait_col]}
        for idx in range(max_rank):
            out[f"rank_{idx + 1}"] = kept[idx] if idx < len(kept) else None
        out_rows.append(out)

    out_df = pd.DataFrame(out_rows)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(dst, index=False)
    return {
        "rows": int(out_df.shape[0]),
        "rank_columns_after": int(max(0, out_df.shape[1] - 1)),
    }


def _filter_metadata_csv(src: Path, dst: Path, allowed_pgs_ids: set[str]) -> dict[str, int]:
    df = pd.read_csv(src)
    if "pgs_ids" not in df.columns:
        dst.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(dst, index=False)
        return {"rows": int(df.shape[0]), "metadata_pgs_removed": 0}

    removed_total = 0
    filtered_lists: list[list[str]] = []
    for raw in df["pgs_ids"].tolist():
        original = _parse_pgs_ids(raw)
        kept = [pgs_id for pgs_id in original if pgs_id in allowed_pgs_ids]
        removed_total += len(original) - len(kept)
        filtered_lists.append(kept)

    out = df.copy()
    out["pgs_ids"] = [repr(values) for values in filtered_lists]
    counts = [len(values) for values in filtered_lists]
    for col in ["pgs_num", "pgs_api_num", "calc_prs_count"]:
        if col in out.columns:
            out[col] = counts
    if "include_in_analysis" in out.columns:
        original_include = out["include_in_analysis"].fillna(0).astype(int)
        out["include_in_analysis"] = [
            int(include == 1 and count > 0) for include, count in zip(original_include, counts)
        ]

    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dst, index=False)
    return {
        "rows": int(out.shape[0]),
        "metadata_pgs_removed": int(removed_total),
        "rows_with_zero_pgs": int(sum(count == 0 for count in counts)),
    }


def _filter_pgs_table_csv(src: Path, dst: Path, allowed_pgs_ids: set[str]) -> dict[str, int]:
    df = pd.read_csv(src)
    id_col = "PGS_ID" if "PGS_ID" in df.columns else None
    if id_col is None:
        shutil.copy2(src, dst)
        return {"rows": int(df.shape[0]), "rows_after": int(df.shape[0])}
    filtered = df[df[id_col].astype(str).str.strip().isin(allowed_pgs_ids)].copy()
    dst.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(dst, index=False)
    return {"rows": int(df.shape[0]), "rows_after": int(filtered.shape[0])}


def _copy_or_filter_csv(
    src: Path,
    dst: Path,
    allowed_pgs_ids: set[str],
    stats: dict[str, dict[str, int]],
) -> None:
    name = src.name
    if "_rankmatrix" in name or "_selfrankmatrix" in name:
        stats[name] = _filter_rank_csv(src, dst, allowed_pgs_ids)
    elif "matrix" in name:
        stats[name] = _filter_matrix_csv(src, dst, allowed_pgs_ids)
    elif "metadata" in name and "prs_" in name:
        stats[name] = _filter_metadata_csv(src, dst, allowed_pgs_ids)
    elif name == "pgs_glm_features.csv":
        stats[name] = _filter_pgs_table_csv(src, dst, allowed_pgs_ids)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        stats[name] = {"copied": 1}


def _build_dataset(
    label: str,
    legacy_dir: Path,
    out_dir: Path,
    allowed_pgs_ids: set[str],
) -> dict[str, Any]:
    if not legacy_dir.exists():
        raise FileNotFoundError(f"Legacy source directory not found: {legacy_dir}")

    stats: dict[str, dict[str, int]] = {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(legacy_dir.glob("*.csv")):
        _copy_or_filter_csv(src, out_dir / src.name, allowed_pgs_ids, stats)

    return {
        "label": label,
        "legacy_source": str(legacy_dir.relative_to(PROJECT_ROOT)),
        "output_dir": str(out_dir.relative_to(PROJECT_ROOT)),
        "allowed_pgs_ids": len(allowed_pgs_ids),
        "files": stats,
    }


def main() -> None:
    binary_allowed = (
        _matrix_pgs_ids(COPY_SOURCE_ROOT / "aou_icd_260217" / "prs_adjauc_matrix_260217_rootcode.csv")
        | _matrix_pgs_ids(COPY_SOURCE_ROOT / "aou_icd_260217" / "prs_adjauc_matrix_260217_childrencode.csv")
    )
    extend_allowed = _matrix_pgs_ids(
        COPY_SOURCE_ROOT / "aou_nontarget_pgs" / "prs_adjauc_matrix_notarget_pgs_qc.csv"
    )
    continuous_allowed = _matrix_pgs_ids(
        COPY_SOURCE_ROOT / "aou_loinc_260225" / "prs_incrementalr2_matrix_260225_loinccode_qc.csv"
    )

    manifest = {
        "purpose": "Preserve legacy target rows and remove only PGS IDs absent from the Genetic_Agent copy no-AoU PGS refresh.",
        "project_root": str(PROJECT_ROOT),
        "datasets": [
            _build_dataset(
                "aou_binary",
                LEGACY_SOURCE_ROOT / "aou_binary",
                OUT_ROOT / "aou_binary",
                binary_allowed,
            ),
            _build_dataset(
                "aou_extend_trait",
                LEGACY_SOURCE_ROOT / "aou_extend_trait",
                OUT_ROOT / "aou_extend_trait",
                extend_allowed,
            ),
            _build_dataset(
                "aou_continuous",
                LEGACY_SOURCE_ROOT / "aou_continuous",
                OUT_ROOT / "aou_continuous",
                continuous_allowed,
            ),
        ],
    }

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote legacy no-AoU PGS artifacts -> {OUT_ROOT}")
    for dataset in manifest["datasets"]:
        print(f"  - {dataset['label']}: allowed_pgs_ids={dataset['allowed_pgs_ids']}")


if __name__ == "__main__":
    main()
