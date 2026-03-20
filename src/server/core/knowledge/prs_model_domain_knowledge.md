# PRS Model Domain Knowledge

Purpose: provide retrieval-friendly field-level policy for direct-match PRS model selection.

Use this ranking order:

1. phenotype alignment and endpoint fidelity
2. method family and model structure (method_name, variants_number)
3. comparable reported performance (effect sizes, PRS-comparable metrics)
4. transportability context (ancestry, training cohorts, study archetype)
5. weak tie-breaks from publication context, date, validation sample size

Global rules:

- Use only visible metadata.
- Down-rank rather than hard-reject unless the mismatch is explicit.
- Missing evidence should lower confidence.
- Do not let one attractive field dominate the decision.
- A model from a disease-focused multi-cohort study should not lose to a pan-trait framework score unless the framework score has clearly stronger endpoint AND metric evidence.
- If several endpoint-faithful candidates from the same disease-focused study family form a coherent cluster, that cluster is strong evidence and should usually beat a lone exact-label or lone high-AUC candidate whose apparent edge comes mainly from recency, exact wording, or a single full-model metric.
- Basic demographic adjustment (`age`, `age^2`, `sex`, PCs, batch, genotyping array) is not heavy clinical leakage. Family history, treatment terms, disease biomarkers, and horizon-conditioned absolute-risk packaging are.
- Unknown covariates are a weaker penalty than explicit non-comparable covariates. Do not reward family history, treatment-aware terms, biomarker adjustment, strong mediator adjustment, or risk-wrapper packaging simply because they are explicitly disclosed.

## High-priority selection rules

These rules are high-priority must-pass gates. Apply them before weaker tie-breaks from exact wording, publication familiarity, or raw validation size.

- Do not let an older exact-label portability score, sparse UKB score, or generic framework score beat a newer disease-focused or multi-cohort direct-match score solely because the older score reports an explicit PRS-only AUROC, has a familiar method name, or has a much larger validation sample.
- Treat horizon-conditioned packaging, age-specific absolute-risk packaging, and named clinical risk calculators as strong negative evidence. Examples include `5-year risk`, `absolute risk`, `screening risk`, `CHARGE-AF`, pooled clinical-risk calculators, or similar wrappers. These are deployment packages, not cleaner PRS evidence.
- If a candidate uses a named clinical risk calculator or explicit age-specific absolute-risk package, treat that as non-comparable deployment packaging, not as stronger disease evidence. Such a candidate should usually rank below a direct disease model with the same disease endpoint and only demographic/PC-style covariates, even when the packaged model has much larger validation support.
- Pediatric-only, childhood-onset, smoker-only, therapy-specific, or otherwise restricted subtype endpoints should not beat a generic disease endpoint when the target disease itself is generic. Large validation size does not erase that endpoint mismatch.
- `Personal history of`, `history of`, survivorship, prior diagnosis, or post-diagnosis survivor phenotypes are not stronger than an active disease diagnosis endpoint for a generic disease target. Treat them as indirect or survivor-enriched endpoints unless no cleaner disease endpoint exists.
- For generic cancer deployment, treat `personal history of`, survivor, prior-diagnosis, or post-diagnosis labels as a severe endpoint mismatch rather than a weak wording variant. Such a model should not beat an active disease, incident cancer, or ordinary case-control breast/prostate/lung/bladder cancer endpoint just because it reports a higher full-model AUROC.
- If `trait_reported`, `trait_efo`, and `phenotyping_reported` point to clearly different diseases, disease phases, or malignancy subtypes, treat that candidate as metadata-contaminated or endpoint-incoherent. Do not let one superficially exact field beat a coherent cluster of direct-match candidates.
- Unknown covariates from a large disease-focused multi-biobank study are a weaker penalty than explicit biomarker-heavy, family-history-heavy, or clinical-risk-calculator-heavy covariates. Prefer the cleaner disease-focused study when the alternative's apparent edge depends on packaged clinical prediction.
- Do not over-penalize common epidemiologic exposure covariates when they are part of standard disease-risk modeling rather than direct outcome measurement. Smoking status/intensity for lung disease or lung cancer is a weaker penalty than thyroid labs, family history packages, or named clinical risk calculators. In contrast, mediator-heavy or broad risk-factor packages such as BMI plus smoking plus site/race/ethnicity for common cardiometabolic disease should still be treated as meaningful penalties if cleaner exact-disease candidates exist.
- For common cardiometabolic disease targets such as atrial fibrillation or hypertension, mediator-heavy prevalence packaging (`BMI`, smoking, site, race/ethnicity, risk-calculator terms) should not outrank an exact disease endpoint with age/sex/PC-style covariates merely because the packaged model reports a larger full-model AUROC or a larger validation sample.
- When several direct-match candidates from the same disease-focused study family or modern method family (`PRSmix`, `PRSmixPlus`, `LDpred2`, `PRS-CSx`, related ensemble or multi-cohort variants) form a coherent cluster with clean demographic covariates and similar endpoints, treat that cluster as stronger evidence than a lone older portability-style or sparse exact-label score.
- When the same exact endpoint is represented by modern multi-biobank or comparative families such as `PRSmix`, `PRSmixPlus`, `UKBB-EUR.MultiPRS.CV`, `LDpred2.CV`, `megaprs.*`, or disease-focused `PRS-CSx`/ensemble variants with age/sex/PC-only or no-covariate packaging, do not let an older `snpnet`, `Cancer PRSweb`, sparse UKB, or other legacy exact-label score win solely because it exposes explicit `PGS AUROC`, `PGS R2`, or more familiar case-control wording.
- If a modern same-endpoint comparative family contributes several closely agreeing candidates with empty/basic covariates and similar OR/HR or R2 support, treat that family as the default favorite over a lone older `snpnet`, `Cancer PRSweb`, `Global Biobank`, or cross-cancer package. The older score should win only if its endpoint is materially cleaner and its apparent advantage does not depend mainly on explicit PRS-only metric availability or much larger validation size.
- Cross-cancer, cross-disease, or pan-trait framework scores should not beat a disease-specific direct-match score unless the framework score has clearly better endpoint fidelity and cleaner comparable metrics. Large validation alone is not enough.
- If a candidate's main advantage is a full-model AUROC that is boosted by biomarkers, family history, or a clinical risk calculator, discount that advantage heavily. If the same high full-model AUROC comes only from age/sex/PCs or standard exposure covariates, treat it as informative but still secondary to endpoint fidelity.
- Treat `phenotype risk score`, `phenotype risk`, broad EHR phenotype summary, or similar phenotype-derived clinical packaging as severe comparability leakage. A direct disease PRS candidate should beat such a package unless no cleaner disease candidate exists.
- A recent disease-focused multi-ancestry score with strong OR/HR and clean endpoint alignment can beat an older exact-label score even when the newer study reports only effect sizes and not an explicit PRS-only AUROC.
- Treat bundled non-genetic risk packaging as a stronger penalty than ordinary demographic or simple epidemiologic adjustment. Named clinical calculators (`CHARGE-AF`), family-history packages, PM2.5 or broad environmental bundles, smoking interaction terms, and similar deployment wrappers should not beat a direct disease score whose covariates are only age/sex/PC-style or simple smoking/BMI-style adjustment.
- For any disease target, do not let `prevalent/progression throughout adulthood`, `risk prediction`, or calculator-augmented packaging outrank an exact disease endpoint with age/sex/PC-style covariates just because the packaged model is larger, more multi-ethnic, or reports a much higher full-model AUROC/C-index.
- For thromboembolic targets, if several direct-match candidates with basic covariates and explicit PRS-only metrics form a coherent cluster, prefer that cluster over a lone small single-ancestry exact-label score with unknown covariates whose apparent edge is one high internal AUROC.
- Within the same publication family and the same exact disease endpoint, modest differences in validation size, wording, or study framing are weak tie-breaks. Prefer the sibling with materially stronger OR/HR, cleaner PRS-only metrics, or cleaner covariates rather than switching families on superficial metadata differences.
- If a named clinical risk calculator (e.g., CHARGE-AF, Framingham, QRISK, pooled cohort equations) appears in covariates, treat that candidate as deployment packaging rather than a clean standalone PRS model. Do not select it while any exact-disease candidate with only age/sex(/PC)-style covariates remains available, regardless of sample size, recency, or full-model metric advantage.
- Within the same organ-site cancer repository or same near-clone endpoint family, if the endpoint and covariates are effectively identical, prefer the sibling with the stronger AUROC/OR package rather than a weaker GWAS-hits near-clone that survives mainly because of sample-size wording.
- Within same-endpoint near-clone families, if the endpoint and covariates are effectively identical, a stronger regularized sibling with better AUROC/OR evidence should beat a weaker sparse sibling. Do not treat the weaker sibling as equally good just because both are exact-label matches.
- Spelling noise, minor formatting variants, or trivial wording differences should not create endpoint mismatches when `trait_reported`, `trait_efo`, and `phenotyping_reported` all point to the same disease entity.
- For any disease target, do not let an older exact-label sparse or framework score win solely because it exposes explicit PGS-only AUROC/R2. If a coherent exact-disease family from modern comparative studies is available with clean age/sex/PC-style covariates, prefer that family unless the older score is otherwise clearly stronger.

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
- broader biology labels when `phenotyping_reported` is still a direct disease diagnosis endpoint for the target disease (for example, `adiposity` with an obesity phecode endpoint)
- combined labels that explicitly contain the target disease, even if they also mention a closely related condition
- near-synonymous disease labels with richer supporting evidence over exact but vague or unspecified labels
- exact disease endpoints with much stronger validation and materially better discrimination, even when they are self-reported
- clinically dominant subtypes when the target label is a broad organ-site cancer or umbrella carcinoma term and the subtype has much stronger support
- familial late-onset forms when the target itself is the same late-onset disease and no early-onset or monogenic enrichment is shown

