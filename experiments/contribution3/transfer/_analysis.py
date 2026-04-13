"""One-shot gap analysis: oracle rank vs selected rank for both benchmark families."""
import json, sys, math
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from experiments.contribution3.transfer.common import load_trait_bundle_index, load_benchmark_target_selection

ROOTCODE_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_binary/prs_adjauc_matrix_binary_combined_rootcode.csv"
NONTARGET_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_extend_trait/prs_adjauc_matrix_binary_extend_qc.csv"
RUNS = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent"

import glob as _glob

def _find_latest_ts(family):
    """Find the most recent run timestamp directory."""
    pattern = str(RUNS / family / "all-tools__*")
    dirs = sorted(_glob.glob(pattern))
    return Path(dirs[-1]).name if dirs else None

# Will be auto-detected; override manually if needed
LATEST_TS = {
    "binary_to_binary": None,  # will auto-detect
    "binary_to_continuous": "all-tools__20260411_200904",
}
HISTORICAL_TS = "all-tools__20260411_131327"

def col_to_pgs(col):
    s = str(col).strip()
    if "__" in s:
        return s.rsplit("__", 1)[-1]
    return s.replace("_hmPOS_GRCh38", "")

def load_matrix(path):
    m = pd.read_csv(path, index_col=0)
    m.columns = [col_to_pgs(c) for c in m.columns]
    return m

def normalize_target_source(raw):
    s = str(raw).strip() if raw else ""
    return "extend_trait" if s in ("nontarget_pgs", "extend_trait") else "rootcode"

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

bundles = load_trait_bundle_index()
bundle_pgs = {b.bundle_id: list(dict.fromkeys(b.candidate_pgs_ids)) for b in bundles}
bundle_labels = {b.bundle_id: b.canonical_label for b in bundles}

mat_rc = load_matrix(ROOTCODE_AUC)
mat_nt = load_matrix(NONTARGET_AUC)

def get_matrix(source):
    return mat_nt if source in ("nontarget_pgs", "extend_trait") else mat_rc

def bundle_ranks_for_target(target_code, source):
    m = get_matrix(source)
    if target_code not in m.index:
        return {}, set()
    row = m.loc[target_code]
    auc_by_pgs = {str(pid): float(v) for pid, v in row.items() if pd.notna(v)}
    auc_by_bundle = {}
    unavail = set()
    for bid, pids in bundle_pgs.items():
        vals = [auc_by_pgs[p] for p in pids if p in auc_by_pgs]
        if vals:
            auc_by_bundle[bid] = max(vals)
        else:
            unavail.add(bid)
    return competition_ranks(auc_by_bundle), unavail

def load_results(path):
    data = json.loads(path.read_text())
    by_target = {}
    for r in data:
        tid = (r.get("target") or {}).get("target_id", "")
        by_target[tid] = r
    return by_target

def get_decision(r):
    return (r or {}).get("decision", {})

def get_best_bundle(r):
    d = get_decision(r)
    if d.get("outcome") != "MATCHED":
        return None
    return str(d.get("best_bundle_id") or "").strip() or None

def get_shortlist(r):
    d = get_decision(r)
    es = d.get("evidence_state") or {}
    cards = es.get("candidate_cards") or []
    ids = [str(c.get("bundle_id") or "").strip() for c in cards if c.get("bundle_id")]
    if ids:
        return list(dict.fromkeys(ids))
    return [str(b).strip() for b in (es.get("shortlist_bundle_ids") or []) if str(b).strip()]

def oracle_from_shortlist(sl, ranks):
    evaluable = [b for b in sl if b in ranks]
    unavail_cnt = len(sl) - len(evaluable)
    if not evaluable:
        return None, None, unavail_cnt
    best = min(evaluable, key=lambda b: ranks[b])
    return best, ranks[best], unavail_cnt

def get_frontier_ids(r):
    d = get_decision(r)
    return d.get("frontier_bundle_ids", [])

def get_cards(r):
    d = get_decision(r)
    es = d.get("evidence_state") or {}
    return es.get("candidate_cards") or []

