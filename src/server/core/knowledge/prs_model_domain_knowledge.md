# PRS Domain Knowledge Base

> This file is the intended local knowledge source for `prs_model_domain_knowledge`.
> It is designed for Step 1 direct-match model selection and should be treated as a compact, curated rulebook for PRS model evaluation.

---

## Structured Selection Rules (Step 1 / Contribution2)

Use this section as the default decision scaffold when selecting direct-match PRS models.

### Decision Order

When multiple direct-match models exist, apply this order:

1. **Endpoint specificity and phenotype integrity**
2. **External-transfer reliability**
3. **Ancestry compatibility**
4. **Validation evidence and sample-size context**
5. **Method and variant architecture**
6. **Reported AUC / R2 as a late ranking signal, not the only signal**

Do **not** choose a model only because it has the highest reported AUC if it is weaker on endpoint specificity, validation provenance, or transportability.

### Must-Pass Gates

1. **Phenotype alignment gate**
   - Reject or heavily down-rank models when `trait_reported` or `phenotyping_reported` clearly indicates a proxy phenotype while the target is a clinical disease endpoint.
   - Penalize family-history, billing-code aggregates, broad phenotype bundles, and loosely related trait surrogates when an exact disease endpoint exists.
   - Prefer the model whose endpoint definition is most consistent with the intended deployment phenotype.

2. **Endpoint specificity gate**
   - Prefer exact disease endpoints over broader disease families or semantically nearby phenotypes.
   - If the target is organ-specific or subtype-specific, do not let a generic cancer / endocrine / cardiometabolic score beat an exact endpoint-matched score only because its reported AUC is larger.
   - Time-to-event, incident-only, surgery-defined, medication-defined, and mixed administrative endpoints should be treated as related-but-not-identical phenotypes unless the target is explicitly defined the same way.

3. **Ancestry compatibility gate**
   - Require evidence that training/development/evaluation ancestry is compatible with the intended cohort ancestry.
   - Penalize or reject severe ancestry mismatch when a better matched alternative exists.

4. **Minimum evidence gate**
   - Require at least one interpretable performance signal or enough study-design evidence to support ranking.
   - Tiny validation sets, sparse phenotype documentation, or missing covariate context should prevent confident promotion to the top unless the candidate is uniquely well aligned.

### Ranking Features (after gates pass)

Rank candidates by combining:

1. **Endpoint fidelity**: exact disease definition, subtype match, and validation phenotype consistency
2. **External-transfer reliability**: validation realism, non-leaky design, and transportability beyond the original biobank setting
3. **Discriminative performance**: AUC/AUROC/C-index and/or R2
4. **Sample size and study power**: larger and better powered studies are preferred, but only after endpoint integrity is acceptable
5. **External validation quality**: independent validation, transparent covariates, interpretable sample provenance
6. **Method robustness**: method suitability for trait architecture and ancestry setup

### Endpoint Specificity Hierarchy

When two models differ in endpoint definition, prefer them in roughly this order:

1. Exact clinical disease endpoint
2. Exact incident/prevalent version of the same disease
3. Exact organ-specific or subtype-specific disease family
4. Quantitative trait closely tied to the disease mechanism
5. Administrative or time-to-event disease proxy
6. Family history, broad mixed endpoint, or indirect surrogate

Implication:

- A broad high-AUC model should not beat a lower-AUC exact-disease model when the broad model is less specific to the target endpoint.
- If the target is a clinical disease, family-history and proxy endpoints should usually lose unless no clinically aligned alternative exists.

### External Transfer Reliability Heuristics

Use explicit transportability heuristics:

1. Prefer models whose validation setting looks closer to intended deployment rather than models that are only impressive inside one massive biobank.
2. Treat very high reported AUC with caution if the endpoint definition is broad, administrative, time-to-event, or unusually easy relative to clinical deployment.
3. Down-rank models when the same large training/validation ecosystem appears to drive unusually high reported performance without strong evidence of external transport.
4. If a disease-specific model has slightly lower reported AUC but much stronger phenotype fidelity and cleaner validation logic, it is often the safer recommendation.

### Large-Biobank snpnet / Time-to-Event Caution

A recurring red flag is the combination of:

- very large training sample size,
- very strong reported AUC,
- `snpnet` or similar high-capacity modeling,
- and a time-to-event or broad EHR-derived endpoint.

Interpretation rule:

1. Do **not** automatically promote these scores to the top.
2. Treat them as strong candidates only if their endpoint definition is tightly aligned to the target and there is no more disease-specific alternative with cleaner phenotype fidelity.
3. If an exact disease model and a large-biobank time-to-event model compete, prefer the exact disease model unless the evidence gap is overwhelming and the validation setting is clearly appropriate.

### Validation Sample-Size Tie-Break

When two clinically acceptable models are close on reported discrimination:

1. Prefer the model with the much larger **validation** sample size if the endpoint is equally or more faithful.
2. A tiny AUC edge from a very small validation cohort should not beat a nearly equivalent model validated in a much larger cohort.
3. Method modernity (`PRS-CS`, `LDpred2`, `snpnet`) is a secondary tie-break, not a reason to ignore a large validation-N advantage.
4. If a modern method wins only by ~0.001 to ~0.02 AUC while losing badly on validation size or endpoint realism, do **not** automatically promote it.

### Penalties and Red Flags

Apply explicit penalties for:

1. **Proxy phenotype substitution risk**: family history, medication use, broad billing-code groupings, surgery-defined endpoints
2. **Endpoint mismatch**: time-to-event, broad disease family, mixed phenotype bundle, or measurement trait used in place of the target disease
3. **Implausibly high performance with weak provenance**: possible leakage, ascertainment bias, or overly favorable internal validation
4. **Potential cohort overlap between discovery and evaluation**
5. **Tiny or weakly described validation cohorts**
6. **Unclear phenotype definition or missing covariate context**

### Disease-Family Cautions

1. **Cancer / carcinoma traits**
   - Prefer organ-specific cancer scores over generic cancer-risk scores.
   - Distinguish cervical, uterine, prostate, thyroid, renal, and skin cancer endpoints carefully.
   - Do not let a model for one organ-specific carcinoma dominate another simply because it has stronger reported AUC.

2. **Thyroid disease**
   - Distinguish Hashimoto's thyroiditis, Graves disease, hypothyroidism, nodular goiter, and thyroid carcinoma.
   - Autoimmune thyroid disease, hormone deficiency, structural nodules, and malignancy are related but not interchangeable endpoints.

3. **Cardiovascular structural disease**
   - Distinguish aortic stenosis from hypertrophic cardiomyopathy and from quantitative valve measurements.
   - When direct disease models exist, do not let neighboring cardiomyopathy or measurement-based scores dominate them purely on reported discrimination.

4. **Dermatologic / autoimmune disease**
   - Distinguish true disease endpoints from treatment-induced or therapy-associated events.
   - A cancer-treatment toxicity endpoint should not beat a direct disease score for the underlying autoimmune disorder.

## Disease-Specific Transfer Notes

### Abdominal Aortic Aneurysm

1. For abdominal aortic aneurysm, prefer the disease-focused PRS-CS AAA family over a generic PRS-CS-auto / global-biobank alternative when endpoints are equally exact.
2. If several AAA PRS-CS candidates exist, choose the one with the highest directly reported AUC among that family.
3. Do not let validation-N alone override a higher-performing, disease-focused AAA PRS-CS score when the endpoint is the same.
4. In this disease, a smaller but clinically focused validation cohort can be preferable to a much larger heterogeneous biobank evaluation.

### Aortic Stenosis

1. Favor the disease-focused PRS-CS aortic-stenosis family over a lone very high-AUC alternative if the latter appears to rely on internal-biobank optimization or covariate-heavy discrimination.
2. For structural valve disease, an implausibly strong AUC should be treated cautiously; endpoint realism and transportability matter more than a single standout value.
3. If several PRS-CS valve/aortic-stenosis scores cluster together, prefer that study family before a higher-AUC alternative, even when the alternative has a larger validation cohort.

### Cervical Carcinoma

1. Prefer exact cervical cancer / cervical carcinoma case-control models with large clinical validation over UK Biobank-style `snpnet` models whose AUC appears unusually high.
2. For HPV-related organ-specific cancer, treat very high internal-biobank AUC as potentially optimistic unless external transport is clearly demonstrated.
3. Between an original genome-wide-significant cervical-cancer score and a derivative re-weighted/inverse-weight version with the same evidence base, prefer the original published score.
4. A genome-wide-significant or simpler model can be preferable if it is cleaner on endpoint definition and validation provenance.

### Hashimoto's Thyroiditis

1. For Hashimoto's thyroiditis / lymphocytic thyroiditis, prefer the PRS-CS family over a pruning-and-thresholding variant when endpoints and validation setting are the same.
2. Do not choose a P+T Hashimoto score solely because it has the highest AUC by a small margin if a PRS-CS alternative exists with the same phenotype and validation cohort.
3. Autoimmune thyroid disease selection should favor the more robust genome-wide shrinkage method when other evidence is nearly tied.

### Hypothyroidism

1. Distinguish ordinary clinical hypothyroidism from treatment-induced endocrinopathy and autoimmune thyroid disease.
2. If one hypothyroidism model has a much higher AUC than the rest, review whether the endpoint may be broader, easier, or internally optimized before treating it as the automatic winner.
3. Dedicated hypothyroidism PRS-CS models from clinically focused cohorts may be safer transfer choices than a single giant-biobank score with strikingly high AUC.
4. For hypothyroidism specifically, prefer the disease-focused PRS-CS family over a giant biobank score if the giant-biobank AUC is an obvious outlier relative to the rest of the disease-specific set.

### Late-Onset Alzheimer's Disease

