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
SHORTLIST_CSV = (
    TRANSFER_RUNS
    / "unified"
    / "all-tools__20260414_015734"
    / "shortlist_recall.csv"
)
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
    TRANSFER_RUNS / "unified" / "evaluation" / "all-tools__end_to_end_eval_detail.csv"
)
PGS_METADATA_CSV = PROJECT_ROOT / "Genetic_Agent" / "disease_preprocess" / "pgs_metadata_binary_combined.csv"
OUT_DIR = Path(__file__).resolve().parent
OUT_JSON = OUT_DIR / "presentation_data.json"
OUT_JS = OUT_DIR / "data.js"

PRS_TOP_N = 100  # show top-N PGS models per target in PRS model level view

# Presentation cohort: strong primary (low competition rank), not "exact oracle only".
MAX_SELECTED_RANK_INCLUSIVE = 5
RUN_LABEL = "all-tools__20260414_015734"

# Targets excluded from the presentation (weak biological rationale or niche phenotype)
EXCLUDED_TARGET_IDS = {"K02", "K04", "N65", "L05"}


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

    shortlist_df = pd.read_csv(SHORTLIST_CSV)
    sr = pd.to_numeric(shortlist_df["selected_bundle_rank"], errors="coerce")
    cohort = shortlist_df[sr <= MAX_SELECTED_RANK_INCLUSIVE].copy()
    target_ids = [str(x).strip() for x in cohort["target_id"].tolist()]

    print(
        f"Run {RUN_LABEL}: {len(target_ids)} targets with "
        f"selected_bundle_rank <= {MAX_SELECTED_RANK_INCLUSIVE} (of {len(shortlist_df)} total)"
    )

    input_type_map = _load_union_input_type_map()
    self_best_auc_map, self_best_pgs_map = _load_self_best_maps()
    eval_detail_map = _load_eval_detail()
    pgs_n_cases_map = _load_pgs_n_cases_map()
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

    results = []
    target_ids = [t for t in target_ids if t not in EXCLUDED_TARGET_IDS]
    for tid in target_ids:
        row = cohort[cohort["target_id"] == tid].iloc[0]
        target_source = str(row["target_source"]).strip()
        target_desc = str(row.get("target_label", "") or "").strip() or tid

        matched_bid = str(row["selected_bundle_id"]).strip()
        oracle_bid = str(row["transfer_eligible_global_oracle_bundle_id"]).strip()
        oracle_label = str(row["transfer_eligible_global_oracle_label"]).strip()
        sel_rank = int(float(row["selected_bundle_rank"])) if pd.notna(row.get("selected_bundle_rank")) else None
        ora_rank = int(float(row["transfer_eligible_global_oracle_rank"])) if pd.notna(
            row.get("transfer_eligible_global_oracle_rank")
        ) else None

        input_type = input_type_map.get(tid, "A")

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
                    "is_oracle": bid == oracle_bid,
                    "is_self": is_self,
                    "max_auc_pgs_id": max_pgs,
                    "max_auc_n_cases": pgs_n_cases_map.get(max_pgs),
                }
            )

        bars.sort(key=lambda x: (-x["max_auc"], x["bundle_id"]))

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

        results.append(
            {
                "target_id": tid,
                "target_label": target_desc,
                "input_type": input_type,
                "target_source": target_source,
                "matched_bundle_id": matched_bid,
                "matched_cross_trait": str(row.get("selected_bundle_label", "")).strip(),
                "selected_bundle_rank": sel_rank,
                "oracle_bundle_id": oracle_bid,
                "oracle_label": oracle_label,
                "oracle_rank": ora_rank,
                "primary_equals_oracle": matched_bid == oracle_bid,
                "benchmark_top_auc": None,
                "self_best_auc": self_best_auc_map.get(tid),
                "confidence": str(row.get("status", "ok")).strip(),
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
        print(f"  {tid}: {len(bars)} Cross Trait bars")

    results.sort(key=lambda x: (x["input_type"], x["target_id"]))

    out = {
        "generated": RUN_LABEL,
        "shortlist_csv": str(SHORTLIST_CSV.relative_to(PROJECT_ROOT)),
        "filter": f"selected_bundle_rank <= {MAX_SELECTED_RANK_INCLUSIVE}",
        "n_targets_total_benchmark": int(len(shortlist_df)),
        "n_targets": len(results),
        "targets": results,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), "utf-8")
    OUT_JS.write_text(
        "const PRESENTATION_DATA = " + json.dumps(out, ensure_ascii=False) + ";\n",
        "utf-8",
    )
    print(f"\nWrote {OUT_JSON.name} and {OUT_JS.name} ({len(results)} targets)")


if __name__ == "__main__":
    main()
