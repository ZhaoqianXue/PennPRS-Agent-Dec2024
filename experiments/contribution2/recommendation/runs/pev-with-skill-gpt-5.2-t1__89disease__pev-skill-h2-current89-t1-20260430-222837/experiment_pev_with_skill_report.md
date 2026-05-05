# Contribution2 PEV With prs-model-evaluator Skill

- Diseases: 89
- Trials per disease: 1
- Model: gpt-5.2
- Union CSV: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__89disease.csv`

## Hit@k

- Hit@1: 22/89 = 24.72%
- Hit@2: 36/89 = 40.45%
- Hit@3: 45/89 = 50.56%
- Hit@4: 55/89 = 61.80%
- Hit@5: 62/89 = 69.66%

## Rank

- Modal mean NRS: 0.6033

## Harness

- TRIAGE, PICK, and CRITIC each consume the shared prs-model-evaluator skill.
- Raw heritability records are exposed as advisory evidence, not embedded in the skill text.
- The final JSON is converted to the existing Contribution2 Step1Decision shape for evaluation.