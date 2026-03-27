"""
Build Local Knowledge Graphs for 52 Cross-List Input Diseases.

Phase 1 of the LLM-Based Local Graph experiment:
- For each input disease, discover genetically correlated neighbors (GWAS Atlas)
- For each target-neighbor pair, query shared genes/pathways (Open Targets)
- Output: one JSON per disease + one Markdown document per disease

Data sources:
  - Heritability (h²): data/heritability/gwas_atlas/gwas_atlas.tsv
  - Genetic Correlation (rg): data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv
  - Shared Gene/Pathway: Open Targets REST API

Usage:
  python -m experiments.contribution3.transfer.configs.build_local_graphs
  python -m experiments.contribution3.transfer.configs.build_local_graphs --skip-opentargets
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

TRANSFER_DIR = Path(__file__).resolve().parents[1]
CROSS_LIST_CSV = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "runs"
    / "cross_list_summary_merged.csv"
)
LOCAL_GRAPHS_DIR = TRANSFER_DIR / "runs" / "local_graphs"
DOCUMENTS_DIR = TRANSFER_DIR / "runs" / "documents"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Load cross-list input diseases (52 diseases)
# ---------------------------------------------------------------------------
def load_cross_list_inputs(csv_path: Path) -> pd.DataFrame:
    """Load the 52 cross-list input diseases from the merged summary CSV."""
    df = pd.read_csv(csv_path)
    # Cross-list inputs: has cross models beating self OR has no self AUC
    is_cross_input = (df["n_cross_models_beating_self"] > 0) | (
        df["has_self_auc"] == False  # noqa: E712
    )
    inputs = df[is_cross_input].copy().reset_index(drop=True)
    log.info(f"Loaded {len(inputs)} cross-list input diseases from {csv_path.name}")
    return inputs


# ---------------------------------------------------------------------------
# KG: get target node + neighbors
# ---------------------------------------------------------------------------
def build_kg_graph(
    kg_service: Any,
    ontology_name: str,
    icd: str,
    rg_z_threshold: float = 2.0,
    h2_z_threshold: float = 2.0,
) -> Dict[str, Any]:
    """
    Query GWAS Atlas (via KG service) for target node and all neighbors.

    Uses manual mapping from trait_mapping.py for reliable resolution,
    since cross-list ontology names often don't match GWAS Atlas uniqTrait.

    Returns dict with target_node, neighbors list, and edges list.
    """
    from experiments.contribution3.transfer.configs.trait_mapping import (
        CROSS_LIST_TO_GWAS_ATLAS,
    )

    # Use manual mapping first, fallback to KG resolution
    resolved_trait = CROSS_LIST_TO_GWAS_ATLAS.get(icd)
    resolve_method = "manual_mapping" if resolved_trait else None

    if not resolved_trait:
        # Fallback: try KG resolution
        resolution = kg_service.resolve_trait_id(ontology_name)
        if isinstance(resolution, dict):
            resolved_trait = resolution.get("resolved_trait_id")
            resolve_method = resolution.get("method")
        if not resolved_trait:
            # Try each semicolon-separated part
            for part in ontology_name.split(";"):
                part = part.strip()
                r2 = kg_service.resolve_trait_id(part)
                if isinstance(r2, dict) and r2.get("resolved_trait_id"):
                    resolved_trait = r2["resolved_trait_id"]
                    resolve_method = r2.get("method")
                    break

    if not resolved_trait:
        return {
            "resolved_trait": None,
            "resolve_method": None,
            "resolve_confidence": None,
            "target_node": None,
            "neighbors": [],
        }

    # Get target trait node
    target_node = kg_service.get_trait_node(resolved_trait)

    target_dict = None
    if target_node:
        target_dict = {
            "trait_id": target_node.trait_id,
            "domain": target_node.domain,
            "h2_meta": target_node.h2_meta,
            "h2_se_meta": target_node.h2_se_meta,
            "h2_z_meta": target_node.h2_z_meta,
            "n_studies": target_node.n_studies,
        }

    # Get full trait-centric graph (nodes + edges with full metadata)
    graph = kg_service.get_trait_centric_graph(
        trait_id=resolved_trait,
        rg_z_threshold=rg_z_threshold,
        h2_z_threshold=h2_z_threshold,
        limit=999,  # No truncation
    )

    # Build neighbor list with full edge data
    neighbors = []
    # Build edge lookup: edges have source_trait and target_trait
    edge_map: Dict[str, Any] = {}
    for edge in graph.edges:
        # Edge connects resolved_trait <-> neighbor
        other = (
            edge.target_trait
            if edge.source_trait == resolved_trait
            else edge.source_trait
        )
        edge_map[other] = edge

    # Build node lookup (skip target itself)
    for node in graph.nodes:
        if node.trait_id == resolved_trait:
            continue
        edge = edge_map.get(node.trait_id)
        if edge is None:
            continue
        neighbors.append(
            {
                "trait_id": node.trait_id,
                "domain": node.domain,
                "h2_meta": node.h2_meta,
                "h2_se_meta": node.h2_se_meta,
                "h2_z_meta": node.h2_z_meta,
                "n_studies": node.n_studies,
                "rg_meta": edge.rg_meta,
                "rg_se_meta": edge.rg_se_meta,
                "rg_z_meta": edge.rg_z_meta,
                "rg_p_meta": edge.rg_p_meta,
                "n_correlations": edge.n_correlations,
                "transfer_score": (edge.rg_meta**2) * (node.h2_meta or 0),
            }
        )

    return {
        "resolved_trait": resolved_trait,
        "resolve_method": resolve_method,
        "resolve_confidence": resolve_method,  # simplify: method doubles as confidence
        "target_node": target_dict,
        "neighbors": neighbors,
    }


# ---------------------------------------------------------------------------
# Open Targets: shared genes for each target-neighbor pair
# ---------------------------------------------------------------------------
def query_shared_genes(
    ot_client: Any,
    target_trait_name: str,
    target_efo: Optional[str],
    target_mondo: Optional[str],
    neighbor_trait_name: str,
    neighbor_efo: Optional[str],
    neighbor_mondo: Optional[str],
    top_n_genes: int = 50,
) -> Dict[str, Any]:
    """
    Query Open Targets for shared genes between target and neighbor.

    Returns dict with shared_genes, shared_pathways, etc.
    """
    from src.server.core.tools.genetic_graph_tools import (
        genetic_graph_validate_mechanism,
    )

    result = genetic_graph_validate_mechanism(
        ot_client=ot_client,
        source_trait_efo=target_efo or "",
        target_trait_efo=neighbor_efo or "",
        source_trait_name=target_trait_name,
        target_trait_name=neighbor_trait_name,
        top_n_genes=top_n_genes,
        phewas_client=None,  # No ExPheWAS
        source_trait_mondo=target_mondo,
        target_trait_mondo=neighbor_mondo,
    )

    # Check if result is ToolError
    if hasattr(result, "error_type"):
        return {
            "n_shared_genes": 0,
            "shared_genes": [],
            "shared_pathways": [],
            "mechanism_summary": result.error_message,
            "confidence_level": "None",
            "error": result.error_type,
        }

    # MechanismValidation result
    shared_genes_list = []
    for g in result.shared_genes:
        gene_dict = {
            "gene_symbol": g.gene_symbol,
            "gene_id": g.gene_id,
            "source_association": g.source_association,
            "target_association": g.target_association,
            "druggability": g.druggability,
            "pathways": g.pathways,
        }
        shared_genes_list.append(gene_dict)

    return {
        "n_shared_genes": len(shared_genes_list),
        "shared_genes": shared_genes_list,
        "shared_pathways": result.shared_pathways,
        "mechanism_summary": result.mechanism_summary,
        "confidence_level": result.confidence_level,
    }


def resolve_ids_for_trait(
    trait_name: str, ot_client: Any, pgs_client: Any = None
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve EFO and MONDO IDs for a trait name."""
    try:
        from src.server.modules.disease.recommendation_agent import (
            resolve_efo_and_mondo_ids,
        )

        return resolve_efo_and_mondo_ids(
            trait_name=trait_name,
            ot_client=ot_client,
            pgs_client=pgs_client,
        )
    except Exception as e:
        log.warning(f"Failed to resolve IDs for '{trait_name}': {e}")
        return (None, None)


