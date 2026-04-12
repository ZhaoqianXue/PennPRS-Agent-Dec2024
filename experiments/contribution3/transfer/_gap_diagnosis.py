"""Diagnose baseline gap sources: where does oracle rank by priority score in the shortlist?"""
import json, sys, math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from experiments.contribution3.transfer.common import load_trait_bundle_index, load_benchmark_target_selection
from experiments.contribution3.transfer.agent import (
    _selection_priority_score,
    CandidateEvidenceCard,
    BINARY_TO_BINARY_CONFIG,
    BINARY_TO_CONTINUOUS_CONFIG,
)

ROOTCODE_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_icd_260217/prs_adjauc_matrix_260217_rootcode.csv"
NONTARGET_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_nontarget_pgs/prs_adjauc_matrix_notarget_pgs_qc.csv"
RUNS = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent"

# Baseline run (original weights)
BASELINE_TS = "all-tools__20260411_131327"

bundles = load_trait_bundle_index()
bundle_pgs = {b.bundle_id: list(dict.fromkeys(b.candidate_pgs_ids)) for b in bundles}
bundle_labels = {b.bundle_id: b.canonical_label for b in bundles}

def col_to_pgs(col):
    s = str(col).strip()
    if "__" in s:
        return s.rsplit("__", 1)[-1]
    return s.replace("_hmPOS_GRCh38", "")

def load_matrix(path):
    m = pd.read_csv(path, index_col=0)
    m.columns = [col_to_pgs(c) for c in m.columns]
    return m

mat_rc = load_matrix(ROOTCODE_AUC)
mat_nt = load_matrix(NONTARGET_AUC)

def get_matrix(source):
    return mat_nt if source == "nontarget_pgs" else mat_rc

def normalize_target_source(raw):
    s = str(raw).strip() if raw else ""
    return "nontarget_pgs" if s == "nontarget_pgs" else "rootcode"

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
        return {}, set()
    row = m.loc[target_code]
    auc_by_pgs = {str(pid): float(v) for pid, v in row.items() if pd.notna(v)}
    auc_by_bundle = {}
    for bid, pids in bundle_pgs.items():
        vals = [auc_by_pgs[p] for p in pids if p in auc_by_pgs]
        if vals:
            auc_by_bundle[bid] = max(vals)
    return competition_ranks(auc_by_bundle), set()

def load_results(path):
    data = json.loads(path.read_text())
    by_target = {}
    for r in data:
        tid = (r.get("target") or {}).get("target_id", "")
        by_target[tid] = r
    return by_target

def get_cards_from_result(r):
    d = (r or {}).get("decision", {})
    es = d.get("evidence_state") or {}
    return es.get("candidate_cards") or []

def get_best_bundle(r):
    d = (r or {}).get("decision", {})
    if d.get("outcome") != "MATCHED":
        return None
    return str(d.get("best_bundle_id") or "").strip() or None

def get_frontier(r):
    d = (r or {}).get("decision", {})
    return d.get("frontier_bundle_ids", [])

def card_priority_score(card_dict, config):
    """Compute priority score from a card dictionary (as stored in results.json)."""
    n_models = card_dict.get("n_models", 0)
    model_support = math.log1p(min(max(n_models, 0), 100))
    prior = card_dict.get("transferability_prior_score", 0)
    utility = card_dict.get("utility_score", 0)
    cheap = card_dict.get("cheap_rank_score", 0)
    fidelity = card_dict.get("phenotype_fidelity_score", 0)
    if config.w_transferability_prior > 0:
        score = (
            (config.w_transferability_prior * prior)
            + (config.w_selection_utility * utility)
            + (config.w_selection_cheap_rank * cheap)
            + (config.w_selection_fidelity * fidelity)
            + (config.w_selection_model_support * model_support)
        )
    else:
        score = utility + (0.25 * math.log1p(min(max(n_models, 0), 25))) + (0.15 * cheap)
    return round(score, 6)


