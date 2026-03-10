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
- A model from a disease-focused multi-cohort study should not lose to a pan-trait framework score unless the framework score has clearly stronger endpoint AND metric evidence.

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

Clinically dominant subtype equivalences:

- When the target disease is a broad umbrella or organ-site term, the clinically dominant manifestation must be treated as semantically equivalent, not as a subtype mismatch. Specific known equivalences include:
  - `obstructive sleep apnea` is the dominant clinical form of `sleep apnea` (~85% of clinical cases); an OSA-labeled model should be preferred over a generic sleep-apnea-labeled model when the OSA model has materially better study design, validation, or performance evidence.
  - `endometrial carcinoma` is the dominant histological subtype of `uterine carcinoma` (~90% of cases); an endometrial-cancer-labeled model should be treated as a strong match for a uterine-carcinoma target, especially when it has better endpoint and performance support than the exact-label alternative.
  - `renal cell carcinoma` is the dominant subtype of `kidney cancer` (~90% of cases).
  - `adenocarcinoma` is the dominant subtype for many organ-site cancer targets.
- When a clinically dominant subtype candidate has materially stronger study design, validation, or performance evidence than the exact-label alternative, the dominant subtype should be preferred.
- Do not penalize the dominant subtype mismatch when it is the overwhelming clinical majority of the umbrella disease.

Down-rank when:

- `phenotyping_reported` is time-to-event, unless the candidate is from a major disease-focused multi-cohort study and the competing alternative is merely a portability or pan-trait framework score
- `phenotyping_reported` is incident-only while the target is generic disease risk, unless the candidate is from a dedicated disease GWAS meta-analysis with much stronger study support than the competing generic-label alternative
- `phenotyping_reported` is horizon-specific, such as 5-year risk
- `phenotyping_reported` is future-risk prediction rather than generic disease status
- `phenotyping_reported` is subtype-only, unless it is the clinically dominant subtype of the target disease
- `phenotyping_reported` is a proxy phenotype
- `phenotyping_reported` is treatment-induced or therapy-specific, unless the genetic basis captured by the score is biologically relevant to the target disease and no better alternative exists
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
- An incident-only or time-to-event endpoint from a major disease-focused multi-cohort study should not automatically lose to a generic-label portability-framework score that only has a modest partial-correlation or similar weak metric. The disease-focused study context and stronger overall evidence package can outweigh the endpoint-type penalty.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

Core rule:

- `performance_metrics` should be interpreted from one representative validation record, not from mixed records.
- When multiple validation records exist, prefer the highest-result European validation record; if no European validation exists, use the highest-result record overall.
- Preserve and inspect the full `classification_metrics` and `other_metrics` from that selected record instead of reducing them to a single scalar.
- Treat top-level `performance_metrics.auc` and `performance_metrics.r2` as PRS-comparable metrics only.
- Prefer explicit `PGS AUROC (no covariates)`, `PGS R2 (no covariates)`, or covariates-regressed-out PRS metrics when available.
- Treat generic `classification_metrics` AUROC/C-index and generic `R²` as full-model metrics unless the metric name explicitly says they are PGS-only or covariates-regressed-out.
- Full-model AUROC can be useful for within-record sanity checking, but it is not the primary cross-model ranking metric for Contribution2 because Contribution1 benchmark AUCs were computed without covariate-boosted full-model discrimination.
- `performance_metrics.auc` and `performance_metrics.r2` are useful only after endpoint and covariate comparability are acceptable.
- Higher reported AUC or R2 is supportive evidence, not decisive evidence.
- Missing metrics should not automatically disqualify a candidate. A model from a disease-focused study with only effect sizes (OR, HR) but no explicit AUC or R2 can still be the best candidate if its study design, cohort context, and method are stronger than a framework score with explicit but modest PRS-comparable metrics.

Effect sizes as PRS-quality signals:

- When a candidate reports only `effect_sizes` (OR per SD, HR per SD, Beta) but no AUROC or R2, use the effect size magnitude as a supportive PRS-quality signal rather than treating the candidate as having no discrimination evidence.
- A strong per-SD OR (e.g., >1.4) or HR (e.g., >1.5) from a well-designed study is meaningful evidence of PRS discriminative power.
- Effect sizes should not override clearly stronger AUC/R2 evidence from a comparably designed study, but they should prevent automatic loss to a framework-generated score whose only advantage is metric availability.
- When comparing a disease-focused study candidate with strong effect sizes against a portability-framework candidate with a weak partial-correlation or modest PRS-only AUC, the effect-size evidence combined with study design should weigh at least equally.

Prefer:

- reported performance from candidates with comparable endpoints
- explicit PRS-only or otherwise PRS-comparable discrimination metrics
- discrimination reported with basic or otherwise comparable covariates
- stable performance evidence that does not depend on obvious endpoint shortcuts
- performance packages that do not rely on downstream clinical disease variables, family history, or treatment context
- performance packages that do not rely on near-outcome quantitative traits or baseline measurements tightly coupled to the target disease

Down-rank when:

- very high AUC or R2 appears on a weaker endpoint
- very high AUC or R2 appears on a narrower endpoint
- very high AUC or R2 appears in a time-to-event, broad EHR, or internally optimized single-biobank setting
- the AUC is a clear outlier relative to the rest of the direct-match set and comes from a high-throughput single-biobank framework
- only a full-model AUROC is reported and the candidate is being treated as if that AUROC were a PRS-only metric
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
- If `classification_metrics` AUROC is high but the visible `other_metrics` suggest only a small incremental AUROC or small PGS-only R2, interpret the AUROC as mostly covariate-driven.
- Unknown covariates should lower confidence, not automatically help or hurt the candidate.

Near-outcome biomarker covariates:

- If covariates include disease-specific clinical laboratory measurements or biomarkers that are tightly coupled to the disease outcome, treat the reported AUC/R2 as severely inflated and essentially non-comparable to models with only demographic or genetic ancestry covariates. Specific known examples:
  - Thyroid function tests (TSH, T4, free T4, anti-TPO antibodies) in models for hypothyroidism, hyperthyroidism, or thyroid disease: these are near-outcome biomarkers that directly measure the disease state. A model reporting AUROC=0.85+ with these covariates is not demonstrating PRS quality; it is demonstrating that thyroid function tests predict thyroid disease.
  - Comorbidity panels (type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, renal failure, atrial fibrillation) in models for cardiovascular diseases like aortic stenosis or heart failure: these represent established clinical risk factors that individually predict the outcome. A model reporting C-index=0.87 with this covariate set is not demonstrating PRS quality; it is demonstrating that clinical comorbidities predict cardiovascular events.
  - BMI in models for obesity: BMI is the outcome definition itself. Including it as a covariate is circular.
  - Disease-specific carrier status or mutation burden variables: these are directly measuring part of the genetic signal, not independent covariates.
- When a model's reported AUC is very high (e.g., >0.80) and the covariates include multiple clinical predictors or near-outcome biomarkers, that AUC provides essentially no evidence about PRS discriminative quality and should not be used to outrank a model with lower AUC but much cleaner (demographic-only) covariates.
- In such cases, look instead at whether the model reports any incremental metrics, PGS-only metrics, or effect sizes that isolate the PRS contribution. If only the covariate-inflated full-model metric is available, treat the performance evidence as uninformative for ranking.

Metric availability bias:

- Do not automatically prefer a model solely because it reports an explicit PRS-comparable metric (e.g., PGS AUROC, partial-r, PGS R2) when a competing model from a much stronger study design reports only effect sizes or full-model metrics with cleaner covariates.
- A model from a major disease-focused multi-cohort GWAS meta-analysis that reports only hazard ratios or odds ratios per SD is not weaker than a portability-framework model that reports a modest partial-correlation (e.g., partial-r < 0.05) or a PGS-only AUROC barely above chance.
- When one candidate has explicit PRS-comparable metrics and another has only effect sizes, compare the strength of the available evidence rather than automatically rewarding metric type. A strong OR=1.7 per SD from a multi-cohort disease study signals meaningful PRS discrimination that a partial-r=0.02 from a portability sweep may not match in real-world deployment.

Tie-break guidance:

- Use AUC and R2 to separate candidates only when endpoint fidelity is already acceptable.
- Small metric gaps should not dominate if endpoint or covariate design differs.
- Material performance and validation advantages can outweigh a more disease-focused narrative when endpoints remain acceptably aligned and covariates are cleaner or more comparable.
- Missing metrics should lower confidence, but they do not automatically lose to inflated or non-comparable AUC.
- If two candidates share the same endpoint family and one reports high AUC only with much heavier covariates, do not let that AUC dominate over a cleaner but partially missing comparator.
- If a candidate's apparent advantage depends on family history, treatment variables, or target-adjacent baseline measurements, treat that advantage as weak unless the comparator evidence is otherwise clearly inferior.
- If two candidates share the same exact disease endpoint family and one candidate's only visible edge is a covariate-heavy AUC built on extensive comorbidity or near-outcome adjustment, do not let that metric automatically outrank a cleaner comparator that lacks AUC but has otherwise comparable support.
- If one model's main advantage is an outlier AUC from a high-throughput single-biobank framework, treat that metric as weak when several cleaner direct-match competitors cluster together in endpoint and study design.
- If no explicit PGS-only AUROC is reported, do not silently substitute the full-model AUROC as the ranking AUC.
- If one candidate reports only effect sizes (OR/HR per SD) while another reports an explicit but modest PRS-comparable metric from a portability framework, the effect-size candidate should not automatically lose. Compare the overall evidence packages including study design, cohort scale, and method context.

### Heritability sanity check

Core rule:

- Use trait heritability as a ceiling and sanity field for PRS-only metrics.
- Do not use heritability to back-calculate an exact full-model AUROC.
- The main role of heritability is to check whether the visible PRS-side metrics are self-consistent and plausibly scaled.

How to use it:

- Compare `PGS R2 (no covariates)` or another clearly PRS-comparable R2 against the best available local heritability estimate for the target trait.
- If the visible PRS-comparable R2 approaches or exceeds trait heritability, suspect metric misuse, scale mismatch, or non-comparable reporting.
- If full-model AUROC is very high but `incremental AUROC` is small and `PGS R2 (no covariates)` is modest relative to heritability, interpret the high AUROC as mainly covariate-driven rather than PRS-driven.
- If `PGS AUROC (no covariates)` is missing, lower confidence instead of promoting the candidate based on full-model AUROC alone.
- If a reported R2 is very high (e.g., >0.15) and the method is C+T or Clumping+Thresholding with unknown covariates, be especially skeptical: C+T-derived scores rarely capture enough genetic variance to explain >15% of trait variance for complex diseases.

Do not over-interpret:

- Heritability is a ceiling/sanity signal, not an exact conversion formula between R2 and AUROC.
- Liability-scale and observed-scale heritability may differ, so use them directionally unless the scale match is explicit.

## 3. validation_sample_size

Core rule:

- `validation_sample_size` is a strong tie-break field, not a primary ranking field.
- `validation_sample_size` should come from the same representative validation record used for `performance_metrics`, `phenotyping_reported`, and `covariates`.

Prefer:

- larger validation cohorts when endpoint fidelity is similar
- larger validation support when reported performance is otherwise close
- much stronger validation support when a cleaner endpoint competes against only a tiny metric gap

Down-rank when:

- a candidate has a very small validation sample
- a large validation sample is being used to justify a weaker phenotype match
- a very large validation sample is being used to rescue non-comparable AUC
- a large validation sample comes from a pan-trait single-biobank framework while a smaller but well-powered disease-focused study cohort has cleaner endpoint evidence

Tie-break guidance:

- Large validation size increases trust only after phenotype alignment is acceptable.
- A small AUC advantage from a tiny validation cohort should not automatically beat a near-tie candidate validated in a much larger cohort.
- Huge validation support alone should not beat a cleaner endpoint or a cleaner covariate design.
- Order-of-magnitude validation differences are meaningful only after checking endpoint fidelity, covariate comparability, and study archetype together.
- When reported discrimination is nearly tied, very large validation support can break the tie even if one candidate uses a self-reported version of the same disease endpoint.
- Very large validation from a portability-framework study should not automatically outweigh a moderately large validation from a disease-focused multi-cohort study.

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

Pan-trait framework identification and penalization:

- Identify candidates coming from pan-trait, pan-phenome, or portability-style high-throughput frameworks. Key signature phrases in publication titles include:
  - "Significant sparse polygenic risk scores across 813 traits" (snpnet UKB framework)
  - "Portability of 245 polygenic scores" (LDpred2 UKB portability framework)
  - "ExPRSweb" or "online repository with polygenic risk scores for common health-related exposures" (ExPRSweb framework)
  - "Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts" (Global Biobank Meta-analysis framework)
  - Any title emphasizing "across N traits" or "across N phenomes" where N is large
