"""
Presentation-friendly 7-section view of M06 RA winner PGS004163.

Output: experiments/contribution2/presentation/figures_m06_pgs_schema/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import fill

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from src.server.core.tools.pgs_single_record import build_single_record

OUT_DIR = PROJECT_ROOT / "experiments/contribution2/presentation/figures_m06_pgs_schema"

COLORS = {
    "agent": "#011F5B",
    "agent_light": "#6E8BBE",
    "card": "#F8FAFC",
    "card_edge": "#D0D7E2",
    "label": "#3D3D3D",
    "value": "#011F5B",
    "muted": "#6D737A",
    "header_bg": "#E8EEF6",
}

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
mpl.rcParams.update({"figure.facecolor": "white", "savefig.facecolor": "white"})


def _load_record() -> dict:
    record = build_single_record("PGS004163")
    if record is None:
        raise RuntimeError("PGS004163 not found in REST dump")
    return record


def _presentation_sections(record: dict) -> list[dict]:
    pt = record["predicted_trait"]
    pm = record["performance_metrics"]
    met = pm["metrics"]
    ev = pm["evaluation_sample"]
    sn = ev["sample_numbers"]
    gwas = record["source_of_variant_associations_gwas"]
    train = record["score_development_training"]
    pub = record["pgs_source"]
    efo = pt["trait_efo"][0] if pt.get("trait_efo") else {}
    or_es = next((e for e in met.get("effect_sizes") or [] if e.get("name_short") == "OR"), None)
    or_txt = "Not reported"
    if or_es:
        or_txt = f"OR {or_es['estimate']:.2f} per SD (95% CI {or_es['ci_lower']:.2f}–{or_es['ci_upper']:.2f})"

    cohorts = ", ".join(ev.get("cohorts") or []) or "—"
    gwas_n = gwas["sample_numbers"].get("individuals")
    train_n = train["sample_numbers"].get("individuals")
    cov_txt = "None — suitable for standalone PRS use" if str(pm.get("covariates")) in ("0", "None") else str(pm["covariates"])

    return [
        {
            "num": "1",
            "title": "predicted_trait",
            "rows": [
                ("trait_reported", pt["trait_reported"]),
                ("trait_efo", f"{efo.get('label', '—')} ({efo.get('id', '—')})"),
            ],
        },
        {
            "num": "2",
            "title": "performance_metrics",
            "rows": [
                ("phenotyping_reported", pm["phenotyping_reported"]),
                ("covariates", cov_txt),
                ("full_model_auroc", f"{met['full_model_auroc']:.3f}" if met.get("full_model_auroc") else "Not reported"),
                ("effect_sizes (OR)", or_txt),
                ("evaluation_sample", f"{cohorts} · {ev.get('ancestry') or '—'} · n={sn.get('individuals', 0):,}"),
            ],
        },
        {
            "num": "3",
            "title": "source_of_variant_associations_gwas",
            "rows": [
                ("sample_numbers", f"{gwas_n:,} individuals" if gwas_n else "Not reported"),
                ("ancestry", gwas.get("ancestry") or "Not reported"),
            ],
        },
        {
            "num": "4",
            "title": "score_development_training",
            "rows": [
                ("sample_numbers", f"{train_n:,} individuals" if train_n else "Not reported"),
                ("ancestry", train.get("ancestry") or "Not reported"),
            ],
        },
        {
            "num": "5",
            "title": "development_method",
            "rows": [
                ("method_name", record["development_method"]["method_name"]),
            ],
        },
        {
            "num": "6",
            "title": "variants",
            "rows": [
                ("variants_number", f"{record['variants']['variants_number']:,}"),
            ],
        },
        {
            "num": "7",
            "title": "pgs_source",
            "rows": [
                ("publication_journal", f"{pub.get('publication_journal') or '—'} ({str(pub.get('date_release') or '')[:4]})"),
                ("publication_title", pub.get("publication_title") or "—"),
            ],
        },
    ]


def _content_lines(section: dict, wrap_w: int = 88) -> list[str]:
    lines: list[str] = []
    for label, value in section["rows"]:
        lines.extend(fill(f"{label}: {value}", width=wrap_w, break_long_words=False).split("\n"))
    return lines


CONTENT_FS = 13.0
CONTENT_LINE_SPACING = 1.72
TITLE_FS = 12.5
TITLE_LINE_SPACING = 1.25


def _line_height_axes(fontsize: float, line_spacing: float) -> float:
    """Approximate one text line in normalized axes coordinates."""
    return (fontsize / 72.0) * line_spacing * 0.95


def _title_lines(title: str, width: int = 24) -> list[str]:
    return fill(title, width=width, break_long_words=False).split("\n")


def _row_weight(section: dict) -> float:
    """Tighter rows for sparse sections; scale with wrapped line count."""
    title_h = len(_title_lines(section["title"])) * _line_height_axes(TITLE_FS, TITLE_LINE_SPACING)
    content_h = len(_content_lines(section)) * _line_height_axes(CONTENT_FS, CONTENT_LINE_SPACING)
    return max(0.34, 0.18 + max(title_h, content_h) * 2.6)


def _draw_row(ax, section: dict) -> None:
    """One full-width horizontal band per evidence category."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    lines = _content_lines(section)
    title_lines = _title_lines(section["title"])
    content_line_h = _line_height_axes(CONTENT_FS, CONTENT_LINE_SPACING)
    title_line_h = _line_height_axes(TITLE_FS, TITLE_LINE_SPACING)
    chrome = 0.14
    title_block_h = len(title_lines) * title_line_h + 0.06
    content_block_h = len(lines) * content_line_h + 0.10
    card_h = min(0.96, max(0.30, chrome + max(title_block_h, content_block_h)))
    y_top = 0.97
    y_bot = y_top - card_h
    card_mid = (y_top + y_bot) / 2

    ax.add_patch(mpatches.FancyBboxPatch(
        (0.01, y_bot), 0.98, card_h,
        boxstyle="round,pad=0.008,rounding_size=0.02",
        facecolor=COLORS["card"], edgecolor=COLORS["card_edge"], linewidth=1.2,
    ))
    ax.add_patch(mpatches.Rectangle(
        (0.01, y_bot), 0.014, card_h, facecolor=COLORS["agent_light"], edgecolor="none",
    ))

    ax.text(0.03, card_mid, section["num"], fontsize=20, fontweight="bold",
            color=COLORS["agent_light"], va="center", ha="left")
    ax.text(
        0.07, card_mid, "\n".join(title_lines), fontsize=TITLE_FS, fontweight="bold",
        color=COLORS["agent"], va="center", ha="left", linespacing=TITLE_LINE_SPACING,
        family="monospace",
    )

    y0 = y_top - 0.11
    ax.text(
        0.40, y0, "\n".join(lines), fontsize=CONTENT_FS, fontweight="bold",
        color=COLORS["value"], va="top", ha="left", linespacing=CONTENT_LINE_SPACING,
    )


def plot_schema(record: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pgs004163_single_record.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    sections = _presentation_sections(record)
    row_heights = [_row_weight(s) for s in sections]
    fig_h = 3.2 + sum(row_heights) * 0.95
    fig = plt.figure(figsize=(15, fig_h))
    gs = gridspec.GridSpec(
        1 + len(sections), 1, figure=fig,
        height_ratios=[0.34, *row_heights],
        hspace=0.10,
    )

    ax_title = fig.add_subplot(gs[0])
    ax_title.axis("off")
    ax_title.text(0.5, 0.72, "M06 Rheumatoid Arthritis — model selected by PRS Agent",
                  ha="center", va="center", fontsize=21, fontweight="bold", color=COLORS["agent"])
    ax_title.text(0.5, 0.18,
                  "PGS004163   ·   7 evidence categories per candidate   ·   All of Us benchmark rank 1 / 25",
                  ha="center", va="center", fontsize=13.5, color=COLORS["muted"])

    for i, section in enumerate(sections, start=1):
        _draw_row(fig.add_subplot(gs[i]), section)

    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.03)
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"m06_pgs004163_schema.{ext}", dpi=300 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote figure to {out_dir}")


def main() -> None:
    plot_schema(_load_record(), OUT_DIR)


if __name__ == "__main__":
    main()
