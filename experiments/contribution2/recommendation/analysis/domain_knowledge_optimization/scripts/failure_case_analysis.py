#!/usr/bin/env python3
"""
Sub-task 2: Failure Case Analysis for Domain Knowledge Optimization.

For each of the 19 diseases where Catalog Search + Domain Knowledge got all Hit@1..5 = No,
performs field-by-field comparison between the agent's selection and the benchmark top models,
extracts agent rationale, classifies error patterns, and produces general domain knowledge
recommendations.

Output: failure_case_analysis_report.md
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
RUN_DIR = BASE / "runs" / "with-domain-gpt-5.2-t10__75disease__updated-domain-knowledge-20260318"
SUMMARY_JSON = RUN_DIR / "experiment_with_domain_summary.json"
RESULTS_JSON = RUN_DIR / "experiment_with_domain_results.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_MD = OUTPUT_DIR / "failure_case_analysis_report.md"

# The 24 Agent Input fields for comparison
COMPARISON_FIELDS = [
    "id",
    "trait_reported",
    "trait_efo",
    "phenotyping_reported",
    "method_name",
    "variants_number",
    "ancestry_distribution",
    "publication.title",
    "publication.journal",
    "date_release",
    "samples_training",
    "training_development_cohorts",
    "validation_sample_size",
    "covariates",
    "performance_metrics.auc",
    "performance_metrics.r2",
    "performance_metrics.full_model_auc",
    "performance_metrics.full_model_r2",
    "performance_metrics.incremental_auc",
    "performance_metrics.selected_validation_ancestry",
    "performance_metrics.record_count",
    "performance_metrics.classification_metrics",
    "performance_metrics.other_metrics",
    "performance_metrics.effect_sizes",
]

# Error type definitions
ERROR_TYPES = [
    "Over-weighted method_name",
    "Confused by inflated/full-model AUC",
    "Exact-label trap",
    "Framework score preferred",
    "Validation size bias",
    "Endpoint mismatch not detected",
    "Missing metrics penalized too harshly",
    "Study family not recognized",
    "Variant count misinterpretation",
    "Covariate comparability ignored",
    "Reported performance mismatch",
    "Publication/recency bias",
]


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


def severity_tier(norm_rank: float) -> str:
    if norm_rank >= 0.75:
        return "Egregious"
    elif norm_rank >= 0.50:
        return "Severe"
    else:
        return "Near-miss"


def classify_errors(
    disease_data: dict,
    agent_model: dict,
    top_models: list[dict],
    rationales: list[str],
) -> list[str]:
    """Heuristic classification of what went wrong."""
    errors = []
    agent_pm = agent_model.get("performance_metrics", {})
    top_pm = top_models[0].get("performance_metrics", {}) if top_models else {}

    # --- Method name bias ---
    agent_method = (agent_model.get("method_name") or "").lower()
    top_methods = [(m.get("method_name") or "").lower() for m in top_models]
    method_mentioned = any("method" in r.lower() or agent_method in r.lower() for r in rationales)
    if method_mentioned and agent_method != top_methods[0] if top_methods else False:
        errors.append("Over-weighted method_name")

    # --- Full-model AUC inflation ---
    agent_full_auc = agent_pm.get("full_model_auc")
    agent_pgs_auc = agent_pm.get("auc") or agent_pm.get("pgs_only_auc")
    top_full_auc = top_pm.get("full_model_auc")
    if agent_full_auc and not agent_pgs_auc:
        # Agent's model only has full_model AUC (potentially inflated)
        if top_models and any(m.get("performance_metrics", {}).get("auc") for m in top_models):
            errors.append("Confused by inflated/full-model AUC")

    # --- Exact label trap ---
    ontology = disease_data["ontology"].lower()
    agent_trait = (agent_model.get("trait_efo") or "").lower()
    top_trait = (top_models[0].get("trait_efo") or "").lower() if top_models else ""
    if ontology in agent_trait and ontology not in top_trait:
        errors.append("Exact-label trap")

    # --- Framework score preferred ---
    framework_patterns = [
        r"813\s*trait", r"245\s*polygenic", r"exprs", r"global\s*biobank",
        r"portability", r"across\s*biobanks", r"pan-.*trait", r"phenome-wide",
    ]
    agent_title = (agent_model.get("publication", {}).get("title") or "").lower()
    is_agent_framework = any(re.search(pat, agent_title) for pat in framework_patterns)
    if is_agent_framework:
        errors.append("Framework score preferred")

    # --- Validation size bias ---
    val_mentioned = any("sample" in r.lower() or "validation" in r.lower() for r in rationales)
    agent_val = agent_model.get("validation_sample_size", "")
    if val_mentioned and agent_val:
        errors.append("Validation size bias")

    # --- Endpoint mismatch ---
    agent_pheno = (agent_model.get("phenotyping_reported") or "").lower()
    top_pheno = (top_models[0].get("phenotyping_reported") or "").lower() if top_models else ""
    if agent_pheno != top_pheno and ("time" in top_pheno or "incident" in top_pheno or "tte" in top_pheno):
        errors.append("Endpoint mismatch not detected")

    # --- Missing metrics penalized ---
    top_has_auc = any(m.get("performance_metrics", {}).get("auc") for m in top_models)
    top_has_es = any(m.get("performance_metrics", {}).get("effect_sizes") for m in top_models)
    if not top_has_auc and top_has_es:
        if agent_pm.get("auc") or agent_pm.get("full_model_auc"):
            errors.append("Missing metrics penalized too harshly")

    # --- Variant count misinterpretation ---
    agent_vars = agent_model.get("variants_number") or 0
    top_vars = top_models[0].get("variants_number") or 0 if top_models else 0
    variant_mentioned = any("variant" in r.lower() for r in rationales)
    if variant_mentioned and abs(agent_vars - top_vars) > 500000:
        errors.append("Variant count misinterpretation")

    # --- Covariate comparability ---
    agent_cov = (agent_model.get("covariates") or "").lower()
    top_cov = (top_models[0].get("covariates") or "").lower() if top_models else ""
    heavy_kw = ["family", "apoe", "charge", "egfr", "tsh", "bmi", "blood pressure", "cholesterol"]
    agent_heavy = any(kw in agent_cov for kw in heavy_kw)
    top_heavy = any(kw in top_cov for kw in heavy_kw)
    if agent_heavy and not top_heavy:
        errors.append("Covariate comparability ignored")

    # --- Publication/recency bias ---
    recency_mentioned = any("recent" in r.lower() or "newer" in r.lower() or "latest" in r.lower() for r in rationales)
    if recency_mentioned:
        errors.append("Publication/recency bias")

    # --- Study family not recognized ---
    agent_cohorts = set(c.lower() for c in (agent_model.get("training_development_cohorts") or []))
    top_cohorts_lists = [set(c.lower() for c in (m.get("training_development_cohorts") or [])) for m in top_models]
    if top_cohorts_lists and len(top_cohorts_lists) >= 2:
        shared = top_cohorts_lists[0]
        for tc in top_cohorts_lists[1:]:
            shared = shared & tc
        if shared and not (shared & agent_cohorts):
            errors.append("Study family not recognized")

    # --- Reported performance mismatch ---
    # If agent's reported metrics look better than top model's reported metrics
    # but benchmark says otherwise
    agent_rep = agent_pm.get("full_model_auc") or agent_pm.get("auc") or 0
    top_rep = top_pm.get("full_model_auc") or top_pm.get("auc") or 0
    if agent_rep > top_rep and agent_rep > 0:
        errors.append("Reported performance mismatch")

    if not errors:
        errors.append("Complex / multi-factor")

    return errors


# ---------------------------------------------------------------------------
# Build per-disease deep-dive
# ---------------------------------------------------------------------------

def build_disease_section(
    dd: dict,
    model_map: dict[str, dict],
    trial_rationales: list[dict],
) -> tuple[list[str], list[str]]:
    """Returns (lines, error_types) for one disease."""
    ontology = dd["ontology"]
    M = dd["n_models"]
    ranked = dd["benchmark_ranked_ids"]
    auc_map = dd["benchmark_auc_by_id"]
    modal = dd["modal_recommendation"]
    modal_count = dd["modal_recommendation_count"]
    rank = ranked.index(modal) + 1 if modal in ranked else None
    norm_rank = rank / M if rank else None

    # Get top-5 benchmark models
    top5_ids = ranked[:min(5, len(ranked))]
    top5_models = [model_map[pid] for pid in top5_ids if pid in model_map]

    # Get agent's selected model
    agent_model = model_map.get(modal, {})

    # Collect all trial recommendations for this disease
    disease_trials = [t for t in trial_rationales if t["ontology"] == ontology]
    rationales = [t.get("rationale", "") for t in disease_trials]
    trial_recs = Counter(t.get("recommended_pgs_id") for t in disease_trials)

    # Classify errors
    errors = classify_errors(dd, agent_model, top5_models, rationales)

    tier = severity_tier(norm_rank) if norm_rank else "Unknown"

    lines = []
    lines.append(f"### {ontology}")
    lines.append("")
    lines.append(f"**Severity**: {tier} | **N Models**: {M} | "
                 f"**Selected**: {modal} (rank {rank}/{M}, norm={norm_rank:.2f}) | "
                 f"**Modal count**: {modal_count}/10")
    lines.append("")

    # Trial recommendation distribution
    lines.append("**Trial recommendations:**")
    for pid, cnt in trial_recs.most_common():
        pid_rank = ranked.index(pid) + 1 if pid in ranked else "?"
        lines.append(f"- {pid} (rank {pid_rank}/{M}): {cnt}/10 trials")
    lines.append("")

    # Field-by-field comparison table
    # Columns: Field | Agent's Pick | Benchmark #1 | Benchmark #2 | ... (up to #3)
    n_bench = min(3, len(top5_models))
    header_parts = ["Field", f"Agent: {modal} (rank {rank})"]
    for i, bm in enumerate(top5_models[:n_bench]):
        bm_rank = ranked.index(bm["id"]) + 1 if bm["id"] in ranked else "?"
        header_parts.append(f"Bench #{i+1}: {bm['id']} (rank {bm_rank})")
    header_parts.append("AoU benchmark AUC")

    lines.append("**Field-by-field comparison:**")
    lines.append("")
    lines.append(f"| {' | '.join(header_parts)} |")
    lines.append(f"| {' | '.join(['---'] * len(header_parts))} |")

    for field in COMPARISON_FIELDS:
        row = [field.replace("performance_metrics.", "pm.")]
        # Agent's value
        agent_val = get_field(agent_model, field)
        row.append(fmt_value(agent_val))
        # Benchmark values
        for bm in top5_models[:n_bench]:
            bm_val = get_field(bm, field)
            row.append(fmt_value(bm_val))
        # AoU benchmark AUC for agent vs benchmarks
        if field == "id":
            agent_auc = auc_map.get(modal, 0)
            row.append(f"Agent: {agent_auc:.4f}")
            for bm in top5_models[:n_bench]:
                pass  # already in header
        else:
            row.append("")
        lines.append(f"| {' | '.join(row)} |")

    # Add AoU benchmark AUC row
    auc_row = ["**AoU benchmark AUC**", fmt_value(auc_map.get(modal))]
    for bm in top5_models[:n_bench]:
        auc_row.append(fmt_value(auc_map.get(bm["id"])))
    auc_row.append("")
    lines.append(f"| {' | '.join(auc_row)} |")

    lines.append("")

    # Agent rationale (first trial, truncated)
    if rationales:
        lines.append("**Agent rationale (trial 1):**")
        lines.append("")
        # Wrap long rationale
        rat = rationales[0][:2000]
        lines.append(f"> {rat}")
        lines.append("")

    # Error classification
    lines.append(f"**Diagnosed error patterns**: {', '.join(errors)}")
    lines.append("")

    # Expert analysis: what should the agent have noticed?
    lines.append("**What the agent should have noticed:**")
    lines.append("")
    if top5_models and agent_model:
        # Compare key differentiators
        top1 = top5_models[0]
        diffs = []
        # Method
        if agent_model.get("method_name") != top1.get("method_name"):
            diffs.append(f"- Benchmark #1 uses **{top1.get('method_name')}** vs agent's **{agent_model.get('method_name')}**")
        # Variants
        av = agent_model.get("variants_number", 0) or 0
        tv = top1.get("variants_number", 0) or 0
        if av != tv:
            diffs.append(f"- Variants: agent={av:,} vs benchmark #1={tv:,}")
        # Training cohorts
        ac = agent_model.get("training_development_cohorts") or []
        tc = top1.get("training_development_cohorts") or []
        if set(ac) != set(tc):
            diffs.append(f"- Training cohorts: agent={ac} vs benchmark #1={tc}")
        # Publication
        ap = agent_model.get("publication", {}).get("title", "")[:80]
        tp = top1.get("publication", {}).get("title", "")[:80]
        if ap != tp:
            diffs.append(f"- Publication: agent=\"{ap}...\" vs benchmark #1=\"{tp}...\"")
        # AUC comparison
        agent_auc_val = auc_map.get(modal, 0)
        top_auc_val = auc_map.get(top1["id"], 0)
        if agent_auc_val and top_auc_val:
            diffs.append(f"- AoU benchmark AUC: agent={agent_auc_val:.4f} vs benchmark #1={top_auc_val:.4f} "
                        f"(gap={top_auc_val - agent_auc_val:.4f})")
        for d in diffs:
            lines.append(d)
    lines.append("")
    lines.append("---")
    lines.append("")

    return lines, errors


# ---------------------------------------------------------------------------
# Aggregated analysis
# ---------------------------------------------------------------------------

def build_aggregated_analysis(all_errors: dict[str, list[str]]) -> list[str]:
    """Aggregate error patterns across all failure diseases."""
    lines = ["## Aggregated General Failure Pattern Analysis", ""]

    # Count patterns
    pattern_diseases = defaultdict(list)
    for ont, errors in all_errors.items():
        for err in errors:
            pattern_diseases[err].append(ont)

    lines.append("| Failure Pattern | Disease Count | Example Diseases |")
    lines.append("|-----------------|--------------|------------------|")
    for pattern, diseases in sorted(pattern_diseases.items(), key=lambda x: -len(x[1])):
        examples = ", ".join(diseases[:4])
        if len(diseases) > 4:
            examples += f" (+{len(diseases)-4} more)"
        lines.append(f"| {pattern} | {len(diseases)} | {examples} |")
    lines.append("")

    # General recommendations per pattern
    lines.append("## Prioritized General Domain Knowledge Recommendations")
    lines.append("")
    lines.append("Each recommendation is **disease-agnostic** — applicable across all ontologies.")
    lines.append("")

    recs = [
        (
            "Reported performance mismatch",
            "Strengthen rule: reported AUC (especially full-model) is NOT a reliable proxy for real-world performance",
            "Field-Level Policies > performance_metrics.auc",
            "Add explicit rule: When all candidates for a disease have only full_model_auc (no PGS-only AUC), "
            "the agent should NOT use reported AUC as a primary differentiator. Instead, fall back to "
            "method_name quality, variant count, training cohort diversity, and study design. "
            "Full-model AUC differences of <0.05 between candidates from the same study are noise, not signal.",
        ),
        (
            "Over-weighted method_name",
            "Adjust method hierarchy based on actual benchmark data",
            "Field-Level Policies > method_name",
            "Update method tiers: PRSmixPlus and PRSmix are top-tier (mean rank ~0.14-0.19). "
            "PRS-CSx outperforms PRS-CS. LDpred2 with cross-validation (LDpred2.CV) outperforms default LDpred2. "
            "The agent should not pick a model solely because its method sounds sophisticated — "
            "method is a WEAK tiebreak, not a primary signal. When two models differ only in method, "
            "prefer the one with more variants and multi-cohort training over method prestige.",
        ),
        (
            "Validation size bias",
            "Down-weight validation sample size as a selection criterion",
            "Field-Level Policies > validation_sample_size",
            "Validation sample size has near-zero correlation (rho=0.13) with benchmark performance. "
            "The agent should treat it as a very weak tiebreak only. A model with n=50K validation "
            "is NOT inherently better than one with n=5K. Never select a model primarily because "
            "it has the largest validation sample.",
        ),
        (
            "Variant count misinterpretation",
            "Add clear guidance on variant count interpretation by method",
            "Field-Level Policies > variants_number",
            "Higher variant counts correlate with better performance (rho=-0.27). "
            "For shrinkage methods (PRS-CS, LDpred2, PRS-CSx): >1M variants is a positive signal. "
            "For the SAME method, prefer the model with MORE variants (e.g., PRS-CSx 1.27M > PRS-CS 383K). "
            "However, variant count must be interpreted in context of method — "
            "a GWAS-hits model with 50 variants is not comparable to a genome-wide shrinkage model with 1M.",
        ),
        (
            "Confused by inflated/full-model AUC",
            "Explicitly warn about full-model AUC inflation from covariates",
            "Field-Level Policies > performance_metrics.auc / covariates",
            "When a model reports only full_model_auc (not PGS-only AUC), the reported AUC includes "
            "contribution from covariates (age, sex, PCs, etc.), which inflates the apparent performance. "
            "Two models from the same study with full_model_auc of 0.70 vs 0.71 are essentially equivalent. "
            "The agent should NEVER prefer one candidate over another solely based on a small full_model_auc difference. "
            "Instead, look for structural differences: method, variant count, GWAS power, training cohorts.",
        ),
        (
            "Study family not recognized",
            "Add rule to identify model families from the same publication",
            "Global Rules",
            "When multiple candidates come from the SAME publication, they form a 'study family'. "
            "Within a family, the agent should identify the best variant (e.g., MTAG vs non-MTAG, "
            "multi-ancestry vs single-ancestry, PRS-CSx vs PRS-CS from same GWAS). "
            "Across families, the agent should compare the best representative from each family "
            "rather than mixing within-family and between-family comparisons.",
        ),
        (
            "Framework score preferred",
            "Strengthen penalty for pan-trait framework models",
            "Field-Level Policies > publication.title / training_development_cohorts",
            "Pan-trait framework models (snpnet UKB 813 traits, ExPRSweb, Global Biobank Meta-analysis) "
            "have mean norm_rank ~0.59 — significantly worse than disease-focused models (~0.49). "
            "The agent should apply a consistent penalty: framework models should only be selected "
            "when no disease-focused alternative exists or when the framework model uses a clearly "
            "superior method (e.g., PRSmixPlus aggregating disease-focused components).",
        ),
        (
            "Exact-label trap",
            "Trait label match should not override structural quality signals",
            "Field-Level Policies > trait_reported",
            "Exact trait_efo match (mean rank 0.49) is only marginally better than partial match (0.54). "
            "An exact label match does NOT guarantee better real-world performance. "
            "The agent should not select a model with an exact label match over a structurally "
            "superior model (better method, more variants, multi-cohort) that has a slight label mismatch.",
        ),
    ]

    for pattern, title, section, detail in recs:
        if pattern in pattern_diseases:
            n = len(pattern_diseases[pattern])
            lines.append(f"### {n}. {title}")
            lines.append("")
            lines.append(f"**Addresses pattern**: {pattern} ({n} diseases)")
            lines.append(f"**Target section**: `{section}`")
            lines.append("")
            lines.append(detail)
            lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Enhancement 4: Precise error classification
# ---------------------------------------------------------------------------

def precise_error_classification(summary, results):
    lines = ["## Precise Error Classification", ""]
    lines.append("Re-classified with precise heuristics. Each error type requires specific evidence.")
    lines.append("")

    failures = []
    for dd in summary["per_disease"]:
        hits = dd.get("modal_recommendation_hit_at_k", {})
        all_no = all(not hits.get(str(k), True) for k in range(1, 6))
        if all_no:
            failures.append(dd)

    trial_by_disease = defaultdict(list)
    for t in results:
        trial_by_disease[t["ontology"]].append(t)

    all_errors = defaultdict(list)
    disease_errors = {}

    for dd in failures:
        ont = dd["ontology"]
        M = dd["n_models"]
        ranked = dd["benchmark_ranked_ids"]
        auc_map = dd["benchmark_auc_by_id"]
        modal = dd["modal_recommendation"]
        modal_rank = ranked.index(modal) + 1 if modal in ranked else None

        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent_model = model_map.get(modal, {})
        top5 = [model_map[pid] for pid in ranked[:5] if pid in model_map]
        top1 = top5[0] if top5 else {}

        trials = trial_by_disease[ont]
        rationales = [t.get("rationale", "") for t in trials]
        combined_rationale = " ".join(rationales).lower()

        errors_with_evidence = []
        agent_pm = agent_model.get("performance_metrics", {})
        top1_pm = top1.get("performance_metrics", {}) if top1 else {}

        # 1. MTAG penalty
        agent_trait = (agent_model.get("trait_reported") or "").lower()
        top1_trait = (top1.get("trait_reported") or "").lower()
        if "mtag" in top1_trait and "mtag" not in agent_trait:
            if "mtag" in combined_rationale:
                errors_with_evidence.append(
                    ("MTAG penalty",
                     f"Agent avoided MTAG model {top1.get('id')}. "
                     f"Top-1 uses MTAG ({top1_trait}), agent picked non-MTAG ({agent_trait}). "
                     f"Rationale mentions MTAG."))

        # 2. Full-model AUC inflation trap
        agent_full_auc = agent_pm.get("full_model_auc")
        top1_full_auc = top1_pm.get("full_model_auc")
        agent_pgs_auc = agent_pm.get("auc")
        if (agent_full_auc and not agent_pgs_auc and
            agent_full_auc > (top1_full_auc or 0)):
            agent_bm_auc = auc_map.get(modal, 0)
            top1_bm_auc = auc_map.get(top1.get("id"), 0)
            if agent_bm_auc < top1_bm_auc:
                top1_auc_str = f"{top1_full_auc:.3f}" if top1_full_auc else "N/A"
                errors_with_evidence.append(
                    ("Full-model AUC inflation",
                     f"Agent's {modal} reported full_model_auc={agent_full_auc:.3f} > "
                     f"top-1's {top1_auc_str}, "
                     f"but benchmark AUC {agent_bm_auc:.4f} < {top1_bm_auc:.4f}. "
                     f"Reported AUC was misleading."))

        # 3. Risk calculator covariate
        agent_cov = (agent_model.get("covariates") or "").lower()
        calc_kw = ["charge-af", "charge af", "risk calculator", "framingham"]
        if any(kw in agent_cov for kw in calc_kw):
            errors_with_evidence.append(
                ("Risk-calculator covariate not penalized enough",
                 f"Agent selected model with covariates including clinical risk calculator: "
                 f"'{agent_model.get('covariates')}'"))

        # 4. Variant count gap
        agent_vars = agent_model.get("variants_number") or 0
        top1_vars = top1.get("variants_number") or 0
        if top1_vars > 0 and agent_vars > 0:
            ratio = top1_vars / agent_vars
            if ratio > 5:
                errors_with_evidence.append(
                    ("Variant count ignored (>5x gap)",
                     f"Agent={agent_vars:,} variants vs top-1={top1_vars:,} ({ratio:.0f}x more). "
                     f"Agent picked a much sparser model."))
            elif ratio > 1.3 and top1_vars > 500000:
                errors_with_evidence.append(
                    ("Variant count under-weighted",
                     f"Agent={agent_vars:,} vs top-1={top1_vars:,} ({ratio:.1f}x). "
                     f"Both use shrinkage methods but top-1 has more variants."))

        # 5. Validation size drove decision
        agent_val = parse_sample_size(agent_model.get("validation_sample_size"))
        top1_val = parse_sample_size(top1.get("validation_sample_size"))
        if agent_val and top1_val and agent_val > top1_val * 2:
            if "validation" in combined_rationale or "sample" in combined_rationale:
                val_patterns = [
                    r"large[r]?\s+(?:validation|evaluation|sample)",
                    r"validation.*n=\d",
                    r"n=[\d,]+.*support",
                    r"well-powered",
                ]
                if any(re.search(pat, combined_rationale) for pat in val_patterns):
                    errors_with_evidence.append(
                        ("Validation size drove decision",
                         f"Agent's validation n={agent_val:,} >> top-1's n={top1_val:,}. "
                         f"Rationale explicitly cites validation size as justification."))

        # 6. Framework score selected over disease-focused
        framework_patterns = [
            r"813\s*trait", r"245\s*polygenic", r"exprs", r"global\s*biobank",
            r"portability", r"across\s*biobanks", r"pan-.*trait", r"phenome-wide",
        ]
        agent_title = (agent_model.get("publication", {}).get("title") or "").lower()
        top1_title = (top1.get("publication", {}).get("title") or "").lower()
        agent_is_framework = any(re.search(pat, agent_title) for pat in framework_patterns)
        top1_is_framework = any(re.search(pat, top1_title) for pat in framework_patterns)
        if agent_is_framework and not top1_is_framework:
            errors_with_evidence.append(
                ("Framework score selected over disease-focused",
                 f"Agent picked framework model ('{agent_model.get('publication', {}).get('title', '')[:80]}') "
                 f"over disease-focused top-1 ('{top1.get('publication', {}).get('title', '')[:80]}')"))

        # 7. Disease-focused narrative over-valued
        if not agent_is_framework and not top1_is_framework:
            if "disease-focused" in combined_rationale or "disease focused" in combined_rationale:
                if agent_vars < top1_vars * 0.5 and modal_rank and modal_rank > M * 0.5:
                    errors_with_evidence.append(
                        ("Disease-focused narrative over-valued",
                         f"Agent justified selection with 'disease-focused' framing but "
                         f"picked structurally weaker model (rank {modal_rank}/{M}). "
                         f"Agent variants={agent_vars:,} vs top-1={top1_vars:,}."))

        # 8. Within-family wrong sibling
        agent_pub = agent_model.get("publication", {}).get("title", "")
        top1_pub = top1.get("publication", {}).get("title", "")
        if agent_pub == top1_pub and agent_pub:
            errors_with_evidence.append(
                ("Within-family wrong sibling",
                 f"Agent and top-1 share same publication '{agent_pub[:80]}' "
                 f"but agent picked wrong sibling. Agent={modal} (rank {modal_rank}), "
                 f"top-1={top1.get('id')} (rank 1)."))

        # 9. Record count over-valued
        agent_rc = agent_pm.get("record_count", 0) or 0
        top1_rc = top1_pm.get("record_count", 0) or 0
        if agent_rc > top1_rc * 3 and "record" in combined_rationale:
            errors_with_evidence.append(
                ("Record count over-valued",
                 f"Agent's record_count={agent_rc} >> top-1's {top1_rc}. "
                 f"Rationale mentions record count."))

        # 10. Multi-cohort training over-valued
        agent_cohorts = agent_model.get("training_development_cohorts") or []
        top1_cohorts = top1.get("training_development_cohorts") or []
        if len(agent_cohorts) > len(top1_cohorts) * 2 and len(agent_cohorts) > 5:
            if "cohort" in combined_rationale or "multi-cohort" in combined_rationale:
                errors_with_evidence.append(
                    ("Multi-cohort training over-valued",
                     f"Agent's {len(agent_cohorts)} cohorts >> top-1's {len(top1_cohorts)}. "
                     f"More cohorts doesn't guarantee better benchmark performance."))

        if not errors_with_evidence:
            errors_with_evidence.append(("Unclassified / complex", "No single dominant error identified."))

        disease_errors[ont] = errors_with_evidence
        for err_type, _ in errors_with_evidence:
            all_errors[err_type].append(ont)

    # Output table
    lines.append("### Precise Error Pattern Summary")
    lines.append("")
    lines.append("| Error Pattern | N Diseases | Diseases |")
    lines.append("|---------------|-----------|----------|")
    for err_type, diseases in sorted(all_errors.items(), key=lambda x: -len(x[1])):
        d_str = ", ".join(diseases[:4])
        if len(diseases) > 4:
            d_str += f" (+{len(diseases)-4})"
        lines.append(f"| {err_type} | {len(diseases)} | {d_str} |")
    lines.append("")

    # Per-disease detailed errors
    lines.append("### Per-Disease Error Details")
    lines.append("")
    for dd in failures:
        ont = dd["ontology"]
        modal = dd["modal_recommendation"]
        ranked = dd["benchmark_ranked_ids"]
        modal_rank = ranked.index(modal) + 1 if modal in ranked else None
        M = dd["n_models"]
        lines.append(f"**{ont}** (selected {modal}, rank {modal_rank}/{M}):")
        for err_type, evidence in disease_errors[ont]:
            lines.append(f"- *{err_type}*: {evidence}")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Enhancement 5: Domain knowledge rule → failure mapping
# ---------------------------------------------------------------------------

def analyze_dk_rule_mapping(summary, results):
    lines = ["## Domain Knowledge Rule → Failure Mapping", ""]
    lines.append("Extracts which domain knowledge rules/concepts the agent cited in its rationale")
    lines.append("for the 19 failure diseases, and whether those rules **helped** or **misled** the agent.")
    lines.append("")

    rule_patterns = [
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
        ("metric availability", r"no.*auroc|no.*auc|missing.*metric|absent.*metric"),
        ("MTAG caution", r"mtag"),
        ("multi-cohort preference", r"multi.cohort|multi.biobank|consortium"),
        ("record count", r"record.count|validation.*record"),
        ("variant count", r"variant|snp count"),
        ("recency", r"recent|newer|latest|date"),
        ("BMI mediator", r"bmi.*mediator|bmi.*covariate"),
        ("risk calculator/wrapper", r"risk.calculator|risk.wrapper|deployment.packag"),
    ]

    failures = []
    for dd in summary["per_disease"]:
        hits = dd.get("modal_recommendation_hit_at_k", {})
        all_no = all(not hits.get(str(k), True) for k in range(1, 6))
        if all_no:
            failures.append(dd)

    trial_by_disease = defaultdict(list)
    for t in results:
        trial_by_disease[t["ontology"]].append(t)

    rule_cite_count = Counter()
    rule_disease_map = defaultdict(list)

    for dd in failures:
        ont = dd["ontology"]
        trials = trial_by_disease[ont]
        combined = " ".join(t.get("rationale", "") for t in trials).lower()

        for rule_name, pattern in rule_patterns:
            if re.search(pattern, combined):
                rule_cite_count[rule_name] += 1
                rule_disease_map[rule_name].append(ont)

    lines.append("### Rules Most Frequently Cited in Failure Rationales")
    lines.append("")
    lines.append("| Domain Knowledge Rule/Concept | Cited in N/19 Failures | Example Diseases | Likely Role |")
    lines.append("|-------------------------------|----------------------|------------------|-------------|")

    likely_misleading = {
        "validation size", "disease-focused preference", "covariate comparability",
        "full-model AUC caution", "CHARGE-AF penalty", "MTAG caution",
        "record count", "multi-cohort preference", "recency",
    }
    likely_helpful = {"framework penalty", "endpoint fidelity", "risk calculator/wrapper"}

    for rule_name, count in rule_cite_count.most_common():
        diseases = rule_disease_map[rule_name][:3]
        d_str = ", ".join(diseases)
        if count > 3:
            d_str += "..."
        role = "Likely MISLEADING" if rule_name in likely_misleading else (
            "Likely helpful" if rule_name in likely_helpful else "Mixed / context-dependent")
        lines.append(f"| {rule_name} | {count} | {d_str} | {role} |")

    lines.append("")

    # Analysis of specific problematic rules
    lines.append("### Rules That Systematically Misled the Agent")
    lines.append("")

    misleading_analysis = [
        ("validation size",
         "The agent frequently cited large validation N as justification for selecting "
         "worse-performing models. Per meta-analysis, validation_sample_size has rho=0.13 "
         "with benchmark performance — essentially noise. The current domain knowledge says "
         "'validation_sample_size is a strong tie-break field' (line 259) which gives the agent "
         "too much weight on this signal."),
        ("disease-focused preference",
         "The agent correctly follows the domain knowledge rule preferring disease-focused models, "
         "but over-applies it. In knee OA, the agent picked a 24-variant GWAS-hits model from a "
         "disease-focused multi-cohort study over a 952K-variant megaprs model because the latter "
         "came from a 'framework for estimating country-specific cumulative incidence'. The domain "
         "knowledge should clarify that 'disease-focused' means the endpoint is disease-relevant, "
         "not that the publication title must be disease-specific."),
        ("covariate comparability",
         "The agent correctly identified covariate issues (e.g., CHARGE-AF, BMI) but sometimes "
         "used covariate concerns to over-penalize the best model. In atrial fibrillation, the "
         "agent recognized CHARGE-AF as problematic in PGS005168's covariates but STILL selected "
         "it, suggesting the rule wasn't strong enough. Meanwhile in other cases the agent used "
         "minor covariate differences as an excuse to reject better models."),
        ("MTAG caution",
         "In dilated cardiomyopathy, the agent explicitly rejected MTAG models (which are actually "
         "benchmark top-3) saying it preferred 'clean generic DCM endpoint without MTAG labeling'. "
         "The domain knowledge does not contain an anti-MTAG rule, but the agent inferred one from "
         "the general 'endpoint fidelity' guidance. MTAG is a legitimate multi-trait analysis method "
         "that often improves power — the domain knowledge should explicitly state MTAG is not a "
         "negative signal."),
        ("full-model AUC caution",
         "The domain knowledge correctly warns about full-model AUC inflation. However, when ALL "
         "candidates for a disease have only full-model AUC (like dilated cardiomyopathy), the "
         "agent cannot use this field to differentiate. The agent then falls back to other signals "
         "(validation size, publication narrative) which are worse predictors. The domain knowledge "
         "should provide explicit fallback guidance for this scenario."),
    ]

    for rule_name, analysis in misleading_analysis:
        if rule_name in rule_cite_count:
            lines.append(f"**{rule_name}** (cited in {rule_cite_count[rule_name]}/19 failures):")
            lines.append("")
            lines.append(analysis)
            lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Enhancement 6: Deep root cause for top 5 egregious failures
# ---------------------------------------------------------------------------

def deep_root_cause_analysis(summary, results):
    lines = ["## Deep Root Cause Analysis — Top 5 Egregious Failures", ""]
    lines.append("For the 5 worst failures, traces the exact chain of reasoning that led to the wrong selection.")
    lines.append("")

    failures = []
    for dd in summary["per_disease"]:
        hits = dd.get("modal_recommendation_hit_at_k", {})
        all_no = all(not hits.get(str(k), True) for k in range(1, 6))
        if all_no:
            modal = dd["modal_recommendation"]
            ranked = dd["benchmark_ranked_ids"]
            M = dd["n_models"]
            rank = ranked.index(modal) + 1 if modal in ranked else None
            failures.append((rank / M if rank else 0, dd))

    failures.sort(key=lambda x: -x[0])
    top5 = failures[:5]

    trial_by_disease = defaultdict(list)
    for t in results:
        trial_by_disease[t["ontology"]].append(t)

    for norm_rank, dd in top5:
        ont = dd["ontology"]
        M = dd["n_models"]
        ranked = dd["benchmark_ranked_ids"]
        auc_map = dd["benchmark_auc_by_id"]
        modal = dd["modal_recommendation"]
        modal_rank = ranked.index(modal) + 1 if modal in ranked else None

        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}
        agent_model = model_map.get(modal, {})
        top1 = model_map.get(ranked[0], {})

        trials = trial_by_disease[ont]

        lines.append(f"### {ont} — rank {modal_rank}/{M} (norm={norm_rank:.2f})")
        lines.append("")

        # Core comparison
        lines.append("**Agent's choice vs Benchmark #1 — Key differentiators:**")
        lines.append("")

        key_fields = [
            ("Method", "method_name"),
            ("Variants", "variants_number"),
            ("Trait reported", "trait_reported"),
            ("Phenotyping", "phenotyping_reported"),
            ("Training cohorts", "training_development_cohorts"),
            ("Validation N", "validation_sample_size"),
            ("Covariates", "covariates"),
            ("Full-model AUC", "performance_metrics.full_model_auc"),
            ("Full-model R²", "performance_metrics.full_model_r2"),
            ("Effect sizes", "performance_metrics.effect_sizes"),
            ("Publication", "publication.title"),
            ("Date", "date_release"),
        ]

        lines.append("| Field | Agent's pick | Benchmark #1 | Favors |")
        lines.append("|-------|-------------|-------------|--------|")

        for label, path in key_fields:
            av = get_field(agent_model, path)
            tv = get_field(top1, path)

            favors = "—"
            if path == "variants_number" and av and tv:
                favors = "Agent" if av > tv else ("Bench" if tv > av else "Tie")
            elif path in ("performance_metrics.full_model_auc", "performance_metrics.full_model_r2") and av and tv:
                favors = "Agent" if av > tv else ("Bench" if tv > av else "Tie")
            elif path == "validation_sample_size":
                av_n = parse_sample_size(str(av)) if av else None
                tv_n = parse_sample_size(str(tv)) if tv else None
                if av_n and tv_n:
                    favors = "Agent" if av_n > tv_n else ("Bench" if tv_n > av_n else "Tie")
            elif path == "performance_metrics.effect_sizes":
                av_max = max((e.get("estimate", 0) for e in (av or []) if e.get("name_short") in ("OR", "HR")), default=0)
                tv_max = max((e.get("estimate", 0) for e in (tv or []) if e.get("name_short") in ("OR", "HR")), default=0)
                if av_max and tv_max:
                    favors = "Agent" if av_max > tv_max else ("Bench" if tv_max > av_max else "Tie")

            # Format values
            if isinstance(av, list) and av and isinstance(av[0], dict):
                av_str = "; ".join(f"{e.get('name_short')}={e.get('estimate')}" for e in av)
            elif isinstance(av, list):
                av_str = ", ".join(str(x) for x in av)[:80]
            elif isinstance(av, float):
                av_str = f"{av:.4f}"
            elif isinstance(av, int):
                av_str = f"{av:,}"
            else:
                av_str = str(av)[:80] if av else "—"

            if isinstance(tv, list) and tv and isinstance(tv[0], dict):
                tv_str = "; ".join(f"{e.get('name_short')}={e.get('estimate')}" for e in tv)
            elif isinstance(tv, list):
                tv_str = ", ".join(str(x) for x in tv)[:80]
            elif isinstance(tv, float):
                tv_str = f"{tv:.4f}"
            elif isinstance(tv, int):
                tv_str = f"{tv:,}"
            else:
                tv_str = str(tv)[:80] if tv else "—"

            lines.append(f"| {label} | {av_str} | {tv_str} | {favors} |")

        # Benchmark AUC
        agent_bm = auc_map.get(modal, 0)
        top1_bm = auc_map.get(ranked[0], 0)
        lines.append(f"| **AoU Benchmark AUC** | **{agent_bm:.4f}** | **{top1_bm:.4f}** | **Bench (gap={top1_bm-agent_bm:.4f})** |")
        lines.append("")

        # Reasoning chain extraction
        rationale = trials[0].get("rationale", "") if trials else ""
        lines.append("**Agent's reasoning chain (trial 1):**")
        lines.append("")

        sentences = [s.strip() for s in re.split(r'[.;]', rationale) if s.strip()]
        lines.append("| Step | Agent's reasoning | Correct? |")
        lines.append("|------|------------------|----------|")
        for i, sent in enumerate(sentences[:10], 1):
            sent_lower = sent.lower()
            correct = "?"
            if "validation" in sent_lower and "large" in sent_lower:
                correct = "MISLEADING — validation N doesn't predict benchmark rank"
            elif "disease-focused" in sent_lower and modal_rank and modal_rank > M * 0.5:
                correct = "MISLEADING — narrative focus doesn't equal structural quality"
            elif "full-model" in sent_lower or "full_model" in sent_lower:
                correct = "CAUTION — full-model AUC not reliable for cross-model comparison"
            elif "mtag" in sent_lower:
                correct = "MISLEADING — MTAG is not a negative signal"
            elif "charge-af" in sent_lower:
                correct = "CORRECT — CHARGE-AF is a comparability concern"
            elif "endpoint" in sent_lower:
                correct = "Partially correct — endpoint matters but not decisive alone"
            elif "variant" in sent_lower:
                if agent_model.get("variants_number", 0) < top1.get("variants_number", 0) * 0.5:
                    correct = "MISSED — should have favored more variants"
            lines.append(f"| {i} | {sent[:150]}{'...' if len(sent)>150 else ''} | {correct} |")
        lines.append("")

        # Root cause summary
        lines.append("**Root cause summary:**")
        lines.append("")

        causes = []
        agent_vars = agent_model.get("variants_number") or 0
        top1_vars = top1.get("variants_number") or 0
        if top1_vars > agent_vars * 1.3 and top1_vars > 100000:
            causes.append(f"Agent ignored that top-1 has {top1_vars:,} variants vs agent's {agent_vars:,} — "
                         f"a {top1_vars/max(agent_vars,1):.0f}x difference favoring top-1.")

        agent_cohorts = agent_model.get("training_development_cohorts") or []
        top1_cohorts = top1.get("training_development_cohorts") or []
        if len(top1_cohorts) > len(agent_cohorts) and len(top1_cohorts) >= 2:
            causes.append(f"Top-1 trained on {len(top1_cohorts)} cohorts ({', '.join(top1_cohorts[:5])}) "
                         f"vs agent's {len(agent_cohorts)} ({', '.join(agent_cohorts[:5])}).")

        if "mtag" in (top1.get("trait_reported") or "").lower() and "mtag" not in (agent_model.get("trait_reported") or "").lower():
            causes.append("Agent penalized MTAG labeling in top-1, treating it as endpoint ambiguity. "
                         "MTAG is a legitimate power-boosting technique, not an endpoint concern.")

        agent_full_auc = agent_model.get("performance_metrics", {}).get("full_model_auc")
        top1_full_auc = top1.get("performance_metrics", {}).get("full_model_auc")
        if agent_full_auc and top1_full_auc and agent_full_auc > top1_full_auc:
            causes.append(f"Agent was attracted by higher reported full-model AUC ({agent_full_auc:.3f} vs "
                         f"{top1_full_auc:.3f}), but this didn't translate to better benchmark performance.")

        agent_val = parse_sample_size(agent_model.get("validation_sample_size"))
        top1_val = parse_sample_size(top1.get("validation_sample_size"))
        if agent_val and top1_val and agent_val > top1_val * 2:
            causes.append(f"Agent over-weighted validation size (n={agent_val:,} vs n={top1_val:,}). "
                         f"Validation N has near-zero predictive value (rho=0.13).")

        agent_cov = (agent_model.get("covariates") or "").lower()
        if any(kw in agent_cov for kw in ["charge-af", "bmi", "family"]):
            causes.append(f"Agent's selected model has problematic covariates: '{agent_model.get('covariates')}'")

        if not causes:
            causes.append("Complex multi-factor failure — no single dominant cause identified.")

        for c in causes:
            lines.append(f"- {c}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading data...")
    with open(SUMMARY_JSON) as f:
        summary = json.load(f)
    with open(RESULTS_JSON) as f:
        results = json.load(f)

    # Build model lookup per disease
    all_errors = {}
    report = []
    report.append("# Failure Case Analysis Report")
    report.append("")
    report.append("Deep-dive analysis of 19 diseases where the Catalog Search + Domain Knowledge arm")
    report.append("failed to select any model within the AoU benchmark top-5 (all Hit@1..5 = No).")
    report.append("")
    report.append("Goal: identify **general** (disease-agnostic) failure patterns to improve domain knowledge.")
    report.append("")

    # Identify failure diseases
    failures = []
    for dd in summary["per_disease"]:
        hits = dd.get("modal_recommendation_hit_at_k", {})
        all_no = all(not hits.get(str(k), True) for k in range(1, 6))
        if all_no:
            modal = dd["modal_recommendation"]
            ranked = dd["benchmark_ranked_ids"]
            M = dd["n_models"]
            rank = ranked.index(modal) + 1 if modal in ranked else None
            norm_rank = rank / M if rank else 0
            failures.append((norm_rank, dd))

    # Sort by severity (worst first)
    failures.sort(key=lambda x: -x[0])

    # Executive summary
    report.append("## Executive Summary")
    report.append("")
    report.append(f"**Total failure diseases**: {len(failures)}/75")
    report.append("")
    report.append("| Severity | Disease | N Models | Selected Model | Rank | Norm Rank |")
    report.append("|----------|---------|----------|---------------|------|-----------|")
    for norm_rank, dd in failures:
        tier = severity_tier(norm_rank)
        modal = dd["modal_recommendation"]
        M = dd["n_models"]
        ranked = dd["benchmark_ranked_ids"]
        rank = ranked.index(modal) + 1 if modal in ranked else "?"
        report.append(f"| {tier} | {dd['ontology']} | {M} | {modal} | {rank}/{M} | {norm_rank:.2f} |")
    report.append("")

    # Per-disease deep dives
    report.append("## Per-Disease Deep Dives")
    report.append("")

    for norm_rank, dd in failures:
        ontology = dd["ontology"]
        print(f"Analyzing {ontology}...")

        # Build model map for this disease
        model_map = {m["id"]: m for m in dd["candidate_models_visible_to_llm"]}

        # Get trial rationales
        disease_trials = [t for t in results if t["ontology"] == ontology]

        section_lines, errors = build_disease_section(dd, model_map, disease_trials)
        report.extend(section_lines)
        all_errors[ontology] = errors

    # Aggregated analysis
    print("Building aggregated analysis...")
    report.extend(build_aggregated_analysis(all_errors))

    # Enhancement 4: Precise error classification
    print("Precise error classification...")
    report.extend(precise_error_classification(summary, results))

    # Enhancement 5: Domain knowledge rule mapping
    print("Domain knowledge rule mapping...")
    report.extend(analyze_dk_rule_mapping(summary, results))

    # Enhancement 6: Deep root cause analysis
    print("Deep root cause analysis (top 5 egregious)...")
    report.extend(deep_root_cause_analysis(summary, results))

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(report), encoding="utf-8")
    print(f"\nReport written to {OUTPUT_MD}")
    print(f"Total lines: {len(report)}")


if __name__ == "__main__":
    main()
