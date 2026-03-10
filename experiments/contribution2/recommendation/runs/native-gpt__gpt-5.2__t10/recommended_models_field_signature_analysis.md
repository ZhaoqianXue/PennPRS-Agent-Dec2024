# Analysis of Recommended Models in `native-gpt__gpt-5.2__t10`

## Scope

This note analyzes why the modal `Recommended Models` were selected in the Native GPT Contribution2 run, using only the fields exposed to the model under the PGS Catalog metadata context:

`trait_reported`, `trait_efo`, `phenotyping_reported`, `performance_metrics`, `validation_sample_size`, `samples_variants`, `samples_training`, `ancestry_distribution`, `method_name`, `variants_number`, `variants_genomebuild`, `covariates`, `training_development_cohorts`, `publication`, and `date_release`.

The analysis is derived from three run artifacts:

- `experiment_native_gpt_batch_requests.jsonl`
- `experiment_native_gpt_results.json`
- `experiment_native_gpt_summary.json`

## Executive Takeaways

- Native GPT behaves as a metadata-driven reranker rather than a domain-aware PRS scientist.
- Its dominant heuristic is: phenotype alignment first, then reported validation strength, then study-scale/portability proxies.
- This heuristic is highly stable: 27/30 diseases had the same recommendation in all 10 trials.
- It is often useful: 20/30 modal recommendations landed in the benchmark `Target_TopK`.
- Its main failure mode is over-trusting reported AUC and large published study size, which do not always translate to the best All of Us performance.

## What Fields Actually Drove Selection

Across 300 trial rationales, the feature mentions were:

| Signal family | Mentions in 300 rationales | Interpretation |
| --- | ---: | --- |
| `auc` | 300 | The primary ranking signal. |
| `trait_match` | 299 | Direct disease alignment was treated as mandatory. |
| `sample_size` | 286 | Main confidence modifier after AUC. |
| `ancestry` | 242 | Important, but usually secondary to AUC and trait match. |
| `r2` | 174 | Useful when present, but not consistently available. |
| `variants` | 166 | Used as a scale/polygenicity proxy. |
| `covariates` | 69 | Occasionally used to justify rigor. |
| `method` | 48 | Mostly a tie-breaker, not a primary driver. |

This shows that the available fields effectively collapsed into three decision axes:

1. Phenotype alignment: `trait_reported`, `trait_efo`, `phenotyping_reported`
2. Reported validation strength: `performance_metrics`, `validation_sample_size`
3. Study scale and portability proxies: `samples_training`, `samples_variants`, `ancestry_distribution`, `method_name`, `variants_number`, `training_development_cohorts`, `date_release`

## Common Characteristics of the Selected Models

The modal recommended models shared a consistent profile:

- Strong ontology-level match. `trait_efo` matched the disease name lexically in 26/30 cases; the remaining 4 were clear ontology synonyms such as kidney cancer vs renal carcinoma.
- Reported performance was almost always visible. 27/30 modal recommendations had a non-null AUC.
- GPT frequently picked the disease-wise metadata winner. The selected model had the highest reported AUC within the disease in 18/30 cases.
- Study size mattered. The selected model had the largest validation sample size in 15/30 diseases.
- Recency mattered. The selected model was the latest release in 15/30 diseases.
- Broader training context helped. The selected model had the largest number of development cohorts in 12/30 diseases.

At the method level, recommendations concentrated in modern dense PRS families:

- PRS-CS family (`PRS-CS`, `PRSCS`, `PRS-CS-auto`, weighted PRS-CS ensemble): 11/30 modal recommendations, 9/11 benchmark hits
- `snpnet`: 7/30 modal recommendations, only 3/7 benchmark hits

This suggests that GPT was attracted to modern large-scale models in general, but PRS-CS-family selections aligned with All of Us benchmark performance more often than `snpnet` selections.

## Why These Models Were Chosen

In practice, Native GPT translated the visible fields into a stable ranking rule:

1. Keep only exact or near-exact direct matches for the target disease.
2. Prefer the model with the strongest reported AUC relative to the global performance landscape.
3. Use validation sample size, ancestry compatibility, variants, cohorts, and recency to justify confidence or break ties.

Representative successful examples:

| Disease | Selected model | Why it looked strongest from visible fields |
| --- | --- | --- |
| Abdominal aortic aneurysm | `PGS003973` | Exact trait match, highest AUC among direct matches (0.882), 1.12M variants, 13 development cohorts |
| Age-related macular degeneration | `PGS004606` | Exact match, AUC 0.71, validation `n=163,011`, recent release (2024-02-20) |
| Open-angle glaucoma | `PGS004944` | Strong phenotype alignment, AUC 0.748, validation `n=407,667`, broad ancestry context |
| Obstructive sleep apnea | `PGS005220` | Exact phenotype alignment, AUC 0.79, 984k variants, large study scale |
| Kidney cancer / renal carcinoma | `PGS004908` | Ontology-equivalent trait mapping, AUC 0.74, validation `n=324,805`, clinically relevant covariates |

These are exactly the kinds of models a metadata-only reranker would favor.

## Where the Heuristic Broke

The failures are informative. The wrong recommendations usually did not look weak in metadata; they looked too strong.

Key evidence:

- 7/10 misses were still the disease-wise highest-AUC model.
- Among modal recommendations with non-null AUC, the median reported AUC was higher for misses than for hits (`0.832` vs `0.740`).
- Several misses were also the newest release or the largest validation study within their disease.

Representative failure patterns:

| Failure pattern | Example | Why GPT picked it | Why it still missed the benchmark |
| --- | --- | --- | --- |
| High reported AUC plus very large validation cohort | `PGS005218` for hypothyroidism | AUC `0.859`, validation `n=441,692`, training `n=1,146,562`, 1.11M variants | It ranked only `3/28` in the All of Us benchmark |
| New, large, high-AUC model | `PGS005237` for prostate cancer | AUC `0.845`, validation `n=184,010`, 517,551 variants, release `2025-10-06` | It ranked `72/96` in the benchmark |
| Standardized high-metric `snpnet` model | `PGS001299` for cervical carcinoma | AUC `0.91431`, R2 `0.22017`, training `n=269,704`, validation `n=67,425` | It ranked `6/6` in the benchmark |
| Same `snpnet` pattern repeated across diseases | `PGS001289` thyroid carcinoma, `PGS001298` obesity, `PGS001536` vitiligo | Strong reported AUC/R2 and clean UKB-style metadata | They ranked `24/32`, `8/10`, and `3/3`, respectively |

The central lesson is that Native GPT was often selecting the model with the best-looking published metadata, not the model with the best external portability to All of Us.

## Interpretation for Contribution2

This run provides a clean feature-attribution result for Contribution2:

- Without domain knowledge, GPT-5.2 mainly relies on `trait_*` fields, `performance_metrics`, and sample-size fields.
- `ancestry`, `variants`, and `method` act as secondary modifiers, not primary ranking signals.
- The model is therefore strong at identifying the most convincing published direct-match model, but weak at correcting for benchmark portability gaps.

That is the main explanation for the observed `66.67%` disease-level accuracy: the agent learned a transparent metadata heuristic that is often reasonable, but incomplete for cross-cohort PRS selection.
