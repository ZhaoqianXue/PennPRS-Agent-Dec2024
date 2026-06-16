---
name: prs-model-transfer
description: Evaluates the predictive quality of polygenic-score (PGS) candidate records from PGS Catalog metadata. Use when ranking multiple candidate PGSs for a fixed trait or fixed source bundle, when verifying a chosen PGS against quality criteria, or whenever PGS Catalog records are being compared on internal quality. Trait-agnostic. Provides advisory empirical patterns; the calling LLM remains the decision-maker.
---

# PRS Model Evaluator

Trait-agnostic guidance for evaluating PGS Catalog candidate records using only the metadata fields available in the records (phenotype labels, performance metrics, training/validation cohort summaries, covariate descriptions, method, publication context). The skill emits **advisory empirical patterns**; the caller weighs them against each other.

## When to use

Invoke when the task is "given a fixed trait or a fixed source bundle, choose the best PGS among several candidates, or verify whether a chosen PGS is reasonable":

- Within-bundle PGS picking once a source bundle is fixed.
- Cross-bundle final-pick reconciliation when each bundle's PGSs are being compared on internal quality.
- Verification of a proposed primary against PGS-quality patterns.

Do **not** invoke for trait-relationship reasoning (which bundle to pick, whether trait A relates to trait B). That decision belongs to a different skill.

## Procedural overview

Treat the candidate records as a fixed list and apply the procedure below. Every step is advisory; if the records do not support the inference, do not force it. **None of the considerations below carry a fixed precedence**; weigh them against each other case-by-case based on what the candidate records actually show.

1. **Identify each candidate's visible fields.** Look at `phenotyping_reported`, `trait_reported`, `trait_efo`, `method_name`, `variants_number`, `samples_training`, training/validation ancestry distributions, `performance_metrics`, the covariate set listed in performance records, and publication context (year, journal).

2. **Consider these factors when comparing candidates** (no fixed ordering):
   - phenotype alignment and endpoint fidelity
   - comparable reported performance (PRS-only vs full-model AUC/OR/HR; PRS-only is the comparable axis when present)
   - transportability context (training and validation cohort ancestry breadth, multi-cohort vs single-cohort, study archetype)
   - polygenic signal strength and breadth (training sample size, variant coverage, robustness across multiple validation cohorts)
   - method family and model structure
   - covariate cleanliness in performance records
   - publication context, date, validation sample size

3. **Keep the role boundary clear.** This skill evaluates the quality of PGS records that are already under consideration. It does not decide which source bundle is most related to the target. In transfer, source relevance is not identical to literal label closeness: record-visible endpoints may be direct, measurement/proxy-like, upstream, intermediate, exposure-like, or otherwise construct-adjacent. Still, generic model-quality advantages can make one PGS preferable only when the candidate records support that trade-off; by themselves they are not proof that one source bundle should beat another, especially when displacing a direct-endpoint candidate whose own PRS evidence is clean and competitive.

4. **Recognise covariate-leakage and packaging patterns** that lower a candidate's standalone PGS quality. Leakage and packaging signals are advisory red flags, never deterministic vetoes. The detail catalogue lives in `reference/02_performance_metrics_auc_performance_metrics_r2_covariates.md`. The catalogue is enumerated by category (clinical risk calculators, family-history packages, biomarker / treatment / mediator adjustment, horizon-conditioned packaging, broad EHR phenotype summaries) rather than by specific traits.

5. **Cluster surviving candidates by study family.** Within the same publication family, compare siblings on the records: cleaner PRS-only metrics, endpoint definition, training scale, variant coverage, validation breadth, and packaging. Do not rank method labels, publication age, "established" use, or large validation breadth by themselves; require the candidate records to show why that signal should matter in the particular comparison.

6. **Express uncertainty.** When two surviving candidates are near-tied on the visible fields, say so. Picking one and declaring high confidence is worse than picking one and noting the tie.

## Cross-trait transfer caveat

When the bundle is being used as a transfer source for a different target trait, the rules above apply to **the PGS's quality and transferability**, not to bundle selection. A few empirical patterns worth keeping in mind for transfer specifically:

- **Endpoint fidelity to the source trait is one consideration, not a label-only rule.** A PGS that faithfully targets its source-trait endpoint is not automatically the best transfer source for a related target trait, but a clean direct-endpoint candidate should not be demoted for a broader or adjacent score on generic validation scale alone. A broader, upstream, intermediate, or measurement-like source can transfer as well or better when the candidate records show cleaner PRS evidence, stronger polygenic signal, or a plausible construct bridge that is visible in the records. If the broader score mainly offers generic scale while the direct-endpoint record is clean and competitive, keep that trade-off explicit.
- **Polygenic signal strength and validation breadth are first-class signals, not standalone trump cards.** Large training sample size, broad variant coverage, and consistent performance across multiple independent validation cohorts are robust transferability indicators. Weigh them with endpoint fidelity, PRS-only metric cleanliness, and packaging rather than treating any single signal as decisive.
- **Multi-trait-analysis / phenotype-integration scores trade off endpoint precision for power.** They are sometimes the right choice and sometimes not — judge from the records, not from the methodological label.
- **Bundle-level trait-relationship reasoning belongs to a different skill.** Do not propose a different source bundle from this skill.

For deeper context on cross-trait transferability, see `reference/08_cross_trait_transfer_considerations.md`.

## Reference files

`reference/` contains the empirical-rule corpus, organised by metadata field family. Each file is loaded on-demand; consult the catalogue when a specific field needs deeper context than the procedural overview provides.

| file | contents |
|---|---|
| `00_preamble.md` | Cross-cutting empirical patterns and factor-importance rules |
| `01_trait_reported_trait_efo_phenotyping_reported.md` | Endpoint-fidelity rules across the three trait label fields |
| `02_performance_metrics_auc_performance_metrics_r2_covariates.md` | Comparable-metrics handling and the covariate-leakage / packaging catalogue |
| `03_validation_sample_size.md` | When validation N is informative and when it isn't |
| `04_training_development_cohorts_samples_training_ancestry_distr.md` | Training-cohort and ancestry-transportability patterns |
| `05_method_name.md` | Method-family considerations |
| `06_publication_title_publication_journal_date_release.md` | Publication-context weak signals |
| `07_variants_number.md` | Variant-count considerations |
| `08_cross_trait_transfer_considerations.md` | Source-bundle plausibility and transferability heuristics |

The reference filenames are zero-padded numerically because callers that need the full corpus concatenate the files in filename-sort order. Do not rename or reorder them without updating any consumer that depends on the order.

## Constraints (binding for any caller)

- **Trait-agnostic.** Never introduce or apply rules that name specific ICD codes, trait categories, or disease families.
- **LLM-led.** Never convert any rule into a hard numeric score, weight, ranking formula, or deterministic veto. Weigh the rules against each other case-by-case.
- **Advisory text only.** Every rule is an empirical pattern, not a deterministic check. Override any rule when the candidate records justify it.
