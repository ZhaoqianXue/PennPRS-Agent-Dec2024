# Contribution2: Domain Knowledge Ablation Study

## Objective

Quantify the marginal contribution of each section in `src/server/core/knowledge/prs_model_domain_knowledge.md` to the PennPRS Agent's PRS model selection accuracy.

This is a **leave-one-out ablation**: for each of the 7 top-level `##` sections in the domain knowledge document, we generate a variant with that section removed and run the full Contribution2 with-domain experiment pipeline.

## Ablation Variants

| Variant ID | Removed Section |
|------------|----------------|
| `no-section1-trait-endpoint` | `## 1. trait_reported / trait_efo / phenotyping_reported` |
| `no-section2-performance-covariates` | `## 2. performance_metrics.auc / performance_metrics.r2 / covariates` |
| `no-section3-validation-sample-size` | `## 3. validation_sample_size` |
| `no-section4-training-cohorts-ancestry` | `## 4. training_development_cohorts / samples_training / ancestry_distribution` |
| `no-section5-method-name` | `## 5. method_name` |
| `no-section6-publication` | `## 6. publication.title / publication.journal / date_release` |
| `no-section7-variants-number` | `## 7. variants_number` |

## Experiment Design

- **Baseline**: Full domain knowledge (latest with-domain run)
- **Lower bound**: No domain knowledge (without-domain run)
- **Disease set**: 30 or 75 diseases
- **Trials**: 10 per disease per variant
- **Model**: gpt-5.2 (locked)
- **Candidate pool**: Same evaluated PGS IDs as Contribution2
- **Metrics**: Modal Hit@1..5, Trial Hit@1..5, NRS

Only the `knowledge_file` path differs between variants; everything else is held constant.

## Directory Structure

```
ablation/
├── README.md
├── docs/
│   └── ablation_comparison_report.md    # Generated comparative report
├── variants/
│   ├── manifest.json                    # Variant metadata
│   ├── no-section1-trait-endpoint.md
│   ├── ...
│   └── no-section7-variants-number.md
├── scripts/
│   ├── generate_ablation_variants.py    # Generate variant .md files
│   ├── run_ablation_experiment.py       # Run experiments
│   └── generate_ablation_report.py      # Generate comparison report
└── runs/                                # One sub-directory per variant run
    ├── ablation-no-section1-trait-endpoint__gpt-5.2-t10__30disease/
    ├── ablation-no-section4-training-cohorts-ancestry__gpt-5.2-t10__30disease/
    └── ...
```

## Workflow

### Step 1: Generate ablation variants (already done)

```bash
python experiments/contribution2/ablation/scripts/generate_ablation_variants.py
```

### Step 2: Run experiments

```bash
# Single variant (smoke test)
python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
    --variant no-section5-method-name --mode prepare-submit --trials 1 --limit 1

# Single variant (full run)
python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
    --variant no-section5-method-name --mode prepare-submit --trials 10

# All variants
python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
    --all --mode prepare-submit --trials 10

# Check status
python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
    --variant no-section5-method-name --mode status

# Collect results
python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
    --variant no-section5-method-name --mode collect

# Collect all
python experiments/contribution2/ablation/scripts/run_ablation_experiment.py \
    --all --mode collect
```

### Step 3: Generate comparison report

```bash
python experiments/contribution2/ablation/scripts/generate_ablation_report.py
```

## Scale

- 7 variants x 30 diseases x 10 trials = 2,100 batch requests (30-disease)
- 7 variants x 75 diseases x 10 trials = 5,250 batch requests (75-disease)
- Each variant is one OpenAI Batch job
- All 7 can be submitted in parallel
