# Prompt-Only Baseline: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison built from the prompt-only baseline experiment summary and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes the benchmark top-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models).
Rows `Hit@1`..`Hit@5` are evaluated over the full disease/trial set; when a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models for that disease.

## High-Level Outcome

- Prompt-Only Baseline `Hit@1`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@2`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@3`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@4`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@5`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean r / M = N/A` (0 modal selections); `trial mean r / M = N/A` (0 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean (M - r) / M = N/A` (0 modal selections); `trial mean (M - r) / M = N/A` (0 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Prompt-Only Baseline: `mean NRS = N/A` (0 modal selections); `trial mean NRS = N/A` (0 trials)


## Per-Disease Tables

### prostate cancer

Candidate pool: `96` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS000044 | PGS001292 | PGS000592 | PGS002793 | N/A | Agent Input |
| AoU benchmark rank | 1/95 | 2/95 | 3/95 | 4/95 | 5/95 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.6295 | 0.6041 | 0.5748 | 0.5665 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Prostate cancer | Prostate cancer | Family history of prostate cancer | Prostate cancer | Prostate cancer | N/A | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | family history of prostate cancer | prostate carcinoma | prostate carcinoma | N/A | Agent Input |
| phenotyping_reported | Cancer of prostate | Elevated serum prostate-specific antigen (PSA) levels | Prostate cancer (FH) | Cancer of prostate | Prostate cancer risk | N/A | Agent Input |
| method_name | PRS-CS | Known susceptibility loci (genome-wide significant SNPs) | snpnet | lassosum | Genome-wide significant SNPs | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM001251 | PPM000104 | PPM008960 | PPM001277 | PPM015450 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | N/A | Agent Input |
| performance_metrics.record_count | 1 | 2 | 5 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5487 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0055 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5910 | N/A | 0.5657 | 0.6160 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0245 | N/A | 0.0115 | 0.0408 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0170 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.573, 'ci_upper': 0.609} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56572, 'ci_lower': 0.5538, 'ci_upper': 0.57764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.616, 'ci_lower': 0.598, 'ci_upper': 0.635} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0245} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.152} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.85, 'ci_lower': 1.76, 'ci_upper': 4.62} | {'name_long': 'OR (per 1-point increase in PRS)', 'name_short': 'OR (per 1-point increase in PRS)', 'estimate': 1.23, 'ci_lower': 1.1, 'ci_upper': 1.37} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01155} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01702} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00547} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.54869, 'ci_lower': 0.53677, 'ci_upper': 0.56062} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0408} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.15} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.55, 'ci_lower': 1.55, 'ci_upper': 4.2} | {'name_long': 'Odds Ratio (OR, top vs average percentile)', 'name_short': 'Odds Ratio (OR, top vs average percentile)', 'estimate': 2.87, 'ci_lower': 1.29, 'ci_upper': 6.4} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.393, 'ci_lower': 1.3, 'ci_upper': 1.493} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.332, 'se': 0.0352} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.537, 'ci_lower': 1.433, 'ci_upper': 1.648} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.43, 'se': 0.0357} | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=17,012 | n=24,905 | n=5,607 | n=1,190 | N/A | Agent Input |
| samples_training | n=5,650 | N/A | n=269,704 | n=5,650 | n=109,323 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (5%), EUR (95%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (2%), AMR (40%), EAS (1%), EUR (92%), MAE (3%) / DEV: AFR (3%), EAS (1%), EUR (96%) / EVAL: EAS (100%) | N/A | Agent Input |
| training_development_cohorts | MGI | ICR IGD PLCO ProtecT UKGPCS deCODE | UKB | MGI | AAPC BCFR BFBOCC BRICOH CBCS CIMBA CNIO CONSIT Chicago DEMOKRITOS DKFZ EMBRACE FCCC G-FaST GC-HBOC GEMO HCSC HEBCS HEBON HUNBOCS HVH ICO ICR IGD ILUH IOVHBOCS IPOBCS MAYO MSKCC MUV NCI OCGN OSU OUH PBCS PLCO ProtecT SWE-BRCA UKB UKGPCS UPENN UPITT VFCTG deCODE kConFab | N/A | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Reducing overdiagnosis by polygenic risk-stratified screening: findings from the Finnish section of the ERSPC. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Application of European-specific polygenic risk scores for predicting prostate cancer risk in different ancestry populations. | N/A | Agent Input |
| publication.journal | Am J Hum Genet | Br J Cancer | PLoS Genet | Am J Hum Genet | Prostate | N/A | Agent Input |
| date_release | 2020-12-15 | 2019-12-18 | 2021-10-21 | 2020-12-15 | 2022-09-29 | N/A | Agent Input |
| variants_number | 1111494 | 66 | 602 | 1334 | 82 | N/A | Agent Input |
| covariates | age, sex, batch PCs 1-4 | cancer stage, Gleason score | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | disease diagnostic age or age at recruitment, subgroups and 10 principal components | N/A | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS005259 | PGS005258 | N/A | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 4/32 | 5/32 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma | Thyroid carcenoma | N/A | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | N/A | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma | thyroid carcenoma | N/A | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | Pruning and Thresholding (P+T) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022743 | PPM022757 | PPM022756 | PPM022742 | PPM022741 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6845 | 0.6135 | 0.6174 | 0.6953 | 0.6862 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.684522760200784} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.613489463745261} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.617388005401901} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.695254013741303} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.686161285410893} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96019114706853} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.673041992501825} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49346171423604} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.401096723418125} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55051776688383} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.438588918302023} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.03688674186851} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.71142253524162} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.016} | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | N/A | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | N/A | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | N/A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | N/A | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 1085173 | 84 | N/A | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | N/A | Agent Input |


### hypothyroidism

Candidate pool: `28` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005268 | PGS005269 | PGS005218 | PGS005267 | PGS004789 | N/A | Agent Input |
| AoU benchmark rank | 1/28 | 2/28 | 3/28 | 4/28 | 5/28 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6575 | 0.6567 | 0.6289 | 0.6240 | 0.6231 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | N/A | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | N/A | Agent Input |
| phenotyping_reported | hypothyroidism | hypothyroidism | Incident hypothyroidism | hypothyroidism | Hypothyroidism | N/A | Agent Input |
| method_name | PRSCS | PRSCS | PRS-CS | Pruning and Thresholding (P+T) | PRSmix | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022751 | PPM022752 | PPM022617 | PPM022750 | PPM021014 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6389 | 0.6386 | 0.8590 | 0.6400 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0410 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638920940728866} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638628477117025} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.041, 'ci_lower': 0.033, 'ci_upper': 0.049} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65808867613792} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.505665539081399} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65210243632159} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.502048680634994} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.133} | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=441,692 | n=94,651 | n=9,462 | N/A | Agent Input |
| samples_training | N/A | N/A | n=1,146,562 | N/A | n=37,851 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | N/A | Agent Input |
| publication.journal | medRxiv | medRxiv | Nat Genet | medRxiv | Cell Genom | N/A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2025-11-10 | 2026-01-19 | 2024-03-28 | N/A | Agent Input |
| variants_number | 1085173 | 1085170 | 1110091 | 439 | 1109333 | N/A | Agent Input |
| covariates | Unknown | Unknown | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | Unknown | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | N/A | Agent Input |