MTAG and multi-trait analysis guidance:

- MTAG (Multi-Trait Analysis of GWAS) is a **legitimate power-boosting technique** that combines GWAS summary statistics across genetically correlated traits to increase effective sample size. MTAG is NOT a negative endpoint signal.
- Models with `(MTAG)` or `Multi-trait` in `trait_reported` that still target the same disease should be treated as **enhanced versions** of the base disease endpoint, not as endpoint mismatches or cross-trait contamination.
- Do NOT penalize MTAG labeling as endpoint ambiguity. When choosing between an MTAG variant and a non-MTAG variant of the same disease model from the same publication family, the MTAG variant should be **mildly preferred** because it leverages additional genetic information to boost statistical power.
- Example: for dilated cardiomyopathy, `Dilated cardiomyopathy (MTAG)` is a stronger model than `Dilated cardiomyopathy` from the same study family — the MTAG version incorporates correlated trait information to boost power.

Clinically dominant subtype equivalences:

- When the target disease is a broad umbrella or organ-site term, the clinically dominant manifestation must be treated as semantically equivalent, not as a subtype mismatch. Specific known equivalences include:
  - `obstructive sleep apnea` is the dominant clinical form of `sleep apnea` (~85% of clinical cases); an OSA-labeled model should be preferred over a generic sleep-apnea-labeled model when the OSA model has materially better study design, validation, or performance evidence.
  - `endometrial carcinoma` is the dominant histological subtype of `uterine carcinoma` (~90% of cases); an endometrial-cancer-labeled model should be treated as a strong match for a uterine-carcinoma target, especially when it has better endpoint and performance support than the exact-label alternative.
  - `renal cell carcinoma` is the dominant subtype of `kidney cancer` (~90% of cases).
  - `Graves' disease` is the dominant autoimmune form of clinical hyperthyroidism; for a generic `hyperthyroidism` target, a Graves-disease-labeled score is a strong direct match when the alternative is an older generic thyrotoxicosis framework score.
  - `adenocarcinoma` is the dominant subtype for many organ-site cancer targets.
- When a clinically dominant subtype candidate has materially stronger study design, validation, or performance evidence than the exact-label alternative, the dominant subtype should be preferred.
- Do not penalize the dominant subtype mismatch when it is the overwhelming clinical majority of the umbrella disease.

Down-rank when:

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

Tie-break guidance:

