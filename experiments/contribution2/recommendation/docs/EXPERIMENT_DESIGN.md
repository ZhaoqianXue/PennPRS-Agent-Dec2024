# Contribution2 Experiment Design

## Objective

Evaluate whether the PennPRS Agent can select a single PRS model that ranks near the top of the disease-specific Contribution1 All of Us benchmark when only direct-match Step 1 tools are available.

**Primary evaluation definition**:
- For each disease, the Agent outputs exactly one `PGS ID`.
- The benchmark keeps the full disease-specific AoU ranking from `top_k_pgs_per_ontology.json`.
- Report `Hit@k` for `k = 1, 2, 3, 4, 5`.
- For `Hit@k`, a disease contributes to the denominator only when it has at least `k` evaluated models.
- If the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`.
- Keep `Normalized Ranking Score (NRS)` alongside the hit metrics.

---

## Ground Truth

### Disease Set

- Source: `experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_union__30disease.csv`
- Size: 30 ontology-level diseases

### Benchmark Labels

- Ranked benchmark PGS IDs: `experiments/contribution2/recommendation/runs/.../top_k_pgs_per_ontology.json`
- Benchmark AoU AUC map: `experiments/contribution2/recommendation/runs/.../benchmark_auc_per_ontology.json`
- Evaluated candidate pool: `experiments/contribution2/recommendation/runs/.../evaluated_pgs_per_ontology.json`

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

---

## Experiment 0: Prompt-Only Baseline

### Scope

This is the lowest-information ablation arm. It isolates the contribution of the LLM's parametric knowledge when no structured metadata is available.

### Setup

| Setting | Value |
|---------|-------|
| Tools | None |
| Candidate visibility | PGS IDs only (no trait, method, performance, or other metadata) |
| Domain knowledge | Disabled |
| Cross-disease Step 2 | Disabled |
| Candidate pool | Evaluated PGS IDs only (`N Models`) — same set as other arms |
| Fallback | Disabled |
| Trials | 10 runs per disease |
| LLM execution | OpenAI Batch API |

### Prompt-Only protocol

1. Use the same diseases and evaluated candidate pool as the other arms.
2. For each disease, provide the candidate PGS IDs (e.g. `[{"id": "PGS000753"}, ...]`) but strip all metadata fields.
3. Disable `prs_model_pgscatalog_search` metadata and `prs_model_domain_knowledge`.
4. Use the same Step 1 system prompt as the other arms.
5. The LLM must rely entirely on parametric knowledge (training data) to select among the candidate IDs.

### Ablation rationale

The three-arm comparison isolates incremental value at each level:

| Arm | Information available | Tests |
|-----|---------------------|-------|
| Prompt-Only Baseline | Candidate PGS IDs only | LLM parametric knowledge |
| Catalog Search Only | IDs + full structured metadata | Value of `prs_model_pgscatalog_search` |
| Catalog Search + Domain Knowledge | IDs + metadata + expert rules | Value of `prs_model_domain_knowledge` |

The candidate set is identical across all three arms; only the information depth changes.

### Batch workflow

```bash
# Prepare requests and submit the batch job
python experiments/contribution2/recommendation/scripts/run_experiment_prompt_only.py

# Check batch status
python experiments/contribution2/recommendation/scripts/run_experiment_prompt_only.py --mode status

# Download completed batch output and compute final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_prompt_only.py --mode collect
```

---

## Experiment 1: Without Domain Knowledge

### Scope

This is the primary Contribution2 experiment and should be executed now.

### Setup

| Setting | Value |
|---------|-------|
| Tools | `prs_model_pgscatalog_search` |
| Domain knowledge | Disabled |
| Cross-disease Step 2 | Disabled |
| Candidate pool | Evaluated PGS IDs only (`N Models`) |
| Fallback | Disabled |
| Trials | 10 runs per disease |
| LLM execution | OpenAI Batch API |

### Without Domain Knowledge protocol

1. Use the 30 diseases from the union CSV.
2. For each disease, restrict Step 1 candidates to `evaluated_pgs_per_ontology.json`.
3. Disable `prs_model_domain_knowledge`.
4. Use the fixed Step 1 prompt and provide only candidate metadata in context.
5. Disable fallback behavior:
   - no fallback Step 1 decision
   - no fallback final report
   - no auto-filled `primary_recommendation`
6. Precompute the local Step 1 context for each disease once:
   - filtered candidate models
   - candidate metadata visible to the LLM
7. Create 10 batch requests per disease and submit them through the OpenAI Batch API.
8. For each completed batch response, extract the single recommended `PGS ID` from the Step 1 structured output.
9. Compute benchmark rank, `Hit@1..5`, and `NRS` from the AoU ranking.

### Stored outputs per run

- `ontology`
- `trial`
- `benchmark_ranked_ids`
- `benchmark_auc_by_id`
- `benchmark_topk_ids`
- `eligible_at_k` (legacy field; now `Hit@1..5` are defined for the full disease/trial set whenever benchmark candidates exist)
- `candidate_model_ids`
- `recommended_pgs_id`
- `recommendation_type`
- `recommendation_confidence`
- `valid_output`
- `hit_at_k`
- `rationale`
- `rationale_features`
- `error`

### Stored outputs per disease

- `trial_hit_counts_at_k`
- `trial_hit_rates_at_k`
- `modal_recommendation`
- `modal_recommendation_count`
- `modal_recommendation_hit_at_k`
- `candidate_models_visible_to_llm`
- `feature_mentions`

### Primary metrics

- `Modal Hit@1..5`: for each disease, take the final recommended model across 10 runs and evaluate against the AoU benchmark top-`k` set using the full disease denominator
- `Trial Hit@1..5`: the same evaluation at the individual-trial level using the full trial denominator
- If a disease has fewer than `k` evaluated models, `Top@k` is defined as all available benchmark-ranked models for that disease
- `Normalized Ranking Score (NRS)`

### Internal diagnostics

The runner still records engineering diagnostics in JSON for debugging, but they are not part of the formal headline metrics:

- aggregate trial-level hit count
- valid-output count/rate

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
- same AoU benchmark ranking and tie-aware `Top@k` definition
- same 10-trial design
- same no-fallback policy
- same Step 1-only direct-match evaluation
- same `Hit@1..5` and `NRS` definition

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
