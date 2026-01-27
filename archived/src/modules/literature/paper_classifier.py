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
                self._model_name = "gpt-4.1-nano"
        return self._client
    
    @property
    def model_name(self) -> str:
        """Get the model name being used."""
        if self._model_name is None:
            _ = self.client  # Trigger lazy init
        return self._model_name or "unknown"
    
    def classify(self, paper: PaperMetadata, max_retries: int = 3) -> ClassificationResult:
        """
        Classify a single paper using structured prompting.
        
        Args:
            paper: Paper metadata with title and abstract
            max_retries: Maximum number of retries for rate limit or parse errors
        
        Returns:
            ClassificationResult with categories and confidence scores
        """
        import time
        import random
        
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
        
        # Check for strict mode configuration
        is_strict = getattr(self._config, 'strict', False)
        
        if is_strict:
            # STRICT MODE: Use new beta parse API
            # Note: We don't need to append the schema to the prompt in strict mode, 
            # as the API handles it, but keeping the prompt structure is generally fine.
            # However, prompt-based schema instructions might be redundant/confusing for strict mode models?
            # Usually it's safer to rely on the API.
            
            messages = [
                {"role": "system", "content": developer_prompt},
                {"role": "user", "content": user_prompt} # Use original user prompt without manual schema injection
            ]
            
            # Retry loop for rate limit
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"Calling beta.chat.completions.parse for PMID:{paper.pmid} (attempt {attempt + 1})")
                    
                    response = self.client.beta.chat.completions.parse(
                        model=self.model_name,
                        messages=messages,
                        response_format=PAPER_CLASSIFICATION_SCHEMA["json_schema"]["schema"],
                        temperature=0.1,
                        max_tokens=1500
                    )
                    
                    if hasattr(response.choices[0].message, 'parsed'):
                        data = response.choices[0].message.parsed
                        # Convert to dict if needed (depends on if schema was pydantic or dict)
                        if hasattr(data, 'model_dump'):
                             data = data.model_dump()
                        elif hasattr(data, 'dict'):
                             data = data.dict()
                    else:
                         # Fallback
                         content = response.choices[0].message.content
                         data = json.loads(content)
                    
                    # Process result
                    # We need to adapt the logic from _parse_response to work with the dict directly
                    # reusing _parse_response by re-serializing is inefficient but safe for specific method logic preservation
                    # OR better: refactor _parse_response to accept dict.
                    # For minimal change risk: modify _parse_response to accept dict OR str?
                    # Let's check _parse_response... it explicitly takes content string.
                    # To reuse _parse_response logic without changes:
                    result = self._parse_response_dict(paper.pmid, data)
                    
                    logger.info(
                        f"Classified PMID:{paper.pmid} -> {result.primary_category.value} "
                        f"(confidence: {result.overall_confidence:.2f})"
                    )
                    return result

                except Exception as e:
                    last_error = e
                    # ... (Rate limit handling logic similar to below) ...
                    error_str = str(e)
                    if "429" in error_str or "rate_limit" in error_str.lower():
                         if attempt < max_retries:
                            wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                            logger.warning(f"Rate limit hit, retrying in {wait_time:.1f}s")
                            time.sleep(wait_time)
                            continue
                    
                    logger.error(f"Error classifying paper {paper.pmid}: {e}")
                    break
            
            return self._create_error_result(paper.pmid, str(last_error))

        # ==========================================
        # LEGACY JSON MODE
        # ==========================================
        
        # Add schema instructions to prompt
        schema_json = json.dumps(PAPER_CLASSIFICATION_SCHEMA["json_schema"]["schema"], indent=2)
        full_user_prompt = user_prompt + f"\n\nYou must output valid JSON strictly following this schema:\n```json\n{schema_json}\n```"
        
        messages = [
            {"role": "system", "content": developer_prompt},
            {"role": "user", "content": full_user_prompt}
        ]
        
        # Retry loop for rate limit and parse error handling
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Calling chat.completions.create for PMID:{paper.pmid} (attempt {attempt + 1})")
                
                # Use chat.completions.create with JSON mode for guaranteed valid JSON
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content
                
                if not content:
                    raise ValueError("Empty response content")
                
                logger.debug(f"LLM Response for {paper.pmid}:\n{content[:500]}...")
                
                # Parse structured response - this should now always succeed with JSON mode
                result = self._parse_response(paper.pmid, content)
                
                # Check if parsing actually succeeded (confidence > 0 means valid parse)
                if result.overall_confidence == 0.0 and "error" in result.llm_reasoning.lower():
                    raise ValueError(f"Parse error: {result.llm_reasoning}")
                
                logger.info(
                    f"Classified PMID:{paper.pmid} -> {result.primary_category.value} "
                    f"(confidence: {result.overall_confidence:.2f})"
                )
                
                return result
                
            except json.JSONDecodeError as e:
                # JSON parse error - retry with fresh request
                last_error = e
                if attempt < max_retries:
                    wait_time = 0.5 + random.uniform(0.1, 0.5)
                    logger.warning(
                        f"JSON parse error for PMID:{paper.pmid}, "
                        f"retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                    continue
                    
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Check for rate limit error (429)
                if "429" in error_str or "rate_limit" in error_str.lower():
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                        logger.warning(
                            f"Rate limit hit for PMID:{paper.pmid}, "
                            f"retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                
                # Check for parse-related errors
                if "parse" in error_str.lower() or "json" in error_str.lower():
                    if attempt < max_retries:
                        wait_time = 0.5 + random.uniform(0.1, 0.5)
                        logger.warning(
                            f"Parse error for PMID:{paper.pmid}, "
                            f"retrying (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                
                # For other errors, log and break
                logger.error(f"Error classifying paper {paper.pmid}: {e}")
                break
        
        # All retries failed
        return self._create_error_result(paper.pmid, str(last_error))
    
    def classify_batch(
        self,
        papers: List[PaperMetadata],
        progress_callback: Optional[callable] = None,
        max_workers: Optional[int] = None
    ) -> List[ClassificationResult]:
        """
        Classify multiple papers with intelligent rate limiting.
        
        Uses proactive rate control to avoid 429 errors entirely.
        API limits: 200K TPM (~80-100 requests/min) and 500 RPM
        
        Args:
            papers: List of papers to classify
            progress_callback: Optional callback(current, total) for progress
            max_workers: Ignored - uses smart sequential processing
        
        Returns:
            List of ClassificationResults in the same order as input papers
        """
        import time
        import threading
        
        total = len(papers)
        
        if total == 0:
            return []
        
        # Rate limiting configuration
        # API: 200K TPM, ~2500 tokens/request = 80 requests/min = 1.33 req/sec
        # Using 2 requests per second (120/min, still under limit for fast models)
        MIN_REQUEST_INTERVAL = 0.5  # seconds between requests (~2 req/sec)
        
        logger.info(f"Classifying {total} papers with smart rate limiting (~2 req/sec)")
        
        results: List[ClassificationResult] = []
        last_request_time = 0.0
        lock = threading.Lock()
        
        start_time = time.perf_counter()
        
        for i, paper in enumerate(papers):
            # Smart rate limiting: ensure minimum interval between requests
            with lock:
                current_time = time.perf_counter()
                elapsed = current_time - last_request_time
                if elapsed < MIN_REQUEST_INTERVAL:
                    sleep_time = MIN_REQUEST_INTERVAL - elapsed
                    time.sleep(sleep_time)
                last_request_time = time.perf_counter()
            
            # Classify with retries built into classify()
            result = self.classify(paper)
            results.append(result)
            
            # Progress reporting
            completed = i + 1
            if progress_callback:
                progress_callback(completed, total)
            
            # Log progress every 50 papers
            if completed % 50 == 0 or completed == total:
                elapsed = time.perf_counter() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / rate if rate > 0 else 0
                logger.info(
                    f"Progress: {completed}/{total} ({completed/total*100:.1f}%) "
                    f"- {rate:.2f} papers/sec - ETA: {eta:.0f}s"
                )
        
        total_time = time.perf_counter() - start_time
        logger.info(
            f"Completed classification of {total} papers in {total_time:.1f}s "
            f"({total_time/total*1000:.0f}ms/paper)"
        )
        
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
            return self._parse_response_dict(pmid, data)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON for PMID:{pmid}: {e}")
            logger.debug(f"Response content: {response_content[:500]}")
            return self._create_error_result(pmid, "JSON parse error")

    def _parse_response_dict(self, pmid: str, data: Dict[str, Any]) -> ClassificationResult:
        """Parse dictionary data into ClassificationResult."""
        
        # Parse the new boolean label format
        labels = data.get("labels", {})
        confidence = data.get("confidence", {})
        evidence = data.get("evidence", {})
        reasoning = data.get("reasoning", "")
        
        # Build categories list from boolean labels
        categories = []
        
        # PRS
        if labels.get("is_prs", False):
            prs_conf = confidence.get("prs_confidence", 0.8)
            prs_evidence = evidence.get("prs_evidence", "")
            categories.append(CategoryScore(
                category=PaperCategory.PRS_PERFORMANCE,
                confidence=float(prs_conf),
                reasoning=prs_evidence
            ))
        
        # Heritability
        if labels.get("is_heritability", False):
            h2_conf = confidence.get("heritability_confidence", 0.8)
            h2_evidence = evidence.get("heritability_evidence", "")
            categories.append(CategoryScore(
                category=PaperCategory.HERITABILITY,
                confidence=float(h2_conf),
                reasoning=h2_evidence
            ))
        
        # Genetic Correlation
        if labels.get("is_genetic_correlation", False):
            rg_conf = confidence.get("genetic_correlation_confidence", 0.8)
            rg_evidence = evidence.get("genetic_correlation_evidence", "")
            categories.append(CategoryScore(
                category=PaperCategory.GENETIC_CORRELATION,
                confidence=float(rg_conf),
                reasoning=rg_evidence
            ))
        
        # If no categories, mark as NOT_RELEVANT
        if not categories:
            categories.append(CategoryScore(
                category=PaperCategory.NOT_RELEVANT,
                confidence=0.9,
                reasoning="No relevant labels identified"
            ))
        
        # Determine primary category (highest confidence or first one)
        primary = max(categories, key=lambda c: c.confidence).category
        
        # Calculate overall confidence
        overall_confidence = max(c.confidence for c in categories)
        
        return ClassificationResult(
            pmid=pmid,
            categories=categories,
            primary_category=primary,
            overall_confidence=overall_confidence,
            llm_reasoning=reasoning,
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
