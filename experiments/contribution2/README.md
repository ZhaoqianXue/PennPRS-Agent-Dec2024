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
│   ├── scripts/           # run_experiment_native_gpt.py, test_agent_n_models_input.py
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
```

### Outputs

| Path | Description |
|------|-------------|
| `disease_selection/runs/selected_diseases_contribution2.csv` | Rootcode selection |
| `disease_selection/runs/selected_diseases_contribution2_childrencode.csv` | Childrencode selection |
| `disease_selection/runs/selected_diseases_contribution2_union.csv` | Union (manual merge) |
| `disease_selection/runs/disease_selection_report*.md` | Reports |
| `disease_selection/metrics/disease_selection_full_metrics*.csv` | Full metrics |

---

## Recommendation (推荐模型)

Evaluate whether the Agent can select a model from `Target_TopK` using direct-match Step 1 tools only.

### 1. Generate Ground Truth

```bash
python experiments/contribution2/recommendation/configs/generate_evaluated_pgs_list.py
```

Outputs: `recommendation/runs/evaluated_pgs_per_ontology.json`, `top_k_pgs_per_ontology.json`

### 2. Run Experiment (Native GPT Batch)

Configure `.env` with `OPENAI_API_KEY` (see `.env.example`). The script loads `.env` automatically and enforces the formal native-GPT protocol:

- 30 diseases from the union CSV
- 10 trials per disease by default
- `prs_model_domain_knowledge` disabled
- Step 2 disabled
- evaluated PGS whitelist enabled
- strict no-fallback mode enabled
- naive baseline: highest reported AUC in PGS Catalog metadata
- OpenAI Batch API execution for LLM Step 1 decisions

Formal headline metrics:

- `Overall Recommended Model Accuracy`
- `Baseline accuracy`

Per-trial chosen PGS IDs are still recorded in the JSON outputs for every disease and every run.
The Markdown report also includes an experiment-cost summary computed from exact completed-batch token usage and OpenAI Batch-tier prices.

```bash
# Prepare requests and submit one OpenAI Batch job
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py

# Quick debug: prepare a smaller batch only
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode prepare --limit 3 --trials 2

# Check batch status later
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode status

# Download completed batch outputs and build final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode collect
```

### 3. Run Experiment (GPT + `prs_model_domain_knowledge`)

This arm keeps the exact same Contribution2 protocol, but enables the local curated knowledge base used by `prs_model_domain_knowledge`.

- fixed model: `gpt-5.2`
- same 30 diseases
- same `N Models` candidate pool
- same 10 trials per disease
- same strict no-fallback policy
- same disease-level report format as the native arm
- plus one extra Markdown report comparing `with domain knowledge` vs archived `native GPT-5.2`

```bash
# Prepare requests and submit one OpenAI Batch job
python experiments/contribution2/recommendation/scripts/run_experiment_domain_knowledge_gpt.py

# Quick debug: prepare a smaller batch only
python experiments/contribution2/recommendation/scripts/run_experiment_domain_knowledge_gpt.py --mode prepare --limit 3 --trials 2

# Check batch status later
python experiments/contribution2/recommendation/scripts/run_experiment_domain_knowledge_gpt.py --mode status

# Download completed batch outputs and build final metrics/report
python experiments/contribution2/recommendation/scripts/run_experiment_domain_knowledge_gpt.py --mode collect
```

### 4. Test N Models Input

```bash
python experiments/contribution2/recommendation/scripts/test_agent_n_models_input.py --limit 5
```

### 5. Native GPT Outputs

| Path | Description |
|------|-------------|
| `recommendation/runs/experiment_native_gpt_batch_requests.jsonl` | OpenAI Batch input JSONL |
| `recommendation/runs/experiment_native_gpt_batch_manifest.json` | Local manifest with disease metadata and trial mapping |
| `recommendation/runs/experiment_native_gpt_batch_job.json` | Latest batch job metadata |
| `recommendation/runs/experiment_native_gpt_batch_output.jsonl` | Downloaded OpenAI Batch output |
| `recommendation/runs/experiment_native_gpt_results.json` | Per-trial results across all diseases |
| `recommendation/runs/experiment_native_gpt_summary.json` | Aggregate summary plus per-disease summaries |
| `recommendation/runs/experiment_native_gpt_report.md` | Human-readable report |

### 6. Domain-Knowledge GPT Outputs

| Path | Description |
|------|-------------|
| `recommendation/runs/experiment_domain_knowledge_gpt_batch_requests.jsonl` | OpenAI Batch input JSONL |
| `recommendation/runs/experiment_domain_knowledge_gpt_batch_manifest.json` | Local manifest with disease metadata and trial mapping |
| `recommendation/runs/experiment_domain_knowledge_gpt_batch_job.json` | Latest batch job metadata |
| `recommendation/runs/experiment_domain_knowledge_gpt_batch_output.jsonl` | Downloaded OpenAI Batch output |
| `recommendation/runs/experiment_domain_knowledge_gpt_results.json` | Per-trial results across all diseases |
| `recommendation/runs/experiment_domain_knowledge_gpt_summary.json` | Aggregate summary plus per-disease summaries |
| `recommendation/runs/experiment_domain_knowledge_gpt_report.md` | Human-readable report with the same format as the native arm |
| `recommendation/runs/experiment_domain_knowledge_vs_native_gpt_report.md` | Comparison report versus archived native GPT-5.2 |

### Design

See [recommendation/docs/EXPERIMENT_DESIGN.md](recommendation/docs/EXPERIMENT_DESIGN.md).
