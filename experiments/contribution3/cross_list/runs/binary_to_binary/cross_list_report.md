# Contribution3: Cross List Report (rootcode)

## Terminology

- **Target trait**: Trait being predicted / transferred into
  - Restricted to **main analysis** ICDs: `include_in_analysis == 1` in `prs_adjauc_metadata` (aligned with C2)
  - **Type A**: target traits **without self AUC**
  - **Type B**: target traits **with self AUC**
  - All target traits in this report are in C1's AUC matrix, so benchmark validation is available.
- **Cross trait**: Trait whose PRS models are recommended for the target trait (binary trait resolved from PGS ontology mapping)
- PGS models with unknown source ontology are **excluded**

## Cross-list workflow

1. **Partition screened target traits** into Type A (without self AUC) and Type B (with self AUC).
2. **Retain cross-list target traits** — Type A target traits need at least one qualifying cross model; Type B target traits need a cross model that beats self.
3. **Determine cross traits** — for each retained target trait, link to retained cross PGS → ontology (see **Top Cross Trait** and `cross_list_detail_*.csv`).
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
| **Cross-list target traits** (retained Type A ∪ retained Type B) | **26** |
| — Retained Type A (Without Self AUC + qualifying cross) | 2 |
| — Retained Type B (With Self AUC + cross beats self) | 24 |
| Total screened rows in matrix filter | 94 |
| Type A total (Without Self AUC) | 4 |
| — Type A without qualifying cross | 2 |
| Type B total (With Self AUC) | 90 |
| — Type B self optimal | 66 |
| Any cross candidates (Type A + Type B) | 26 |

*Partition:* `Type A retained` (2) + `Type A no qualifying cross` (2) + `Type B beats self` (24) + `Type B self optimal` (66) = **94**. *Cross-list target traits* = 2 + 24 = **26**.


## Type A: Target Traits Without Self AUC

*Included in the retained cross-list target traits.*

Total: 2 target traits

| Target ICD | Target Trait | Top Cross AUC | Cross Trait ICD | Top Cross Trait | N Cross Models |
|-----------|--------------|---------------|-----------------|-----------------|----------------|
| M93 | slipped epiphyses | 0.571133 | C54 | endometrial cancer; endometrial carcinom | 1813 |
| H20 | iritis | 0.570921 | M45; M19; M36; M06 | ankylosing spondylitis; arthritis; conne | 1813 |

## Type A: Without Self AUC But No Qualifying Cross

*Not included in the retained cross-list target traits under current rules; best available cross-trait evidence shown for reference.*

Total: 2 target traits

| Target ICD | Target Trait | Top Available Cross AUC | Cross Trait ICD | Top Cross Trait | Available N Cross Models |
|-----------|--------------|-------------------------|-----------------|-----------------|--------------------------|
| B07 | common wart | 0.525604 | C43 | melanoma | 1813 |
| E27 | chronic primary adrenal insufficiency | 0.548029 | F32 | depressive disorder; major depressive di | 1813 |

## Type B: Cross-Trait PRS Beats Self

*Included in the retained cross-list target traits.*

Total: 24 target traits

| Target ICD | Target Trait | Self Best AUC | Top Cross AUC | Improvement | Cross Trait ICD | Top Cross Trait | N Cross Models | N Unique Cross Traits |
|-----------|--------------|---------------|---------------|-------------|-----------------|-----------------|----------------|----------------|
| N40 | benign prostatic hyperplasia | 0.523621 | 0.642255 | +0.1186 | C61; N41 | prostate cancer; prostate carcinoma; pro | 1 | 3 |
| M05 | acpa-negative rheumatoid arthritis; acpa | 0.555909 | 0.659479 | +0.1036 | M19; M36; M10; M06 | arthritis; connective tissue disease; go | 27 | 7 |
| C54 | endometrial cancer; endometrial carcinom | 0.533241 | 0.631408 | +0.0982 | F32 | depressive disorder; major depressive di | 209 | 95 |
| J43 | emphysema | 0.529203 | 0.613674 | +0.0845 | J44 | chronic obstructive pulmonary disease | 19 | 22 |
| G30 | alzheimer disease; late-onset alzheimer' | 0.591008 | 0.662392 | +0.0714 | F32 | depressive disorder; major depressive di | 36 | 37 |
| D25 | uterine fibroid | 0.526428 | 0.586495 | +0.0601 | D26 | uterine benign neoplasm | 16 | 13 |
| I27 | cor pulmonale | 0.524334 | 0.584039 | +0.0597 | E66 | obesity; overnutrition | 36 | 28 |
| S52 | radius fracture | 0.521229 | 0.577664 | +0.0564 | M84; M81 | bone fracture; osteoporosis | 6 | 2 |
| N04 | nephrotic syndrome | 0.544952 | 0.600912 | +0.0560 | C34 | lung cancer; lung carcinoma | 19 | 18 |
| F43 | post-traumatic stress disorder | 0.501665 | 0.554185 | +0.0525 | F32 | depressive disorder; major depressive di | 34 | 23 |
| F03 | dementia | 0.575756 | 0.622799 | +0.0470 | F32 | depressive disorder; major depressive di | 7 | 7 |
| D04 | skin carcinoma in situ | 0.580195 | 0.62584 | +0.0456 | C43 | melanoma | 7 | 2 |
| I21 | acute myocardial infarction; non-st elev | 0.577853 | 0.622277 | +0.0444 | I25 | coronary artery disease; coronary athero | 10 | 5 |
| C56 | high grade ovarian serous adenocarcinoma | 0.585803 | 0.629103 | +0.0433 | C61; N41 | prostate cancer; prostate carcinoma; pro | 7 | 6 |
| F31 | bipolar disorder; bipolar ii disorder | 0.56366 | 0.606284 | +0.0426 | F32 | depressive disorder; major depressive di | 3 | 2 |
| J33 | nasal cavity polyp | 0.555651 | 0.597926 | +0.0423 | J45 | asthma | 30 | 1 |
| M34 | systemic scleroderma | 0.575363 | 0.616099 | +0.0407 | M36; M32 | connective tissue disease; lupus erythem | 3 | 3 |
| L03 | cellulitis | 0.519058 | 0.556386 | +0.0373 | E66 | obesity; overnutrition | 6 | 10 |
| F90 | attention deficit hyperactivity disorder | 0.520508 | 0.557077 | +0.0366 | F32 | depressive disorder; major depressive di | 4 | 2 |
| L55 | sunburn | 0.520772 | 0.557133 | +0.0364 | I10 | hypertension | 9 | 6 |
| N02 | iga glomerulonephritis | 0.519844 | 0.552574 | +0.0327 | J45 | asthma | 6 | 12 |
| G40 | epilepsy | 0.525585 | 0.554606 | +0.0290 | R51 | headache; headache disorder | 1 | 2 |
| E88 | metabolic syndrome | 0.531998 | 0.560397 | +0.0284 | E66 | obesity; overnutrition | 2 | 3 |
| I24 | myocardial infarction | 0.580234 | 0.607032 | +0.0268 | I25 | coronary artery disease; coronary athero | 1 | 3 |

## Type B: Self Models Already Optimal

*Not included in the retained cross-list target traits (self PRS sufficient under current rules; reference only).*

Total: 66 target traits

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
| I80 | phlebitis | 0.578337 | 3 |
| F32 | depressive disorder; major depressive disorder | 0.5779 | 30 |
| M08 | enthesitis-related juvenile idiopathic arthritis;  | 0.576778 | 4 |
| M81 | osteoporosis | 0.573768 | 13 |
| D68 | blood coagulation disease; congenital vitamin k-de | 0.57209 | 3 |
| I42 | cardiomyopathy; dilated cardiomyopathy; hypertroph | 0.571636 | 13 |
| N20 | nephrolithiasis; ureterolithiasis; urolithiasis | 0.569235 | 5 |
| I35 | aortic stenosis | 0.568355 | 8 |
| C67 | urinary bladder cancer; urinary bladder carcinoma | 0.568161 | 20 |
| N17 | acute kidney injury; kidney failure | 0.56605 | 27 |
| I20 | angina pectoris | 0.565284 | 19 |
| G20 | parkinson disease | 0.561607 | 11 |
| C34 | bronchus cancer; lung adenocarcinoma; lung cancer; | 0.559652 | 35 |
| D86 | sarcoidosis; skin sarcoidosis | 0.557763 | 4 |
| N18 | chronic kidney disease | 0.556599 | 22 |
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
| J30 | allergic rhinitis; seasonal allergic rhinitis; vas | 0.525578 | 2 |
| H91 | hearing loss | 0.524251 | 4 |
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
| D64 | anemia | 0.50106 | 1 |
| R94 | abnormal ekg | 0.500572 | 1 |
| I49 | brugada syndrome | 0.497895 | 2 |