- Incident-only, time-to-event, and self-reported exact disease endpoints are all acceptable but none is an automatic winner.
- Self-reported exact disease should not automatically lose to a clinically ascertained alternative if it has much stronger validation support and materially better reported discrimination.
- If discrimination is nearly identical, self-reported exact disease with orders-of-magnitude larger validation support can beat a clinically phrased alternative.
- Diagnostic-code and phecode instantiations of the same disease should not automatically lose to literal disease-string endpoints.
- A broader `trait_reported` label should not automatically lose when `phenotyping_reported` is a direct diagnosis endpoint for the target disease.
- Exact trait match provides only a **marginal advantage** over partial/subtype match. Do NOT select an exact-label model over a structurally superior model (better method tier, more variants, stronger study design) solely because of label exactness.
- Do not over-penalize minor wording differences when the disease concept is clearly the same.
- Do not automatically prefer an exact but vague label over a near-synonymous candidate with much richer evidence.
- Do not automatically prefer an exact but unspecified umbrella label from a portability-style or sparse-metadata study over a near-synonymous clinically specific disease label with much stronger validation and reported discrimination.
- Do not automatically prefer a broad umbrella label over a clinically dominant subtype with much stronger endpoint and study support.
- Fixed-horizon future-risk or prediction-oriented endpoints should not outrank a generic disease endpoint for generic deployment unless the generic disease candidates are otherwise much weaker.
- Fixed-horizon, age-specific absolute-risk, screening-stratification, or similar risk-wrapper formulations should be treated as deployment packaging rather than stronger phenotype evidence. They should not beat a direct disease diagnosis, incidence, or case-control endpoint solely because of larger validation or higher full-model AUROC.
- If a horizon-conditioned or age-specific risk package reports only full-model discrimination and no clearly isolated PRS-only metric or effect-size advantage, it should usually rank below a direct disease endpoint from the same disease family.
- When the target is a broad organ-site cancer concept, dominant subtypes such as the most common site-specific carcinoma can be preferred if they are the only candidates with clearly stronger endpoint and study evidence, especially when the broad-label alternative mainly comes from a portability-style framework.
- If several near-synonymous subtype or diagnosis-anchored candidates form a coherent high-support cluster, that cluster should be treated as stronger evidence than a lone exact-label framework score.
- An incident-only or time-to-event endpoint from a major disease-focused multi-cohort study should not automatically lose to a generic-label portability-framework score that only has a modest partial-correlation or similar weak metric. The disease-focused study context and stronger overall evidence package can outweigh the endpoint-type penalty.
- Minor anatomical qualifiers, tissue descriptors, or formatting variants should not create a mismatch when `trait_reported`, `trait_efo`, and `phenotyping_reported` all point to the same underlying disease entity.
- Composite endpoints remain valid direct matches when the target disease is explicitly present in the endpoint and the added component is a closely related manifestation, subtype, or companion diagnosis from the same clinical spectrum.
- Case-control endpoints that contrast the target disease against a benign, precursor, or common differential-diagnosis condition remain direct matches because the disease arm is still the target endpoint.
- Familial forms remain direct matches when the disease concept and age-of-onset class are otherwise unchanged and no monogenic, syndromic, or clearly enriched special-population construct is explicit.
- When phenotype fields are noisy, partially contradictory, or likely contaminated by catalog artifacts, resolve the ranking from the most coherent disease-level evidence package across `trait_reported`, `trait_efo`, `phenotyping_reported`, publication context, effect sizes, performance metrics, and covariates rather than letting one anomalous field dominate.

## 2. performance_metrics.auc / performance_metrics.r2 / covariates

Core rule:

- `performance_metrics` should be interpreted from one representative validation record, not from mixed records.
- When multiple validation records exist, prefer the highest-result European validation record; if no European validation exists, use the highest-result record overall.
- Preserve and inspect the full `classification_metrics` and `other_metrics` from that selected record instead of reducing them to a single scalar.
- Treat top-level `performance_metrics.auc` and `performance_metrics.r2` as PRS-comparable metrics only.
- Prefer explicit `PGS AUROC (no covariates)`, `PGS R2 (no covariates)`, or covariates-regressed-out PRS metrics when available.
- Treat generic `classification_metrics` AUROC/C-index and generic `R²` as full-model metrics unless the metric name explicitly says they are PGS-only or covariates-regressed-out.
- Full-model AUROC can be useful for within-record sanity checking, but it is not the primary cross-model ranking metric because real-world PRS performance is measured without covariate-boosted full-model discrimination.
- `performance_metrics.auc` and `performance_metrics.r2` are useful only after endpoint and covariate comparability are acceptable.
- `performance_metrics.r2` (when available as PRS-only R²) is among the **strongest field-level predictors** of real-world PRS performance. Prefer models reporting PRS-only R² over those with only full-model metrics.
- Higher reported AUC or R2 is supportive evidence, not decisive evidence.
- Missing metrics should not automatically disqualify a candidate. A model from a disease-focused study with only effect sizes (OR, HR) but no explicit AUC or R2 can still be the best candidate if its study design, cohort context, and method are stronger than a framework score with explicit but modest PRS-comparable metrics.

Effect sizes as PRS-quality signals:

- When a candidate reports only `effect_sizes` (OR per SD, HR per SD, Beta) but no AUROC or R2, use the effect size magnitude as a supportive PRS-quality signal rather than treating the candidate as having no discrimination evidence.
- OR per SD is a **strong predictor** of real-world PRS performance — stronger than reported AUC. HR per SD is also a meaningful predictor.
- OR and HR magnitude guidelines: OR≥1.5 or HR≥1.5 per SD indicates strong PRS discriminative power; OR 1.3–1.5 or HR 1.2–1.5 is moderate; OR<1.3 or HR<1.2 suggests weak PRS signal.
- A strong per-SD OR (≥1.5) or HR (≥1.5) from a well-designed study is **meaningful evidence** of PRS discriminative power and should be weighted more heavily than validation sample size or record count.
- Effect sizes should not override clearly stronger AUC/R2 evidence from a comparably designed study, but they should prevent automatic loss to a framework-generated score whose only advantage is metric availability.
- When comparing a disease-focused study candidate with strong effect sizes against a portability-framework candidate with a weak partial-correlation or modest PRS-only AUC, the effect-size evidence combined with study design should weigh at least equally.

