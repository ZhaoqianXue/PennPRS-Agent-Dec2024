"""Fast two-stage shortlist simulation.

Uses pre-computed DE weights from Step 1 (72/80 at K=90).
Tests exact recall at various caps with sequential rescue tracks.
"""
from __future__ import annotations
import math, json, sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    UNIFIED_CONFIG, _build_candidate_card, _gc_lookup,
    _is_significant_gc, _target_source_for_dossier,
    _bundle_lookup as agent_bundle_lookup,
)
from experiments.contribution3.transfer.common import (
    bundle_has_source_universe_pgs, is_self_like_bundle, load_candidate_dossiers,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows
from experiments.contribution3.transfer.prompts.transfer_prompt import CandidateEvidenceCard

UNIFIED_RESULTS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_154807/results.json"
)
UNIFIED_DOSSIERS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "candidate_dossiers.json"
)

MUST_INCLUDE = {
    'C22', 'E79', 'D05', 'L68', 'B18', 'M05', 'L05', 'L56',
    'C54', 'F11', 'N97', 'N91', 'G30',
}

# Best DE weights from previous analysis (72/80 at K=90)
MAIN_WEIGHTS = {
    "prior": 2.305, "fidelity": -1.666, "utility": 0.417, "cheap": 4.472,
    "lexical": -0.052, "log_models": -0.221, "gc_rg": 3.302, "gc_sig": -1.558,
    "fid_x_cheap": 2.362, "fid_x_util": -1.861, "sqrt_prior_x_fid": -1.692,
}
OPT_FEATS = list(MAIN_WEIGHTS.keys())
MAIN_W = np.array([MAIN_WEIGHTS[k] for k in OPT_FEATS])


def _prescreen_gc(row):
    for tr in row.get("tool_trace") or []:
        if tr.get("name") == "cross_trait_genetic_correlation" and tr.get("phase") == "candidate_prescreen":
            return _gc_lookup(tr.get("result"))
    return {}


def card_features(c: CandidateEvidenceCard) -> dict:
    gc_rg = abs(float(c.gc.rg or 0)) if c.gc and c.gc.rg is not None else 0.0
    gc_sig = 1.0 if _is_significant_gc(c.gc) else 0.0
    return {
        "prior": c.transferability_prior_score,
        "fidelity": c.phenotype_fidelity_score,
        "utility": c.utility_score,
        "cheap": c.cheap_rank_score,
        "lexical": c.lexical_match_score,
        "n_models": c.n_models,
        "log_models": math.log1p(min(max(c.n_models, 0), 200)),
        "gc_rg": gc_rg,
        "gc_sig": gc_sig,
        "fid_x_cheap": c.phenotype_fidelity_score * c.cheap_rank_score,
        "fid_x_util": c.phenotype_fidelity_score * c.utility_score,
        "sqrt_prior_x_fid": math.sqrt(c.transferability_prior_score) * c.phenotype_fidelity_score,
    }


def load_all():
    results = json.loads(UNIFIED_RESULTS.read_text())
    results_by_target = {
        str((r.get("target") or {}).get("target_id") or "").strip(): r
        for r in results if (r.get("target") or {}).get("target_id")
    }
    del results
    dossiers = load_candidate_dossiers(UNIFIED_DOSSIERS)
    dossiers_by_target = {d.target.target_id: d for d in dossiers}
    recall_rows = build_shortlist_recall_rows(
        benchmark_family="unified", results_path=UNIFIED_RESULTS,
        candidate_dossiers_path=UNIFIED_DOSSIERS)
    oracle_map = {}
    for rrow in recall_rows:
        if rrow.get("status") == "ok" and rrow.get("oracle_in_candidate_dossier"):
            oracle_map[str(rrow["target_id"])] = str(rrow["transfer_eligible_global_oracle_bundle_id"])
    config = UNIFIED_CONFIG
    data = []
    for tid, oracle_id in sorted(oracle_map.items()):
        dossier = dossiers_by_target.get(tid)
        row = results_by_target.get(tid)
        if not dossier or not row:
            continue
        gc_map = _prescreen_gc(row)
        target_source = _target_source_for_dossier(dossier, "unified")
        bl = agent_bundle_lookup(dossier)
        cids = [b.bundle_id for b in dossier.candidates
                if not is_self_like_bundle(dossier.target, b)
                and bundle_has_source_universe_pgs(b, target_source)]
        cards = [_build_candidate_card(dossier, bl[bid], gc_row=gc_map.get(bid),
                                        config=config, target_source=target_source)
                 for bid in cids if bid in bl]
        feats = [(c.bundle_id, card_features(c)) for c in cards]
        data.append((tid, oracle_id, feats))
    return data


