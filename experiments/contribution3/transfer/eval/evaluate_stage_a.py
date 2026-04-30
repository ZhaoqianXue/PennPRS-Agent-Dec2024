"""Lightweight Stage-A (cross-trait) evaluator.

Loads a `results.json` produced with `run --stop-after bundle_posterior`
(or any full run — the `supporting_bundles` field is populated either way)
and reports per-target whether the empirical oracle PGS's bundle made it
into the supporting list. No PGS hydration or model-picker stages need to
have run.

Outputs a CSV row per target plus a summary header to stdout.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ROOTCODE_AUC_MATRIX = PROJECT_ROOT / "experiments/contribution1/result/aou_binary/prs_adjauc_matrix_binary_combined_rootcode.csv"
NONTARGET_AUC_MATRIX = PROJECT_ROOT / "experiments/contribution1/result/aou_extend_trait/prs_adjauc_matrix_binary_extend_qc.csv"
BUNDLE_INDEX = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/trait_bundle_index.json"


def col_to_pgs(c: str) -> str:
    s = str(c).strip()
    if "__" in s:
        s = s.rsplit("__", 1)[-1]
    return s.replace("_hmPOS_GRCh38", "")


def _auc_matrix_path(target_source: str) -> Path:
    return NONTARGET_AUC_MATRIX if target_source in ("nontarget_pgs", "extend_trait") else ROOTCODE_AUC_MATRIX


def _normalize_target_source(raw: Any) -> str:
    txt = str(raw or "").strip()
    return "extend_trait" if txt in ("nontarget_pgs", "extend_trait") else "rootcode_main_analysis"


def _oracle_pgs_for_target(target_id: str, source: str, matrix_cache: dict[str, pd.DataFrame]) -> str | None:
    """Find empirical oracle PGS for `target_id`. Tries the explicit source first
    (if known) then falls back to the other matrix, since some run results don't
    record `target_source` and the same `input_icd` only lives in one of them.
    """
    candidate_paths = [_auc_matrix_path(source)]
    other_path = NONTARGET_AUC_MATRIX if candidate_paths[0] == ROOTCODE_AUC_MATRIX else ROOTCODE_AUC_MATRIX
    candidate_paths.append(other_path)
    for path in candidate_paths:
        if str(path) not in matrix_cache:
            matrix_cache[str(path)] = pd.read_csv(path, index_col=0)
        matrix = matrix_cache[str(path)]
        if target_id not in matrix.index:
            continue
        row = matrix.loc[target_id].dropna()
        if row.empty:
            continue
        best_col = row.idxmax()
        return col_to_pgs(str(best_col))
    return None


def _rank_fraction_map(target_id: str, source: str, matrix_cache: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {pgs_id: rank_fraction in [0,1)} for this target, by AUC desc."""
    candidate_paths = [_auc_matrix_path(source)]
    other_path = NONTARGET_AUC_MATRIX if candidate_paths[0] == ROOTCODE_AUC_MATRIX else ROOTCODE_AUC_MATRIX
    candidate_paths.append(other_path)
    for path in candidate_paths:
        if str(path) not in matrix_cache:
            matrix_cache[str(path)] = pd.read_csv(path, index_col=0)
        matrix = matrix_cache[str(path)]
        if target_id not in matrix.index:
            continue
        row = matrix.loc[target_id].dropna()
        if row.empty:
            continue
        sorted_ids = row.sort_values(ascending=False).index.tolist()
        n = len(sorted_ids)
        return {col_to_pgs(str(c)): i / n for i, c in enumerate(sorted_ids)}
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="Path to results.json")
    ap.add_argument("--out", default="", help="Optional output CSV path")
    ap.add_argument("--show-failures", action="store_true",
                    help="Print per-target detail for failures (oracle missing)")
    args = ap.parse_args()

    results_path = Path(args.results)
    results = json.loads(results_path.read_text())

    bundle_pgs: dict[str, list[str]] = {}
    if BUNDLE_INDEX.exists():
        for entry in json.loads(BUNDLE_INDEX.read_text()):
            bundle_pgs.setdefault(entry["bundle_id"], list(entry.get("candidate_pgs_ids", [])))

    matrix_cache: dict[str, pd.DataFrame] = {}

    rows: list[dict[str, Any]] = []
    for r in results:
        tgt = r["target"]
        target_id = tgt.get("target_id") or tgt.get("input_icd")
        source = _normalize_target_source(tgt.get("target_source"))
        oracle_pgs = _oracle_pgs_for_target(target_id, source, matrix_cache)
        oracle_bundle = None
        if oracle_pgs:
            for bid, pgs_list in bundle_pgs.items():
                if oracle_pgs in pgs_list:
                    oracle_bundle = bid
                    break

        decision = r.get("decision", {})
        supporting = [b["bundle_id"] for b in decision.get("supporting_bundles", [])]
        st = decision.get("search_trace", {})
        probed = list(st.get("probed_bundle_ids") or [])
        retained_last = []
        rounds = st.get("probe_rounds") or []
        if rounds:
            retained_last = list(rounds[-1].get("retained_bundle_ids") or [])
        ot_verified = list(st.get("ot_verified_bundle_ids") or [])

        # Match official evaluator semantics: oracle considered "in <stage>" iff
        # the oracle PGS appears in the union of candidate_pgs_ids across the
        # bundles seen at that stage (not just bundle-id membership).
        def _bundles_contain_oracle(bundle_ids: list[str]) -> bool:
            if not oracle_pgs:
                return False
            for bid in bundle_ids:
                if oracle_pgs in bundle_pgs.get(bid, []):
                    return True
            return False

        oracle_in_probe = _bundles_contain_oracle(probed)
        oracle_in_retained = _bundles_contain_oracle(retained_last)
        oracle_in_ot = _bundles_contain_oracle(ot_verified)
        oracle_in_supporting = _bundles_contain_oracle(supporting)

        # bundle_pgs may be a stale snapshot; fall back to True if oracle was reported
        # by official eval. We can also detect 'oracle bundle unknown' separately.
        if oracle_bundle is None and oracle_pgs is None:
            phase_lost = "no_oracle"
        elif oracle_bundle is None:
            phase_lost = "oracle_pgs_not_indexed"
        elif oracle_in_supporting:
            phase_lost = "kept"
        elif oracle_in_retained:
            phase_lost = "lost_at_bundle_posterior"
        elif oracle_in_probe:
            phase_lost = "lost_at_probe_reflection"
        else:
            phase_lost = "lost_at_initial_probe"

        # Reachability metrics: best rank_fraction of any supporting PGS
        rf_map = _rank_fraction_map(target_id, source, matrix_cache)
        sup_pgs: set[str] = set()
        for bid in supporting:
            sup_pgs.update(bundle_pgs.get(bid, []))
        rf_in_supp = [rf_map[p] for p in sup_pgs if p in rf_map]
        best_rf = min(rf_in_supp) if rf_in_supp else 1.0
        top_05_reach = best_rf <= 0.005
        top_1_reach = best_rf <= 0.01
        top_2_5_reach = best_rf <= 0.025
        top_5_reach = best_rf <= 0.05
        top_10_reach = best_rf <= 0.10

        rows.append({
            "target_id": target_id,
            "target_label": tgt.get("target_label"),
            "input_type": tgt.get("input_type"),
            "target_source": source,
            "oracle_pgs": oracle_pgs,
            "oracle_bundle": oracle_bundle,
            "oracle_in_probe_pool": oracle_in_probe,
            "oracle_in_retained_last_round": oracle_in_retained,
            "oracle_in_ot_verified": oracle_in_ot,
            "oracle_in_supporting_bundles": oracle_in_supporting,
            "best_rf_in_supporting": round(best_rf, 6),
            "top_0_5pct_reachable": top_05_reach,
            "top_1pct_reachable": top_1_reach,
            "top_2_5pct_reachable": top_2_5_reach,
            "top_5pct_reachable": top_5_reach,
            "top_10pct_reachable": top_10_reach,
            "phase_lost": phase_lost,
            "supporting_bundles": "|".join(supporting),
            "n_supporting": len(supporting),
            "n_probed": len(probed),
            "n_retained_last": len(retained_last),
        })

    # Summary
    n = len(rows)
    counts = defaultdict(int)
    for r in rows:
        counts[r["phase_lost"]] += 1
    in_probe = sum(1 for r in rows if r["oracle_in_probe_pool"])
    in_retained = sum(1 for r in rows if r["oracle_in_retained_last_round"])
    in_supporting = sum(1 for r in rows if r["oracle_in_supporting_bundles"])
    has_bundle = sum(1 for r in rows if r["oracle_bundle"])

    # Reachability counts
    t05 = sum(1 for r in rows if r["top_0_5pct_reachable"])
    t1 = sum(1 for r in rows if r["top_1pct_reachable"])
    t25 = sum(1 for r in rows if r["top_2_5pct_reachable"])
    t5 = sum(1 for r in rows if r["top_5pct_reachable"])
    t10 = sum(1 for r in rows if r["top_10pct_reachable"])

    print(f"=== Stage-A summary ({n} targets) ===")
    print(f"  oracle bundle resolvable:           {has_bundle}/{n} ({has_bundle/n:.4f})")
    print(f"  oracle in initial+expanded probes:  {in_probe}/{n} ({in_probe/n:.4f})")
    print(f"  oracle in last-round retained:      {in_retained}/{n} ({in_retained/n:.4f})")
    print(f"  oracle in supporting_bundles:       {in_supporting}/{n} ({in_supporting/n:.4f})")
    print(f"\n  Reachability (any supporting PGS in top K%):")
    print(f"    top_0_5pct_reachable: {t05}/{n} ({t05/n:.4f})")
    print(f"    top_1pct_reachable:   {t1}/{n} ({t1/n:.4f})")
    print(f"    top_2_5pct_reachable: {t25}/{n} ({t25/n:.4f})")
    print(f"    top_5pct_reachable:   {t5}/{n} ({t5/n:.4f})")
    print(f"    top_10pct_reachable:  {t10}/{n} ({t10/n:.4f})")
    print(f"\n  Phase where oracle was lost:")
    for k in ["kept", "lost_at_bundle_posterior", "lost_at_probe_reflection",
              "lost_at_initial_probe", "oracle_pgs_not_indexed", "no_oracle"]:
        print(f"    {k:30s}  {counts[k]:>3d}")

    if args.show_failures:
        print("\n  Targets where oracle bundle is in retained but not in supporting (bundle_posterior dropped it):")
        for r in rows:
            if r["phase_lost"] == "lost_at_bundle_posterior":
                print(f"    {r['target_id']:5s} oracle_bundle={r['oracle_bundle']:20s} retained_n={r['n_retained_last']:>3d} supporting_n={r['n_supporting']:>2d} -> {r['supporting_bundles']}")
        print("\n  Targets where oracle bundle is in probe pool but lost during reflection:")
        for r in rows:
            if r["phase_lost"] == "lost_at_probe_reflection":
                print(f"    {r['target_id']:5s} oracle_bundle={r['oracle_bundle']:20s} probed_n={r['n_probed']:>3d} retained_last_n={r['n_retained_last']:>3d}")
        print("\n  Targets where oracle bundle never made it into any probe round:")
        for r in rows:
            if r["phase_lost"] == "lost_at_initial_probe":
                print(f"    {r['target_id']:5s} oracle_bundle={r['oracle_bundle']:20s} probed_n={r['n_probed']:>3d}")

        print("\n  Targets where top_0_5pct is NOT reachable (no supporting PGS ranks in top 0.5%):")
        for r in rows:
            if not r["top_0_5pct_reachable"]:
                print(f"    {r['target_id']:5s} best_rf={r['best_rf_in_supporting']:.4f} supporting={r['supporting_bundles']}")

    if args.out:
        outpath = Path(args.out)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with outpath.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  Wrote per-target CSV -> {outpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
