# Heritability Classification & Extraction Strategy

> **Document Created**: January 14, 2026  
> **Last Updated**: January 15, 2026  
> **Related To**: `implementation_modules.md` - Module 1: Literature Mining Engine  
> **Purpose**: Document the validation strategy for Heritability classification and define the extraction schema

### Key Files

| Type | Path | Description |
|------|------|-------------|
| **Ground Truth Data** | `data/validation/heritability_gold_standard.json` | 200 labeled papers (100 positive, 100 negative) |
| **Build Script** | `scripts/build_heritability_ground_truth.py` | Script to generate ground truth dataset |
| **Test Script** | `scripts/test_heritability_classifier.py` | Script to evaluate classifier accuracy |
| **Test Results** | `data/test_results/heritability_classifier_test_*.json` | Detailed classification results |

---

## Background & Motivation

The PennPRS Agent's Literature Mining Engine uses LLM-based classification to identify papers containing:
1. **PRS Performance Metrics** - validated against PGS Catalog
2. **Heritability (h²) Estimates** - validation strategy needed ⬅️ *this document*
3. **Genetic Correlation (rg) Data** - validation strategy TBD

While PRS classification can be validated using the **PGS Catalog** as a gold standard (containing ~750+ curated papers with associated PMIDs), Heritability classification requires a different validation approach since there is no single equivalent "official" literature curation database for h² estimates.

---

## Question 1: How to Validate Heritability Classification Ability?

### The Challenge

Unlike PRS classification which can be validated using the **PGS Catalog** as a gold standard (~750+ curated papers with PMIDs), Heritability classification faces a unique challenge: **there is no equivalent "Heritability Catalog"** that curates papers reporting h² estimates.

### Our Implemented Solution

We constructed a **balanced ground truth dataset** with both positive and negative samples:

#### Positive Samples (Papers WITH heritability in abstract)
- **Source**: PubMed search using heritability-specific queries
- **Queries Used**:
  - `"SNP heritability"[Title/Abstract]`
  - `"SNP-heritability"[Title/Abstract]`
  - `"LD score regression"[Title/Abstract] AND heritability`
  - `GCTA[Title/Abstract] AND "heritability" AND "h2"`
- **Validation Method**: Keyword matching in abstract (verified presence of heritability-related patterns)
- **Pattern Examples**: `h² =`, `SNP-heritability`, `heritability estimate`, `LDSC heritability`
- **Samples Collected**: 100 papers

#### Negative Samples (Papers WITHOUT heritability in abstract)
- **Source**: PGS Catalog publications (PRS papers)
- **Rationale**: PRS papers typically focus on prediction, not heritability estimation
- **Validation Method**: Verified absence of heritability keywords in abstract
- **Samples Collected**: 100 papers

#### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Abstract-level validation** | Classifier only sees abstracts, so ground truth should be based on abstract content, not full text |
| **Balanced dataset (1:1)** | Equal positive/negative samples to properly measure both Recall and Precision |
| **PGS Catalog as negative source** | High-quality, curated PRS papers that rarely report h² values |
| **Keyword-based auto-labeling** | Scalable approach; papers with explicit h² patterns are reliably heritability papers |

### Implementation Details

```
Ground Truth Dataset Structure:

data/validation/heritability_gold_standard.json
├── metadata
│   ├── created: "2026-01-15"
│   ├── version: "1.0"
│   ├── total_positive: 100
│   └── total_negative: 100
├── positive_samples[]
│   ├── pmid, title, abstract
│   ├── expected_classification: { is_heritability: true }
│   ├── matched_patterns: ["SNP[- ]heritability", ...]
│   └── validation_status: "auto_keyword_match"
└── negative_samples[]
    ├── pmid, title, abstract
    ├── expected_classification: { is_heritability: false }
    └── validation_status: "auto_keyword_absence"
```

### Success Criteria & Results