# ---- Main analysis ----
for family in ["binary_to_binary", "binary_to_continuous"]:
    print(f"\n{'='*80}")
    print(f"  BENCHMARK FAMILY: {family}")
    print(f"{'='*80}")

    latest_ts = (LATEST_TS.get(family) if isinstance(LATEST_TS, dict) else LATEST_TS) or _find_latest_ts(family)
    if not latest_ts:
        print(f"  [SKIP] no runs found for {family}")
        continue
    print(f"  Latest: {latest_ts}")
    print(f"  Historical: {HISTORICAL_TS}")
    latest_path = RUNS / family / latest_ts / "results.json"
    hist_path = RUNS / family / HISTORICAL_TS / "results.json"

    if not latest_path.exists():
        print(f"  [SKIP] {latest_path} not found")
        continue

    latest = load_results(latest_path)
    hist = load_results(hist_path) if hist_path.exists() else {}

    try:
        df_sel = load_benchmark_target_selection(benchmark_family=family, selected_only=True)
    except Exception as e:
        print(f"  [SKIP] cannot load benchmark selection: {e}")
        continue

    target_meta = {}
    for _, row in df_sel.iterrows():
        tid = str(row.get("input_icd") or "").strip()
        if not tid:
            continue
        src = normalize_target_source(row.get("target_source"))
        label = str(row.get("input_ontology") or row.get("input_description") or tid).strip()
        target_meta[tid] = {"source": src, "label": label}

    rows = []
    for tid, meta in target_meta.items():
        lr = latest.get(tid)
        hr = hist.get(tid)
        lb = get_best_bundle(lr)
        hb = get_best_bundle(hr)
        if lb is None and hb is None:
            continue

        ranks, global_unavail = bundle_ranks_for_target(tid, meta["source"])
        total_evaluable = len(ranks)

        sl_latest = get_shortlist(lr)
        sl_hist = get_shortlist(hr)
        oracle_bid, oracle_rank, sl_unavail = oracle_from_shortlist(sl_latest, ranks)
        hist_oracle_bid, hist_oracle_rank, hist_sl_unavail = oracle_from_shortlist(sl_hist, ranks)

        lr_rank = ranks.get(lb) if lb else None
        hr_rank = ranks.get(hb) if hb else None

        # Evidence analysis
        cards = get_cards(lr)
        oracle_card = None
        selected_card = None
        for c in cards:
            if c.get("bundle_id") == oracle_bid:
                oracle_card = c
            if c.get("bundle_id") == lb:
                selected_card = c

        gap = (lr_rank - oracle_rank) if lr_rank is not None and oracle_rank is not None else None
        hist_gap = (hr_rank - oracle_rank) if hr_rank is not None and oracle_rank is not None else None

        rows.append({
            "target_id": tid,
            "target_label": meta["label"][:50],
            "total_evaluable_bundles": total_evaluable,
            "oracle_rank": oracle_rank,
            "oracle_bid": oracle_bid,
            "oracle_label": bundle_labels.get(oracle_bid or "", "")[:40],
            "latest_rank": lr_rank,
            "latest_bid": lb,
            "latest_label": bundle_labels.get(lb or "", "")[:40],
            "hist_rank": hr_rank,
            "hist_bid": hb,
            "gap_to_oracle": gap,
            "hist_gap_to_oracle": hist_gap,
            "shortlist_size": len(sl_latest),
            "shortlist_unavail": sl_unavail,
            "oracle_in_shortlist": oracle_bid in sl_latest if oracle_bid else False,
        })

    if not rows:
        print("  No MATCHED targets found.")
        continue

    # Print rank table
    print(f"\n  Targets: {len(rows)}")
    print(f"\n  {'target':<8} {'oracle':>6} {'latest':>7} {'hist':>6} {'gap':>5} {'h_gap':>5} {'sl_sz':>5} {'sl_na':>5} {'orc_in_sl':>9} | latest_label")
    print(f"  {'-'*8} {'-'*6} {'-'*7} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*9} + {'-'*40}")
    for r in sorted(rows, key=lambda x: (x["gap_to_oracle"] or 999, x["target_id"])):
        print(f"  {r['target_id']:<8} {str(r['oracle_rank'] or 'na'):>6} {str(r['latest_rank'] or 'na'):>7} {str(r['hist_rank'] or 'na'):>6} {str(r['gap_to_oracle'] or 'na'):>5} {str(r['hist_gap_to_oracle'] or 'na'):>5} {r['shortlist_size']:>5} {r['shortlist_unavail']:>5} {str(r['oracle_in_shortlist']):>9} | {r['latest_label']}")

    # Summary
    gaps = [r["gap_to_oracle"] for r in rows if r["gap_to_oracle"] is not None]
    hist_gaps = [r["hist_gap_to_oracle"] for r in rows if r["hist_gap_to_oracle"] is not None]
    exact_hits = sum(1 for g in gaps if g == 0)
    improved = sum(1 for r in rows if r["gap_to_oracle"] is not None and r["hist_gap_to_oracle"] is not None and r["gap_to_oracle"] < r["hist_gap_to_oracle"])
    same = sum(1 for r in rows if r["gap_to_oracle"] is not None and r["hist_gap_to_oracle"] is not None and r["gap_to_oracle"] == r["hist_gap_to_oracle"])
    worse = sum(1 for r in rows if r["gap_to_oracle"] is not None and r["hist_gap_to_oracle"] is not None and r["gap_to_oracle"] > r["hist_gap_to_oracle"])
    mean_gap = sum(gaps) / len(gaps) if gaps else float("nan")
    mean_hist_gap = sum(hist_gaps) / len(hist_gaps) if hist_gaps else float("nan")
    median_gap = sorted(gaps)[len(gaps)//2] if gaps else float("nan")

    print(f"\n  Summary:")
    print(f"    Targets with MATCHED outcome:  {len(rows)}")
    print(f"    Exact oracle hits:             {exact_hits}/{len(gaps)}")
    print(f"    Mean gap to oracle:            {mean_gap:.2f}")
    print(f"    Median gap to oracle:          {median_gap}")
    print(f"    Mean historical gap to oracle: {mean_hist_gap:.2f}")
    print(f"    vs historical: improved={improved}, same={same}, worse={worse}")
    print(f"    Oracle NOT in shortlist:        {sum(1 for r in rows if not r['oracle_in_shortlist'])}")
    print(f"    Shortlist unavail bundles (avg): {sum(r['shortlist_unavail'] for r in rows)/len(rows):.1f}")

    # Detailed gap analysis: for targets with gap > 0, show evidence comparison
    print(f"\n  --- Gap Analysis (gap > 0) ---")
    for r in sorted(rows, key=lambda x: -(x["gap_to_oracle"] or 0)):
        if (r["gap_to_oracle"] or 0) <= 0:
            continue
        tid = r["target_id"]
        lr = latest.get(tid)
        cards = get_cards(lr)
        card_by_id = {c["bundle_id"]: c for c in cards}
        oracle_c = card_by_id.get(r["oracle_bid"])
        selected_c = card_by_id.get(r["latest_bid"])

        print(f"\n  {tid} ({r['target_label']}) gap={r['gap_to_oracle']}")
        print(f"    Selected: {r['latest_bid']} ({r['latest_label']}) rank={r['latest_rank']}")
        print(f"    Oracle:   {r['oracle_bid']} ({r['oracle_label']}) rank={r['oracle_rank']}")

        if selected_c:
            print(f"    Selected evidence: utility={selected_c.get('utility_score',0):.3f} cheap={selected_c.get('cheap_rank_score',0):.3f} prior={selected_c.get('transferability_prior_score',0):.3f} arch={selected_c.get('archetype','?')[:30]}")
            gc = selected_c.get("gc") or {}
            print(f"      GC: rg={gc.get('rg','?')} p={gc.get('p_value','?')} strength={gc.get('evidence_strength','?')}")
            ot = selected_c.get("open_targets") or {}
            print(f"      OT: overlap={ot.get('weighted_shared_target_overlap_score','?')} conf={ot.get('confidence_level','?')} genetic_supp={ot.get('genetic_support_present','?')}")
            print(f"      Tags: {selected_c.get('evidence_tags', [])}")

        if oracle_c:
            print(f"    Oracle evidence: utility={oracle_c.get('utility_score',0):.3f} cheap={oracle_c.get('cheap_rank_score',0):.3f} prior={oracle_c.get('transferability_prior_score',0):.3f} arch={oracle_c.get('archetype','?')[:30]}")
            gc = oracle_c.get("gc") or {}
            print(f"      GC: rg={gc.get('rg','?')} p={gc.get('p_value','?')} strength={gc.get('evidence_strength','?')}")
            ot = oracle_c.get("open_targets") or {}
            print(f"      OT: overlap={ot.get('weighted_shared_target_overlap_score','?')} conf={ot.get('confidence_level','?')} genetic_supp={ot.get('genetic_support_present','?')}")
            print(f"      Tags: {oracle_c.get('evidence_tags', [])}")
        elif r["oracle_bid"] and r["oracle_bid"] not in card_by_id:
            print(f"    Oracle bundle NOT in shortlist cards!")

        # Show frontier
        frontier = get_frontier_ids(lr)
        print(f"    Frontier: {frontier}")
        oracle_in_frontier = r["oracle_bid"] in frontier
        print(f"    Oracle in frontier: {oracle_in_frontier}")
