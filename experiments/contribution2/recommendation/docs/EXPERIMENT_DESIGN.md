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
- `ancestry_distribution`
- `publication.title`
- `publication.journal`
- `date_release`
- `samples_training`
- `performance_metrics`
- `phenotyping_reported`
- `covariates`
- `training_development_cohorts`
- `validation_sample_size`

These fields come from the `[Agent + UI]` specification in [sop.md](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/.agent/blueprints/sop.md#L370) and the actual LLM context summarization logic in [recommendation_agent.py](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/src/server/modules/disease/recommendation_agent.py#L203).

For scores with multiple PGS Catalog validation records, the agent does not mix fields across records. It selects one representative validation record using this rule:

- highest-result `European` validation record, if any
- otherwise highest-result validation record overall

Here, `highest-result` first prefers explicit PRS-comparable metrics from that validation record:

- `PGS AUROC (no covariates)` over full-model AUROC
- `PGS R2 (no covariates)` or covariates-regressed-out R² over full-model R²
- if no PRS-comparable metric exists, then fall back to the best visible full-model metric only for representative-record selection

The selected record's top-level `performance_metrics.auc` / `performance_metrics.r2` are therefore PRS-comparable metrics when explicitly available, while `classification_metrics`, `other_metrics`, `full_model_auc`, `full_model_r2`, and `incremental_auc` remain available for sanity checking and interpretation.
The agent-facing `performance_metrics` preserves the selected record's full `classification_metrics` and `other_metrics`, while `phenotyping_reported`, `covariates`, and `validation_sample_size` are aligned to that same selected record.
The global `prs_model_performance_landscape` now uses the same comparable-metric semantics: a score contributes to landscape `auc` / `r2` only when an explicit PRS-comparable metric is available from its selected validation record; full-model AUROC/R² do not fill those comparable distributions.

---

## Experiment 1: Without Domain Knowledge

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
| Baseline | Highest reported PGS-only AUROC in PGS Catalog metadata, when available |
| LLM execution | OpenAI Batch API |

### Without Domain Knowledge protocol

1. Use the 30 diseases from the union CSV.
2. For each disease, restrict Step 1 candidates to `evaluated_pgs_per_ontology.json`.
3. Disable `prs_model_domain_knowledge`.
4. Use the fixed Step 1 prompt and provide only candidate metadata plus `prs_model_performance_landscape` in context.
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

- `Overall Recommended Model Accuracy`: for each disease, take the final recommended model across 10 runs and test whether it is in `Target_TopK`
- `Baseline accuracy`: deterministic baseline using the model with highest reported PGS-only AUROC in PGS Catalog metadata, when available

### Internal diagnostics

The runner still records engineering diagnostics in JSON for debugging, but they are not part of the formal headline metrics:

- aggregate trial-level hit count
- valid-output count/rate

### Naive baseline

Use one deterministic baseline only:

- `Highest reported PGS-only AUROC in PGS Catalog metadata`

For each disease, select the candidate model with the largest reported PRS-comparable `performance_metrics["auc"]` among the evaluated candidate pool, then test whether that baseline recommendation belongs to `Target_TopK`.

Do not fall back to full-model AUROC for this baseline. If no candidate reports a PRS-comparable AUROC, the baseline is treated as unavailable for that disease.

### Cost accounting

The Markdown report includes an experiment cost summary.

- Preferred method: exact completed-batch token usage from the OpenAI Batch object multiplied by the official OpenAI Batch-tier token prices for the model that was used.
- If the project later runs with a dedicated OpenAI project plus an org admin key, the team can additionally reconcile against the OpenAI Costs API for billing-window validation.

### Notes

- The earlier 11-disease pilot based on a small-candidate subset is a debug run only, not the formal Contribution2 result.
- Candidate-order sensitivity is intentionally deferred and should be tracked as future work, not part of the current formal experiment.

### Batch workflow

```bash
# Prepare requests and submit the batch job
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py

# Debug only: prepare a smaller batch locally
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode prepare --limit 3 --trials 2

# Check batch status
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode status

# Download completed batch output and compute final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode collect
```

### Output files

| Path | Description |
|------|-------------|
| `runs/experiment_without_domain_batch_requests.jsonl` | OpenAI Batch input JSONL |
| `runs/experiment_without_domain_batch_manifest.json` | Local manifest with disease metadata and request mapping |
| `runs/experiment_without_domain_batch_job.json` | Batch job metadata |
| `runs/experiment_without_domain_batch_output.jsonl` | Downloaded OpenAI Batch output |
| `runs/experiment_without_domain_batch_errors.jsonl` | Downloaded OpenAI Batch errors (if any) |
| `runs/experiment_without_domain_results.json` | Per-trial results |
| `runs/experiment_without_domain_summary.json` | Aggregate summary plus per-disease summaries |
| `runs/experiment_without_domain_report.md` | Human-readable report |

---

## Experiment 2: With Domain Knowledge

### Status

Implementation ready. Formal execution still requires an explicit run decision.

### Scope

Experiment 2 is a strict paired ablation against the archived Without Domain Knowledge GPT-5.2 result.

The only intentional change relative to the Without Domain Knowledge arm is:

- Enable local `prs_model_domain_knowledge`

Everything else remains fixed:

- same 30 diseases
- same evaluated candidate pool (`N Models`)
- same `Target_TopK` labels
- same 10-trial design
- same no-fallback policy
- same Step 1-only direct-match evaluation
- same success definition

### Domain knowledge implementation

For Contribution2, `prs_model_domain_knowledge` is intentionally implemented as retrieval from the curated local knowledge base:

- source: `src/server/core/knowledge/prs_model_domain_knowledge.md`
- source type: `local`
- purpose: inject stable model-selection rules about endpoint fidelity, PRS-comparable metric interpretation, heritability sanity checks, transferability, ancestry compatibility, penalties, and method priors

This experiment therefore evaluates:

- `With Domain Knowledge`

not live web-search-based guideline retrieval.

### Model

- fixed model for this arm: `gpt-5.2`

This is locked so Experiment 2 can be compared directly with the archived Without Domain Knowledge GPT-5.2 run.

### Outputs

The arm produces a disease-level report with the same format as the Without Domain Knowledge report, plus one additional comparison report.

Main outputs:

- `runs/experiment_with_domain_results.json`
- `runs/experiment_with_domain_summary.json`
- `runs/experiment_with_domain_report.md`

Comparison output:

- `runs/experiment_with_vs_without_domain_report.md`

### Comparison targets

- `Overall Recommended Model Accuracy`
- `Baseline accuracy`
- disease-level comparison against the archived Without Domain Knowledge GPT-5.2 run
- `Win / Loss / Tie-Hit / Tie-Miss`

### Batch workflow

```bash
# Prepare requests and submit the domain-knowledge batch job
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py

# Debug only: prepare a smaller local batch
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py --mode prepare --limit 3 --trials 2

# Check batch status
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py --mode status

# Download completed batch output and compute final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py --mode collect
```