| Metric | Target | Actual (Jan 15, 2026) | Status |
|--------|--------|----------------------|--------|
| **Recall** | ≥ 95% | **97.00%** | ✅ Achieved |
| **Precision** | ≥ 85% | **83.62%** | ⚠️ Slightly below |
| **F1 Score** | ≥ 0.90 | **0.8981** | ⚠️ Nearly achieved |
| **Specificity** | ≥ 80% | **81.00%** | ✅ Achieved |
| **Accuracy** | ≥ 85% | **89.00%** | ✅ Achieved |

### Alternative Approaches Considered (Not Used)

| Approach | Why Not Used |
|----------|--------------|
| **LD Hub papers as positive samples** | LD Hub contains GWAS papers, not papers that report h² - abstracts often don't mention heritability |
| **Manual annotation only** | Too time-consuming; keyword matching is reliable for heritability papers |
| **Full-text validation** | Classifier only processes abstracts, so validation should match classifier scope |

---

## Question 2: What Fields Should Heritability Extractor Extract?

> **Note**: The Heritability Extractor processes **full text** (not just abstracts), enabling extraction of detailed information that may not appear in abstracts. This includes p-values, LDSC intercepts, and other technical details typically found in the Methods or Results sections.

### Comparison with Major Databases (Verified January 2026)

Based on actual database schemas from Neale Lab UK Biobank LDSC, LD Hub, and GWAS Atlas:

#### Neale Lab UK Biobank LDSC Fields
| Column Name | Description |
|-------------|-------------|
| `h2` | SNP heritability (liability scale for binary phenotypes) |
| `h2_se` | Standard error of h² |
| `h2_pval` | P-value for h² > 0 |
| `prevalence` | Population prevalence (for binary phenotypes) |
| `N` | Effective sample size |
| `lambda_gc` | Genomic inflation factor |
| `intercept_ratio` | Proportion of inflation not explained by LD |

#### LD Hub Fields
| Field | Description |
|-------|-------------|
| h² | SNP heritability |
| SE | Standard error |
| Intercept | LDSC intercept (distinguishes polygenicity from confounding) |

#### GWAS Atlas Fields
| Column Name | Description |
|-------------|-------------|
| `SNPh2` | SNP heritability |
| `SNPh2_se` | Standard error |
| `SNPh2_z` | Z-statistics for h² |
| `LambdaGC` | Genomic inflation factor |
| `Intercept` | LDSC intercept |
| `Chi2` | Mean chi-squared |

### Corrected Field Comparison

| Field | Neale Lab | LD Hub | GWAS Atlas | Decision |
|-------|-----------|--------|------------|----------|
| **h²** | ✅ `h2` | ✅ | ✅ `SNPh2` | **Keep** |
| **SE** | ✅ `h2_se` | ✅ | ✅ `SNPh2_se` | **Keep** |
| **p-value** | ✅ `h2_pval` | ❌ | ❌ (has Z-score) | **Add** |
| **Scale** | ✅ (liability) | ✅ | ✅ | **Keep** |
| **Method** | ✅ (LDSC) | ✅ (LDSC) | ✅ (LDSC) | **Keep** |
| **Sample Size** | ✅ `N` | ✅ | varies | **Keep** |
| **Ancestry** | ❌ (UK only) | ✅ | ❌ (EUR/EAS) | **Keep** |
| **Prevalence** | ✅ | ✅ | ✅ | **Keep** |
| **Intercept** | ✅ `intercept_ratio` | ✅ | ✅ | **Add** |
| **Lambda GC** | ✅ `lambda_gc` | ❌ | ✅ `LambdaGC` | **Add** |
| **Z-score** | ❌ | ❌ | ✅ `SNPh2_z` | **Add** |

### Final Schema Decision

Based on industry standards, the Heritability Schema should include:

#### Fields to Keep (Core)

