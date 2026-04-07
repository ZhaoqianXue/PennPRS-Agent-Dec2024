# Cross-Trait Transfer Benchmark Report (All Targets)

_This report summarizes explicit Type A targets from `contribution1/aou_nontarget_pgs` together with Type B targets from the main rootcode adjAUC benchmark universe._

## Selection Rules


| Target Type | Selection Standard |
|-------------|--------------------|
| Type A target<br>- no self AUC benchmark | - `top_cross_auc >= 0.55`<br>- `best_split_gap >= 0.025` (sort cross diseases/traits by AUC, compute adjacent gaps `AUC_k - AUC_(k+1)`, and take the largest one as `best_split_gap`) |
| Type B target<br>- self AUC benchmark available | - `self_best_auc < 0.60`<br>- `top_cross_auc >= 0.55`<br>- `cross_auc - self_auc >= 0.025`<br>- `best_split_gap >= 0.025` (sort cross diseases/traits by AUC, compute adjacent gaps `AUC_k - AUC_(k+1)`, and take the largest one as `best_split_gap`) |

## Binary-to-Binary

- Screened target traits: **348** (Type A: 227, Type B: 121)
- **Selected for benchmark: 23** (Type A: 15, Type B: 8)

### Selected Type A Targets (Binary-to-Binary)

| ICD | Description | Cross Diseases >= 0.55 | Top Cross AUC | Top Cross Name | Best Split | Best Gap |
|-----|-------------|-----------------------|---------------|----------------|------------|----------|
| N65 | Disproportion of reconstructed breast    | 94 / 129 | 0.7607 | Unspecified site of breast cancer | Top-1 | 0.0652 |
| N91 | Absent, scanty and rare menstruation     | 87 / 129 | 0.7179 | Other intervertebral disc displacement | Top-5 | 0.0302 |
| M1A | Chronic gout                             | 23 / 129 | 0.7136 | Systemic disord of conn tiss in oth diseases classd elswhr / | Top-3 | 0.1237 |
| E11 | Type 2 diabetes mellitus                 | 29 / 129 | 0.6741 | Essential (primary) hypertension | Top-1 | 0.0479 |
| E79 | Hyperuricemia w/o signs of inflam arthri | 12 / 129 | 0.6528 | Systemic disord of conn tiss in oth diseases classd elswhr / | Top-3 | 0.0734 |
| D05 | Intraductal carcinoma in situ of left br | 22 / 129 | 0.6478 | Unspecified site of breast cancer | Top-1 | 0.0600 |
| E08 | Diabetes due to underlying condition w/o | 27 / 129 | 0.6433 | Essential (primary) hypertension | Top-1 | 0.0307 |
| N52 | Male erectile dysfunction                | 6 / 129 | 0.6425 | Malignant neoplasm of prostate / Inflammatory disease of pro | Top-2 | 0.0765 |
| D03 | Melanoma in situ                         | 4 / 129 | 0.6213 | Basal cell carcinoma of skin / Malignant melanoma of skin | Top-4 | 0.0381 |
| D24 | Benign neoplasm of breast                | 26 / 129 | 0.6167 | Unspecified site of breast cancer | Top-1 | 0.0284 |
| F22 | Delusional disorders                     | 8 / 129 | 0.6105 | Schizophrenia | Top-2 | 0.0357 |
| F60 | Borderline personality disorder          | 20 / 129 | 0.6016 | Major depressive disorder | Top-1 | 0.0266 |
| E01 | Iodine-deficiency related thyroid disord | 3 / 129 | 0.5959 | Nontoxic multinodular goiter | Top-1 | 0.0307 |
| Q23 | Congenital insufficiency of aortic valve | 4 / 129 | 0.5934 | Coronary atherosclerosis due to calcified coronary lesion /  | Top-3 | 0.0397 |
| K70 | Alcoholic cirrhosis of liver without asc | 7 / 129 | 0.5919 | Alcohol dependence | Top-1 | 0.0282 |

### Rejected Type A Targets (Binary-to-Binary): 212

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type A: no cross disease with AUC >= 0.55 | 127 |
| Type A: best split too close to tail | 26 |
| Type A: best split gap < 0.025 | 59 |

### Selected Type B Targets (Binary-to-Binary)

| ICD | Description | Cross Diseases Beating Self | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |
|-----|-------------|-----------------------------|--------------|---------------|----------------|-----------------|------------|----------|
| N40 | Benign prostatic hyperplasia without low | 2 / 128 | 0.5236 | 0.6423 | Malignant neoplasm of prostate / Inflammatory disease of pro | +0.1186 | Top-2 | 0.0998 |
| M05 | Rheumatoid arthritis | 7 / 128 | 0.5559 | 0.6595 | Gout / Systemic disord of conn tiss in oth diseases classd e | +0.1036 | Top-4 | 0.0522 |
| J43 | Emphysema | 16 / 128 | 0.5292 | 0.6137 | Chronic obstructive pulmonary disease | +0.0845 | Top-1 | 0.0299 |
| S52 | Unspecified fracture of the lower end of | 2 / 128 | 0.5212 | 0.5777 | nasal bones / Age-related osteoporosis w/o current pathologi | +0.0564 | Top-2 | 0.0507 |
| D04 | Carcinoma in situ of skin of other parts | 2 / 128 | 0.5802 | 0.6258 | Malignant melanoma of skin | +0.0456 | Top-3 | 0.0550 |
| F31 | Bipolar disorder | 1 / 128 | 0.5637 | 0.6063 | Major depressive disorder | +0.0426 | Top-1 | 0.0307 |
| J33 | Polyp of nasal cavity | 1 / 128 | 0.5557 | 0.5979 | asthma | +0.0423 | Top-4 | 0.0272 |
| F90 | Attention-deficit hyperactivity disorder | 1 / 128 | 0.5205 | 0.5571 | Major depressive disorder | +0.0366 | Top-1 | 0.0266 |

### Rejected Type B Targets (Binary-to-Binary): 113

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type B: self AUC >= 0.60 | 31 |
| Type B: no qualifying cross disease | 59 |
| Type B: top cross disease AUC < 0.55 | 7 |
| Type B: best split gap < 0.025 | 16 |

## Binary-to-Continuous

- Screened target traits: **348** (Type A: 227, Type B: 121)
- **Selected for benchmark: 29** (Type A: 21, Type B: 8)

### Selected Type A Targets (Binary-to-Continuous)

| ICD | Description | Cross Traits >= 0.55 | Top Cross AUC | Top Cross Name | Best Split | Best Gap |
|-----|-------------|---------------------|---------------|----------------|------------|----------|
| E11 | Type 2 diabetes mellitus                 | 7 / 36 | 0.6578 | Hemoglobin A1c/Hemoglobin.total in Blood / Hemoglobin [Mass/ | Top-4 | 0.0598 |
| I16 | Hypertensive urgency                     | 8 / 36 | 0.6431 | Diastolic blood pressure | Top-4 | 0.0313 |
| E10 | Type 1 diabetes mellitus                 | 4 / 36 | 0.6359 | Hemoglobin A1c/Hemoglobin.total in Blood / Hemoglobin [Mass/ | Top-2 | 0.0628 |
| E08 | Diabetes due to underlying condition w/o | 7 / 36 | 0.6280 | Hemoglobin A1c/Hemoglobin.total in Blood / Hemoglobin [Mass/ | Top-4 | 0.0545 |
| F50 | Eating disorders                         | 2 / 36 | 0.6245 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0807 |
| I11 | Hypertensive heart disease with heart fa | 7 / 36 | 0.6148 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0262 |
| J96 | Acute respiratory failure with hypoxia   | 6 / 36 | 0.5986 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0378 |
| K74 | Fibrosis and cirrhosis of liver          | 4 / 36 | 0.5865 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0286 |
| J41 | Simple chronic bronchitis                | 3 / 36 | 0.5852 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0336 |
| I15 | Hypertension secondary to endocrine diso | 6 / 36 | 0.5846 | Diastolic blood pressure | Top-6 | 0.0387 |
| F11 | Opioid dependence, uncomplicated         | 7 / 36 | 0.5834 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0252 |
| K43 | Ventral hernia                           | 2 / 36 | 0.5767 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0424 |
| K42 | Umbilical hernia                         | 2 / 36 | 0.5767 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0344 |
| B20 | Human immunodeficiency virus [HIV] disea | 2 / 36 | 0.5748 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0299 |
| K81 | Cholecystitis                            | 2 / 36 | 0.5738 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0297 |
| D47 | Monoclonal gammopathy                    | 1 / 36 | 0.5730 | Platelets [#/volume] in Blood by Automated count | Top-1 | 0.0364 |
| L02 | Cutaneous abscess, furuncle and carbuncl | 2 / 36 | 0.5713 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0255 |
| N26 | Atrophy of kidney (terminal)             | 2 / 36 | 0.5711 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0318 |
| K80 | Cholelithiasis                           | 2 / 36 | 0.5693 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0302 |
| K02 | Dental caries                            | 2 / 36 | 0.5677 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0260 |
| K65 | Peritoneal abscess                       | 2 / 36 | 0.5588 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0250 |

### Rejected Type A Targets (Binary-to-Continuous): 206

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type A: no cross trait with AUC >= 0.55 | 150 |
| Type A: best split too close to tail | 32 |
| Type A: best split gap < 0.025 | 24 |

### Selected Type B Targets (Binary-to-Continuous)

| ICD | Description | Cross Traits Beating Self | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |
|-----|-------------|---------------------------|--------------|---------------|----------------|-----------------|------------|----------|
| C54 | Malignant neoplasm of endometrium | 21 / 36 | 0.5332 | 0.6336 | Hemoglobin [Mass/volume] in Blood / Erythrocyte [DistWidth]  | +0.1003 | Top-35 | 0.0269 |
| N04 | Nephrotic syndrome with unspecified morp | 2 / 36 | 0.5450 | 0.6190 | Body weight / Body mass index (BMI) [Ratio] | +0.0741 | Top-2 | 0.0511 |
| I27 | Cor pulmonale (chronic) | 2 / 36 | 0.5243 | 0.5949 | Body weight / Body mass index (BMI) [Ratio] | +0.0706 | Top-2 | 0.0470 |
| G30 | Alzheimer's disease | 11 / 36 | 0.5910 | 0.6597 | Erythrocytes [#/volume] in Blood by Automated count | +0.0687 | Top-34 | 0.0498 |
| C56 | Malignant neoplasm of unspecified ovary | 5 / 36 | 0.5858 | 0.6489 | Cholesterol in HDL [Mass/volume] in Serum or Plasma | +0.0631 | Top-34 | 0.0466 |
| D25 | Leiomyoma of uterus | 3 / 36 | 0.5264 | 0.5733 | Estradiol (E2) [Mass/volume] in Serum or Plasma | +0.0469 | Top-35 | 0.0348 |
| L03 | Cellulitis | 2 / 36 | 0.5191 | 0.5647 | Body weight / Body mass index (BMI) [Ratio] | +0.0457 | Top-2 | 0.0258 |
| J33 | Polyp of nasal cavity | 2 / 36 | 0.5557 | 0.5902 | Eosinophils [#/volume] in Blood by Automated count / Eosinop | +0.0346 | Top-2 | 0.0425 |

### Rejected Type B Targets (Binary-to-Continuous): 113

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type B: self AUC >= 0.60 | 31 |
| Type B: no qualifying cross trait | 71 |
| Type B: top cross trait AUC < 0.55 | 7 |
| Type B: best split gap < 0.025 | 4 |

