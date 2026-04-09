# Contribution3 Transfer: Latest End-to-End Evaluation Report

## Scope

This report is generated from the latest completed transfer batch outputs under `experiments/contribution3/transfer/runs/tool_calling_agent`.

- Generated at: `2026-04-07 17:01 EDT`
- Conditions compared: `gpt-only` vs `all-tools`
- Benchmark families: `binary_to_binary`, `binary_to_continuous`
- This report only uses the native `official_metrics.hit_at_percent` outputs from `evaluate_end_to_end.py`.
- Other c3 metrics are intentionally omitted here.
- Companion per-target report: [latest_per_target_comparison.md](latest_per_target_comparison.md)

## Transfer Study Design

This comparison keeps the benchmark target set fixed and changes only the transfer / recommendation condition.

| Arm | Transfer step | Recommendation step | What it tests |
| --- | --- | --- | --- |
| `gpt-only` | LLM-only cross-trait transfer without tool evidence | Contribution2 recommendation without domain knowledge | Parametric transfer baseline |
| `all-tools` | Tool-assisted cross-trait transfer with evidence tools | Contribution2 recommendation with domain knowledge | Value of tool-assisted transfer plus domain-informed model selection |

## High-Level Outcome

- `all-tools` is better at: `Top 5%`, `Top 15%`, `Top 20%`, `Top 25%`.
- `gpt-only` is better at: `Top 10%`.
- Tied at: `none`.

## Percentile Hit Definition

