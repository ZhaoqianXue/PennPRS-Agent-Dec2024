"""
Trait Classification Module

Uses LLM to classify GWAS traits as Binary (disease/case-control) or Continuous (quantitative measurement),
and extracts ancestry information from sample descriptions.
"""

from langchain_openai import ChatOpenAI
import json


def classify_trait(trait_name: str, sample_info: str = None) -> dict:
    """
    Use LLM to classify a GWAS trait and extract ancestry information.
    
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
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
    
    prompt = f"""Analyze the following GWAS trait and sample information.

Trait Name: {trait_name}
{f"Sample Info: {sample_info}" if sample_info else ""}

Tasks:
1. Classify the trait as "Binary" (disease/case-control study) or "Continuous" (quantitative trait/measurement)
2. Extract the primary ancestry from the sample info

Rules for Trait Type:
- Diseases, disorders, syndromes, conditions → Binary
- Measurements, levels, counts, ratios → Continuous

Rules for Ancestry (use these codes):
- European, British, Finnish → EUR
- African, African American → AFR
- East Asian, Japanese, Chinese, Korean → EAS
- South Asian, Indian → SAS
- Hispanic, Latino, Admixed American → AMR
- If multiple ancestries or unclear → EUR (most common default)

Respond with ONLY a JSON object in this exact format:
{{"trait_type": "Binary" or "Continuous", "ancestry": "EUR" or "AFR" or "EAS" or "SAS" or "AMR", "confidence": "high" or "medium" or "low", "reasoning": "brief explanation"}}"""
    
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
    
    # Trait type detection
    disease_keywords = [
        "disease", "disorder", "cancer", "syndrome", "diabetes", "alzheimer", "parkinson",
        "schizophrenia", "depression", "infection", "failure", "infarction", "stroke",
        "carcinoma", "leukemia", "arthritis", "asthma", "obesity"
    ]
    is_binary = any(kw in trait_lower for kw in disease_keywords)
    
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
        "reasoning": f"Fallback heuristic classification (LLM error: {error_msg})" if error_msg else "Fallback heuristic classification"
    }
