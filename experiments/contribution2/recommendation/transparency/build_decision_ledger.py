"""
Decision-ledger generator: a faithfulness-independent, code-emitted explanation
of WHY the within-trait PRS Agent recommends the PGS it does, for ANY disease.

The explanation is NOT the model's self-narration (which is unfaithful — reasoning
models verbalize the decisive factor ~25% of the time). It is reconstructed by
replaying the machine-checkable mirror of the appraisal skill (skill_rules.yaml)
over the exact structured evidence the model saw, joined to:
  - the agent's actual Stage-1 shortlist / Stage-2 pick (from the saved run),
  - the no-skill General-LLM pick (the single-variable counterfactual),
  - the held-out All-of-Us adjusted-AUC rank (joined last, never seen by the model),
  - a faithfulness audit: did the model's rationale even mention its decisive act?

Outputs per disease (under transparency/ledgers/):
  {disease}_ledger.csv        one row per candidate PGS (evidence + fired rules + decisions + AoU rank)
  {disease}_audit.json        faithfulness audit + counterfactual attribution
  {disease}_decision_card.md  human-readable step-by-step explanation

Trait-agnostic: nothing names a disease or PGS; swapping the disease swaps only data.

Run (any disease):
  .venv/bin/python experiments/contribution2/recommendation/transparency/build_decision_ledger.py "rheumatoid arthritis"
  .venv/bin/python .../build_decision_ledger.py --all      # all 44
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
import pandas as pd
from src.server.core.tools.pgs_single_record import build_single_record, load_rest_dump

ROOT = Path(os.getcwd())
TRANSP = ROOT / "experiments/contribution2/recommendation/transparency"
GT_DIR = ROOT / "experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
RUNS = ROOT / "experiments/contribution2/recommendation/runs"
AGENT_RUN = RUNS / "topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-20260610-002512"
LLM_RUN = RUNS / "without-domain-gpt-5.4-t1__44disease__efoclean44"
OUT = TRANSP / "ledgers"


# ---------------------------------------------------------------------------
# Evidence parsing (pure code over the single-record schema the model saw)
# ---------------------------------------------------------------------------
def _covariate_class(cov) -> str:
    s = str(cov or "").strip().lower()
    if s in ("", "0", "none", "nan", "null"):
        return "none"
    heavy = ["family history", "framingham", "charge", "qrisk", "pooled cohort",
             "absolute risk", "5-year", "10-year", "phenotype risk score", "treatment",
             "biomarker", "ldl", "hdl", "creatinine", "egfr", "hba1c", "glucose",
             "diabet", "blood pressure", "medication"]
    if any(h in s for h in heavy):
        # distinguish near-outcome biomarker from family-history/calculator packaging
        if any(b in s for b in ["biomarker", "ldl", "hdl", "creatinine", "egfr", "hba1c", "glucose"]):
            return "near_outcome_biomarker"
        return "heavy_clinical"
    basic_terms = {"age", "sex", "pc", "pcs", "pca", "array", "batch", "genotyping",
                   "site", "study", "principal", "components", "ancestry"}
    tokens = re.split(r"[,\s\-\(\)0-9]+", s)
    nonbasic = [t for t in tokens if t and not any(b in t for b in basic_terms)]
    mild_epi = {"smoking", "smoke", "bmi", "alcohol", "pack", "parity", "contraceptive"}
    if not nonbasic:
        return "basic"
    if all(any(m in t for m in mild_epi) for t in nonbasic):
        return "mild_epi"
    return "heavy_clinical"


def _evidence(pgs_id: str, dump) -> dict:
    r = build_single_record(pgs_id, dump) or {}
    pm = r.get("performance_metrics") or {}
    m = pm.get("metrics") or {}
    es = pm.get("evaluation_sample") or {}
    eff = {e.get("name_short"): e.get("estimate") for e in (m.get("effect_sizes") or [])}
    method = (r.get("development_method") or {}).get("method_name") or ""
    return {
        "pgs_id": pgs_id,
        "full_model_auroc": m.get("full_model_auroc"),
        "pgs_only_auroc": m.get("pgs_only_auroc"),
        "pgs_only_r2": m.get("pgs_only_r2"),
        "c_index": m.get("c_index"),
        "or_per_sd": eff.get("OR"),
        "hr_per_sd": eff.get("HR"),
        "covariate_class": _covariate_class(pm.get("covariates")),
        "method": method,
        "method_is_ensemble": bool(re.search(r"multi.?prs|ensemble|prsmix|metaprs|mixsc|combin", method, re.I)),
        "n_eval_cohorts": len(es.get("cohorts") or []),
        "endpoint": pm.get("phenotyping_reported"),
    }


# ---------------------------------------------------------------------------
# Rule predicates — mirror skill_rules.yaml exactly (keyed by id)
# ---------------------------------------------------------------------------
def _num(x):
    return x if isinstance(x, (int, float)) else None


def _fire(ev: dict, best_full_auroc) -> list[tuple[str, int]]:
    """Return [(rule_id, polarity)] of rules that fire on this candidate."""
    f = []
    auc, p_auc, p_r2 = _num(ev["full_model_auroc"]), _num(ev["pgs_only_auroc"]), _num(ev["pgs_only_r2"])
    orv, hrv = _num(ev["or_per_sd"]), _num(ev["hr_per_sd"])
    eff_max = max([v for v in (orv, hrv) if v is not None], default=None)
    cc = ev["covariate_class"]
    if p_auc is not None or p_r2 is not None:
        f.append(("§2.pgs_only_present", +3))
    if eff_max is not None and eff_max >= 1.5:
        f.append(("§2.or_hr_strong", +2))
    elif eff_max is not None and eff_max >= 1.3:
        f.append(("§2.or_hr_moderate", +1))
    if auc is not None and p_auc is None and p_r2 is None:
        f.append(("§2.full_auroc_not_primary", -1))
    if auc is not None and orv is None and hrv is None and p_auc is None and p_r2 is None:
        f.append(("§2.headline_auroc_no_clean_effect", -2))
    if auc is not None and best_full_auroc is not None and abs(auc - best_full_auroc) < 0.05:
        f.append(("§2.auroc_gap_noise", 0))
    if cc in ("none", "basic"):
        f.append(("§2.covariate_clean", +1))
    if cc in ("heavy_clinical", "near_outcome_biomarker"):
        f.append(("§2.covariate_leakage", -2))
    if ev["method_is_ensemble"]:
        f.append(("§5.ensemble_favorable", +1))
    if ev["n_eval_cohorts"] >= 2:
        f.append(("§3.multi_cohort_robust", +1))
    return f


# ---------------------------------------------------------------------------
# Build one disease ledger
# ---------------------------------------------------------------------------
def _norm(s):
    return " ".join(str(s).lower().split())


def _load_runs():
    agent_sum = json.loads((AGENT_RUN / "experiment_topk_holistic_rerank_batch_summary.json").read_text())
    agent_s2 = json.loads((AGENT_RUN / "experiment_topk_holistic_rerank_batch_stage2_results.json").read_text())
    shortlists = agent_sum["pairwise_rerank"]["ranked_candidates_by_ontology"]
    s2_by_ont = {r["ontology"]: r for r in agent_s2}
    llm = json.loads((LLM_RUN / "experiment_without_domain_results.json").read_text())
    llm_list = llm if isinstance(llm, list) else llm.get("results", [])
    llm_by_ont = {}
    for r in llm_list:
        if isinstance(r, dict) and r.get("ontology"):
            llm_by_ont.setdefault(r["ontology"], r)
    bench = json.loads((GT_DIR / "benchmark_auc_per_ontology.json").read_text())
    return shortlists, s2_by_ont, llm_by_ont, bench


def build_ledger(disease: str, dump, runs) -> dict:
    shortlists, s2_by_ont, llm_by_ont, bench = runs
    key = _norm(disease)
    aou = bench.get(key) or {}
    if not aou:
        raise SystemExit(f"no ground truth for '{disease}'")
    pool = list(aou.keys())
    ranked = sorted(pool, key=lambda p: aou[p], reverse=True)
    aou_rank = {p: i + 1 for i, p in enumerate(ranked)}

    s2 = s2_by_ont.get(disease, {})
    shortlist = shortlists.get(disease, [])
    agent_pick = s2.get("winner_model_id")
    rationale = s2.get("rationale") or ""
    llm = llm_by_ont.get(disease, {})
    llm_pick = llm.get("recommended_pgs_id")

    evs = {p: _evidence(p, dump) for p in pool}
    best_full = max([_num(evs[p]["full_model_auroc"]) for p in pool if _num(evs[p]["full_model_auroc"]) is not None], default=None)

    rows = []
    for p in pool:
        ev = evs[p]
        fired = _fire(ev, best_full)
        score = sum(pol for _, pol in fired)
        neg = [(rid, pol) for rid, pol in fired if pol < 0]
        excl_rule = min(neg, key=lambda x: x[1])[0] if neg else ""
        rows.append({
            **{k: ev[k] for k in ["pgs_id", "full_model_auroc", "pgs_only_auroc", "pgs_only_r2",
                                  "or_per_sd", "hr_per_sd", "covariate_class", "method",
                                  "method_is_ensemble", "n_eval_cohorts", "endpoint"]},
            "fired_rules": ";".join(rid for rid, _ in fired),
            "transparency_score": score,
            "stage1_kept": p in shortlist,
            "stage1_exclusion_rule": "" if p in shortlist else excl_rule,
            "stage2_rank": (shortlist.index(p) + 1) if p in shortlist else None,
            "is_agent_pick": p == agent_pick,
            "is_general_llm_pick": p == llm_pick,
            "aou_auc": round(aou[p], 6),
            "aou_rank": aou_rank[p],
        })
    df = pd.DataFrame(rows).sort_values("aou_rank").reset_index(drop=True)

    # faithfulness audit: did the model's rationale name the candidate it excluded
    # at Stage-1 that the no-skill LLM picked (the decisive divergence)?
    decisive_excluded = llm_pick if (llm_pick and llm_pick not in shortlist) else None
    mentioned = bool(decisive_excluded and decisive_excluded in rationale)
    audit = {
        "disease": disease,
        "pool_n": len(pool),
        "agent_pick": agent_pick, "agent_pick_aou_rank": aou_rank.get(agent_pick),
        "general_llm_pick": llm_pick, "general_llm_pick_aou_rank": aou_rank.get(llm_pick),
        "agent_hit_at_1": aou_rank.get(agent_pick) == 1,
        "skill_decisive": bool(agent_pick != llm_pick),
        "decisive_act": (f"excluded {decisive_excluded} at Stage-1; the no-skill LLM picked it on headline metrics"
                         if decisive_excluded else "agent and no-skill LLM converged"),
        "model_rationale_mentions_decisive_excluded": mentioned,
        "faithfulness_flag": ("UNFAITHFUL: decisive Stage-1 exclusion not verbalized — the explanation is the ledger, not this text"
                              if (decisive_excluded and not mentioned) else "n/a"),
        "model_stated_rationale": rationale,
    }
    return {"df": df, "audit": audit, "shortlist": shortlist}


def _card_md(disease, res) -> str:
    df, a = res["df"], res["audit"]
    pick = df[df.is_agent_pick]
    llm = df[df.is_general_llm_pick]
    L = [f"# Decision card — {disease}", "",
         f"**Pool:** {a['pool_n']} same-EFO PGS · **Agent pick:** `{a['agent_pick']}` → AoU rank "
         f"**{a['agent_pick_aou_rank']}** ({'HIT@1 ✓' if a['agent_hit_at_1'] else 'miss'})",
         f"**No-skill General LLM pick:** `{a['general_llm_pick']}` → AoU rank **{a['general_llm_pick_aou_rank']}**"
         f"  ·  skill-decisive: **{a['skill_decisive']}**", ""]
    if a["skill_decisive"] and not pick.empty and not llm.empty:
        pr, lr = pick.iloc[0], llm.iloc[0]
        L += ["## Why the skill flips the pick (code-reconstructed, not model narration)", "",
              f"| field | Agent `{pr.pgs_id}` (AoU rank {pr.aou_rank}) | General-LLM `{lr.pgs_id}` (AoU rank {lr.aou_rank}) |",
              "|---|---|---|",
              f"| full_model_auroc | {pr.full_model_auroc} | {lr.full_model_auroc} |",
              f"| pgs_only_auroc/r2 | {pr.pgs_only_auroc}/{pr.pgs_only_r2} | {lr.pgs_only_auroc}/{lr.pgs_only_r2} |",
              f"| per-SD OR/HR | {pr.or_per_sd}/{pr.hr_per_sd} | {lr.or_per_sd}/{lr.hr_per_sd} |",
              f"| covariate_class | {pr.covariate_class} | {lr.covariate_class} |",
              f"| method (ensemble?) | {pr.method} ({pr.method_is_ensemble}) | {lr.method} ({lr.method_is_ensemble}) |",
              f"| fired skill rules | {pr.fired_rules} | {lr.fired_rules} |", "",
              f"- Stage-1 exclusion of the no-skill pick: rule **{llm.iloc[0].stage1_exclusion_rule or '—'}**"
              f" (kept by Agent Stage-1: {bool(lr.stage1_kept)}).", ""]
    L += ["## Faithfulness audit",
          f"- decisive act: {a['decisive_act']}",
          f"- model rationale mentions it: **{a['model_rationale_mentions_decisive_excluded']}** → {a['faithfulness_flag']}",
          f"- model's stated rationale (quarantined): _{a['model_stated_rationale'][:300]}…_", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("disease", nargs="?")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    dump = load_rest_dump()
    runs = _load_runs()
    bench = runs[3]
    targets = list(bench.keys()) if args.all else [args.disease]
    summary = []
    for d in targets:
        res = build_ledger(d, dump, runs)
        safe = _norm(d).replace(" ", "_")
        res["df"].to_csv(OUT / f"{safe}_ledger.csv", index=False)
        (OUT / f"{safe}_audit.json").write_text(json.dumps(res["audit"], indent=2))
        (OUT / f"{safe}_decision_card.md").write_text(_card_md(d, res))
        a = res["audit"]
        summary.append(dict(disease=d, agent_rank=a["agent_pick_aou_rank"], hit1=a["agent_hit_at_1"],
                            skill_decisive=a["skill_decisive"], unfaithful=(a["faithfulness_flag"] != "n/a")))
        print(f"  {d:34s} agent_rank={a['agent_pick_aou_rank']} hit@1={a['agent_hit_at_1']} "
              f"skill_decisive={a['skill_decisive']} unfaithful_rationale={a['faithfulness_flag']!='n/a'}")
    if args.all:
        pd.DataFrame(summary).to_csv(OUT / "_summary.csv", index=False)
        print(f"\nwrote {len(summary)} ledgers + _summary.csv to {OUT}")


if __name__ == "__main__":
    main()
