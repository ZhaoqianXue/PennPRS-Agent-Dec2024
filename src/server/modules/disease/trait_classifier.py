"""
Trait Classification Module

Provides both a simple keyword-based classifier (fast fallback) and 
integration with the Agentic Study Classifier (accurate, API-based).

Use classify_trait() for simple cases or classify_study_agentic() for 
full API-based classification.
"""

from src.server.core.llm_config import get_llm  # Centralized LLM config
from src.server.core.system_prompts import TRAIT_CLASSIFIER_PROMPT_TEMPLATE
import json
import logging

logger = logging.getLogger(__name__)


def classify_trait(trait_name: str, sample_info: str = None) -> dict:
    """
    Use LLM to classify a GWAS trait and extract ancestry information.
    
    This is a fast, heuristic-based classifier for when you don't have
    a study ID. For more accurate classification with a study ID, use
    classify_study_agentic() instead.
    
    Args:
        trait_name: Name of the trait (e.g., "Alzheimer's disease", "LDL cholesterol levels")
        sample_info: Optional sample information string (e.g., "472,868 European ancestry individuals")
    
    Returns:
        dict with keys:
            - trait_type: "Binary" or "Continuous"
            - ancestry: "EUR", "AFR", "EAS", "SAS", or "AMR"
            - confidence: "high", "medium", or "low"
            - reasoning: Brief explanation of the classification
    """
    llm = get_llm("trait_classifier")
    
    sample_info_section = f"Sample Info: {sample_info}" if sample_info else ""
    prompt = TRAIT_CLASSIFIER_PROMPT_TEMPLATE.format(
        trait_name=trait_name,
        sample_info_section=sample_info_section
    )
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Handle markdown code blocks
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        result = json.loads(content)
        return {
            "trait_type": result.get("trait_type", "Continuous"),
            "ancestry": result.get("ancestry", "EUR"),
            "confidence": result.get("confidence", "medium"),
            "reasoning": result.get("reasoning", "")
        }
    except Exception as e:
        # Fallback: simple heuristic
        return _fallback_classification(trait_name, sample_info, str(e))


def _fallback_classification(trait_name: str, sample_info: str = None, error_msg: str = "") -> dict:
    """
    Fallback classification using keyword matching when LLM fails.
    """
    trait_lower = trait_name.lower()
    sample_lower = (sample_info or "").lower()
    
    # Check for Continuous Exceptions first (Family History / Proxy)
    if "family history" in trait_lower or "proxy" in trait_lower or "gwax" in trait_lower:
        is_binary = False
        reasoning = "Continuous (Proxy/Family History)"
    else:
        # Trait type detection
        disease_keywords = [
            "disease", "disorder", "cancer", "syndrome", "diabetes", "alzheimer", "parkinson",
            "schizophrenia", "depression", "infection", "failure", "infarction", "stroke",
            "carcinoma", "leukemia", "arthritis", "asthma", "obesity"
        ]
        is_binary = any(kw in trait_lower for kw in disease_keywords)
        reasoning = "Binary (Disease Keyword)" if is_binary else "Continuous (Default)"
    
    # Ancestry detection
    ancestry = "EUR"  # Default
    if "african" in sample_lower or "afro" in sample_lower:
        ancestry = "AFR"
    elif any(kw in sample_lower for kw in ["east asian", "japanese", "chinese", "korean"]):
        ancestry = "EAS"
    elif any(kw in sample_lower for kw in ["south asian", "indian"]):
        ancestry = "SAS"
    elif any(kw in sample_lower for kw in ["hispanic", "latino", "latin american"]):
        ancestry = "AMR"
    
    return {
        "trait_type": "Binary" if is_binary else "Continuous",
        "ancestry": ancestry,
        "confidence": "low",
        "reasoning": f"Fallback heuristic: {reasoning} (LLM error: {error_msg})" if error_msg else f"Fallback heuristic: {reasoning}"
    }


def classify_study_agentic(study_id: str) -> dict:
    """
    Agentic classification using GWAS Catalog API data.
    
    This is the recommended method when you have a study ID.
    It fetches real study metadata from the API and uses LLM
    to make an informed classification decision.
    
    Args:
        study_id: GWAS Catalog study accession (e.g., GCST90012877)
    
    Returns:
        dict with keys:
            - study_id: The study accession ID
            - trait_type: "Binary" or "Continuous"
            - sample_size: Total sample size (N)
            - n_cases: Number of cases (for Binary traits, else None)
            - n_controls: Number of controls (for Binary traits, else None)
            - neff: Effective sample size for Binary (else None)
            - ancestry: "EUR", "AFR", "EAS", "SAS", or "AMR"
            - confidence: "high", "medium", or "low"
            - reasoning: Brief explanation of the classification
    """
    try:
        from src.server.modules.disease.agentic_study_classifier import classify_trait_from_study
        return classify_trait_from_study(study_id)
    except ImportError as e:
        logger.error(f"Agentic classifier not available: {e}")
        # Fallback to fetching minimal data and using simple classifier
        return _fallback_classify_study(study_id)
    except Exception as e:
        logger.error(f"Agentic classification failed for {study_id}: {e}")
        return _fallback_classify_study(study_id)


def _fallback_classify_study(study_id: str) -> dict:
    """
    Fallback study classification when agentic classifier fails.
    Fetches basic data from API and uses simple heuristics.
    """
    import requests
    
    try:
        url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            trait = data.get("diseaseTrait", {}).get("trait", "Unknown")
            sample_info = data.get("initialSampleSize", "")
            
            # Extract sample size
            sample_size = 0
            ancestries = data.get("ancestries", [])
            if ancestries:
                sample_size = ancestries[0].get("numberOfIndividuals", 0)
            
            # Use simple classifier
            simple_result = _fallback_classification(trait, sample_info)
            
            return {
                "study_id": study_id,
                "trait_type": simple_result["trait_type"],
                "sample_size": sample_size,
                "n_cases": None,
                "n_controls": None,
                "neff": None,
                "ancestry": simple_result["ancestry"],
                "confidence": "low",
                "reasoning": f"Fallback: {simple_result['reasoning']}"
            }
    except Exception as e:
        logger.error(f"Fallback classification failed for {study_id}: {e}")
    
    # Ultimate fallback
    return {
        "study_id": study_id,
        "trait_type": "Continuous",
        "sample_size": 0,
        "n_cases": None,
        "n_controls": None,
        "neff": None,
        "ancestry": "EUR",
        "confidence": "low",
        "reasoning": "Unable to classify study"
    }