### hodgkins lymphoma

Candidate pool: `27` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000639 | PGS003449 | PGS000638 | PGS003454 | PGS000648 | N/A | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 4/27 | 5/27 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6180 | 0.6120 | 0.6014 | 0.5597 | 0.5586 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Hodgkin's disease | Hodgkin lymphoma | Hodgkin's disease | Diffuse large B-cell lymphoma | Chronic lymphocytic leukemia | N/A | Agent Input |
| trait_efo | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | diffuse large B-cell lymphoma | chronic lymphocytic leukemia | N/A | Agent Input |
| phenotyping_reported | Hodgkin's disease | Chronic lymphocytic leukemia | Hodgkin's disease | Chronic lymphocytic leukemia | Lymphoid leukemia, chronic | N/A | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | GWAS Hits | Genome-wide significant SNPs | Pruning and Thresholding (P+T) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM001324 | PPM017231 | PPM001323 | PPM017225 | PPM001333 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 4 | 1 | 4 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6200 | N/A | 0.6010 | N/A | 0.6960 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0276 | N/A | 0.0193 | N/A | 0.1020 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.601, 'ci_lower': 0.535, 'ci_upper': 0.671} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.621, 'ci_upper': 0.764} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0193} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0824} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.62, 'ci_lower': 0.258, 'ci_upper': 10.1} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.102} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0776} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 12.9, 'ci_lower': 4.45, 'ci_upper': 37.6} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 0.97, 'ci_upper': 1.08} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.377, 'ci_lower': 1.08, 'ci_upper': 1.755} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.32, 'se': 0.124} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.14, 'ci_upper': 1.54} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.124, 'ci_lower': 1.648, 'ci_upper': 2.738} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.753, 'se': 0.13} | N/A | Agent Input |
| validation_sample_size | n=775 | n=20,134 | n=775 | n=20,134 | n=756 | N/A | Agent Input |
| samples_training | n=736 | N/A | n=736 | N/A | n=730 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | N/A | MGI | N/A | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | N/A | Agent Input |
| publication.journal | Am J Hum Genet | Leukemia | Am J Hum Genet | Leukemia | Am J Hum Genet | N/A | Agent Input |
| date_release | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2023-03-24 | 2020-12-15 | N/A | Agent Input |
| variants_number | 20 | 21 | 16 | 5 | 44 | N/A | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | N/A | Agent Input |


### obstructive sleep apnea

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005219 | PGS003479 | PGS003213 | PGS003857 | N/A | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Obstructive sleep apnea | Sleep apnea | Obstructive sleep apnea | N/A | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | obstructive sleep apnea | N/A | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | DBP | Sleep Apnea | BMI adjusted obstructive sleep apnea | N/A | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | LDpred2 | PRS-CS | Genome-wide significant SNPs | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022620 | PPM022619 | PPM017318 | PPM015955 | PPM018710 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Hispanic or Latin American | European | African unspecified, Asian unspecified, European, Hispanic or Latin American, Not reported | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 34 | 1 | 2 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.7900 | N/A | 0.5270 | 0.7700 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.527, 'ci_lower': 0.517, 'ci_upper': 0.536} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77, 'ci_lower': 0.75, 'ci_upper': 0.78} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.98, 'ci_lower': 1.74, 'ci_upper': 2.24} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.038, 'se': 0.093} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.106, 'ci_lower': 1.071, 'ci_upper': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.101, 'se': 0.0162} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.014, 'se': 0.017} | N/A | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=1,115 | n=21,354 | n=40,193 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=21,209 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (19%), AMR (8%), ASN (1%), EUR (72%) / EVAL: MAE (100%) | N/A | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | N/A | UKB | MVP | N/A | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Genetic determinants of cardiometabolic and pulmonary phenotypes and obstructive sleep apnoea in HCHS/SOL. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Genome-wide association study of obstructive sleep apnoea in the Million Veteran Program uncovers genetic heterogeneity by sex. | N/A | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | EBioMedicine | N/A | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2023-03-24 | 2022-11-23 | 2023-09-01 | N/A | Agent Input |
| variants_number | 984184 | 982740 | 836839 | 1111194 | 18 | N/A | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Age, sex, center, 5 genetic PCs, Hispanic/Latino background, BMI | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | BMI, age, sex, genetic batch, PCs 1-10 | N/A | Agent Input |


### sleep apnea

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005219 | PGS003479 | PGS003213 | PGS003857 | N/A | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Obstructive sleep apnea | Sleep apnea | Obstructive sleep apnea | N/A | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | obstructive sleep apnea | N/A | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | DBP | Sleep Apnea | BMI adjusted obstructive sleep apnea | N/A | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | LDpred2 | PRS-CS | Genome-wide significant SNPs | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022620 | PPM022619 | PPM017318 | PPM015955 | PPM018710 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Hispanic or Latin American | European | African unspecified, Asian unspecified, European, Hispanic or Latin American, Not reported | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 34 | 1 | 2 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.7900 | N/A | 0.5270 | 0.7700 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.527, 'ci_lower': 0.517, 'ci_upper': 0.536} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77, 'ci_lower': 0.75, 'ci_upper': 0.78} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.98, 'ci_lower': 1.74, 'ci_upper': 2.24} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.038, 'se': 0.093} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.106, 'ci_lower': 1.071, 'ci_upper': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.101, 'se': 0.0162} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.014, 'se': 0.017} | N/A | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=1,115 | n=21,354 | n=40,193 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=21,209 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (19%), AMR (8%), ASN (1%), EUR (72%) / EVAL: MAE (100%) | N/A | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | N/A | UKB | MVP | N/A | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Genetic determinants of cardiometabolic and pulmonary phenotypes and obstructive sleep apnoea in HCHS/SOL. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Genome-wide association study of obstructive sleep apnoea in the Million Veteran Program uncovers genetic heterogeneity by sex. | N/A | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | EBioMedicine | N/A | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2023-03-24 | 2022-11-23 | 2023-09-01 | N/A | Agent Input |
| variants_number | 984184 | 982740 | 836839 | 1111194 | 18 | N/A | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Age, sex, center, 5 genetic PCs, Hispanic/Latino background, BMI | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | BMI, age, sex, genetic batch, PCs 1-10 | N/A | Agent Input |


### testicular neoplasm

Candidate pool: `14` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | N/A | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | N/A | Agent Input |
| trait_efo | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | N/A | Agent Input |
| phenotyping_reported | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | N/A | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | lassosum | snpnet | Pruning and Thresholding (P+T) | lassosum | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM002067 | PPM001285 | PPM008544 | PPM001284 | PPM001282 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6296 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0157 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7870 | 0.6360 | 0.8391 | 0.6370 | 0.6560 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.6050 | 0.0460 | 0.1291 | 0.0473 | 0.0487 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0313 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.636, 'ci_lower': 0.565, 'ci_upper': 0.698} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.637, 'ci_lower': 0.568, 'ci_upper': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656, 'ci_lower': 0.593, 'ci_upper': 0.717} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.046} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0839} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 6.35, 'ci_lower': 1.81, 'ci_upper': 22.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0473} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0844} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.35, 'ci_lower': 1.08, 'ci_upper': 17.5} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.084} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.72, 'ci_lower': 0.568, 'ci_upper': 13.1} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.619, 'ci_lower': 1.267, 'ci_upper': 2.067} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.482, 'se': 0.125} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.628, 'ci_lower': 1.281, 'ci_upper': 2.069} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.487, 'se': 0.122} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.667, 'ci_lower': 1.296, 'ci_upper': 2.143} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.511, 'se': 0.128} | N/A | Agent Input |
| validation_sample_size | n=179,537 | n=755 | n=67,425 | n=755 | n=755 | N/A | Agent Input |
| samples_training | N/A | n=776 | n=269,704 | n=776 | n=776 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | MGI | UKB | MGI | MGI | N/A | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | N/A | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | N/A | Agent Input |
| date_release | 2021-05-28 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | N/A | Agent Input |
| variants_number | 52 | 250 | 280 | 31 | 771 | N/A | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | N/A | Agent Input |


### uterine carcinoma

Candidate pool: `14` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002735 | PGS004244 | N/A | Agent Input |
| AoU benchmark rank | 1/14 | 2/14 | 3/14 | 4/14 | 5/14 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5609 | 0.5519 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Endometrial cancer | N/A | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | N/A | Agent Input |
| phenotyping_reported | Incident endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Risk of endometrial cancer | Endometrial cancer | N/A | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | PRSice-2 | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM002041 | PPM002057 | PPM016256 | PPM014832 | PPM020301 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 2 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7550 | 0.7540 | 0.7610 | 0.5600 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4860 | 0.1100 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.755} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.754} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56, 'ci_lower': 0.54, 'ci_upper': 0.57} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': 'Odds ratio (OR, third vs first tertile)', 'name_short': 'Odds ratio (OR, third vs first tertile)', 'estimate': 1.55, 'ci_lower': 1.37, 'ci_upper': 1.74} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.1, 'ci_upper': 1.29} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.18, 'ci_lower': 1.09, 'ci_upper': 1.27} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.25, 'ci_lower': 1.14, 'ci_upper': 1.36} | N/A | Agent Input |
| validation_sample_size | n=212,156 | n=212,156 | n=144,479 | n=118,636 | n=133,830 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,757 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | N/A | N/A | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Development and evaluation of polygenic risk scores for prediction of endometrial cancer risk in European women. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | N/A | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Genet Med | NPJ Precis Oncol | N/A | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-07-21 | 2023-12-15 | N/A | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 16 | N/A | Agent Input |
| covariates | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | first 10 genetic principal components | N/A | Agent Input |


### kidney cancer

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS000787 | PGS000722 | PGS004245 | PGS000076 | N/A | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | N/A | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal cell carcinoma | renal cell carcinoma | N/A | Agent Input |
| phenotyping_reported | Kidney cancer | Incident kidney cancer | Incident kidney cancer | Kidney cancer | Incident kidney cancer | N/A | Agent Input |
| method_name | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM002058 | PPM001652 | PPM020302 | PPM002042 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 2 | 3 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | 0.7220 | 0.5670 | N/A | 0.7220 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.3660 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.723, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.543, 'ci_upper': 0.591} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.366} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.15, 'ci_lower': 1.07, 'ci_upper': 1.24} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.02, 'ci_upper': 1.45} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | N/A | Agent Input |
| validation_sample_size | n=324,805 | n=391,610 | n=400,812 | n=133,830 | n=391,610 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | N/A | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | N/A | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | N/A | Agent Input |
| publication.journal | Nat Genet | Nat Commun | JNCI Cancer Spectr | NPJ Precis Oncol | Nat Commun | N/A | Agent Input |
| date_release | 2024-05-22 | 2021-05-28 | 2021-02-03 | 2023-12-15 | 2020-02-12 | N/A | Agent Input |
| variants_number | 107 | 19 | 15 | 12 | 19 | N/A | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Genotyping array | first 10 genetic principal components | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | N/A | Agent Input |


### obesity

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005154 | PGS003959 | PGS002033 | PGS005145 | N/A | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6311 | 0.6165 | 0.5798 | 0.5753 | 0.5667 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Adiposity | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | N/A | Agent Input |
| trait_efo | obesity | obesity | obesity | obesity, overweight body mass index status, overnutrition | obesity | N/A | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | N/A | Agent Input |
| method_name | LDpred2-auto | CT-SLEB | Genome-wide significant SNPs | LDpred2 (bigsnpr) | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022667 | PPM022374 | PPM019107 | PPM011135 | PPM022365 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | East Asian | European, Not reported | European | East Asian | N/A | Agent Input |
| performance_metrics.record_count | 2 | 1 | 7 | 8 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0789, 'ci_lower': 0.0651, 'ci_upper': 0.0927} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.76187749677908} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.149, 'se': 0.028} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.60817500694587} | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=58,688 | n=27,429 | n=20,000 | n=58,688 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | GWAS: NR (33%), EUR (67%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EAS (100%) / EVAL: EAS (100%) | N/A | Agent Input |
| training_development_cohorts | EGG GIANT UKB | BBJ | N/A | UKB | BBJ | N/A | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | The sulfur microbial diet and increased risk of obesity: Findings from a population-based prospective cohort study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | N/A | Agent Input |
| publication.journal | Nat Commun | Commun Biol | Clin Nutr | Am J Hum Genet | Commun Biol | N/A | Agent Input |
| date_release | 2025-10-06 | 2025-03-17 | 2023-10-17 | 2022-01-10 | 2025-03-17 | N/A | Agent Input |
| variants_number | 709828 | 443124 | 940 | 846292 | 908466 | N/A | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex | Age, sex, race, centres, education, Townsend deprivation index, household income, smoking, alcohol consumption, physical activity, sleep pattern, energy intake, and BMI, WC or BF% at baseline | sex, age, birth date, deprivation index, 16 PCs | age, sex | N/A | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS002089 | PGS003424 | N/A | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7188 | 0.6491 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis | N/A | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | N/A | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | N/A | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | LDpred2 (bigsnpr) | LDpred2 | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM009896 | PPM008844 | PPM008849 | PPM011572 | PPM017077 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | N/A | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | 0.7265 | 0.7346 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0988 | 0.1023 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7433 | 0.7488 | N/A | 0.7605 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1092 | 0.1150 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.1299 | 0.1269 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7605} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0653, 'ci_upper': 0.0941} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0919, 'ci_lower': 0.0775, 'ci_upper': 0.1063} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=18,262 | n=1,298 | N/A | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=391,124 | N/A | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | N/A | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | N/A | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | N/A | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Am J Hum Genet | J Transl Med | N/A | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2022-01-10 | 2023-02-08 | N/A | Agent Input |
| variants_number | 85 | 10 | 10 | 22026 | 100 | N/A | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | N/A | Agent Input |


### aortic stenosis

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS004911 | PGS004910 | N/A | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.5181 | 0.5166 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | N/A | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | N/A | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022737 | PPM022738 | PPM022739 | PPM021367 | PPM021366 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.8000 | 0.7300 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0480 | 0.0310 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.4, 'ci_upper': 1.66} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.41, 'ci_upper': 1.67} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | N/A | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=343,182 | n=343,182 | N/A | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | N/A | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | N/A | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | N/A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2025-02-26 | 2025-02-26 | N/A | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 374114 | 374190 | N/A | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | N/A | Agent Input |


### renal carcinoma

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS000787 | PGS000722 | PGS004245 | PGS000076 | N/A | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | N/A | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal cell carcinoma | renal cell carcinoma | N/A | Agent Input |
| phenotyping_reported | Kidney cancer | Incident kidney cancer | Incident kidney cancer | Kidney cancer | Incident kidney cancer | N/A | Agent Input |
| method_name | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM002058 | PPM001652 | PPM020302 | PPM002042 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 2 | 3 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | 0.7220 | 0.5670 | N/A | 0.7220 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.3660 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.723, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.543, 'ci_upper': 0.591} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.366} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.15, 'ci_lower': 1.07, 'ci_upper': 1.24} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.02, 'ci_upper': 1.45} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | N/A | Agent Input |
| validation_sample_size | n=324,805 | n=391,610 | n=400,812 | n=133,830 | n=391,610 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | N/A | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | N/A | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | N/A | Agent Input |
| publication.journal | Nat Genet | Nat Commun | JNCI Cancer Spectr | NPJ Precis Oncol | Nat Commun | N/A | Agent Input |
| date_release | 2024-05-22 | 2021-05-28 | 2021-02-03 | 2023-12-15 | 2020-02-12 | N/A | Agent Input |
| variants_number | 107 | 19 | 15 | 12 | 19 | N/A | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Genotyping array | first 10 genetic principal components | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | N/A | Agent Input |


### graves disease

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005264 | PGS002023 | PGS001042 | N/A | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.7677 | 0.7535 | 0.6667 | 0.6320 | 0.6290 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis with or without goiter | Thyrotoxicosis [hyperthyroidism] (time-to-event) | N/A | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Thyrotoxicosis | N/A | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | Thyrotoxicosis with or without goiter | TTE thyrotoxicosis [hyperthyroidism] | N/A | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | snpnet | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022749 | PPM022748 | PPM022747 | PPM011058 | PPM007972 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 5 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.6339 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0236 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6637 | 0.6652 | 0.6587 | N/A | 0.7130 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0591 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0467 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.663730746326419} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6587} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0199, 'ci_lower': 0.0057, 'ci_upper': 0.034} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54332658848452} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.433940209108075} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.008} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.008} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,108 | n=67,425 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | N/A | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | N/A | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | PLoS Genet | N/A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2021-10-21 | N/A | Agent Input |
| variants_number | 1085170 | 1085173 | 112 | 279385 | 226 | N/A | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | N/A | Agent Input |


### nodular goiter

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005263 | PGS005262 | PGS005261 | PGS002022 | PGS001814 | N/A | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.7033 | 0.6911 | 0.6158 | 0.5575 | 0.5493 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | N/A | Agent Input |
| trait_efo | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | multinodular goiter, nontoxic goiter | multinodular goiter, nontoxic goiter | N/A | Agent Input |
| phenotyping_reported | benign nodular gioter | benign nodular gioter | benign nodular gioter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | N/A | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022746 | PPM022745 | PPM022744 | PPM011050 | PPM009412 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 8 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5876 | 0.5933 | 0.5854 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.587559211464932} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.585439091716637} | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.024, 'ci_lower': 0.0098, 'ci_upper': 0.0382} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0277, 'ci_lower': 0.0135, 'ci_upper': 0.0419} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.36199799551033} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.308952736001074} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.048} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.047} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,043 | n=19,043 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | N/A | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | N/A | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | Am J Hum Genet | N/A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2022-01-10 | N/A | Agent Input |
| variants_number | 1085170 | 1085173 | 110 | 375470 | 322 | N/A | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | N/A | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS004530 | N/A | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5578 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | I26 (Pulmonary embolism) | N/A | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | N/A | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | I26 (Pulmonary embolism) | N/A | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | RFDiseasemetaPRS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM008890 | PPM008900 | PPM008885 | PPM008897 | PPM020645 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | N/A | Agent Input |
| performance_metrics.auc | 0.5916 | 0.6077 | 0.6114 | 0.6003 | N/A | N/A | Agent Input |
| performance_metrics.r2 | 0.0133 | 0.0140 | 0.0151 | 0.0115 | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6535 | 0.6762 | 0.6750 | 0.6242 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0337 | 0.0406 | 0.0400 | 0.0176 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | 0.0350 | 0.0293 | 0.0315 | 0.0446 | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65354, 'ci_lower': 0.63231, 'ci_upper': 0.67477} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03366} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03495} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01331} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59164, 'ci_lower': 0.56886, 'ci_upper': 0.61442} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.242446} | N/A | Agent Input |
| validation_sample_size | n=24,838 | n=24,905 | n=24,905 | n=67,349 | n=56,192 | N/A | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=174,489 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | N/A | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | N/A | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Commun Biol | N/A | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2024-03-18 | N/A | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 1059939 | N/A | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | N/A | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS001784 | PGS000753 | N/A | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.5618 | 0.5388 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | N/A | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | N/A | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | N/A | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS-auto | Pruning and Thresholding (P+T) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM019137 | PPM017103 | PPM019134 | PPM009288 | PPM001912 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 7 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0147 | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8820 | 0.7080 | 0.6900 | 0.8680 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0055 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.708, 'ci_lower': 0.691, 'ci_upper': 0.725} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00547} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | N/A | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=6,940 | n=350,767 | n=46,564 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=8,772 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | N/A | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | MAYO-VDB MVP | N/A | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | N/A | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Cell Genom | Circulation | N/A | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2022-09-08 | 2021-04-07 | N/A | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 911440 | 29 | N/A | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, PCs (1-5) | N/A | Agent Input |


