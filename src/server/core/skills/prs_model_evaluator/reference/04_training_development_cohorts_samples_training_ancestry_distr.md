## 4. training_development_cohorts / samples_training / ancestry_distribution

Key empirical finding:

- `training_development_cohorts` is mainly a transportability field. The number of training cohorts has only a **marginal** effect on real-world performance. Study archetype (disease-focused vs framework) matters far more than cohort count.
- `samples_training` has **negligible predictive value** for real-world PRS performance. Larger training samples do NOT predict better real-world performance. Training sample size is not a meaningful differentiator.
- Study archetype matters more than raw training size.

Positive signals (indicators of stronger real-world performance):

- disease-focused development
- consortium-style development
- multi-cohort development that looks externally oriented rather than internally optimized
- disease-specific development over broad high-throughput frameworks when endpoint evidence is otherwise similar
- disease-focused multi-cohort development over single-biobank portability sweeps when the latter mainly contributes generic labels rather than richer disease evidence
- broad multi-cohort disease studies when they look biologically and clinically targeted rather than trait-agnostic
- large disease-focused multi-cohort or global studies when exact-disease endpoint fidelity remains acceptable and the competing alternative is mainly a single-ancestry metric winner
- repeated support from multiple candidates in the same disease-focused study family when they share endpoint, ancestry, and validation context

Pan-trait framework identification and evidence:

- **Framework models underperform disease-focused models systematically.** Pan-trait and portability-framework models generalize less well to independent external cohorts than disease-focused models. Selecting a framework score over a disease-focused alternative is a frequent and costly error pattern.
- Identify candidates coming from pan-trait, pan-phenome, or portability-style high-throughput frameworks. Key signature phrases in publication titles include:
  - "Significant sparse polygenic risk scores across 813 traits" (L1-penalized sparse pan-trait UKB framework)
  - "Portability of 245 polygenic scores" (UKB portability framework)
  - "ExPRSweb" or "online repository with polygenic risk scores for common health-related exposures" (ExPRSweb framework)
  - "Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts" (Global Biobank Meta-analysis framework)
  - Any title emphasizing "across N traits" or "across N phenomes" where N is large
- **When a disease-focused alternative exists with acceptable endpoint fidelity, the framework model is not the stronger choice.** The framework model is stronger only if it has clearly superior endpoint fidelity AND methodological properties AND metric evidence — not just one of these.
- **Framework penalty is proportional to method quality.** Framework models using methodologically strong approaches (multi-score aggregation, genome-wide Bayesian mixture/shrinkage, cross-ancestry extensions) receive a lighter framework penalty than framework models using sparse or thresholding methods.
- When the only visible metric advantage of a framework model is a modest PRS-comparable metric (e.g., partial-r < 0.05, PGS AUROC < 0.60) while a disease-focused model has stronger effect sizes, larger disease-specific training, or richer multi-cohort validation, the disease-focused model is the stronger choice.
- L1-penalized sparse models from the pan-trait UKB framework (the "813 traits" paper) have a characteristic signature: typically low variant counts (single-digit to low-thousands), L1-penalized sparse method, UKB as sole training/dev cohort, and standardized covariates (age, sex, UKB array type, Genotype PCs). These models generalize poorly to independent external cohorts despite having complete and well-formatted PGS Catalog metadata.

Warning signals (indicators of weaker real-world performance):

- the candidate is mainly supported by a single-biobank pan-trait workflow
- the candidate comes from a portability or pan-phenome sweep with limited disease-specific evidence
- a very large training sample is the main reason the model looks attractive
- the candidate is essentially a framework score surfaced by many cohorts but not clearly optimized for the target disease endpoint

When candidates are otherwise similar:

- `training_development_cohorts` is informative for judging whether the model is disease-focused or generic.
- `samples_training` is only supporting evidence — it has negligible predictive value and does not reliably drive a decision.
- Large training size does not compensate for weaker endpoint fidelity.
- Within the same publication family, modest cohort-list or training-size differences are weak signals.
- Single-biobank portability papers do not reliably outperform disease-focused multi-cohort studies unless they also have clearly cleaner endpoint evidence and comparable metrics.
- A coherent disease-focused multi-cohort study family with exact or near-exact endpoints can still outperform a lone portability or legacy exact-label score even when the family has unknown covariates, if the competitor's main edge comes from explicit clinical augmentation or risk-wrapper packaging.
- When several candidates from the same study family are all endpoint-faithful and share the same validation/evaluation context, that repeated family pattern is corroborating evidence rather than redundancy.
- A disease-focused multi-cohort study with many contributing biobanks (e.g., >5 cohorts including AllofUs, BioMe, FinnGen, UKB, MVP, etc.) is strong evidence of external validation and is the stronger choice over single-biobank framework scores.

### Ancestry context

- `ancestry_distribution` is a compatibility and transportability field.
- Multi-ancestry appearance is not automatically an advantage.
- Models evaluated only in non-EUR ancestry contexts tend to perform materially worse in diverse external cohorts. Multi-ancestry and EUR evaluation perform similarly, while non-EUR-only evaluation is a weakness. For GWAS ancestry, multi-ancestry and EUR-only GWAS perform similarly; non-EUR-only GWAS is a weaker signal.
- Evaluation ancestry is often more informative than broad GWAS ancestry labels.
- A candidate is not stronger simply because the ancestry string looks more diverse.
- Multi-ancestry evaluation from a disease-focused multi-cohort study (e.g., AllofUs, MVP, diverse biobanks) is supportive evidence of model robustness.
- When deployment ancestry is unspecified, ancestry is less informative and lowers confidence rather than supporting over-ranking.

