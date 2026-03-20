#!/usr/bin/env python3
"""
Regression Analysis: Identify diseases where Catalog Search + Domain Knowledge (DK)
performed worse than Catalog Search Only (CS), analyze root causes, and produce
actionable recommendations to prevent domain knowledge from degrading model selection.

Output: regression_analysis_report.md
"""

from __future__ import annotations

import json
import math
import re
import statistics
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import scipy.stats as ss

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[3]  # experiments/contribution2/recommendation
DK_RUN_DIR = BASE / "runs" / "with-domain-gpt-5.2-t10__75disease__updated-domain-knowledge-20260318"
CS_RUN_DIR = BASE / "runs" / "without-domain-gpt-5.2-t10__75disease__three-arm-rerun-20260316"

DK_SUMMARY = DK_RUN_DIR / "experiment_with_domain_summary.json"
DK_RESULTS = DK_RUN_DIR / "experiment_with_domain_results.json"
CS_SUMMARY = CS_RUN_DIR / "experiment_without_domain_summary.json"
CS_RESULTS = CS_RUN_DIR / "experiment_without_domain_results.json"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_MD = OUTPUT_DIR / "regression_analysis_report.md"

# ---------------------------------------------------------------------------
# Method family mapping (shared with other analysis scripts)
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
    "UKBB-EUR.MultiPRS.CV": "MultiPRS family",
    "shaPRS + LDpred2": "shaPRS",
    "SNPs passing genome-wide significance": "GWAS Hits / GWS variants",
}

# 24 Agent Input fields for comparison
COMPARISON_FIELDS = [
    "id", "trait_reported", "trait_efo", "phenotyping_reported",
    "method_name", "variants_number", "ancestry_distribution",
    "publication.title", "publication.journal", "date_release",
    "samples_training", "training_development_cohorts",
    "validation_sample_size", "covariates",
    "performance_metrics.auc", "performance_metrics.r2",
    "performance_metrics.full_model_auc", "performance_metrics.full_model_r2",
    "performance_metrics.incremental_auc",
    "performance_metrics.selected_validation_ancestry",
    "performance_metrics.record_count",
    "performance_metrics.classification_metrics",
    "performance_metrics.other_metrics",
    "performance_metrics.effect_sizes",
]

