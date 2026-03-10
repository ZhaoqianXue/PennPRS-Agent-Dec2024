# PRS Model Domain Knowledge

Purpose: provide retrieval-friendly field-level policy for direct-match PRS model selection.

Use this ranking order:

1. phenotype alignment and endpoint fidelity
2. comparable reported performance
3. validation support
4. transportability context
5. weak tie-breaks from method, publication context, and model shape

Global rules:

- Use only visible metadata.
- Down-rank rather than hard-reject unless the mismatch is explicit.
- Missing evidence should lower confidence.
- Do not let one attractive field dominate the decision.

## 1. trait_reported / trait_efo / phenotyping_reported

Core rule:

- `phenotyping_reported` is the main endpoint fidelity field.
- `trait_reported` and `trait_efo` are concept-alignment fields.
- Endpoint fidelity matters more than surface label similarity.

Prefer:

- generic disease endpoint
- direct clinical disease phenotype
- phenotype definition closest to intended deployment

Down-rank when:

- `phenotyping_reported` is time-to-event
- `phenotyping_reported` is incident-only while the target is generic disease risk
- `phenotyping_reported` is horizon-specific, such as 5-year risk
- `phenotyping_reported` is subtype-only
- `phenotyping_reported` is a proxy phenotype
- `phenotyping_reported` is treatment-induced or therapy-specific
- `phenotyping_reported` is a broad administrative phenotype bundle

Tie-break guidance:

- If `trait_reported` and `trait_efo` look aligned but `phenotyping_reported` is narrower or shifted, prefer the candidate with the cleaner endpoint.
- Incident-only and time-to-event endpoints are related-but-not-identical to generic disease deployment targets.
- Incident-only should not automatically beat incident+prevalent or general case-control disease endpoints.
- Self-reported exact disease endpoints are weaker than adjudicated clinical endpoints, but they are still acceptable direct matches when the disease concept is exact and the validation evidence is much stronger.
- Do not automatically prefer an exact but vague or unspecified label over a near-synonymous candidate with richer disease evidence.
- Do not automatically prefer a broad umbrella label over a clinically dominant subtype when the subtype candidate has much stronger supporting evidence.
- Do not over-penalize minor wording differences when the disease concept is clearly the same.
- Do not reward a cleaner-looking disease label if the validation phenotype is less faithful.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

Core rule:

- `performance_metrics.auc` and `performance_metrics.r2` are useful only after phenotype comparability is acceptable.
- Higher reported AUC or R2 is supportive evidence, not decisive evidence.

Prefer:

- reported performance from candidates with comparable endpoints
- stable performance evidence that does not depend on obvious phenotype shortcuts

Down-rank when:

- very high AUC or R2 appears on a weaker endpoint
- very high AUC or R2 appears on a narrower endpoint
- reported performance is not comparable across studies
- performance depends on heavy clinical covariates

Covariate rule:

- Treat `covariates` as a comparability and optimism field.
- Heavy clinical covariates can make reported discrimination look better than the PRS alone.
- Unknown covariates should lower confidence, not automatically help or hurt the candidate.

Tie-break guidance:

- Use AUC and R2 to separate candidates only when endpoint fidelity is already acceptable.
- Small metric gaps should not dominate if endpoint or study design differs.
- Treat unusually high AUC with caution when it comes from time-to-event, broad EHR-derived, or heavily optimized internal-biobank settings.
- If discrimination depends on many downstream clinical covariates, do not compare that AUC head-to-head against candidates adjusted only with basic demographics or ancestry PCs.
- If two candidates come from the same study family and share the same endpoint and validation context, the one candidate with the only reported AUC should not automatically win.

## 3. validation_sample_size

Core rule:

- `validation_sample_size` is a strong tie-break field, not a primary ranking field.

Prefer:

- larger validation cohorts when endpoint fidelity is similar
- larger validation support when reported performance is otherwise close

Down-rank when:

- a candidate has a very small validation sample
- a large validation sample is being used to justify a weaker phenotype match

Tie-break guidance:

- Large validation size increases trust only after phenotype alignment is acceptable.
- A small AUC advantage from a tiny validation cohort should not automatically beat a near-tie candidate validated in a much larger cohort.
- Use `validation_sample_size` to raise or lower confidence before using it to dominate rank.
- When AUC values are nearly tied or not directly comparable, favor the candidate with clearly stronger validation support.
- Approximate near-ties should be treated as tie-break situations, not as decisive metric wins.

