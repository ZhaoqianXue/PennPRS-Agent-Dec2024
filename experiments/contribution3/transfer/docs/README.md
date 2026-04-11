# Contribution3 Transfer Docs

This directory contains Markdown reports rendered from the latest batch outputs under `../runs/tool_calling_agent`.

## Files

- `latest_end_to_end_report.md`: macro metrics, family metrics, match coverage, and the biggest AUC gains/losses between `gpt-only` and `all-tools`.
- `latest_per_target_comparison.md`: side-by-side target-level comparison across both benchmark families.

## Regenerate

Run this after finishing `run`, `recommend`, and `evaluate-end-to-end` for both conditions and both benchmark families:

```bash
python experiments/contribution3/transfer/batch/run_batch.py generate-docs
```

## Source Artifacts

Transfer `run` outputs are append-only by default:

- `../runs/tool_calling_agent/<benchmark_family>/<condition>__<YYYYMMDD_HHMMSS>/results.json`

The benchmark-family assets stay in their stable locations, including:

- `../runs/tool_calling_agent/<benchmark_family>/candidate_dossiers.json`
- `../runs/tool_calling_agent/trait_bundle_index.json`

The generated reports are built from:

- `../runs/tool_calling_agent/*/*/results.json`
- `../runs/tool_calling_agent/*/*/contribution2_recommendations.json`
- `../runs/tool_calling_agent/*/evaluation/*__end_to_end_eval_summary.json`
- `../runs/tool_calling_agent/*/evaluation/*__end_to_end_eval_detail.csv`