def two_stage_shortlist(feats_list, main_w, main_size, rescue_configs, cap):
    """Build shortlist: main ranking (top-main_size) + sequential rescue.
    rescue_configs: [(feat_name, max_rescue_entries), ...]
    """
    bids = [bid for bid, _ in feats_list]
    n = len(bids)

    # Build feature matrix
    mat = np.zeros((n, len(OPT_FEATS)))
    feat_by_bid = {}
    for i, (bid, f) in enumerate(feats_list):
        for j, fk in enumerate(OPT_FEATS):
            mat[i, j] = f[fk]
        feat_by_bid[bid] = f

    # Stage 1: main ranking
    scores = mat @ main_w
    order = np.argsort(-scores)
    shortlist = [bids[i] for i in order[:main_size]]
    seen = set(shortlist)

    # Stage 2: sequential rescue
    for feat_name, max_entries in rescue_configs:
        if len(shortlist) >= cap:
            break
        # Sort remaining candidates by rescue feature
        remaining = [(bid, feat_by_bid[bid][feat_name]) for bid in bids if bid not in seen]
        remaining.sort(key=lambda x: (-x[1], x[0]))
        added = 0
        for bid, _ in remaining:
            if added >= max_entries or len(shortlist) >= cap:
                break
            seen.add(bid)
            shortlist.append(bid)
            added += 1

    return shortlist


