# Full44 Clean Retained Two-Arm Results

Only the two user-specified retained OpenAI-costed LLM experiment results are shown here. Other comparison, failed-variant, and General-baseline artifacts from this cleanup pass were moved to archive.

Formal three-arm naming is defined in `within_formal_three_arm_definitions_20260615.md`. In that file, the retained prompt-only/no-skill/single-stage arm is called **General LLM**.

| Arm | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 | Cost |
|---|---:|---:|---:|---:|---:|---:|
| PRS Agent double-stage | 15/44 | 20/44 | 23/44 | 24/44 | 25/44 | $5.4003 |
| General LLM (prompt-only/no-skill/single-stage) | 11/44 | 16/44 | 20/44 | 23/44 | 27/44 | $4.2713 |

## Retained Source Runs

- PRS Agent double-stage: `experiments/contribution2/recommendation/runs/pairwise-rerank-gpt-5.4-t1__44disease__full44-current-stage12-gpt54-direct-20260615-20260614-232423`
- General LLM (prompt-only/no-skill/single-stage): `experiments/contribution2/recommendation/runs/pairwise-rerank-gpt-5.4-t1__44disease__full44-promptonly-noskill-gpt54-singlefullpool-20260615-20260615-021147`

## Archived Non-Retained Artifacts

`experiments/contribution2/recommendation/archive/cleanup_20260615_keep_two_runs/archive_manifest.tsv`
