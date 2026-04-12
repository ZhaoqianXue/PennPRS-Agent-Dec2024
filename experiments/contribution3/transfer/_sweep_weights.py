"""Sweep w_selection_utility to find optimal value per family."""
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

def priority_score(card, w_prior, w_utility, w_cheap=0.05, w_fid=0.08, w_model=0.02, model_cap=100):
    n = card.get("n_models", 0)
    ms = math.log1p(min(max(n, 0), model_cap))
    prior = card.get("transferability_prior_score", 0)
    if w_prior > 0:
        return round(
            w_prior * prior + w_utility * card.get("utility_score", 0)
            + w_cheap * card.get("cheap_rank_score", 0)
            + w_fid * card.get("phenotype_fidelity_score", 0)
            + w_model * ms, 6)
    return card.get("utility_score", 0) + 0.25 * math.log1p(min(max(n, 0), 25)) + 0.15 * card.get("cheap_rank_score", 0)


def evaluate(family, w_prior, w_utility):
    path = RUNS / family / BASELINE_TS / "results.json"
    if not path.exists():
        return None
    results = load_results(path)
    try:
        df_sel = load_benchmark_target_selection(benchmark_family=family, selected_only=True)
    except Exception:
        return None

    target_meta = {}
    for _, row in df_sel.iterrows():
        tid = str(row.get("input_icd") or "").strip()
        if tid:
            target_meta[tid] = {"source": normalize_target_source(row.get("target_source"))}

    total_gap = 0
    exact_hits = 0
    n_eval = 0
    regressions = []

    # Also compute baseline for comparison
    total_gap_base = 0
    exact_base = 0

    for tid, meta in sorted(target_meta.items()):
        r = results.get(tid)
        cards = get_cards(r)
        if not cards:
            continue
        ranks = bundle_ranks_for_target(tid, meta["source"])

        evaluable = [(c["bundle_id"], ranks.get(c["bundle_id"])) for c in cards if ranks.get(c["bundle_id"]) is not None]
        if not evaluable:
            continue
        oracle_bid, oracle_rank = min(evaluable, key=lambda x: x[1])

        # Baseline
        for c in cards:
            c["_base"] = priority_score(c, w_prior, 0.05)
        base_sorted = sorted(cards, key=lambda c: (-c["_base"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        base_primary = base_sorted[0]["bundle_id"]
        base_rank = ranks.get(base_primary)
        base_gap = (base_rank - oracle_rank) if base_rank is not None else None
        if base_gap is not None:
            total_gap_base += base_gap
            if base_gap == 0:
                exact_base += 1

        # Proposed
        for c in cards:
            c["_prop"] = priority_score(c, w_prior, w_utility)
        prop_sorted = sorted(cards, key=lambda c: (-c["_prop"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        prop_primary = prop_sorted[0]["bundle_id"]
        prop_rank = ranks.get(prop_primary)
        prop_gap = (prop_rank - oracle_rank) if prop_rank is not None else None

        if prop_gap is not None:
            total_gap += prop_gap
            n_eval += 1
            if prop_gap == 0:
                exact_hits += 1

        if base_gap is not None and prop_gap is not None and prop_gap > base_gap:
            regressions.append((tid, base_gap, prop_gap))

    return {
        "total_gap": total_gap,
        "total_gap_base": total_gap_base,
        "exact_hits": exact_hits,
        "exact_base": exact_base,
        "n_eval": n_eval,
        "n_regressions": len(regressions),
        "regressions": regressions,
    }


# Sweep
for family in ["binary_to_binary", "binary_to_continuous"]:
    w_prior = 0.2 if family == "binary_to_binary" else 1.0
    print(f"\n{'='*90}")
    print(f"  SWEEP: {family} (w_prior={w_prior})")
    print(f"{'='*90}")
    print(f"  {'w_util':>6} {'total_gap':>9} {'base_gap':>8} {'delta':>6} {'exact':>5} {'base_ex':>7} {'regr':>4} | regressions")
    print(f"  {'-'*6} {'-'*9} {'-'*8} {'-'*6} {'-'*5} {'-'*7} {'-'*4} + {'-'*50}")

    for w_util in [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15]:
        r = evaluate(family, w_prior, w_util)
        if r is None:
            continue
        delta = r["total_gap"] - r["total_gap_base"]
        reg_str = "; ".join(f"{t}({bg}→{pg})" for t, bg, pg in r["regressions"][:5])
        print(f"  {w_util:>6.2f} {r['total_gap']:>9} {r['total_gap_base']:>8} {delta:>+6} {r['exact_hits']:>5} {r['exact_base']:>7} {r['n_regressions']:>4} | {reg_str}")
