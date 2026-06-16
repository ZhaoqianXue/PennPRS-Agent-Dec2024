# PGS Evidence Appraisal

Empirical patterns for appraising a candidate PGS Catalog model's record-visible metadata and predicting how well it will perform in **external validation**. Every pattern is advisory — an overridable empirical regularity, never a hard filter or numeric rule. Weigh patterns against each other case-by-case.

Each candidate is one self-contained representative record (the most informative evaluation per candidate is selected upstream). Compare candidates against each other; there is no record-selection step to perform here.

The numbered sections below correspond one-to-one to the seven sections of the single-record PGS schema, so a finding can always be traced to the schema field it came from. The unnumbered **Cross-cutting appraisal principles** layer holds the reasoning that spans fields or candidates and therefore belongs to no single field.

## Contents

- [Cross-cutting appraisal principles](#cross-cutting-appraisal-principles)
- [1. predicted_trait — endpoint fidelity](#1-predicted_trait)
- [2. performance_metrics — metrics, covariates, evaluation sample](#2-performance_metrics)
- [3. source_of_variant_associations_gwas](#3-source_of_variant_associations_gwas)
- [4. score_development_training](#4-score_development_training)
- [5. development_method](#5-development_method)
- [6. variants](#6-variants)
- [7. pgs_source — publication context](#7-pgs_source)

---

## Cross-cutting appraisal principles

Empirical patterns that span fields or candidates and therefore map to no single schema field (sections 1–7). The weighing posture and the rough field-importance order live in the skill's procedure (SKILL.md); this layer holds the field- and candidate-spanning knowledge that the procedure draws on.

**Comparability:**

- Partial mismatches lower confidence but do not invalidate a candidate unless the mismatch is explicit.
- Missing evidence lowers confidence in a candidate.
- No single attractive field reliably compensates for weaknesses across other dimensions.

**Study archetype (the single most important prior).** A model from a disease-focused multi-cohort study consistently outperforms a pan-trait / portability framework score in external validation, **unless** the framework score has clearly stronger endpoint **and** metric evidence. Choosing a framework score over an available disease-focused alternative is the single most common and costly error pattern in PRS selection; large evaluation support alone never justifies it. The framework penalty is proportional to method quality (a framework using genome-wide Bayesian shrinkage earns a lighter penalty than one using sparse/thresholding methods). Detection cues live in the field sections: publication-title signatures in `pgs_source` (§7), sparse single-biobank development profiles in `source_of_variant_associations_gwas` (§3) and `development_method` (§5).

**Cross-candidate patterns:**

- When several endpoint-faithful candidates from the same disease-focused study family form a coherent cluster, that cluster is strong evidence and typically outperforms a lone exact-label or lone high-AUROC candidate whose apparent edge comes mainly from recency, exact wording, or a single full-model metric.
- Within the same publication family and the same exact endpoint, modest differences in evaluation size, wording, or study framing are weak signals; the candidate with materially stronger OR/HR, cleaner PRS-only metrics, or cleaner covariates is the stronger choice. Among same-endpoint near-clones with effectively identical endpoint and covariates, a stronger regularized candidate with better AUROC/OR evidence beats a weaker sparse one.
- An older exact-label portability score, sparse UKB score, or generic framework score that appears to beat a newer disease-focused or multi-cohort direct-match score **solely** because it reports an explicit PRS-only metric, has a familiar method name, or has a much larger evaluation sample is typically a selection artifact, not genuine superiority.
- A cleaner-but-visibly-weaker candidate is not automatically preferable to a strong direct-endpoint candidate with less perfectly separated metric reporting. PRS-only metrics are cleaner when available, but full-model AUROC/C-index, OR/HR, evaluation scale, endpoint alignment, and method context remain meaningful predictive evidence when the visible covariates are conventional or similarly packaged across candidates. Do not turn metric cleanliness into an implicit veto.

---

## 1. predicted_trait

Fields: `predicted_trait.trait_reported`, `predicted_trait.trait_efo[]`. Endpoint fidelity is read together with `performance_metrics.phenotyping_reported` (the endpoint definition of the evaluation, which physically lives in §2).

- `phenotyping_reported` is the primary endpoint-fidelity field. `trait_reported` and `trait_efo` are concept-alignment fields, not final deployment proof. Endpoint fidelity matters more than surface label similarity.

Positive signals (stronger real-world performance):

- direct clinical disease endpoint; generic case-control or incident-plus-prevalent endpoint when the target is a generic disease concept
- diagnostic-code or phecode-based endpoints that directly map to the same disease concept
- disease-adjacent or broader-biology labels when `phenotyping_reported` is still a direct diagnosis endpoint for the target (e.g., an `adiposity` label with an obesity phecode endpoint)
- combined labels that explicitly contain the target disease; near-synonymous labels with richer supporting evidence over exact-but-vague labels
- exact endpoints with much stronger evaluation and materially better discrimination, even when self-reported
- clinically dominant subtypes when the target label is a broad organ-site cancer or umbrella term and the subtype has much stronger support
- familial late-onset forms when the target is the same late-onset disease and no early-onset or monogenic enrichment is shown
- explicit diagnosis/phecode endpoints over broad weight-state, nutrition-bundle, or administrative composite phenotypes

MTAG and multi-trait analysis:

- MTAG (Multi-Trait Analysis of GWAS) is a legitimate power-boosting technique that combines GWAS summary statistics across genetically correlated traits to increase effective sample size. MTAG is **not** a negative endpoint signal.
- Candidates with `(MTAG)` or `Multi-trait` in `trait_reported` that still target the same disease are enhanced versions of the base endpoint, not endpoint mismatches. When choosing between an MTAG variant and a non-MTAG variant of the same disease from the same publication family, the MTAG variant is mildly preferred (e.g., `Dilated cardiomyopathy (MTAG)` over `Dilated cardiomyopathy`).

Clinically dominant subtype equivalences (semantically equivalent, not subtype mismatch, when the target is a broad umbrella/organ-site term):

- `obstructive sleep apnea` is the dominant form of `sleep apnea` (~85% of clinical cases)
- `endometrial carcinoma` is the dominant subtype of `uterine carcinoma` (~90%)
- `renal cell carcinoma` is the dominant subtype of `kidney cancer` (~90%)
- `Graves' disease` is the dominant autoimmune form of clinical hyperthyroidism
- `adenocarcinoma` is the dominant subtype for many organ-site cancers
- When a dominant-subtype candidate has materially stronger study design, evaluation, or performance than the exact-label alternative, the dominant subtype is the stronger choice. The dominant-subtype mismatch is not a meaningful penalty.

Warning signals (weaker real-world performance):

- `phenotyping_reported` is time-to-event, unless the candidate is from a major disease-focused multi-cohort study and the alternative is merely a portability or pan-trait framework score
- `phenotyping_reported` is incident-only while the target is generic disease risk, unless from a dedicated disease GWAS meta-analysis with much stronger support than the alternative
- `phenotyping_reported` is horizon-specific (e.g., 5-year risk), future-risk prediction, or an age/horizon-conditioned absolute-risk package rather than direct disease status
- `phenotyping_reported` is subtype-only (unless the clinically dominant subtype), a proxy phenotype, treatment-induced/therapy-specific, or a broad administrative phenotype bundle
- pediatric-only, childhood-onset, smoker-only, or otherwise restricted subtype endpoints when the target is generic — large evaluation size does not erase the mismatch
- `personal history of`, `history of`, survivorship, or post-diagnosis survivor phenotypes — these are indirect or survivor-enriched endpoints, weaker than an active diagnosis endpoint for a generic target
- when `trait_reported`, `trait_efo`, and `phenotyping_reported` point to clearly different diseases, phases, or malignancy subtypes, the candidate is metadata-contaminated or endpoint-incoherent — one superficially exact field does not reliably outperform a coherent cluster of direct-match candidates

Endpoint robustness when candidates are otherwise similar:

- Incident-only, time-to-event, and self-reported exact disease endpoints are all acceptable; none is an automatic winner. Self-reported exact disease does not automatically lose to a clinically ascertained alternative if it has much stronger evaluation support and materially better reported discrimination.
- Diagnostic-code and phecode instantiations do not automatically lose to literal disease-string endpoints.
- Exact trait match provides only a marginal advantage over partial/subtype match. An exact-label model is not the stronger choice over a structurally superior model (stronger method, more variants, stronger study design) solely because of label exactness.
- Spelling noise, minor wording, anatomical-qualifier, tissue-descriptor, or formatting variants are not meaningful mismatches when `trait_reported`, `trait_efo`, and `phenotyping_reported` all point to the same disease entity.
- Fixed-horizon, age-specific absolute-risk, or screening-stratification formulations are deployment packaging, not stronger phenotype evidence; they do not reliably outperform a direct diagnosis/incidence/case-control endpoint solely because of larger evaluation or higher `full_model_auroc`.
- Composite endpoints remain valid direct matches when the target disease is explicitly present and the added component is a closely related manifestation/subtype/companion diagnosis. Case-control endpoints contrasting the target against a benign/precursor/differential condition remain direct matches because the disease arm is still the target. Familial forms remain direct matches when the disease concept and age-of-onset class are unchanged and no monogenic/syndromic construct is explicit.
- When phenotype fields are noisy, partially contradictory, or likely contaminated by catalog artifacts, rank on the most coherent disease-level evidence package across `trait_reported`, `trait_efo`, `phenotyping_reported`, publication context, effect sizes, performance metrics, and covariates rather than letting one anomalous field dominate.

---

## 2. performance_metrics

Fields: `performance_metrics.{phenotyping_reported, covariates, metrics{pgs_only_r2, pgs_only_auroc, full_model_auroc, c_index, effect_sizes[]}, evaluation_sample{sample_numbers{individuals, cases, controls}, ancestry, cohorts[]}}`. Each candidate exposes one metrics block; there is no across-record mixing to resolve. (`phenotyping_reported`'s endpoint-fidelity rules are in §1.)

### Metrics and the usable-axis ordering

- `pgs_only_r2` and `pgs_only_auroc` are PRS-comparable metrics — the discrimination of the score with covariates regressed out. They are the most reliable performance indicators when present.
- `full_model_auroc` and `c_index` are full-model metrics (score **plus** covariates) unless the record explicitly states otherwise. They are real signal but covariate-inflated, so they rank lowest among usable axes and are not the primary cross-candidate ranking metric: real-world PRS performance is measured without covariate-boosted full-model discrimination.
- Usable-axis strength, strongest to weakest: PRS-only R²/AUROC > per-SD OR/HR effect sizes > `c_index` > `full_model_auroc` > none. A candidate with only `full_model_auroc` is not treated as if that value were a PRS-only metric.
- `pgs_only_r2` (PRS-only R²) is among the strongest field-level predictors of real-world PRS performance. Candidates reporting PRS-only R² are more informative than those with only full-model metrics.
- Higher reported metrics are supportive, not decisive. Missing metrics lower confidence but do not automatically disqualify a candidate: a disease-focused candidate with only effect sizes (OR/HR) but no `pgs_only_*` can still be the best choice if its study design, cohort context, and method are stronger than a framework score with explicit but modest PRS-comparable metrics.
- Metrics are informative for separating candidates only after endpoint and covariate comparability are acceptable. Small metric gaps are not meaningful differentiators when endpoint or covariate design differs.
- `c_index` (concordance) typically accompanies survival / time-to-event models reporting HR. Read it like `full_model_auroc` (full-model unless stated PGS-only) — informative when the covariate set is only demographic/basic, heavily discounted when it rests on biomarker or treatment-aware adjustment.
- There is no separate incremental-AUROC field. When both `full_model_auroc` and `pgs_only_auroc` are present, the increment is `full_model_auroc − pgs_only_auroc`; a large `full_model_auroc` with a small implied increment (and modest `pgs_only_r2`) indicates mostly covariate-driven discrimination, not PRS strength.

Effect sizes as PRS-quality signals (`effect_sizes[]`, typically `name_short` ∈ {OR, HR}, per SD, with `estimate` and a confidence interval `ci_lower`/`ci_upper`):

- When a candidate reports only `effect_sizes` and no AUROC/R², use the per-SD `estimate` magnitude as a supportive discrimination signal rather than treating the candidate as having no evidence.
- OR per SD is a strong predictor of real-world PRS performance — stronger than reported AUC. HR per SD is also meaningful.
- Magnitude guidelines on `estimate`: OR ≥ 1.5 or HR ≥ 1.5 per SD indicates strong PRS discriminative power; OR 1.3–1.5 or HR 1.2–1.5 is moderate; OR < 1.3 or HR < 1.2 suggests weak PRS signal.
- A wide confidence interval (`ci_upper − ci_lower` large relative to `estimate`) means the effect-size point estimate is imprecise — weight it less than a tight interval around the same estimate.
- A strong per-SD OR/HR (≥ 1.5) from a well-designed study is meaningful evidence of PRS discriminative power and carries more weight than evaluation sample size. Effect sizes do not override clearly stronger AUROC/R² evidence from a comparably designed study, but they prevent automatic loss to a framework score whose only advantage is metric availability. A recent disease-focused multi-ancestry score with strong OR/HR and clean endpoint alignment can outperform an older exact-label score even when it reports only effect sizes.

Positive performance signals: reported performance from candidates with comparable endpoints; explicit PRS-only metrics; discrimination reported with basic/comparable covariates; `full_model_auroc`/`c_index` from only demographic/basic adjustment; performance that does not rely on downstream clinical disease variables, family history, or treatment context.

Warning performance signals: very high AUROC/R² on a weaker endpoint, in a time-to-event / broad-EHR / internally optimized single-biobank setting, or as a clear outlier relative to the rest of the direct-match set; only a `full_model_auroc` reported and treated as if PRS-only; performance depending on heavy clinical covariates (heavy covariates **and** no PRS-only metric is the worst-performing combination), on disease-adjacent clinical variables, or on an age-specific absolute-risk / horizon-conditioned risk package; within the same endpoint family, the only visible AUROC coming from the more covariate-heavy candidate.

Metric-availability bias: a candidate is not automatically stronger solely because it reports an explicit PRS-comparable metric when a competitor from a much stronger study design reports only effect sizes or full-model metrics with cleaner covariates. Compare the strength of available evidence rather than rewarding metric type.

### Covariates

- `covariates` functions as a comparability and optimism field. The heavier the covariate set, the larger the gap between reported full-model discrimination and actual standalone PRS performance.
- `age`, `age^2`, `sex`, ancestry PCs, batch, and genotyping array are basic covariates and usually remain comparable across studies; basic demographic adjustment is **not** heavy clinical leakage.
- Standard epidemiological covariates that are part of routine disease-risk modeling (e.g., smoking for lung cancer/COPD, BMI for cardiometabolic disease, alcohol for liver disease) are **mild** comparability adjustments, not heavy clinical leakage. They become concerning only when bundled with multiple additional clinical predictors, family history, or near-outcome biomarkers.
- Covariate penalties apply proportionally: a single standard epidemiological covariate is a weaker concern than a bundle of clinical predictors or near-outcome biomarkers.
- Heavy / non-comparable covariates: family history, treatment-aware terms, disease biomarkers, strong mediator adjustment, and absolute-risk calibration / age-specific risk wrappers make the reported metric less comparable to a PRS-only or PRS-light setting. These are not less concerning simply because they are explicitly disclosed.
- Named clinical risk calculators and packaging are strong negative evidence for standalone PRS quality: horizon-conditioned packaging, age-specific absolute-risk packaging, and named calculators (e.g., `CHARGE-AF`, Framingham, QRISK, pooled cohort equations, `5-year risk`, `absolute risk`, `screening risk`) are deployment packages, not cleaner PRS evidence. A candidate using such packaging is typically outperformed in external validation by a direct disease model with only demographic/PC-style covariates, even when the packaged model has much larger evaluation support. `Phenotype risk score` / broad-EHR phenotype packaging is severe comparability leakage. Bundled non-genetic packaging (named calculators, family-history packages, PM2.5/environmental bundles, smoking interaction terms) is a stronger penalty than ordinary demographic or simple epidemiologic adjustment.
- A `full_model_auroc` boosted by biomarkers, family history, or a clinical calculator is a heavily discounted advantage. A high `full_model_auroc` from only age/sex/PCs or standard exposures is informative but still secondary to endpoint fidelity.
- `covariates = 0`, `None`, or an explicitly empty field is usually no added non-genetic covariates, not hidden clinical augmentation.
- Unknown covariates lower confidence but do not automatically help or hurt. When one candidate has unknown covariates and another explicitly uses family history, treatment variables, disease biomarkers, or risk-wrapper adjustment, the explicit clinical augmentation is the stronger comparability concern.

Near-outcome biomarker covariates: when covariates include disease-specific clinical lab measurements or biomarkers tightly coupled to the outcome, the reported `full_model_auroc`/R² is severely inflated and essentially non-comparable to demographic-only models. When `full_model_auroc` is very high (e.g., > 0.80) and covariates include multiple clinical predictors or near-outcome biomarkers, that value provides essentially no evidence about PRS discriminative quality; a candidate with lower full-model AUROC but much cleaner covariates is more informative. The PRS-only metrics or effect sizes that isolate the PRS contribution are then the only informative performance evidence.

### Fallback when no PRS-only metric is available

When no candidate in the pool reports a PRS-only metric (`pgs_only_r2` / `pgs_only_auroc`), AUROC cannot differentiate candidates. Evaluation sample size and publication narrative are weak and unreliable as the primary differentiator. The following fallback ordering is more reliable:

1. **Methodological properties** (§5 Principle A / Principle B) — the strongest structural signal.
2. **Variant count and effect-size magnitude** — higher variant count within the same method family is positive; a strong per-SD OR (> 1.5) or HR (> 1.5) signals meaningful PRS discriminative power even without AUROC.
3. **Small `full_model_auroc` differences** between candidates with similar covariates are essentially noise — a difference under ~0.05 is not a meaningful differentiator. Structural differences are more informative.

When both candidates report only `full_model_auroc` (no PRS-only metrics), their values are essentially incomparable for ranking — especially with different covariate sets — and structural signals (method, variant count, study design) are more reliable differentiators.

### Heritability sanity check (external ceiling on PRS-only R²)

Trait heritability is **not** part of the candidate record — it is external evidence (e.g., a local h² estimate for the target trait) used only as a ceiling and sanity check on PRS-only metrics, never a ranking axis on its own.

- A clearly PRS-comparable R² (`pgs_only_r2`) can be compared against the best available heritability estimate. When the visible PRS-comparable R² approaches or exceeds trait heritability, suspect metric misuse, scale mismatch, or non-comparable reporting.
- When `full_model_auroc` is very high but the implied increment is small and `pgs_only_r2` is modest relative to heritability, the high AUROC is mainly covariate-driven rather than PRS-driven.
- When a reported R² is very high (e.g., > 0.15) and the method is a clumping-and-thresholding or pruning-and-thresholding pipeline with unknown covariates, that R² is suspect: simple thresholding pipelines rarely capture enough genetic variance to explain > 15% of trait variance for complex diseases.
- Do not promote a candidate on heritability grounds and do not discard a direct, well-supported candidate solely because a heritability estimate is missing.

### Evaluation sample (`evaluation_sample`)

- Evaluation sample size (`sample_numbers.individuals`) is a **very weak** signal for real-world PRS performance — a last-resort tie-break, not a meaningful differentiator. Larger evaluation N does not reliably predict better external performance, and selecting primarily on evaluation size rarely yields the best-performing model.
- The case/control split (`sample_numbers.cases`/`controls`) is a study-design signal, not a power signal: a reasonable case count matters more than a large `individuals` count dominated by controls. A very small `cases` count makes the reported metrics less stable regardless of total `individuals`.
- Evaluation ancestry (`evaluation_sample.ancestry`) is often more informative than the broad GWAS-ancestry label (§3). PGS portability is governed by how well the **validation ancestry matches the target population**, not by a European default. Multi-ancestry evaluation — especially from a disease-focused multi-cohort study — is the strongest portability evidence. Single-ancestry evaluation is narrower evidence of broad-cohort performance: a high headline metric demonstrated in **only one** ancestry (European-only **or** non-European-only) is a narrower guarantee of broad performance than a modestly-lower metric demonstrated across diverse ancestries. Do **not** treat non-European-only evaluation as a blanket weakness — a validation in any single ancestry is relevant, robust evidence for deployments that include that ancestry, and for a broad/diverse target a single non-European validation is no weaker per se than a single European one. When deployment ancestry is genuinely unspecified, ancestry lowers confidence rather than supporting over-ranking; do not let a single-cohort headline metric override demonstrated cross-ancestry robustness.
- Evaluation cohorts (`evaluation_sample.cohorts[]`): consistent performance across several independent evaluation cohorts is a robustness signal stronger than the highest single-cohort metric.

Warning signals (large evaluation N indicating weaker, not stronger, real-world performance): a large evaluation sample used to justify a weaker phenotype match or to rescue a non-comparable AUROC; a large evaluation sample from a pan-trait single-biobank framework while a smaller but well-powered disease-focused cohort has cleaner endpoint evidence; a large evaluation sample as the primary justification for selection. Evaluation size is informative as a tie-break only when all other signals are genuinely indistinguishable, and even then only minimally and only after phenotype alignment is acceptable. Modest evaluation-size differences within the same publication family are essentially meaningless.

---

## 3. source_of_variant_associations_gwas

Fields: `source_of_variant_associations_gwas.{sample_numbers{individuals, cases, controls}, ancestry, cohorts[]}` — the discovery GWAS behind the score. Ancestry may list several broad categories when the discovery GWAS is multi-ancestry.

- Mainly a transportability field. The discovery-GWAS sample size has negligible predictive value on its own — larger GWAS samples do **not** by themselves predict better real-world performance. Study archetype (disease-focused vs framework, see the cross-cutting layer) matters far more than raw GWAS size.
- GWAS ancestry: multi-ancestry and European-only discovery GWAS perform similarly; a non-European-only GWAS is a weaker signal. A more diverse-looking ancestry string is not automatically an advantage.
- GWAS cohort breadth (`cohorts[]`): a disease-focused multi-cohort discovery study with many contributing biobanks (e.g., > 5 cohorts including All of Us, BioMe, FinnGen, UKB, MVP) is strong evidence of external validity and is the stronger choice over single-biobank framework scores.

Framework vs disease-focused development (detection of the cross-cutting archetype prior):

- Framework models underperform disease-focused models systematically — they generalize less well to independent external cohorts. Identify candidates coming from pan-trait, pan-phenome, or portability-style high-throughput frameworks: the title signatures are listed in §7, and the development profile is characteristic — e.g., L1-penalized sparse pan-trait UKB scores typically have low variant counts, UKB as the sole discovery/development cohort, and standardized covariates, and generalize poorly despite complete metadata.
- When a disease-focused alternative exists with acceptable endpoint fidelity, the framework model is not the stronger choice unless it has clearly superior endpoint fidelity **and** method **and** metric evidence — not just one. The framework penalty is proportional to method quality (lighter for genome-wide Bayesian shrinkage / multi-score aggregation / cross-ancestry extensions than for sparse/thresholding methods).
- A single-biobank portability sweep does not reliably outperform a disease-focused multi-cohort discovery study unless it also has cleaner endpoint evidence and comparable metrics.

---

## 4. score_development_training

Fields: `score_development_training.{sample_numbers{individuals, cases, controls}, ancestry}` — the sample the score weights were fit/tuned on.

- `score_development_training` sample size has negligible predictive value: larger training samples do **not** predict better real-world performance, and training size is not a meaningful differentiator. Study archetype matters more than raw training size.
- Training ancestry is a compatibility/transportability field. A model whose development is essentially a single-biobank pan-trait workflow (large training sample as the main attraction, limited disease-specific evidence) is a warning sign; pair training-ancestry reasoning with the discovery-GWAS and evaluation-ancestry signals (§3, §2) rather than reading it in isolation.
- A coherent disease-focused multi-cohort study family whose candidates share endpoint, ancestry, and evaluation context is corroborating evidence (see the cross-cutting cluster pattern), and can outperform a lone portability or legacy exact-label score even with unknown covariates when the competitor's edge comes from explicit clinical augmentation or risk-wrapper packaging.

---

## 5. development_method

Field: `development_method.method_name`.

- `method_name` is a structural signal that helps separate candidates once endpoint fidelity and performance evidence are already comparable. Method alone does not override empirical evidence from the same disease family: within the same publication family, when two candidates share endpoint and covariates but use different methods, the one with stronger reported discrimination (higher AUROC, stronger effect sizes) is the stronger choice — not the one with the nominally stronger method.
- Method modernity alone is not a quality proxy.
- For diseases with strong individual-locus effects (e.g., Hodgkin lymphoma, testicular cancer, bladder cancer, macular degeneration), sparse or variant-selection methods can outperform genome-wide shrinkage because the genetic architecture is concentrated in a few major loci.

Two method distinctions with consistent empirical support:

- **Principle A — multi-score aggregation outperforms single-score construction.** Methods that aggregate, ensemble, or optimally combine multiple component scores capture complementary genetic signal and achieve stronger external validation. Identification clues: names/descriptions suggesting combination, mixing, weighted aggregation, meta-scoring, or ensembling.
- **Principle B — genome-wide shrinkage outperforms sparse/thresholding for polygenic traits.** Genome-wide continuous-shrinkage methods (modelling all/most variants with continuous regularization) capture distributed polygenic signal more effectively than sparse selection / thresholding (C+T, P+T, L1-penalized sparse) for most complex polygenic diseases. This is a structural signal, not an absolute rule — the gap varies by disease and GWAS quality.

Method–study-design interaction:

- A genome-wide shrinkage method from a disease-focused multi-cohort GWAS meta-analysis is a positive signal over a sparse method from a pan-trait single-biobank framework. L1-penalized regression from pan-trait single-biobank frameworks typically yields very sparse scores that generalize poorly.
- Methods using only genome-wide-significant variants (small SNP sets) can be effective when the variants were identified in large, well-powered disease-focused GWAS, especially for diseases with strong individual-locus effects.
- The full pipeline matters, not just the base variant-selection step: a method combining thresholding with additional shrinkage, empirical-Bayes estimation, or cross-ancestry transfer is stronger than simple thresholding alone. Variant spellings/capitalizations/abbreviations of the same underlying method are equivalent.

Common misconceptions: sparser methods are not worse in all cases; newer methods are not inherently more portable; more complex methods are not inherently more clinically credible.

---

## 6. variants

Field: `variants.variants_number`.

- A moderate structural signal. For most diseases, more variants correlate with better external validation performance **within the same method family**.
- Variant count is most informative for comparing candidates within the same method family. Cross-method variant-count comparison (e.g., genome-wide shrinkage vs GWAS-hits) just reflects the method distinction from §5 and is not an independent signal.
- For same-publication siblings using the same method, a ≥ 1.5× variant-count difference is a meaningful structural signal; the candidate with more variants is generally stronger.

Exceptions:

- For diseases with strong individual-locus effects (some cancers, autoimmune diseases, macular degeneration), GWAS-hits models with few variants can be competitive; for a meaningful minority of diseases the variant-count signal is weak or reversed.
- Very low variant counts (single-digit to low-tens) combined with a pan-trait framework origin is a warning sign — the model likely does not capture enough polygenic signal for complex traits.

---

## 7. pgs_source

Fields: `pgs_source.{publication_title, publication_journal, date_release}`.

- These are weak context fields. Their main informative role is identifying study type, not ranking prestige.
- **"Disease-focused" is defined by endpoint alignment, not title framing.** A model from a multi-trait comparative or benchmarking paper is still disease-focused if its endpoint directly targets the query disease. Classify a model as non-disease-focused only when the study design does not specifically validate or optimize for the target endpoint. Title framing (e.g., "across N cancers", "polygenic scores in five biobanks") is a weak proxy — the actual endpoint, covariates, and development design are what matter.
- `publication_title` helps detect study type: disease-specific, cross-disease, cross-cancer, multitrait/pan-phenome, portability, risk-factor integration, related-trait rather than exact-disease, or exposure/lifestyle/treatment-centered (where the PRS may be auxiliary).

Framework-paper title signatures (the publication-side detection of the cross-cutting archetype prior):

- "Significant sparse polygenic risk scores across 813 traits in UK Biobank" = L1-penalized sparse pan-trait UKB framework (frequently does not generalize well)
- "Portability of 245 polygenic scores when derived from the UK Biobank" = UKB portability framework
- "ExPRSweb ..." = exposure-PRS framework
- "Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts" = Global Biobank meta-analysis framework
- Any title emphasizing "across N traits/phenomes" where N is large. These framework papers are valuable for method benchmarking but their per-disease scores are not optimized for any specific disease and do not reliably outperform disease-focused alternatives. By contrast, disease-specific comparative papers (e.g., "Evaluation of polygenic scoring methods in five biobanks ...") are not pan-trait framework scores when the candidate remains a direct endpoint match with empty/basic covariates; cross-cancer external evaluation is not a pan-trait framework when the candidate's endpoint is the exact target cancer and evaluation is large.

Factors that do **not** reliably predict performance: a newer `date_release`; a higher-profile `publication_journal`; a broader-sounding `publication_title`; portability / pan-phenome / global-biobank framing when disease-specific evidence is weaker. Recency or journal prestige does not override phenotype fidelity, comparable performance, or transportability. A disease-focused GWAS meta-analysis from a named disease consortium is generally the stronger choice over a generic pan-trait framework paper, even if older or in preprint.
