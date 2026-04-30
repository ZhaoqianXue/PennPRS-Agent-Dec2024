# PICK-stage emphasis: PGS quality signals for cross-trait transfer

This override supplements the procedural overview in SKILL.md for the
PICK stage specifically, where the source bundle has already been
fixed by an upstream stage and the task is to choose the best PGS
within that bundle as a transfer source for the target.

For cross-trait transfer, weigh the following signals together — none
has fixed precedence; the candidate records decide which signal
dominates in any given comparison.

## Signals to weigh

- **Polygenic signal robustness is a first-class signal.** Candidates
  with large training samples, broad variant coverage, and consistent
  performance across multiple independent validation cohorts
  (especially across ancestries) carry transferable polygenic
  information even when their source-trait endpoint is less specific.
  Do not treat these as weak tie-breakers underneath endpoint
  fidelity.

- **Endpoint specificity and polygenic breadth are complementary, not
  ranked.** A PGS narrowly tuned to its source-trait endpoint can
  transfer well, but is not automatically better than a broader,
  well-powered sibling. Decide from empirical signals: which
  candidate has cleaner PRS-only metrics, more diverse validation,
  more robust cross-cohort consistency?

- **Multi-trait integration scores can transfer either way.** Methods
  that integrate related phenotypes (power-boost, multi-trait
  analysis) sometimes transfer better because they leverage shared
  genetic architecture, sometimes worse because the integration
  introduces noise. The methodological label alone does not determine
  the outcome — judge from the records.

- **Same-source clusters.** When several candidates come from the same
  publication family, pick based on which one has the strongest
  visible quality signals (cleaner PRS-only metrics, better
  cross-cohort consistency, larger and more diverse training
  samples), not on which one most narrowly matches the source-trait
  label.

- **Acknowledge ties.** When two surviving candidates are roughly
  comparable on the visible fields, say so in your rationale rather
  than artificially declaring one the winner. The downstream stages
  can revisit ties; an over-confident pick is harder to recover from.

## What this override is and is not

This override does **not** override the empirical patterns in the
canonical reference corpus. It points out which of those patterns
matter most for transfer specifically, so that PICK does not default
to a same-trait-style endpoint-fidelity-first ordering when transfer
is the actual task.

## Constraints (binding)

- Apply each pattern only when the candidate records show the
  signal; do not infer from labels alone.
- Do not introduce or apply rules that name specific traits, ICD
  codes, organ systems, or disease families.
- The decision is yours. This guidance describes empirical signals
  that often matter for transfer; it does not score, weight, or veto
  candidates.
