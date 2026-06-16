# Within-trait three-method comparison

> Superseded for current formal reporting.
> Use `within_formal_three_arm_definitions_20260615.md` for the retained clean Full44 three-arm names and results.
> The table below is an older 44-disease comparison and is kept only as historical context.

- Disease set: **44 diseases** | Model: **gpt-5.4** | Scorer: AoU-benchmark Hit@k (tie-aware top-k)

| Method | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---|---|---|---|---|---|
| PRS Agent (LLM + harness + reworked skill) | 19/44 (43.2%) | 24/44 (54.5%) | 27/44 (61.4%) | 28/44 (63.6%) | 30/44 (68.2%) |
| General LLM selector (no skill/tools) | 9/44 (20.4%) | 15/44 (34.1%) | 23/44 (52.3%) | 26/44 (59.1%) | 29/44 (65.9%) |
| PGS Catalog reported-max (reported_max_auroc_or_c_index_disease_consistent) | 4/44 (9.1%) | 9/44 (20.4%) | 14/44 (31.8%) | 18/44 (40.9%) | 22/44 (50.0%) |

- **Hit@1 lift**: PRS Agent 43.2% vs General LLM 20.4% (+22.7pp) vs reported-max 9.1% (+34.1pp)
