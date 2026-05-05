# Contribution2 Harness Engineering Positioning

Status: current positioning, last updated 2026-05-03.
Parent: `docs/architecture/pennprs_three_pillar_framing.md`
Related: `diagnose.md`, `production_ready.md`, `2026_harness_engineering_sources.md`

## Current Position

c2 is a **same-trait PGS-selection harness** under Pillar 2. The current production candidate is a **single generator-evaluator harness**, not iterD-final and not the exploratory Round46 consensus ensemble.

The kept path is R38-style top-5 holistic hidden-benchmark reranking:

- the sealed `prs_model_evaluator` Agent Skill remains the evidence layer;
- heritability records remain the second evidence channel;
- Stage 1 generates a primary pick plus top-5 shortlist from the Skill/H2-enriched candidate context;
- Stage 2 is a separated holistic evaluator over that bounded top-5 shortlist;
- the final recommendation is the Stage 2 hidden-benchmark winner.

This preserves the agent-skill story while avoiding the empirically falsified pure-ReAct failure mode where gpt-5.2 under-fetches Skill sections.

## Reference Floor

iterD-final remains the benchmark floor, not the desired final architecture:

`runs/minimal-lift-gpt-5.2-t1__89disease__iterD-final-cur89-t1-20260430-234950/`

Hit@1=0.3371, H2=0.5393, H3=0.6517, H4=0.7079, H5=0.7416.

## Current Candidate

Round47 N=2 fresh verification selected the R38-style single path:

| Architecture | Mean H1 | H1 Range | Mean H2 | Mean H3 | Mean H4 | Mean H5 |
|---|---:|---:|---:|---:|---:|---:|
| **R38 top-5 holistic hidden** | **0.3820** | **0.0000** | **0.5842** | **0.6798** | **0.7359** | **0.7921** |
| R33 top-3 pairwise hidden | 0.3932 | 0.0225 | 0.5730 | 0.6629 | 0.7191 | 0.7752 |
| R42 top-5 performance proxy | 0.3764 | 0.0562 | 0.5786 | 0.6573 | 0.7135 | 0.7640 |

R33 has a slightly higher mean Hit@1, but R38 is more stable and has better mean Hit@2-Hit@5. For a distribution-wide c2 benchmark with H1 emphasis, R38 is the better production compromise.

## Why Pure ReAct Was Not Kept

The ReAct pivot tested section-addressed Skill reads, all-reference reads, preloaded all-reference observations, JSON-schema terminal output, inline full Skill, h2-only tool surface, forced h2 calls, and iterD-style h2 formatting. None beat iterD-final; the best ReAct run reached H1=0.3034.

Mechanistic lesson: for this fixed-candidate structured-selection task, gpt-5.2 does not reliably know which Skill sections it needs to fetch. Pre-feeding the Skill/H2 evidence is load-bearing. Harness engineering here is better expressed as bounded evaluator orchestration over a shared evidence substrate, not as an open-ended tool loop.

## Why Round46 Was Not Kept

Round46 consensus was a useful exploratory diagnostic and reached H1=0.4270, but it combines three evaluator paths and is too heavy for the production c2 story. The requested N=2 fresh comparison showed that R38 is a stable single-path evaluator with distribution-wide lift over iterD-final, so production should keep the simpler single-path harness.

## Constraints Preserved

- No trait-, disease-, ICD-, PGS-ID-, whitelist-, blacklist-, or case-by-case rules.
- No numeric scoring formulas or deterministic disease-specific vetoes.
- No new external evidence tools.
- Skill/H2 remain the only evidence substrate.
- Output remains compatible with existing `per_disease[i].modal_recommendation_hit_at_k` and `trial_hit_at_k` summary tooling.
