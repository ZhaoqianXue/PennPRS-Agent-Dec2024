"""Show detailed changes at w_utility=0.06 for both families."""
import json, sys, math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from experiments.contribution3.transfer.common import load_trait_bundle_index, load_benchmark_target_selection

ROOTCODE_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_icd_260217/prs_adjauc_matrix_260217_rootcode.csv"
NONTARGET_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_nontarget_pgs/prs_adjauc_matrix_notarget_pgs_qc.csv"
RUNS = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent"
BASELINE_TS = "all-tools__20260411_131327"

bundles_idx = load_trait_bundle_index()
bundle_pgs = {b.bundle_id: list(dict.fromkeys(b.candidate_pgs_ids)) for b in bundles_idx}
bundle_labels = {b.bundle_id: b.canonical_label for b in bundles_idx}

def col_to_pgs(col):
    s = str(col).strip()
    return s.rsplit("__", 1)[-1] if "__" in s else s.replace("_hmPOS_GRCh38", "")

def load_matrix(path):
    m = pd.read_csv(path, index_col=0)
    m.columns = [col_to_pgs(c) for c in m.columns]
    return m

mat_rc = load_matrix(ROOTCODE_AUC)
mat_nt = load_matrix(NONTARGET_AUC)

def get_matrix(source):
    return mat_nt if source == "nontarget_pgs" else mat_rc

def normalize_target_source(raw):
    return "nontarget_pgs" if str(raw).strip() == "nontarget_pgs" else "rootcode"

def competition_ranks(auc_by_bundle):
    ranked = sorted(auc_by_bundle, key=lambda b: (-auc_by_bundle[b], b))
    ranks, prev, cr = {}, None, 0
    for idx, bid in enumerate(ranked, 1):
        a = auc_by_bundle[bid]
        if prev is None or a != prev:
            cr = idx
            prev = a
        ranks[bid] = cr
    return ranks

def bundle_ranks_for_target(target_code, source):
    m = get_matrix(source)
    if target_code not in m.index:
        return {}
    row = m.loc[target_code]
    auc_by_pgs = {str(pid): float(v) for pid, v in row.items() if pd.notna(v)}
    auc_by_bundle = {}
    for bid, pids in bundle_pgs.items():
        vals = [auc_by_pgs[p] for p in pids if p in auc_by_pgs]
        if vals:
            auc_by_bundle[bid] = max(vals)
    return competition_ranks(auc_by_bundle)

def load_results(path):
    data = json.loads(path.read_text())
    return {(r.get("target") or {}).get("target_id", ""): r for r in data}

def get_cards(r):
    d = (r or {}).get("decision", {})
    return (d.get("evidence_state") or {}).get("candidate_cards") or []

def priority_score(card, w_prior, w_utility, w_cheap=0.05, w_fid=0.08, w_model=0.02):
    n = card.get("n_models", 0)
    ms = math.log1p(min(max(n, 0), 100))
    prior = card.get("transferability_prior_score", 0)
    if w_prior > 0:
        return round(w_prior * prior + w_utility * card.get("utility_score", 0)
            + w_cheap * card.get("cheap_rank_score", 0) + w_fid * card.get("phenotype_fidelity_score", 0)
            + w_model * ms, 6)
    return 0


for family, w_prior, w_util_new in [("binary_to_binary", 0.2, 0.06), ("binary_to_continuous", 1.0, 0.07)]:
    print(f"\n{'='*95}")
    print(f"  DETAIL: {family} w_utility 0.05 → {w_util_new}")
    print(f"{'='*95}")

    path = RUNS / family / BASELINE_TS / "results.json"
    results = load_results(path)
    df_sel = load_benchmark_target_selection(benchmark_family=family, selected_only=True)

    target_meta = {}
    for _, row in df_sel.iterrows():
        tid = str(row.get("input_icd") or "").strip()
        if tid:
            target_meta[tid] = {"source": normalize_target_source(row.get("target_source"))}

    print(f"\n  {'tid':<8} {'orc_rk':>6} {'base_rk':>7} {'prop_rk':>7} {'b_gap':>5} {'p_gap':>5} {'delta':>6} | base → proposed")
    print(f"  {'-'*8} {'-'*6} {'-'*7} {'-'*7} {'-'*5} {'-'*5} {'-'*6} + {'-'*60}")

    for tid in sorted(target_meta):
        meta = target_meta[tid]
        r = results.get(tid)
        cards = get_cards(r)
        if not cards:
            continue
        ranks = bundle_ranks_for_target(tid, meta["source"])
        evaluable = [(c["bundle_id"], ranks.get(c["bundle_id"])) for c in cards if ranks.get(c["bundle_id"]) is not None]
        if not evaluable:
            continue
        oracle_bid, oracle_rank = min(evaluable, key=lambda x: x[1])

        for c in cards:
            c["_base"] = priority_score(c, w_prior, 0.05)
            c["_prop"] = priority_score(c, w_prior, w_util_new)

        base_sorted = sorted(cards, key=lambda c: (-c["_base"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        prop_sorted = sorted(cards, key=lambda c: (-c["_prop"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        bp = base_sorted[0]["bundle_id"]
        pp = prop_sorted[0]["bundle_id"]
        br = ranks.get(bp)
        pr = ranks.get(pp)
        bg = (br - oracle_rank) if br is not None else None
        pg = (pr - oracle_rank) if pr is not None else None
        delta = (pg - bg) if pg is not None and bg is not None else None

        changed = bp != pp
        sym = ""
        if delta is not None and delta < 0:
            sym = " ↑IMPROVED"
        elif delta is not None and delta > 0:
            sym = " ↓REGRESSED"

        bl = bundle_labels.get(bp, "")[:25]
        pl = bundle_labels.get(pp, "")[:25]
        arrow = f"{bl} → {pl}" if changed else bl

        print(f"  {tid:<8} {oracle_rank:>6} {br if br else 'na':>7} {pr if pr else 'na':>7} {bg if bg is not None else 'na':>5} {pg if pg is not None else 'na':>5} {delta if delta is not None else 'na':>6} | {arrow}{sym}")
