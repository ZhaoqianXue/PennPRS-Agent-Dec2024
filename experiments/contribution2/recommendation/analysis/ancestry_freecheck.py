"""FREE CHECK (no OpenAI cost): does an ancestry-transferability signal exist in
the PGS Catalog dump that (a) distinguishes the AoU-best PGS from the Agent's
pick on the 6 target diseases, and (b) correlates with AoU rank across the full
candidate pool? Trait-agnostic throughout.

Run: .venv/bin/python experiments/contribution2/recommendation/analysis/ancestry_freecheck.py
"""
from __future__ import annotations
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
GT = ROOT / "experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
RUN = ROOT / "experiments/contribution2/recommendation/runs/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-20260610-002512"
DUMP = ROOT / "data/pgs_all_metadata/pgs_full_rest_dump.jsonl"

import sys
sys.path.insert(0, str(ROOT))
from src.server.core.tools.prs_model_tools import (
    _select_representative_performance_record,
    _extract_validation_ancestries,
    _extract_metric_summary_from_metrics_dict,
)

TARGETS = [
    "type 2 diabetes mellitus", "breast carcinoma", "prostate carcinoma",
    "hypertension", "alzheimer disease", "ovarian neoplasm",
]

# ---- load dump ----
DUMPIDX = {}
with open(DUMP) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        pid = r.get("pgs_id") or (r.get("score") or {}).get("id")
        if pid:
            DUMPIDX[pid] = r

topk = json.load(open(GT / "top_k_pgs_per_ontology.json"))
bench = json.load(open(GT / "benchmark_auc_per_ontology.json"))
summ = json.load(open(RUN / "experiment_topk_holistic_rerank_batch_summary.json"))
per = {d["ontology"]: d for d in summ["per_disease"]}


def anc_signals(pgs_id):
    """Ancestry signals from the dump for one PGS. All trait-agnostic."""
    rec = DUMPIDX.get(pgs_id)
    if not rec:
        return None
    sc = rec.get("score") or {}
    ad = sc.get("ancestry_distribution") or {}
    perf = rec.get("performance") or []
    # eval-ancestry distribution (the HIDDEN multi-ancestry signal)
    ev = (ad.get("eval") or {}).get("dist") or {}
    ev_multi = (ad.get("eval") or {}).get("multi") or []
    dev = (ad.get("dev") or {}).get("dist") or {}
    gwas = (ad.get("gwas") or {}).get("dist") or {}
    # what the LLM CURRENTLY sees: European-preferred single record
    sel = _select_representative_performance_record(perf, sc.get("trait_reported") or "")
    sel_anc = _extract_validation_ancestries(sel) if sel else []
    # ALL eval-record ancestries (across every performance record)
    all_anc = set()
    for p in perf:
        for a in _extract_validation_ancestries(p):
            all_anc.add(a)
    non_eur_keys = {k for k in ev if k.upper() not in ("EUR",)}
    return {
        "eval_dist": ev,
        "eval_multi": ev_multi,
        "dev_dist": dev,
        "gwas_dist": gwas,
        "n_eval_ancestry_groups": len([k for k in ev if ev.get(k)]),
        "eval_has_AFR": ev.get("AFR", 0) > 0,
        "eval_has_AMR": (ev.get("AMR", 0) or ev.get("HIS", 0) or ev.get("LAT", 0)) > 0,
        "eval_has_EAS": (ev.get("EAS", 0) or ev.get("ASN", 0)) > 0,
        "eval_is_multi": bool(ev_multi) or len([k for k in ev if ev.get(k)]) > 1,
        "eval_eur_pct": ev.get("EUR", None),
        "eval_nonEUR_pct": round(sum(v for k, v in ev.items() if k.upper() != "EUR"), 1) if ev else None,
        "dev_is_multi": len([k for k in dev if dev.get(k)]) > 1,
        "dev_nonEUR": len([k for k in dev if dev.get(k) and k.upper() != "EUR"]) > 0,
        "selected_record_ancestry": sel_anc,  # what LLM sees now
        "all_record_ancestries": sorted(all_anc),
        "hidden_nonEUR_eval": sorted(a for a in all_anc if "eur" not in a.lower())
                              and not any("eur" not in a.lower() for a in sel_anc),
    }


def rank_of(pgs_id, ranked):
    return ranked.index(pgs_id) + 1 if pgs_id in ranked else None


print("=" * 100)
print("PART A: AoU-best vs Agent-pick — ancestry profile (6 targets)")
print("=" * 100)
for dz in TARGETS:
    ranked = topk[dz]
    d = per[dz]
    best = ranked[0]
    agent = d["modal_recommendation"]
    agent_rank = d["modal_recommendation_rank"]
    baseline = (d.get("baseline") or {}).get("pgs_id")
    baseline_rank = (d.get("baseline") or {}).get("rank")
    print(f"\n### {dz}  (pool={d['n_models']})")
    for label, pid, rk in [("AoU-BEST (rank1)", best, 1),
                            ("AGENT pick", agent, agent_rank),
                            ("reported-max", baseline, baseline_rank)]:
        s = anc_signals(pid)
        if not s:
            print(f"  {label:18s} {pid}  [NOT IN DUMP]")
            continue
        print(f"  {label:18s} {pid}  rank={rk}")
        print(f"      LLM-sees eval ancestry : {s['selected_record_ancestry']}")
        print(f"      ALL eval ancestries    : {s['all_record_ancestries']}")
        print(f"      eval_dist (AoU-relevant): {s['eval_dist']}  multi={s['eval_multi']}")
        print(f"      dev_dist                : {s['dev_dist']}")
        print(f"      #eval-groups={s['n_eval_ancestry_groups']} AFR={s['eval_has_AFR']} "
              f"AMR={s['eval_has_AMR']} EAS={s['eval_has_EAS']} multi_eval={s['eval_is_multi']} "
              f"nonEUR%={s['eval_nonEUR_pct']}")

print("\n" + "=" * 100)
print("PART B: pooled correlation — does an ancestry signal predict AoU rank? (within each pool)")
print("  Test: among the pool, do the AoU top-quartile PGS differ from bottom-quartile on each signal?")
print("=" * 100)

import statistics
signals = ["n_eval_ancestry_groups", "eval_has_AFR", "eval_has_AMR", "eval_has_EAS",
           "eval_is_multi", "dev_is_multi", "dev_nonEUR"]


def spearman(xs, ys):
    # rank-based correlation, no scipy
    n = len(xs)
    if n < 3:
        return None
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(rx), mean(ry)
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den = (sum((rx[i] - mx) ** 2 for i in range(n)) * sum((ry[i] - my) ** 2 for i in range(n))) ** 0.5
    return num / den if den else None


# For ALL 44 diseases, compute per-pool spearman(signal, -rank) i.e. higher signal -> better(lower) rank => positive corr with adj-auc
allrows = []
for dz, ranked in topk.items():
    bdict = bench.get(dz) or {}
    pool = [p for p in ranked if anc_signals(p)]
    if len(pool) < 6:
        continue
    aucs = [bdict.get(p, 0.0) for p in pool]
    sigvals = {sg: [] for sg in signals}
    for p in pool:
        s = anc_signals(p)
        for sg in signals:
            v = s[sg]
            sigvals[sg].append(float(v) if isinstance(v, bool) else float(v or 0))
    row = {"disease": dz, "pool": len(pool), "target": dz in TARGETS}
    for sg in signals:
        row[sg] = spearman(sigvals[sg], aucs)
    allrows.append(row)

print(f"\nPer-disease Spearman(signal, AoU adj-AUC).  +ve => signal predicts BETTER AoU.")
hdr = f"{'disease':32s} {'pool':>4s} " + " ".join(f"{sg[:9]:>9s}" for sg in signals)
print(hdr)
for row in allrows:
    star = "*" if row["target"] else " "
    cells = " ".join((f"{row[sg]:+.2f}" if row[sg] is not None else "  n/a").rjust(9) for sg in signals)
    print(f"{star}{row['disease'][:31]:31s} {row['pool']:>4d} {cells}")

print("\n--- mean Spearman across diseases ---")
for sg in signals:
    vals = [r[sg] for r in allrows if r[sg] is not None]
    tvals = [r[sg] for r in allrows if r[sg] is not None and r["target"]]
    print(f"  {sg:24s} all44 mean={mean(vals):+.3f} (n={len(vals)})   "
          f"targets6 mean={mean(tvals):+.3f} (n={len(tvals)})" if tvals else "")
