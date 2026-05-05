# Contribution2 PEV With prs-model-evaluator Skill

- Diseases: 2
- Trials per disease: 1
- Model: gpt-5.2
- Union CSV: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__89disease.csv`

## Hit@k

- Hit@1: 1/2 = 50.00%
- Hit@2: 1/2 = 50.00%
- Hit@3: 1/2 = 50.00%
- Hit@4: 2/2 = 100.00%
- Hit@5: 2/2 = 100.00%

## Rank

- Modal mean NRS: 0.7000

## Harness

- TRIAGE, PICK, and CRITIC each consume the shared prs-model-evaluator skill.
- Raw heritability records are exposed as advisory evidence, not embedded in the skill text.
- The final JSON is converted to the existing Contribution2 Step1Decision shape for evaluation.