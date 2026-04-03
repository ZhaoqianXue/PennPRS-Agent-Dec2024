# Contribution3: Binary-to-Continuous Cross List Report (rootcode)

## Terminology

- **Target trait**: Trait being predicted / transferred into
  - Restricted to **main analysis** ICDs: `include_in_analysis == 1` in `prs_adjauc_metadata` (aligned with C2)
  - **Type A**: target traits **without self AUC**
  - **Type B**: target traits **with self AUC**
  - All target traits in this report are in C1's AUC matrix, so benchmark validation is available.
- **Cross trait**: Trait whose PRS models are recommended for the target trait (continuous trait resolved from LOINC metadata mapping)
- PGS models with unknown source ontology are **excluded**

## Cross-list workflow

1. **Partition screened target traits** into Type A (without self AUC) and Type B (with self AUC).
2. **Retain cross-list target traits** — Type A target traits need at least one qualifying cross model; Type B target traits need a cross model that beats self.
3. **Determine cross traits** — for each retained target trait, link to retained cross PGS → LOINC trait metadata (see **Top Cross Trait** and `cross_list_detail_*.csv`).
4. **Cross-Trait Transfer** — adjust and validate transfer policy using these target-trait / cross-trait pairs.

## Selection Criterion

- Type A (without self AUC): require at least one non-self PGS model with a known mapped cross trait
- Type B (with self AUC): require at least one non-self PGS model with cross AUC > best self AUC
- When self AUC exists: require **cross AUC − self best AUC > 0.025** per retained model
- Require **Top Cross AUC > 0.55** for the target trait to enter the cross-list
- Exclude target traits with **self best AUC > 0.6** (strong self PRS)

## Type A / Type B Summary

| Metric | Count |
|--------|-------|
| **Cross-list target traits** (retained Type A ∪ retained Type B) | **13** |
| — Retained Type A (Without Self AUC + qualifying cross) | 1 |
| — Retained Type B (With Self AUC + cross beats self) | 12 |
| Total screened rows in matrix filter | 94 |
| Type A total (Without Self AUC) | 4 |
| — Type A without qualifying cross | 3 |
| Type B total (With Self AUC) | 90 |
| — Type B self optimal | 78 |
| Any cross candidates (Type A + Type B) | 13 |

*Partition:* `Type A retained` (1) + `Type A no qualifying cross` (3) + `Type B beats self` (12) + `Type B self optimal` (78) = **94**. *Cross-list target traits* = 1 + 12 = **13**.


## Type A: Target Traits Without Self AUC

*Included in the retained cross-list target traits.*

Total: 1 target traits

| Target ICD | Target Trait | Top Cross AUC | Cross Trait LOINC | Top Cross Trait | N Cross Models |
|-----------|--------------|---------------|-----------------|-----------------|----------------|
| M93 | slipped epiphyses | 0.583678 | 39156-5 | body mass index | 1519 |

## Type A: Without Self AUC But No Qualifying Cross

*Not included in the retained cross-list target traits under current rules; best available cross-trait evidence shown for reference.*

Total: 3 target traits

| Target ICD | Target Trait | Top Available Cross AUC | Cross Trait LOINC | Top Cross Trait | Available N Cross Models |
|-----------|--------------|-------------------------|-----------------|-----------------|--------------------------|
| B07 | common wart | 0.517954 | 2085-9 | high density lipoprotein cholesterol mea | 1519 |
| E27 | chronic primary adrenal insufficiency | 0.542002 | 29463-7 | body weight | 1519 |
| H20 | iritis | 0.534871 | 62292-8 | vitamin d level | 1519 |

## Type B: Cross-Trait PRS Beats Self

*Included in the retained cross-list target traits.*

Total: 12 target traits

| Target ICD | Target Trait | Self Best AUC | Top Cross AUC | Improvement | Cross Trait LOINC | Top Cross Trait | N Cross Models | N Unique Cross Traits |
|-----------|--------------|---------------|---------------|-------------|-----------------|-----------------|----------------|----------------|
| C54 | endometrial cancer; endometrial carcinom | 0.533241 | 0.633583 | +0.1003 | 718-7 | hemoglobin measurement | 194 | 21 |
| N04 | nephrotic syndrome | 0.544952 | 0.619041 | +0.0741 | 39156-5 | body mass index | 265 | 2 |
| I27 | cor pulmonale | 0.524334 | 0.594913 | +0.0706 | 39156-5 | body mass index | 346 | 2 |
| G30 | alzheimer disease; late-onset alzheimer' | 0.591008 | 0.659679 | +0.0687 | 789-8 | erythrocyte count | 86 | 11 |
| C56 | high grade ovarian serous adenocarcinoma | 0.585803 | 0.648888 | +0.0631 | 2085-9 | high density lipoprotein cholesterol mea | 7 | 5 |
| D25 | uterine fibroid | 0.526428 | 0.573299 | +0.0469 | 2243-4 | estradiol measurement | 3 | 3 |
| L03 | cellulitis | 0.519058 | 0.564727 | +0.0457 | 39156-5 | body mass index | 233 | 2 |
| L55 | sunburn | 0.520772 | 0.558261 | +0.0375 | 4548-4 | hba1c measurement | 12 | 4 |
| N02 | iga glomerulonephritis | 0.519844 | 0.555222 | +0.0354 | 39156-5 | body mass index | 19 | 3 |
| J33 | nasal cavity polyp | 0.555651 | 0.590233 | +0.0346 | 711-2 | eosinophil count | 9 | 2 |
| E88 | metabolic syndrome | 0.531998 | 0.563283 | +0.0313 | 39156-5 | body mass index | 89 | 2 |
| J43 | emphysema | 0.529203 | 0.558548 | +0.0293 | 39156-5 | body mass index | 31 | 3 |

## Type B: Self Models Already Optimal

*Not included in the retained cross-list target traits (self PRS sufficient under current rules; reference only).*

Total: 78 target traits

| Target ICD | Target Trait | Self Best AUC | Self N Models |
|-----------|--------------|---------------|---------------|
| H40 | glaucoma; open-angle glaucoma | 0.599808 | 15 |
| F17 | nicotine dependence | 0.597113 | 2 |
| I26 | pulmonary embolism | 0.590905 | 7 |
| I71 | abdominal aortic aneurysm | 0.590415 | 6 |
| F10 | alcohol dependence; alcohol-induced mental disorde | 0.587597 | 6 |
| C64 | kidney cancer; renal carcinoma; renal cell carcino | 0.584114 | 10 |
| M06 | rheumatoid arthritis | 0.583496 | 48 |
| I70 | peripheral arterial disease | 0.583453 | 2 |
| I83 | varicose veins | 0.58039 | 6 |
| I24 | myocardial infarction | 0.580234 | 35 |
| D04 | skin carcinoma in situ | 0.580195 | 3 |
| I80 | phlebitis | 0.578337 | 3 |
| F32 | depressive disorder; major depressive disorder | 0.5779 | 30 |
| I21 | acute myocardial infarction; non-st elevation myoc | 0.577853 | 3 |
| M08 | enthesitis-related juvenile idiopathic arthritis;  | 0.576778 | 4 |
| F03 | dementia | 0.575756 | 65 |
| M34 | systemic scleroderma | 0.575363 | 1 |
| M81 | osteoporosis | 0.573768 | 13 |
| D68 | blood coagulation disease; congenital vitamin k-de | 0.57209 | 3 |
| I42 | cardiomyopathy; dilated cardiomyopathy; hypertroph | 0.571636 | 13 |
| N20 | nephrolithiasis; ureterolithiasis; urolithiasis | 0.569235 | 5 |
| I35 | aortic stenosis | 0.568355 | 8 |
| C67 | urinary bladder cancer; urinary bladder carcinoma | 0.568161 | 20 |
| N17 | acute kidney injury; kidney failure | 0.56605 | 27 |
| I20 | angina pectoris | 0.565284 | 19 |
| F31 | bipolar disorder; bipolar ii disorder | 0.56366 | 3 |
| G20 | parkinson disease | 0.561607 | 11 |
| C34 | bronchus cancer; lung adenocarcinoma; lung cancer; | 0.559652 | 35 |
| D86 | sarcoidosis; skin sarcoidosis | 0.557763 | 4 |
| N18 | chronic kidney disease | 0.556599 | 22 |
| M05 | acpa-negative rheumatoid arthritis; acpa-positive  | 0.555909 | 2 |
| M17 | knee osteoarthritis | 0.551133 | 7 |
| G47 | insomnia; narcolepsy; narcolepsy-cataplexy syndrom | 0.548797 | 44 |
| F41 | anxiety disorder | 0.54798 | 3 |
| L20 | atopic eczema | 0.546164 | 6 |
| J84 | idiopathic pulmonary fibrosis; interstitial lung d | 0.54541 | 4 |
| H33 | retinal break; retinal detachment | 0.544784 | 4 |
| M16 | hip osteoarthritis | 0.544752 | 7 |
| I73 | peripheral vascular disease | 0.541283 | 4 |
| M19 | arthritis; osteoarthritis | 0.539981 | 107 |
| R51 | headache; headache disorder | 0.539761 | 9 |
| E53 | vitamin b12 deficiency | 0.537925 | 1 |
| H18 | corneal disease; corneal dystrophy; keratoconus | 0.537542 | 4 |
| M84 | bone fracture | 0.537539 | 42 |
| H90 | age-related hearing impairment; deafness; hearing  | 0.536356 | 6 |
| L72 | epidermal inclusion cyst; follicular cyst | 0.536191 | 3 |
| C85 | non-hodgkins lymphoma | 0.534691 | 22 |
| R55 | syncope | 0.53439 | 2 |
| L82 | seborrheic keratosis | 0.531145 | 2 |
| H35 | age-related macular degeneration; macular degenera | 0.530209 | 7 |
| M47 | spondylosis | 0.52984 | 5 |
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
| R94 | abnormal ekg | 0.500572 | 1 |
| I49 | brugada syndrome | 0.497895 | 2 |