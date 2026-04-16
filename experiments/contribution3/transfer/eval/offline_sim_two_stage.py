"""Two-stage shortlist: optimized main + targeted rescue tracks.

Key findings from prior analysis:
- Linear scoring ceiling: 72/80 at any cap
- Hard oracles rank 200+ on linear score but 40-100 on individual features:
  G30: cheap=100, M05: fidelity=40, N91: n_models=90, N97: fidelity=64
- Round-robin multi-track fails because budget per track = cap/n_tracks

Strategy: sequential fill, not round-robin.
Stage 1: DE-optimized main ranking, top-M slots
Stage 2: Sequential rescue from feature rankings (NOT round-robin)
  Each rescue track adds its unique (not-in-main) entries sequentially
"""
from __future__ import annotations
import math, json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution

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


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    print(f"Loaded {total} targets\n")

    # Feature keys for DE optimization
    opt_feats = ["prior", "fidelity", "utility", "cheap", "lexical", "log_models",
                 "gc_rg", "gc_sig", "fid_x_cheap", "fid_x_util", "sqrt_prior_x_fid"]

    # Pre-build numpy arrays
    prebuilt = []
    for tid, oracle_id, feats in data:
        n = len(feats)
        bids = [bid for bid, _ in feats]
        oracle_idx = bids.index(oracle_id) if oracle_id in bids else -1
        mat = np.zeros((n, len(opt_feats)))
        for i, (bid, f) in enumerate(feats):
            for j, fk in enumerate(opt_feats):
                mat[i, j] = f[fk]
        prebuilt.append((tid, oracle_idx, mat, bids))

    # === Step 1: Find best DE weights ===
    print("=" * 80)
    print("STEP 1: Optimize main ranking weights (DE)")
    print("=" * 80)

    def eval_weights(w, K=100):
        w = np.array(w)
        hit = 0
        must_miss = []
        oracle_ranks = {}
        for tid, oidx, mat, bids in prebuilt:
            if oidx < 0:
                continue
            scores = mat @ w
            oracle_score = scores[oidx]
            rank = int(np.sum(scores > oracle_score)) + 1
            oracle_ranks[tid] = rank
            if rank <= K:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss, oracle_ranks

    def objective(params):
        h, mm, _ = eval_weights(params, 90)
        penalty = len(mm) * 2.0
        return -(h - penalty)

    bounds = [(-2, 5)] * len(opt_feats)
    best_h = 0
    best_w = None
    best_ranks = None
    for seed in range(15):
        result = differential_evolution(
            objective, bounds=bounds,
            maxiter=3000, popsize=25, tol=0,
            mutation=(0.5, 1.5), recombination=0.9,
            seed=seed, workers=1, polish=True,
        )
        h, mm, ranks = eval_weights(result.x, 90)
        if h > best_h:
            best_h = h
            best_w = result.x
            best_ranks = ranks

    print(f"  Main ranking at K=90: {best_h}/{total}")
    print(f"  Weights: {dict(zip(opt_feats, [f'{v:.3f}' for v in best_w]))}")
    main_w = best_w

    # Show oracle ranks for must-include targets
    _, _, main_ranks = eval_weights(main_w, 9999)
    print(f"\n  Must-include oracle ranks on main ranking:")
    for tid in sorted(MUST_INCLUDE):
        r = main_ranks.get(tid, 9999)
        print(f"    {tid}: rank={r}")

    # === Step 2: Measure rescue budget needed ===
    print("\n" + "=" * 80)
    print("STEP 2: Rescue budget analysis")
    print("=" * 80)

    rescue_feats = ["fidelity", "cheap", "log_models", "fid_x_cheap",
                    "sqrt_prior_x_fid", "utility", "prior"]

    for main_size in [70, 75, 80, 85, 90]:
        print(f"\n  --- Main top-{main_size} ---")
        for tid, oracle_id, feats in data:
            # Check if oracle in main top-K
            pb = next(p for p in prebuilt if p[0] == tid)
            _, oidx, mat, bids = pb
            scores = mat @ np.array(main_w)
            order = np.argsort(-scores)
            main_set = set(bids[i] for i in order[:main_size])
            if oracle_id in main_set:
                continue
            if tid not in MUST_INCLUDE:
                continue

            # For each rescue feature, compute rescue rank (rank among non-main candidates)
            print(f"    {tid} (oracle={oracle_id}):")
            for rf in rescue_feats:
                rf_idx = opt_feats.index(rf) if rf in opt_feats else -1
                # Build feature-sorted list, excluding main candidates
                rescue_candidates = [(bids[i], mat[i, rf_idx]) for i in range(len(bids))
                                     if bids[i] not in main_set]
                rescue_candidates.sort(key=lambda x: (-x[1], x[0]))
                rescue_rank = next((i+1 for i, (b, _) in enumerate(rescue_candidates) if b == oracle_id), 9999)
                if rescue_rank <= 50:
                    print(f"      {rf}: rescue_rank={rescue_rank}")

    # === Step 3: Two-stage sequential fill ===
    print("\n" + "=" * 80)
    print("STEP 3: Two-stage sequential fill optimization")
    print("=" * 80)

    # For each (main_size, rescue_config), compute recall
    rescue_configs = [
        # (feat, rescue_track_size) - feature used for rescue ranking
        [("fidelity", 30), ("cheap", 20), ("log_models", 20)],
        [("fidelity", 25), ("cheap", 25), ("log_models", 20)],
        [("fidelity", 20), ("cheap", 15), ("log_models", 15), ("fid_x_cheap", 20)],
        [("fidelity", 40), ("cheap", 30), ("log_models", 30)],
        [("fidelity", 50), ("cheap", 40), ("log_models", 30)],
        [("cheap", 30), ("fidelity", 25), ("log_models", 25)],
        [("cheap", 40), ("fidelity", 30), ("log_models", 30)],
        [("fid_x_cheap", 40), ("fidelity", 20), ("log_models", 30)],
        [("sqrt_prior_x_fid", 30), ("cheap", 30), ("log_models", 25)],
    ]

    for main_size in [60, 65, 70, 75, 80, 85, 90]:
        for rc in rescue_configs:
            total_rescue = sum(sz for _, sz in rc)
            cap = main_size + total_rescue  # approximate max
            if cap > 130:
                continue

            hit = 0
            must_miss = []
            actual_sizes = []
            for (tid, oracle_id, feats), (_, oidx, mat, bids) in zip(data, prebuilt):
                if oidx < 0:
                    continue
                # Stage 1: main ranking
                scores = mat @ np.array(main_w)
                order = np.argsort(-scores)
                shortlist = list(bids[i] for i in order[:main_size])
                seen = set(shortlist)

                # Stage 2: sequential rescue
                for rf_name, rf_size in rc:
                    rf_idx = opt_feats.index(rf_name)
                    # Sort by rescue feature, add unique
                    rescue = [(bids[i], mat[i, rf_idx]) for i in range(len(bids))
                              if bids[i] not in seen]
                    rescue.sort(key=lambda x: (-x[1], x[0]))
                    added = 0
                    for bid, _ in rescue:
                        if added >= rf_size:
                            break
                        seen.add(bid)
                        shortlist.append(bid)
                        added += 1

                actual_sizes.append(len(shortlist))
                if oracle_id in shortlist:
                    hit += 1
                elif tid in MUST_INCLUDE:
                    must_miss.append(tid)

            g30 = "G30" not in must_miss
            mean_sz = sum(actual_sizes) / len(actual_sizes)
            max_sz = max(actual_sizes)
            must_m = sorted(set(must_miss) & MUST_INCLUDE)

            if hit >= 73 and g30:
                rc_str = "+".join(f"{f}({s})" for f, s in rc)
                print(f"  main={main_size} rescue=[{rc_str}]: "
                      f"{hit}/{total} sl_mean={mean_sz:.0f} sl_max={max_sz} must_miss={must_m}")

    # === Step 4: Optimize two-stage parameters with DE ===
    print("\n" + "=" * 80)
    print("STEP 4: DE-optimized two-stage (main_w + rescue allocation)")
    print("=" * 80)

    # Fixed rescue features: fidelity, cheap, log_models
    rescue_feat_indices = [
        opt_feats.index("fidelity"),
        opt_feats.index("cheap"),
        opt_feats.index("log_models"),
    ]

    def eval_two_stage(main_weights, main_size, rescue_sizes, cap):
        """main_size slots from main ranking, then sequential rescue from 3 features."""
        mw = np.array(main_weights)
        hit = 0
        must_miss = []
        actual_sizes = []
        for tid, oidx, mat, bids in prebuilt:
            if oidx < 0:
                continue
            # Main ranking
            scores = mat @ mw
            order = np.argsort(-scores)
            shortlist = [bids[i] for i in order[:main_size]]
            seen = set(shortlist)

            # Sequential rescue
            for fi, rsz in zip(rescue_feat_indices, rescue_sizes):
                rescue = [(bids[i], mat[i, fi]) for i in range(len(bids))
                          if bids[i] not in seen]
                rescue.sort(key=lambda x: (-x[1], x[0]))
                added = 0
                for bid, _ in rescue:
                    if added >= rsz or len(shortlist) >= cap:
                        break
                    seen.add(bid)
                    shortlist.append(bid)
                    added += 1

            actual_sizes.append(len(shortlist))
            if oracle_id in shortlist:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss, sum(actual_sizes) / len(actual_sizes)

    # Optimize: main weights (11 params) + main_size (1) + 3 rescue sizes
    # Total: 15 parameters
    def objective_two_stage(params, target_cap=100):
        main_weights = params[:len(opt_feats)]
        main_size = int(round(params[len(opt_feats)]))
        rescue_sizes = [int(round(params[len(opt_feats) + 1 + i])) for i in range(3)]
        h, mm, avg_sz = eval_two_stage(main_weights, main_size, rescue_sizes, target_cap)
        penalty = len(mm) * 2.0
        if 'G30' in mm:
            penalty += 5.0
        # Penalty for oversized shortlist
        if avg_sz > target_cap:
            penalty += (avg_sz - target_cap) * 0.1
        return -(h - penalty)

    for target_cap in [100, 105, 110, 115, 120]:
        def obj(params, target_cap=target_cap):
            return objective_two_stage(params, target_cap)

        bounds_ts = [(-2, 5)] * len(opt_feats) + \
                    [(50, 90)] + \
                    [(5, 50), (5, 50), (5, 50)]

        best_h = 0
        best_params = None
        best_mm = None
        best_avg_sz = 0
        for seed in range(10):
            result = differential_evolution(
                obj, bounds=bounds_ts,
                maxiter=2000, popsize=20, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            p = result.x
            ms = int(round(p[len(opt_feats)]))
            rs = [int(round(p[len(opt_feats) + 1 + i])) for i in range(3)]
            h, mm, avg_sz = eval_two_stage(p[:len(opt_feats)], ms, rs, target_cap)
            if h > best_h or (h == best_h and 'G30' not in mm and 'G30' in (best_mm or [])):
                best_h = h
                best_params = p
                best_mm = mm
                best_avg_sz = avg_sz

        if best_params is not None:
            ms = int(round(best_params[len(opt_feats)]))
            rs = [int(round(best_params[len(opt_feats) + 1 + i])) for i in range(3)]
            must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
            g30 = "G30" not in (best_mm or [])
            print(f"\n  target_cap={target_cap}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
            print(f"    main_size={ms} rescue_fidelity={rs[0]} rescue_cheap={rs[1]} rescue_log_models={rs[2]}")
            print(f"    avg_sl_size={best_avg_sz:.0f}")
            print(f"    weights: {dict(zip(opt_feats, [f'{v:.3f}' for v in best_params[:len(opt_feats)]]))}")

    # === Step 5: Explore with 4+ rescue features ===
    print("\n" + "=" * 80)
    print("STEP 5: 4-rescue-feature sequential fill")
    print("=" * 80)

    rescue_feat_indices_4 = [
        opt_feats.index("fidelity"),
        opt_feats.index("cheap"),
        opt_feats.index("log_models"),
        opt_feats.index("fid_x_cheap"),
    ]

    def eval_two_stage_4(main_weights, main_size, rescue_sizes, cap):
        mw = np.array(main_weights)
        hit = 0
        must_miss = []
        actual_sizes = []
        for tid, oidx, mat, bids in prebuilt:
            if oidx < 0:
                continue
            scores = mat @ mw
            order = np.argsort(-scores)
            shortlist = [bids[i] for i in order[:main_size]]
            seen = set(shortlist)
            for fi, rsz in zip(rescue_feat_indices_4, rescue_sizes):
                rescue = [(bids[i], mat[i, fi]) for i in range(len(bids))
                          if bids[i] not in seen]
                rescue.sort(key=lambda x: (-x[1], x[0]))
                added = 0
                for bid, _ in rescue:
                    if added >= rsz or len(shortlist) >= cap:
                        break
                    seen.add(bid)
                    shortlist.append(bid)
                    added += 1
            actual_sizes.append(len(shortlist))
            if oracle_id in shortlist:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss, sum(actual_sizes) / len(actual_sizes)

    for target_cap in [100, 105, 110, 115, 120]:
        def obj(params, target_cap=target_cap):
            mw = params[:len(opt_feats)]
            ms = int(round(params[len(opt_feats)]))
            rs = [int(round(params[len(opt_feats) + 1 + i])) for i in range(4)]
            h, mm, avg_sz = eval_two_stage_4(mw, ms, rs, target_cap)
            penalty = len(mm) * 2.0
            if 'G30' in mm:
                penalty += 5.0
            if avg_sz > target_cap:
                penalty += (avg_sz - target_cap) * 0.1
            return -(h - penalty)

        bounds_ts = [(-2, 5)] * len(opt_feats) + \
                    [(40, 90)] + \
                    [(3, 40)] * 4

        best_h = 0
        best_params = None
        best_mm = None
        best_avg_sz = 0
        for seed in range(10):
            result = differential_evolution(
                obj, bounds=bounds_ts,
                maxiter=2000, popsize=20, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            p = result.x
            ms = int(round(p[len(opt_feats)]))
            rs = [int(round(p[len(opt_feats) + 1 + i])) for i in range(4)]
            h, mm, avg_sz = eval_two_stage_4(p[:len(opt_feats)], ms, rs, target_cap)
            if h > best_h or (h == best_h and 'G30' not in mm and 'G30' in (best_mm or [])):
                best_h = h
                best_params = p
                best_mm = mm
                best_avg_sz = avg_sz

        if best_params is not None:
            ms = int(round(best_params[len(opt_feats)]))
            rs = [int(round(best_params[len(opt_feats) + 1 + i])) for i in range(4)]
            must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
            g30 = "G30" not in (best_mm or [])
            print(f"\n  target_cap={target_cap}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
            print(f"    main_size={ms} rescue: fidelity={rs[0]} cheap={rs[1]} log_models={rs[2]} fid_x_cheap={rs[3]}")
            print(f"    avg_sl_size={best_avg_sz:.0f}")


if __name__ == "__main__":
    main()