Prefer:

- reported performance from candidates with comparable endpoints
- explicit PRS-only or otherwise PRS-comparable discrimination metrics
- discrimination reported with basic or otherwise comparable covariates
- full-model metrics that use only demographic/basic adjustment (`age`, `age^2`, `sex`, PCs, array, batch)
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
- performance depends on heavy clinical covariates (models with heavy covariates AND no reported PGS-only AUC are the worst-performing combination)
- performance depends on disease-adjacent clinical variables such as family history or established downstream clinical predictors
- performance depends on treatment assignment, treatment interaction, or other intervention-context variables
- reported discrimination comes from an age-specific absolute-risk or horizon-conditioned risk package rather than a direct PRS discrimination setting
- performance depends on near-outcome baseline measurements such as body-size, organ-function, or disease-severity variables that are tightly coupled to the target phenotype
- the only candidate with reported AUC in a study family wins solely because competing models have null metrics
- the only visible AUC comes from the more covariate-heavy or more internally optimized candidate within the same endpoint family
- the reported metric appears to come from a combined clinical-risk package rather than something close to PRS-plus-basic covariates

Covariate rule:

- Treat `covariates` as a comparability and optimism field.
- Heavy clinical covariates can make reported discrimination look substantially better than the PRS alone. The heavier the covariate set, the larger the gap between reported AUC and actual standalone PRS performance. Basic demographic covariates introduce modest inflation; heavy clinical covariates or lifestyle/exposure bundles can inflate reported AUC substantially relative to real-world PRS-only performance.
- `age`, `age^2`, `sex`, ancestry PCs, batch, and genotyping array are basic covariates and usually remain comparable across studies.
- Standard epidemiological covariates that are part of routine disease-risk modeling (e.g., smoking status for lung cancer or COPD, BMI for cardiometabolic diseases, alcohol use for liver disease) should be treated as **mild** comparability adjustments, not as heavy clinical leakage. Only penalize these when they are bundled with multiple additional clinical predictors, family history, or near-outcome biomarkers. Do not reject a model solely because it adjusts for one or two standard risk factors that are universally included in clinical epidemiology for that disease.
- Family history or disease-related clinical predictors can also make the reported metric less comparable to a PRS-only or PRS-light setting.
- Treatment variables, intervention terms, and near-outcome baseline measurements can make the metric reflect prognostic enrichment rather than PRS quality.
- Absolute-risk calibration or age-specific absolute-risk adjustment should be treated as a risk-package wrapper, not as a neutral covariate set.
- `covariates = 0`, `None`, or an explicitly empty covariate field should usually be interpreted as no added non-genetic covariates rather than as hidden clinical augmentation. When other fields are otherwise comparable, such models are often closer to PRS-only evidence than models that explicitly add family history, risk calculators, or disease-adjacent predictors.
- Family history plus broad exposure or behavior bundles (`smoking` interactions, PM2.5 or other environmental exposures, UV-behavior variables, PSA/stage variables, disease-stage terms) is a strong non-comparability signal. Such packages are usually less trustworthy for standalone PRS ranking than a cleaner direct-match model with only age/sex/PC-style covariates or a modest simple exposure adjustment.
- If `classification_metrics` AUROC is high but the visible `other_metrics` suggest only a small incremental AUROC or small PGS-only R2, interpret the AUROC as mostly covariate-driven.
- Unknown covariates should lower confidence, not automatically help or hurt the candidate.
- If one candidate has unknown covariates and another explicitly uses family history, treatment variables, disease biomarkers, strong mediators, or risk-wrapper adjustment, the explicit clinical augmentation is the stronger comparability concern. Unknown should not automatically lose to it.

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
- Within the same study family and same endpoint, an explicitly mediator-adjusted version should not automatically outrank an otherwise similar unadjusted version for generic deployment.
- If two candidates share the same exact disease endpoint family and one candidate's only visible edge is a covariate-heavy AUC built on extensive comorbidity or near-outcome adjustment, do not let that metric automatically outrank a cleaner comparator that lacks AUC but has otherwise comparable support.
- If a risk-wrapper or horizon-conditioned candidate's main edge is a high full-model AUROC, do not let that metric outrank a direct disease endpoint that has cleaner covariates plus either effect-size evidence or otherwise coherent disease-focused support.
- If one model's main advantage is an outlier AUC from a high-throughput single-biobank framework, treat that metric as weak when several cleaner direct-match competitors cluster together in endpoint and study design.
- If no explicit PGS-only AUROC is reported, do not silently substitute the full-model AUROC as the ranking AUC.
- When comparing two models and BOTH report only full-model AUC (no PGS-only metrics), treat their AUC values as essentially incomparable for ranking purposes — especially when they use different covariate sets. Fall back to structural signals (method tier, variant count, study design) rather than letting small full-model AUC differences drive the decision.
- If one candidate reports only effect sizes (OR/HR per SD) while another reports an explicit but modest PRS-comparable metric from a portability framework, the effect-size candidate should not automatically lose. Compare the overall evidence packages including study design, cohort scale, and method context.
- Full-model C-index or AUROC with only basic demographic covariates can still be informative; do not penalize it as if it came from biomarker-heavy or treatment-aware clinical packaging.
- Within the same publication family and same endpoint family, a materially stronger OR/HR can break ties even if another candidate has slightly larger validation size or a more familiar evaluation ancestry.

### Fallback guidance when ALL candidates lack PGS-only AUC

When no candidate in the pool reports a PGS-only or PRS-comparable AUC (all candidates report only full-model metrics or no AUC at all), the agent cannot use AUC to differentiate. In this scenario:

- Do NOT fall back to validation sample size or publication narrative as the primary differentiator — these are weak signals.
- Instead, use the following fallback ranking order:
  1. **Method family tier** (S/A/B/C/D from Section 5) — this is the strongest structural signal.
  2. **Variant count** — higher variant count within the same method family is a positive signal.
  3. **Effect size magnitude** (OR/HR per SD) — a strong OR (>1.5) or HR (>1.5) signals meaningful PRS discriminative power even without AUC.
  4. **Full-model R²** — while inflated, full-model R² is a stronger differentiator than full-model AUC and can help when all candidates report it.
  5. **Small full-model AUC differences** between candidates with similar covariates are essentially noise. A difference of less than ~0.05 (e.g., 0.70 vs 0.67) should not drive the decision. Look for structural differences instead.

