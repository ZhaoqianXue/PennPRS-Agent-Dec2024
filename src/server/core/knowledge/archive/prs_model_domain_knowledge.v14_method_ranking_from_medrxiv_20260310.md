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
- combined or generic disease endpoints over fixed-horizon future-risk endpoints when the target itself is a generic disease concept
- diagnostic-code or phecode-based disease endpoints when they directly map to the same disease concept
- disease-adjacent trait labels when `phenotyping_reported` is still a direct diagnosis endpoint for the target disease and the study context remains disease-focused
- near-synonymous disease labels with richer supporting evidence over exact but vague or unspecified labels
- exact disease endpoints with much stronger validation and materially better discrimination, even when they are self-reported
- clinically dominant subtypes when the target label is a broad organ-site cancer or umbrella carcinoma term and the subtype has much stronger support

Down-rank when:

- `phenotyping_reported` is time-to-event
- `phenotyping_reported` is incident-only while the target is generic disease risk
- `phenotyping_reported` is horizon-specific, such as 5-year risk
- `phenotyping_reported` is future-risk prediction rather than generic disease status
- `phenotyping_reported` is subtype-only
- `phenotyping_reported` is a proxy phenotype
- `phenotyping_reported` is treatment-induced or therapy-specific
- `phenotyping_reported` is a broad administrative phenotype bundle
- the label is broad or vague while a competing candidate is a clinically dominant subtype with much stronger support
- the endpoint is generic but unspecified and mainly surfaced by a portability or pan-trait framework rather than a disease-focused study
- the score is an exact broad-label match from a portability or framework paper while several near-synonymous subtype or diagnosis-anchored candidates have richer support

Tie-break guidance:

- Incident-only, time-to-event, and self-reported exact disease endpoints are all acceptable but none is an automatic winner.
- Self-reported exact disease should not automatically lose to a clinically ascertained alternative if it has much stronger validation support and materially better reported discrimination.
- If discrimination is nearly identical, self-reported exact disease with orders-of-magnitude larger validation support can beat a clinically phrased alternative.
- Diagnostic-code and phecode instantiations of the same disease should not automatically lose to literal disease-string endpoints.
- A broader `trait_reported` label should not automatically lose when `phenotyping_reported` is a direct diagnosis endpoint for the target disease.
- Do not over-penalize minor wording differences when the disease concept is clearly the same.
- Do not automatically prefer an exact but vague label over a near-synonymous candidate with much richer evidence.
- Do not automatically prefer an exact but unspecified umbrella label from a portability-style or sparse-metadata study over a near-synonymous clinically specific disease label with much stronger validation and reported discrimination.
- Do not automatically prefer a broad umbrella label over a clinically dominant subtype with much stronger endpoint and study support.
- Fixed-horizon future-risk or prediction-oriented endpoints should not outrank a generic disease endpoint for generic deployment unless the generic disease candidates are otherwise much weaker.
- When the target is a broad organ-site cancer concept, dominant subtypes such as the most common site-specific carcinoma can be preferred if they are the only candidates with clearly stronger endpoint and study evidence, especially when the broad-label alternative mainly comes from a portability-style framework.
- If several near-synonymous subtype or diagnosis-anchored candidates form a coherent high-support cluster, that cluster should be treated as stronger evidence than a lone exact-label framework score.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

Core rule:

- `performance_metrics.auc` and `performance_metrics.r2` are useful only after endpoint and covariate comparability are acceptable.
- Higher reported AUC or R2 is supportive evidence, not decisive evidence.

Prefer:

- reported performance from candidates with comparable endpoints
- discrimination reported with basic or otherwise comparable covariates
- stable performance evidence that does not depend on obvious endpoint shortcuts
- performance packages that do not rely on downstream clinical disease variables, family history, or treatment context
- performance packages that do not rely on near-outcome quantitative traits or baseline measurements tightly coupled to the target disease

Down-rank when:

- very high AUC or R2 appears on a weaker endpoint
- very high AUC or R2 appears on a narrower endpoint
- very high AUC or R2 appears in a time-to-event, broad EHR, or internally optimized single-biobank setting
- the AUC is a clear outlier relative to the rest of the direct-match set and comes from a high-throughput single-biobank framework
- reported performance is not comparable across studies
- performance depends on heavy clinical covariates
- performance depends on disease-adjacent clinical variables such as family history or established downstream clinical predictors
- performance depends on treatment assignment, treatment interaction, or other intervention-context variables
- performance depends on near-outcome baseline measurements such as body-size, organ-function, or disease-severity variables that are tightly coupled to the target phenotype
- the only candidate with reported AUC in a study family wins solely because competing models have null metrics
- the only visible AUC comes from the more covariate-heavy or more internally optimized candidate within the same endpoint family
- the reported metric appears to come from a combined clinical-risk package rather than something close to PRS-plus-basic covariates

