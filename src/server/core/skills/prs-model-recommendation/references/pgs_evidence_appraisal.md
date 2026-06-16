# PGS Evidence Appraisal

Field-level appraisal patterns for reading one candidate PGS Catalog record and judging same-trait
validation support. Sections follow the current single-record schema order. Each pattern is
an empirical regularity, weighed against the full visible record rather than applied as a fixed rule.

## Contents

- [1. id](#1-id)
- [2. predicted_trait](#2-predicted_trait)
- [3. development_method](#3-development_method)
- [4. variants](#4-variants)
- [5. pgs_source](#5-pgs_source)
- [6. source_of_variant_associations_gwas](#6-source_of_variant_associations_gwas)
- [7. score_development_training](#7-score_development_training)
- [8. performance_metrics](#8-performance_metrics)

---

## 1. id

Field: `id`. The identifier is an address for the visible record, not evidence of quality. It supports
traceability, output validation, and duplicate detection. Ranking should come from the record fields
below, not familiarity with the identifier or its lexical order.

---

## 2. predicted_trait

Fields: `predicted_trait.trait_reported`, `predicted_trait.trait_efo[]`, read with each
`performance_metrics[].phenotyping_reported`.

- `phenotyping_reported` is the endpoint-fidelity field for evaluation; `trait_reported` and
  `trait_efo` establish concept alignment. Endpoint fidelity outweighs surface-label similarity.
- Stronger endpoints are direct clinical disease, case-control, incident-plus-prevalent,
  diagnostic-code, or phecode endpoints mapping to the target concept. Combined or familial labels can
  remain strong when they preserve the same disease and age-of-onset class.
- Weaker endpoints include horizon-specific or absolute-risk packaging, treatment-induced or survivor
  phenotypes, restricted subtypes for a generic target, and broad administrative bundles. Large
  evaluation samples leave these endpoint mismatches in place.
- Multi-trait analyses can be legitimate power boosters when the evaluated endpoint remains the target.
  Spelling, formatting, or anatomical-qualifier variants are minor when the record fields agree on the
  same disease-level concept.

---

## 3. development_method

Field: `development_method.method_name`. Method is a structural signal once endpoint and performance
evidence are comparable.

- Multi-score aggregation, ensembling, meta-scoring, or optimally weighted component scores often capture
  complementary signal and validate more strongly than single-score construction.
- Genome-wide shrinkage and continuous regularization across many variants generally capture distributed
  polygenic signal better than sparse selection or plain thresholding for complex traits.
- Sparse or variant-selected scores can be competitive when the genetic architecture is concentrated and
  the variants came from a well-powered disease-focused study.
- Method labels are most useful with study context: a shrinkage or aggregation method from a
  disease-focused multi-cohort effort is stronger evidence than a sparse score from a single-source
  pan-trait framework. Within one publication family, same-endpoint empirical performance can outweigh
  nominal method modernity.

---

## 4. variants

Field: `variants.variants_number`. Variant count is a moderate structural signal, most informative
within a method family.

- Among same-method, same-endpoint siblings, a materially larger variant set usually favours the broader
  score because it captures more distributed signal.
- Across methods, variant count mostly restates the method distinction: genome-wide shrinkage naturally
  uses many variants, while sparse or genome-wide-significant approaches use fewer.
- Very low counts together with a pan-trait framework origin warn of limited polygenic capture for
  complex traits. Low counts remain plausible for concentrated architectures when the rest of the record
  supports that interpretation.

---

## 5. pgs_source

Fields: `pgs_source.publication_title`, `pgs_source.publication_journal`,
`pgs_source.date_release`. These are weak context fields whose main value is identifying study type.

- Disease-focused status is defined by endpoint alignment and validation design, not title wording
  alone. A comparative paper can still provide disease-focused evidence when the candidate is validated
  on the target endpoint.
- Framework-origin cues include large pan-phenome sweeps, portability papers built from one source
  cohort, exposure-score resources, global cross-biobank surveys, and broad "across many traits" framing.
  These papers are useful context but their per-disease scores are often less optimized for a specific
  endpoint than disease-focused alternatives.
- Recency, journal prestige, broad title framing, and a polished publication narrative are last-order
  context. They yield to endpoint fidelity, comparable performance evidence, transportability, and study
  design.

---

## 6. source_of_variant_associations_gwas

Fields: `source_of_variant_associations_gwas[]`, each `{sample_numbers, ancestry, cohorts}`. This is a
transportability and study-archetype field.

- Discovery-GWAS scale has limited standalone ranking value. Study design, endpoint match, and cohort
  breadth usually matter more than raw discovery size.
- Disease-focused multi-cohort discovery evidence is a strong validation-support signal. A sparse
  single-source pan-trait development source is weaker even with complete metadata.
- Ancestry breadth should be read with evaluation ancestry and the supplied `target_ancestry`.
  Multi-ancestry and European-only discovery can both be credible depending on the validation setting; a
  diverse-looking ancestry string is not, by itself, proof of portability.

---

## 7. score_development_training

Fields: `score_development_training[]`, each `{sample_numbers, ancestry}`. This field describes where
the score weights were fit or tuned.

- Training size alone has little predictive value. A very large single-biobank training sample is weak
  evidence when disease-specific validation is thin.
- Training ancestry is a compatibility signal read with discovery and evaluation ancestry, not in
  isolation. The strongest transportability evidence comes from coherent support across development,
  discovery, and evaluation records relative to `target_ancestry`.
- A coherent study family sharing endpoint, ancestry context, and evaluation design can corroborate a
  candidate even when some headline metrics are absent.

---

## 8. performance_metrics

Fields: `performance_metrics[]`, each `{performance_id, phenotyping_reported, covariates,
effect_sizes[], classification_metrics[], other_metrics[], evaluation_samples[]}`. Integrate across all
performance records before comparing candidates.

**Metric type and comparability.** Classify each metric from its `metric_name`, estimate, interval, and
the record's `covariates`. Covariate-free AUROC/R² is the cleanest single discrimination evidence when
endpoint and evaluation context match. Per-SD OR/HR in `effect_sizes[]` is strong standalone evidence,
especially when estimates are large and intervals are tight. C-index and covariate-adjusted AUROC are
usable but less comparable across unrelated studies. Small numeric gaps across different endpoints or
covariate designs are weak differentiators.

**Covariates.** Age, sex, ancestry principal components, batch, and array are basic adjustments. Routine
epidemiological variables are mild. Family history, treatment terms, disease biomarkers, near-outcome
labs, strong mediators, and absolute-risk calculators can make full-model discrimination reflect those
inputs rather than standalone PRS quality. A very high full-model AUROC with heavy covariates is mainly
clinical-package evidence; effect sizes and covariate-free metrics then carry the PRS comparison.
Empty, `None`, or `0` covariates usually indicate no added non-genetic adjustment.

**Evaluation samples.** Evaluation ancestry, cohort breadth, and case count matter more than total
individuals alone. A reasonable case count is more informative than a very large control-dominated
sample. Multi-cohort evaluation with ancestry relevant to `target_ancestry` is stronger portability
evidence than a single flattering cohort. Consistency across independent records beats the highest
single metric.

**Heritability context.** Trait-level heritability supplied with the input is an external ceiling and
sanity check for covariate-free R²-like metrics. It is not a ranking axis by itself. Apparent R² values
near or beyond the trait ceiling suggest scale mismatch, metric misuse, or covariate-driven reporting.
