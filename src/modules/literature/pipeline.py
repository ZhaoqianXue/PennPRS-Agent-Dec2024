"""
Literature Mining Workflow

LangGraph-based workflow orchestration for the Literature Mining Engine.
Implements the Supervisor + Workers architecture:

1. SUPERVISOR (This module - Orchestrator)
   - Manages workflow state
   - Routes papers through pipeline
   - Aggregates results
   - Handles errors and retries

2. CLASSIFIER AGENT → Classifies papers into categories
3. EXTRACTOR AGENTS → Extract structured data (parallel for multi-category papers)
4. VALIDATOR AGENT → Validate and deduplicate

This follows the architecture defined in implementation_modules.md
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Annotated, TypedDict, Sequence
from pathlib import Path

# LangGraph imports - will gracefully degrade if not installed
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not installed. Install with: pip install langgraph")

from .entities import (
    PaperMetadata,
    ClassificationResult,
    PRSModelExtraction,
    HeritabilityExtraction,
    GeneticCorrelationExtraction,
    ExtractionResult,
    ValidationResult,
    ValidationStatus,
    PaperCategory,
    WorkflowState,
    DataSource
)
from .pubmed import PubMedClient
from .paper_classifier import PaperClassifier, RuleBasedClassifier
from .information_extractor import PRSExtractor, HeritabilityExtractor, GeneticCorrelationExtractor
from .validator import Validator

logger = logging.getLogger(__name__)


# ============================================================================
# Workflow State (for LangGraph)
# ============================================================================

class LiteratureMiningState(TypedDict):
    """State for the LangGraph workflow."""
    # Input
    disease: str
    max_papers: int
    search_type: str  # "all", "prs", "heritability", "genetic_correlation"
    
    # Papers
    papers: List[PaperMetadata]
    current_index: int
    
    # Results by stage
    classifications: List[ClassificationResult]
    prs_extractions: List[PRSModelExtraction]
    h2_extractions: List[HeritabilityExtraction]
    rg_extractions: List[GeneticCorrelationExtraction]
    validations: List[ValidationResult]
    
    # Final outputs
    valid_prs: List[PRSModelExtraction]
    valid_h2: List[HeritabilityExtraction]
    valid_rg: List[GeneticCorrelationExtraction]
    review_queue: List[ValidationResult]
    
    # Status
    status: str
    errors: List[str]
    started_at: Optional[str]
    completed_at: Optional[str]


# ============================================================================
# Simple Workflow (without LangGraph)
# ============================================================================

class LiteratureMiningWorkflow:
    """
    Orchestrator for the literature mining pipeline.
    
    If LangGraph is available, uses graph-based orchestration.
    Otherwise, runs a simple sequential pipeline.
    
    Architecture:
    ```
    PubMed Search → Classify Papers → Extract Data → Validate → Store
                         │                  │
                         ▼                  ▼
                   (Multi-label)    (Parallel Extractors)
                                    - PRS Extractor
                                    - h² Extractor  
                                    - rg Extractor
    ```
    """
    
    def __init__(
        self,
        pubmed_client: Optional[PubMedClient] = None,
        classifier: Optional[PaperClassifier] = None,
        use_rule_based_classifier: bool = False,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the workflow.
        
        All LLM components use centralized configuration from src/core/llm_config.py
        
        Args:
            pubmed_client: PubMed client instance
            classifier: Paper classifier instance
            use_rule_based_classifier: Use keyword-based classifier instead of LLM
            data_dir: Directory for storing results
        """
        self.pubmed_client = pubmed_client or PubMedClient()
        
        if classifier:
            self.classifier = classifier
        elif use_rule_based_classifier:
            self.classifier = RuleBasedClassifier()
        else:
            # Uses centralized LLM config
            self.classifier = PaperClassifier()
        
        # Initialize extractors (all use centralized LLM config)
        self.prs_extractor = PRSExtractor()
        self.h2_extractor = HeritabilityExtractor()
        self.rg_extractor = GeneticCorrelationExtractor()
        
        # Initialize validator
        self.validator = Validator()
        
        # Data directory
        self.data_dir = Path(data_dir or "data/literature")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # LangGraph workflow (built lazily)
        self._graph = None
    
    # =========================================================================
    # Main Entry Points
    # =========================================================================
    
    def run(
        self,
        disease: str,
        max_papers: int = 50,
        search_type: str = "all",
        progress_callback: Optional[callable] = None
    ) -> WorkflowState:
        """
        Run the complete literature mining workflow for a disease.
        
        Args:
            disease: Disease/trait name to search
            max_papers: Maximum papers to process
            search_type: "all", "prs", "heritability", or "genetic_correlation"
            progress_callback: Optional callback(stage, current, total)
        
        Returns:
            WorkflowState with all results
        """
        state = WorkflowState(
            query=f"{disease} literature mining",
            disease=disease,
            max_papers=max_papers,
            status="initialized",
            started_at=datetime.now()
        )
        
        try:
            # Stage 1: Search PubMed
            state = self._search_papers(state, search_type, progress_callback)
            
            if not state.papers:
                state.status = "completed"
                state.completed_at = datetime.now()
                return state
            
            # Stage 2: Classify papers
            state = self._classify_papers(state, progress_callback)
            
            # Stage 3: Extract data from relevant papers
            state = self._extract_data(state, progress_callback)
            
            # Stage 4: Validate extractions
            state = self._validate_data(state, progress_callback)
            
            # Stage 5: Store results
            self._store_results(state)
            
            state.status = "completed"
            state.completed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            state.errors.append(str(e))
            state.status = "failed"
            state.completed_at = datetime.now()
        
        return state
    
    def run_prs_only(
        self,
        disease: str,
        max_papers: int = 50,
        progress_callback: Optional[callable] = None
    ) -> List[PRSModelExtraction]:
        """
        Run workflow focused on PRS extraction only.
        
        Convenience method for getting just PRS models.
        """
        state = self.run(
            disease=disease,
            max_papers=max_papers,
            search_type="prs",
            progress_callback=progress_callback
        )
        return state.valid_prs_models
    
    def run_heritability_only(
        self,
        disease: str,
        max_papers: int = 50,
        progress_callback: Optional[callable] = None
    ) -> List[HeritabilityExtraction]:
        """Run workflow focused on heritability extraction only."""
        state = self.run(
            disease=disease,
            max_papers=max_papers,
            search_type="heritability",
            progress_callback=progress_callback
        )
        return state.valid_heritability
    
    # =========================================================================
    # Pipeline Stages
    # =========================================================================
    
    def _search_papers(
        self,
        state: WorkflowState,
        search_type: str,
        progress_callback: Optional[callable]
    ) -> WorkflowState:
        """Stage 1: Search PubMed for relevant papers."""
        state.status = "searching"
        
        if progress_callback:
            progress_callback("searching", 0, 1)
        
        disease = state.disease
        max_papers = state.max_papers
        
        # Search based on type
        if search_type == "prs":
            result = self.pubmed_client.search_prs_papers(disease, max_papers)
        elif search_type == "heritability":
            result = self.pubmed_client.search_heritability_papers(disease, max_papers)
        elif search_type == "genetic_correlation":
            result = self.pubmed_client.search_genetic_correlation_papers(disease, max_papers)
        else:
            # Combined search for all types
            prs_result = self.pubmed_client.search_prs_papers(disease, max_papers // 3)
            h2_result = self.pubmed_client.search_heritability_papers(disease, max_papers // 3)
            rg_result = self.pubmed_client.search_genetic_correlation_papers(disease, max_papers // 3)
            
            # Combine and deduplicate PMIDs
            all_pmids = list(set(prs_result.pmids + h2_result.pmids + rg_result.pmids))[:max_papers]
            
            # Fetch papers
            state.papers = self.pubmed_client.fetch_papers(all_pmids)
            
            if progress_callback:
                progress_callback("searching", 1, 1)
            
            logger.info(f"Found {len(state.papers)} papers for '{disease}'")
            return state
        
        # Single search type - fetch papers
        if result.pmids:
            state.papers = self.pubmed_client.fetch_papers(result.pmids)
        
        if progress_callback:
            progress_callback("searching", 1, 1)
        
        logger.info(f"Found {len(state.papers)} papers for '{disease}' ({search_type})")
        return state
    
    def _classify_papers(
        self,
        state: WorkflowState,
        progress_callback: Optional[callable]
    ) -> WorkflowState:
        """Stage 2: Classify papers into categories."""
        state.status = "classifying"
        
        total = len(state.papers)
        
        def classify_progress(current, total_papers):
            if progress_callback:
                progress_callback("classifying", current, total_papers)
        
        state.classifications = self.classifier.classify_batch(
            state.papers,
            progress_callback=classify_progress
        )
        
        # Count relevant papers
        relevant = sum(1 for c in state.classifications if c.is_relevant)
        logger.info(f"Classified {total} papers: {relevant} relevant")
        
        return state
    
    def _extract_data(
        self,
        state: WorkflowState,
        progress_callback: Optional[callable]
    ) -> WorkflowState:
        """Stage 3: Extract structured data from classified papers."""
        state.status = "extracting"
        
        # Build lookup of papers by PMID
        papers_by_pmid = {p.pmid: p for p in state.papers}
        
        # Get PMIDs for each category
        prs_pmids = []
        h2_pmids = []
        rg_pmids = []
        
        for classification in state.classifications:
            if classification.has_prs:
                prs_pmids.append(classification.pmid)
            if classification.has_heritability:
                h2_pmids.append(classification.pmid)
            if classification.has_genetic_correlation:
                rg_pmids.append(classification.pmid)
        
        total_extractions = len(prs_pmids) + len(h2_pmids) + len(rg_pmids)
        current = 0
        
        # Extract PRS data
        for pmid in prs_pmids:
            if pmid in papers_by_pmid:
                extractions = self.prs_extractor.extract(papers_by_pmid[pmid])
                state.extractions.extend([
                    ExtractionResult(pmid=pmid, prs_models=extractions)
                ])
                for ext in extractions:
                    if ext not in state.valid_prs_models:
                        state.valid_prs_models.append(ext)
            current += 1
            if progress_callback:
                progress_callback("extracting", current, total_extractions)
        
        # Extract heritability data
        for pmid in h2_pmids:
            if pmid in papers_by_pmid:
                extractions = self.h2_extractor.extract(papers_by_pmid[pmid])
                for ext in extractions:
                    if ext not in state.valid_heritability:
                        state.valid_heritability.append(ext)
            current += 1
            if progress_callback:
                progress_callback("extracting", current, total_extractions)
        
        # Extract genetic correlation data
        for pmid in rg_pmids:
            if pmid in papers_by_pmid:
                extractions = self.rg_extractor.extract(papers_by_pmid[pmid])
                for ext in extractions:
                    if ext not in state.valid_genetic_correlations:
                        state.valid_genetic_correlations.append(ext)
            current += 1
            if progress_callback:
                progress_callback("extracting", current, total_extractions)
        
        logger.info(
            f"Extracted: {len(state.valid_prs_models)} PRS, "
            f"{len(state.valid_heritability)} h², "
            f"{len(state.valid_genetic_correlations)} rg"
        )
        
        return state
    
    def _validate_data(
        self,
        state: WorkflowState,
        progress_callback: Optional[callable]
    ) -> WorkflowState:
        """Stage 4: Validate all extractions."""
        state.status = "validating"
        
        all_extractions = (
            state.valid_prs_models +
            state.valid_heritability +
            state.valid_genetic_correlations
        )
        
        total = len(all_extractions)
        
        for i, extraction in enumerate(all_extractions):
            validation = self.validator.validate(extraction)
            state.validations.append(validation)
            
            if progress_callback:
                progress_callback("validating", i + 1, total)
        
        # Filter to valid extractions
        valid_prs = []
        valid_h2 = []
        valid_rg = []
        
        for validation in state.validations:
            if validation.status == ValidationStatus.VALID:
                if validation.extraction_type == "prs":
                    # Find original extraction
                    for ext in state.valid_prs_models:
                        if ext.id == validation.extraction_id:
                            valid_prs.append(ext)
                            break
                elif validation.extraction_type == "heritability":
                    for ext in state.valid_heritability:
                        if ext.id == validation.extraction_id:
                            valid_h2.append(ext)
                            break
                elif validation.extraction_type == "genetic_correlation":
                    for ext in state.valid_genetic_correlations:
                        if ext.id == validation.extraction_id:
                            valid_rg.append(ext)
                            break
        
        state.valid_prs_models = valid_prs
        state.valid_heritability = valid_h2
        state.valid_genetic_correlations = valid_rg
        
        # Generate validation report
        report = self.validator.generate_validation_report(state.validations)
        logger.info(f"Validation complete: {report['valid']}/{report['total_validated']} valid")
        
        return state
    
    def _store_results(self, state: WorkflowState):
        """Stage 5: Store results to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        disease_slug = state.disease.lower().replace(" ", "_")[:30]
        
        # Store extracted data
        output_dir = self.data_dir / "extracted_metrics" / disease_slug
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # PRS models
        if state.valid_prs_models:
            prs_file = output_dir / f"prs_models_{timestamp}.json"
            with open(prs_file, "w") as f:
                json.dump(
                    [m.model_dump() for m in state.valid_prs_models],
                    f,
                    indent=2,
                    default=str
                )
            logger.info(f"Saved {len(state.valid_prs_models)} PRS models to {prs_file}")
        
        # Heritability
        if state.valid_heritability:
            h2_file = output_dir / f"heritability_{timestamp}.json"
            with open(h2_file, "w") as f:
                json.dump(
                    [h.model_dump() for h in state.valid_heritability],
                    f,
                    indent=2,
                    default=str
                )
            logger.info(f"Saved {len(state.valid_heritability)} h² estimates to {h2_file}")
        
        # Genetic correlations
        if state.valid_genetic_correlations:
            rg_file = output_dir / f"genetic_correlations_{timestamp}.json"
            with open(rg_file, "w") as f:
                json.dump(
                    [r.model_dump() for r in state.valid_genetic_correlations],
                    f,
                    indent=2,
                    default=str
                )
            logger.info(f"Saved {len(state.valid_genetic_correlations)} rg values to {rg_file}")
        
        # Store validation report
        if state.validations:
            review_validations = self.validator.get_review_queue(state.validations)
            if review_validations:
                review_dir = self.data_dir / "validation_queue" / disease_slug
                review_dir.mkdir(parents=True, exist_ok=True)
                
                review_file = review_dir / f"review_queue_{timestamp}.json"
                with open(review_file, "w") as f:
                    json.dump(
                        [v.model_dump() for v in review_validations],
                        f,
                        indent=2,
                        default=str
                    )
                logger.info(f"Saved {len(review_validations)} items for review to {review_file}")
    
    # =========================================================================
    # LangGraph Integration (Optional)
    # =========================================================================
    
    def build_langgraph(self):
        """
        Build a LangGraph for more sophisticated workflow control.
        
        This provides:
        - Parallel execution of extractors
        - Better error handling
        - Checkpoint/resume capability
        - Visual workflow debugging
        
        Requires: pip install langgraph
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError(
                "LangGraph is not installed. Install with: pip install langgraph"
            )
        
        # Define the workflow graph
        workflow = StateGraph(LiteratureMiningState)
        
        # Add nodes for each stage
        workflow.add_node("search", self._lg_search_node)
        workflow.add_node("classify", self._lg_classify_node)
        workflow.add_node("extract_prs", self._lg_extract_prs_node)
        workflow.add_node("extract_h2", self._lg_extract_h2_node)
        workflow.add_node("extract_rg", self._lg_extract_rg_node)
        workflow.add_node("validate", self._lg_validate_node)
        workflow.add_node("store", self._lg_store_node)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("search")
        workflow.add_edge("search", "classify")
        
        # After classification, run extractors in parallel
        workflow.add_conditional_edges(
            "classify",
            self._lg_route_extractors,
            {
                "extract_all": "extract_prs",
                "extract_prs": "extract_prs",
                "extract_h2": "extract_h2",
                "extract_rg": "extract_rg",
                "skip": "validate"
            }
        )
        
        # Extractors lead to validation
        workflow.add_edge("extract_prs", "extract_h2")
        workflow.add_edge("extract_h2", "extract_rg")
        workflow.add_edge("extract_rg", "validate")
        
        # Validation leads to storage and end
        workflow.add_edge("validate", "store")
        workflow.add_edge("store", END)
        
        self._graph = workflow.compile()
        return self._graph
    
    def _lg_search_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Search PubMed."""
        disease = state["disease"]
        max_papers = state["max_papers"]
        search_type = state.get("search_type", "all")
        
        if search_type == "prs":
            result = self.pubmed_client.search_prs_papers(disease, max_papers)
        elif search_type == "heritability":
            result = self.pubmed_client.search_heritability_papers(disease, max_papers)
        elif search_type == "genetic_correlation":
            result = self.pubmed_client.search_genetic_correlation_papers(disease, max_papers)
        else:
            result = self.pubmed_client.search_prs_papers(disease, max_papers)
        
        papers = self.pubmed_client.fetch_papers(result.pmids)
        state["papers"] = papers
        state["status"] = "searched"
        
        return state
    
    def _lg_classify_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Classify papers."""
        papers = state["papers"]
        classifications = self.classifier.classify_batch(papers)
        state["classifications"] = classifications
        state["status"] = "classified"
        return state
    
    def _lg_route_extractors(self, state: LiteratureMiningState) -> str:
        """Route to appropriate extractors based on classifications."""
        classifications = state.get("classifications", [])
        
        if not classifications:
            return "skip"
        
        has_prs = any(c.has_prs for c in classifications)
        has_h2 = any(c.has_heritability for c in classifications)
        has_rg = any(c.has_genetic_correlation for c in classifications)
        
        if has_prs and has_h2 and has_rg:
            return "extract_all"
        elif has_prs:
            return "extract_prs"
        elif has_h2:
            return "extract_h2"
        elif has_rg:
            return "extract_rg"
        else:
            return "skip"
    
    def _lg_extract_prs_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Extract PRS data."""
        papers_by_pmid = {p.pmid: p for p in state["papers"]}
        prs_pmids = [c.pmid for c in state["classifications"] if c.has_prs]
        
        extractions = []
        for pmid in prs_pmids:
            if pmid in papers_by_pmid:
                exts = self.prs_extractor.extract(papers_by_pmid[pmid])
                extractions.extend(exts)
        
        state["prs_extractions"] = extractions
        return state
    
    def _lg_extract_h2_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Extract heritability data."""
        papers_by_pmid = {p.pmid: p for p in state["papers"]}
        h2_pmids = [c.pmid for c in state["classifications"] if c.has_heritability]
        
        extractions = []
        for pmid in h2_pmids:
            if pmid in papers_by_pmid:
                exts = self.h2_extractor.extract(papers_by_pmid[pmid])
                extractions.extend(exts)
        
        state["h2_extractions"] = extractions
        return state
    
    def _lg_extract_rg_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Extract genetic correlation data."""
        papers_by_pmid = {p.pmid: p for p in state["papers"]}
        rg_pmids = [c.pmid for c in state["classifications"] if c.has_genetic_correlation]
        
        extractions = []
        for pmid in rg_pmids:
            if pmid in papers_by_pmid:
                exts = self.rg_extractor.extract(papers_by_pmid[pmid])
                extractions.extend(exts)
        
        state["rg_extractions"] = extractions
        return state
    
    def _lg_validate_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Validate all extractions."""
        all_extractions = (
            state.get("prs_extractions", []) +
            state.get("h2_extractions", []) +
            state.get("rg_extractions", [])
        )
        
        validations = []
        valid_prs = []
        valid_h2 = []
        valid_rg = []
        review_queue = []
        
        for extraction in all_extractions:
            validation = self.validator.validate(extraction)
            validations.append(validation)
            
            if validation.status == ValidationStatus.VALID:
                if isinstance(extraction, PRSModelExtraction):
                    valid_prs.append(extraction)
                elif isinstance(extraction, HeritabilityExtraction):
                    valid_h2.append(extraction)
                elif isinstance(extraction, GeneticCorrelationExtraction):
                    valid_rg.append(extraction)
            elif validation.status == ValidationStatus.NEEDS_REVIEW:
                review_queue.append(validation)
        
        state["validations"] = validations
        state["valid_prs"] = valid_prs
        state["valid_h2"] = valid_h2
        state["valid_rg"] = valid_rg
        state["review_queue"] = review_queue
        state["status"] = "validated"
        
        return state
    
    def _lg_store_node(self, state: LiteratureMiningState) -> LiteratureMiningState:
        """LangGraph node: Store results."""
        # Convert to WorkflowState format for storage
        workflow_state = WorkflowState(
            disease=state["disease"],
            valid_prs_models=state.get("valid_prs", []),
            valid_heritability=state.get("valid_h2", []),
            valid_genetic_correlations=state.get("valid_rg", []),
            validations=state.get("validations", [])
        )
        
        self._store_results(workflow_state)
        
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        
        return state


# ============================================================================
# Convenience Functions
# ============================================================================

def mine_literature(
    disease: str,
    max_papers: int = 50,
    search_type: str = "all",
    use_langgraph: bool = False
) -> WorkflowState:
    """
    Convenience function to run literature mining.
    
    LLM configuration is managed centrally in src/core/llm_config.py
    
    Args:
        disease: Disease/trait to search
        max_papers: Maximum papers to process
        search_type: "all", "prs", "heritability", or "genetic_correlation"
        use_langgraph: Whether to use LangGraph orchestration
    
    Returns:
        WorkflowState with results
    
    Example:
        >>> from src.modules.literature import mine_literature
        >>> results = mine_literature("Alzheimer's Disease", max_papers=20)
        >>> print(f"Found {len(results.valid_prs_models)} PRS models")
    """
    workflow = LiteratureMiningWorkflow()
    
    if use_langgraph and LANGGRAPH_AVAILABLE:
        graph = workflow.build_langgraph()
        initial_state: LiteratureMiningState = {
            "disease": disease,
            "max_papers": max_papers,
            "search_type": search_type,
            "papers": [],
            "current_index": 0,
            "classifications": [],
            "prs_extractions": [],
            "h2_extractions": [],
            "rg_extractions": [],
            "validations": [],
            "valid_prs": [],
            "valid_h2": [],
            "valid_rg": [],
            "review_queue": [],
            "status": "initialized",
            "errors": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        final_state = graph.invoke(initial_state)
        
        # Convert to WorkflowState
        return WorkflowState(
            disease=disease,
            valid_prs_models=final_state.get("valid_prs", []),
            valid_heritability=final_state.get("valid_h2", []),
            valid_genetic_correlations=final_state.get("valid_rg", []),
            status=final_state.get("status", "unknown")
        )
    else:
        return workflow.run(
            disease=disease,
            max_papers=max_papers,
            search_type=search_type
        )


async def mine_literature_async(
    disease: str,
    max_papers: int = 50,
    search_type: str = "all"
) -> WorkflowState:
    """
    Async version of literature mining.
    
    Useful for web server integration where non-blocking is important.
    """
    import asyncio
    
    # Run in thread pool since PubMed/OpenAI clients are synchronous
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: mine_literature(disease, max_papers, search_type)
    )
    return result
