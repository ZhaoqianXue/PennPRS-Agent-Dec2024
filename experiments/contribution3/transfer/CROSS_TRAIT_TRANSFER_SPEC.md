# Cross Trait Transfer Spec

## Status

This document is the current source of truth for Contribution3 Cross Trait Transfer.

- Active implementation: `experiments/contribution3/transfer/`
- Active runtime condition: `all-tools`
- Scope: binary-input target universe only for v1
- Current target universe: the 28 retained binary-input target traits from `experiments/contribution3/cross_list/analysis/phase2/binary_target_cross_trait_summary.csv`

## Module Boundary

Cross Trait Transfer is a **tool-calling matching module**, not a model-ranking module.

- Responsibility:
  - map a `target trait` to the single best `cross trait bundle`
  - or abstain with `NO_MATCH`
- Not responsible for:
  - ranking individual PGS models
  - downstream PRS ranking
  - evaluation of Contribution2

Once a bundle is matched, the module passes that bundle's `candidate_pgs_ids` to Contribution2 Step 1, which remains the only PRS model recommendation module.

## Runtime Contract

### Input

- `TargetTraitQuery`
  - `target_id`
  - `target_code`
  - `target_label`
  - `target_type`
  - `aliases`
- `CandidateBundleDossier`
  - static candidate bundle context only
  - bundle order must be deterministic
  - dossier must not expose retrieval scores or any implied rank

### Output

- `MATCHED(best_bundle_id)` with:
  - `best_cross_trait`
  - `candidate_pgs_ids`
  - `confidence`
  - `rationale`
  - `evidence_summary`
- or `NO_MATCH`

## Static Assets

### TraitBundleIndex

Built from:

- `data/pgs_all_metadata/pgs_all_metadata_scores.csv`
- `data/pgs_all_metadata/pgs_all_metadata_efo_traits.csv`
- `data/pgs_all_metadata/pgs_all_metadata_performance_metrics.csv`

Each bundle includes:

- `bundle_id`
- `canonical_label`
- `bundle_type`
- `aliases`
- `candidate_pgs_ids`
- `n_models`
- `source_efo_ids`
- `source_mondo_ids`

Generated asset:

- `experiments/contribution3/transfer/runs/tool_calling_agent/trait_bundle_index.json`

### CandidateBundleDossier

Built offline from the full bundle index for each retained target.

Design constraints:

- dossier is a compressed candidate pool, not a decision tool
- dossier can use lexical / overlap / metadata heuristics for recall
- dossier must not leak retrieval rank into the LLM decision
- dossier must exclude self-like bundles

Generated asset:

- `experiments/contribution3/transfer/runs/tool_calling_agent/binary_candidate_dossiers.json`

## Agent Runtime

Cross Trait Transfer is implemented as a single LLM tool-calling agent with exactly **three runtime tools**.

### Tool 1: `cross_trait_genetic_correlation`

Purpose:

- query genetic correlation evidence between the target trait and a batch of candidate bundles

Returns per candidate:

- `rg_meta`
- `rg_z_meta`
- `n_correlations`
- provenance / missing-data reason

### Tool 2: `cross_trait_heritability`

Purpose:

- query heritability evidence for candidate bundles

Returns per candidate:

- `best_h2`
- `source`
- `ancestry`
- `confidence`

### Tool 3: `cross_trait_open_targets`

Purpose:

- query shared-gene / pathway mechanism evidence for shortlisted candidates

Returns per candidate:

- `shared_genes`
- `shared_pathways`
- `confidence_level`
- `mechanism_summary`
- unavailable reason

Internal ontology resolution is allowed inside this tool, but it does not count as a separate tool.

## Agent Decision Policy

The LLM is the decision-maker. The runtime is **not** a deterministic reranker.

Required policy:

- inspect multiple dossier candidates before deciding
- do not use dossier order as evidence
- do not use lexical / semantic similarity as the main ranking signal
- use only:
  - genetic correlation
  - heritability
  - Open Targets mechanism evidence
  - LLM synthesis over those tool outputs
- return `NO_MATCH` when evidence is not strong enough

Recommended tool-use pattern:

1. screen multiple candidates with `cross_trait_genetic_correlation`
2. gather `cross_trait_heritability` for stronger finalists
3. gather `cross_trait_open_targets` for finalists
4. compare evidence and output one bundle or `NO_MATCH`

## Contribution2 Handoff

If the agent returns `MATCHED(best_bundle_id)`:

- resolve the matched bundle
- extract its `candidate_pgs_ids`
- pass that whitelist to Contribution2 Step 1

Contribution2 then performs PRS model ranking exactly as in Contribution2.

Current adapter:

- `experiments/contribution3/transfer/contribution2_adapter.py`

## Evaluation

Cross Trait Transfer is evaluated as a **bundle-matching** task only.

Silver labels:

- `experiments/contribution3/cross_list/analysis/phase2/binary_cross_trait_shortlist.csv`

Important:

- the shortlist is **not** a runtime input
- the shortlist is the silver-label evaluation source
- Contribution2 evaluation is out of scope for Contribution3 evaluation

Current evaluation outputs:

- `experiments/contribution3/transfer/runs/tool_calling_agent/evaluation/cross_trait_transfer_eval_detail.csv`
- `experiments/contribution3/transfer/runs/tool_calling_agent/evaluation/cross_trait_transfer_eval_summary.json`

Primary metrics:

- `weighted_hit@1`
- `weighted_mrr`
- `bundle_resolution_rate`
- `matched_rate`
- `abstain_precision`
- average tool calls
- tool coverage by tool type

## Current Development Priority

Current priority is to stabilize the `all-tools` condition.

- do not prioritize ablations yet
- treat `dossier-only`, `gc-only`, and `gc-h2` as later analysis conditions
- focus on fixing bad `MATCHED` outputs and bad `NO_MATCH` abstains under `all-tools`

## Current Online Result Snapshot

Current full online run:

- condition: `all-tools`
- targets: `28`
- `MATCHED`: `18`
- `NO_MATCH`: `10`

Current evaluation snapshot:

- `weighted_hit@1 = 0.3107`
- `weighted_mrr = 0.3107`
- `bundle_resolution_rate = 0.9643`
- `matched_rate = 0.6429`
- `abstain_precision = 0.1000`
- `average_tool_calls = 2.7143`

These numbers are descriptive, not a freeze point. They indicate that the tool-calling architecture is online, but the `all-tools` policy still needs tuning.

## Related Files

- `experiments/contribution3/transfer/common.py`
- `experiments/contribution3/transfer/tools.py`
- `experiments/contribution3/transfer/agent.py`
- `experiments/contribution3/transfer/batch/run_batch.py`
- `experiments/contribution3/transfer/eval/evaluate.py`
- `experiments/contribution3/transfer/prompts/transfer_prompt.py`
- `experiments/contribution3/cross_list/cross_trait_transfer_todo.md`
