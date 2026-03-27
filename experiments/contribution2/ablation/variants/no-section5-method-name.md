<!-- ABLATION: removed section "## 5. method_name" -->
# PRS Model Domain Knowledge

Purpose: field-level domain knowledge for PRS model selection, summarizing empirical evidence on which model characteristics predict real-world external validation performance.

Empirical evidence supports the following factor importance ordering for predicting real-world PRS performance:

1. phenotype alignment and endpoint fidelity
2. comparable reported performance (effect sizes, PRS-comparable metrics)
3. transportability context (ancestry, training cohorts, study archetype)
4. method family and model structure (method_name, variants_number)
5. weak signals from publication context, date, validation sample size

Cross-cutting empirical patterns:

- Reliable selection depends only on visible metadata fields.
- Partial mismatches lower confidence but do not invalidate a candidate unless the mismatch is explicit.
- Missing evidence lowers confidence in a candidate.
- No single attractive field reliably compensates for weaknesses across other dimensions.
- A model from a disease-focused multi-cohort study consistently outperforms a pan-trait framework score in external validation unless the framework score has clearly stronger endpoint AND metric evidence.
- When several endpoint-faithful candidates from the same disease-focused study family form a coherent cluster, that cluster is strong evidence and typically outperforms a lone exact-label or lone high-AUC candidate whose apparent edge comes mainly from recency, exact wording, or a single full-model metric.
- Basic demographic adjustment (`age`, `age^2`, `sex`, PCs, batch, genotyping array) is not heavy clinical leakage. Family history, treatment terms, disease biomarkers, and horizon-conditioned absolute-risk packaging are.
- Unknown covariates are a weaker penalty than explicit non-comparable covariates. Family history, treatment-aware terms, biomarker adjustment, strong mediator adjustment, and risk-wrapper packaging are not less concerning simply because they are explicitly disclosed.
- Horizon-conditioned packaging, age-specific absolute-risk packaging, and named clinical risk calculators (e.g., `CHARGE-AF`, Framingham, QRISK, pooled cohort equations, `5-year risk`, `absolute risk`, `screening risk`) are strong negative evidence for standalone PRS quality. These are deployment packages, not cleaner PRS evidence. A candidate that uses such packaging is typically outperformed in external validation by a direct disease model with only demographic/PC-style covariates, even when the packaged model has much larger validation support.
- A full-model AUROC that is boosted by biomarkers, family history, or a clinical risk calculator is a heavily discounted advantage. A high full-model AUROC that comes only from age/sex/PCs or standard exposure covariates is informative but still secondary to endpoint fidelity.
- Cross-cancer, cross-disease, or pan-trait framework scores do not reliably outperform a disease-specific direct-match score unless the framework score has clearly better endpoint fidelity and cleaner comparable metrics. Large validation alone is not sufficient.
- An older exact-label portability score, sparse UKB score, or generic framework score that appears to beat a newer disease-focused or multi-cohort direct-match score solely because the older score reports an explicit PRS-only AUROC, has a familiar method name, or has a much larger validation sample is typically a selection artifact rather than genuine superiority.
- `Phenotype risk score`, `phenotype risk`, broad EHR phenotype summary, or similar phenotype-derived clinical packaging represents severe comparability leakage. A direct disease PRS candidate is the stronger choice over such a package unless no cleaner disease candidate exists.
- Bundled non-genetic risk packaging (named clinical calculators, family-history packages, PM2.5 or broad environmental bundles, smoking interaction terms) is a stronger penalty than ordinary demographic or simple epidemiologic adjustment.
- Within the same publication family and the same exact disease endpoint, modest differences in validation size, wording, or study framing are weak signals. The sibling with materially stronger OR/HR, cleaner PRS-only metrics, or cleaner covariates is the stronger choice.
- Within same-endpoint near-clone families, when the endpoint and covariates are effectively identical, a stronger regularized sibling with better AUROC/OR evidence outperforms a weaker sparse sibling.
- Spelling noise, minor formatting variants, or trivial wording differences are not meaningful endpoint mismatches when `trait_reported`, `trait_efo`, and `phenotyping_reported` all point to the same disease entity.
- Disease-focused multi-cohort meta-analysis models with exact endpoints and only basic demographic covariates are typically the stronger choice over older prevalent-endpoint sparse models, even when the older model has a larger single-biobank validation sample.
- An MTAG-enhanced variant from the same disease study family is a stronger choice than the base variant — MTAG leverages genetically correlated trait information to boost power and is not a cross-trait contamination signal.

## 1. trait_reported / trait_efo / phenotyping_reported

Key empirical finding:

- `phenotyping_reported` is the primary endpoint-fidelity field.
- `trait_reported` and `trait_efo` are concept-alignment fields, not final deployment proof.
- Endpoint fidelity matters more than surface label similarity.

Positive signals (indicators of stronger real-world performance):

- direct clinical disease endpoint
- generic disease endpoint for generic disease-risk deployment
- general case-control or incident-plus-prevalent disease endpoint when the target is a generic disease concept
- combined or generic disease endpoints over fixed-horizon future-risk endpoints when the target itself is a generic disease concept
- diagnostic-code or phecode-based disease endpoints when they directly map to the same disease concept
- disease-adjacent trait labels when `phenotyping_reported` is still a direct diagnosis endpoint for the target disease and the study context remains disease-focused
- broader biology labels when `phenotyping_reported` is still a direct disease diagnosis endpoint for the target disease (for example, `adiposity` with an obesity phecode endpoint)
- combined labels that explicitly contain the target disease, even if they also mention a closely related condition
- near-synonymous disease labels with richer supporting evidence over exact but vague or unspecified labels
- exact disease endpoints with much stronger validation and materially better discrimination, even when they are self-reported
- clinically dominant subtypes when the target label is a broad organ-site cancer or umbrella carcinoma term and the subtype has much stronger support
- familial late-onset forms when the target itself is the same late-onset disease and no early-onset or monogenic enrichment is shown
- explicit diagnosis or phecode endpoints over broad weight-state, nutrition-bundle, or administrative composite phenotypes
- a broader biology label anchored by an explicit disease phecode over an exact-label time-to-event framework score, unless the framework score has clearly stronger comparable PRS-only evidence

MTAG and multi-trait analysis guidance:

- MTAG (Multi-Trait Analysis of GWAS) is a **legitimate power-boosting technique** that combines GWAS summary statistics across genetically correlated traits to increase effective sample size. MTAG is NOT a negative endpoint signal.
- Models with `(MTAG)` or `Multi-trait` in `trait_reported` that still target the same disease are **enhanced versions** of the base disease endpoint, not endpoint mismatches or cross-trait contamination.
- MTAG labeling is not endpoint ambiguity. When choosing between an MTAG variant and a non-MTAG variant of the same disease model from the same publication family, the MTAG variant is **mildly preferred** because it leverages additional genetic information to boost statistical power.
- Example: for dilated cardiomyopathy, `Dilated cardiomyopathy (MTAG)` is a stronger model than `Dilated cardiomyopathy` from the same study family — the MTAG version incorporates correlated trait information to boost power.

Clinically dominant subtype equivalences:

- When the target disease is a broad umbrella or organ-site term, the clinically dominant manifestation is semantically equivalent, not a subtype mismatch. Specific known equivalences include:
  - `obstructive sleep apnea` is the dominant clinical form of `sleep apnea` (~85% of clinical cases); an OSA-labeled model is the stronger choice over a generic sleep-apnea-labeled model when the OSA model has materially better study design, validation, or performance evidence.
  - `endometrial carcinoma` is the dominant histological subtype of `uterine carcinoma` (~90% of cases); an endometrial-cancer-labeled model is a strong match for a uterine-carcinoma target, especially when it has better endpoint and performance support than the exact-label alternative.
  - `renal cell carcinoma` is the dominant subtype of `kidney cancer` (~90% of cases).
  - `Graves' disease` is the dominant autoimmune form of clinical hyperthyroidism; for a generic `hyperthyroidism` target, a Graves-disease-labeled score is a strong direct match when the alternative is an older generic thyrotoxicosis framework score.
  - `adenocarcinoma` is the dominant subtype for many organ-site cancer targets.
