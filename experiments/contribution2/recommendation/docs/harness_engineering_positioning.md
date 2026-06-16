# Contribution2 Harness Engineering Positioning

Status: current positioning, last updated 2026-05-19.
Parent: `docs/architecture/pennprs_agent_paper_framing.md`
Related: `diagnose.md`, `production_ready.md`, `2026_harness_engineering_sources.md`

## Current Position

c2 is the **within-phenotype / same-trait PGS recommendation harness** inside the paper-facing PRS Agent architecture:

```text
LLM orchestration layer
└── Task-specific agent harness layer
    └── c2 within-phenotype PGS recommendation harness
        └── calls PRS Model Skill and tool layer:
            PGS Catalog metadata, heritability records, PRS Model Skill (`prs_model_evaluator`)
```

The c2 harness is invoked after the LLM orchestration layer has formulated a model-recommendation request and confirmed that target-phenotype PGS candidates exist. It is a task-specific harness that compares a fixed candidate universe using PRS evidence and the shared PRS Model Skill.

The current production candidate is a **single generator-selection harness**, not iterD-final and not the exploratory Round46 consensus ensemble.

The kept path is R38-style top-5 holistic hidden-benchmark reranking:

- the sealed PRS Model Skill implementation (`prs_model_evaluator`) remains the reusable PRS skill input;
- heritability records remain the second c2 evidence input;
- Stage 1 generates a primary pick plus top-5 shortlist from the Skill/H2-enriched candidate context;
- Stage 2 is a final-selection step over that bounded top-5 shortlist;
- the final recommendation is the Stage 2 hidden-benchmark winner.

This preserves the agent-skill story while avoiding the empirically falsified pure-ReAct failure mode where gpt-5.2 under-fetches Skill sections.

Paper-facing Methods wording should describe c2 as part of the task-specific agent harness layer:

> The within-phenotype harness is invoked when target-phenotype PGS records are available. It uses a Skill- and heritability-grounded generator-selection design: a generator forms a bounded shortlist from the retrieved PGS records, and a final-selection step returns the recommended model with alternatives and caveats.

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

Mechanistic lesson: for this fixed-candidate structured-selection task, gpt-5.2 does not reliably know which Skill sections it needs to fetch. Pre-feeding the Skill/H2 evidence is load-bearing. Harness engineering here is better expressed as bounded generator-selection orchestration over the PRS Model Skill and tool layer, not as an open-ended tool loop.

## Why Round46 Was Not Kept

Round46 consensus was a useful exploratory diagnostic and reached H1=0.4270, but it combines three evaluator paths and is too heavy for the production c2 story. The requested N=2 fresh comparison showed that R38 is a stable single-path evaluator with distribution-wide lift over iterD-final, so production should keep the simpler single-path harness.

## Constraints Preserved

- No trait-, disease-, ICD-, PGS-ID-, whitelist-, blacklist-, or case-by-case rules.
- No numeric scoring formulas or deterministic disease-specific vetoes.
- No new external evidence tools.
- Skill/H2 remain the only c2 PRS tool-and-skill inputs.
- Output remains compatible with existing `per_disease[i].modal_recommendation_hit_at_k` and `trial_hit_at_k` summary tooling.

## 2026 Architecture References For c2

Use the parent framing document for full references. The c2-specific takeaways are:

- AstaBench (ICLR 2026) and HAL (ICLR 2026) support treating the harness as an evaluable unit with traces, costs and controlled tool access, not as incidental prompt text.
- Tools are under-documented (ICLR 2026) supports explicit naming of PGS Catalog retrieval and heritability inputs rather than burying them inside generic context.
- PolySkill (ICLR 2026), SkillsBench (2026 resource) and the Agentic Skills SoK (2026 preprint) support treating the PRS Model Skill as a reusable procedural/domain capability consumed by the harness.
- CellVoyager (Nature Methods 2026) and SR-Scientist (ICLR 2026) support the broader single-agent scientific pattern: LLM orchestration selects a task path, while executable scientific tools and evaluation traces carry the scientific work.
