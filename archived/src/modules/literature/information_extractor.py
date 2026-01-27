"""
Information Extractor Agents

LLM-based extractors for structured data from paper full text:
- PRSExtractor: Extract PRS model performance metrics
- HeritabilityExtractor: Extract SNP-heritability estimates
- GeneticCorrelationExtractor: Extract rg values between traits

Uses structured prompting with JSON Schema constrained output.
Each extractor runs independently and can be parallelized.

Note: Extractors process FULL TEXT (not just abstracts) for comprehensive extraction.
Classifier uses abstracts for initial classification; Extractors use full text for detailed extraction.
"""

import json
import logging
import re
from typing import List, Optional, Dict, Any, TypeVar
from abc import ABC, abstractmethod

from .entities import (
    PaperMetadata,
    PRSModelExtraction,
    HeritabilityExtraction,
    GeneticCorrelationExtraction,
    PRSMethod,
    HeritabilityMethod,
    GeneticCorrelationMethod,
    DataSource
)
from .prompts import get_prompt, format_user_prompt
from .schemas import (
    PRS_EXTRACTION_SCHEMA,
    HERITABILITY_EXTRACTION_SCHEMA,
    GENETIC_CORRELATION_EXTRACTION_SCHEMA
)
from langchain_core.messages import SystemMessage, HumanMessage
from src.lib.langextract import LangExtractor

logger = logging.getLogger(__name__)

T = TypeVar('T', PRSModelExtraction, HeritabilityExtraction, GeneticCorrelationExtraction)


# ============================================================================
# Base Extractor
# ============================================================================

