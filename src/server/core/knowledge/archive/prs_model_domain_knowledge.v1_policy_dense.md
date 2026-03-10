# PRS Model Domain Knowledge

This knowledge base provides field-level policy for direct-match PRS model selection.
Use it to interpret visible PGS Catalog metadata during Step 1 ranking.

## Overall Ranking Principle

Apply the fields in this order:

1. Endpoint fidelity and disease-definition fidelity
2. Comparable reported performance
3. Validation support
4. Transportability context from cohorts and ancestry
5. Weak tie-breaks from method, publication context, and model shape

General rules:

- Prefer down-ranking over hard rejection unless the mismatch is explicit.
- Lower confidence when evidence is missing, heterogeneous, or not directly comparable.
- Do not let a single attractive metadata feature dominate the decision.

## 1. trait_reported / trait_efo / phenotyping_reported

These fields define how well a candidate actually matches the target disease.

Policy:

- Treat `trait_reported` and `trait_efo` as label-level alignment fields.
- Treat `phenotyping_reported` as the most important field for deployment-facing endpoint fidelity.
- If `trait_reported` and `trait_efo` look aligned but `phenotyping_reported` is narrower, shifted, or specialized, down-rank the candidate.
- Prefer a generic disease endpoint over:
  - time-to-event endpoints
  - horizon-specific endpoints such as 5-year incident risk
  - incident-only endpoints when the target is the generic disease
  - subtype-only endpoints
  - proxy phenotypes
  - treatment-induced or therapy-specific phenotypes
  - broad administrative phenotype bundles
- Do not overreact to superficial wording differences when the disease concept is the same.
- Do not let a cleaner-looking label override a more faithful phenotype definition.

Interpretation guidance:

- `phenotyping_reported` should break ties and also overrule superficial string matching when needed.
- `trait_efo` is useful for concept normalization, but it is not enough on its own to prove endpoint equivalence.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

These fields describe reported validation performance, but they are only meaningful when comparison is fair.

Policy:

- Use `performance_metrics.auc` and `performance_metrics.r2` only after phenotype fidelity is acceptable.
- A higher reported AUC or R2 is supportive evidence, not decisive evidence.
- Do not let a very high AUC or R2 override a weaker endpoint match.
- Treat small performance gaps as weak evidence when studies differ in phenotype definition, cohort design, or covariate adjustment.
- Missing AUC or R2 should lower confidence, but should not automatically eliminate a clinically better-matched candidate.

Covariate policy:

- Treat `covariates` mainly as a comparability and optimism signal, not as a ranking reward.
- If a model reports strong discrimination with heavy clinical covariates, consider that metric potentially optimistic for pure PRS selection.
- If covariates are minimal or unknown, avoid assuming either superiority or inferiority; just lower confidence when direct comparison is unclear.

Interpretation guidance:

- Prefer performance metrics that are believable in context over metrics that are simply larger.
- When high discrimination appears together with endpoint narrowing or heavy covariate adjustment, down-weight the metric.

## 3. validation_sample_size

This field measures how much direct validation support a candidate has.

Policy:

- Use `validation_sample_size` as a strong tie-break only after endpoint fidelity is acceptable.
- Larger validation cohorts increase trust when the compared candidates are evaluated on similarly faithful endpoints.
- Do not let a large validation sample rescue a weakly matched phenotype.
- A tiny performance advantage from a small validation cohort should not automatically beat a near-tie candidate validated in a much larger cohort.
- If the leading candidate has a very small validation set, reduce confidence even if other fields look favorable.

Interpretation guidance:

- `validation_sample_size` should usually influence confidence before it determines rank.
- The main question is whether the reported performance looks stable and externally believable, not whether the sample size is simply maximal.

## 4. training_development_cohorts / samples_training

These fields describe where the score came from and how likely it is to transfer beyond its original setting.

Policy:

- Use `training_development_cohorts` to infer study archetype and transportability.
- Favor disease-focused or consortium-style development over generic single-biobank sweeps when other evidence is close.
- Do not automatically prefer a candidate just because it was trained in a very large biobank.
- Treat `samples_training` as supportive scale evidence, not as a primary ranking field.
- A large training sample cannot compensate for weaker endpoint fidelity.
- Multiple development cohorts can increase confidence when they reflect broader and more realistic disease evidence, but only if phenotype fidelity remains acceptable.

Interpretation guidance:

- Single-biobank origin, especially from a broad pan-trait modeling framework, should trigger caution rather than automatic preference.
- Cross-cancer, pan-phenome, or multitrait development contexts may be useful, but they are not automatically better than disease-specific development.

## 5. method_name

This field describes how the PRS was built, but method modernity is weak evidence.

Policy:

- Treat `method_name` as a weak tie-break only.
- Do not automatically prefer `snpnet`, `PRS-CS`, `LDpred2`, `lassosum`, or any other method solely because it looks newer, denser, or more complex.
- Do not assume sparse models are inferior.
- Do not assume dense or high-capacity models are more portable.
- Use method differences only after phenotype fidelity, reported performance comparability, validation support, and cohort context have already been considered.

Interpretation guidance:

- Method name helps interpret model style, not model quality.
- If a model wins mainly because the method name looks stronger, confidence should be reduced.

## 6. ancestry_distribution

This field should be used to judge compatibility and transportability boundaries, not to reward cosmetic diversity.

Policy:

- Use `ancestry_distribution` to assess whether the evidence context plausibly matches intended deployment.
- Do not automatically prefer a model because the ancestry string looks broader or more diverse.
- Evaluation ancestry is often more informative than broad GWAS ancestry labels.
- Explicit ancestry mismatch should lower confidence.
- If deployment ancestry is not specified, do not over-interpret this field.

Interpretation guidance:

- Multi-ancestry appearance is not automatically an advantage.
- A narrower but cleaner ancestry context can be more credible than a broader but less interpretable one.

## 7. publication.title / publication.journal / date_release

These fields help identify study type and context, but they are weak ranking signals.

Policy:

- Use `publication.title` primarily to identify the study archetype:
  - disease-specific study
  - cross-cancer study
  - multitrait or pan-phenome sweep
  - broad biobank portability paper
  - related-trait rather than exact-disease study
- Use `publication.journal` only as weak contextual evidence.
- Use `date_release` only as weak contextual evidence.
- Do not automatically prefer a newer release.
- Do not automatically prefer a more prominent journal.
- Do not let publication prestige or recency override endpoint fidelity, comparable performance, or transportability concerns.

Interpretation guidance:

- Publication context is useful for understanding what kind of model is being surfaced.
- It is not a substitute for disease-definition fidelity.

## 8. variants_number

This field describes model size, not model quality.

Policy:

- Treat `variants_number` as a model-shape descriptor only.
- Do not rank candidates directly by the number of variants.
- Do not assume that more variants means better performance or better portability.
- Do not assume that fewer variants means better interpretability or deployment value.
- Use this field only in combination with method and study context, and only as weak interpretive evidence.

Interpretation guidance:

- `variants_number` varies widely across good and bad candidates.
- Large differences in SNP count should not drive selection on their own.
