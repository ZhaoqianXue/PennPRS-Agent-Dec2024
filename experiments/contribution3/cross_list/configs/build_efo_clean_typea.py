"""
Contribution3: EFO-clean Type A cross-trait benchmark.

Two facts fixed here (same EFO-attribution contamination as the within rebuild):
- DISEASE donor attribution `pgs_id_list_260217.csv` is contaminated (avg 1.94
  source traits/PGS, 55% multi-attributed) AND incomplete (133 source diseases,
  missing E10/E11 etc.).
- MEASUREMENT donor attribution (LOINC metadata) is also contaminated (avg 1.43).

Both feed the legacy Type A target selection. There is NO b2b/b2c split in the
project: every one of the ~2958 extend-matrix PGS is a candidate transfer donor,
disease OR measurement, and the official eval ranks the agent's pick among ALL of
them (PGS-level).

This produces:
1. TARGET SELECTION using the SAME standard that produced the legacy 60
   (`build_b2b_type_a_benchmark` + `build_b2c_type_a_benchmark` + post-hoc, with
   min_best_split_gap=0), but on CLEAN disease + measurement attribution. Result:
   58 targets (the contaminated recompute is 59; the frozen paired80 is 60 — so
   cleaning the data changes WHICH targets more than HOW MANY).
2. A UNIFIED clean ground-truth ranking for each selected target: every donor PGS
   grouped by its OWN PGS-Catalog `trait_efo` (disease + measurement together),
   ranked by best donor AUC. Clean by construction — no external attribution file.

Clean attribution: a donor PGS belongs to a source trait iff that trait's EFO is
in the PGS's own trait_efo. Disease source set = union(within case>=200, cross
133) + curated related-EFO additions (colorectal->C18, diabetes umbrella->E11,
eczematoid->L30); measurement source set = the LOINC metadata traits.

Run: /Users/zhaoqianxue/anaconda3/bin/python \
       experiments/contribution3/cross_list/configs/build_efo_clean_typea.py
"""
from __future__ import annotations

import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CONFIGS_DIR = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "configs"
LATEST_DIR = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "benchmark_contrib1_latest"
for p in (str(CONFIGS_DIR), str(LATEST_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

CATALOG_TRAITS = PROJECT_ROOT / "experiments" / "contribution2" / "disease_selection" / "efo_rebuild" / "pgs_catalog_traits_all.json"
REST_DUMP = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_full_rest_dump.jsonl"
WITHIN_META = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "legacy_no_aou_pgs" / "aou_binary" / "prs_adjauc_metadata_binary_combined_rootcode.csv"
CROSS_PGS_LIST = PROJECT_ROOT / "experiments" / "contribution1" / "disease_preprocess" / "pgs_id_list_260217.csv"
LEGACY_NO_AOU = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "legacy_no_aou_pgs"
LOINC_META = LEGACY_NO_AOU / "aou_continuous" / "prs_incrementalr2_metadata_260225_loinccode.csv"
EXTEND_MATRIX = LEGACY_NO_AOU / "aou_extend_trait" / "prs_adjauc_matrix_binary_extend_qc.csv"
OUT_DIR = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "benchmark_efoclean_typeA"
OLD_PAIRED80 = PROJECT_ROOT / "experiments" / "contribution3" / "cross_list" / "benchmark_legacy_no_aou_pgs" / "unified" / "target_selection.csv"

# curated related-EFO additions for clear granularity gaps (broad umbrellas
# cardiovascular/endocrine disorder deliberately excluded).
RELATED_EFO_BY_ROOTCODE = {
    "C18": ["MONDO_0005575", "MONDO_0024331"],  # colorectal cancer/carcinoma
    "E11": ["MONDO_0005015"],                   # diabetes mellitus umbrella
    "L30": ["HP_0000964"],                      # eczematoid dermatitis
}

_CANCER = {"carcinoma", "cancer", "neoplasm", "tumor", "tumour", "malignant", "malignancy", "adenocarcinoma"}
_DROP = {"disease", "disorder", "the", "of", "gland"}


def _norm(s):
    return " ".join(str(s).lower().split())


def _concept(s):
    toks = "".join(c if (c.isalnum() or c == " ") else " " for c in _norm(s)).split()
    return frozenset("CANCER" if t in _CANCER else t for t in toks if t not in _DROP)


def _parse(s):
    try:
        out = ast.literal_eval(str(s))
        return list(out) if isinstance(out, (list, tuple)) else [out]
    except (ValueError, SyntaxError):
        return []


def _col_to_pgs_id(col):
    col = str(col).strip()
    return col.rsplit("__", 1)[-1] if "__" in col else col.replace("_hmPOS_GRCh38", "")


def _load():
    traits = json.loads(CATALOG_TRAITS.read_text())
    id2label = {t["id"]: t["label"] for t in traits}
    id2assoc = {t["id"]: set(t.get("associated_pgs_ids") or []) for t in traits}
    label2id, syn2id = {}, {}
    for t in traits:
        label2id.setdefault(_norm(t["label"]), t["id"])
        for s in (t.get("trait_synonyms") or []):
            syn2id.setdefault(_norm(s), t["id"])
    pgs_efo, pgs_traits = {}, {}
    with open(REST_DUMP, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            te = rec.get("score", {}).get("trait_efo") or []
            pgs_efo[rec["pgs_id"]] = set(t.get("id") for t in te)
            pgs_traits[rec["pgs_id"]] = [(t.get("id"), t.get("label")) for t in te if t.get("label")]

    def resolve(ont, ids):
        n = _norm(ont)
        if n in label2id:
            return label2id[n]
        if n in syn2id:
            return syn2id[n]
        pe = Counter()
        for p in ids:
            for e in pgs_efo.get(p, set()):
                pe[e] += 1
        d = _concept(ont)
        cands = [e for e in pe if d and d <= _concept(id2label.get(e, ""))]
        if cands:
            return max(cands, key=lambda e: len(id2assoc.get(e, set())))
        return pe.most_common(1)[0][0] if pe else None

    return id2label, pgs_efo, pgs_traits, resolve


def build_clean_disease_maps(pgs_efo, id2label, resolve):
    within = pd.read_csv(WITHIN_META)
    within = within[pd.to_numeric(within["case_num"], errors="coerce").fillna(0) >= 200]
    cross = pd.read_csv(CROSS_PGS_LIST)
    icd_efos, icd_label = defaultdict(set), {}
    for src in (within, cross):
        for _, r in src.iterrows():
            e = resolve(str(r["ontology"]).strip(), _parse(r["pgs_ids"]))
            if e:
                icd = str(r["icd_root"]).strip()
                icd_efos[icd].add(e)
                icd_label.setdefault(icd, id2label.get(e, str(r["ontology"]).strip()))
    for icd, extra in RELATED_EFO_BY_ROOTCODE.items():
        if icd in icd_efos:
            icd_efos[icd].update(extra)
    name_of, seen = {}, {}
    for icd in icd_efos:
        base = icd_label.get(icd, icd)
        nm = base if base not in seen else f"{base} [{icd}]"
        seen[nm] = icd
        name_of[icd] = nm
    p2o, self_pgs, po2icd = defaultdict(set), defaultdict(set), {}
    for p, ev in pgs_efo.items():
        for icd, efos in icd_efos.items():
            if ev & efos:
                p2o[p].add(name_of[icd])
                self_pgs[icd].add(p)
                po2icd[(p, name_of[icd])] = icd
    icd2onts = {icd: [name_of[icd]] for icd in icd_efos}
    audit = pd.DataFrame([{"icd_root": icd, "name": name_of[icd], "n_efos": len(icd_efos[icd]),
                           "n_donor_pgs": len(self_pgs[icd])} for icd in sorted(icd_efos)])
    return dict(p2o), dict(self_pgs), icd2onts, po2icd, audit


def build_clean_measurement_map(pgs_efo, resolve):
    lo = pd.read_csv(LOINC_META)
    loinc_efo, loinc_meta = {}, {}
    for _, r in lo.iterrows():
        e = resolve(str(r["ontology"]).strip(), _parse(r["pgs_ids"]))
        loinc = str(r["loinc"]).strip()
        if e:
            loinc_efo[loinc] = e
        loinc_meta[loinc] = (str(r["ontology"]).strip(), str(r.get("description", "")).strip())
    out = defaultdict(list)
    for p, ev in pgs_efo.items():
        for loinc, e in loinc_efo.items():
            if e in ev:
                ont, desc = loinc_meta[loinc]
                out[p].append({"output_loinc": loinc, "output_ontology": ont, "output_description": desc})
    return dict(out)


def main():
    import build_benchmark as bb
    import rebuild_outputs as latest

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    id2label, pgs_efo, pgs_traits, resolve = _load()
    d_p2o, d_self, d_icd2onts, d_po2icd, audit = build_clean_disease_maps(pgs_efo, id2label, resolve)
    m_map = build_clean_measurement_map(pgs_efo, resolve)
    audit.to_csv(OUT_DIR / "source_disease_efo_map.csv", index=False)

    # --- 1) SELECTION via the legacy "60" method on clean data ---
    bb.build_pgs_to_ontology_map_full = lambda: {p: set(v) for p, v in d_p2o.items()}
    bb.build_icd_to_self_pgs_full = lambda: {i: set(v) for i, v in d_self.items()}
    bb.build_icd_to_ontologies_full = lambda: {i: list(v) for i, v in d_icd2onts.items()}
    bb.build_pgs_ontology_to_icd_map = lambda: dict(d_po2icd)
    bb.build_pgs_to_continuous_trait_map = lambda: {p: list(v) for p, v in m_map.items()}
    bb.CONTRIB1_LOINC_RESULT_DIR = LEGACY_NO_AOU / "aou_continuous"

    ext = pd.read_csv(EXTEND_MATRIX, index_col=0)
    allowed = set(ext.index.astype(str))
    titles = latest._load_canonical_icd_titles(latest.ICD_CANONICAL_TITLES_PATH)
    b2b, _ = bb.build_b2b_type_a_benchmark(ext, allowed, min_best_split_gap=0.0)
    b2c, _ = bb.build_b2c_type_a_benchmark(ext, allowed, min_best_split_gap=0.0)

    def _ph(df):
        out = df.copy()
        for idx, row in out[out["selected"]].iterrows():
            icd = str(row.get("input_icd", "")).strip()
            d = titles.get(icd, row.get("input_description", ""))
            out.at[idx, "input_description"] = d
            if (icd in latest.POST_HOC_ICD_BLOCKLIST or latest._primary_post_hoc_reason(d, "")
                    or latest._union_exclusion_reason(d, "", icd)):
                out.at[idx, "selected"] = False
        return out

    b2b, b2c = _ph(b2b), _ph(b2c)
    sel_icds = sorted(set(b2b[b2b["selected"]]["input_icd"].astype(str))
                      | set(b2c[b2c["selected"]]["input_icd"].astype(str)))
    desc_of = {str(r["input_icd"]).strip(): titles.get(str(r["input_icd"]).strip(), r.get("input_description", ""))
               for _, r in pd.concat([b2b, b2c]).iterrows()}

    # --- 2) UNIFIED clean ground-truth ranking for the selected targets ---
    col_pgs = {c: _col_to_pgs_id(c) for c in ext.columns}
    gt_rows, sel_rows = [], []
    for icd in sel_icds:
        auc_row = ext.loc[icd]
        trait_models, trait_disp = defaultdict(list), {}
        for col, pgs in col_pgs.items():
            v = auc_row[col]
            if not (pd.notna(v) and isinstance(v, (int, float))):
                continue
            for eid, lab in pgs_traits.get(pgs, []):
                k = _norm(lab)
                trait_models[k].append((pgs, float(v)))
                trait_disp.setdefault(k, lab)
        ranking = sorted(
            ({"source_trait": trait_disp[k], "n_pgs": len(v),
              "best_auc": round(max(v, key=lambda x: x[1])[1], 6),
              "best_pgs_id": max(v, key=lambda x: x[1])[0]} for k, v in trait_models.items()),
            key=lambda r: r["best_auc"], reverse=True)
        for i, r in enumerate(ranking, 1):
            r["rank"] = i
            gt_rows.append({"target_icd": icd, "target_description": desc_of.get(icd, ""), **r})
        top = ranking[0] if ranking else {}
        sel_rows.append({"input_type": "A", "target_source": "extend_trait", "input_icd": icd,
                         "input_ontology": "", "input_description": desc_of.get(icd, ""),
                         "n_source_traits": len(ranking), "top_cross_trait": top.get("source_trait", ""),
                         "top_cross_auc": top.get("best_auc"), "selected": True})

    (OUT_DIR / "unified").mkdir(exist_ok=True)
    pd.DataFrame(sel_rows).to_csv(OUT_DIR / "unified" / "target_selection.csv", index=False)
    pd.DataFrame(gt_rows).to_csv(OUT_DIR / "unified" / "ground_truth_ranking.csv", index=False)

    old = pd.read_csv(OLD_PAIRED80)
    old60 = set(old[old["input_type"] == "A"]["input_icd"].astype(str))
    new = set(sel_icds)
    print(f"EFO-clean Type A (legacy '60' standard + clean data): {len(new)} targets")
    print(f"  dropped vs frozen-60: {sorted(old60 - new)}")
    print(f"  added vs frozen-60  : {sorted(new - old60)}")
    print(f"  unified GT rows: {len(gt_rows)} ; source diseases: {len(audit)}")
    print(f"  outputs -> {OUT_DIR}")


if __name__ == "__main__":
    main()
