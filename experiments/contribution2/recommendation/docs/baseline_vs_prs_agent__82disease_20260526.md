# Baseline vs PRS Agent on updated 82-disease within-phenotype benchmark

Generated on 2026-05-26 from the updated Contribution 2 disease union after AoU-overlap filtering of the benchmark matrix.

## Inputs
- Disease list: `experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__82disease.csv`
- Plain disease list: `experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__82disease.txt`
- Baseline run: `experiments/contribution2/recommendation/runs/without-domain-gpt-5.2-t1__82disease__c82-within-baseline-20260526`
- PRS Agent run: `experiments/contribution2/recommendation/runs/pairwise-rerank-gpt-5.2-t1__82disease__c82-within-agent-top5-final-20260526-20260526-120628`
- Per-disease comparison CSV: `experiments/contribution2/recommendation/docs/baseline_vs_prs_agent__82disease_20260526.csv`

## Evaluation mapping
- `selected-model AUC`: AoU benchmark AUC of the PGS model selected by each method.
- `Hit@k`: whether the selected PGS model is among the empirical benchmark top-k models for the disease.
- `Top percentile hit`: whether the selected PGS model is within the top empirical benchmark percentile among candidates.
- `Rank`: empirical benchmark rank of the selected PGS model; lower is better.
- `Coverage`: fraction of diseases for which the method produced a valid PGS ID present in the benchmark candidate set.

## Aggregate results

| Metric | Baseline LLM | PRS Agent | Difference |
|---|---:|---:|---:|
| Valid output coverage | 82/82 (1.000) | 82/82 (1.000) | +0.000 |
| Mean selected-model AUC | 0.587 | 0.598 | +0.011 |
| Median selected-model AUC | 0.573 | 0.582 | +0.009 |
| Mean empirical rank | 6.79 | 4.77 | -2.02 |
| Mean rank percentile | 0.509 | 0.393 | -0.116 |
| Hit@1 | 22/82 (0.268) | 36/82 (0.439) | +14 hits (+0.171) |
| Hit@3 | 42/82 (0.512) | 54/82 (0.658) | +12 hits (+0.146) |
| Hit@5 | 57/82 (0.695) | 63/82 (0.768) | +6 hits (+0.073) |
| Top 5% hit | 23/82 (0.281) | 39/82 (0.476) | +16 hits (+0.195) |
| Top 10% hit | 25/82 (0.305) | 41/82 (0.500) | +16 hits (+0.195) |
| Top 25% hit | 35/82 (0.427) | 51/82 (0.622) | +16 hits (+0.195) |

## Selected-model AUC movement
- Exact AUC movement: PRS Agent higher in 29/82, tied in 47/82, lower in 6/82.
- With a +/-0.0025 near-tie band: PRS Agent higher in 28/82, near-tied in 48/82, lower in 6/82.
- Mean paired AUC change: +0.011; median paired AUC change: +0.000.
- Largest AUC gain: +0.174; largest AUC loss: -0.038.

## Largest gains

| Disease | Baseline PGS | Baseline AUC | PRS Agent PGS | PRS Agent AUC | Delta AUC | Rank change |
|---|---:|---:|---:|---:|---:|---:|
| testicular carcinoma | PGS000604 | 0.747 | PGS000796 | 0.921 | +0.174 | +9 |
| obesity | PGS001298 | 0.560 | PGS005235 | 0.648 | +0.087 | +7 |
| ulcerative colitis | PGS001306 | 0.600 | PGS004253 | 0.677 | +0.077 | +4 |
| chronic obstructive pulmonary disease | PGS001332 | 0.529 | PGS001783 | 0.606 | +0.076 | +8 |
| abdominal aortic aneurysm | PGS001784 | 0.562 | PGS003973 | 0.637 | +0.076 | +3 |
| late-onset alzheimer's disease | PGS000334 | 0.514 | PGS000054 | 0.569 | +0.055 | +2 |
| dupuytren contracture | PGS001254 | 0.632 | PGS002092 | 0.678 | +0.046 | +2 |
| myocardial infarction | PGS001316 | 0.546 | PGS004528 | 0.592 | +0.045 | +10 |
| coronary artery disease | PGS000013 | 0.576 | PGS003725 | 0.621 | +0.044 | +26 |
| cervical carcinoma | PGS001299 | 0.338 | PGS003428 | 0.380 | +0.042 | +1 |

## Diseases with lower selected-model AUC

| Disease | Baseline PGS | Baseline AUC | PRS Agent PGS | PRS Agent AUC | Delta AUC | Rank change |
|---|---:|---:|---:|---:|---:|---:|
| ovarian neoplasm | PGS000544 | 0.570 | PGS000550 | 0.532 | -0.038 | -8 |
| sleep apnea | PGS005220 | 0.578 | PGS005219 | 0.545 | -0.033 | -1 |
| lupus erythematosus | PGS003960 | 0.562 | PGS000754 | 0.542 | -0.020 | -1 |
| osteoporosis | PGS001274 | 0.563 | PGS004565 | 0.545 | -0.018 | -4 |
| knee osteoarthritis | PGS001192 | 0.525 | PGS002729 | 0.508 | -0.017 | -2 |
| urinary bladder cancer | PGS000071 | 0.556 | PGS000613 | 0.553 | -0.003 | -1 |

## Notes
- This is a single-trial run for each method across 82 diseases, using the updated no-AoU-overlap benchmark matrix.
- PRS Agent here refers to GPT-5.2 with the PRS Agent harness context and PRS Skill, followed by top-5 final selection.
- Baseline LLM here refers to GPT-5.2 direct selection from candidate model information without the PRS Agent harness context or PRS Skill.
