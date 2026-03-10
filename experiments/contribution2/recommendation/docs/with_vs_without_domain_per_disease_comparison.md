# With Domain Knowledge vs Without Domain Knowledge: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison built from the latest with-domain and without-domain experiment summaries and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes all models in the benchmark `Target_TopK` set, listed in benchmark order as `Target #1..#K`, followed by the current with-domain, without-domain, and baseline selections.

## High-Level Outcome

- With Domain Knowledge: `25/30 = 83.33%`; `trial_hits = 240/300 = 80.00%`
- Without Domain Knowledge: `19/30 = 63.33%`; `trial_hits = 190/300 = 63.33%`
- Baseline: `11/30 = 36.67%`

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`, with `r = 1` as best and `r = M` as worst.
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- With Domain Knowledge: `mean NRS = 0.8393` (30 modal selections); `trial mean NRS = 0.8247` (300 trials)
- Without Domain Knowledge: `mean NRS = 0.6797` (30 modal selections); `trial mean NRS = 0.6743` (300 trials)

## Per-Disease Tables

### prostate cancer

Candidate pool: `96` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS005238 | PGS005237 | PGS001291 | Agent Input |
| AoU benchmark rank | 1/95 | 51/95 | 72/95 | 18/95 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.5402 | 0.5205 | 0.5551 | Benchmark Only |
| In Target_TopK | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 7/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Prostate cancer | Prostate carcinoma | Prostate carcinoma | Prostate cancer | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | 5-year incident prostate cancer | 5-year incident prostate cancer | Prostate cancer | Agent Input |
| method_name | PRS-CS | LDpred2 | SCT (Stacked Clumping and Thresholding) | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM001251 | PPM022696 | PPM022695 | PPM008955 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 10 | 10 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6544 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0316 | Agent Input |
| performance_metrics.full_model_auc | 0.5910 | 0.7890 | 0.7810 | 0.9110 | Agent Input |
| performance_metrics.full_model_r2 | 0.0245 | N/A | N/A | 0.2959 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0145 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.573, 'ci_upper': 0.609} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.789, 'ci_lower': 0.782, 'ci_upper': 0.796} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.781, 'ci_lower': 0.774, 'ci_upper': 0.788} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.91101, 'ci_lower': 0.90322, 'ci_upper': 0.91879} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0245} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.152} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.85, 'ci_lower': 1.76, 'ci_upper': 4.62} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.29589} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01454} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.03164} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.65437, 'ci_lower': 0.62906, 'ci_upper': 0.67968} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.393, 'ci_lower': 1.3, 'ci_upper': 1.493} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.332, 'se': 0.0352} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=184,010 | n=184,010 | n=24,905 | Agent Input |
| samples_training | n=5,650 | n=10,000 | n=10,000 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | MGI | UKB | UKB | UKB | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | HGG Adv | HGG Adv | PLoS Genet | Agent Input |
| date_release | 2020-12-15 | 2025-10-06 | 2025-10-06 | 2021-10-21 | Agent Input |
| variants_number | 1111494 | 964607 | 517551 | 948 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Age-specific absolute risk adjusted by PGS relative risk | Age-specific absolute risk adjusted by PGS relative risk | age, sex, UKB array type, Genotype PCs | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS000208 | PGS001289 | PGS001289 | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 16/32 | 24/32 | 24/32 | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.5890 | 0.5636 | 0.5636 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid cancer | Thyroid cancer | Thyroid cancer | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | Thyroid cancer | Thyroid cancer | Thyroid cancer | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | Genome-wide significant variants | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022743 | PPM022757 | PPM022756 | PPM000632 | PPM008947 | PPM008947 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.6184 | 0.6184 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0124 | 0.0124 | Agent Input |
| performance_metrics.full_model_auc | 0.6845 | 0.6135 | 0.6174 | 0.7510 | 0.6374 | 0.6374 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0160 | 0.0160 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0339 | 0.0339 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.684522760200784} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.613489463745261} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.617388005401901} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.751, 'ci_lower': 0.736, 'ci_upper': 0.768} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63744, 'ci_lower': 0.5901, 'ci_upper': 0.68478} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63744, 'ci_lower': 0.5901, 'ci_upper': 0.68478} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.016} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03389} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01236} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61843, 'ci_lower': 0.56413, 'ci_upper': 0.67273} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.016} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03389} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01236} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61843, 'ci_lower': 0.56413, 'ci_upper': 0.67273} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96019114706853} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.673041992501825} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49346171423604} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.401096723418125} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55051776688383} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.438588918302023} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=130,279 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | NBS UKB | UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Assessing thyroid cancer risk using polygenic risk scores. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Proc Natl Acad Sci U S A | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2020-07-01 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 10 | 11 | 11 | Agent Input |
| covariates | Unknown | Unknown | Unknown | gender, birth year, family history of disease (1st or 2nd degree relative) | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### hypothyroidism

Candidate pool: `28` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005268 | PGS005268 | PGS005218 | PGS001181 | Agent Input |
| AoU benchmark rank | 1/28 | 1/28 | 3/28 | 14/28 | Benchmark Only |
| AoU benchmark AUC | 0.6575 | 0.6575 | 0.6289 | 0.6090 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 7/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Other hypothyroidism (time-to-event) | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | Agent Input |
| phenotyping_reported | hypothyroidism | hypothyroidism | Incident hypothyroidism | TTE other hypothyroidism | Agent Input |
| method_name | PRSCS | PRSCS | PRS-CS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022751 | PPM022751 | PPM022617 | PPM008598 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6896 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0742 | Agent Input |
| performance_metrics.full_model_auc | 0.6389 | 0.6389 | 0.8590 | 0.7669 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.1513 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0729 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638920940728866} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638920940728866} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76691, 'ci_lower': 0.7602, 'ci_upper': 0.77362} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.15134} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0729} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.07419} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.68962, 'ci_lower': 0.68178, 'ci_upper': 0.69747} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65808867613792} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.505665539081399} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65808867613792} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.505665539081399} | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=441,692 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | n=1,146,562 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | Nat Genet | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2025-11-10 | 2021-10-21 | Agent Input |
| variants_number | 1085173 | 1085173 | 1110091 | 4739 | Agent Input |
| covariates | Unknown | Unknown | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | age, sex, UKB array type, Genotype PCs | Agent Input |


### hodgkins lymphoma

Candidate pool: `27` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000639 | PGS003449 | PGS000638 | PGS000639 | PGS000639 | PGS000874 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 1/27 | 1/27 | 10/27 | Benchmark Only |
| AoU benchmark AUC | 0.6180 | 0.6120 | 0.6014 | 0.6180 | 0.6180 | 0.5379 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Hodgkin's disease | Hodgkin lymphoma | Hodgkin's disease | Hodgkin's disease | Hodgkin's disease | Chronic lymphocytic leukemia | Agent Input |
| trait_efo | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | chronic lymphocytic leukemia | Agent Input |
| phenotyping_reported | Hodgkin's disease | Chronic lymphocytic leukemia | Hodgkin's disease | Hodgkin's disease | Hodgkin's disease | Chronic lymphocytic leukemia in individuals with a family history of hematological cancers | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | GWAS Hits | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Representative SNPs from chronic lymphocytic leukemia susceptibility loci | Agent Input |
| performance_metrics.selected_performance_id | PPM001324 | PPM017231 | PPM001323 | PPM001324 | PPM001324 | PPM002495 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European, NR | Agent Input |
| performance_metrics.record_count | 1 | 4 | 1 | 1 | 1 | 17 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6200 | N/A | 0.6010 | 0.6200 | 0.6200 | 0.8610 | Agent Input |
| performance_metrics.full_model_r2 | 0.0276 | N/A | 0.0193 | 0.0276 | 0.0276 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.601, 'ci_lower': 0.535, 'ci_upper': 0.671} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.861, 'ci_lower': 0.82, 'ci_upper': 0.9} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0193} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0824} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.62, 'ci_lower': 0.258, 'ci_upper': 10.1} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 0.97, 'ci_upper': 1.08} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.377, 'ci_lower': 1.08, 'ci_upper': 1.755} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.32, 'se': 0.124} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.79, 'ci_lower': 2.44, 'ci_upper': 5.87} | Agent Input |
| validation_sample_size | n=775 | n=20,134 | n=775 | n=775 | n=775 | n=3,958 | Agent Input |
| samples_training | n=736 | N/A | n=736 | n=736 | n=736 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: NR (50%), AFR (12%), EUR (25%), MAE (12%) | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | MGI | MGI | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Association of polygenic risk score with the risk of chronic lymphocytic leukemia and monoclonal B-cell lymphocytosis. | Agent Input |
| publication.journal | Am J Hum Genet | Leukemia | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Blood | Agent Input |
| date_release | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2021-08-26 | Agent Input |
| variants_number | 20 | 21 | 16 | 20 | 20 | 41 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Age, sex, study, socioeconomic status (when available) | Agent Input |


### obstructive sleep apnea

Candidate pool: `20` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005220 | PGS005220 | PGS005219 | Agent Input |
| AoU benchmark rank | 1/20 | 1/20 | 1/20 | 2/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5784 | 0.5784 | 0.5454 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | PPM022620 | PPM022620 | PPM022620 | PPM022619 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.7900 | 0.7900 | 0.7900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.98, 'ci_lower': 1.74, 'ci_upper': 2.24} | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=21,975 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2025-06-16 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 984184 | 984184 | 982740 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### sleep apnea

Candidate pool: `20` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005220 | PGS005220 | PGS005219 | Agent Input |
| AoU benchmark rank | 1/20 | 1/20 | 1/20 | 2/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5784 | 0.5784 | 0.5454 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | PPM022620 | PPM022620 | PPM022620 | PPM022619 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.7900 | 0.7900 | 0.7900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.98, 'ci_lower': 1.74, 'ci_upper': 2.24} | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=21,975 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2025-06-16 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 984184 | 984184 | 982740 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### testicular neoplasm

Candidate pool: `14` models. Benchmark `Target_TopK`: `5`.


| Field | Target #1 | Target #2 | Target #3 | Target #4 | Target #5 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | PGS000796 | PGS001164 | PGS001164 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 1/13 | 3/13 | 3/13 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | 0.9212 | 0.9044 | 0.9044 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | Benchmark target #4 | Benchmark target #5 | 5/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Testicular cancer | Testicular cancer | Agent Input |
| trait_efo | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | Agent Input |
| phenotyping_reported | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Incident testicular cancer | Testicular cancer | Testicular cancer | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | lassosum | snpnet | Pruning and Thresholding (P+T) | lassosum | 52 variants from Graff et al (PGS000086) with inverse variant weights | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM002067 | PPM001285 | PPM008544 | PPM001284 | PPM001282 | PPM002067 | PPM008544 | PPM008544 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 1 | 1 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6296 | N/A | N/A | N/A | 0.6296 | 0.6296 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0157 | N/A | N/A | N/A | 0.0157 | 0.0157 | Agent Input |
| performance_metrics.full_model_auc | 0.7870 | 0.6360 | 0.8391 | 0.6370 | 0.6560 | 0.7870 | 0.8391 | 0.8391 | Agent Input |
| performance_metrics.full_model_r2 | 0.6050 | 0.0460 | 0.1291 | 0.0473 | 0.0487 | 0.6050 | 0.1291 | 0.1291 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0313 | N/A | N/A | N/A | 0.0313 | 0.0313 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.636, 'ci_lower': 0.565, 'ci_upper': 0.698} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.637, 'ci_lower': 0.568, 'ci_upper': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656, 'ci_lower': 0.593, 'ci_upper': 0.717} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.046} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0839} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 6.35, 'ci_lower': 1.81, 'ci_upper': 22.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0473} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0844} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.35, 'ci_lower': 1.08, 'ci_upper': 17.5} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.084} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.72, 'ci_lower': 0.568, 'ci_upper': 13.1} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.619, 'ci_lower': 1.267, 'ci_upper': 2.067} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.482, 'se': 0.125} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.628, 'ci_lower': 1.281, 'ci_upper': 2.069} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.487, 'se': 0.122} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.667, 'ci_lower': 1.296, 'ci_upper': 2.143} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.511, 'se': 0.128} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | N/A | N/A | Agent Input |
| validation_sample_size | n=179,537 | n=755 | n=67,425 | n=755 | n=755 | n=179,537 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | n=776 | n=269,704 | n=776 | n=776 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | MGI | UKB | MGI | MGI | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | UKB | UKB | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-05-28 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | 2021-05-28 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 52 | 250 | 280 | 31 | 771 | 52 | 280 | 280 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Age at assessment, genotyping array, PCs(1-15) | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### uterine carcinoma

Candidate pool: `14` models. Benchmark `Target_TopK`: `4`.


| Field | Target #1 | Target #2 | Target #3 | Target #4 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002735 | PGS003381 | PGS001795 | PGS001299 | Agent Input |
| AoU benchmark rank | 1/14 | 2/14 | 3/14 | 4/14 | 3/14 | 9/14 | 10/14 | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5609 | 0.5970 | 0.5044 | 0.4564 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | Benchmark target #4 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Uterine endometrial carcinoma | Uterine cancer | Cervical cancer | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | uterine carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Risk of endometrial cancer | uterine endometrial carcinoma | Uterine cancer | Cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | lassosum | PRS-CS-auto | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM002041 | PPM002057 | PPM016256 | PPM014832 | PPM016256 | PPM009299 | PPM008994 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 2 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.5522 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0019 | 0.0026 | Agent Input |
| performance_metrics.full_model_auc | 0.7550 | 0.7540 | 0.7610 | 0.5600 | 0.7610 | 0.6600 | 0.7676 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4860 | 0.1100 | N/A | 0.1100 | N/A | 0.1128 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0068 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.755} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.754} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56, 'ci_lower': 0.54, 'ci_upper': 0.57} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76761, 'ci_lower': 0.74661, 'ci_upper': 0.7886} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': 'Odds ratio (OR, third vs first tertile)', 'name_short': 'Odds ratio (OR, third vs first tertile)', 'estimate': 1.55, 'ci_lower': 1.37, 'ci_upper': 1.74} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.001948} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11284} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00676} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00263} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55215, 'ci_lower': 0.51478, 'ci_upper': 0.58952} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.1, 'ci_upper': 1.29} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.18, 'ci_lower': 1.09, 'ci_upper': 1.27} | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=212,156 | n=212,156 | n=144,479 | n=118,636 | n=144,479 | n=170,276 | n=24,905 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,757 | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (15%), EUR (84%), OTH (80%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | N/A | BBJ BioMe BioVU CCPM CKB EB FinnGen HUNT MGBB MGI deCODE | UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Development and evaluation of polygenic risk scores for prediction of endometrial cancer risk in European women. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Genet Med | Cancer Res | Cell Genom | PLoS Genet | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-07-21 | 2023-01-19 | 2022-09-08 | 2021-10-21 | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 529365 | 911692 | 24 | Agent Input |
| covariates | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | age, top 20 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### kidney cancer

Candidate pool: `10` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS004908 | PGS004908 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/10 | 1/10 | 1/10 | 1/10 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5824 | 0.5824 | 0.5824 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal carcinoma | renal carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM021361 | PPM021361 | PPM021361 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 2 | 2 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | 0.7400 | 0.7400 | 0.7400 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | Agent Input |
| validation_sample_size | n=324,805 | n=324,805 | n=324,805 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | BBJ FinnGen NCI | BBJ FinnGen NCI | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2024-05-22 | 2024-05-22 | 2024-05-22 | Agent Input |
| variants_number | 107 | 107 | 107 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### obesity

Candidate pool: `10` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005235 | PGS001298 | PGS001298 | Agent Input |
| AoU benchmark rank | 1/10 | 1/10 | 8/10 | 8/10 | Benchmark Only |
| AoU benchmark AUC | 0.6311 | 0.6311 | 0.5549 | 0.5549 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Adiposity | Adiposity | Obesity (time-to-event) | Obesity (time-to-event) | Agent Input |
| trait_efo | obesity | obesity | obesity | obesity | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity (phecode: 278.1) | TTE obesity | TTE obesity | Agent Input |
| method_name | LDpred2-auto | LDpred2-auto | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022667 | PPM022667 | PPM008991 | PPM008991 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 2 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5757 | 0.5757 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0115 | 0.0115 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.5956 | 0.5956 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0181 | 0.0181 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0336 | 0.0336 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | N/A | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=100,960 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | EGG GIANT UKB | UKB | UKB | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2025-10-06 | 2025-10-06 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 709828 | 709828 | 9227 | 9227 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex, batch, and the first 10 genetic principal components | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS001267 | PGS001268 | PGS001268 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 2/9 | 3/9 | 3/9 | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7397 | 0.7362 | 0.7362 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis (time-to-event) | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | TTE ankylosing spondylitis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009896 | PPM008844 | PPM008849 | PPM008844 | PPM008849 | PPM008849 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | 0.7265 | 0.7346 | 0.7265 | 0.7346 | 0.7346 | Agent Input |
| performance_metrics.r2 | N/A | 0.0988 | 0.1023 | 0.0988 | 0.1023 | 0.1023 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7433 | 0.7488 | 0.7433 | 0.7488 | 0.7488 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1092 | 0.1150 | 0.1092 | 0.1150 | 0.1150 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.1299 | 0.1269 | 0.1299 | 0.1269 | 0.1269 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0653, 'ci_upper': 0.0941} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 85 | 10 | 10 | 10 | 10 | 10 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### aortic stenosis

Candidate pool: `8` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS005254 | PGS005252 | PGS005252 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 1/8 | 8/8 | 8/8 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.6375 | 0.3445 | 0.3445 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Aortic stenosis | Aortic stenosis | Aortic stenosis | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | aortic stenosis | aortic stenosis | aortic stenosis | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Incident aortic stenosis cases | Incident aortic stenosis cases | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | LDPred2 | LDPred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM022737 | PPM022738 | PPM022739 | PPM022737 | PPM022733 | PPM022733 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | 0.8700 | 0.8700 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.87} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.87} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.4, 'ci_upper': 1.66} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.41, 'ci_upper': 1.67} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.92} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.92} | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=244,450 | n=446,895 | n=446,895 | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | n=205,483 | n=47,691 | n=47,691 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | N/A | MGBB | MGBB | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 1110912 | 1119377 | 1119377 | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | Agent Input |


### renal carcinoma

Candidate pool: `8` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS004908 | PGS004908 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/8 | 1/8 | 1/8 | 1/8 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5824 | 0.5824 | 0.5824 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal carcinoma | renal carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM021361 | PPM021361 | PPM021361 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 2 | 2 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | 0.7400 | 0.7400 | 0.7400 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | Agent Input |
| validation_sample_size | n=324,805 | n=324,805 | n=324,805 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | BBJ FinnGen NCI | BBJ FinnGen NCI | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2024-05-22 | 2024-05-22 | 2024-05-22 | Agent Input |
| variants_number | 107 | 107 | 107 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### graves disease

Candidate pool: `7` models. Benchmark `Target_TopK`: `2`.


| Field | Target #1 | Target #2 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005265 | PGS005265 | PGS001042 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 2/7 | 2/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.7677 | 0.7535 | 0.7535 | 0.7535 | 0.6290 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | graves' disease | TTE thyrotoxicosis [hyperthyroidism] | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022749 | PPM022748 | PPM022748 | PPM022748 | PPM007972 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.6339 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0236 | Agent Input |
| performance_metrics.full_model_auc | 0.6637 | 0.6652 | 0.6652 | 0.6652 | 0.7130 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0591 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0467 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.663730746326419} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54332658848452} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.433940209108075} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1085173 | 1085173 | 1085173 | 226 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### nodular goiter

Candidate pool: `7` models. Benchmark `Target_TopK`: `2`.


| Field | Target #1 | Target #2 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005263 | PGS005262 | PGS005262 | PGS005262 | PGS005273 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 2/7 | 2/7 | 6/7 | Benchmark Only |
| AoU benchmark AUC | 0.7033 | 0.6911 | 0.6911 | 0.6911 | 0.4540 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Agent Input |
| trait_efo | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | benign, thyroid carcinoma, nodular goiter | Agent Input |
| phenotyping_reported | benign nodular gioter | benign nodular gioter | benign nodular gioter | benign nodular gioter | thyroid carcenoma vs benign nodular goiter | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | PRSCS | Agent Input |
| performance_metrics.selected_performance_id | PPM022746 | PPM022745 | PPM022745 | PPM022745 | PPM022756 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5876 | 0.5933 | 0.5933 | 0.5933 | 0.6174 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.587559211464932} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.617388005401901} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.36199799551033} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.308952736001074} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55051776688383} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.438588918302023} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1085170 | 1085173 | 1085173 | 1085173 | 1085164 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. Benchmark `Target_TopK`: `4`.


| Field | Target #1 | Target #2 | Target #3 | Target #4 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS003861 | PGS001280 | PGS001277 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 7/7 | 2/7 | 3/7 | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5129 | 0.5916 | 0.5907 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | Benchmark target #4 | 6/10 trials | 7/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | Pulmonary embolism | PE (time-to-event) | PE +/- DVT | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism | pulmonary embolism, deep vein thrombosis | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | Pulmonary embolism | TTE PE | PE +/- DVT | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | PRSice-2 | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008890 | PPM008900 | PPM008885 | PPM008897 | PPM018751 | PPM008900 | PPM008885 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | 0.5916 | 0.6077 | 0.6114 | 0.6003 | N/A | 0.6077 | 0.6114 | Agent Input |
| performance_metrics.r2 | 0.0133 | 0.0140 | 0.0151 | 0.0115 | N/A | 0.0140 | 0.0151 | Agent Input |
| performance_metrics.full_model_auc | 0.6535 | 0.6762 | 0.6750 | 0.6242 | 0.7650 | 0.6762 | 0.6750 | Agent Input |
| performance_metrics.full_model_r2 | 0.0337 | 0.0406 | 0.0400 | 0.0176 | N/A | 0.0406 | 0.0400 | Agent Input |
| performance_metrics.incremental_auc | 0.0350 | 0.0293 | 0.0315 | 0.0446 | N/A | 0.0293 | 0.0315 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65354, 'ci_lower': 0.63231, 'ci_upper': 0.67477} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.765} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03366} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03495} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01331} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59164, 'ci_lower': 0.56886, 'ci_upper': 0.61442} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | {'name_long': 'Odds ratio (OR, 30-70th quantile vs <90th quantile)', 'name_short': 'Odds ratio (OR, 30-70th quantile vs <90th quantile)', 'estimate': 5.08, 'ci_lower': 4.109, 'ci_upper': 6.282} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=24,838 | n=24,905 | n=24,905 | n=67,349 | n=9,456 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | CURES_China | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Genome-wide association analyses identified novel susceptibility loci for pulmonary embolism among Han Chinese population. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | BMC Med | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2023-09-01 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 288 | 88 | 96 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS003972 | PGS003973 | PGS003973 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 3/6 | 1/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.6312 | 0.6374 | 0.6374 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 8/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM019137 | PPM017103 | PPM019134 | PPM019134 | PPM019137 | PPM019137 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 3 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8820 | 0.7080 | 0.6900 | 0.6900 | 0.8820 | 0.8820 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0055 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.708, 'ci_lower': 0.691, 'ci_upper': 0.725} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00547} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=6,940 | n=6,940 | n=7,517 | n=7,517 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2023-11-01 | 2023-11-01 | 2023-11-01 | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 1118997 | 1118997 | 1118997 | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | Unknown | Age, Age^2, Sex | Age, Age^2, Sex | Agent Input |


### age-related macular degeneration

Candidate pool: `6` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004606 | PGS002269 | PGS004952 | PGS004606 | PGS004606 | PGS004952 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 1/6 | 1/6 | 3/6 | Benchmark Only |
| AoU benchmark AUC | 0.6547 | 0.6530 | 0.6512 | 0.6547 | 0.6547 | 0.6512 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | 6/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | Agent Input |
| phenotyping_reported | Age-related macular degeneration | Rentinal layer thickness (photoreceptor inner and outer segments) | Late age-related macular degeneration (Clinical Classification) | Age-related macular degeneration | Age-related macular degeneration | Late age-related macular degeneration (Clinical Classification) | Agent Input |
| method_name | PRS-CS | Independent variants associated with AMD | Genome-wide significant SNPs | PRS-CS | PRS-CS | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM020767 | PPM012920 | PPM021761 | PPM020767 | PPM020767 | PPM021761 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, South Asian, Not reported | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 6 | 1 | 1 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7100 | N/A | 0.8420 | 0.7100 | 0.7100 | 0.8420 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.21, 'ci_lower': -0.23, 'ci_upper': -0.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | Agent Input |
| validation_sample_size | n=163,011 | n=44,823 | n=1,232 | n=163,011 | n=163,011 | n=1,232 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | IAMDGC | IAMDGC | IAMDGC | Agent Input |
| publication.title | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Agent Input |
| publication.journal | Nat Genet | Ophthalmology | Invest Ophthalmol Vis Sci | Nat Genet | Nat Genet | Invest Ophthalmol Vis Sci | Agent Input |
| date_release | 2024-02-20 | 2022-04-01 | 2024-09-19 | 2024-02-20 | 2024-02-20 | 2024-09-19 | Agent Input |
| variants_number | 1000946 | 47 | 52 | 1000946 | 1000946 | 52 | Agent Input |
| covariates | age, sex, principal components 1-10 | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | Age, sex, survey membership, 10 PCs | age, sex, principal components 1-10 | age, sex, principal components 1-10 | Age, sex, survey membership, 10 PCs | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS003428 | PGS001299 | PGS001299 | Agent Input |
| AoU benchmark rank | 1/6 | 5/6 | 6/6 | 6/6 | Benchmark Only |
| AoU benchmark AUC | 0.6925 | 0.3846 | 0.3401 | 0.3401 | Benchmark Only |
| In Target_TopK | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 8/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident cervical cancer | Incident cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | LDpred | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM002039 | PPM017102 | PPM008994 | PPM008994 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5522 | 0.5522 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0026 | 0.0026 | Agent Input |
| performance_metrics.full_model_auc | 0.7450 | 0.6130 | 0.7676 | 0.7676 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1128 | 0.1128 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0068 | 0.0068 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76761, 'ci_lower': 0.74661, 'ci_upper': 0.7886} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76761, 'ci_lower': 0.74661, 'ci_upper': 0.7886} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11284} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00676} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00263} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55215, 'ci_lower': 0.51478, 'ci_upper': 0.58952} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11284} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00676} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00263} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55215, 'ci_lower': 0.51478, 'ci_upper': 0.58952} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | N/A | N/A | Agent Input |
| validation_sample_size | n=211,795 | n=128,113 | n=24,905 | n=24,905 | Agent Input |
| samples_training | N/A | n=4,295 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | TwinGene | EB FinnGen KP UKB | UKB | UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Hum Mol Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2020-02-12 | 2023-04-28 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 10 | 2894555 | 24 | 24 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | age, smoking | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### cutaneous melanoma

Candidate pool: `5` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS003382 | PGS003382 | PGS003382 | Agent Input |
| AoU benchmark rank | 1/5 | 1/5 | 1/5 | 1/5 | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.6239 | 0.6239 | 0.6239 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 8/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Skin cutaneous melanoma | Skin cutaneous melanoma | Skin cutaneous melanoma | Agent Input |
| trait_efo | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | skin cutaneous melanoma | skin cutaneous melanoma | skin cutaneous melanoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM016257 | PPM016257 | PPM016257 | PPM016257 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6820 | 0.6820 | 0.6820 | 0.6820 | Agent Input |
| performance_metrics.full_model_r2 | 0.0261 | 0.0261 | 0.0261 | 0.0261 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=273,786 | n=273,786 | n=273,786 | n=273,786 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | N/A | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Agent Input |
| publication.journal | Cancer Res | Cancer Res | Cancer Res | Cancer Res | Agent Input |
| date_release | 2023-01-19 | 2023-01-19 | 2023-01-19 | 2023-01-19 | Agent Input |
| variants_number | 672 | 672 | 672 | 672 | Agent Input |
| covariates | age, sex, top 20 genetic principal components | age, sex, top 20 genetic principal components | age, sex, top 20 genetic principal components | age, sex, top 20 genetic principal components | Agent Input |


### late-onset alzheimer's disease

Candidate pool: `5` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000054 | PGS000054 | PGS004918 | PGS004918 | Agent Input |
| AoU benchmark rank | 1/5 | 1/5 | 4/5 | 4/5 | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5690 | 0.5114 | 0.5114 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 8/10 trials | 6/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Alzheimer's disease (late onset) | Alzheimer's disease (late onset) | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Agent Input |
| trait_efo | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | Agent Input |
| phenotyping_reported | Familial late-onset Alzheimer's disease (LOAD) | Familial late-onset Alzheimer's disease (LOAD) | Late-onset Alzheimer's disease | Late-onset Alzheimer's disease | Agent Input |
| method_name | Genome-wide significant variants | Genome-wide significant variants | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM000135 | PPM000135 | PPM021384 | PPM021384 | Agent Input |
| performance_metrics.selected_validation_ancestry | Hispanic or Latin American | Hispanic or Latin American | European | European | Agent Input |
| performance_metrics.record_count | 3 | 3 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7310 | 0.7310 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.731} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.731} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73, 'ci_lower': 1.57, 'ci_upper': 1.93} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73, 'ci_lower': 1.57, 'ci_upper': 1.93} | N/A | N/A | Agent Input |
| validation_sample_size | n=3,324 | n=3,324 | n=136 | n=136 | Agent Input |
| samples_training | N/A | N/A | n=439 | n=439 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ADGC BfDR CHARGE EADI GERAD | ADGC BfDR CHARGE EADI GERAD | Agent Input |
| publication.title | Polygenic risk scores in familial Alzheimer disease. | Polygenic risk scores in familial Alzheimer disease. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Agent Input |
| publication.journal | Neurology | Neurology | Neurobiol Aging | Neurobiol Aging | Agent Input |
| date_release | 2019-12-18 | 2019-12-18 | 2024-06-12 | 2024-06-12 | Agent Input |
| variants_number | 21 | 21 | 8 | 8 | Agent Input |
| covariates | Age, sex | Age, sex | Unknown | Unknown | Agent Input |


### open-angle glaucoma

Candidate pool: `5` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004944 | PGS004944 | PGS004944 | PGS001797 | Agent Input |
| AoU benchmark rank | 1/5 | 1/5 | 1/5 | 2/5 | Benchmark Only |
| AoU benchmark AUC | 0.6405 | 0.6405 | 0.6405 | 0.6264 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 9/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Agent Input |
| trait_efo | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | Agent Input |
| phenotyping_reported | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Agent Input |
| method_name | Lassosum | Lassosum | Lassosum | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM021744 | PPM021744 | PPM021744 | PPM009313 | Agent Input |
| performance_metrics.selected_validation_ancestry | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | European | Agent Input |
| performance_metrics.record_count | 8 | 8 | 8 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0315 | Agent Input |
| performance_metrics.full_model_auc | 0.7480 | 0.7480 | 0.7480 | 0.7490 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.749} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.031479} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | N/A | Agent Input |
| validation_sample_size | n=407,667 | n=407,667 | n=407,667 | n=7,128 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), ASN (60%), EAS (18%), EUR (79%), OTH (60%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI TWB UCLA UKB | Agent Input |
| publication.title | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | JAMA Ophthalmol | JAMA Ophthalmol | JAMA Ophthalmol | Cell Genom | Agent Input |
| date_release | 2024-08-29 | 2024-08-29 | 2024-08-29 | 2022-09-08 | Agent Input |
| variants_number | 144019 | 144019 | 144019 | 885417 | Agent Input |
| covariates | Age, age2, sex, ancestry | Age, age2, sex, ancestry | Age, age2, sex, ancestry | sex,age, 20PCs | Agent Input |


### alcohol dependence

Candidate pool: `4` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002738 | PGS002738 | PGS002738 | N/A | Agent Input |
| AoU benchmark rank | 1/4 | 1/4 | 1/4 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6051 | 0.6051 | 0.6051 | N/A | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Alcohol use disorder | Alcohol use disorder | Alcohol use disorder | N/A | Agent Input |
| trait_efo | alcohol dependence | alcohol dependence | alcohol dependence | N/A | Agent Input |
| phenotyping_reported | Alcohol use disorder | Alcohol use disorder | Alcohol use disorder | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM014841 | PPM014841 | PPM014841 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 4 | 4 | 4 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | N/A | Agent Input |
| validation_sample_size | n=7,900 | n=7,900 | n=7,900 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | MVP UKB | MVP UKB | MVP UKB | N/A | Agent Input |
| publication.title | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | N/A | Agent Input |
| publication.journal | Alcohol Clin Exp Res | Alcohol Clin Exp Res | Alcohol Clin Exp Res | N/A | Agent Input |
| date_release | 2022-08-03 | 2022-08-03 | 2022-08-03 | N/A | Agent Input |
| variants_number | 326000 | 326000 | 326000 | N/A | Agent Input |
| covariates | Unknown | Unknown | Unknown | N/A | Agent Input |


### hypertrophic cardiomyopathy

Candidate pool: `4` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004911 | PGS000739 | PGS004910 | PGS004911 | PGS004911 | PGS000739 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 1/4 | 1/4 | 2/4 | Benchmark Only |
| AoU benchmark AUC | 0.6036 | 0.5891 | 0.5873 | 0.6036 | 0.6036 | 0.5891 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | 8/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Agent Input |
| trait_efo | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | Genome-wide significant variants | PRS-CS | PRS-CS | PRS-CS | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM021367 | PPM018531 | PPM021366 | PPM021367 | PPM021367 | PPM018531 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 1 | 1 | 1 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8000 | 0.8210 | 0.7300 | 0.8000 | 0.8000 | 0.8210 | Agent Input |
| performance_metrics.full_model_r2 | 0.0480 | N/A | 0.0310 | 0.0480 | 0.0480 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | Agent Input |
| validation_sample_size | n=343,182 | n=184,511 | n=343,182 | n=343,182 | n=343,182 | n=184,511 | Agent Input |
| samples_training | N/A | n=47,737 | N/A | N/A | N/A | n=47,737 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | Agent Input |
| training_development_cohorts | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | Agent Input |
| publication.title | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-02-26 | 2021-02-23 | 2025-02-26 | 2025-02-26 | 2025-02-26 | 2021-02-23 | Agent Input |
| variants_number | 374114 | 27 | 374190 | 374114 | 374114 | 27 | Agent Input |
| covariates | age, age^2, sex, PC1-10 | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | Agent Input |


### juvenile idiopathic arthritis

Candidate pool: `4` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000114 | PGS000114 | PGS000114 | PGS000324 | Agent Input |
| AoU benchmark rank | 1/4 | 1/4 | 1/4 | 4/4 | Benchmark Only |
| AoU benchmark AUC | 0.5768 | 0.5768 | 0.5768 | 0.5230 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Enthesitis-related Juvenile Idiophatic Arthritis | Agent Input |
| trait_efo | juvenile idiopathic arthritis | juvenile idiopathic arthritis | juvenile idiopathic arthritis | enthesitis-related juvenile idiopathic arthritis | Agent Input |
| phenotyping_reported | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Enthesitis-related Arthritis | Agent Input |
| method_name | SparSNP | SparSNP | SparSNP | SparSNP | Agent Input |
| performance_metrics.selected_performance_id | PPM000263 | PPM000263 | PPM000263 | PPM000874 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 4 | 4 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7380 | 0.7380 | 0.7380 | 0.9300 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.93, 'ci_lower': 0.86, 'ci_upper': 0.99} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.09, 'ci_lower': 2.07, 'ci_upper': 5.04} | Agent Input |
| validation_sample_size | n=940 | n=940 | n=940 | n=594 | Agent Input |
| samples_training | n=7,505 | n=7,505 | n=7,505 | n=5,354 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | Agent Input |
| publication.title | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Agent Input |
| publication.journal | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Agent Input |
| date_release | 2020-02-27 | 2020-02-27 | 2020-02-27 | 2020-09-18 | Agent Input |
| variants_number | 26 | 26 | 26 | 138 | Agent Input |
| covariates | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | Agent Input |


### peripheral vascular disease

Candidate pool: `4` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005217 | PGS005217 | PGS001843 | PGS005217 | Agent Input |
| AoU benchmark rank | 1/4 | 1/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.5862 | 0.5862 | 0.5123 | 0.5862 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 9/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Peripheral artery disease | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Agent Input |
| trait_efo | peripheral arterial disease | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | Agent Input |
| phenotyping_reported | Incident peripheral artery disease | Incident peripheral artery disease | Peripheral vascular disease, unspecified | Incident peripheral artery disease | Agent Input |
| method_name | LDpred2 | LDpred2 | Penalized regression (bigstatsr) | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM022612 | PPM022612 | PPM009634 | PPM022612 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | European | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | Agent Input |
| performance_metrics.record_count | 15 | 15 | 8 | 15 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7310 | 0.7310 | N/A | 0.7310 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0151, 'ci_lower': 0.0011, 'ci_upper': 0.029} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | Agent Input |
| validation_sample_size | n=304,294 | n=304,294 | n=19,668 | n=304,294 | Agent Input |
| samples_training | n=96,239 | n=96,239 | n=391,124 | n=96,239 | Agent Input |
| ancestry_distribution | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | Agent Input |
| training_development_cohorts | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | Agent Input |
| publication.title | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Agent Input |
| publication.journal | JAMA Cardiol | JAMA Cardiol | Am J Hum Genet | JAMA Cardiol | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2022-01-10 | 2025-06-16 | Agent Input |
| variants_number | 1296292 | 1296292 | 242 | 1296292 | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | age, sex and the first ten principal components of genetic ancestry | Agent Input |


### hashimoto's thyroiditis

Candidate pool: `3` models. Benchmark `Target_TopK`: `2`.


| Field | Target #1 | Target #2 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005272 | PGS005271 | PGS005271 | PGS005270 | PGS005270 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.7941 | 0.7940 | 0.7940 | 0.6412 | 0.6412 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | 8/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Agent Input |
| trait_efo | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Agent Input |
| phenotyping_reported | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM022755 | PPM022754 | PPM022754 | PPM022753 | PPM022753 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6054 | 0.6297 | 0.6297 | 0.6387 | 0.6387 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.605418550899187} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.629725726511746} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.629725726511746} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41698139161814} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.348528828383883} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54908058789994} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.437661585839951} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54908058789994} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.437661585839951} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1085142 | 1085156 | 1085156 | 55 | 55 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | Agent Input |


### preeclampsia

Candidate pool: `3` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003586 | PGS003586 | PGS003586 | N/A | Agent Input |
| AoU benchmark rank | 1/3 | 1/3 | 1/3 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.8077 | 0.8077 | 0.8077 | N/A | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Pre-eclampsia | Pre-eclampsia | Pre-eclampsia | N/A | Agent Input |
| trait_efo | preeclampsia | preeclampsia | preeclampsia | N/A | Agent Input |
| phenotyping_reported | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM018280 | PPM018280 | PPM018280 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | N/A | Agent Input |
| validation_sample_size | n=25,582 | n=25,582 | n=25,582 | N/A | Agent Input |
| samples_training | n=212,034 | n=212,034 | n=212,034 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | N/A | Agent Input |
| publication.title | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | N/A | Agent Input |
| publication.journal | Nat Med | Nat Med | Nat Med | N/A | Agent Input |
| date_release | 2023-06-22 | 2023-06-22 | 2023-06-22 | N/A | Agent Input |
| variants_number | 1087033 | 1087033 | 1087033 | N/A | Agent Input |
| covariates | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | N/A | Agent Input |


### skin carcinoma in situ

Candidate pool: `3` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000471 | PGS000471 | PGS000471 | PGS000471 | Agent Input |
| AoU benchmark rank | 1/3 | 1/3 | 1/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.6010 | 0.6010 | 0.6010 | 0.6010 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| trait_efo | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | Agent Input |
| phenotyping_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| method_name | lassosum | lassosum | lassosum | lassosum | Agent Input |
| performance_metrics.selected_performance_id | PPM001156 | PPM001156 | PPM001156 | PPM001156 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5690 | 0.5690 | 0.5690 | 0.5690 | Agent Input |
| performance_metrics.full_model_r2 | 0.0255 | 0.0255 | 0.0255 | 0.0255 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | Agent Input |
| validation_sample_size | n=5,500 | n=5,500 | n=5,500 | n=5,500 | Agent Input |
| samples_training | n=6,005 | n=6,005 | n=6,005 | n=6,005 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | MGI | MGI | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 7 | 7 | 7 | 7 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### vitiligo

Candidate pool: `3` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | With Domain Knowledge | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000760 | PGS000738 | PGS001536 | PGS001536 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.6417 | 0.6276 | 0.5669 | 0.5669 | Benchmark Only |
| In Target_TopK | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 7/10 trials | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Vitiligo | Vitiligo | Vitiligo (time-to-event) | Vitiligo (time-to-event) | Agent Input |
| trait_efo | Vitiligo | Vitiligo | Vitiligo | Vitiligo | Agent Input |
| phenotyping_reported | anti-PD-L1 induced hypothyroidism in cancer patients | Red hair | TTE vitiligo | TTE vitiligo | Agent Input |
| method_name | GCTA-COJO forward selection highest PPA variants | Genome-wide significant variants | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM001935 | PPM018438 | PPM005219 | PPM005219 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6419 | 0.6419 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0162 | 0.0162 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6345 | 0.6345 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0386 | 0.0169 | 0.0169 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0816 | 0.0816 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'meta-analysis p-value', 'name_short': 'meta-analysis p-value', 'estimate': 1.1e-06} | {'name_long': 'pseudo R²', 'name_short': 'pseudo R²', 'estimate': 0.038569956} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.41, 'ci_lower': 1.22, 'ci_upper': 1.61} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.694777831} | N/A | N/A | Agent Input |
| validation_sample_size | n=1,584 | n=4,702 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=408,959 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-06-11 | 2021-02-23 | 2021-11-25 | 2021-11-25 | Agent Input |
| variants_number | 42 | 48 | 77 | 77 | Agent Input |
| covariates | 5 genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |
