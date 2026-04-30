## 5. method_name

Key empirical finding:

- `method_name` is a structural signal that helps separate candidates when endpoint fidelity and performance evidence are already comparable.
- Method properties are informative for differentiating candidates only after endpoint alignment, covariate comparability, and available performance evidence have been considered. Method alone does not override empirical evidence from the same disease family.
- Within the same publication family, empirical evidence takes precedence over methodological ranking. When two siblings from the same study share the same endpoint and covariates but use different methods, the sibling with stronger reported discrimination (higher AUC, stronger effect sizes) is the stronger choice, not the one with stronger methodological properties.
- For diseases with strong individual-locus effects (e.g., Hodgkin lymphoma, testicular cancer, bladder cancer, macular degeneration), sparse or variant-selection-based models can outperform genome-wide shrinkage methods because the genetic architecture is concentrated in a few major loci rather than distributed across the genome.
- Method modernity alone is not a quality proxy.

### Methodological principles

Two broad method distinctions have consistent empirical support for predicting external validation performance:

**Principle A — Multi-score aggregation outperforms single-score construction**

Methods that aggregate, ensemble, or optimally combine multiple component polygenic scores into a single composite consistently achieve stronger real-world external validation performance. They capture complementary genetic signals across different GWAS sources, method families, or ancestry backgrounds. When available for the target disease, a multi-score aggregation method is a positive structural signal over any single-score method.

Identification clues: method names or descriptions suggesting combination, mixing, summation, weighted aggregation, meta-scoring, or ensemble of multiple PRS components.

**Principle B — Genome-wide shrinkage outperforms sparse/thresholding for polygenic traits**

- Genome-wide continuous shrinkage methods model all or most variants simultaneously, applying continuous regularization to effect sizes rather than hard selection. For most complex polygenic diseases, they capture distributed polygenic signal more effectively than sparse approaches.
- Sparse selection / thresholding methods (clumping-and-thresholding, pruning-and-thresholding, L1-penalized sparse regression) retain only variants passing a significance or penalization threshold. For highly polygenic traits, this loses substantial predictive signal.
- This distinction is a structural signal, not an absolute rule. The performance gap varies by disease and by the quality of the underlying GWAS.

Method-study-design interaction:

- A genome-wide shrinkage method from a disease-focused multi-cohort GWAS meta-analysis is a positive signal over a sparse method from a pan-trait single-biobank framework.
- L1-penalized regression models from pan-trait single-biobank frameworks typically yield very sparse scores that generalize poorly to independent cohorts.
- Clumping-and-thresholding and pruning-and-thresholding pipelines have limited polygenic signal capture. When such a method reports very high R² (e.g., R² > 0.15 for a complex polygenic trait) with unknown covariates, that R² is likely inflated or non-comparable.
- Methods using only genome-wide significant variants (small SNP sets) can be effective when the variants were identified in large, well-powered disease-focused GWAS, especially for diseases with strong individual-locus effects.
- The full methodological pipeline matters, not just the base variant-selection step. A method that combines thresholding with additional shrinkage, empirical Bayes estimation, or cross-ancestry transfer learning steps is methodologically stronger than simple thresholding alone.
- Variant spellings, capitalizations, or abbreviations of the same underlying method are equivalent. The method's actual statistical procedure determines its classification, not surface-level string differences.

Common misconceptions:

- sparser methods are not worse in ALL cases — for diseases with strong individual-locus effects, small-variant-set methods can perform well
- newer methods are not inherently more portable
- more complex methods are not inherently more clinically credible

When candidates are otherwise similar:

- Method distinctions are most informative when comparing across study families. Within the same study family, empirical evidence (effect sizes, AUC, study design) is more informative than method label.
- Among candidates with similar methodological approaches, method alone does not reliably drive selection — other fields (variants, performance, study design) are more informative.
- An L1-penalized sparse model from a pan-trait framework paper does not reliably outperform a genome-wide shrinkage model from a disease-focused study, even if the sparse model has a slightly higher reported metric.

