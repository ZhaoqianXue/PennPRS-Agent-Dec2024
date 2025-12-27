"""
Agentic Study Classifier

Uses GWAS Catalog REST API to fetch study metadata, then leverages LLM 
to intelligently classify whether a study is Binary or Continuous,
and extract accurate sample size information.

This is a true "agentic" approach rather than simple keyword matching.
"""

import json
import requests
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
import logging
from functools import lru_cache
import time

from src.core.llm_config import get_llm  # Centralized LLM config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class StudyClassification(BaseModel):
    """Structured output for study classification."""
    study_id: str = Field(description="The GWAS study accession ID (e.g., GCST90012877)")
    trait_type: Literal["Binary", "Continuous"] = Field(
        description="Whether the trait is Binary (disease/case-control) or Continuous (quantitative measurement)"
    )
    sample_size: int = Field(description="Total sample size (N)")
    n_cases: Optional[int] = Field(default=None, description="Number of cases (for Binary traits)")
    n_controls: Optional[int] = Field(default=None, description="Number of controls (for Binary traits)")
    neff: Optional[float] = Field(
        default=None, 
        description="Effective sample size for Binary traits: 4 / (1/n_cases + 1/n_controls)"
    )
    ancestry: str = Field(default="EUR", description="Primary ancestry code (EUR, AFR, EAS, SAS, AMR)")
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level of the classification"
    )
    reasoning: str = Field(description="Brief explanation of the classification decision")


class GWASStudyData(BaseModel):
    """Raw data fetched from GWAS Catalog API."""
    study_id: str
    trait: str
    initial_sample_size: str
    replication_sample_size: Optional[str] = None
    ancestries: List[Dict[str, Any]] = []
    publication_title: Optional[str] = None
    full_api_response: Dict[str, Any] = {}


class ClassifierState(BaseModel):
    """State for the LangGraph workflow."""
    study_id: str
    study_data: Optional[GWASStudyData] = None
    classification: Optional[StudyClassification] = None
    error: Optional[str] = None


# ============================================================================
# GWAS Catalog API Client (Async for Speed)
# ============================================================================

