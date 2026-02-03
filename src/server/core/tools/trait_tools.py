# src/server/core/tools/trait_tools.py
"""
Trait Tools for Module 3.
Provides trait synonym expansion as callable tools for the Agent.
"""
from typing import Union
from src.server.core.tool_schemas import TraitSynonymResult, ToolError
from src.server.core.trait_synonym_expander import get_trait_expander, TraitExpansionResult
import logging

logger = logging.getLogger(__name__)

def trait_synonym_expand(
    trait_query: str,
    max_synonyms: int = 10,
    include_icd10: bool = False,  # Changed default: exclude codes for genetic graph
    include_efo: bool = False,    # Changed default: exclude codes for genetic graph
    include_related: bool = False
) -> Union[TraitExpansionResult, ToolError]:
    """
    Expand a trait query with synonyms and semantically equivalent terms.
    
    This tool helps the Agent discover alternative trait names that might be used
    in different data sources. For example, "Breast cancer" and "Malignant neoplasm of breast"
    refer to the same condition but may be indexed differently.
    
    **Note**: By default, this excludes ICD-10 and EFO codes, as they are not suitable
    for Knowledge Graph queries (GWAS Atlas uses trait names, not codes).
    
    The Agent should use this tool when:
    - Initial tool calls return no results or empty results
    - The Agent wants to ensure comprehensive coverage across data sources
    - The Agent needs to map between different trait naming conventions
    
    Args:
        trait_query: Original trait query string
        max_synonyms: Maximum number of synonyms to generate (default 10)
        include_icd10: Whether to include ICD-10 codes (default False for genetic graph)
        include_efo: Whether to include EFO terms (default False for genetic graph)
        include_related: Whether to include semantically related terms (default False)
        
    Returns:
        TraitExpansionResult with expanded queries and synonym metadata, or ToolError on failure
    """
    try:
        expander = get_trait_expander()
        result = expander.expand_trait_query(
            trait_query,
            max_synonyms=max_synonyms,
            include_icd10=include_icd10,
            include_efo=include_efo,
            include_related=include_related
        )
        return result
    except Exception as e:
        return ToolError(
            tool_name="trait_synonym_expand",
            error_type=type(e).__name__,
            error_message=str(e),
            context={"trait_query": trait_query}
        )
