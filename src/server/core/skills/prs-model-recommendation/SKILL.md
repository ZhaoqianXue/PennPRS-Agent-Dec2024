---
name: prs-model-recommendation
description: Use when choosing or verifying the best same-phenotype PGS Catalog model for a fixed target phenotype from candidate records with visible metadata. Do not use for cross-phenotype transfer, new model training, full-pool baseline judging, or recommendations where candidate records are not visible.
---

# PGS Model Recommendation (within-trait)

<!-- Scope note: this skill supplies reusable domain judgment for appraising same-trait
PGS Catalog records. It carries no task workflow, no candidate-count guidance, and no
trait-specific answers — runtime orchestration lives in the calling system prompt. -->

Appraise candidate PGS Catalog models the way a statistical geneticist judges which score is
best supported for the fixed (`target_trait`, `target_ancestry`)
pair supplied with the input. Judge each candidate on its record-visible metadata plus any
trait-specific heritability evidence supplied with the input.

Each candidate is **one self-contained record holding all of its PGS Catalog evidence** — every
performance record, and within each record every evaluation sample, plus every discovery-GWAS and
training block. Nothing is pre-selected, split, or aggregated: integrate across a candidate's own
records first, then compare candidates. The record carries one identifier plus seven fixed
sections (`id`, `predicted_trait`, `development_method`, `variants`, `pgs_source`,
`source_of_variant_associations_gwas`, `score_development_training`, `performance_metrics`):

- `predicted_trait` — `trait_reported`, `trait_efo[].{label,id}`
- `development_method` — `method_name`
- `variants` — `variants_number`
- `pgs_source` — `publication_title`, `publication_journal`, `date_release`
- `source_of_variant_associations_gwas[]` — discovery-GWAS blocks, each `sample_numbers{individuals,cases,controls}`, `ancestry`, `cohorts[]`
- `score_development_training[]` — training blocks, each `sample_numbers{individuals,cases,controls}`, `ancestry`
- `performance_metrics[]` — performance records, each `{performance_id, phenotyping_reported, covariates, effect_sizes[], classification_metrics[], other_metrics[], evaluation_samples[]}`; every metric is `{metric_name, estimate, ci_lower?, ci_upper?}`; every evaluation sample is `{sample_numbers{...}, ancestry, cohorts[]}`.

Metric appraisal comes from the metric name, its estimate and interval, the record's covariates, effect
sizes, and evaluation samples. Those fields distinguish covariate-free PRS discrimination,
covariate-adjusted full-model discrimination, per-SD effect sizes, and R²-like quantities.

Boundary: this skill supplies same-trait PRS evidence judgment. The field-level details live in
`references/pgs_evidence_appraisal.md`. Runtime orchestration, candidate-universe boundaries, output
schema, routing, and JSON formatting belong to the calling system prompt.

## What predicts same-trait support

These considerations form the reasoning order below, strongest predictor first. They are priors,
weighed against each other on what each record actually shows; a candidate strong on the upper
considerations and quiet on the lower ones is often the better score.

1. **Endpoint fidelity.** Whether the record measures the target disease itself. `phenotyping_reported`
   is the endpoint-fidelity field, read per performance record; `trait_reported`/`trait_efo` are
   concept-alignment fields. A direct diagnosis/case-control/incidence endpoint outweighs a
   surface-matching label.

2. **Study archetype** — the strongest structural prior, and the one most often decisive. A
   disease-focused, multi-cohort effort generalises better than a pan-trait, portability, or
   single-biobank framework sweep. Integrative multi-score aggregation and genome-wide shrinkage
   capture more transferable polygenic signal than sparse single-source construction. These archetype
   and method qualities carry weight **even when the disease-focused or integrative score reports
   fewer headline numbers** than a framework competitor.

3. **Comparability of the performance evidence — metric availability is not metric superiority.**
   A reported discrimination figure informs a comparison only as far as its covariates and endpoint
   make it comparable across candidates. A candidate that merely *displays* a clean covariate-free
   AUROC/R² is not thereby the stronger score: the cleanest-looking number frequently comes from a
   pan-trait framework score or from a covariate-inflated full model. Usable-axis cleanliness runs
   covariate-free AUROC/R² > per-SD OR/HR > C-index > covariate-adjusted AUROC; a figure resting on
   family history, biomarkers, treatment, mediators, or a risk-calculator/absolute-risk wrapper
   reflects those inputs rather than the score, and ranks below a clean figure even when numerically
   higher. A missing covariate-free metric lowers comparability, leaving method, archetype, effect
   size, and endpoint to carry the comparison; it is not inferiority. A displayed AUROC from a broad
   framework, a cumulative-incidence package, or repeated modest C-index rows can be weaker than a direct
   disease score with no AUROC when that record has a strong per-SD effect, cleaner endpoint, and more
   coherent study design.

4. **Transportability to `target_ancestry`.** PGS portability is governed by how well the
   validation ancestry matches the `target_ancestry`, read across all evaluation and GWAS blocks,
   together with cohort breadth — more informative than a European-default assumption.

5. **Polygenic signal and structure** — training/discovery scale, `variants_number`, method family,
   and robustness across a candidate's cohorts and performance records — as structural separators once
   the considerations above are comparable. Within one method family and endpoint, more variants and
   stronger, tighter effect sizes favour the candidate.

6. **Publication context and evaluation size** — release date, journal, and validation N are weak
   context. Recency, prestige, breadth of wording, and a large evaluation sample hold no predictive
   weight by themselves, and serve at most as a last tie-break once everything above is genuinely even.

## Holding the judgment calibrated

- A clean metric, a familiar method name, a recent date, or a large evaluation sample is one signal
  among the whole record, not a veto over it.
- Where a trait's signal concentrates in a few major loci, a compact or variant-selected score can be
  genuinely strong; structural priors bend to what the records show.
- Candidates from one disease-focused study family that corroborate each other are stronger evidence
  than a lone exact-label or lone high-number candidate whose edge rests on recency, wording, or a
  single covariate-adjusted metric.
- Heritability evidence, when supplied, serves as an external ceiling and sanity check on
  covariate-free R²-like metrics, not as a ranking axis.
- When candidates are genuinely close on the visible evidence, calibrated uncertainty is more useful
  than confident precision.

## Detailed empirical patterns

`references/pgs_evidence_appraisal.md` is the field-level appraisal reference, organised in current
single-record schema order and read only when more detail is needed for a field-level comparison.
