"""Simulate effect of weight changes on primary selection using baseline evidence cards."""
import json, sys, math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from experiments.contribution3.transfer.common import load_trait_bundle_index, load_benchmark_target_selection

ROOTCODE_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_binary/prs_adjauc_matrix_binary_combined_rootcode.csv"
NONTARGET_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_extend_trait/prs_adjauc_matrix_binary_extend_qc.csv"
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
    return mat_nt if source in ("nontarget_pgs", "extend_trait") else mat_rc

def normalize_target_source(raw):
    return "extend_trait" if str(raw).strip() in ("nontarget_pgs", "extend_trait") else "rootcode"

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

def priority_score(card, w_prior, w_utility, w_cheap, w_fid, w_model, model_cap=100):
    n = card.get("n_models", 0)
    ms = math.log1p(min(max(n, 0), model_cap))
    prior = card.get("transferability_prior_score", 0)
    if w_prior > 0:
        return round(
            w_prior * prior
            + w_utility * card.get("utility_score", 0)
            + w_cheap * card.get("cheap_rank_score", 0)
            + w_fid * card.get("phenotype_fidelity_score", 0)
            + w_model * ms, 6
        )
    return card.get("utility_score", 0) + 0.25 * math.log1p(min(max(n, 0), 25)) + 0.15 * card.get("cheap_rank_score", 0)

# Weight configs to simulate
CONFIGS = {
    "binary_to_binary": {
        "baseline": {"w_prior": 0.2, "w_utility": 0.05, "w_cheap": 0.05, "w_fid": 0.08, "w_model": 0.02},
        "proposed": {"w_prior": 0.2, "w_utility": 0.10, "w_cheap": 0.05, "w_fid": 0.08, "w_model": 0.02},
    },
    "binary_to_continuous": {
        "baseline": {"w_prior": 1.0, "w_utility": 0.05, "w_cheap": 0.05, "w_fid": 0.08, "w_model": 0.02},
        "proposed": {"w_prior": 1.0, "w_utility": 0.10, "w_cheap": 0.05, "w_fid": 0.08, "w_model": 0.02},
    },
}