```python
heritability_estimate:
  ├── h2                 # SNP-heritability (0.0-1.0)
  ├── se                 # Standard Error
  └── scale              # liability/observed/not_specified

method:
  ├── estimation_method  # LDSC, GCTA, GREML, BOLT-REML, SumHer, HESS, other
  └── method_detail      # Additional details

population:
  ├── sample_size
  ├── ancestry
  └── prevalence         # For liability scale conversion

extraction_metadata:
  ├── confidence
  └── source_text
```

#### Fields to Add (Industry Standard)

| Field | Location | Type | Rationale |
|-------|----------|------|-----------|
| `p_value` | heritability_estimate | number \| null | Neale Lab has `h2_pval`; essential for quality filtering |
| `intercept` | method | number \| null | All 3 platforms have this; key QC metric for LDSC |
| `lambda_gc` | method | number \| null | Neale Lab + GWAS Atlas have this; genomic inflation indicator |
| `z_score` | heritability_estimate | number \| null | GWAS Atlas has this; can derive p-value if missing |

#### Fields to Remove (Not Industry Standard)

| Field | Reason |
|-------|--------|
| ~~`ci_lower`~~ | No major platform provides 95% CI |
| ~~`ci_upper`~~ | No major platform provides 95% CI |

### Updated Schema Structure

```python
# HERITABILITY_EXTRACTION_SCHEMA (Final)

heritability_estimate:
  ├── h2                 # SNP-heritability (0.0-1.0)
  ├── se                 # Standard Error
  ├── scale              # liability/observed/not_specified
  ├── p_value            # NEW: Statistical significance (Neale Lab)
  └── z_score            # NEW: Z-statistics (GWAS Atlas)

method:
  ├── estimation_method  # LDSC, GCTA, GREML, BOLT-REML, SumHer, HESS, other
  ├── method_detail      # Additional details
  ├── intercept          # NEW: LDSC intercept (all platforms)
  └── lambda_gc          # NEW: Genomic inflation factor

population:
  ├── sample_size
  ├── ancestry
  └── prevalence         # Population prevalence

extraction_metadata:
  ├── confidence
  └── source_text        # Verbatim quote from paper
```

---

## Implementation Roadmap

### Phase 1: Classifier Validation (Priority: High) ✅ COMPLETED

1. **Build Ground Truth Dataset** ✅
   - [x] Collect PMIDs from PubMed search for heritability papers (100 positive samples)
   - [x] Collect PMIDs from PGS Catalog for negative samples (100 negative samples)
   - [x] Create `data/validation/heritability_gold_standard.json`
   - [x] Create build script: `scripts/build_heritability_ground_truth.py`

2. **Run Validation Tests** ✅
   - [x] Test classifier on ground truth dataset (200 papers)
   - [x] Calculate Recall, Precision, F1
   - [x] Identify failure cases for prompt improvement
   - [x] Create test script: `scripts/test_heritability_classifier.py`
   - [x] Save results to: `data/test_results/heritability_classifier_test_*.json`

### Phase 2: Schema Enhancement (Priority: Medium) 🚧 PENDING

1. **Update Schema**
   - [ ] Add `p_value` to `heritability_estimate`
   - [ ] Add `intercept` to `method`
   - [ ] Add `gwas_source` section with `gwas_id` and `snp_count`

2. **Update Extractor Prompts**
   - [ ] Modify extraction prompts to capture new fields
   - [ ] Test extraction on sample papers

### Phase 3: Extraction Validation (Priority: Medium) 🚧 PENDING

1. **Validate Extraction Accuracy**
   - [ ] Compare extracted h² values against Neale Lab/LD Hub ground truth
   - [ ] Calculate accuracy metrics for numeric extraction
   - [ ] Identify common extraction errors

---

## Validation Test Results (Phase 1)

> **Test Date**: January 15, 2026  
> **Model**: gpt-4.1-nano  
> **Test Duration**: ~290 seconds (200 papers @ ~2 req/sec)

### Confusion Matrix

