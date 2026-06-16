# Cross Optimized Implementation Spec

Status: additive prototype.

This directory implements a leak-controlled, batch-oriented optimized version
of Contribution 3 cross-trait transfer. It must not modify the existing
within-trait Contribution 2 pipeline or the existing Contribution 3 transfer
pipeline.

## Data Boundary

Runtime optimization may use:

- PGS Catalog metadata and local PGS Catalog cache fields.
- Target identifiers, labels, ontology labels, descriptions, target source,
  and Type A / Type B labels from the existing benchmark target-selection CSV.
- AUC-matrix headers only, to determine whether a PGS ID is evaluable in the
  benchmark source universe.
- Raw source metadata such as method, variant count, ancestry fields,
  publication metadata, and original PGS Catalog performance records when
  added by future hydration code.

Runtime optimization must not use:

- Per-target AUC row values from Contribution 1.
- Any oracle, benchmark-top, selected-rank, percentile, GPR, regret, or AUC
  gain derived from Contribution 1 evaluation rows.
- `self_best_auc` or target-specific old-run failure labels.
- Old run details that reveal target-specific empirical performance.

The frozen evaluation step is the only boundary allowed to read target-row AUC
values.

## Pipeline

1. Build a compact PGS Catalog.
2. Retrieve a high-recall candidate source-bundle universe using metadata only.
3. Build batch JSONL requests for Stage A source-bundle shortlist.
4. Build batch JSONL requests for Stage B PGS selection from selected bundles.
5. Freeze predictions and write a hash manifest.
6. Evaluate frozen predictions against the Contribution 1 matrix.

## Engineering Rules

- Keep prompt inputs compact and high-signal.
- Keep static prompt prefixes stable for prompt caching.
- Use batch-compatible request builders.
- Run `leak_guard` on every generated prompt body before submission.
- Log token usage and cost after batch output collection.
- Treat all eval outputs as post-freeze artifacts.
