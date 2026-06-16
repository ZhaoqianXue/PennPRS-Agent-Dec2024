# Within Formal Three-Arm Definitions

This file is the canonical naming and scope definition for the clean Full44 within-phenotype PRS selection comparison.
Use these names in reports, figures, captions, and ablation summaries unless this file is explicitly superseded.

## Scope

- Benchmark: EFO-clean 44-disease within-phenotype PRS selection.
- Scoring: AoU benchmark rank within each disease-specific evaluated PGS set; lower rank is better.
- Hit@k: true when the selected PGS rank is less than or equal to k.
- Candidate universe: fixed within-disease PGS candidate pool; no arm may add new PGS IDs.
- Candidate order: clean stable-hash-shuffled order for LLM arms.
- Model: gpt-5.4 family run set retained on 2026-06-15.

## Formal Arms

| Formal display name | Stable key | Definition | LLM | PRS skill | Architecture | Cost accounting |
|---|---|---|---:|---:|---|---|
| PRS Agent | `prs_agent_double_stage` | Full PRS Agent with skill-grounded within-phenotype system prompts. Stage 1 emits a bounded carried-forward shortlist; Stage 2 selects from that carried set. | Yes | Yes | Double-stage: Stage 1 shortlist plus Stage 2 compact selector | OpenAI API cost recorded |
| General LLM | `general_llm_prompt_only_no_skill_single_stage` | The prompt-only/no-skill/single-stage fullpool arm. It receives the same PGS schema/candidate records and a within-selection system prompt, but no PRS Agent skill context and no two-stage shortlist. | Yes | No | Single-stage fullpool judge | OpenAI API cost recorded |
| PGS Report | `pgs_report_reported_max_baseline` | Deterministic PGS Catalog reported-performance baseline within the same fixed candidate pool. It selects the candidate with the strongest disease-consistent reported PGS Catalog performance record used by the report baseline. | No | No | Report/catalog-derived baseline, no LLM selector | No OpenAI API cost |

## Naming Rules

- `General LLM` is the formal display name for `general_llm_prompt_only_no_skill_single_stage`.
- `General LLM` in this comparison does **not** mean the archived `GENERAL_LLM_BASELINE_SYSTEM_PROMPT` experiment.
- `General LLM` does **not** use the PRS Agent skill, neutral digest as a decision aid beyond visible schema compression, Stage 1 shortlist, or Stage 2 carried-set selector.
- `PRS Agent` means the retained clean double-stage PRS Agent run, not earlier skill-iteration, proxy-ranker, audit, pairwise, or hidden-benchmark ablations.
- `PGS Report` means the deterministic PGS Catalog reported-performance/report baseline. It is not an LLM selector.
- If implementation details are needed in methods text, write: `General LLM (prompt-only/no-skill/single-stage fullpool)`.
- If compact figure labels are needed, use: `PRS Agent`, `General LLM`, and `PGS Report`.

## Retained Aggregate Results

| Arm | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 | Cost |
|---|---:|---:|---:|---:|---:|---:|
| PRS Agent | 15/44 (34.09%) | 20/44 (45.45%) | 23/44 (52.27%) | 24/44 (54.55%) | 25/44 (56.82%) | $5.4003 |
| General LLM | 11/44 (25.00%) | 16/44 (36.36%) | 20/44 (45.45%) | 23/44 (52.27%) | 27/44 (61.36%) | $4.2713 |
| PGS Report | 5/44 (11.36%) | 8/44 (18.18%) | 15/44 (34.09%) | 21/44 (47.73%) | 22/44 (50.00%) | - |

## Retained Source Artifacts

- PRS Agent:
  `experiments/contribution2/recommendation/runs/pairwise-rerank-gpt-5.4-t1__44disease__full44-current-stage12-gpt54-direct-20260615-20260614-232423/experiment_pairwise_rerank_summary.json`
- General LLM:
  `experiments/contribution2/recommendation/runs/pairwise-rerank-gpt-5.4-t1__44disease__full44-promptonly-noskill-gpt54-singlefullpool-20260615-20260615-021147/experiment_pairwise_rerank_summary.json`
- PGS Report:
  `experiments/contribution2/recommendation/archive/cleanup_20260615_keep_two_runs/docs/full44_three_arm_prs_promptonly_pgs_report_20260615.json`

## Archived Or Non-Formal Arms

The following are not formal arms for this three-arm comparison:

- Correct General LLM baseline using `GENERAL_LLM_BASELINE_SYSTEM_PROMPT`.
- Earlier General/no-skill runs that were not the retained prompt-only/no-skill/single-stage fullpool run.
- Earlier PRS Agent skill iterations, proxy-ranker variants, hidden-benchmark objectives, pairwise judges, audit traces, or Stage2-only replays.
- Target10-only experiments and Stage2-only replays; these may be ablations or development diagnostics, but not formal Full44 three-arm results.

## Relationship To Two-Arm Retained Results

`full44_clean_retained_two_arm_results_20260615.md` preserves the two OpenAI-costed LLM runs requested during cleanup.
This file extends the fixed comparison vocabulary by adding the non-LLM `PGS Report` arm and by making `General LLM` the formal display name for the retained prompt-only/no-skill/single-stage arm.
