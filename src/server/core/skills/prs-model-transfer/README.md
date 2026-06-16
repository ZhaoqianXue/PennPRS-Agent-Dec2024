# prs-model-transfer — developer notes

Developer-facing documentation. **Not loaded into any model context** — the loader injects only `SKILL.md` and any opted-in files under `references/`.

## What this skill is

Cross-phenotype PRS model transfer: identifying, evaluating, and ranking cross-trait PGS sources when a target trait has no high-quality same-trait PGS (or its same-trait PGS underperforms). This is the "Cross-phenotype PRS model transfer" capability, consumed by the contribution3 transfer pipeline.

The sibling skill `prs-model-recommendation` handles within-trait selection and owns the record-quality appraisal corpus (`prs-model-recommendation/references/pgs_evidence_appraisal.md`). When this skill needs those record-quality patterns it reads that file directly — there is no shared `_shared/` folder.

## ⚠️ This folder is a relocation only — not yet reconciled. Do NOT treat it as final.

The contribution3 transfer architecture that consumes this skill is **accepted/frozen (v16, accepted 2026-04-27)**. To avoid disturbing it, this folder was created by relocating the existing assets with the **SKILL.md body left byte-identical** to the previous `prs_model_evaluator/SKILL.md`. The only change applied is the frontmatter `name` (`prs-model-evaluator` → `prs-model-transfer`), which is **not** injected into the c3 view (`load_c3_view` injects only the body + the `description`), so the c3-facing prompt is unchanged.

The following are deliberately **deferred** to a later pass that re-runs the c3 evals before changing anything the model reads:

- **Rename in body.** The body still reads `# PRS Model Evaluator` and uses "evaluator" framing. "Evaluator" under-describes a skill that drives ranking/selection; rename to transfer/appraisal framing — but only with c3 re-validation, since the body is the c3 prompt.
- **Reference paths in body are legacy.** The "Reference files" table and the cross-trait pointer still name `reference/00..08`. The cross-trait file now lives at `references/cross_trait_transfer.md` (relocated verbatim from the old `reference/08_cross_trait_transfer_considerations.md`); the record-quality files moved to the sibling `prs-model-recommendation` skill. These in-body paths are inert (c3 opts out of all reference files by default) but stale, and should be reconciled in the same c3-revalidating pass.
- **Boundary cleanup (two-axis model).** The body still carries a "Constraints (binding for any caller)" block mixing agent-facing guidance (advisory / weigh case-by-case — keep) with developer-facing authoring discipline (trait-agnostic authoring, never compile rules into code weights — should move here to the README, as was done for `prs-model-recommendation`). Apply the same split here only with c3 re-validation.

See `prs-model-recommendation/README.md` for the two-axis content boundary (WHERE: skill vs system prompt; WHO: agent-facing vs developer-facing) and the authoring discipline this skill should eventually adopt.

## references/

- `cross_trait_transfer.md` — bundle-universe / probe-selection / mechanistic-evidence / multi-ancestry-breadth / cross-bundle-reconciliation heuristics for transfer. Uses the contribution3 transfer data model (bundles, `performance_records`, `ancestry_broad`, `performance_digest`), **not** the within-trait single-record PGS schema — do not re-point its field names to the single-record schema; they are a different model. Relocated verbatim from legacy `reference/08`.
