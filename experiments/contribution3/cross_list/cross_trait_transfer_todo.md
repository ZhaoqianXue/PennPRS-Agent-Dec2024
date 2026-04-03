# Cross-Trait Transfer TODO

## Current Working Decision

- Cross-trait transfer is now defined as a **tool-calling matching module**, not a local-graph transfer module.
- Runtime input is **not** the shortlist. Runtime input is:
  - `TargetTraitQuery`
  - `CandidateBundleDossier` built from the full `TraitBundleIndex`
- The current source-of-truth spec is:
  [CROSS_TRAIT_TRANSFER_SPEC.md](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution3/transfer/CROSS_TRAIT_TRANSFER_SPEC.md)
- The shortlist file:
  [binary_cross_trait_shortlist.csv](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution3/cross_list/analysis/phase2/binary_cross_trait_shortlist.csv)
  is used as the current silver-label evaluation source, not as runtime candidate input.
- Do not block transfer pipeline development on additional cross-trait cleanup.
- Family-level redundancy and hubness are not current blockers for development, because multiple related donor traits can all be useful opportunities for a target trait.

## Deferred Review TODO

- Add a dedicated review pass for `Questionable donor` target-cross pairs before final candidate freeze or final result interpretation.
- For now, use the current operational proxy:
  `Questionable donor = pair appears in binary_cross_trait_shortlist.csv and plausibility == low`
- Review goal:
  distinguish between
  `statistically strong but biologically believable`
  and
  `generic biomarker / proxy / likely spurious donor`

## Immediate Development Priority

- Stabilize the `all-tools` runtime condition first.
- Defer ablations until `all-tools` is producing acceptable matching behavior.
- Keep `Questionable donor` handling as a later curation and interpretation step, not a prerequisite for transfer-agent development.
