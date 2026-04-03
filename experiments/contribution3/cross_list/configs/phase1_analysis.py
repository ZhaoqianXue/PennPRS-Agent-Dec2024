"""
Phase 1 Diagnostics for Cross-Trait Selection
=============================================
Analyzes binary-input streams only: b2b, b2c.

1.1  PGS Model Specificity        — how many retained target traits does each donor PGS support?
1.2  Cross-Trait Hub Analysis     — how often does each cross trait appear across retained targets?
1.3  Target Cross-Trait Rank Curve — per target trait, how many candidate cross traits exist and
                                     whether there is a clear winner versus a diffuse tail
1.4  Cross-Trait Selection Summary — stream-level diagnostics for shortlist difficulty and hubness
"""

import csv
import statistics
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "runs"
B2B_DIR = BASE / "binary_to_binary"
B2C_DIR = BASE / "binary_to_continuous"
OUTPUT_DIR = BASE.parent / "analysis" / "phase1"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Remove stale outputs so the directory reflects the current binary-input-only,
# cross-trait-selection-oriented Phase 1 scope.
for stale_pattern in ("*_c2b.csv", "*_c2c.csv", "1_3_*.csv", "1_4_*.csv"):
    for stale_path in OUTPUT_DIR.glob(stale_pattern):
        stale_path.unlink()


# ═══════════════════════════════════════════════════════════════════════════════
# Stream configuration — unify column names across binary and continuous streams
# ═══════════════════════════════════════════════════════════════════════════════

STREAM_CONFIG = {
    "b2b": {
        "dir": B2B_DIR,
        "input_id_col": "input_icd",
        "output_col": "output_disease",
        "metric_col": "cross_auc",
        "improvement_col": "auc_improvement",
        "self_metric_col": "self_best_auc",
        "has_self_col": "has_self_auc",
        "summary_n_col": "n_cross_models_beating_self",
        "metric_label": "AUC",
    },
    "b2c": {
        "dir": B2C_DIR,
        "input_id_col": "input_icd",
        "output_col": "output_ontology",
        "metric_col": "cross_auc",
        "improvement_col": "auc_improvement",
        "self_metric_col": "self_best_auc",
        "has_self_col": "has_self_auc",
        "summary_n_col": "n_cross_models_beating_self",
        "metric_label": "AUC",
    },
}


def load_detail(path):
    """Load all detail rows; retained cross-list inputs are filtered via summary."""
    with open(path) as f:
        return list(csv.DictReader(f))


def load_summary_cross_list_inputs(path, n_col):
    """Load retained cross-list inputs with n_cross_models_beating_self > 0."""
    with open(path) as f:
        return [
            r for r in csv.DictReader(f)
            if int(r[n_col]) > 0
        ]


def filter_detail_to_retained_targets(detail_rows, summary_rows, input_id_col):
    """Keep only rows whose target trait appears in retained cross-list summary."""
    retained_ids = {r[input_id_col] for r in summary_rows}
    return [r for r in detail_rows if r[input_id_col] in retained_ids]


def build_summary_map(summary_rows, input_id_col):
    return {r[input_id_col]: r for r in summary_rows}


def _parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def _effective_improvement(row, improvement_col, metric_col, has_self_col):
    """Use the same downstream scoring path for Type A and Type B.

    If self score exists, use the explicit improvement column.
    If self score is missing (Type A), fall back to the cross metric itself.
    """
    raw_improvement = str(row.get(improvement_col, "")).strip()
    if raw_improvement:
        return float(raw_improvement)
    if not _parse_bool(row.get(has_self_col, "")):
        raw_metric = str(row.get(metric_col, "")).strip()
        if raw_metric:
            return float(raw_metric)
    return None


def safe_quantile(values, q):
    """Compute quantile q (0-1) from a sorted-descending list using statistics module."""
    if len(values) < 2:
        return values[0] if values else float("nan")
    # statistics.quantiles needs ascending order and returns cut points
    ascending = sorted(values)
    # Use linear interpolation quantile
    n = len(ascending)
    pos = q * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return ascending[lo] + frac * (ascending[hi] - ascending[lo])


# ─── Load all streams ────────────────────────────────────────────────────────

