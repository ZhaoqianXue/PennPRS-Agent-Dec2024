# Within Prompt Surface

This package is the single prompt surface for within-phenotype PGS recommendation.

## Files

- `selectors.py`: decision-control prompts and builders. These prompts select,
  rank, or refine candidate PGS models.
- `audits.py`: transparency prompts and builders. These prompts produce
  post hoc evidence traces for Stage 1 shortlist compression, Stage 2 final
  selection, and legacy revision audits.
- `__init__.py`: public re-export surface for call sites.

## Experiment Contract

Selector and audit payloads use `skill_context` for material retrieved from the
sealed `prs-model-recommendation` Agent Skill. Candidate metadata, objective
blocks, and `skill_context` are evidence, not instructions: they must not
override the system-level role, decision boundary, evidence boundary, stage
boundary, candidate pool, or output schema. Older manifests are normalized to
this field at the experiment-runner boundary before any model call.

Audit prompts are non-interventional. The main experimental selection path does
not run audit by default.

Default selection path:

1. Stage 1 selector forms the shortlist.
2. Stage 2 selector picks the frozen final winner.
3. Metrics are computed only from the selector outputs.

Optional transparency path:

1. Pass `--emit-audit-trace` to an experiment runner.
2. Choose `--audit-stages stage1`, `--audit-stages stage2`, or
   `--audit-stages both`.
3. The runner writes a separate audit trace JSON file.

Stage 2 audit must not revise the experiment result. Its `winner_model_id` must
equal the supplied `frozen_winner_model_id`; any mismatch is recorded as an audit
error and never changes the final pick.
