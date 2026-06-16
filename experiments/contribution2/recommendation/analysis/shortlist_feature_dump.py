"""For each of the 6 targets, dump the full build_single_record serialization of
every Stage-1 shortlist member + the AoU rank-1 model, side by side, to find the
trait-agnostic feature that separates the AoU-best member from the headline pick.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from src.server.core.tools.pgs_single_record import build_single_record

RUN = ROOT / "experiments/contribution2/recommendation/runs/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-20260610-002512"
GT = ROOT / "experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
topk = json.load(open(GT / "top_k_pgs_per_ontology.json"))
bench = json.load(open(GT / "benchmark_auc_per_ontology.json"))
s1 = {x["ontology"]: x for x in json.load(open(RUN / "experiment_topk_holistic_rerank_batch_stage1_results.json"))}
summ = json.load(open(RUN / "experiment_topk_holistic_rerank_batch_summary.json"))
per = {d["ontology"]: d for d in summ["per_disease"]}
TARGETS = ["type 2 diabetes mellitus", "breast carcinoma", "prostate carcinoma",
           "hypertension", "alzheimer disease", "ovarian neoplasm"]


def rk(p, r):
    return r.index(p) + 1 if p in r else None


def feat(pid):
    rec = build_single_record(pid) or {}
    pm = rec.get("performance_metrics") or {}
    m = pm.get("metrics") or {}
    es = m.get("effect_sizes") or []
    es_s = ",".join(f"{e['name_short']}{e['estimate']}" for e in es) or "-"
    gw = rec.get("source_of_variant_associations_gwas") or {}
    tr = rec.get("score_development_training") or {}
    return {
        "var": rec.get("variants", {}).get("variants_number"),
        "method": (rec.get("development_method") or {}).get("method_name"),
        "date": (rec.get("pgs_source") or {}).get("date_release"),
        "gwas_n": (gw.get("sample_numbers") or {}).get("individuals"),
        "gwas_anc": gw.get("ancestry"),
        "train_n": (tr.get("sample_numbers") or {}).get("individuals"),
        "train_anc": tr.get("ancestry"),
        "prs_auc": m.get("pgs_only_auroc"),
        "prs_r2": m.get("pgs_only_r2"),
        "full_auroc": m.get("full_model_auroc"),
        "c_index": m.get("c_index"),
        "eff": es_s,
        "eval_anc": (pm.get("evaluation_sample") or {}).get("ancestry"),
        "eval_n": (pm.get("evaluation_sample") or {}).get("sample_numbers", {}).get("individuals"),
        "cov": (pm.get("covariates") or "")[:40],
        "pheno": (pm.get("phenotyping_reported") or "")[:30],
    }


for dz in TARGETS:
    ranked = topk[dz]
    dec = s1[dz]["decision"]
    shortlist = [dec["best_model_id"]] + (dec.get("top_alternatives") or [])
    final = per[dz]["modal_recommendation"]
    extra = [ranked[0], ranked[1], ranked[2]]  # AoU top-3
    ids = []
    for p in shortlist + extra:
        if p not in ids:
            ids.append(p)
    print("\n" + "=" * 130)
    print(f"{dz}  (pool={per[dz]['n_models']})   FINAL pick={final} (r{rk(final, ranked)})")
    print("=" * 130)
    hdr = f"{'PGS':10s} {'AoU':>4s} {'role':6s} {'var':>9s} {'method':16s} {'date':5s} {'gwas_n':>9s} {'train_anc':10s} {'prs_auc':>7s} {'prs_r2':>6s} {'fullAUC':>7s} {'cidx':>5s} {'eff':12s} {'eval_anc':10s}"
    print(hdr)
    for p in ids:
        f = feat(p)
        aour = rk(p, ranked)
        role = "PICK" if p == final else ("short" if p in shortlist else "AoUtop")
        date = (f["date"] or "")[:4]
        ta = (f["train_anc"] or "")[:9]
        ea = (f["eval_anc"] or "")[:9]
        mn = (f["method"] or "")[:15]
        print(f"{p:10s} {str(aour):>4s} {role:6s} {str(f['var']):>9s} {mn:16s} {date:5s} {str(f['gwas_n']):>9s} {ta:10s} "
              f"{str(f['prs_auc'] or '-'):>7s} {str(f['prs_r2'] or '-'):>6s} {str(f['full_auroc'] or '-'):>7s} {str(f['c_index'] or '-'):>5s} {f['eff']:12s} {ea:10s}")
