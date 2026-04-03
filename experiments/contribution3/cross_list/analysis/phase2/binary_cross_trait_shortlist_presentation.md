# Final Binary-Input Cross-Trait Shortlist

This document is generated from the current Phase 2 outputs for presentation use.

## Scope

- Binary-input retained target universe: `26`
- Type A target traits: `2`
- Type B target traits: `24`
- Targets with shortlisted cross traits: `25`
- Targets without shortlisted cross traits: `1`

## Notes

- `Type A target trait` means this target trait does not have a self AUC benchmark in Contribution1, so cross-trait selection is based on cross-trait PRS performance alone.
- `Type B target trait` means this target trait does have a self AUC benchmark in Contribution1, so cross traits are compared against the target's own self PRS.
- One ICD corresponds to one target trait. The long semicolon-separated source label is a synonym bundle, not multiple different target traits. This document shows only the first synonym as the short display name for readability.
- `Available Cross Trait Types` means whether the final recommended cross traits for a target come from binary traits, continuous traits, or both.
- For Type A cross traits, Phase 2 now keeps only candidates with `Best PGS AUC > 0.55`.
- `Best PGS AUC` and `Median PGS AUC` are computed across all candidate PGS models under that cross trait.
- For Type B, `AUC Gain vs Self` means `cross-trait best AUC - self-trait best AUC`.
- `Why It Was Kept` is the current Phase 2 biological plausibility note, not an external causal validation result.

## 1. Target Trait

### 1.1 Type A Target Trait

| Target ICD | Target Trait | Available Cross Trait Types | N Recommended Cross Traits | Top Recommended Cross Trait | Top Recommended Cross Trait AUC | Top Recommended Cross Trait Plausibility |
| --- | --- | --- | --- | --- | --- | --- |
| H20 | iritis | binary only | 3 | ankylosing spondylitis | 0.570921 | high |
| M93 | slipped epiphyses | binary + continuous | 8 | spondylosis | 0.560271 | high |

### 1.2 Type B Target Trait

| Target ICD | Target Trait | Available Cross Trait Types | N Recommended Cross Traits | Top Recommended Cross Trait | Top AUC Gain vs Self | Top Recommended Cross Trait Plausibility |
| --- | --- | --- | --- | --- | --- | --- |
| C54 | endometrial cancer | binary + continuous | 10 | hodgkins lymphoma | 0.064114 | high |
| C56 | high grade ovarian serous adenocarcinoma | binary + continuous | 4 | prostate cancer | 0.033900 | high |
| D04 | skin carcinoma in situ | binary only | 2 | melanoma | 0.045645 | high |
| D25 | uterine fibroid | binary + continuous | 7 | estradiol measurement | 0.046871 | high |
| E88 | metabolic syndrome | binary + continuous | 5 | body mass index | 0.031285 | high |
| F03 | dementia | binary only | 0 |  |  |  |
| F31 | bipolar disorder | binary only | 1 | depressive disorder | 0.042624 | high |
| F43 | post-traumatic stress disorder | binary only | 4 | depressive disorder | 0.052520 | high |
| F90 | attention deficit hyperactivity disorder | binary only | 1 | depressive disorder | 0.036569 | high |
| G30 | alzheimer disease | binary + continuous | 9 | erythrocyte count | 0.068671 | low |
| G40 | epilepsy | binary only | 1 | headache | 0.029021 | high |
| I21 | acute myocardial infarction | binary only | 2 | coronary artery disease | 0.044424 | high |
| I24 | myocardial infarction | binary only | 1 | coronary artery disease | 0.026798 | high |
| I27 | cor pulmonale | binary + continuous | 8 | heart disease | 0.052702 | high |
| J33 | nasal cavity polyp | binary + continuous | 3 | eosinophil percentage of leukocytes | 0.034582 | high |
| J43 | emphysema | binary + continuous | 5 | chronic obstructive pulmonary disease | 0.084471 | high |
| L03 | cellulitis | binary + continuous | 4 | body mass index | 0.045669 | medium |
| L55 | sunburn | binary only | 1 | dermatitis | 0.029100 | high |
| M05 | acpa-negative rheumatoid arthritis | binary only | 3 | arthritis | 0.051413 | high |
| M34 | systemic scleroderma | binary only | 1 | connective tissue disease | 0.040736 | high |
| N02 | iga glomerulonephritis | binary only | 4 | hypertension | 0.026285 | high |
| N04 | nephrotic syndrome | binary + continuous | 8 | kidney failure | 0.026911 | high |
| N40 | benign prostatic hyperplasia | binary only | 1 | prostate cancer | 0.118634 | high |
| S52 | radius fracture | binary only | 3 | bone fracture | 0.056435 | high |

## 2. Target Trait's Cross Trait

### 2.1 Type A Target Trait's Cross Trait

#### H20 — iritis

- `Input Type`: A  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 3  `Top Recommended Cross Trait`: ankylosing spondylitis

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | ankylosing spondylitis | high | HLA-B27 shared autoimmune | 9 |  | 0.570921 |  |
| 2 | binary | arthritis; connective tissue disease; juvenile idiopathic arthritis | high | HLA-B27 shared autoimmune | 1 |  | 0.568106 |  |
| 3 | binary | arthritis; connective tissue disease; enthesitis-related juvenile idiopathic art | high | HLA-B27 shared autoimmune | 1 |  | 0.557169 |  |

#### M93 — slipped epiphyses

- `Input Type`: A  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 8  `Top Recommended Cross Trait`: spondylosis

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | spondylosis | high | same broad system: musculoskeletal | 4 | PGS004484 | 0.560271 | 0.524358 |
| 2 | binary | endometrial cancer | low | no known pathway: musculoskeletal_bone → neoplasm_gynecologic | 7 | PGS003381 | 0.571133 | 0.527818 |
| 3 | binary | hypothyroidism | medium | thyroid → bone metabolism | 24 | PGS002702 | 0.560428 | 0.534091 |
| 4 | binary | alzheimer disease | low | no known pathway: musculoskeletal_bone → neuropsych_dementia | 47 | PGS003440 | 0.559642 | 0.509689 |
| 5 | binary | bronchus cancer | low | no known pathway: musculoskeletal_bone → neoplasm_lung | 10 | PGS000396 | 0.556977 | 0.540097 |
| 6 | continuous | body mass index | low | no known pathway: musculoskeletal_bone → metabolic_obesity | 125 | PGS005198 | 0.583678 | 0.535209 |
| 7 | continuous | body weight | low | no known pathway: musculoskeletal_bone → metabolic_obesity | 227 | PGS005198 | 0.583678 | 0.522164 |
| 8 | continuous | body weights and measures | low | no known pathway: musculoskeletal_bone → metabolic_obesity | 227 | PGS005198 | 0.583678 | 0.522164 |

### 2.2 Type B Target Trait's Cross Trait

#### C54 — endometrial cancer

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 10  `Top Recommended Cross Trait`: hodgkins lymphoma

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | hodgkins lymphoma | high | same broad system: neoplasm | 5 | PGS000641 | 0.597355 | 0.572513 | 0.064114 | 0.039272 |
| 2 | binary | urinary bladder cancer | high | same broad system: neoplasm | 10 | PGS000615 | 0.594939 | 0.585325 | 0.061698 | 0.052084 |
| 3 | binary | thyroid carcinoma | high | same broad system: neoplasm | 4 | PGS005259 | 0.602514 | 0.596308 | 0.069273 | 0.063067 |
| 4 | binary | lung adenocarcinoma | high | same broad system: neoplasm | 1 | PGS003393 | 0.601255 | 0.601255 | 0.068014 | 0.068014 |
| 5 | binary | squamous cell carcinoma | high | same broad system: neoplasm | 3 | PGS000365 | 0.598127 | 0.577928 | 0.064886 | 0.044687 |
| 6 | continuous | red cell distribution width | low | no known pathway: neoplasm_gynecologic → hematologic_rbc | 13 | PGS002712 | 0.633583 | 0.613955 | 0.100342 | 0.080714 |
| 7 | continuous | lipoprotein a measurement | low | no known pathway: neoplasm_gynecologic → metabolic_lipid | 12 | PGS000313 | 0.614628 | 0.602154 | 0.081387 | 0.068913 |
| 8 | continuous | systolic blood pressure | low | likely confounded via BMI | 12 | PGS005015 | 0.622266 | 0.580475 | 0.089025 | 0.047234 |
| 9 | continuous | lymphocyte percentage of leukocytes | low | no known pathway: neoplasm_gynecologic → hematologic_wbc | 7 | PGS001986 | 0.588128 | 0.581383 | 0.054887 | 0.048142 |
| 10 | continuous | c-reactive protein measurement | low | no known pathway: neoplasm_gynecologic → inflammatory | 14 | PGS004335 | 0.594661 | 0.586104 | 0.061420 | 0.052863 |

#### C56 — high grade ovarian serous adenocarcinoma

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 4  `Top Recommended Cross Trait`: prostate cancer

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | prostate cancer | high | same broad system: neoplasm | 1 | PGS001292 | 0.619703 | 0.619703 | 0.033900 | 0.033900 |
| 2 | binary | prostate cancer; prostate carcinoma | high | same broad system: neoplasm | 3 | PGS003460 | 0.629103 | 0.627650 | 0.043300 | 0.041847 |
| 3 | binary | breast carcinoma | high | same broad system: neoplasm | 1 | PGS000529 | 0.612455 | 0.612455 | 0.026652 | 0.026652 |
| 4 | continuous | high density lipoprotein cholesterol measurement | low | no known pathway: neoplasm_gynecologic → metabolic_lipid | 2 | PGS002284 | 0.648888 | 0.634532 | 0.063085 | 0.048729 |

#### D04 — skin carcinoma in situ

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 2  `Top Recommended Cross Trait`: melanoma

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | melanoma | high | identical disease system | 2 | PGS004834 | 0.625840 | 0.623488 | 0.045645 | 0.043293 |
| 2 | binary | squamous cell carcinoma | high | identical disease system | 5 | PGS000464 | 0.611741 | 0.611741 | 0.031546 | 0.031546 |

#### D25 — uterine fibroid

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 7  `Top Recommended Cross Trait`: estradiol measurement

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | continuous | estradiol measurement | high | hormonal pathway in gynecologic cancer | 1 | PGS001182 | 0.573299 | 0.573299 | 0.046871 | 0.046871 |
| 2 | binary | uterine benign neoplasm | high | identical disease system | 2 | PGS002021 | 0.586495 | 0.577676 | 0.060067 | 0.051248 |
| 3 | continuous | testosterone measurement | high | hormonal pathway in gynecologic cancer | 1 | PGS002130 | 0.553343 | 0.553343 | 0.026915 | 0.026915 |
| 4 | binary | ovarian neoplasm | high | identical disease system | 1 | PGS000555 | 0.557960 | 0.557960 | 0.031532 | 0.031532 |
| 5 | binary | ovarian carcinoma | high | identical disease system | 2 | PGS005166 | 0.554385 | 0.553382 | 0.027957 | 0.026954 |
| 6 | binary | thyroid carcinoma | high | same broad system: neoplasm | 1 | PGS005258 | 0.552823 | 0.552823 | 0.026395 | 0.026395 |
| 7 | binary | prostate cancer | high | same broad system: neoplasm | 1 | PGS002798 | 0.554543 | 0.554543 | 0.028115 | 0.028115 |

#### E88 — metabolic syndrome

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 5  `Top Recommended Cross Trait`: body mass index

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | continuous | body mass index | high | same broad system: metabolic | 27 | PGS002313 | 0.563283 | 0.559650 | 0.031285 | 0.027652 |
| 2 | continuous | body weight | high | same broad system: metabolic | 31 | PGS002313 | 0.563283 | 0.559401 | 0.031285 | 0.027403 |
| 3 | continuous | body weights and measures | high | same broad system: metabolic | 31 | PGS002313 | 0.563283 | 0.559401 | 0.031285 | 0.027403 |
| 4 | binary | obesity | high | same broad system: metabolic | 1 | PGS005235 | 0.560397 | 0.560397 | 0.028399 | 0.028399 |
| 5 | binary | hypertension | medium | metabolic syndrome includes hypertension | 1 | PGS004839 | 0.558279 | 0.558279 | 0.026281 | 0.026281 |

#### F03 — dementia

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 0  `Top Recommended Cross Trait`: N/A

No shortlisted cross trait. Best available candidate: `anxiety disorder` (`binary only`, Plausibility `low`, Score `0.034769`, previous Tier `3`).

#### F31 — bipolar disorder

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: depressive disorder

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | depressive disorder | high | identical disease system | 3 | PGS004760 | 0.606284 | 0.594793 | 0.042624 | 0.031133 |

#### F43 — post-traumatic stress disorder

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 4  `Top Recommended Cross Trait`: depressive disorder

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | depressive disorder; major depressive disorder | high | same broad system: mental | 16 | PGS004760 | 0.554185 | 0.532425 | 0.052520 | 0.030760 |
| 2 | binary | depressive disorder | high | same broad system: mental | 1 | PGS000140 | 0.530226 | 0.530226 | 0.028561 | 0.028561 |
| 3 | binary | anxiety disorder | high | same broad system: mental | 1 | PGS004521 | 0.534711 | 0.534711 | 0.033046 | 0.033046 |
| 4 | binary | nicotine dependence | high | same broad system: mental | 1 | PGS002037 | 0.529374 | 0.529374 | 0.027709 | 0.027709 |

#### F90 — attention deficit hyperactivity disorder

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: depressive disorder

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | depressive disorder | high | same broad system: mental | 4 | PGS003333 | 0.557077 | 0.554719 | 0.036569 | 0.034211 |

#### G30 — alzheimer disease

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 9  `Top Recommended Cross Trait`: erythrocyte count

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | continuous | erythrocyte count | low | no direct genetic pathway | 6 | PGS003925 | 0.659679 | 0.625852 | 0.068671 | 0.034843 |
| 2 | continuous | triglyceride measurement | low | no known pathway: neuropsych_dementia → metabolic_lipid | 28 | PGS004663 | 0.657501 | 0.633137 | 0.066493 | 0.042129 |
| 3 | binary | headache | low | no known pathway: neuropsych_dementia → neurological_pain | 1 | PGS000909 | 0.648940 | 0.648940 | 0.057932 | 0.057932 |
| 4 | binary | bronchus cancer | low | no known pathway: neuropsych_dementia → neoplasm_lung | 3 | PGS000394 | 0.644101 | 0.644101 | 0.053093 | 0.053093 |
| 5 | continuous | hemoglobin measurement | low | no direct genetic pathway | 19 | PGS004967 | 0.649516 | 0.625491 | 0.058508 | 0.034483 |
| 6 | binary | acute lymphoblastic leukemia | low | no known pathway: neuropsych_dementia → neoplasm_hematologic | 1 |  | 0.641393 |  | 0.050385 |  |
| 7 | continuous | hba1c measurement | low | no known pathway: neuropsych_dementia → metabolic_diabetes | 12 | PGS003471 | 0.645541 | 0.626314 | 0.054533 | 0.035307 |
| 8 | binary | atrial fibrillation | low | no known pathway: neuropsych_dementia → cardiovascular | 6 | PGS004290 | 0.646740 | 0.631532 | 0.055732 | 0.040524 |
| 9 | binary | parkinson disease | medium | shared neurodegeneration (Lewy body overlap) | 1 | PGS000123 | 0.618065 | 0.618065 | 0.027057 | 0.027057 |

#### G40 — epilepsy

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: headache

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | headache | high | same broad system: neurological | 1 | PGS004798 | 0.554606 | 0.554606 | 0.029021 | 0.029021 |

#### I21 — acute myocardial infarction

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 2  `Top Recommended Cross Trait`: coronary artery disease

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | coronary artery disease | high | identical disease system | 9 | PGS003725 | 0.622277 | 0.611613 | 0.044424 | 0.033760 |
| 2 | binary | peripheral arterial disease | high | same broad system: cardiovascular | 1 | PGS005217 | 0.618235 | 0.618235 | 0.040382 | 0.040382 |

#### I24 — myocardial infarction

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: coronary artery disease

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | coronary artery disease | high | identical disease system | 1 | PGS004745 | 0.607032 | 0.607032 | 0.026798 | 0.026798 |

#### I27 — cor pulmonale

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 8  `Top Recommended Cross Trait`: heart disease

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | heart disease | high | same broad system: cardiovascular | 3 | PGS005097 | 0.577036 | 0.554678 | 0.052702 | 0.030344 |
| 2 | continuous | body mass index | medium | obesity → CVD risk factor | 80 | PGS005203 | 0.594913 | 0.569738 | 0.070579 | 0.045403 |
| 3 | continuous | body weight | medium | obesity → CVD risk factor | 133 | PGS005203 | 0.594913 | 0.570685 | 0.070579 | 0.046351 |
| 4 | continuous | body weights and measures | medium | obesity → CVD risk factor | 133 | PGS005203 | 0.594913 | 0.570685 | 0.070579 | 0.046351 |
| 5 | binary | syncope | high | same broad system: cardiovascular | 1 | PGS004568 | 0.549633 | 0.549633 | 0.025299 | 0.025299 |
| 6 | binary | essential hypertension | high | same broad system: cardiovascular | 3 | PGS004787 | 0.558495 | 0.549353 | 0.034161 | 0.025019 |
| 7 | binary | pulmonary embolism | high | same broad system: cardiovascular | 1 | PGS004530 | 0.551055 | 0.551055 | 0.026721 | 0.026721 |
| 8 | binary | obesity | medium | obesity → CVD risk factor | 3 | PGS005235 | 0.584039 | 0.569972 | 0.059705 | 0.045638 |

#### J33 — nasal cavity polyp

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 3  `Top Recommended Cross Trait`: eosinophil percentage of leukocytes

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | continuous | eosinophil percentage of leukocytes | high | eosinophils in nasal polyps | 4 | PGS001949 | 0.590233 | 0.587169 | 0.034582 | 0.031518 |
| 2 | continuous | eosinophil count | high | eosinophils in nasal polyps | 5 | PGS001949 | 0.590233 | 0.586753 | 0.034582 | 0.031102 |
| 3 | binary | asthma | high | same broad system: respiratory | 30 | PGS004723 | 0.597926 | 0.590626 | 0.042275 | 0.034975 |

#### J43 — emphysema

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 5  `Top Recommended Cross Trait`: chronic obstructive pulmonary disease

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | chronic obstructive pulmonary disease | high | identical disease system | 5 | PGS001783 | 0.613674 | 0.582042 | 0.084471 | 0.052839 |
| 2 | binary | nicotine dependence | medium | smoking → COPD pathway | 2 | PGS002037 | 0.583782 | 0.571859 | 0.054579 | 0.042656 |
| 3 | continuous | body weight | medium | obesity worsens COPD | 12 | PGS002840 | 0.558548 | 0.558053 | 0.029345 | 0.028851 |
| 4 | continuous | body weights and measures | medium | obesity worsens COPD | 12 | PGS002840 | 0.558548 | 0.558053 | 0.029345 | 0.028851 |
| 5 | continuous | body mass index | medium | obesity worsens COPD | 6 | PGS002840 | 0.558548 | 0.558118 | 0.029345 | 0.028915 |

#### L03 — cellulitis

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 4  `Top Recommended Cross Trait`: body mass index

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | continuous | body mass index | medium | obesity → cellulitis risk factor | 49 | PGS005199 | 0.564727 | 0.554317 | 0.045669 | 0.035259 |
| 2 | continuous | body weight | medium | obesity → cellulitis risk factor | 92 | PGS005199 | 0.564727 | 0.549508 | 0.045669 | 0.030450 |
| 3 | continuous | body weights and measures | medium | obesity → cellulitis risk factor | 92 | PGS005199 | 0.564727 | 0.549508 | 0.045669 | 0.030450 |
| 4 | binary | obesity | medium | obesity → cellulitis risk factor | 2 | PGS005235 | 0.556386 | 0.551355 | 0.037328 | 0.032297 |

#### L55 — sunburn

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: dermatitis

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | dermatitis | high | same broad system: skin | 4 | PGS005309 | 0.549872 | 0.548851 | 0.029100 | 0.028078 |

#### M05 — acpa-negative rheumatoid arthritis

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 3  `Top Recommended Cross Trait`: arthritis

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | arthritis; connective tissue disease; polymyalgia rheumatica | high | identical disease system | 2 | PGS001878 | 0.607322 | 0.606437 | 0.051413 | 0.050528 |
| 2 | binary | arthritis; connective tissue disease; gout | high | identical disease system | 23 | PGS004817 | 0.659479 | 0.622366 | 0.103570 | 0.066457 |
| 3 | binary | iga glomerulonephritis | medium | lupus nephritis / autoimmune renal | 1 | PGS005284 | 0.583293 | 0.583293 | 0.027384 | 0.027384 |

#### M34 — systemic scleroderma

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: connective tissue disease

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | connective tissue disease | high | identical disease system | 3 | PGS000803 | 0.616099 | 0.614548 | 0.040736 | 0.039185 |

#### N02 — iga glomerulonephritis

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 4  `Top Recommended Cross Trait`: hypertension

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | hypertension | high | renal-hypertension axis | 1 | PGS000856 | 0.546129 | 0.546129 | 0.026285 | 0.026285 |
| 2 | binary | arthritis | medium | lupus nephritis / autoimmune renal | 1 |  | 0.545392 |  | 0.025548 |  |
| 3 | binary | connective tissue disease | medium | lupus nephritis / autoimmune renal | 1 | PGS000754 | 0.549481 | 0.549481 | 0.029637 | 0.029637 |
| 4 | binary | heart disease | medium | CKD → CVD risk pathway | 1 | PGS000709 | 0.545924 | 0.545924 | 0.026080 | 0.026080 |

#### N04 — nephrotic syndrome

- `Input Type`: B  `Available Cross Trait Types`: binary + continuous
- `N Recommended Cross Traits`: 8  `Top Recommended Cross Trait`: kidney failure

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | kidney failure | high | identical disease system | 1 | PGS004562 | 0.571863 | 0.571863 | 0.026911 | 0.026911 |
| 2 | binary | hypertension | high | renal-hypertension axis | 5 | PGS004839 | 0.586768 | 0.579720 | 0.041816 | 0.034768 |
| 3 | continuous | body mass index | low | weak: obesity confounding only | 51 | PGS001943 | 0.619041 | 0.592781 | 0.074089 | 0.047829 |
| 4 | continuous | body weight | low | weak: obesity confounding only | 107 | PGS001943 | 0.619041 | 0.589583 | 0.074089 | 0.044631 |
| 5 | continuous | body weights and measures | low | weak: obesity confounding only | 107 | PGS001943 | 0.619041 | 0.589583 | 0.074089 | 0.044631 |
| 6 | binary | heart disease | medium | CKD → CVD risk pathway | 1 | PGS005039 | 0.575970 | 0.575970 | 0.031018 | 0.031018 |
| 7 | binary | obesity | low | weak: obesity confounding only | 4 | PGS005235 | 0.596606 | 0.576831 | 0.051654 | 0.031879 |
| 8 | binary | atrial fibrillation | medium | CKD → CVD risk pathway | 2 | PGS004440 | 0.577038 | 0.574676 | 0.032086 | 0.029724 |

#### N40 — benign prostatic hyperplasia

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 1  `Top Recommended Cross Trait`: prostate cancer

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | prostate cancer | high | same prostate tissue | 1 | PGS000067 | 0.642255 | 0.642255 | 0.118634 | 0.118634 |

#### S52 — radius fracture

- `Input Type`: B  `Available Cross Trait Types`: binary only
- `N Recommended Cross Traits`: 3  `Top Recommended Cross Trait`: bone fracture

| Rank | Cross Trait Type | Cross Trait | Biological Plausibility | Why It Was Kept | N Candidate PRS Models | Best PGS ID | Best PGS AUC | Median PGS AUC | Best AUC Gain vs Self | Median AUC Gain vs Self |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | binary | bone fracture; osteoporosis | high | identical disease system | 1 | PGS002768 | 0.577664 | 0.577664 | 0.056435 | 0.056435 |
| 2 | binary | osteoporosis | high | identical disease system | 4 | PGS004810 | 0.576973 | 0.567333 | 0.055744 | 0.046103 |
| 3 | binary | bone fracture | high | identical disease system | 1 | PGS002137 | 0.555245 | 0.555245 | 0.034016 | 0.034016 |

