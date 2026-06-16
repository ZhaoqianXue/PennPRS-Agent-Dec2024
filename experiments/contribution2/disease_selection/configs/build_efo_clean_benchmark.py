"""
EFO-clean Contribution2 within-trait benchmark builder (per-rootcode, 3 steps).

Motivation
----------
The legacy 45-disease list and its candidate pools were derived from the
Contribution1 AUC metadata `pgs_ids` column, which was retrieved too broadly: a
disease's pool contained PGS belonging to *other* diseases' EFO traits (e.g.
gout's 59-PGS pool = 32 gout + 27 rheumatoid arthritis). PGS Catalog is keyed by
EFO trait, so the within-trait benchmark must be SELF-PGS ONLY: the PGS that PGS
Catalog associates with the disease's own EFO trait, intersected with the PGS
that Contribution1 actually evaluated in All of Us.

This rebuilds the benchmark from scratch, per ICD rootcode, in the user-specified
order:

  STEP 1 - candidate pool, for EVERY rootcode.
      For each rootcode, the canonical EFO is the EFO -- among the EFOs that the
      rootcode's own Contribution1 ontology rows resolve to -- holding the most
      evaluated PGS. (Off-target diseases are never rows under the target
      rootcode, so this is contamination-proof and needs no hand overrides.)
      candidate_pool(rootcode) = canonical-EFO associated PGS  INTERSECT  the PGS
      columns Contribution1 evaluated. This count drives selection.

  STEP 2 - disease list.
      Keep rootcodes with |candidate_pool| >= MIN_CANDIDATE_POOL and best-PGS
      AUC >= MIN_TOP1_AUC. Purely objective / trait-agnostic; no allowlist or
      blacklist.

  STEP 3 - evaluation pool (ground truth).
      For the selected diseases only, emit the candidate pool ranked by AoU
      adjusted AUC (= the answer key), in the JSON schema the recommendation
      harness already consumes.

EFO resolution per ontology row: exact PGS Catalog label -> trait synonym ->
guarded plurality (the row's own contaminated pool, restricted to EFOs sharing
the disease's normalized medical concept, max evaluated).

Trait-agnostic note: this is BENCHMARK CONSTRUCTION and may use the EFO ontology.
The recommendation agent never sees any of this mapping.

Run: /Users/zhaoqianxue/anaconda3/bin/python \
       experiments/contribution2/disease_selection/configs/build_efo_clean_benchmark.py
"""
from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Selection parameters (user-chosen)
# ---------------------------------------------------------------------------
MIN_CANDIDATE_POOL = 6     # >= 6 evaluated self-PGS to be a non-trivial pick task
MIN_TOP1_AUC = 0.55        # best self-PGS must be meaningfully predictive
MIN_CASE_COUNT = 200       # AoU case-count floor for a reliable AUC

# Disease universe. "case200" = every rootcode with case_count >= MIN_CASE_COUNT,
# which recovers diseases Contribution1 flagged include_in_analysis=0 only because
# its broad pgs_ids retrieval returned zero candidates (pgs_num=0) -- e.g. celiac
# disease, multiple sclerosis, cholelithiasis. "included" = Contribution1's own
# include_in_analysis==1 set (more conservative).
UNIVERSE_MODE = "case200"  # "case200" | "included"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONFIGS_DIR = Path(__file__).resolve().parent
DISEASE_SELECTION_DIR = CONFIGS_DIR.parent
PROJECT_ROOT = CONFIGS_DIR.parents[3]
CONTRIB1_DIR = (
    PROJECT_ROOT / "experiments" / "contribution1" / "result"
    / "legacy_no_aou_pgs" / "aou_binary"
)
REST_DUMP = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_full_rest_dump.jsonl"
EFO_REBUILD_DIR = DISEASE_SELECTION_DIR / "efo_rebuild"
CATALOG_TRAITS = EFO_REBUILD_DIR / "pgs_catalog_traits_all.json"
GROUND_TRUTH_DIR = EFO_REBUILD_DIR / "ground-truth__efoclean"


def _norm(s: object) -> str:
    return " ".join(str(s).lower().split())


# medical-concept normalization, used only by the guarded plurality fallback
_CANCER = {"carcinoma", "cancer", "neoplasm", "tumor", "tumour", "malignant",
           "malignancy", "adenocarcinoma"}
_DROP = {"disease", "disorder", "the", "of", "gland"}


def _concept(s: str) -> frozenset[str]:
    toks = "".join(c if (c.isalnum() or c == " ") else " " for c in _norm(s)).split()
    return frozenset("CANCER" if t in _CANCER else t for t in toks if t not in _DROP)


def _parse_pgs_ids(s: object) -> list[str]:
    try:
        out = ast.literal_eval(str(s))
        return list(out) if isinstance(out, (list, tuple)) else [out]
    except (ValueError, SyntaxError):
        return []


