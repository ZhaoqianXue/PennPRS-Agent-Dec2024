# Cross Optimized

Additive, leak-controlled optimized cross-trait transfer prototype.

This directory does not modify the existing Contribution 2 within-trait
pipeline or the existing Contribution 3 transfer pipeline.

## Build Assets

```bash
python -m experiments.contribution3.cross_optimized.assets.build_compact_catalog \
  --out experiments/contribution3/cross_optimized/runs/assets/compact_catalog.json
```

## Build Stage A Batch Requests

```bash
python -m experiments.contribution3.cross_optimized.batch.build_requests stage-a \
  --catalog experiments/contribution3/cross_optimized/runs/assets/compact_catalog.json \
  --out experiments/contribution3/cross_optimized/runs/stage_a_requests.jsonl
```

The request builder runs `leak_guard` on each request body before writing it.
You can also scan a generated JSONL explicitly:

```bash
python -m experiments.contribution3.cross_optimized.leak_guard \
  experiments/contribution3/cross_optimized/runs/stage_a_requests.jsonl
```

Submit and collect:

```bash
python -m experiments.contribution3.cross_optimized.batch.submit \
  --jsonl experiments/contribution3/cross_optimized/runs/stage_a_requests.jsonl \
  --job-out experiments/contribution3/cross_optimized/runs/stage_a_batch_job.json

python -m experiments.contribution3.cross_optimized.batch.collect \
  --job experiments/contribution3/cross_optimized/runs/stage_a_batch_job.json \
  --output experiments/contribution3/cross_optimized/runs/stage_a_output.jsonl \
  --errors experiments/contribution3/cross_optimized/runs/stage_a_errors.jsonl \
  --status-out experiments/contribution3/cross_optimized/runs/stage_a_batch_status.json
```

## Build Stage B Batch Requests

Create a Stage A selection JSON in either form:

```json
{
  "B18": ["efo_0000001", "mondo_0000002"]
}
```

or:

```json
[
  {"target_id": "B18", "selected_bundle_ids": ["efo_0000001"]}
]
```

Then build Stage B:

```bash
python -m experiments.contribution3.cross_optimized.batch.build_requests stage-b \
  --catalog experiments/contribution3/cross_optimized/runs/assets/compact_catalog.json \
  --stage-a-selection experiments/contribution3/cross_optimized/runs/stage_a_selection.json \
  --out experiments/contribution3/cross_optimized/runs/stage_b_requests.jsonl
```

## Freeze Predictions

```bash
python -m experiments.contribution3.cross_optimized.batch.freeze_predictions \
  --predictions experiments/contribution3/cross_optimized/runs/predictions.json \
  --manifest experiments/contribution3/cross_optimized/runs/predictions.freeze_manifest.json
```

The freeze step scans the prediction payload for forbidden evaluation fields
and records a SHA-256 hash.

## Evaluate Frozen Predictions

This is the only boundary that reads target-row AUC values.

```bash
python -m experiments.contribution3.cross_optimized.eval.evaluate_frozen \
  --predictions experiments/contribution3/cross_optimized/runs/predictions.json \
  --manifest experiments/contribution3/cross_optimized/runs/predictions.freeze_manifest.json \
  --detail-out experiments/contribution3/cross_optimized/runs/eval_detail.csv \
  --summary-out experiments/contribution3/cross_optimized/runs/eval_summary.json
```

## Cost Ledger

Provide an explicit price manifest because model pricing changes over time:

```json
{
  "gpt-5.4-nano": {
    "input_per_1m": 0.0,
    "cached_input_per_1m": 0.0,
    "output_per_1m": 0.0,
    "batch_discount": 0.5
  }
}
```

Then parse Batch API output:

```bash
python -m experiments.contribution3.cross_optimized.batch.cost_ledger \
  --batch-output experiments/contribution3/cross_optimized/runs/stage_a_output.jsonl \
  --price-manifest experiments/contribution3/cross_optimized/runs/price_manifest.json \
  --out experiments/contribution3/cross_optimized/runs/stage_a_cost_ledger.jsonl
```