### age-related macular degeneration

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004606 | PGS002269 | PGS004952 | PGS001834 | PGS002041 | N/A | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6547 | 0.6530 | 0.6512 | 0.6133 | 0.6093 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | N/A | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | N/A | Agent Input |
| phenotyping_reported | Age-related macular degeneration | Rentinal layer thickness (photoreceptor inner and outer segments) | Late age-related macular degeneration (Clinical Classification) | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | N/A | Agent Input |
| method_name | PRS-CS | Independent variants associated with AMD | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM020767 | PPM012920 | PPM021761 | PPM009564 | PPM011194 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, South Asian, Not reported | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 3 | 6 | 8 | 8 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7100 | N/A | 0.8420 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0034, 'ci_upper': 0.0315} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0159, 'ci_lower': 0.0018, 'ci_upper': 0.0299} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.21, 'ci_lower': -0.23, 'ci_upper': -0.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=163,011 | n=44,823 | n=1,232 | n=19,413 | n=19,413 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | N/A | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | UKB | UKB | N/A | Agent Input |
| publication.title | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | N/A | Agent Input |
| publication.journal | Nat Genet | Ophthalmology | Invest Ophthalmol Vis Sci | Am J Hum Genet | Am J Hum Genet | N/A | Agent Input |
| date_release | 2024-02-20 | 2022-04-01 | 2024-09-19 | 2022-01-10 | 2022-01-10 | N/A | Agent Input |
| variants_number | 1000946 | 47 | 52 | 157 | 116538 | N/A | Agent Input |
| covariates | age, sex, principal components 1-10 | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | Age, sex, survey membership, 10 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | N/A | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS000784 | PGS003389 | PGS005165 | PGS003428 | N/A | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6925 | 0.6679 | 0.4759 | 0.4709 | 0.3846 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | N/A | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | N/A | Agent Input |
| phenotyping_reported | Incident cervical cancer | Incident cervical cancer | cervical cancer | Cervical Cancer | Incident cervical cancer | N/A | Agent Input |
| method_name | Genome-wide significant variants | 10 variants from Graff et al (PGS000073) with inverse variant weights | lassosum | Known susceptibility loci (genome-wide significant SNPs) | LDpred | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM002039 | PPM002055 | PPM016264 | PPM022403 | PPM017102 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | East Asian | European | N/A | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7450 | 0.7450 | 0.5630 | 0.5660 | 0.6130 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4370 | 0.0016 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.563} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.566} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.437} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00158} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.21, 'ci_lower': 1.07, 'ci_upper': 1.35} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.06, 'ci_upper': 1.36} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.182} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | N/A | Agent Input |
| validation_sample_size | n=211,795 | n=211,795 | n=144,374 | n=57,359 | n=128,113 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=4,295 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | TwinGene | NCI Seattle TwinGene Umea WTCCC | N/A | BBJ | EB FinnGen KP UKB | N/A | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Polygenic risk scores for pan-cancer risk prediction in the Chinese population: A population-based cohort study based on the China Kadoorie Biobank. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | N/A | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | PLoS Med | Hum Mol Genet | N/A | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2025-03-17 | 2023-04-28 | N/A | Agent Input |
| variants_number | 10 | 10 | 2814 | 15 | 2894555 | N/A | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | age, top 20 genetic principal components | Age,Sex (if applicable),Region,Top 10 genetic ancestry principal components | age, smoking | N/A | Agent Input |


### cutaneous melanoma

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS004247 | PGS000766 | PGS003745 | PGS000339 | N/A | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.5934 | 0.5886 | 0.5812 | 0.5663 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Melanoma | Cutaneous melanoma | Skin Melanoma | Cutaneous melanoma | N/A | Agent Input |
| trait_efo | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | N/A | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | Melanoma | Incident cutaneous melanoma | Skin Melanoma | Cutaneous melanoma in multiplex melanoma families | N/A | Agent Input |
| method_name | Pruning and Thresholding (P+T) | PRSice-2 | Variants associated with melanoma | Genome-wide significant SNPs | Clumping and Thresholding (C+T) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM016257 | PPM020304 | PPM001962 | PPM018501 | PPM000921 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 2 | 7 | 1 | 2 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6820 | N/A | 0.6430 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0261 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.643, 'ci_lower': 0.584, 'ci_upper': 0.702} | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | N/A | N/A | N/A | {'name_long': 'Difference of PRS (deltaPRS; melanoma family cases vs. unrelated controls)', 'name_short': 'Difference of PRS (deltaPRS; melanoma family cases vs. unrelated controls)', 'estimate': 0.505, 'se': 0.036} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.78, 'ci_lower': 1.62, 'ci_upper': 1.96} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.46, 'ci_lower': 1.2, 'ci_upper': 1.77} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.34, 'ci_upper': 1.66} | N/A | N/A | Agent Input |
| validation_sample_size | n=273,786 | n=133,830 | n=12,712 | n=448 | n=3,066 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,402 | n=3,666 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | N/A | N/A | 23andMe AMFS CPSII DEMOKRITOS Essen-Heidelberg GenoMEL HPFS LMC MDACCS MELARISK MIA NHS PAH PLCO Q-MEGA SEARCH UKB WAMHS | UKB | BATS MIA PAH | N/A | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Genomic Risk Score for Melanoma in a Prospective Study of Older Individuals. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Multiplex melanoma families are enriched for polygenic risk. | N/A | Agent Input |
| publication.journal | Cancer Res | NPJ Precis Oncol | J Natl Cancer Inst | EBioMedicine | Hum Mol Genet | N/A | Agent Input |
| date_release | 2023-01-19 | 2023-12-15 | 2021-05-28 | 2023-06-01 | 2020-11-05 | N/A | Agent Input |
| variants_number | 672 | 65 | 56 | 57 | 22 | N/A | Agent Input |
| covariates | age, sex, top 20 genetic principal components | first 10 genetic principal components | Sex, melanoma family history, treatment (aspirin/placebo), age at enrolment, PRS*treatment | Unknown | PCs (1-10) | N/A | Agent Input |


