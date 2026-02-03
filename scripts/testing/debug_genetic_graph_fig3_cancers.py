import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from dotenv import load_dotenv


@dataclass(frozen=True)
class CancerPanel:
    panel: str
    trait_query: str


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


def _slugify(text: str, max_len: int = 60) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in (text or "").strip())
    safe = "_".join([p for p in safe.split("_") if p])
    return safe[:max_len] if safe else "unknown"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _diagnose_get_neighbors_failure(err: Dict[str, Any]) -> str:
    et = (err or {}).get("error_type") or ""
    msg = (err or {}).get("error_message") or ""
    if et == "TraitNotFound":
        return (
            "Trait name not found in the Knowledge Graph. "
            "Fix: implement trait canonicalization / synonym mapping (e.g., map to uniqTrait used by KG), "
            "or add a fallback that tries alternate trait strings (e.g., remove 'cancer', add 'carcinoma')."
        )
    if "empty" in msg.lower():
        return (
            "Knowledge Graph datasets appear empty. "
            "Fix: ensure heritability + genetic correlation data are loaded (h2_df and gc_df non-empty) "
            "before running neighbor queries."
        )
    return (
        "Unexpected failure calling genetic_graph_get_neighbors. "
        "Fix: inspect ToolError context and upstream KG service exceptions; add structured debug logs."
    )


def _diagnose_verify_study_power_failure(err: Dict[str, Any]) -> str:
    et = (err or {}).get("error_type") or ""
    if et == "EdgeNotFound":
        return (
            "Edge provenance not found even though a neighbor edge exists. "
            "Likely directionality mismatch (stored as trait2->trait1). "
            "Fix: make get_edge_provenance symmetric (check both orientations), "
            "or normalize trait1/trait2 columns to canonical uniqTrait before filtering."
        )
    return (
        "Unexpected failure calling genetic_graph_verify_study_power. "
        "Fix: inspect ToolError context and validate gc_client dataframe columns and filters."
    )


def _diagnose_validate_mechanism_failure(reason: str) -> str:
    r = (reason or "").lower()
    if "efo" in r and "not found" in r:
        return (
            "EFO ID resolution failed. "
            "Fix: strengthen EFO resolution (use Open Targets grouped search, synonyms, and PGS trait mapping), "
            "or accept MONDO IDs and translate to EFO when possible."
        )
    if "timeout" in r or "rate" in r or "429" in r:
        return (
            "Open Targets / PheWAS API rate limiting or timeout. "
            "Fix: add retry with backoff, caching, and lower top_n_genes for debug."
        )
    return (
        "Mechanism validation failed or returned weak evidence. "
        "Fix: improve ontology mapping and increase top_n_genes; treat Low confidence as 'soft-fail' "
        "and still allow the neighbor candidate for consideration with caveats."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Debug the Genetic Graph Tools pipeline for the Fig.3 cancers (standalone, no Step2a gating)."
    )
    parser.add_argument("--limit", type=int, default=10, help="Max neighbors returned per cancer trait.")
    parser.add_argument("--rg-z", type=float, default=2.0, help="Minimum |rg_z_meta| threshold.")
    parser.add_argument("--h2-z", type=float, default=2.0, help="Minimum h2_z_meta threshold.")
    parser.add_argument("--study-power-k", type=int, default=2, help="Verify study power for top-K neighbors.")
    parser.add_argument("--mechanism-k", type=int, default=2, help="Validate mechanism for top-K neighbors.")
    parser.add_argument("--skip-study-power", action="store_true", help="Skip genetic_graph_verify_study_power.")
    parser.add_argument("--skip-mechanism", action="store_true", help="Skip genetic_graph_validate_mechanism.")
    parser.add_argument(
        "--panels",
        type=str,
        default="",
        help="Comma-separated subset of panels/traits to run (e.g., 'Breast,Esophageal' or 'Breast cancer').",
    )
    parser.add_argument("--out-dir", type=str, default="", help="Output directory (default: output/debug/...).")
    args = parser.parse_args()

    # Ensure project root is importable when running as a script.
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Load environment variables from .env for LLM-enabled resolution.
    try:
        load_dotenv(dotenv_path=project_root / ".env", override=False)
    except Exception:
        # Best-effort: do not fail debug runs due to dotenv edge cases.
        pass

    from src.server.core.tools.genetic_graph_tools import (
        genetic_graph_get_neighbors,
        genetic_graph_verify_study_power,
        genetic_graph_validate_mechanism,
    )
    from src.server.core.tool_schemas import ToolError, NeighborResult, MechanismValidation
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:6]
    out_dir = Path(args.out_dir) if args.out_dir else (project_root / "output" / "debug" / f"genetic_graph_fig3_{run_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Initializing KnowledgeGraphService (may take ~1-3 minutes on first load)...", file=sys.stderr, flush=True)
    kg_service = KnowledgeGraphService()
    print("KnowledgeGraphService ready.", file=sys.stderr, flush=True)
    print(f"LLM resolver enabled? {bool(os.getenv('OPENAI_API_KEY')) and os.getenv('KG_TRAIT_RESOLVER_LLM','1')=='1'}", file=sys.stderr, flush=True)

    # Optional clients (only needed for mechanism validation).
    ot_client = None
    phewas_client = None
    pgs_client = None
    prs_model_pgscatalog_search = None
    resolve_efo_id = None
    resolve_efo_candidates = None
    select_best_efo_candidate = None
    if not bool(args.skip_mechanism) and int(args.mechanism_k) > 0:
        from src.server.core.opentargets_client import OpenTargetsClient
        from src.server.core.phewas_client import PheWASClient
        from src.server.core.pgs_catalog_client import PGSCatalogClient
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search as _pgs_search
        from src.server.modules.disease.recommendation_agent import (
            resolve_efo_id as _resolve_efo_id,
            resolve_efo_candidates as _resolve_efo_candidates,
            select_best_efo_candidate as _select_best_efo_candidate,
        )

        ot_client = OpenTargetsClient()
        phewas_client = PheWASClient()
        pgs_client = PGSCatalogClient()
        prs_model_pgscatalog_search = _pgs_search
        resolve_efo_id = _resolve_efo_id
        resolve_efo_candidates = _resolve_efo_candidates
        select_best_efo_candidate = _select_best_efo_candidate

    results: List[Dict[str, Any]] = []

    selected = FIG3_CANCERS
    if args.panels:
        wanted = {p.strip().lower() for p in args.panels.split(",") if p.strip()}
        selected = [
            c for c in FIG3_CANCERS
            if c.panel.lower() in wanted or c.trait_query.lower() in wanted
        ]
        if not selected:
            print("ERROR: --panels provided but no panels matched.", file=sys.stderr, flush=True)
            return 2

    for item in selected:
        t0 = time.time()
        panel_slug = _slugify(item.panel)
        trait = item.trait_query
        print(f"[{item.panel}] get_neighbors start: {trait}", file=sys.stderr, flush=True)

        row: Dict[str, Any] = {
            "panel": item.panel,
            "trait": trait,
            "params": {"limit": args.limit, "rg_z": args.rg_z, "h2_z": args.h2_z},
            "get_neighbors": {},
            "neighbors": [],
        }

        neighbors_res = genetic_graph_get_neighbors(
            kg_service=kg_service,
            trait_id=trait,
            rg_z_threshold=float(args.rg_z),
            h2_z_threshold=float(args.h2_z),
            limit=int(args.limit),
        )

        if isinstance(neighbors_res, ToolError):
            err = neighbors_res.model_dump()
            row["get_neighbors"] = {"status": "error", **err, "fix": _diagnose_get_neighbors_failure(err)}
            row["duration_s"] = round(time.time() - t0, 3)
            results.append(row)
            _write_json(out_dir / "per_trait" / f"{panel_slug}.json", row)
            print(f"[{item.panel}] get_neighbors error: {err.get('error_type')} | {err.get('error_message')}", file=sys.stderr, flush=True)
            continue

        if not isinstance(neighbors_res, NeighborResult):
            row["get_neighbors"] = {
                "status": "error",
                "error_type": "UnexpectedReturnType",
                "error_message": f"Expected NeighborResult, got {type(neighbors_res).__name__}",
                "fix": "Fix: validate genetic_graph_get_neighbors return types and exception handling.",
            }
            row["duration_s"] = round(time.time() - t0, 3)
            results.append(row)
            _write_json(out_dir / "per_trait" / f"{panel_slug}.json", row)
            continue

        neighbor_ids = [n.trait_id for n in (neighbors_res.neighbors or [])]
        row["get_neighbors"] = {
            "status": "ok",
            "query_trait": getattr(neighbors_res, "query_trait", None),
            "resolved_by": getattr(neighbors_res, "resolved_by", None),
            "resolution_confidence": getattr(neighbors_res, "resolution_confidence", None),
            "target_trait": getattr(neighbors_res, "target_trait", trait),
            "target_h2_meta": neighbors_res.target_h2_meta,
            "neighbors_returned": len(neighbor_ids),
            "neighbors": neighbor_ids,
        }
        print(f"[{item.panel}] get_neighbors ok: neighbors={len(neighbor_ids)}", file=sys.stderr, flush=True)

        # IMPORTANT: Mimic real Step2a ordering as closely as possible.
        # In production, downstream steps use the *target_trait* (user input) plus KG outputs.
        # Here we keep both:
        # - user_trait: original query string (for EFO/semantic operations)
        # - kg_trait: canonical KG trait used by get_neighbors (for KG-edge operations)
        user_trait = trait
        kg_trait = row["get_neighbors"]["target_trait"]

        # Pre-resolve target EFO only if mechanism validation is enabled.
        target_efo = None
        if ot_client and pgs_client and prs_model_pgscatalog_search and resolve_efo_id:
            target_models = prs_model_pgscatalog_search(pgs_client, user_trait, limit=10)
            target_efo = resolve_efo_id(
                trait_name=user_trait,
                ot_client=ot_client,
                pgs_client=pgs_client,
                pgs_models=target_models.models,
            )
            # Fallback: if the user label cannot be resolved, try the KG-canonical trait.
            if not target_efo and kg_trait and kg_trait != user_trait:
                target_efo = resolve_efo_id(
                    trait_name=kg_trait,
                    ot_client=ot_client,
                    pgs_client=pgs_client,
                    pgs_models=target_models.models,
                )
            row["target_efo"] = target_efo

        for idx, neighbor_trait in enumerate(neighbor_ids):
            n_entry: Dict[str, Any] = {
                "neighbor_trait": neighbor_trait,
                "verify_study_power": None,
                "validate_mechanism": None,
            }

            # Step: genetic_graph_validate_mechanism (biological translator)
            if not args.skip_mechanism and idx < int(args.mechanism_k):
                if (
                    not ot_client
                    or not pgs_client
                    or not phewas_client
                    or not prs_model_pgscatalog_search
                    or not resolve_efo_id
                    or not resolve_efo_candidates
                    or not select_best_efo_candidate
                ):
                    n_entry["validate_mechanism"] = {
                        "status": "error",
                        "error_type": "MechanismDepsNotInitialized",
                        "error_message": "Mechanism validation dependencies were not initialized.",
                        "fix": "Fix: ensure OpenTargetsClient/PGSCatalogClient/PheWASClient are available and initialized.",
                    }
                    row["neighbors"].append(n_entry)
                    continue
                if not target_efo:
                    n_entry["validate_mechanism"] = {
                        "status": "error",
                        "error_type": "EfoNotFound",
                        "error_message": f"No EFO resolved for target trait '{user_trait}'",
                        "fix": _diagnose_validate_mechanism_failure("EFO not found for target"),
                    }
                else:
                    # Real Step2a uses multi-source candidate generation + optional mechanism calls
                    # to disambiguate ontology mapping.
                    neighbor_models = prs_model_pgscatalog_search(pgs_client, neighbor_trait, limit=10)
                    neighbor_candidates = resolve_efo_candidates(
                        trait_name=neighbor_trait,
                        ot_client=ot_client,
                        pgs_client=pgs_client,
                        pgs_models=neighbor_models.models,
                    )
                    n_entry["neighbor_candidates_count"] = len(neighbor_candidates or [])
                    if not neighbor_candidates:
                        n_entry["validate_mechanism"] = {
                            "status": "error",
                            "error_type": "EfoNotFound",
                            "error_message": f"No EFO resolved for neighbor trait '{neighbor_trait}'",
                            "fix": _diagnose_validate_mechanism_failure("EFO not found for neighbor"),
                        }
                    else:
                        def validate_fn(source_efo: str, target_efo_id: str, source_trait_name: str, target_trait_name: str):
                            return genetic_graph_validate_mechanism(
                                ot_client=ot_client,
                                source_trait_efo=source_efo,
                                target_trait_efo=target_efo_id,
                                source_trait_name=source_trait_name,
                                target_trait_name=target_trait_name,
                                top_n_genes=50,
                                phewas_client=phewas_client,
                            )

                        selected_candidate, mech = select_best_efo_candidate(
                            target_trait_name=user_trait,
                            target_efo_id=target_efo,
                            neighbor_trait_name=neighbor_trait,
                            candidates=neighbor_candidates,
                            validate_fn=validate_fn,
                        )
                        n_entry["neighbor_efo"] = selected_candidate.id if selected_candidate else None
                        n_entry["neighbor_efo_source"] = selected_candidate.source if selected_candidate else None

                        # Mirror production: if mechanism was not computed during disambiguation,
                        # compute it once using the selected candidate.
                        if selected_candidate and mech is None:
                            mech = validate_fn(target_efo, selected_candidate.id, user_trait, neighbor_trait)

                        if isinstance(mech, ToolError):
                            err = mech.model_dump()
                            n_entry["validate_mechanism"] = {
                                "status": "error",
                                **err,
                                "fix": _diagnose_validate_mechanism_failure(err.get("error_message", "")),
                            }
                        elif isinstance(mech, MechanismValidation):
                            n_entry["validate_mechanism"] = {
                                "status": "ok",
                                "confidence": mech.confidence_level,
                                "shared_genes": [g.gene_symbol for g in mech.shared_genes[:10]],
                                "shared_genes_count": len(mech.shared_genes),
                                "phewas_evidence_count": mech.phewas_evidence_count,
                                "mechanism_summary": mech.mechanism_summary,
                                "soft_fail": mech.confidence_level == "Low",
                                "fix_if_soft_fail": (
                                    "If treating Low confidence as failure: raise top_n_genes, improve EFO mapping, "
                                    "or accept the candidate but force Low-confidence caveats."
                                ),
                            }
                        else:
                            n_entry["validate_mechanism"] = {
                                "status": "error",
                                "error_type": "UnexpectedReturnType",
                                "error_message": f"Expected MechanismValidation/ToolError, got {type(mech).__name__}",
                                "fix": "Fix: validate genetic_graph_validate_mechanism return types and exception handling.",
                            }

            # Step: genetic_graph_verify_study_power (provenance)
            # Real Step2a performs this after (or in parallel with) mechanism evaluation, and caps calls.
            if not args.skip_study_power and idx < int(args.study_power_k):
                sp = genetic_graph_verify_study_power(
                    kg_service=kg_service,
                    source_trait=kg_trait,
                    target_trait=neighbor_trait,
                )
                if isinstance(sp, ToolError):
                    err = sp.model_dump()
                    n_entry["verify_study_power"] = {"status": "error", **err, "fix": _diagnose_verify_study_power_failure(err)}
                else:
                    n_entry["verify_study_power"] = {
                        "status": "ok",
                        "n_correlations": getattr(sp, "n_correlations", None),
                        "rg_meta": getattr(sp, "rg_meta", None),
                    }

            row["neighbors"].append(n_entry)

        row["duration_s"] = round(time.time() - t0, 3)
        results.append(row)
        _write_json(out_dir / "per_trait" / f"{panel_slug}.json", row)

    summary = {
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "params": {
            "limit": int(args.limit),
            "rg_z_threshold": float(args.rg_z),
            "h2_z_threshold": float(args.h2_z),
            "study_power_k": int(args.study_power_k),
            "mechanism_k": int(args.mechanism_k),
            "skip_study_power": bool(args.skip_study_power),
            "skip_mechanism": bool(args.skip_mechanism),
        },
        "results": results,
    }
    _write_json(out_dir / "summary.json", summary)

    # Print a compact console summary for fast iteration.
    print(f"Written: {out_dir / 'summary.json'}")
    for r in results:
        status = r.get("get_neighbors", {}).get("status")
        n = r.get("get_neighbors", {}).get("neighbors_returned")
        print(f"- {r['panel']}: {r['trait']} | get_neighbors={status} | neighbors={n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

