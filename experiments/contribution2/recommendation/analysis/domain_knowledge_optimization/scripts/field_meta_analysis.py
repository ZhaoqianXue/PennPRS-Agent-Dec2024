#!/usr/bin/env python3
"""
Sub-task 1: Comprehensive Meta-Analysis of All Agent Input Fields.

For each of the 24 Agent Input fields, performs:
  Layer 1 — Full distribution profile across ALL models in all 75 diseases.
  Layer 2 — Correlation with AoU benchmark normalized rank (r/M).
  Layer 3 — Actionable pattern extraction for general domain knowledge rules.

Output: field_meta_analysis_report.md
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
RUN_DIR = BASE / "runs" / "with-domain-gpt-5.2-t10__75disease__updated-domain-knowledge-20260318"
SUMMARY_JSON = RUN_DIR / "experiment_with_domain_summary.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_MD = OUTPUT_DIR / "field_meta_analysis_report.md"
RESULTS_JSON = RUN_DIR / "experiment_with_domain_results.json"

# ---------------------------------------------------------------------------
# Method family mapping (Enhancement 1)
# ---------------------------------------------------------------------------
METHOD_FAMILY_MAP = {
    # PRS-CS family
    "PRS-CS": "PRS-CS family",
    "PRS-CS-auto": "PRS-CS family",
    "PRSCS": "PRS-CS family",
    "prscs": "PRS-CS family",
    "PRS-CS.CV": "PRS-CS family",
    # PRS-CSx family
    "PRS-CSx": "PRS-CSx family",
    "prscsx": "PRS-CSx family",
    "PRS-CSx (gene-based)": "PRS-CSx family",
    # LDpred2 family
    "LDpred2": "LDpred2 family",
    "LDpred2-auto": "LDpred2 family",
    "LDpred2.CV": "LDpred2 family",
    "LDpred2 (bigsnpr)": "LDpred2 family",
    "LDPred2Auto": "LDpred2 family",
    # LDpred (legacy) family
    "LDpred": "LDpred (legacy)",
    "ldpred": "LDpred (legacy)",
    # PRSmix family
    "PRSmix": "PRSmix/Plus family",
    "PRSmixPlus": "PRSmix/Plus family",
    "PRSsum": "PRSmix/Plus family",
    # Lassosum family
    "lassosum": "Lassosum family",
    "lassosum2": "Lassosum family",
    "Lassosum": "Lassosum family",
    "lassosum.CV": "Lassosum family",
    "lassosum.auto": "Lassosum family",
    # SBayesR family
    "SBayesR": "SBayesR family",
    "SBayesR-auto": "SBayesR family",
    # MegaPRS family
    "megaprs.auto": "MegaPRS family",
    "megaprs.CV": "MegaPRS family",
    # snpnet family
    "snpnet": "snpnet family",
    "snpnet (multi-PRS)": "snpnet family",
    "SnpNet": "snpnet family",
    # LASSO family
    "LASSO": "LASSO/Penalized family",
    "LASSO penalized regression": "LASSO/Penalized family",
    "Penalized regression (bigstatsr)": "LASSO/Penalized family",
    # P+T / C+T family
    "Pruning and Thresholding (P+T)": "P+T / C+T family",
    "Clumping and Thresholding (C+T)": "P+T / C+T family",
    "Clumping and thresholding": "P+T / C+T family",
    "Maximum clumping and thresholding (maxCT)": "P+T / C+T family",
    "Stacked clumping and thresholding (SCT)": "P+T / C+T family",
    "P-value thresholding": "P+T / C+T family",
    # PRSice family
    "PRSice": "PRSice family",
    "PRSice-2": "PRSice family",
    # GWAS Hits family
    "GWAS Hits": "GWAS Hits / GWS variants",
    "Genome-wide significant variants": "GWAS Hits / GWS variants",
    "Genome-wide significant SNPs": "GWAS Hits / GWS variants",
    "Known susceptibility loci (genome-wide significant SNPs)": "GWAS Hits / GWS variants",
    "Clumping of genome-wide significant variants": "GWAS Hits / GWS variants",
    # GenoBoost
    "GenoBoost": "GenoBoost",
    # BOLT-LMM
    "BOLT-LMM": "BOLT-LMM",
    # SDPR
    "SDPR": "SDPR",
    # DBSLMM
    "DBSLMM": "DBSLMM family",
    "DBSLMM-auto": "DBSLMM family",
    # MetaPRS/MetaGRS
    "MetaPRS": "Meta-PRS / Ensemble",
    "metaGRS": "Meta-PRS / Ensemble",
    "MetaGRS of 44 component PGS": "Meta-PRS / Ensemble",
    # CT-SLEB
    "CT-SLEB": "CT-SLEB",
    # PolyFun-pred
    "PolyFun-pred": "PolyFun-pred",
    # RFDiseasemetaPRS
    "RFDiseasemetaPRS": "RFDiseasemetaPRS",
    # PLINK
    "PLINK": "PLINK",
    # SparSNP
    "SparSNP": "SparSNP",
    # MultiPRS
    "UKBB-EUR.MultiPRS.CV": "MultiPRS family",
    # shaPRS
    "shaPRS + LDpred2": "shaPRS",
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
    if "prsmix" in ml:
        return "PRSmix/Plus family"
    if "lassosum" in ml:
        return "Lassosum family"
    if "sbayesr" in ml:
        return "SBayesR family"
    if "megaprs" in ml:
        return "MegaPRS family"
    if "snpnet" in ml:
        return "snpnet family"
    if "lasso" in ml or "penalized" in ml:
        return "LASSO/Penalized family"
    if "clumping" in ml or "thresholding" in ml or "p+t" in ml or "c+t" in ml or "pruning" in ml:
        return "P+T / C+T family"
    if "prsice" in ml:
        return "PRSice family"
    if "gwas hit" in ml or "genome-wide significant" in ml or "susceptibility loci" in ml:
        return "GWAS Hits / GWS variants"
    if "genoboost" in ml:
        return "GenoBoost"
    if "bolt" in ml:
        return "BOLT-LMM"
    if "dbslmm" in ml:
        return "DBSLMM family"
    if "variants from" in ml or "variants associated" in ml or "snps" in ml.lower():
        return "GWAS Hits / GWS variants"
    return "Other / Disease-specific"


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_data():
    with open(SUMMARY_JSON) as f:
        summary = json.load(f)
    rows = []  # flat list of (ontology, model_dict, norm_rank, benchmark_auc)
    for dd in summary["per_disease"]:
        ontology = dd["ontology"]
        ranked = dd["benchmark_ranked_ids"]
        auc_map = dd["benchmark_auc_by_id"]
        M = len(ranked)
        rank_lookup = {pid: i + 1 for i, pid in enumerate(ranked)}
        for m in dd["candidate_models_visible_to_llm"]:
            mid = m["id"]
            r = rank_lookup.get(mid)
            if r is None:
                continue
            norm_rank = r / M  # smaller = better
            bm_auc = auc_map.get(mid)
            rows.append({
                "ontology": ontology,
                "model": m,
                "rank": r,
                "M": M,
                "norm_rank": norm_rank,
                "benchmark_auc": bm_auc,
            })
    return rows, summary


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def parse_sample_size(s: str | None) -> int | None:
    if not s or s == "N/A":
        return None
    nums = re.findall(r"[\d,]+", s)
    if not nums:
        return None
    return int(nums[0].replace(",", ""))


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


def fmt(val, decimals=4):
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:.{decimals}f}"
    return str(val)


def mean_safe(vals):
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def median_safe(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def stdev_safe(vals):
    vals = [v for v in vals if v is not None]
    return statistics.stdev(vals) if len(vals) >= 2 else None


def category_rank_table(cat_ranks: dict[str, list[float]]) -> list[str]:
    """Return markdown table rows for category -> (count, mean_rank, median_rank)."""
    lines = []
    lines.append("| Category | Count | Mean norm_rank (r/M) | Median norm_rank | Interpretation |")
    lines.append("|----------|-------|---------------------|-----------------|----------------|")
    sorted_cats = sorted(cat_ranks.items(), key=lambda x: mean_safe(x[1]) or 999)
    for cat, ranks in sorted_cats:
        n = len(ranks)
        mn = mean_safe(ranks)
        md = median_safe(ranks)
        interp = "better" if mn and mn < 0.4 else ("neutral" if mn and mn < 0.6 else "worse")
        lines.append(f"| {cat} | {n} | {fmt(mn)} | {fmt(md)} | {interp} |")
    return lines


# ---------------------------------------------------------------------------
# Field analysis functions
# ---------------------------------------------------------------------------

def analyze_method_name(rows):
    lines = ["### method_name", ""]
    cat_ranks = defaultdict(list)
    for r in rows:
        method = r["model"].get("method_name", "Unknown") or "Unknown"
        cat_ranks[method].append(r["norm_rank"])
    lines.append(f"**Total unique methods**: {len(cat_ranks)}")
    lines.append("")
    lines.extend(category_rank_table(cat_ranks))
    # Spearman with method encoded as mean rank
    method_mean = {m: mean_safe(rs) for m, rs in cat_ranks.items()}
    xs = [method_mean[r["model"].get("method_name", "Unknown") or "Unknown"] for r in rows]
    ys = [r["norm_rank"] for r in rows]
    rho, p, n = spearman(xs, ys)
    lines.append("")
    lines.append(f"**Spearman correlation** (method mean rank vs norm_rank): rho={fmt(rho)}, p={fmt(p)}, n={n}")
    lines.append("")
    # Key findings
    top_methods = [cat for cat, rs in sorted(cat_ranks.items(), key=lambda x: mean_safe(x[1]) or 999) if len(rs) >= 5][:5]
    bot_methods = [cat for cat, rs in sorted(cat_ranks.items(), key=lambda x: mean_safe(x[1]) or 999, reverse=True) if len(rs) >= 5][:5]
    lines.append("**Key Findings**:")
    lines.append(f"- Top-performing methods (n>=5): {', '.join(top_methods)}")
    lines.append(f"- Worst-performing methods (n>=5): {', '.join(bot_methods)}")
    lines.append("")
    return lines


def analyze_numeric_field(rows, field_path: str, field_label: str, extract_fn=None):
    lines = [f"### {field_label}", ""]
    values = []
    norm_ranks = []
    n_available = 0
    n_total = len(rows)
    for r in rows:
        if extract_fn:
            val = extract_fn(r["model"])
        else:
            parts = field_path.split(".")
            obj = r["model"]
            for p in parts:
                if isinstance(obj, dict):
                    obj = obj.get(p)
                else:
                    obj = None
                    break
            val = obj
        if val is not None and not (isinstance(val, float) and math.isnan(val)):
            n_available += 1
            values.append(val)
            norm_ranks.append(r["norm_rank"])
    lines.append(f"**Availability**: {n_available}/{n_total} ({100*n_available/n_total:.1f}%)")
    if not values:
        lines.append("*No data available for this field.*")
        lines.append("")
        return lines
    lines.append(f"**Distribution**: mean={fmt(mean_safe(values))}, median={fmt(median_safe(values))}, "
                 f"stdev={fmt(stdev_safe(values))}, min={fmt(min(values))}, max={fmt(max(values))}")
    rho, p, n = spearman(values, norm_ranks)
    lines.append(f"**Spearman correlation with norm_rank (r/M)**: rho={fmt(rho)}, p={fmt(p)}, n={n}")
    interp = ""
    if rho is not None:
        if rho < -0.1:
            interp = "Higher values tend to have BETTER benchmark rank (lower r/M)."
        elif rho > 0.1:
            interp = "Higher values tend to have WORSE benchmark rank (higher r/M)."
        else:
            interp = "No meaningful linear relationship."
    lines.append(f"**Interpretation**: {interp}")
    lines.append("")
    # Bin analysis
    if len(values) >= 20:
        try:
            sorted_vals = sorted(values)
            q25 = sorted_vals[len(sorted_vals) // 4]
            q50 = sorted_vals[len(sorted_vals) // 2]
            q75 = sorted_vals[3 * len(sorted_vals) // 4]
            bins = {"Q1 (lowest 25%)": [], "Q2": [], "Q3": [], "Q4 (highest 25%)": []}
            for v, nr in zip(values, norm_ranks):
                if v <= q25:
                    bins["Q1 (lowest 25%)"].append(nr)
                elif v <= q50:
                    bins["Q2"].append(nr)
                elif v <= q75:
                    bins["Q3"].append(nr)
                else:
                    bins["Q4 (highest 25%)"].append(nr)
            lines.extend(category_rank_table(bins))
            lines.append("")
        except Exception:
            pass
    return lines


def analyze_trait_match(rows):
    lines = ["### trait_reported / trait_efo / phenotyping_reported", ""]
    lines.append("Categorization of how well the model's reported trait matches the target disease ontology.")
    lines.append("")
    cat_ranks = defaultdict(list)
    for r in rows:
        ontology = r["ontology"].lower().strip()
        trait_r = (r["model"].get("trait_reported") or "").lower().strip()
        trait_efo = (r["model"].get("trait_efo") or "").lower().strip()
        pheno = (r["model"].get("phenotyping_reported") or "").lower().strip()

        # Categorize match quality
        if ontology in trait_efo or trait_efo in ontology:
            if "time" in trait_r or "tte" in trait_r or "survival" in trait_r or "incident" in trait_r:
                cat = "Exact + TTE/Incident"
            elif "mtag" in trait_r or "multi-trait" in trait_r.lower():
                cat = "Exact + MTAG/Multi-trait"
            else:
                cat = "Exact match"
        elif any(w in trait_efo for w in ontology.split()) or any(w in ontology for w in trait_efo.split() if len(w) > 3):
            cat = "Partial/Subtype match"
        else:
            cat = "Cross-disease/Distant"

        cat_ranks[cat].append(r["norm_rank"])

    lines.extend(category_rank_table(cat_ranks))
    lines.append("")
    lines.append("**Key Findings**:")
    for cat, rs in sorted(cat_ranks.items(), key=lambda x: mean_safe(x[1]) or 999):
        mn = mean_safe(rs)
        lines.append(f"- {cat}: n={len(rs)}, mean norm_rank={fmt(mn)}")
    lines.append("")
    return lines


def analyze_ancestry(rows):
    lines = ["### ancestry_distribution", ""]
    cat_ranks = defaultdict(list)
    eval_cats = defaultdict(list)
    for r in rows:
        anc = r["model"].get("ancestry_distribution", "") or ""

        # Overall categorization
        if not anc:
            cat_ranks["Unknown/Empty"].append(r["norm_rank"])
        elif "multi" in anc.lower() or ("EUR" in anc and ("AFR" in anc or "EAS" in anc or "SAS" in anc or "AMR" in anc)):
            cat_ranks["Multi-ancestry"].append(r["norm_rank"])
        elif "EUR" in anc and "AFR" not in anc and "EAS" not in anc:
            cat_ranks["EUR-only"].append(r["norm_rank"])
        else:
            cat_ranks["Other/Non-EUR"].append(r["norm_rank"])

        # Eval ancestry
        eval_match = re.search(r"EVAL:\s*(.+?)(?:\||$)", anc)
        if eval_match:
            eval_str = eval_match.group(1).strip()
            if "EUR" in eval_str and ("AFR" in eval_str or "EAS" in eval_str):
                eval_cats["Multi-ancestry eval"].append(r["norm_rank"])
            elif "EUR" in eval_str:
                eval_cats["EUR eval"].append(r["norm_rank"])
            else:
                eval_cats["Non-EUR eval"].append(r["norm_rank"])
        else:
            eval_cats["Unknown eval"].append(r["norm_rank"])

    lines.append("**Overall Ancestry Pattern:**")
    lines.extend(category_rank_table(cat_ranks))
    lines.append("")
    lines.append("**Evaluation Ancestry:**")
    lines.extend(category_rank_table(eval_cats))
    lines.append("")
    return lines


def analyze_covariates(rows):
    lines = ["### covariates", ""]
    cat_ranks = defaultdict(list)

    heavy_keywords = ["family", "apoe", "charge", "framingham", "egfr", "tsh", "bmi",
                      "blood pressure", "cholesterol", "hdl", "ldl", "triglyceride",
                      "glucose", "hba1c", "creatinine", "albumin", "bilirubin",
                      "risk score", "risk calculator", "clinical"]
    moderate_keywords = ["smoking", "alcohol", "education", "income", "townsend",
                         "deprivation", "body mass", "waist", "height", "weight"]

    for r in rows:
        cov = (r["model"].get("covariates") or "").lower().strip()
        if not cov or cov in ("unknown", "n/a", "0"):
            cat = "None/Unknown"
        elif any(kw in cov for kw in heavy_keywords):
            cat = "Heavy (biomarkers/clinical)"
        elif any(kw in cov for kw in moderate_keywords):
            cat = "Moderate (lifestyle)"
        elif any(kw in cov for kw in ["age", "sex", "pc", "principal"]):
            cat = "Basic (age/sex/PCs)"
        else:
            cat = "Other"
        cat_ranks[cat].append(r["norm_rank"])

    lines.extend(category_rank_table(cat_ranks))
    lines.append("")

    # Also check reported AUC vs benchmark AUC discrepancy by covariate category
    lines.append("**Reported AUC vs Benchmark AUC by Covariate Category:**")
    lines.append("")
    lines.append("| Category | Mean reported AUC | Mean benchmark AUC | Discrepancy |")
    lines.append("|----------|------------------|-------------------|-------------|")
    for cat in ["None/Unknown", "Basic (age/sex/PCs)", "Moderate (lifestyle)", "Heavy (biomarkers/clinical)", "Other"]:
        reported_aucs = []
        benchmark_aucs = []
        for r in rows:
            cov = (r["model"].get("covariates") or "").lower().strip()
            if not cov or cov in ("unknown", "n/a", "0"):
                c = "None/Unknown"
            elif any(kw in cov for kw in heavy_keywords):
                c = "Heavy (biomarkers/clinical)"
            elif any(kw in cov for kw in moderate_keywords):
                c = "Moderate (lifestyle)"
            elif any(kw in cov for kw in ["age", "sex", "pc", "principal"]):
                c = "Basic (age/sex/PCs)"
            else:
                c = "Other"
            if c != cat:
                continue
            pm = r["model"].get("performance_metrics", {})
            rep_auc = pm.get("auc") or pm.get("full_model_auc")
            bm_auc = r["benchmark_auc"]
            if rep_auc and bm_auc:
                reported_aucs.append(rep_auc)
                benchmark_aucs.append(bm_auc)
        if reported_aucs:
            mean_rep = mean_safe(reported_aucs)
            mean_bm = mean_safe(benchmark_aucs)
            disc = mean_rep - mean_bm if mean_rep and mean_bm else None
            lines.append(f"| {cat} | {fmt(mean_rep)} | {fmt(mean_bm)} | {fmt(disc)} |")
    lines.append("")
    return lines


def analyze_cohorts(rows):
    lines = ["### training_development_cohorts", ""]
    cat_ranks = defaultdict(list)
    cohort_counter = Counter()

    for r in rows:
        cohorts = r["model"].get("training_development_cohorts") or []
        n_cohorts = len(cohorts)
        cohorts_lower = [c.lower() for c in cohorts]

        for c in cohorts:
            cohort_counter[c] += 1

        # Categorize
        if n_cohorts == 0:
            cat = "No cohorts listed"
        elif n_cohorts == 1:
            if "ukb" in cohorts_lower[0] or "uk biobank" in cohorts_lower[0]:
                cat = "UKB-only (single cohort)"
            else:
                cat = "Single cohort (non-UKB)"
        elif n_cohorts <= 3:
            cat = "2-3 cohorts"
        else:
            cat = "4+ cohorts (multi-cohort)"
        cat_ranks[cat].append(r["norm_rank"])

    lines.extend(category_rank_table(cat_ranks))
    lines.append("")

    # Spearman: n_cohorts vs rank
    xs = [len(r["model"].get("training_development_cohorts") or []) for r in rows]
    ys = [r["norm_rank"] for r in rows]
    rho, p, n = spearman(xs, ys)
    lines.append(f"**Spearman correlation** (n_cohorts vs norm_rank): rho={fmt(rho)}, p={fmt(p)}, n={n}")
    lines.append("")

    # Top cohorts
    lines.append("**Most common cohorts (top 20):**")
    lines.append("")
    lines.append("| Cohort | Count |")
    lines.append("|--------|-------|")
    for cohort, cnt in cohort_counter.most_common(20):
        lines.append(f"| {cohort} | {cnt} |")
    lines.append("")
    return lines


def analyze_publication(rows):
    lines = ["### publication.title / publication.journal", ""]

    # Study type classification
    framework_patterns = [
        r"813\s*trait", r"245\s*polygenic", r"exprs", r"global\s*biobank",
        r"portability", r"across\s*biobanks", r"atlas\s*of\s*polygenic",
        r"pan-.*trait", r"phenome-wide", r"multi-trait", r"mtag",
    ]
    cat_ranks = defaultdict(list)
    journal_ranks = defaultdict(list)

    for r in rows:
        title = (r["model"].get("publication", {}).get("title") or "").lower()
        journal = r["model"].get("publication", {}).get("journal") or "Unknown"

        is_framework = any(re.search(pat, title) for pat in framework_patterns)
        if is_framework:
            cat = "Pan-trait / Framework"
        elif any(kw in title for kw in ["portability", "transferability", "transportability"]):
            cat = "Portability / Transferability study"
        elif any(kw in title for kw in ["benchmark", "comparison", "evaluate", "assessment"]):
            cat = "Benchmarking / Comparative"
        else:
            cat = "Disease-focused"

        cat_ranks[cat].append(r["norm_rank"])
        journal_ranks[journal].append(r["norm_rank"])

    lines.append("**Study Type Classification:**")
    lines.extend(category_rank_table(cat_ranks))
    lines.append("")

    # Journal analysis (top 15)
    lines.append("**Top 15 Journals by Model Count:**")
    lines.append("")
    lines.append("| Journal | Count | Mean norm_rank |")
    lines.append("|---------|-------|---------------|")
    for j, rs in sorted(journal_ranks.items(), key=lambda x: -len(x[1]))[:15]:
        lines.append(f"| {j} | {len(rs)} | {fmt(mean_safe(rs))} |")
    lines.append("")
    return lines


def analyze_date_release(rows):
    lines = ["### date_release", ""]
    # Parse dates and compute year
    year_ranks = defaultdict(list)
    years = []
    norm_ranks = []
    for r in rows:
        d = r["model"].get("date_release", "")
        if d:
            try:
                year = int(d[:4])
                year_ranks[str(year)].append(r["norm_rank"])
                years.append(year)
                norm_ranks.append(r["norm_rank"])
            except (ValueError, IndexError):
                pass

    rho, p, n = spearman(years, norm_ranks)
    lines.append(f"**Spearman correlation** (release year vs norm_rank): rho={fmt(rho)}, p={fmt(p)}, n={n}")
    if rho is not None and rho < -0.05:
        lines.append("*Newer models tend to have better benchmark rank.*")
    elif rho is not None and rho > 0.05:
        lines.append("*Older models tend to have better benchmark rank.*")
    lines.append("")
    lines.extend(category_rank_table(year_ranks))
    lines.append("")
    return lines


def analyze_variants(rows):
    lines = ["### variants_number", ""]
    values = []
    norm_ranks = []
    cat_ranks = defaultdict(list)
    for r in rows:
        v = r["model"].get("variants_number")
        if v and v > 0:
            values.append(v)
            norm_ranks.append(r["norm_rank"])
            if v < 100:
                cat = "<100"
            elif v < 1000:
                cat = "100-1K"
            elif v < 10000:
                cat = "1K-10K"
            elif v < 100000:
                cat = "10K-100K"
            elif v < 500000:
                cat = "100K-500K"
            elif v < 1000000:
                cat = "500K-1M"
            else:
                cat = ">1M"
            cat_ranks[cat].append(r["norm_rank"])

    log_values = [math.log10(v) for v in values]
    rho, p, n = spearman(log_values, norm_ranks)
    lines.append(f"**Distribution**: n={len(values)}, median={fmt(median_safe(values), 0)}, "
                 f"min={min(values) if values else 'N/A'}, max={max(values) if values else 'N/A'}")
    lines.append(f"**Spearman correlation** (log10(variants) vs norm_rank): rho={fmt(rho)}, p={fmt(p)}, n={n}")
    lines.append("")
    lines.extend(category_rank_table(cat_ranks))
    lines.append("")
    return lines


def analyze_effect_sizes(rows):
    lines = ["### performance_metrics.effect_sizes", ""]
    has_es_ranks = defaultdict(list)  # "Has effect sizes" vs "No effect sizes"
    type_ranks = defaultdict(list)   # OR, HR, Beta etc

    for r in rows:
        pm = r["model"].get("performance_metrics", {})
        es = pm.get("effect_sizes") or []
        if es:
            has_es_ranks["Has effect sizes"].append(r["norm_rank"])
            for e in es:
                short = e.get("name_short", "Unknown")
                type_ranks[short].append(r["norm_rank"])
        else:
            has_es_ranks["No effect sizes"].append(r["norm_rank"])

    lines.append("**Availability:**")
    lines.extend(category_rank_table(has_es_ranks))
    lines.append("")
    lines.append("**By Effect Size Type:**")
    lines.extend(category_rank_table(type_ranks))
    lines.append("")
    return lines


def analyze_classification_other_metrics(rows):
    lines = ["### performance_metrics.classification_metrics / other_metrics", ""]

    cm_type_ranks = defaultdict(list)
    om_type_ranks = defaultdict(list)

    for r in rows:
        pm = r["model"].get("performance_metrics", {})
        cms = pm.get("classification_metrics") or []
        oms = pm.get("other_metrics") or []

        for c in cms:
            cm_type_ranks[c.get("name_short", "Unknown")].append(r["norm_rank"])
        for o in oms:
            om_type_ranks[o.get("name_short", "Unknown")].append(r["norm_rank"])

    if cm_type_ranks:
        lines.append("**Classification Metrics Types:**")
        lines.extend(category_rank_table(cm_type_ranks))
        lines.append("")
    if om_type_ranks:
        lines.append("**Other Metrics Types:**")
        lines.extend(category_rank_table(om_type_ranks))
        lines.append("")
    return lines


def analyze_validation_ancestry(rows):
    lines = ["### performance_metrics.selected_validation_ancestry", ""]
    cat_ranks = defaultdict(list)
    for r in rows:
        pm = r["model"].get("performance_metrics", {})
        anc = pm.get("selected_validation_ancestry") or "Unknown"
        cat_ranks[anc].append(r["norm_rank"])
    lines.extend(category_rank_table(cat_ranks))
    lines.append("")
    return lines


def analyze_record_count(rows):
    return analyze_numeric_field(
        rows, "performance_metrics.record_count", "performance_metrics.record_count"
    )


def analyze_reported_vs_benchmark_auc(rows):
    """Special analysis: scatter of reported AUC (pgs_only or full_model) vs benchmark AUC."""
    lines = ["### Reported AUC vs Benchmark AUC (Inflation Analysis)", ""]

    # Collect data for pgs-only AUC
    pgs_only = []
    full_model = []
    for r in rows:
        pm = r["model"].get("performance_metrics", {})
        bm = r["benchmark_auc"]
        if bm is None:
            continue
        auc_pgs = pm.get("auc") or pm.get("pgs_only_auc")
        auc_full = pm.get("full_model_auc")
        if auc_pgs is not None:
            pgs_only.append((auc_pgs, bm, r["norm_rank"], r["ontology"], r["model"]["id"]))
        if auc_full is not None:
            full_model.append((auc_full, bm, r["norm_rank"], r["ontology"], r["model"]["id"]))

    if pgs_only:
        rep_vals = [x[0] for x in pgs_only]
        bm_vals = [x[1] for x in pgs_only]
        rho, p, n = spearman(rep_vals, bm_vals)
        lines.append(f"**PGS-only AUC vs Benchmark AUC**: rho={fmt(rho)}, p={fmt(p)}, n={n}")
        # Find biggest positive discrepancies (reported >> benchmark)
        discreps = [(x[0] - x[1], x) for x in pgs_only]
        discreps.sort(reverse=True)
        lines.append("")
        lines.append("**Top 10 inflation cases (reported PGS-only AUC >> benchmark AUC):**")
        lines.append("")
        lines.append("| Model | Ontology | Reported AUC | Benchmark AUC | Gap |")
        lines.append("|-------|----------|-------------|--------------|-----|")
        for gap, (rep, bm, nr, ont, mid) in discreps[:10]:
            lines.append(f"| {mid} | {ont} | {fmt(rep)} | {fmt(bm)} | {fmt(gap)} |")
        lines.append("")

    if full_model:
        rep_vals = [x[0] for x in full_model]
        bm_vals = [x[1] for x in full_model]
        rho, p, n = spearman(rep_vals, bm_vals)
        lines.append(f"**Full-model AUC vs Benchmark AUC**: rho={fmt(rho)}, p={fmt(p)}, n={n}")
        discreps = [(x[0] - x[1], x) for x in full_model]
        discreps.sort(reverse=True)
        lines.append("")
        lines.append("**Top 10 inflation cases (reported full-model AUC >> benchmark AUC):**")
        lines.append("")
        lines.append("| Model | Ontology | Reported full AUC | Benchmark AUC | Gap |")
        lines.append("|-------|----------|------------------|--------------|-----|")
        for gap, (rep, bm, nr, ont, mid) in discreps[:10]:
            lines.append(f"| {mid} | {ont} | {fmt(rep)} | {fmt(bm)} | {fmt(gap)} |")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Enhancement 1: Method family consolidation
# ---------------------------------------------------------------------------

def analyze_method_families(rows):
    lines = ["### Method Family Consolidation (152 raw methods → ~25 families)", ""]
    lines.append("Methods consolidated into families for actionable tier analysis.")
    lines.append("")

    family_ranks = defaultdict(list)
    for r in rows:
        method = r["model"].get("method_name") or "Unknown"
        family = get_method_family(method)
        family_ranks[family].append(r["norm_rank"])

    lines.append("| Method Family | N Models | Mean norm_rank | Median norm_rank | Tier |")
    lines.append("|---------------|----------|---------------|-----------------|------|")

    sorted_families = sorted(family_ranks.items(), key=lambda x: mean_safe(x[1]) or 999)
    for fam, ranks in sorted_families:
        n = len(ranks)
        mn = mean_safe(ranks)
        md = median_safe(ranks)
        if mn is not None:
            if mn < 0.30:
                tier = "S-tier"
            elif mn < 0.40:
                tier = "A-tier"
            elif mn < 0.50:
                tier = "B-tier"
            elif mn < 0.60:
                tier = "C-tier"
            else:
                tier = "D-tier"
        else:
            tier = "?"
        lines.append(f"| {fam} | {n} | {fmt(mn)} | {fmt(md)} | {tier} |")

    lines.append("")

    # Key head-to-head comparisons
    lines.append("**Key Head-to-Head Comparisons:**")
    lines.append("")
    comparisons = [
        ("PRS-CSx family", "PRS-CS family", "PRS-CSx vs PRS-CS"),
        ("LDpred2 family", "LDpred (legacy)", "LDpred2 vs LDpred (legacy)"),
        ("PRSmix/Plus family", "PRS-CS family", "PRSmix/Plus vs PRS-CS"),
        ("MegaPRS family", "PRS-CS family", "MegaPRS vs PRS-CS"),
        ("snpnet family", "LDpred2 family", "snpnet vs LDpred2"),
        ("GWAS Hits / GWS variants", "PRS-CS family", "GWAS Hits vs PRS-CS"),
        ("P+T / C+T family", "PRS-CS family", "P+T/C+T vs PRS-CS"),
    ]
    for fam_a, fam_b, label in comparisons:
        ra = family_ranks.get(fam_a, [])
        rb = family_ranks.get(fam_b, [])
        if ra and rb:
            ma = mean_safe(ra)
            mb = mean_safe(rb)
            winner = fam_a if (ma or 999) < (mb or 999) else fam_b
            lines.append(f"- **{label}**: {fam_a} mean={fmt(ma)} (n={len(ra)}) vs "
                        f"{fam_b} mean={fmt(mb)} (n={len(rb)}) → **{winner} wins**")
    lines.append("")

    # Actionable tier summary
    lines.append("**Actionable Method Tier Summary** (n≥5 only):")
    lines.append("")
    for fam, ranks in sorted_families:
        mn = mean_safe(ranks)
        n = len(ranks)
        if n >= 5 and mn is not None:
            if mn < 0.30:
                lines.append(f"- **S-tier** (mean rank <0.30): {fam} (n={n}, mean={fmt(mn)})")
            elif mn < 0.40:
                lines.append(f"- **A-tier** (mean rank 0.30-0.40): {fam} (n={n}, mean={fmt(mn)})")
            elif mn < 0.50:
                lines.append(f"- **B-tier** (mean rank 0.40-0.50): {fam} (n={n}, mean={fmt(mn)})")
            elif mn >= 0.50:
                lines.append(f"- **C/D-tier** (mean rank ≥0.50): {fam} (n={n}, mean={fmt(mn)})")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Enhancement 2: Per-disease internal Spearman
# ---------------------------------------------------------------------------

def analyze_per_disease_spearman(rows, summary):
    lines = ["### Per-Disease Internal Spearman Correlations", ""]
    lines.append("For each field, compute Spearman rho WITHIN each disease, then report the distribution")
    lines.append("of per-disease rho values. This reflects the agent's actual ranking scenario.")
    lines.append("")

    def _get_field(model, path):
        parts = path.split(".")
        obj = model
        for p in parts:
            obj = obj.get(p) if isinstance(obj, dict) else None
            if obj is None:
                return None
        return obj

    # Group rows by ontology
    by_disease = defaultdict(list)
    for r in rows:
        by_disease[r["ontology"]].append(r)

    fields_to_analyze = [
        ("variants_number", lambda m: m.get("variants_number")),
        ("full_model_auc", lambda m: _get_field(m, "performance_metrics.full_model_auc")),
        ("full_model_r2", lambda m: _get_field(m, "performance_metrics.full_model_r2")),
        ("validation_sample_size", lambda m: parse_sample_size(m.get("validation_sample_size"))),
        ("samples_training", lambda m: parse_sample_size(m.get("samples_training"))),
        ("record_count", lambda m: _get_field(m, "performance_metrics.record_count")),
        ("date_release_year", lambda m: int(m.get("date_release", "0000")[:4]) if m.get("date_release") else None),
        ("n_cohorts", lambda m: len(m.get("training_development_cohorts") or [])),
    ]

    lines.append("| Field | N diseases (n≥5) | Median rho | Mean rho | % diseases rho<0 (better=lower rank) | Interpretation |")
    lines.append("|-------|------------------|-----------|---------|--------------------------------------|----------------|")

    for field_name, extract_fn in fields_to_analyze:
        rhos = []
        for ont, disease_rows in by_disease.items():
            if len(disease_rows) < 5:
                continue
            vals = [extract_fn(r["model"]) for r in disease_rows]
            nrs = [r["norm_rank"] for r in disease_rows]
            rho, p, n = spearman(vals, nrs)
            if rho is not None:
                rhos.append(rho)

        if rhos:
            med_rho = median_safe(rhos)
            mean_rho = mean_safe(rhos)
            pct_negative = sum(1 for r in rhos if r < 0) / len(rhos) * 100
            if mean_rho < -0.1:
                interp = "Higher values → BETTER rank (useful signal)"
            elif mean_rho > 0.1:
                interp = "Higher values → WORSE rank (reverse signal)"
            else:
                interp = "Weak / inconsistent signal"
            lines.append(f"| {field_name} | {len(rhos)} | {fmt(med_rho)} | {fmt(mean_rho)} | {pct_negative:.0f}% | {interp} |")
        else:
            lines.append(f"| {field_name} | 0 | N/A | N/A | N/A | Insufficient data |")

    lines.append("")

    # Detailed per-disease breakdown for variants_number
    lines.append("**Per-Disease Spearman for variants_number (top signal):**")
    lines.append("")
    lines.append("| Disease | N models | Spearman rho | Interpretation |")
    lines.append("|---------|----------|-------------|----------------|")

    variant_rhos = []
    for ont, disease_rows in sorted(by_disease.items()):
        if len(disease_rows) < 5:
            continue
        vals = [r["model"].get("variants_number") for r in disease_rows]
        nrs = [r["norm_rank"] for r in disease_rows]
        rho, p, n = spearman(vals, nrs)
        if rho is not None:
            variant_rhos.append((ont, len(disease_rows), rho))

    for ont, n, rho in sorted(variant_rhos, key=lambda x: x[2]):
        interp = "more variants → better" if rho < -0.2 else ("more variants → worse" if rho > 0.2 else "weak")
        lines.append(f"| {ont} | {n} | {fmt(rho)} | {interp} |")

    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Enhancement 3: Effect size magnitude analysis
# ---------------------------------------------------------------------------

def analyze_effect_size_magnitude(rows):
    lines = ["### Effect Size Magnitude vs Benchmark Rank", ""]

    # Collect OR and HR values
    or_data = []
    hr_data = []

    for r in rows:
        pm = r["model"].get("performance_metrics", {})
        es = pm.get("effect_sizes") or []
        for e in es:
            short = e.get("name_short", "")
            est = e.get("estimate")
            if est is None:
                continue
            if short == "OR":
                or_data.append((est, r["norm_rank"], r["model"]["id"], r["ontology"]))
            elif short == "HR":
                hr_data.append((est, r["norm_rank"], r["model"]["id"], r["ontology"]))

    # OR analysis
    if or_data:
        lines.append("**Odds Ratio (OR) per SD:**")
        lines.append("")
        lines.append(f"N models with OR: {len(or_data)}")

        or_vals = [x[0] for x in or_data]
        or_nrs = [x[1] for x in or_data]
        rho, p, n = spearman(or_vals, or_nrs)
        lines.append(f"Spearman (OR vs norm_rank): rho={fmt(rho)}, p={fmt(p)}, n={n}")
        lines.append("")

        bins = {
            "OR < 1.1": [], "1.1 ≤ OR < 1.3": [], "1.3 ≤ OR < 1.5": [],
            "1.5 ≤ OR < 2.0": [], "OR ≥ 2.0": [],
        }
        for or_val, nr, mid, ont in or_data:
            if or_val < 1.1:
                bins["OR < 1.1"].append(nr)
            elif or_val < 1.3:
                bins["1.1 ≤ OR < 1.3"].append(nr)
            elif or_val < 1.5:
                bins["1.3 ≤ OR < 1.5"].append(nr)
            elif or_val < 2.0:
                bins["1.5 ≤ OR < 2.0"].append(nr)
            else:
                bins["OR ≥ 2.0"].append(nr)

        lines.append("| OR Range | N Models | Mean norm_rank | Median norm_rank | Interpretation |")
        lines.append("|----------|----------|---------------|-----------------|----------------|")
        for label, nrs in bins.items():
            if nrs:
                mn = mean_safe(nrs)
                md = median_safe(nrs)
                interp = "better" if mn and mn < 0.4 else ("neutral" if mn and mn < 0.6 else "worse")
                lines.append(f"| {label} | {len(nrs)} | {fmt(mn)} | {fmt(md)} | {interp} |")
        lines.append("")

    # HR analysis
    if hr_data:
        lines.append("**Hazard Ratio (HR) per SD:**")
        lines.append("")
        lines.append(f"N models with HR: {len(hr_data)}")

        hr_vals = [x[0] for x in hr_data]
        hr_nrs = [x[1] for x in hr_data]
        rho, p, n = spearman(hr_vals, hr_nrs)
        lines.append(f"Spearman (HR vs norm_rank): rho={fmt(rho)}, p={fmt(p)}, n={n}")
        lines.append("")

        bins_hr = {
            "HR < 1.2": [], "1.2 ≤ HR < 1.5": [], "1.5 ≤ HR < 2.0": [], "HR ≥ 2.0": [],
        }
        for hr_val, nr, mid, ont in hr_data:
            if hr_val < 1.2:
                bins_hr["HR < 1.2"].append(nr)
            elif hr_val < 1.5:
                bins_hr["1.2 ≤ HR < 1.5"].append(nr)
            elif hr_val < 2.0:
                bins_hr["1.5 ≤ HR < 2.0"].append(nr)
            else:
                bins_hr["HR ≥ 2.0"].append(nr)

        lines.append("| HR Range | N Models | Mean norm_rank | Median norm_rank |")
        lines.append("|----------|----------|---------------|-----------------|")
        for label, nrs in bins_hr.items():
            if nrs:
                lines.append(f"| {label} | {len(nrs)} | {fmt(mean_safe(nrs))} | {fmt(median_safe(nrs))} |")
        lines.append("")

    # Can effect sizes substitute for missing AUC?
    lines.append("**Can Strong Effect Sizes Compensate for Missing AUC?**")
    lines.append("")
    has_auc_no_es = []
    no_auc_has_es = []
    has_both = []
    neither = []
    for r in rows:
        pm = r["model"].get("performance_metrics", {})
        has_auc = (pm.get("auc") is not None) or (pm.get("full_model_auc") is not None)
        has_es = bool(pm.get("effect_sizes"))
        if has_auc and has_es:
            has_both.append(r["norm_rank"])
        elif has_auc and not has_es:
            has_auc_no_es.append(r["norm_rank"])
        elif not has_auc and has_es:
            no_auc_has_es.append(r["norm_rank"])
        else:
            neither.append(r["norm_rank"])

    lines.append("| Category | N Models | Mean norm_rank | Median norm_rank |")
    lines.append("|----------|----------|---------------|-----------------|")
    for label, vals in [
        ("Has AUC + Effect Sizes", has_both),
        ("Has AUC only", has_auc_no_es),
        ("Has Effect Sizes only (no AUC)", no_auc_has_es),
        ("Neither", neither),
    ]:
        if vals:
            lines.append(f"| {label} | {len(vals)} | {fmt(mean_safe(vals))} | {fmt(median_safe(vals))} |")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Cross-field interaction analysis
# ---------------------------------------------------------------------------

def analyze_cross_field(rows):
    lines = ["## Cross-Field Interaction Findings", ""]

    # Method + Study type
    lines.append("### Method x Study Type")
    lines.append("")
    framework_patterns = [
        r"813\s*trait", r"245\s*polygenic", r"exprs", r"global\s*biobank",
        r"portability", r"across\s*biobanks", r"pan-.*trait", r"phenome-wide",
    ]
    combo_ranks = defaultdict(list)
    for r in rows:
        method = r["model"].get("method_name") or "Unknown"
        title = (r["model"].get("publication", {}).get("title") or "").lower()
        is_framework = any(re.search(pat, title) for pat in framework_patterns)
        study = "Framework" if is_framework else "Disease-focused"
        combo_ranks[f"{method} + {study}"].append(r["norm_rank"])

    # Show combos with n>=10
    lines.append("| Method + Study Type | Count | Mean norm_rank |")
    lines.append("|---------------------|-------|---------------|")
    for combo, rs in sorted(combo_ranks.items(), key=lambda x: mean_safe(x[1]) or 999):
        if len(rs) >= 10:
            lines.append(f"| {combo} | {len(rs)} | {fmt(mean_safe(rs))} |")
    lines.append("")

    # Covariates + reported AUC availability
    lines.append("### Covariate Load x AUC Availability")
    lines.append("")
    heavy_keywords = ["family", "apoe", "charge", "framingham", "egfr", "tsh",
                      "blood pressure", "cholesterol", "hdl", "ldl"]
    combo_ranks2 = defaultdict(list)
    for r in rows:
        cov = (r["model"].get("covariates") or "").lower()
        is_heavy = any(kw in cov for kw in heavy_keywords)
        cov_cat = "Heavy covariates" if is_heavy else "Basic/None"
        pm = r["model"].get("performance_metrics", {})
        has_auc = pm.get("auc") is not None or pm.get("full_model_auc") is not None
        auc_cat = "Has reported AUC" if has_auc else "No reported AUC"
        combo_ranks2[f"{cov_cat} + {auc_cat}"].append(r["norm_rank"])

    lines.extend(category_rank_table(combo_ranks2))
    lines.append("")

    # Variants + Method
    lines.append("### Variants Range x Method")
    lines.append("")
    combo_ranks3 = defaultdict(list)
    for r in rows:
        v = r["model"].get("variants_number") or 0
        method = r["model"].get("method_name") or "Unknown"
        if v >= 1000000:
            v_cat = ">1M variants"
        elif v >= 100000:
            v_cat = "100K-1M variants"
        else:
            v_cat = "<100K variants"
        combo_ranks3[f"{v_cat} + {method}"].append(r["norm_rank"])

    lines.append("| Variants x Method | Count | Mean norm_rank |")
    lines.append("|-------------------|-------|---------------|")
    for combo, rs in sorted(combo_ranks3.items(), key=lambda x: mean_safe(x[1]) or 999):
        if len(rs) >= 10:
            lines.append(f"| {combo} | {len(rs)} | {fmt(mean_safe(rs))} |")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------

def build_executive_summary(rows):
    lines = ["## Executive Summary", ""]
    lines.append(f"**Total models analyzed**: {len(rows)} across 75 diseases")
    lines.append("")

    # Compute per-field correlation strength
    field_corr = {}

    # method_name (use category mean rank approach)
    method_ranks = defaultdict(list)
    for r in rows:
        m = r["model"].get("method_name") or "Unknown"
        method_ranks[m].append(r["norm_rank"])
    method_mean = {m: mean_safe(rs) for m, rs in method_ranks.items()}
    xs = [method_mean[r["model"].get("method_name") or "Unknown"] for r in rows]
    ys = [r["norm_rank"] for r in rows]
    rho, p, _ = spearman(xs, ys)
    if rho is not None:
        field_corr["method_name"] = abs(rho)

    # Numeric fields
    numeric_fields = [
        ("performance_metrics.auc", "auc"),
        ("performance_metrics.full_model_auc", "full_model_auc"),
        ("performance_metrics.r2", "r2"),
        ("variants_number", "variants_number"),
        ("performance_metrics.record_count", "record_count"),
    ]
    for field_path, label in numeric_fields:
        vals = []
        nrs = []
        for r in rows:
            parts = field_path.split(".")
            obj = r["model"]
            for p in parts:
                obj = obj.get(p) if isinstance(obj, dict) else None
                if obj is None:
                    break
            if obj is not None:
                vals.append(obj)
                nrs.append(r["norm_rank"])
        rho, p, _ = spearman(vals, nrs)
        if rho is not None:
            field_corr[label] = abs(rho)

    # Sample sizes
    for field_name in ["validation_sample_size", "samples_training"]:
        vals, nrs = [], []
        for r in rows:
            v = parse_sample_size(r["model"].get(field_name))
            if v is not None:
                vals.append(v)
                nrs.append(r["norm_rank"])
        rho, p, _ = spearman(vals, nrs)
        if rho is not None:
            field_corr[field_name] = abs(rho)

    # Release year
    vals, nrs = [], []
    for r in rows:
        d = r["model"].get("date_release", "")
        if d:
            try:
                vals.append(int(d[:4]))
                nrs.append(r["norm_rank"])
            except (ValueError, IndexError):
                pass
    rho, p, _ = spearman(vals, nrs)
    if rho is not None:
        field_corr["date_release"] = abs(rho)

    lines.append("**Field Correlation Strength with Benchmark Performance (|Spearman rho|):**")
    lines.append("")
    lines.append("| Field | |rho| | Predictive Power |")
    lines.append("|-------|-------|-----------------|")
    for field, rho_abs in sorted(field_corr.items(), key=lambda x: -x[1]):
        power = "Strong" if rho_abs > 0.3 else ("Moderate" if rho_abs > 0.15 else "Weak")
        lines.append(f"| {field} | {fmt(rho_abs)} | {power} |")
    lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading data...")
    rows, summary = load_data()
    print(f"Loaded {len(rows)} model-disease pairs across {len(summary['per_disease'])} diseases.")

    report = []
    report.append("# Agent Input Field Comprehensive Meta-Analysis")
    report.append("")
    report.append("Analysis of all 24 Agent Input fields across ALL PRS models in 75 diseases,")
    report.append("correlating field values with AoU benchmark normalized rank (r/M, lower = better).")
    report.append("")

    # Executive summary
    print("Building executive summary...")
    report.extend(build_executive_summary(rows))

    # Per-field analyses
    report.append("## Per-Field Analysis")
    report.append("")

    print("Analyzing trait match...")
    report.extend(analyze_trait_match(rows))

    print("Analyzing method_name (raw)...")
    report.extend(analyze_method_name(rows))

    print("Analyzing method families (consolidated)...")
    report.extend(analyze_method_families(rows))

    print("Analyzing performance_metrics.auc...")
    report.extend(analyze_numeric_field(rows, "performance_metrics.auc", "performance_metrics.auc (PGS-only)"))

    print("Analyzing performance_metrics.full_model_auc...")
    report.extend(analyze_numeric_field(rows, "performance_metrics.full_model_auc", "performance_metrics.full_model_auc"))

    print("Analyzing performance_metrics.r2...")
    report.extend(analyze_numeric_field(rows, "performance_metrics.r2", "performance_metrics.r2"))

    print("Analyzing performance_metrics.full_model_r2...")
    report.extend(analyze_numeric_field(rows, "performance_metrics.full_model_r2", "performance_metrics.full_model_r2"))

    print("Analyzing performance_metrics.incremental_auc...")
    report.extend(analyze_numeric_field(rows, "performance_metrics.incremental_auc", "performance_metrics.incremental_auc"))

    print("Analyzing reported vs benchmark AUC (inflation)...")
    report.extend(analyze_reported_vs_benchmark_auc(rows))

    print("Analyzing effect_sizes...")
    report.extend(analyze_effect_sizes(rows))

    print("Analyzing effect size magnitudes (OR/HR bins)...")
    report.extend(analyze_effect_size_magnitude(rows))

    print("Analyzing classification/other metrics...")
    report.extend(analyze_classification_other_metrics(rows))

    print("Analyzing validation_sample_size...")
    report.extend(analyze_numeric_field(
        rows, "validation_sample_size", "validation_sample_size",
        extract_fn=lambda m: parse_sample_size(m.get("validation_sample_size"))
    ))

    print("Analyzing samples_training...")
    report.extend(analyze_numeric_field(
        rows, "samples_training", "samples_training",
        extract_fn=lambda m: parse_sample_size(m.get("samples_training"))
    ))

    print("Analyzing ancestry_distribution...")
    report.extend(analyze_ancestry(rows))

    print("Analyzing training_development_cohorts...")
    report.extend(analyze_cohorts(rows))

    print("Analyzing publication...")
    report.extend(analyze_publication(rows))

    print("Analyzing date_release...")
    report.extend(analyze_date_release(rows))

    print("Analyzing variants_number...")
    report.extend(analyze_variants(rows))

    print("Analyzing covariates...")
    report.extend(analyze_covariates(rows))

    print("Analyzing validation ancestry...")
    report.extend(analyze_validation_ancestry(rows))

    print("Analyzing record_count...")
    report.extend(analyze_record_count(rows))

    # Per-disease Spearman analysis
    print("Analyzing per-disease internal Spearman correlations...")
    report.extend(analyze_per_disease_spearman(rows, summary))

    # Cross-field analysis
    print("Analyzing cross-field interactions...")
    report.extend(analyze_cross_field(rows))

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(report), encoding="utf-8")
    print(f"\nReport written to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