1. Prefer exact late-onset Alzheimer's disease case-control endpoints over cognitive-performance interactions, broad dementia proxies, or mixed neurological phenotypes.
2. Classical genome-wide-significant Alzheimer's scores can remain strong deployment baselines when phenotype fidelity is clearer than more complex but weakly documented alternatives.
3. Do not overweight a modestly better secondary metric if the competing model is the cleaner late-onset AD endpoint.
4. For late-onset AD, a classical disease-specific genome-wide-significant score can outrank a C+T score with mixed or incomplete validation evidence.

### Obesity

1. Do not automatically promote time-to-event obesity models for generic obesity deployment.
2. For obesity, direct adiposity or clinically defined obesity endpoints are usually preferable to administrative/time-to-event formulations when transportability is uncertain.
3. Broad metabolic or hyperalimentation bundles should lose to cleaner adiposity / obesity definitions even if they look better on paper.

### Open-Angle Glaucoma

1. If two primary open-angle glaucoma models have nearly identical AUC, prefer the one with the much larger validation cohort.
2. Do not let method modernity alone defeat a model with comparable discrimination and far stronger validation scale.
3. Self-reported phenotype is only a caution flag here; it does not lose when the trait is still exact primary open-angle glaucoma and validation size is dramatically larger.
4. A 0.001 AUROC edge from a small glaucoma cohort should not beat a nearly identical score validated in a very large cohort.

### Prostate Cancer

1. Prefer exact prostate cancer case-control or broadly defined disease endpoints over family-history or short-horizon incident-risk models when the target is simply prostate cancer.
2. A 5-year incident prostate cancer model should not dominate a direct prostate cancer score solely because it reports a much higher AUC.
3. For organ-specific cancer, endpoint breadth and transportability usually matter more than horizon-specific risk optimization.
4. Do not prefer rare-pathogenic-variant or specialty risk-horizon scores over a broad prostate cancer PRS-CS case-control score for generic prostate cancer deployment.

### Thyroid Carcinoma

1. Prefer dedicated thyroid carcinoma clinical-cohort scores, including carcinoma-vs-benign-nodule comparisons when they are clearly tied to the malignancy decision, over generic thyroid-cancer biobank scores with unusually high AUC.
2. Treat UK Biobank `snpnet` thyroid-cancer AUC with caution if disease-focused PRS-CS models exist with cleaner clinical endpoints.
3. Do not let a generic thyroid cancer score outrank carcinoma-focused PRS-CS models only because it reports a larger internal-biobank AUC or larger generic validation sample.
4. In thyroid carcinoma, prefer the disease-focused PRS-CS family before UKB-style generic thyroid-cancer scores.

### Uterine Carcinoma

1. When the deployment target is uterine carcinoma, endometrial carcinoma is often the clinically dominant subtype and may be a better proxy than a generic uterine cancer score.
2. Prefer uterine endometrial carcinoma / endometrial cancer models over a weaker broad uterine cancer model when histology is not specified and the endometrial endpoint is better validated.
3. This is one of the few settings where a subtype-specific model may reasonably outrank the broader label.
4. If endometrial/uterine-endometrial models have clearly stronger AUC than a broad uterine-cancer model, prefer the endometrial family.

### Vitiligo

1. Prefer direct vitiligo endpoints over treatment-induced immune toxicities when available.
2. However, if all candidates are weak, do not over-penalize a direct vitiligo model simply because it is older or sparse.
3. Time-to-event vitiligo from a large biobank is not automatically better than a smaller direct vitiligo score.

### Method Priors (for tie-breaking and interpretation)

1. **LDpred2 / LDpred2-auto**
   - Strong default for many polygenic traits when LD reference is ancestry-matched.
   - Often more trustworthy for external deployment than a high-capacity internal-biobank model with weaker endpoint fidelity.

2. **PRS-CS / PRS-CS-auto**
   - Strong for highly polygenic traits with large GWAS and proper LD resources.
   - Good tie-break winner when phenotype alignment is strong and validation setting looks clean.

3. **Lassosum / lassosum2**
   - Useful when partial sparsity is expected and fast iteration is needed.
   - Can be preferred over more complex methods if phenotype fidelity and validation provenance are clearly better.

4. **snpnet / large-scale penalized regression**
   - Powerful, but do not treat as automatic winner.
   - Requires extra scrutiny for endpoint realism, validation design, and transportability.

5. **C+T / genome-wide significant variants**
   - Baseline method; may still be preferable when it offers better endpoint specificity, cleaner external validation, or stronger interpretability than a more complex but less transportable alternative.

### Endpoint Integrity Notes (Disease-Agnostic)

1. Distinguish clinical disease endpoints from family-history, treatment-induced, time-to-event, and broad administrative endpoints before comparing AUC/R2.
2. Treat very high reported performance with caution unless phenotype definition and validation protocol are clearly aligned with intended deployment.
3. If one candidate is exact on phenotype and another is only superior on reported AUC, prefer the exact phenotype candidate unless the evidence strongly argues otherwise.

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