class GWASCatalogAPIClient:
    """Async client for GWAS Catalog REST API."""
    
    BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api"
    
    @staticmethod
    async def fetch_study_async(study_id: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Fetch study data asynchronously."""
        url = f"{GWASCatalogAPIClient.BASE_URL}/studies/{study_id}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Failed to fetch {study_id}: HTTP {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching {study_id}: {e}")
            return {}
    
    @staticmethod
    def fetch_study_sync(study_id: str) -> Dict[str, Any]:
        """Fetch study data synchronously (fallback)."""
        url = f"{GWASCatalogAPIClient.BASE_URL}/studies/{study_id}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch {study_id}: HTTP {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching {study_id}: {e}")
            return {}

    @staticmethod
    async def fetch_associations_async(study_id: str, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Fetch study associations to check for OR vs Beta."""
        url = f"{GWASCatalogAPIClient.BASE_URL}/studies/{study_id}/associations?projection=associationByStudy"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract embedded associations
                    return data.get("_embedded", {}).get("associations", [])[:5]  # Limit to 5 for speed
                return []
        except Exception as e:
            logger.error(f"Error fetching associations for {study_id}: {e}")
            return []


# ============================================================================
# Heuristic Pre-Classification (Skip LLM when possible)
# ============================================================================

import re

def parse_sample_description(sample_desc: str) -> Dict[str, Any]:
    """
    Parse sample description to extract cases, controls, and total N.
    Returns parsed data if confident, None if ambiguous (needs LLM).
    """
    if not sample_desc:
        return None
    
    sample_lower = sample_desc.lower()
    
    # Pattern 1: "N cases, M controls"
    cases_pattern = r'([\d,]+)\s*(?:european\s*ancestry\s*)?(?:\w+\s*)?cases'
    controls_pattern = r'([\d,]+)\s*(?:european\s*ancestry\s*)?(?:\w+\s*)?controls'
    
    cases_match = re.search(cases_pattern, sample_lower)
    controls_match = re.search(controls_pattern, sample_lower)
    
    if cases_match and controls_match:
        n_cases = int(cases_match.group(1).replace(',', ''))
        n_controls = int(controls_match.group(1).replace(',', ''))
        return {
            "type": "binary",
            "n_cases": n_cases,
            "n_controls": n_controls,
            "total_n": n_cases + n_controls,
            "neff": 4.0 / (1.0/n_cases + 1.0/n_controls)
        }
    
    # Pattern 2: "N individuals" or "N European ancestry individuals" (no cases/controls)
    # Supports: "321,047 European ancestry individuals"
    individuals_pattern = r'([\d,]+)\s+(?:\w+\s+)*individuals'
    individuals_match = re.search(individuals_pattern, sample_lower)
    
    if individuals_match and 'cases' not in sample_lower and 'controls' not in sample_lower:
        total_n = int(individuals_match.group(1).replace(',', ''))
        return {
            "type": "continuous",
            "total_n": total_n,
            "n_cases": None,
            "n_controls": None,
            "neff": None
        }
    
    return None  # Ambiguous, needs LLM


def detect_effect_type(associations: List[Dict[str, Any]]) -> Optional[str]:
    """
    Detect whether study uses Beta (Continuous) or OR (Binary) from associations.
    This is the most reliable signal.
    """
    has_beta = False
    has_or = False
    
    for a in associations[:5]:
        if a.get("betaNum") is not None:
            has_beta = True
        if a.get("orPerCopyNum") is not None:
            has_or = True
    
    if has_beta and not has_or:
        return "continuous"
    if has_or and not has_beta:
        return "binary"
    
    return None  # Ambiguous or mixed


def extract_ancestry(ancestries: List[Dict[str, Any]], sample_desc: str) -> str:
    """Extract primary ancestry code."""
    # Try from ancestries data
    if ancestries:
        for anc in ancestries:
            groups = anc.get("ancestralGroups", [])
            for g in groups:
                group_name = g.get("ancestralGroup", "").lower()
                if "european" in group_name:
                    return "EUR"
                if "african" in group_name:
                    return "AFR"
                if "east asian" in group_name:
                    return "EAS"
                if "south asian" in group_name:
                    return "SAS"
                if "hispanic" in group_name or "latin" in group_name:
                    return "AMR"
    
    # Fallback: parse from sample description
    sample_lower = sample_desc.lower() if sample_desc else ""
    if "european" in sample_lower or "british" in sample_lower:
        return "EUR"
    if "african" in sample_lower:
        return "AFR"
    if "east asian" in sample_lower or "japanese" in sample_lower or "chinese" in sample_lower:
        return "EAS"
    if "south asian" in sample_lower or "indian" in sample_lower:
        return "SAS"
    if "hispanic" in sample_lower or "latino" in sample_lower:
        return "AMR"
    
    return "EUR"  # Default


def try_heuristic_classification(
    study_id: str,
    trait: str,
    sample_desc: str,
    ancestries: List[Dict[str, Any]],
    associations: List[Dict[str, Any]]
) -> Optional[StudyClassification]:
    """
    Try to classify without LLM using heuristics.
    Returns classification if confident, None if LLM is needed.
    """
    # 1. Detect effect type from associations (most reliable)
    effect_type = detect_effect_type(associations)
    
    # 2. Parse sample description
    sample_parsed = parse_sample_description(sample_desc)
    
    # 3. Check for family history / proxy (always continuous)
    trait_lower = trait.lower()
    is_proxy = "family history" in trait_lower or "proxy" in trait_lower
    
    # 4. Determine classification
    ancestry = extract_ancestry(ancestries, sample_desc)
    
    # Case A: Effect type is Beta (OR not present) → Continuous
    if effect_type == "continuous":
        total_n = sample_parsed["total_n"] if sample_parsed else 0
        if not total_n:
            # Try to get from ancestries
            if ancestries:
                total_n = ancestries[0].get("numberOfIndividuals", 0)
        
        return StudyClassification(
            study_id=study_id,
            trait_type="Continuous",
            sample_size=total_n,
            n_cases=None,
            n_controls=None,
            neff=None,
            ancestry=ancestry,
            confidence="high",
            reasoning="Association effects use Beta (linear regression), indicating continuous trait analysis"
        )
    
    # Case B: Effect type is OR AND sample has cases/controls → Binary
    if effect_type == "binary" and sample_parsed and sample_parsed["type"] == "binary":
        return StudyClassification(
            study_id=study_id,
            trait_type="Binary",
            sample_size=sample_parsed["total_n"],
            n_cases=sample_parsed["n_cases"],
            n_controls=sample_parsed["n_controls"],
            neff=sample_parsed["neff"],
            ancestry=ancestry,
            confidence="high",
            reasoning="Association effects use OR (logistic regression) with explicit cases/controls"
        )
    
    # Case C: Clear cases/controls in sample desc, no effect data but not proxy
    if sample_parsed and sample_parsed["type"] == "binary" and not is_proxy:
        return StudyClassification(
            study_id=study_id,
            trait_type="Binary",
            sample_size=sample_parsed["total_n"],
            n_cases=sample_parsed["n_cases"],
            n_controls=sample_parsed["n_controls"],
            neff=sample_parsed["neff"],
            ancestry=ancestry,
            confidence="medium",
            reasoning="Sample description has explicit cases/controls"
        )
    
    # Case D: Clear individuals only (no cases/controls) → Continuous
    if sample_parsed and sample_parsed["type"] == "continuous":
        return StudyClassification(
            study_id=study_id,
            trait_type="Continuous",
            sample_size=sample_parsed["total_n"],
            n_cases=None,
            n_controls=None,
            neff=None,
            ancestry=ancestry,
            confidence="medium",
            reasoning="Sample description shows total individuals without case/control split"
        )
    
    # Cannot determine confidently, need LLM
    return None


# ============================================================================
# LLM-based Classifier
# ============================================================================

SYSTEM_PROMPT = """You are an expert geneticist and biostatistician specializing in GWAS (Genome-Wide Association Studies).
Your task is to analyze GWAS study metadata and determine:
1. Whether the trait is Binary (disease/case-control) or Continuous (quantitative measurement)
2. The accurate sample size components

CRITICAL RULES FOR CLASSIFICATION:

## PRIMARY SIGNAL: Association Effect Type (MOST IMPORTANT!)
Look at the "association_effects" field in the API context:
- **If Beta values are reported (e.g., "Beta: 0.077")** → Study was analyzed as **CONTINUOUS** (linear regression)
- **If OR values are reported (e.g., "OR: 1.25")** → Study was analyzed as **BINARY** (logistic regression)
This is the most reliable indicator! Effect type overrides trait name.

## Binary Traits (Report N_cases, N_controls, and calculate Neff)
- Association effect is OR (Odds Ratio)
- Sample description contains "cases" AND "controls"
- True case/control diseases without family history proxy design

## Continuous Traits (Report total N only)
- Association effect is Beta coefficient
- Quantitative measurements (e.g., "Height", "BMI", "Blood pressure")
- Levels, concentrations, counts, ratios
- **CRITICAL EXCEPTION**: "Family history" studies, "proxy-cases", "GWAX" analyses use Beta effects and should be classified as CONTINUOUS, even if the underlying phenotype is a disease
- Any study where sample description shows only total N without case/control split

## Ancestry Mapping
- European, British, Finnish, German, French → EUR
- African, African American, Afro-Caribbean → AFR
- East Asian, Japanese, Chinese, Korean → EAS
- South Asian, Indian, Pakistani → SAS
- Hispanic, Latino, Latin American, Admixed American → AMR
- Multiple ancestries → Use the dominant one

## Sample Size Extraction
- Parse the initialSampleSize field carefully
- For Binary: Extract N_cases and N_controls, calculate Neff = 4 / (1/N_cases + 1/N_controls)
- For Continuous: Use total N (look for "individuals" count)

Respond with a valid JSON object matching the required schema."""


def create_classifier_chain():
    """Create the LLM classifier chain with structured output."""
    
    # Get LLM from centralized config (already configured with JSON mode)
    llm = get_llm("agentic_classifier")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", """Analyze this GWAS study and classify it:

Study ID: {study_id}
Trait: {trait}
Initial Sample Size: {initial_sample_size}
Replication Sample Size: {replication_sample_size}
Ancestries: {ancestries}
Publication Title: {publication_title}

Additional Context (raw API response excerpt):
{api_context}

Provide your classification as a JSON object with these fields:
- study_id: string
- trait_type: "Binary" or "Continuous"
- sample_size: integer (total N)
- n_cases: integer or null
- n_controls: integer or null
- neff: float or null (only for Binary: 4 / (1/n_cases + 1/n_controls))
- ancestry: "EUR", "AFR", "EAS", "SAS", or "AMR"
- confidence: "high", "medium", or "low"
- reasoning: string explaining your decision""")
    ])
    
    return prompt | llm


# ============================================================================
# LangGraph Workflow Nodes
# ============================================================================

async def fetch_study_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Fetch study data from GWAS Catalog API."""
    study_id = state["study_id"]
    
    t_start = time.time()
    
    async with aiohttp.ClientSession() as session:
        # STEP 1: Fetch study data first (faster, ~1s)
        study_data = await GWASCatalogAPIClient.fetch_study_async(study_id, session)
        
        if not study_data:
            return {"error": f"Failed to fetch study data for {study_id}"}
        
        initial_sample = study_data.get("initialSampleSize", "").lower()
        ancestries = study_data.get("ancestries", [])
        trait = study_data.get("diseaseTrait", {}).get("trait", "Unknown")
        
        # STEP 2: Quick check - is sample description clear enough?
        # If we can determine type from sample desc alone, skip associations fetch
        sample_parsed = parse_sample_description(initial_sample)
        trait_lower = trait.lower()
        is_proxy = "family history" in trait_lower or "proxy" in trait_lower
        
        associations = []
        need_associations = False
        
        # Cases where we need associations:
        # - Sample desc is ambiguous
        # - Have cases/controls but it's a proxy study (need to verify with Beta)
        if sample_parsed is None:
            need_associations = True
        elif sample_parsed["type"] == "binary" and is_proxy:
            need_associations = True  # Proxy studies use Beta even with case/control language
        
        if need_associations:
            associations = await GWASCatalogAPIClient.fetch_associations_async(study_id, session)
    
    fetch_time = time.time() - t_start
    logger.info(f"[Timing] API fetch for {study_id}: {fetch_time:.3f}s (assoc fetched: {need_associations})")
    
    # ============================================================
    # TRY HEURISTIC CLASSIFICATION FIRST (Skip LLM if confident)
    # ============================================================
    t_heuristic = time.time()
    heuristic_result = try_heuristic_classification(
        study_id=study_id,
        trait=trait,
        sample_desc=initial_sample,
        ancestries=ancestries,
        associations=associations
    )
    
    if heuristic_result:
        logger.info(f"[Timing] Heuristic classification (skipped LLM): {time.time() - t_heuristic:.3f}s")
        # Return directly with classification, skip LLM node
        return {
            "study_data": None,  # Not needed
            "classification": heuristic_result,
            "skip_llm": True
        }
    
    # ============================================================
    # HEURISTIC FAILED - Prepare data for LLM
    # ============================================================
    replication_sample = study_data.get("replicationSampleSize", "")
    pub_info = study_data.get("publicationInfo", {})
    pub_title = pub_info.get("title", "")
    
    # Simplified context for LLM (minimal info for speed)
    assoc_effects = []
    for a in associations[:3]:
        if a.get("orPerCopyNum"):
            assoc_effects.append(f"OR={a.get('orPerCopyNum')}")
        if a.get("betaNum"):
            assoc_effects.append(f"Beta={a.get('betaNum')}")
    
    parsed_data = GWASStudyData(
        study_id=study_id,
        trait=trait,
        initial_sample_size=initial_sample,
        replication_sample_size=replication_sample,
        ancestries=ancestries,
        publication_title=pub_title,
        full_api_response={"effects": assoc_effects}  # Minimal context
    )
    
    return {"study_data": parsed_data, "skip_llm": False}


async def classify_with_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Use LLM to classify the study."""
    study_data: GWASStudyData = state.get("study_data")
    
    if not study_data:
        return {"error": "No study data available for classification"}
    
    t_start = time.time()
    
    chain = create_classifier_chain()
    
    # Prepare inputs
    ancestries_str = json.dumps(study_data.ancestries, indent=2) if study_data.ancestries else "Not specified"
    api_context_str = json.dumps(study_data.full_api_response, indent=2)
    
    try:
        response = await chain.ainvoke({
            "study_id": study_data.study_id,
            "trait": study_data.trait,
            "initial_sample_size": study_data.initial_sample_size,
            "replication_sample_size": study_data.replication_sample_size or "NA",
            "ancestries": ancestries_str,
            "publication_title": study_data.publication_title or "Not available",
            "api_context": api_context_str
        })
        
        logger.info(f"[Timing] LLM classification for {study_data.study_id}: {time.time() - t_start:.3f}s")
        
        # Parse response
        result = json.loads(response.content)
        
        classification = StudyClassification(
            study_id=result.get("study_id", study_data.study_id),
            trait_type=result.get("trait_type", "Continuous"),
            sample_size=result.get("sample_size", 0),
            n_cases=result.get("n_cases"),
            n_controls=result.get("n_controls"),
            neff=result.get("neff"),
            ancestry=result.get("ancestry", "EUR"),
            confidence=result.get("confidence", "medium"),
            reasoning=result.get("reasoning", "")
        )
        
        return {"classification": classification}
        
    except Exception as e:
        logger.error(f"LLM classification failed: {e}")
        return {"error": f"Classification failed: {str(e)}"}


def should_continue(state: Dict[str, Any]) -> str:
    """Conditional edge: Check if we should continue to classification."""
    if state.get("error"):
        return "end"
    
    # Skip LLM if heuristic classification already succeeded
    if state.get("skip_llm") or state.get("classification"):
        return "end"
    
    if state.get("study_data"):
        return "classify"
    
    return "end"


def finalize(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Finalize and return results."""
    return state


# ============================================================================
# Build LangGraph Workflow
# ============================================================================

def build_classifier_graph():
    """Build the LangGraph workflow for study classification."""
    
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("fetch_data", fetch_study_data)
    workflow.add_node("classify", classify_with_llm)
    workflow.add_node("finalize", finalize)
    
    # Set entry point
    workflow.set_entry_point("fetch_data")
    
    # Add edges
    workflow.add_conditional_edges(
        "fetch_data",
        should_continue,
        {
            "classify": "classify",
            "end": "finalize"
        }
    )
    workflow.add_edge("classify", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# ============================================================================
# Main API Functions
# ============================================================================

# Global cached graph
_classifier_graph = None

def get_classifier_graph():
    """Get or create the classifier graph (singleton)."""
    global _classifier_graph
    if _classifier_graph is None:
        _classifier_graph = build_classifier_graph()
    return _classifier_graph


async def classify_study_async(study_id: str) -> StudyClassification:
    """
    Asynchronously classify a GWAS study.
    
    Args:
        study_id: GWAS Catalog study accession (e.g., GCST90012877)
    
    Returns:
        StudyClassification with trait_type, sample_size, ancestry, etc.
    """
    graph = get_classifier_graph()
    
    result = await graph.ainvoke({"study_id": study_id})
    
    if result.get("error"):
        # Return a default classification with error info
        return StudyClassification(
            study_id=study_id,
            trait_type="Continuous",
            sample_size=0,
            ancestry="EUR",
            confidence="low",
            reasoning=f"Classification failed: {result.get('error')}"
        )
    
    return result.get("classification")


def classify_study_sync(study_id: str) -> StudyClassification:
    """
    Synchronously classify a GWAS study (wrapper for async).
    
    Args:
        study_id: GWAS Catalog study accession (e.g., GCST90012877)
    
    Returns:
        StudyClassification with trait_type, sample_size, ancestry, etc.
    """
    return asyncio.run(classify_study_async(study_id))


async def classify_studies_batch_async(study_ids: List[str], max_concurrent: int = 5) -> List[StudyClassification]:
    """
    Classify multiple studies in parallel with concurrency limit.
    
    Args:
        study_ids: List of GWAS Catalog study accessions
        max_concurrent: Maximum number of concurrent classifications
    
    Returns:
        List of StudyClassification objects
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def classify_with_limit(study_id: str) -> StudyClassification:
        async with semaphore:
            return await classify_study_async(study_id)
    
    tasks = [classify_with_limit(sid) for sid in study_ids]
    results = await asyncio.gather(*tasks)
    
    return results


# ============================================================================
# Simple API for Integration
# ============================================================================

def classify_trait_from_study(study_id: str) -> dict:
    """
    Simple API to classify a study - returns a dict for easy integration.
    
    This is the main function to use from other modules.
    
    Args:
        study_id: GWAS Catalog study accession (e.g., GCST90012877)
    
    Returns:
        dict with keys: trait_type, sample_size, n_cases, n_controls, neff, ancestry, confidence, reasoning
    """
    try:
        classification = classify_study_sync(study_id)
        return classification.model_dump()
    except Exception as e:
        logger.error(f"Failed to classify study {study_id}: {e}")
        return {
            "study_id": study_id,
            "trait_type": "Continuous",
            "sample_size": 0,
            "n_cases": None,
            "n_controls": None,
            "neff": None,
            "ancestry": "EUR",
            "confidence": "low",
            "reasoning": f"Classification failed: {str(e)}"
        }


# ============================================================================
# CLI Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    
    test_ids = [
        "GCST90012877",  # Alzheimer's + family history (should be Continuous)
        "GCST006979",    # Major depressive disorder (should be Binary)
        "GCST007429",    # Lung function FVC (should be Continuous)
    ]
    
    if len(sys.argv) > 1:
        test_ids = sys.argv[1:]
    
    print("=" * 60)
    print("Agentic Study Classifier - Test Run")
    print("=" * 60)
    
    for study_id in test_ids:
        print(f"\nClassifying: {study_id}")
        print("-" * 40)
        
        t_start = time.time()
        result = classify_trait_from_study(study_id)
        elapsed = time.time() - t_start
        
        print(f"Trait Type: {result['trait_type']}")
        print(f"Sample Size: {result['sample_size']:,}")
        if result['n_cases']:
            print(f"N Cases: {result['n_cases']:,}")
        if result['n_controls']:
            print(f"N Controls: {result['n_controls']:,}")
        if result['neff']:
            print(f"Neff: {result['neff']:,.0f}")
        print(f"Ancestry: {result['ancestry']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Time: {elapsed:.2f}s")
