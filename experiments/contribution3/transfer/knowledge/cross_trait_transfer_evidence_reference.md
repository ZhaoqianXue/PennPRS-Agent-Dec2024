# Cross-Trait Transfer Evidence Reference

Purpose: field-level evidence reference for cross-trait PRS transfer, summarizing the scientific signals that should support a `target trait -> cross trait bundle` match.

This document is a human-facing interpretation reference. The active runtime spec is:

- [CROSS_TRAIT_TRANSFER_SPEC.md](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution3/transfer/CROSS_TRAIT_TRANSFER_SPEC.md)

## Evidence Priority

Empirical evidence supports the following priority order for cross-trait transfer:

1. genetic correlation strength and statistical reliability
2. shared mechanism evidence from Open Targets
3. cross-trait heritability as a transfer ceiling
4. biological coherence between the target trait and the candidate cross trait

## Genetic Correlation

Key principle:

- `rg` is the primary statistical signal for cross-trait transferability.
- Higher `|rg|` indicates more shared genetic architecture between target and candidate traits.
- Reliability matters; stronger `rg_z` and more replicated study support should be preferred when available.

Positive signals:

- high `|rg|`
- strong `rg_z`
- consistent direction across evidence sources
- coherence with known biology

Warning signals:

- weak or noisy `rg`
- biologically implausible pairings with little other support
- apparently strong `rg` without supporting mechanism evidence

## Open Targets Mechanism Evidence

Key principle:

- Shared genes and shared pathways provide mechanistic support for why a cross-trait match should transfer.

Positive signals:

- multiple shared genes
- coherent pathways relevant to both traits
- strong evidence for the same genes in both traits

Warning signals:

- no shared genes/pathways despite moderate statistical evidence
- genes strongly supported for only one side of the pair
- mechanism evidence dominated by weak literature co-mention

## Heritability

Key principle:

- Candidate-trait heritability acts as a transfer ceiling.
- Even with strong correlation, a candidate with weak heritability offers limited transferable signal.

Positive signals:

- non-trivial heritability with acceptable confidence
- evidence from well-powered GWAS domains

Warning signals:

- near-zero or unstable heritability
- obvious low-signal candidates that cannot support meaningful transfer

## Practical Interpretation

The strongest cross-trait matches are those where:

- genetic correlation is strong
- Open Targets shows shared genes or pathways
- candidate heritability is non-trivial
- the overall pairing is biologically interpretable

The weakest matches are those where:

- the candidate looks like a generic biomarker proxy
- statistical evidence is weak or unstable
- Open Targets adds little or no mechanism support

## Current Development Note

Current development is focused on stabilizing the `all-tools` condition of the Cross Trait Transfer agent.

- Keep the evidence interpretation centered on:
  - `cross_trait_genetic_correlation`
  - `cross_trait_heritability`
  - `cross_trait_open_targets`
- Do not reinterpret this document as an alternative runtime workflow.
