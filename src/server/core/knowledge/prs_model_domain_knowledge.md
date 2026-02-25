# PRS Domain Knowledge Base

> This file serves as the local knowledge source for `prs_model_domain_knowledge` tool.
> Future versions will upgrade to web search with constrained domains.

---

## Structured Selection Rules (Step 1 / Contribution2)

Use this section as the default decision scaffold when selecting direct-match PRS models.

### Must-Pass Gates

1. **Phenotype alignment gate**
   - Reject models when `trait_reported` or `phenotyping_reported` clearly indicates a proxy phenotype (for example, family-history-only endpoints) while the target is a clinical disease endpoint.
   - Prefer the model whose endpoint definition is most consistent with deployment phenotype coding.

2. **Ancestry compatibility gate**
   - Require evidence that training/development/evaluation ancestry is compatible with the target cohort ancestry.
   - Penalize or reject models with severe ancestry mismatch when a matched-ancestry alternative exists.

3. **Minimum evidence gate**
   - Require at least one usable discriminative performance metric (AUC/AUROC/C-index for binary traits, R2 for quantitative traits) and interpretable sample-size context.

### Ranking Features (after gates pass)

Rank candidates by combining:

1. **Discriminative performance**: AUC/AUROC/C-index and/or R2
2. **Sample size and study power**: larger and better powered studies are preferred
3. **External validation quality**: independent validation and transparent covariate reporting
4. **Method robustness**: method suitability for trait architecture and ancestry setup

### Penalties and Red Flags

Apply explicit penalties for:

1. **Proxy phenotype substitution risk** (family history used as disease surrogate)
2. **Implausibly high performance with weak provenance** (possible leakage/ascertainment bias)
3. **Potential cohort overlap between discovery and evaluation**
4. **Unclear phenotype definition or missing covariate context**

### Method Priors (for tie-breaking and interpretation)

1. **LDpred2 / LDpred2-auto**
   - Strong default for many polygenic traits when LD reference is ancestry-matched.
2. **PRS-CS / PRS-CS-auto**
   - Strong for highly polygenic traits with large GWAS and proper LD resources.
3. **Lassosum2**
   - Useful when partial sparsity is expected and fast iteration is needed.
4. **C+T**
   - Baseline method; use for sanity checks or low-resource settings, not as default winner for highly polygenic traits.

### Endpoint Integrity Notes (Disease-Agnostic)

1. Distinguish clinical disease endpoints from family-history or broad proxy endpoints before comparing AUC/R2 across models.
2. Treat very high reported performance with caution unless phenotype definition and validation protocol are clearly aligned with intended deployment.

---

## Model Selection Guidelines

### LDpred2

**Best For:** Large-effect polygenic traits with moderate-to-high heritability (e.g., height, BMI, psychiatric disorders).

**Key Strengths:**
- Bayesian framework with automatic shrinkage
- Handles LD structure from external reference panels
- `auto` mode requires minimal hyperparameter tuning
- Robust performance across ancestry groups when matched LD panels used

**Limitations:**
- Computationally intensive for very large GWAS
- Requires well-matched LD reference panel
- May underperform for rare variant traits

**Recommended Sample Size:** N > 50,000 for optimal performance.

**Citation:** Prive et al. (2021) Bioinformatics. PMID: 33326037

---

### PRS-CS

**Best For:** Highly polygenic traits with large discovery GWAS (e.g., schizophrenia, educational attainment).

**Key Strengths:**
- Continuous shrinkage prior handles polygenicity well
- `auto` mode estimates global shrinkage from data
- Excellent cross-ancestry transferability with ancestry-matched LD
- Fast computation with pre-computed LD matrices

**Limitations:**
- Requires pre-computed LD reference (1000G or UK Biobank)
- Fixed phi mode may need grid search
- Less optimal for oligogenic traits

**Recommended Sample Size:** N > 100,000 for best results.

**Citation:** Ge et al. (2019) Nature Communications. PMID: 30992449

---

### Lassosum2

**Best For:** Traits where sparsity is expected (fewer large-effect variants).

**Key Strengths:**
- L1 regularization induces sparsity
- Fast computation
- Good for traits with moderate polygenicity
- Handles correlated variants well via elastic net

**Limitations:**
- May miss small-effect variants in highly polygenic traits
- Hyperparameter tuning required (lambda, s)
- Less flexible than fully Bayesian methods

**Recommended Sample Size:** N > 30,000.

