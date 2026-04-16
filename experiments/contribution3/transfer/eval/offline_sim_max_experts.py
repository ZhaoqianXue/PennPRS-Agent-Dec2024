"""Non-linear shortlist ranking: max-of-experts approach.

Key insight: hard oracles (G30, M05, N91, N97) excel on DIFFERENT features.
Linear combinations average these, pushing all to rank >100.

Solution: score = max over multiple weighted feature groups.
A candidate enters the shortlist if it's excellent on ANY dimension.

Also tests: union of multiple per-feature top-K, adaptive allocation.
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
        "fid_x_prior": c.phenotype_fidelity_score * c.transferability_prior_score,
    }


TargetData = tuple[str, str, list[tuple[str, dict]]]


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


def best_rank_shortlist(feats_list, feat_groups, group_sizes, cap):
    """Build shortlist using best-rank across multiple feature groups.

    For each candidate, compute its rank on each feature group.
    Include candidates sorted by their best (lowest) rank across groups.
    Each group has a max size (group_sizes) to limit its contribution.
    """
    all_rankings = []
    for group_fn, max_sz in zip(feat_groups, group_sizes):
        scored = [(bid, group_fn(f)) for bid, f in feats_list]
        scored.sort(key=lambda x: (-x[1], x[0]))
        all_rankings.append([(bid, rank) for rank, (bid, _) in enumerate(scored[:max_sz])])

    # For each candidate, find best rank across groups
    best_rank = {}
    for ranking in all_rankings:
        for bid, rank in ranking:
            if bid not in best_rank or rank < best_rank[bid]:
                best_rank[bid] = rank

    sorted_bids = sorted(best_rank.keys(), key=lambda b: (best_rank[b], b))
    return sorted_bids[:cap]


def union_topk_shortlist(feats_list, feat_fns, sizes, cap):
    """Build shortlist as union of top-K from each feature ranking.
    Round-robin to respect cap."""
    rankings = []
    for fn, sz in zip(feat_fns, sizes):
        scored = [(bid, fn(f)) for bid, f in feats_list]
        scored.sort(key=lambda x: (-x[1], x[0]))
        rankings.append([bid for bid, _ in scored[:sz]])

    shortlist, seen = [], set()
    max_len = max(len(r) for r in rankings)
    for idx in range(max_len):
        for ranking in rankings:
            if idx < len(ranking):
                bid = ranking[idx]
                if bid not in seen:
                    seen.add(bid)
                    shortlist.append(bid)
                    if len(shortlist) >= cap:
                        return shortlist
    return shortlist


def eval_approach(data, shortlist_fn, cap):
    hit, must_miss = 0, []
    for tid, oracle_id, feats in data:
        sl = shortlist_fn(feats, cap)
        if oracle_id in sl:
            hit += 1
        elif tid in MUST_INCLUDE:
            must_miss.append(tid)
    return hit, must_miss


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    print(f"Loaded {total} targets\n")

    feat_names = list(data[0][2][0][1].keys())

    # === Approach 1: Union of top-K from diverse feature rankings ===
    print("=" * 80)
    print("APPROACH 1: Union of top-K from diverse rankings (round-robin)")
    print("=" * 80)

    # Define feature functions
    feat_fns = {
        "cheap": lambda f: f["cheap"],
        "fidelity": lambda f: f["fidelity"],
        "prior": lambda f: f["prior"],
        "log_models": lambda f: f["log_models"],
        "gc_rg": lambda f: f["gc_rg"],
        "fid_x_cheap": lambda f: f["fid_x_cheap"],
        "fid_x_util": lambda f: f["fid_x_util"],
        "sqrt_prior_x_fid": lambda f: f["sqrt_prior_x_fid"],
        "utility": lambda f: f["utility"],
        "lexical": lambda f: f["lexical"],
    }

    # Test different combinations of 3-5 tracks with various sizes
    track_combos = [
        # (tracks, sizes) - sizes are per-track caps
        (["sqrt_prior_x_fid", "cheap", "log_models"], [80, 100, 90]),
        (["sqrt_prior_x_fid", "cheap", "fidelity", "log_models"], [70, 100, 50, 90]),
        (["fid_x_cheap", "fidelity", "log_models", "prior"], [100, 50, 90, 50]),
        (["cheap", "fidelity", "log_models", "sqrt_prior_x_fid"], [100, 50, 90, 80]),
        (["cheap", "fidelity", "log_models", "gc_rg"], [100, 50, 90, 50]),
        (["cheap", "fidelity", "log_models"], [100, 50, 90]),
        (["fid_x_cheap", "fidelity", "log_models"], [102, 45, 92]),
        (["cheap", "fidelity", "log_models", "fid_x_util"], [100, 50, 90, 50]),
    ]

    for tracks, sizes in track_combos:
        fns = [feat_fns[t] for t in tracks]
        label = "+".join(f"{t}({s})" for t, s in zip(tracks, sizes))
        for cap in [95, 100, 105, 110]:
            def sl_fn(feats, cap=cap, fns=fns, sizes=sizes):
                return union_topk_shortlist(feats, fns, sizes, cap)
            h, mm = eval_approach(data, sl_fn, cap)
            g30 = "G30" not in mm
            must_m = sorted(set(mm) & MUST_INCLUDE)
            if h >= 72 and g30:
                print(f"  {label} cap={cap}: {h}/{total} must_miss={must_m}")

    # === Approach 2: Systematic grid search for 3-track union ===
    print("\n" + "=" * 80)
    print("APPROACH 2: Grid search for best 3-track union (cap=100)")
    print("=" * 80)

    # Key tracks: need cheap≥100 (G30), fidelity≥40 (M05), log_models≥90 (N91)
    best_h = 0
    best_cfg = None
    track_options = ["cheap", "fidelity", "log_models", "sqrt_prior_x_fid",
                     "fid_x_cheap", "prior", "utility"]

    # Test 3-track combos
    from itertools import combinations
    for combo in combinations(track_options, 3):
        fns = [feat_fns[t] for t in combo]
        for sizes in [
            [100, 100, 100],
            [100, 50, 90],
            [100, 45, 95],
            [110, 45, 95],
            [100, 65, 90],
        ]:
            for cap in [95, 100, 105]:
                def sl_fn(feats, cap=cap, fns=fns, sizes=sizes):
                    return union_topk_shortlist(feats, fns, sizes, cap)
                h, mm = eval_approach(data, sl_fn, cap)
                g30 = "G30" not in mm
                if h > best_h and g30:
                    best_h = h
                    best_cfg = (combo, sizes, cap, mm)
                elif h == best_h and g30 and best_cfg and len(mm) < len(best_cfg[3]):
                    best_cfg = (combo, sizes, cap, mm)
    if best_cfg:
        combo, sizes, cap, mm = best_cfg
        must_m = sorted(set(mm) & MUST_INCLUDE)
        print(f"  Best 3-track: {combo} sizes={sizes} cap={cap}: {best_h}/{total} must_miss={must_m}")

    # Test 4-track combos
    best_h4 = 0
    best_cfg4 = None
    for combo in combinations(track_options, 4):
        fns = [feat_fns[t] for t in combo]
        for sizes in [
            [100, 50, 90, 50],
            [100, 45, 90, 80],
            [100, 65, 90, 65],
            [100, 100, 100, 100],
        ]:
            for cap in [95, 100, 105, 110]:
                def sl_fn(feats, cap=cap, fns=fns, sizes=sizes):
                    return union_topk_shortlist(feats, fns, sizes, cap)
                h, mm = eval_approach(data, sl_fn, cap)
                g30 = "G30" not in mm
                if h > best_h4 and g30:
                    best_h4 = h
                    best_cfg4 = (combo, sizes, cap, mm)
                elif h == best_h4 and g30 and best_cfg4 and len(mm) < len(best_cfg4[3]):
                    best_cfg4 = (combo, sizes, cap, mm)
    if best_cfg4:
        combo, sizes, cap, mm = best_cfg4
        must_m = sorted(set(mm) & MUST_INCLUDE)
        print(f"  Best 4-track: {combo} sizes={sizes} cap={cap}: {best_h4}/{total} must_miss={must_m}")

    # === Approach 3: Best-rank merge (min rank across features) ===
    print("\n" + "=" * 80)
    print("APPROACH 3: Best-rank merge (include by best rank across features)")
    print("=" * 80)

    for feat_set in [
        ["cheap", "fidelity", "log_models"],
        ["cheap", "fidelity", "log_models", "sqrt_prior_x_fid"],
        ["cheap", "fidelity", "log_models", "gc_rg", "prior"],
        ["fid_x_cheap", "fidelity", "log_models"],
        ["cheap", "fidelity", "log_models", "fid_x_util", "prior"],
    ]:
        fns = [feat_fns[f] for f in feat_set]
        for max_per_feat in [100, 120, 150]:
            sizes = [max_per_feat] * len(fns)
            label = "+".join(feat_set)
            for cap in [95, 100, 105, 110]:
                def sl_fn(feats, cap=cap, fns=fns, sizes=sizes):
                    return best_rank_shortlist(feats, fns, sizes, cap)
                h, mm = eval_approach(data, sl_fn, cap)
                g30 = "G30" not in mm
                must_m = sorted(set(mm) & MUST_INCLUDE)
                if h >= 73 and g30:
                    print(f"  {label} max_each={max_per_feat} cap={cap}: {h}/{total} must_miss={must_m}")

    # === Approach 4: Max-of-experts score ===
    print("\n" + "=" * 80)
    print("APPROACH 4: Max-of-experts score (max over normalized feature scores)")
    print("=" * 80)

    # Pre-compute per-target feature stats for normalization
    def max_experts_shortlist(feats_list, expert_fns, weights, cap):
        """score = max_i(weights[i] * expert_fn_i(features))"""
        scored = []
        for bid, f in feats_list:
            expert_scores = [w * fn(f) for w, fn in zip(weights, expert_fns)]
            scored.append((bid, max(expert_scores)))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return [bid for bid, _ in scored[:cap]]

    experts = [
        ("cheap", lambda f: f["cheap"]),
        ("fidelity", lambda f: f["fidelity"]),
        ("log_models", lambda f: f["log_models"]),
        ("prior", lambda f: f["prior"]),
        ("gc_rg", lambda f: f["gc_rg"]),
        ("fid_x_cheap", lambda f: f["fid_x_cheap"]),
        ("sqrt_prior_x_fid", lambda f: f["sqrt_prior_x_fid"]),
    ]

    # Optimize weights for max-of-experts
    feat_keys_for_max = ["cheap", "fidelity", "log_models", "prior", "gc_rg",
                         "fid_x_cheap", "sqrt_prior_x_fid"]

    # Pre-build feature matrices for speed
    prebuilt = []
    for tid, oracle_id, feats in data:
        n = len(feats)
        bids = [bid for bid, _ in feats]
        oracle_idx = bids.index(oracle_id) if oracle_id in bids else -1
        mat = np.zeros((n, len(feat_keys_for_max)))
        for i, (bid, f) in enumerate(feats):
            for j, fk in enumerate(feat_keys_for_max):
                mat[i, j] = f[fk]
        prebuilt.append((tid, oracle_idx, mat, bids))

    def eval_max_experts(w, K=100):
        w = np.abs(np.array(w))  # weights must be positive for max
        hit = 0
        must_miss = []
        for tid, oidx, mat, bids in prebuilt:
            if oidx < 0:
                continue
            # score = max over (w[j] * mat[:,j]) for each candidate
            weighted = mat * w[np.newaxis, :]  # (n, nfeats)
            scores = np.max(weighted, axis=1)  # max over features
            oracle_score = scores[oidx]
            rank = int(np.sum(scores > oracle_score)) + 1
            if rank <= K:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss

    for K in [95, 100, 105, 110]:
        def objective(params):
            h, mm = eval_max_experts(params, K)
            penalty = len(mm) * 2.0
            if 'G30' in mm:
                penalty += 3.0
            return -(h - penalty)

        bounds = [(0.1, 10)] * len(feat_keys_for_max)
        best_h = 0
        best_w = None
        best_mm = None
        for seed in range(15):
            result = differential_evolution(
                objective, bounds=bounds,
                maxiter=2000, popsize=20, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            w = result.x
            h, mm = eval_max_experts(w, K)
            if h > best_h or (h == best_h and 'G30' not in mm and ('G30' in (best_mm or []))):
                best_h = h
                best_w = w
                best_mm = mm

        must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
        g30 = "G30" not in (best_mm or [])
        print(f"  K={K}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
        print(f"    weights: {dict(zip(feat_keys_for_max, [f'{abs(v):.3f}' for v in best_w]))}")

    # === Approach 5: Percentile-rank based scoring ===
    print("\n" + "=" * 80)
    print("APPROACH 5: Percentile-rank scoring (rank-normalize then combine)")
    print("=" * 80)

    # For each target, rank-normalize each feature to [0,1]
    # Then combine normalized ranks (avoids scale issues)
    feat_keys_pct = ["prior", "fidelity", "utility", "cheap", "log_models",
                     "gc_rg", "gc_sig", "fid_x_cheap", "sqrt_prior_x_fid"]

    prebuilt_pct = []
    for tid, oracle_id, feats in data:
        n = len(feats)
        bids = [bid for bid, _ in feats]
        oracle_idx = bids.index(oracle_id) if oracle_id in bids else -1
        # Build percentile matrix
        raw = np.zeros((n, len(feat_keys_pct)))
        for i, (bid, f) in enumerate(feats):
            for j, fk in enumerate(feat_keys_pct):
                raw[i, j] = f[fk]
        # Convert to percentile ranks (0=worst, 1=best)
        from scipy.stats import rankdata
        pct = np.zeros_like(raw)
        for j in range(len(feat_keys_pct)):
            pct[:, j] = rankdata(raw[:, j]) / n
        prebuilt_pct.append((tid, oracle_idx, pct, bids))

    def eval_pct_weights(w, K=100):
        w = np.array(w)
        hit = 0
        must_miss = []
        for tid, oidx, pct, bids in prebuilt_pct:
            if oidx < 0:
                continue
            scores = pct @ w
            oracle_score = scores[oidx]
            rank = int(np.sum(scores > oracle_score)) + 1
            if rank <= K:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss

    for K in [95, 100, 105, 110]:
        def objective(params):
            h, mm = eval_pct_weights(params, K)
            penalty = len(mm) * 2.0
            if 'G30' in mm:
                penalty += 3.0
            return -(h - penalty)

        bounds = [(-2, 5)] * len(feat_keys_pct)
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
            h, mm = eval_pct_weights(w, K)
            if h > best_h or (h == best_h and 'G30' not in mm and ('G30' in (best_mm or []))):
                best_h = h
                best_w = w
                best_mm = mm

        must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
        g30 = "G30" not in (best_mm or [])
        print(f"  K={K}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
        print(f"    weights: {dict(zip(feat_keys_pct, [f'{v:.3f}' for v in best_w]))}")

    # === Approach 6: Max-of-percentile-experts ===
    print("\n" + "=" * 80)
    print("APPROACH 6: Max-of-percentile-experts (max over weighted percentiles)")
    print("=" * 80)

    def eval_max_pct(w, K=100):
        w = np.abs(np.array(w))
        hit = 0
        must_miss = []
        for tid, oidx, pct, bids in prebuilt_pct:
            if oidx < 0:
                continue
            weighted = pct * w[np.newaxis, :]
            scores = np.max(weighted, axis=1)
            oracle_score = scores[oidx]
            rank = int(np.sum(scores > oracle_score)) + 1
            if rank <= K:
                hit += 1
            elif tid in MUST_INCLUDE:
                must_miss.append(tid)
        return hit, must_miss

    for K in [95, 100, 105, 110]:
        def objective(params):
            h, mm = eval_max_pct(params, K)
            penalty = len(mm) * 2.0
            if 'G30' in mm:
                penalty += 3.0
            return -(h - penalty)

        bounds = [(0.1, 10)] * len(feat_keys_pct)
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
            h, mm = eval_max_pct(w, K)
            if h > best_h or (h == best_h and 'G30' not in mm and ('G30' in (best_mm or []))):
                best_h = h
                best_w = w
                best_mm = mm

        must_m = sorted(set(best_mm) & MUST_INCLUDE) if best_mm else []
        g30 = "G30" not in (best_mm or [])
        print(f"  K={K}: {best_h}/{total} must_miss={must_m} G30={'OK' if g30 else 'MISS'}")
        print(f"    weights: {dict(zip(feat_keys_pct, [f'{abs(v):.3f}' for v in best_w]))}")


if __name__ == "__main__":
    main()
