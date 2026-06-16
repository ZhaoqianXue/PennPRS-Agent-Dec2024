# Type A59 cross-phenotype baseline vs PRS Agent presentation figures

These figures compare two methods: Baseline LLM and PRS Agent.

## Files
- `fig1_cross_overall_performance_typeA59`: scatter + mean AUC/GPR + Hit@top-percentile accuracy.
- `fig2_cross_delta_auc_waterfall_typeA59`: target-level selected-model AUC gains/losses with representative transfer changes.
- `fig3_cross_transfer_source_landscape_typeA59`: transfer frontier size, reused source traits, and target-to-source categories.
- `fig4_cross_micro_transfer_case_studies_typeA59`: source-trait transfer case studies for selected targets.
- `table1_cross_percentile_evaluation_matrix_typeA59`: Hit@top-percentile cross-phenotype evaluation matrix.

Each figure/table image is exported as PNG.

## Key numbers
- Coverage: Baseline 1.000; PRS Agent 1.000.
- Mean selected-model AUC: 0.531 -> 0.544.
- Mean global percentile rank: 0.769 -> 0.811.
- Mean absolute AUC regret: 0.058 -> 0.045.
- Paired AUC: 34 improved, 6 tied, 19 lower.
- Transfer frontier size: median 168; range 42-665.

## Source data
- `source_data/typeA59_baseline_vs_prs_agent.csv`
- `source_data/typeA59_baseline_vs_prs_agent_summary.json`
- `source_data/typeA59_micro_case_studies.csv`
- `source_data/table1_cross_percentile_evaluation_matrix.csv`
