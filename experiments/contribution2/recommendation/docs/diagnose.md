# Phase A Reproducibility Failure — Diagnosis & Proposed Patches

**Date:** 2026-05-02
**Result:** Phase A **FAILED** the reproducibility threshold and Phase B is **NOT entered**.
**Threshold:** N=2 mean Hit@1 ≥ iterD-final (0.3371) + 3pp = 0.3671.
**Observed:** N=2 mean Hit@1 = 0.3483 ( = +1.1pp over iterD-final). Below threshold by –1.9pp.

## What was run

Two end-to-end fresh chat.completions runs of
`run_experiment_consistency_routed_pairwise.py` over the 89-disease cur-89
manifest at temperature 0, seed 42, workers 20:

- `runs/consistency-routed-pairwise-gpt-5.2-t1__89disease__phaseA-fresh-run1-cur89-20260502-204305/`
- `runs/consistency-routed-pairwise-gpt-5.2-t1__89disease__phaseA-fresh-run2-cur89-20260502-204555/`

Compared against:

- iterD-final baseline: `runs/minimal-lift-gpt-5.2-t1__89disease__iterD-final-cur89-t1-20260430-234950/`
- Post-hoc Round 5: `runs/consistency-routed-pairwise-gpt-5.2-t1__89disease__round5-prod-from-existing-20260502-201710/` (deterministic post-processing of iterD-final + Round 1 artifacts)
- Round 1 source: `runs/pairwise-rerank-gpt-5.2-t1__89disease__round1-pairwise-cur89-20260502-194632/`

## Hit@K table

| Source | H1 | H2 | H3 | H4 | H5 |
|---|---|---|---|---|---|
| iterD-final (Batch API) | 0.3371 | 0.5393 | 0.6517 | 0.7079 | 0.7416 |
| Post-hoc Round 5 | **0.3933** | **0.5843** | **0.6854** | 0.7191 | 0.7640 |
| Phase A fresh run 1 | 0.3708 | 0.5506 | 0.6404 | 0.6854 | 0.7416 |
| Phase A fresh run 2 | 0.3258 | 0.5169 | 0.6067 | 0.6854 | 0.7416 |
| **Phase A N=2 mean** | **0.3483** | **0.5337** | **0.6236** | **0.6854** | **0.7416** |

The post-hoc Round 5 result is **not reproduced** by fresh runs. Worse, the
two fresh runs themselves disagree on H1 by 4.5pp.

## Root cause: gpt-5.2 t=0 seed=42 is non-deterministic at the call surface

Same prompt, same temperature, same seed, same model name produces *different*
picks across calls. The disagreement counts on this 89-ontology task are:

### Stage 0 (pristine `CO_SCIENTIST_STEP1_PROMPT`, no schema augmentation)

| Comparison | Disagree / 89 |
|---|---|
| fresh run 1 vs iterD-final (Batch API) | 10 |
| fresh run 2 vs iterD-final (Batch API) | 15 |
| fresh run 1 vs fresh run 2 (both chat.completions) | 11 |

### Stage 1 (schema-augmented prompt asking for `top_alternatives`)

| Comparison | Disagree / 89 |
|---|---|
| fresh run 1 vs Round 1 Stage 1 | 18 |
| fresh run 2 vs Round 1 Stage 1 | 15 |
| fresh run 1 vs fresh run 2 | 11 |

### Routing decisions cascade the noise

The router compares Stage 0's pick to Stage 1's pick. When either or both
flip stochastically, the routing decision flips:

- Fresh run 1: 72 consistent / 16 fallback / 1 missing.
- Fresh run 2: 64 consistent / 24 fallback / 1 missing.
- **16 / 89 ontologies routed differently between the two fresh runs.**

13 / 89 final picks differ between the two fresh runs even though both used the same model, prompts, temperature, and seed.

### Implication for the post-hoc result

The post-hoc Round 5 (H1=0.3933) was constructed from a *particular* lucky
draw: iterD-final's Batch API picks happened to be H1-correct on 5 ontologies
that Round 1's Stage 1 disagreed with. Re-running Stage 0 + Stage 1 fresh
re-rolls that draw and breaks the coincidence. The architectural lever
(consistency-routed pairwise) is real, but the magnitude of its lift is
dominated by call-surface noise on this test size (89 ontologies, single trial).

## Where the H1 swing came from

Comparing fresh run 1 (H1=33) vs fresh run 2 (H1=29), 13 final picks differ.
Out of those 13:

- Several flipped from `consistent_borda` (use Round 1's pairwise winner) to
  `fallback_disagree` (use Stage 0's pristine pick) because Stage 1 changed
  its primary pick on a stochastic re-roll.
- A few flipped because Stage 0 itself produced a different pristine pick.
- The pairwise judge calls also differ between runs, but Stage 2 noise is
  dominated by Stage 0 + Stage 1 noise upstream.

The downstream metric is unstable because the upstream stages are unstable.

## Why prior rounds appeared to work / fail

- iterD-final, Round 1, and post-hoc Round 5 each consume a *fixed* set of
  Stage 1 outputs. Comparing them against each other measures the *aggregation
  rule* (single pick vs pairwise vs consistency routing) on a fixed sample.
- Phase A consumes *new* Stage 1 outputs. The aggregation rule is unchanged,
  but the inputs are noisier samples from the same nominal distribution. The
  net Hit@1 reflects both the rule and the sample.
- Round 2 and Round 3 (rolled back earlier) regressed badly enough to look
  signal-not-noise. Round 1 and Round 5's apparent lifts of ~3-5pp are within
  the call-surface noise band and so are NOT confidently above iterD-final.

## Patches to consider before re-attempting Phase B

The patches are listed in priority order, with the rationale and expected
trade-off for each. None have been applied yet — this document is the artifact
that Phase A's stop-condition required.

### P1. Switch Stage 0 + Stage 1 + pairwise to OpenAI Batch API for evaluation

**Why:** iterD-final was generated via OpenAI Batch API. The Batch API and
chat.completions surface use different sampling internals — empirically up to
15 / 89 picks differ on the same prompt. Running everything through the same
Batch API path eliminates the cross-surface stochasticity and makes the
Round-5 routing deterministic relative to iterD-final.

**Cost:** Batch API has a 24h completion window, so iteration is much slower
than the ~3-min sync runs. Acceptable for a final production validation, not
for inner loops.

### P2. N-trial averaging of Stage 0 + Stage 1 with internal majority/Borda denoising

**Why:** If single-trial t=0 drift is ~10-15 picks per stage, taking the
*mode* of k=3 or k=5 trials at t=0 (or t=0.3 with Borda) will collapse the
drift to the genuinely uncertain ontologies. The pristine baseline becomes
"trial-stable iterD-final pick" rather than "single-shot lucky draw".
Routing then operates on stable inputs.

**Cost:** Linear LLM-call increase. With workers=20 it's still under 10 min
per round.

### P3. Compute the trial-average H1 metric, not single-trial Hit@1

**Why:** The prior runs used `--trials 1` so `modal_recommendation` is just
one stochastic draw. With `--trials 5` (using the existing chunked-choices
infrastructure) `modal_recommendation` is the modal pick across 5 trials,
which is much less noisy. iterF / iterG already used trials=3 / 5 but voted
on single picks at t=0 / t=0.3 — at gpt-5.2's near-deterministic distribution
the votes degenerate. With t=0.3 + trials=5 at the *Stage 1* level (not
ranked-voting), modal_recommendation should at least give a stable iterD-style
baseline to route against.

**Cost:** 5x LLM calls for Stage 0 / Stage 1.

### P4. Drop the consistency router; commit to pure Round 1 (pairwise rerank)

**Why:** The post-hoc Round 5 lift over Round 1 was small (+2 H1 in absolute
hits) and entirely inside the noise band. Round 1's pairwise judging is the
load-bearing mechanism per the Bavaresco et al. 2026 result. A pure Round 1
pipeline run multiple times and trial-averaged is likely as good in
expectation as the consistency-routed variant, with simpler architecture.

**Cost:** Forfeits the schema-perturbation regression recovery (Round 5's
nominal advantage). But that recovery was within noise anyway.

### P5. Replace pairwise judging with rubric-anchored top-K judging (single-call top-K)

**Why:** Pairwise needs 3 calls per ontology (top-3 case); a single-call
top-K judgment over the same shortlist eliminates 2/3 of the Stage 2 noise
budget while still giving the judge the comparative framing that fixes the
within-prompt-rank-discrimination failure mode. The Bavaresco et al. result
favors pairwise *only when budget allows multiple comparisons*; for a fixed
small candidate set, a structured top-K rubric in one call may be more
sample-efficient.

**Cost:** Loses the independence-across-pairs that gives Borda its variance
reduction. Worth trying as an alternative in Phase B if P1+P2 succeed.

## Recommended next step

Combine **P1 + P2** as the minimum viable patch:

1. Run Stage 0 (pristine) + Stage 1 (schema-augmented) + pairwise via the
   OpenAI Batch API (matching iterD-final's surface) instead of
   chat.completions.
2. Within Stage 0 and Stage 1, request `n=5` choices in the same Batch API
   request so Stage 0/Stage 1 each emit a 5-trial mode rather than a single
   pick. The existing `_choice_chunks` machinery in
   `run_experiment_without_domain.py` already supports this.

Re-run Phase A with this patched pipeline. The success criterion remains:
N=2 mean H1 ≥ 0.3671. Only then enter Phase B.

## What this diagnosis does NOT yet tell us

- Whether the *true* expected Hit@1 of consistency-routed pairwise is above
  iterD-final at all, or whether the apparent lift is purely sample-flavor.
  P2's modal denoising is the cleanest way to find out.
- Whether iterD-final itself is reproducible. The "baseline" we have been
  comparing against is also a single Batch API draw. Re-running iterD-final
  through Batch API multiple times would tell us how stable that anchor
  itself is.

A full Phase B push to H1 ≥ 0.5 on top of an unreproducible baseline is
premature. The honest read is: the architectural levers studied (pairwise
rerank, consistency routing) are plausibly net-positive but their magnitude
is below the per-call noise floor on this 89-target test size, and we cannot
distinguish the two from chance until the upstream Stage 0 / Stage 1 sources
are denoised.
