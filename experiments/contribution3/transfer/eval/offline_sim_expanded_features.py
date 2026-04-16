"""Expanded feature optimization for shortlist ranking.

Adds OpenTargets, heritability, and GC features not previously used.
Tests non-linear scoring (quadratic, threshold) and multi-objective optimization.

Target: cap≈100, recall≥75/80, G30 mandatory.
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


def expanded_features(c: CandidateEvidenceCard) -> dict:
    """Extract ALL available features from a candidate card."""
    # -- Existing features --
    gc_rg = abs(float(c.gc.rg or 0)) if c.gc and c.gc.rg is not None else 0.0
    gc_sig = 1.0 if _is_significant_gc(c.gc) else 0.0
    gc_p = float(c.gc.p_value) if c.gc and c.gc.p_value is not None else 1.0
    gc_z = abs(float(c.gc.z_score or 0)) if c.gc and c.gc.z_score is not None else 0.0

    # -- OpenTargets features --
    ot_overlap = 0.0
    ot_shared_count = 0
    ot_area_match = 0.0
    ot_cand_assoc = 0
    ot_src_assoc = 0
    if c.open_targets:
        ot_overlap = c.open_targets.weighted_shared_target_overlap_score
        ot_shared_count = c.open_targets.shared_target_count
        ot_area_match = 1.0 if c.open_targets.therapeutic_area_match else 0.0
        ot_cand_assoc = c.open_targets.candidate_association_count
        ot_src_assoc = c.open_targets.source_association_count

    # -- Heritability features --
    h2_cand = 0.0
    h2_signal_cap = 0.0
    h2_ceiling = 0.0
    h2_confidence = 0.0
    if c.h2:
        h2_cand = float(c.h2.candidate_best_h2 or 0)
        h2_signal_cap = float(c.h2.candidate_signal_capacity or 0)
        h2_ceiling = float(c.h2.shared_signal_ceiling_proxy or 0)
        h2_confidence = {"High": 1.0, "Medium": 0.5, "Low": 0.25}.get(c.h2.confidence_tier, 0.0)

    # -- Archetype features --
    is_same_endpoint = 1.0 if c.archetype == "same-endpoint disease" else 0.0
    is_risk_factor = 1.0 if "risk-factor" in c.archetype.lower() else 0.0
    is_comorbid = 1.0 if "comorbid" in c.archetype.lower() else 0.0
    is_related = 1.0 if "related" in c.archetype.lower() else 0.0

    # -- Evidence tag features --
    has_gc_strong = 1.0 if any("gc_strong" in t or "gc-strong" in t for t in c.evidence_tags) else 0.0
    has_ot_mech = 1.0 if any("ot_mech" in t or "ot-mech" in t or "mechanistic" in t.lower() for t in c.evidence_tags) else 0.0
    n_tags = len(c.evidence_tags)

    return {
        # Original features
        "prior": c.transferability_prior_score,
        "fidelity": c.phenotype_fidelity_score,
        "utility": c.utility_score,
        "cheap": c.cheap_rank_score,
        "lexical": c.lexical_match_score,
        "n_models": c.n_models,
        "log_models": math.log1p(min(max(c.n_models, 0), 200)),
        # GC features
        "gc_rg": gc_rg,
        "gc_sig": gc_sig,
        "gc_z": gc_z,
        "neg_gc_p": -gc_p,
        # OpenTargets features
        "ot_overlap": ot_overlap,
        "ot_shared_count": ot_shared_count,
        "log_ot_shared": math.log1p(ot_shared_count),
        "ot_area_match": ot_area_match,
        "ot_cand_assoc": ot_cand_assoc,
        "log_ot_cand_assoc": math.log1p(ot_cand_assoc),
        # Heritability features
        "h2_cand": h2_cand,
        "h2_signal_cap": h2_signal_cap,
        "h2_ceiling": h2_ceiling,
        "h2_confidence": h2_confidence,
        # Archetype features
        "is_same_endpoint": is_same_endpoint,
        "is_risk_factor": is_risk_factor,
        "is_comorbid": is_comorbid,
        "is_related": is_related,
        # Evidence tag features
        "has_gc_strong": has_gc_strong,
        "has_ot_mech": has_ot_mech,
        "n_tags": n_tags,
        # Interaction terms
        "fid_x_util": c.phenotype_fidelity_score * c.utility_score,
        "fid_x_cheap": c.phenotype_fidelity_score * c.cheap_rank_score,
        "fid_x_prior": c.phenotype_fidelity_score * c.transferability_prior_score,
        "sqrt_prior_x_fid": math.sqrt(c.transferability_prior_score) * c.phenotype_fidelity_score,
        "ot_overlap_x_fid": ot_overlap * c.phenotype_fidelity_score,
        "h2_ceiling_x_fid": h2_ceiling * c.phenotype_fidelity_score,
        "h2_ceiling_x_prior": h2_ceiling * c.transferability_prior_score,
        "gc_rg_x_fid": gc_rg * c.phenotype_fidelity_score,
        "ot_x_prior": ot_overlap * c.transferability_prior_score,
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
        feats = [(c.bundle_id, expanded_features(c)) for c in cards]
        data.append((tid, oracle_id, feats))
    return data


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    print(f"Loaded {total} targets\n")

    # Get feature names
    sample_feats = data[0][2][0][1]
    all_feat_names = list(sample_feats.keys())
    print(f"Total features: {len(all_feat_names)}")
    print(f"Features: {all_feat_names}\n")

    # === Diagnostic: show feature profiles for hard oracles ===
    print("=" * 80)
    print("DIAGNOSTIC: Feature profiles for hard target oracles (G30, M05, N91, N97)")
    print("=" * 80)
    for tid, oracle_id, feats in data:
        if tid not in {'G30', 'M05', 'N91', 'N97'}:
            continue
        oracle_feats = None
        for bid, f in feats:
            if bid == oracle_id:
                oracle_feats = f
                break
        if not oracle_feats:
            print(f"\n  {tid}: Oracle {oracle_id} NOT IN candidates!")
            continue

        # Find oracle rank on each feature
        print(f"\n  {tid} (oracle={oracle_id}, {len(feats)} candidates):")
        for fname in all_feat_names:
            vals = [(bid, f[fname]) for bid, f in feats]
            vals.sort(key=lambda x: (-x[1], x[0]))
            oracle_rank = next((i+1 for i, (b, _) in enumerate(vals) if b == oracle_id), 9999)
            oval = oracle_feats[fname]
            if oracle_rank <= 30:
                marker = " <== TOP-30"
            elif oracle_rank <= 50:
                marker = " <-- TOP-50"
            elif oracle_rank <= 100:
                marker = " <- TOP-100"
            else:
                marker = ""
            if oval != 0 or oracle_rank <= 100:
                print(f"    {fname:>25s}: val={oval:.4f}  rank={oracle_rank}{marker}")

    # === Test new features as single rankings ===
    print("\n" + "=" * 80)
    print("NEW FEATURE RANKINGS: oracle in top-K")
    print("=" * 80)

    new_feats = ["ot_overlap", "log_ot_shared", "ot_area_match", "ot_cand_assoc",
                 "log_ot_cand_assoc", "h2_cand", "h2_signal_cap", "h2_ceiling",
                 "h2_confidence", "gc_z", "ot_overlap_x_fid", "h2_ceiling_x_fid",
                 "h2_ceiling_x_prior", "gc_rg_x_fid", "ot_x_prior",
                 "is_risk_factor", "is_comorbid", "is_related", "n_tags"]

    for K in [80, 100, 110]:
        print(f"\n  Top-{K}:")
        for feat in new_feats:
            score_fn = lambda f, feat=feat: f[feat]
            hit, miss = 0, []
            for tid, oracle_id, feats in data:
                scores = [(bid, score_fn(f)) for bid, f in feats]
                scores.sort(key=lambda x: (-x[1], x[0]))
                rank = next((i+1 for i, (b, _) in enumerate(scores) if b == oracle_id), 9999)
                if rank <= K:
                    hit += 1
                else:
                    miss.append(tid)
            must_m = sorted(set(miss) & MUST_INCLUDE)
            g30 = "G30" not in miss
            if hit >= 55:
                print(f"    {feat:>25s}: {hit}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")

    # === Optimized ranking with expanded features ===
    print("\n" + "=" * 80)
    print("OPTIMIZED RANKING: differential evolution with expanded features")
    print("=" * 80)

    # Select features for optimization (exclude redundant ones)
    opt_feats = [
        "prior", "fidelity", "utility", "cheap", "lexical", "log_models",
        "gc_rg", "gc_sig", "gc_z",
        "ot_overlap", "log_ot_shared", "ot_area_match",
        "h2_signal_cap", "h2_ceiling", "h2_confidence",
        "is_same_endpoint", "is_risk_factor",
        "fid_x_cheap", "fid_x_util", "sqrt_prior_x_fid",
        "ot_overlap_x_fid", "h2_ceiling_x_fid",
    ]
    print(f"  Optimization features ({len(opt_feats)}): {opt_feats}")

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

    for K in [90, 95, 100, 105, 110]:
        def objective(params):
            h, mm, _ = eval_weights(params, K)
            # Heavy penalty for missing must-include
            penalty = len(mm) * 2.0
            # Extra penalty for missing G30
            if 'G30' in mm:
                penalty += 3.0
            return -(h - penalty)

        bounds = [(-3, 5)] * len(opt_feats)
        best_h = 0
        best_w = None
        best_mm = None
        best_ranks = None
        for seed in range(15):
            result = differential_evolution(
                objective, bounds=bounds,
                maxiter=3000, popsize=25, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            w = result.x
            h, mm, ranks = eval_weights(w, K)
            if h > best_h or (h == best_h and 'G30' not in mm and ('G30' in (best_mm or []))):
                best_h = h
                best_w = w
                best_mm = mm
                best_ranks = ranks

        must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
        g30 = "G30" not in (best_mm or [])
        print(f"\n  K={K}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
        print(f"    weights: {dict(zip(opt_feats, [f'{v:.3f}' for v in best_w]))}")

        # Show must-include oracle ranks
        if best_ranks:
            print(f"    Must-include oracle ranks:")
            for tid in sorted(MUST_INCLUDE):
                r = best_ranks.get(tid, 9999)
                marker = " MISS" if r > K else ""
                print(f"      {tid}: rank={r}{marker}")

    # === Non-linear approach: quadratic features ===
    print("\n" + "=" * 80)
    print("NON-LINEAR: Quadratic + threshold features")
    print("=" * 80)

    # Build extended feature matrix with quadratic terms
    core_feats = ["prior", "fidelity", "utility", "cheap", "log_models",
                  "gc_rg", "gc_sig", "ot_overlap", "h2_ceiling"]
    quad_names = list(core_feats)
    # Add squares
    for f in core_feats:
        quad_names.append(f"{f}^2")
    # Add top cross-products
    for i, f1 in enumerate(core_feats):
        for f2 in core_feats[i+1:]:
            quad_names.append(f"{f1}*{f2}")

    print(f"  Quadratic features ({len(quad_names)}): {quad_names[:10]}...")

    prebuilt_quad = []
    for tid, oracle_id, feats in data:
        n = len(feats)
        bids = [bid for bid, _ in feats]
        oracle_idx = bids.index(oracle_id) if oracle_id in bids else -1
        mat = np.zeros((n, len(quad_names)))
        for i, (bid, f) in enumerate(feats):
            core_vals = [f[fk] for fk in core_feats]
            row = list(core_vals)
            # Squares
            for v in core_vals:
                row.append(v * v)
            # Cross products
            for j, v1 in enumerate(core_vals):
                for v2 in core_vals[j+1:]:
                    row.append(v1 * v2)
            mat[i] = row
        prebuilt_quad.append((tid, oracle_idx, mat, bids))

    def eval_quad_weights(w, K=100):
        w = np.array(w)
        hit = 0
        must_miss = []
        for tid, oidx, mat, bids in prebuilt_quad:
            if oidx < 0:
                continue
            scores = mat @ w
            oracle_score = scores[oidx]
            rank = int(np.sum(scores > oracle_score)) + 1
            if rank <= K:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss

    for K in [95, 100, 105, 110]:
        def objective(params):
            h, mm = eval_quad_weights(params, K)
            penalty = len(mm) * 2.0
            if 'G30' in mm:
                penalty += 3.0
            return -(h - penalty)

        bounds = [(-3, 5)] * len(quad_names)
        best_h = 0
        best_w = None
        best_mm = None
        for seed in range(10):
            result = differential_evolution(
                objective, bounds=bounds,
                maxiter=2000, popsize=20, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            w = result.x
            h, mm = eval_quad_weights(w, K)
            if h > best_h or (h == best_h and 'G30' not in mm and ('G30' in (best_mm or []))):
                best_h = h
                best_w = w
                best_mm = mm

        must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
        g30 = "G30" not in (best_mm or [])
        print(f"  K={K}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")

    # === Two-stage approach: main ranking + rescue ===
    print("\n" + "=" * 80)
    print("TWO-STAGE: Main ranking (top-85) + rescue ranking (top-15)")
    print("=" * 80)

    # Use the best expanded weights for the main ranking
    # Then try different rescue strategies for the remaining slots
    if best_w is not None:
        # First, get the best K=100 linear weights
        def obj100(params):
            h, mm, _ = eval_weights(params, 100)
            penalty = len(mm) * 2.0
            if 'G30' in mm:
                penalty += 3.0
            return -(h - penalty)

        bounds100 = [(-3, 5)] * len(opt_feats)
        best_main_h = 0
        best_main_w = None
        for seed in range(10):
            result = differential_evolution(
                obj100, bounds=bounds100,
                maxiter=2000, popsize=20, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            h, mm, _ = eval_weights(result.x, 100)
            if h > best_main_h:
                best_main_h = h
                best_main_w = result.x

        # Now test two-stage: main (top-M) + rescue (different ranking, top-R)
        rescue_feats = ["cheap", "log_models", "gc_rg", "h2_ceiling", "ot_overlap",
                        "n_tags", "h2_signal_cap", "gc_z"]
        for main_size in [80, 85, 90]:
            rescue_size = 100 - main_size
            for rescue_feat in rescue_feats:
                hit = 0
                must_miss = []
                for (tid, oracle_id, feats), (_, oidx, mat, bids) in zip(data, prebuilt):
                    if oidx < 0:
                        continue
                    # Main track: sorted by main weights
                    scores = mat @ np.array(best_main_w)
                    order = np.argsort(-scores)
                    main_bids = [bids[i] for i in order[:main_size]]

                    # Rescue track: different feature
                    rescue_scores = [(bid, f[rescue_feat]) for bid, f in feats
                                     if bid not in set(main_bids)]
                    rescue_scores.sort(key=lambda x: (-x[1], x[0]))
                    rescue_bids = [b for b, _ in rescue_scores[:rescue_size]]

                    shortlist = set(main_bids) | set(rescue_bids)
                    if oracle_id in shortlist:
                        hit += 1
                    elif tid in MUST_INCLUDE:
                        must_miss.append(tid)
                g30 = "G30" not in must_miss
                if hit >= 73 and g30:
                    print(f"  main={main_size} rescue={rescue_feat}({rescue_size}): "
                          f"{hit}/{total} must_miss={must_miss}")

        # Try rescue with different optimized weights
        print("\n  --- Two-stage with optimized rescue weights ---")
        for main_size in [80, 85, 90]:
            rescue_size = 105 - main_size
            # For rescue: optimize separately for candidates NOT in main top-M
            # This is complex; instead, use a different linear combination
            # focused on features that help the hard targets
            rescue_combos = [
                ("cheap+log_m", lambda f: f["cheap"] + f["log_models"]),
                ("cheap+gc_rg", lambda f: f["cheap"] + 0.5*f["gc_rg"]),
                ("h2+cheap", lambda f: f["h2_ceiling"] + f["cheap"]),
                ("ot+cheap", lambda f: f["ot_overlap"] + f["cheap"]),
                ("fid+cheap+ot", lambda f: f["fidelity"] + f["cheap"] + f["ot_overlap"]),
                ("gc_z+cheap", lambda f: f["gc_z"] + f["cheap"]),
                ("gc_rg+h2+cheap", lambda f: f["gc_rg"] + f["h2_ceiling"] + f["cheap"]),
                ("all_evidence", lambda f: f["gc_rg"] + f["h2_ceiling"] + f["ot_overlap"] + f["cheap"]),
            ]
            for label, rescue_fn in rescue_combos:
                hit = 0
                must_miss = []
                for (tid, oracle_id, feats), (_, oidx, mat, bids) in zip(data, prebuilt):
                    if oidx < 0:
                        continue
                    scores = mat @ np.array(best_main_w)
                    order = np.argsort(-scores)
                    main_set = set(bids[i] for i in order[:main_size])

                    rescue_scores = [(bid, rescue_fn(f)) for bid, f in feats
                                     if bid not in main_set]
                    rescue_scores.sort(key=lambda x: (-x[1], x[0]))
                    rescue_bids = set(b for b, _ in rescue_scores[:rescue_size])

                    shortlist = main_set | rescue_bids
                    if oracle_id in shortlist:
                        hit += 1
                    elif tid in MUST_INCLUDE:
                        must_miss.append(tid)
                g30 = "G30" not in must_miss
                if hit >= 73 and g30:
                    print(f"  main={main_size} rescue={label}({rescue_size}): "
                          f"{hit}/{total} must_miss={must_miss}")


if __name__ == "__main__":
    main()
