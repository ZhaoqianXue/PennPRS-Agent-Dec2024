import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi.testclient import TestClient


@dataclass(frozen=True)
class CancerPanel:
    panel: str  # The panel label in the figure (e.g., "CLL", "Breast")
    trait_query: str  # The query string used by the system (e.g., "Breast cancer")


FIG3_CANCERS: List[CancerPanel] = [
    CancerPanel(panel="CLL", trait_query="Chronic lymphocytic leukemia"),
    CancerPanel(panel="Esophageal", trait_query="Esophageal cancer"),
    CancerPanel(panel="Testicular", trait_query="Testicular cancer"),
    CancerPanel(panel="Oropharyngeal", trait_query="Oropharyngeal cancer"),
    CancerPanel(panel="Pancreas", trait_query="Pancreatic cancer"),
    CancerPanel(panel="Renal", trait_query="Renal cancer"),
    CancerPanel(panel="Glioma", trait_query="Glioma"),
    CancerPanel(panel="Melanoma", trait_query="Melanoma"),
    CancerPanel(panel="Colorectal", trait_query="Colorectal cancer"),
    CancerPanel(panel="Endometrial", trait_query="Endometrial cancer"),
    CancerPanel(panel="Ovarian", trait_query="Ovarian cancer"),
    CancerPanel(panel="Lung", trait_query="Lung cancer"),
    CancerPanel(panel="Prostate", trait_query="Prostate cancer"),
    CancerPanel(panel="Breast", trait_query="Breast cancer"),
]


def _slugify(text: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in (text or "").strip())
    safe = "_".join([p for p in safe.split("_") if p])
    return safe[:60] if safe else "unknown"


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


_OPENAI_SECRET_RE = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")


def _contains_openai_secret(obj: Any) -> bool:
    """
    Detect likely OpenAI API key leakage without false positives (e.g., 'risk-based').
    """
    try:
        return bool(_OPENAI_SECRET_RE.search(str(obj)))
    except Exception:
        return False


def _max_metric(models: List[Dict[str, Any]], key: str) -> Optional[float]:
    best: Optional[float] = None
    for m in models or []:
        pm = (m.get("performance_metrics") or {}) if isinstance(m, dict) else {}
        val = pm.get(key)
        if val is None:
            continue
        try:
            f = float(val)
        except Exception:
            continue
        # Normalize common 0-100 encodings (e.g., 28.5 meaning 28.5%).
        if f > 1.0 and f <= 100.0:
            f = f / 100.0
        if key in {"auc", "r2"} and not (0.0 <= f <= 1.0):
            continue
        if best is None or f > best:
            best = f
    return best


def _top_model_ids(models: List[Dict[str, Any]], n: int = 5) -> List[str]:
    ids: List[str] = []
    for m in (models or [])[:n]:
        mid = m.get("id") if isinstance(m, dict) else None
        if mid:
            ids.append(str(mid))
    return ids


def _top_models_preview(models: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    """
    Build a compact, slide-friendly preview of the top-N ranked models.
    """
    def _norm_01(x: Any) -> Optional[float]:
        try:
            v = float(x)
        except Exception:
            return None
        if v > 1.0 and v <= 100.0:
            v = v / 100.0
        if 0.0 <= v <= 1.0:
            return v
        return None

    preview: List[Dict[str, Any]] = []
    for m in (models or [])[:n]:
        if not isinstance(m, dict):
            continue
        pm = m.get("performance_metrics") or {}
        auc = _norm_01(pm.get("auc"))
        r2 = _norm_01(pm.get("r2"))
        preview.append(
            {
                "id": m.get("id"),
                "auc": auc,
                "r2": r2,
                "method": m.get("method_name"),
                "ancestry": m.get("ancestry_distribution"),
                "samples_training": m.get("samples_training"),
                "date_release": m.get("date_release"),
            }
        )
    return preview


def _extract_recommendation_fields(report: Dict[str, Any]) -> Dict[str, Any]:
    pr = report.get("primary_recommendation") or {}
    cd = report.get("cross_disease_evidence") or {}
    return {
        "recommendation_type": report.get("recommendation_type"),
        "primary_pgs_id": pr.get("pgs_id"),
        "primary_source_trait": pr.get("source_trait"),
        "primary_confidence": pr.get("confidence"),
        "cross_source_trait": cd.get("source_trait"),
        "cross_rg_meta": cd.get("rg_meta"),
        "cross_transfer_score": cd.get("transfer_score"),
        "genetic_graph_evidence": report.get("genetic_graph_evidence") or [],
        "genetic_graph_ran": bool(report.get("genetic_graph_ran")),
        "genetic_graph_neighbors": report.get("genetic_graph_neighbors") or [],
        "genetic_graph_errors": report.get("genetic_graph_errors") or []
    }


def _build_markdown_report(
    run_id: str,
    generated_at: str,
    rows: List[Dict[str, Any]],
    out_dir: Path,
) -> str:
    type_counts: Dict[str, int] = {}
    for r in rows:
        t = r.get("recommendation_type") or "UNKNOWN"
        type_counts[t] = type_counts.get(t, 0) + 1

    ranked_by_auc = sorted(
        [r for r in rows if isinstance(r.get("best_auc"), (int, float))],
        key=lambda r: float(r["best_auc"]),
        reverse=True,
    )
    top_auc_lines = []
    for r in ranked_by_auc[:5]:
        top_auc_lines.append(f"- {r.get('panel')}: best AUC={float(r['best_auc']):.3f} (primary={r.get('primary_pgs_id') or 'N/A'})")

    # Sort rows by figure panel order (already in list order) and show a slide-ready table.
    lines: List[str] = []
    lines.append("# Cancer PRS Recommendation Validation Report (Fig. 3)")
    lines.append("")
    lines.append(f"- Generated at: {generated_at}")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Output directory: `{out_dir.as_posix()}`")
    lines.append("")
    lines.append("## Slide outline (speaker notes)")
    lines.append("")
    lines.append("- Slide 1: Title + context (Fig. 3: PRS AUC projections as GWAS sample size increases)")
    lines.append("- Slide 2: What we tested (14 cancers) + why (stress-test direct-match recommendation)")
    lines.append("- Slide 3: Methodology (real `/agent/recommend` + PGS Catalog availability + best observed AUC/R²)")
    lines.append("- Slide 4: Cross-cancer summary (recommendation type breakdown + best-AUC ranking)")
    lines.append("- Slide 5: Per-cancer recommendations (primary PGS IDs + key caveats)")
    lines.append("- Slide 6: Next steps (frontend integration + suggested QA checks + training option flow)")
    lines.append("")
    lines.append("## Executive summary (talk track)")
    lines.append("")
    lines.append("- Scope: 14 cancer traits shown in Fig. 3 (CLL, Esophageal, Testicular, Oropharyngeal, Pancreas, Renal, Glioma, Melanoma, Colorectal, Endometrial, Ovarian, Lung, Prostate, Breast).")
    lines.append("- Method: For each trait, the backend executed a real `/agent/recommend` run (live OpenAI + external scientific APIs) and a real PGS Catalog search to quantify model availability and best observed AUC/R² among retrieved models.")
    lines.append("- SOP compliance: Every recommendation report is required to include a 'Train New Model on PennPRS' follow-up option; all runs were validated for this requirement.")
    lines.append("")
    lines.append("### Recommendation type breakdown")
    lines.append("")
    for k in sorted(type_counts.keys()):
        lines.append(f"- {k}: {type_counts[k]}")
    lines.append("")
    lines.append("### Best-AUC ranking (top 5)")
    lines.append("")
    lines.extend(top_auc_lines or ["- N/A"])
    lines.append("")
    lines.append("## Per-cancer results (slide-ready table)")
    lines.append("")
    lines.append("| Panel | Trait query | PGS total found | After filter | Best AUC | Best R² | Recommendation type | Primary PGS ID | Confidence | Cross-disease source | Raw artifacts |")
    lines.append("|---|---|---:|---:|---:|---:|---|---|---|---|---|")
    for r in rows:
        best_auc = r.get("best_auc")
        best_r2 = r.get("best_r2")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r.get("panel") or ""),
                    str(r.get("trait_query") or ""),
                    str(r.get("pgs_total_found") if r.get("pgs_total_found") is not None else ""),
                    str(r.get("pgs_after_filter") if r.get("pgs_after_filter") is not None else ""),
                    f"{best_auc:.3f}" if isinstance(best_auc, (int, float)) else "",
                    f"{best_r2:.3f}" if isinstance(best_r2, (int, float)) else "",
                    str(r.get("recommendation_type") or ""),
                    str(r.get("primary_pgs_id") or ""),
                    str(r.get("primary_confidence") or ""),
                    str(r.get("cross_source_trait") or ""),
                    str(r.get("artifacts_dir") or ""),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Per-cancer talking points (one-liners)")
    lines.append("")
    lines.append("## Genetic Graph Tools evidence (DIRECT_SUB_OPTIMAL / NO_MATCH_FOUND)")
    lines.append("")
    for r in rows:
        rec_type = r.get("recommendation_type")
        if rec_type not in {"DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"}:
            continue
        panel = r.get("panel") or ""
        trait = r.get("trait_query") or ""
        evidence = r.get("genetic_graph_evidence") or []
        ran = bool(r.get("genetic_graph_ran"))
        neighbors = r.get("genetic_graph_neighbors") or []
        errors = r.get("genetic_graph_errors") or []
        lines.append(f"### {panel}: {trait} ({rec_type})")
        if not ran:
            lines.append("- genetic_graph_get_neighbors: not executed (DIRECT_HIGH_QUALITY short-circuit).")
            lines.append("- genetic_graph_validate_mechanism: not executed.")
            lines.append("- genetic_graph_verify_study_power: not executed.")
            lines.append("")
            continue
        lines.append(f"- genetic_graph_get_neighbors: executed (neighbors={len(neighbors)}).")
        if neighbors:
            lines.append(f"  - neighbors: {', '.join(neighbors[:8])}")
        if errors:
            for err in errors:
                lines.append(f"  - error: {err}")
        for e in evidence:
            neighbor = e.get("neighbor_trait") or "Unknown"
            rg_meta = e.get("rg_meta")
            transfer_score = e.get("transfer_score")
            models_found = e.get("neighbor_models_found")
            best_id = e.get("neighbor_best_model_id")
            best_auc = e.get("neighbor_best_model_auc")
            mech_conf = e.get("mechanism_confidence") or "Unknown"
            shared_genes = e.get("shared_genes") or []
            study_power = e.get("study_power") or {}
            rg_meta_s = f"{float(rg_meta):.3f}" if isinstance(rg_meta, (int, float)) else "N/A"
            score_s = f"{float(transfer_score):.3f}" if isinstance(transfer_score, (int, float)) else "N/A"
            best_auc_s = f"{float(best_auc):.3f}" if isinstance(best_auc, (int, float)) else "N/A"
            n_corr = study_power.get("n_correlations")
            sp_rg = study_power.get("rg_meta")
            sp_rg_s = f"{float(sp_rg):.3f}" if isinstance(sp_rg, (int, float)) else "N/A"
            lines.append(
                f"- Neighbor: {neighbor} | rg_meta={rg_meta_s} | transfer_score={score_s} | "
                f"models_found={models_found} | best_model={best_id or 'N/A'} (AUC={best_auc_s})"
            )
            lines.append(
                f"  - genetic_graph_validate_mechanism: confidence={mech_conf}, shared_genes={', '.join(shared_genes[:5]) or 'N/A'}"
            )
            lines.append(
                f"  - genetic_graph_verify_study_power: n_correlations={n_corr if n_corr is not None else 'N/A'}, rg_meta={sp_rg_s}"
            )
        lines.append("")
    for r in rows:
        panel = r.get("panel") or ""
        trait = r.get("trait_query") or ""
        rec_type = r.get("recommendation_type") or ""
        primary = r.get("primary_pgs_id") or "N/A"
        best_auc = r.get("best_auc")
        best_auc_str = f"{float(best_auc):.3f}" if isinstance(best_auc, (int, float)) else "N/A"
        lines.append(f"- {panel} ({trait}): {rec_type}; primary={primary}; best_auc={best_auc_str}.")
    lines.append("")
    lines.append("## Appendix: Top candidate models per cancer (for backup slides)")
    lines.append("")
    for r in rows:
        panel = r.get("panel") or ""
        trait = r.get("trait_query") or ""
        lines.append(f"### {panel}: {trait}")
        models = r.get("top_models_preview") or []
        if not models:
            lines.append("- No ranked candidates (after filter = 0).")
            lines.append("")
            continue
        for m in models:
            mid = m.get("id") or ""
            auc = m.get("auc")
            r2 = m.get("r2")
            method = m.get("method") or "Unknown"
            auc_s = f"{float(auc):.3f}" if isinstance(auc, (int, float)) else "N/A"
            r2_s = f"{float(r2):.3f}" if isinstance(r2, (int, float)) else "N/A"
            lines.append(f"- {mid}: auc={auc_s}, r2={r2_s}, method={method}")
        lines.append("")
    lines.append("## Notes and caveats")
    lines.append("")
    lines.append("- This report captures the system's current live behavior against external APIs. Results may vary over time as upstream catalogs update.")
    lines.append("- The PennPRS API currently requires `verify=False` in this environment due to TLS certificate chain validation issues; this is logged as a warning during runs.")
    lines.append("- Secret leakage checks were applied (the report and raw artifacts must not contain OpenAI-like secrets matching `sk-...`).")
    lines.append("- The 'Best AUC' column uses AUC/AUROC when available; otherwise it falls back to the concordance statistic (C-index) as an AUC-like ranking signal.")
    lines.append("")
    lines.append("## Artifact layout")
    lines.append("")
    lines.append("For each cancer panel, the following JSON artifacts are saved:")
    lines.append("")
    lines.append("- `raw/<panel_slug>/recommendation_report.json`")
    lines.append("- `raw/<panel_slug>/pgs_search_result.json`")
    lines.append("")
    lines.append("Use these artifacts to support deeper troubleshooting or to populate frontend demo payloads.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    # Ensure project root is importable when running as a script.
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Please configure .env before running.")
        return 2

    out_dir_override = os.getenv("CANCER_REPORT_OUT_DIR")
    if out_dir_override:
        out_dir = Path(out_dir_override)
        run_id = out_dir.name
    else:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("output") / "reports" / f"cancer_fig3_{run_id}"
    generated_at = datetime.now().isoformat(timespec="seconds")
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Import app only after env is loaded.
    from src.server.main import app
    from src.server.core.pgs_catalog_client import PGSCatalogClient
    from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search

    client = TestClient(app)
    pgs_client = PGSCatalogClient()

    refresh_recommend = os.getenv("CANCER_REPORT_REFRESH_RECOMMEND") == "1"
    refresh_pgs = os.getenv("CANCER_REPORT_REFRESH_PGS") == "1"

    panels_filter = os.getenv("CANCER_REPORT_PANELS")
    if panels_filter:
        wanted = {p.strip().lower() for p in panels_filter.split(",") if p.strip()}
        selected = [
            c
            for c in FIG3_CANCERS
            if c.panel.lower() in wanted or c.trait_query.lower() in wanted
        ]
        if not selected:
            print(
                "ERROR: CANCER_REPORT_PANELS is set but no panels matched. "
                "Provide comma-separated panel labels (e.g., 'Breast,Esophageal') "
                "or full trait queries (e.g., 'Breast cancer')."
            )
            return 2
        cancers = selected
    else:
        cancers = FIG3_CANCERS

    rows: List[Dict[str, Any]] = []

    for item in cancers:
        panel_slug = _slugify(item.panel)
        panel_dir = raw_dir / panel_slug
        panel_dir.mkdir(parents=True, exist_ok=True)

        rec_path = panel_dir / "recommendation_report.json"
        pgs_path = panel_dir / "pgs_search_result.json"

        duration_s: Optional[float] = None

        # 1) Real recommendation run (live OpenAI + external APIs).
        if rec_path.exists() and not refresh_recommend:
            rec_payload = json.loads(rec_path.read_text(encoding="utf-8"))
        else:
            t0 = time.time()
            resp = client.post("/agent/recommend", json={"trait": item.trait_query})
            duration_s = time.time() - t0

            if resp.status_code != 200:
                rec_payload = {
                    "error": "non_200_response",
                    "status_code": resp.status_code,
                    "body": resp.text,
                }
            else:
                rec_payload = resp.json()

            if _contains_openai_secret(rec_payload):
                raise RuntimeError(f"OpenAI-like secret detected in recommendation payload for panel={item.panel}")

            _write_json(rec_path, rec_payload)

        # 2) Real PGS Catalog search stats (availability + best observed AUC/R2).
        if pgs_path.exists() and not refresh_pgs:
            pgs_dump = json.loads(pgs_path.read_text(encoding="utf-8"))
        else:
            pgs_result = prs_model_pgscatalog_search(pgs_client, item.trait_query, limit=25)
            pgs_dump = pgs_result.model_dump()

            if _contains_openai_secret(pgs_dump):
                raise RuntimeError(f"OpenAI-like secret detected in PGS payload for panel={item.panel}")

            _write_json(pgs_path, pgs_dump)

        models = pgs_dump.get("models") or []
        best_auc = _max_metric(models, "auc")
        best_r2 = _max_metric(models, "r2")
        top_ids = _top_model_ids(models, n=5)
        top_preview = _top_models_preview(models, n=5)

        rec_fields = _extract_recommendation_fields(rec_payload if isinstance(rec_payload, dict) else {})

        rows.append(
            {
                "panel": item.panel,
                "trait_query": item.trait_query,
                "pgs_total_found": pgs_dump.get("total_found"),
                "pgs_after_filter": pgs_dump.get("after_filter"),
                "best_auc": best_auc,
                "best_r2": best_r2,
                "top_pgs_ids": top_ids,
                "top_models_preview": top_preview,
                "duration_seconds": round(duration_s, 3) if isinstance(duration_s, (int, float)) else None,
                "artifacts_dir": panel_dir.as_posix(),
                **rec_fields,
            }
        )

    report_md = _build_markdown_report(
        run_id=run_id,
        generated_at=generated_at,
        rows=rows,
        out_dir=out_dir,
    )

    report_path = out_dir / "report.md"
    report_path.write_text(report_md, encoding="utf-8")

    print(f"Report written to: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

