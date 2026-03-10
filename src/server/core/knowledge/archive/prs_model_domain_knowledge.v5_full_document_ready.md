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

- `phenotyping_reported` is the primary endpoint-fidelity field.
- `trait_reported` and `trait_efo` are concept-alignment fields, not final deployment proof.
- Endpoint fidelity matters more than surface label similarity.

Prefer:

- direct clinical disease endpoint
- generic disease endpoint for generic disease-risk deployment
- general case-control or incident-plus-prevalent disease endpoint when the target is a generic disease concept
- near-synonymous disease labels with richer supporting evidence over exact but vague or unspecified labels

Down-rank when:

- `phenotyping_reported` is time-to-event
- `phenotyping_reported` is incident-only while the target is generic disease risk
- `phenotyping_reported` is horizon-specific, such as 5-year risk
- `phenotyping_reported` is subtype-only
- `phenotyping_reported` is a proxy phenotype
- `phenotyping_reported` is treatment-induced or therapy-specific
- `phenotyping_reported` is a broad administrative phenotype bundle
- the label is broad or vague while a competing candidate is a clinically dominant subtype with much stronger support

Tie-break guidance:

- Incident-only, time-to-event, and self-reported exact disease endpoints are all acceptable but none is an automatic winner.
- Do not over-penalize minor wording differences when the disease concept is clearly the same.
- Do not automatically prefer an exact but vague label over a near-synonymous candidate with much richer evidence.
- Do not automatically prefer a broad umbrella label over a clinically dominant subtype with much stronger endpoint and study support.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

Core rule:

- `performance_metrics.auc` and `performance_metrics.r2` are useful only after endpoint and covariate comparability are acceptable.
- Higher reported AUC or R2 is supportive evidence, not decisive evidence.

Prefer:

- reported performance from candidates with comparable endpoints
- discrimination reported with basic or otherwise comparable covariates
- stable performance evidence that does not depend on obvious endpoint shortcuts

Down-rank when:

- very high AUC or R2 appears on a weaker endpoint
- very high AUC or R2 appears on a narrower endpoint
- very high AUC or R2 appears in a time-to-event, broad EHR, or internally optimized single-biobank setting
- reported performance is not comparable across studies
- performance depends on heavy clinical covariates
- the only candidate with reported AUC in a study family wins solely because competing models have null metrics

Covariate rule:

- Treat `covariates` as a comparability and optimism field.
- Heavy clinical covariates can make reported discrimination look better than the PRS alone.
- Unknown covariates should lower confidence, not automatically help or hurt the candidate.

Tie-break guidance:

- Use AUC and R2 to separate candidates only when endpoint fidelity is already acceptable.
- Small metric gaps should not dominate if endpoint or covariate design differs.
- Missing metrics should lower confidence, but they do not automatically lose to inflated or non-comparable AUC.

## 3. validation_sample_size

Core rule:

- `validation_sample_size` is a strong tie-break field, not a primary ranking field.

Prefer:

- larger validation cohorts when endpoint fidelity is similar
- larger validation support when reported performance is otherwise close
- much stronger validation support when a cleaner endpoint competes against only a tiny metric gap

Down-rank when:

- a candidate has a very small validation sample
- a large validation sample is being used to justify a weaker phenotype match
- a very large validation sample is being used to rescue non-comparable AUC

Tie-break guidance:

- Large validation size increases trust only after phenotype alignment is acceptable.
- A small AUC advantage from a tiny validation cohort should not automatically beat a near-tie candidate validated in a much larger cohort.
- Huge validation support alone should not beat a cleaner endpoint or a cleaner covariate design.

## 4. training_development_cohorts / samples_training

Core rule:

- `training_development_cohorts` is mainly a transportability field.
- `samples_training` is mainly a scale field.
- Study archetype matters more than raw training size.

Prefer:

- disease-focused development
- consortium-style development
- multi-cohort development that looks externally oriented rather than internally optimized
- disease-specific development over broad high-throughput frameworks when endpoint evidence is otherwise similar

Down-rank when:

- the candidate is mainly supported by a single-biobank pan-trait workflow
- the candidate comes from a portability or pan-phenome sweep with limited disease-specific evidence
- a very large training sample is the main reason the model looks attractive

Tie-break guidance:

- Use `training_development_cohorts` to judge whether the model is disease-focused or generic.
- Use `samples_training` only as supporting evidence.
- Large training size cannot compensate for weaker endpoint fidelity.
- Within the same publication family, modest cohort-list or training-size differences are weak tie-breaks.

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
- If candidates are otherwise closely matched within the same study family, LD-aware shrinkage methods such as `PRS-CS`, `LDpred`, or `LDpred2` may be mildly preferred over very sparse P+T or GWAS-hit constructions.
- If a candidate wins mainly because the method name looks stronger, lower confidence.
- `snpnet` or other high-capacity penalized regression methods need extra caution when their advantage comes mainly from single-biobank optimization or unusually high internal AUC.

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
- portability, pan-phenome, global-biobank, or high-throughput framing when disease-specific evidence is weaker

Tie-break guidance:

- Use publication context to understand what kind of model is being surfaced.
- Titles that emphasize portability, pan-phenome breadth, many traits, or broad biobank screening often indicate framework papers rather than automatic deployment winners.
- Do not let recency or journal prestige override phenotype fidelity, comparable performance, or transportability.

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
