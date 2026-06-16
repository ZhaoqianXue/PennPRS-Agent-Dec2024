---
name: prs-model-recommendation
description: Appraises and ranks candidate polygenic-score (PGS) Catalog models for a single fixed target trait using only each model's record-visible metadata (trait labels, performance metrics, covariates, development and evaluation samples, method, variant count, publication). Use when choosing the best same-trait PGS among several candidates for a fixed trait, when verifying a proposed PGS against quality criteria, or whenever same-trait PGS Catalog records are compared on intrinsic predictive quality. Trait-agnostic; advisory.
---

# PGS Model Recommendation (within-trait)

Appraise candidate PGS Catalog models the way a statistical geneticist judges which score will generalise best in **external validation**, then rank them and recommend the strongest. The target trait is fixed. Reason only from each candidate's record-visible metadata; do not invoke outside knowledge about specific diseases.

Each candidate arrives as **one self-contained representative record plus, when available, a compact validation-ancestry profile**. The primary `performance_metrics` section is still the single most informative evaluation selected upstream; non-null `evaluation_ancestry_profile` is emitted when a European-only representative record would otherwise hide multiple non-European or multi-ancestry validation records. Each record has eight sections:

- `predicted_trait` — `trait_reported`, `trait_efo[].{label,id}`
- `performance_metrics` — `phenotyping_reported`, `covariates`, `metrics{pgs_only_r2, pgs_only_auroc, full_model_auroc, c_index, effect_sizes[]}`, `evaluation_sample{sample_numbers{individuals,cases,controls}, ancestry, cohorts[]}`
- `evaluation_ancestry_profile` — either `null` when no hidden diverse validation-record breadth is available, or an object with `record_count`, `representative_performance_id`, `selected_validation_ancestry`, `catalog_eval_ancestry_distribution`, `observed_validation_ancestries[]`, and compact `additional_validation_records[]` summaries for non-representative diverse/multi-ancestry validation records
- `source_of_variant_associations_gwas` — `sample_numbers{individuals,cases,controls}`, `ancestry`, `cohorts[]`
- `score_development_training` — `sample_numbers{individuals,cases,controls}`, `ancestry`
- `development_method` — `method_name`
- `variants` — `variants_number`
- `pgs_source` — `publication_title`, `publication_journal`, `date_release`

## When to use

- Choosing the best same-trait PGS among several candidates for a fixed trait.
- Verifying whether a proposed primary PGS is reasonable on quality grounds.

Do **not** use this skill to decide which trait or source bundle is *related* to the target — that is cross-trait transfer reasoning and belongs to the `prs-model-transfer` skill. This skill judges the quality of records already under consideration; it does not choose the trait.

## How to appraise

Treat the candidates as a fixed list. **Every consideration below is advisory and carries no fixed precedence — weigh them against each other case-by-case based on what the records actually show. If the records do not support an inference, do not force it.**

1. **Read each candidate's visible fields** across all eight sections above.

2. **Weigh these factors (listed in rough order of how strongly they predict external validation — a prior, not a precedence rule; weigh case-by-case):**
   - endpoint fidelity (`phenotyping_reported` is the primary endpoint-fidelity field; `predicted_trait.trait_reported` / `trait_efo` are concept-alignment fields)
   - comparable performance: PRS-only metrics (`metrics.pgs_only_r2`, `metrics.pgs_only_auroc`) are the comparable axis when present; per-SD effect sizes (`metrics.effect_sizes[]`, e.g. OR/HR) are strong standalone-quality signals; `metrics.full_model_auroc` and `metrics.c_index` are real but covariate-inflated and rank lowest among usable axes
   - transportability: evaluation and GWAS `ancestry` breadth, multi-cohort vs single-cohort (`cohorts[]`), study archetype (disease-focused vs pan-trait framework)
   - validation-ancestry profile: whether the representative record is only one slice of a broader validation set, and whether additional validation records show consistent endpoint/metric evidence in non-European or multi-ancestry contexts
   - polygenic signal: training scale (`score_development_training`, `source_of_variant_associations_gwas`), `variants.variants_number`, robustness across cohorts
   - method family and model structure (`development_method.method_name`)
   - covariate cleanliness in `performance_metrics.covariates`
   - publication context (`pgs_source.date_release`, journal) and evaluation sample size — weak signals

3. **Recognise covariate-leakage and packaging patterns** that lower a candidate's standalone PGS quality (clinical risk calculators, family-history packages, biomarker/treatment/mediator adjustment, horizon-conditioned absolute-risk packaging, broad-EHR phenotype summaries). These are advisory red flags, never deterministic vetoes.

4. **Cluster surviving candidates by study family** and compare siblings on the record: cleaner PRS-only metrics, endpoint definition, training scale, variant coverage, evaluation breadth, covariate cleanliness. Treat `evaluation_ancestry_profile` as supporting context for transportability, not as a hard rule: a diverse profile strengthens a candidate only when endpoint and metric evidence remain coherent. Do not rank method labels, publication recency, ancestry breadth, or large evaluation size by themselves — require the records to show why that signal should matter in the particular comparison.

5. **Express uncertainty.** When two candidates are near-tied on the visible fields, say so. Picking one and declaring high confidence is worse than picking one and noting the tie.

## Detailed empirical patterns

`references/pgs_evidence_appraisal.md` holds the full empirical-pattern corpus, organised by record section. **Read it in full when appraising candidates — within a single trait every section bears on every comparison, so the corpus is loaded whole rather than selectively.** It begins with a table of contents.
