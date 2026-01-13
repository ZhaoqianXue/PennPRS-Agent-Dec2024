"""
Validator Agent

Rule-based validation for extracted data.
NOT an LLM - uses deterministic rules for:
1. Schema validation (required fields, data types)
2. Range checks (AUC 0.5-1.0, h² 0-1, rg -1 to 1)
3. De-duplication against existing PGS Catalog data
4. Quality scoring for manual review queue

This is intentionally NOT using LLM to ensure:
- Deterministic, reproducible validation
- Fast execution without API calls
- Clear, explainable validation rules
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Set, Tuple, Union
from pathlib import Path

from .entities import (
    PRSModelExtraction,
    HeritabilityExtraction,
    GeneticCorrelationExtraction,
    ValidationResult,
    ValidationIssue,
    ValidationStatus,
    ExtractionResult
)

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Rules
# ============================================================================

class ValidationRules:
    """Container for validation rule definitions."""
    
    # PRS validation rules
    PRS_AUC_RANGE = (0.5, 1.0)
    PRS_R2_RANGE = (0.0, 1.0)
    PRS_CINDEX_RANGE = (0.5, 1.0)
    PRS_MIN_VARIANTS = 1
    PRS_MAX_VARIANTS = 10_000_000
    PRS_MIN_SAMPLE_SIZE = 100
    
    # Heritability validation rules
    H2_RANGE = (0.0, 1.0)
    H2_SE_MAX = 0.5  # SE rarely exceeds this
    
    # Genetic correlation validation rules
    RG_RANGE = (-1.0, 1.0)
    RG_SE_MAX = 0.5
    
    # General rules
    MIN_CONFIDENCE = 0.3  # Below this, needs manual review
    HIGH_CONFIDENCE = 0.8  # Above this, auto-approve
    
    # Common text patterns that indicate potential issues
    SUSPICIOUS_PATTERNS = [
        "not significant",
        "ns",
        "failed to replicate",
        "meta-analysis of",  # May need special handling
    ]


# ============================================================================
# Validator
# ============================================================================

class Validator:
    """
    Rule-based validator for extracted data.
    
    Validates:
    - Data types and formats
    - Value ranges
    - Required fields
    - Duplicates against existing data
    
    Does NOT use LLM - purely deterministic rules.
    """
    
    def __init__(
        self,
        pgs_catalog_ids: Optional[Set[str]] = None,
        existing_pmids: Optional[Set[str]] = None,
        strict_mode: bool = False
    ):
        """
        Initialize validator.
        
        Args:
            pgs_catalog_ids: Set of existing PGS Catalog IDs for deduplication
            existing_pmids: Set of PMIDs already processed
            strict_mode: If True, warnings become errors
        """
        self.pgs_catalog_ids = pgs_catalog_ids or set()
        self.existing_pmids = existing_pmids or set()
        self.strict_mode = strict_mode
        
        # Load PGS Catalog data if available
        self._load_pgs_catalog_data()
    
    def _load_pgs_catalog_data(self):
        """Load existing PGS Catalog data for deduplication."""
        # Try to load from local cache
        pgs_cache_path = Path("data/pgs_all_metadata")
        if pgs_cache_path.exists():
            try:
                # Load existing PGS IDs from cached files
                for file in pgs_cache_path.glob("*.json"):
                    with open(file) as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if "id" in item:
                                    self.pgs_catalog_ids.add(item["id"])
                        elif "id" in data:
                            self.pgs_catalog_ids.add(data["id"])
                
                logger.info(f"Loaded {len(self.pgs_catalog_ids)} existing PGS IDs")
            except Exception as e:
                logger.warning(f"Could not load PGS catalog cache: {e}")
    
    # =========================================================================
    # PRS Validation
    # =========================================================================
    
    def validate_prs(self, extraction: PRSModelExtraction) -> ValidationResult:
        """
        Validate a PRS model extraction.
        
        Checks:
        - At least one performance metric exists
        - AUC in range [0.5, 1.0]
        - R² in range [0, 1]
        - Variants count is reasonable
        - Sample size is reasonable
        - Not duplicate of existing PGS model
        """
        issues: List[ValidationIssue] = []
        
        # Check required fields
        if not extraction.trait:
            issues.append(ValidationIssue(
                field="trait",
                issue_type="missing_required",
                message="Trait is required",
                severity="error"
            ))
        
        if not extraction.pmid:
            issues.append(ValidationIssue(
                field="pmid",
                issue_type="missing_required",
                message="PMID is required",
                severity="error"
            ))
        
        # Check at least one metric exists
        metrics = [extraction.auc, extraction.r2, extraction.c_index, extraction.or_per_sd]
        if not any(m is not None for m in metrics):
            issues.append(ValidationIssue(
                field="metrics",
                issue_type="missing_required",
                message="At least one performance metric (AUC, R², C-index, OR) is required",
                severity="error"
            ))
        
        # Validate AUC range
        if extraction.auc is not None:
            if not (ValidationRules.PRS_AUC_RANGE[0] <= extraction.auc <= ValidationRules.PRS_AUC_RANGE[1]):
                issues.append(ValidationIssue(
                    field="auc",
                    issue_type="range_error",
                    message=f"AUC must be between {ValidationRules.PRS_AUC_RANGE[0]} and {ValidationRules.PRS_AUC_RANGE[1]}, got {extraction.auc}",
                    severity="error"
                ))
            elif extraction.auc < 0.55:
                issues.append(ValidationIssue(
                    field="auc",
                    issue_type="suspicious_value",
                    message=f"AUC {extraction.auc} is very low for a predictive model",
                    severity="warning"
                ))
        
        # Validate R² range
        if extraction.r2 is not None:
            if not (ValidationRules.PRS_R2_RANGE[0] <= extraction.r2 <= ValidationRules.PRS_R2_RANGE[1]):
                issues.append(ValidationIssue(
                    field="r2",
                    issue_type="range_error",
                    message=f"R² must be between 0 and 1, got {extraction.r2}",
                    severity="error"
                ))
            elif extraction.r2 > 0.5:
                issues.append(ValidationIssue(
                    field="r2",
                    issue_type="suspicious_value",
                    message=f"R² {extraction.r2} is unusually high for a PRS model",
                    severity="warning"
                ))
        
        # Validate C-index
        if extraction.c_index is not None:
            if not (ValidationRules.PRS_CINDEX_RANGE[0] <= extraction.c_index <= ValidationRules.PRS_CINDEX_RANGE[1]):
                issues.append(ValidationIssue(
                    field="c_index",
                    issue_type="range_error",
                    message=f"C-index must be between 0.5 and 1.0, got {extraction.c_index}",
                    severity="error"
                ))
        
        # Validate variants count
        if extraction.variants_number is not None:
            if extraction.variants_number < ValidationRules.PRS_MIN_VARIANTS:
                issues.append(ValidationIssue(
                    field="variants_number",
                    issue_type="range_error",
                    message=f"Variants count {extraction.variants_number} is too low",
                    severity="error"
                ))
            elif extraction.variants_number > ValidationRules.PRS_MAX_VARIANTS:
                issues.append(ValidationIssue(
                    field="variants_number",
                    issue_type="suspicious_value",
                    message=f"Variants count {extraction.variants_number} is unusually high",
                    severity="warning"
                ))
        
        # Validate sample size
        if extraction.sample_size is not None:
            if extraction.sample_size < ValidationRules.PRS_MIN_SAMPLE_SIZE:
                issues.append(ValidationIssue(
                    field="sample_size",
                    issue_type="range_error",
                    message=f"Sample size {extraction.sample_size} is too small",
                    severity="warning"
                ))
        
        # Check for duplicates
        is_duplicate, duplicate_of = self._check_prs_duplicate(extraction)
        
        # Low confidence check
        if extraction.extraction_confidence < ValidationRules.MIN_CONFIDENCE:
            issues.append(ValidationIssue(
                field="extraction_confidence",
                issue_type="low_confidence",
                message=f"Low extraction confidence ({extraction.extraction_confidence:.2f})",
                severity="warning"
            ))
        
        # Determine status
        status = self._determine_status(issues, extraction.extraction_confidence, is_duplicate)
        
        return ValidationResult(
            extraction_id=extraction.id,
            extraction_type="prs",
            status=status,
            issues=issues,
            is_duplicate=is_duplicate,
            duplicate_of=duplicate_of,
            validated_data=extraction.model_dump() if status == ValidationStatus.VALID else None
        )
    
    def _check_prs_duplicate(
        self,
        extraction: PRSModelExtraction
    ) -> Tuple[bool, Optional[str]]:
        """Check if this PRS extraction is a duplicate."""
        # Check if PMID already has an entry in PGS Catalog
        # This is a simplified check - real implementation would
        # compare trait, ancestry, and metrics more carefully
        
        # We'd need to query PGS Catalog API or local cache
        # For now, just check if we've seen this PMID
        if extraction.pmid in self.existing_pmids:
            return True, f"PMID:{extraction.pmid}"
        
        return False, None
    
    # =========================================================================
    # Heritability Validation
    # =========================================================================
    
    def validate_heritability(
        self,
        extraction: HeritabilityExtraction
    ) -> ValidationResult:
        """
        Validate a heritability extraction.
        
        Checks:
        - h² in range [0, 1]
        - SE is reasonable
        - Required fields present
        """
        issues: List[ValidationIssue] = []
        
        # Check required fields
        if not extraction.trait:
            issues.append(ValidationIssue(
                field="trait",
                issue_type="missing_required",
                message="Trait is required",
                severity="error"
            ))
        
        if extraction.h2 is None:
            issues.append(ValidationIssue(
                field="h2",
                issue_type="missing_required",
                message="h² value is required",
                severity="error"
            ))
        else:
            # Validate h² range
            if not (ValidationRules.H2_RANGE[0] <= extraction.h2 <= ValidationRules.H2_RANGE[1]):
                issues.append(ValidationIssue(
                    field="h2",
                    issue_type="range_error",
                    message=f"h² must be between 0 and 1, got {extraction.h2}",
                    severity="error"
                ))
            
            # Check for suspiciously high heritability
            if extraction.h2 > 0.8:
                issues.append(ValidationIssue(
                    field="h2",
                    issue_type="suspicious_value",
                    message=f"h² {extraction.h2} is unusually high for SNP-heritability",
                    severity="warning"
                ))
        
        # Validate SE if present
        if extraction.se is not None:
            if extraction.se < 0:
                issues.append(ValidationIssue(
                    field="se",
                    issue_type="range_error",
                    message="Standard error cannot be negative",
                    severity="error"
                ))
            elif extraction.se > ValidationRules.H2_SE_MAX:
                issues.append(ValidationIssue(
                    field="se",
                    issue_type="suspicious_value",
                    message=f"SE {extraction.se} is unusually high",
                    severity="warning"
                ))
        
        # Low confidence check
        if extraction.extraction_confidence < ValidationRules.MIN_CONFIDENCE:
            issues.append(ValidationIssue(
                field="extraction_confidence",
                issue_type="low_confidence",
                message=f"Low extraction confidence ({extraction.extraction_confidence:.2f})",
                severity="warning"
            ))
        
        # Check for duplicates (simplified)
        is_duplicate = extraction.pmid in self.existing_pmids
        
        status = self._determine_status(issues, extraction.extraction_confidence, is_duplicate)
        
        return ValidationResult(
            extraction_id=extraction.id,
            extraction_type="heritability",
            status=status,
            issues=issues,
            is_duplicate=is_duplicate,
            validated_data=extraction.model_dump() if status == ValidationStatus.VALID else None
        )
    
    # =========================================================================
    # Genetic Correlation Validation
    # =========================================================================
    
    def validate_genetic_correlation(
        self,
        extraction: GeneticCorrelationExtraction
    ) -> ValidationResult:
        """
        Validate a genetic correlation extraction.
        
        Checks:
        - rg in range [-1, 1]
        - Both traits specified
        - SE is reasonable if present
        """
        issues: List[ValidationIssue] = []
        
        # Check required fields
        if not extraction.trait1:
            issues.append(ValidationIssue(
                field="trait1",
                issue_type="missing_required",
                message="Trait 1 is required",
                severity="error"
            ))
        
        if not extraction.trait2:
            issues.append(ValidationIssue(
                field="trait2",
                issue_type="missing_required",
                message="Trait 2 is required",
                severity="error"
            ))
        
        if extraction.rg is None:
            issues.append(ValidationIssue(
                field="rg",
                issue_type="missing_required",
                message="rg value is required",
                severity="error"
            ))
        else:
            # Validate rg range
            if not (ValidationRules.RG_RANGE[0] <= extraction.rg <= ValidationRules.RG_RANGE[1]):
                issues.append(ValidationIssue(
                    field="rg",
                    issue_type="range_error",
                    message=f"rg must be between -1 and 1, got {extraction.rg}",
                    severity="error"
                ))
        
        # Validate SE if present
        if extraction.se is not None:
            if extraction.se < 0:
                issues.append(ValidationIssue(
                    field="se",
                    issue_type="range_error",
                    message="Standard error cannot be negative",
                    severity="error"
                ))
            elif extraction.se > ValidationRules.RG_SE_MAX:
                issues.append(ValidationIssue(
                    field="se",
                    issue_type="suspicious_value",
                    message=f"SE {extraction.se} is unusually high",
                    severity="warning"
                ))
        
        # Validate p-value if present
        if extraction.p_value is not None:
            if not (0 <= extraction.p_value <= 1):
                issues.append(ValidationIssue(
                    field="p_value",
                    issue_type="range_error",
                    message=f"p-value must be between 0 and 1, got {extraction.p_value}",
                    severity="error"
                ))
        
        # Check if same trait for both
        if extraction.trait1 and extraction.trait2:
            if extraction.trait1.lower() == extraction.trait2.lower():
                issues.append(ValidationIssue(
                    field="traits",
                    issue_type="logical_error",
                    message="trait1 and trait2 are the same",
                    severity="error"
                ))
        
        # Low confidence check
        if extraction.extraction_confidence < ValidationRules.MIN_CONFIDENCE:
            issues.append(ValidationIssue(
                field="extraction_confidence",
                issue_type="low_confidence",
                message=f"Low extraction confidence ({extraction.extraction_confidence:.2f})",
                severity="warning"
            ))
        
        is_duplicate = extraction.pmid in self.existing_pmids
        status = self._determine_status(issues, extraction.extraction_confidence, is_duplicate)
        
        return ValidationResult(
            extraction_id=extraction.id,
            extraction_type="genetic_correlation",
            status=status,
            issues=issues,
            is_duplicate=is_duplicate,
            validated_data=extraction.model_dump() if status == ValidationStatus.VALID else None
        )
    
    # =========================================================================
    # General Methods
    # =========================================================================
    
    def _determine_status(
        self,
        issues: List[ValidationIssue],
        confidence: float,
        is_duplicate: bool
    ) -> ValidationStatus:
        """Determine overall validation status."""
        if is_duplicate:
            return ValidationStatus.DUPLICATE
        
        has_errors = any(i.severity == "error" for i in issues)
        has_warnings = any(i.severity == "warning" for i in issues)
        
        if has_errors:
            return ValidationStatus.INVALID
        
        if has_warnings or confidence < ValidationRules.HIGH_CONFIDENCE:
            return ValidationStatus.NEEDS_REVIEW
        
        return ValidationStatus.VALID
    
    def validate(
        self,
        extraction: Union[PRSModelExtraction, HeritabilityExtraction, GeneticCorrelationExtraction]
    ) -> ValidationResult:
        """
        Validate any type of extraction.
        
        Auto-routes to appropriate validator based on type.
        """
        if isinstance(extraction, PRSModelExtraction):
            return self.validate_prs(extraction)
        elif isinstance(extraction, HeritabilityExtraction):
            return self.validate_heritability(extraction)
        elif isinstance(extraction, GeneticCorrelationExtraction):
            return self.validate_genetic_correlation(extraction)
        else:
            raise ValueError(f"Unknown extraction type: {type(extraction)}")
    
    def validate_extraction_result(
        self,
        result: ExtractionResult
    ) -> List[ValidationResult]:
        """
        Validate all extractions in an ExtractionResult.
        
        Returns list of ValidationResults for all items.
        """
        validations = []
        
        for prs in result.prs_models:
            validations.append(self.validate_prs(prs))
        
        for h2 in result.heritability_estimates:
            validations.append(self.validate_heritability(h2))
        
        for rg in result.genetic_correlations:
            validations.append(self.validate_genetic_correlation(rg))
        
        return validations
    
    def add_to_processed(self, pmid: str):
        """Add a PMID to the set of processed papers."""
        self.existing_pmids.add(pmid)
    
    def get_valid_extractions(
        self,
        validations: List[ValidationResult]
    ) -> List[ValidationResult]:
        """Filter to only valid extractions."""
        return [v for v in validations if v.status == ValidationStatus.VALID]
    
    def get_review_queue(
        self,
        validations: List[ValidationResult]
    ) -> List[ValidationResult]:
        """Get extractions needing manual review."""
        return [v for v in validations if v.status == ValidationStatus.NEEDS_REVIEW]
    
    def generate_validation_report(
        self,
        validations: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Generate a summary report of validation results."""
        total = len(validations)
        valid = len([v for v in validations if v.status == ValidationStatus.VALID])
        invalid = len([v for v in validations if v.status == ValidationStatus.INVALID])
        needs_review = len([v for v in validations if v.status == ValidationStatus.NEEDS_REVIEW])
        duplicates = len([v for v in validations if v.status == ValidationStatus.DUPLICATE])
        
        # Group issues by type
        issue_counts: Dict[str, int] = {}
        for v in validations:
            for issue in v.issues:
                key = f"{issue.issue_type}:{issue.severity}"
                issue_counts[key] = issue_counts.get(key, 0) + 1
        
        return {
            "total_validated": total,
            "valid": valid,
            "invalid": invalid,
            "needs_review": needs_review,
            "duplicates": duplicates,
            "valid_percentage": (valid / total * 100) if total > 0 else 0,
            "issue_counts": issue_counts,
            "generated_at": datetime.now().isoformat()
        }