# ---------------------------------------------------------------------------
# Load reference data
# ---------------------------------------------------------------------------
def load_context() -> dict:
    traits = json.loads(CATALOG_TRAITS.read_text())
    id2label, id2assoc, label2id, syn2id = {}, {}, {}, {}
    for t in traits:
        tid = t["id"]
        id2label[tid] = t["label"]
        id2assoc[tid] = set(t.get("associated_pgs_ids") or [])
        label2id.setdefault(_norm(t["label"]), tid)
        for s in (t.get("trait_synonyms") or []):
            syn2id.setdefault(_norm(s), tid)

    pgs_efo: dict[str, list[str]] = {}
    with open(REST_DUMP, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            pgs_efo[rec["pgs_id"]] = [t.get("id") for t in (rec.get("score", {}).get("trait_efo") or [])]

    matrix = pd.read_csv(CONTRIB1_DIR / "prs_adjauc_matrix_binary_combined_rootcode.csv")
    matrix = matrix.set_index("trait")
    pgs_to_col = {c.replace("_hmPOS_GRCh38", ""): c for c in matrix.columns}
    matrix_pgs = set(pgs_to_col)

    meta = pd.read_csv(CONTRIB1_DIR / "prs_adjauc_metadata_binary_combined_rootcode.csv")
    case = pd.read_csv(CONTRIB1_DIR / "trait_case_count_binary_combined_rootcode.csv")
    case_map = case.drop_duplicates("ICD10_code").set_index("ICD10_code")["case_count"].to_dict()

    return dict(id2label=id2label, id2assoc=id2assoc, label2id=label2id, syn2id=syn2id,
                pgs_efo=pgs_efo, matrix=matrix, pgs_to_col=pgs_to_col,
                matrix_pgs=matrix_pgs, meta=meta, case_map=case_map)


# ---------------------------------------------------------------------------
# EFO resolution for one ontology row
# ---------------------------------------------------------------------------
def resolve_ontology_efo(ontology: str, current_pgs_ids: list[str], ctx: dict) -> tuple[str | None, str]:
    n = _norm(ontology)
    if n in ctx["label2id"]:
        return ctx["label2id"][n], "label"
    if n in ctx["syn2id"]:
        return ctx["syn2id"][n], "synonym"
    pool_efos = Counter()
    for p in current_pgs_ids:
        for e in ctx["pgs_efo"].get(p, []):
            pool_efos[e] += 1
    dcon = _concept(ontology)
    cands = [e for e in pool_efos if dcon and dcon <= _concept(ctx["id2label"].get(e, ""))]
    if cands:
        best = max(cands, key=lambda e: len(ctx["id2assoc"].get(e, set()) & ctx["matrix_pgs"]))
        return best, "plurality-self"
    if pool_efos:
        return pool_efos.most_common(1)[0][0], "plurality-raw"
    return None, "unresolved"


# ---------------------------------------------------------------------------
# STEP 1: candidate pool per rootcode
# ---------------------------------------------------------------------------
def build_candidate_pools(ctx: dict) -> pd.DataFrame:
    meta = ctx["meta"]
    if UNIVERSE_MODE == "included":
        inc = meta[meta["include_in_analysis"] == 1]
    else:  # case200: every rootcode with adequate AoU case count
        inc = meta[meta["icd_root"].map(lambda r: ctx["case_map"].get(r, 0) >= MIN_CASE_COUNT)]
    rows = []
    for icd_root, grp in inc.groupby("icd_root"):
        # resolve every ontology row under this rootcode, keep the EFO with the
        # most evaluated PGS (= the canonical disease trait for this rootcode).
        per_efo: dict[str, dict] = {}
        for _, r in grp.iterrows():
            efo, method = resolve_ontology_efo(r["ontology"], _parse_pgs_ids(r["pgs_ids"]), ctx)
            if not efo:
                continue
            pool = ctx["id2assoc"].get(efo, set()) & ctx["matrix_pgs"]
            if efo not in per_efo or len(pool) > per_efo[efo]["pool_n"]:
                per_efo[efo] = dict(ontology=r["ontology"], method=method,
                                    pool=sorted(pool), pool_n=len(pool))
        if not per_efo:
            continue
        best_efo = max(per_efo, key=lambda e: per_efo[e]["pool_n"])
        best = per_efo[best_efo]

        # AUC ranking from the (dense) matrix row for this rootcode.
        ranked = []
        if icd_root in ctx["matrix"].index:
            mrow = ctx["matrix"].loc[icd_root]
            aucs = {p: float(mrow[ctx["pgs_to_col"][p]]) for p in best["pool"]
                    if pd.notna(mrow[ctx["pgs_to_col"][p]])}
            ranked = sorted(aucs.items(), key=lambda kv: kv[1], reverse=True)
        auc_vals = [v for _, v in ranked]
        top1 = auc_vals[0] if auc_vals else None
        gaps = [auc_vals[i] - auc_vals[i + 1] for i in range(min(5, len(auc_vals) - 1))]
        max_gap = max(gaps) if gaps else 0.0

        rows.append(dict(
            icd_root=icd_root,
            disease=best["ontology"],
            canonical_efo=best_efo,
            canonical_label=ctx["id2label"].get(best_efo, ""),
            resolution_method=best["method"],
            candidate_pool=len(best["pool"]),
            catalog_related=len(ctx["id2assoc"].get(best_efo, set())),
            case_count=int(ctx["case_map"].get(icd_root, 0)),
            mean_auc=round(sum(auc_vals) / len(auc_vals), 4) if auc_vals else None,
            median_auc=round(float(pd.Series(auc_vals).median()), 4) if auc_vals else None,
            min_auc=round(min(auc_vals), 4) if auc_vals else None,
            max_gap=round(max_gap, 4),
            **{f"top{i+1}_auc": (round(auc_vals[i], 4) if i < len(auc_vals) else None) for i in range(10)},
            ranked_pgs=[p for p, _ in ranked],
            ranked_auc={p: round(v, 6) for p, v in ranked},
        ))
    return pd.DataFrame(rows).sort_values("candidate_pool", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# STEP 2 + 3
# ---------------------------------------------------------------------------
def select_and_emit(pools: pd.DataFrame) -> pd.DataFrame:
    pools = pools.copy()
    pools["selected"] = (
        (pools["candidate_pool"] >= MIN_CANDIDATE_POOL)
        & (pools["top1_auc"].fillna(0) >= MIN_TOP1_AUC)
    )
    pools["exclude_reason"] = ""
    pools.loc[pools["candidate_pool"] < MIN_CANDIDATE_POOL, "exclude_reason"] = "pool<6"
    pools.loc[(pools["candidate_pool"] >= MIN_CANDIDATE_POOL) & (pools["top1_auc"].fillna(0) < MIN_TOP1_AUC),
              "exclude_reason"] = "top1<0.55"
    selected = pools[pools["selected"]].sort_values("candidate_pool", ascending=False).reset_index(drop=True)

    # STEP 3: ground-truth JSONs (keyed by normalized disease name).
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    evaluated, top_k, bench = {}, {}, {}
    for _, r in selected.iterrows():
        key = _norm(r["disease"])
        evaluated[key] = list(r["ranked_pgs"])
        top_k[key] = list(r["ranked_pgs"])
        bench[key] = dict(r["ranked_auc"])
    (GROUND_TRUTH_DIR / "evaluated_pgs_per_ontology.json").write_text(json.dumps(evaluated, indent=2, sort_keys=True))
    (GROUND_TRUTH_DIR / "top_k_pgs_per_ontology.json").write_text(json.dumps(top_k, indent=2, sort_keys=True))
    (GROUND_TRUTH_DIR / "benchmark_auc_per_ontology.json").write_text(json.dumps(bench, indent=2, sort_keys=True))
    return selected, pools


def _cell(v):
    return "-" if v is None or (isinstance(v, float) and pd.isna(v)) else v


def write_disease_list(selected: pd.DataFrame) -> Path:
    n = len(selected)
    out = EFO_REBUILD_DIR / f"selected_diseases_efoclean__{n}disease.csv"
    rows = []
    for _, r in selected.iterrows():
        rows.append({
            "Ontology": r["disease"],
            "ICD": r["icd_root"],
            "N Models": r["candidate_pool"],
            "Max": _cell(r["top1_auc"]),
            "Mean": _cell(r["mean_auc"]),
            "Median": _cell(r["median_auc"]),
            "Min": _cell(r["min_auc"]),
            **{f"Top-{i}": _cell(r.get(f"top{i}_auc")) for i in range(1, 11)},
            "Case N": r["case_count"],
            "QC1 (>=0.025)": "Yes" if r["max_gap"] >= 0.025 else "No",
            "EFO": r["canonical_efo"],
            "EFO Label": r["canonical_label"],
            "Source": "rootcode",
        })
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    (EFO_REBUILD_DIR / f"selected_diseases_efoclean__{n}disease.txt").write_text(
        "\n".join(df["Ontology"].astype(str)) + "\n")
    return out


def main() -> None:
    EFO_REBUILD_DIR.mkdir(parents=True, exist_ok=True)
    ctx = load_context()

    print("== STEP 1: candidate pool per rootcode ==")
    pools = build_candidate_pools(ctx)
    print(f"   rootcodes resolved: {len(pools)}")

    print("== STEP 2 + 3: select + emit ground truth ==")
    selected, pools = select_and_emit(pools)

    # persist the full per-rootcode candidate table (with selection columns)
    keep_cols = ["icd_root", "disease", "canonical_efo", "canonical_label", "resolution_method",
                 "candidate_pool", "catalog_related", "case_count", "top1_auc", "mean_auc",
                 "max_gap", "selected", "exclude_reason"]
    pools[keep_cols].sort_values(["selected", "candidate_pool"], ascending=[False, False]).to_csv(
        EFO_REBUILD_DIR / "candidate_pool_per_rootcode.csv", index=False)

    list_path = write_disease_list(selected)
    print(f"\n   selected diseases : {len(selected)}")
    print(f"   disease list      : {list_path.name}")
    print(f"   ground truth      : {GROUND_TRUTH_DIR.name}/")
    print(f"   candidate table   : candidate_pool_per_rootcode.csv ({len(pools)} rootcodes)")


if __name__ == "__main__":
    main()
