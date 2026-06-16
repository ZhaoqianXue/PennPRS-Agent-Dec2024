---
name: cross_transfer_judge
description: Decide source-trait transfer candidates from provided PGS Catalog metadata and compact evidence.
---

# Cross Transfer Judge

Use this skill when selecting a source trait and a PGS model for a target that
needs cross-trait transfer.

## Allowed Inputs

Use only the target metadata, PGS Catalog metadata, compact source-bundle
cards, and raw evidence explicitly provided in the prompt. Treat missing
evidence as unavailable. Do not assume access to hidden files, private data,
external calculations, or prior decisions.

## Source-Trait Reasoning

Separate these questions:

1. Is the source trait on the same phenotypic axis as the target?
2. Is it a plausible biological, measurement, proxy, upstream, downstream, or
   construct-adjacent source?
3. Is the source too broad or too generic to support transfer?
4. Is the source a self-like weak same-trait bundle that should not displace
   cross-trait evidence?

Prefer evidence-visible relationships over broad name similarity. Treat
lexical similarity as one signal, not a complete argument.

When many source bundles are present, do not pick a PGS by scanning all models
for the most impressive method label or variant count. First choose the source
axis that best supports transfer, then choose the best PGS inside that source.
After that, compare the leading source-axis candidates against each other.

Do not automatically prefer the closest-looking phenotype label. A close label
with a weak, sparse, narrow, or poorly evaluated PGS can lose to a less direct
source when the latter is a coherent upstream, downstream, measurement, proxy,
or construct-adjacent axis and has much stronger visible PGS evidence.

Conversely, do not pick a broad generalist source on scale, recency, method
branding, variant count, or ancestry breadth alone. The source still needs a
record-visible bridge to the target. If the bridge is thin, keep it in the
frontier rather than making it primary.

## Clinical-vs-Measurement Calibration

When the target is a clinical condition, diagnosis, syndrome, procedure
outcome, or other non-laboratory phenotype, do not automatically prefer a
quantitative biomarker or measurement source merely because it sounds
mechanistic, upstream, or physiologic. A measurement source must explain the
target phenotype with a specific bridge visible from the prompt; otherwise it
is a broad proxy. This is not a disease-category rule: it is a general
source-type calibration.

Conversely, do not automatically prefer a clinical diagnosis source merely
because it is more label-like. A diagnosis, construct, or syndrome source can
beat a measurement source when it captures liability closer to the target and
has credible PRS evidence. A measurement source can still win when it is a
central causal, mechanistic, or construct-adjacent axis for the target and its
visible PGS evidence is materially stronger.

When clinical and measurement candidates are both coherent, decide by asking
which source has the more specific, evidence-supported transfer bridge to the
target, then compare visible PGS evidence. Do not let explanatory-sounding
labels substitute for record-visible support.

## PGS Reasoning

Within a selected source bundle, compare PGS models using endpoint fit,
method, variant count in method context, validation breadth, ancestry coverage,
publication context, release date, and raw performance descriptions when
available. Do not substitute covariate-heavy full-model metrics for PRS-only
evidence.

## Same-Source PGS Model Calibration

When two PGS candidates share the same source axis, mapped construct, or source
bundle, source fit no longer decides the choice. Compare the PGS models as
alternative implementations for the same transfer source.

In same-source comparisons, headline metrics are not automatically comparable.
Do not choose a model only because it has the largest best_auc, best_r2, sample
count, validation count, ancestry set, release date, or variant count. These
fields can reflect endpoint definition, cohort construction, covariate use,
reporting choices, or a source-specific outcome rather than a target-portable
PRS signal.

Ask which model has the stronger target-portable PRS signal from the provided
record: endpoint definition, method family, PRS-only versus covariate-heavy
evidence when visible, odds/hazard/beta estimates when relevant, evaluation
record context, ancestry context, release context, and whether the model looks
over-specialized to the source endpoint. A model with smaller headline metrics
can win when its evidence is more endpoint-relevant or more clearly PRS-based.
A model with larger headline metrics can still win when those metrics are
record-visible, comparable, and supported by method and endpoint context.

## Binary and Time-to-Event Effect Calibration

When the target or leading source is a clinical diagnosis, binary phenotype,
case-control endpoint, time-to-event endpoint, or liability-like outcome,
odds ratios, hazard ratios, beta estimates, and other effect-size fields can be
important evidence for risk separation. Use them as context, not a formula.

Do not automatically prefer AUC or R2 over effect-size evidence for diagnosis
or time-to-event transfer. AUC, R2, odds ratios, hazard ratios, beta estimates,
sample counts, and record counts can all be non-comparable when endpoint
definitions, cohorts, covariates, or reporting conventions differ. Ask whether
the metric is aligned with the target's endpoint type and whether it appears to
describe PRS signal rather than a covariate-heavy full model.

Effect-size evidence does not rescue a weak source bridge. A candidate still
needs a coherent source axis and endpoint fit. When source and endpoint fit are
coherent, a model with visible odds, hazard, or beta evidence can beat a model
with larger AUC or R2 if the latter looks less target-portable or less clearly
PRS-based. This is a general endpoint-metric calibration, not a disease-specific
rule.

## Tool Evidence Calibration

Raw tool evidence, including OpenTargets associated-target overlap, shared
therapeutic areas, shared ancestors, literature snippets, or genetic-correlation
snippets, is auxiliary context. It can support or weaken a proposed transfer
bridge, but it is not a source bridge by itself, not a formula, not authority,
not a vote, and not a reason to bypass source-axis coherence.

Shared associated targets can be inflated for broad, well-studied traits;
absence of overlap can reflect missing mappings, sparse data, or incomplete
tool coverage. Use ontology matches, shared ancestors, shared therapeutic
areas, and shared target examples as reasons to audit a candidate's source
relationship. The final choice still comes from source-axis coherence, endpoint
fit, and visible PGS evidence in the provided record.

Use this order of operations in Stage B:

1. Identify 3-6 plausible source axes from the provided bundles.
2. For each source axis, pick the strongest local PGS candidate using visible
   PGS metadata.
3. Reconcile the local winners across source axes.
4. Put the primary first, and keep plausible alternatives from different
   source axes in the frontier.

In chunked Stage B, optimize recall rather than finality. The chunk-local
primary is provisional; Stage C will reconcile across chunks. If the chunk has
enough candidates, return 8-12 frontier PGS IDs. The frontier should include
the best local model from each plausible source axis, plus diverse strong PGS
candidates that differ by source bundle, method family, raw performance signal,
or endpoint specificity. Do not collapse the frontier to 2-4 IDs merely because
one candidate looks best inside the chunk.

Penalize local winners that are selected only because they are first in the
list, have a familiar label, or have a large variant count without a clear
source-transfer argument.

## Output Discipline

Always cite the candidate fields used for each decision. Keep rationales short.
For Stage B and Stage C, rationale text must stay under 120 words; use terse
field paths in evidence lists rather than narrative.
When evidence is thin, preserve a frontier rather than over-claiming certainty.
