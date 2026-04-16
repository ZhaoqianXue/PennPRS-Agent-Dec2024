"""Verify max-of-percentile-experts result (80/80 at K=95).

Independent verification + cross-validation to check for overfitting.
"""
from __future__ import annotations
import math, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
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

FEAT_KEYS = ["prior", "fidelity", "utility", "cheap", "log_models",
             "gc_rg", "gc_sig", "fid_x_cheap", "sqrt_prior_x_fid"]

# Weights from DE optimization (K=95 result)
W_K95 = np.array([2.631, 1.134, 1.673, 1.187, 1.408, 0.978, 7.816, 0.539, 2.135])
W_K100 = np.array([1.475, 0.476, 2.943, 3.140, 2.546, 4.044, 9.064, 0.573, 1.359])


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
        "log_models": math.log1p(min(max(c.n_models, 0), 200)),
        "gc_rg": gc_rg,
        "gc_sig": gc_sig,
        "fid_x_cheap": c.phenotype_fidelity_score * c.cheap_rank_score,
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


def build_pct_data(data):
    """Build percentile-rank matrices."""
    prebuilt = []
    for tid, oracle_id, feats in data:
        n = len(feats)
        bids = [bid for bid, _ in feats]
        oracle_idx = bids.index(oracle_id) if oracle_id in bids else -1
        raw = np.zeros((n, len(FEAT_KEYS)))
        for i, (bid, f) in enumerate(feats):
            for j, fk in enumerate(FEAT_KEYS):
                raw[i, j] = f[fk]
        pct = np.zeros_like(raw)
        for j in range(len(FEAT_KEYS)):
            pct[:, j] = rankdata(raw[:, j]) / n
        prebuilt.append((tid, oracle_idx, pct, bids))
    return prebuilt


def eval_max_pct(prebuilt, w, K=100):
    w = np.abs(np.array(w))
    results = []
    for tid, oidx, pct, bids in prebuilt:
        if oidx < 0:
            continue
        weighted = pct * w[np.newaxis, :]
        scores = np.max(weighted, axis=1)
        oracle_score = scores[oidx]
        rank = int(np.sum(scores > oracle_score)) + 1
        # Which feature gives oracle its max score?
        oracle_pct = pct[oidx]
        oracle_weighted = oracle_pct * w
        best_feat_idx = np.argmax(oracle_weighted)
        results.append({
            "tid": tid, "rank": rank, "oracle_score": oracle_score,
            "best_feat": FEAT_KEYS[best_feat_idx],
            "best_feat_pct": oracle_pct[best_feat_idx],
            "best_feat_weighted": oracle_weighted[best_feat_idx],
            "n_candidates": len(bids),
            "n_higher": int(np.sum(scores > oracle_score)),
        })
    return results


def main():
    print("Loading data...")
    data = load_all()
    total = len(data)
    print(f"Loaded {total} targets\n")

    prebuilt = build_pct_data(data)

    # === Verify K=95 weights ===
    print("=" * 80)
    print("VERIFICATION: K=95 weights")
    print("=" * 80)
    results = eval_max_pct(prebuilt, W_K95, K=95)
    hit = sum(1 for r in results if r["rank"] <= 95)
    miss = [r for r in results if r["rank"] > 95]
    print(f"  Recall: {hit}/{total}")
    if miss:
        print(f"  Misses: {[(r['tid'], r['rank']) for r in miss]}")

    # Per-target details for must-include
    print(f"\n  Must-include target details:")
    for r in results:
        if r["tid"] in MUST_INCLUDE:
            print(f"    {r['tid']}: rank={r['rank']}/{r['n_candidates']} "
                  f"best_feat={r['best_feat']}(pct={r['best_feat_pct']:.3f}, "
                  f"weighted={r['best_feat_weighted']:.3f}) "
                  f"n_higher={r['n_higher']}")

    # Hard targets details
    print(f"\n  Hard target feature breakdown:")
    for r in results:
        if r["tid"] in {'G30', 'M05', 'N91', 'N97'}:
            tidx = next(i for i, (t, _, _, _) in enumerate(prebuilt) if t == r["tid"])
            _, oidx, pct, _ = prebuilt[tidx]
            oracle_pct = pct[oidx]
            oracle_weighted = oracle_pct * np.abs(W_K95)
            print(f"    {r['tid']} (rank={r['rank']}):")
            for j, fk in enumerate(FEAT_KEYS):
                print(f"      {fk:>20s}: pct={oracle_pct[j]:.3f} weighted={oracle_weighted[j]:.3f}")
            print(f"      MAX score = {max(oracle_weighted):.3f}")

    # How many candidates have gc_sig for each hard target?
    print(f"\n  GC significance counts per hard target:")
    for (tid, oracle_id, feats), (_, oidx, pct, bids) in zip(data, prebuilt):
        if tid in {'G30', 'M05', 'N91', 'N97'}:
            gc_sig_count = sum(1 for _, f in feats if f["gc_sig"] > 0)
            print(f"    {tid}: {gc_sig_count}/{len(feats)} candidates have gc_sig=1")

    # === Verify K=100 weights ===
    print(f"\n  K=100 weights: ", end="")
    results100 = eval_max_pct(prebuilt, W_K100, K=100)
    hit100 = sum(1 for r in results100 if r["rank"] <= 100)
    print(f"{hit100}/{total}")

    # === Cross-validation: leave-one-out ===
    print("\n" + "=" * 80)
    print("CROSS-VALIDATION: leave-one-out")
    print("=" * 80)

    cv_hits = 0
    cv_misses = []
    for holdout_idx in range(len(prebuilt)):
        # Train on all except holdout
        train = [prebuilt[i] for i in range(len(prebuilt)) if i != holdout_idx]
        test = [prebuilt[holdout_idx]]

        def objective(params):
            w = np.abs(np.array(params))
            h = 0
            for tid, oidx, pct, bids in train:
                if oidx < 0:
                    continue
                weighted = pct * w[np.newaxis, :]
                scores = np.max(weighted, axis=1)
                oracle_score = scores[oidx]
                rank = int(np.sum(scores > oracle_score)) + 1
                if rank <= 95:
                    h += 1
            return -h

        bounds = [(0.1, 10)] * len(FEAT_KEYS)
        best_w = None
        best_train_h = 0
        for seed in range(5):
            result = differential_evolution(
                objective, bounds=bounds,
                maxiter=1000, popsize=15, tol=0,
                mutation=(0.5, 1.5), recombination=0.9,
                seed=seed, workers=1, polish=True,
            )
            h_train = -result.fun
            if h_train > best_train_h:
                best_train_h = h_train
                best_w = result.x

        # Test on holdout
        tid, oidx, pct, bids = test[0]
        if oidx >= 0:
            w = np.abs(np.array(best_w))
            weighted = pct * w[np.newaxis, :]
            scores = np.max(weighted, axis=1)
            oracle_score = scores[oidx]
            rank = int(np.sum(scores > oracle_score)) + 1
            if rank <= 95:
                cv_hits += 1
            else:
                cv_misses.append((tid, rank))

    print(f"  LOO-CV recall: {cv_hits}/{total}")
    if cv_misses:
        cv_must_miss = [(t, r) for t, r in cv_misses if t in MUST_INCLUDE]
        print(f"  CV misses: {cv_misses}")
        print(f"  CV must-include misses: {cv_must_miss}")
    else:
        print(f"  Perfect generalization!")


if __name__ == "__main__":
    main()
