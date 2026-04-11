# Cross Trait Transfer Spec

## Status

This document is the current source of truth for Contribution3 Cross Trait Evaluation.

- Active implementation: `experiments/contribution3/transfer/`
- Active runtime condition: `all-tools`
- Supported benchmark families:
  - `binary_to_binary`
  - `binary_to_continuous`
- Runtime target universe comes from:
  - `experiments/contribution3/cross_list/benchmark/<benchmark_family>/target_selection.csv`

## Module Boundary

Cross Trait Transfer remains a tool-calling matching module.

- Responsibility:
  - map a target trait to the single best cross-trait bundle
  - or abstain with `NO_MATCH`
- Downstream handoff:
  - pass `candidate_pgs_ids` from the matched bundle to Contribution2 Step 1
  - let Contribution2 select the final `PGS model`

Contribution3 evaluation is now end-to-end:

- `Cross Trait Transfer + PRS Recommendation`
- evaluated on the full Contribution1 AUC matrix

## Runtime Assets

### Shared Bundle Index

Built from the global PGS metadata:

- `data/pgs_all_metadata/pgs_all_metadata_scores.csv`
- `data/pgs_all_metadata/pgs_all_metadata_efo_traits.csv`

Output:

- `experiments/contribution3/transfer/runs/tool_calling_agent/trait_bundle_index.json`

### Benchmark-Specific Candidate Dossiers

Built per benchmark family from selected benchmark targets.

Output pattern:

- `experiments/contribution3/transfer/runs/tool_calling_agent/<benchmark_family>/candidate_dossiers.json`

## Agent Runtime

Cross Trait Transfer is implemented as one LLM tool-calling agent with three tools:

1. `cross_trait_genetic_correlation`
2. `cross_trait_heritability`
3. `cross_trait_open_targets`

The agent selects one bundle or returns `NO_MATCH`.

## Contribution2 Handoff

If the transfer agent returns `MATCHED(best_bundle_id)`:

- resolve the matched bundle
- extract `candidate_pgs_ids`
- hydrate Step 1 candidates directly from that explicit whitelist
- call Contribution2 Step 1 on that exact candidate universe
- output one final `best_model_id`

## Evaluation

Evaluation is no longer the old silver-label bundle-matching task.

`ground_truth_ranking.csv` under the benchmark folders remains a debugging asset only.

Current evaluation target:

- final recommended `PGS model`

Current benchmark:

- for each selected target trait, rank the recommended `PGS model`
- against the full Contribution1 AUC row for that target

Current matrix sources:

- Type B / main root benchmark:
  - `experiments/contribution1/result/aou_icd_260217/prs_adjauc_matrix_260217_rootcode.csv`
- Type A / nontarget benchmark:
  - `experiments/contribution1/result/aou_nontarget_pgs/prs_adjauc_matrix_notarget_pgs_qc.csv`

Current output pattern:

- transfer results:
  - `experiments/contribution3/transfer/runs/tool_calling_agent/<benchmark_family>/<condition>__<YYYYMMDD_HHMMSS>/results.json`
  - `candidate_dossiers.json` and `trait_bundle_index.json` remain in their existing stable asset locations.
- Contribution2 handoff results:
  - `experiments/contribution3/transfer/runs/tool_calling_agent/<benchmark_family>/<condition>/contribution2_recommendations.json`
- end-to-end evaluation detail:
  - `experiments/contribution3/transfer/runs/tool_calling_agent/<benchmark_family>/evaluation/<condition>__end_to_end_eval_detail.csv`
- end-to-end evaluation summary:
  - `experiments/contribution3/transfer/runs/tool_calling_agent/<benchmark_family>/evaluation/<condition>__end_to_end_eval_summary.json`

Primary metrics:

- `Mean-GPR`
  - Global Percentile Rank on the full Contribution1 AUC row
  - for evaluated targets:
    - `GPR_t = 1 - (rank_t - 1) / (n_t - 1)`
  - `NO_MATCH` / non-evaluable targets contribute `0` in the type-level average
- `Hit@Top 5% / 10% / 15% / 20% / 25%`
  - percentile hit on the full Contribution1 AUC row, not trait-local candidate pools
  - `NO_MATCH` / non-evaluable targets count as miss
- `Mean Absolute AUC Regret`
  - `top_auc_t - selected_auc_t`
  - averaged over evaluated targets within each type
- Type A / Type B official summaries
  - report the same three metrics separately for Type A and Type B
- Overall macro average
  - the official overall score is the macro-average of Type A and Type B metrics, so one type does not dominate because it has more targets

Runtime diagnostics kept in the summary JSON but not treated as official evaluation metrics:

- `coverage`
- `no_match_rate`
- `mean_rank`
- `mean_rank_fraction`
- `step1_universe_match_rate`

## CLI

Prepare benchmark-specific assets:

```bash
python experiments/contribution3/transfer/batch/run_batch.py prepare-assets --benchmark-family binary_to_binary
```

Run transfer:

```bash
python experiments/contribution3/transfer/batch/run_batch.py run --condition all-tools --benchmark-family binary_to_binary
```

Run Contribution2 handoff:

```bash
python experiments/contribution3/transfer/batch/run_batch.py recommend --condition all-tools --benchmark-family binary_to_binary
```

Run end-to-end evaluation:

```bash
python experiments/contribution3/transfer/batch/run_batch.py evaluate-end-to-end --condition all-tools --benchmark-family binary_to_binary
```
