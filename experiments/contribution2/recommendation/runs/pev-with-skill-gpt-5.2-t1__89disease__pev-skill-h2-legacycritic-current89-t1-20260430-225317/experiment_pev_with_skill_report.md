# Contribution2 PEV With prs-model-evaluator Skill

- Diseases: 89
- Trials per disease: 1
- Model: gpt-5.2
- Union CSV: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__89disease.csv`

## Hit@k

- Hit@1: 28/89 = 31.46%
- Hit@2: 44/89 = 49.44%
- Hit@3: 57/89 = 64.04%
- Hit@4: 62/89 = 69.66%
- Hit@5: 67/89 = 75.28%

## Rank

- Modal mean NRS: 0.6896

## Harness

- TRIAGE, PICK, and CRITIC each consume the shared prs-model-evaluator skill.
- Raw heritability records are exposed as advisory evidence, not embedded in the skill text.
- The final JSON is converted to the existing Contribution2 Step1Decision shape for evaluation.