### late-onset alzheimer's disease

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000054 | PGS002289 | PGS000334 | PGS004918 | PGS000053 | N/A | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5203 | 0.5144 | 0.5114 | 0.4346 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Alzheimer's disease (late onset) | Late-onset Alzheimer's disease | Late-onset Alzheimer’s disease | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Alzheimer's disease (late onset) | N/A | Agent Input |
| trait_efo | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | N/A | Agent Input |
| phenotyping_reported | Familial late-onset Alzheimer's disease (LOAD) | Pairs matching (short-term memory and attention) no. of correct online round 1 x age interaction | Late-onset Alzheimer’s disease | Late-onset Alzheimer's disease | Familial late-onset Alzheimer's disease (LOAD) | N/A | Agent Input |
| method_name | Genome-wide significant variants | GWAS-significant variants (including APOE) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Genome-wide significant variants | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM000135 | PPM012988 | PPM000901 | PPM021384 | PPM000133 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | Hispanic or Latin American | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 3 | 13 | 2 | 1 | 3 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7310 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1910 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.731} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Difference in mean cognition per decacde increase in age per 1-SD higher GRS (%)', 'name_short': 'Difference in mean cognition per decacde increase in age per 1-SD higher GRS (%)', 'estimate': 11.5} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.191, 'ci_lower': 0.131, 'ci_upper': 0.269} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73, 'ci_lower': 1.57, 'ci_upper': 1.93} | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.29, 'ci_lower': 1.21, 'ci_upper': 1.37} | N/A | Agent Input |
| validation_sample_size | n=3,324 | n=497,087 | n=3,810 | n=136 | n=4,792 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | n=439 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (19%), EUR (81%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | IGAP UKB | ADGC BfDR CHARGE EADI GERAD | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | N/A | Agent Input |
| publication.title | Polygenic risk scores in familial Alzheimer disease. | Association of Genetic Variants Linked to Late-Onset Alzheimer Disease With Cognitive Test Performance by Midlife. | Risk prediction of late-onset Alzheimer's disease implies an oligogenic architecture. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Polygenic risk scores in familial Alzheimer disease. | N/A | Agent Input |
| publication.journal | Neurology | JAMA Netw Open | Nat Commun | Neurobiol Aging | Neurology | N/A | Agent Input |
| date_release | 2019-12-18 | 2022-05-18 | 2020-10-16 | 2024-06-12 | 2019-12-18 | N/A | Agent Input |
| variants_number | 21 | 23 | 22 | 8 | 21 | N/A | Agent Input |
| covariates | Age, sex | Unknown | Unknown | Unknown | Age, sex | N/A | Agent Input |


### open-angle glaucoma

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004944 | PGS001797 | PGS002741 | PGS000764 | PGS000350 | N/A | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6405 | 0.6264 | 0.6173 | 0.5749 | 0.5668 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 0/10 trials | Benchmark Only |
| trait_reported | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary-open angle glaucoma | Primary open-angle glaucoma | N/A | Agent Input |
| trait_efo | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | N/A | Agent Input |
| phenotyping_reported | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary-open angle glaucoma | Primary open-angle glaucoma | N/A | Agent Input |
| method_name | Lassosum | PRS-CS-auto | Genome-wide significant SNPs | SNPs associated with primary-open angle glaucoma were selected from the GWAS Catalog | Genome-wide significant variants | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM021744 | PPM009313 | PPM014900 | PPM001956 | PPM000997 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | European | European | African American or Afro-Caribbean, African unspecified | European | N/A | Agent Input |
| performance_metrics.record_count | 8 | 1 | 5 | 2 | 2 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0315 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7480 | 0.7490 | 0.6700 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.749} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67, 'ci_lower': 0.66, 'ci_upper': 0.68} | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.031479} | N/A | {'name_long': 'Odds Ratio (OR per 1 point increase)', 'name_short': 'Odds Ratio (OR per 1 point increase)', 'estimate': 1.08, 'ci_lower': 1.06, 'ci_upper': 1.11} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.24, 'ci_lower': 1.21, 'ci_upper': 1.27} | N/A | Agent Input |
| validation_sample_size | n=407,667 | n=7,128 | n=3,382 | n=3,830 | n=6,538 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), ASN (60%), EAS (18%), EUR (79%), OTH (60%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: AFR (50%), EUR (50%) | GWAS: MAE (100%) / EVAL: MAO (100%) | GWAS: EUR (94%), MAO (6%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | N/A | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI TWB UCLA UKB | N/A | N/A | ALIENOR ANZRAG BATS BES BMES ERF FES GEP GHS GIST HPFS Iowa MEEI Marshfield NEIGHBOR NHS OHTS ORCADES QIMR REHS RES RS SCES SIMES SINDI TEST TwinsUK WGHS deCODE | N/A | Agent Input |
| publication.title | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Glaucoma genetic risk scores in the Million Veteran Program. | The Role of Genetic Ancestry as a Risk Factor for Primary Open-angle Glaucoma in African Americans. | Association of a Primary Open-Angle Glaucoma Genetic Risk Score With Earlier Age at Diagnosis. | N/A | Agent Input |
| publication.journal | JAMA Ophthalmol | Cell Genom | Ophthalmology | Invest Ophthalmol Vis Sci | JAMA Ophthalmol | N/A | Agent Input |
| date_release | 2024-08-29 | 2022-09-08 | 2022-08-03 | 2021-04-28 | 2020-12-08 | N/A | Agent Input |
| variants_number | 144019 | 885417 | 127 | 23 | 12 | N/A | Agent Input |
| covariates | Age, age2, sex, ancestry | sex,age, 20PCs | Age, sex, and 10 sample-specific PCs | Age, ancestry (q0), gender | sex, DNA source, population structure | N/A | Agent Input |


### alcohol dependence

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002738 | PGS000201 | PGS000202 | PGS002739 | N/A | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6051 | 0.5762 | 0.5742 | 0.5224 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 0/10 trials | Benchmark Only |
| trait_reported | Alcohol use disorder | Problematic alcohol use | Problematic alcohol use | Alcohol use disorder | N/A | Agent Input |
| trait_efo | alcohol dependence | alcohol dependence measurement | alcohol dependence measurement | alcohol dependence | N/A | Agent Input |
| phenotyping_reported | Alcohol use disorder | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CSx (gene-based) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM014841 | PPM000626 | PPM000629 | PPM014842 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | African American or Afro-Caribbean | N/A | Agent Input |
| performance_metrics.record_count | 4 | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.01192} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.00456} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.76, 'ci_lower': 1.32, 'ci_upper': 2.34} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.099, 'se': 0.01} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.043, 'se': 0.019} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.17, 'se': 0.03} | N/A | Agent Input |
| validation_sample_size | n=7,900 | n=7,599 | n=1,251 | n=6,315 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (12%), EUR (88%) / EVAL: AFR (100%) | N/A | Agent Input |
| training_development_cohorts | MVP UKB | UKB | UKB | MVP PGC UKB | N/A | Agent Input |
| publication.title | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Gene-based polygenic risk scores analysis of alcohol use disorder in African Americans. | N/A | Agent Input |
| publication.journal | Alcohol Clin Exp Res | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | N/A | Agent Input |
| date_release | 2022-08-03 | 2020-07-01 | 2020-07-01 | 2022-08-03 | N/A | Agent Input |
| variants_number | 326000 | 1094954 | 1083002 | 858 | N/A | Agent Input |
| covariates | Unknown | sex, age of last observation, 10 Genetic PCs, genotyping array, data collection site | sex, age of last observation, 10 Genetic PCs | Unknown | N/A | Agent Input |


### hypertrophic cardiomyopathy

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004911 | PGS000739 | PGS004910 | PGS000778 | N/A | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6036 | 0.5891 | 0.5873 | 0.5514 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 0/10 trials | Benchmark Only |
| trait_reported | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | N/A | Agent Input |
| trait_efo | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | N/A | Agent Input |
| phenotyping_reported | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Clinical events in individuals with a pathogenic or likely pathogenic sarcomeric variant | N/A | Agent Input |
| method_name | PRS-CS | Genome-wide significant variants | PRS-CS | Genome-wide significant variants | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM021367 | PPM018531 | PPM021366 | PPM002016 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Not reported | N/A | Agent Input |
| performance_metrics.record_count | 1 | 8 | 1 | 6 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8000 | 0.8210 | 0.7300 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0480 | N/A | 0.0310 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.06, 'ci_upper': 1.54} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.247, 'se': 0.095} | N/A | Agent Input |
| validation_sample_size | n=343,182 | n=184,511 | n=343,182 | n=368 | N/A | Agent Input |
| samples_training | N/A | n=47,737 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: NR (100%) | N/A | Agent Input |
| training_development_cohorts | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | BRRD GEL HCMR RBH-CRB | ERSPC LHSC MHI NL4 RBH-CRB UKDHP UMCG | N/A | Agent Input |
| publication.title | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Shared genetic pathways contribute to risk of hypertrophic and dilated cardiomyopathies with opposite directions of effect. | N/A | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | N/A | Agent Input |
| date_release | 2025-02-26 | 2021-02-23 | 2025-02-26 | 2021-05-28 | N/A | Agent Input |
| variants_number | 374114 | 27 | 374190 | 20 | N/A | Agent Input |
| covariates | age, age^2, sex, PC1-10 | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | age, age^2, sex, PC1-10 | Genetic relatedness matrix, sex | N/A | Agent Input |


### juvenile idiopathic arthritis

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000114 | PGS000325 | PGS000326 | PGS000324 | N/A | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5768 | 0.5517 | 0.5315 | 0.5230 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 0/10 trials | Benchmark Only |
| trait_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis (Juvenile Idiophatic Arthritis) | Enthesitis-related Juvenile Idiophatic Arthritis | N/A | Agent Input |
| trait_efo | juvenile idiopathic arthritis | oligoarticular juvenile idiopathic arthritis | polyarticular juvenile idiopathic arthritis, rheumatoid factor negative | enthesitis-related juvenile idiopathic arthritis | N/A | Agent Input |
| phenotyping_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis | Enthesitis-related Arthritis | N/A | Agent Input |
| method_name | SparSNP | SparSNP | SparSNP | SparSNP | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM000263 | PPM000875 | PPM000877 | PPM000874 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 4 | 4 | 4 | 4 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7380 | 0.8000 | 0.7600 | 0.9300 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8, 'ci_lower': 0.77, 'ci_upper': 0.84} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76, 'ci_lower': 0.72, 'ci_upper': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.93, 'ci_lower': 0.86, 'ci_upper': 0.99} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93, 'ci_lower': 1.75, 'ci_upper': 2.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.51, 'ci_lower': 1.35, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.09, 'ci_lower': 2.07, 'ci_upper': 5.04} | N/A | Agent Input |
| validation_sample_size | n=940 | n=3,157 | n=3,089 | n=594 | N/A | Agent Input |
| samples_training | n=7,505 | n=6,137 | n=5,733 | n=5,354 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | N/A | Agent Input |
| publication.title | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | N/A | Agent Input |
| publication.journal | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | N/A | Agent Input |
| date_release | 2020-02-27 | 2020-09-18 | 2020-09-18 | 2020-09-18 | N/A | Agent Input |
| variants_number | 26 | 21 | 12 | 138 | N/A | Agent Input |
| covariates | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | N/A | Agent Input |


### peripheral vascular disease

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005217 | PGS002055 | PGS005158 | PGS001843 | N/A | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.5862 | 0.5195 | 0.5176 | 0.5123 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 0/10 trials | Benchmark Only |
| trait_reported | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Peripheral vascular disease, unspecified | N/A | Agent Input |
| trait_efo | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | peripheral vascular disease | N/A | Agent Input |
| phenotyping_reported | Incident peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease in type 2 diabetes | Peripheral vascular disease, unspecified | N/A | Agent Input |
| method_name | LDpred2 | LDpred2 (bigsnpr) | Genome-wide significant SNPs | Penalized regression (bigstatsr) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022612 | PPM011302 | PPM022378 | PPM009634 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 15 | 8 | 2 | 8 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7310 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0035, 'ci_upper': 0.0315} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0151, 'ci_lower': 0.0011, 'ci_upper': 0.029} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.13, 'ci_lower': 1.03, 'ci_upper': 1.23} | N/A | N/A | Agent Input |
| validation_sample_size | n=304,294 | n=19,668 | n=10,836 | n=19,668 | N/A | Agent Input |
| samples_training | n=96,239 | n=391,124 | N/A | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: AFR (20%), AMR (8%), EUR (72%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | N/A | Agent Input |
| training_development_cohorts | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | N/A | UKB | N/A | Agent Input |
| publication.title | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Modifiable Lifestyle Factors, Genetic Risk, and Incident Peripheral Artery Disease Among Individuals With Type 2 Diabetes: A Prospective Study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | N/A | Agent Input |
| publication.journal | JAMA Cardiol | Am J Hum Genet | Diabetes Care | Am J Hum Genet | N/A | Agent Input |
| date_release | 2025-06-16 | 2022-01-10 | 2025-02-26 | 2022-01-10 | N/A | Agent Input |
| variants_number | 1296292 | 599514 | 19 | 242 | N/A | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | age (continuous, years), sex (male, female), Townsend Deprivation Index (continuous), race/ethnicity (White, others), education attainment (college or university degree, A/AS levels or equivalent or O levels/GCSEs or equivalent or other professional qualifications, or none of the above), family history of CVD (yes, no), prevalence of hypertension (yes, no), use of antihypertensive medication (yes, no), use of lipidlowing medication (yes, no), use of aspirin (yes, no), diabetes duration (continuous, years), HbA1c (continuous, %), use of diabetes medication (none, only oral medication pills, or only insulin or combination of oral medications and insulin), genotype measurement batch, the first 10 principal components of ancestry, weighted healthy lifestyle scores (continuous) | sex, age, birth date, deprivation index, 16 PCs | N/A | Agent Input |


### hashimoto's thyroiditis

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005272 | PGS005271 | PGS005270 | N/A | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.7941 | 0.7940 | 0.6412 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 0/10 trials | Benchmark Only |
| trait_reported | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | N/A | Agent Input |
| trait_efo | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | N/A | Agent Input |
| phenotyping_reported | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | N/A | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM022755 | PPM022754 | PPM022753 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6054 | 0.6297 | 0.6387 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.605418550899187} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.629725726511746} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41698139161814} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.348528828383883} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54908058789994} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.437661585839951} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | N/A | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | N/A | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | N/A | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | N/A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | N/A | Agent Input |
| variants_number | 1085142 | 1085156 | 55 | N/A | Agent Input |
| covariates | Unknown | Unknown | Unknown | N/A | Agent Input |


