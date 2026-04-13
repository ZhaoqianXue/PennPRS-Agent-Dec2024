"""
Recompute utility scores from raw evidence fields stored in results.json cards.
Sweeps over utility-formula parameters (w_mechanistic_overlap, ancestor_bonus,
endophenotype_fidelity_base) combined with selection weights.

This gives the true expected impact of utility-formula changes WITHOUT re-running the agent.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import load_trait_bundle_index, load_benchmark_target_selection

ROOTCODE_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_binary/prs_adjauc_matrix_binary_combined_rootcode.csv"
NONTARGET_AUC = PROJECT_ROOT / "experiments/contribution1/result/aou_extend_trait/prs_adjauc_matrix_binary_extend_qc.csv"
RUNS = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent"
LATEST_TS = "all-tools__20260411_211443"

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


def load_family(family):
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


# ── Utility recomputation ────────────────────────────────────────────────────

ARCHETYPE_BASE_FIDELITY = {
    "same-endpoint disease": 0.95,
    "adjacent disease family": 0.76,
    "composite liability trait": 0.68,
    "mechanistic endophenotype / organ-function measurement": 0.66,
    "administrative/exposure/treatment/family-history proxy": 0.15,
}


@dataclass
class UtilityFormulaCfg:
    # TransferConfig utility weights
    w_statistical_overlap: float = 2.0
    w_mechanistic_overlap: float = 3.5
    w_signal_capacity: float = 1.2
    w_phenotype_fidelity: float = 2.8
    concordance_bonus: float = 0.8
    concordance_penalty: float = -0.4
    # OT adjustments
    ancestor_bonus_3plus: float = 0.30    # was +0.3 for ≥3 ancestors
    ancestor_bonus_1plus: float = 0.10    # was +0.1 for ≥1 ancestor
    mechanistic_cap: float = 99.0         # hard cap on mechanistic_overlap (was uncapped ~2.15)
    cross_ta_penalty_mult: float = 0.40   # was 0.4 for cross-TA
    literature_penalty: float = 0.25      # was -0.25
    # Fidelity base overrides
    endophenotype_base: float = 0.66      # default 0.66
    # GC resolution discount floor (copy from TransferConfig)
    gc_discount_floor: float = 0.0
    apply_gc_resolution_discount: bool = True
    gc_cheap_rank_significant: float = 1.6
    gc_cheap_rank_nonsignificant: float = 0.6


def _gc_discount_raw(gc: dict | None) -> float:
    if gc is None:
        return 0.0
    mult = 1.0
    for key in ("target_resolution", "candidate_resolution"):
        res = (gc or {}).get(key)
        if not res:
            continue
        conf = res.get("confidence", "Unresolved") if isinstance(res, dict) else "Unresolved"
        if conf == "High":
            pass
        elif conf == "Moderate":
            mult *= 0.7
        elif conf == "Low":
            mult *= 0.3
        else:
            mult *= 0.0
    return mult


def _configured_gc_discount(gc: dict | None, cfg: UtilityFormulaCfg) -> float:
    if not cfg.apply_gc_resolution_discount:
        return 1.0
    raw = _gc_discount_raw(gc)
    return max(raw, cfg.gc_discount_floor)


def _is_significant_gc_dict(gc: dict | None) -> bool:
    return bool(gc and gc.get("rg") is not None and gc.get("p_value") is not None and gc["p_value"] < 0.05)


def _is_strong_gc_dict(gc: dict | None) -> bool:
    return bool(_is_significant_gc_dict(gc) and abs(float(gc.get("rg") or 0.0)) >= 0.30)


def _is_supported_ot_dict(ot: dict | None) -> bool:
    return bool(ot and ot.get("weighted_shared_target_overlap_score", 0) >= 0.20 and ot.get("shared_target_count", 0) >= 1)


def _is_strong_ot_dict(ot: dict | None) -> bool:
    return bool(
        ot and ot.get("confidence_level") in {"High", "Moderate"}
        and ot.get("genetic_support_present")
        and ot.get("weighted_shared_target_overlap_score", 0) >= 0.35
    )


def _is_explicit_ot_discordance_dict(ot: dict | None) -> bool:
    return bool(ot and ot.get("pair_status") == "no_shared_targets")


def recompute_fidelity_score(card: dict, cfg: UtilityFormulaCfg) -> float:
    """Recompute fidelity score with possibly different endophenotype base."""
    archetype = card.get("archetype", "adjacent disease family")
    base_map = dict(ARCHETYPE_BASE_FIDELITY)
    base_map["mechanistic endophenotype / organ-function measurement"] = cfg.endophenotype_base
    base = base_map.get(archetype, 0.66)
    lexical = card.get("lexical_match_score", 0) / 100.0
    shared = min(card.get("shared_token_count", 0), 3) * 0.05
    score = min(1.0, base + (0.15 * lexical) + shared)
    return round(score, 6)


def recompute_utility_score(card: dict, cfg: UtilityFormulaCfg) -> float:
    archetype = card.get("archetype", "adjacent disease family")
    gc: dict | None = card.get("gc")
    h2: dict | None = card.get("h2")
    ot: dict | None = card.get("open_targets")
    n_models = card.get("n_models", 0)
    fidelity = recompute_fidelity_score(card, cfg)

    # Phase 1: Statistical overlap
    statistical_overlap = 0.0
    if gc and gc.get("rg") is not None:
        rg = abs(float(gc["rg"]))
        if gc.get("p_value") is not None and gc["p_value"] < 0.05:
            statistical_overlap = min(1.5, rg / 0.20)
        else:
            statistical_overlap = min(0.5, rg / 0.40)
        gc_discount = _configured_gc_discount(gc, cfg)
        statistical_overlap *= gc_discount

    # Phase 2: Mechanistic overlap
    mechanistic_overlap = 0.0
    if ot:
        mechanistic_overlap = min(1.5, ot.get("weighted_shared_target_overlap_score", 0) / 0.30)
        if ot.get("literature_dominance_warning"):
            mechanistic_overlap = max(0.0, mechanistic_overlap - cfg.literature_penalty)
        # Cross-TA penalty
        src_ta = ot.get("source_therapeutic_areas") or []
        cand_ta = ot.get("candidate_therapeutic_areas") or []
        if not ot.get("therapeutic_area_match") and src_ta and cand_ta:
            mechanistic_overlap *= cfg.cross_ta_penalty_mult
        # Ancestor overlap
        anc_count = ot.get("shared_ancestor_count", 0)
        if anc_count >= 3:
            mechanistic_overlap += cfg.ancestor_bonus_3plus
        elif anc_count >= 1:
            mechanistic_overlap += cfg.ancestor_bonus_1plus
        # Phenotype overlap
        pheno_score = ot.get("phenotype_overlap_score", 0.0)
        if pheno_score >= 0.15:
            mechanistic_overlap += 0.35
        elif pheno_score >= 0.05:
            mechanistic_overlap += 0.15
        # Cap
        mechanistic_overlap = min(mechanistic_overlap, cfg.mechanistic_cap)

    # Phase 3: Signal capacity
    signal_capacity = 0.0
    if h2:
        candidate_h2 = h2.get("candidate_signal_capacity") or 0.0
        shared_ceiling = h2.get("shared_signal_ceiling_proxy") or candidate_h2
        signal_capacity = min(1.0, shared_ceiling / 0.010)

    utility = (
        (statistical_overlap * cfg.w_statistical_overlap)
        + (mechanistic_overlap * cfg.w_mechanistic_overlap)
        + (signal_capacity * cfg.w_signal_capacity)
        + (fidelity * cfg.w_phenotype_fidelity)
    )

    # Phase 4: Concordance
    gc_strong = _is_strong_gc_dict(gc)
    ot_strong = _is_strong_ot_dict(ot)
    ot_supported = _is_supported_ot_dict(ot)
    if gc_strong and ot_strong:
        utility += cfg.concordance_bonus
    elif _is_significant_gc_dict(gc) and ot_supported and not gc_strong:
        utility += cfg.concordance_bonus * 0.5
    elif gc_strong and _is_explicit_ot_discordance_dict(ot) and not ot_supported:
        utility += cfg.concordance_penalty

    # Phase 5: Model count
    if n_models >= 5:
        utility += 0.15
    elif n_models < 3:
        utility -= 0.2

    # Phase 6: Archetype
    if archetype == "administrative/exposure/treatment/family-history proxy":
        utility -= 1.6

    return round(utility, 6)


def priority_score_from_card(card: dict, utility: float, fidelity: float,
                               w_prior: float, w_utility: float, w_cheap: float,
                               w_fid: float, w_model: float) -> float:
    prior = card.get("transferability_prior_score", 0.0)
    n = card.get("n_models", 0)
    ms = math.log1p(min(max(n, 0), 100))
    cheap = card.get("cheap_rank_score", 0.0)
    if w_prior > 0:
        return round(w_prior * prior + w_utility * utility + w_cheap * cheap + w_fid * fidelity + w_model * ms, 6)
    n25 = math.log1p(min(max(n, 0), 25))
    return round(utility + 0.25 * n25 + 0.15 * cheap, 6)


def simulate_with_recompute(family: str, results: dict, target_meta: dict,
                             uf_cfg: UtilityFormulaCfg,
                             sel_weights: dict) -> dict:
    """Simulate selection using recomputed utility and priority scores."""
    total_gap = 0
    exact_hits = 0
    n_targets = 0
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

        # Recompute scores for each card
        scored = []
        for c in cards:
            util = recompute_utility_score(c, uf_cfg)
            fid = recompute_fidelity_score(c, uf_cfg)
            ps = priority_score_from_card(c, util, fid, **sel_weights)
            scored.append((ps, -util, c.get("bundle_id", ""), c, util, fid))
        scored.sort()  # ascending, so negate ps when appending
        # Actually sort descending by ps
        scored = sorted(scored, key=lambda x: (-x[0], x[1], x[2]))

        selected_bid = scored[0][2]
        selected_rank = ranks.get(selected_bid)
        if selected_rank is None:
            continue

        gap = selected_rank - oracle_rank
        total_gap += gap
        if gap == 0:
            exact_hits += 1
        n_targets += 1

        oracle_card_data = next((s for s in scored if s[2] == oracle_bid), None)
        rows.append({
            "tid": tid,
            "oracle_bid": oracle_bid,
            "oracle_rank": oracle_rank,
            "oracle_util": oracle_card_data[4] if oracle_card_data else 0,
            "oracle_ps": -oracle_card_data[0] if oracle_card_data else 0,  # fix negation
            "selected_bid": selected_bid,
            "selected_rank": selected_rank,
            "selected_util": scored[0][4],
            "selected_ps": scored[0][0],
            "gap": gap,
            "hit": int(gap == 0),
        })

    mean_gap = total_gap / n_targets if n_targets else float("inf")
    return {
        "total_gap": total_gap,
        "exact_hits": exact_hits,
        "n_targets": n_targets,
        "mean_gap": mean_gap,
        "rows": rows,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

CONFIGS_TO_TEST = [
    # (label, UtilityFormulaCfg, selection_weights_dict)

    # ── Binary-to-Binary ──────────────────────────────────────────────────────
    ("b2b_BASELINE", "binary_to_binary",
     UtilityFormulaCfg(w_statistical_overlap=2.0, w_mechanistic_overlap=3.5, w_signal_capacity=1.2,
                       w_phenotype_fidelity=2.8, concordance_bonus=0.8, concordance_penalty=-0.4,
                       ancestor_bonus_3plus=0.30, ancestor_bonus_1plus=0.10, mechanistic_cap=99.0,
                       gc_discount_floor=0.0),
     dict(w_prior=0.2, w_utility=0.06, w_cheap=0.05, w_fid=0.08, w_model=0.02)),

    ("b2b_SWEEP_BEST", "binary_to_binary",
     UtilityFormulaCfg(w_statistical_overlap=2.0, w_mechanistic_overlap=3.5, w_signal_capacity=1.2,
                       w_phenotype_fidelity=2.8, concordance_bonus=0.8, concordance_penalty=-0.4,
                       ancestor_bonus_3plus=0.30, ancestor_bonus_1plus=0.10, mechanistic_cap=99.0,
                       gc_discount_floor=0.0),
     dict(w_prior=0.2, w_utility=0.04, w_cheap=0.05, w_fid=0.08, w_model=0.001)),

    ("b2b_OT_REDUCED", "binary_to_binary",
     UtilityFormulaCfg(w_statistical_overlap=2.0, w_mechanistic_overlap=2.0, w_signal_capacity=1.2,
                       w_phenotype_fidelity=2.8, concordance_bonus=0.8, concordance_penalty=-0.4,
                       ancestor_bonus_3plus=0.15, ancestor_bonus_1plus=0.05, mechanistic_cap=1.5,
                       gc_discount_floor=0.0),
     dict(w_prior=0.2, w_utility=0.04, w_cheap=0.05, w_fid=0.08, w_model=0.001)),

    ("b2b_OT_STRICT", "binary_to_binary",
     UtilityFormulaCfg(w_statistical_overlap=2.0, w_mechanistic_overlap=1.5, w_signal_capacity=1.2,
                       w_phenotype_fidelity=2.8, concordance_bonus=0.8, concordance_penalty=-0.4,
                       ancestor_bonus_3plus=0.10, ancestor_bonus_1plus=0.03, mechanistic_cap=1.5,
                       gc_discount_floor=0.0),
     dict(w_prior=0.2, w_utility=0.04, w_cheap=0.05, w_fid=0.08, w_model=0.001)),

    ("b2b_OT_STRICT+PRIOR", "binary_to_binary",
     UtilityFormulaCfg(w_statistical_overlap=2.0, w_mechanistic_overlap=1.5, w_signal_capacity=1.2,
                       w_phenotype_fidelity=2.8, concordance_bonus=0.8, concordance_penalty=-0.4,
                       ancestor_bonus_3plus=0.10, ancestor_bonus_1plus=0.03, mechanistic_cap=1.5,
                       gc_discount_floor=0.0),
     dict(w_prior=0.4, w_utility=0.04, w_cheap=0.03, w_fid=0.08, w_model=0.001)),

    # ── Binary-to-Continuous ─────────────────────────────────────────────────
    ("b2c_BASELINE", "binary_to_continuous",
     UtilityFormulaCfg(w_statistical_overlap=3.2, w_mechanistic_overlap=2.5, w_signal_capacity=1.4,
                       w_phenotype_fidelity=2.1, concordance_bonus=0.5, concordance_penalty=-0.2,
                       ancestor_bonus_3plus=0.30, ancestor_bonus_1plus=0.10, mechanistic_cap=99.0,
                       gc_discount_floor=0.3, apply_gc_resolution_discount=True,
                       endophenotype_base=0.66),
     dict(w_prior=1.0, w_utility=0.07, w_cheap=0.05, w_fid=0.08, w_model=0.02)),

    ("b2c_SWEEP_BEST", "binary_to_continuous",
     UtilityFormulaCfg(w_statistical_overlap=3.2, w_mechanistic_overlap=2.5, w_signal_capacity=1.4,
                       w_phenotype_fidelity=2.1, concordance_bonus=0.5, concordance_penalty=-0.2,
                       ancestor_bonus_3plus=0.30, ancestor_bonus_1plus=0.10, mechanistic_cap=99.0,
                       gc_discount_floor=0.3, apply_gc_resolution_discount=True,
                       endophenotype_base=0.66),
     dict(w_prior=1.0, w_utility=0.07, w_cheap=0.05, w_fid=0.06, w_model=0.001)),

    ("b2c_OT_REDUCED", "binary_to_continuous",
     UtilityFormulaCfg(w_statistical_overlap=3.2, w_mechanistic_overlap=1.2, w_signal_capacity=1.4,
                       w_phenotype_fidelity=2.1, concordance_bonus=0.5, concordance_penalty=-0.2,
                       ancestor_bonus_3plus=0.15, ancestor_bonus_1plus=0.05, mechanistic_cap=1.5,
                       gc_discount_floor=0.3, apply_gc_resolution_discount=True,
                       endophenotype_base=0.71),
     dict(w_prior=1.0, w_utility=0.07, w_cheap=0.05, w_fid=0.06, w_model=0.001)),

    ("b2c_OT_STRICT", "binary_to_continuous",
     UtilityFormulaCfg(w_statistical_overlap=3.2, w_mechanistic_overlap=0.8, w_signal_capacity=1.4,
                       w_phenotype_fidelity=2.1, concordance_bonus=0.5, concordance_penalty=-0.2,
                       ancestor_bonus_3plus=0.10, ancestor_bonus_1plus=0.03, mechanistic_cap=1.2,
                       gc_discount_floor=0.3, apply_gc_resolution_discount=True,
                       endophenotype_base=0.71),
     dict(w_prior=1.0, w_utility=0.07, w_cheap=0.05, w_fid=0.06, w_model=0.001)),

    ("b2c_OT_STRICT+ENDO", "binary_to_continuous",
     UtilityFormulaCfg(w_statistical_overlap=3.2, w_mechanistic_overlap=0.8, w_signal_capacity=1.4,
                       w_phenotype_fidelity=2.1, concordance_bonus=0.5, concordance_penalty=-0.2,
                       ancestor_bonus_3plus=0.10, ancestor_bonus_1plus=0.03, mechanistic_cap=1.2,
                       gc_discount_floor=0.3, apply_gc_resolution_discount=True,
                       endophenotype_base=0.75),
     dict(w_prior=1.0, w_utility=0.07, w_cheap=0.05, w_fid=0.06, w_model=0.001)),

    ("b2c_OT_STRICT+HIGH_PRIOR", "binary_to_continuous",
     UtilityFormulaCfg(w_statistical_overlap=3.2, w_mechanistic_overlap=0.8, w_signal_capacity=1.4,
                       w_phenotype_fidelity=2.1, concordance_bonus=0.5, concordance_penalty=-0.2,
                       ancestor_bonus_3plus=0.10, ancestor_bonus_1plus=0.03, mechanistic_cap=1.2,
                       gc_discount_floor=0.3, apply_gc_resolution_discount=True,
                       endophenotype_base=0.75),
     dict(w_prior=1.5, w_utility=0.05, w_cheap=0.03, w_fid=0.06, w_model=0.001)),
]

if __name__ == "__main__":
    family_results_cache: dict[str, tuple] = {}
    for family in ["binary_to_binary", "binary_to_continuous"]:
        r, tm = load_family(family)
        family_results_cache[family] = (r, tm)

    print(f"\n{'='*120}")
    print(f"  UTILITY RECOMPUTE SIMULATION")
    print(f"{'='*120}")
    print(f"\n  {'label':<35} {'family':<25}  total_gap  hits  n  mean_gap")
    print(f"  {'-'*35} {'-'*25}  {'-'*9}  {'-'*4}  {'-'  }  {'-'*8}")

    best_by_family: dict[str, tuple] = {}

    for label, family, uf_cfg, sel_w in CONFIGS_TO_TEST:
        results, target_meta = family_results_cache[family]
        if results is None or not target_meta:
            continue
        stats = simulate_with_recompute(family, results, target_meta, uf_cfg, sel_w)
        baseline_label = f"{family[:3]}_BASELINE"
        marker = ""
        if label.endswith("BASELINE"):
            marker = "  [baseline]"
        print(f"  {label:<35} {family:<25}  {stats['total_gap']:>9}  {stats['exact_hits']:>4}/{stats['n_targets']}  {stats['mean_gap']:>8.2f}{marker}")

        # Track best by family
        if family not in best_by_family or stats["total_gap"] < best_by_family[family][0]:
            best_by_family[family] = (stats["total_gap"], label, stats, uf_cfg, sel_w)

    print(f"\n{'='*120}")
    print(f"  PER-TARGET DETAIL FOR BEST CONFIG PER FAMILY")
    print(f"{'='*120}")

    for family, (total_gap, label, stats, uf_cfg, sel_w) in best_by_family.items():
        print(f"\n  Best for {family}: {label}  (total_gap={total_gap}, hits={stats['exact_hits']}/{stats['n_targets']})")
        print(f"  Utility formula: w_mech={uf_cfg.w_mechanistic_overlap}, anc3={uf_cfg.ancestor_bonus_3plus}, anc1={uf_cfg.ancestor_bonus_1plus}, cap={uf_cfg.mechanistic_cap}, endo_base={uf_cfg.endophenotype_base}")
        print(f"  Selection weights: {sel_w}")
        print(f"\n  {'tid':<8} {'gap':>5} {'hit':>4} | {'oracle_label':<30} {'sel_label':<30} oracle_rank sel_rank")
        for row in sorted(stats["rows"], key=lambda x: -x["gap"]):
            print(f"  {row['tid']:<8} {row['gap']:>5} {row['hit']:>4} | {bundle_labels.get(row['oracle_bid'], '')[:30]:<30} {bundle_labels.get(row['selected_bid'], '')[:30]:<30} {row['oracle_rank']:>11} {row['selected_rank']:>8}")