class BaseExtractor(ABC):
    """
    Abstract base class for information extractors.
    
    Uses structured prompting following best practices:
    - Developer prompt: Defines role, extraction rules, quality guards
    - User prompt: Provides paper metadata for extraction
    - JSON Schema: Constrains output for reliable parsing
    
    All extractors use centralized LLM config from src/core/llm_config.py
    """
    
    # Each subclass defines its task name for prompt lookup
    MAX_RETRIES: int = 3
    TASK_NAME: str = ""
    CONFIG_KEY: str = "literature_extractor"
    SCHEMA: Dict[str, Any] = None
    

    def __init__(self):
        """Initialize the extractor."""
        self._client = None
        self._model_name = None
        self._config = None
        self.lang_extractor = LangExtractor()
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client from centralized config."""
        if self._client is None:
            try:
                from src.core.llm_config import get_config
                from openai import OpenAI
                self._config = get_config(self.CONFIG_KEY)
                self._model_name = self._config.model
                self._client = OpenAI()
                logger.debug(f"{self.__class__.__name__} using model: {self._model_name}")
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
            _ = self.client
        return self._model_name or "unknown"
    
    @abstractmethod
    def _parse_response(self, paper: PaperMetadata, response_data: Dict) -> List[T]:
        """Parse LLM response into extraction objects."""
        pass
    
    def extract(self, paper: PaperMetadata) -> List[T]:
        """
        Extract structured data from a paper.
        
        Args:
            paper: Paper metadata with title and full text content
        
        Returns:
            List of extracted data objects (may be empty)
        """
        # Get prompts
        developer_prompt = get_prompt(self.TASK_NAME, "developer")
        
        # Use full text if available, otherwise fall back to abstract
        text_content = paper.full_text if hasattr(paper, 'full_text') and paper.full_text else paper.abstract
        if not text_content:
            text_content = "(No content available)"
        
        user_prompt = format_user_prompt(
            self.TASK_NAME,
            pmid=paper.pmid,
            title=paper.title,
            text=text_content,  # Full text or abstract as fallback
            journal=paper.journal or "Unknown",
            year=paper.publication_date.year if paper.publication_date else "Unknown"
        )
        
        try:
            messages = [
                {"role": "system", "content": developer_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use structured output to enforce schema if available
            if self.SCHEMA:
                # Check for strict mode configuration
                is_strict = getattr(self._config, 'strict', False)
                
                if is_strict:
                    # STRICT MODE: Use standard create with json_schema response_format
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        response_format=self.SCHEMA
                    )
                    
                    content = response.choices[0].message.content
                    data = self._parse_json(content)
                        
                else:
                    # LEGACY JSON MODE
                    # Add schema instructions to prompt for robust text-based extraction
                    schema_json = json.dumps(self.SCHEMA["json_schema"]["schema"], indent=2)
                    prompt_suffix = f"\n\nYou must output valid JSON strictly following this schema:\n```json\n{schema_json}\n```"
                    
                    # Append to the last user message
                    if isinstance(messages[-1], HumanMessage):
                        messages[-1].content += prompt_suffix
                    elif isinstance(messages[-1], dict) and messages[-1].get("role") == "user":
                        messages[-1]["content"] += prompt_suffix
                    
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        response_format={"type": "json_object"}
                    )
                    
                    content = response.choices[0].message.content
                    data = self._parse_json(content)

            else:
                # No schema - standard generation
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages
                )
                content = response.choices[0].message.content
                data = self._parse_json(content)
                
            if data is None:
                return []
            
            results = self._parse_response(paper, data)

            
            logger.info(
                f"{self.__class__.__name__}: Extracted {len(results)} items "
                f"from PMID:{paper.pmid}"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Extraction error for PMID:{paper.pmid}: {e}")
            return []
    
    def extract_batch(
        self,
        papers: List[PaperMetadata],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, List[T]]:
        """
        Extract from multiple papers.
        
        Args:
            papers: List of papers to process
            progress_callback: Optional callback(current, total)
        
        Returns:
            Dict mapping PMID to list of extractions
        """
        results = {}
        total = len(papers)
        
        for i, paper in enumerate(papers):
            extractions = self.extract(paper)
            if extractions:
                results[paper.pmid] = extractions
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results
    
    def _parse_json(self, content: str) -> Optional[Dict]:
        """Parse JSON from LLM response, handling code blocks."""
        try:
            # Handle markdown code blocks
            text = content.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}")
            logger.debug(f"Content: {content[:500]}")
            return None
    
    # =========================================================================
    # Common parsing utilities
    # =========================================================================
    
    def _parse_float(self, value: Any, convert_percent: bool = True) -> Optional[float]:
        """Safely parse a float value."""
        if value is None:
            return None
        try:
            f = float(value)
            if convert_percent and f > 1 and f <= 100:
                f = f / 100
            return f
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Safely parse an integer value."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(",", "").replace(" ", "")
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _get_evidence_html(self, paper: PaperMetadata, snippet: Optional[str]) -> Optional[str]:
        """Generate HTML evidence snippet if text is available."""
        if not snippet:
            return None
        
        text_content = paper.full_text if hasattr(paper, 'full_text') and paper.full_text else paper.abstract
        if not text_content:
            return None
            
        evidence = self.lang_extractor.locate_evidence(text_content, snippet)
        if evidence:
            return evidence.to_html_snippet()
        return None

# ============================================================================
# PRS Extractor
# ============================================================================

class PRSExtractor(BaseExtractor):
    """
    Extract PRS model performance data from papers.
    
    Extracts: AUC, R², C-index, OR/HR per SD, sample size, ancestry, method.
    """
    
    TASK_NAME = "prs_extraction"
    SCHEMA = PRS_EXTRACTION_SCHEMA
    
    def _parse_response(
        self,
        paper: PaperMetadata,
        response_data: Dict
    ) -> List[PRSModelExtraction]:
        """Parse LLM response into PRSModelExtraction objects."""
        results = []
        extractions = response_data.get("extractions", [])
        
        for i, item in enumerate(extractions):
            try:
                # Extract performance metrics
                metrics = item.get("performance_metrics", {})
                auc = self._parse_float(metrics.get("auc"))
                r2 = self._parse_float(metrics.get("r2"))
                c_index = self._parse_float(metrics.get("c_index"))
                or_per_sd = self._parse_float(metrics.get("or_per_sd"), convert_percent=False)
                
                # Skip if no metrics
                if not any([auc, r2, c_index, or_per_sd]):
                    logger.debug(f"Skipping extraction without metrics for PMID:{paper.pmid}")
                    continue
                
                # Extract model characteristics
                model_chars = item.get("model_characteristics", {})
                method = self._parse_prs_method(model_chars.get("method"))
                
                # Extract population info
                population = item.get("population", {})
                
                # Extract metadata
                metadata = item.get("extraction_metadata", {})
                
                extraction = PRSModelExtraction(
                    pmid=paper.pmid,
                    source=DataSource.LITERATURE_MINING,
                    trait=item.get("trait", ""),
                    auc=auc,
                    r2=r2,
                    c_index=c_index,
                    or_per_sd=or_per_sd,
                    variants_number=self._parse_int(model_chars.get("variants_number")),
                    method=method,
                    method_detail=model_chars.get("method_detail"),
                    sample_size=self._parse_int(population.get("sample_size")),
                    ancestry=population.get("ancestry"),
                    cohort=population.get("cohort"),
                    gwas_id=item.get("gwas_source", {}).get("gwas_id"),
                    publication=f"{paper.journal}, {paper.publication_date.year if paper.publication_date else ''}",
                    publication_year=paper.publication_date.year if paper.publication_date else None,
                    extraction_confidence=float(metadata.get("confidence", 0.7)),
                    raw_text_snippet=metadata.get("source_text", "")[:500],
                    evidence_html=self._get_evidence_html(paper, metadata.get("source_text"))
                )
                
                extraction.generate_id(sequence=i + 1)
                results.append(extraction)
                
            except Exception as e:
                logger.warning(f"Error parsing PRS extraction: {e}")
                continue
        
        return results
    
    def _parse_prs_method(self, method_str: Optional[str]) -> Optional[PRSMethod]:
        """Parse PRS method string to enum."""
        if not method_str:
            return None
        
        method_map = {
            "PRS-CS": PRSMethod.PRS_CS,
            "PRSCS": PRSMethod.PRS_CS,
            "LDpred2": PRSMethod.LDPRED2,
            "LDPRED2": PRSMethod.LDPRED2,
            "C+T": PRSMethod.CT,
            "P+T": PRSMethod.CT,
            "CT": PRSMethod.CT,
            "lassosum": PRSMethod.LASSOSUM,
            "PRSice": PRSMethod.PRSICE,
            "SBayesR": PRSMethod.SBAYESR,
        }
        
        method_upper = method_str.upper().replace("-", "").replace("+", "")
        for key, value in method_map.items():
            if key.upper().replace("-", "").replace("+", "") == method_upper:
                return value
        
        return PRSMethod.OTHER


# ============================================================================
# Heritability Extractor
# ============================================================================

class HeritabilityExtractor(BaseExtractor):
    """
    Extract SNP-heritability (h²) estimates from papers.
    
    Extracts: h², SE, method, sample size, ancestry, scale.
    """
    
    TASK_NAME = "heritability_extraction"
    SCHEMA = HERITABILITY_EXTRACTION_SCHEMA
    
    def _parse_response(
        self,
        paper: PaperMetadata,
        response_data: Dict
    ) -> List[HeritabilityExtraction]:
        """Parse LLM response into HeritabilityExtraction objects."""
        results = []
        extractions = response_data.get("extractions", [])
        
        for i, item in enumerate(extractions):
            try:
                # Extract heritability estimate
                h2_data = item.get("heritability_estimate", {})
                h2 = self._parse_h2(h2_data.get("h2"))
                
                if h2 is None:
                    continue
                
                # Extract method
                method_data = item.get("method", {})
                method = self._parse_h2_method(method_data.get("estimation_method"))
                
                # Extract population
                population = item.get("population", {})
                
                # Extract metadata
                metadata = item.get("extraction_metadata", {})
                
                # Parse new fields
                scale = h2_data.get("scale", "not_specified")
                if scale not in ["liability", "observed", "not_specified"]:
                    scale = "not_specified"
                
                extraction = HeritabilityExtraction(
                    id=f"H2-{paper.pmid}-{i+1:03d}",
                    pmid=paper.pmid,
                    source=DataSource.LITERATURE_MINING,
                    trait=item.get("trait", ""),
                    h2=h2,
                    se=self._parse_float(h2_data.get("se"), convert_percent=False),
                    scale=scale,
                    p_value=self._parse_float(h2_data.get("p_value"), convert_percent=False),
                    z_score=self._parse_float(h2_data.get("z_score"), convert_percent=False),
                    method=method,
                    method_detail=method_data.get("method_detail"),
                    intercept=self._parse_float(method_data.get("intercept"), convert_percent=False),
                    lambda_gc=self._parse_float(method_data.get("lambda_gc"), convert_percent=False),
                    sample_size=self._parse_int(population.get("sample_size")),
                    ancestry=population.get("ancestry"),
                    prevalence=self._parse_float(population.get("prevalence"), convert_percent=True),
                    publication=f"{paper.journal}, {paper.publication_date.year if paper.publication_date else ''}",
                    publication_year=paper.publication_date.year if paper.publication_date else None,
                    extraction_confidence=float(metadata.get("confidence", 0.7)),
                    raw_text_snippet=metadata.get("source_text", "")[:500],
                    evidence_html=self._get_evidence_html(paper, metadata.get("source_text"))
                )
                
                results.append(extraction)
                
            except Exception as e:
                logger.warning(f"Error parsing heritability extraction: {e}")
                continue
        
        return results
    
    def _parse_h2(self, value: Any) -> Optional[float]:
        """Parse h² value, handling percentages."""
        if value is None:
            return None
        try:
            h2 = float(value)
            if h2 > 1:
                h2 = h2 / 100
            if 0 <= h2 <= 1:
                return h2
            return None
        except (ValueError, TypeError):
            return None
    
    def _parse_h2_method(self, method_str: Optional[str]) -> Optional[HeritabilityMethod]:
        """Parse heritability method string to enum."""
        if not method_str:
            return None
        
        method_map = {
            "LDSC": HeritabilityMethod.LDSC,
            "GCTA": HeritabilityMethod.GCTA,
            "GREML": HeritabilityMethod.GREML,
            "BOLT-REML": HeritabilityMethod.BOLT_REML,
            "BOLTREML": HeritabilityMethod.BOLT_REML,
        }
        
        method_upper = method_str.upper().replace("-", "")
        for key, value in method_map.items():
            if key.replace("-", "") == method_upper:
                return value
        
        return HeritabilityMethod.OTHER


# ============================================================================
# Genetic Correlation Extractor
# ============================================================================

class GeneticCorrelationExtractor(BaseExtractor):
    """
    Extract genetic correlation (rg) data from papers.
    
    Extracts: trait pairs, rg, SE, p-value, method.
    """
    
    TASK_NAME = "genetic_correlation_extraction"
    SCHEMA = GENETIC_CORRELATION_EXTRACTION_SCHEMA
    
    def _parse_response(
        self,
        paper: PaperMetadata,
        response_data: Dict
    ) -> List[GeneticCorrelationExtraction]:
        """Parse LLM response into GeneticCorrelationExtraction objects."""
        results = []
        extractions = response_data.get("extractions", [])
        
        for i, item in enumerate(extractions):
            try:
                # Extract trait pair
                trait_pair = item.get("trait_pair", {})
                trait1 = trait_pair.get("trait1", "")
                trait2 = trait_pair.get("trait2", "")
                
                if not trait1 or not trait2:
                    continue
                
                # Extract correlation estimate
                corr = item.get("correlation_estimate", {})
                rg = self._parse_rg(corr.get("rg"))
                
                if rg is None:
                    continue
                
                # Extract method
                method_data = item.get("method", {})
                method = self._parse_rg_method(method_data.get("estimation_method"))
                
                # Extract population
                population = item.get("population", {})
                
                # Extract metadata
                metadata = item.get("extraction_metadata", {})
                
                extraction = GeneticCorrelationExtraction(
                    id=f"RG-{paper.pmid}-{i+1:03d}",
                    pmid=paper.pmid,
                    source=DataSource.LITERATURE_MINING,
                    trait1=trait1,
                    trait2=trait2,
                    rg=rg,
                    se=self._parse_float(corr.get("se"), convert_percent=False),
                    p_value=self._parse_pvalue(corr.get("p_value")),
                    method=method,
                    sample_size=self._parse_int(population.get("sample_size_trait1")),
                    ancestry=population.get("ancestry"),
                    publication=f"{paper.journal}, {paper.publication_date.year if paper.publication_date else ''}",
                    publication_year=paper.publication_date.year if paper.publication_date else None,
                    extraction_confidence=float(metadata.get("confidence", 0.7)),
                    raw_text_snippet=metadata.get("source_text", "")[:500],
                    evidence_html=self._get_evidence_html(paper, metadata.get("source_text"))
                )
                
                results.append(extraction)
                
            except Exception as e:
                logger.warning(f"Error parsing rg extraction: {e}")
                continue
        
        return results
    
    def _parse_rg(self, value: Any) -> Optional[float]:
        """Parse rg value, ensuring valid range."""
        if value is None:
            return None
        try:
            rg = float(value)
            if -1 <= rg <= 1:
                return rg
            return None
        except (ValueError, TypeError):
            return None
    
    def _parse_pvalue(self, value: Any) -> Optional[float]:
        """Parse p-value, handling scientific notation."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.lower().replace("×", "e").replace("x", "e")
                value = re.sub(r'\s*10\^?\s*', 'e', value)
            p = float(value)
            if 0 <= p <= 1:
                return p
            return None
        except (ValueError, TypeError):
            return None
    
    def _parse_rg_method(self, method_str: Optional[str]) -> Optional[GeneticCorrelationMethod]:
        """Parse genetic correlation method string to enum."""
        if not method_str:
            return None
        
        method_map = {
            "LDSC": GeneticCorrelationMethod.LDSC,
            "HDL": GeneticCorrelationMethod.HDL,
            "GNOVA": GeneticCorrelationMethod.GNOVA,
            "SuperGNOVA": GeneticCorrelationMethod.SUPERGNOVA,
            "SUPERGNOVA": GeneticCorrelationMethod.SUPERGNOVA,
        }
        
        method_upper = method_str.upper()
        return method_map.get(method_upper, GeneticCorrelationMethod.OTHER)


# ============================================================================
# Extractor Factory
# ============================================================================

class ExtractorFactory:
    """Factory for creating extractor instances.
    
    All extractors use centralized LLM config from src/core/llm_config.py
    """
    
    _extractors = {
        "prs": PRSExtractor,
        "heritability": HeritabilityExtractor,
        "genetic_correlation": GeneticCorrelationExtractor,
    }
    
    @classmethod
    def create(cls, extractor_type: str) -> BaseExtractor:
        """
        Create an extractor instance.
        
        Args:
            extractor_type: One of "prs", "heritability", "genetic_correlation"
        
        Returns:
            Extractor instance (uses centralized LLM config)
        """
        if extractor_type not in cls._extractors:
            raise ValueError(f"Unknown extractor type: {extractor_type}")
        
        return cls._extractors[extractor_type]()
    
    @classmethod
    def create_all(cls) -> Dict[str, BaseExtractor]:
        """Create all extractor instances."""
        return {
            name: cls.create(name)
            for name in cls._extractors
        }