def eval_config(data, main_w, main_size, rescue_configs, cap):
    hit, must_miss, sizes = 0, [], []
    for tid, oracle_id, feats in data:
        sl = two_stage_shortlist(feats, main_w, main_size, rescue_configs, cap)
        sizes.append(len(sl))
        if oracle_id in sl:
            hit += 1
        elif tid in MUST_INCLUDE:
            must_miss.append(tid)
    return hit, must_miss, sum(sizes)/len(sizes), max(sizes)


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    print(f"Loaded {total} targets\n")

    # === Baseline: main ranking only ===
    print("=" * 80)
    print("BASELINE: Main DE-optimized ranking only")
    print("=" * 80)
    for K in range(85, 131, 5):
        h, mm, avg_sz, max_sz = eval_config(data, MAIN_W, K, [], K)
        must_m = sorted(set(mm) & MUST_INCLUDE)
        g30 = "G30" not in mm
        if h >= 70 or g30:
            print(f"  K={K}: {h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'} avg_sz={avg_sz:.0f}")

    # === Two-stage with various rescue orders ===
    print("\n" + "=" * 80)
    print("TWO-STAGE: Main + sequential rescue")
    print("=" * 80)

    # Define rescue configurations to test
    # Based on rescue budget analysis:
    # G30 needs cheap(40), M05 needs fidelity(27), N91 needs log_models(29), N97 needs fidelity(49)

    rescue_orders = [
        # Name, rescue config list
        ("fid→cheap→lm", [("fidelity", 200), ("cheap", 200), ("log_models", 200)]),
        ("cheap→fid→lm", [("cheap", 200), ("fidelity", 200), ("log_models", 200)]),
        ("lm→fid→cheap", [("log_models", 200), ("fidelity", 200), ("cheap", 200)]),
        ("fid→lm→cheap", [("fidelity", 200), ("log_models", 200), ("cheap", 200)]),
        ("cheap→lm→fid", [("cheap", 200), ("log_models", 200), ("fidelity", 200)]),
        ("lm→cheap→fid", [("log_models", 200), ("cheap", 200), ("fidelity", 200)]),
        # With fid_x_cheap (combined signal for G30+M05)
        ("fxc→lm→fid", [("fid_x_cheap", 200), ("log_models", 200), ("fidelity", 200)]),
        ("fxc→fid→lm", [("fid_x_cheap", 200), ("fidelity", 200), ("log_models", 200)]),
        # With sqrt_prior_x_fid
        ("spf→cheap→lm", [("sqrt_prior_x_fid", 200), ("cheap", 200), ("log_models", 200)]),
        # 4 rescue tracks
        ("fid→cheap→lm→fxc", [("fidelity", 200), ("cheap", 200), ("log_models", 200), ("fid_x_cheap", 200)]),
        ("cheap→fid→lm→spf", [("cheap", 200), ("fidelity", 200), ("log_models", 200), ("sqrt_prior_x_fid", 200)]),
    ]

    for main_size in [60, 65, 70, 75, 80, 85, 90]:
        print(f"\n  --- Main={main_size} ---")
        for label, rescue in rescue_orders:
            for cap in range(90, 151, 5):
                h, mm, avg_sz, max_sz = eval_config(data, MAIN_W, main_size, rescue, cap)
                must_m = sorted(set(mm) & MUST_INCLUDE)
                g30 = "G30" not in mm
                if h >= 74 and g30:
                    print(f"    {label} cap={cap}: {h}/{total} must_miss={must_m} avg={avg_sz:.0f} max={max_sz}")
                    break  # Found best cap for this config, move on

    # === Detailed progression for best configs ===
    print("\n" + "=" * 80)
    print("DETAILED PROGRESSION: Best configs at each cap")
    print("=" * 80)

    for main_size in [70, 75, 80]:
        for label, rescue in [
            ("fid→cheap→lm", [("fidelity", 200), ("cheap", 200), ("log_models", 200)]),
            ("cheap→fid→lm", [("cheap", 200), ("fidelity", 200), ("log_models", 200)]),
            ("fid→lm→cheap", [("fidelity", 200), ("log_models", 200), ("cheap", 200)]),
        ]:
            print(f"\n  Main={main_size}, rescue={label}:")
            for cap in range(90, 171, 5):
                h, mm, avg_sz, max_sz = eval_config(data, MAIN_W, main_size, rescue, cap)
                must_m = sorted(set(mm) & MUST_INCLUDE)
                g30 = "G30" not in mm
                print(f"    cap={cap}: {h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'} avg={avg_sz:.0f}")
                if h >= 76 and g30:
                    break

    # === Find absolute minimum cap for 75/80 with G30 ===
    print("\n" + "=" * 80)
    print("MINIMUM CAP for 75/80 with G30")
    print("=" * 80)

    best_cap = 999
    best_label = None
    for main_size in range(50, 91, 5):
        for label, rescue in rescue_orders:
            for cap in range(90, 200):
                h, mm, avg_sz, max_sz = eval_config(data, MAIN_W, main_size, rescue, cap)
                g30 = "G30" not in mm
                if h >= 75 and g30 and cap < best_cap:
                    best_cap = cap
                    best_label = f"main={main_size} rescue={label}"
                    print(f"  Found: {best_label} cap={cap}: {h}/{total} avg={avg_sz:.0f} max={max_sz} mm={sorted(set(mm) & MUST_INCLUDE)}")
                    break  # Found this config's min cap

    if best_label:
        print(f"\n  BEST: {best_label} at cap={best_cap}")

    # === Also test: pure multi-track shortlist from agent.py ===
    print("\n" + "=" * 80)
    print("COMPARISON: Original multi-track round-robin")
    print("=" * 80)

    from experiments.contribution3.transfer.eval.offline_sim_shortlist_80 import load_and_precompute
    track_data = load_and_precompute()
    for cap in range(90, 201, 5):
        # Use large track sizes
        h = sum(1 for d in track_data
                if d.oracle_in_shortlist(3, 54, 45, 65, 104, cap))
        mm = [d.tid for d in track_data
              if not d.oracle_in_shortlist(3, 54, 45, 65, 104, cap) and d.tid in MUST_INCLUDE]
        g30 = "G30" not in mm
        if h >= 72 or g30:
            print(f"  rr cap={cap}: {h}/{total} must_miss={sorted(mm)} G30={'OK' if g30 else 'MISS'}")
        if h >= 76:
            break


if __name__ == "__main__":
    main()