### performance_metrics.record_count

- `record_count` (the number of records in the validation/evaluation sample) has **negligible predictive value** for real-world PRS performance. Larger record counts do not predict better models.
- Do NOT use record_count as a differentiator. A model validated on 100K records is NOT inherently better than one validated on 10K records.
- Record count is often redundant with `validation_sample_size` and carries the same negligible predictive value.

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

- `validation_sample_size` is a **very weak signal** for real-world PRS performance. It should be treated as a **last-resort tie-break**, not a meaningful differentiator.
- Larger validation sample size does not predict better real-world performance. Models with larger validation samples are NOT inherently better — selecting based on validation size is a common error that leads to choosing models that generalize poorly.
- `validation_sample_size` should come from the same representative validation record used for `performance_metrics`, `phenotyping_reported`, and `covariates`.
- **Never select a model primarily because it has the largest validation sample.** A model with n=50K validation is NOT inherently better than one with n=5K.

Down-rank when:

- a large validation sample is being used to justify a weaker phenotype match
- a very large validation sample is being used to rescue non-comparable AUC
- a large validation sample comes from a pan-trait single-biobank framework while a smaller but well-powered disease-focused study cohort has cleaner endpoint evidence
- a large validation sample is the agent's primary justification for selection — this is almost always a mistake

Tie-break guidance:

- Only use validation size as a tie-break when ALL other signals (endpoint, method, variants, performance, study design) are genuinely indistinguishable.
- Large validation size increases trust only after phenotype alignment is acceptable, and even then only minimally.
- Huge validation support alone should not beat a cleaner endpoint, a better method family, more variants, or a cleaner covariate design.
- Very large validation from a portability-framework study should not automatically outweigh a moderately large validation from a disease-focused multi-cohort study.
- Modest validation-size differences within the same publication family are essentially meaningless.
- Larger validation size should not beat a candidate with materially stronger method tier, variant count, or effect sizes.

## 4. training_development_cohorts / samples_training

Core rule:

- `training_development_cohorts` is mainly a transportability field. The number of training cohorts has only a **marginal** effect on real-world performance. Do NOT over-weight cohort count as a primary differentiator — study archetype (disease-focused vs framework) matters far more than cohort count.
- `samples_training` has **negligible predictive value** for real-world PRS performance. Larger training samples do NOT predict better real-world performance. Do not use training sample size as a differentiator.
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

- **Framework models underperform disease-focused models systematically.** Pan-trait and portability-framework models generalize less well to independent external cohorts than disease-focused models. Selecting a framework score over a disease-focused alternative is a frequent and costly error pattern.
- Identify candidates coming from pan-trait, pan-phenome, or portability-style high-throughput frameworks. Key signature phrases in publication titles include:
  - "Significant sparse polygenic risk scores across 813 traits" (snpnet UKB framework)
  - "Portability of 245 polygenic scores" (LDpred2 UKB portability framework)
  - "ExPRSweb" or "online repository with polygenic risk scores for common health-related exposures" (ExPRSweb framework)
  - "Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts" (Global Biobank Meta-analysis framework)
  - Any title emphasizing "across N traits" or "across N phenomes" where N is large
- **Decision rule: When a disease-focused alternative exists with acceptable endpoint fidelity, do NOT select a framework model.** The framework model should only win if it has clearly superior endpoint fidelity AND method tier AND metric evidence — not just one of these. A framework model's complete metadata, large sample size, or modest metric advantage is NOT sufficient to override a disease-focused alternative.
- **Framework penalty should be proportional to method quality.** Framework models using S-tier or A-tier methods (PRSmixPlus, MegaPRS, LDpred2, PRS-CSx) should receive a lighter framework penalty than C/D-tier framework models (snpnet, C+T). The framework penalty primarily targets the combination of generic study design AND weak method — an S-tier method from a benchmarking/comparative study with the exact target endpoint is structurally different from a C-tier snpnet pan-trait framework score.
- When the only visible metric advantage of a framework model is a modest PRS-comparable metric (e.g., partial-r < 0.05, PGS AUROC < 0.60) while a disease-focused model has stronger effect sizes, larger disease-specific training, or richer multi-cohort validation, the disease-focused model should be preferred.
- UKB snpnet models (from the "813 traits" paper) have a characteristic signature: typically low variant counts (single-digit to low-thousands), `snpnet` method, UKB as sole training/dev cohort, and standardized covariates (age, sex, UKB array type, Genotype PCs). These models generalize poorly to independent external cohorts despite having complete and well-formatted PGS Catalog metadata. Do not let snpnet framework completeness of metadata mislead you into selecting them over disease-focused alternatives.

Down-rank when:

- the candidate is mainly supported by a single-biobank pan-trait workflow
- the candidate comes from a portability or pan-phenome sweep with limited disease-specific evidence
- a very large training sample is the main reason the model looks attractive
- the candidate is essentially a framework score surfaced by many cohorts but not clearly optimized for the target disease endpoint
- the candidate comes from an ExPRSweb-style exposure or trait repository and the disease-focused context is unclear

Tie-break guidance:

- Use `training_development_cohorts` to judge whether the model is disease-focused or generic.
- Use `samples_training` only as supporting evidence — it has negligible predictive value and should never drive a decision.
- Large training size cannot compensate for weaker endpoint fidelity.
- Within the same publication family, modest cohort-list or training-size differences are weak tie-breaks.
- Single-biobank portability papers should not beat disease-focused multi-cohort studies unless they also have clearly cleaner endpoint evidence and comparable metrics.
- When two candidates are both endpoint-faithful, do not automatically let a single-ancestry large-metric model beat a disease-focused multi-cohort or global study unless the former also has cleaner covariates and no stronger portability concerns.
- A coherent disease-focused multi-cohort study family with exact or near-exact endpoints can still beat a lone portability or legacy exact-label score even when the family has unknown covariates, if the competitor's main edge comes from explicit clinical augmentation or risk-wrapper packaging.
- If several candidates from the same study family are all endpoint-faithful and share the same validation/evaluation context, treat that repeated family pattern as corroborating evidence rather than redundancy.
- A disease-focused multi-cohort study with many contributing biobanks (e.g., >5 cohorts including AllofUs, BioMe, FinnGen, UKB, MVP, etc.) is strong evidence of external validation and should be preferred over single-biobank framework scores.