# DK rule patterns for rationale parsing
RULE_PATTERNS = [
    ("endpoint fidelity", r"endpoint\s+fidelity|phenotyping_reported|endpoint\s+alignment"),
    ("covariate comparability", r"covariate|covariates|non-comparable|comparability"),
    ("CHARGE-AF penalty", r"charge-af|charge.af"),
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
    ("BMI mediator", r"bmi.*mediator|bmi.*covariate"),
    ("risk calculator/wrapper", r"risk.calculator|risk.wrapper|deployment.packag"),
    ("method tier / S-tier", r"s.tier|top.tier|prsmix|megaprs"),
    ("method tier / penalize", r"c.tier|d.tier|low.tier|snpnet.*penali"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def get_field(model: dict, field_path: str) -> Any:
    parts = field_path.split(".")
    obj = model
    for p in parts:
        if isinstance(obj, dict):
            obj = obj.get(p)
        else:
            return None
    return obj


def fmt_value(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.4f}"
    if isinstance(val, list):
        if not val:
            return "—"
        if isinstance(val[0], dict):
            parts = []
            for item in val:
                name = item.get("name_short", "")
                est = item.get("estimate", "")
                ci_lo = item.get("ci_lower")
                ci_hi = item.get("ci_upper")
                if ci_lo and ci_hi:
                    parts.append(f"{name}={est} [{ci_lo:.3f}-{ci_hi:.3f}]")
                else:
                    parts.append(f"{name}={est}")
            return "; ".join(parts)
        return ", ".join(str(v) for v in val)
    if isinstance(val, int):
        return f"{val:,}"
    return str(val)[:120]


def parse_sample_size(s: str | None) -> int | None:
    if not s or s == "N/A":
        return None
    nums = re.findall(r"[\d,]+", s)
    return int(nums[0].replace(",", "")) if nums else None


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


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    print("Loading DK data...")
    with open(DK_SUMMARY) as f:
        dk_summary = json.load(f)
    with open(DK_RESULTS) as f:
        dk_results = json.load(f)

    print("Loading CS data...")
    with open(CS_SUMMARY) as f:
        cs_summary = json.load(f)
    with open(CS_RESULTS) as f:
        cs_results = json.load(f)

    return dk_summary, dk_results, cs_summary, cs_results


# ---------------------------------------------------------------------------
# Regression identification
# ---------------------------------------------------------------------------

def identify_regressions(dk_summary, cs_summary):
    """Identify diseases where DK modal rank > CS modal rank."""
    dk_by_ont = {dd["ontology"]: dd for dd in dk_summary["per_disease"]}
    cs_by_ont = {dd["ontology"]: dd for dd in cs_summary["per_disease"]}

    all_diseases = []
    for ont in dk_by_ont:
        dk_dd = dk_by_ont[ont]
        cs_dd = cs_by_ont.get(ont)
        if not cs_dd:
            continue

        dk_modal = dk_dd["modal_recommendation"]
        cs_modal = cs_dd["modal_recommendation"]
        dk_ranked = dk_dd["benchmark_ranked_ids"]
        cs_ranked = cs_dd["benchmark_ranked_ids"]
        M = dk_dd["n_models"]

        dk_rank = dk_ranked.index(dk_modal) + 1 if dk_modal in dk_ranked else M
        cs_rank = cs_ranked.index(cs_modal) + 1 if cs_modal in cs_ranked else M

        rank_delta = dk_rank - cs_rank  # positive = regression

        # CS Hit@k
        cs_hits = cs_dd.get("modal_recommendation_hit_at_k", {})
        cs_any_hit = any(cs_hits.get(str(k), False) for k in range(1, 6))
        cs_hit1 = cs_hits.get("1", False)
        cs_best_hit = None
        for k in range(1, 6):
            if cs_hits.get(str(k), False):
                cs_best_hit = k
                break

        # DK Hit@k
        dk_hits = dk_dd.get("modal_recommendation_hit_at_k", {})
        dk_any_hit = any(dk_hits.get(str(k), False) for k in range(1, 6))
        dk_hit1 = dk_hits.get("1", False)
        dk_best_hit = None
        for k in range(1, 6):
            if dk_hits.get(str(k), False):
                dk_best_hit = k
                break

        # Classify severity
        if cs_any_hit and not dk_any_hit:
            severity = "Severe (CS hit, DK lost all)"
        elif rank_delta > 0 and cs_hit1 and not dk_hit1:
            severity = "Moderate (CS Hit@1, DK lost it)"
        elif rank_delta > 5:
            severity = "Moderate (large rank drop)"
        elif rank_delta > 0:
            severity = "Mild"
        elif rank_delta == 0:
            severity = "No change"
        else:
            severity = "Improved"

        all_diseases.append({
            "ontology": ont,
            "n_models": M,
            "dk_modal": dk_modal,
            "cs_modal": cs_modal,
            "dk_rank": dk_rank,
            "cs_rank": cs_rank,
            "rank_delta": rank_delta,
            "dk_hit1": dk_hit1,
            "cs_hit1": cs_hit1,
            "dk_any_hit": dk_any_hit,
            "cs_any_hit": cs_any_hit,
            "dk_best_hit": dk_best_hit,
            "cs_best_hit": cs_best_hit,
            "severity": severity,
            "dk_dd": dk_dd,
            "cs_dd": cs_dd,
        })

    return all_diseases


# ---------------------------------------------------------------------------
# Section 1: Overview
# ---------------------------------------------------------------------------

def build_overview(all_diseases):
    lines = ["## 1. Regression Overview", ""]

    regressions = [d for d in all_diseases if d["rank_delta"] > 0]
    improvements = [d for d in all_diseases if d["rank_delta"] < 0]
    no_change = [d for d in all_diseases if d["rank_delta"] == 0]

    severe = [d for d in regressions if "Severe" in d["severity"]]
    moderate = [d for d in regressions if "Moderate" in d["severity"]]
    mild = [d for d in regressions if d["severity"] == "Mild"]

    lines.append(f"- **Total diseases**: {len(all_diseases)}")
    lines.append(f"- **Regressions (DK rank > CS rank)**: {len(regressions)}")
    lines.append(f"  - Severe (CS hit, DK lost all hits): {len(severe)}")
    lines.append(f"  - Moderate (lost Hit@1 or large rank drop): {len(moderate)}")
    lines.append(f"  - Mild: {len(mild)}")
    lines.append(f"- **No change**: {len(no_change)}")
    lines.append(f"- **Improvements (DK rank < CS rank)**: {len(improvements)}")
    lines.append("")

    # Summary stats
    reg_deltas = [d["rank_delta"] for d in regressions]
    imp_deltas = [abs(d["rank_delta"]) for d in improvements]
    lines.append(f"- Mean regression rank delta: {mean_safe(reg_deltas):.1f}" if reg_deltas else "- No regressions")
    lines.append(f"- Mean improvement rank delta: {mean_safe(imp_deltas):.1f}" if imp_deltas else "- No improvements")
    lines.append("")

    # Full table sorted by rank_delta descending
    lines.append("### Full Disease Table (sorted by rank delta, worst first)")
    lines.append("")
    lines.append("| Ontology | N Models | CS Modal | CS Rank | CS Hit | DK Modal | DK Rank | DK Hit | Rank Delta | Severity |")
    lines.append("|----------|----------|----------|---------|--------|----------|---------|--------|------------|----------|")

    sorted_diseases = sorted(all_diseases, key=lambda d: -d["rank_delta"])
    for d in sorted_diseases:
        cs_hit_str = f"@{d['cs_best_hit']}" if d["cs_best_hit"] else "None"
        dk_hit_str = f"@{d['dk_best_hit']}" if d["dk_best_hit"] else "None"
        delta_str = f"+{d['rank_delta']}" if d["rank_delta"] > 0 else str(d["rank_delta"])
        lines.append(
            f"| {d['ontology']} | {d['n_models']} | {d['cs_modal']} | "
            f"{d['cs_rank']}/{d['n_models']} | {cs_hit_str} | {d['dk_modal']} | "
            f"{d['dk_rank']}/{d['n_models']} | {dk_hit_str} | {delta_str} | {d['severity']} |"
        )
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Section 2: Field-by-field comparison for each regression disease
# ---------------------------------------------------------------------------

def build_field_comparisons(all_diseases):
    regressions = [d for d in all_diseases if d["rank_delta"] > 0]
    regressions.sort(key=lambda d: -d["rank_delta"])

    lines = ["## 2. Field-by-Field Comparison for Regression Diseases", ""]
    lines.append(f"Detailed comparison of CS selection vs DK selection vs Benchmark #1 for {len(regressions)} regression diseases.")
    lines.append("")

    for d in regressions:
        dk_dd = d["dk_dd"]
        cs_dd = d["cs_dd"]
        ont = d["ontology"]
        M = d["n_models"]
        ranked = dk_dd["benchmark_ranked_ids"]
        auc_map = dk_dd["benchmark_auc_by_id"]

        model_map = {m["id"]: m for m in dk_dd["candidate_models_visible_to_llm"]}

        cs_model = model_map.get(d["cs_modal"], {})
        dk_model = model_map.get(d["dk_modal"], {})
        bench1 = model_map.get(ranked[0], {}) if ranked else {}

        lines.append(f"### {ont}")
        lines.append("")
        lines.append(f"**N Models**: {M} | **CS**: {d['cs_modal']} (rank {d['cs_rank']}/{M}) | "
                     f"**DK**: {d['dk_modal']} (rank {d['dk_rank']}/{M}) | "
                     f"**Rank delta**: +{d['rank_delta']} | **Severity**: {d['severity']}")
        lines.append("")

        # Field comparison table
        lines.append(f"| Field | CS: {d['cs_modal']} (rank {d['cs_rank']}) | "
                     f"DK: {d['dk_modal']} (rank {d['dk_rank']}) | "
                     f"Bench #1: {ranked[0] if ranked else '?'} (rank 1) | Diff? |")
        lines.append(f"| --- | --- | --- | --- | --- |")

        for field in COMPARISON_FIELDS:
            short_field = field.replace("performance_metrics.", "pm.")
            cs_val = get_field(cs_model, field)
            dk_val = get_field(dk_model, field)
            bench_val = get_field(bench1, field)

            cs_str = fmt_value(cs_val)
            dk_str = fmt_value(dk_val)
            bench_str = fmt_value(bench_val)

            # Mark if CS and DK differ
            diff = ""
            if field == "id":
                diff = "Yes" if d["cs_modal"] != d["dk_modal"] else "No"
            elif cs_str != dk_str:
                diff = "**YES**"
            else:
                diff = ""

            lines.append(f"| {short_field} | {cs_str} | {dk_str} | {bench_str} | {diff} |")

        # AoU benchmark AUC row
        cs_auc = auc_map.get(d["cs_modal"], 0)
        dk_auc = auc_map.get(d["dk_modal"], 0)
        bench_auc = auc_map.get(ranked[0], 0) if ranked else 0
        lines.append(f"| **AoU benchmark AUC** | **{cs_auc:.4f}** | **{dk_auc:.4f}** | **{bench_auc:.4f}** | "
                     f"gap={cs_auc - dk_auc:.4f} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Section 3: DK rule attribution
# ---------------------------------------------------------------------------

def build_rule_attribution(all_diseases, dk_results, cs_results):
    lines = ["## 3. Domain Knowledge Rule Attribution", ""]
    lines.append("Which DK rules are cited more frequently in regression diseases vs non-regression diseases?")
    lines.append("")

    regressions = {d["ontology"] for d in all_diseases if d["rank_delta"] > 0}
    non_regressions = {d["ontology"] for d in all_diseases if d["rank_delta"] <= 0}

    dk_by_disease = defaultdict(list)
    for t in dk_results:
        dk_by_disease[t["ontology"]].append(t)

    cs_by_disease = defaultdict(list)
    for t in cs_results:
        cs_by_disease[t["ontology"]].append(t)

    # Count rule citations in DK rationales for regression vs non-regression
    reg_rule_count = Counter()
    nonreg_rule_count = Counter()
    rule_regression_diseases = defaultdict(list)

    for ont in regressions:
        trials = dk_by_disease.get(ont, [])
        combined = " ".join(t.get("rationale", "") for t in trials).lower()
        for rule_name, pattern in RULE_PATTERNS:
            if re.search(pattern, combined):
                reg_rule_count[rule_name] += 1
                rule_regression_diseases[rule_name].append(ont)

    for ont in non_regressions:
        trials = dk_by_disease.get(ont, [])
        combined = " ".join(t.get("rationale", "") for t in trials).lower()
        for rule_name, pattern in RULE_PATTERNS:
            if re.search(pattern, combined):
                nonreg_rule_count[rule_name] += 1

    all_rules = set(reg_rule_count.keys()) | set(nonreg_rule_count.keys())

    lines.append(f"| DK Rule/Concept | Cited in Regressions (N/{len(regressions)}) | "
                 f"Cited in Non-Regressions (N/{len(non_regressions)}) | "
                 f"Regression Rate | Enrichment |")
    lines.append("|-----------------|---------------------|--------------------------|-----------------|------------|")

    for rule_name in sorted(all_rules, key=lambda r: -(reg_rule_count[r] / max(reg_rule_count[r] + nonreg_rule_count[r], 1))):
        rc = reg_rule_count[rule_name]
        nrc = nonreg_rule_count[rule_name]
        total = rc + nrc
        reg_rate = rc / total * 100 if total > 0 else 0

        # Enrichment: is this rule more common in regressions relative to base rate?
        base_rate = len(regressions) / (len(regressions) + len(non_regressions)) * 100
        if reg_rate > base_rate + 10:
            enrichment = "**ENRICHED in regressions**"
        elif reg_rate < base_rate - 10:
            enrichment = "Depleted in regressions"
        else:
            enrichment = "Similar"

        diseases_str = ", ".join(rule_regression_diseases[rule_name][:3])
        if len(rule_regression_diseases[rule_name]) > 3:
            diseases_str += "..."

        lines.append(f"| {rule_name} | {rc} ({rc/len(regressions)*100:.0f}%) | "
                     f"{nrc} ({nrc/len(non_regressions)*100:.0f}%) | {reg_rate:.0f}% | {enrichment} |")

    lines.append("")

    # Identify rules uniquely associated with regressions
    lines.append("### Rules Most Enriched in Regression Rationales")
    lines.append("")
    for rule_name in sorted(all_rules, key=lambda r: -(reg_rule_count[r] / max(reg_rule_count[r] + nonreg_rule_count[r], 1))):
        rc = reg_rule_count[rule_name]
        nrc = nonreg_rule_count[rule_name]
        total = rc + nrc
        if total < 3:
            continue
        reg_rate = rc / total * 100
        base_rate = len(regressions) / (len(regressions) + len(non_regressions)) * 100
        if reg_rate > base_rate + 10:
            lines.append(f"- **{rule_name}**: cited in {rc}/{len(regressions)} regressions vs "
                        f"{nrc}/{len(non_regressions)} non-regressions ({reg_rate:.0f}% regression rate). "
                        f"Diseases: {', '.join(rule_regression_diseases[rule_name][:5])}")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Section 4: Regression pattern classification
# ---------------------------------------------------------------------------

def classify_regression_pattern(d, dk_results, cs_results):
    """Classify the root cause of a regression for one disease."""
    dk_dd = d["dk_dd"]
    cs_dd = d["cs_dd"]
    ont = d["ontology"]
    ranked = dk_dd["benchmark_ranked_ids"]
    model_map = {m["id"]: m for m in dk_dd["candidate_models_visible_to_llm"]}

    cs_model = model_map.get(d["cs_modal"], {})
    dk_model = model_map.get(d["dk_modal"], {})

    dk_trials = [t for t in dk_results if t["ontology"] == ont]
    cs_trials = [t for t in cs_results if t["ontology"] == ont]
    dk_rationale = " ".join(t.get("rationale", "") for t in dk_trials).lower()
    cs_rationale = " ".join(t.get("rationale", "") for t in cs_trials).lower()

    patterns = []

    # 1. Framework penalty overcorrection
    framework_pats = [r"813\s*trait", r"exprs", r"global\s*biobank", r"portability",
                      r"across\s*biobanks", r"pan-.*trait", r"phenome-wide"]
    cs_title = (cs_model.get("publication", {}).get("title") or "").lower()
    dk_title = (dk_model.get("publication", {}).get("title") or "").lower()
    cs_is_framework = any(re.search(p, cs_title) for p in framework_pats)

    if cs_is_framework and not any(re.search(p, dk_title) for p in framework_pats):
        if "framework" in dk_rationale or "pan-trait" in dk_rationale:
            patterns.append("Framework penalty overcorrection")

    # 2. Method hierarchy override
    cs_method = cs_model.get("method_name", "")
    dk_method = dk_model.get("method_name", "")
    cs_fam = get_method_family(cs_method)
    dk_fam = get_method_family(dk_method)
    if cs_fam != dk_fam and ("method" in dk_rationale or "tier" in dk_rationale):
        patterns.append("Method hierarchy override")

    # 3. Endpoint fidelity over-applied
    cs_trait = (cs_model.get("trait_reported") or "").lower()
    dk_trait = (dk_model.get("trait_reported") or "").lower()
    if cs_trait != dk_trait and ("endpoint" in dk_rationale or "fidelity" in dk_rationale):
        patterns.append("Endpoint fidelity over-applied")

    # 4. Covariate penalty overcorrection
    cs_cov = (cs_model.get("covariates") or "").lower()
    dk_cov = (dk_model.get("covariates") or "").lower()
    if cs_cov != dk_cov and ("covariate" in dk_rationale or "comparability" in dk_rationale):
        patterns.append("Covariate penalty overcorrection")

    # 5. Disease-focused narrative capture
    if ("disease-focused" in dk_rationale or "disease-specific" in dk_rationale or
        "disease focused" in dk_rationale):
        # Check if DK picked a structurally weaker model
        dk_vars = dk_model.get("variants_number") or 0
        cs_vars = cs_model.get("variants_number") or 0
        if dk_vars < cs_vars * 0.5 or d["dk_rank"] > d["cs_rank"] * 1.5:
            patterns.append("Disease-focused narrative capture")

    # 6. Study family confusion
    cs_pub = cs_model.get("publication", {}).get("title", "")
    dk_pub = dk_model.get("publication", {}).get("title", "")
    if cs_pub == dk_pub and cs_pub:
        patterns.append("Within-family wrong sibling")

    # 7. Validation size misapplied
    cs_val = parse_sample_size(cs_model.get("validation_sample_size"))
    dk_val = parse_sample_size(dk_model.get("validation_sample_size"))
    if dk_val and cs_val and dk_val > cs_val * 2:
        if "validation" in dk_rationale or "sample size" in dk_rationale:
            patterns.append("Validation size drove switch")

    # 8. Effect size / reported performance drove switch
    dk_pm = dk_model.get("performance_metrics", {})
    cs_pm = cs_model.get("performance_metrics", {})
    dk_full_auc = dk_pm.get("full_model_auc") or 0
    cs_full_auc = cs_pm.get("full_model_auc") or 0
    if dk_full_auc > cs_full_auc and dk_full_auc > 0:
        if "auc" in dk_rationale or "performance" in dk_rationale:
            patterns.append("Reported performance mismatch")

    if not patterns:
        patterns.append("Unclassified / multi-factor")

    return patterns


def build_pattern_classification(all_diseases, dk_results, cs_results):
    regressions = [d for d in all_diseases if d["rank_delta"] > 0]
    regressions.sort(key=lambda d: -d["rank_delta"])

    lines = ["## 4. Regression Pattern Classification", ""]

    pattern_diseases = defaultdict(list)
    disease_patterns = {}

    for d in regressions:
        patterns = classify_regression_pattern(d, dk_results, cs_results)
        disease_patterns[d["ontology"]] = patterns
        for p in patterns:
            pattern_diseases[p].append(d["ontology"])

    # Summary table
    lines.append("### Pattern Frequency")
    lines.append("")
    lines.append("| Pattern | Count | Diseases | Total Rank Degradation |")
    lines.append("|---------|-------|----------|----------------------|")

    for pattern, diseases in sorted(pattern_diseases.items(), key=lambda x: -len(x[1])):
        total_delta = sum(d["rank_delta"] for d in regressions if d["ontology"] in diseases)
        disease_str = ", ".join(diseases[:4])
        if len(diseases) > 4:
            disease_str += f" (+{len(diseases) - 4})"
        lines.append(f"| {pattern} | {len(diseases)} | {disease_str} | +{total_delta} |")
    lines.append("")

    # Per-disease classification
    lines.append("### Per-Disease Pattern Assignment")
    lines.append("")
    lines.append("| Disease | Rank Delta | Severity | Patterns |")
    lines.append("|---------|-----------|----------|----------|")
    for d in regressions:
        patterns = disease_patterns.get(d["ontology"], ["?"])
        lines.append(f"| {d['ontology']} | +{d['rank_delta']} | {d['severity']} | {', '.join(patterns)} |")
    lines.append("")

    # Severity cross-table
    lines.append("### Pattern × Severity Cross-Table")
    lines.append("")
    severity_levels = ["Severe (CS hit, DK lost all)", "Moderate (CS Hit@1, DK lost it)",
                       "Moderate (large rank drop)", "Mild"]
    patterns_list = sorted(pattern_diseases.keys(), key=lambda p: -len(pattern_diseases[p]))

    header = "| Pattern | " + " | ".join(severity_levels) + " |"
    lines.append(header)
    lines.append("| --- | " + " | ".join(["---"] * len(severity_levels)) + " |")

    for pattern in patterns_list:
        row = [pattern]
        for sev in severity_levels:
            count = sum(1 for d in regressions
                       if d["ontology"] in pattern_diseases[pattern] and d["severity"] == sev)
            row.append(str(count) if count > 0 else "—")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Section 5: Actionable recommendations
# ---------------------------------------------------------------------------

def build_recommendations(all_diseases, dk_results, cs_results):
    regressions = [d for d in all_diseases if d["rank_delta"] > 0]
    lines = ["## 5. Actionable Recommendations", ""]
    lines.append("Targeted modifications to domain knowledge to prevent regressions while preserving gains.")
    lines.append("")

    # Classify all regressions
    pattern_diseases = defaultdict(list)
    for d in regressions:
        patterns = classify_regression_pattern(d, dk_results, cs_results)
        for p in patterns:
            pattern_diseases[p].append(d)

    recommendations = [
        (
            "Method hierarchy override",
            "DK method tier guidance caused the agent to switch to a different method family "
            "that happens to rank worse on the AoU benchmark.",
            "Section 5 (method_name) in prs_model_domain_knowledge.md",
            "Add a 'regression guard' rule: when the CS arm (without domain knowledge) already "
            "selected a model, the method tier preference should NOT override a selection that "
            "already has strong structural signals (exact endpoint match, high variant count, "
            "disease-focused publication). Method tier should only be used as a tie-break, not "
            "as a primary override signal.",
            "Low — method tier is already described as a moderately strong signal; this just "
            "clarifies its role as a differentiator rather than an overrider.",
        ),
        (
            "Endpoint fidelity over-applied",
            "DK endpoint fidelity rules caused the agent to prefer a model with a closer "
            "trait label match but worse structural quality.",
            "Section 1 (trait_reported) in prs_model_domain_knowledge.md",
            "Clarify that endpoint fidelity is a NECESSARY filter (reject clearly wrong endpoints) "
            "but NOT a ranking signal among models that all match the target disease. Two models "
            "with 'Heart failure' vs 'Heart failure (MTAG)' should be considered equivalent in "
            "endpoint fidelity. The agent should not prefer one over the other based on label alone.",
            "Low — preserves endpoint filtering while preventing over-differentiation.",
        ),
        (
            "Disease-focused narrative capture",
            "DK disease-focused preference caused the agent to select a model from a disease-specific "
            "study even when a structurally superior model (more variants, better method) existed.",
            "Section 7 (publication) in prs_model_domain_knowledge.md",
            "Add clarification: 'disease-focused' refers to the model's phenotype target, not the "
            "publication's title or framing. A model from a large multi-trait study that includes "
            "the target disease as a specific endpoint IS disease-focused. Only penalize models "
            "where the phenotype definition is clearly misaligned (e.g., using BMI as a proxy for obesity).",
            "Medium — changes interpretation of 'disease-focused' which currently helps in many cases.",
        ),
        (
            "Framework penalty overcorrection",
            "DK framework penalty caused the agent to reject a framework model that CS correctly selected.",
            "Section 7 (publication) and High-priority corrections in prs_model_domain_knowledge.md",
            "Add exceptions to the framework penalty: framework models that use S-tier or A-tier methods "
            "(PRSmixPlus, MegaPRS, LDpred2) should NOT be penalized as heavily as generic snpnet framework "
            "models. The framework penalty should primarily target C-tier/D-tier method framework scores.",
            "Medium — requires distinguishing framework quality levels.",
        ),
        (
            "Covariate penalty overcorrection",
            "DK covariate comparability rules caused the agent to reject a model that CS correctly accepted.",
            "Section 2 (covariates) in prs_model_domain_knowledge.md",
            "Narrow the covariate penalty scope: only apply strong covariate penalties for known near-outcome "
            "biomarkers (e.g., eGFR for CKD, CHARGE-AF score for AF). Standard epidemiological covariates "
            "(age, sex, PCs, BMI, smoking) should NOT trigger a covariate penalty even if they differ "
            "between candidates.",
            "Low — makes the covariate penalty more targeted.",
        ),
        (
            "Reported performance mismatch",
            "DK performance comparison rules led the agent to prefer a model with higher reported "
            "full-model AUC that didn't translate to better benchmark performance.",
            "Section 2 (performance_metrics) in prs_model_domain_knowledge.md",
            "Strengthen the existing full-model AUC warning: when comparing two models and BOTH "
            "only have full_model_auc (no PGS-only metrics), the agent should treat their AUC values "
            "as essentially incomparable and fall back to structural signals (method, variants, study design).",
            "Low — reinforces an existing rule.",
        ),
        (
            "Validation size drove switch",
            "DK allowed validation sample size to influence the switch from CS's correct pick.",
            "Section 3 (validation_sample_size) in prs_model_domain_knowledge.md",
            "Further downweight validation sample size. Current text says 'very weak signal' but "
            "the agent still uses it. Add explicit prohibition: 'validation_sample_size should NEVER "
            "cause the agent to switch from one model to another. It is only a documentation note.'",
            "Low — validation size has rho=0.13, nearly zero predictive value.",
        ),
    ]

    for pattern, description, location, fix, risk in recommendations:
        if pattern in pattern_diseases:
            diseases = pattern_diseases[pattern]
            total_delta = sum(d["rank_delta"] for d in diseases)
            lines.append(f"### {pattern}")
            lines.append("")
            lines.append(f"**Affected diseases**: {len(diseases)} | **Total rank degradation**: +{total_delta}")
            lines.append(f"**Diseases**: {', '.join(d['ontology'] for d in diseases)}")
            lines.append("")
            lines.append(f"**Problem**: {description}")
            lines.append("")
            lines.append(f"**Location in DK**: `{location}`")
            lines.append("")
            lines.append(f"**Proposed fix**: {fix}")
            lines.append("")
            lines.append(f"**Risk assessment**: {risk}")
            lines.append("")
            lines.append("---")
            lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Section 6: Severe regression profiles
# ---------------------------------------------------------------------------

def build_severe_profiles(all_diseases, dk_results, cs_results):
    severe = [d for d in all_diseases
              if d["rank_delta"] > 0 and d["cs_any_hit"] and not d["dk_any_hit"]]

    if not severe:
        return ["## 6. Severe Regression Profiles", "",
                "No severe regressions found (all DK selections maintained at least one hit).", ""]

    severe.sort(key=lambda d: -d["rank_delta"])

    lines = ["## 6. Severe Regression Profiles", ""]
    lines.append(f"Diseases where CS achieved at least one Hit@1..5 but DK lost ALL hits ({len(severe)} diseases).")
    lines.append("")

    dk_by_disease = defaultdict(list)
    for t in dk_results:
        dk_by_disease[t["ontology"]].append(t)

    cs_by_disease = defaultdict(list)
    for t in cs_results:
        cs_by_disease[t["ontology"]].append(t)

    for d in severe:
        ont = d["ontology"]
        dk_dd = d["dk_dd"]
        cs_dd = d["cs_dd"]
        M = d["n_models"]
        ranked = dk_dd["benchmark_ranked_ids"]
        auc_map = dk_dd["benchmark_auc_by_id"]
        model_map = {m["id"]: m for m in dk_dd["candidate_models_visible_to_llm"]}

        cs_model = model_map.get(d["cs_modal"], {})
        dk_model = model_map.get(d["dk_modal"], {})
        bench1 = model_map.get(ranked[0], {}) if ranked else {}

        lines.append(f"### {ont}")
        lines.append("")
        lines.append(f"**CS selected**: {d['cs_modal']} (rank {d['cs_rank']}/{M}, Hit@{d['cs_best_hit']}) | "
                     f"**DK selected**: {d['dk_modal']} (rank {d['dk_rank']}/{M}, no hits) | "
                     f"**Benchmark #1**: {ranked[0] if ranked else '?'}")
        lines.append("")

        # Key field comparison
        key_fields = [
            ("Method", "method_name"),
            ("Trait reported", "trait_reported"),
            ("Phenotyping", "phenotyping_reported"),
            ("Variants", "variants_number"),
            ("Training cohorts", "training_development_cohorts"),
            ("Validation N", "validation_sample_size"),
            ("Covariates", "covariates"),
            ("Full-model AUC", "performance_metrics.full_model_auc"),
            ("Effect sizes", "performance_metrics.effect_sizes"),
            ("Publication", "publication.title"),
            ("Date", "date_release"),
        ]

        lines.append("| Field | CS Pick (worked) | DK Pick (failed) | Bench #1 |")
        lines.append("|-------|-----------------|------------------|----------|")

        for label, path in key_fields:
            cs_val = get_field(cs_model, path)
            dk_val = get_field(dk_model, path)
            bench_val = get_field(bench1, path)

            if isinstance(cs_val, list) and cs_val and isinstance(cs_val[0], dict):
                cs_str = "; ".join(f"{e.get('name_short')}={e.get('estimate')}" for e in cs_val)[:80]
            elif isinstance(cs_val, list):
                cs_str = ", ".join(str(x) for x in cs_val)[:80]
            elif isinstance(cs_val, (int, float)):
                cs_str = f"{cs_val:,}" if isinstance(cs_val, int) else f"{cs_val:.4f}"
            else:
                cs_str = str(cs_val)[:80] if cs_val else "—"

            if isinstance(dk_val, list) and dk_val and isinstance(dk_val[0], dict):
                dk_str = "; ".join(f"{e.get('name_short')}={e.get('estimate')}" for e in dk_val)[:80]
            elif isinstance(dk_val, list):
                dk_str = ", ".join(str(x) for x in dk_val)[:80]
            elif isinstance(dk_val, (int, float)):
                dk_str = f"{dk_val:,}" if isinstance(dk_val, int) else f"{dk_val:.4f}"
            else:
                dk_str = str(dk_val)[:80] if dk_val else "—"

            if isinstance(bench_val, list) and bench_val and isinstance(bench_val[0], dict):
                bench_str = "; ".join(f"{e.get('name_short')}={e.get('estimate')}" for e in bench_val)[:80]
            elif isinstance(bench_val, list):
                bench_str = ", ".join(str(x) for x in bench_val)[:80]
            elif isinstance(bench_val, (int, float)):
                bench_str = f"{bench_val:,}" if isinstance(bench_val, int) else f"{bench_val:.4f}"
            else:
                bench_str = str(bench_val)[:80] if bench_val else "—"

            lines.append(f"| {label} | {cs_str} | {dk_str} | {bench_str} |")

        # AoU AUC
        cs_auc = auc_map.get(d["cs_modal"], 0)
        dk_auc = auc_map.get(d["dk_modal"], 0)
        bench_auc = auc_map.get(ranked[0], 0) if ranked else 0
        lines.append(f"| **AoU Benchmark AUC** | **{cs_auc:.4f}** | **{dk_auc:.4f}** | **{bench_auc:.4f}** |")
        lines.append("")

        # DK rationale excerpt
        dk_trials = dk_by_disease.get(ont, [])
        if dk_trials:
            lines.append("**DK rationale (trial 1):**")
            lines.append("")
            rat = dk_trials[0].get("rationale", "")[:2000]
            lines.append(f"> {rat}")
            lines.append("")

        # CS rationale excerpt
        cs_trials = cs_by_disease.get(ont, [])
        if cs_trials:
            lines.append("**CS rationale (trial 1):**")
            lines.append("")
            rat = cs_trials[0].get("rationale", "")[:2000]
            lines.append(f"> {rat}")
            lines.append("")

        # Root cause
        patterns = classify_regression_pattern(d, dk_results, cs_results)
        lines.append(f"**Classified patterns**: {', '.join(patterns)}")
        lines.append("")

        # What DK rules likely caused the switch
        lines.append("**Root cause analysis:**")
        lines.append("")
        dk_combined = " ".join(t.get("rationale", "") for t in dk_trials).lower()
        cs_combined = " ".join(t.get("rationale", "") for t in cs_trials).lower()

        # Find DK-specific themes (in DK rationale but not CS rationale)
        dk_specific_rules = []
        for rule_name, pattern in RULE_PATTERNS:
            dk_match = bool(re.search(pattern, dk_combined))
            cs_match = bool(re.search(pattern, cs_combined))
            if dk_match and not cs_match:
                dk_specific_rules.append(rule_name)

        if dk_specific_rules:
            lines.append(f"- DK-specific reasoning themes (not in CS rationale): **{', '.join(dk_specific_rules)}**")
        else:
            lines.append("- No DK-specific reasoning themes identified (same themes as CS)")

        # Structural comparison
        cs_vars = cs_model.get("variants_number") or 0
        dk_vars = dk_model.get("variants_number") or 0
        if cs_vars != dk_vars:
            lines.append(f"- Variant count: CS={cs_vars:,} vs DK={dk_vars:,} "
                        f"({'CS has more' if cs_vars > dk_vars else 'DK has more'})")

        cs_method_fam = get_method_family(cs_model.get("method_name", ""))
        dk_method_fam = get_method_family(dk_model.get("method_name", ""))
        if cs_method_fam != dk_method_fam:
            lines.append(f"- Method family: CS={cs_method_fam} vs DK={dk_method_fam}")

        lines.append("")
        lines.append("---")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Section 7: Improvement analysis (for contrast)
# ---------------------------------------------------------------------------

def build_improvement_summary(all_diseases):
    improvements = [d for d in all_diseases if d["rank_delta"] < 0]
    improvements.sort(key=lambda d: d["rank_delta"])

    lines = ["## 7. Improvement Summary (for contrast)", ""]
    lines.append(f"DK improved over CS in {len(improvements)} diseases. "
                 f"Understanding what DK does RIGHT helps preserve these gains while fixing regressions.")
    lines.append("")

    if not improvements:
        lines.append("No improvements found.")
        lines.append("")
        return lines

    lines.append("| Disease | N Models | CS Rank | DK Rank | Rank Improvement | DK Hit | CS Hit |")
    lines.append("|---------|----------|---------|---------|-----------------|--------|--------|")

    for d in improvements:
        cs_hit_str = f"@{d['cs_best_hit']}" if d["cs_best_hit"] else "None"
        dk_hit_str = f"@{d['dk_best_hit']}" if d["dk_best_hit"] else "None"
        lines.append(f"| {d['ontology']} | {d['n_models']} | {d['cs_rank']}/{d['n_models']} | "
                     f"{d['dk_rank']}/{d['n_models']} | {abs(d['rank_delta'])} | {dk_hit_str} | {cs_hit_str} |")
    lines.append("")

    # DK gained hits
    gained_hits = [d for d in improvements if d["dk_any_hit"] and not d["cs_any_hit"]]
    if gained_hits:
        lines.append(f"### Diseases where DK gained hits that CS missed ({len(gained_hits)})")
        lines.append("")
        for d in gained_hits:
            lines.append(f"- **{d['ontology']}**: CS rank {d['cs_rank']}/{d['n_models']} (no hit) → "
                        f"DK rank {d['dk_rank']}/{d['n_models']} (Hit@{d['dk_best_hit']})")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dk_summary, dk_results, cs_summary, cs_results = load_data()

    print("Identifying regressions...")
    all_diseases = identify_regressions(dk_summary, cs_summary)

    report = []
    report.append("# Regression Analysis Report")
    report.append("")
    report.append("Analysis of diseases where Catalog Search + Domain Knowledge (DK) performed")
    report.append("worse than Catalog Search Only (CS) in terms of AoU benchmark rank.")
    report.append("Goal: identify domain knowledge rules that caused regressions and propose targeted fixes")
    report.append("to prevent DK from degrading model selection quality.")
    report.append("")

    print("Building overview...")
    report.extend(build_overview(all_diseases))

    print("Building field comparisons...")
    report.extend(build_field_comparisons(all_diseases))

    print("Building rule attribution...")
    report.extend(build_rule_attribution(all_diseases, dk_results, cs_results))

    print("Building pattern classification...")
    report.extend(build_pattern_classification(all_diseases, dk_results, cs_results))

    print("Building recommendations...")
    report.extend(build_recommendations(all_diseases, dk_results, cs_results))

    print("Building severe regression profiles...")
    report.extend(build_severe_profiles(all_diseases, dk_results, cs_results))

    print("Building improvement summary...")
    report.extend(build_improvement_summary(all_diseases))

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(report), encoding="utf-8")
    print(f"\nReport written to {OUTPUT_MD}")
    print(f"Total lines: {len(report)}")


if __name__ == "__main__":
    main()
