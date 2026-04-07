# Catalog-Gap Hard-Drop Rules

This note documents the hard-drop filter applied to
[`avail_traits.csv`](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution3/cross_list/catalog_gap/avail_traits.csv)
by
[`filter_avail_traits_hard_drop.py`](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution3/cross_list/catalog_gap/filter_avail_traits_hard_drop.py).

The script now fetches ICD descriptions live from the official NLM Clinical
Tables ICD-10-CM API instead of reading local description files:
[Clinical Tables ICD-10-CM API](https://clinicaltables.nlm.nih.gov/apidoc/icd10cm/v3/doc.html).
For non-leaf ICD roots, the script aggregates matching descendant ICD-10-CM
names from the API and uses that aggregated text for filtering.

## Why this filter exists

`avail_traits.csv` is only an upstream "available ICD" pool. It is not yet a
curated list of disease endpoints worth carrying into PennPRS catalog-gap work.

Per the project SOP, Contribution 1 should benchmark a curated set of
representative disease traits rather than every available All of Us ICD.
The overlap / SOP scripts in this repo already treat symptoms, injuries,
measurements, status codes, and overly broad labels as poor disease targets.

This filter removes only the traits that are obviously low-value for the
current disease-focused PRS benchmark / transfer workflow.

## Output files

Running the script writes:

- `avail_traits_hard_drop.csv`: excluded ICDs with category and reason
- `avail_traits_keep.csv`: remaining ICDs after hard-drop filtering

## Description source

- Input ICD roots still come from `avail_traits.csv`.
- `description` is now built from live ICD-10-CM API results.
- The script queries the ICD root against the API, keeps only codes whose ICD
  code starts with that root, and aggregates the matched names.
- Hard-drop classification stays conservative.
- Prefix-based hard-drop rules (`R`, `Z`, `O`, `S/T/V/W/X/Y`) are unchanged.
- The non-prefix hard-drop rules continue to use the manually curated ICD-root
  sets already defined for this workflow, rather than auto-dropping any root
  whose descendant API text happens to contain a trigger word.
- The `description` field written to CSV is a shortened display summary derived
  from those API-matched names.

## Hard-drop categories

### 1. `injury_toxic_external`

Includes ICD roots in the `S/T/V/W/X/Y` family and similar acute event traits.

Why drop:

- These are acute injuries, poisonings, external-cause events, or
  procedure-linked events.
- They are not stable disease endpoints.
- Their phenotype definition is dominated by trauma, exposure, accident,
  or care context rather than baseline disease biology.
- They are poor targets for disease-level PRS benchmark or cross-disease transfer.

Examples:

- `S06` concussion
- `S02` nasal fracture
- `S69` unspecified hand/wrist injury
- `T14` unspecified body-region injury
- `T50` poisoning by unspecified drugs
- `Y83` / `Y84` procedure-caused abnormal reaction

### 2. `symptom_abnormal_finding`

Includes ICD roots in the `R` family, plus a small number of symptom-like pain
traits outside `R`.

Why drop:

- These are symptoms, complaints, test abnormalities, or imaging findings,
  not disease entities.
- They are biologically nonspecific and aggregate many unrelated causes.
- A PRS benchmark on these traits is hard to interpret and hard to align with
  disease-focused PGS Catalog traits.

Examples:

- `R89` abnormal finding in specimens
- `R91` abnormal lung finding
- `R10` abdominal pain
- `R05` cough
- `R73` hyperglycemia, unspecified
- `R97` elevated PSA

### 3. `status_aftercare_allergy`

Includes ICD roots in the `Z` family.

Why drop:

- These are status, aftercare, susceptibility, screening, or encounter codes.
- They represent healthcare process, background condition, device presence,
  or prior history rather than active disease.
- They are not appropriate as primary disease endpoints for catalog-gap PRS work.

Examples:

- `Z48` aftercare following surgery for neoplasm
- `Z95` presence of coronary angioplasty implant and graft
- `Z99` dependence on devices
- `Z15` genetic susceptibility to other disease
- `Z71` feared complaint with no diagnosis

### 4. `pregnancy_perinatal`

Includes ICD roots in the `O` family.

Why drop:

- These are pregnancy- or perinatal-specific endpoints.
- They depend on a narrow life-stage context and are out of scope for the
  current general disease-focused catalog-gap workflow.
- They should be handled in a dedicated obstetric/perinatal project if needed.

Examples:

- `O09` supervision of elderly multigravida
- `O03` spontaneous abortion
- `O48` post-term pregnancy
- `O99` diseases complicating pregnancy

### 5. `postproc_complication_status`

Includes non-`Z` ICDs whose description clearly indicates postsurgical or
postprocedural state / complication.

Why drop:

- These traits are dominated by treatment history or care pathway.
- They are not primary disease endpoints.
- Genetic signal is difficult to interpret separately from intervention history.

Examples:

- `K91` postsurgical malabsorption
- `K66` postprocedural adhesions
- `E89` postprocedural hypothyroidism

### 6. `broad_unspecified_umbrella`

Includes vague disorder families such as "other specified disorders of X" or
"disease of X, unspecified".

Why drop:

- These umbrella codes combine heterogeneous biology under one broad label.
- They are too vague to be clean targets for PRS benchmark or trait transfer.
- Matching them to PGS Catalog traits or external trait IDs is unstable.

Examples:

- `E07` disorder of thyroid, unspecified
- `G95` disease of spinal cord, unspecified
- `J34` other specified disorders of nose and nasal sinuses
- `K31` other diseases of stomach and duodenum
- `N64` other specified disorders of breast

### 7. `acute_or_exposure_dominant_infectious`

Includes acute infectious traits whose phenotype is dominated by short-term
exposure or encounter context rather than stable disease liability.

Why drop:

- These are usually transient infectious episodes.
- Their signal is driven more by exposure and healthcare timing than by a
  stable disease-risk target.
- They are weak fits for disease-level PRS benchmark or transfer.

Examples:

- `J06` acute upper respiratory infection
- `J20` acute bronchitis
- `J02` acute pharyngitis
- `A09` infectious gastroenteritis
- `B34` viral infection, unspecified

### 8. `secondary_manifestation_or_complication`

Includes traits that are usually downstream manifestations, physiologic
consequences, or complication states.

Why drop:

- These are often consequences of other diseases rather than primary diseases.
- A PRS benchmark on these traits is hard to interpret biologically.
- They are poor targets for catalog-gap trait triage.

Examples:

- `J90` pleural effusion
- `I31` pericardial effusion
- `I51` cardiomegaly
- `D63` anemia in chronic kidney disease

### 9. `non_specific_benign_or_uncertain_neoplasm`

Includes benign, uncertain-behavior, or otherwise poorly specified neoplasm
traits.

Why drop:

- These are not clean malignant-disease endpoints.
- Some are too broad, some are benign, and some have uncertain biologic target
  definition.
- They are weak fits for the current disease-focused catalog-gap workflow.

Examples:

- `D31` benign neoplasm of choroid
- `D48` neoplasm of uncertain behavior of skin
- `D49` neoplasm of unspecified behavior of bone / soft tissue / skin
- `C80` malignant primary neoplasm, unspecified

### 10. `escaped_broad_unspecified_group`

Includes additional vague disease-group labels that were still too broad to
keep after the first-pass hard-drop rules.

Why drop:

- These remain heterogeneous umbrella groups.
- They do not define a sufficiently clean disease endpoint for catalog-gap
  PRS triage.

Examples:

- `K83` other specified diseases of biliary tract
- `M79` other specified soft tissue disorders
- `M12` arthropathy, unspecified
- `M13` polyarthritis, unspecified

## Current expected counts

With the current `avail_traits.csv`, the script should produce:

- `252` hard-drop ICDs
- `395` kept ICDs

Category counts:

- `injury_toxic_external`: `83`
- `symptom_abnormal_finding`: `70`
- `status_aftercare_allergy`: `22`
- `pregnancy_perinatal`: `17`
- `broad_unspecified_umbrella`: `18`
- `postproc_complication_status`: `3`
- `acute_or_exposure_dominant_infectious`: `12`
- `secondary_manifestation_or_complication`: `6`
- `non_specific_benign_or_uncertain_neoplasm`: `11`
- `escaped_broad_unspecified_group`: `10`
