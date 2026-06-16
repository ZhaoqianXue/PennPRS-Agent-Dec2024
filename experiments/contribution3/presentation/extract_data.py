"""
Extract per Cross Trait AUC distribution for unified transfer runs (see deck: Cross Trait).

Filters targets by *selected_bundle_rank* (global competition rank of the agent's
primary Cross Trait; CSV column name unchanged) — default: rank <= 5 (not "oracle rank == 1 only").

Writes:
  - presentation_data.json
  - data.js (const PRESENTATION_DATA = ...)

Usage (from repo root):
  python experiments/contribution3/presentation/extract_data.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSFER_RUNS = PROJECT_ROOT / "experiments" / "contribution3" / "transfer" / "runs" / "tool_calling_agent"
BUNDLE_INDEX_JSON = TRANSFER_RUNS / "trait_bundle_index.json"
RUN_DIR_NAME = "all-tools__paired80_legacy_no_aou_tuned_HO_breadth_20260509_w20"
EVAL_DIR_NAME = f"evaluation__{RUN_DIR_NAME.split('__', 1)[1]}"  # mirrors the run timestamp
# Run and eval dirs are nested under the retained ablation parent.
RUN_PARENT_SUBDIR = "ablation__no_all_tools_tuned_breadth"
RESULTS_JSON = TRANSFER_RUNS / "unified" / RUN_PARENT_SUBDIR / RUN_DIR_NAME / "results.json"
DOSSIER_JSON = TRANSFER_RUNS / "unified" / "candidate_dossiers.json"
BENCHMARK_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_contrib1_latest"
)
UNION_TARGETS_CSV = BENCHMARK_DIR / "union_selected_targets.csv"
B2B_SELECTION_CSV = BENCHMARK_DIR / "binary_to_binary" / "target_selection.csv"
B2C_SELECTION_CSV = BENCHMARK_DIR / "binary_to_continuous" / "target_selection.csv"
EVAL_DETAIL_CSV = (
    TRANSFER_RUNS / "unified" / RUN_PARENT_SUBDIR / EVAL_DIR_NAME / "all-tools__end_to_end_eval_detail.csv"
)
PGS_METADATA_CSV = PROJECT_ROOT / "experiments" / "contribution1" / "disease_preprocess" / "pgs_metadata_260217.csv"
OUT_DIR = Path(__file__).resolve().parent
OUT_JSON = OUT_DIR / "presentation_data.json"
OUT_JS = OUT_DIR / "data.js"

PRS_TOP_N = 100  # show top-N PGS models per target in PRS model level view

# Presentation cohort: include the full benchmark — set rank filter wide open
# and clear the curatorial exclusion list so all 80 targets render.
MAX_SELECTED_RANK_INCLUSIVE = 10**9
RUN_LABEL = RUN_DIR_NAME

# Targets excluded from the presentation (weak biological rationale or niche phenotype).
# Empty = include everything; was {"K02", "K04", "N65", "L05"} in the curated cohort.
EXCLUDED_TARGET_IDS: set[str] = set()


def _load_evaluate_module():
    path = PROJECT_ROOT / "experiments" / "contribution3" / "transfer" / "eval" / "evaluate_end_to_end.py"
    spec = importlib.util.spec_from_file_location("evaluate_end_to_end", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _load_union_input_type_map() -> dict[str, str]:
    """Map ICD -> 'A' or 'B' for card styling when union_selected_targets.csv exists."""
    if not UNION_TARGETS_CSV.exists():
        return {}
    u = pd.read_csv(UNION_TARGETS_CSV)
    if "input_icd" not in u.columns:
        return {}
    out: dict[str, str] = {}
    for _, r in u.iterrows():
        icd = str(r["input_icd"]).strip()
        it_b = str(r.get("input_type_b2b", "") or "").strip()
        it_c = str(r.get("input_type_b2c", "") or "").strip()
        # Benchmark tables use "Type A" / "Type B" style strings.
        is_b = ("Type B" in it_b) or ("Type B" in it_c) or (it_b.upper() == "B") or (it_c.upper() == "B")
        out[icd] = "B" if is_b else "A"
    return out


def _load_self_best_maps() -> tuple[dict[str, float], dict[str, str]]:
    """Return (icd->self_best_auc, icd->self_best_pgs) for Type B targets."""
    auc_map: dict[str, float] = {}
    pgs_map: dict[str, str] = {}
    for csv_path in [B2B_SELECTION_CSV, B2C_SELECTION_CSV]:
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path)
        if "input_icd" not in df.columns or "self_best_auc" not in df.columns:
            continue
        for _, r in df.iterrows():
            icd = str(r["input_icd"]).strip()
            val = r["self_best_auc"]
            pgs = str(r.get("self_best_pgs", "") or "").strip()
            if pd.notna(val) and icd not in auc_map:
                auc_map[icd] = round(float(val), 6)
            if pgs and icd not in pgs_map:
                pgs_map[icd] = pgs
    return auc_map, pgs_map


def _load_pgs_n_cases_map() -> dict[str, int | None]:
    """Map pgs_id -> num_training_cases (None if missing)."""
    if not PGS_METADATA_CSV.exists():
        return {}
    df = pd.read_csv(PGS_METADATA_CSV, usecols=["PGS_ID", "num_training_cases"])
    out: dict[str, int | None] = {}
    for _, r in df.iterrows():
        pgs = str(r["PGS_ID"]).strip()
        val = r["num_training_cases"]
        out[pgs] = int(val) if pd.notna(val) and val > 0 else None
    return out


def _as_int(v):
    return int(v) if pd.notna(v) and v > 0 else None


def _as_text(v):
    if pd.isna(v):
        return None
    t = str(v).strip()
    return t if t and t.lower() != "nan" else None


def _load_pgs_metadata_map() -> dict[str, dict]:
    """Map pgs_id -> GWAS-sample metadata for the tooltip.

    Layered, first-wins: Contribution1's curated binary + measurement CSVs
    (which use a uniform schema) cover ~3060 / 3196 PGS in the contribution3
    matrix; the remaining ~140 PGS fall back to the upstream PGS Catalog dump
    (`data/pgs_all_metadata/`) so every bar in the chart has hover info.
    """
    out: dict[str, dict] = {}

    GENETIC_AGENT_COLS = [
        "PGS_ID",
        "num_training_cases",
        "num_training_controls",
        "num_training_sample",
        "training_ancestry",
        "training_method",
        "training_cohort",
        "num_variant",
    ]

    def _add_genetic_agent_csv(path: Path) -> None:
        if not path.exists():
            return
        df = pd.read_csv(path, usecols=lambda c: c in GENETIC_AGENT_COLS)
        for _, r in df.iterrows():
            pgs = str(r["PGS_ID"]).strip()
            if pgs in out:
                continue
            out[pgs] = {
                "n_cases":    _as_int(r.get("num_training_cases")),
                "n_controls": _as_int(r.get("num_training_controls")),
                "n_total":    _as_int(r.get("num_training_sample")),
                "n_variant":  _as_int(r.get("num_variant")),
                "ancestry":   _as_text(r.get("training_ancestry")),
                "method":     _as_text(r.get("training_method")),
                "cohort":     _as_text(r.get("training_cohort")),
            }

    # Layer 1: binary disease (current source).
    _add_genetic_agent_csv(PGS_METADATA_CSV)
    # Layer 2: continuous-measurement traits — same schema, sibling directory.
    _add_genetic_agent_csv(
        PROJECT_ROOT / "experiments" / "contribution1" / "measurement_preprocess" / "pgs_metadata_260225.csv"
    )

    # Layer 3: PGS Catalog dump — only used to fill PGS that the curated CSVs
    # don't cover. We never overwrite curated entries. Score-development data
    # gives training-side counts; the scores file gives variant count + method.
    pgs_dir = PROJECT_ROOT / "data" / "pgs_all_metadata"
    scores_csv = pgs_dir / "pgs_all_metadata_scores.csv"
    dev_csv = pgs_dir / "pgs_all_metadata_score_development_samples.csv"
    if scores_csv.exists() and dev_csv.exists():
        scores_df = pd.read_csv(scores_csv, low_memory=False)
        dev_df = pd.read_csv(dev_csv, low_memory=False)
        scores_lookup = scores_df.set_index("Polygenic Score (PGS) ID").to_dict("index")
        # Prefer "Score Development/Training" row; fall back to first GWAS row.
        train_df = dev_df[dev_df["Stage of PGS Development"] == "Score Development/Training"]
        gwas_df = dev_df[dev_df["Stage of PGS Development"] == "Source of Variant Associations (GWAS)"]
        train_first = train_df.groupby("Polygenic Score (PGS) ID", sort=False).first()
        gwas_first = gwas_df.groupby("Polygenic Score (PGS) ID", sort=False).first()
        all_pgs = set(scores_lookup.keys())
        for pgs in all_pgs:
            if pgs in out:
                continue
            sample_row = (
                train_first.loc[pgs] if pgs in train_first.index
                else (gwas_first.loc[pgs] if pgs in gwas_first.index else None)
            )
            scores_row = scores_lookup.get(pgs, {})
            out[pgs] = {
                "n_cases":    _as_int(sample_row.get("Number of Cases")) if sample_row is not None else None,
                "n_controls": _as_int(sample_row.get("Number of Controls")) if sample_row is not None else None,
                "n_total":    _as_int(sample_row.get("Number of Individuals")) if sample_row is not None else None,
                "n_variant":  _as_int(scores_row.get("Number of Variants")),
                "ancestry":   _as_text(sample_row.get("Broad Ancestry Category")) if sample_row is not None else None,
                "method":     _as_text(scores_row.get("PGS Development Method")),
                "cohort":     _as_text(sample_row.get("Cohort(s)")) if sample_row is not None else None,
            }

    return out


def _load_eval_detail() -> dict[str, dict]:
    """Map target_id -> eval detail row (recommended_model_id, benchmark_top_model_id, etc.)"""
    if not EVAL_DETAIL_CSV.exists():
        return {}
    df = pd.read_csv(EVAL_DETAIL_CSV)
    out: dict[str, dict] = {}
    for _, r in df.iterrows():
        tid = str(r["target_id"]).strip()
        out[tid] = {
            "recommended_model_id": str(r.get("recommended_model_id", "") or "").strip(),
            "benchmark_top_model_id": str(r.get("benchmark_top_model_id", "") or "").strip(),
            "selected_model_auc": float(r["selected_model_auc"]) if pd.notna(r.get("selected_model_auc")) else None,
            "selected_model_rank": int(r["selected_model_rank"]) if pd.notna(r.get("selected_model_rank")) else None,
            "selected_model_gpr": float(r["selected_model_gpr"]) if pd.notna(r.get("selected_model_gpr")) else None,
        }
    return out


def main() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    bundles = json.loads(BUNDLE_INDEX_JSON.read_text("utf-8"))
    bundle_type_map: dict[str, str] = {}
    bundle_label_map: dict[str, str] = {}
    pgs_to_bundle: dict[str, str] = {}  # pgs_id -> bundle_id
    for b in bundles:
        bid = b["bundle_id"]
        bundle_type_map[bid] = b.get("bundle_type", "unknown")
        bundle_label_map[bid] = b.get("canonical_label", bid)
        for pgs in b.get("candidate_pgs_ids") or []:
            pgs_to_bundle[pgs] = bid

    # Load per-target target metadata (incl. aliases for self-like detection)
    # from results.json — the new run format no longer ships a precomputed
    # shortlist_recall.csv, so we derive selected_bundle_rank and the
    # transfer-eligible global oracle inline from the AUC matrix.
    raw_results = json.loads(RESULTS_JSON.read_text("utf-8"))
    target_meta_by_id: dict[str, dict] = {}
    for r in raw_results:
        tgt = r.get("target") or {}
        tid = str(tgt.get("target_id") or "").strip()
        if tid:
            target_meta_by_id[tid] = tgt

    # Per-target detail lives in the eval CSV: matched_bundle_id, matched_cross_trait,
    # target_source, input_type, plus the PRS-level recommended/oracle/AUC fields.
    eval_df = pd.read_csv(EVAL_DETAIL_CSV)
    n_total_eval = len(eval_df)
    print(f"Run {RUN_LABEL}: eval CSV has {n_total_eval} targets, results.json has {len(raw_results)}")

    input_type_map = _load_union_input_type_map()
    self_best_auc_map, self_best_pgs_map = _load_self_best_maps()
    eval_detail_map = _load_eval_detail()
    pgs_n_cases_map = _load_pgs_n_cases_map()
    pgs_metadata_map = _load_pgs_metadata_map()
    print(f"Loaded self_best_auc for {len(self_best_auc_map)} ICDs")
    print(f"Loaded eval detail for {len(eval_detail_map)} targets")
    print(f"Loaded num_training_cases for {sum(1 for v in pgs_n_cases_map.values() if v is not None)} PGS models")
    if input_type_map:
        print(f"Loaded input Type A/B map for {len(input_type_map)} ICDs from {UNION_TARGETS_CSV.name}")
    else:
        print("No union_selected_targets.csv — defaulting all cards to Type A styling")

    dossiers = json.loads(Path(DOSSIER_JSON).read_text("utf-8"))
    dossier_by_target: dict[str, list] = {}
    for d in dossiers:
        tid = str(d["target"]["target_id"]).strip()
        dossier_by_target[tid] = d["candidates"]

    e2e = _load_evaluate_module()

    # Lazy import — pulled in here so a missing thefuzz install fails loudly
    # at extract time rather than during construction of the constants block.
    from experiments.contribution3.transfer.common import (
        TargetTraitQuery,
        is_self_like_bundle,
        load_trait_bundle_index,
    )
    bundle_objs = load_trait_bundle_index(BUNDLE_INDEX_JSON)
    bundle_obj_by_id = {b.bundle_id: b for b in bundle_objs}

    results = []
    skipped_excluded = 0
    skipped_no_match = 0
    skipped_rank = 0
    for _, row in eval_df.iterrows():
        tid = str(row["target_id"]).strip()
        if tid in EXCLUDED_TARGET_IDS:
            skipped_excluded += 1
            continue

        matched_bid_raw = row.get("matched_bundle_id")
        matched_bid = str(matched_bid_raw).strip() if pd.notna(matched_bid_raw) else ""
        if not matched_bid or matched_bid.lower() == "nan":
            skipped_no_match += 1
            continue

        target_source = str(row["target_source"]).strip()
        target_desc = str(row.get("target_description", "") or "").strip() or tid
        matched_cross_trait_raw = row.get("matched_cross_trait")
        matched_cross_trait = (
            str(matched_cross_trait_raw).strip()
            if pd.notna(matched_cross_trait_raw) and str(matched_cross_trait_raw).strip()
            else bundle_label_map.get(matched_bid, matched_bid)
        )

        # Authoritative input_type from eval CSV; fall back to union map.
        input_type_raw = str(row.get("input_type", "") or "").strip()
        input_type = input_type_raw or input_type_map.get(tid, "A")

        try:
            _, _, auc_by_id = e2e._build_full_matrix_ranking(tid, target_source)
        except Exception as exc:
            print(f"  skip {tid}: matrix error: {exc}")
            continue

        self_pgs = self_best_pgs_map.get(tid)  # None for Type A

        covered_prs: set[str] = set()
        bars: list[dict] = []
        for b in bundles:
            bid = b["bundle_id"]
            pgs_list = b.get("candidate_pgs_ids") or []
            auc_pairs = [(p, auc_by_id[p]) for p in pgs_list if p in auc_by_id]
            if not auc_pairs:
                continue
            for p, _ in auc_pairs:
                covered_prs.add(p)
            is_self = bool(self_pgs and self_pgs in pgs_list)
            aucs_sorted = sorted(v for _, v in auc_pairs)
            n = len(aucs_sorted)
            mean_auc = sum(aucs_sorted) / n
            median_auc = aucs_sorted[n // 2] if n % 2 == 1 else (aucs_sorted[n // 2 - 1] + aucs_sorted[n // 2]) / 2
            max_pgs = max(auc_pairs, key=lambda x: x[1])[0]
            bars.append(
                {
                    "bundle_id": bid,
                    "label": bundle_label_map.get(bid, bid),
                    "bundle_type": bundle_type_map.get(bid, "unknown"),
                    "max_auc": round(max(aucs_sorted), 6),
                    "min_auc": round(min(aucs_sorted), 6),
                    "mean_auc": round(mean_auc, 6),
                    "median_auc": round(median_auc, 6),
                    "n_models_hit": n,
                    "is_selected": bid == matched_bid,
                    "is_oracle": False,  # filled in after we resolve the global oracle
                    "is_self": is_self,
                    "max_auc_pgs_id": max_pgs,
                    "max_auc_n_cases": pgs_n_cases_map.get(max_pgs),
                }
            )

        bars.sort(key=lambda x: (-x["max_auc"], x["bundle_id"]))

        # Resolve transfer-eligible global oracle = best non-self-like bundle.
        # Mirrors the deleted shortlist_recall._oracle_bundle helper so the
        # new flow reproduces the same oracle/rank semantics as the old CSV.
        target_meta = target_meta_by_id.get(tid, {})
        target_query = TargetTraitQuery(
            target_id=tid,
            target_code=str(target_meta.get("target_code", tid) or tid),
            target_label=str(target_meta.get("target_label", target_desc) or target_desc),
            target_type=str(target_meta.get("target_type", "binary") or "binary"),
            aliases=list(target_meta.get("aliases") or []),
        )
        oracle_bid = ""
        oracle_label = ""
        oracle_rank = None
        for i, b in enumerate(bars):
            bundle_obj = bundle_obj_by_id.get(b["bundle_id"])
            if bundle_obj is None or is_self_like_bundle(target_query, bundle_obj):
                continue
            oracle_bid = b["bundle_id"]
            oracle_label = b["label"]
            oracle_rank = i + 1
            b["is_oracle"] = True
            break

        # Selected bundle's competition rank — used for cohort filtering.
        sel_rank = None
        for i, b in enumerate(bars):
            if b["bundle_id"] == matched_bid:
                sel_rank = i + 1
                break
        if sel_rank is None or sel_rank > MAX_SELECTED_RANK_INCLUSIVE:
            skipped_rank += 1
            continue

        # Full ranking for presentation "full view" toggle (preview uses top 50 + extras).
        bars_full = [dict(b) for b in bars]

        top_bars = bars[:50]
        top_ids = {b["bundle_id"] for b in top_bars}
        for b in bars[50:]:
            if b["is_selected"] or b["is_oracle"] or b["is_self"]:
                if b["bundle_id"] not in top_ids:
                    top_bars.append(b)
        top_bars.sort(key=lambda x: (-x["max_auc"], x["bundle_id"]))
        bars = top_bars

        # ── PRS model level bars ───────────────────────────────────────
        eval_row = eval_detail_map.get(tid, {})
        recommended_pgs = eval_row.get("recommended_model_id", "")
        oracle_pgs = eval_row.get("benchmark_top_model_id", "")

        prs_bars_all: list[dict] = []
        for pgs_id, auc_val in auc_by_id.items():
            bid = pgs_to_bundle.get(pgs_id, "")
            prs_bars_all.append({
                "pgs_id": pgs_id,
                "label": pgs_id,
                "bundle_id": bid,
                "bundle_label": bundle_label_map.get(bid, ""),
                "bundle_type": bundle_type_map.get(bid, "unknown"),
                "auc": round(auc_val, 6),
                "is_recommended": pgs_id == recommended_pgs,
                "is_oracle": pgs_id == oracle_pgs,
            })
        prs_bars_all.sort(key=lambda x: -x["auc"])
        prs_bars_full = [dict(b) for b in prs_bars_all]

        # top N, always keeping recommended + oracle
        prs_top = prs_bars_all[:PRS_TOP_N]
        top_pgs_ids = {b["pgs_id"] for b in prs_top}
        for b in prs_bars_all[PRS_TOP_N:]:
            if b["is_recommended"] or b["is_oracle"]:
                if b["pgs_id"] not in top_pgs_ids:
                    prs_top.append(b)
        prs_top.sort(key=lambda x: -x["auc"])

        shortlist_candidates = []
        for c in dossier_by_target.get(tid, [])[:15]:
            shortlist_candidates.append(
                {
                    "bundle_id": c["bundle_id"],
                    "label": c["canonical_label"],
                    "bundle_type": c.get("bundle_type", "unknown"),
                    "n_models": c.get("n_models", 0),
                }
            )

        confidence_raw = row.get("status")
        confidence = str(confidence_raw).strip() if pd.notna(confidence_raw) else "ok"

        results.append(
            {
                "target_id": tid,
                "target_label": target_desc,
                "input_type": input_type,
                "target_source": target_source,
                "matched_bundle_id": matched_bid,
                "matched_cross_trait": matched_cross_trait,
                "selected_bundle_rank": sel_rank,
                "oracle_bundle_id": oracle_bid,
                "oracle_label": oracle_label,
                "oracle_rank": oracle_rank,
                "primary_equals_oracle": matched_bid == oracle_bid,
                "benchmark_top_auc": None,
                "self_best_auc": self_best_auc_map.get(tid),
                "confidence": confidence,
                "bars": bars,
                "bars_full": bars_full,
                "shortlist_candidates": shortlist_candidates,
                "recommended_model_id": recommended_pgs,
                "oracle_model_id": oracle_pgs,
                "selected_model_auc": eval_row.get("selected_model_auc"),
                "selected_model_rank": eval_row.get("selected_model_rank"),
                "selected_model_gpr": eval_row.get("selected_model_gpr"),
                "prs_bars": prs_top,
                "prs_bars_full": prs_bars_full,
            }
        )
        print(f"  {tid}: rank={sel_rank}, {len(bars)} Cross Trait bars")

    print(
        f"\nKept {len(results)} targets (excluded={skipped_excluded}, "
        f"no_match={skipped_no_match}, rank>{MAX_SELECTED_RANK_INCLUSIVE}={skipped_rank})"
    )
    results.sort(key=lambda x: (x["input_type"], x["target_id"]))

    out = {
        "generated": RUN_LABEL,
        "results_json": str(RESULTS_JSON.relative_to(PROJECT_ROOT)),
        "filter": f"selected_bundle_rank <= {MAX_SELECTED_RANK_INCLUSIVE}",
        "n_targets_total_benchmark": int(n_total_eval),
        "n_targets": len(results),
        "targets": results,
        # Shared lookup keyed by PGS_ID; the frontend reads it for hover tooltips
        # (GWAS cases/controls/ancestry/method/cohort) instead of duplicating the
        # fields across every bar of every target.
        "pgs_metadata": pgs_metadata_map,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), "utf-8")
    OUT_JS.write_text(
        "const PRESENTATION_DATA = " + json.dumps(out, ensure_ascii=False) + ";\n",
        "utf-8",
    )
    print(f"\nWrote {OUT_JSON.name} and {OUT_JS.name} ({len(results)} targets)")


if __name__ == "__main__":
    main()
