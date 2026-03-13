# Contribution2: LLM-Based PRS Model Selection

This module advances Contribution2 of the PennPRS Agent paper: understanding how GPT uses captured PRS model features (sample size, ancestry, method, training cohort, etc.) to select optimal models.

## Structure

```
contribution2/
├── disease_selection/     # 筛选疾病 (disease selection from All of Us benchmark)
│   ├── configs/           # select_diseases_contribution2.py
│   ├── runs/              # Selected CSVs, reports
│   └── metrics/           # Full metrics
│
├── recommendation/       # 推荐模型 (Agent model recommendation evaluation)
│   ├── configs/           # generate_evaluated_pgs_list.py
│   ├── scripts/           # run_experiment_without_domain.py, test_agent_n_models_input.py
│   ├── docs/              # EXPERIMENT_DESIGN.md
│   └── runs/              # evaluated_pgs, top_k_pgs, experiment results
│
└── README.md
```

---

## Disease Selection (筛选疾病)

Select diseases from the All of Us benchmark (Contribution1) based on QC1–QC3 criteria.

### Run

```bash
# Rootcode (default)
python experiments/contribution2/disease_selection/configs/select_diseases_contribution2.py

# Childrencode
python experiments/contribution2/disease_selection/configs/select_diseases_contribution2.py --childrencode

# Legacy threshold used by the current 30-disease benchmark
python experiments/contribution2/disease_selection/configs/select_diseases_contribution2.py --min-n-models 3

# Build a canonicalized current-method union (does not touch the frozen 30-disease benchmark)
python experiments/contribution2/disease_selection/configs/build_current_method_union.py
```

### Outputs

| Path | Description |
|------|-------------|
| `disease_selection/runs/selected_diseases_contribution2.csv` | Rootcode selection |
| `disease_selection/runs/selected_diseases_contribution2_childrencode.csv` | Childrencode selection |
| `disease_selection/runs/selected_diseases_contribution2_union.csv` | Frozen union benchmark (manual merge; not auto-synced to latest selection code) |
| `disease_selection/runs/selected_diseases_contribution2_current_union.csv` | Canonicalized current-method union; directly usable by recommendation ground-truth generation without manual `Target_TopK` annotation |
| `disease_selection/runs/selected_diseases_contribution2_current_union_details.csv` | Audit/detail view for canonical merge decisions and source coverage |
| `disease_selection/runs/disease_selection_report*.md` | Reports |
| `disease_selection/metrics/disease_selection_full_metrics*.csv` | Full metrics |

---

## Recommendation (推荐模型)

Evaluate whether the Agent can select a highly ranked model under the Contribution1 All of Us benchmark using direct-match Step 1 tools only.

### 1. Generate Ground Truth

```bash
# Frozen 30-disease union
python experiments/contribution2/recommendation/configs/generate_evaluated_pgs_list.py

# Current 60-disease canonical union
python experiments/contribution2/recommendation/configs/generate_evaluated_pgs_list.py \
  --union-csv experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union.csv
```

Outputs:
- `evaluated_pgs_per_ontology.json`
- `top_k_pgs_per_ontology.json` (full benchmark ranking, not manual Target_TopK labels)
- `benchmark_auc_per_ontology.json`

### 2. Run Experiment (Without Domain Knowledge Batch)

Configure `.env` with `OPENAI_API_KEY` (see `.env.example`). The script loads `.env` automatically and enforces the formal without-domain protocol:

- diseases from the selected union CSV (default: frozen 30-disease union)
- 10 trials per disease by default
- `prs_model_domain_knowledge` disabled
- Step 2 disabled
- evaluated PGS whitelist enabled
- strict no-fallback mode enabled
- naive baseline: highest reported PGS-only AUROC in PGS Catalog metadata, when available
- OpenAI Batch API execution for LLM Step 1 decisions

Formal headline metrics:

- `Modal Hit@1..5`
- `Trial Hit@1..5`
- `Baseline Hit@1..5`
- `Normalized Ranking Score (NRS)`