## 4. training_development_cohorts / samples_training

Core rule:

- `training_development_cohorts` is mainly a transportability field.
- `samples_training` is mainly a scale field.
- Study archetype matters more than raw training size.

Prefer:

- disease-focused development
- consortium-style development
- development context that looks externally oriented rather than internally optimized

Down-rank when:

- the candidate is mainly supported by a single-biobank pan-trait workflow
- the candidate comes from a generic high-throughput sweep with limited disease-specific evidence
- a very large training sample is the main reason the model looks attractive

Tie-break guidance:

- Use `training_development_cohorts` to judge whether the model is disease-specific or generic.
- Use `samples_training` only as supporting evidence.
- Large training size cannot compensate for weaker endpoint fidelity.
- Portability papers, pan-phenome sweeps, and broad single-biobank modeling frameworks are useful context but are not automatic deployment winners.
- If a broad high-throughput model competes with a more disease-focused model, prefer the disease-focused candidate unless the broad model has clearly cleaner and stronger evidence.
- When candidates come from the same publication family, small cohort-list differences are weak tie-breaks.

## 5. method_name

Core rule:

- `method_name` is a weak tie-break field.
- Method modernity is not a quality proxy.

Do not automatically prefer:

- `snpnet`
- `PRS-CS`
- `PRS-CS-auto`
- `LDpred2`
- `LDpred2-auto`
- `lassosum`
- `lassosum2`

Do not automatically assume:

- denser methods are better
- sparser methods are worse
- newer methods are more portable
- more complex methods are more clinically credible

Tie-break guidance:

- Use `method_name` only after endpoint fidelity, comparable performance, validation support, and transportability have already been considered.
- If a candidate wins mainly because the method name looks stronger, lower confidence.
- Mild method priors are allowed only in near-tie situations.
- If candidates are otherwise closely matched, LD-aware shrinkage methods such as `PRS-CS`, `PRS-CS-auto`, `LDpred`, and `LDpred2` can beat very sparse P+T or GWAS-hit constructions.
- `snpnet` and other high-capacity penalized-regression methods need extra caution when their advantage comes mainly from single-biobank optimization or unusually high internal AUC.
- Simpler methods can still win when endpoint fidelity and validation evidence are cleaner.

## 6. ancestry_distribution

Core rule:

- `ancestry_distribution` is a compatibility and transportability field.
- Multi-ancestry appearance is not automatically an advantage.

Prefer:

- ancestry context that is interpretable for the intended deployment
- evaluation ancestry that is easier to trust for the target use case

Down-rank when:

- the evaluation ancestry is clearly mismatched
- the ancestry label looks broad but the deployment relevance is unclear

Tie-break guidance:

- Evaluation ancestry is often more informative than broad GWAS ancestry labels.
- Do not reward a candidate simply because the ancestry string looks more diverse.
- If deployment ancestry is unspecified, use this field cautiously and lower confidence rather than over-rank.

## 7. publication.title / publication.journal / date_release

Core rule:

- These fields are weak context fields.
- Their main job is to identify study type, not to rank prestige.

Use `publication.title` to detect:

- disease-specific study
- cross-disease study
- cross-cancer study
- multitrait or pan-phenome study
- portability study
- related-trait rather than exact-disease study

Do not automatically prefer:

- a newer `date_release`
- a higher-profile `publication.journal`
- a broader or more ambitious-sounding `publication.title`

Tie-break guidance:

- Use publication context to understand what kind of model is being surfaced.
- Do not let recency or journal prestige override phenotype fidelity, comparable performance, or transportability.
- Cross-disease, cross-cancer, portability, and pan-phenome framing are not automatic penalties, but they should not outrank stronger disease-specific evidence by title alone.
- A prospective or disease-specific publication can be useful supportive evidence, but it should not automatically beat a direct disease model with clearly stronger validation and performance support.

## 8. variants_number

Core rule:

- `variants_number` is a model-shape field, not a quality field.

Do not automatically assume:

- more variants means better performance
- more variants means better portability
- fewer variants means better interpretability
- fewer variants means better deployment value

Tie-break guidance:

- Use `variants_number` only as weak interpretive context.
- Large SNP-count differences should not drive ranking on their own.
- `variants_number` should never be the primary reason to select a model.
