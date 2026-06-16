# Contribution 2 Harness Engineering Candidate

**Date:** 2026-05-19

**Current verdict:** keep a single, clean generator-selection architecture. Do not ship the Round46 consensus ensemble. The production candidate is **R38-style top-5 holistic hidden-benchmark reranking**.

Rationale: R33 has slightly higher N=2 mean Hit@1, but R38 is more stable and has better N=2 mean Hit@2, Hit@3, Hit@4, and Hit@5. Since c2 should show distribution-wide lift rather than only a fragile top-1 edge, R38 is the cleaner production choice.

## N=2 Fresh Verification

All runs below use the iterD-final 89-disease manifest, gpt-5.2, temperature=0, seed=42, chat.completions, workers=30.

| Architecture | Fresh 1 H1 | Fresh 2 H1 | Mean H1 | H1 Range | Mean H2 | Mean H3 | Mean H4 | Mean H5 | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **R38 top-5 holistic hidden-benchmark judge** | **0.3820** | **0.3820** | **0.3820** | **0.0000** | **0.5842** | **0.6798** | **0.7359** | **0.7921** | **keep** |
| R33 top-3 pairwise hidden-benchmark judge | 0.3820 | 0.4045 | 0.3932 | 0.0225 | 0.5730 | 0.6629 | 0.7191 | 0.7752 | higher H1, weaker H2-H5 |
| R42 top-5 performance-proxy judge | 0.3483 | 0.4045 | 0.3764 | 0.0562 | 0.5786 | 0.6573 | 0.7135 | 0.7640 | unstable |

Reference floor:

| Run | H1 | H2 | H3 | H4 | H5 |
|---|---:|---:|---:|---:|---:|
| iterD-final | 0.3371 | 0.5393 | 0.6517 | 0.7079 | 0.7416 |

R38 clears iterD-final across every Hit@K in the N=2 fresh mean:

- H1: +4.49 pp
- H2: +4.49 pp
- H3: +2.81 pp
- H4: +2.80 pp
- H5: +5.05 pp

## Kept Architecture

Production wrapper:

`experiments/contribution2/recommendation/scripts/run_experiment_top5_holistic_lift.py`

Equivalent explicit command:

```bash
python experiments/contribution2/recommendation/scripts/run_experiment_pairwise_rerank.py \
  --manifest experiments/contribution2/recommendation/runs/minimal-lift-gpt-5.2-t1__89disease__iterD-final-cur89-t1-20260430-234950/experiment_minimal_lift_batch_manifest.json \
  --run-tag <tag> \
  --model gpt-5.2 \
  --workers 30 \
  --top-k 5 \
  --evaluator topk_judge \
  --objective hidden_benchmark \
  --stage1-objective support
```

Mechanism:

- Stage 1 uses the existing Skill/H2-enriched evidence shape from the iterD-final manifest, but asks for a primary pick plus top-5 shortlist.
- Stage 2 runs a final-selection step over the top-5 shortlist.
- The final recommendation is the Stage 2 winner.

This is a general harness rule. It does not use trait-, disease-, ICD-, PGS-ID-, whitelist-, blacklist-, or case-by-case logic.

## Why Not Round46

Round46 reached H1=0.4270 by combining R38/R33/R42 with a fixed consensus rule. That result is non-oracle and still general, but it is not the right production shape: it triples evaluator surface area, makes the c2 story less clean, and increases run cost without proving that a single evaluator is stable.

The requested N=2 fresh comparison showed that R38 is a stable single-path architecture with distribution-wide lift over iterD-final. Keep the simpler architecture.

## Why This Counts As Harness Engineering

c2 is no longer just the iterD fixed workflow. The harness now separates generation from evaluation:

- the sealed PRS Model Skill and heritability evidence remain the fixed PRS evidence inputs;
- Stage 1 generates a bounded top-5 candidate shortlist from that evidence;
- Stage 2 acts as a final-selection step over the shortlist;
- the harness exposes the evaluator objective as a fixed hidden-benchmark selection frame.

This matches the generator-selection / evaluator-optimizer family of harness engineering while preserving the PRS Model Skill framing.

## Remaining Production Step

The current N=2 verification was run through fast chat.completions. Before final lock, run the kept R38-style wrapper twice through the intended production execution surface if production will use Batch API. Acceptance criterion: no H1 regression vs iterD-final and mean Hit@1-Hit@5 remains above iterD-final.
