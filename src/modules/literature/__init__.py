"""
PennPRS Agent - Literature Mining Engine

This module implements an LLM-driven pipeline for extracting structured
genetic data from PubMed literature, including:
- PRS performance metrics (AUC, R², sample size, etc.)
- SNP-heritability (h²) estimates
- Genetic correlation (rg) data

Architecture: Supervisor + Workers (Agentic Pipeline)
- Supervisor: Orchestrates workflow, routes papers to workers
- Classifier Agent (LLM): Multi-label classification of papers
- Extractor Agents (LLM x 3): PRS, h², rg extraction
- Validator Agent (Rule-based): Schema validation + deduplication

Prompt Design:
- Structured Prompting with clear role/objective/rules
- Schema-Constrained Output (JSON Schema)
- Quality Guards for LLM behavior
"""

# Data models (entities)
from .entities import (
    PaperMetadata,
    ClassificationResult,
    CategoryScore,
    PaperCategory,
    PRSModelExtraction,
    HeritabilityExtraction,
    GeneticCorrelationExtraction,
    ExtractionResult,
    ValidationResult,
    ValidationIssue,
    ValidationStatus,
    WorkflowState,
    DataSource,
    PRSMethod,
    HeritabilityMethod,
    GeneticCorrelationMethod,
)

# PubMed client
from .pubmed import PubMedClient

# Classifiers
from .paper_classifier import PaperClassifier, RuleBasedClassifier

# Extractors
from .information_extractor import (
    PRSExtractor,
    HeritabilityExtractor as H2Extractor,
    GeneticCorrelationExtractor as RgExtractor,
    ExtractorFactory,
)

# Validator
from .validator import Validator

# Workflow
from .pipeline import LiteratureMiningWorkflow, mine_literature

# Prompts and Schemas (for advanced users)
from .prompts import get_prompt, format_user_prompt, PROMPTS
from .schemas import get_schema, ALL_SCHEMAS

__all__ = [
    # Data Models
    "PaperMetadata",
    "ClassificationResult",
    "CategoryScore",
    "PaperCategory",
    "PRSModelExtraction",
    "HeritabilityExtraction",
    "GeneticCorrelationExtraction",
    "ExtractionResult",
    "ValidationResult",
    "ValidationIssue",
    "ValidationStatus",
    "WorkflowState",
    "DataSource",
    "PRSMethod",
    "HeritabilityMethod",
    "GeneticCorrelationMethod",
    # Components
    "PubMedClient",
    "PaperClassifier",
    "RuleBasedClassifier",
    "PRSExtractor",
    "H2Extractor",
    "RgExtractor",
    "ExtractorFactory",
    "Validator",
    "LiteratureMiningWorkflow",
    "mine_literature",
    # Advanced
    "get_prompt",
    "format_user_prompt",
    "PROMPTS",
    "get_schema",
    "ALL_SCHEMAS",
]
