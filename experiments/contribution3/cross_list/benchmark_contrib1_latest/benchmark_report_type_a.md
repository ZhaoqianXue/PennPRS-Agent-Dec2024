# Cross-Trait Transfer Benchmark Report (Type A)

_This report summarizes Type A targets only. These targets come from the explicit `contribution1/result/aou_extend_trait` universe._

## Selection Rules


| Target Type | Selection Standard |
|-------------|--------------------|
| Type A target<br>- no self AUC benchmark | - `top_cross_auc >= 0.55`<br>- `best_split_gap >= 0.000` (sort cross diseases/traits by AUC, compute adjacent gaps `AUC_k - AUC_(k+1)`, and take the largest one as `best_split_gap`) |
| Type B target<br>- self AUC benchmark available | - `self_best_auc < 0.60`<br>- `top_cross_auc >= 0.55`<br>- `cross_auc - self_auc >= 0.025`<br>- `best_split_gap >= 0.000` (sort cross diseases/traits by AUC, compute adjacent gaps `AUC_k - AUC_(k+1)`, and take the largest one as `best_split_gap`) |

## Binary-to-Binary

- Screened target traits: **208** (Type A only)
- **Selected for benchmark: 67**

### Selected Targets (Binary-to-Binary)

| ICD | Description | Cross Diseases >= 0.55 | Top Cross AUC | Top Cross Name | Best Split | Best Gap |
|-----|-------------|-----------------------|---------------|----------------|------------|----------|
| N65 | Disproportion of reconstructed breast    | 94 / 129 | 0.7607 | Unspecified site of breast cancer | Top-1 | 0.0652 |
| N91 | Absent, scanty and rare menstruation     | 87 / 129 | 0.7179 | Other intervertebral disc displacement | Top-5 | 0.0302 |
| M1A | Chronic gout                             | 23 / 129 | 0.7136 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr | Top-3 | 0.1237 |
| I16 | Hypertensive urgency                     | 30 / 129 | 0.6535 | Essential (primary) hypertension | Top-1 | 0.0229 |
| E79 | Hyperuricemia w/o signs of inflam arthri | 12 / 129 | 0.6528 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr | Top-3 | 0.0734 |
| D05 | Intraductal carcinoma in situ of left br | 22 / 129 | 0.6478 | Unspecified site of breast cancer | Top-1 | 0.0600 |
| E08 | Diabetes due to underlying condition w/o | 27 / 129 | 0.6433 | Essential (primary) hypertension | Top-1 | 0.0307 |
| N52 | Male erectile dysfunction                | 6 / 129 | 0.6425 | Malignant neoplasm of prostate / Inflammatory disease of prostate | Top-2 | 0.0765 |
| D03 | Melanoma in situ                         | 4 / 129 | 0.6213 | Basal cell carcinoma of skin / Malignant melanoma of skin | Top-4 | 0.0381 |
| D24 | Benign neoplasm of breast                | 26 / 129 | 0.6167 | Unspecified site of breast cancer | Top-1 | 0.0284 |
| L11 | Transient acantholytic dermatosis [Grove | 20 / 129 | 0.6145 | Malignant melanoma of skin | Top-3 | 0.0160 |
| I11 | Hypertensive heart disease with heart fa | 28 / 129 | 0.6129 | Coronary atherosclerosis due to calcified coronary lesion | Top-10 | 0.0140 |
| F22 | Delusional disorders                     | 8 / 129 | 0.6105 | Schizophrenia | Top-2 | 0.0357 |
| F14 | Cocaine abuse, uncomplicated             | 35 / 129 | 0.6084 | Headache | Top-20 | 0.0090 |
| I15 | Hypertension secondary to endocrine diso | 17 / 129 | 0.6027 | Essential (primary) hypertension | Top-1 | 0.0232 |
| F60 | Borderline personality disorder          | 20 / 129 | 0.6016 | Major depressive disorder | Top-1 | 0.0266 |
| N97 | Female infertility                       | 28 / 129 | 0.5970 | Acne vulgaris | Top-4 | 0.0130 |
| F11 | Opioid dependence, uncomplicated         | 31 / 129 | 0.5966 | Major depressive disorder | Top-11 | 0.0093 |
| E01 | Iodine-deficiency related thyroid disord | 3 / 129 | 0.5959 | Nontoxic multinodular goiter | Top-1 | 0.0307 |
| Q23 | Congenital insufficiency of aortic valve | 4 / 129 | 0.5934 | Coronary atherosclerosis due to calcified coronary lesion / Nonrheumatic aortic (valve) stenosis / Rheumatic aortic valve disease | Top-3 | 0.0397 |
| J96 | Acute respiratory failure with hypoxia   | 27 / 129 | 0.5922 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-5 | 0.0066 |
| M86 | Osteomyelitis                            | 23 / 129 | 0.5920 | Essential (primary) hypertension | Top-9 | 0.0146 |
| B18 | Chronic viral hepatitis C                | 26 / 129 | 0.5909 | Alcohol dependence | Top-9 | 0.0108 |
| K75 | Nonalcoholic steatohepatitis (NASH)      | 20 / 129 | 0.5900 | Essential (primary) hypertension | Top-1 | 0.0138 |
| N25 | Secondary hyperparathyroidism of renal o | 20 / 129 | 0.5891 | Obesity | Top-2 | 0.0131 |
| N61 | Inflammatory disorders of breast         | 26 / 129 | 0.5886 | Anxiety disorder / Post-traumatic stress disorder | Top-2 | 0.0119 |
| J41 | Simple chronic bronchitis                | 21 / 129 | 0.5808 | Alcohol dependence | Top-4 | 0.0064 |
| B20 | Human immunodeficiency virus [HIV] disea | 20 / 129 | 0.5791 | Chronic obstructive pulmonary disease | Top-1 | 0.0081 |
| F44 | Conversion disorder with seizures or con | 6 / 129 | 0.5786 | Major depressive disorder | Top-1 | 0.0142 |
| E78 | Disorders of lipoprotein metabolism and  | 6 / 129 | 0.5766 | Coronary atherosclerosis due to calcified coronary lesion | Top-3 | 0.0174 |
| I69 | sequelae of cerebral infarction          | 14 / 129 | 0.5763 | native arteries of extrm w intrmt claud / Peripheral vascular disease | Top-3 | 0.0080 |
| L57 | Actinic keratosis                        | 3 / 129 | 0.5758 | Malignant melanoma of skin | Top-1 | 0.0167 |
| F33 | Major depressive disorder, recurrent     | 2 / 129 | 0.5750 | Major depressive disorder | Top-1 | 0.0239 |
| F42 | Obsessive-compulsive disorder            | 2 / 129 | 0.5742 | Major depressive disorder | Top-1 | 0.0199 |
| K43 | Ventral hernia                           | 8 / 129 | 0.5712 | Obesity | Top-1 | 0.0118 |
| L05 | Pilonidal cyst and sinus                 | 11 / 129 | 0.5691 | Malignant neoplasm of bladder | Top-11 | 0.0061 |
| K02 | Dental caries                            | 15 / 129 | 0.5687 | Major depressive disorder | Top-6 | 0.0065 |
| K04 | Periapical abscess without sinus         | 12 / 129 | 0.5687 | Major depressive disorder | Top-1 | 0.0090 |
| N21 | Calculus in bladder                      | 1 / 129 | 0.5680 | Calculus of kidney | Top-1 | 0.0189 |
| K85 | Acute pancreatitis                       | 12 / 129 | 0.5671 | Coronary atherosclerosis due to calcified coronary lesion | Top-1 | 0.0107 |
| L68 | Hirsutism                                | 8 / 129 | 0.5666 | Unspecified osteoarthritis / Systemic disord of conn tiss in oth diseases classd elswhr | Top-3 | 0.0084 |
| L02 | Cutaneous abscess, furuncle and carbuncl | 10 / 129 | 0.5644 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-6 | 0.0086 |
| K81 | Cholecystitis                            | 6 / 129 | 0.5643 | Essential (primary) hypertension | Top-2 | 0.0069 |
| N84 | Polyp of corpus uteri                    | 9 / 129 | 0.5638 | asthma | Top-1 | 0.0100 |
| E87 | Hypokalemia                              | 11 / 129 | 0.5628 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-36 | 0.0034 |
| E86 | Dehydration                              | 9 / 129 | 0.5627 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-4 | 0.0051 |
| N10 | Acute pyelonephritis                     | 9 / 129 | 0.5613 | Obesity | Top-7 | 0.0084 |
| K65 | Peritoneal abscess                       | 9 / 129 | 0.5613 | Coronary atherosclerosis due to calcified coronary lesion / Chronic diastolic (congestive) heart failure | Top-2 | 0.0052 |
| G43 | Migraine                                 | 1 / 129 | 0.5606 | Headache | Top-1 | 0.0148 |
| G83 | Cauda equina syndrome                    | 2 / 129 | 0.5604 | native arteries of extrm w intrmt claud / Peripheral vascular disease | Top-2 | 0.0105 |
| K25 | Gastric ulcer                            | 5 / 129 | 0.5583 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-4 | 0.0045 |
| I44 | Atrioventricular block, first degree     | 6 / 129 | 0.5582 | Coronary atherosclerosis due to calcified coronary lesion | Top-6 | 0.0089 |
| F34 | Dysthymic disorder                       | 1 / 129 | 0.5557 | Major depressive disorder | Top-1 | 0.0168 |
| N12 | Tubulo-interstitial nephritis, not spcf  | 1 / 129 | 0.5556 | Essential (primary) hypertension | Top-1 | 0.0097 |
| L56 | Oth acute skin changes due to ultraviole | 2 / 129 | 0.5548 | Sunburn | Top-2 | 0.0087 |
| G56 | Carpal tunnel syndrome, right upper limb | 2 / 129 | 0.5542 | Essential (primary) hypertension | Top-3 | 0.0063 |
| E72 | Methylenetetrahydrofolate reductase defi | 1 / 129 | 0.5542 | Major depressive disorder | Top-1 | 0.0093 |
| G96 | Cerebrospinal fluid leak                 | 1 / 129 | 0.5542 | Headache | Top-1 | 0.0174 |
| N13 | Obstructive and reflux uropathy          | 1 / 129 | 0.5531 | Essential (primary) hypertension | Top-1 | 0.0089 |
| E21 | Hyperparathyroidism and other disorders  | 4 / 129 | 0.5527 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-23 | 0.0041 |
| K21 | Gastro-esophageal reflux disease         | 1 / 129 | 0.5527 | Major depressive disorder | Top-1 | 0.0106 |
| K03 | Deposits [accretions] on teeth           | 1 / 129 | 0.5526 | Major depressive disorder | Top-1 | 0.0077 |
| B37 | Candidiasis                              | 1 / 129 | 0.5520 | Essential (primary) hypertension | Top-8 | 0.0051 |
| C76 | Malignant neoplasm of head, face and nec | 2 / 129 | 0.5512 | Systemic disord of conn tiss in oth diseases classd elswhr / Systemic lupus erythematosus | Top-2 | 0.0082 |
| A04 | Enterocolitis d/t Clostridium difficile, | 1 / 129 | 0.5509 | Major depressive disorder | Top-1 | 0.0053 |
| M27 | Inflammatory conditions of jaws          | 1 / 129 | 0.5506 | Headache | Top-6 | 0.0046 |
| D62 | Acute posthemorrhagic anemia             | 6 / 129 | 0.5506 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | Top-25 | 0.0046 |

### Rejected Targets (Binary-to-Binary): 141

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type A: no cross disease with AUC >= 0.55 | 117 |
| Type A: best split too close to tail | 24 |

## Binary-to-Continuous

- Screened target traits: **208** (Type A only)
- **Selected for benchmark: 40**

### Selected Targets (Binary-to-Continuous)

| ICD | Description | Cross Traits >= 0.55 | Top Cross AUC | Top Cross Name | Best Split | Best Gap |
|-----|-------------|---------------------|---------------|----------------|------------|----------|
| I16 | Hypertensive urgency                     | 8 / 36 | 0.6431 | Diastolic blood pressure | Top-4 | 0.0313 |
| E08 | Diabetes due to underlying condition w/o | 7 / 36 | 0.6280 | Hemoglobin A1c/Hemoglobin.total in Blood / Hemoglobin [Mass/volume] in Blood | Top-4 | 0.0545 |
| I11 | Hypertensive heart disease with heart fa | 7 / 36 | 0.6148 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0262 |
| J96 | Acute respiratory failure with hypoxia   | 6 / 36 | 0.5986 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0378 |
| N25 | Secondary hyperparathyroidism of renal o | 6 / 36 | 0.5964 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0206 |
| J41 | Simple chronic bronchitis                | 3 / 36 | 0.5852 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0336 |
| F14 | Cocaine abuse, uncomplicated             | 8 / 36 | 0.5849 | Body weight | Top-6 | 0.0115 |
| I15 | Hypertension secondary to endocrine diso | 6 / 36 | 0.5846 | Diastolic blood pressure | Top-6 | 0.0387 |
| K75 | Nonalcoholic steatohepatitis (NASH)      | 5 / 36 | 0.5845 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0214 |
| F11 | Opioid dependence, uncomplicated         | 7 / 36 | 0.5834 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0252 |
| F05 | Delirium due to known physiological cond | 6 / 36 | 0.5780 | Body weight / Body mass index (BMI) [Ratio] | Top-3 | 0.0159 |
| K43 | Ventral hernia                           | 2 / 36 | 0.5767 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0424 |
| K42 | Umbilical hernia                         | 2 / 36 | 0.5767 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0344 |
| G92 | Toxic encephalopathy                     | 7 / 36 | 0.5751 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0177 |
| B20 | Human immunodeficiency virus [HIV] disea | 2 / 36 | 0.5748 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0299 |
| K81 | Cholecystitis                            | 2 / 36 | 0.5738 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0297 |
| D47 | Monoclonal gammopathy                    | 1 / 36 | 0.5730 | Platelets [#/volume] in Blood by Automated count | Top-1 | 0.0364 |
| F60 | Borderline personality disorder          | 3 / 36 | 0.5723 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0221 |
| L02 | Cutaneous abscess, furuncle and carbuncl | 2 / 36 | 0.5713 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0255 |
| N26 | Atrophy of kidney (terminal)             | 2 / 36 | 0.5711 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0318 |
| K02 | Dental caries                            | 2 / 36 | 0.5677 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0260 |
| I44 | Atrioventricular block, first degree     | 2 / 36 | 0.5661 | Body weight | Top-2 | 0.0207 |
| K04 | Periapical abscess without sinus         | 2 / 36 | 0.5637 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0175 |
| G83 | Cauda equina syndrome                    | 2 / 36 | 0.5636 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0157 |
| M00 | Pyogenic arthritis                       | 2 / 36 | 0.5594 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0141 |
| G56 | Carpal tunnel syndrome, right upper limb | 2 / 36 | 0.5593 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0190 |
| K65 | Peritoneal abscess                       | 2 / 36 | 0.5588 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0250 |
| I85 | Esophageal varices without bleeding      | 2 / 36 | 0.5586 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0100 |
| B18 | Chronic viral hepatitis C                | 2 / 36 | 0.5585 | Body weight | Top-11 | 0.0081 |
| N60 | Solitary cyst of left breast             | 2 / 36 | 0.5565 | Monocytes [#/volume] in Blood by Automated count | Top-2 | 0.0145 |
| K25 | Gastric ulcer                            | 2 / 36 | 0.5564 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0227 |
| D62 | Acute posthemorrhagic anemia             | 2 / 36 | 0.5546 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0138 |
| E21 | Hyperparathyroidism and other disorders  | 2 / 36 | 0.5542 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0193 |
| F44 | Conversion disorder with seizures or con | 1 / 36 | 0.5540 | Body weight | Top-1 | 0.0085 |
| N12 | Tubulo-interstitial nephritis, not spcf  | 3 / 36 | 0.5532 | Body weight | Top-4 | 0.0142 |
| D50 | Iron deficiency anemia                   | 2 / 36 | 0.5532 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0130 |
| B37 | Candidiasis                              | 2 / 36 | 0.5521 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0146 |
| C22 | Liver cell carcinoma                     | 3 / 36 | 0.5520 | Lymphocytes [#/volume] in Blood | Top-4 | 0.0062 |
| F33 | Major depressive disorder, recurrent     | 2 / 36 | 0.5512 | Body weight / Body mass index (BMI) [Ratio] | Top-2 | 0.0186 |
| N13 | Obstructive and reflux uropathy          | 2 / 36 | 0.5500 | Hemoglobin A1c/Hemoglobin.total in Blood / Hemoglobin [Mass/volume] in Blood | Top-4 | 0.0076 |

### Rejected Targets (Binary-to-Continuous): 168

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type A: no cross trait with AUC >= 0.55 | 136 |
| Type A: best split too close to tail | 32 |

