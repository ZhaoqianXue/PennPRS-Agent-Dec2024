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

