"""
Core Logic for Module 2: Knowledge Graph Service.
Implements the Genetic Correlation Traversal logic defined in 'sop.md'.

Features:
- Dynamic Graph Construction (Nodes/Edges)
- Node Heritability Integration
- Weighted Scoring (rg^2 * h2)
- NEW: Trait-Centric Graph with Meta-Analysis aggregation
"""
from typing import List, Optional, Union, Dict, Any, Tuple
import os
import re
import pandas as pd
from src.server.modules.genetic_correlation.gwas_atlas_client import GWASAtlasGCClient
from src.server.modules.heritability.gwas_atlas_client import GWASAtlasClient as HeritabilityClient
from src.server.modules.heritability.models import HeritabilityEstimate
from src.server.modules.knowledge_graph.models import (
    KnowledgeGraphResult, 
    KnowledgeGraphNode, 
    GeneticCorrelationEdge,
    PrioritizedNeighbor,
    # NEW: Trait-Centric models
    TraitNode,
    GeneticCorrelationEdgeMeta,
    TraitCentricGraphResult
)
from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator

import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    Service for querying and traversing the Genetic Architecture Graph.
    
    The Knowledge Graph is implemented as a Virtual/Dynamic Graph,
    constructed on-demand from local GWAS Atlas data.
    """
    
    def __init__(
        self, 
        gc_client: Optional[GWASAtlasGCClient] = None,
        h2_client: Optional[HeritabilityClient] = None,
        # Legacy parameter for backward compatibility
        client: Optional[GWASAtlasGCClient] = None
    ):
        """
        Initialize the Knowledge Graph Service.
        
        Args:
            gc_client: Genetic Correlation client (GWAS Atlas)
            h2_client: Heritability client (GWAS Atlas)
            client: Legacy parameter, alias for gc_client
        """
        # Support both new and legacy parameter names
        self.gc_client = gc_client or client or GWASAtlasGCClient()
        self.h2_client = h2_client or HeritabilityClient()

        # Cache heavy aggregators (EdgeAggregator preprocess is O(N) over GC pairs).
        # Without caching, every neighbor query re-processes ~1.4M rows, making the tool unusably slow.
        self._trait_aggregator: Optional[TraitAggregator] = None
        self._edge_aggregator: Optional[EdgeAggregator] = None
        self._id_to_trait: Optional[Dict[int, str]] = None

        # Trait resolution caches (user query -> canonical uniqTrait).
        # This is used to make the Genetic Graph tools robust to free-form user trait strings.
        self._trait_alias_strings: Optional[List[str]] = None
        self._trait_alias_to_canonical: Optional[Dict[str, List[str]]] = None
        self._canonical_meta: Optional[Dict[str, Dict[str, Any]]] = None
        self._trait_resolution_cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _normalize_trait_text(text: str) -> str:
        """
        Normalize a free-form trait string for lookup.

        This is intentionally conservative (no aggressive stopword stripping) to keep behavior
        high-transferable across many trait types (disease, biomarker, behavior, etc.).
        """
        cleaned = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def _informative_tokens(cls, text: str) -> List[str]:
        """
        Extract "informative" tokens for semantic matching.

        This helps avoid brittle mappings where a generic subset string (e.g., "Cancer")
        outranks a specific query (e.g., "Esophageal cancer") under token_set_ratio.
        """
        stop = {
            # Generic biomedical words
            "disease", "syndrome", "disorder", "trait", "condition",
            # Neoplasm generic terms
            "cancer", "carcinoma", "tumor", "tumour", "neoplasm", "malignant", "benign",
            # Common boilerplate tokens in GWAS Atlas labels
            "diagnoses", "diagnosis", "main", "icd", "icd10", "history", "illnesses", "illness",
            # English stopwords
            "of", "and", "the", "a", "an", "in", "on", "at", "for", "to", "with", "without",
        }
        tokens = [t for t in cls._normalize_trait_text(text).split() if len(t) > 2 and t not in stop]
        return tokens

    def _ensure_trait_alias_index(self) -> bool:
        """
        Build a lightweight alias index from the heritability table:
        - aliases include both `uniqTrait` (canonical) and `Trait` (display label)
        - each alias maps to one or more canonical `uniqTrait` IDs
        - meta provides domain/chapter for LLM disambiguation
        """
        if self._trait_alias_strings is not None and self._trait_alias_to_canonical is not None and self._canonical_meta is not None:
            return True

        h2_df = self.h2_client.df
        if h2_df.empty:
            self._trait_alias_strings = []
            self._trait_alias_to_canonical = {}
            self._canonical_meta = {}
            return False

        if "uniqTrait" not in h2_df.columns:
            logger.warning("Heritability table missing 'uniqTrait' column; trait resolution disabled.")
            self._trait_alias_strings = []
            self._trait_alias_to_canonical = {}
            self._canonical_meta = {}
            return False

        alias_to_canon: Dict[str, set] = {}
        alias_strings: set = set()
        canonical_meta: Dict[str, Dict[str, Any]] = {}

        # Prefer itertuples for speed.
        cols = ["uniqTrait"]
        if "Trait" in h2_df.columns:
            cols.append("Trait")
        if "Domain" in h2_df.columns:
            cols.append("Domain")
        if "ChapterLevel" in h2_df.columns:
            cols.append("ChapterLevel")

        for row in h2_df[cols].itertuples(index=False):
            canonical = getattr(row, "uniqTrait", None)
            if canonical is None:
                continue
            canonical = str(canonical).strip()
            if not canonical:
                continue

            label = getattr(row, "Trait", None) if hasattr(row, "Trait") else None
            label = str(label).strip() if label is not None else ""

            domain = getattr(row, "Domain", None) if hasattr(row, "Domain") else None
            chapter = getattr(row, "ChapterLevel", None) if hasattr(row, "ChapterLevel") else None

            if canonical not in canonical_meta:
                canonical_meta[canonical] = {
                    "label": label or canonical,
                    "domain": str(domain).strip() if domain is not None else None,
                    "chapter_level": str(chapter).strip() if chapter is not None else None,
                }

            # Add canonical and label as aliases.
            for alias in {canonical, label}:
                if not alias:
                    continue
                alias = str(alias).strip()
                if not alias:
                    continue
                alias_strings.add(alias)
                norm = self._normalize_trait_text(alias)
                if not norm:
                    continue
                alias_to_canon.setdefault(norm, set()).add(canonical)

        self._trait_alias_strings = sorted(alias_strings)
        self._trait_alias_to_canonical = {k: sorted(list(v)) for k, v in alias_to_canon.items()}
        self._canonical_meta = canonical_meta
        return True

    def resolve_trait_id(
        self,
        query_trait: str,
        *,
        max_candidates: int = 8
    ) -> Dict[str, Any]:
        """
        Resolve a free-form trait string to the Knowledge Graph canonical `uniqTrait`.

        Only performs exact/alias matching (no fuzzy matching).
        For semantic expansion, use trait_synonym_expand instead.

        Returns:
            Dict with keys:
              - resolved_trait_id: Optional[str]
              - method: str (exact|alias|none)
              - confidence: str (High|Moderate|Low)
              - candidates: List[Dict[str, Any]] (top candidates with scores/meta)
              - rationale: str (English)
        """
        self._ensure_trait_alias_index()
        norm_q = self._normalize_trait_text(query_trait)
        if not norm_q or not self._trait_alias_to_canonical or not self._canonical_meta:
            return {
                "resolved_trait_id": None,
                "method": "none",
                "confidence": "Low",
                "candidates": [],
                "rationale": "Heritability trait index is unavailable or query is empty.",
            }

        # Cache by normalized query to avoid repeated LLM calls.
        cached = self._trait_resolution_cache.get(norm_q)
        if cached:
            return cached

        canon_hits = self._trait_alias_to_canonical.get(norm_q, [])
        if len(canon_hits) == 1:
            resolved = canon_hits[0]
            out = {
                "resolved_trait_id": resolved,
                "method": "alias",
                "confidence": "High",
                "candidates": [{"trait_id": resolved, "score": 100, **(self._canonical_meta.get(resolved) or {})}],
                "rationale": "Exact alias match after normalization.",
            }
            self._trait_resolution_cache[norm_q] = out
            return out

        if len(canon_hits) > 1:
            # Multiple canonicals share the same normalized alias; treat as ambiguous.
            candidates = [
                {"trait_id": t, "score": 100, **(self._canonical_meta.get(t) or {})}
                for t in canon_hits[:max_candidates]
            ]
            out = {
                "resolved_trait_id": canon_hits[0],
                "method": "alias",
                "confidence": "Low",
                "candidates": candidates,
                "rationale": "Multiple canonical traits match the same normalized alias; defaulting to first candidate.",
            }
            self._trait_resolution_cache[norm_q] = out
            return out

        # No exact/alias match found - return None
        # Fuzzy matching removed: trait_synonym_expand already handles semantic expansion
        out = {
            "resolved_trait_id": None,
            "method": "none",
            "confidence": "Low",
            "candidates": [],
            "rationale": "No exact or alias match found. Use trait_synonym_expand for semantic expansion.",
        }
        self._trait_resolution_cache[norm_q] = out
        return out

    def _ensure_aggregators(self) -> bool:
        """
        Lazily build and cache aggregators used by trait-centric APIs.

        Returns:
            True if aggregators are ready, False if required datasets are empty.
        """
        if self._trait_aggregator is not None and self._edge_aggregator is not None and self._id_to_trait is not None:
            return True

        h2_df = self.h2_client.df
        gc_df = self.gc_client._data if hasattr(self.gc_client, "_data") else pd.DataFrame()
        if h2_df.empty or gc_df.empty:
            return False

        self._trait_aggregator = TraitAggregator(h2_df=h2_df)
        self._id_to_trait = self._trait_aggregator.get_id_to_trait_map()
        self._edge_aggregator = EdgeAggregator(gc_df=gc_df, id_to_trait_map=self._id_to_trait)
        return True

    def _get_heritability(self, trait_name: str) -> Optional[HeritabilityEstimate]:
        """
        Query heritability for a trait by name.
        
        Args:
            trait_name: Name of the trait to look up
            
        Returns:
            HeritabilityEstimate object or None if not found
        """
        try:
            results = self.h2_client.search_trait(trait_name, limit=1)
            if results:
                return results[0]
        except Exception as e:
            logger.warning(f"Failed to get heritability for '{trait_name}': {e}")
        return None

    def get_neighbors(
        self, 
        trait_id: Union[str, int], 
        p_threshold: float = 0.05,
        include_h2: bool = True
    ) -> KnowledgeGraphResult:
        """
        Query genetic neighbors for a given trait.
        
        Args:
            trait_id: Source Trait ID (e.g. EFO_00001 or numeric ID)
            p_threshold: Significance cutoff (Default 0.05)
            include_h2: Whether to populate heritability for each node
            
        Returns:
            KnowledgeGraphResult with nodes and edges
        """
        # Get genetic correlations from GWAS Atlas
        raw_results = self.gc_client.get_correlations(trait_id, p_threshold=p_threshold)
        
        edges = []
        nodes = []
        seen_nodes = set()
        
        for res in raw_results:
            # Create Edge
            edge = GeneticCorrelationEdge(
                source=str(trait_id),
                target=str(res.id2),
                rg=res.rg,
                p_value=res.p,
                se=res.se
            )
            edges.append(edge)
            
            # Create Node (Target)
            node_id = str(res.id2)
            if node_id not in seen_nodes:
                label = getattr(res, 'trait_2_name', "Unknown")
                
                # Query heritability if requested
                h2_value = None
                if include_h2 and label and label != "Unknown":
                    est = self._get_heritability(str(label))
                    if est:
                        h2_value = est.h2_obs
                
                node = KnowledgeGraphNode(
                    id=node_id,
                    label=str(label),
                    h2=h2_value
                )
                nodes.append(node)
                seen_nodes.add(node_id)
                
        return KnowledgeGraphResult(nodes=nodes, edges=edges)

    def get_prioritized_neighbors(
        self,
        trait_id: Union[str, int],
        p_threshold: float = 0.05
    ) -> List[PrioritizedNeighbor]:
        """
        Get neighbors ranked by weighted score: rg^2 * h2.
        
        This method prioritizes genetically correlated traits that are both:
        1. Highly correlated with the target (high rg)
        2. Biologically viable for PRS transfer (significant h2)
        
        Args:
            trait_id: Source Trait ID
            p_threshold: Significance cutoff (Default 0.05)
            
        Returns:
            List of PrioritizedNeighbor sorted by score descending.
            Nodes without significant h2 (Z > 2) are excluded.
        """
        # Get genetic correlations
        raw_results = self.gc_client.get_correlations(trait_id, p_threshold=p_threshold)
        
        prioritized = []
        
        for res in raw_results:
            trait_name = getattr(res, 'trait_2_name', None)
            if not trait_name or trait_name == "Unknown":
                continue
            
            # Get heritability for the neighbor
            est = self._get_heritability(str(trait_name))
            if est is None:
                continue

            # Filter: Heritability Validity (Z > 2)
            # If Z is missing, we conservatively check if h2_obs > 0 and se is small, 
            # but usually Z is present. If Z is None, skip to be safe? 
            # Or use h2_obs > 0? Standard is Z > 2.
            if est.h2_z is None or est.h2_z <= 2.0:
                 continue
            
            h2_value = est.h2_obs
            
            # Calculate weighted score: rg^2 * h2
            rg_squared = res.rg ** 2
            score = rg_squared * h2_value
            
            neighbor = PrioritizedNeighbor(
                trait_id=str(res.id2),
                trait_name=str(trait_name),
                rg=res.rg,
                h2=h2_value,
                score=score,
                p_value=res.p
            )
            prioritized.append(neighbor)
        
        # Sort by score descending
        prioritized.sort(key=lambda x: x.score, reverse=True)
        
        return prioritized

    # =========================================================================
    # NEW TRAIT-CENTRIC METHODS (per sop.md Module 2 refactored spec)
    # =========================================================================
    
    def get_trait_node(self, trait_id: str) -> Optional[TraitNode]:
        """
        Get aggregated TraitNode for a given trait.
        
        Uses meta-analysis to aggregate heritability across all Studies
        for the same Trait (uniqTrait).
        
        Args:
            trait_id: Trait canonical name (uniqTrait)
            
        Returns:
            TraitNode with meta-analyzed h2 and study provenance, or None if not found
        """
        h2_df = self.h2_client.df
        if h2_df.empty:
            return None
        if self._trait_aggregator is None:
            self._trait_aggregator = TraitAggregator(h2_df=h2_df)
        return self._trait_aggregator.get_trait_node(trait_id)
    
    def get_prioritized_neighbors_v2(
        self,
        trait_id: str,
        rg_z_threshold: float = 2.0,
        h2_z_threshold: float = 2.0
    ) -> List[PrioritizedNeighbor]:
        """
        Get neighbors ranked by meta-analyzed score: rg_meta^2 * h2_meta.
        
        Uses Trait-level aggregation per sop.md Module 2 spec:
        - Groups Studies by uniqTrait
        - Applies inverse-variance weighted meta-analysis for both h^2 and r_g
        - Filters by |rg_z_meta| > threshold and h2_z_meta > threshold
        
        Args:
            trait_id: Source Trait ID (uniqTrait)
            rg_z_threshold: Minimum |rg_z_meta| (default 2.0, ~p<0.05)
            h2_z_threshold: Minimum h2_z_meta (default 2.0)
            
        Returns:
            List of PrioritizedNeighbor sorted by score descending.
            Only neighbors passing both Z-score filters are included.
        """
        if not self._ensure_aggregators():
            return []

        trait_aggregator = self._trait_aggregator
        edge_aggregator = self._edge_aggregator
        if trait_aggregator is None or edge_aggregator is None:
            return []

        # Get neighbor traits (O(1) lookup after EdgeAggregator preprocess).
        neighbor_traits = edge_aggregator.get_neighbor_traits(trait_id)
        
        prioritized = []
        
        for neighbor_id in neighbor_traits:
            # Get edge with meta-analyzed rg
            edge = edge_aggregator.get_aggregated_edge(trait_id, neighbor_id)
            if edge is None:
                continue
            
            # Filter by rg significance: |rg_z_meta| > threshold
            if edge.rg_z_meta is None or abs(edge.rg_z_meta) <= rg_z_threshold:
                continue
            
            # Get neighbor node with meta-analyzed h2
            neighbor_node = trait_aggregator.get_trait_node(neighbor_id)
            if neighbor_node is None:
                continue
            
            # Filter by h2 validity: h2_z_meta > threshold
            if neighbor_node.h2_z_meta is None or neighbor_node.h2_z_meta <= h2_z_threshold:
                continue
            
            if neighbor_node.h2_meta is None:
                continue
            
            # Calculate score: rg_meta^2 * h2_meta
            score = (edge.rg_meta ** 2) * neighbor_node.h2_meta
            
            neighbor = PrioritizedNeighbor(
                trait_id=neighbor_id,
                trait_name=neighbor_id,  # trait_id is the canonical name
                rg=edge.rg_meta,
                h2=neighbor_node.h2_meta,
                score=score,
                p_value=edge.rg_p_meta or 0.0,
                rg_z=edge.rg_z_meta,
                n_correlations=edge.n_correlations
            )
            prioritized.append(neighbor)
        
        # Sort by score descending
        prioritized.sort(key=lambda x: x.score, reverse=True)
        
        return prioritized
    
    def get_trait_centric_graph(
        self,
        trait_id: str,
        rg_z_threshold: float = 2.0,
        h2_z_threshold: float = 2.0,
        limit: int = 50
    ) -> TraitCentricGraphResult:
        """
        Get complete trait-centric graph for a given trait.
        
        Returns the source trait node and all connected neighbor nodes
        with their edges, using meta-analysis aggregation.
        
        Args:
            trait_id: Source Trait ID (uniqTrait)
            rg_z_threshold: Minimum |rg_z_meta|
            h2_z_threshold: Minimum h2_z_meta
            limit: Maximum number of neighbors to include
            
        Returns:
            TraitCentricGraphResult with nodes and edges
        """
        nodes = []
        edges = []
        
        # Get source trait node
        source_node = self.get_trait_node(trait_id)
        if source_node:
            nodes.append(source_node)
        
        # Get prioritized neighbors
        neighbors = self.get_prioritized_neighbors_v2(
            trait_id=trait_id,
            rg_z_threshold=rg_z_threshold,
            h2_z_threshold=h2_z_threshold
        )[:limit]
        
        h2_df = self.h2_client.df
        gc_df = self.gc_client._data if hasattr(self.gc_client, '_data') else pd.DataFrame()
        
        if not h2_df.empty and not gc_df.empty:
            trait_aggregator = TraitAggregator(h2_df=h2_df)
            id_to_trait = trait_aggregator.get_id_to_trait_map()
            edge_aggregator = EdgeAggregator(gc_df=gc_df, id_to_trait_map=id_to_trait)
            
            for neighbor in neighbors:
                # Add neighbor node
                neighbor_node = trait_aggregator.get_trait_node(neighbor.trait_id)
                if neighbor_node:
                    nodes.append(neighbor_node)
                
                # Add edge
                edge = edge_aggregator.get_aggregated_edge(trait_id, neighbor.trait_id)
                if edge:
                    edges.append(edge)
        
        return TraitCentricGraphResult(nodes=nodes, edges=edges)

    def get_edge_provenance(
        self,
        source_trait: str,
        target_trait: str
    ):
        """
        Get detailed study-pair provenance for a specific genetic correlation edge.
        
        Implements sop.md Module 3 genetic_graph_verify_study_power dependency.
        JIT Loading: Only called when Agent needs deep quality control.
        
        Args:
            source_trait: Source trait canonical name
            target_trait: Target trait canonical name
            
        Returns:
            StudyPowerResult with correlation provenance, or None if edge not found
        """
        from src.server.core.tool_schemas import StudyPowerResult, CorrelationProvenance
        from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
        
        # Get raw correlations for source trait
        if hasattr(self.gc_client, 'get_correlations_for_trait'):
            correlations_df = self.gc_client.get_correlations_for_trait(source_trait)
        elif hasattr(self.gc_client, '_data') and not self.gc_client._data.empty:
            # Fallback to filtering internal data
            gc_df = self.gc_client._data
            correlations_df = gc_df[
                (gc_df['trait1'].str.lower() == source_trait.lower()) |
                (gc_df['uniqTrait1'].str.lower() == source_trait.lower())
            ] if 'trait1' in gc_df.columns else pd.DataFrame()
        else:
            return None
        
        if correlations_df.empty:
            return None
        
        # Filter to edges involving target_trait
        target_lower = target_trait.lower()
        
        if 'trait2' in correlations_df.columns:
            edge_correlations = correlations_df[
                correlations_df['trait2'].str.lower() == target_lower
            ]
        elif 'uniqTrait2' in correlations_df.columns:
            edge_correlations = correlations_df[
                correlations_df['uniqTrait2'].str.lower() == target_lower
            ]
        else:
            return None
        
        if edge_correlations.empty:
            return None
        
        # Build study metadata cache
        study_cache = self._build_study_cache()
        
        # Build provenance list
        provenance_list = []
        for _, row in edge_correlations.iterrows():
            study1_id = int(row.get('id1', 0))
            study2_id = int(row.get('id2', 0))
            
            study1_meta = study_cache.get(study1_id, {})
            study2_meta = study_cache.get(study2_id, {})
            
            prov = CorrelationProvenance(
                study1_id=study1_id,
                study1_n=study1_meta.get('n', 0),
                study1_population=study1_meta.get('population', 'Unknown'),
                study1_pmid=study1_meta.get('pmid', ''),
                study2_id=study2_id,
                study2_n=study2_meta.get('n', 0),
                study2_population=study2_meta.get('population', 'Unknown'),
                study2_pmid=study2_meta.get('pmid', ''),
                rg=float(row.get('rg', 0)),
                se=float(row.get('se', 0)),
                p=float(row.get('p', 1))
            )
            provenance_list.append(prov)
        
        if not provenance_list:
            return None
        
        # Calculate meta-analyzed rg using inverse-variance weighting
        rg_se_pairs = [(p.rg, p.se) for p in provenance_list if p.se > 0]
        if rg_se_pairs:
            rg_values = [v for v, _ in rg_se_pairs]
            se_values = [s for _, s in rg_se_pairs]
            meta_result = inverse_variance_meta_analysis(rg_values, se_values)
            rg_meta = meta_result.get('theta_meta', provenance_list[0].rg)
        else:
            rg_meta = provenance_list[0].rg if provenance_list else 0.0

        return StudyPowerResult(
            source_trait=source_trait,
            target_trait=target_trait,
            rg_meta=rg_meta,
            n_correlations=len(provenance_list),
            correlations=provenance_list
        )
    
    def _build_study_cache(self) -> Dict[int, dict]:
        """
        Build cache of study metadata (n, population, pmid) from heritability data.
        
        Returns:
            Dict mapping study_id to metadata dict
        """
        if hasattr(self, '_study_cache'):
            return self._study_cache
        
        self._study_cache = {}
        
        if hasattr(self.h2_client, 'get_all_estimates'):
            try:
                h2_data = self.h2_client.get_all_estimates()
                for est in h2_data:
                    study_id = getattr(est, 'study_id', None)
                    if study_id:
                        self._study_cache[study_id] = {
                            'n': getattr(est, 'sample_size', 0),
                            'population': getattr(est, 'population', 'Unknown'),
                            'pmid': getattr(est, 'pmid', '')
                        }
            except Exception as e:
                logger.warning(f"Failed to build study cache: {e}")
        
        return self._study_cache