```
                        Predicted
                     h²=True   h²=False
Actual h²=True         97         3        → 97% Recall
Actual h²=False        19        81        → 81% Specificity
                       ↓
                    84% Precision
```

### Performance Metrics Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **True Positives** | 97 | Papers correctly identified as heritability |
| **True Negatives** | 81 | Papers correctly identified as non-heritability |
| **False Positives** | 19 | Non-h² papers incorrectly classified as h² |
| **False Negatives** | 3 | Heritability papers missed by classifier |
| **Recall** | 97.00% | Excellent - almost all h² papers detected |
| **Precision** | 83.62% | Good - some false alarms |
| **Specificity** | 81.00% | Good - correctly rejects most non-h² papers |
| **Accuracy** | 89.00% | Very good overall |
| **F1 Score** | 0.8981 | Excellent balance |

### Error Analysis

#### False Negatives (3 missed heritability papers)

| PMID | Issue |
|------|-------|
| 39813287 | Needs investigation |
| 34326547 | Needs investigation |
| 29472613 | Needs investigation |

*Recommendation: Review these papers to understand why they weren't classified as heritability.*

#### False Positives (19 papers incorrectly flagged as h²)

| PMID | Confidence | Likely Cause |
|------|------------|---------------|
| 31327509 | 0.80 | Discusses genetic architecture |
| 38153744 | 0.90 | Mentions heritability conceptually |
| 32873964 | 0.90 | PRS paper with genetic variance discussion |
| 34662357 | 0.80 | Genetic architecture terminology |
| 37181462 | 0.90 | Related genetic concepts |
| ... | ... | (14 more) |

*Recommendation: Refine prompts to require explicit h² numeric values, not just heritability discussion.*

### Key Findings

1. **Recall is excellent (97%)**: The classifier successfully identifies almost all papers that report heritability estimates.

2. **Precision needs improvement (84%)**: Some papers that discuss "heritability" or "genetic architecture" conceptually are being flagged even though they don't report specific h² values.

3. **Improvement suggestions**:
   - Strengthen prompt to require **specific h² numeric values**
   - Distinguish between "discussing heritability" vs "reporting h² estimates"
   - Add keywords like "h² =", "heritability was", "SNP-heritability of 0.XX" as strong indicators

### Files Generated

| File | Description |
|------|-------------|
| `data/validation/heritability_gold_standard.json` | Ground truth dataset (200 papers) |
| `scripts/build_heritability_ground_truth.py` | Script to build ground truth |
| `scripts/test_heritability_classifier.py` | Script to run validation test |
| `data/test_results/heritability_classifier_test_20260115_*.json` | Detailed test results |

---

## References

1. **LD Hub**: Zheng, J. et al. (2017). LD Hub: a centralized database and web interface for LD score regression. *Bioinformatics*, 33(2), 272-274. PMID: 27663502
2. **LDSC Method**: Bulik-Sullivan, B. et al. (2015). LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. *Nature Genetics*, 47(3), 291-295. PMID: 25642630
3. **Neale Lab UK Biobank**: https://nealelab.github.io/UKBB_ldsc/
4. **GWAS Atlas**: Watanabe, K. et al. (2019). A global overview of pleiotropy and genetic architecture in complex traits. *Nature Genetics*, 51, 1339-1348.

---

## Appendix: Example Heritability Papers for Testing

These papers are known to contain SNP-heritability estimates and can be used for initial classifier testing:

| PMID | Title (Abbreviated) | Trait | Method |
|------|---------------------|-------|--------|
| 25642630 | LD Score regression distinguishes confounding... | Multiple | LDSC |
| 26414676 | Genetic contributions to risk of schizophrenia... | Schizophrenia | LDSC |
| 28957414 | Genome-wide association analyses identify 44 risk variants... | Major depressive disorder | LDSC |
| 30104766 | Genome-wide association study identifies 74 loci... | Educational attainment | LDSC |

*Note: This list should be expanded during Phase 1 validation work.*