For `Hit@k`, diseases with fewer than `k` evaluated models are excluded from the denominator.
If the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`.

Per-trial chosen PGS IDs are still recorded in the JSON outputs for every disease and every run.
The Markdown report also includes an experiment-cost summary computed from exact completed-batch token usage and OpenAI Batch-tier prices.

```bash
# Prepare requests and submit one OpenAI Batch job (frozen 30-disease union)
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py

# Current 60-disease canonical union
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py \
  --union-csv experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union.csv

# Quick debug: prepare a smaller batch only
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode prepare --limit 3 --trials 2

# Check batch status later
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode status

# Download completed batch outputs and build final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode collect
```

### 3. Run Experiment (With Domain Knowledge)

This arm keeps the exact same Contribution2 protocol, but enables the local curated knowledge base used by `prs_model_domain_knowledge`.

- fixed model: `gpt-5.2`
- same diseases as the selected union CSV in the paired without-domain run
- same `N Models` candidate pool
- same 10 trials per disease
- same strict no-fallback policy
- same disease-level report format as the Without Domain Knowledge arm
- plus one extra Markdown report comparing `With Domain Knowledge` vs the archived `without-domain-gpt-5.2-t10` run

```bash
# Prepare requests and submit one OpenAI Batch job
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py

# Current 60-disease canonical union (comparison defaults to the matching without-domain run)
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py \
  --union-csv experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union.csv

# Quick debug: prepare a smaller batch only
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py --mode prepare --limit 3 --trials 2

# Check batch status later
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py --mode status

# Download completed batch outputs and build final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py --mode collect
```

For non-default disease lists such as the current 60-disease canonical union, the per-disease docs are written to dataset-specific filenames, for example:

- `recommendation/docs/without_domain_per_disease_comparison__current-union.md`
- `recommendation/docs/with_vs_without_domain_per_disease_comparison__current-union.md`

This preserves the existing 30-disease docs.

### 4. Test N Models Input

```bash
python experiments/contribution2/recommendation/scripts/test_agent_n_models_input.py --limit 5
```

### 5. Without Domain Knowledge Outputs

| Path | Description |
|------|-------------|
| `recommendation/runs/experiment_without_domain_batch_requests.jsonl` | OpenAI Batch input JSONL |
| `recommendation/runs/experiment_without_domain_batch_manifest.json` | Local manifest with disease metadata and trial mapping |
| `recommendation/runs/experiment_without_domain_batch_job.json` | Latest batch job metadata |
| `recommendation/runs/experiment_without_domain_batch_output.jsonl` | Downloaded OpenAI Batch output |
| `recommendation/runs/experiment_without_domain_results.json` | Per-trial results across all diseases |
| `recommendation/runs/experiment_without_domain_summary.json` | Aggregate summary plus per-disease summaries |
| `recommendation/runs/experiment_without_domain_report.md` | Human-readable report |

### 6. With Domain Knowledge Outputs

| Path | Description |
|------|-------------|
| `recommendation/runs/experiment_with_domain_batch_requests.jsonl` | OpenAI Batch input JSONL |
| `recommendation/runs/experiment_with_domain_batch_manifest.json` | Local manifest with disease metadata and trial mapping |
| `recommendation/runs/experiment_with_domain_batch_job.json` | Latest batch job metadata |
| `recommendation/runs/experiment_with_domain_batch_output.jsonl` | Downloaded OpenAI Batch output |
| `recommendation/runs/experiment_with_domain_results.json` | Per-trial results across all diseases |
| `recommendation/runs/experiment_with_domain_summary.json` | Aggregate summary plus per-disease summaries |
| `recommendation/runs/experiment_with_domain_report.md` | Human-readable report with the same format as the Without Domain Knowledge arm |
| `recommendation/runs/experiment_with_vs_without_domain_report.md` | Comparison report versus the matching without-domain run for the same disease list |

### Design

See [recommendation/docs/EXPERIMENT_DESIGN.md](recommendation/docs/EXPERIMENT_DESIGN.md).
