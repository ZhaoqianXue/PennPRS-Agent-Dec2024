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

