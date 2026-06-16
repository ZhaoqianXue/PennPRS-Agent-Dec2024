# Archived Within Prompt Surfaces

Archived on 2026-06-15 after retaining only the two formal result arms:

- PRS Agent double-stage:
  - `WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT`
  - `WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT`
  - `WITHIN_STAGE2_SELECTOR_SYSTEM_PROMPT`
- PRS Agent prompt-only/no-skill/single-stage:
  - `WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT`

The active package `src.server.core.within_prompts` exports only those retained
system prompts plus the required Stage-1 and Stage-2/fullpool user-message
builders. Everything else here is non-production historical/ablation material.

Archived files:

- `selectors_pre_cleanup_20260615.py`: previous selector/general/pairwise/ranker/
  ReAct/refinement/objective prompt surfaces.
- `audits_pre_cleanup_20260615.py`: previous audit prompt surfaces and audit
  message builders.

Do not import these files from production paths. They exist only so historical
artifacts and old ablation scripts remain inspectable.
