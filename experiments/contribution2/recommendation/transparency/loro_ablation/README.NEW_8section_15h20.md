# prs-model-recommendation — developer notes

Developer-facing documentation for this skill. **This file is not loaded into any model context** — the skill loader injects only `SKILL.md` and the files under `references/`. Everything that is authoring discipline, project labelling, or maintenance history lives here, never in `SKILL.md`.

## What this skill is

Within-trait PGS model recommendation: given a single fixed target trait and several candidate PGS Catalog models (each serialized as one representative single record plus a compact validation-ancestry profile when a European-only representative record would otherwise hide multiple non-European or multi-ancestry validation records), appraise and rank the candidates on record-visible quality and recommend the strongest. This is the "Within-phenotype PRS model recommendation" capability.

The sibling skill `prs-model-transfer` handles cross-phenotype transfer (which trait/bundle is related to the target). If that skill ever needs this skill's record-quality patterns, it reads `references/pgs_evidence_appraisal.md` directly — there is no shared `_shared/` folder.

## Two-axis content boundary (enforce this when editing)

Two orthogonal axes decide where any piece of text belongs. Keep them straight.

**WHERE — Skill vs System Prompt:**
- *Skill* = portable, reusable domain knowledge + procedure for the capability, independent of which agent/harness loads it. → `SKILL.md` + `references/`.
- *System Prompt* = the calling agent's role, task framing, I/O contract, and runtime constraints. → lives in the harness, not here. The skill must never contain harness-specific framing.

**WHO — Agent-facing vs Developer-facing:**
- *Agent-facing* = text the model needs to do the task, written in functional language. → may appear in `SKILL.md`/`references/` (if domain knowledge) or in the system prompt (if role/IO).
- *Developer-facing* = project code-names, authoring discipline, internal labels, maintenance notes. → README / manifest / logging / metadata only. **Never in the model's context** (and note: HTML comments inside `SKILL.md` are still sent to the model, so they are not a hiding place — put developer notes here instead).

Consequence to watch for in the harness: project labels such as `Contribution2`, `PEV harness`, `iter11`, or internal stage code-names are developer-facing and must not appear in the system prompt the model sees. The system prompt should state the functional role ("you select the single best PGS for one fixed target trait from the candidate records"); the project label belongs only in logs/config.

## Authoring discipline (developer-facing — deliberately kept out of SKILL.md)

These were previously stated as agent-facing "constraints" inside the old SKILL.md. They are really instructions to the *author* of the skill, so they live here:

- **Trait-agnostic authoring.** Never write rules that name specific ICD codes, trait categories, or disease families. The corpus must read identically for any disease. (The agent-facing residue — "stay trait-agnostic in your reasoning, do not special-case diseases" — is a one-line reasoning posture that belongs in the system prompt, not a repeated skill constraint.)
- **LLM-led, never code-compiled.** Never convert any pattern in `references/pgs_evidence_appraisal.md` into a hard numeric score, weight, ranking formula, or deterministic veto in code. The patterns are advisory and weighed case-by-case by the model. (The agent-facing residue — "these are advisory, weigh case-by-case, no fixed precedence" — *is* load-bearing and stays in `SKILL.md`/the corpus, because without it the model treats heuristics as hard filters and over-selects, which measurably hurts.)

## Consumption

Within-trait recommendation loads the **whole** corpus every time: `SKILL.md` (procedure + agent-facing guidance) plus the single `references/pgs_evidence_appraisal.md` file, injected together. The corpus is intentionally one merged file rather than per-field files, because within a single trait every section bears on every candidate comparison — the content is not mutually exclusive, so progressive (selective) disclosure buys nothing and only fragments the corpus. Keep it one file with a table of contents.

## Schema-alignment changelog (old multi-record schema → current single-record schema)

The corpus was migrated from the legacy field vocabulary to the fixed-section single-record schema. For maintainers tracing why a rule reads the way it does:

**Renames / relocations:**
- `trait_reported`, `trait_efo` → `predicted_trait.{trait_reported, trait_efo[].{label,id}}`
- `phenotyping_reported` → `performance_metrics.phenotyping_reported`
- `performance_metrics.auc/r2`, `classification_metrics`, `other_metrics` → `performance_metrics.metrics.{pgs_only_r2, pgs_only_auroc, full_model_auroc, c_index, effect_sizes[]}`
- "PGS AUROC (no covariates)" / "PGS R2 (no covariates)" → `metrics.pgs_only_auroc` / `metrics.pgs_only_r2` (now structural fields, no longer free-text metric-name parsing)
- `validation_sample_size` → `performance_metrics.evaluation_sample.sample_numbers.{individuals,cases,controls}`
- `samples_training` + `samples_variants` + `ancestry_distribution` (old `training_development_cohorts` union) → split into `source_of_variant_associations_gwas` + `score_development_training`; ancestry is now a single broad value per primary section, with validation breadth summarized separately in `evaluation_ancestry_profile`
- `method_name` → `development_method.method_name`
- `variants_number` → `variants.variants_number`
- `publication.*` → `pgs_source.{publication_title, publication_journal, date_release}`
- `covariates` → `performance_metrics.covariates`

**Deleted (signal no longer exists / now done in code):**
- Multi-record selection guidance ("pick the representative validation record / highest-result European record / else highest overall"). Record selection is now deterministic upstream in `_select_representative_performance_record`; the model sees exactly one record per candidate, so this guidance was removed.
- European-record selection by ancestry within a candidate (no multi-record set to filter in the model; evaluation ancestry of the selected representative is checked directly).

**Added (new schema surfaces signal the old corpus did not exploit):**
- `c_index` is now a first-class metric — Section 2 gives it explicit handling (concordance for survival/HR models; full-model unless stated PGS-only).
- `cases`/`controls` split in sample numbers — Section 2 reads it as a study-design (not power) signal.
- `effect_sizes[]` now carry confidence intervals (`ci_lower`/`ci_upper`) — Section 2 weighs interval width as estimate precision.
- Incremental AUROC has no field; Section 2 derives it as `full_model_auroc − pgs_only_auroc` when both are present.
- Beta is dropped from effect sizes (redundant with OR); the corpus references OR/HR per SD.
- Non-null `evaluation_ancestry_profile` restores compact visibility into validation breadth: `record_count`, observed validation ancestries, the selected representative ID/ancestry, and up to three non-representative diverse/multi-ancestry validation records. This is supporting evidence for transportability, not a deterministic record-selection rule.

**Cross-trait content removed from this skill:** the legacy `reference/08_cross_trait_transfer_considerations.md` (bundle/probe/Open-Targets/multi-record transfer reasoning) does not belong to within-trait recommendation and now lives in the `prs-model-transfer` skill. The old within consumer concatenated it by accident.
