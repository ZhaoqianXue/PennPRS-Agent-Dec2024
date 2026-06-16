"""Decisive free test: which already-in-dump feature, if any, robustly predicts
AoU adjusted-AUC rank across the 44 pools? Per-disease Spearman(feature, AoU adjAUC).
"""
from __future__ import annotations
import json, sys, math
from pathlib import Path
from statistics import mean
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from src.server.core.tools.pgs_single_record import build_single_record
GT = ROOT / "experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
topk = json.load(open(GT / "top_k_pgs_per_ontology.json"))
bench = json.load(open(GT / "benchmark_auc_per_ontology.json"))
TARGETS = {"type 2 diabetes mellitus", "breast carcinoma", "prostate carcinoma",
           "hypertension", "alzheimer disease", "ovarian neoplasm"}


def feats(pid):
    rec = build_single_record(pid)
    if not rec:
        return None
    pm = rec.get("performance_metrics") or {}
    m = pm.get("metrics") or {}
    es = m.get("effect_sizes") or []
    or_hr = None
    for e in es:
        if e.get("estimate"):
            or_hr = e["estimate"]; break
    gw = rec.get("source_of_variant_associations_gwas") or {}
    var = rec.get("variants", {}).get("variants_number")
    date = (rec.get("pgs_source") or {}).get("date_release") or ""
    yr = None
    try:
        yr = int(str(date)[:4])
    except Exception:
        pass
    return {
        "log_var": math.log10(var) if var else None,
        "year": yr,
        "log_gwas": math.log10(gw.get("sample_numbers", {}).get("individuals")) if (gw.get("sample_numbers") or {}).get("individuals") else None,
        "full_auroc": m.get("full_model_auroc"),
        "prs_auc": m.get("pgs_only_auroc"),
        "prs_r2": m.get("pgs_only_r2"),
        "or_hr": or_hr,
        "log_evaln": math.log10((pm.get("evaluation_sample") or {}).get("sample_numbers", {}).get("individuals")) if ((pm.get("evaluation_sample") or {}).get("sample_numbers") or {}).get("individuals") else None,
    }


def spearman(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 4:
        return None
    xs2 = [p[0] for p in pairs]; ys2 = [p[1] for p in pairs]
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0]*len(v); i = 0
        while i < len(v):
            j = i
            while j+1 < len(v) and v[order[j+1]] == v[order[i]]:
                j += 1
            avg = (i+j)/2.0+1
            for k in range(i, j+1):
                r[order[k]] = avg
            i = j+1
        return r
    rx, ry = ranks(xs2), ranks(ys2)
    mx, my = mean(rx), mean(ry)
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    den = (sum((rx[i]-mx)**2 for i in range(n))*sum((ry[i]-my)**2 for i in range(n)))**0.5
    return num/den if den else None


FEATURES = ["log_var", "year", "log_gwas", "full_auroc", "prs_auc", "prs_r2", "or_hr", "log_evaln"]
rows = []
for dz, ranked in topk.items():
    bdict = bench.get(dz) or {}
    pool = [p for p in ranked if feats(p)]
    if len(pool) < 6:
        continue
    F = {p: feats(p) for p in pool}
    aucs = [bdict.get(p, 0.0) for p in pool]
    row = {"dz": dz, "n": len(pool), "tgt": dz in TARGETS}
    for ft in FEATURES:
        row[ft] = spearman([F[p][ft] for p in pool], aucs)
    rows.append(row)

print(f"Per-disease Spearman(feature, AoU adjAUC). +ve => higher feature predicts BETTER AoU.\n")
print(f"{'disease':32s} {'n':>4s} " + " ".join(f"{ft[:8]:>8s}" for ft in FEATURES))
for r in sorted(rows, key=lambda x: (not x["tgt"], x["dz"])):
    star = "*" if r["tgt"] else " "
    print(f"{star}{r['dz'][:31]:31s} {r['n']:>4d} " + " ".join((f"{r[ft]:+.2f}" if r[ft] is not None else "  n/a").rjust(8) for ft in FEATURES))

print("\n--- MEAN Spearman ---")
print(f"{'feature':12s} {'all44':>8s} {'targets6':>9s}")
for ft in FEATURES:
    av = [r[ft] for r in rows if r[ft] is not None]
    tv = [r[ft] for r in rows if r[ft] is not None and r["tgt"]]
    print(f"{ft:12s} {mean(av):+.3f}({len(av):2d}) {mean(tv):+.3f}({len(tv)})" if tv else f"{ft:12s} {mean(av):+.3f}")