- When a clinically dominant subtype candidate has materially stronger study design, validation, or performance evidence than the exact-label alternative, the dominant subtype is the stronger choice.
- The dominant subtype mismatch is not a meaningful penalty when it is the overwhelming clinical majority of the umbrella disease.

Warning signals (indicators of weaker real-world performance):

- `phenotyping_reported` is time-to-event, unless the candidate is from a major disease-focused multi-cohort study and the competing alternative is merely a portability or pan-trait framework score
- `phenotyping_reported` is incident-only while the target is generic disease risk, unless the candidate is from a dedicated disease GWAS meta-analysis with much stronger study support than the competing generic-label alternative
- `phenotyping_reported` is horizon-specific, such as 5-year risk
- `phenotyping_reported` is future-risk prediction rather than generic disease status
- `phenotyping_reported` is an age-conditioned or horizon-conditioned absolute-risk package rather than direct disease status
- `phenotyping_reported` is subtype-only, unless it is the clinically dominant subtype of the target disease
- `phenotyping_reported` is a proxy phenotype
- `phenotyping_reported` is treatment-induced or therapy-specific, unless the genetic basis captured by the score is biologically relevant to the target disease and no better alternative exists
- `phenotyping_reported` is a broad administrative phenotype bundle
- the label is broad or vague while a competing candidate is a clinically dominant subtype with much stronger support
- the endpoint is generic but unspecified and mainly surfaced by a portability or pan-trait framework rather than a disease-focused study
- the score is an exact broad-label match from a portability or framework paper while several near-synonymous subtype or diagnosis-anchored candidates have richer support
- pediatric-only, childhood-onset, smoker-only, therapy-specific, or otherwise restricted subtype endpoints when the target disease itself is generic — large validation size does not erase that endpoint mismatch
- `personal history of`, `history of`, survivorship, prior diagnosis, or post-diagnosis survivor phenotypes — these function as indirect or survivor-enriched endpoints and are weaker than an active disease diagnosis endpoint for a generic disease target
- when `trait_reported`, `trait_efo`, and `phenotyping_reported` point to clearly different diseases, disease phases, or malignancy subtypes, that candidate is metadata-contaminated or endpoint-incoherent — one superficially exact field does not reliably outperform a coherent cluster of direct-match candidates

When candidates are otherwise similar:

- Incident-only, time-to-event, and self-reported exact disease endpoints are all acceptable but none is an automatic winner.
- Self-reported exact disease does not automatically lose to a clinically ascertained alternative if it has much stronger validation support and materially better reported discrimination.
- When discrimination is nearly identical, self-reported exact disease with orders-of-magnitude larger validation support can outperform a clinically phrased alternative.
- Diagnostic-code and phecode instantiations of the same disease do not automatically lose to literal disease-string endpoints.
- A broader `trait_reported` label does not automatically lose when `phenotyping_reported` is a direct diagnosis endpoint for the target disease.
- Exact trait match provides only a **marginal advantage** over partial/subtype match. An exact-label model is not the stronger choice over a structurally superior model (stronger methodological properties, more variants, stronger study design) solely because of label exactness.
- Minor wording differences are not meaningful penalties when the disease concept is clearly the same.
- An exact but vague label is not automatically stronger than a near-synonymous candidate with much richer evidence.
- An exact but unspecified umbrella label from a portability-style or sparse-metadata study is not automatically stronger than a near-synonymous clinically specific disease label with much stronger validation and reported discrimination.
- A broad umbrella label is not automatically stronger than a clinically dominant subtype with much stronger endpoint and study support.
- Fixed-horizon, age-specific absolute-risk, screening-stratification, or similar risk-wrapper formulations are deployment packaging rather than stronger phenotype evidence. They do not reliably outperform a direct disease diagnosis, incidence, or case-control endpoint solely because of larger validation or higher full-model AUROC.
- When the target is a broad organ-site cancer concept, dominant subtypes such as the most common site-specific carcinoma can be the stronger choice if they are the only candidates with clearly stronger endpoint and study evidence, especially when the broad-label alternative mainly comes from a portability-style framework.
- When several near-synonymous subtype or diagnosis-anchored candidates form a coherent high-support cluster, that cluster is stronger evidence than a lone exact-label framework score.
- An incident-only or time-to-event endpoint from a major disease-focused multi-cohort study does not automatically lose to a generic-label portability-framework score that only has a modest partial-correlation or similar weak metric. The disease-focused study context and stronger overall evidence package can outweigh the endpoint-type penalty.
- Minor anatomical qualifiers, tissue descriptors, or formatting variants are not meaningful mismatches when `trait_reported`, `trait_efo`, and `phenotyping_reported` all point to the same underlying disease entity.
- Composite endpoints remain valid direct matches when the target disease is explicitly present in the endpoint and the added component is a closely related manifestation, subtype, or companion diagnosis from the same clinical spectrum.
- Case-control endpoints that contrast the target disease against a benign, precursor, or common differential-diagnosis condition remain direct matches because the disease arm is still the target endpoint.
- Familial forms remain direct matches when the disease concept and age-of-onset class are otherwise unchanged and no monogenic, syndromic, or clearly enriched special-population construct is explicit.
- When phenotype fields are noisy, partially contradictory, or likely contaminated by catalog artifacts, the most coherent disease-level evidence package across `trait_reported`, `trait_efo`, `phenotyping_reported`, publication context, effect sizes, performance metrics, and covariates is the better basis for ranking rather than letting one anomalous field dominate.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

Key empirical finding:

- `performance_metrics` is most reliably interpreted from one representative validation record, not from mixed records.
- When multiple validation records exist, the highest-result European validation record is the most informative; if no European validation exists, the highest-result record overall is the best available.
- The full `classification_metrics` and `other_metrics` from that selected record are more informative than a single scalar.
- Top-level `performance_metrics.auc` and `performance_metrics.r2` are PRS-comparable metrics only.
- Explicit `PGS AUROC (no covariates)`, `PGS R2 (no covariates)`, or covariates-regressed-out PRS metrics are the most reliable performance indicators when available.
- Generic `classification_metrics` AUROC/C-index and generic `R²` are full-model metrics unless the metric name explicitly says they are PGS-only or covariates-regressed-out.
- Full-model AUROC can be useful for within-record sanity checking, but it is not the primary cross-model ranking metric because real-world PRS performance is measured without covariate-boosted full-model discrimination.
- `performance_metrics.auc` and `performance_metrics.r2` are informative only after endpoint and covariate comparability are acceptable.
- `performance_metrics.r2` (when available as PRS-only R²) is among the **strongest field-level predictors** of real-world PRS performance. Models reporting PRS-only R² are more informative than those with only full-model metrics.
- Higher reported AUC or R2 is supportive evidence, not decisive evidence.
- Missing metrics do not automatically disqualify a candidate. A model from a disease-focused study with only effect sizes (OR, HR) but no explicit AUC or R2 can still be the best candidate if its study design, cohort context, and method are stronger than a framework score with explicit but modest PRS-comparable metrics.

Effect sizes as PRS-quality signals:

- When a candidate reports only `effect_sizes` (OR per SD, HR per SD, Beta) but no AUROC or R2, use the effect size magnitude as a supportive PRS-quality signal rather than treating the candidate as having no discrimination evidence.
- OR per SD is a **strong predictor** of real-world PRS performance — stronger than reported AUC. HR per SD is also a meaningful predictor.
- OR and HR magnitude guidelines: OR≥1.5 or HR≥1.5 per SD indicates strong PRS discriminative power; OR 1.3–1.5 or HR 1.2–1.5 is moderate; OR<1.3 or HR<1.2 suggests weak PRS signal.
- A strong per-SD OR (≥1.5) or HR (≥1.5) from a well-designed study is **meaningful evidence** of PRS discriminative power and carries more weight than validation sample size or record count.
- Effect sizes do not override clearly stronger AUC/R2 evidence from a comparably designed study, but they prevent automatic loss to a framework-generated score whose only advantage is metric availability.
- When comparing a disease-focused study candidate with strong effect sizes against a portability-framework candidate with a weak partial-correlation or modest PRS-only AUC, the effect-size evidence combined with study design weighs at least equally.
- A recent disease-focused multi-ancestry score with strong OR/HR and clean endpoint alignment can outperform an older exact-label score even when the newer study reports only effect sizes and not an explicit PRS-only AUROC.

Positive signals (indicators of stronger real-world performance):

- reported performance from candidates with comparable endpoints
- explicit PRS-only or otherwise PRS-comparable discrimination metrics
- discrimination reported with basic or otherwise comparable covariates
- full-model metrics that use only demographic/basic adjustment (`age`, `age^2`, `sex`, PCs, array, batch)
- stable performance evidence that does not depend on obvious endpoint shortcuts
- performance packages that do not rely on downstream clinical disease variables, family history, or treatment context

Warning signals (indicators of weaker real-world performance):

- very high AUC or R2 appears on a weaker endpoint
- very high AUC or R2 appears in a time-to-event, broad EHR, or internally optimized single-biobank setting
- the AUC is a clear outlier relative to the rest of the direct-match set and comes from a high-throughput single-biobank framework
- only a full-model AUROC is reported and the candidate is being treated as if that AUROC were a PRS-only metric
- reported performance is not comparable across studies
- performance depends on heavy clinical covariates (models with heavy covariates AND no reported PGS-only AUC are the worst-performing combination)
- performance depends on disease-adjacent clinical variables such as family history or established downstream clinical predictors
- reported discrimination comes from an age-specific absolute-risk or horizon-conditioned risk package rather than a direct PRS discrimination setting
- the only visible AUC comes from the more covariate-heavy or more internally optimized candidate within the same endpoint family

Covariate evidence:

- `covariates` functions as a comparability and optimism field.
- Heavy clinical covariates can make reported discrimination look substantially better than the PRS alone. The heavier the covariate set, the larger the gap between reported AUC and actual standalone PRS performance.
- `age`, `age^2`, `sex`, ancestry PCs, batch, and genotyping array are basic covariates and usually remain comparable across studies.
- Standard epidemiological covariates that are part of routine disease-risk modeling (e.g., smoking status for lung cancer or COPD, BMI for cardiometabolic diseases, alcohol use for liver disease) are **mild** comparability adjustments, not heavy clinical leakage. They become concerning only when bundled with multiple additional clinical predictors, family history, or near-outcome biomarkers.
- Covariate penalties apply proportionally: a single standard epidemiological covariate is a weaker comparability concern than a bundle of multiple clinical predictors or near-outcome biomarkers.
- Family history or disease-related clinical predictors can also make the reported metric less comparable to a PRS-only or PRS-light setting.
- Absolute-risk calibration or age-specific absolute-risk adjustment is a risk-package wrapper, not a neutral covariate set.
- `covariates = 0`, `None`, or an explicitly empty covariate field is usually interpretable as no added non-genetic covariates rather than hidden clinical augmentation.
- Unknown covariates from a large disease-focused multi-biobank study are a weaker penalty than explicit biomarker-heavy, family-history-heavy, or clinical-risk-calculator-heavy covariates. The cleaner disease-focused study is the stronger choice when the alternative's apparent edge depends on packaged clinical prediction.
- Unknown covariates lower confidence but do not automatically help or hurt the candidate. When one candidate has unknown covariates and another explicitly uses family history, treatment variables, disease biomarkers, or risk-wrapper adjustment, the explicit clinical augmentation is the stronger comparability concern.
- If `classification_metrics` AUROC is high but the visible `other_metrics` suggest only a small incremental AUROC or small PGS-only R2, interpret the AUROC as mostly covariate-driven.

Near-outcome biomarker covariates:

- When covariates include disease-specific clinical laboratory measurements or biomarkers that are tightly coupled to the disease outcome, the reported AUC/R2 is severely inflated and essentially non-comparable to models with only demographic or genetic ancestry covariates.
- When a model's reported AUC is very high (e.g., >0.80) and the covariates include multiple clinical predictors or near-outcome biomarkers, that AUC provides essentially no evidence about PRS discriminative quality. A model with lower AUC but much cleaner (demographic-only) covariates is the more informative candidate.
- The model's incremental metrics, PGS-only metrics, or effect sizes that isolate the PRS contribution are more informative. If only the covariate-inflated full-model metric is available, the performance evidence is uninformative for ranking.

Metric availability bias:

- A model is not automatically stronger solely because it reports an explicit PRS-comparable metric when a competing model from a much stronger study design reports only effect sizes or full-model metrics with cleaner covariates.
- When one candidate has explicit PRS-comparable metrics and another has only effect sizes, compare the strength of the available evidence rather than automatically rewarding metric type.

### Fallback guidance when ALL candidates lack PGS-only AUC

When no candidate in the pool reports a PGS-only or PRS-comparable AUC, AUC cannot differentiate. In this scenario:

- Validation sample size and publication narrative are weak signals and unreliable as the primary differentiator.
- The following fallback ranking order is more reliable:
  1. **Methodological properties** (from Section 5's property framework) — this is the strongest structural signal.
  2. **Variant count and effect size magnitude** — higher variant count within the same method family is a positive signal; a strong OR (>1.5) or HR (>1.5) signals meaningful PRS discriminative power even without AUC.
  3. **Small full-model AUC differences** between candidates with similar covariates are essentially noise. A difference of less than ~0.05 is not a meaningful differentiator. Structural differences are more informative.

### performance_metrics.record_count

- `record_count` has **negligible predictive value** for real-world PRS performance. Larger record counts do not predict better models.
- Record count is often redundant with `validation_sample_size` and carries the same negligible predictive value.

### Heritability sanity check

Key empirical finding:

- Trait heritability functions as a ceiling and sanity field for PRS-only metrics.
- Heritability is not useful for back-calculating an exact full-model AUROC.

How heritability informs interpretation:

- `PGS R2 (no covariates)` or another clearly PRS-comparable R2 can be compared against the best available local heritability estimate for the target trait.
- When the visible PRS-comparable R2 approaches or exceeds trait heritability, that suggests metric misuse, scale mismatch, or non-comparable reporting.
- When full-model AUROC is very high but `incremental AUROC` is small and `PGS R2 (no covariates)` is modest relative to heritability, the high AUROC is mainly covariate-driven rather than PRS-driven.
- When `PGS AUROC (no covariates)` is missing, confidence is lower. The candidate is not reliably promoted based on full-model AUROC alone.
- When a reported R2 is very high (e.g., >0.15) and the method is a clumping-and-thresholding or pruning-and-thresholding pipeline with unknown covariates, that R2 is suspect: scores derived from simple thresholding pipelines rarely capture enough genetic variance to explain >15% of trait variance for complex diseases.

When candidates are otherwise similar:

- AUC and R2 are informative for separating candidates only when endpoint fidelity is already acceptable.
- Small metric gaps are not meaningful differentiators when endpoint or covariate design differs.
- Missing metrics lower confidence, but they do not automatically lose to inflated or non-comparable AUC.
- When two candidates share the same endpoint family and one reports high AUC only with much heavier covariates, that AUC does not reliably indicate a stronger model.
- A candidate whose apparent advantage depends on family history, treatment variables, or target-adjacent baseline measurements has a weak advantage unless the comparator evidence is otherwise clearly inferior.
- When two candidates share the same exact disease endpoint family and one candidate's only visible edge is a covariate-heavy AUC built on extensive comorbidity or near-outcome adjustment, that metric does not reliably indicate a stronger model compared to a cleaner comparator.
- When no explicit PGS-only AUROC is reported, the full-model AUROC is not a valid substitute as the ranking AUC.
- When comparing two models and BOTH report only full-model AUC (no PGS-only metrics), their AUC values are essentially incomparable for ranking purposes — especially when they use different covariate sets. Structural signals (methodological properties, variant count, study design) are more reliable differentiators.
- Full-model C-index or AUROC with only basic demographic covariates can still be informative; it is not comparable to biomarker-heavy or treatment-aware clinical packaging.
- Within the same publication family and same endpoint family, a materially stronger OR/HR can break ties even if another candidate has slightly larger validation size or a more familiar evaluation ancestry.

## 3. validation_sample_size

Key empirical finding:

- `validation_sample_size` is a **very weak signal** for real-world PRS performance. It is a **last-resort tie-break**, not a meaningful differentiator.
- Larger validation sample size does not reliably predict better real-world performance. Selecting based primarily on validation size rarely leads to the best-performing model in external validation.
- `validation_sample_size` is most informative when drawn from the same representative validation record used for `performance_metrics`, `phenotyping_reported`, and `covariates`.

Warning signals (indicators of weaker real-world performance):

- a large validation sample is being used to justify a weaker phenotype match
- a very large validation sample is being used to rescue non-comparable AUC
- a large validation sample comes from a pan-trait single-biobank framework while a smaller but well-powered disease-focused study cohort has cleaner endpoint evidence
- a large validation sample is the primary justification for selection — this rarely predicts better external validation performance

When candidates are otherwise similar:

- Validation size is informative as a tie-break only when ALL other signals (endpoint, method, variants, performance, study design) are genuinely indistinguishable.
- Large validation size increases trust only after phenotype alignment is acceptable, and even then only minimally.
- Huge validation support alone does not reliably outperform a cleaner endpoint, a better method family, more variants, or a cleaner covariate design.
- Very large validation from a portability-framework study does not automatically outweigh a moderately large validation from a disease-focused multi-cohort study.
- Modest validation-size differences within the same publication family are essentially meaningless.
- Larger validation size does not reliably outperform a candidate with materially stronger methodological properties, variant count, or effect sizes.
- Large validation from a well-designed disease-focused study can be mildly supportive when the candidate is already endpoint-comparable and other signals are genuinely similar.

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

## 7. variants_number

Key empirical finding:

- `variants_number` is a moderate structural signal. For most diseases, more variants correlate with better external validation performance within the same method family.
- Variant count is most informative for comparing candidates **within** the same method family. Cross-method variant count comparison (e.g., genome-wide shrinkage vs GWAS-hits) reflects the method distinction already captured in Section 5 and is not an independent signal.

Within-method variant count comparison:

- For the **same method family**, the model with more variants is generally the stronger choice — the additional variants capture more polygenic signal.
- For **same-publication siblings** using the same method, a 1.5x or greater variant count difference is a meaningful structural signal.

Exceptions:

- For diseases with strong individual-locus effects (e.g., some cancers, autoimmune diseases, macular degeneration), GWAS-hits models with few variants can be competitive. For a meaningful minority of diseases, the variant count signal is weak or reversed.
- Very low variant counts (single-digit to low-tens) combined with a pan-trait framework origin is a warning sign: the model likely does not capture enough polygenic signal for complex traits.
