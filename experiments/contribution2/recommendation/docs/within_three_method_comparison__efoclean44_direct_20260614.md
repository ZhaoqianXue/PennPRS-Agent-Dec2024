# Within-trait three-method comparison

> Superseded for current formal reporting.
> Use `within_formal_three_arm_definitions_20260615.md` for the retained clean Full44 three-arm names and results.
> The table below is an older direct-run comparison and is kept only as historical context.

- Disease set: **44 diseases** | Model: **gpt-5.4** | Scorer: AoU-benchmark Hit@k (tie-aware top-k)

| Method | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---|---|---|---|---|---|
| PRS Agent (LLM + harness + reworked skill) | 17/44 (38.6%) | 20/44 (45.5%) | 24/44 (54.5%) | 26/44 (59.1%) | 28/44 (63.6%) |
| General LLM selector (no skill/tools) | 12/44 (27.3%) | 20/44 (45.5%) | 24/44 (54.5%) | 26/44 (59.1%) | 28/44 (63.6%) |
| PGS Catalog reported-max (reported_max_auroc_or_c_index_disease_consistent) | 5/44 (11.4%) | 9/44 (20.4%) | 15/44 (34.1%) | 21/44 (47.7%) | 22/44 (50.0%) |

- **Hit@1 lift**: PRS Agent 38.6% vs General LLM 27.3% (+11.4pp) vs reported-max 11.4% (+27.3pp)
- **API cost (gpt-5.4)**: PRS Agent $5.5051 | General LLM $3.4756 | PGS reported-max $0.00 (deterministic, no LLM calls)
