"""
LLM Configuration Module

Centralized configuration for all LLM models used throughout the PennPRS Agent.
Modify this file to change model settings across all modules.

Usage:
    from src.server.core.llm_config import get_llm, LLMConfig
    
    # Get default LLM
    llm = get_llm()
    
    # Get specific module's LLM
    llm = get_llm("agentic_classifier")
    
    # Access raw config
    config = LLMConfig.AGENTIC_CLASSIFIER
"""

import os
from dataclasses import dataclass
from dataclasses import replace
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration Dataclass
# ============================================================================

@dataclass
class ModelConfig:
    """Configuration for a single LLM model."""
    model: str = "gpt-5.2"
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout: Optional[int] = 30
    json_mode: bool = False
    strict: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for ChatOpenAI kwargs."""
        config = {
            "model": self.model,
            "temperature": self.temperature,
        }
        if self.max_tokens:
            config["max_tokens"] = self.max_tokens
        if self.timeout:
            config["timeout"] = self.timeout
        if self.json_mode and not self.strict:
            config["model_kwargs"] = {"response_format": {"type": "json_object"}}
        # Note: strict mode is typically applied at the .with_structured_output() level, 
        # but if using raw model_kwargs with json_schema, it would go here.
        # For now, we expose the flag so consumers can use it.
        return config


# ============================================================================
# LLM Configurations for Different Modules
# ============================================================================

class LLMConfig:
    """
    Central configuration for all LLM models in PennPRS Agent.
    
    Modify these settings to change model behavior across the entire application.
    """
    
    # =========================================================================
    # DEFAULT CONFIGURATION
    # Used when no specific configuration is requested
    # =========================================================================
    DEFAULT = ModelConfig(
        model="gpt-5.2",
        temperature=0.0,
        timeout=30
    )
    
    # =========================================================================
    # PROTEIN MODULE: PennPRS-Protein Workflow
    # Used in: src/modules/protein/workflow.py
    # Purpose: Protein search and result interpretation
    # =========================================================================
    PROTEIN_WORKFLOW = ModelConfig(
        model="gpt-5.2",
        temperature=0.0,
        timeout=30
    )
    
    # =========================================================================
    # DISEASE MODULE: PennPRS-Disease Workflow
    # Used in: src/modules/disease/workflow.py
    # Purpose: Disease/trait analysis, model recommendations
    # =========================================================================
    DISEASE_WORKFLOW = ModelConfig(
        model="gpt-5.2",
        temperature=0.0,
        timeout=30
    )
    
    # =========================================================================
    # TRAIT CLASSIFIER (Simple)
    # Used in: src/modules/disease/trait_classifier.py
    # Purpose: Quick trait classification (Binary vs Continuous)
    # =========================================================================
    TRAIT_CLASSIFIER = ModelConfig(
        model="gpt-5.2",
        temperature=0.0,
        timeout=30
    )
    
    # =========================================================================
    # AGENTIC STUDY CLASSIFIER
    # Used in: src/modules/disease/agentic_study_classifier.py
    # Purpose: Intelligent GWAS study classification with API data
    # Note: Uses JSON mode for structured output
    # =========================================================================
    AGENTIC_CLASSIFIER = ModelConfig(
        model="gpt-5.2",

        temperature=0.0,
        timeout=60,
        json_mode=False,
        strict=True
    )
    
    # =========================================================================
    # LITERATURE MODULE: Deprecated
    # =========================================================================
    # Literature module has been archived. Configs removed.


# ============================================================================
# Module Name to Config Mapping
# ============================================================================

_CONFIG_MAP = {
    "default": LLMConfig.DEFAULT,
    "protein": LLMConfig.PROTEIN_WORKFLOW,
    "protein_workflow": LLMConfig.PROTEIN_WORKFLOW,
    "disease": LLMConfig.DISEASE_WORKFLOW,
    "disease_workflow": LLMConfig.DISEASE_WORKFLOW,
    "trait_classifier": LLMConfig.TRAIT_CLASSIFIER,
    "agentic_classifier": LLMConfig.AGENTIC_CLASSIFIER,
    "agentic_study_classifier": LLMConfig.AGENTIC_CLASSIFIER,
    # Literature Mining Module - Archived
    # Compatibility aliases (some tests and scripts still expect these keys).
    # They fall back to DEFAULT to avoid breaking import-time behavior.
    "literature_classifier": LLMConfig.DEFAULT,
    "paper_classifier": LLMConfig.DEFAULT,
    "literature_extractor": LLMConfig.DEFAULT,
    "prs_extractor": LLMConfig.DEFAULT,
    "heritability_extractor": LLMConfig.DEFAULT,
    "genetic_correlation_extractor": LLMConfig.DEFAULT,
    # Backward compatibility aliases
    "function3": LLMConfig.PROTEIN_WORKFLOW,
    "function3_workflow": LLMConfig.PROTEIN_WORKFLOW,
    "function4": LLMConfig.DISEASE_WORKFLOW,
    "function4_workflow": LLMConfig.DISEASE_WORKFLOW,
}


# ============================================================================
# Factory Functions
# ============================================================================

def get_llm(module: str = "default") -> ChatOpenAI:
    """
    Get a configured ChatOpenAI instance for a specific module.
    
    Args:
        module: Module name. Options:
            - "default": Default configuration
            - "protein" / "protein_workflow": Proteomics workflow
            - "disease" / "disease_workflow": PRS training workflow
            - "trait_classifier": Simple trait classifier
            - "agentic_classifier" / "agentic_study_classifier": Agentic classifier
    
    Returns:
        Configured ChatOpenAI instance
    
    Example:
        llm = get_llm("agentic_classifier")
        response = llm.invoke("Classify this trait...")
    """
    config = _CONFIG_MAP.get(module.lower(), LLMConfig.DEFAULT)

    # Optional environment override (project rule: OPENAI_MODEL).
    # This enables quick runtime switching without code changes.
    model_override = os.getenv("OPENAI_MODEL")
    if model_override:
        config = replace(config, model=model_override)
    
    logger.debug(f"Creating LLM for module '{module}': {config.model}, temp={config.temperature}")
    
    return ChatOpenAI(**config.to_dict())


def get_config(module: str = "default") -> ModelConfig:
    """
    Get the raw configuration for a module.
    
    Args:
        module: Module name (see get_llm for options)
    
    Returns:
        ModelConfig instance
    """
    return _CONFIG_MAP.get(module.lower(), LLMConfig.DEFAULT)


def list_configs() -> Dict[str, Dict[str, Any]]:
    """
    List all available configurations.
    
    Returns:
        Dict mapping module names to their configurations
    """
    return {
        name: config.to_dict() 
        for name, config in _CONFIG_MAP.items()
    }


# ============================================================================
# Configuration Summary (for debugging)
# ============================================================================

def print_config_summary():
    """Print a summary of all LLM configurations."""
    print("=" * 60)
    print("PennPRS Agent - LLM Configuration Summary")
    print("=" * 60)
    
    unique_configs = {
        "DEFAULT": LLMConfig.DEFAULT,
        "PROTEIN_WORKFLOW": LLMConfig.PROTEIN_WORKFLOW,
        "DISEASE_WORKFLOW": LLMConfig.DISEASE_WORKFLOW,
        "TRAIT_CLASSIFIER": LLMConfig.TRAIT_CLASSIFIER,
        "AGENTIC_CLASSIFIER": LLMConfig.AGENTIC_CLASSIFIER,
    }
    
    for name, config in unique_configs.items():
        print(f"\n{name}:")
        print(f"  Model: {config.model}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Timeout: {config.timeout}s")
        print(f"  JSON Mode: {config.json_mode}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_config_summary()
