"""
Trait Synonym Expander Service.

Provides semantic expansion of trait queries to include synonyms, alternative names,
and semantically equivalent terms. Uses LLM to generate comprehensive trait query variations.

This service is used by all Module 3 tools to ensure comprehensive trait coverage:
- prs_model_pgscatalog_search
- genetic_graph_get_neighbors
- genetic_graph_verify_study_power
- genetic_graph_validate_mechanism
- prs_model_domain_knowledge
- prs_model_performance_landscape
- pennprs_train_model
"""
import logging
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.server.core.llm_config import get_llm

logger = logging.getLogger(__name__)


class TraitSynonym(BaseModel):
    """A synonym or alternative name for a trait."""
    synonym: str = Field(..., description="Alternative name or synonym for the trait")
    relationship: str = Field(..., description="Relationship type: exact_synonym, broader_term, narrower_term, related_term, icd10_code, efo_id, or other")
    confidence: str = Field(..., description="Confidence level: High, Moderate, or Low")
    rationale: Optional[str] = Field(None, description="Brief explanation of why this is a synonym")


class TraitExpansionResult(BaseModel):
    """Result of trait synonym expansion."""
    original_query: str
    expanded_queries: List[str] = Field(..., description="List of expanded query terms including original")
    synonyms: List[TraitSynonym] = Field(..., description="List of identified synonyms with metadata")
    method: str = Field(..., description="Expansion method: llm, cache, or none")
    confidence: str = Field(..., description="Overall confidence: High, Moderate, or Low")


