# Contribution2 PEV With prs-model-evaluator Skill

- Diseases: 11
- Trials per disease: 1
- Model: gpt-5.2
- Union CSV: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__89disease.csv`

## Hit@k

- Hit@1: 5/11 = 45.45%
- Hit@2: 7/11 = 63.64%
- Hit@3: 7/11 = 63.64%
- Hit@4: 9/11 = 81.82%
- Hit@5: 9/11 = 81.82%

## Rank

- Modal mean NRS: 0.7302

## Harness

- TRIAGE, PICK, and CRITIC each consume the shared prs-model-evaluator skill.
- Raw heritability records are exposed as advisory evidence, not embedded in the skill text.
- The final JSON is converted to the existing Contribution2 Step1Decision shape for evaluation.