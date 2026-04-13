"""
Regenerate benchmark CSVs and reports in this directory only.

Uses Contribution1 result layout:
  - Type B (self PRS / self AUC): aou_binary (disease adjAUC) + aou_continuous (LOINC metadata + matrix paths)
  - Type A (no self PRS on target): aou_extend_trait (extend adjAUC matrix + trait_case_count_extend ICD list)

Screening: `min_best_split_gap=0` (see `benchmark_config.json`). Other thresholds use `build_benchmark` defaults.

Also writes (same folder):

  - `union_selected_targets.csv` — one row per distinct `input_icd` in B2B ∪ B2C (`selected==True`), with coverage flags
  - `union_selected_icds.json` — sorted list of those ICD codes
  - After `build_benchmark`, target descriptions are overwritten from `icd10cm_root_category_titles.json` (101 ICD-10-CM category titles).
  - Post-hoc **deselection**: (1) ICD blocklist **E86** (dehydration), **L55** (sunburn); (2) label tokens **other**, **unspecified**, **not specified**, **sequelae**, **toxic** (see `_primary_post_hoc_reason`). B2B/B2C `target_selection.csv` and `ground_truth_ranking.csv` are updated accordingly.
  - The union post-filter uses the same primary rules plus **Unsp**, **NEC**, **Oth acute** (see `_union_exclusion_reason`). Markdown reports from `build_benchmark` may still show pre-filter counts unless regenerated.

Does not modify files under cross_list/configs/. Run from repo root:

  python experiments/contribution3/cross_list/benchmark_contrib1_latest/rebuild_outputs.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CONFIGS_DIR = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "configs"
OUT_DIR = Path(__file__).resolve().parent
ICD_CANONICAL_TITLES_PATH = OUT_DIR / "icd10cm_root_category_titles.json"

# Explicit ICD roots dropped after canonical titles (dehydration, sunburn).
POST_HOC_ICD_BLOCKLIST = frozenset({"E86", "L55"})

CONTRIB1 = PROJECT_ROOT / "experiments" / "contribution1" / "result"
AOU_CONTINUOUS = CONTRIB1 / "aou_continuous"
AOU_EXTEND = CONTRIB1 / "aou_extend_trait"


def _load_extend_type_a_matrix() -> pd.DataFrame:
    path = AOU_EXTEND / "prs_adjauc_matrix_binary_extend_qc.csv"
    if not path.exists():
        raise FileNotFoundError(f"Extend trait matrix not found: {path}")
    return pd.read_csv(path, index_col=0)


def _combined_label_text(desc: object, ont: object) -> str:
    d = "" if desc is None or (isinstance(desc, float) and pd.isna(desc)) else str(desc)
    o = "" if ont is None or (isinstance(ont, float) and pd.isna(ont)) else str(ont)
    return " ".join((d + " " + o).lower().split())


def _primary_post_hoc_reason(desc: object, ont: object) -> Optional[str]:
    """
    User-requested post-hoc drops on combined label text (description + ontology).

    Rules: ``other`` (word), ``unspecified`` (word), ``not specified`` (substring),
    ``sequelae`` (word), ``toxic`` (word).
    """
    t = _combined_label_text(desc, ont)
    if re.search(r"\bother\b", t):
        return "contains_other"
    if re.search(r"\bunspecified\b", t):
        return "unspecified"
    if "not specified" in t:
        return "not_specified"
    if re.search(r"\bsequelae\b", t):
        return "sequelae"
    if re.search(r"\btoxic\b", t):
        return "toxic"
    return None


def _union_exclusion_reason(
    input_description: str,
    input_ontology: str,
    input_icd: str = "",
) -> Optional[str]:
    """
    Return a short reason if this union row should be dropped, else None.

    Primary: ICD blocklist, then `_primary_post_hoc_reason`, then Unsp, NEC, Oth acute.
    """
    icd = str(input_icd or "").strip()
    if icd in POST_HOC_ICD_BLOCKLIST:
        return "manual_icd_blocklist"
    r = _primary_post_hoc_reason(input_description, input_ontology)
    if r:
        return r
    t = _combined_label_text(input_description, input_ontology)
    if re.search(r"(?<![a-z])unsp(?![a-z])", t):
        return "Unsp_abbrev"
    if "not elsewhere classified" in t:
        return "nec"
    if re.search(r"\both acute\b", t):
        return "oth_acute"
    return None


def _deselect_benchmark_targets_post_hoc(out_dir: Path) -> None:
    """
    Set selected=False when ICD is blocklisted or `_primary_post_hoc_reason` matches; drop GT rows.
    """
    for sub in ("binary_to_binary", "binary_to_continuous"):
        ts = out_dir / sub / "target_selection.csv"
        if not ts.exists():
            continue
        df = pd.read_csv(ts)
        if "selected" not in df.columns:
            continue
        removed_icds: list[str] = []
        for i in df.index:
            row = df.loc[i]
            if not bool(row.get("selected", False)):
                continue
            icd = str(row.get("input_icd", "")).strip()
            desc = row.get("input_description", "")
            ont = row.get("input_ontology", "")
            if icd in POST_HOC_ICD_BLOCKLIST:
                reason = "manual_blocklist_E86_L55"
            else:
                reason = _primary_post_hoc_reason(desc, ont) or ""
            if not reason:
                continue
            df.at[i, "selected"] = False
            if icd:
                removed_icds.append(icd)
            sr = str(row.get("selection_reason", "") or "")
            tag = f"dropped_post_hoc: {reason}"
            df.at[i, "selection_reason"] = f"{sr}; {tag}" if sr else tag
        df.to_csv(ts, index=False)

        gt = out_dir / sub / "ground_truth_ranking.csv"
        if not gt.exists() or not removed_icds:
            if removed_icds:
                print(f"  {sub}: deselected {len(removed_icds)} target(s) (post-hoc label rules)")
            continue
        gdf = pd.read_csv(gt)
        if "target_icd" not in gdf.columns:
            continue
        bad = set(removed_icds)
        before = len(gdf)
        gdf = gdf[~gdf["target_icd"].astype(str).str.strip().isin(bad)]
        gdf.to_csv(gt, index=False)
        print(
            f"  {sub}: deselected {len(removed_icds)} target(s) (post-hoc label rules); "
            f"ground_truth_ranking {before} -> {len(gdf)} rows"
        )


def _load_canonical_icd_titles(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for k, v in raw.items():
        if k.startswith("_") or k == "_meta":
            continue
        if isinstance(v, str) and v.strip():
            out[str(k).strip()] = v.strip()
    return out


def _apply_canonical_icd_descriptions(out_dir: Path, titles: dict[str, str]) -> None:
    """Overwrite target-side ICD descriptions using icd10cm_root_category_titles.json."""
    if not titles:
        return

    def _patch_csv(csv_path: Path) -> None:
        if not csv_path.exists():
            return
        df = pd.read_csv(csv_path)
        if "input_icd" in df.columns and "input_description" in df.columns:
            icd_col = df["input_icd"].astype(str).str.strip()
            mapped = icd_col.map(titles)
            df["input_description"] = mapped.where(mapped.notna(), df["input_description"])
        if "target_icd" in df.columns and "target_description" in df.columns:
            ticd = df["target_icd"].astype(str).str.strip()
            tmapped = ticd.map(titles)
            df["target_description"] = tmapped.where(tmapped.notna(), df["target_description"])
        df.to_csv(csv_path, index=False)

    for sub in ("binary_to_binary", "binary_to_continuous"):
        for name in ("target_selection.csv", "ground_truth_ranking.csv"):
            _patch_csv(out_dir / sub / name)


def _filter_union_lists(out_dir: Path) -> None:
    """Remove low-information ICD labels from union CSV/JSON; write exclusion manifest."""
    csv_path = out_dir / "union_selected_targets.csv"
    if not csv_path.exists():
        return

    df = pd.read_csv(csv_path)
    reasons: list[str] = []
    for _, row in df.iterrows():
        desc = str(row.get("input_description", "") or "")
        ont = str(row.get("input_ontology", "") or "")
        icd = str(row.get("input_icd", "") or "")
        r = _union_exclusion_reason(desc, ont, icd)
        reasons.append(r or "")

    df["_exclude"] = reasons
    excluded = df[df["_exclude"] != ""].copy()
    kept = df[df["_exclude"] == ""].drop(columns=["_exclude"])

    excluded = excluded.rename(columns={"_exclude": "exclusion_reason"})
    excluded_path = out_dir / "union_excluded_targets.csv"
    excluded[["input_icd", "exclusion_reason", "coverage", "input_description", "input_ontology"]].to_csv(
        excluded_path, index=False
    )

    ex_icds = sorted(excluded["input_icd"].astype(str).str.strip().unique().tolist())
    ex_records = excluded[["input_icd", "exclusion_reason"]].drop_duplicates("input_icd").to_dict("records")
    (out_dir / "union_excluded_icds.json").write_text(json.dumps(ex_records, indent=2) + "\n", encoding="utf-8")

    kept.to_csv(csv_path, index=False)
    kept_icds = sorted(kept["input_icd"].astype(str).str.strip().tolist())
    (out_dir / "union_selected_icds.json").write_text(json.dumps(kept_icds, indent=2) + "\n", encoding="utf-8")

    print(
        f"Union filter: kept {len(kept_icds)} ICDs, excluded {len(ex_icds)} "
        f"(see {excluded_path.name})"
    )


def _load_extend_type_a_icds() -> set[str]:
    path = AOU_EXTEND / "trait_case_count_extend.csv"
    if not path.exists():
        raise FileNotFoundError(f"Extend trait case count not found: {path}")
    traits = pd.read_csv(path)
    return set(traits["icd"].astype(str).str.strip())


def _write_union_selected_list(out_dir: Path) -> None:
    """Write B2B ∪ B2C selected target ICD list at the benchmark root."""
    p2b = out_dir / "binary_to_binary" / "target_selection.csv"
    p2c = out_dir / "binary_to_continuous" / "target_selection.csv"
    if not p2b.exists() or not p2c.exists():
        return

    b2b = pd.read_csv(p2b)
    b2c = pd.read_csv(p2c)
    if "selected" not in b2b.columns or "selected" not in b2c.columns:
        return

    sb = b2b[b2b["selected"].fillna(False).astype(bool)].copy()
    sc = b2c[b2c["selected"].fillna(False).astype(bool)].copy()

    def _icd_key(s: object) -> str:
        return str(s).strip()

    sb["input_icd"] = sb["input_icd"].map(_icd_key)
    sc["input_icd"] = sc["input_icd"].map(_icd_key)

    ids_b = set(sb["input_icd"])
    ids_c = set(sc["input_icd"])
    union_icds = sorted(ids_b | ids_c)

    rows: list[dict[str, object]] = []
    for icd in union_icds:
        row_b = sb[sb["input_icd"] == icd]
        row_c = sc[sc["input_icd"] == icd]
        in_b = not row_b.empty
        in_c = not row_c.empty
        if in_b and in_c:
            coverage = "both"
        elif in_b:
            coverage = "b2b_only"
        else:
            coverage = "b2c_only"

        def _cell(series: pd.Series, key: str) -> str:
            if key not in series.index:
                return ""
            v = series.get(key)
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return ""
            t = str(v).strip()
            return "" if t.lower() == "nan" else t

        rbo = row_b.iloc[0] if in_b else None
        rco = row_c.iloc[0] if in_c else None

        ont = _cell(rbo, "input_ontology") if rbo is not None else ""
        desc = _cell(rbo, "input_description") if rbo is not None else ""
        if not ont and rco is not None:
            ont = _cell(rco, "input_ontology")
        if not desc and rco is not None:
            desc = _cell(rco, "input_description")

        it_b = _cell(rbo, "input_type") if rbo is not None else ""
        it_c = _cell(rco, "input_type") if rco is not None else ""

        rows.append({
            "input_icd": icd,
            "coverage": coverage,
            "selected_binary_to_binary": in_b,
            "selected_binary_to_continuous": in_c,
            "input_type_b2b": it_b,
            "input_type_b2c": it_c,
            "input_ontology": ont,
            "input_description": desc,
        })

    union_df = pd.DataFrame(rows)
    union_path = out_dir / "union_selected_targets.csv"
    union_df.to_csv(union_path, index=False)

    json_path = out_dir / "union_selected_icds.json"
    json_path.write_text(json.dumps(union_icds, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(union_icds)} union ICDs to {union_path.name} and {json_path.name}")


def _patch_reports_text(text: str) -> str:
    """Align wording with actual data sources (extend_trait vs legacy nontarget_pgs)."""
    return (
        text.replace("contribution1/aou_nontarget_pgs", "contribution1/result/aou_extend_trait")
        .replace("`aou_nontarget_pgs`", "`aou_extend_trait`")
        .replace("nontarget_pgs", "extend_trait")
    )


def main() -> None:
    sys.path.insert(0, str(CONFIGS_DIR))
    import build_cross_list as bcl  # noqa: E402
    import build_benchmark as bb  # noqa: E402

    # Type B continuous: use refreshed continuous outputs under contribution1/result/aou_continuous
    bcl.CONTRIB1_LOINC_RESULT_DIR = AOU_CONTINUOUS

    # Type A: extend-trait universe (targets without self PRS in primary benchmark)
    bb.load_nontarget_type_a_matrix = _load_extend_type_a_matrix
    bb.load_nontarget_type_a_icds = _load_extend_type_a_icds

    argv_backup = sys.argv[:]
    try:
        sys.argv = [
            "build_benchmark.py",
            "--output-benchmark-root",
            str(OUT_DIR),
            "--min-best-split-gap",
            "0",
        ]
        bb.main()
    finally:
        sys.argv = argv_backup

    titles = _load_canonical_icd_titles(ICD_CANONICAL_TITLES_PATH)
    _apply_canonical_icd_descriptions(OUT_DIR, titles)
    if titles:
        print(f"Applied {len(titles)} canonical ICD category titles from {ICD_CANONICAL_TITLES_PATH.name}")

    print(
        "Post-hoc deselect: ICD blocklist E86/L55 | other | unspecified | not specified | "
        "sequelae | toxic (description + ontology)..."
    )
    _deselect_benchmark_targets_post_hoc(OUT_DIR)

    # Fix target_source label for Type A rows (pipeline still emits legacy string)
    for sub in ("binary_to_binary", "binary_to_continuous"):
        for name in ("target_selection.csv", "ground_truth_ranking.csv"):
            p = OUT_DIR / sub / name
            if not p.exists():
                continue
            txt = p.read_text(encoding="utf-8")
            txt = txt.replace("nontarget_pgs", "extend_trait")
            p.write_text(txt, encoding="utf-8")

    for name in (
        "benchmark_report_type_a.md",
        "benchmark_report_type_b.md",
        "benchmark_report_all_target_trait.md",
    ):
        p = OUT_DIR / name
        if p.exists():
            p.write_text(_patch_reports_text(p.read_text(encoding="utf-8")), encoding="utf-8")

    cfg = OUT_DIR / "benchmark_config.json"
    if cfg.exists():
        meta = json.loads(cfg.read_text(encoding="utf-8"))
        meta["type_a_source"] = "aou_extend_trait"
        meta["type_b_binary_matrix"] = "contribution1/result/aou_binary"
        meta["type_b_continuous_loinc_dir"] = "contribution1/result/aou_continuous"
        cfg.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    _write_union_selected_list(OUT_DIR)
    _filter_union_lists(OUT_DIR)

    if cfg.exists():
        meta = json.loads(cfg.read_text(encoding="utf-8"))
        union_path = OUT_DIR / "union_selected_icds.json"
        if union_path.exists():
            meta["union_selected_icd_count"] = len(json.loads(union_path.read_text(encoding="utf-8")))
            ex_path = OUT_DIR / "union_excluded_icds.json"
            if ex_path.exists():
                meta["union_excluded_icd_count"] = len(json.loads(ex_path.read_text(encoding="utf-8")))
        cfg.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Done. Outputs under {OUT_DIR}")


if __name__ == "__main__":
    main()
