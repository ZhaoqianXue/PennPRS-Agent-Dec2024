"""
Within-trait PRS model selection — three-arm comparison on the EFO-clean
44-disease benchmark. Produces the within-figure SUITE.

Canonical current arm definitions live in:
  experiments/contribution2/recommendation/docs/within_formal_three_arm_definitions_20260615.md

Current formal display names:
  PRS Agent .................................. retained double-stage PRS Agent
  General LLM ................................ prompt-only/no-skill/single-stage fullpool arm
  PGS Report ................................. deterministic PGS Catalog reported-performance/report baseline

Replaces (renamed from) plot_82disease_baseline_vs_prs_agent.py: contaminated
82-disease / gpt-5.2 / catalog-CSV data is gone; data now comes straight from the
saved runs/baselines (no catalog CSVs).

Figures (figures_44disease_efoclean/):
  fig0_ablation ....... (a) 2×2 harness×skill Hit@1 matrix, (b) 8-section LORO bars
  fig1_overall ........ (a) Agent-vs-General-LLM selected-AUC scatter,
                        (b) Agent-vs-PGS-Report selected-AUC scatter
                        (window 0.50-0.75 drops testicular + the <0.50 lows; grey =
                         identical pick AUC only; labels colour-coded by category)
  fig2_hitk ........... (a) Hit@1..5 selection accuracy (3 methods),
                        (b) overall mean selected-model AUC per method (one number each)
  fig3_landscape ...... single panel: per-disease rank (x) + pool size (line extent),
                        three methods by marker shape and colour (all 44)
  fig4_delta_waterfall  per-disease ΔAUC (Agent − General LLM), sorted
  fig5_micro_case_studies  2×4 model-landscape panels for eight hand-picked diseases

Run: /Users/zhaoqianxue/anaconda3/bin/python \
       experiments/contribution2/presentation/scripts/plot_44disease_three_method_comparison.py
  optional: --model-tag gpt-5.2 (point at the gpt-5.2 runs once collected)
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from textwrap import fill

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[4]
RUNS = PROJECT_ROOT / "experiments/contribution2/recommendation/runs"
BENCHMARK_CSV = (
    PROJECT_ROOT / "experiments/contribution2/disease_selection/efo_rebuild"
    / "selected_diseases_efoclean__44disease.csv"
)

AGENT_LABEL = "PRS Agent"
GENERAL_LLM_LABEL = "General LLM"
CATALOG_LABEL = "PGS Report"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
mpl.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 1.2,
    "xtick.major.width": 1.1, "ytick.major.width": 1.1, "xtick.major.size": 4, "ytick.major.size": 4,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "legend.frameon": False,
})
COLORS = {
    "baseline": "#777777", "catalog": "#B7652A", "agent": "#011F5B", "agent_light": "#6E8BBE",
    "gain": "#2A9D8F", "loss": "#B65A5C", "neutral": "#C8CDD2", "grid": "#E6E9ED",
    "text": "#111111", "muted": "#6D737A",
}
M = {"agent": (COLORS["agent"], "o", AGENT_LABEL),
     "baseline": (COLORS["baseline"], "s", GENERAL_LLM_LABEL),
     "catalog": (COLORS["catalog"], "^", CATALOG_LABEL)}

MICRO_CASES = [
    "coronary artery disease",
    "atrial fibrillation",
    "asthma",
    "rheumatoid arthritis",
    "obesity",
    "ankylosing spondylitis",
    "angina pectoris",
    "abdominal aortic aneurysm",
]

CATEGORY_KEYWORDS = {
    "Cancer": ["carcinoma", "cancer", "melanoma", "lymphoma", "leukemia", "myeloma", "neoplasm"],
    "Cardiometabolic": ["coronary", "artery", "hypertens", "atrial", "heart", "diabet", "obesity",
                        "cholesterol", "angina", "cardiomyopathy", "aneurysm", "embolism", "varicose", "cholelith"],
    "Immune/endocrine": ["arthritis", "lupus", "psoriasis", "thyroid", "spondylitis", "sclerosis",
                         "celiac", "graves", "hypothyroid"],
    "Neurologic/psychiatric": ["alzheimer", "dementia", "parkinson", "depress", "schizo", "sclerosis"],
    "Respiratory": ["asthma", "pulmonary", "obstructive"],
    "Renal/urologic": ["kidney", "renal", "bladder", "prostate", "ovarian", "cervical", "testicular"],
}


def category_for_disease(name: str) -> str:
    n = name.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in n for k in kws):
            return cat
    return "Other"


def title_case(name: str) -> str:
    return " ".join(w.capitalize() if w.islower() else w for w in name.split())


def _delta_tier(delta: float) -> str:
    """Classify Agent − comparator ΔAUC; identical only when exactly zero."""
    if delta == 0:
        return "identical"
    return "higher" if delta > 0 else "lower"


def _icd_by_ontology() -> dict[str, str]:
    df = pd.read_csv(BENCHMARK_CSV)
    return {str(row.Ontology).lower(): str(row.ICD) for row in df.itertuples()}


def _micro_case_title(ontology: str, icd_map: dict[str, str]) -> str:
    label = title_case(ontology)
    icd = icd_map.get(ontology.lower())
    return f"{label} ({icd})" if icd else label


# ---------------------------------------------------------------------------
def _runs(model_tag: str):
    agent = next(RUNS.glob(f"topk-holistic-rerank-batch-{model_tag}-t1__44disease__efoclean44-skillv2*")) \
        if model_tag == "gpt-5.4" else next(RUNS.glob(f"topk-holistic-rerank-batch-{model_tag}-t1__44disease__efoclean44-gpt52*"))
    llm = next(RUNS.glob(f"without-domain-{model_tag}-t1__44disease__efoclean44*"))
    return agent, llm


def load_df(model_tag: str):
    agent_dir, llm_dir = _runs(model_tag)
    ag = json.loads((agent_dir / "experiment_topk_holistic_rerank_batch_summary.json").read_text())
    ll = json.loads((llm_dir / "experiment_without_domain_summary.json").read_text())
    agpd = {d["ontology"]: d for d in ag["per_disease"]}
    llpd = {d["ontology"]: d for d in ll["per_disease"]}
    rows = []
    for ont, d in agpd.items():
        auc = d.get("benchmark_auc_by_id", {})
        ap, lp = d.get("modal_recommendation"), llpd.get(ont, {}).get("modal_recommendation")
        bp = (d.get("baseline") or {}).get("pgs_id")
        rows.append({
            "disease": ont, "model_count": d["n_models"], "category": category_for_disease(ont),
            "disease_label": title_case(ont),
            "agent_selected_auc": auc.get(ap), "baseline_selected_auc": auc.get(lp),
            "catalog_selected_auc": auc.get(bp),
            "agent_rank": d.get("modal_recommendation_rank"),
            "baseline_rank": llpd.get(ont, {}).get("modal_recommendation_rank"),
            "catalog_rank": (d.get("baseline") or {}).get("rank"),
        })
    df = pd.DataFrame(rows)
    df["delta_auc"] = df["agent_selected_auc"] - df["baseline_selected_auc"]
    def hitk(s, base=False):
        src = (s.get("baseline") or {}).get("hit_at_k") if base else s.get("trial_hit_at_k")
        return {int(k): src[k]["accuracy"] for k in ["1", "2", "3", "4", "5"]}
    curves = {"agent": hitk(ag), "baseline": hitk(ll), "catalog": hitk(ll, base=True)}
    # Hit@K accuracy as raw counts (all three methods).
    N = ag["modal_hit_at_k"]["1"]["eligible"]
    cat_hit = (ag.get("baseline") or {}).get("hit_at_k", {})
    hit_counts = {"agent": {k: ag["modal_hit_at_k"][str(k)]["hits"] for k in (1, 2, 3, 4, 5)},
                  "baseline": {k: ll["modal_hit_at_k"][str(k)]["hits"] for k in (1, 2, 3, 4, 5)},
                  "catalog": {k: cat_hit.get(str(k), {}).get("hits") for k in (1, 2, 3, 4, 5)}}
    # overall mean selected-model AUC per method, over all N diseases (K-independent: each
    # method makes one pick, so this is a single number per method — shown as fig2 panel b).
    mean_auc = {"agent": float(df["agent_selected_auc"].mean()),
                "baseline": float(df["baseline_selected_auc"].mean()),
                "catalog": float(df["catalog_selected_auc"].mean())}
    extras = {"N": N, "hit_counts": hit_counts, "mean_auc": mean_auc}
    return df, curves, extras


def save(fig, out_dir, stem):
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"{stem}.{ext}", dpi=400, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def panel_label(ax, lab, x=-0.1, y=1.03):
    ax.text(x, y, lab, transform=ax.transAxes, fontsize=18, fontweight="bold", va="bottom")


# ---------------------------------------------------------------------------
# fig1 — overall: two selected-AUC scatters (a: vs General LLM, b: vs PGS Report)
#                 + Hit@K accuracy (c) + Hit@K mean AUC (d), both PRS Agent vs Baseline
# ---------------------------------------------------------------------------
SCATTER_WINDOW = (0.50, 0.75)   # drop the lone high outlier (testicular 0.92) and <0.50 lows
SCATTER_ANCHORS = ["ankylosing spondylitis", "multiple sclerosis", "gout"]  # always-labelled high-AUC points
MAX_HIGHER_LABELS = 8           # moderate density on the agent-higher side; all lower points are labelled


def _place_labels(ax, d, other_col, diseases):
    """Direct-label `diseases` in black, with a white halo so points/leaders never bleed
    through the text, and short category-coloured leaders (green = Agent higher, red =
    Agent lower) that start at the text edge so nothing overlaps anything else.
    """
    sub = d[d["disease"].isin(diseases)]
    if sub.empty:
        return

    def cat_color(row):
        dd = row["agent_selected_auc"] - row[other_col]
        tier = _delta_tier(dd)
        return COLORS["gain"] if tier == "higher" else COLORS["loss"] if tier == "lower" else "#555555"

    halo = [pe.withStroke(linewidth=2.4, foreground="white")]
    anchors, texts = [], []
    for _, r in sub.iterrows():
        above = r["agent_selected_auc"] >= r[other_col]
        anchors.append((r[other_col], r["agent_selected_auc"], cat_color(r)))
        texts.append(ax.text(r[other_col] + (-0.010 if above else 0.010),
                             r["agent_selected_auc"] + (0.010 if above else -0.010),
                             fill(title_case(r["disease"]), 14), fontsize=6.9, ha="center",
                             va="center", color=COLORS["text"], zorder=6, path_effects=halo))
    adjust_text(texts, ax=ax, x=d[other_col].to_numpy(), y=d["agent_selected_auc"].to_numpy(),
                force_text=(1.1, 1.4), force_static=(0.6, 0.8), force_pull=(0.002, 0.002),
                expand=(1.7, 2.1), max_move=(70, 70), ensure_inside_axes=True)
    # leaders behind the markers. annotate shrink convention: shrinkA = tail (text) end,
    # shrinkB = head (point) end. shrinkB=0 reaches the marker exactly; shrinkA keeps the
    # tail clear of the label so the line never cuts through the text.
    for t, (px, py, col) in zip(texts, anchors):
        ax.annotate("", xy=(px, py), xytext=t.get_position(),
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.8, alpha=0.95,
                                    shrinkA=8, shrinkB=0), zorder=2)


def _scatter_panel(ax, df, other_col, other_label, panel_lab):
    lo, hi = SCATTER_WINDOW
    ax.grid(True, color=COLORS["grid"], lw=0.8); ax.set_axisbelow(True)
    d = df.dropna(subset=[other_col, "agent_selected_auc"]).copy()
    d = d[d[other_col].between(lo, hi) & d["agent_selected_auc"].between(lo, hi)].copy()
    delta = d["agent_selected_auc"] - d[other_col]
    specs = [(delta > 0, COLORS["gain"], "PRS Agent higher"),
             (delta == 0, COLORS["neutral"], "Identical pick"),
             (delta < 0, COLORS["loss"], "PRS Agent lower")]
    for mask, color, _ in specs:
        g = d.loc[mask]
        ax.scatter(g[other_col], g["agent_selected_auc"], s=72, color=color,
                   edgecolor="white", linewidth=0.7, alpha=0.96, zorder=3)
    ax.plot([lo, hi], [lo, hi], ls=(0, (5, 4)), color="black", lw=1.6, zorder=2)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"{other_label} selected-model AUC", fontsize=12.5, fontweight="bold")
    ax.set_ylabel(f"{AGENT_LABEL} selected-model AUC", fontsize=12.5, fontweight="bold")
    ax.tick_params(labelsize=11); panel_label(ax, panel_lab, -0.14, 1.02)
    # label the top-|ΔAUC| agent-higher movers + ALL agent-lower points + in-window anchors
    higher = d.loc[delta > 0]
    top_high = set(higher.assign(absd=(higher["agent_selected_auc"] - higher[other_col]).abs())
                   .sort_values("absd", ascending=False).head(MAX_HIGHER_LABELS)["disease"])
    to_label = top_high | set(d.loc[delta < 0, "disease"]) | (set(SCATTER_ANCHORS) & set(d["disease"]))
    _place_labels(ax, d, other_col, to_label)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor=c, markeredgecolor="white",
                              markersize=8, label=f"{l} (n={int(m.sum())})") for m, c, l in specs],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=9.2)


def _band3_panel(ax, ks, series, labels, ylabel, title, panel_lab, ylim, leg_loc):
    """Three-method (Agent / General LLM / PGS Report) line panel with direct value labels.

    `series` and `labels` are dicts keyed agent/baseline/catalog. Per-K labels are placed
    top/middle/right/bottom to avoid overlap; the hero (Agent) line is drawn heaviest.
    """
    cols = {k: M[k][0] for k in ("agent", "baseline", "catalog")}
    style = {"agent": (3.2, 9.0), "baseline": (2.4, 7.0), "catalog": (2.4, 7.0)}  # emphasise the hero line
    for key in ("catalog", "baseline", "agent"):           # agent drawn last (on top)
        lw, ms = style[key]
        ax.plot(ks, series[key], color=cols[key], marker="o", ms=ms, lw=lw, zorder=3,
                markeredgecolor="white", markeredgewidth=0.7)
    for i, k in enumerate(ks):
        ranked = sorted(("agent", "baseline", "catalog"), key=lambda key: series[key][i], reverse=True)
        slots = {ranked[0]: (0, 11, "center"), ranked[1]: (9, 0, "left"), ranked[2]: (0, -16, "center")}
        for key in ("agent", "baseline", "catalog"):
            dx, dy, ha = slots[key]
            ax.annotate(labels[key][i], (k, series[key][i]), textcoords="offset points", xytext=(dx, dy),
                        ha=ha, va="center", fontsize=9.0, color=cols[key], zorder=7,
                        fontweight="bold" if key == "agent" else "normal",
                        path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    ax.set_xticks(ks); ax.set_xticklabels([f"Hit@{k}" for k in ks]); ax.set_xlim(0.55, 5.7)
    ax.set_ylabel(ylabel, fontsize=12.5, fontweight="bold"); ax.set_ylim(*ylim)
    ax.grid(True, axis="y", color=COLORS["grid"], lw=0.9); ax.set_axisbelow(True); ax.tick_params(labelsize=11.5)
    ax.set_title(title, fontsize=13, fontweight="bold"); panel_label(ax, panel_lab, -0.13, 1.03)
    # legend with the hero (PRS Agent) listed first, matching the line stacking
    handles = [Line2D([0], [0], color=cols[k], marker="o", lw=2.6, ms=7.5,
                      markeredgecolor="white", markeredgewidth=0.7, label=M[k][2])
               for k in ("agent", "baseline", "catalog")]
    ax.legend(handles=handles, loc=leg_loc, fontsize=9.5)


def fig1_overall(df, extras, out_dir, model_tag):
    """Figure 1 — the two selected-AUC scatters (Agent vs General LLM; Agent vs PGS Report)."""
    N = extras["N"]
    fig, axes = plt.subplots(1, 2, figsize=(14.4, 7.6))
    _scatter_panel(axes[0], df, "baseline_selected_auc", GENERAL_LLM_LABEL, "a")
    _scatter_panel(axes[1], df, "catalog_selected_auc", CATALOG_LABEL, "b")
    fig.suptitle(f"PRS Agent selects higher-AUC PRS models than the baselines across {N} diseases ({model_tag})",
                 fontsize=15.5, fontweight="bold", y=1.0)
    fig.subplots_adjust(wspace=0.30, top=0.90, bottom=0.16)
    save(fig, out_dir, "fig1_overall_44disease")


def _mean_auc_panel(ax, means, N, panel_lab):
    """Overall mean selected-model AUC per method (one number each; not a function of K).

    NOTE: the y-axis is truncated at 0.55 (per request) rather than the principled chance
    baseline 0.5, so bar heights visually exaggerate the (small) differences — fine for
    slides, but add a broken-axis mark or use a dot plot if this goes into a paper.
    """
    keys = ["agent", "baseline", "catalog"]
    xs = np.arange(3)
    base = 0.55
    halo = [pe.withStroke(linewidth=2.6, foreground="white")]
    for x, k in zip(xs, keys):
        ax.bar(x, means[k] - base, bottom=base, width=0.64, color=M[k][0],
               edgecolor="white", linewidth=0.8, zorder=3)
        ax.annotate(f"{means[k]:.3f}", (x, means[k]), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=12, fontweight="bold" if k == "agent" else "normal",
                    color=M[k][0], zorder=7, path_effects=halo)
    ax.set_xticks(xs)
    ax.set_xticklabels(["PRS Agent", "General LLM", "PGS Report"], fontsize=10.5)
    ax.set_xlim(-0.6, 2.6); ax.set_ylim(base, 0.595)
    ax.set_ylabel("Mean selected-model AUC", fontsize=12.5, fontweight="bold")
    ax.grid(True, axis="y", color=COLORS["grid"], lw=0.9); ax.set_axisbelow(True); ax.tick_params(labelsize=11)
    ax.set_title(f"Mean selected-model AUC (N={N})", fontsize=13, fontweight="bold")
    panel_label(ax, panel_lab, -0.13, 1.03)


def fig2_hitk(curves, extras, out_dir, model_tag):
    """Figure 2 — (a) Hit@K selection accuracy and (b) overall mean selected-model AUC."""
    N = extras["N"]; ks = [1, 2, 3, 4, 5]; hc = extras["hit_counts"]
    keys = ("agent", "baseline", "catalog")
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.4))
    _band3_panel(axes[0], ks, {key: [curves[key][k] for k in ks] for key in keys},
                 {key: [f"{hc[key][k]}/{N}" for k in ks] for key in keys},
                 "Selection accuracy", f"Hit@K accuracy (N={N})", "a", (0.0, 0.8), "upper left")
    _mean_auc_panel(axes[1], extras["mean_auc"], N, "b")
    fig.suptitle(f"PRS Agent leads on both selection accuracy and selected-model AUC ({model_tag})",
                 fontsize=15.5, fontweight="bold", y=1.0)
    fig.subplots_adjust(wspace=0.26, top=0.88, bottom=0.13)
    save(fig, out_dir, "fig2_hitk_44disease")


# ---------------------------------------------------------------------------
# fig3 — single-panel landscape: selected-model rank (x) + candidate-pool size (track)
# ---------------------------------------------------------------------------
def _landscape_log_ticks(xmax: float) -> list[int]:
    """Log-axis tick positions: dense at low ranks (small pools) + decade anchors."""
    ticks = [t for t in (1, 2, 3, 5, 10, 20, 50, 100, 150, 200) if t <= xmax]
    return ticks or [1]


def fig3_landscape(df, out_dir, model_tag):
    """Figure 3 — single-panel landscape view. One row per disease: a track spans rank 1 ->
    pool size (its right end = total # candidate PGS), and each method's selected model sits
    at its empirical rank (marker shape + colour = method). Markers are vertically staggered
    within each row so coincident ranks remain visible."""
    d = df.sort_values("model_count", ascending=False).reset_index(drop=True)
    n = len(d); y = np.arange(n)[::-1]
    x_max = float(d.model_count.max()) * 1.2
    # fixed vertical lanes per method so overlapping ranks stay readable
    y_dodge = {"baseline": -0.24, "catalog": 0.0, "agent": 0.24}
    fig, ax = plt.subplots(figsize=(13.4, 13.8))

    # alternating row bands to guide the eye across the wide axis
    for i, yi in enumerate(y):
        if i % 2 == 0:
            ax.axhspan(yi - 0.5, yi + 0.5, color="#F5F6F8", zorder=0)
    # pool-extent track (rank 1 -> pool size) with a cap at the pool end
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.plot([1, r.model_count], [yi, yi], color="#C7CDD5", lw=2.6, zorder=1, solid_capstyle="round")
        ax.plot([r.model_count], [yi], marker="|", color="#8A9098", ms=9, mew=1.7, zorder=2)

    # method markers (shape + colour = method); agent drawn last (on top)
    rank_halo = [pe.withStroke(linewidth=3.0, foreground="white")]
    method_order = [("baseline", "o", 62), ("catalog", "X", 82), ("agent", "*", 230)]
    for key, mk, sz in method_order:
        sub = d.dropna(subset=[f"{key}_rank"])
        yi = y[sub.index.to_numpy()] + y_dodge[key]
        ax.scatter(sub[f"{key}_rank"], yi, color=M[key][0], marker=mk, s=sz,
                   edgecolor="white", linewidth=0.6, zorder=4)

    # rank labels: one label per distinct rank within each disease row
    for idx, row in d.iterrows():
        yi_base = y[idx]
        pool = int(row.model_count)
        by_rank: dict[int, list[str]] = {}
        for key, _, _ in method_order:
            rk = row.get(f"{key}_rank")
            if pd.notna(rk):
                by_rank.setdefault(int(rk), []).append(key)
        for rank, keys in by_rank.items():
            solo = len(keys) == 1
            yi = yi_base + (y_dodge[keys[0]] if solo else 0.0)
            near_end = rank >= max(2, int(pool * 0.72))
            dx, ha = (-12, "right") if near_end else (12, "left")
            ax.annotate(
                str(rank), (rank, yi), textcoords="offset points", xytext=(dx, 0),
                ha=ha, va="center", fontsize=11.5, color=COLORS["text"],
                fontweight="bold", zorder=5, path_effects=rank_halo,
            )

    ax.set_yticks(y)
    ax.set_yticklabels([f"{t}  (n={p})" for t, p in zip(d.disease_label, d.model_count)], fontsize=7.6)
    ax.set_xscale("log")
    ax.set_xlim(0.85, x_max); ax.set_ylim(-1.3, n - 0.85)
    ax.axvline(1, color=COLORS["gain"], lw=1.4, ls=(0, (4, 3)), zorder=0)
    log_ticks = _landscape_log_ticks(x_max)
    ax.xaxis.set_major_locator(FixedLocator(log_ticks))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(round(v))}"))
    ax.set_xlabel("Benchmark rank of selected model (1 = best)",
                  fontsize=12, fontweight="bold", labelpad=6)
    ax.grid(True, axis="x", color=COLORS["grid"], lw=1.0); ax.set_axisbelow(True); ax.tick_params(labelsize=10)

    leg = [("agent", "*", 15), ("baseline", "o", 10), ("catalog", "X", 11)]
    handles = [Line2D([0], [0], marker=mk, color="none", markerfacecolor=M[k][0], markeredgecolor="white",
                      markersize=ms, label=M[k][2]) for k, mk, ms in leg]
    handles.append(Line2D([0], [0], linestyle="none", marker="", color="none",
                          label="Markers staggered vertically when ranks coincide"))
    ax.legend(handles=handles, loc="lower right", fontsize=9.5, title="Selected by", title_fontsize=10.5)

    title = (f"Model-landscape view: selected-model rank and candidate-pool size "
             f"across {n} diseases ({model_tag})")
    ax.text(-0.02, 1.008, title, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=14.5, fontweight="bold", clip_on=False)
    fig.subplots_adjust(top=0.975, bottom=0.055)
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"fig3_landscape_44disease.{ext}", dpi=400,
                    bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# ---------------------------------------------------------------------------
# fig5 — micro case studies: rank–AUC landscape for hand-picked diseases
# ---------------------------------------------------------------------------
def _load_per_disease(model_tag: str):
    agent_dir, llm_dir = _runs(model_tag)
    ag = json.loads((agent_dir / "experiment_topk_holistic_rerank_batch_summary.json").read_text())
    ll = json.loads((llm_dir / "experiment_without_domain_summary.json").read_text())
    agpd = {d["ontology"]: d for d in ag["per_disease"]}
    llpd = {d["ontology"]: d for d in ll["per_disease"]}
    return agpd, llpd


def _landscape_table(ontology: str, agpd: dict, llpd: dict) -> pd.DataFrame:
    d, ll = agpd[ontology], llpd[ontology]
    auc_by_id = d.get("benchmark_auc_by_id", {})
    agent_id = d.get("modal_recommendation")
    llm_id = ll.get("modal_recommendation")
    catalog_id = (d.get("baseline") or {}).get("pgs_id")
    rows = []
    for rank, pgs_id in enumerate(d.get("benchmark_ranked_ids", []), start=1):
        rows.append({
            "pgs_id": pgs_id,
            "auc": float(auc_by_id[pgs_id]),
            "rank": rank,
            "agent": pgs_id == agent_id,
            "baseline": pgs_id == llm_id,
            "catalog": pgs_id == catalog_id,
        })
    return pd.DataFrame(rows)


def _rank_window(n_models: int, ranks: list[int]) -> int:
    ranks = [int(r) for r in ranks if pd.notna(r)]
    if n_models <= 15:
        return n_models
    if not ranks:
        return min(n_models, 35)
    return min(n_models, max(35, max(ranks) + 8))


_MICRO_LABEL = {"agent": "PRS Agent", "baseline": "General LLM", "catalog": "PGS Report"}
_MICRO_OFFSET = {"catalog": (9, -15), "baseline": (9, 0), "agent": (9, 14)}


def fig5_micro_case_studies(model_tag: str, out_dir: Path) -> None:
    """Figure 5 — 2×4 rank–AUC landscape panels for eight curated diseases."""
    agpd, llpd = _load_per_disease(model_tag)
    icd_map = _icd_by_ontology()
    source_dir = out_dir / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 4, figsize=(22.5, 10.4))
    halo = [pe.withStroke(linewidth=2.6, foreground="white")]
    method_specs = [
        ("catalog", "X", 110, COLORS["catalog"]),
        ("baseline", "o", 78, COLORS["baseline"]),
        ("agent", "*", 240, COLORS["agent"]),
    ]

    for i, ontology in enumerate(MICRO_CASES):
        ax = axes.ravel()[i]
        panel_lab = chr(ord("a") + i)
        panel_label(ax, panel_lab, -0.12, 1.04)
        d = agpd[ontology]
        ll = llpd[ontology]
        landscape = _landscape_table(ontology, agpd, llpd)
        landscape.to_csv(source_dir / f"candidate_landscape__{ontology.replace(' ', '_')}.csv", index=False)

        n_models = int(d["n_models"])
        ranks = [d.get("modal_recommendation_rank"), ll.get("modal_recommendation_rank"),
                 (d.get("baseline") or {}).get("rank")]
        show_to = _rank_window(n_models, ranks)
        sub = landscape.loc[landscape["rank"] <= show_to].copy()

        ax.plot(sub["rank"], sub["auc"], color=COLORS["neutral"], lw=2.0,
                marker="o", ms=4.0, markerfacecolor=COLORS["neutral"],
                markeredgecolor="white", markeredgewidth=0.3, zorder=1)
        for key, mk, sz, color in method_specs:
            hit = sub.loc[sub[key]]
            if hit.empty:
                continue
            row = hit.iloc[0]
            ax.scatter(row["rank"], row["auc"], marker=mk, s=sz, color=color,
                       edgecolor="white", linewidth=0.7, zorder=4)
            dx, dy = _MICRO_OFFSET[key]
            ax.annotate(
                f"{_MICRO_LABEL[key]}\nrank {int(row['rank'])}",
                (row["rank"], row["auc"]),
                textcoords="offset points", xytext=(dx, dy),
                fontsize=10.5, color=color, fontweight="bold", ha="left", va="center",
                linespacing=1.05, zorder=5, path_effects=halo,
            )

        y0, y1 = float(sub["auc"].min()), float(sub["auc"].max())
        pad = max(0.012, (y1 - y0) * 0.14)
        ax.set_xlim(0.6, show_to + 0.55)
        ax.set_ylim(y0 - pad, y1 + pad)
        ax.set_title(_micro_case_title(ontology, icd_map), fontsize=13.5, fontweight="bold", pad=8)
        ax.set_xlabel("Empirical model rank", fontsize=12, fontweight="bold")
        if i % 4 == 0:
            ax.set_ylabel("AoU benchmark AUC", fontsize=12, fontweight="bold")
        ax.grid(True, color=COLORS["grid"], lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=11)
        ax.text(0.98, 0.97, f"{n_models} models, ranks 1–{show_to} shown",
                transform=ax.transAxes, ha="right", va="top", fontsize=10, color=COLORS["muted"])

    handles = [
        Line2D([0], [0], marker="X", color="none", markerfacecolor=COLORS["catalog"],
               markeredgecolor="white", markersize=10, label=CATALOG_LABEL),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["baseline"],
               markeredgecolor="white", markersize=9, label=GENERAL_LLM_LABEL),
        Line2D([0], [0], marker="*", color="none", markerfacecolor=COLORS["agent"],
               markeredgecolor="white", markersize=14, label=AGENT_LABEL),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=11.5, bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("Micro case studies: model-landscape view of selected PRS models",
                 fontsize=18, fontweight="bold", y=0.995)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.88, bottom=0.14, wspace=0.28, hspace=0.42)
    save(fig, out_dir, "fig5_micro_case_studies_44disease")


# ---------------------------------------------------------------------------
# fig0 — ablation dashboard: harness×skill bars + section LORO (static table)
# ---------------------------------------------------------------------------
N_DISEASES = 44


def _hit_pct(hits: int, n: int = N_DISEASES) -> float:
    return round(hits / n * 100, 1)


def _ablation_arms() -> list[tuple[str, int, bool]]:
    """(label, hits, is_full_system) sorted ascending by Hit@1."""
    arms = [
        ("General LLM (no Harness – no Skill)", 9, False),
        ("PRS Agent (2-stage Harness – no Skill)", 11, False),
        ("PRS Agent (no Harness – full Skill)", 13, False),
        ("PRS Agent (2-stage Harness – full Skill)", 19, True),
    ]
    return sorted(arms, key=lambda x: x[1])


def _ablation_loro(full_pct: float) -> list[tuple[str, int, float]]:
    """(section label, hits, drop_pp vs full)."""
    rows = [
        ("§5 development_method", 13),
        ("§1 predicted_trait", 14),
        ("§3 gwas_source", 14),
        ("§4 score_training", 14),
        ("§2 performance_metrics", 15),
        ("§6 variants", 15),
        ("§7 pgs_source", 15),
    ]
    out = []
    for sec, hits in rows:
        pct = _hit_pct(hits)
        out.append((sec, hits, round(pct - full_pct, 1)))
    return out


def fig0_ablation(out_dir: Path, model_tag: str = "gpt-5.4") -> None:
    """Figure 0 — ablation dashboard (Phase A/B complete; noise-floor replicate pending)."""
    arms = _ablation_arms()
    full_pct = _hit_pct(next(h for _, h, full in arms if full))
    loro = _ablation_loro(full_pct)

    source_dir = out_dir / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {"config": label, "hit_at_1_pct": _hit_pct(hits), "hits": hits, "n": N_DISEASES, "type": "factorial"}
        for label, hits, _ in arms
    ] + [
        {"config": f"full minus {sec}", "hit_at_1_pct": _hit_pct(hits), "hits": hits,
         "n": N_DISEASES, "vs_full_pp": drop, "type": "loro"}
        for sec, hits, drop in loro
    ]).to_csv(source_dir / "ablation_hit1_summary.csv", index=False)

    fig = plt.figure(figsize=(15.5, 11.0))
    gs = gridspec.GridSpec(2, 1, figure=fig, height_ratios=[0.88, 1.12], hspace=0.38)
    halo = [pe.withStroke(linewidth=2.4, foreground="white")]

    fig.suptitle(f"Ablation: skill and harness contributions to Hit@1 ({N_DISEASES} diseases, {model_tag})",
                 fontsize=15.5, fontweight="bold", y=0.98)

    bar_b = COLORS["agent_light"]

    ax_a = fig.add_subplot(gs[0])
    panel_label(ax_a, "a", -0.05, 1.03)
    ax_a.set_title("Harness × skill factorial ablation — Hit@1", fontsize=12.5, fontweight="bold", pad=10)
    y_a = np.arange(len(arms))
    vals_a = [_hit_pct(h) for _, h, _ in arms]
    bar_cols_a = [
        COLORS["baseline"] if label.startswith("General LLM")
        else COLORS["agent"] if full
        else COLORS["agent_light"]
        for label, _, full in arms
    ]
    ax_a.barh(y_a, vals_a, color=bar_cols_a, height=0.58, zorder=3)
    for yi, (label, hits, _) in enumerate(arms):
        ax_a.text(vals_a[yi] + 0.4, yi, f"{vals_a[yi]:.1f}%  ({hits}/{N_DISEASES})",
                  va="center", fontsize=10.5, fontweight="bold", color=COLORS["text"],
                  zorder=4, path_effects=halo)
    ax_a.set_yticks(y_a)
    ax_a.set_yticklabels([label for label, _, _ in arms], fontsize=10.5)
    ax_a.set_xlim(0, 50)
    ax_a.set_xlabel("Hit@1 accuracy (%)", fontsize=12, fontweight="bold")
    ax_a.grid(True, axis="x", color=COLORS["grid"], lw=0.8)
    ax_a.set_axisbelow(True)
    ax_a.tick_params(labelsize=10.5)
    ax_a.invert_yaxis()

    ax_b = fig.add_subplot(gs[1])
    panel_label(ax_b, "b", -0.05, 1.03)
    ax_b.set_title("Leave-one-out: full skill minus one section — Hit@1", fontsize=12.5, fontweight="bold", pad=14)

    labels_b = [f"− {sec}" for sec, _, _ in loro]
    vals_b = [_hit_pct(h) for _, h, _ in loro]
    y_b = np.arange(len(loro))
    ax_b.barh(y_b, vals_b, color=bar_b, height=0.58, zorder=3)
    ax_b.axvline(full_pct, color=COLORS["agent"], lw=1.6, ls=(0, (5, 4)), zorder=1)
    ax_b.annotate(
        AGENT_LABEL,
        xy=(full_pct, 1.0), xycoords=("data", "axes fraction"),
        xytext=(0, 5), textcoords="offset points",
        ha="center", va="bottom", fontsize=9.5, color=COLORS["agent"], fontweight="bold",
        clip_on=False,
    )
    for yi, (_, hits, drop) in enumerate(loro):
        ax_b.text(vals_b[yi] + 0.35, yi, f"{vals_b[yi]:.1f}%  ({hits}/{N_DISEASES})",
                  va="center", fontsize=10.5, fontweight="bold", color=COLORS["text"],
                  zorder=4, path_effects=halo)
        ax_b.text(16.0, yi, f"{drop:+.1f}pp", va="center", ha="right",
                  fontsize=9.5, color=COLORS["muted"])
    ax_b.set_yticks(y_b)
    ax_b.set_yticklabels(labels_b, fontsize=11)
    ax_b.set_xlim(16, 48)
    ax_b.set_xlabel("Hit@1 accuracy (%)", fontsize=12, fontweight="bold")
    ax_b.grid(True, axis="x", color=COLORS["grid"], lw=0.8)
    ax_b.set_axisbelow(True)
    ax_b.tick_params(labelsize=10.5)
    ax_b.invert_yaxis()

    fig.subplots_adjust(left=0.34, right=0.96, top=0.88, bottom=0.08)
    save(fig, out_dir, "fig0_ablation_44disease")


# ---------------------------------------------------------------------------
# fig4 — ΔAUC waterfall (Agent − General LLM), per disease
# ---------------------------------------------------------------------------
def fig4_delta_waterfall(df, out_dir, model_tag):
    d = df.dropna(subset=["delta_auc"]).sort_values("delta_auc").reset_index(drop=True)
    colors = [COLORS["gain"] if _delta_tier(v) == "higher" else COLORS["loss"]
              if _delta_tier(v) == "lower" else COLORS["neutral"]
              for v in d.delta_auc]
    fig, ax = plt.subplots(figsize=(16.0, 6.8))
    ax.bar(range(len(d)), d.delta_auc, color=colors, width=0.85, zorder=3)
    ax.axhline(0, color="black", lw=1.0)
    ax.set_xticks(range(len(d)))
    ax.set_xticklabels(d.disease_label, rotation=90, fontsize=6.8)
    ax.set_ylabel("Δ selected-model AUC (PRS Agent − General LLM)", fontsize=12.5, fontweight="bold")
    ax.grid(True, axis="y", color=COLORS["grid"], lw=1.0); ax.set_axisbelow(True); ax.tick_params(labelsize=10)
    npos = int((d.delta_auc > 0).sum()); nneg = int((d.delta_auc < 0).sum()); nident = int((d.delta_auc == 0).sum())
    ax.text(0.01, 0.96, f"Higher with Agent: {npos} · Lower: {nneg} · Identical: {nident}",
            transform=ax.transAxes, fontsize=11, color=COLORS["muted"], va="top")
    fig.suptitle(f"Where the skill helps: per-disease selected-AUC gain over the skill-free LLM ({model_tag})",
                 fontsize=15, fontweight="bold", y=1.0)
    save(fig, out_dir, "fig4_delta_waterfall_44disease")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-tag", default="gpt-5.4")
    args = ap.parse_args()
    out_dir = PROJECT_ROOT / f"experiments/contribution2/presentation/figures_44disease_efoclean"
    if args.model_tag != "gpt-5.4":
        out_dir = out_dir.with_name(out_dir.name + f"_{args.model_tag}")
    out_dir.mkdir(parents=True, exist_ok=True)
    fig0_ablation(out_dir, args.model_tag)
    df, curves, extras = load_df(args.model_tag)
    fig1_overall(df, extras, out_dir, args.model_tag)
    fig2_hitk(curves, extras, out_dir, args.model_tag)
    fig3_landscape(df, out_dir, args.model_tag)
    fig4_delta_waterfall(df, out_dir, args.model_tag)
    fig5_micro_case_studies(args.model_tag, out_dir)
    print(f"Wrote 6 figures to {out_dir}")
    print(f"  Hit@1: agent {curves['agent'][1]:.1%}  general-LLM {curves['baseline'][1]:.1%}  pgs-report {curves['catalog'][1]:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