## 5. method_name

Core rule:

- `method_name` is a **strong structural signal** — the strongest single field-level predictor of real-world PRS performance. Selecting a model from the right method family is critical for external validation success.
- Method family should be used as a **primary differentiator** after endpoint fidelity, not merely as a weak tie-break.
- However, method tier should NOT override clear within-family empirical performance evidence. When two models from the same publication family share the same disease endpoint and covariates, the model with stronger reported discrimination (higher AUC, stronger effect sizes) should be preferred even if it uses a lower-tier method. Method tier differentiates across study families; within the same family, empirical evidence takes precedence.
- For diseases with strong individual-locus effects (e.g., Hodgkin lymphoma, testicular cancer, bladder cancer, macular degeneration), sparse GWAS-hits or P+T models can outperform genome-wide shrinkage methods because the genetic architecture is concentrated in a few major loci rather than distributed across the genome. Do not force a genome-wide shrinkage preference when empirical evidence within the same study family clearly favors a sparse model.
- Method modernity alone is not a quality proxy, but the tier system below reflects established real-world external validation performance patterns.

Method family tiers (based on real-world external validation performance):

- **S-tier** (strongly prefer): `PRSmix`, `PRSmixPlus`, `PRSsum`; `MegaPRS` / `megaprs.auto` / `megaprs.CV`; `MultiPRS` / `UKBB-EUR.MultiPRS.CV`; `Meta-PRS` / `MetaGRS` / ensemble methods; `CT-SLEB`
- **A-tier** (prefer): `SBayesR` / `SBayesR-auto`; `LDpred2` / `LDpred2-auto` / `LDpred2.CV` / `LDpred2 (bigsnpr)`; `PRS-CSx` / `prscsx` (the multi-ancestry extension of PRS-CS with methodological advantages in diverse-ancestry contexts)
- **B-tier** (neutral): `LDpred` / `ldpred` legacy; `PRS-CS` / `PRS-CS-auto` / `PRSCS` / `prscs`; `LASSO` / penalized regression; `BOLT-LMM`; `GenoBoost`; `PolyFun-pred`; `SDPR`; `RFDiseasemetaPRS`
- **C-tier** (down-rank): `PRSice` / `PRSice-2`; `Lassosum` / `lassosum` / `lassosum2`; `snpnet` / `SnpNet`; `GWAS Hits` / `Genome-wide significant variants` / `Genome-wide significant SNPs`
- **D-tier** (strongly down-rank): `Pruning and Thresholding (P+T)` / `Clumping and Thresholding (C+T)` / `maxCT` / `SCT`; `DBSLMM` / `DBSLMM-auto`; `PLINK`; `SparSNP`

Key head-to-head comparisons:

- **PRS-CSx vs PRS-CS**: PRS-CSx should be preferred over PRS-CS when both are available for the same disease endpoint, as PRS-CSx leverages multi-ancestry GWAS data for improved cross-population transferability.
- **LDpred2 vs LDpred (legacy)**: LDpred2 should be preferred over LDpred legacy. LDpred2 is the methodological successor with improved computational framework and shrinkage estimation.
- **PRSmix/Plus vs all others**: PRSmix/Plus family models aggregate multiple component PRSs and consistently achieve the best real-world external validation performance. When available, they should be strongly preferred.
- **Genome-wide shrinkage (A/B-tier) vs sparse methods (C/D-tier)**: A genome-wide shrinkage method from a disease-focused study should be strongly preferred over a sparse method from a pan-trait framework. The performance gap between genome-wide shrinkage methods and sparse methods is large and consistent across diseases.

Method-study-design interaction:

- A genome-wide shrinkage method (PRS-CS, PRSCS, LDpred2, LDpred2-auto, PRS-CSx) from a disease-focused multi-cohort GWAS meta-analysis should be strongly preferred over a sparse method (snpnet, C+T, GWS variants) from a pan-trait single-biobank framework, because the genome-wide shrinkage method captures more of the polygenic signal and the disease-focused context ensures endpoint relevance.
- `snpnet` models from pan-trait UKB frameworks (the "813 traits" paper) typically produce very sparse scores that may not capture enough genetic variance for complex polygenic traits. Despite complete metadata, they often generalize poorly to independent cohorts (C-tier).
- `C+T` (Clumping and Thresholding) and similar simple thresholding methods have limited polygenic signal capture (D-tier). If a C+T model reports very high R2 (e.g., R2 > 0.15 for a complex polygenic trait) with unknown covariates, treat that R2 as likely inflated or non-comparable.
- `Genome-wide significant variants` or `GWAS Hits` methods using small numbers of SNPs are C-tier but can be effective when the variants were identified in large, well-powered GWAS studies focused on the target disease, especially for diseases with strong individual-locus effects (e.g., some cancers, autoimmune diseases).
- Weighted PRS summation or multi-PRS methods that combine multiple component scores can capture both polygenic background and strong individual-locus effects; they should not be penalized for method complexity.
- `PRSCS` (case-sensitive variant of PRS-CS) from multi-ancestry disease studies should be treated equivalently to `PRS-CS` in the method ranking.

Do not automatically assume:

- sparser methods are worse in ALL cases — for diseases with strong individual-locus effects, GWAS-hits methods can perform well
- newer methods are more portable
- more complex methods are more clinically credible
- rare-pathogenic or monogenic-leaning constructions are better for generic common-disease PRS deployment

Tie-break guidance:

- Use the method family tier system above as a **primary differentiator** after endpoint fidelity has been established, not merely as a weak tie-break.
- If two candidates share the same endpoint and one uses an S/A-tier method while the other uses a C/D-tier method, the S/A-tier method should be strongly preferred unless the C/D-tier candidate has overwhelmingly stronger evidence on all other dimensions.
- Within the same tier, method alone should not drive selection — use other fields (variants, performance, study design) to differentiate.
- **Within the same study family**, method tier is a weak tiebreaker — empirical performance (reported AUC, effect sizes, R²) should take precedence. If two siblings from the same publication share the same endpoint and covariates but use different methods, prefer the sibling with stronger reported discrimination, not the one with the higher method tier.
- If candidates are otherwise closely matched within the same study family, prefer the higher-tier method only when empirical evidence is indistinguishable.
- If candidates share the same publication family and endpoint, prefer the genome-wide shrinkage score over a sparse construction unless the sparse construction has a clearly larger metric advantage.
- A `snpnet` model from a pan-trait framework paper should not beat a genome-wide shrinkage model (PRS-CS, LDpred2) from a disease-focused study, even if the snpnet model has a slightly higher reported metric, because snpnet pan-trait models tend to generalize poorly to independent cohorts.
- Rare-pathogenic or clearly monogenic-leaning constructions should not automatically outrank genome-wide polygenic scores for generic common-disease risk unless the metadata show unusually strong and clean disease-level support.

## 6. ancestry_distribution

Core rule:

- `ancestry_distribution` is a compatibility and transportability field.
- Multi-ancestry appearance is not automatically an advantage.
- Models evaluated only in non-EUR ancestry contexts tend to perform materially worse in diverse external cohorts. Multi-ancestry and EUR evaluation perform similarly, while non-EUR-only evaluation is a weakness. For GWAS ancestry, multi-ancestry and EUR-only GWAS perform similarly; non-EUR-only GWAS is a weaker signal.

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
- If deployment ancestry is unspecified, a single-ancestry non-overlapping candidate (for example, EAS-only) should not outrank otherwise comparable EUR or multi-ancestry candidates merely because it has an exact label or a higher full-model metric.
- Within the same study family and same endpoint family, do not automatically prefer the European candidate if a non-European candidate has materially stronger effect sizes and no other major weakness.

## 7. publication.title / publication.journal / date_release

Core rule:

- These fields are weak context fields.
- Their main job is to identify study type, not to rank prestige.

**"Disease-focused" is defined by endpoint alignment, not publication title framing.** A model from a multi-trait comparative study or benchmarking paper is still "disease-focused" if its endpoint directly targets the query disease. Only classify a model as "non-disease-focused" when the study design does not specifically validate or optimize for the target disease endpoint. Publication title framing (e.g., "across N cancers" or "polygenic scores in five biobanks") is a weak proxy for disease focus — the actual endpoint, covariates, and training design are what matter.

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
- These framework papers are valuable for method benchmarking but their per-disease scores are not optimized for any specific disease and should not be preferred over disease-focused alternatives. Selecting framework models over available disease-focused alternatives is the single most common error pattern in PRS model selection. When you see a framework paper signature, actively search for a disease-focused alternative before selecting it.
- By contrast, disease-specific comparative papers such as "Evaluation of polygenic scoring methods in five biobanks..." that compare several model families within one exact disease endpoint should not be penalized as pan-trait framework scores when the candidate remains a direct match and the covariate field is empty or basic.

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
- Cross-cancer external evaluation is not the same as a pan-trait framework paper; if the endpoint is the exact target disease and the model was externally validated in large cohorts, do not penalize it as if it were a generic phenome sweep.
- Disease-focused publication framing is supportive but weak; it should not override materially stronger validation/performance from a broader evaluation study when endpoint fidelity remains acceptable.
- Repeated candidates from the same disease-focused study family are supportive when they remain endpoint-faithful and internally consistent.
- Do not let recency or journal prestige override phenotype fidelity, comparable performance, or transportability.
- A disease-focused GWAS meta-analysis (e.g., from a named disease consortium) should generally be preferred over a generic pan-trait framework paper from UKB, even if the meta-analysis is older or in preprint form.
- Prospective studies whose title or design centers on treatment assignment, modifiable risk-factor integration, or intervention interaction should not automatically be treated as the best standalone PRS source.
- Cost-effectiveness or screening-stratification papers can contain useful PRSs, but the paper framing itself is not proof that the score is the best standalone deployment model.

## 8. variants_number

Core rule:

- `variants_number` is a **moderate-to-strong structural signal** — among the top field-level predictors of real-world PRS performance. For most diseases, more variants correlate with better external validation performance. Successfully selected models typically have orders of magnitude more variants than poorly selected ones.
- `variants_number` should be used as a **meaningful differentiator**, especially when comparing models within the same method family or across method families.
- Variant count must always be interpreted in the context of method — a GWAS-hits model with 50 variants is structurally different from a genome-wide shrinkage model with 1M variants.

Variant count guidance:

- **>500K variants** (genome-wide shrinkage): positive signal for methods like PRS-CS, LDpred2, PRS-CSx, MegaPRS, SBayesR — these models capture broad polygenic signal.
- **100K-500K variants**: still a positive range for shrinkage methods.
- **10K-100K variants**: neutral range.
- **1K-10K variants**: weak; often from sparse penalized methods or older approaches.
- **100-1K variants**: down-rank; typically sparse P+T or limited SNP selections.
- **<100 variants** (GWAS hits): down-rank for polygenic traits; can still work for diseases with strong individual-locus effects.

Within-method variant count comparison:

- For the **same method family**, prefer the model with MORE variants. Example: PRS-CSx with 1.27M variants should beat PRS-CS with 383K variants when both target the same disease — the additional variants capture more polygenic signal.
- For **same-publication siblings** using the same method, a 1.5x or greater variant count difference favoring one sibling is a meaningful structural signal.
- When a >5x variant count gap exists between two candidates and the one with fewer variants does not have a clear structural advantage (e.g., disease-specific GWAS hits for a strong-locus disease), the higher-variant model should be preferred.

Exceptions:

- For diseases with strong individual-locus effects (e.g., some cancers, autoimmune diseases, macular degeneration), GWAS-hits models with few variants can be competitive. For a meaningful minority of diseases, the variant count signal is weak or reversed — cross-method variant count comparison is unreliable when the disease has strong individual-locus effects.
- Very high variant counts (>100K) from genome-wide shrinkage methods are expected and should not be penalized; they reflect the method's design rather than overfitting.
- Very low variant counts (single-digit to low-tens) combined with a pan-trait framework origin is a strong warning sign: the model likely does not capture enough polygenic signal for complex traits.

