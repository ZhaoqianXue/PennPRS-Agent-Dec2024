"""Decisive net-EV test: within each Stage-1 shortlist, if the agent picked the
2nd-best / median / min reported-metric sibling instead of the max, what is the
NET Hit@1 across all 44? This tests whether a trait-agnostic 'don't pick the
max among ties' de-biasing nets positive (vs the winner's-curse it would create
elsewhere). Free.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from statistics import median
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from src.server.core.tools.pgs_single_record import build_single_record
RUN = ROOT / "experiments/contribution2/recommendation/runs/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-20260610-002512"
GT = ROOT / "experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
topk = json.load(open(GT / "top_k_pgs_per_ontology.json"))
s1 = {x["ontology"]: x for x in json.load(open(RUN / "experiment_topk_holistic_rerank_batch_stage1_results.json"))}
summ = json.load(open(RUN / "experiment_topk_holistic_rerank_batch_summary.json"))
per = {d["ontology"]: d for d in summ["per_disease"]}
TARGETS = {"type 2 diabetes mellitus", "breast carcinoma", "prostate carcinoma",
           "hypertension", "alzheimer disease", "ovarian neoplasm"}


def metric(pid):
    """The single 'headline discrimination' number the agent ranks on:
    full_auroc, else OR/HR estimate, else prs_auc. Trait-agnostic."""
    rec = build_single_record(pid)
    if not rec:
        return None
    m = (rec.get("performance_metrics") or {}).get("metrics") or {}
    if m.get("full_model_auroc") is not None:
        return ("full", m["full_model_auroc"])
    es = m.get("effect_sizes") or []
    for e in es:
        if e.get("estimate"):
            return ("or", e["estimate"])
    if m.get("pgs_only_auroc") is not None:
        return ("prsauc", m["pgs_only_auroc"])
    if m.get("c_index") is not None:
        return ("cidx", m["c_index"])
    return None


def rk(p, r):
    return r.index(p) + 1 if p in r else 9999


strategies = ["actual", "max", "2nd", "median", "min"]
hit = {s: 0 for s in strategies}
ranks = {s: [] for s in strategies}
thit = {s: 0 for s in strategies}  # targets only
detail = []
for dz, ranked in topk.items():
    dec = s1[dz]["decision"]
    shortlist = [dec["best_model_id"]] + (dec.get("top_alternatives") or [])
    shortlist = [p for p in shortlist if p]
    actual = per[dz]["modal_recommendation"]
    # rank shortlist by headline metric (same axis only, comparable). Use numeric value.
    scored = [(p, metric(p)) for p in shortlist]
    scored = [(p, v[1]) for p, v in scored if v is not None]
    if len(scored) < 2:
        continue
    scored.sort(key=lambda x: x[1], reverse=True)  # max metric first
    picks = {
        "actual": actual,
        "max": scored[0][0],
        "2nd": scored[1][0] if len(scored) > 1 else scored[0][0],
        "median": scored[len(scored) // 2][0],
        "min": scored[-1][0],
    }
    for s in strategies:
        rr = rk(picks[s], ranked)
        ranks[s].append(rr)
        if rr == 1:
            hit[s] += 1
            if dz in TARGETS:
                thit[s] += 1
    if dz in TARGETS:
        detail.append((dz, {s: rk(picks[s], ranked) for s in strategies}))

n = len(ranks["actual"])
print(f"Across {n} diseases with scorable shortlists:\n")
print(f"{'strategy':10s} {'Hit@1':>6s} {'Hit@1%':>7s} {'meanRank':>9s} {'medRank':>8s} {'targetHit':>10s}")
for s in strategies:
    print(f"{s:10s} {hit[s]:>6d} {100*hit[s]/n:>6.1f}% {sum(ranks[s])/n:>9.1f} {median(ranks[s]):>8.1f} {thit[s]:>10d}")

print("\n--- 6 targets: AoU rank under each strategy ---")
print(f"{'disease':28s} " + " ".join(f"{s:>7s}" for s in strategies))
for dz, d in detail:
    print(f"{dz[:27]:27s} " + " ".join(f"{d[s]:>7d}" for s in strategies))