**Citation:** Mak et al. (2017) Genetic Epidemiology. PMID: 28295174

---

### C+T (Clumping + Thresholding)

**Best For:** Quick baseline PRS; traits with sparse genetic architecture.

**Key Strengths:**
- Simple and fast
- No LD reference panel required (uses summary stats directly)
- Good baseline for comparison
- Works well for Mendelian-like traits

**Limitations:**
- Suboptimal for highly polygenic traits
- Sensitive to p-value threshold choice
- Ignores LD information beyond clumping window

**Recommended Sample Size:** Any (but larger is better).

**Citation:** International Schizophrenia Consortium (2009) Nature. PMID: 19571811

---

## Ancestry Considerations

### European (EUR)
- Most GWAS data available
- Best-performing PRS due to sample size
- Reference: 1000G EUR, UK Biobank

### East Asian (EAS)
- Growing GWAS availability (BBJ, China Kadoorie)
- Use EAS-matched LD panel (1000G EAS)
- Cross-ancestry transfer may reduce R² by 20-50%

### African (AFR)
- Highest genetic diversity
- PRS transferability lowest (~10-30% of EUR R²)
- Requires AFR-specific GWAS for best performance
- Multi-ancestry methods (PRS-CSx) recommended

### South Asian (SAS)
- Moderate GWAS availability
- SAS-matched LD panels improving
- Consider admixture-aware methods

### Admixed Populations
- Use local ancestry-aware methods
- PRS-CSx or SDPR for multi-ancestry training
- Validate in matched cohort if possible

---

## Quality Control Thresholds

### GWAS Summary Statistics QC

| Metric | Recommended Threshold |
|:-------|:----------------------|
| Sample Size | N > 10,000 (minimum) |
| SNP Count | > 500,000 HapMap3 SNPs |
| Lambda GC | 1.0 - 1.2 (no inflation) |
| Intercept (LDSC) | < 1.1 |
| h² SNP (LDSC) | Significantly > 0 |

### Model Performance Benchmarks

| Trait Type | Good AUC | Excellent AUC |
|:-----------|:---------|:--------------|
| Binary (disease) | > 0.65 | > 0.75 |
| Quantitative | N/A | N/A |

| Trait Type | Good R² | Excellent R² |
|:-----------|:--------|:-------------|
| Quantitative | > 0.05 | > 0.15 |
| Binary (liability) | > 0.03 | > 0.10 |

---

## Cross-Disease Transfer Learning

### When to Consider Transfer Learning

1. **Low sample size for target trait** (N < 50,000)
2. **High genetic correlation** (|rg| > 0.5) with well-powered trait
3. **Shared biological mechanisms** confirmed via pathway analysis
4. **Ancestry-matched populations** between source and target

### Transfer Learning Approaches

1. **Multi-trait PRS (mtPRS):**
   - Weight source PRS by rg
   - Combine with target-specific PRS
   - Best when rg is high and target GWAS underpowered

2. **MTAG (Multi-Trait Analysis of GWAS):**
   - Joint analysis increases effective sample size
   - Works well for correlated traits
   - Requires summary stats only

3. **PRS-CS-mult:**
   - Multi-ancestry extension of PRS-CS
   - Leverages shared genetic architecture
   - Better cross-population transfer

---

## Common Pitfalls

1. **LD Reference Mismatch:** Using EUR LD panel for EAS samples dramatically reduces performance.

2. **Winner's Curse:** Validating in overlapping discovery cohort inflates R².

3. **Phenotype Heterogeneity:** "Type 2 Diabetes" from UK Biobank vs. hospital records may differ.

4. **Covariate Adjustment:** Always adjust for age, sex, and population structure (PCs).

5. **Overfitting p-value Threshold:** Use nested cross-validation for C+T threshold selection.

---

## Recommended Workflow

1. **Start with C+T** as a baseline (fast, interpretable)
2. **Try LDpred2-auto** for most traits (good default)
3. **Use PRS-CS-auto** for highly polygenic traits
4. **Compare performance** on held-out validation set
5. **Consider multi-ancestry methods** if diverse target population

---

## References

- Choi SW et al. (2020) Tutorial: a guide to performing polygenic risk score analyses. *Nature Protocols*. PMID: 32709988
- Wand H et al. (2021) Improving reporting standards for polygenic scores. *Nature*. PMID: 33828378
- Martin AR et al. (2019) Clinical use of current polygenic risk scores may exacerbate health disparities. *Nature Genetics*. PMID: 30926966
