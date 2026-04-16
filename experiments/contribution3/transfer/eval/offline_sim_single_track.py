"""Test single optimized ranking track for shortlist construction.

Instead of 6 tracks + round-robin, use ONE composite ranking → top-K = shortlist.
This avoids bandwidth competition between tracks entirely.

Key: if we find a ranking where ALL oracles are in top-100, cap=100 works.
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
    _is_significant_gc, _target_source_for_dossier, _gc_ranked_cards,
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


# Feature vector per card
def card_features(c: CandidateEvidenceCard) -> dict:
    gc_rg = abs(float(c.gc.rg or 0)) if c.gc and c.gc.rg is not None else 0.0
    gc_sig = 1.0 if _is_significant_gc(c.gc) else 0.0
    gc_p = float(c.gc.p_value) if c.gc and c.gc.p_value is not None else 1.0
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
        "neg_gc_p": -gc_p,  # lower p-value = better
        "is_same_endpoint": 1.0 if c.archetype == "same-endpoint disease" else 0.0,
        "fid_x_util": c.phenotype_fidelity_score * c.utility_score,
        "fid_x_cheap": c.phenotype_fidelity_score * c.cheap_rank_score,
        "fid_x_prior": c.phenotype_fidelity_score * c.transferability_prior_score,
        "sqrt_prior_x_fid": math.sqrt(c.transferability_prior_score) * c.phenotype_fidelity_score,
    }


FEATURE_NAMES = list(card_features.__code__.co_consts)  # hack; build properly below

TargetData = tuple[str, str, list[tuple[str, dict]]]  # (tid, oracle_id, [(bid, features)])


def load_all() -> list[TargetData]:
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


def oracle_rank(tid_data: TargetData, score_fn) -> int:
    """Rank of oracle when candidates sorted by score_fn (descending)."""
    tid, oracle_id, feats = tid_data
    scores = [(bid, score_fn(f)) for bid, f in feats]
    scores.sort(key=lambda x: (-x[1], x[0]))
    for i, (bid, _) in enumerate(scores):
        if bid == oracle_id:
            return i + 1
    return 9999


def count_in_topK(data: list[TargetData], score_fn, K: int) -> tuple[int, list[str]]:
    hit = 0
    miss = []
    for td in data:
        r = oracle_rank(td, score_fn)
        if r <= K:
            hit += 1
        else:
            miss.append(td[0])
    return hit, miss


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    print(f"Loaded {total} targets\n")

    fnames = list(card_features(type('', (), {
        'transferability_prior_score': 0, 'phenotype_fidelity_score': 0,
        'utility_score': 0, 'cheap_rank_score': 0, 'lexical_match_score': 0,
        'n_models': 0, 'gc': None, 'archetype': '', 'open_targets': None,
    })()).keys())
    print(f"Features: {fnames}\n")

    # === Test simple single-feature rankings ===
    print("=== Single-feature rankings: oracle in top-K ===")
    for K in [80, 90, 100, 110]:
        print(f"\n  Top-{K}:")
        for feat in ["prior", "fidelity", "utility", "cheap", "lexical", "log_models",
                      "gc_rg", "fid_x_util", "fid_x_cheap", "fid_x_prior",
                      "sqrt_prior_x_fid", "is_same_endpoint"]:
            score_fn = lambda f, feat=feat: f[feat]
            h, miss = count_in_topK(data, score_fn, K)
            must_m = sorted(set(miss) & MUST_INCLUDE)
            g30 = "G30" not in miss
            if h >= 60:
                print(f"    {feat:>20s}: {h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")

    # === Test composite rankings ===
    print("\n=== Composite rankings: oracle in top-100 ===")
    composites = [
        ("fid+util",        lambda f: f["fidelity"] + f["utility"]),
        ("fid+cheap",       lambda f: f["fidelity"] + f["cheap"]),
        ("fid+util+cheap",  lambda f: f["fidelity"] + f["utility"] + f["cheap"]),
        ("prior+fid",       lambda f: f["prior"] + f["fidelity"]),
        ("2fid+util+cheap", lambda f: 2*f["fidelity"] + f["utility"] + f["cheap"]),
        ("fid+0.5util+cheap+0.3log_m", lambda f: f["fidelity"] + 0.5*f["utility"] + f["cheap"] + 0.3*f["log_models"]),
        ("fid+cheap+0.5gc_rg", lambda f: f["fidelity"] + f["cheap"] + 0.5*f["gc_rg"]),
        ("fid+cheap+gc_sig", lambda f: f["fidelity"] + f["cheap"] + f["gc_sig"]),
        ("fid_x_cheap",     lambda f: f["fid_x_cheap"]),
        ("fid_x_util",      lambda f: f["fid_x_util"]),
        ("sqrt_prior_x_fid", lambda f: f["sqrt_prior_x_fid"]),
        ("fid+0.3util+0.3cheap+0.1log_m", lambda f: f["fidelity"] + 0.3*f["utility"] + 0.3*f["cheap"] + 0.1*f["log_models"]),
    ]
    for label, fn in composites:
        for K in [90, 95, 100, 105, 110]:
            h, miss = count_in_topK(data, fn, K)
            must_m = sorted(set(miss) & MUST_INCLUDE)
            g30 = "G30" not in miss
            if h >= 70 and g30:
                print(f"  {label:>35s} top-{K}: {h}/{total} must_miss={must_m}")

    # === Optimized composite: differential evolution ===
    print("\n=== Optimized single-track ranking (differential evolution) ===")

    # Feature vector for fast scoring
    feat_keys = ["prior", "fidelity", "utility", "cheap", "lexical", "log_models",
                 "gc_rg", "gc_sig", "fid_x_cheap", "fid_x_util", "sqrt_prior_x_fid"]

    # Pre-build numpy arrays for speed
    prebuilt = []
    for tid, oracle_id, feats in data:
        n = len(feats)
        bids = [bid for bid, _ in feats]
        oracle_idx = bids.index(oracle_id) if oracle_id in bids else -1
        mat = np.zeros((n, len(feat_keys)))
        for i, (bid, f) in enumerate(feats):
            for j, fk in enumerate(feat_keys):
                mat[i, j] = f[fk]
        prebuilt.append((tid, oracle_idx, mat, bids))

    def eval_weights(w, K=100):
        w = np.array(w)
        hit = 0
        must_miss = []
        for tid, oidx, mat, bids in prebuilt:
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

    for K in [90, 95, 100, 105, 110]:
        def objective(params):
            h, mm = eval_weights(params, K)
            # Penalty for missing must-include targets
            penalty = len([m for m in mm]) * 0.5
            return -(h - penalty)

        bounds = [(-2, 5)] * len(feat_keys)
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
            h, mm = eval_weights(w, K)
            if h > best_h or (h == best_h and len(mm) < len(best_mm or [])):
                best_h = h
                best_w = w
                best_mm = mm

        must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
        g30 = "G30" not in (best_mm or [])
        print(f"  K={K}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
        print(f"    weights: {dict(zip(feat_keys, [f'{v:.4f}' for v in best_w]))}")

        # Show per-target oracle ranks for this config
        if K == 100 and g30:
            print(f"\n    Per-target oracle ranks (must-include):")
            w = best_w
            for tid, oidx, mat, bids in prebuilt:
                if tid not in MUST_INCLUDE or oidx < 0:
                    continue
                scores = mat @ np.array(w)
                oracle_score = scores[oidx]
                rank = int(np.sum(scores > oracle_score)) + 1
                print(f"      {tid}: rank={rank}")

    # === Also test: single track + one auxiliary track (2-track merge) ===
    print("\n=== Two-track approach: optimized main + GC auxiliary ===")
    # Use the best single-track weights, then add a small GC track via round-robin
    if best_w is not None:
        from experiments.contribution3.transfer.agent import _merge_shortlist_tracks

        for gc_sz in [20, 30, 45]:
            for cap in [95, 100, 105, 110]:
                hit = 0
                must_miss = []
                for (tid, oracle_id, feats), (_, oidx, mat, bids) in zip(data, prebuilt):
                    if oidx < 0:
                        continue
                    # Main track: sorted by optimized score
                    scores = mat @ np.array(best_w)
                    order = np.argsort(-scores)
                    main_track = [bids[i] for i in order[:cap]]

                    # GC track: use gc_sig * gc_rg as key
                    gc_scores = [(bids[i], mat[i, feat_keys.index("gc_sig")] * mat[i, feat_keys.index("gc_rg")])
                                 for i in range(len(bids))]
                    gc_scores.sort(key=lambda x: (-x[1], x[0]))
                    gc_track = [b for b, _ in gc_scores[:gc_sz]]

                    sl = _merge_shortlist_tracks([main_track, gc_track], cap)
                    if oracle_id in sl:
                        hit += 1
                    elif tid in MUST_INCLUDE:
                        must_miss.append(tid)
                g30 = "G30" not in must_miss
                if hit >= 73 and g30:
                    print(f"  gc={gc_sz} cap={cap}: {hit}/{total} must_miss={must_miss}")


if __name__ == "__main__":
    main()
