# Catalog Search Only: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison built from the catalog search only experiment summary and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes the benchmark top-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models).
Rows `Hit@1`..`Hit@5` are evaluated over the full disease/trial set; when a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models for that disease.

## High-Level Outcome

- Catalog Search Only `Hit@1`: `0/1 = 0.00%`; `trial_hits = 0/10 = 0.00%`
- Catalog Search Only `Hit@2`: `0/1 = 0.00%`; `trial_hits = 0/10 = 0.00%`
- Catalog Search Only `Hit@3`: `0/1 = 0.00%`; `trial_hits = 0/10 = 0.00%`
- Catalog Search Only `Hit@4`: `0/1 = 0.00%`; `trial_hits = 0/10 = 0.00%`
- Catalog Search Only `Hit@5`: `0/1 = 0.00%`; `trial_hits = 0/10 = 0.00%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search Only: `mean r / M = 0.7692` (1 modal selections); `trial mean r / M = 0.7692` (10 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search Only: `mean (M - r) / M = 0.2308` (1 modal selections); `trial mean (M - r) / M = 0.2308` (10 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search Only: `mean NRS = 0.2500` (1 modal selections); `trial mean NRS = 0.2500` (10 trials)


## Per-Disease Tables

### testicular carcinoma

Candidate pool: `13` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000086 | PGS000600 | PGS001164 | PGS000599 | PGS000604 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 10/13 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9182 | 0.9128 | 0.9044 | 0.9021 | 0.7468 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Testicular cancer | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Agent Input |
| trait_efo | testicular cancer, testicular germ cell tumor | testicular cancer, testicular germ cell tumor | testicular cancer | testicular cancer | testicular cancer | testicular cancer | Agent Input |
| phenotyping_reported | Incident testicular cancer | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | Genome-wide significant variants | lassosum | snpnet | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM002067 | PPM002051 | PPM001285 | PPM008544 | PPM001284 | PPM001289 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | 3 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6296 | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0157 | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7870 | 0.7830 | 0.6360 | 0.8391 | 0.6370 | 0.7030 | Agent Input |
| performance_metrics.full_model_r2 | 0.6050 | N/A | 0.0460 | 0.1291 | 0.0473 | 0.0882 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0313 | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.783} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.034} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.636, 'ci_lower': 0.565, 'ci_upper': 0.698} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.637, 'ci_lower': 0.568, 'ci_upper': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703, 'ci_lower': 0.659, 'ci_upper': 0.745} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.046} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0839} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 6.35, 'ci_lower': 1.81, 'ci_upper': 22.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0473} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0844} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.35, 'ci_lower': 1.08, 'ci_upper': 17.5} | {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0793} {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0882} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.6, 'ci_lower': 1.75, 'ci_upper': 12.1} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.18, 'ci_lower': 1.66, 'ci_upper': 2.87} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.619, 'ci_lower': 1.267, 'ci_upper': 2.067} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.482, 'se': 0.125} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.628, 'ci_lower': 1.281, 'ci_upper': 2.069} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.487, 'se': 0.122} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.106, 'ci_lower': 1.729, 'ci_upper': 2.565} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.745, 'se': 0.101} | Agent Input |
| validation_sample_size | n=179,537 | n=179,537 | n=755 | n=67,425 | n=755 | n=1,484 | Agent Input |
| samples_training | N/A | N/A | n=776 | n=269,704 | n=776 | n=1,671 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | B58C FCCC NCI PennCATH UKBS UKTCC UPENN | MGI | UKB | MGI | UKB | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2021-05-28 | 2020-02-12 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 52 | 52 | 250 | 280 | 31 | 44 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |
