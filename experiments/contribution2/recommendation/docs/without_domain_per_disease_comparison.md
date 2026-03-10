# Without Domain Knowledge: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison built from the without-domain experiment summary and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes all models in the benchmark `Target_TopK` set, listed in benchmark order as `Target #1..#K`.

## High-Level Outcome

- Without Domain Knowledge: `19/30 = 63.33%`; `trial_hits = 190/300 = 63.33%`
- Baseline: `11/30 = 36.67%`

## Per-Disease Tables

### prostate cancer

Candidate pool: `96` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS005237 | PGS001291 | Agent Input |
| AoU benchmark rank | 1/95 | 72/95 | 18/95 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.5205 | 0.5551 | Benchmark Only |
| In Target_TopK | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Prostate cancer | Prostate carcinoma | Prostate cancer | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | 5-year incident prostate cancer | Prostate cancer | Agent Input |
| method_name | PRS-CS | SCT (Stacked Clumping and Thresholding) | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.5910 | 0.8450 | 0.9701 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.4016 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=184,010 | n=67,425 | Agent Input |
| samples_training | n=5,650 | n=10,000 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | MGI | UKB | UKB | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | HGG Adv | PLoS Genet | Agent Input |
| date_release | 2020-12-15 | 2025-10-06 | 2021-10-21 | Agent Input |
| variants_number | 1111494 | 517551 | 948 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | - | age, sex, UKB array type, Genotype PCs | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS001289 | PGS001289 | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 24/32 | 24/32 | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.5636 | 0.5636 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid cancer | Thyroid cancer | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | Thyroid cancer | Thyroid cancer | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6845 | 0.6135 | 0.6174 | 0.8323 | 0.8323 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.1670 | 0.1670 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 11 | 11 | Agent Input |
| covariates | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### hypothyroidism

Candidate pool: `28` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005268 | PGS005218 | PGS005218 | Agent Input |
| AoU benchmark rank | 1/28 | 3/28 | 3/28 | Benchmark Only |
| AoU benchmark AUC | 0.6575 | 0.6289 | 0.6289 | Benchmark Only |
| In Target_TopK | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | Agent Input |
| phenotyping_reported | hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| method_name | PRSCS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6389 | 0.8590 | 0.8590 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=441,692 | n=441,692 | Agent Input |
| samples_training | N/A | n=1,146,562 | n=1,146,562 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | 23andMe CHB DBDS EB FinnGen UKB deCODE | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Agent Input |
| publication.journal | medRxiv | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2025-11-10 | 2025-11-10 | Agent Input |
| variants_number | 1085173 | 1110091 | 1110091 | Agent Input |
| covariates | Unknown | age, sex, PC1, PC2, PC3, PC4 | age, sex, PC1, PC2, PC3, PC4 | Agent Input |


### hodgkins lymphoma

Candidate pool: `27` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000639 | PGS003449 | PGS000638 | PGS000639 | PGS000874 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 1/27 | 10/27 | Benchmark Only |
| AoU benchmark AUC | 0.6180 | 0.6120 | 0.6014 | 0.6180 | 0.5379 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Hodgkin's disease | Hodgkin lymphoma | Hodgkin's disease | Hodgkin's disease | Chronic lymphocytic leukemia | Agent Input |
| trait_efo | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | chronic lymphocytic leukemia | Agent Input |
| phenotyping_reported | Hodgkin's disease | Chronic lymphocytic leukemia | Hodgkin's disease | Hodgkin's disease | Chronic lymphocytic leukemia | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | GWAS Hits | Pruning and Thresholding (P+T) | Representative SNPs from chronic lymphocytic leukemia susceptibility loci | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6200 | N/A | 0.6010 | 0.6200 | 0.8610 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=775 | n=20,134 | n=775 | n=775 | n=3,958 | Agent Input |
| samples_training | n=736 | N/A | n=736 | n=736 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: NR (50%), AFR (12%), EUR (25%), MAE (12%) | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | MGI | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Association of polygenic risk score with the risk of chronic lymphocytic leukemia and monoclonal B-cell lymphocytosis. | Agent Input |
| publication.journal | Am J Hum Genet | Leukemia | Am J Hum Genet | Am J Hum Genet | Blood | Agent Input |
| date_release | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2020-12-15 | 2021-08-26 | Agent Input |
| variants_number | 20 | 21 | 16 | 20 | 41 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Age, sex, study, socioeconomic status (when available) | Agent Input |


### obstructive sleep apnea

Candidate pool: `20` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005220 | PGS005219 | Agent Input |
| AoU benchmark rank | 1/20 | 1/20 | 2/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5784 | 0.5454 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7900 | 0.7900 | 0.7900 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 984184 | 982740 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### sleep apnea

Candidate pool: `20` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005220 | PGS005219 | Agent Input |
| AoU benchmark rank | 1/20 | 1/20 | 2/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5784 | 0.5454 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7900 | 0.7900 | 0.7900 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 984184 | 982740 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### testicular neoplasm

Candidate pool: `14` models. Benchmark `Target_TopK`: `5`.


| Field | Target #1 | Target #2 | Target #3 | Target #4 | Target #5 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | PGS001164 | PGS001164 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 3/13 | 3/13 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | 0.9044 | 0.9044 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | Benchmark target #4 | Benchmark target #5 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Testicular cancer | Agent Input |
| trait_efo | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | Agent Input |
| phenotyping_reported | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Testicular cancer | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | lassosum | snpnet | Pruning and Thresholding (P+T) | lassosum | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7870 | 0.6360 | 0.9816 | 0.6370 | 0.6560 | 0.9816 | 0.9816 | Agent Input |
| performance_metrics.r2 | 0.6050 | N/A | 0.2970 | N/A | N/A | 0.2970 | 0.2970 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=179,537 | n=755 | n=67,425 | n=755 | n=755 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | n=776 | n=269,704 | n=776 | n=776 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | MGI | UKB | MGI | MGI | UKB | UKB | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-05-28 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 52 | 250 | 280 | 31 | 771 | 280 | 280 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### uterine carcinoma

Candidate pool: `14` models. Benchmark `Target_TopK`: `4`.


