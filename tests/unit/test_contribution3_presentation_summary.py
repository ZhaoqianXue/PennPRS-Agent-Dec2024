from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRESENTATION_HTML = REPO_ROOT / "experiments" / "contribution3" / "presentation" / "index.html"


def test_top05_kpi_uses_official_macro_average_not_frontend_count():
    """Top 0.5% is the official A/B macro-average, not a micro count over 80 targets."""
    html = PRESENTATION_HTML.read_text(encoding="utf-8")

    assert "official A/B macro-average top-0.5% rate" in html
    assert "num: `${top05}<span class=\"kpi-num-sep\">/</span>${denom}`, label: 'in top 0.5%'" not in html
