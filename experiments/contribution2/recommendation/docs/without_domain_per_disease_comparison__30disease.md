# Without Domain Knowledge: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison built from the without-domain experiment summary and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes the benchmark top-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models).
Rows `Hit@1`..`Hit@5` are evaluated over the full disease/trial set; when a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models for that disease.

## High-Level Outcome

- Without Domain Knowledge `Hit@1`: `14/30 = 46.67%`; `trial_hits = 134/300 = 44.67%`
- Without Domain Knowledge `Hit@2`: `17/30 = 56.67%`; `trial_hits = 164/300 = 54.67%`
- Without Domain Knowledge `Hit@3`: `22/30 = 73.33%`; `trial_hits = 222/300 = 74.00%`
- Without Domain Knowledge `Hit@4`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`
- Without Domain Knowledge `Hit@5`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Without Domain Knowledge: `mean r / M = 0.4264` (30 modal selections); `trial mean r / M = 0.4310` (300 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Without Domain Knowledge: `mean (M - r) / M = 0.5736` (30 modal selections); `trial mean (M - r) / M = 0.5690` (300 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Without Domain Knowledge: `mean NRS = 0.6790` (30 modal selections); `trial mean NRS = 0.6736` (300 trials)


## Per-Disease Tables

### prostate cancer

Candidate pool: `96` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS000044 | PGS001292 | PGS000592 | PGS002793 | PGS005237 | Agent Input |
| AoU benchmark rank | 1/95 | 2/95 | 3/95 | 4/95 | 5/95 | 72/95 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.6295 | 0.6041 | 0.5748 | 0.5665 | 0.5205 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Prostate cancer | Prostate cancer | Family history of prostate cancer | Prostate cancer | Prostate cancer | Prostate carcinoma | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | family history of prostate cancer | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | Elevated serum prostate-specific antigen (PSA) levels | Prostate cancer (FH) | Cancer of prostate | Prostate cancer risk | 5-year incident prostate cancer | Agent Input |
| method_name | PRS-CS | Known susceptibility loci (genome-wide significant SNPs) | snpnet | lassosum | Genome-wide significant SNPs | SCT (Stacked Clumping and Thresholding) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.5910 | N/A | 0.6209 | 0.6160 | N/A | 0.8450 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0357 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=17,012 | n=67,425 | n=5,607 | n=1,190 | n=184,010 | Agent Input |
| samples_training | n=5,650 | N/A | n=269,704 | n=5,650 | n=109,323 | n=10,000 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (5%), EUR (95%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (2%), AMR (40%), EAS (1%), EUR (92%), MAE (3%) / DEV: AFR (3%), EAS (1%), EUR (96%) / EVAL: EAS (100%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | Agent Input |
| training_development_cohorts | MGI | ICR IGD PLCO ProtecT UKGPCS deCODE | UKB | MGI | AAPC BCFR BFBOCC BRICOH CBCS CIMBA CNIO CONSIT Chicago DEMOKRITOS DKFZ EMBRACE FCCC G-FaST GC-HBOC GEMO HCSC HEBCS HEBON HUNBOCS HVH ICO ICR IGD ILUH IOVHBOCS IPOBCS MAYO MSKCC MUV NCI OCGN OSU OUH PBCS PLCO ProtecT SWE-BRCA UKB UKGPCS UPENN UPITT VFCTG deCODE kConFab | UKB | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Reducing overdiagnosis by polygenic risk-stratified screening: findings from the Finnish section of the ERSPC. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Application of European-specific polygenic risk scores for predicting prostate cancer risk in different ancestry populations. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Agent Input |
| publication.journal | Am J Hum Genet | Br J Cancer | PLoS Genet | Am J Hum Genet | Prostate | HGG Adv | Agent Input |
| date_release | 2020-12-15 | 2019-12-18 | 2021-10-21 | 2020-12-15 | 2022-09-29 | 2025-10-06 | Agent Input |
| variants_number | 1111494 | 66 | 602 | 1334 | 82 | 517551 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | cancer stage, Gleason score | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | disease diagnostic age or age at recruitment, subgroups and 10 principal components | - | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS005259 | PGS005258 | PGS001289 | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 4/32 | 5/32 | 24/32 | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | 0.5636 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma | Thyroid carcenoma | Thyroid cancer | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma | thyroid carcenoma | Thyroid cancer | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | Pruning and Thresholding (P+T) | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6845 | 0.6135 | 0.6174 | 0.6953 | 0.6862 | 0.8323 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.1670 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 1085173 | 84 | 11 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### hypothyroidism

Candidate pool: `28` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005268 | PGS005269 | PGS005218 | PGS005267 | PGS004789 | PGS005218 | Agent Input |
| AoU benchmark rank | 1/28 | 2/28 | 3/28 | 4/28 | 5/28 | 3/28 | Benchmark Only |
| AoU benchmark AUC | 0.6575 | 0.6567 | 0.6289 | 0.6240 | 0.6231 | 0.6289 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | Agent Input |
| phenotyping_reported | hypothyroidism | hypothyroidism | Hypothyroidism | hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| method_name | PRSCS | PRSCS | PRS-CS | Pruning and Thresholding (P+T) | PRSmix | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6389 | 0.6386 | 0.8590 | 0.6400 | N/A | 0.8590 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=441,692 | n=94,651 | n=9,462 | n=441,692 | Agent Input |
| samples_training | N/A | N/A | n=1,146,562 | N/A | n=37,851 | n=1,146,562 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs | 23andMe CHB DBDS EB FinnGen UKB deCODE | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Agent Input |
| publication.journal | medRxiv | medRxiv | Nat Genet | medRxiv | Cell Genom | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2025-11-10 | 2026-01-19 | 2024-03-28 | 2025-11-10 | Agent Input |
| variants_number | 1085173 | 1085170 | 1110091 | 439 | 1109333 | 1110091 | Agent Input |
| covariates | Unknown | Unknown | age, sex, PC1, PC2, PC3, PC4 | Unknown | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4 | Agent Input |


### hodgkins lymphoma

Candidate pool: `27` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000639 | PGS003449 | PGS000638 | PGS003454 | PGS000648 | PGS000639 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 4/27 | 5/27 | 1/27 | Benchmark Only |
| AoU benchmark AUC | 0.6180 | 0.6120 | 0.6014 | 0.5597 | 0.5586 | 0.6180 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Hodgkin's disease | Hodgkin lymphoma | Hodgkin's disease | Diffuse large B-cell lymphoma | Chronic lymphocytic leukemia | Hodgkin's disease | Agent Input |
| trait_efo | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | diffuse large B-cell lymphoma | chronic lymphocytic leukemia | Hodgkins lymphoma | Agent Input |
| phenotyping_reported | Hodgkin's disease | Chronic lymphocytic leukemia | Hodgkin's disease | Chronic lymphocytic leukemia | Lymphoid leukemia, chronic | Hodgkin's disease | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | GWAS Hits | Genome-wide significant SNPs | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6200 | N/A | 0.6010 | N/A | 0.6960 | 0.6200 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=775 | n=20,134 | n=775 | n=20,134 | n=756 | n=775 | Agent Input |
| samples_training | n=736 | N/A | n=736 | N/A | n=730 | n=736 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | N/A | MGI | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Leukemia | Am J Hum Genet | Leukemia | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 20 | 21 | 16 | 5 | 44 | 20 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### obstructive sleep apnea

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005219 | PGS003479 | PGS003213 | PGS003857 | PGS005220 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 1/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | 0.5784 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Obstructive sleep apnea | Sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea (UnadjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | DBP | Sleep Apnea | BMI unadjusted obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | LDpred2 | PRS-CS | Genome-wide significant SNPs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7900 | 0.7900 | N/A | 0.5270 | 0.7700 | 0.7900 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=1,115 | n=21,354 | n=40,193 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | n=21,209 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (19%), AMR (8%), ASN (1%), EUR (72%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | N/A | UKB | MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Genetic determinants of cardiometabolic and pulmonary phenotypes and obstructive sleep apnoea in HCHS/SOL. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Genome-wide association study of obstructive sleep apnoea in the Million Veteran Program uncovers genetic heterogeneity by sex. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2023-03-24 | 2022-11-23 | 2023-09-01 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 982740 | 836839 | 1111194 | 18 | 984184 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Age, sex, center, 5 genetic PCs, Hispanic/Latino background, BMI | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | age, sex, genetic batch, PCs 1-10 | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### sleep apnea

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005219 | PGS003479 | PGS003213 | PGS003857 | PGS005220 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 1/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | 0.5784 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Obstructive sleep apnea | Sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea (UnadjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | DBP | Sleep Apnea | BMI unadjusted obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | LDpred2 | PRS-CS | Genome-wide significant SNPs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7900 | 0.7900 | N/A | 0.5270 | 0.7700 | 0.7900 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=1,115 | n=21,354 | n=40,193 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | n=21,209 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (19%), AMR (8%), ASN (1%), EUR (72%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | N/A | UKB | MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Genetic determinants of cardiometabolic and pulmonary phenotypes and obstructive sleep apnoea in HCHS/SOL. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Genome-wide association study of obstructive sleep apnoea in the Million Veteran Program uncovers genetic heterogeneity by sex. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2023-03-24 | 2022-11-23 | 2023-09-01 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 982740 | 836839 | 1111194 | 18 | 984184 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Age, sex, center, 5 genetic PCs, Hispanic/Latino background, BMI | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | age, sex, genetic batch, PCs 1-10 | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### testicular neoplasm

Candidate pool: `14` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | PGS001164 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 3/13 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | 0.9044 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Agent Input |
| trait_efo | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | Agent Input |
| phenotyping_reported | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | lassosum | snpnet | Pruning and Thresholding (P+T) | lassosum | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7870 | 0.6360 | 0.9816 | 0.6370 | 0.6560 | 0.9816 | Agent Input |
| performance_metrics.r2 | 0.6050 | N/A | 0.2970 | N/A | N/A | 0.2970 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=179,537 | n=755 | n=67,425 | n=755 | n=755 | n=67,425 | Agent Input |
| samples_training | N/A | n=776 | n=269,704 | n=776 | n=776 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | MGI | UKB | MGI | MGI | UKB | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Agent Input |
| date_release | 2021-05-28 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | 2021-10-21 | Agent Input |
| variants_number | 52 | 250 | 280 | 31 | 771 | 280 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | Agent Input |


### uterine carcinoma

Candidate pool: `14` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002735 | PGS004244 | PGS001795 | Agent Input |
| AoU benchmark rank | 1/14 | 2/14 | 3/14 | 4/14 | 5/14 | 9/14 | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5609 | 0.5519 | 0.5044 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Endometrial cancer | Uterine cancer | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | uterine carcinoma | Agent Input |
| phenotyping_reported | Endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Risk of endometrial cancer | Endometrial cancer | Uterine cancer | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | PRSice-2 | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7550 | 0.7540 | 0.7610 | 0.5600 | N/A | 0.6600 | Agent Input |
| performance_metrics.r2 | N/A | 0.4860 | 0.1100 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=221,699 | n=212,156 | n=144,479 | n=118,636 | n=133,830 | n=170,276 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,757 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (15%), EUR (84%), OTH (80%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | N/A | BBJ BioMe BioVU CCPM CKB EB FinnGen HUNT MGBB MGI deCODE | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Development and evaluation of polygenic risk scores for prediction of endometrial cancer risk in European women. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Genet Med | NPJ Precis Oncol | Cell Genom | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-07-21 | 2023-12-15 | 2022-09-08 | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 16 | 911692 | Agent Input |
| covariates | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, 10 PCs. | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | first 10 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### kidney cancer

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS000787 | PGS000722 | PGS004245 | PGS000076 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | 0.5824 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal cell carcinoma | renal cell carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Incident kidney cancer | Incident kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7400 | 0.7220 | 0.5670 | N/A | 0.7220 | 0.7400 | Agent Input |
| performance_metrics.r2 | N/A | 0.3660 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=324,805 | n=391,610 | n=400,812 | n=133,830 | n=411,695 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | N/A | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | JNCI Cancer Spectr | NPJ Precis Oncol | Nat Commun | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2021-05-28 | 2021-02-03 | 2023-12-15 | 2020-02-12 | 2024-05-22 | Agent Input |
| variants_number | 107 | 19 | 15 | 12 | 19 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Genotyping array | first 10 genetic principal components | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, sex, 10 PCs. | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### obesity

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005154 | PGS003959 | PGS002033 | PGS005145 | PGS001298 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 8/10 | Benchmark Only |
| AoU benchmark AUC | 0.6311 | 0.6165 | 0.5798 | 0.5753 | 0.5667 | 0.5549 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Adiposity | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Obesity (time-to-event) | Agent Input |
| trait_efo | obesity | obesity | obesity | obesity, overweight body mass index status, overnutrition | obesity | obesity | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | TTE obesity | Agent Input |
| method_name | LDpred2-auto | CT-SLEB | Genome-wide significant SNPs | LDpred2 (bigsnpr) | PRS-CS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.6533 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0423 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=58,688 | n=27,429 | n=20,000 | n=58,688 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | GWAS: NR (33%), EUR (67%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | BBJ | N/A | UKB | BBJ | UKB | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | The sulfur microbial diet and increased risk of obesity: Findings from a population-based prospective cohort study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Commun Biol | Clin Nutr | Am J Hum Genet | Commun Biol | PLoS Genet | Agent Input |
| date_release | 2025-10-06 | 2025-03-17 | 2023-10-17 | 2022-01-10 | 2025-03-17 | 2021-10-21 | Agent Input |
| variants_number | 709828 | 443124 | 940 | 846292 | 908466 | 9227 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex | Age, sex, race, centres, education, Townsend deprivation index, household income, smoking, alcohol consumption, physical activity, sleep pattern, energy intake, and BMI, WC or BF% at baseline | sex, age, birth date, deprivation index, 16 PCs | age, sex | age, sex, UKB array type, Genotype PCs | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS002089 | PGS003424 | PGS001268 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 3/9 | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7188 | 0.6491 | 0.7362 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | LDpred2 (bigsnpr) | LDpred2 | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | 0.9891 | 0.9915 | N/A | 0.7605 | 0.9915 | Agent Input |
| performance_metrics.r2 | N/A | 0.4432 | 0.4486 | N/A | N/A | 0.4486 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=18,262 | n=1,298 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=391,124 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Am J Hum Genet | J Transl Med | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2022-01-10 | 2023-02-08 | 2021-10-21 | Agent Input |
| variants_number | 85 | 10 | 10 | 22026 | 100 | 10 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### aortic stenosis

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS004911 | PGS004910 | PGS005252 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 8/8 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.5181 | 0.5166 | 0.3445 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Aortic stenosis | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | aortic stenosis | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Incident aortic stenosis cases | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | LDPred2 | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.8000 | 0.7300 | 0.8700 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0480 | 0.0310 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=343,182 | n=343,182 | n=446,895 | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | N/A | N/A | n=47,691 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | MGBB | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2025-02-26 | 2025-02-26 | 2026-01-19 | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 374114 | 374190 | 1119377 | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | Agent Input |


### renal carcinoma

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS000787 | PGS000722 | PGS004245 | PGS000076 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 1/8 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | 0.5824 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal cell carcinoma | renal cell carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Incident kidney cancer | Incident kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7400 | 0.7220 | 0.5670 | N/A | 0.7220 | 0.7400 | Agent Input |
| performance_metrics.r2 | N/A | 0.3660 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=324,805 | n=391,610 | n=400,812 | n=133,830 | n=411,695 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | N/A | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | JNCI Cancer Spectr | NPJ Precis Oncol | Nat Commun | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2021-05-28 | 2021-02-03 | 2023-12-15 | 2020-02-12 | 2024-05-22 | Agent Input |
| variants_number | 107 | 19 | 15 | 12 | 19 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Genotyping array | first 10 genetic principal components | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, sex, 10 PCs. | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### graves disease

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005264 | PGS002023 | PGS001042 | PGS005265 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | Benchmark Only |
| AoU benchmark AUC | 0.7677 | 0.7535 | 0.6667 | 0.6320 | 0.6290 | 0.7535 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis with or without goiter | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Graves' disease | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Thyrotoxicosis | Graves disease | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | Thyrotoxicosis with or without goiter | TTE thyrotoxicosis [hyperthyroidism] | graves' disease | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | snpnet | PRSCS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6637 | 0.6652 | 0.6587 | N/A | 0.7429 | 0.6652 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0808 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,108 | n=67,425 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | PLoS Genet | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2021-10-21 | 2026-01-19 | Agent Input |
| variants_number | 1085170 | 1085173 | 112 | 279385 | 226 | 1085173 | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | Unknown | Agent Input |


### nodular goiter

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005263 | PGS005262 | PGS005261 | PGS002022 | PGS001814 | PGS005262 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | Benchmark Only |
| AoU benchmark AUC | 0.7033 | 0.6911 | 0.6158 | 0.5575 | 0.5493 | 0.6911 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | Benign nodular goiter | Agent Input |
| trait_efo | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | multinodular goiter, nontoxic goiter | multinodular goiter, nontoxic goiter | benign, nodular goiter | Agent Input |
| phenotyping_reported | benign nodular gioter | benign nodular gioter | benign nodular gioter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | benign nodular gioter | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | PRSCS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.5876 | 0.5933 | 0.5854 | N/A | N/A | 0.5933 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,043 | n=19,043 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | Am J Hum Genet | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2022-01-10 | 2026-01-19 | Agent Input |
| variants_number | 1085170 | 1085173 | 110 | 375470 | 322 | 1085173 | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS004530 | PGS001280 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5578 | 0.5916 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | I26 (Pulmonary embolism) | PE (time-to-event) | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | I26 (Pulmonary embolism) | TTE PE | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | RFDiseasemetaPRS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6674 | 0.8074 | 0.8083 | 0.8256 | N/A | 0.8074 | Agent Input |
| performance_metrics.r2 | 0.0364 | 0.1233 | 0.1233 | 0.1674 | N/A | 0.1233 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=67,349 | n=67,425 | n=67,425 | n=67,349 | n=56,192 | n=67,425 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=174,489 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Commun Biol | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 1059939 | 88 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS001784 | PGS000753 | PGS003973 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.5618 | 0.5388 | 0.6374 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS-auto | Pruning and Thresholding (P+T) | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.8820 | 0.7080 | 0.6900 | 0.8680 | N/A | 0.8820 | Agent Input |
| performance_metrics.r2 | N/A | 0.0055 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=7,324 | n=350,767 | n=47,098 | n=7,517 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=8,772 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | MAYO-VDB MVP | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Cell Genom | Circulation | Nat Genet | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2022-09-08 | 2021-04-07 | 2023-11-01 | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 911440 | 29 | 1118997 | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, PCs (1-5) | Age, Age^2, Sex | Agent Input |


### age-related macular degeneration

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004606 | PGS002269 | PGS004952 | PGS001834 | PGS002041 | PGS004606 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6547 | 0.6530 | 0.6512 | 0.6133 | 0.6093 | 0.6547 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | Agent Input |
| phenotyping_reported | Age-related macular degeneration | Rentinal layer thickness (photoreceptor inner and outer segments) | Early age-related macular degeneration (Clinical Classification) | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Agent Input |
| method_name | PRS-CS | Independent variants associated with AMD | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7100 | N/A | 0.8420 | N/A | N/A | 0.7100 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=163,011 | n=44,823 | n=1,780 | n=19,413 | n=19,413 | n=163,011 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | UKB | UKB | IAMDGC | Agent Input |
| publication.title | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Agent Input |
| publication.journal | Nat Genet | Ophthalmology | Invest Ophthalmol Vis Sci | Am J Hum Genet | Am J Hum Genet | Nat Genet | Agent Input |
| date_release | 2024-02-20 | 2022-04-01 | 2024-09-19 | 2022-01-10 | 2022-01-10 | 2024-02-20 | Agent Input |
| variants_number | 1000946 | 47 | 52 | 157 | 116538 | 1000946 | Agent Input |
| covariates | age, sex, principal components 1-10 | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | Age, sex, survey membership, 10 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, principal components 1-10 | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS000784 | PGS003389 | PGS005165 | PGS003428 | PGS001299 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 | Benchmark Only |
| AoU benchmark AUC | 0.6925 | 0.6679 | 0.4759 | 0.4709 | 0.3846 | 0.3401 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Cervical cancer | Incident cervical cancer | cervical cancer | Cervical Cancer | Incident cervical cancer | Cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 10 variants from Graff et al (PGS000073) with inverse variant weights | lassosum | Known susceptibility loci (genome-wide significant SNPs) | LDpred | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7450 | 0.7450 | 0.5630 | 0.5660 | 0.6130 | 0.9143 | Agent Input |
| performance_metrics.r2 | N/A | 0.4370 | 0.0016 | N/A | N/A | 0.2202 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=226,216 | n=211,795 | n=144,374 | n=57,359 | n=128,113 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=4,295 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | TwinGene | NCI Seattle TwinGene Umea WTCCC | N/A | BBJ | EB FinnGen KP UKB | UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Polygenic risk scores for pan-cancer risk prediction in the Chinese population: A population-based cohort study based on the China Kadoorie Biobank. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | PLoS Med | Hum Mol Genet | PLoS Genet | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2025-03-17 | 2023-04-28 | 2021-10-21 | Agent Input |
| variants_number | 10 | 10 | 2814 | 15 | 2894555 | 24 | Agent Input |
| covariates | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, 10 PCs. | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | age, top 20 genetic principal components | Age,Sex (if applicable),Region,Top 10 genetic ancestry principal components | age, smoking | age, sex, UKB array type, Genotype PCs | Agent Input |


### cutaneous melanoma

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS004247 | PGS000766 | PGS003745 | PGS000339 | PGS003382 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 1/5 | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.5934 | 0.5886 | 0.5812 | 0.5663 | 0.6239 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Melanoma | Cutaneous melanoma | Skin Melanoma | Cutaneous melanoma | Skin cutaneous melanoma | Agent Input |
| trait_efo | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | Melanoma | Incident cutaneous melanoma | Skin Melanoma | Cutaneous melanoma in multiplex melanoma families | skin cutaneous melanoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | PRSice-2 | Variants associated with melanoma | Genome-wide significant SNPs | Clumping and Thresholding (C+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6820 | N/A | 0.6400 | N/A | N/A | 0.6820 | Agent Input |
| performance_metrics.r2 | 0.0261 | N/A | N/A | N/A | N/A | 0.0261 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=273,786 | n=133,830 | n=12,712 | n=448 | n=3,066 | n=273,786 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,402 | n=3,666 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | 23andMe AMFS CPSII DEMOKRITOS Essen-Heidelberg GenoMEL HPFS LMC MDACCS MELARISK MIA NHS PAH PLCO Q-MEGA SEARCH UKB WAMHS | UKB | BATS MIA PAH | N/A | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Genomic Risk Score for Melanoma in a Prospective Study of Older Individuals. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Multiplex melanoma families are enriched for polygenic risk. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Agent Input |
| publication.journal | Cancer Res | NPJ Precis Oncol | J Natl Cancer Inst | EBioMedicine | Hum Mol Genet | Cancer Res | Agent Input |
| date_release | 2023-01-19 | 2023-12-15 | 2021-05-28 | 2023-06-01 | 2020-11-05 | 2023-01-19 | Agent Input |
| variants_number | 672 | 65 | 56 | 57 | 22 | 672 | Agent Input |
| covariates | age, sex, top 20 genetic principal components | first 10 genetic principal components | Sex, melanoma family history, treatment (aspirin/placebo), age at enrolment, PRS*treatment | Unknown | PCs (1-10) | age, sex, top 20 genetic principal components | Agent Input |


### late-onset alzheimer's disease

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000054 | PGS002289 | PGS000334 | PGS004918 | PGS000053 | PGS004918 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 4/5 | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5203 | 0.5144 | 0.5114 | 0.4346 | 0.5114 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | Benchmark Only |
| trait_reported | Alzheimer's disease (late onset) | Late-onset Alzheimer's disease | Late-onset Alzheimer’s disease | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Alzheimer's disease (late onset) | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Agent Input |
| trait_efo | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | Agent Input |
| phenotyping_reported | Familial late-onset Alzheimer's disease (LOAD) | Pairs matching (short-term memory and attention) no. of correct online round 1 x age interaction | Late-onset Alzheimer’s disease | Late-onset Alzheimer's disease | Familial late-onset Alzheimer's disease (LOAD) | Late-onset Alzheimer's disease | Agent Input |
| method_name | Genome-wide significant variants | GWAS-significant variants (including APOE) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Genome-wide significant variants | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.7310 | N/A | 0.7310 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.1910 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=3,324 | n=497,087 | n=5,347 | n=136 | n=4,792 | n=136 | Agent Input |
| samples_training | N/A | N/A | N/A | n=439 | N/A | n=439 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (19%), EUR (81%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | IGAP UKB | ADGC BfDR CHARGE EADI GERAD | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ADGC BfDR CHARGE EADI GERAD | Agent Input |
| publication.title | Polygenic risk scores in familial Alzheimer disease. | Association of Genetic Variants Linked to Late-Onset Alzheimer Disease With Cognitive Test Performance by Midlife. | Risk prediction of late-onset Alzheimer's disease implies an oligogenic architecture. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Polygenic risk scores in familial Alzheimer disease. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Agent Input |
| publication.journal | Neurology | JAMA Netw Open | Nat Commun | Neurobiol Aging | Neurology | Neurobiol Aging | Agent Input |
| date_release | 2019-12-18 | 2022-05-18 | 2020-10-16 | 2024-06-12 | 2019-12-18 | 2024-06-12 | Agent Input |
| variants_number | 21 | 23 | 22 | 8 | 21 | 8 | Agent Input |
| covariates | Age, sex | Unknown | Unknown | Unknown | Age, sex | Unknown | Agent Input |


### open-angle glaucoma

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004944 | PGS001797 | PGS002741 | PGS000764 | PGS000350 | PGS004944 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 1/5 | Benchmark Only |
| AoU benchmark AUC | 0.6405 | 0.6264 | 0.6173 | 0.5749 | 0.5668 | 0.6405 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary-open angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Agent Input |
| trait_efo | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | Agent Input |
| phenotyping_reported | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary-open angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma (self-reported) | Agent Input |
| method_name | Lassosum | PRS-CS-auto | Genome-wide significant SNPs | SNPs associated with primary-open angle glaucoma were selected from the GWAS Catalog | Genome-wide significant variants | Lassosum | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7480 | 0.7490 | 0.6900 | N/A | N/A | 0.7480 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=407,667 | n=7,128 | n=3,382 | n=3,830 | n=6,538 | n=407,667 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), ASN (60%), EAS (18%), EUR (79%), OTH (60%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: AFR (50%), EUR (50%) | GWAS: MAE (100%) / EVAL: MAO (100%) | GWAS: EUR (94%), MAO (6%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | N/A | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI TWB UCLA UKB | N/A | N/A | ALIENOR ANZRAG BATS BES BMES ERF FES GEP GHS GIST HPFS Iowa MEEI Marshfield NEIGHBOR NHS OHTS ORCADES QIMR REHS RES RS SCES SIMES SINDI TEST TwinsUK WGHS deCODE | N/A | Agent Input |
| publication.title | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Glaucoma genetic risk scores in the Million Veteran Program. | The Role of Genetic Ancestry as a Risk Factor for Primary Open-angle Glaucoma in African Americans. | Association of a Primary Open-Angle Glaucoma Genetic Risk Score With Earlier Age at Diagnosis. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Agent Input |
| publication.journal | JAMA Ophthalmol | Cell Genom | Ophthalmology | Invest Ophthalmol Vis Sci | JAMA Ophthalmol | JAMA Ophthalmol | Agent Input |
| date_release | 2024-08-29 | 2022-09-08 | 2022-08-03 | 2021-04-28 | 2020-12-08 | 2024-08-29 | Agent Input |
| variants_number | 144019 | 885417 | 127 | 23 | 12 | 144019 | Agent Input |
| covariates | Age, age2, sex, ancestry | sex,age, 20PCs | Age, sex, and 10 sample-specific PCs | Age, ancestry (q0), gender | sex, DNA source, population structure | Age, age2, sex, ancestry | Agent Input |


### alcohol dependence

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002738 | PGS000201 | PGS000202 | PGS002739 | PGS002738 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.6051 | 0.5762 | 0.5742 | 0.5224 | 0.6051 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Alcohol use disorder | Problematic alcohol use | Problematic alcohol use | Alcohol use disorder | Alcohol use disorder | Agent Input |
| trait_efo | alcohol dependence | alcohol dependence measurement | alcohol dependence measurement | alcohol dependence | alcohol dependence | Agent Input |
| phenotyping_reported | Alcohol use disorder (AUD) in individuals with family history of AUD | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder | Alcohol use disorder (AUD) in individuals with family history of AUD | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CSx (gene-based) | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=7,900 | n=7,599 | n=1,251 | n=6,315 | n=7,900 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (12%), EUR (88%) / EVAL: AFR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MVP UKB | UKB | UKB | MVP PGC UKB | MVP UKB | Agent Input |
| publication.title | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Gene-based polygenic risk scores analysis of alcohol use disorder in African Americans. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Agent Input |
| publication.journal | Alcohol Clin Exp Res | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Alcohol Clin Exp Res | Agent Input |
| date_release | 2022-08-03 | 2020-07-01 | 2020-07-01 | 2022-08-03 | 2022-08-03 | Agent Input |
| variants_number | 326000 | 1094954 | 1083002 | 858 | 326000 | Agent Input |
| covariates | Unknown | sex, age of last observation, 10 Genetic PCs, genotyping array, data collection site | sex, age of last observation, 10 Genetic PCs | Unknown | Unknown | Agent Input |


### hypertrophic cardiomyopathy

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004911 | PGS000739 | PGS004910 | PGS000778 | PGS004911 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.6036 | 0.5891 | 0.5873 | 0.5514 | 0.6036 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 8/10 trials | Benchmark Only |
| trait_reported | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy (MTAG) | Agent Input |
| trait_efo | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Maximal left ventricular wall thickness indexed to body surface area (mm/m^2) in individuals with a pathogenic or likely pathogenic sarcomeric variant | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | Genome-wide significant variants | PRS-CS | Genome-wide significant variants | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.8000 | 0.8210 | 0.7300 | N/A | 0.8000 | Agent Input |
| performance_metrics.r2 | 0.0480 | N/A | 0.0310 | N/A | 0.0480 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=343,182 | n=184,511 | n=343,182 | n=368 | n=343,182 | Agent Input |
| samples_training | N/A | n=47,737 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: NR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | BRRD GEL HCMR RBH-CRB | ERSPC LHSC MHI NL4 RBH-CRB UKDHP UMCG | BRRD GEL HCMR RBH-CRB | Agent Input |
| publication.title | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Shared genetic pathways contribute to risk of hypertrophic and dilated cardiomyopathies with opposite directions of effect. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-02-26 | 2021-02-23 | 2025-02-26 | 2021-05-28 | 2025-02-26 | Agent Input |
| variants_number | 374114 | 27 | 374190 | 20 | 374114 | Agent Input |
| covariates | age, age^2, sex, PC1-10 | Age, gender, PCs(1-10) | age, age^2, sex, PC1-10 | Genetic relatedness matrix | age, age^2, sex, PC1-10 | Agent Input |


### juvenile idiopathic arthritis

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000114 | PGS000325 | PGS000326 | PGS000324 | PGS000114 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.5768 | 0.5517 | 0.5315 | 0.5230 | 0.5768 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis (Juvenile Idiophatic Arthritis) | Enthesitis-related Juvenile Idiophatic Arthritis | Juvenile Idiopathic Arthritis | Agent Input |
| trait_efo | juvenile idiopathic arthritis | oligoarticular juvenile idiopathic arthritis | polyarticular juvenile idiopathic arthritis, rheumatoid factor negative | enthesitis-related juvenile idiopathic arthritis | juvenile idiopathic arthritis | Agent Input |
| phenotyping_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis | Enthesitis-related Arthritis | Juvenile Idiopathic Arthritis | Agent Input |
| method_name | SparSNP | SparSNP | SparSNP | SparSNP | SparSNP | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7380 | 0.8000 | 0.7600 | 0.9300 | 0.7380 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=3,513 | n=3,157 | n=3,089 | n=3,020 | n=3,513 | Agent Input |
| samples_training | n=7,505 | n=6,137 | n=5,733 | n=5,354 | n=7,505 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | Agent Input |
| publication.title | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Agent Input |
| publication.journal | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Agent Input |
| date_release | 2020-02-27 | 2020-09-18 | 2020-09-18 | 2020-09-18 | 2020-02-27 | Agent Input |
| variants_number | 26 | 21 | 12 | 138 | 26 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | Agent Input |


### peripheral vascular disease

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005217 | PGS002055 | PGS005158 | PGS001843 | PGS001843 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 4/4 | Benchmark Only |
| AoU benchmark AUC | 0.5862 | 0.5195 | 0.5176 | 0.5123 | 0.5123 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 9/10 trials | Benchmark Only |
| trait_reported | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral vascular disease, unspecified | Agent Input |
| trait_efo | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | peripheral vascular disease | peripheral vascular disease | Agent Input |
| phenotyping_reported | Incident and prevelant peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease in type 2 diabetes | Peripheral vascular disease, unspecified | Peripheral vascular disease, unspecified | Agent Input |
| method_name | LDpred2 | LDpred2 (bigsnpr) | Genome-wide significant SNPs | Penalized regression (bigstatsr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7310 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | 0.3166 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=304,294 | n=19,668 | n=10,836 | n=19,668 | n=19,668 | Agent Input |
| samples_training | n=96,239 | n=391,124 | N/A | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: AFR (20%), AMR (8%), EUR (72%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | Agent Input |
| training_development_cohorts | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Modifiable Lifestyle Factors, Genetic Risk, and Incident Peripheral Artery Disease Among Individuals With Type 2 Diabetes: A Prospective Study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | JAMA Cardiol | Am J Hum Genet | Diabetes Care | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2025-06-16 | 2022-01-10 | 2025-02-26 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 1296292 | 599514 | 19 | 242 | 242 | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | age (continuous, years), sex (male, female), Townsend Deprivation Index (continuous), race/ethnicity (White, others), education attainment (college or university degree, A/AS levels or equivalent or O levels/GCSEs or equivalent or other professional qualifications, or none of the above), family history of CVD (yes, no), prevalence of hypertension (yes, no), use of antihypertensive medication (yes, no), use of lipidlowing medication (yes, no), use of aspirin (yes, no), diabetes duration (continuous, years), HbA1c (continuous, %), use of diabetes medication (none, only oral medication pills, or only insulin or combination of oral medications and insulin), genotype measurement batch, the first 10 principal components of ancestry, weighted healthy lifestyle scores (continuous) | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### hashimoto's thyroiditis

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005272 | PGS005271 | PGS005270 | PGS005270 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.7941 | 0.7940 | 0.6412 | 0.6412 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Agent Input |
| trait_efo | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Agent Input |
| phenotyping_reported | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6054 | 0.6297 | 0.6387 | 0.6387 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1085142 | 1085156 | 55 | 55 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Agent Input |


### preeclampsia

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003586 | PGS004593 | PGS003587 | PGS003586 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.8077 | 0.7604 | 0.5709 | 0.8077 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Pre-eclampsia | Preeclampsia | Gestational hypertension | Pre-eclampsia | Agent Input |
| trait_efo | preeclampsia | preeclampsia | preeclampsia | preeclampsia | Agent Input |
| phenotyping_reported | Pre-eclampsia/eclampsia | Gestational hypertension | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=25,582 | n=138,317 | n=25,582 | n=25,582 | Agent Input |
| samples_training | n=212,034 | N/A | n=212,034 | n=212,034 | Agent Input |
| ancestry_distribution | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (1%), ASN (7%), EUR (91%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | N/A | BBJ BioMe EB FinnGen G&H MGBB UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | Agent Input |
| publication.title | Polygenic prediction of preeclampsia and gestational hypertension. | Associations of polygenic risk scores for preeclampsia and blood pressure with hypertensive disorders of pregnancy. | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | Agent Input |
| publication.journal | Nat Med | J Hypertens | Nat Med | Nat Med | Agent Input |
| date_release | 2023-06-22 | 2024-01-26 | 2023-06-22 | 2023-06-22 | Agent Input |
| variants_number | 1087033 | 1102059 | 1087916 | 1087033 | Agent Input |
| covariates | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Collection year, genotyping batch, and the first 10 genetic principal components | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Agent Input |


### skin carcinoma in situ

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000471 | PGS000470 | PGS000469 | PGS000471 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.6010 | 0.5529 | 0.5041 | 0.6010 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| trait_efo | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | Agent Input |
| phenotyping_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| method_name | lassosum | Pruning and Thresholding (P+T) | PRS-CS | lassosum | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.5690 | 0.5570 | 0.5240 | 0.5690 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=5,500 | n=5,500 | n=5,500 | n=5,500 | Agent Input |
| samples_training | n=6,005 | n=6,005 | n=6,005 | n=6,005 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | MGI | MGI | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 7 | 5 | 1119238 | 7 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### vitiligo

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000760 | PGS000738 | PGS001536 | PGS001536 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.6417 | 0.6276 | 0.5669 | 0.5669 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Vitiligo | Vitiligo | Vitiligo (time-to-event) | Vitiligo (time-to-event) | Agent Input |
| trait_efo | Vitiligo | Vitiligo | Vitiligo | Vitiligo | Agent Input |
| phenotyping_reported | anti-PD-L1 induced hypothyroidism in cancer patients | Vitiligo | TTE vitiligo | TTE vitiligo | Agent Input |
| method_name | GCTA-COJO forward selection highest PPA variants | Genome-wide significant variants | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.8277 | 0.8277 | Agent Input |
| performance_metrics.r2 | N/A | 0.0325 | 0.0805 | 0.0805 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=1,584 | n=4,987 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=408,959 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-06-11 | 2021-02-23 | 2021-11-25 | 2021-11-25 | Agent Input |
| variants_number | 42 | 48 | 77 | 77 | Agent Input |
| covariates | 5 genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |

