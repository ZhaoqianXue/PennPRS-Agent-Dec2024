# Contribution3: Binary-to-Continuous Cross List Report (rootcode)

## Terminology

- **Input disease**: Disease needing transfer (user query, lacks good self PRS models)
  - **Type A (matrix)**: In C1's AUC matrix (has ground truth for verification)
    - Restricted to **main analysis** ICDs: `include_in_analysis == 1` in `prs_adjauc_metadata` (aligned with C2)
  - **Type A cross-list inputs** (for downstream Cross-Disease Transfer): **only** the union of:
    1. **Cross-Disease PRS Beats Self** — has self AUC and a qualifying cross model;
    2. **Input Diseases Without Self AUC** — no self AUC and at least one qualifying cross model.
    Diseases in **Self Models Already Optimal** and **Without Self AUC But No Qualifying Cross** are **not** Type A cross-list inputs (listed for reference).
  - **Type B**: NOT in C1's AUC matrix (no ground truth); processed **after** Type A cross-list transfer is finalized
- **Output continuous trait**: Measurement trait whose PRS models are recommended for the input disease (from LOINC metadata mapping)
- PGS models with unknown source ontology are **excluded**

## Cross-list workflow

1. **Define Type A input diseases** — use **Cross-Disease PRS Beats Self** ∪ **Input Diseases Without Self AUC** (tables below).
2. **Determine output traits** — for each Type A input, link to retained cross PGS → LOINC trait metadata (see **Top Output Trait** and `cross_list_detail_*.csv`).
3. **Cross-Disease Transfer** — adjust and validate transfer policy using these input–output pairs.
4. **Type B** — after step 3, handle input diseases not in C1's matrix (no AUC ground truth).

## Selection Criterion (Type A)

- At least one non-self PGS model (known source) has cross AUC > best self AUC
- When self AUC exists: require **cross AUC − self best AUC > 0.025** per retained model
- Require **Top Cross AUC > 0.55** for the input disease to enter the cross-list
- Exclude input diseases with **self best AUC > 0.6** (strong self PRS)

## Type A Summary

| Metric | Count |
|--------|-------|
| **Type A cross-list input diseases** (Beats Self ∪ Without Self AUC) | **16** |
|   — Cross-Disease PRS Beats Self | 11 |
|   — Input Diseases Without Self AUC | 5 |
| Total Type A rows in matrix filter (incl. Self optimal) | 94 |
| With self AUC | 83 |
| Without self AUC but no qualifying cross | 6 |
| Self optimal (reference only; not cross-list inputs) | 72 |
| Any cross candidates (incl. no-self) | 16 |

*Partition (all screened traits):* `Without self + qualifying cross` (5) + `Without self + no qualifying cross` (6) + `Cross beats self` (11) + `Self optimal` (72) = **94**. *Cross-list inputs* = 11 + 5 = **16**.

## Type A: Cross-Disease PRS Beats Self

*Included in **Type A cross-list input diseases**.*

Total: 11 diseases

| Input ICD | Input Ontology | Self Best AUC | Top Cross AUC | Improvement | Output LOINC | Top Output Trait | N Cross | N Output Traits |
|-----------|----------------|---------------|---------------|-------------|----------------|--------------------|---------|------------------|
| C54 | endometrial cancer; endometrial carcinom | 0.533241 | 0.633583 | +0.1003 | 718-7 | hemoglobin measurement | 194 | 21 |
| N04 | nephrotic syndrome | 0.544952 | 0.619041 | +0.0741 | 39156-5 | body mass index | 265 | 2 |
| I27 | cor pulmonale | 0.524334 | 0.594913 | +0.0706 | 39156-5 | body mass index | 346 | 2 |
| G30 | alzheimer disease; late-onset alzheimer' | 0.591008 | 0.659679 | +0.0687 | 789-8 | erythrocyte count | 86 | 11 |
| C56 | high grade ovarian serous adenocarcinoma | 0.585803 | 0.648888 | +0.0631 | 2085-9 | high density lipoprotein cholesterol mea | 7 | 5 |
| D25 | uterine fibroid | 0.526428 | 0.573299 | +0.0469 | 2243-4 | estradiol measurement | 3 | 3 |
| L03 | cellulitis | 0.519058 | 0.564727 | +0.0457 | 39156-5 | body mass index | 233 | 2 |
| N02 | iga glomerulonephritis | 0.519844 | 0.555222 | +0.0354 | 39156-5 | body mass index | 19 | 3 |
| J33 | nasal cavity polyp | 0.555651 | 0.590233 | +0.0346 | 711-2 | eosinophil count | 9 | 2 |
| E88 | metabolic syndrome | 0.531998 | 0.563283 | +0.0313 | 39156-5 | body mass index | 89 | 2 |
| J43 | emphysema | 0.529203 | 0.558548 | +0.0293 | 39156-5 | body mass index | 31 | 3 |

## Type A: Input Diseases Without Self AUC

*Included in **Type A cross-list input diseases**.*

Total: 5 diseases

| Input ICD | Input Ontology | Top Cross AUC | Output LOINC | Top Output Trait | N Cross |
|-----------|----------------|---------------|----------------|--------------------|---------|
| M34 | systemic scleroderma | 0.58728 | 39156-5 | body mass index | 1519 |
| M93 | slipped epiphyses | 0.583678 | 39156-5 | body mass index | 1519 |
| F20 | schizophrenia | 0.57309 | 29463-7 | body weight | 1519 |
| L55 | sunburn | 0.558261 | 4548-4 | hba1c measurement | 1519 |
| I83 | varicose veins | 0.557041 | 29463-7 | body weight | 1519 |

## Type A: Without Self AUC But No Qualifying Cross

*Not included in **Type A cross-list input diseases** under current rules; reference only.*

Total: 6 diseases

| Input ICD | Input Ontology | Self Best AUC | Top Cross AUC | N Cross |
|-----------|----------------|---------------|---------------|---------|
| B07 | common wart | nan | nan | 0 |
| E27 | chronic primary adrenal insufficiency | nan | nan | 0 |
| H20 | iritis | nan | nan | 0 |
| H33 | retinal break; retinal detachment | nan | nan | 0 |
| L82 | seborrheic keratosis | nan | nan | 0 |
| R55 | syncope | nan | nan | 0 |

## Type A: Self Models Already Optimal

*Not included in **Type A cross-list input diseases** (self PRS sufficient under current rules; reference only).

Total: 72 diseases

| Input ICD | Input Ontology | Self Best AUC | Self N Models |
|-----------|----------------|---------------|---------------|
| H40 | glaucoma; open-angle glaucoma | 0.599808 | 15 |
| F17 | nicotine dependence | 0.597113 | 2 |
| I26 | pulmonary embolism | 0.590905 | 7 |
| I71 | abdominal aortic aneurysm | 0.590415 | 6 |
| F10 | alcohol dependence; alcohol-induced mental disorde | 0.587597 | 6 |
| C64 | kidney cancer; renal carcinoma; renal cell carcino | 0.584114 | 10 |
| M06 | rheumatoid arthritis | 0.583496 | 48 |
| I70 | peripheral arterial disease | 0.583453 | 2 |
| I24 | myocardial infarction | 0.580234 | 35 |
| D04 | skin carcinoma in situ | 0.580195 | 3 |
| I80 | phlebitis | 0.578337 | 3 |
| F32 | depressive disorder; major depressive disorder | 0.5779 | 30 |
| I21 | acute myocardial infarction; non-st elevation myoc | 0.577853 | 3 |
| M08 | enthesitis-related juvenile idiopathic arthritis;  | 0.576778 | 4 |
| F03 | dementia | 0.575756 | 65 |
| M81 | osteoporosis | 0.573768 | 13 |
| D68 | blood coagulation disease; congenital vitamin k-de | 0.57209 | 3 |
| I42 | cardiomyopathy; dilated cardiomyopathy; hypertroph | 0.571636 | 13 |
| I35 | aortic stenosis | 0.568355 | 8 |
| C67 | urinary bladder cancer; urinary bladder carcinoma | 0.568161 | 20 |
| N17 | acute kidney injury; kidney failure | 0.56605 | 27 |
| I20 | angina pectoris | 0.565284 | 19 |
| F31 | bipolar disorder; bipolar ii disorder | 0.56366 | 3 |
| G20 | parkinson disease | 0.561607 | 11 |
| C34 | bronchus cancer; lung adenocarcinoma; lung cancer; | 0.559652 | 35 |
| D86 | sarcoidosis; skin sarcoidosis | 0.557299 | 4 |
| N20 | nephrolithiasis; ureterolithiasis; urolithiasis | 0.556646 | 5 |
| N18 | chronic kidney disease | 0.556599 | 22 |
| M05 | acpa-negative rheumatoid arthritis; acpa-positive  | 0.555909 | 2 |
| M17 | knee osteoarthritis | 0.551133 | 7 |
| G47 | insomnia; narcolepsy; narcolepsy-cataplexy syndrom | 0.548797 | 44 |
| F41 | anxiety disorder | 0.54798 | 3 |
| L20 | atopic eczema | 0.546164 | 6 |
| J84 | idiopathic pulmonary fibrosis; interstitial lung d | 0.54541 | 4 |
| M16 | hip osteoarthritis | 0.544752 | 7 |
| I73 | peripheral vascular disease | 0.541283 | 4 |
| M19 | arthritis; osteoarthritis | 0.539981 | 107 |
| R51 | headache; headache disorder | 0.539761 | 9 |
| E53 | vitamin b12 deficiency | 0.537925 | 1 |
| H18 | corneal disease; corneal dystrophy; keratoconus | 0.537542 | 4 |
| H90 | age-related hearing impairment; deafness; hearing  | 0.536356 | 6 |
| L72 | epidermal inclusion cyst; follicular cyst | 0.536191 | 3 |
| C85 | non-hodgkins lymphoma | 0.534691 | 22 |
| H35 | age-related macular degeneration; macular degenera | 0.530209 | 7 |
| M51 | intervertebral disc displacement | 0.529606 | 2 |
| M72 | dupuytren contracture; fibroblastic disorder | 0.529341 | 4 |
| N80 | endometriosis | 0.527713 | 3 |
| L30 | dermatitis | 0.526629 | 47 |
| N81 | pelvic organ prolapse; prolapse of female genital  | 0.525886 | 3 |
| G40 | epilepsy | 0.525585 | 2 |
| J30 | allergic rhinitis; seasonal allergic rhinitis; vas | 0.525578 | 2 |
| H91 | hearing loss | 0.524251 | 4 |
| N40 | benign prostatic hyperplasia | 0.523621 | 3 |
| S52 | radius fracture | 0.521229 | 1 |
| F90 | attention deficit hyperactivity disorder | 0.520508 | 2 |
| B02 | herpes zoster | 0.517092 | 1 |
| K64 | hemorrhoid | 0.516285 | 6 |
| E83 | iron metabolism disease | 0.514469 | 2 |
| G58 | mononeuropathy | 0.513813 | 2 |
| U07 | covid-19 | 0.512474 | 3 |
| I34 | mitral valve prolapse | 0.512168 | 1 |
| M35 | polymyalgia rheumatica | 0.509077 | 3 |
| L70 | disorder of pilosebaceous unit | 0.508423 | 3 |
| H25 | cataract | 0.507764 | 8 |
| M67 | ganglion or cyst of synovium/tendon/bursa | 0.505619 | 1 |
| L28 | prurigo nodularis | 0.50419 | 1 |
| Q74 | congenital deformities of limbs | 0.502481 | 2 |
| F43 | post-traumatic stress disorder | 0.501665 | 1 |
| D64 | anemia | 0.50106 | 1 |
| M47 | spondylosis | 0.500678 | 5 |
| R94 | abnormal ekg | 0.500572 | 1 |
| I49 | brugada syndrome | 0.497895 | 2 |

## Type B: Input Diseases NOT in C1 (n=1215)

*Process **after** Type A cross-list transfer (steps 1–3) is finalized.*

These binary diseases (ICD chapters A-N) have >1000 cases in All of Us
but are not in C1's AUC matrix. No ground truth available for measurement-level mapping.

| Input ICD | Description | Cases | Controls |
|-----------|-------------|-------|----------|
| E785 | Hyperlipidemia, unspecified                        | 71956 | 110537 |
| G8929 | Other chronic pain                                 | 58761 | 123732 |
| K219 | Gastro-esophageal reflux disease without esophagit | 57785 | 124708 |
| F419 | Anxiety disorder, unspecified                      | 48832 | 133661 |
| E669 | Obesity, unspecified                               | 39152 | 143341 |
| E559 | Vitamin D deficiency, unspecified                  | 36611 | 145882 |
| F329 | Major depressive disorder, single episode, unspeci | 35335 | 147158 |
| G4733 | Obstructive sleep apnea (adult) (pediatric)        | 34474 | 148019 |
| M545 | Low back pain                                      | 33718 | 148775 |
| J069 | Acute upper respiratory infection, unspecified     | 33017 | 149476 |
| D649 | Anemia, unspecified                                | 32293 | 150200 |
| L821 | Other seborrheic keratosis                         | 30871 | 151622 |
| M542 | Cervicalgia                                        | 30565 | 151928 |
| M25561 | Pain in right knee | 29982 | 152511 |
| E039 | Hypothyroidism, unspecified                        | 29932 | 152561 |
| E119 | Type 2 diabetes mellitus without complications     | 29427 | 153066 |
| E782 | Mixed hyperlipidemia                               | 29186 | 153307 |
| M25562 | Pain in left knee | 28470 | 154023 |
| M549 | Dorsalgia, unspecified                             | 27913 | 154580 |
| M5450 | Low back pain, unspecified                         | 27450 | 155043 |
| I2510 | Athscl heart disease of native coronary artery w/o | 27031 | 155462 |
| E7800 | Pure hypercholesterolemia, unspecified             | 26812 | 155681 |
| N390 | Urinary tract infection, site not specified        | 26632 | 155861 |
| D229 | Melanocytic nevi, unspecified                      | 26293 | 156200 |
| J029 | Acute pharyngitis, unspecified                     | 26263 | 156230 |
| M1990 | Unspecified osteoarthritis, unspecified site       | 26070 | 156423 |
| K5900 | Constipation, unspecified                          | 23296 | 159197 |
| M25511 | Pain in right shoulder | 23294 | 159199 |
| G4700 | Insomnia, unspecified                              | 22866 | 159627 |
| J45909 | Unspecified asthma, uncomplicated | 22805 | 159688 |
| K5730 | Dvrtclos of lg int w/o perforation or abscess w/o  | 22669 | 159824 |
| F32A | Depression, unspecified                            | 22108 | 160385 |
| L989 | Disorder of the skin and subcutaneous tissue, unsp | 22005 | 160488 |
| E6601 | Morbid (severe) obesity due to excess calories     | 21421 | 161072 |
| L570 | Actinic keratosis                                  | 21353 | 161140 |
| M7989 | Other specified soft tissue disorders              | 21198 | 161295 |
| M25512 | Pain in left shoulder | 20934 | 161559 |
| F411 | Generalized anxiety disorder                       | 20764 | 161729 |
| M25551 | Pain in right hip | 19765 | 162728 |
| H903 | Sensorineural hearing loss, bilateral              | 19683 | 162810 |
| M8580 | Oth disrd of bone density and structure, unspecifi | 19494 | 162999 |
| H524 | Presbyopia                                         | 19331 | 163162 |
| M79671 | Pain in right foot | 19294 | 163199 |
| J309 | Allergic rhinitis, unspecified                     | 18984 | 163509 |
| M79672 | Pain in left foot | 18651 | 163842 |
| L814 | Other melanin hyperpigmentation                    | 18636 | 163857 |
| M810 | Age-related osteoporosis w/o current pathological  | 18547 | 163946 |
| D485 | Neoplasm of uncertain behavior of skin             | 18246 | 164247 |
| G4730 | Sleep apnea, unspecified                           | 18219 | 164274 |
| K635 | Polyp of colon                                     | 18131 | 164362 |
| ... | (1165 more) | | |