# ---------------------------------------------------------------------------
# Markdown document assembly (Phase 2)
# ---------------------------------------------------------------------------
def assemble_document(local_graph: Dict[str, Any]) -> str:
    """Convert a local graph JSON to a Markdown document for LLM input."""
    lines = []
    icd = local_graph["input_icd"]
    ontology = local_graph["input_ontology"]
    target = local_graph.get("target_node") or {}

    lines.append(f"# Target Disease: {ontology} ({icd})")
    lines.append("")

    h2 = target.get("h2_meta")
    h2_z = target.get("h2_z_meta")
    n_studies = target.get("n_studies", "?")
    domain = target.get("domain", "Unknown")
    h2_str = f"h2={h2:.4f}" if h2 is not None else "h2=N/A"
    h2_z_str = f"z={h2_z:.1f}" if h2_z is not None else "z=N/A"
    lines.append(f"- Heritability: {h2_str} ({h2_z_str}, {n_studies} studies)")
    lines.append(f"- Domain: {domain}")
    lines.append("")

    neighbors = local_graph.get("neighbors", [])
    shared_genes_data = local_graph.get("shared_genes_by_neighbor", {})

    if not neighbors:
        lines.append("No genetically correlated neighbors found.")
        return "\n".join(lines)

    lines.append(
        f"# Genetically Correlated Neighbors ({len(neighbors)} traits, "
        f"all |rg_z|>2, h2_z>2)"
    )
    lines.append("")

    for nb in neighbors:
        trait_id = nb["trait_id"]
        nb_domain = nb.get("domain", "Unknown")
        nb_h2 = nb.get("h2_meta")
        nb_h2_z = nb.get("h2_z_meta")
        nb_n_studies = nb.get("n_studies", "?")
        rg = nb.get("rg_meta")
        rg_z = nb.get("rg_z_meta")
        rg_p = nb.get("rg_p_meta")
        n_corr = nb.get("n_correlations", "?")

        lines.append(f"## {trait_id}")
        lines.append(f"- Domain: {nb_domain}")

        h2_str = f"h2={nb_h2:.4f}" if nb_h2 is not None else "h2=N/A"
        h2_z_str = f"z={nb_h2_z:.1f}" if nb_h2_z is not None else "z=N/A"
        lines.append(f"- Heritability: {h2_str} ({h2_z_str}, {nb_n_studies} studies)")

        rg_str = f"rg={rg:.4f}" if rg is not None else "rg=N/A"
        rg_z_str = f"z={rg_z:.1f}" if rg_z is not None else "z=N/A"
        rg_p_str = f"p={rg_p:.2e}" if rg_p is not None else "p=N/A"
        lines.append(
            f"- Genetic Correlation: {rg_str}, {rg_z_str}, "
            f"{rg_p_str} ({n_corr} study-pairs)"
        )

        # Shared genes section
        sg_data = shared_genes_data.get(trait_id, {})
        n_sg = sg_data.get("n_shared_genes", 0)
        confidence = sg_data.get("confidence_level", "N/A")
        error = sg_data.get("error")

        if error:
            lines.append(f"- Shared Genes (Open Targets): query failed ({error})")
        elif n_sg == 0:
            lines.append("- Shared Genes (Open Targets): none found")
        else:
            lines.append(
                f"- Shared Genes (Open Targets): {n_sg} genes "
                f"(confidence: {confidence})"
            )
            # List top genes
            genes = sg_data.get("shared_genes", [])
            gene_strs = []
            for g in genes[:10]:  # Show top 10
                sym = g["gene_symbol"]
                src = g["source_association"]
                tgt = g["target_association"]
                gene_strs.append(f"{sym} (target={src:.2f}, neighbor={tgt:.2f})")
            if gene_strs:
                lines.append(f"  Top genes: {', '.join(gene_strs)}")
            pathways = sg_data.get("shared_pathways", [])
            if pathways:
                lines.append(f"  Shared pathways: {', '.join(pathways[:5])}")

        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Build local graphs for C3 transfer")
    parser.add_argument(
        "--skip-opentargets",
        action="store_true",
        help="Skip Open Targets queries (build rg-only graphs)",
    )
    parser.add_argument(
        "--diseases",
        type=str,
        default=None,
        help="Comma-separated ICD codes to process (default: all 52)",
    )
    parser.add_argument(
        "--ot-delay",
        type=float,
        default=1.0,
        help="Delay in seconds between Open Targets API calls (default: 1.0)",
    )
    args = parser.parse_args()

    # Ensure output dirs exist
    LOCAL_GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load cross-list input diseases
    cross_list = load_cross_list_inputs(CROSS_LIST_CSV)
    if args.diseases:
        target_icds = set(args.diseases.split(","))
        cross_list = cross_list[cross_list["input_icd"].isin(target_icds)]
        log.info(f"Filtered to {len(cross_list)} diseases: {target_icds}")

    # Initialize KG service
    log.info("Initializing KnowledgeGraphService (loading GWAS Atlas data)...")
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService

    kg_service = KnowledgeGraphService()
    log.info("KG service ready.")

    # Initialize Open Targets client (if needed)
    ot_client = None
    if not args.skip_opentargets:
        log.info("Initializing OpenTargetsClient...")
        from src.server.core.opentargets_client import OpenTargetsClient

        ot_client = OpenTargetsClient()
        log.info("Open Targets client ready.")

    # Process each disease
    results_summary = []
    for idx, row in cross_list.iterrows():
        icd = row["input_icd"]
        ontology = row["input_ontology"]
        top_output = row.get("top_output_disease", "")
        top_cross_auc = row.get("top_cross_auc", None)

        log.info(f"[{idx+1}/{len(cross_list)}] Processing {icd}: {ontology}")

        # Phase 1.1: KG graph (h² + rg from GWAS Atlas)
        kg_data = build_kg_graph(kg_service, ontology, icd=icd)
        n_neighbors = len(kg_data["neighbors"])
        log.info(
            f"  Resolved to '{kg_data['resolved_trait']}' "
            f"({kg_data['resolve_method']}), {n_neighbors} neighbors"
        )

        # Phase 1.2: Shared genes (Open Targets)
        shared_genes_by_neighbor: Dict[str, Dict] = {}
        if ot_client and n_neighbors > 0:
            # Resolve target EFO/MONDO IDs
            target_trait_for_ot = kg_data["resolved_trait"] or ontology
            target_efo, target_mondo = resolve_ids_for_trait(
                target_trait_for_ot, ot_client
            )
            if not target_efo and not target_mondo:
                # Try with ontology name
                target_efo, target_mondo = resolve_ids_for_trait(ontology, ot_client)

            log.info(
                f"  Target IDs: EFO={target_efo}, MONDO={target_mondo}"
            )

            for ni, nb in enumerate(kg_data["neighbors"]):
                nb_trait = nb["trait_id"]
                log.info(
                    f"  [{ni+1}/{n_neighbors}] Shared genes: "
                    f"{nb_trait}..."
                )

                # Resolve neighbor EFO/MONDO IDs
                nb_efo, nb_mondo = resolve_ids_for_trait(nb_trait, ot_client)

                if (target_efo or target_mondo) and (nb_efo or nb_mondo):
                    sg_result = query_shared_genes(
                        ot_client=ot_client,
                        target_trait_name=target_trait_for_ot,
                        target_efo=target_efo,
                        target_mondo=target_mondo,
                        neighbor_trait_name=nb_trait,
                        neighbor_efo=nb_efo,
                        neighbor_mondo=nb_mondo,
                    )
                    shared_genes_by_neighbor[nb_trait] = sg_result
                    n_sg = sg_result.get("n_shared_genes", 0)
                    log.info(f"    -> {n_sg} shared genes")
                else:
                    shared_genes_by_neighbor[nb_trait] = {
                        "n_shared_genes": 0,
                        "shared_genes": [],
                        "shared_pathways": [],
                        "mechanism_summary": "Could not resolve EFO/MONDO IDs",
                        "confidence_level": "None",
                        "error": "id_resolution_failed",
                    }
                    log.info("    -> skipped (no EFO/MONDO IDs)")

                # Rate limiting
                time.sleep(args.ot_delay)

        # Assemble local graph
        local_graph = {
            "input_icd": icd,
            "input_ontology": ontology,
            "input_description": row.get("input_description", ""),
            "has_self_auc": bool(row.get("has_self_auc", False)),
            "self_best_auc": (
                float(row["self_best_auc"])
                if pd.notna(row.get("self_best_auc"))
                else None
            ),
            "top_output_disease": top_output if pd.notna(top_output) else None,
            "top_cross_auc": (
                float(top_cross_auc) if pd.notna(top_cross_auc) else None
            ),
            "resolved_trait": kg_data["resolved_trait"],
            "resolve_method": kg_data["resolve_method"],
            "resolve_confidence": kg_data["resolve_confidence"],
            "target_node": kg_data["target_node"],
            "neighbors": kg_data["neighbors"],
            "shared_genes_by_neighbor": shared_genes_by_neighbor,
        }

        # Save JSON
        json_path = LOCAL_GRAPHS_DIR / f"local_graph_{icd}.json"
        with open(json_path, "w") as f:
            json.dump(local_graph, f, indent=2, default=str)

        # Save Markdown document
        doc = assemble_document(local_graph)
        doc_path = DOCUMENTS_DIR / f"local_graph_{icd}.md"
        with open(doc_path, "w") as f:
            f.write(doc)

        results_summary.append(
            {
                "icd": icd,
                "ontology": ontology,
                "resolved_trait": kg_data["resolved_trait"],
                "n_neighbors": n_neighbors,
                "n_neighbors_with_shared_genes": sum(
                    1
                    for v in shared_genes_by_neighbor.values()
                    if v.get("n_shared_genes", 0) > 0
                ),
                "top_output_disease": top_output if pd.notna(top_output) else None,
            }
        )

        log.info(
            f"  Saved: {json_path.name}, {doc_path.name}"
        )

    # Save summary
    summary_path = TRANSFER_DIR / "runs" / "local_graphs_summary.csv"
    pd.DataFrame(results_summary).to_csv(summary_path, index=False)
    log.info(f"\nDone. Summary saved to {summary_path}")
    log.info(f"Total: {len(results_summary)} diseases processed")


if __name__ == "__main__":
    main()