stream_data = {}  # label -> {"detail": [...], "summary": [...], "cfg": {...}}
for label, cfg in STREAM_CONFIG.items():
    detail_path = cfg["dir"] / "cross_list_detail.csv"
    summary_path = cfg["dir"] / "cross_list_summary.csv"
    if not detail_path.exists() or not summary_path.exists():
        print(f"[WARN] Skipping {label}: files not found at {cfg['dir']}")
        continue
    detail = load_detail(detail_path)
    summary = load_summary_cross_list_inputs(summary_path, cfg["summary_n_col"])
    retained_detail = filter_detail_to_retained_targets(detail, summary, cfg["input_id_col"])
    stream_data[label] = {
        "detail": detail,
        "retained_detail": retained_detail,
        "summary": summary,
        "summary_map": build_summary_map(summary, cfg["input_id_col"]),
        "cfg": cfg,
    }
    print(
        f"Loaded {label} detail: {len(detail)} rows, retained detail: {len(retained_detail)} rows, "
        f"summary: {len(summary)} target traits"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 1.1  PGS Model Specificity
# ═══════════════════════════════════════════════════════════════════════════════

def pgs_specificity(detail_rows, label, input_id_col, output_col):
    """For each PGS, count how many retained target traits it supports."""
    pgs_to_inputs = defaultdict(set)
    for r in detail_rows:
        pgs_id = r["output_pgs_id"]
        input_id = r[input_id_col]
        pgs_to_inputs[pgs_id].add(input_id)

    # Build rows sorted by number of inputs (desc)
    rows = []
    for pgs_id, inputs in pgs_to_inputs.items():
        # Get one example output for this PGS
        example_output = ""
        for r in detail_rows:
            if r["output_pgs_id"] == pgs_id:
                example_output = r.get(output_col, "")[:80]
                break
        rows.append({
            "pgs_id": pgs_id,
            "n_target_traits": len(inputs),
            "target_traits": "; ".join(sorted(inputs)),
            "example_cross_trait": example_output,
            "specificity_score": round(1.0 / len(inputs), 4),
        })
    rows.sort(key=lambda x: x["n_target_traits"], reverse=True)

    if not rows:
        print(f"\n1.1 PGS Model Specificity — {label}: NO DATA")
        return rows

    # Write CSV
    outpath = OUTPUT_DIR / f"1_1_pgs_specificity_{label}.csv"
    with open(outpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    # Print summary
    print(f"\n{'='*70}")
    print(f"1.1 PGS Model Specificity — {label}")
    print(f"{'='*70}")
    print(f"Total unique PGS models: {len(rows)}")

    # Distribution of n_target_traits
    n_dist = Counter(r["n_target_traits"] for r in rows)
    print(f"\nDistribution of n_target_traits:")
    for n in sorted(n_dist.keys(), reverse=True):
        pct = n_dist[n] / len(rows) * 100
        bar = "█" * int(pct / 2)
        print(f"  {n:>3d} targets: {n_dist[n]:>4d} PGS ({pct:5.1f}%) {bar}")

    # Top non-specific PGS
    print(f"\nTop 15 non-specific PGS (support most target traits):")
    print(f"  {'PGS ID':<12s} {'N Targets':>9s}  {'Specificity':>11s}  Example Cross Trait")
    for r in rows[:15]:
        print(f"  {r['pgs_id']:<12s} {r['n_target_traits']:>9d}  {r['specificity_score']:>11.4f}  {r['example_cross_trait'][:50]}")

    return rows


spec_results = {}
for label, sd in stream_data.items():
    cfg = sd["cfg"]
    spec_results[label] = pgs_specificity(
        sd["retained_detail"], label, cfg["input_id_col"], cfg["output_col"]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 1.2  Output Hub Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def output_hub_analysis(detail_rows, label, input_id_col, output_col, metric_col):
    """For each cross trait, count how many retained target traits it serves."""
    output_to_inputs = defaultdict(set)
    output_to_models = defaultdict(set)
    output_to_best_metric = defaultdict(float)

    for r in detail_rows:
        out = r[output_col]
        inp = r[input_id_col]
        output_to_inputs[out].add(inp)
        output_to_models[out].add(r["output_pgs_id"])
        val = float(r[metric_col])
        if val > output_to_best_metric[out]:
            output_to_best_metric[out] = val

    rows = []
    for out, inputs in output_to_inputs.items():
        rows.append({
            "cross_trait": out[:100],
            "n_target_traits_served": len(inputs),
            "n_pgs_models": len(output_to_models[out]),
            "best_cross_metric": round(output_to_best_metric[out], 6),
            "target_traits": "; ".join(sorted(inputs)),
        })
    rows.sort(key=lambda x: x["n_target_traits_served"], reverse=True)

    if not rows:
        print(f"\n1.2 Cross-Trait Hub Analysis — {label}: NO DATA")
        return rows

    outpath = OUTPUT_DIR / f"1_2_output_hub_{label}.csv"
    with open(outpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    print(f"\n{'='*70}")
    print(f"1.2 Cross-Trait Hub Analysis — {label}")
    print(f"{'='*70}")
    print(f"Total unique cross traits: {len(rows)}")

    # Distribution
    n_dist = Counter(r["n_target_traits_served"] for r in rows)
    print(f"\nDistribution of n_target_traits_served:")
    for n in sorted(n_dist.keys(), reverse=True):
        pct = n_dist[n] / len(rows) * 100
        print(f"  serves {n:>3d} targets: {n_dist[n]:>4d} cross traits ({pct:5.1f}%)")

    # Top hubs
    print(f"\nTop 20 hub cross traits (serve most target traits):")
    print(f"  {'Cross Trait':<55s} {'N Targets':>9s} {'N PGS':>6s}")
    for r in rows[:20]:
        print(f"  {r['cross_trait'][:55]:<55s} {r['n_target_traits_served']:>9d} {r['n_pgs_models']:>6d}")

    # Cross traits that serve only 1 target are most specific.
    specific = [r for r in rows if r["n_target_traits_served"] == 1]
    print(f"\nSpecific cross traits (serve only 1 target): {len(specific)}/{len(rows)} ({len(specific)/len(rows)*100:.1f}%)")

    return rows


hub_results = {}
for label, sd in stream_data.items():
    cfg = sd["cfg"]
    hub_results[label] = output_hub_analysis(
        sd["retained_detail"], label, cfg["input_id_col"], cfg["output_col"], cfg["metric_col"]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 1.3  Target Cross-Trait Rank Curve
# ═══════════════════════════════════════════════════════════════════════════════

def classify_selection_profile(n_cross_traits_ge_0025):
    if n_cross_traits_ge_0025 == 0:
        return "weak"
    if n_cross_traits_ge_0025 <= 3:
        return "focused"
    if n_cross_traits_ge_0025 <= 10:
        return "moderate"
    return "diffuse"


def target_cross_trait_rank_curve(detail_rows, summary_rows, summary_map, label, cfg):
    """Aggregate model-level rows into target-cross trait pairs and rank them."""
    input_id_col = cfg["input_id_col"]
    output_col = cfg["output_col"]
    improvement_col = cfg["improvement_col"]
    metric_col = cfg["metric_col"]
    self_metric_col = cfg["self_metric_col"]
    has_self_col = cfg["has_self_col"]
    metric_label = cfg["metric_label"]

    retained_target_ids = {r[input_id_col] for r in summary_rows}
    target_groups = defaultdict(list)
    for row in detail_rows:
        target_groups[row[input_id_col]].append(row)

    rows = []
    for target_id in sorted(retained_target_ids):
        group = target_groups.get(target_id, [])
        pair_rows = defaultdict(list)
        for row in group:
            cross_trait = row.get(output_col, "")
            effective_improvement = _effective_improvement(row, improvement_col, metric_col, has_self_col)
            raw_metric = str(row.get(metric_col, "")).strip()
            if not cross_trait or effective_improvement is None or not raw_metric:
                continue
            pair_rows[cross_trait].append({
                "effective_improvement": effective_improvement,
                "cross_metric": float(raw_metric),
                "pgs_id": row["output_pgs_id"],
            })

        if not pair_rows:
            continue

        ranked_pairs = []
        for cross_trait, stats in pair_rows.items():
            best_entry = max(stats, key=lambda item: (item["effective_improvement"], item["cross_metric"], item["pgs_id"]))
            ranked_pairs.append({
                "cross_trait": cross_trait[:80],
                "best_improvement": best_entry["effective_improvement"],
                "best_cross_metric": best_entry["cross_metric"],
                "n_models": len(stats),
            })

        ranked_pairs.sort(
            key=lambda item: (
                -item["best_improvement"],
                -item["best_cross_metric"],
                item["cross_trait"],
            )
        )

        top1 = ranked_pairs[0]
        top2 = ranked_pairs[1] if len(ranked_pairs) > 1 else None
        top3 = ranked_pairs[2] if len(ranked_pairs) > 2 else None

        n_candidate_cross_traits = len(ranked_pairs)
        n_cross_models = sum(item["n_models"] for item in ranked_pairs)
        n_cross_traits_ge_0025 = sum(1 for item in ranked_pairs if item["best_improvement"] >= 0.025)
        n_cross_traits_ge_0050 = sum(1 for item in ranked_pairs if item["best_improvement"] >= 0.050)
        n_cross_traits_ge_0100 = sum(1 for item in ranked_pairs if item["best_improvement"] >= 0.100)
        gap_top1_top2 = top1["best_improvement"] - top2["best_improvement"] if top2 else ""
        gap_top1_top3 = top1["best_improvement"] - top3["best_improvement"] if top3 else ""
        top5_sum = sum(item["best_improvement"] for item in ranked_pairs[:5])
        top1_share_top5 = (top1["best_improvement"] / top5_sum) if top5_sum > 0 else ""
        summary_row = summary_map.get(target_id, {})

        rows.append({
            "target_id": target_id,
            "target_trait": summary_row.get("input_ontology", group[0].get("input_ontology", ""))[:80],
            "input_type": summary_row.get("input_type", ""),
            "has_self": summary_row.get(has_self_col, group[0].get(has_self_col, "")),
            "self_best_metric": summary_row.get(self_metric_col, group[0].get(self_metric_col, "")),
            "n_cross_models": n_cross_models,
            "n_candidate_cross_traits": n_candidate_cross_traits,
            "n_cross_traits_ge_0025": n_cross_traits_ge_0025,
            "n_cross_traits_ge_0050": n_cross_traits_ge_0050,
            "n_cross_traits_ge_0100": n_cross_traits_ge_0100,
            "selection_profile": classify_selection_profile(n_cross_traits_ge_0025),
            "top1_cross_trait": top1["cross_trait"],
            "top1_improvement": round(top1["best_improvement"], 6),
            "top1_n_models": top1["n_models"],
            "top2_cross_trait": top2["cross_trait"] if top2 else "",
            "top2_improvement": round(top2["best_improvement"], 6) if top2 else "",
            "top3_cross_trait": top3["cross_trait"] if top3 else "",
            "top3_improvement": round(top3["best_improvement"], 6) if top3 else "",
            "gap_top1_top2": round(gap_top1_top2, 6) if gap_top1_top2 != "" else "",
            "gap_top1_top3": round(gap_top1_top3, 6) if gap_top1_top3 != "" else "",
            "top1_share_top5": round(top1_share_top5, 4) if top1_share_top5 != "" else "",
        })

    rows.sort(key=lambda row: (-row["n_cross_traits_ge_0025"], -row["top1_improvement"], row["target_id"]))

    if not rows:
        print(f"\n1.3 {metric_label} Target Cross-Trait Rank Curve — {label}: NO DATA")
        return rows

    outpath = OUTPUT_DIR / f"1_3_target_cross_trait_rank_curve_{label}.csv"
    with open(outpath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*70}")
    print(f"1.3 {metric_label} Target Cross-Trait Rank Curve — {label}")
    print(f"{'='*70}")
    print(f"\n{'ID':<10s} {'Target Trait':<32s} {'N_pair':>6s} {'N>=.025':>8s} {'Top1':>7s} {'Gap12':>7s} {'Profile':<9s} Top Cross Trait")
    print(f"{'-'*10} {'-'*32} {'-'*6} {'-'*8} {'-'*7} {'-'*7} {'-'*9} {'-'*30}")
    for row in rows:
        gap12 = f"{row['gap_top1_top2']:.4f}" if row["gap_top1_top2"] != "" else "N/A"
        print(
            f"{row['target_id']:<10s} {row['target_trait'][:32]:<32s} "
            f"{row['n_candidate_cross_traits']:>6d} {row['n_cross_traits_ge_0025']:>8d} "
            f"{row['top1_improvement']:>7.4f} {gap12:>7s} {row['selection_profile']:<9s} "
            f"{row['top1_cross_trait'][:30]}"
        )

    profile_counts = Counter(row["selection_profile"] for row in rows)
    print(f"\nSelection profile counts:")
    for profile in ["focused", "moderate", "diffuse", "weak"]:
        print(f"  {profile:<8s}: {profile_counts.get(profile, 0)}")

    return rows


rank_results = {}
for label, sd in stream_data.items():
    rank_results[label] = target_cross_trait_rank_curve(
        sd["retained_detail"], sd["summary"], sd["summary_map"], label, sd["cfg"]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 1.4  Cross-Trait Selection Summary
# ═══════════════════════════════════════════════════════════════════════════════

def cross_trait_selection_summary(all_rank_results, all_hub_results):
    """Summarize how difficult cross-trait shortlisting will be in each stream."""
    print(f"\n{'='*70}")
    print("1.4 Cross-Trait Selection Summary across Binary-Input Streams")
    print(f"{'='*70}")

    summary_rows = []

    for label, rows in all_rank_results.items():
        if not rows:
            continue

        hub_rows = all_hub_results.get(label, [])
        all_top1 = [row["top1_improvement"] for row in rows]
        all_candidate = [row["n_candidate_cross_traits"] for row in rows]
        all_actionable = [row["n_cross_traits_ge_0025"] for row in rows]
        all_gap12 = [row["gap_top1_top2"] for row in rows if row["gap_top1_top2"] != ""]
        all_top1_share = [row["top1_share_top5"] for row in rows if row["top1_share_top5"] != ""]
        all_targets_per_cross_trait = [row["n_target_traits_served"] for row in hub_rows]

        n_targets = len(rows)
        n_cross_traits = len(hub_rows)
        mean_top1 = statistics.mean(all_top1)
        median_top1 = statistics.median(all_top1)
        mean_candidate = statistics.mean(all_candidate)
        median_candidate = statistics.median(all_candidate)
        mean_actionable = statistics.mean(all_actionable)
        median_actionable = statistics.median(all_actionable)
        pct_clear_gap_0010 = sum(1 for gap in all_gap12 if float(gap) >= 0.010) / n_targets * 100
        pct_clear_gap_0025 = sum(1 for gap in all_gap12 if float(gap) >= 0.025) / n_targets * 100
        pct_focused = sum(1 for row in rows if row["selection_profile"] == "focused") / n_targets * 100
        pct_diffuse = sum(1 for row in rows if row["selection_profile"] == "diffuse") / n_targets * 100
        mean_targets_per_cross_trait = statistics.mean(all_targets_per_cross_trait) if all_targets_per_cross_trait else 0
        median_targets_per_cross_trait = statistics.median(all_targets_per_cross_trait) if all_targets_per_cross_trait else 0
        pct_specific_cross_traits = (
            sum(1 for row in hub_rows if row["n_target_traits_served"] == 1) / n_cross_traits * 100
            if n_cross_traits else 0
        )
        pct_hub_cross_traits = (
            sum(1 for row in hub_rows if row["n_target_traits_served"] >= 5) / n_cross_traits * 100
            if n_cross_traits else 0
        )
        mean_top1_share = statistics.mean(all_top1_share) if all_top1_share else 0

        print(f"\n--- {label}: {n_targets} retained target traits ---")
        print(f"  Candidate cross traits per target: mean={mean_candidate:.1f}, median={median_candidate:.1f}")
        print(f"  Actionable cross traits (improvement >= 0.025): mean={mean_actionable:.1f}, median={median_actionable:.1f}")
        print(f"  Top-1 improvement: mean={mean_top1:.4f}, median={median_top1:.4f}")
        print(f"  Clear top-1 gap >= 0.010: {pct_clear_gap_0010:.1f}% of targets")
        print(f"  Clear top-1 gap >= 0.025: {pct_clear_gap_0025:.1f}% of targets")
        print(f"  Selection profile mix: focused={pct_focused:.1f}%, diffuse={pct_diffuse:.1f}%")
        print(f"  Cross-trait hubness: mean targets/cross trait={mean_targets_per_cross_trait:.1f}, median={median_targets_per_cross_trait:.1f}")
        print(f"  Specific cross traits (serve 1 target): {pct_specific_cross_traits:.1f}%")
        print(f"  Hub cross traits (serve >=5 targets): {pct_hub_cross_traits:.1f}%")

        summary_rows.append({
            "stream": label,
            "n_retained_targets": n_targets,
            "n_unique_cross_traits": n_cross_traits,
            "mean_candidate_cross_traits_per_target": round(mean_candidate, 2),
            "median_candidate_cross_traits_per_target": round(median_candidate, 2),
            "mean_actionable_cross_traits_per_target": round(mean_actionable, 2),
            "median_actionable_cross_traits_per_target": round(median_actionable, 2),
            "mean_top1_improvement": round(mean_top1, 6),
            "median_top1_improvement": round(median_top1, 6),
            "pct_targets_clear_gap_ge_0010": round(pct_clear_gap_0010, 1),
            "pct_targets_clear_gap_ge_0025": round(pct_clear_gap_0025, 1),
            "pct_targets_focused": round(pct_focused, 1),
            "pct_targets_diffuse": round(pct_diffuse, 1),
            "mean_targets_per_cross_trait": round(mean_targets_per_cross_trait, 2),
            "median_targets_per_cross_trait": round(median_targets_per_cross_trait, 2),
            "pct_cross_traits_specific_1_target": round(pct_specific_cross_traits, 1),
            "pct_cross_traits_hub_ge_5_targets": round(pct_hub_cross_traits, 1),
            "mean_top1_share_top5": round(mean_top1_share, 4),
        })

    if summary_rows:
        outpath = OUTPUT_DIR / "1_4_cross_trait_selection_summary.csv"
        with open(outpath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nCross-trait selection summary saved to: {outpath}")

    return summary_rows


selection_summary = cross_trait_selection_summary(rank_results, hub_results)


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-stream comparison: shared retained target traits in b2b and b2c
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n{'='*70}")
print("Cross-Stream Comparison: Shared retained target traits in b2b and b2c")
print(f"{'='*70}")

b2b_rank = rank_results.get("b2b", [])
b2c_rank = rank_results.get("b2c", [])

b2b_ids = {row["target_id"] for row in b2b_rank}
b2c_ids = {row["target_id"] for row in b2c_rank}
both = b2b_ids & b2c_ids
b2b_only = b2b_ids - b2c_ids
b2c_only = b2c_ids - b2b_ids

print(f"In both b2b and b2c: {len(both)} — {sorted(both)}")
print(f"b2b only:            {len(b2b_only)} — {sorted(b2b_only)}")
print(f"b2c only:            {len(b2c_only)} — {sorted(b2c_only)}")

if both:
    b2b_map = {row["target_id"]: row for row in b2b_rank}
    b2c_map = {row["target_id"]: row for row in b2c_rank}
    print(f"\n{'ID':<10s} {'Target Trait':<28s} | {'b2b top1':<22s} {'N>=.025':>7s} | {'b2c top1':<22s} {'N>=.025':>7s}")
    for target_id in sorted(both):
        b2b_row = b2b_map[target_id]
        b2c_row = b2c_map[target_id]
        print(
            f"{target_id:<10s} {b2b_row['target_trait'][:28]:<28s} | "
            f"{b2b_row['top1_cross_trait'][:22]:<22s} {b2b_row['n_cross_traits_ge_0025']:>7d} | "
            f"{b2c_row['top1_cross_trait'][:22]:<22s} {b2c_row['n_cross_traits_ge_0025']:>7d}"
        )

print(f"\n{'='*70}")
print(f"Phase 1 analysis complete. Output files in: {OUTPUT_DIR}")
print(f"{'='*70}")