for family in ["binary_to_binary", "binary_to_continuous"]:
    config = BINARY_TO_BINARY_CONFIG if family == "binary_to_binary" else BINARY_TO_CONTINUOUS_CONFIG
    print(f"\n{'='*90}")
    print(f"  GAP DIAGNOSIS: {family} (baseline run {BASELINE_TS})")
    print(f"{'='*90}")

    path = RUNS / family / BASELINE_TS / "results.json"
    if not path.exists():
        print(f"  [SKIP] {path}")
        continue

    results = load_results(path)
    try:
        df_sel = load_benchmark_target_selection(benchmark_family=family, selected_only=True)
    except Exception as e:
        print(f"  [SKIP] {e}")
        continue

    target_meta = {}
    for _, row in df_sel.iterrows():
        tid = str(row.get("input_icd") or "").strip()
        if not tid:
            continue
        src = normalize_target_source(row.get("target_source"))
        target_meta[tid] = {"source": src}

    gap_cases = []
    exact_cases = []

    for tid, meta in target_meta.items():
        r = results.get(tid)
        selected_bid = get_best_bundle(r)
        if selected_bid is None:
            continue

        ranks, _ = bundle_ranks_for_target(tid, meta["source"])
        cards = get_cards_from_result(r)
        frontier = get_frontier(r)
        if not cards:
            continue

        # Compute priority scores for all cards
        scored = []
        for c in cards:
            bid = c.get("bundle_id", "")
            ps = card_priority_score(c, config)
            auc_rank = ranks.get(bid)
            scored.append({
                "bundle_id": bid,
                "priority_score": ps,
                "utility": c.get("utility_score", 0),
                "prior": c.get("transferability_prior_score", 0),
                "cheap_rank": c.get("cheap_rank_score", 0),
                "fidelity": c.get("phenotype_fidelity_score", 0),
                "n_models": c.get("n_models", 0),
                "auc_rank": auc_rank,
                "in_frontier": bid in frontier,
                "is_selected": bid == selected_bid,
                "archetype": c.get("archetype", "?"),
            })

        scored.sort(key=lambda x: -x["priority_score"])

        # Find oracle (best AUC rank in shortlist)
        evaluable = [s for s in scored if s["auc_rank"] is not None]
        if not evaluable:
            continue
        oracle = min(evaluable, key=lambda s: s["auc_rank"])
        oracle_bid = oracle["bundle_id"]
        oracle_auc_rank = oracle["auc_rank"]

        selected_auc_rank = ranks.get(selected_bid)
        gap = (selected_auc_rank - oracle_auc_rank) if selected_auc_rank and oracle_auc_rank else None

        # Oracle's position by priority score
        oracle_ps_rank = next((i+1 for i, s in enumerate(scored) if s["bundle_id"] == oracle_bid), None)

        entry = {
            "tid": tid,
            "n_shortlist": len(scored),
            "oracle_bid": oracle_bid,
            "oracle_auc_rank": oracle_auc_rank,
            "oracle_ps_rank": oracle_ps_rank,
            "oracle_priority_score": oracle["priority_score"],
            "oracle_utility": oracle["utility"],
            "oracle_prior": oracle["prior"],
            "oracle_in_frontier": oracle["in_frontier"],
            "selected_bid": selected_bid,
            "selected_auc_rank": selected_auc_rank,
            "selected_ps_rank": next((i+1 for i, s in enumerate(scored) if s["bundle_id"] == selected_bid), None),
            "selected_priority_score": next((s["priority_score"] for s in scored if s["bundle_id"] == selected_bid), None),
            "selected_utility": next((s["utility"] for s in scored if s["bundle_id"] == selected_bid), None),
            "selected_prior": next((s["prior"] for s in scored if s["bundle_id"] == selected_bid), None),
            "gap": gap,
            "all_scored": scored,
        }

        if gap and gap > 0:
            gap_cases.append(entry)
        elif gap == 0:
            exact_cases.append(entry)

    # Print summary
    print(f"\n  Exact oracle hits: {len(exact_cases)}, Gap>0: {len(gap_cases)}")
    print(f"\n  --- GAP CASES: Oracle position by priority score ---")
    print(f"  {'target':<8} {'gap':>5} {'orc_ps':>6} {'orc_auc':>7} {'sel_ps':>6} {'sel_auc':>7} {'n_sl':>4} {'orc_front':>9} | oracle_ps_score  sel_ps_score  orc_prior  sel_prior  orc_util  sel_util")
    print(f"  {'-'*8} {'-'*5} {'-'*6} {'-'*7} {'-'*6} {'-'*7} {'-'*4} {'-'*9} + {'-'*80}")

    for e in sorted(gap_cases, key=lambda x: -(x["gap"] or 0)):
        print(f"  {e['tid']:<8} {e['gap'] or 'na':>5} {e['oracle_ps_rank'] or 'na':>6} {e['oracle_auc_rank'] or 'na':>7} {e['selected_ps_rank'] or 'na':>6} {e['selected_auc_rank'] or 'na':>7} {e['n_shortlist']:>4} {str(e['oracle_in_frontier']):>9} | {e['oracle_priority_score']:.4f}  {e['selected_priority_score']:.4f}  {e['oracle_prior']:.3f}  {e['selected_prior']:.3f}  {e['oracle_utility']:.3f}  {e['selected_utility']:.3f}")

    # Distribution of oracle's priority-score rank
    ps_ranks = [e["oracle_ps_rank"] for e in gap_cases if e["oracle_ps_rank"]]
    if ps_ranks:
        print(f"\n  Oracle priority-score rank distribution (gap>0 cases):")
        for r in sorted(set(ps_ranks)):
            cnt = ps_ranks.count(r)
            print(f"    PS rank {r}: {cnt} targets")
        print(f"    Median oracle PS rank: {sorted(ps_ranks)[len(ps_ranks)//2]}")
        print(f"    Oracle in top-3 (current frontier): {sum(1 for r in ps_ranks if r <= 3)}/{len(ps_ranks)}")
        print(f"    Oracle in top-5: {sum(1 for r in ps_ranks if r <= 5)}/{len(ps_ranks)}")
        print(f"    Oracle in top-7: {sum(1 for r in ps_ranks if r <= 7)}/{len(ps_ranks)}")