| Field | Target #1 | Target #2 | Target #3 | Target #4 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002735 | PGS001795 | PGS001299 | Agent Input |
| AoU benchmark rank | 1/14 | 2/14 | 3/14 | 4/14 | 9/14 | 10/14 | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5609 | 0.5044 | 0.4564 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | Benchmark target #4 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Uterine cancer | Cervical cancer | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | uterine carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Risk of endometrial cancer | Uterine cancer | Cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | PRS-CS-auto | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7550 | 0.7540 | 0.7610 | 0.5600 | 0.6600 | 0.9143 | Agent Input |
| performance_metrics.r2 | N/A | 0.4860 | 0.1100 | N/A | N/A | 0.2202 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=221,699 | n=212,156 | n=144,479 | n=118,636 | n=170,276 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,757 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (15%), EUR (84%), OTH (80%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | BBJ BioMe BioVU CCPM CKB EB FinnGen HUNT MGBB MGI deCODE | UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Development and evaluation of polygenic risk scores for prediction of endometrial cancer risk in European women. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Genet Med | Cell Genom | PLoS Genet | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-07-21 | 2022-09-08 | 2021-10-21 | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 911692 | 24 | Agent Input |
| covariates | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, 10 PCs. | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### kidney cancer

Candidate pool: `10` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS004908 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/10 | 1/10 | 1/10 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5824 | 0.5824 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7400 | 0.7400 | 0.7400 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=324,805 | n=324,805 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | BBJ FinnGen NCI | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2024-05-22 | 2024-05-22 | Agent Input |
| variants_number | 107 | 107 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### obesity

Candidate pool: `10` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS001298 | PGS001298 | Agent Input |
| AoU benchmark rank | 1/10 | 8/10 | 8/10 | Benchmark Only |
| AoU benchmark AUC | 0.6311 | 0.5549 | 0.5549 | Benchmark Only |
| In Target_TopK | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Adiposity | Obesity (time-to-event) | Obesity (time-to-event) | Agent Input |
| trait_efo | obesity | obesity | obesity | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | TTE obesity | TTE obesity | Agent Input |
| method_name | LDpred2-auto | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | 0.6533 | 0.6533 | Agent Input |
| performance_metrics.r2 | N/A | 0.0423 | 0.0423 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | UKB | UKB | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2025-10-06 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 709828 | 9227 | 9227 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS001268 | PGS001268 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 3/9 | 3/9 | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7362 | 0.7362 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis (time-to-event) | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | TTE ankylosing spondylitis | TTE ankylosing spondylitis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | 0.9891 | 0.9915 | 0.9915 | 0.9915 | Agent Input |
| performance_metrics.r2 | N/A | 0.4432 | 0.4486 | 0.4486 | 0.4486 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 85 | 10 | 10 | 10 | 10 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### aortic stenosis

Candidate pool: `8` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS005252 | PGS005252 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 8/8 | 8/8 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.3445 | 0.3445 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Aortic stenosis | Aortic stenosis | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | aortic stenosis | aortic stenosis | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Incident aortic stenosis cases | Incident aortic stenosis cases | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | LDPred2 | LDPred2 | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.8700 | 0.8700 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=446,895 | n=446,895 | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | n=47,691 | n=47,691 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | MGBB | MGBB | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 1119377 | 1119377 | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | Agent Input |


### renal carcinoma

Candidate pool: `8` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS004908 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/8 | 1/8 | 1/8 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5824 | 0.5824 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7400 | 0.7400 | 0.7400 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=324,805 | n=324,805 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | BBJ FinnGen NCI | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2024-05-22 | 2024-05-22 | Agent Input |
| variants_number | 107 | 107 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### graves disease

Candidate pool: `7` models. Benchmark `Target_TopK`: `2`.


| Field | Target #1 | Target #2 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005265 | PGS001042 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 2/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.7677 | 0.7535 | 0.7535 | 0.6290 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | TTE thyrotoxicosis [hyperthyroidism] | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6637 | 0.6652 | 0.6652 | 0.7429 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0808 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1085173 | 1085173 | 226 | Agent Input |
| covariates | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### nodular goiter

Candidate pool: `7` models. Benchmark `Target_TopK`: `2`.


| Field | Target #1 | Target #2 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005263 | PGS005262 | PGS005262 | PGS005273 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 2/7 | 6/7 | Benchmark Only |
| AoU benchmark AUC | 0.7033 | 0.6911 | 0.6911 | 0.4540 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Agent Input |
| trait_efo | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | benign, thyroid carcinoma, nodular goiter | Agent Input |
| phenotyping_reported | benign nodular gioter | benign nodular gioter | benign nodular gioter | thyroid carcenoma vs benign nodular goiter | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.5876 | 0.5933 | 0.5933 | 0.6174 | Agent Input |
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
| training_development_cohorts | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1085170 | 1085173 | 1085173 | 1085164 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. Benchmark `Target_TopK`: `4`.


| Field | Target #1 | Target #2 | Target #3 | Target #4 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS001280 | PGS001279 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 2/7 | 4/7 | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5916 | 0.5885 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | Benchmark target #4 | 7/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | PE (time-to-event) | previously: Blood clot in the lung | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | TTE PE | Blood clot in the lung | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6674 | 0.8074 | 0.8083 | 0.8256 | 0.8074 | 0.8256 | Agent Input |
| performance_metrics.r2 | 0.0364 | 0.1233 | 0.1233 | 0.1674 | 0.1233 | 0.1674 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=67,349 | n=67,425 | n=67,425 | n=67,349 | n=67,425 | n=67,349 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=269,704 | n=269,382 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 88 | 94 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS003973 | PGS003973 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 1/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.6374 | 0.6374 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.8820 | 0.7080 | 0.6900 | 0.8820 | 0.8820 | Agent Input |
| performance_metrics.r2 | N/A | 0.0055 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=7,324 | n=7,517 | n=7,517 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2023-11-01 | 2023-11-01 | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 1118997 | 1118997 | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | Age, Age^2, Sex | Age, Age^2, Sex | Agent Input |


### age-related macular degeneration

Candidate pool: `6` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004606 | PGS002269 | PGS004952 | PGS004606 | PGS004952 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 1/6 | 3/6 | Benchmark Only |
| AoU benchmark AUC | 0.6547 | 0.6530 | 0.6512 | 0.6547 | 0.6512 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 6/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | Agent Input |
| phenotyping_reported | Age-related macular degeneration | Rentinal layer thickness (photoreceptor inner and outer segments) | Early age-related macular degeneration (Clinical Classification) | Age-related macular degeneration | Early age-related macular degeneration (Clinical Classification) | Agent Input |
| method_name | PRS-CS | Independent variants associated with AMD | Genome-wide significant SNPs | PRS-CS | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7100 | N/A | 0.8420 | 0.7100 | 0.8420 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=163,011 | n=44,823 | n=1,780 | n=163,011 | n=1,780 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | IAMDGC | IAMDGC | Agent Input |
| publication.title | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Agent Input |
| publication.journal | Nat Genet | Ophthalmology | Invest Ophthalmol Vis Sci | Nat Genet | Invest Ophthalmol Vis Sci | Agent Input |
| date_release | 2024-02-20 | 2022-04-01 | 2024-09-19 | 2024-02-20 | 2024-09-19 | Agent Input |
| variants_number | 1000946 | 47 | 52 | 1000946 | 52 | Agent Input |
| covariates | age, sex, principal components 1-10 | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | Age, sex, survey membership, 10 PCs | age, sex, principal components 1-10 | Age, sex, survey membership, 10 PCs | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS001299 | PGS001299 | Agent Input |
| AoU benchmark rank | 1/6 | 6/6 | 6/6 | Benchmark Only |
| AoU benchmark AUC | 0.6925 | 0.3401 | 0.3401 | Benchmark Only |
| In Target_TopK | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7450 | 0.9143 | 0.9143 | Agent Input |
| performance_metrics.r2 | N/A | 0.2202 | 0.2202 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=226,216 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | TwinGene | UKB | UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2020-02-12 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 10 | 24 | 24 | Agent Input |
| covariates | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, 10 PCs. | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### cutaneous melanoma

Candidate pool: `5` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS003382 | PGS003382 | Agent Input |
| AoU benchmark rank | 1/5 | 1/5 | 1/5 | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.6239 | 0.6239 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Skin cutaneous melanoma | Skin cutaneous melanoma | Agent Input |
| trait_efo | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | skin cutaneous melanoma | skin cutaneous melanoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.6820 | 0.6820 | 0.6820 | Agent Input |
| performance_metrics.r2 | 0.0261 | 0.0261 | 0.0261 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=273,786 | n=273,786 | n=273,786 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Agent Input |
| publication.journal | Cancer Res | Cancer Res | Cancer Res | Agent Input |
| date_release | 2023-01-19 | 2023-01-19 | 2023-01-19 | Agent Input |
| variants_number | 672 | 672 | 672 | Agent Input |
| covariates | age, sex, top 20 genetic principal components | age, sex, top 20 genetic principal components | age, sex, top 20 genetic principal components | Agent Input |


### late-onset alzheimer's disease

Candidate pool: `5` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000054 | PGS004918 | PGS004918 | Agent Input |
| AoU benchmark rank | 1/5 | 4/5 | 4/5 | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5114 | 0.5114 | Benchmark Only |
| In Target_TopK | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 6/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Alzheimer's disease (late onset) | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Agent Input |
| trait_efo | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | Agent Input |
| phenotyping_reported | Familial late-onset Alzheimer's disease (LOAD) | Late-onset Alzheimer's disease | Late-onset Alzheimer's disease | Agent Input |
| method_name | Genome-wide significant variants | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | 0.7310 | 0.7310 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=3,324 | n=136 | n=136 | Agent Input |
| samples_training | N/A | n=439 | n=439 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ADGC BfDR CHARGE EADI GERAD | ADGC BfDR CHARGE EADI GERAD | Agent Input |
| publication.title | Polygenic risk scores in familial Alzheimer disease. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Agent Input |
| publication.journal | Neurology | Neurobiol Aging | Neurobiol Aging | Agent Input |
| date_release | 2019-12-18 | 2024-06-12 | 2024-06-12 | Agent Input |
| variants_number | 21 | 8 | 8 | Agent Input |
| covariates | Age, sex | Unknown | Unknown | Agent Input |


### open-angle glaucoma

Candidate pool: `5` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004944 | PGS004944 | PGS001797 | Agent Input |
| AoU benchmark rank | 1/5 | 1/5 | 2/5 | Benchmark Only |
| AoU benchmark AUC | 0.6405 | 0.6405 | 0.6264 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Agent Input |
| trait_efo | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | Agent Input |
| phenotyping_reported | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Agent Input |
| method_name | Lassosum | Lassosum | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7480 | 0.7480 | 0.7490 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=407,667 | n=407,667 | n=7,128 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), ASN (60%), EAS (18%), EUR (79%), OTH (60%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI TWB UCLA UKB | Agent Input |
| publication.title | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | JAMA Ophthalmol | JAMA Ophthalmol | Cell Genom | Agent Input |
| date_release | 2024-08-29 | 2024-08-29 | 2022-09-08 | Agent Input |
| variants_number | 144019 | 144019 | 885417 | Agent Input |
| covariates | Age, age2, sex, ancestry | Age, age2, sex, ancestry | sex,age, 20PCs | Agent Input |


### alcohol dependence

Candidate pool: `4` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002738 | PGS002738 | N/A | Agent Input |
| AoU benchmark rank | 1/4 | 1/4 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6051 | 0.6051 | N/A | Benchmark Only |
| In Target_TopK | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Alcohol use disorder | Alcohol use disorder | N/A | Agent Input |
| trait_efo | alcohol dependence | alcohol dependence | N/A | Agent Input |
| phenotyping_reported | Alcohol use disorder (AUD) in individuals with family history of AUD | Alcohol use disorder (AUD) in individuals with family history of AUD | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=7,900 | n=7,900 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | MVP UKB | MVP UKB | N/A | Agent Input |
| publication.title | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | N/A | Agent Input |
| publication.journal | Alcohol Clin Exp Res | Alcohol Clin Exp Res | N/A | Agent Input |
| date_release | 2022-08-03 | 2022-08-03 | N/A | Agent Input |
| variants_number | 326000 | 326000 | N/A | Agent Input |
| covariates | Unknown | Unknown | N/A | Agent Input |


### hypertrophic cardiomyopathy

Candidate pool: `4` models. Benchmark `Target_TopK`: `3`.


| Field | Target #1 | Target #2 | Target #3 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004911 | PGS000739 | PGS004910 | PGS004911 | PGS000739 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 1/4 | 2/4 | Benchmark Only |
| AoU benchmark AUC | 0.6036 | 0.5891 | 0.5873 | 0.6036 | 0.5891 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | Benchmark target #3 | 8/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Agent Input |
| trait_efo | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | Genome-wide significant variants | PRS-CS | PRS-CS | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.8000 | 0.8210 | 0.7300 | 0.8000 | 0.8210 | Agent Input |
| performance_metrics.r2 | 0.0480 | N/A | 0.0310 | 0.0480 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=343,182 | n=184,511 | n=343,182 | n=343,182 | n=184,511 | Agent Input |
| samples_training | N/A | n=47,737 | N/A | N/A | n=47,737 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | Agent Input |
| training_development_cohorts | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | Agent Input |
| publication.title | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-02-26 | 2021-02-23 | 2025-02-26 | 2025-02-26 | 2021-02-23 | Agent Input |
| variants_number | 374114 | 27 | 374190 | 374114 | 27 | Agent Input |
| covariates | age, age^2, sex, PC1-10 | Age, gender, PCs(1-10) | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | Age, gender, PCs(1-10) | Agent Input |


### juvenile idiopathic arthritis

Candidate pool: `4` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000114 | PGS000114 | PGS000324 | Agent Input |
| AoU benchmark rank | 1/4 | 1/4 | 4/4 | Benchmark Only |
| AoU benchmark AUC | 0.5768 | 0.5768 | 0.5230 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Enthesitis-related Juvenile Idiophatic Arthritis | Agent Input |
| trait_efo | juvenile idiopathic arthritis | juvenile idiopathic arthritis | enthesitis-related juvenile idiopathic arthritis | Agent Input |
| phenotyping_reported | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Enthesitis-related Arthritis | Agent Input |
| method_name | SparSNP | SparSNP | SparSNP | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7380 | 0.7380 | 0.9300 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=3,513 | n=3,513 | n=3,020 | Agent Input |
| samples_training | n=7,505 | n=7,505 | n=5,354 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | Agent Input |
| publication.title | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Agent Input |
| publication.journal | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Agent Input |
| date_release | 2020-02-27 | 2020-02-27 | 2020-09-18 | Agent Input |
| variants_number | 26 | 26 | 138 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Agent Input |


### peripheral vascular disease

Candidate pool: `4` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005217 | PGS001843 | PGS005217 | Agent Input |
| AoU benchmark rank | 1/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.5862 | 0.5123 | 0.5862 | Benchmark Only |
| In Target_TopK | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 9/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Agent Input |
| trait_efo | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | Agent Input |
| phenotyping_reported | Incident and prevelant peripheral artery disease | Peripheral vascular disease, unspecified | Incident and prevelant peripheral artery disease | Agent Input |
| method_name | LDpred2 | Penalized regression (bigstatsr) | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.7310 | N/A | 0.7310 | Agent Input |
| performance_metrics.r2 | 0.3166 | N/A | 0.3166 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=304,294 | n=19,668 | n=304,294 | Agent Input |
| samples_training | n=96,239 | n=391,124 | n=96,239 | Agent Input |
| ancestry_distribution | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | Agent Input |
| training_development_cohorts | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | Agent Input |
| publication.title | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Agent Input |
| publication.journal | JAMA Cardiol | Am J Hum Genet | JAMA Cardiol | Agent Input |
| date_release | 2025-06-16 | 2022-01-10 | 2025-06-16 | Agent Input |
| variants_number | 1296292 | 242 | 1296292 | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | age, sex and the first ten principal components of genetic ancestry | Agent Input |


### hashimoto's thyroiditis

Candidate pool: `3` models. Benchmark `Target_TopK`: `2`.


| Field | Target #1 | Target #2 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005272 | PGS005271 | PGS005270 | PGS005270 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.7941 | 0.7940 | 0.6412 | 0.6412 | Benchmark Only |
| In Target_TopK | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | Benchmark target #2 | 10/10 trials | Rule-based baseline | Benchmark Only |
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

Candidate pool: `3` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003586 | PGS003586 | N/A | Agent Input |
| AoU benchmark rank | 1/3 | 1/3 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.8077 | 0.8077 | N/A | Benchmark Only |
| In Target_TopK | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Pre-eclampsia | Pre-eclampsia | N/A | Agent Input |
| trait_efo | preeclampsia | preeclampsia | N/A | Agent Input |
| phenotyping_reported | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=25,582 | n=25,582 | N/A | Agent Input |
| samples_training | n=212,034 | n=212,034 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | N/A | Agent Input |
| publication.title | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | N/A | Agent Input |
| publication.journal | Nat Med | Nat Med | N/A | Agent Input |
| date_release | 2023-06-22 | 2023-06-22 | N/A | Agent Input |
| variants_number | 1087033 | 1087033 | N/A | Agent Input |
| covariates | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | N/A | Agent Input |


### skin carcinoma in situ

Candidate pool: `3` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000471 | PGS000471 | PGS000471 | Agent Input |
| AoU benchmark rank | 1/3 | 1/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.6010 | 0.6010 | 0.6010 | Benchmark Only |
| In Target_TopK | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| trait_efo | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | Agent Input |
| phenotyping_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| method_name | lassosum | lassosum | lassosum | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | 0.5690 | 0.5690 | 0.5690 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=5,500 | n=5,500 | n=5,500 | Agent Input |
| samples_training | n=6,005 | n=6,005 | n=6,005 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | MGI | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 7 | 7 | 7 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### vitiligo

Candidate pool: `3` models. Benchmark `Target_TopK`: `1`.


| Field | Target #1 | Without Domain Knowledge | Baseline | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000760 | PGS001536 | PGS001536 | Agent Input |
| AoU benchmark rank | 1/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.6417 | 0.5669 | 0.5669 | Benchmark Only |
| In Target_TopK | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark target #1 | 10/10 trials | Rule-based baseline | Benchmark Only |
| trait_reported | Vitiligo | Vitiligo (time-to-event) | Vitiligo (time-to-event) | Agent Input |
| trait_efo | Vitiligo | Vitiligo | Vitiligo | Agent Input |
| phenotyping_reported | anti-PD-L1 induced hypothyroidism in cancer patients | TTE vitiligo | TTE vitiligo | Agent Input |
| method_name | GCTA-COJO forward selection highest PPA variants | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | N/A | N/A | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | N/A | N/A | N/A | Agent Input |
| performance_metrics.record_count | N/A | N/A | N/A | Agent Input |
| performance_metrics.auc | N/A | 0.8277 | 0.8277 | Agent Input |
| performance_metrics.r2 | N/A | 0.0805 | 0.0805 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=1,584 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=408,959 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | Agent Input |
| publication.title | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-06-11 | 2021-11-25 | 2021-11-25 | Agent Input |
| variants_number | 42 | 77 | 77 | Agent Input |
| covariates | 5 genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |

