"""
Offline sweep to find optimal _selection_priority_score weights.
Reads stored card scores from the latest results.json (20260411_211443).
Tests weight combinations and computes oracle vs selected rank gap.
Does NOT run the agent – pure offline simulation on existing card data.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (
    load_trait_bundle_index,
    load_benchmark_target_selection,
)

ROOTCODE_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_binary/prs_adjauc_matrix_binary_combined_rootcode.csv"
NONTARGET_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_extend_trait/prs_adjauc_matrix_binary_extend_qc.csv"
RUNS = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent"
LATEST_TS = "all-tools__20260411_211443"

# ── Bundle metadata ──────────────────────────────────────────────────────────
bundles_idx = load_trait_bundle_index()
bundle_pgs   = {b.bundle_id: list(dict.fromkeys(b.candidate_pgs_ids)) for b in bundles_idx}
bundle_labels = {b.bundle_id: b.canonical_label for b in bundles_idx}


def col_to_pgs(col: str) -> str:
    s = str(col).strip()
    return s.rsplit("__", 1)[-1] if "__" in s else s.replace("_hmPOS_GRCh38", "")


def load_matrix(path: Path) -> pd.DataFrame:
    m = pd.read_csv(path, index_col=0)
    m.columns = [col_to_pgs(c) for c in m.columns]
    return m


mat_rc = load_matrix(ROOTCODE_AUC)
mat_nt = load_matrix(NONTARGET_AUC)


def get_matrix(source: str) -> pd.DataFrame:
    return mat_nt if source in ("nontarget_pgs", "extend_trait") else mat_rc


def normalize_target_source(raw) -> str:
    return "extend_trait" if str(raw).strip() in ("nontarget_pgs", "extend_trait") else "rootcode"


def competition_ranks(auc_by_bundle: dict) -> dict:
    ranked = sorted(auc_by_bundle, key=lambda b: (-auc_by_bundle[b], b))
    ranks, prev, cr = {}, None, 0
    for idx, bid in enumerate(ranked, 1):
        a = auc_by_bundle[bid]
        if prev is None or a != prev:
            cr = idx
            prev = a
        ranks[bid] = cr
    return ranks


def bundle_ranks_for_target(target_code: str, source: str) -> dict:
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


def load_results(path: Path) -> dict:
    data = json.loads(path.read_text())
    return {(r.get("target") or {}).get("target_id", ""): r for r in data}


def get_cards(r) -> list:
    d = (r or {}).get("decision", {})
    return (d.get("evidence_state") or {}).get("candidate_cards") or []


def priority_score(card: dict, w_prior: float, w_utility: float, w_cheap: float,
                   w_fid: float, w_model: float, model_cap: int = 100) -> float:
    n = card.get("n_models", 0)
    ms = math.log1p(min(max(n, 0), model_cap))
    prior = card.get("transferability_prior_score", 0.0)
    if w_prior > 0:
        return round(
            w_prior * prior
            + w_utility * card.get("utility_score", 0.0)
            + w_cheap  * card.get("cheap_rank_score", 0.0)
            + w_fid    * card.get("phenotype_fidelity_score", 0.0)
            + w_model  * ms,
            6,
        )
    n25 = math.log1p(min(max(n, 0), 25))
    return card.get("utility_score", 0.0) + 0.25 * n25 + 0.15 * card.get("cheap_rank_score", 0.0)


def simulate_family(family: str, cfg: dict, results: dict, target_meta: dict) -> dict:
    total_gap = 0
    exact_hits = 0
    n_targets = 0
    n_unavailable_oracle = 0

    for tid, meta in sorted(target_meta.items()):
        r = results.get(tid)
        cards = get_cards(r)
        if not cards:
            continue

        ranks = bundle_ranks_for_target(tid, meta["source"])
        evaluable = [(c["bundle_id"], ranks.get(c["bundle_id"])) for c in cards if c["bundle_id"] in ranks]
        if not evaluable:
            n_unavailable_oracle += 1
            continue

        oracle_bid, oracle_rank = min(evaluable, key=lambda x: x[1])

        # Score cards and pick top-1
        scored = sorted(
            cards,
            key=lambda c: (
                -priority_score(c, **cfg),
                -c.get("utility_score", 0),
                -c.get("cheap_rank_score", 0),
                c.get("bundle_id", ""),
            ),
        )
        selected_bid = scored[0]["bundle_id"]
        selected_rank = ranks.get(selected_bid)

        if selected_rank is None:
            continue

        gap = selected_rank - oracle_rank
        total_gap += gap
        if gap == 0:
            exact_hits += 1
        n_targets += 1

    mean_gap = total_gap / n_targets if n_targets else float("inf")
    return {
        "total_gap": total_gap,
        "exact_hits": exact_hits,
        "n_targets": n_targets,
        "mean_gap": mean_gap,
        "n_unavailable_oracle": n_unavailable_oracle,
    }


# ── Per-target detail for a given config ──────────────────────────────────────
def detail_family(family: str, cfg: dict, results: dict, target_meta: dict) -> list:
    rows = []
    for tid, meta in sorted(target_meta.items()):
        r = results.get(tid)
        cards = get_cards(r)
        if not cards:
            continue

        ranks = bundle_ranks_for_target(tid, meta["source"])
        evaluable = [(c["bundle_id"], ranks.get(c["bundle_id"])) for c in cards if c["bundle_id"] in ranks]
        if not evaluable:
            continue

        oracle_bid, oracle_rank = min(evaluable, key=lambda x: x[1])

        scored = sorted(
            cards,
            key=lambda c: (
                -priority_score(c, **cfg),
                -c.get("utility_score", 0),
                c.get("bundle_id", ""),
            ),
        )
        selected_bid = scored[0]["bundle_id"]
        selected_rank = ranks.get(selected_bid)
        if selected_rank is None:
            continue

        oracle_card = next((c for c in cards if c["bundle_id"] == oracle_bid), {})
        selected_card = scored[0]

        rows.append({
            "family": family,
            "target_id": tid,
            "oracle_bid": oracle_bid,
            "oracle_label": bundle_labels.get(oracle_bid, "")[:30],
            "oracle_rank": oracle_rank,
            "oracle_ps": round(priority_score(oracle_card, **cfg), 4),
            "oracle_utility": oracle_card.get("utility_score", 0),
            "oracle_prior": oracle_card.get("transferability_prior_score", 0),
            "selected_bid": selected_bid,
            "selected_label": bundle_labels.get(selected_bid, "")[:30],
            "selected_rank": selected_rank,
            "selected_ps": round(priority_score(selected_card, **cfg), 4),
            "selected_utility": selected_card.get("utility_score", 0),
            "selected_prior": selected_card.get("transferability_prior_score", 0),
            "gap": selected_rank - oracle_rank,
            "hit": int(selected_rank == oracle_rank),
        })
    return rows


def load_family(family: str):
    path = RUNS / family / LATEST_TS / "results.json"
    if not path.exists():
        return None, None
    results = load_results(path)
    try:
        df_sel = load_benchmark_target_selection(benchmark_family=family, selected_only=True)
    except Exception:
        return results, {}
    target_meta = {}
    for _, row in df_sel.iterrows():
        tid = str(row.get("input_icd") or "").strip()
        if tid:
            target_meta[tid] = {"source": normalize_target_source(row.get("target_source"))}
    return results, target_meta


# ── Baseline configs (current code) ─────────────────────────────────────────
CURRENT_B2B = dict(w_prior=0.2, w_utility=0.06, w_cheap=0.05, w_fid=0.08, w_model=0.02)
CURRENT_B2C = dict(w_prior=1.0, w_utility=0.07, w_cheap=0.05, w_fid=0.08, w_model=0.02)


# ── Weight grid search ───────────────────────────────────────────────────────
def sweep(family: str, base_w_prior: float, results: dict, target_meta: dict) -> list:
    """Grid search over utility, cheap, model weights."""
    candidates = []

    w_prior_opts  = [base_w_prior, base_w_prior * 1.5, base_w_prior * 2.0, base_w_prior * 3.0]
    w_utility_opts = [0.001, 0.002, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]
    w_cheap_opts   = [0.01, 0.02, 0.03, 0.05]
    w_fid_opts     = [0.04, 0.06, 0.08, 0.10]
    w_model_opts   = [0.001, 0.005, 0.01, 0.02]

    for wp, wu, wc, wf, wm in itertools.product(
        w_prior_opts, w_utility_opts, w_cheap_opts, w_fid_opts, w_model_opts
    ):
        cfg = dict(w_prior=wp, w_utility=wu, w_cheap=wc, w_fid=wf, w_model=wm)
        stats = simulate_family(family, cfg, results, target_meta)
        candidates.append({**cfg, **stats})

    return sorted(candidates, key=lambda x: (x["total_gap"], -x["exact_hits"]))


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for family, current_cfg, base_prior in [
        ("binary_to_binary",   CURRENT_B2B, 0.2),
        ("binary_to_continuous", CURRENT_B2C, 1.0),
    ]:
        results, target_meta = load_family(family)
        if results is None:
            continue
        if not target_meta:
            print(f"[SKIP] no target_meta for {family}")
            continue

        print(f"\n{'='*90}")
        print(f"  SWEEP: {family}")
        print(f"{'='*90}")

        # Baseline
        baseline = simulate_family(family, current_cfg, results, target_meta)
        print(f"\n  Baseline: total_gap={baseline['total_gap']}  exact_hits={baseline['exact_hits']}/{baseline['n_targets']}  mean_gap={baseline['mean_gap']:.2f}")

        # Sweep
        ranked = sweep(family, base_prior, results, target_meta)
        print(f"\n  Top-20 configs by total_gap:")
        print(f"  {'w_prior':>7} {'w_util':>6} {'w_cheap':>7} {'w_fid':>6} {'w_model':>7}  |  total_gap  exact_hits  mean_gap")
        print(f"  {'-'*7} {'-'*6} {'-'*7} {'-'*6} {'-'*7}  +  {'-'*9}  {'-'*10}  {'-'*8}")
        for r in ranked[:20]:
            marker = " *** BEST" if r is ranked[0] else ""
            print(f"  {r['w_prior']:>7.3f} {r['w_utility']:>6.3f} {r['w_cheap']:>7.3f} {r['w_fid']:>6.3f} {r['w_model']:>7.3f}  |  {r['total_gap']:>9}  {r['exact_hits']:>10}/{r['n_targets']}  {r['mean_gap']:>8.2f}{marker}")

        # Show per-target details for best config
        best_cfg = {k: ranked[0][k] for k in ["w_prior", "w_utility", "w_cheap", "w_fid", "w_model"]}
        detail_rows = detail_family(family, best_cfg, results, target_meta)
        print(f"\n  Per-target detail with best config {best_cfg}:")
        print(f"  {'tid':<8} {'gap':>5} {'hit':>4} | {'oracle_label':<30} {'sel_label':<30} | orc_ps  sel_ps  orc_rank  sel_rank")
        for dr in sorted(detail_rows, key=lambda x: -x["gap"]):
            print(f"  {dr['target_id']:<8} {dr['gap']:>5} {dr['hit']:>4} | {dr['oracle_label']:<30} {dr['selected_label']:<30} | {dr['oracle_ps']:>7.4f} {dr['selected_ps']:>7.4f} {dr['oracle_rank']:>8} {dr['selected_rank']:>8}")

        total_new = sum(r["gap"] for r in detail_rows)
        new_hits = sum(r["hit"] for r in detail_rows)
        print(f"\n  Best config total_gap={total_new}  exact_hits={new_hits}/{len(detail_rows)}  mean_gap={total_new/len(detail_rows):.2f}")
        print(f"  vs baseline: total_gap={baseline['total_gap']}  exact_hits={baseline['exact_hits']}/{baseline['n_targets']}  mean_gap={baseline['mean_gap']:.2f}")
        improvement = baseline['total_gap'] - total_new
        print(f"  Gap reduction: {improvement} ({improvement/max(baseline['total_gap'],1)*100:.1f}%)")
