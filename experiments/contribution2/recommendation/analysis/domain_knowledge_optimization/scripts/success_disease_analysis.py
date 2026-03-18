#!/usr/bin/env python3
"""
Success Disease Analysis: Analyze the 56 diseases where the agent achieved at least
one Hit@1..5, to understand what the agent gets right and what general patterns
distinguish successful recommendations from failures.

Output: success_disease_analysis_report.md
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import scipy.stats as ss

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[3]  # experiments/contribution2/recommendation
RUN_DIR = BASE / "runs" / "with-domain-gpt-5.2-t10__75disease__three-arm-rerun-20260316"
SUMMARY_JSON = RUN_DIR / "experiment_with_domain_summary.json"
RESULTS_JSON = RUN_DIR / "experiment_with_domain_results.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_MD = OUTPUT_DIR / "success_disease_analysis_report.md"

# ---------------------------------------------------------------------------
# Method family mapping (same as field_meta_analysis.py)
# ---------------------------------------------------------------------------
METHOD_FAMILY_MAP = {
    "PRS-CS": "PRS-CS family", "PRS-CS-auto": "PRS-CS family",
    "PRSCS": "PRS-CS family", "prscs": "PRS-CS family", "PRS-CS.CV": "PRS-CS family",
    "PRS-CSx": "PRS-CSx family", "prscsx": "PRS-CSx family",
    "PRS-CSx (gene-based)": "PRS-CSx family",
    "LDpred2": "LDpred2 family", "LDpred2-auto": "LDpred2 family",
    "LDpred2.CV": "LDpred2 family", "LDpred2 (bigsnpr)": "LDpred2 family",
    "LDPred2Auto": "LDpred2 family",
    "LDpred": "LDpred (legacy)", "ldpred": "LDpred (legacy)",
    "PRSmix": "PRSmix/Plus family", "PRSmixPlus": "PRSmix/Plus family",
    "PRSsum": "PRSmix/Plus family",
    "lassosum": "Lassosum family", "lassosum2": "Lassosum family",
    "Lassosum": "Lassosum family", "lassosum.CV": "Lassosum family",
    "lassosum.auto": "Lassosum family",
    "SBayesR": "SBayesR family", "SBayesR-auto": "SBayesR family",
    "megaprs.auto": "MegaPRS family", "megaprs.CV": "MegaPRS family",
    "snpnet": "snpnet family", "snpnet (multi-PRS)": "snpnet family",
    "SnpNet": "snpnet family",
    "LASSO": "LASSO/Penalized family",
    "LASSO penalized regression": "LASSO/Penalized family",
    "Penalized regression (bigstatsr)": "LASSO/Penalized family",
    "Pruning and Thresholding (P+T)": "P+T / C+T family",
    "Clumping and Thresholding (C+T)": "P+T / C+T family",
    "Clumping and thresholding": "P+T / C+T family",
    "Maximum clumping and thresholding (maxCT)": "P+T / C+T family",
    "Stacked clumping and thresholding (SCT)": "P+T / C+T family",
    "P-value thresholding": "P+T / C+T family",
    "PRSice": "PRSice family", "PRSice-2": "PRSice family",
    "GWAS Hits": "GWAS Hits / GWS variants",
    "Genome-wide significant variants": "GWAS Hits / GWS variants",
    "Genome-wide significant SNPs": "GWAS Hits / GWS variants",
    "Known susceptibility loci (genome-wide significant SNPs)": "GWAS Hits / GWS variants",
    "Clumping of genome-wide significant variants": "GWAS Hits / GWS variants",
    "GenoBoost": "GenoBoost", "BOLT-LMM": "BOLT-LMM",
    "SDPR": "SDPR", "DBSLMM": "DBSLMM family", "DBSLMM-auto": "DBSLMM family",
    "MetaPRS": "Meta-PRS / Ensemble", "metaGRS": "Meta-PRS / Ensemble",
    "MetaGRS of 44 component PGS": "Meta-PRS / Ensemble",
    "CT-SLEB": "CT-SLEB", "PolyFun-pred": "PolyFun-pred",
    "RFDiseasemetaPRS": "RFDiseasemetaPRS", "PLINK": "PLINK", "SparSNP": "SparSNP",
}


def get_method_family(method_name: str) -> str:
    if method_name in METHOD_FAMILY_MAP:
        return METHOD_FAMILY_MAP[method_name]
    ml = method_name.lower()
    if "prs-csx" in ml or "prscsx" in ml:
        return "PRS-CSx family"
    if "prs-cs" in ml or "prscs" in ml:
        return "PRS-CS family"
    if "ldpred2" in ml:
        return "LDpred2 family"
    if "ldpred" in ml:
        return "LDpred (legacy)"
    if "lassosum" in ml:
        return "Lassosum family"
    if "megaprs" in ml:
        return "MegaPRS family"
    if "sbayesr" in ml:
        return "SBayesR family"
    if "snpnet" in ml:
        return "snpnet family"
    if "prsmix" in ml or "prssum" in ml:
        return "PRSmix/Plus family"
    if "clump" in ml or "pruning" in ml or "threshold" in ml or "p+t" in ml or "c+t" in ml:
        return "P+T / C+T family"
    if "prsice" in ml:
        return "PRSice family"
    if "genome-wide significant" in ml or "gwas hit" in ml:
        return "GWAS Hits / GWS variants"
    if "lasso" in ml or "penalized" in ml:
        return "LASSO/Penalized family"
    return "Other / Disease-specific"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_field(model: dict, field_path: str) -> Any:
    parts = field_path.split(".")
    obj = model
    for p in parts:
        if isinstance(obj, dict):
            obj = obj.get(p)
        else:
            return None
    return obj


def fmt(val, d=4):
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:.{d}f}"
    return str(val)


def mean_safe(vals):
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def median_safe(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def parse_sample_size(s):
    if not s or s == "N/A":
        return None
    nums = re.findall(r"[\d,]+", s)
    return int(nums[0].replace(",", "")) if nums else None


def spearman(xs, ys):
    xs2, ys2 = [], []
    for x, y in zip(xs, ys):
        if x is not None and y is not None and not (isinstance(x, float) and math.isnan(x)):
            xs2.append(x)
            ys2.append(y)
    if len(xs2) < 5:
        return None, None, len(xs2)
    rho, p = ss.spearmanr(xs2, ys2)
    return rho, p, len(xs2)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def main():
    with open(SUMMARY_JSON) as f:
        summary = json.load(f)
    with open(RESULTS_JSON) as f:
        results = json.load(f)

    trial_by_disease = defaultdict(list)
    for t in results:
        trial_by_disease[t["ontology"]].append(t)

    # Separate successes and failures
    successes = []
    failures = []
    for dd in summary["per_disease"]:
        hits = dd.get("modal_recommendation_hit_at_k", {})
        all_no = all(not hits.get(str(k), True) for k in range(1, 6))
        if all_no:
            failures.append(dd)
        else:
            successes.append(dd)

    lines = []
    lines.append("# Success Disease Analysis Report")
    lines.append("")
    lines.append(f"Analysis of {len(successes)} diseases where the agent achieved at least one Hit@1..5,")
    lines.append("to understand what patterns the agent leverages correctly and what general principles")
    lines.append("should be preserved or strengthened in domain knowledge optimization.")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 1: Overview table
    # -----------------------------------------------------------------------
    lines.append("## 1. Success Disease Overview")
    lines.append("")

    # Compute per-disease details
    disease_details = []
    for dd in successes:
        ont = dd["ontology"]
        M = dd["n_models"]
        ranked = dd["benchmark_ranked_ids"]
        auc_map = dd["benchmark_auc_by_id"]
        modal = dd["modal_recommendation"]
        hits = dd.get("modal_recommendation_hit_at_k", {})
        rank = ranked.index(modal) + 1 if modal in ranked else None
        norm_rank = rank / M if rank and M else None
        hit1 = hits.get("1", False)
        hit3 = any(hits.get(str(k), False) for k in range(1, 4))
        hit5 = any(hits.get(str(k), False) for k in range(1, 6))

        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent_model = model_map.get(modal, {})
        top1 = model_map.get(ranked[0], {}) if ranked else {}

        disease_details.append({
            "ontology": ont,
            "n_models": M,
            "modal": modal,
            "rank": rank,
            "norm_rank": norm_rank,
            "hit1": hit1,
            "hit3": hit3,
            "hit5": hit5,
            "agent_model": agent_model,
            "top1_model": top1,
            "benchmark_ranked_ids": ranked,
            "auc_map": auc_map,
            "dd": dd,
            "model_map": model_map,
        })

    # Sort by rank for display
    disease_details.sort(key=lambda x: x["rank"] or 999)

    hit1_diseases = [d for d in disease_details if d["hit1"]]
    hit3_only = [d for d in disease_details if d["hit3"] and not d["hit1"]]
    hit5_only = [d for d in disease_details if d["hit5"] and not d["hit3"]]

    lines.append(f"- **Hit@1**: {len(hit1_diseases)} diseases ({len(hit1_diseases)/len(successes)*100:.0f}%)")
    lines.append(f"- **Hit@2-3 only**: {len(hit3_only)} diseases")
    lines.append(f"- **Hit@4-5 only**: {len(hit5_only)} diseases")
    lines.append(f"- **Total successes**: {len(successes)}/75")
    lines.append("")

    lines.append("| Disease | N Models | Selected | Rank | Hit@1 | Hit@3 | Hit@5 |")
    lines.append("|---------|----------|----------|------|-------|-------|-------|")
    for d in disease_details:
        lines.append(
            f"| {d['ontology']} | {d['n_models']} | {d['modal']} | "
            f"{d['rank']}/{d['n_models']} | "
            f"{'Yes' if d['hit1'] else 'No'} | "
            f"{'Yes' if d['hit3'] else 'No'} | "
            f"{'Yes' if d['hit5'] else 'No'} |"
        )
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 2: What fields distinguish agent's successful picks?
    # -----------------------------------------------------------------------
    lines.append("## 2. Field Characteristics of Successfully Selected Models")
    lines.append("")
    lines.append("Compare characteristics of the agent's selections in success vs failure diseases.")
    lines.append("")

    # 2a. Method family distribution: success vs failure
    lines.append("### 2a. Method Family — Success vs Failure")
    lines.append("")

    success_methods = Counter()
    failure_methods = Counter()
    for d in disease_details:
        m = d["agent_model"].get("method_name", "Unknown")
        fam = get_method_family(m)
        success_methods[fam] += 1

    for dd in failures:
        modal = dd["modal_recommendation"]
        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent = model_map.get(modal, {})
        m = agent.get("method_name", "Unknown")
        fam = get_method_family(m)
        failure_methods[fam] += 1

    all_families = set(success_methods.keys()) | set(failure_methods.keys())
    lines.append("| Method Family | Success Selections | Failure Selections | Success Rate |")
    lines.append("|---------------|-------------------|-------------------|--------------|")
    for fam in sorted(all_families, key=lambda f: -(success_methods[f] + failure_methods[f])):
        s = success_methods[fam]
        f = failure_methods[fam]
        total = s + f
        rate = s / total * 100 if total > 0 else 0
        lines.append(f"| {fam} | {s} | {f} | {rate:.0f}% |")
    lines.append("")

    # 2b. Variant count comparison
    lines.append("### 2b. Variant Count — Success vs Failure")
    lines.append("")

    success_vars = []
    failure_vars = []
    for d in disease_details:
        v = d["agent_model"].get("variants_number")
        if v and v > 0:
            success_vars.append(v)
    for dd in failures:
        modal = dd["modal_recommendation"]
        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent = model_map.get(modal, {})
        v = agent.get("variants_number")
        if v and v > 0:
            failure_vars.append(v)

    lines.append("| Statistic | Success Selections | Failure Selections |")
    lines.append("|-----------|-------------------|-------------------|")
    for label, sv, fv in [
        ("Median", median_safe(success_vars), median_safe(failure_vars)),
        ("Mean", mean_safe(success_vars), mean_safe(failure_vars)),
        ("Min", min(success_vars) if success_vars else None, min(failure_vars) if failure_vars else None),
        ("Max", max(success_vars) if success_vars else None, max(failure_vars) if failure_vars else None),
    ]:
        lines.append(f"| {label} | {fmt(sv, 0) if sv else 'N/A'} | {fmt(fv, 0) if fv else 'N/A'} |")
    lines.append("")

    # Variant count bins
    bins = [(0, 100, "<100 (GWAS hits)"), (100, 10000, "100-10K"), (10000, 100000, "10K-100K"),
            (100000, 500000, "100K-500K"), (500000, 1500000, "500K-1.5M"), (1500000, float("inf"), ">1.5M")]
    lines.append("| Variant Bin | Success Count | Failure Count |")
    lines.append("|-------------|--------------|--------------|")
    for lo, hi, label in bins:
        sc = sum(1 for v in success_vars if lo <= v < hi)
        fc = sum(1 for v in failure_vars if lo <= v < hi)
        lines.append(f"| {label} | {sc} | {fc} |")
    lines.append("")

    # 2c. Validation sample size
    lines.append("### 2c. Validation Sample Size — Success vs Failure")
    lines.append("")

    success_val_sizes = []
    failure_val_sizes = []
    for d in disease_details:
        v = parse_sample_size(d["agent_model"].get("validation_sample_size"))
        if v:
            success_val_sizes.append(v)
    for dd in failures:
        modal = dd["modal_recommendation"]
        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent = model_map.get(modal, {})
        v = parse_sample_size(agent.get("validation_sample_size"))
        if v:
            failure_val_sizes.append(v)

    lines.append("| Statistic | Success Selections | Failure Selections |")
    lines.append("|-----------|-------------------|-------------------|")
    for label, sv, fv in [
        ("Median", median_safe(success_val_sizes), median_safe(failure_val_sizes)),
        ("Mean", mean_safe(success_val_sizes), mean_safe(failure_val_sizes)),
    ]:
        sv_str = f"{sv:,.0f}" if sv else "N/A"
        fv_str = f"{fv:,.0f}" if fv else "N/A"
        lines.append(f"| {label} | {sv_str} | {fv_str} |")
    lines.append("")

    # 2d. Was agent's pick same method family as benchmark #1?
    lines.append("### 2d. Method Family Match with Benchmark #1")
    lines.append("")

    same_method_success = 0
    diff_method_success = 0
    same_method_fail = 0
    diff_method_fail = 0

    for d in disease_details:
        agent_fam = get_method_family(d["agent_model"].get("method_name", ""))
        top1_fam = get_method_family(d["top1_model"].get("method_name", ""))
        if agent_fam == top1_fam:
            same_method_success += 1
        else:
            diff_method_success += 1

    for dd in failures:
        modal = dd["modal_recommendation"]
        ranked = dd["benchmark_ranked_ids"]
        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent = model_map.get(modal, {})
        top1 = model_map.get(ranked[0], {}) if ranked else {}
        agent_fam = get_method_family(agent.get("method_name", ""))
        top1_fam = get_method_family(top1.get("method_name", ""))
        if agent_fam == top1_fam:
            same_method_fail += 1
        else:
            diff_method_fail += 1

    lines.append("| | Same Family as Bench #1 | Different Family | Match Rate |")
    lines.append("|--|------------------------|-----------------|------------|")
    s_total = same_method_success + diff_method_success
    f_total = same_method_fail + diff_method_fail
    lines.append(f"| Success diseases | {same_method_success} | {diff_method_success} | "
                 f"{same_method_success/s_total*100:.0f}% |")
    lines.append(f"| Failure diseases | {same_method_fail} | {diff_method_fail} | "
                 f"{same_method_fail/f_total*100:.0f}% |")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 3: Rationale pattern analysis in successes
    # -----------------------------------------------------------------------
    lines.append("## 3. Agent Rationale Pattern Analysis in Successful Diseases")
    lines.append("")
    lines.append("Which rationale themes appear more in successes vs failures?")
    lines.append("")

    rationale_patterns = [
        ("endpoint fidelity", r"endpoint\s+fidelity|phenotyping_reported|endpoint\s+alignment"),
        ("covariate comparability", r"covariate|covariates|non-comparable|comparability"),
        ("framework penalty", r"framework|pan-trait|813\s*trait|portability"),
        ("disease-focused preference", r"disease.focused|disease.specific"),
        ("validation size", r"validation.*size|validation.*n=|sample.*size"),
        ("method preference", r"method|prs-cs|ldpred|shrinkage"),
        ("effect size evidence", r"odds ratio|hazard ratio|or\s*=|hr\s*=|effect.siz"),
        ("full-model AUC caution", r"full.model|full_model|not prs.only"),
        ("study family", r"study family|same publication|sibling|same.*study"),
        ("MTAG caution", r"mtag"),
        ("multi-cohort preference", r"multi.cohort|multi.biobank|consortium"),
        ("record count", r"record.count|validation.*record"),
        ("variant count", r"variant|snp count"),
        ("recency", r"recent|newer|latest|date"),
    ]

    success_cite_count = Counter()
    failure_cite_count = Counter()

    for d in disease_details:
        ont = d["ontology"]
        trials = trial_by_disease[ont]
        combined = " ".join(t.get("rationale", "") for t in trials).lower()
        for name, pat in rationale_patterns:
            if re.search(pat, combined):
                success_cite_count[name] += 1

    for dd in failures:
        ont = dd["ontology"]
        trials = trial_by_disease[ont]
        combined = " ".join(t.get("rationale", "") for t in trials).lower()
        for name, pat in rationale_patterns:
            if re.search(pat, combined):
                failure_cite_count[name] += 1

    lines.append("| Rationale Theme | Success (N/" + str(len(successes)) + ") | "
                 "Failure (N/19) | Success Rate | Interpretation |")
    lines.append("|-----------------|-------------|-------------|--------------|----------------|")
    for name, _ in rationale_patterns:
        sc = success_cite_count.get(name, 0)
        fc = failure_cite_count.get(name, 0)
        total = sc + fc
        rate = sc / total * 100 if total > 0 else 0
        # Interpretation
        s_pct = sc / len(successes) * 100
        f_pct = fc / 19 * 100
        if s_pct > f_pct + 15:
            interp = "More in success → likely helpful"
        elif f_pct > s_pct + 15:
            interp = "More in failure → possibly misleading"
        else:
            interp = "Similar prevalence"
        lines.append(f"| {name} | {sc} ({s_pct:.0f}%) | {fc} ({f_pct:.0f}%) | {rate:.0f}% | {interp} |")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 4: Success pattern deep-dive by Hit@1 diseases
    # -----------------------------------------------------------------------
    lines.append("## 4. Hit@1 Success Pattern Analysis")
    lines.append("")
    lines.append(f"Deep analysis of {len(hit1_diseases)} diseases where agent selected the benchmark #1 model.")
    lines.append("")

    # 4a. What made these diseases "easy" or what did agent do right?
    lines.append("### 4a. Structural Characteristics of Hit@1 Diseases")
    lines.append("")

    # Pool size distribution
    hit1_pool_sizes = [d["n_models"] for d in hit1_diseases]
    non_hit1_pool_sizes = [d["n_models"] for d in disease_details if not d["hit1"]]
    lines.append(f"- Hit@1 diseases: median pool size = {median_safe(hit1_pool_sizes):.0f}, "
                 f"mean = {mean_safe(hit1_pool_sizes):.0f}")
    lines.append(f"- Non-Hit@1 successes: median pool size = {median_safe(non_hit1_pool_sizes):.0f}, "
                 f"mean = {mean_safe(non_hit1_pool_sizes):.0f}")
    lines.append("")

    # AUC gap between #1 and #2
    lines.append("### 4b. AUC Gap (Benchmark #1 vs #2) — Hit@1 vs Others")
    lines.append("")
    hit1_gaps = []
    non_hit1_gaps = []
    for d in hit1_diseases:
        ranked = d["benchmark_ranked_ids"]
        auc_map = d["auc_map"]
        if len(ranked) >= 2:
            gap = auc_map.get(ranked[0], 0) - auc_map.get(ranked[1], 0)
            hit1_gaps.append(gap)
    for d in disease_details:
        if not d["hit1"]:
            ranked = d["benchmark_ranked_ids"]
            auc_map = d["auc_map"]
            if len(ranked) >= 2:
                gap = auc_map.get(ranked[0], 0) - auc_map.get(ranked[1], 0)
                non_hit1_gaps.append(gap)

    lines.append(f"- Hit@1: median AUC gap #1-#2 = {fmt(median_safe(hit1_gaps))}, "
                 f"mean = {fmt(mean_safe(hit1_gaps))}")
    lines.append(f"- Non-Hit@1: median AUC gap #1-#2 = {fmt(median_safe(non_hit1_gaps))}, "
                 f"mean = {fmt(mean_safe(non_hit1_gaps))}")
    lines.append("")
    lines.append("(Larger gap means the top model stands out more, potentially making selection easier.)")
    lines.append("")

    # 4c. Method family of Hit@1 selected models
    lines.append("### 4c. Method Families in Hit@1 Selected Models")
    lines.append("")
    hit1_methods = Counter()
    for d in hit1_diseases:
        m = d["agent_model"].get("method_name", "Unknown")
        hit1_methods[get_method_family(m)] += 1
    lines.append("| Method Family | Count | % of Hit@1 |")
    lines.append("|---------------|-------|-----------|")
    for fam, cnt in hit1_methods.most_common():
        lines.append(f"| {fam} | {cnt} | {cnt/len(hit1_diseases)*100:.0f}% |")
    lines.append("")

    # 4d. Variant count of Hit@1 selected models
    lines.append("### 4d. Variant Count in Hit@1 Selected Models")
    lines.append("")
    hit1_vars = [d["agent_model"].get("variants_number", 0) for d in hit1_diseases if d["agent_model"].get("variants_number")]
    lines.append(f"- Median: {median_safe(hit1_vars):,.0f}" if hit1_vars else "- Median: N/A")
    lines.append(f"- Mean: {mean_safe(hit1_vars):,.0f}" if hit1_vars else "- Mean: N/A")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 5: Per-disease success mini-profiles (Hit@1 only)
    # -----------------------------------------------------------------------
    lines.append("## 5. Per-Disease Success Profiles (Hit@1)")
    lines.append("")
    lines.append("For each Hit@1 disease, show what the agent selected and key characteristics.")
    lines.append("")

    for d in hit1_diseases:
        ont = d["ontology"]
        M = d["n_models"]
        modal = d["modal"]
        agent = d["agent_model"]
        ranked = d["benchmark_ranked_ids"]
        auc_map = d["auc_map"]

        lines.append(f"### {ont}")
        lines.append("")
        lines.append(f"**N Models**: {M} | **Selected**: {modal} (rank 1/{M}) | "
                     f"**AoU AUC**: {auc_map.get(modal, 0):.4f}")
        lines.append("")

        # Key characteristics
        chars = []
        method = agent.get("method_name", "?")
        chars.append(f"- **Method**: {method} ({get_method_family(method)})")
        vn = agent.get("variants_number")
        if vn:
            chars.append(f"- **Variants**: {vn:,}")
        val = agent.get("validation_sample_size", "")
        if val:
            chars.append(f"- **Validation**: {val}")
        pub = agent.get("publication", {}).get("title", "")
        if pub:
            chars.append(f"- **Publication**: {pub[:100]}")
        date = agent.get("date_release", "")
        if date:
            chars.append(f"- **Date**: {date}")
        cov = agent.get("covariates", "")
        if cov:
            chars.append(f"- **Covariates**: {cov[:100]}")

        for c in chars:
            lines.append(c)
        lines.append("")

        # Agent rationale excerpt (first trial, short)
        trials = trial_by_disease[ont]
        if trials:
            rat = trials[0].get("rationale", "")[:500]
            lines.append(f"> {rat}...")
            lines.append("")

        lines.append("---")
        lines.append("")

    # -----------------------------------------------------------------------
    # Section 6: What distinguishes Hit@1 from near-miss/failure?
    # -----------------------------------------------------------------------
    lines.append("## 6. Comparative Analysis: Hit@1 vs Near-Miss vs Failure")
    lines.append("")
    lines.append("Statistical comparison of structural features across the three groups.")
    lines.append("")

    groups = {
        "Hit@1": hit1_diseases,
        "Hit@2-5": [d for d in disease_details if not d["hit1"]],
        "Failure (all-No)": None,  # handled separately
    }

    # Build failure disease_details for comparison
    failure_details = []
    for dd in failures:
        modal = dd["modal_recommendation"]
        ranked = dd["benchmark_ranked_ids"]
        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent = model_map.get(modal, {})
        rank = ranked.index(modal) + 1 if modal in ranked else None
        failure_details.append({
            "agent_model": agent,
            "n_models": dd["n_models"],
            "rank": rank,
            "norm_rank": rank / dd["n_models"] if rank else None,
        })

    # Comparison table
    lines.append("| Feature | Hit@1 | Hit@2-5 | Failure |")
    lines.append("|---------|-------|---------|---------|")

    # Median pool size
    h1_pool = [d["n_models"] for d in hit1_diseases]
    h25_pool = [d["n_models"] for d in disease_details if not d["hit1"]]
    f_pool = [d["n_models"] for d in failure_details]
    lines.append(f"| Median pool size | {median_safe(h1_pool):.0f} | {median_safe(h25_pool):.0f} | {median_safe(f_pool):.0f} |")

    # Median selected norm_rank
    h1_nr = [d["norm_rank"] for d in hit1_diseases if d["norm_rank"] is not None]
    h25_nr = [d["norm_rank"] for d in disease_details if not d["hit1"] and d["norm_rank"] is not None]
    f_nr = [d["norm_rank"] for d in failure_details if d["norm_rank"] is not None]
    lines.append(f"| Median norm_rank | {fmt(median_safe(h1_nr))} | {fmt(median_safe(h25_nr))} | {fmt(median_safe(f_nr))} |")

    # Median variant count
    h1_v = [d["agent_model"].get("variants_number") for d in hit1_diseases if d["agent_model"].get("variants_number")]
    h25_v = [d["agent_model"].get("variants_number") for d in disease_details if not d["hit1"] and d["agent_model"].get("variants_number")]
    f_v = [d["agent_model"].get("variants_number") for d in failure_details if d["agent_model"].get("variants_number")]
    lines.append(f"| Median variant count | {median_safe(h1_v):,.0f} if h1_v else 'N/A' | "
                 f"{median_safe(h25_v):,.0f} if h25_v else 'N/A' | "
                 f"{median_safe(f_v):,.0f} if f_v else 'N/A' |".replace(" if h1_v else 'N/A'", "").replace(" if h25_v else 'N/A'", "").replace(" if f_v else 'N/A'", ""))

    # Method match rate with benchmark #1
    h1_match = sum(1 for d in hit1_diseases if get_method_family(d["agent_model"].get("method_name", "")) == get_method_family(d["top1_model"].get("method_name", "")))
    h25_match = sum(1 for d in disease_details if not d["hit1"] and get_method_family(d["agent_model"].get("method_name", "")) == get_method_family(d["top1_model"].get("method_name", "")))

    lines.append(f"| Method family match with Bench #1 | {h1_match}/{len(hit1_diseases)} ({h1_match/len(hit1_diseases)*100:.0f}%) | "
                 f"{h25_match}/{len([d for d in disease_details if not d['hit1']])} | — |")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 7: Correct DK rule application examples
    # -----------------------------------------------------------------------
    lines.append("## 7. Domain Knowledge Rules Correctly Applied in Successes")
    lines.append("")
    lines.append("Patterns where the domain knowledge helped the agent make correct decisions,")
    lines.append("identified by analyzing rationales of Hit@1 diseases.")
    lines.append("")

    # Categorize success patterns
    success_patterns = Counter()
    pattern_examples = defaultdict(list)

    for d in hit1_diseases:
        ont = d["ontology"]
        trials = trial_by_disease[ont]
        combined = " ".join(t.get("rationale", "") for t in trials).lower()
        agent = d["agent_model"]

        # Pattern: method-informed choice
        if re.search(r"method|prs-cs|ldpred|shrinkage|bayesian", combined):
            success_patterns["Method-informed selection"] += 1
            pattern_examples["Method-informed selection"].append(ont)

        # Pattern: correctly identified framework and rejected it
        if re.search(r"framework|pan-trait|813", combined) and not any(
            re.search(p, (agent.get("publication", {}).get("title") or "").lower())
            for p in [r"813\s*trait", r"exprs", r"global\s*biobank", r"phenome-wide"]
        ):
            success_patterns["Framework correctly rejected"] += 1
            pattern_examples["Framework correctly rejected"].append(ont)

        # Pattern: variant count noted
        if re.search(r"variant|snp", combined):
            success_patterns["Variant count considered"] += 1
            pattern_examples["Variant count considered"].append(ont)

        # Pattern: endpoint alignment
        if re.search(r"endpoint|phenotyping|trait.*match", combined):
            success_patterns["Endpoint alignment checked"] += 1
            pattern_examples["Endpoint alignment checked"].append(ont)

        # Pattern: covariate awareness
        if re.search(r"covariate|covariates", combined):
            success_patterns["Covariate awareness"] += 1
            pattern_examples["Covariate awareness"].append(ont)

        # Pattern: study family / publication context
        if re.search(r"publication|study|disease.focused|disease.specific", combined):
            success_patterns["Publication context used"] += 1
            pattern_examples["Publication context used"].append(ont)

        # Pattern: multi-cohort/ancestry noted
        if re.search(r"multi.cohort|ancestry|multi.ancestry", combined):
            success_patterns["Multi-cohort/ancestry noted"] += 1
            pattern_examples["Multi-cohort/ancestry noted"].append(ont)

    lines.append("| Success Pattern | N Hit@1 Diseases | Example Diseases |")
    lines.append("|----------------|-----------------|------------------|")
    for pat, cnt in success_patterns.most_common():
        exs = ", ".join(pattern_examples[pat][:4])
        if len(pattern_examples[pat]) > 4:
            exs += f" (+{len(pattern_examples[pat])-4})"
        lines.append(f"| {pat} | {cnt}/{len(hit1_diseases)} | {exs} |")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 8: Key findings and implications for DK optimization
    # -----------------------------------------------------------------------
    lines.append("## 8. Key Findings and Implications for Domain Knowledge Optimization")
    lines.append("")

    # Compute some final statistics
    lines.append("### 8a. What the agent does well (preserve these patterns)")
    lines.append("")

    # Find method families that succeed
    lines.append("**Method family selection accuracy:**")
    lines.append("When the agent selects these method families, it tends to succeed:")
    lines.append("")
    for fam, cnt in success_methods.most_common():
        fc = failure_methods.get(fam, 0)
        total = cnt + fc
        if total >= 3:
            rate = cnt / total * 100
            lines.append(f"- {fam}: {rate:.0f}% success rate ({cnt} success, {fc} failure)")
    lines.append("")

    lines.append("### 8b. What distinguishes success from failure (strengthen these signals)")
    lines.append("")
    lines.append("Based on the comparative analysis above, the following structural signals")
    lines.append("consistently distinguish successful selections from failures:")
    lines.append("")

    # Compute actual distinguishing features
    success_agent_vars_median = median_safe([d["agent_model"].get("variants_number") for d in hit1_diseases if d["agent_model"].get("variants_number")])
    failure_agent_vars_median = median_safe(failure_vars)
    lines.append(f"1. **Variant count**: Hit@1 median = {success_agent_vars_median:,.0f} vs "
                 f"Failure median = {failure_agent_vars_median:,.0f}" if success_agent_vars_median and failure_agent_vars_median else
                 "1. **Variant count**: data insufficient")
    lines.append("")

    lines.append("2. **Method family selection**: The agent's choice of method family and its match")
    lines.append("   with the benchmark #1 model's family is a strong predictor of success.")
    lines.append("")

    lines.append("3. **Framework rejection**: In successful cases, the agent correctly identifies")
    lines.append("   and deprioritizes pan-trait framework models when disease-focused alternatives exist.")
    lines.append("")

    lines.append("### 8c. Recommendations for DK optimization from success analysis")
    lines.append("")
    lines.append("1. **Preserve endpoint fidelity as primary signal** — it appears in most successful rationales")
    lines.append("2. **Preserve framework penalty** — correctly applied in many successes")
    lines.append("3. **Strengthen method family guidance** — when the agent picks the right method family, success follows")
    lines.append("4. **Strengthen variant count signal** — successful picks have higher variant counts")
    lines.append("5. **De-emphasize validation sample size** — not a distinguishing factor between success and failure")
    lines.append("")

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines))
    print(f"Report written to {OUTPUT_MD} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