## 9. Disease-family policy

Apply these family-level policies only after confirming that the candidate remains a true direct match for the target disease concept.

- Endocrine and thyroid-spectrum diseases: treat hormone panels, thyroid-state biomarkers, autoantibodies, family history, and similar disease-state covariates as strong sources of metric inflation. When several direct-match candidates come from the same coherent disease-focused endocrine study family, prefer that family over legacy exact-label models whose main advantage is a biomarker-inflated or family-history-inflated full-model metric. Within one endocrine-focused family, unknown covariates are a confidence penalty, not an automatic loss to explicit biomarker-heavy or family-history-heavy packaging; endpoint fidelity, cleaner covariates, and stronger effect sizes matter more than modest full-model AUROC gaps. In same-family conflicts, explicit family history or biomarker augmentation is a stronger negative than unknown covariates. A disease-focused endocrine study family should usually outrank a portability-oriented common-disease score or legacy exact-label score when the latter's apparent edge comes mainly from larger validation, cleaner wording, or higher full-model AUROC rather than cleaner covariates or stronger disease-specific effect sizes.
- Metabolic and anthropometric diseases: a broader biology-oriented trait label can still be a direct match when `phenotyping_reported` is an exact disease diagnosis, disease phecode, or other explicit disease endpoint. Explicit diagnosis or phecode endpoints should usually beat broad weight-state, nutrition-bundle, or administrative composite phenotypes, especially when the latter come from portability-style frameworks. Prefer disease-endpoint models over broad administrative-bundle phenotypes or framework-derived time-to-event variants unless those alternatives have clearly stronger comparable PRS-only evidence. A broader biology label anchored by an explicit disease phecode should usually outrank an exact-label time-to-event framework score unless the framework score has clearly stronger comparable PRS-only evidence.
- Thromboembolic diseases: endpoints that explicitly include the target thrombotic event together with a closely related event remain direct matches if the target event is still clearly represented. When deployment ancestry is unspecified, do not let a single-ancestry exact-label candidate outrank otherwise comparable EUR or mixed-ancestry direct-match candidates solely on label exactness or one full-model metric.
- Cardiovascular and large-vessel diseases: disease-focused multi-cohort meta-analysis models with exact endpoints and only basic demographic covariates should usually be preferred over older prevalent-endpoint sparse models. In this family, `age`, `age^2`, and `sex` are basic adjustment variables, not heavy clinical leakage. Older prevalent-endpoint sparse models should not beat exact-endpoint multi-cohort families mainly on validation size, simpler packaging, or modest effect-size differences.
- Organ-site cancers and sex-specific neoplasms: cross-cancer external evaluation is not equivalent to a pan-trait framework when the candidate's endpoint is the exact target cancer and validation is large. Closely related organ-site labels within the same malignant disease family should be treated as direct matches. Fixed-horizon, age-specific absolute-risk, or screening-oriented cancer packages should not beat generic diagnosis endpoints on AUROC alone, and prospective or intervention-aware risk packages that rely on family history, treatment assignment, PSA/stage variables, UV-behavior bundles, or similar disease-adjacent exposure packaging should be down-ranked. Upstream epidemiologic or reproductive covariates used for cancer risk modeling are less problematic than family history, treatment variables, or disease-state biomarkers, but an older cross-cancer or screening-style package should not outrank a newer direct-match cancer score with age/sex/PC-only or no-covariate packaging when the newer score also has materially stronger OR/HR or R2 support.
- Musculoskeletal degenerative diseases: for site-specific osteoarthritis targets, direct site-specific osteoarthritis diagnosis or incident site-specific osteoarthritis should usually beat total-joint-replacement endpoints, broad clinical-osteoarthritis labels, or BMI/SES-packaged models unless those alternatives have clearly stronger PRS-only evidence. BMI is a meaningful mediator for osteoarthritis risk, not a reason to reward the packaged model.
- Hematologic malignancies: `acute` vs `chronic`, `lymphoblastic` vs `lymphocytic`, and `leukemia` vs `lymphoma` distinctions are material disease-identity differences, not weak subtype differences. A candidate whose fields mix these entities should be treated as endpoint-incoherent rather than as an acceptable direct match. Family-history-restricted or survivor-enriched leukemia scores should not beat a coherent exact-disease family.
- Respiratory and smoking-linked cancers/diseases: simple smoking-status adjustment can still be comparable evidence, and simple smoking/BMI adjustment can remain acceptable for generic lung-cancer deployment when the endpoint is otherwise a direct disease match. By contrast, family history plus smoking interactions, PM2.5/environment bundles, spirometry/lung-function variables, or smoker-only framing are stronger penalties. For generic asthma deployment, pediatric-only or childhood-onset asthma should usually lose to generic asthma or doctor-diagnosed asthma. For generic lung-cancer deployment, a family-history-plus-PM2.5-plus-smoking-interaction package should usually lose to a direct lung-cancer model with simpler smoking/BMI-style covariates.
- Immune-mediated and autoimmune diseases: if catalog metadata are noisy, partially contradictory, or obviously mixed with phenotype artifacts, do not let one anomalous field dominate. Reconstruct the ranking from the full evidence package: exact trait/efo alignment, disease-focused study context, covariate cleanliness, and effect-size or PRS-comparable performance support.
- Late-onset neurodegenerative diseases: familial late-onset forms remain direct matches to generic late-onset disease deployment unless a clear early-onset or monogenic mismatch is visible. Within the same study family, materially stronger effect sizes should usually outweigh slightly larger validation size or a more familiar evaluation ancestry. If two siblings share the same familial late-onset Alzheimer endpoint and the same basic `Age, sex` covariates, the materially stronger OR sibling should win even when its validation cohort is smaller.
- Sleep-disordered breathing diseases: prefer the clinically dominant subtype over a broader umbrella breathing-disorder label when the dominant-subtype model is at least as well supported on endpoint fidelity, validation, and performance evidence. When otherwise similar same-family candidates differ mainly by explicit mediator-adjustment labeling, do not let the adjusted label win by default for generic deployment.
