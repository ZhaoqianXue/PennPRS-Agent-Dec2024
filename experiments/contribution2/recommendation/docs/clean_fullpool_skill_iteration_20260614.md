# Clean single-stage fullpool skill iteration, 2026-06-14

## Scope

This iteration tested whether a skill-only refinement could improve the clean
single-stage fullpool PRS Agent selector after candidate-order decontamination.
The run used `gpt-5.4-mini`, `stable_hash_shuffle`, seed `pennprs-order-v1`,
`fullpool_judge`, `support` objective, and no fixed `top_k`.

The tested skill hypothesis emphasized:

- same-publication / same-study-family comparisons;
- same evaluation-context metric comparison;
- treating sample size and case count as precision/context fields rather than
  primary ranking axes;
- reducing headline metric availability bias.

The hypothesis did not improve clean performance and was not retained in the
production skill/reference files.

## Request inspection

Full44 dry run:

- manifest: `runs/with-domain-gpt-5.4-mini-t1__44disease__full44-skill-clean-v1-dryrun-20260614/experiment_with_domain_batch_manifest.json`
- requests: 44/44
- candidate order: `stable_hash_shuffle`
- seed: `pennprs-order-v1`
- candidate order equals benchmark order: 0/44
- benchmark top1 in first position: 3/44
- LLM-visible context contains `skill_context`: yes
- LLM-visible context contains `benchmark_ranked_ids`: no
- LLM-visible context contains `evidence_flags`: no
- forbidden prompt text hits for hidden benchmark / benchmark rank / top1 /
  external-validation performance / benchmark-selection: none in live fullpool
  request surface inspected.

Target10 dry run:

- manifest: `runs/with-domain-gpt-5.4-mini-t1__44disease__target10-skill-clean-v1-dryrun-20260614/experiment_with_domain_batch_manifest.json`
- requests: 10/10
- candidate order equals benchmark order: 0/10
- benchmark top1 in first position: 0/10
- LLM-visible context contains `skill_context`: yes
- LLM-visible context contains `benchmark_ranked_ids`: no

General/no-skill isolation was checked against
`runs/without-domain-gpt-5.4-mini-t1__44disease__general-cleanorder-dryrun-20260614/experiment_without_domain_batch_manifest.json`:
`skill_context=false`, `domain_knowledge=false`, candidate order source
`stable_hash_shuffle`, candidate order equals benchmark order 0/44.

## Results

| Run | Hit@1 | Hit@5 | Rank distribution |
| --- | ---: | ---: | --- |
| Clean PRS Agent seed v1 baseline | 7/44 | 22/44 | 1:7, 2-5:15, 6-10:15, 11-20:4, >20:3 |
| Clean PRS Agent seed v2 baseline | 11/44 | 24/44 | 1:11, 2-5:13, 6-10:11, 11-20:4, >20:5 |
| Clean PRS Agent seed v3 baseline | 8/44 | 23/44 | 1:8, 2-5:15, 6-10:11, 11-20:5, >20:5 |
| Clean General/no-skill seed v1 | 7/44 | 25/44 | 1:7, 2-5:18, 6-10:9, 11-20:6, >20:4 |
| Tested skill hypothesis, seed v1 | 6/44 | 20/44 | 1:6, 2-5:14, 6-10:18, 11-20:3, >20:3 |

Target10 with the tested skill hypothesis remained 0/10 Hit@1 and 0/10 Hit@5.

Compared with clean PRS Agent seed v1, the tested skill hypothesis improved
four diseases by benchmark rank and regressed seven:

- Improved: abdominal aortic aneurysm, glaucoma, major depressive disorder,
  urinary bladder carcinoma.
- Regressed: alzheimer disease, basal cell carcinoma, celiac disease, chronic
  kidney disease, chronic lymphocytic leukemia, knee osteoarthritis, prostate
  carcinoma.

The target10 winners were all outside Hit@5:

| Trait | Winner | Rank | Benchmark top1 |
| --- | --- | ---: | --- |
| type 2 diabetes mellitus | PGS002308 | 9/146 | PGS004838 |
| breast carcinoma | PGS003380 | 10/134 | PGS004579 |
| prostate carcinoma | PGS003766 | 66/89 | PGS000566 |
| hypertension | PGS001320 | 10/65 | PGS004786 |
| asthma | PGS001344 | 14/63 | PGS004724 |
| alzheimer disease | PGS004116 | 31/47 | PGS001348 |
| thyroid carcinoma | PGS000207 | 10/27 | PGS001799 |
| psoriasis | PGS001312 | 15/22 | PGS005311 |
| major depressive disorder | PGS003579 | 11/22 | PGS003333 |
| ovarian neoplasm | PGS000549 | 6/21 | PGS000546 |

## Cost

Full44 tested skill run:

- run: `runs/pairwise-rerank-gpt-5.4-mini-t1__44disease__full44-skill-clean-v1-singlefullpool-20260614-20260614-172739`
- calls: 44
- input tokens: 1,175,456
- cached input tokens: 0
- output tokens: 9,783
- total tokens: 1,185,239
- estimated cost: USD 0.9256

Target10 diagnostic run:

- run: `runs/pairwise-rerank-gpt-5.4-mini-t1__44disease__target10-skill-clean-v1-singlefullpool-20260614-20260614-172900`
- calls: 10
- input tokens: 533,016
- cached input tokens: 529,920
- output tokens: 2,329
- total tokens: 535,345
- estimated cost: USD 0.0525

Total incremental API cost for this iteration: USD 0.9781.

## Decision

The skill/reference refinement was reverted because it degraded clean full44
Hit@1, clean full44 Hit@5, and did not improve target10. The retained code
change is limited to production prompt wording and guardrail tests that remove
external-validation / benchmark-selection framing from LLM-visible production
prompt surfaces.

No additional stable-hash seeds were run because the single clean seed did not
beat the historical clean PRS Agent or clean General/no-skill baselines.