for family in ["binary_to_binary", "binary_to_continuous"]:
    print(f"\n{'='*95}")
    print(f"  SIMULATION: {family}")
    print(f"{'='*95}")

    path = RUNS / family / BASELINE_TS / "results.json"
    if not path.exists():
        continue
    results = load_results(path)
    try:
        df_sel = load_benchmark_target_selection(benchmark_family=family, selected_only=True)
    except Exception:
        continue

    target_meta = {}
    for _, row in df_sel.iterrows():
        tid = str(row.get("input_icd") or "").strip()
        if tid:
            target_meta[tid] = {"source": normalize_target_source(row.get("target_source"))}

    base_cfg = CONFIGS[family]["baseline"]
    prop_cfg = CONFIGS[family]["proposed"]

    changes = []
    for tid, meta in sorted(target_meta.items()):
        r = results.get(tid)
        cards = get_cards(r)
        if not cards:
            continue

        ranks = bundle_ranks_for_target(tid, meta["source"])

        # Score all cards under both configs
        for c in cards:
            c["_base_ps"] = priority_score(c, **base_cfg)
            c["_prop_ps"] = priority_score(c, **prop_cfg)

        base_sorted = sorted(cards, key=lambda c: (-c["_base_ps"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        prop_sorted = sorted(cards, key=lambda c: (-c["_prop_ps"], -c.get("utility_score", 0), c.get("bundle_id", "")))

        base_primary = base_sorted[0]["bundle_id"]
        prop_primary = prop_sorted[0]["bundle_id"]

        # Find oracle
        evaluable = [(c["bundle_id"], ranks.get(c["bundle_id"])) for c in cards if ranks.get(c["bundle_id"]) is not None]
        if not evaluable:
            continue
        oracle_bid, oracle_rank = min(evaluable, key=lambda x: x[1])

        base_rank = ranks.get(base_primary)
        prop_rank = ranks.get(prop_primary)
        base_gap = (base_rank - oracle_rank) if base_rank and oracle_rank else None
        prop_gap = (prop_rank - oracle_rank) if prop_rank and oracle_rank else None

        changed = base_primary != prop_primary
        if changed or (base_gap and base_gap > 0):
            changes.append({
                "tid": tid,
                "changed": changed,
                "base_primary": base_primary,
                "prop_primary": prop_primary,
                "oracle": oracle_bid,
                "oracle_rank": oracle_rank,
                "base_rank": base_rank,
                "prop_rank": prop_rank,
                "base_gap": base_gap,
                "prop_gap": prop_gap,
                "base_label": bundle_labels.get(base_primary, "")[:30],
                "prop_label": bundle_labels.get(prop_primary, "")[:30],
            })

    # Print all cases
    print(f"\n  {'tid':<8} {'changed':>7} {'base_gap':>8} {'prop_gap':>8} {'delta':>6} | base_primary → prop_primary")
    print(f"  {'-'*8} {'-'*7} {'-'*8} {'-'*8} {'-'*6} + {'-'*60}")

    total_base = 0
    total_prop = 0
    n_improved = 0
    n_regressed = 0
    n_same = 0
    base_exact = 0
    prop_exact = 0

    for tid, meta in sorted(target_meta.items()):
        r = results.get(tid)
        cards = get_cards(r)
        if not cards:
            continue
        ranks = bundle_ranks_for_target(tid, meta["source"])
        for c in cards:
            c["_base_ps"] = priority_score(c, **base_cfg)
            c["_prop_ps"] = priority_score(c, **prop_cfg)
        base_sorted = sorted(cards, key=lambda c: (-c["_base_ps"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        prop_sorted = sorted(cards, key=lambda c: (-c["_prop_ps"], -c.get("utility_score", 0), c.get("bundle_id", "")))
        base_primary = base_sorted[0]["bundle_id"]
        prop_primary = prop_sorted[0]["bundle_id"]
        evaluable = [(c["bundle_id"], ranks.get(c["bundle_id"])) for c in cards if ranks.get(c["bundle_id"]) is not None]
        if not evaluable:
            continue
        oracle_bid, oracle_rank = min(evaluable, key=lambda x: x[1])
        base_rank = ranks.get(base_primary)
        prop_rank = ranks.get(prop_primary)
        base_gap = (base_rank - oracle_rank) if base_rank is not None and oracle_rank is not None else None
        prop_gap = (prop_rank - oracle_rank) if prop_rank is not None and oracle_rank is not None else None

        if base_gap is not None:
            total_base += base_gap
            if base_gap == 0:
                base_exact += 1
        if prop_gap is not None:
            total_prop += prop_gap
            if prop_gap == 0:
                prop_exact += 1

        changed = base_primary != prop_primary
        if base_gap is not None and prop_gap is not None:
            if prop_gap < base_gap:
                n_improved += 1
            elif prop_gap > base_gap:
                n_regressed += 1
            else:
                n_same += 1

        delta = None
        if base_gap is not None and prop_gap is not None:
            delta = prop_gap - base_gap

        if changed or (base_gap and base_gap > 0):
            sym = "↑" if (delta and delta < 0) else ("↓" if (delta and delta > 0) else " ")
            print(f"  {tid:<8} {'YES' if changed else 'no':>7} {base_gap if base_gap is not None else 'na':>8} {prop_gap if prop_gap is not None else 'na':>8} {delta if delta is not None else 'na':>6}{sym}| {bundle_labels.get(base_primary,'')[:30]} → {bundle_labels.get(prop_primary,'')[:30]}")

    n_total = n_improved + n_regressed + n_same
    print(f"\n  SUMMARY:")
    print(f"    Improved: {n_improved}, Same: {n_same}, Regressed: {n_regressed}")
    print(f"    Base exact hits: {base_exact}, Proposed exact hits: {prop_exact}")
    print(f"    Base total gap: {total_base}, Proposed total gap: {total_prop}")
    mean_base = total_base / n_total if n_total else 0
    mean_prop = total_prop / n_total if n_total else 0
    print(f"    Base mean gap: {mean_base:.2f}, Proposed mean gap: {mean_prop:.2f}")