- These framework-generated models have lower prior probability of being the best deployment model for any specific disease because they were not optimized for that disease endpoint.
- When a disease-focused alternative exists (from a dedicated GWAS, disease consortium, or disease-specific publication), the framework model should be penalized relative to the disease-focused model unless the framework model also has substantially cleaner endpoint, covariate, and metric evidence.
- When the only visible metric advantage of a framework model is a modest PRS-comparable metric (e.g., partial-r < 0.05, PGS AUROC < 0.60) while a disease-focused model has stronger effect sizes, larger disease-specific training, or richer multi-cohort validation, the disease-focused model should be preferred.
- UKB snpnet models (from the "813 traits" paper) have a characteristic signature: typically low variant counts (single-digit to low-thousands), `snpnet` method, UKB as sole training/dev cohort, and standardized covariates (age, sex, UKB array type, Genotype PCs). These models often rank poorly in independent external evaluations despite having complete and well-formatted PGS Catalog metadata.

Down-rank when:

- the candidate is mainly supported by a single-biobank pan-trait workflow
- the candidate comes from a portability or pan-phenome sweep with limited disease-specific evidence
- a very large training sample is the main reason the model looks attractive
- the candidate is essentially a framework score surfaced by many cohorts but not clearly optimized for the target disease endpoint
- the candidate comes from an ExPRSweb-style exposure or trait repository and the disease-focused context is unclear

Tie-break guidance:

- Use `training_development_cohorts` to judge whether the model is disease-focused or generic.
- Use `samples_training` only as supporting evidence.
- Large training size cannot compensate for weaker endpoint fidelity.
- Within the same publication family, modest cohort-list or training-size differences are weak tie-breaks.
- Single-biobank portability papers should not beat disease-focused multi-cohort studies unless they also have clearly cleaner endpoint evidence and comparable metrics.
- When two candidates are both endpoint-faithful, do not automatically let a single-ancestry large-metric model beat a disease-focused multi-cohort or global study unless the former also has cleaner covariates and no stronger portability concerns.
- If several candidates from the same study family are all endpoint-faithful and share the same validation/evaluation context, treat that repeated family pattern as corroborating evidence rather than redundancy.
- A disease-focused multi-cohort study with many contributing biobanks (e.g., >5 cohorts including AllofUs, BioMe, FinnGen, UKB, MVP, etc.) is strong evidence of external validation and should be preferred over single-biobank framework scores.

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
- source-sensitive middle prior: `SBayesR`, `lassosum`, `DBSLMM`, `PRS-CS`, `PRS-CS-auto`, `PRSCS`
- low prior: `LDpred2-inf`, `LDpred`, `C+T`, `Clumping and Thresholding (C+T)`

Method-study-design interaction:

- A genome-wide shrinkage method (PRS-CS, PRSCS, LDpred2, LDpred2-auto) from a disease-focused multi-cohort GWAS meta-analysis should be strongly preferred over a sparse method (snpnet, C+T, GWS variants) from a pan-trait single-biobank framework, because the genome-wide shrinkage method captures more of the polygenic signal and the disease-focused context ensures endpoint relevance.
- `snpnet` models from pan-trait UKB frameworks (the "813 traits" paper) typically produce very sparse scores that may not capture enough genetic variance for complex polygenic traits. Despite complete metadata, they often generalize poorly to independent cohorts.
- `C+T` (Clumping and Thresholding) and similar simple thresholding methods have limited polygenic signal capture. If a C+T model reports very high R2 (e.g., R2 > 0.15 for a complex polygenic trait) with unknown covariates, treat that R2 as likely inflated or non-comparable.
- `Genome-wide significant variants` or `GWAS Hits` methods using small numbers of SNPs can be effective when the variants were identified in large, well-powered GWAS studies focused on the target disease, especially for diseases with strong individual-locus effects (e.g., some cancers, autoimmune diseases).
- Weighted PRS summation or multi-PRS methods that combine multiple component scores can capture both polygenic background and strong individual-locus effects; they should not be penalized for method complexity.
- `PRSCS` (case-sensitive variant of PRS-CS) from multi-ancestry disease studies should be treated equivalently to `PRS-CS` in the method ranking.

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
- If two candidates are otherwise closely matched and both fall within the paper's benchmark scope, the literature-derived prior above can be used as a mild tie-break.
- If a candidate wins mainly because it is `PRS-CS` or `PRS-CS-auto`, lower confidence unless non-method fields clearly support it.
- If a candidate wins mainly because it is `LDpred2` or `AnnoPred`, keep that advantage mild; do not let it override materially cleaner endpoint or study-design evidence from another method.
- If a candidate's only method advantage is being `C+T`, `LDpred`, or `LDpred2-inf`, treat that as a negative rather than a positive tie-break unless the non-method metadata are clearly stronger.
- If a candidate's only method advantage is being `SCT`, `lassosum2`, or `DBSLMM`, remember that the literature benchmark showed source-sensitive ordering; use extra caution instead of treating them as uniformly top-tier.
- If candidates are otherwise closely matched within the same study family, LD-aware shrinkage methods such as `PRS-CS`, `LDpred`, or `LDpred2` may be mildly preferred over very sparse P+T or GWAS-hit constructions.
- If candidates are otherwise closely matched within the same endpoint family, do not let a very sparse P+T score beat a genome-wide shrinkage score solely because of a modest AUC edge.
- If candidates share the same publication family, phenotype, validation cohort, and ancestry context, a modest AUC edge from an ultra-sparse construction is weak evidence against a genome-wide shrinkage score.
- If candidates share the same publication family, endpoint, validation size, ancestry context, and similarly missing covariates, prefer the genome-wide shrinkage score unless the sparse construction has a clearly larger, not merely modest, metric advantage.
- If a candidate wins mainly because the method name looks stronger, lower confidence.
- `snpnet` or other high-capacity penalized regression methods need extra caution when their advantage comes mainly from single-biobank optimization or unusually high internal AUC.
- Rare-pathogenic or clearly monogenic-leaning constructions should not automatically outrank genome-wide polygenic scores for generic common-disease risk unless the metadata show unusually strong and clean disease-level support.
- A `snpnet` model from a pan-trait framework paper should not beat a genome-wide shrinkage model (PRS-CS, LDpred2) from a disease-focused study, even if the snpnet model has a slightly higher reported metric, because snpnet pan-trait models tend to generalize poorly to independent cohorts.

## 6. ancestry_distribution

Core rule:

- `ancestry_distribution` is a compatibility and transportability field.
- Multi-ancestry appearance is not automatically an advantage.

Prefer:

- ancestry context that is interpretable for the intended deployment
- evaluation ancestry that is easier to trust for the target use case
- multi-ancestry evaluation from disease-focused studies, as this signals broader validation

Down-rank when:

- the evaluation ancestry is clearly mismatched
- the ancestry label looks broad but the deployment relevance is unclear

Tie-break guidance:

- Evaluation ancestry is often more informative than broad GWAS ancestry labels.
- Do not reward a candidate simply because the ancestry string looks more diverse.
- If deployment ancestry is unspecified, use this field cautiously and lower confidence rather than over-rank.
- Do not let mixed-ancestry evaluation beat a much stronger exact-disease candidate by itself.
- A single non-EUR or mixed-ancestry evaluation is not automatically more deployable than a much larger exact-disease evaluation in one ancestry.
- Multi-ancestry evaluation from a disease-focused multi-cohort study (e.g., AllofUs, MVP, diverse biobanks) is supportive evidence of model robustness.

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

Key framework paper signatures to identify and penalize:

- "Significant sparse polygenic risk scores across 813 traits in UK Biobank" = snpnet pan-trait UKB framework (frequently produces scores that do not generalize well to independent cohorts)
- "Portability of 245 polygenic scores when derived from the UK Biobank" = LDpred2 UKB portability framework
- "ExPRSweb: An online repository with polygenic risk scores for common health-related exposures" = ExPRSweb exposure-PRS framework
- "Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts" = Global Biobank meta-analysis framework (PRS-CS-auto)
- These framework papers are valuable for method benchmarking but their per-disease scores are not optimized for any specific disease and should not be preferred over disease-focused alternatives.

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
- A disease-focused GWAS meta-analysis (e.g., from a named disease consortium) should generally be preferred over a generic pan-trait framework paper from UKB, even if the meta-analysis is older or in preprint form.

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
- Very low variant counts (single-digit to low-tens) combined with a pan-trait framework origin is a warning sign: the model may not capture enough polygenic signal for complex traits.
- Very high variant counts (>100K) from genome-wide shrinkage methods are expected and should not be penalized; they reflect the method's design rather than overfitting.