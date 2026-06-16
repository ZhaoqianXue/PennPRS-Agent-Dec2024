"""Deterministic error analysis for the 10 within-trait Hit@1 misses.

Reads the canonical PRS Agent run (stage1 shortlist + stage2 winner + scored
results) and, for each target trait, records:
  - benchmark top1 PGS (AoU rank-1) and its AUC
  - agent final pick + benchmark rank + AUC
  - stage1 shortlist (best + alternatives); whether top1 is inside it
  - whether top1 is even in the candidate pool
  - stage2 winner vs stage1 best (did stage2 move the pick?)
  - a coarse failure class: POOL_RECALL / STAGE1_RECALL / STAGE2_PRECISION
  - compact 7-section visible metadata for top1 vs agent pick (for diffing)

No LLM calls. Pure read of run artifacts. Output: errors.json + console table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(
    "experiments/contribution2/recommendation/runs/"
    "pairwise-rerank-gpt-5.4-t1__44disease__efoclean44-prs-agent-final-direct-20260614-20260613-230920"
)
OUT = Path("experiments/contribution2/recommendation/analysis/target10_hit1/errors.json")

TARGETS = [
    "type 2 diabetes mellitus",
    "breast carcinoma",
    "prostate carcinoma",
    "hypertension",
    "asthma",
    "alzheimer disease",
    "thyroid carcinoma",
    "major depressive disorder",
    "psoriasis",
    "ovarian neoplasm",
]


def load(name: str):
    return json.loads((RUN / name).read_text(encoding="utf-8"))


def compact_record(rec: dict) -> dict:
    """Collapse a candidate's 7-section view to the fields a reviewer compares."""
    if rec is None:
        return {}
    pt = rec.get("predicted_trait", {}) or {}
    pm_list = rec.get("performance_metrics", []) or []
    perf = []
    for pm in pm_list:
        perf.append(
            {
                "phenotyping_reported": pm.get("phenotyping_reported"),
                "covariates": pm.get("covariates"),
                "effect_sizes": [
                    f"{m.get('metric_name')}={m.get('estimate')}"
                    for m in (pm.get("effect_sizes") or [])
                ],
                "classification_metrics": [
                    f"{m.get('metric_name')}={m.get('estimate')}"
                    for m in (pm.get("classification_metrics") or [])
                ],
                "other_metrics": [
                    f"{m.get('metric_name')}={m.get('estimate')}"
                    for m in (pm.get("other_metrics") or [])
                ],
                "eval_ancestries": sorted(
                    {s.get("ancestry") for s in (pm.get("evaluation_samples") or [])}
                ),
                "eval_individuals": [
                    (s.get("sample_numbers") or {}).get("individuals")
                    for s in (pm.get("evaluation_samples") or [])
                ],
            }
        )
    return {
        "id": rec.get("id"),
        "trait_reported": pt.get("trait_reported"),
        "trait_efo": [e.get("label") for e in (pt.get("trait_efo") or [])],
        "method": (rec.get("development_method") or {}).get("method_name"),
        "variants": (rec.get("variants") or {}).get("variants_number"),
        "publication_title": (rec.get("pgs_source") or {}).get("publication_title"),
        "journal": (rec.get("pgs_source") or {}).get("publication_journal"),
        "date_release": (rec.get("pgs_source") or {}).get("date_release"),
        "gwas_ancestries": sorted(
            {b.get("ancestry") for b in (rec.get("source_of_variant_associations_gwas") or [])}
        ),
        "n_perf_records": len(pm_list),
        "performance": perf,
    }


def main() -> int:
    results = {r["ontology"]: r for r in load("experiment_pairwise_rerank_results.json")}
    stage1 = {r["ontology"]: r for r in load("experiment_pairwise_rerank_stage1_results.json")}
    stage2 = {r["ontology"]: r for r in load("experiment_pairwise_rerank_stage2_results.json")}

    out = []
    for trait in TARGETS:
        res = results[trait]
        s1 = stage1[trait]
        s2 = stage2[trait]

        ranked = res["benchmark_ranked_ids"]
        auc_by_id = res.get("benchmark_auc_by_id", {})
        pool = res["candidate_model_ids"]
        top1 = ranked[0]
        pick = res["recommended_pgs_id"]

        dec = s1["decision"]
        s1_best = dec.get("best_model_id")
        s1_alts = dec.get("top_alternatives") or []
        shortlist = [s1_best] + [a for a in s1_alts if a != s1_best]
        s2_winner = s2.get("winner_model_id")

        ctx = json.loads(s1["context_json"])
        models = {m["id"]: m for m in ctx["direct_models"]["models"]}

        top1_in_pool = top1 in pool
        top1_in_shortlist = top1 in shortlist

        if not top1_in_pool:
            fclass = "POOL_RECALL"  # top1 absent from candidate universe
        elif not top1_in_shortlist:
            fclass = "STAGE1_RECALL"  # top1 in pool, dropped before final selection
        elif pick != top1:
            fclass = "STAGE2_PRECISION"  # top1 survived to shortlist, not chosen
        else:
            fclass = "HIT"

        def rank_of(pgs):
            return ranked.index(pgs) + 1 if pgs in ranked else None

        out.append(
            {
                "trait": trait,
                "n_models": res["n_models"],
                "benchmark_top1": top1,
                "top1_auc": auc_by_id.get(top1),
                "agent_pick": pick,
                "agent_rank": res["recommended_rank"],
                "agent_pick_auc": auc_by_id.get(pick),
                "stage1_best": s1_best,
                "stage1_best_rank": rank_of(s1_best),
                "shortlist": shortlist,
                "shortlist_ranks": [rank_of(x) for x in shortlist],
                "stage2_winner": s2_winner,
                "stage2_moved_pick": s2_winner != s1_best,
                "top1_in_pool": top1_in_pool,
                "top1_in_shortlist": top1_in_shortlist,
                "best_shortlist_rank": min(
                    [r for r in [rank_of(x) for x in shortlist] if r is not None],
                    default=None,
                ),
                "failure_class": fclass,
                "top1_record": compact_record(models.get(top1)),
                "pick_record": compact_record(models.get(pick)),
            }
        )

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # console summary
    print(f"{'trait':<32}{'N':>4} {'top1':>10} {'pick':>10} {'rank':>6} "
          f"{'s1best_rk':>9} {'best_sl_rk':>10} {'class':>16}")
    print("-" * 100)
    for o in out:
        print(f"{o['trait']:<32}{o['n_models']:>4} {o['benchmark_top1']:>10} "
              f"{o['agent_pick']:>10} {str(o['agent_rank']):>6} "
              f"{str(o['stage1_best_rank']):>9} {str(o['best_shortlist_rank']):>10} "
              f"{o['failure_class']:>16}")
    print()
    from collections import Counter
    print("failure class counts:", dict(Counter(o["failure_class"] for o in out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
