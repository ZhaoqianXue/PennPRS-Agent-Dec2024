# Contribution2 Experiment Design

## Objective

Evaluate whether the PennPRS Agent can select a single PRS model that belongs to the disease-specific `Target_TopK` benchmark set when only direct-match Step 1 tools are available.

**Success definition**:
- For each disease, the Agent outputs exactly one `PGS ID`.
- A run is successful iff `recommended_pgs_id` belongs to the first `K` models in `top_k_pgs_per_ontology.json`, where `K = Target_TopK` from the union CSV.

---

## Ground Truth

### Disease Set

- Source: `experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_union.csv`
- Size: 30 ontology-level diseases

### Benchmark Labels

- `Target_TopK`: stored in the union CSV
- Ranked benchmark PGS IDs: `experiments/contribution2/recommendation/runs/top_k_pgs_per_ontology.json`
- Evaluated candidate pool: `experiments/contribution2/recommendation/runs/evaluated_pgs_per_ontology.json`

The experiment must restrict the Agent candidate pool to the evaluated PGS IDs only, so that Step 1 is compared against the exact same model universe used by Contribution1.

---

## LLM-Visible PGS Fields

The experiment-level feature attribution must only use fields that are actually serialized into the LLM context.

### Candidate model fields available to the Agent

- `id`
- `trait_reported`
- `trait_efo`
- `method_name`
- `variants_number`
- `variants_genomebuild`
- `ancestry_distribution`
- `publication`
- `date_release`
- `samples_variants`
- `samples_training`
- `performance_metrics`
- `phenotyping_reported`
- `covariates`
- `sampleset`
- `training_development_cohorts`
- `validation_sample_size`

These fields come from the `[Agent + UI]` specification in [sop.md](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/.agent/blueprints/sop.md#L370) and the actual LLM context summarization logic in [recommendation_agent.py](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/src/server/modules/disease/recommendation_agent.py#L203).

---

## Experiment 1: Native GPT

### Scope

This is the primary Contribution2 experiment and should be executed now.

### Setup

| Setting | Value |
|---------|-------|
| Tools | `prs_model_pgscatalog_search` + `prs_model_performance_landscape` |
| Domain knowledge | Disabled |
| Cross-disease Step 2 | Disabled |
| Candidate pool | Evaluated PGS IDs only (`N Models`) |
| Fallback | Disabled |
| Trials | 10 runs per disease |
| Baseline | Highest reported AUC in PGS Catalog metadata |
| LLM execution | OpenAI Batch API |

### Native GPT protocol

1. Use the 30 diseases from the union CSV.
2. For each disease, restrict Step 1 candidates to `evaluated_pgs_per_ontology.json`.
3. Disable `prs_model_domain_knowledge`.
4. Use the native Step 1 prompt that explicitly instructs the LLM to reason only from candidate metadata plus `prs_model_performance_landscape`.
5. Disable fallback behavior:
   - no fallback Step 1 decision
   - no fallback final report
   - no auto-filled `primary_recommendation`
6. Precompute the local Step 1 context for each disease once:
   - filtered candidate models
   - candidate metadata visible to the LLM
   - global `prs_model_performance_landscape`
7. Create 10 batch requests per disease and submit them through the OpenAI Batch API.
8. For each completed batch response, extract the single recommended `PGS ID` from the Step 1 structured output.
9. Mark the run as a hit iff the recommended `PGS ID` belongs to `Target_TopK`.

### Stored outputs per run

- `ontology`
- `trial`
- `target_topk`
- `target_topk_ids`
- `candidate_model_ids`
- `recommended_pgs_id`
- `recommendation_type`
- `recommendation_confidence`
- `valid_output`
- `in_target_topk`
- `rationale`
- `rationale_features`
- `error`

### Stored outputs per disease

- `trial_hits`
- `trial_hit_rate`
- `modal_recommendation`
- `modal_recommendation_count`
- `modal_recommendation_in_target_topk`
- `candidate_models_visible_to_llm`
- `feature_mentions`
- `baseline`
- `baseline_in_target_topk`

### Primary metrics

- `Mean disease hit rate`: average of the 30 disease-specific hit rates
- `Majority-vote accuracy`: for each disease, take the modal recommendation across 10 runs and test whether it is in `Target_TopK`
- `Baseline accuracy`: deterministic baseline using the model with highest reported AUC in PGS Catalog metadata

### Internal diagnostics

The runner still records engineering diagnostics in JSON for debugging, but they are not part of the formal headline metrics:

- aggregate trial-level hit count
- valid-output count/rate
- optional bootstrap interval for `Mean disease hit rate`

### Naive baseline

Use one deterministic baseline only:

- `Highest reported AUC in PGS Catalog metadata`

For each disease, select the candidate model with the largest reported `performance_metrics["auc"]` among the evaluated candidate pool, then test whether that baseline recommendation belongs to `Target_TopK`.

### Notes

- The earlier 11-disease pilot based on a small-candidate subset is a debug run only, not the formal Contribution2 result.
- Candidate-order sensitivity is intentionally deferred and should be tracked as future work, not part of the current formal experiment.

### Batch workflow

```bash
# Prepare requests and submit the batch job
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py

# Debug only: prepare a smaller batch locally
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode prepare --limit 3 --trials 2

# Check batch status
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode status

# Download completed batch output and compute final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode collect
```

### Output files

| Path | Description |
|------|-------------|
| `runs/experiment_native_gpt_batch_requests.jsonl` | OpenAI Batch input JSONL |
| `runs/experiment_native_gpt_batch_manifest.json` | Local manifest with disease metadata and request mapping |
| `runs/experiment_native_gpt_batch_job.json` | Batch job metadata |
| `runs/experiment_native_gpt_batch_output.jsonl` | Downloaded OpenAI Batch output |
| `runs/experiment_native_gpt_batch_errors.jsonl` | Downloaded OpenAI Batch errors (if any) |
| `runs/experiment_native_gpt_results.json` | Per-trial results |
| `runs/experiment_native_gpt_summary.json` | Aggregate summary plus per-disease summaries |
| `runs/experiment_native_gpt_report.md` | Human-readable report |

---

## Experiment 2: GPT + Domain Knowledge

### Status

On hold. Do not execute yet.

### Protocol lock

When this experiment starts later, everything must remain identical to Experiment 1 except one factor:

- Enable `prs_model_domain_knowledge`

All other settings must stay fixed:

- same 30 diseases
- same evaluated candidate pool
- same `Target_TopK` labels
- same 10-trial design
- same no-fallback policy
- same evaluation and output schema

### Comparison targets

- mean disease hit rate
- majority-vote accuracy
- valid output rate
- per-disease delta
- rationale feature shifts
