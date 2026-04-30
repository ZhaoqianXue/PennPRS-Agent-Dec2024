## 6. publication.title / publication.journal / date_release

Key empirical finding:

- These fields are weak context fields.
- Their main informative role is identifying study type, not ranking prestige.

**"Disease-focused" is defined by endpoint alignment, not publication title framing.** A model from a multi-trait comparative study or benchmarking paper is still "disease-focused" if its endpoint directly targets the query disease. Only classify a model as "non-disease-focused" when the study design does not specifically validate or optimize for the target disease endpoint. Publication title framing (e.g., "across N cancers" or "polygenic scores in five biobanks") is a weak proxy for disease focus — the actual endpoint, covariates, and training design are what matter.

`publication.title` is informative for detecting:

- disease-specific study
- cross-disease study
- cross-cancer study
- multitrait or pan-phenome study
- portability study
- risk-factor integration study
- related-trait rather than exact-disease study
- exposure-, lifestyle-, or treatment-centered study where the PRS may be an auxiliary predictor rather than the main disease-genetics object

Key framework paper signatures and their implications:

- "Significant sparse polygenic risk scores across 813 traits in UK Biobank" = L1-penalized sparse pan-trait UKB framework (frequently produces scores that do not generalize well to independent cohorts)
- "Portability of 245 polygenic scores when derived from the UK Biobank" = UKB portability framework
- "ExPRSweb: An online repository with polygenic risk scores for common health-related exposures" = ExPRSweb exposure-PRS framework
- "Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts" = Global Biobank meta-analysis framework (Bayesian continuous shrinkage with auto-tuning)
- These framework papers are valuable for method benchmarking but their per-disease scores are not optimized for any specific disease and do not reliably outperform disease-focused alternatives. Selecting framework models over available disease-focused alternatives is the single most common error pattern in PRS model selection.
- By contrast, disease-specific comparative papers such as "Evaluation of polygenic scoring methods in five biobanks..." that compare several model families within one exact disease endpoint are not pan-trait framework scores when the candidate remains a direct match and the covariate field is empty or basic.
- Cross-cancer external evaluation is not equivalent to a pan-trait framework when the candidate's endpoint is the exact target cancer and validation is large.

Factors that do not reliably predict performance:

- a newer `date_release`
- a higher-profile `publication.journal`
- a broader or more ambitious-sounding `publication.title`
- portability, pan-phenome, global-biobank, or high-throughput framing when disease-specific evidence is weaker

When candidates are otherwise similar:

- Publication context is informative for understanding what kind of model is being surfaced.
- Titles that emphasize portability, pan-phenome breadth, many traits, or broad biobank screening often indicate framework papers rather than automatic deployment winners.
- Titles that emphasize external evaluation in independent biobanks or a disease-focused multi-cohort study can be supportive when the candidate remains endpoint-faithful.
- Global multi-ancestry disease studies are supportive when they are clearly disease-focused; they are not weaker simply because they are newer or in preprint form.
- Titles centered on exposure effects, diet, treatment response, or non-genetic prognostic framing are weaker evidence when the goal is generic disease-risk PRS selection.
- Repeated candidates from the same disease-focused study family are supportive when they remain endpoint-faithful and internally consistent.
- Recency or journal prestige does not override phenotype fidelity, comparable performance, or transportability.
- A disease-focused GWAS meta-analysis (e.g., from a named disease consortium) is generally the stronger choice over a generic pan-trait framework paper from UKB, even if the meta-analysis is older or in preprint form.

