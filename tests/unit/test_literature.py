"""
Tests for the Literature Mining Module

Run with: pytest tests/test_literature.py -v
"""

import pytest
from datetime import date, datetime
from typing import List

from pydantic import ValidationError as PydanticValidationError

from src.modules.literature.entities import (
    PaperMetadata,
    ClassificationResult,
    CategoryScore,
    PaperCategory,
    PRSModelExtraction,
    HeritabilityExtraction,
    GeneticCorrelationExtraction,
    GeneticCorrelationMethod,
    ValidationResult,
    ValidationStatus,
    PRSMethod,
    HeritabilityMethod,
    DataSource
)
from src.modules.literature.validator import Validator, ValidationRules
from src.modules.literature.paper_classifier import RuleBasedClassifier


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_paper() -> PaperMetadata:
    """Create a sample paper for testing."""
    return PaperMetadata(
        pmid="12345678",
        title="Polygenic risk score for Alzheimer's disease",
        abstract="""
        We developed a polygenic risk score (PRS) for Alzheimer's disease using 
        genome-wide association study data from 455,258 individuals. The PRS 
        achieved an AUC of 0.78 in an independent European cohort. The model 
        includes 84 variants and was constructed using PRS-CS method. 
        SNP-heritability was estimated at h2 = 0.24 (SE = 0.03) using LDSC.
        """,
        authors=["John Smith", "Jane Doe"],
        journal="Nature Genetics",
        publication_date=date(2024, 1, 15),
        doi="10.1038/ng.12345"
    )


@pytest.fixture
def sample_prs_extraction() -> PRSModelExtraction:
    """Create a sample PRS extraction."""
    return PRSModelExtraction(
        id="LIT-ALZ-2024-001",
        pmid="12345678",
        source=DataSource.LITERATURE_MINING,
        trait="Alzheimer's Disease",
        auc=0.78,
        r2=0.08,
        variants_number=84,
        method=PRSMethod.PRS_CS,
        sample_size=455258,
        ancestry="European",
        extraction_confidence=0.85
    )


@pytest.fixture
def sample_h2_extraction() -> HeritabilityExtraction:
    """Create a sample heritability extraction."""
    return HeritabilityExtraction(
        id="H2-12345678-001",
        pmid="12345678",
        source=DataSource.LITERATURE_MINING,
        trait="Alzheimer's Disease",
        h2=0.24,
        se=0.03,
        method=HeritabilityMethod.LDSC,
        sample_size=455258,
        ancestry="European",
        extraction_confidence=0.9
    )


@pytest.fixture
def sample_rg_extraction() -> GeneticCorrelationExtraction:
    """Create a sample genetic correlation extraction."""
    return GeneticCorrelationExtraction(
        id="RG-12345678-001",
        pmid="12345678",
        source=DataSource.LITERATURE_MINING,
        trait1="Alzheimer's Disease",
        trait2="Type 2 Diabetes",
        rg=0.38,
        se=0.05,
        p_value=1.2e-8,
        method=GeneticCorrelationMethod.LDSC,
        extraction_confidence=0.85
    )


# ============================================================================
# Model Tests
# ============================================================================

class TestPaperMetadata:
    """Tests for PaperMetadata model."""
    
    def test_create_paper(self, sample_paper):
        """Test creating a paper metadata object."""
        assert sample_paper.pmid == "12345678"
        assert "Alzheimer" in sample_paper.title
        assert len(sample_paper.authors) == 2
    
    def test_pubmed_url(self, sample_paper):
        """Test PubMed URL generation."""
        assert sample_paper.pubmed_url == "https://pubmed.ncbi.nlm.nih.gov/12345678/"


class TestClassificationResult:
    """Tests for ClassificationResult model."""
    
    def test_relevant_paper(self):
        """Test classification of relevant paper."""
        result = ClassificationResult(
            pmid="12345678",
            categories=[
                CategoryScore(
                    category=PaperCategory.PRS_PERFORMANCE,
                    confidence=0.9
                ),
                CategoryScore(
                    category=PaperCategory.HERITABILITY,
                    confidence=0.7
                )
            ],
            primary_category=PaperCategory.PRS_PERFORMANCE,
            overall_confidence=0.9
        )
        
        assert result.is_relevant
        assert result.has_prs
        assert result.has_heritability
        assert not result.has_genetic_correlation
    
    def test_not_relevant_paper(self):
        """Test classification of non-relevant paper."""
        result = ClassificationResult(
            pmid="12345678",
            categories=[
                CategoryScore(
                    category=PaperCategory.NOT_RELEVANT,
                    confidence=0.95
                )
            ],
            primary_category=PaperCategory.NOT_RELEVANT,
            overall_confidence=0.95
        )
        
        assert not result.is_relevant
        assert not result.has_prs


class TestPRSModelExtraction:
    """Tests for PRS extraction model."""
    
    def test_valid_extraction(self, sample_prs_extraction):
        """Test valid PRS extraction."""
        assert sample_prs_extraction.auc == 0.78
        assert sample_prs_extraction.method == PRSMethod.PRS_CS
        assert sample_prs_extraction.source == DataSource.LITERATURE_MINING
    
    def test_generate_id(self):
        """Test ID generation."""
        extraction = PRSModelExtraction(
            pmid="12345678",
            trait="Alzheimer's Disease",
            auc=0.75
        )
        
        generated_id = extraction.generate_id(sequence=1)
        assert generated_id.startswith("LIT-ALZ-")
        assert "-001" in generated_id
    
    def test_auc_validation(self):
        """Test AUC range validation."""
        # Valid AUC
        extraction = PRSModelExtraction(
            pmid="12345678",
            trait="Test",
            auc=0.75
        )
        assert extraction.auc == 0.75
        
        # AUC below 0.5 should be rejected
        extraction2 = PRSModelExtraction(
            pmid="12345678",
            trait="Test",
            auc=0.3
        )
        assert extraction2.auc is None  # Validator converts invalid to None


# ============================================================================
# Validator Tests
# ============================================================================

class TestValidator:
    """Tests for the Validator."""
    
    @pytest.fixture
    def validator(self):
        return Validator()
    
    def test_valid_prs(self, validator, sample_prs_extraction):
        """Test validation of valid PRS extraction."""
        result = validator.validate_prs(sample_prs_extraction)
        
        assert result.status == ValidationStatus.VALID
        assert not result.has_errors
        assert result.validated_data is not None
    
    def test_invalid_prs_no_metrics(self, validator):
        """Test PRS without any metrics is invalid."""
        extraction = PRSModelExtraction(
            pmid="12345678",
            trait="Alzheimer's Disease"
            # No metrics (auc, r2, etc.)
        )
        
        result = validator.validate_prs(extraction)
        
        assert result.status == ValidationStatus.INVALID
        assert result.has_errors
        assert any("metric" in str(i.message).lower() for i in result.issues)
    
    def test_invalid_prs_out_of_range_auc(self, validator):
        """Test PRS with out-of-range AUC - Pydantic rejects at creation."""
        # Pydantic validates ranges at object creation time
        with pytest.raises(PydanticValidationError) as exc_info:
            PRSModelExtraction(
                pmid="12345678",
                trait="Alzheimer's Disease",
                auc=1.5  # Invalid: > 1.0
            )
        
        assert "auc" in str(exc_info.value).lower()
    
    def test_valid_heritability(self, validator, sample_h2_extraction):
        """Test validation of valid heritability extraction."""
        result = validator.validate_heritability(sample_h2_extraction)
        
        assert result.status == ValidationStatus.VALID
        assert not result.has_errors
    
    def test_invalid_heritability_out_of_range(self, validator):
        """Test heritability with out-of-range h2 - Pydantic rejects at creation."""
        # Pydantic validates ranges at object creation time
        with pytest.raises(PydanticValidationError) as exc_info:
            HeritabilityExtraction(
                pmid="12345678",
                trait="Test",
                h2=1.5  # Invalid: > 1.0
            )
        
        assert "h2" in str(exc_info.value).lower() or "h²" in str(exc_info.value)
    
    def test_valid_genetic_correlation(self, validator, sample_rg_extraction):
        """Test validation of valid genetic correlation."""
        result = validator.validate_genetic_correlation(sample_rg_extraction)
        
        assert result.status == ValidationStatus.VALID
        assert not result.has_errors
    
    def test_invalid_rg_same_traits(self, validator):
        """Test that same trait1 and trait2 is invalid."""
        extraction = GeneticCorrelationExtraction(
            pmid="12345678",
            trait1="Alzheimer's Disease",
            trait2="Alzheimer's Disease",  # Same as trait1
            rg=0.5
        )
        
        result = validator.validate_genetic_correlation(extraction)
        
        assert result.status == ValidationStatus.INVALID
        assert any("same" in str(i.message).lower() for i in result.issues)
    
    def test_validation_report(self, validator, sample_prs_extraction, sample_h2_extraction):
        """Test validation report generation."""
        validations = [
            validator.validate_prs(sample_prs_extraction),
            validator.validate_heritability(sample_h2_extraction)
        ]
        
        report = validator.generate_validation_report(validations)
        
        assert "total_validated" in report
        assert report["total_validated"] == 2
        assert "valid_percentage" in report


# ============================================================================
# Rule-Based Classifier Tests
# ============================================================================

class TestRuleBasedClassifier:
    """Tests for the rule-based classifier."""
    
    @pytest.fixture
    def classifier(self):
        return RuleBasedClassifier()
    
    def test_classify_prs_paper(self, classifier, sample_paper):
        """Test classification of PRS paper."""
        result = classifier.classify(sample_paper)
        
        assert result.is_relevant
        assert result.has_prs
        # The abstract also mentions heritability
        assert result.has_heritability
    
    def test_classify_non_relevant(self, classifier):
        """Test classification of non-relevant paper."""
        paper = PaperMetadata(
            pmid="99999999",
            title="Effects of exercise on cardiovascular health",
            abstract="This randomized controlled trial examined the effects of aerobic exercise on cardiovascular outcomes in healthy adults."
        )
        
        result = classifier.classify(paper)
        
        assert not result.is_relevant
        assert result.primary_category == PaperCategory.NOT_RELEVANT


# ============================================================================
# Integration Tests (require API keys)
# ============================================================================

@pytest.mark.skipif(
    False,  # Run integration tests
    reason="Integration tests enabled"
)
class TestPubMedIntegration:
    """Integration tests for PubMed API."""
    
    def test_search(self):
        from src.modules.literature.pubmed import PubMedClient
        
        client = PubMedClient()
        result = client.search("Alzheimer's disease polygenic risk score", max_results=5)
        
        assert result.total_count > 0
        assert len(result.pmids) <= 5
    
    def test_fetch_paper(self):
        from src.modules.literature.pubmed import PubMedClient
        
        client = PubMedClient()
        # Use a known PMID
        papers = client.fetch_papers(["30617256"])
        
        assert len(papers) == 1
        assert papers[0].pmid == "30617256"
        assert papers[0].title  # Has a title


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