### preeclampsia

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003586 | PGS004593 | PGS003587 | N/A | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.8077 | 0.7604 | 0.5709 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 0/10 trials | Benchmark Only |
| trait_reported | Pre-eclampsia | Preeclampsia | Gestational hypertension | N/A | Agent Input |
| trait_efo | preeclampsia | preeclampsia | preeclampsia | N/A | Agent Input |
| phenotyping_reported | Pre-eclampsia/eclampsia | Gestational hypertension | Pre-eclampsia/eclampsia | N/A | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM018280 | PPM020743 | PPM018281 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.14, 'ci_upper': 1.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.2, 'ci_lower': 1.14, 'ci_upper': 1.26} | N/A | Agent Input |
| validation_sample_size | n=25,582 | n=138,317 | n=25,582 | N/A | Agent Input |
| samples_training | n=212,034 | N/A | n=212,034 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (1%), ASN (7%), EUR (91%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | N/A | BBJ BioMe EB FinnGen G&H MGBB UKB | N/A | Agent Input |
| publication.title | Polygenic prediction of preeclampsia and gestational hypertension. | Associations of polygenic risk scores for preeclampsia and blood pressure with hypertensive disorders of pregnancy. | Polygenic prediction of preeclampsia and gestational hypertension. | N/A | Agent Input |
| publication.journal | Nat Med | J Hypertens | Nat Med | N/A | Agent Input |
| date_release | 2023-06-22 | 2024-01-26 | 2023-06-22 | N/A | Agent Input |
| variants_number | 1087033 | 1102059 | 1087916 | N/A | Agent Input |
| covariates | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Collection year, genotyping batch, and the first 10 genetic principal components | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | N/A | Agent Input |


### skin carcinoma in situ

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000471 | PGS000470 | PGS000469 | N/A | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6010 | 0.5529 | 0.5041 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 0/10 trials | Benchmark Only |
| trait_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | N/A | Agent Input |
| trait_efo | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | N/A | Agent Input |
| phenotyping_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | N/A | Agent Input |
| method_name | lassosum | Pruning and Thresholding (P+T) | PRS-CS | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM001156 | PPM001155 | PPM001154 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5690 | 0.5570 | 0.5240 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0255 | 0.0154 | 0.0014 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.557, 'ci_lower': 0.531, 'ci_upper': 0.582} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.524, 'ci_lower': 0.499, 'ci_upper': 0.549} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0154} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.093} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.45, 'ci_lower': 1.34, 'ci_upper': 4.45} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00141} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0939} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.48, 'ci_lower': 0.703, 'ci_upper': 3.1} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.308, 'ci_lower': 1.208, 'ci_upper': 1.417} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.269, 'se': 0.0407} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.09, 'ci_lower': 1.001, 'ci_upper': 1.188} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.0865, 'se': 0.0437} | N/A | Agent Input |
| validation_sample_size | n=5,500 | n=5,500 | n=5,500 | N/A | Agent Input |
| samples_training | n=6,005 | n=6,005 | n=6,005 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | N/A | Agent Input |
| training_development_cohorts | MGI | MGI | MGI | N/A | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | N/A | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | N/A | Agent Input |
| date_release | 2020-12-15 | 2020-12-15 | 2020-12-15 | N/A | Agent Input |
| variants_number | 7 | 5 | 1119238 | N/A | Agent Input |
| covariates | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | N/A | Agent Input |


### vitiligo

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000760 | PGS000738 | PGS001536 | N/A | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | N/A | Benchmark Only |
| AoU benchmark AUC | 0.6417 | 0.6276 | 0.5669 | N/A | Benchmark Only |
| Hit@1 | Yes | No | No | N/A | Benchmark Only |
| Hit@2 | Yes | Yes | No | N/A | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | N/A | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 0/10 trials | Benchmark Only |
| trait_reported | Vitiligo | Vitiligo | Vitiligo (time-to-event) | N/A | Agent Input |
| trait_efo | Vitiligo | Vitiligo | Vitiligo | N/A | Agent Input |
| phenotyping_reported | anti-PD-L1 induced hypothyroidism in cancer patients | Red hair | TTE vitiligo | N/A | Agent Input |
| method_name | GCTA-COJO forward selection highest PPA variants | Genome-wide significant variants | snpnet | N/A | Agent Input |
| performance_metrics.selected_performance_id | PPM001935 | PPM018438 | PPM005219 | N/A | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | N/A | Agent Input |
| performance_metrics.record_count | 1 | 8 | 5 | N/A | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6419 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0162 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6345 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0386 | 0.0169 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0816 | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'meta-analysis p-value', 'name_short': 'meta-analysis p-value', 'estimate': 1.1e-06} | {'name_long': 'pseudo R²', 'name_short': 'pseudo R²', 'estimate': 0.038569956} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.41, 'ci_lower': 1.22, 'ci_upper': 1.61} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.694777831} | N/A | N/A | Agent Input |
| validation_sample_size | n=1,584 | n=4,702 | n=67,425 | N/A | Agent Input |
| samples_training | n=408,959 | N/A | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | N/A | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | N/A | Agent Input |
| publication.title | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | N/A | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | N/A | Agent Input |
| date_release | 2021-06-11 | 2021-02-23 | 2021-11-25 | N/A | Agent Input |
| variants_number | 42 | 48 | 77 | N/A | Agent Input |
| covariates | 5 genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | N/A | Agent Input |