- Inputs: `M` = number of benchmark-eligible PGS models for the target in the full AoU matrix; `r` = tie-averaged benchmark rank of the selected PGS among those `M` models.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each threshold, define `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if the AoU benchmark rank satisfies `r <= c_q`.
- The values below come directly from `official_metrics.hit_at_percent` in the c3 summary JSON.
- Larger is better.

## Top 5% Hit

- `gpt-only`: `overall average = 38.75%`; `binary_to_binary=48.34%`; `binary_to_continuous=29.16%`
- `all-tools`: `overall average = 41.87%`; `binary_to_binary=54.58%`; `binary_to_continuous=29.16%`
- `delta (all-tools - gpt-only)`: `overall average = +3.12pp`; `binary_to_binary=+6.24pp`; `binary_to_continuous=0.00pp`

## Top 10% Hit

- `gpt-only`: `overall average = 56.43%`; `binary_to_binary=67.91%`; `binary_to_continuous=44.94%`
- `all-tools`: `overall average = 54.11%`; `binary_to_binary=70.42%`; `binary_to_continuous=37.80%`
- `delta (all-tools - gpt-only)`: `overall average = -2.32pp`; `binary_to_binary=+2.51pp`; `binary_to_continuous=-7.14pp`

## Top 15% Hit

- `gpt-only`: `overall average = 60.74%`; `binary_to_binary=67.91%`; `binary_to_continuous=53.57%`
- `all-tools`: `overall average = 62.74%`; `binary_to_binary=70.42%`; `binary_to_continuous=55.06%`
- `delta (all-tools - gpt-only)`: `overall average = +2.00pp`; `binary_to_binary=+2.51pp`; `binary_to_continuous=+1.49pp`

## Top 20% Hit

- `gpt-only`: `overall average = 62.41%`; `binary_to_binary=71.25%`; `binary_to_continuous=53.57%`
- `all-tools`: `overall average = 68.92%`; `binary_to_binary=80.41%`; `binary_to_continuous=57.44%`
- `delta (all-tools - gpt-only)`: `overall average = +6.52pp`; `binary_to_binary=+9.16pp`; `binary_to_continuous=+3.87pp`

## Top 25% Hit

- `gpt-only`: `overall average = 64.08%`; `binary_to_binary=74.59%`; `binary_to_continuous=53.57%`
- `all-tools`: `overall average = 70.60%`; `binary_to_binary=83.75%`; `binary_to_continuous=57.44%`
- `delta (all-tools - gpt-only)`: `overall average = +6.52pp`; `binary_to_binary=+9.16pp`; `binary_to_continuous=+3.87pp`

## Hit Summary Table

| Threshold | gpt-only Overall Average | all-tools Overall Average | Delta (all-tools - gpt-only) |
| --- | ---: | ---: | ---: |
| `Top 5%` | 38.75% | 41.87% | +3.12pp |
| `Top 10%` | 56.43% | 54.11% | -2.32pp |
| `Top 15%` | 60.74% | 62.74% | +2.00pp |
| `Top 20%` | 62.41% | 68.92% | +6.52pp |
| `Top 25%` | 64.08% | 70.60% | +6.52pp |

## Family Breakdown

| Threshold | binary_to_binary gpt-only | binary_to_binary all-tools | binary_to_continuous gpt-only | binary_to_continuous all-tools |
| --- | ---: | ---: | ---: | ---: |
| `Top 5%` | 48.34% | 54.58% | 29.16% | 29.16% |
| `Top 10%` | 67.91% | 70.42% | 44.94% | 37.80% |
| `Top 15%` | 67.91% | 70.42% | 53.57% | 55.06% |
| `Top 20%` | 71.25% | 80.41% | 53.57% | 57.44% |
| `Top 25%` | 74.59% | 83.75% | 53.57% | 57.44% |

## Source Files

### `binary_to_binary`

- `gpt-only`: [runs/tool_calling_agent/binary_to_binary/evaluation/gpt-only__end_to_end_eval_summary.json](../runs/tool_calling_agent/binary_to_binary/evaluation/gpt-only__end_to_end_eval_summary.json), [runs/tool_calling_agent/binary_to_binary/evaluation/gpt-only__end_to_end_eval_detail.csv](../runs/tool_calling_agent/binary_to_binary/evaluation/gpt-only__end_to_end_eval_detail.csv), [runs/tool_calling_agent/binary_to_binary/gpt-only/results.json](../runs/tool_calling_agent/binary_to_binary/gpt-only/results.json), [runs/tool_calling_agent/binary_to_binary/gpt-only/contribution2_recommendations.json](../runs/tool_calling_agent/binary_to_binary/gpt-only/contribution2_recommendations.json)
- `all-tools`: [runs/tool_calling_agent/binary_to_binary/evaluation/all-tools__end_to_end_eval_summary.json](../runs/tool_calling_agent/binary_to_binary/evaluation/all-tools__end_to_end_eval_summary.json), [runs/tool_calling_agent/binary_to_binary/evaluation/all-tools__end_to_end_eval_detail.csv](../runs/tool_calling_agent/binary_to_binary/evaluation/all-tools__end_to_end_eval_detail.csv), [runs/tool_calling_agent/binary_to_binary/all-tools/results.json](../runs/tool_calling_agent/binary_to_binary/all-tools/results.json), [runs/tool_calling_agent/binary_to_binary/all-tools/contribution2_recommendations.json](../runs/tool_calling_agent/binary_to_binary/all-tools/contribution2_recommendations.json)

### `binary_to_continuous`

- `gpt-only`: [runs/tool_calling_agent/binary_to_continuous/evaluation/gpt-only__end_to_end_eval_summary.json](../runs/tool_calling_agent/binary_to_continuous/evaluation/gpt-only__end_to_end_eval_summary.json), [runs/tool_calling_agent/binary_to_continuous/evaluation/gpt-only__end_to_end_eval_detail.csv](../runs/tool_calling_agent/binary_to_continuous/evaluation/gpt-only__end_to_end_eval_detail.csv), [runs/tool_calling_agent/binary_to_continuous/gpt-only/results.json](../runs/tool_calling_agent/binary_to_continuous/gpt-only/results.json), [runs/tool_calling_agent/binary_to_continuous/gpt-only/contribution2_recommendations.json](../runs/tool_calling_agent/binary_to_continuous/gpt-only/contribution2_recommendations.json)
- `all-tools`: [runs/tool_calling_agent/binary_to_continuous/evaluation/all-tools__end_to_end_eval_summary.json](../runs/tool_calling_agent/binary_to_continuous/evaluation/all-tools__end_to_end_eval_summary.json), [runs/tool_calling_agent/binary_to_continuous/evaluation/all-tools__end_to_end_eval_detail.csv](../runs/tool_calling_agent/binary_to_continuous/evaluation/all-tools__end_to_end_eval_detail.csv), [runs/tool_calling_agent/binary_to_continuous/all-tools/results.json](../runs/tool_calling_agent/binary_to_continuous/all-tools/results.json), [runs/tool_calling_agent/binary_to_continuous/all-tools/contribution2_recommendations.json](../runs/tool_calling_agent/binary_to_continuous/all-tools/contribution2_recommendations.json)
