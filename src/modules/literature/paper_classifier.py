"""
Paper Classifier Agent

LLM-based multi-label classifier that categorizes papers into:
- PRS_PERFORMANCE: Papers reporting PRS model performance metrics
- HERITABILITY: Papers reporting SNP-heritability estimates
- GENETIC_CORRELATION: Papers reporting genetic correlations
- NOT_RELEVANT: Papers not relevant for extraction

Uses structured prompting with JSON Schema constrained output.
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field

from .entities import (
    PaperMetadata,
    ClassificationResult,
    CategoryScore,
    PaperCategory
)
from .prompts import get_prompt, format_user_prompt
from .schemas import PAPER_CLASSIFICATION_SCHEMA
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


# ============================================================================
# Paper Classifier (Structured Output Version)
# ============================================================================

class PaperClassifier:
    """
    LLM-based paper classifier for the literature mining pipeline.
    
    Uses structured prompting with JSON Schema constrained output
    following best practices from expert prompt engineering.
    
    Architecture:
    - Developer prompt: Defines role, categories, reasoning requirements
    - User prompt: Provides paper metadata for classification
    - JSON Schema: Constrains LLM output for reliable parsing
    """
    
    def __init__(self):
        """
        Initialize the classifier.
        
        Uses centralized LLM configuration from src/core/llm_config.py
        """
        self._client = None
        self._model_name = None
        self._config = None
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client from centralized config."""
        if self._client is None:
            try:
                from src.core.llm_config import get_config
                from openai import OpenAI
                self._config = get_config("literature_classifier")
                self._model_name = self._config.model
                # Initialize OpenAI client with API key from environment
                self._client = OpenAI()
                logger.debug(f"PaperClassifier using model: {self._model_name}")
            except ImportError as e:
                logger.warning(f"Could not import llm_config: {e}. Using default.")
                from openai import OpenAI
                self._client = OpenAI()
                self._model_name = "gpt-4o-mini"
        return self._client
    
    @property
    def model_name(self) -> str:
        """Get the model name being used."""
        if self._model_name is None:
            _ = self.client  # Trigger lazy init
        return self._model_name or "unknown"
    
    def classify(self, paper: PaperMetadata) -> ClassificationResult:
        """
        Classify a single paper using structured prompting.
        
        Args:
            paper: Paper metadata with title and abstract
        
        Returns:
            ClassificationResult with categories and confidence scores
        """
        # Get prompts
        developer_prompt = get_prompt("classification", "developer")
        user_prompt = format_user_prompt(
            "classification",
            pmid=paper.pmid,
            title=paper.title,
            abstract=paper.abstract[:4000] if paper.abstract else "(No abstract available)",
            journal=paper.journal or "Unknown",
            year=paper.publication_date.year if paper.publication_date else "Unknown"
        )
        
        try:
            messages = [
                {"role": "system", "content": developer_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use structured output to enforce schema via native OpenAI client
            # Determine if we should use response_format={"type": "json_schema", ...}
            # which is required for Strict Structured Outputs
            
            # Use OpenAI 'responses' endpoint with tools for structured output
            # The 'responses' endpoint typically uses tools to structure the output
            
            # Add schema instructions to prompt since tools/strict mode is unreliable with this beta endpoint
            schema_json = json.dumps(PAPER_CLASSIFICATION_SCHEMA["json_schema"]["schema"], indent=2)
            prompt_suffix = f"\n\nYou must output valid JSON strictly following this schema:\n```json\n{schema_json}\n```"
            
            # Append to the last user message
            if isinstance(messages[-1], HumanMessage):
                messages[-1].content += prompt_suffix
            elif isinstance(messages[-1], dict) and messages[-1].get("role") == "user":
                messages[-1]["content"] += prompt_suffix
            
            logger.debug(f"Calling responses.create with text-based schema enforcement")
            
            response = self.client.responses.create(
                model=self.model_name,
                input=messages
                # Not using tools/tool_choice as they result in empty args with this model/endpoint
            )
            
            
            content = ""
            if hasattr(response, 'output'):
                 if isinstance(response.output, list):
                     for block in response.output:
                         if hasattr(block, 'type'):
                             if block.type == 'message':
                                 # Check if message has multiple content blocks
                                 if hasattr(block, 'content') and isinstance(block.content, list):
                                     for msg_part in block.content:
                                         if hasattr(msg_part, 'type') and msg_part.type == 'output_text':
                                             content = msg_part.text
                                             break
                                 elif hasattr(block, 'content'): # Maybe simple string?
                                     content = str(block.content)
                                 
                             if content: break
                 else:
                     content = str(response.output)
            elif hasattr(response, 'choices'): # Fallback
                 content = response.choices[0].message.content
                     
            elif hasattr(response, 'choices'): # Fallback
                 tool_calls = response.choices[0].message.tool_calls
                 if tool_calls:
                     content = tool_calls[0].function.arguments
                 else:
                     content = response.choices[0].message.content
            
            if not content:
                logger.warning("Could not extract content from response object.")
            logger.debug(f"LLM Response for {paper.pmid}:\n{content}")
            
            # Parse structured response
            result = self._parse_response(paper.pmid, content)
            
            logger.info(
                f"Classified PMID:{paper.pmid} -> {result.primary_category.value} "
                f"(confidence: {result.overall_confidence:.2f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying paper {paper.pmid}: {e}")
            return self._create_error_result(paper.pmid, str(e))
    
    def classify_batch(
        self,
        papers: List[PaperMetadata],
        progress_callback: Optional[callable] = None
    ) -> List[ClassificationResult]:
        """
        Classify multiple papers.
        
        Args:
            papers: List of papers to classify
            progress_callback: Optional callback(current, total) for progress
        
        Returns:
            List of ClassificationResults
        """
        results = []
        total = len(papers)
        
        for i, paper in enumerate(papers):
            result = self.classify(paper)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results
    
    def _parse_response(self, pmid: str, response_content: str) -> ClassificationResult:
        """Parse structured LLM response into ClassificationResult."""
        try:
            # Handle potential markdown code blocks
            content = response_content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            data = json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON for PMID:{pmid}: {e}")
            logger.debug(f"Response content: {response_content[:500]}")
            return self._create_error_result(pmid, "JSON parse error")
        
        # Parse classifications from structured response
        categories = []
        for cls in data.get("classifications", []):
            try:
                category = PaperCategory(cls["category"])
                
                # Get key evidence if available
                key_evidence = cls.get("key_evidence", [])
                reasoning = cls.get("reasoning", "")
                if key_evidence:
                    reasoning = f"{reasoning} Key evidence: {', '.join(key_evidence[:3])}"
                
                categories.append(CategoryScore(
                    category=category,
                    confidence=float(cls.get("confidence", 0.5)),
                    reasoning=reasoning
                ))
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing category: {cls}, error: {e}")
                continue
        
        # Determine primary category
        try:
            primary = PaperCategory(data.get("primary_category", "NOT_RELEVANT"))
        except ValueError:
            primary = PaperCategory.NOT_RELEVANT
        
        # Calculate overall confidence
        if categories:
            relevant_cats = [c for c in categories if c.category != PaperCategory.NOT_RELEVANT]
            if relevant_cats:
                overall_confidence = max(c.confidence for c in relevant_cats)
            else:
                overall_confidence = categories[0].confidence
        else:
            overall_confidence = 0.0
        
        # Build comprehensive reasoning
        overall_reasoning = data.get("overall_reasoning", "")
        data_availability = data.get("data_availability", {})
        if data_availability:
            available_data = [k for k, v in data_availability.items() if v]
            if available_data:
                overall_reasoning += f" [Available data: {', '.join(available_data)}]"
        
        return ClassificationResult(
            pmid=pmid,
            categories=categories,
            primary_category=primary,
            overall_confidence=overall_confidence,
            llm_reasoning=overall_reasoning,
            model_used=self.model_name
        )
    
    def _create_error_result(self, pmid: str, error_msg: str) -> ClassificationResult:
        """Create a default result for error cases."""
        return ClassificationResult(
            pmid=pmid,
            categories=[CategoryScore(
                category=PaperCategory.NOT_RELEVANT,
                confidence=0.0,
                reasoning=f"Classification error: {error_msg}"
            )],
            primary_category=PaperCategory.NOT_RELEVANT,
            overall_confidence=0.0,
            llm_reasoning=f"Error during classification: {error_msg}",
            model_used=self.model_name
        )
    
    # =========================================================================
    # Filtering Helpers
    # =========================================================================
    
    def filter_relevant(
        self,
        results: List[ClassificationResult],
        min_confidence: float = 0.5
    ) -> List[ClassificationResult]:
        """
        Filter classification results to only relevant papers.
        
        Args:
            results: List of classification results
            min_confidence: Minimum confidence threshold
        
        Returns:
            Filtered list of relevant papers
        """
        return [
            r for r in results
            if r.is_relevant and r.overall_confidence >= min_confidence
        ]
    
    def filter_by_category(
        self,
        results: List[ClassificationResult],
        category: PaperCategory,
        min_confidence: float = 0.5
    ) -> List[ClassificationResult]:
        """
        Filter results by specific category.
        
        Args:
            results: List of classification results
            category: Category to filter for
            min_confidence: Minimum confidence threshold
        
        Returns:
            Filtered list of papers matching category
        """
        return [
            r for r in results
            if any(
                c.category == category and c.confidence >= min_confidence
                for c in r.categories
            )
        ]
    
    def get_papers_for_extraction(
        self,
        results: List[ClassificationResult],
        min_confidence: float = 0.5
    ) -> Dict[PaperCategory, List[str]]:
        """
        Get PMIDs organized by extraction category.
        
        Args:
            results: List of classification results
            min_confidence: Minimum confidence threshold
        
        Returns:
            Dict mapping category to list of PMIDs for that category
        """
        category_pmids = {
            PaperCategory.PRS_PERFORMANCE: [],
            PaperCategory.HERITABILITY: [],
            PaperCategory.GENETIC_CORRELATION: []
        }
        
        for result in results:
            for cat_score in result.categories:
                if (
                    cat_score.category != PaperCategory.NOT_RELEVANT
                    and cat_score.confidence >= min_confidence
                ):
                    category_pmids[cat_score.category].append(result.pmid)
        
        return category_pmids


# ============================================================================
# Rule-Based Fallback Classifier
# ============================================================================

class RuleBasedClassifier:
    """
    Simple rule-based classifier as fallback or for testing.
    
    Uses keyword matching to classify papers without LLM.
    Less accurate but faster and cheaper.
    """
    
    # Keywords for each category (weighted by importance)
    PRS_KEYWORDS = {
        "high": ["polygenic risk score", "polygenic score", "genetic risk score", 
                 "PRS", "PGS", "polygenic prediction"],
        "medium": ["risk prediction", "predictive performance", "discrimination", 
                   "risk stratification", "AUC"],
        "low": ["C-statistic", "R-squared", "odds ratio per", "hazard ratio per"]
    }
    
    H2_KEYWORDS = {
        "high": ["heritability", "h2", "h²", "SNP-heritability", "snp heritability"],
        "medium": ["LDSC", "LD score", "GCTA", "GREML", "genetic variance"],
        "low": ["genetic architecture", "variance explained", "BOLT-REML"]
    }
    
    RG_KEYWORDS = {
        "high": ["genetic correlation", "rg =", "rg=", "genetically correlated"],
        "medium": ["cross-trait", "shared genetic", "pleiotropy", "bivariate"],
        "low": ["genetic overlap", "common genetic factors", "genetic covariance"]
    }
    
    def classify(self, paper: PaperMetadata) -> ClassificationResult:
        """Classify paper using keyword matching."""
        text = f"{paper.title} {paper.abstract}".lower()
        
        categories = []
        
        # Check each category
        for category, keywords, threshold in [
            (PaperCategory.PRS_PERFORMANCE, self.PRS_KEYWORDS, 0.3),
            (PaperCategory.HERITABILITY, self.H2_KEYWORDS, 0.3),
            (PaperCategory.GENETIC_CORRELATION, self.RG_KEYWORDS, 0.3),
        ]:
            score, matched = self._calculate_score(text, keywords)
            if score >= threshold:
                categories.append(CategoryScore(
                    category=category,
                    confidence=min(score, 1.0),
                    reasoning=f"Matched keywords: {', '.join(matched[:5])}"
                ))
        
        # If no matches, mark as not relevant
        if not categories:
            categories.append(CategoryScore(
                category=PaperCategory.NOT_RELEVANT,
                confidence=0.8,
                reasoning="No relevant keywords found"
            ))
        
        # Determine primary category (highest confidence)
        primary = max(categories, key=lambda c: c.confidence)
        
        return ClassificationResult(
            pmid=paper.pmid,
            categories=categories,
            primary_category=primary.category,
            overall_confidence=primary.confidence,
            llm_reasoning="Rule-based classification using keyword matching",
            model_used="rule-based"
        )
    
    def _calculate_score(
        self, 
        text: str, 
        keywords: Dict[str, List[str]]
    ) -> tuple[float, List[str]]:
        """Calculate confidence score based on keyword presence."""
        score = 0.0
        matched = []
        
        for weight, terms in keywords.items():
            for term in terms:
                if term.lower() in text:
                    matched.append(term)
                    if weight == "high":
                        score += 0.4
                    elif weight == "medium":
                        score += 0.2
                    else:  # low
                        score += 0.1
        
        return score, matched