Covariate rule:

- Treat `covariates` as a comparability and optimism field.
- Heavy clinical covariates can make reported discrimination look better than the PRS alone.
- Family history or disease-related clinical predictors can also make the reported metric less comparable to a PRS-only or PRS-light setting.
- Treatment variables, intervention terms, and near-outcome baseline measurements can make the metric reflect prognostic enrichment rather than PRS quality.
- Unknown covariates should lower confidence, not automatically help or hurt the candidate.

Tie-break guidance:

- Use AUC and R2 to separate candidates only when endpoint fidelity is already acceptable.
- Small metric gaps should not dominate if endpoint or covariate design differs.
- Material performance and validation advantages can outweigh a more disease-focused narrative when endpoints remain acceptably aligned and covariates are cleaner or more comparable.
- Missing metrics should lower confidence, but they do not automatically lose to inflated or non-comparable AUC.
- If two candidates share the same endpoint family and one reports high AUC only with much heavier covariates, do not let that AUC dominate over a cleaner but partially missing comparator.
- If a candidate’s apparent advantage depends on family history, treatment variables, or target-adjacent baseline measurements, treat that advantage as weak unless the comparator evidence is otherwise clearly inferior.
- If two candidates share the same exact disease endpoint family and one candidate’s only visible edge is a covariate-heavy AUC built on extensive comorbidity or near-outcome adjustment, do not let that metric automatically outrank a cleaner comparator that lacks AUC but has otherwise comparable support.
- If one model’s main advantage is an outlier AUC from a high-throughput single-biobank framework, treat that metric as weak when several cleaner direct-match competitors cluster together in endpoint and study design.

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
- Order-of-magnitude validation differences are meaningful only after checking endpoint fidelity, covariate comparability, and study archetype together.
- When reported discrimination is nearly tied, very large validation support can break the tie even if one candidate uses a self-reported version of the same disease endpoint.

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
- disease-focused multi-cohort development over single-biobank portability sweeps when the latter mainly contributes generic labels rather than richer disease evidence
- broad multi-cohort disease studies when they look biologically and clinically targeted rather than trait-agnostic
- large disease-focused multi-cohort or global studies when exact-disease endpoint fidelity remains acceptable and the competing alternative is mainly a single-ancestry metric winner
- repeated support from multiple candidates in the same disease-focused study family when they share endpoint, ancestry, and validation context

Down-rank when:

- the candidate is mainly supported by a single-biobank pan-trait workflow
- the candidate comes from a portability or pan-phenome sweep with limited disease-specific evidence
- a very large training sample is the main reason the model looks attractive
- the candidate is essentially a framework score surfaced by many cohorts but not clearly optimized for the target disease endpoint

Tie-break guidance:

- Use `training_development_cohorts` to judge whether the model is disease-focused or generic.
- Use `samples_training` only as supporting evidence.
- Large training size cannot compensate for weaker endpoint fidelity.
- Within the same publication family, modest cohort-list or training-size differences are weak tie-breaks.
- Single-biobank portability papers should not beat disease-focused multi-cohort studies unless they also have clearly cleaner endpoint evidence and comparable metrics.
- When two candidates are both endpoint-faithful, do not automatically let a single-ancestry large-metric model beat a disease-focused multi-cohort or global study unless the former also has cleaner covariates and no stronger portability concerns.
- If several candidates from the same study family are all endpoint-faithful and share the same validation/evaluation context, treat that repeated family pattern as corroborating evidence rather than redundancy.

## 5. method_name

Core rule:

- `method_name` is a weak tie-break field.
- Method modernity is not a quality proxy.
- Use literature-derived method rankings only as a weak prior after phenotype alignment, comparable performance, validation support, and transportability have already been checked.

Literature-derived ranking reference:

- A March 2026 medRxiv spectral-ranking benchmark of 14 GWAS-summary-statistics single-ancestry PRS methods found `LDpred2` and `AnnoPred` to be the most consistently top-ranked methods overall.
- The same benchmark found `C+T`, `LDpred`, and `LDpred2-inf` to be the most consistently low-ranked methods overall.
- `SCT` and `lassosum2` performed strongly in the larger applied/benchmarking-paper ranking, but were less uniformly dominant across all ranking views.
- `DBSLMM` showed notable rank instability across ranking sources and should not be treated as a stable top-tier method prior.
- `PRS-CS` and `PRS-CS-auto` were not consistently top-tier in this benchmark and should not be preferred solely because they are common or modern.
- The paper also emphasized that most middle-ranked methods had overlapping confidence intervals and that there is no universally best method across phenotypes.
- This benchmark is most relevant to standard GWAS-summary-statistics single-ancestry PRS methods. It should not be overextended to methods outside that scope, such as individual-level-data penalized regression frameworks.

Weak method prior for otherwise closely matched candidates:

- top prior: `LDpred2`, `AnnoPred`
- upper-middle prior: `LDpred2-auto`, `LDpred-funct`, `lassosum2`, `SCT`
- source-sensitive middle prior: `SBayesR`, `lassosum`, `DBSLMM`, `PRS-CS`, `PRS-CS-auto`
- low prior: `LDpred2-inf`, `LDpred`, `C+T`

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
- rare-pathogenic or monogenic-leaning constructions are better for generic common-disease PRS deployment

Tie-break guidance:

- Use `method_name` only after endpoint fidelity, comparable performance, validation support, and transportability have already been considered.
- If two candidates are otherwise closely matched and both fall within the paper’s benchmark scope, the literature-derived prior above can be used as a mild tie-break.
- If a candidate wins mainly because it is `PRS-CS` or `PRS-CS-auto`, lower confidence unless non-method fields clearly support it.
- If a candidate wins mainly because it is `LDpred2` or `AnnoPred`, keep that advantage mild; do not let it override materially cleaner endpoint or study-design evidence from another method.
- If a candidate’s only method advantage is being `C+T`, `LDpred`, or `LDpred2-inf`, treat that as a negative rather than a positive tie-break unless the non-method metadata are clearly stronger.
- If a candidate’s only method advantage is being `SCT`, `lassosum2`, or `DBSLMM`, remember that the literature benchmark showed source-sensitive ordering; use extra caution instead of treating them as uniformly top-tier.
- If candidates are otherwise closely matched within the same study family, LD-aware shrinkage methods such as `PRS-CS`, `LDpred`, or `LDpred2` may be mildly preferred over very sparse P+T or GWAS-hit constructions.
- If candidates are otherwise closely matched within the same endpoint family, do not let a very sparse P+T score beat a genome-wide shrinkage score solely because of a modest AUC edge.
- If candidates share the same publication family, phenotype, validation cohort, and ancestry context, a modest AUC edge from an ultra-sparse construction is weak evidence against a genome-wide shrinkage score.
- If candidates share the same publication family, endpoint, validation size, ancestry context, and similarly missing covariates, prefer the genome-wide shrinkage score unless the sparse construction has a clearly larger, not merely modest, metric advantage.
- If a candidate wins mainly because the method name looks stronger, lower confidence.
- `snpnet` or other high-capacity penalized regression methods need extra caution when their advantage comes mainly from single-biobank optimization or unusually high internal AUC.
- Rare-pathogenic or clearly monogenic-leaning constructions should not automatically outrank genome-wide polygenic scores for generic common-disease risk unless the metadata show unusually strong and clean disease-level support.

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
- Do not let mixed-ancestry evaluation beat a much stronger exact-disease candidate by itself.
- A single non-EUR or mixed-ancestry evaluation is not automatically more deployable than a much larger exact-disease evaluation in one ancestry.

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
- risk-factor integration study
- related-trait rather than exact-disease study
- exposure-, lifestyle-, or treatment-centered study where the PRS may be an auxiliary predictor rather than the main disease-genetics object

Do not automatically prefer:

- a newer `date_release`
- a higher-profile `publication.journal`
- a broader or more ambitious-sounding `publication.title`
- portability, pan-phenome, global-biobank, or high-throughput framing when disease-specific evidence is weaker
- older disease-focused papers with cleaner endpoint fit over newer multi-cohort disease studies by default
- newer multi-cohort disease studies over older disease-focused studies by default

Tie-break guidance:

- Use publication context to understand what kind of model is being surfaced.
- Titles that emphasize portability, pan-phenome breadth, many traits, or broad biobank screening often indicate framework papers rather than automatic deployment winners.
- Titles that emphasize external evaluation in independent biobanks or a disease-focused multi-cohort study can be supportive when the candidate remains endpoint-faithful.
- Global multi-ancestry disease studies are supportive when they are clearly disease-focused; they should not be dismissed simply because they are newer or in preprint form.
- Titles centered on exposure effects, diet, treatment response, or non-genetic prognostic framing should be treated cautiously when the goal is generic disease-risk PRS selection.
- If an exposure-, lifestyle-, or treatment-centered paper surfaces a PRS only as an auxiliary predictor, do not let that title framing beat a disease-genetics candidate with similarly direct phenotype support.
- If a paper centers on integrating disease PRSs with risk-factor PRSs, treat it as a framework-style context rather than direct evidence that its disease score is the best standalone PRS.
- Cross-cancer or broad evaluation framing is not automatically disqualifying if the candidate remains a dominant subtype match with stronger endpoint and study support than a broad-label alternative.
- Disease-focused publication framing is supportive but weak; it should not override materially stronger validation/performance from a broader evaluation study when endpoint fidelity remains acceptable.
- Repeated candidates from the same disease-focused study family are supportive when they remain endpoint-faithful and internally consistent.
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