class TraitSynonymExpander:
    """
    Service for expanding trait queries with synonyms and semantically equivalent terms.
    
    Uses LLM to generate comprehensive trait variations, ensuring that queries like
    "Breast cancer" also match "Malignant neoplasm of breast" and vice versa.
    """
    
    def __init__(self):
        """Initialize the trait synonym expander."""
        self._cache: Dict[str, TraitExpansionResult] = {}
        self._llm = None
    
    def _get_llm(self):
        """Lazy load LLM."""
        if self._llm is None:
            self._llm = get_llm("disease_workflow")
        return self._llm
    
    def expand_trait_query(
        self,
        trait_query: str,
        *,
        max_synonyms: int = 10,
        include_icd10: bool = True,
        include_efo: bool = True,
        include_related: bool = True
    ) -> TraitExpansionResult:
        """
        Expand a trait query with synonyms and semantically equivalent terms.
        
        This method uses LLM to generate comprehensive trait variations, including:
        - Exact synonyms (e.g., "Breast cancer" <-> "Malignant neoplasm of breast")
        - Broader terms (e.g., "Type 2 Diabetes" -> "Diabetes")
        - Narrower terms (e.g., "Cancer" -> "Breast cancer", "Lung cancer")
        - ICD-10 codes (if include_icd10=True)
        - EFO IDs/terms (if include_efo=True)
        - Related terms (if include_related=True)
        
        Args:
            trait_query: Original trait query string
            max_synonyms: Maximum number of synonyms to generate (default 10)
            include_icd10: Whether to include ICD-10 codes (default True)
            include_efo: Whether to include EFO terms (default True)
            include_related: Whether to include semantically related terms (default False)
            
        Returns:
            TraitExpansionResult with expanded queries and synonym metadata
        """
        # Check cache first
        cache_key = f"{trait_query.lower().strip()}:{max_synonyms}:{include_icd10}:{include_efo}:{include_related}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for trait expansion: {trait_query}")
            return self._cache[cache_key]
        
        # Generate synonyms using LLM
        try:
            synonyms = self._generate_synonyms_with_llm(
                trait_query,
                max_synonyms=max_synonyms,
                include_icd10=include_icd10,
                include_efo=include_efo,
                include_related=include_related
            )
        except Exception as e:
            logger.warning(f"LLM synonym generation failed for '{trait_query}': {e}")
            # Fallback: return original query only
            result = TraitExpansionResult(
                original_query=trait_query,
                expanded_queries=[trait_query],
                synonyms=[],
                method="none",
                confidence="Low"
            )
            self._cache[cache_key] = result
            return result
        
        # Build expanded queries list (filter out codes if not requested)
        expanded_queries = [trait_query]  # Always include original
        for syn in synonyms:
            if syn.synonym and syn.synonym.lower() != trait_query.lower():
                # Skip codes if not requested
                if not include_icd10 and syn.relationship == "icd10_code":
                    continue
                if not include_efo and syn.relationship == "efo_id":
                    continue
                # Also check if synonym itself looks like a code
                if not include_icd10 and len(syn.synonym) >= 2 and syn.synonym[0] in ('C', 'E', 'I') and syn.synonym[1:].replace('.', '').isdigit():
                    continue
                if not include_efo and (syn.synonym.startswith('EFO_') or syn.synonym.startswith('MONDO_')):
                    continue
                expanded_queries.append(syn.synonym)
        
        # Determine overall confidence
        if synonyms:
            high_conf_count = sum(1 for s in synonyms if s.confidence == "High")
            if high_conf_count >= len(synonyms) * 0.7:
                overall_confidence = "High"
            elif high_conf_count >= len(synonyms) * 0.4:
                overall_confidence = "Moderate"
            else:
                overall_confidence = "Low"
        else:
            overall_confidence = "Low"
        
        result = TraitExpansionResult(
            original_query=trait_query,
            expanded_queries=expanded_queries,
            synonyms=synonyms,
            method="llm",
            confidence=overall_confidence
        )
        
        # Cache result
        self._cache[cache_key] = result
        return result
    
    def _generate_synonyms_with_llm(
        self,
        trait_query: str,
        *,
        max_synonyms: int = 10,
        include_icd10: bool = True,
        include_efo: bool = True,
        include_related: bool = True
    ) -> List[TraitSynonym]:
        """
        Use LLM to generate trait synonyms.
        
        Args:
            trait_query: Original trait query
            max_synonyms: Maximum number of synonyms to generate
            include_icd10: Whether to include ICD-10 codes
            include_efo: Whether to include EFO terms
            include_related: Whether to include related terms
            
        Returns:
            List of TraitSynonym objects
        """
        system_prompt = """You are a biomedical ontology expert specializing in trait and disease terminology.

Your task is to generate comprehensive synonyms and alternative names for a given trait query.

Guidelines:
1. **Exact Synonyms**: Include medical terms that refer to the exact same condition
   - Example: "Breast cancer" <-> "Malignant neoplasm of breast" <-> "Carcinoma of breast"
   - Example: "Type 2 Diabetes" <-> "T2D" <-> "Non-insulin dependent diabetes mellitus"

2. **Broader Terms**: Include more general categories (if relevant)
   - Example: "Breast cancer" -> "Cancer" (but only if it helps find more data)

3. **Narrower Terms**: Include more specific subtypes (if relevant)
   - Example: "Diabetes" -> "Type 2 Diabetes", "Type 1 Diabetes"

4. **ICD-10 Codes**: Include ICD-10 codes if you know them
   - Example: "Breast cancer" -> "C50" (Malignant neoplasm of breast)

5. **EFO Terms**: Include EFO ontology terms if you know them
   - Example: "Breast cancer" -> "EFO_0000305" or "breast carcinoma"

6. **Related Terms**: Include semantically related terms that might be used interchangeably
   - Example: "Schizophrenia" -> "Schizophrenic disorder"

7. **Avoid**: 
   - Family history proxies (unless query explicitly asks for them)
   - Screening procedures (unless query explicitly asks for them)
   - Unrelated conditions
   - Overly generic terms that would match too many things

Return a JSON list of synonyms with their relationship types and confidence levels."""

        # Build human prompt with conditional includes
        include_parts = ["- Exact synonyms (same condition, different name)"]
        relationship_options = ["exact_synonym", "broader_term", "narrower_term", "related_term", "other"]
        if include_icd10:
            include_parts.append("- ICD-10 codes (if known)")
            relationship_options.append("icd10_code")
        if include_efo:
            include_parts.append("- EFO ontology terms (if known)")
            relationship_options.append("efo_id")
        if include_related:
            include_parts.append("- Related terms (semantically equivalent)")
        
        human_prompt = f"""Trait query: {{trait_query}}

Generate up to {{max_synonyms}} synonyms and alternative names for this trait.

Include:
{chr(10).join(include_parts)}

**CRITICAL**: Do NOT include ICD-10 codes or EFO IDs unless explicitly requested above.

Return a JSON list with fields: synonym, relationship, confidence, rationale.
- relationship: one of {", ".join(relationship_options)}
- confidence: "High" (certain), "Moderate" (likely), "Low" (possible)
- rationale: brief explanation (optional)"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])
        
        llm = self._get_llm()
        
        # Use structured output for reliable parsing
        class SynonymList(BaseModel):
            synonyms: List[TraitSynonym]
        
        chain = prompt | llm.with_structured_output(
            SynonymList,
            method="json_schema",
            strict=True
        )
        
        response = chain.invoke({
            "trait_query": trait_query,
            "max_synonyms": max_synonyms
        })
        
        # Filter out codes if not requested
        synonyms = response.synonyms[:max_synonyms]
        if not include_icd10 or not include_efo:
            filtered_synonyms = []
            for syn in synonyms:
                # Exclude ICD-10 codes if not requested
                if not include_icd10 and syn.relationship == "icd10_code":
                    continue
                # Exclude EFO IDs if not requested
                if not include_efo and syn.relationship == "efo_id":
                    continue
                # Also check if synonym itself looks like a code
                if not include_icd10 and syn.synonym and len(syn.synonym) >= 2 and syn.synonym[0] in ('C', 'E', 'I') and syn.synonym[1:].replace('.', '').isdigit():
                    continue
                if not include_efo and syn.synonym and (syn.synonym.startswith('EFO_') or syn.synonym.startswith('MONDO_')):
                    continue
                filtered_synonyms.append(syn)
            synonyms = filtered_synonyms
        
        return synonyms
    
    def get_expanded_queries(self, trait_query: str, **kwargs) -> List[str]:
        """
        Convenience method to get just the expanded query list.
        
        Args:
            trait_query: Original trait query
            **kwargs: Additional arguments passed to expand_trait_query
            
        Returns:
            List of expanded query strings
        """
        result = self.expand_trait_query(trait_query, **kwargs)
        return result.expanded_queries


# Singleton instance
_expander_instance: Optional[TraitSynonymExpander] = None


def get_trait_expander() -> TraitSynonymExpander:
    """Get the singleton TraitSynonymExpander instance."""
    global _expander_instance
    if _expander_instance is None:
        _expander_instance = TraitSynonymExpander()
    return _expander_instance
