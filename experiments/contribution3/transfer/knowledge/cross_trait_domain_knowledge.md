# Cross-Trait PRS Transfer Skill

Purpose: sealed empirical guidance for cross-trait polygenic-risk-score (PRS)
transfer. This file is the only place where transfer heuristics live. Prompt
files provide role, schema, and procedural constraints only.

This skill assumes no external evidence tools. Use only the target dossier,
candidate bundle metadata, ontology identifiers, aliases, model records, and
PGS performance metadata supplied in the current run. Do not invent biological
facts that are not inferable from those inputs.

Cross-cutting principles:

- The objective is transfer to the target cohort, not peak published source
  trait performance.
- First decide whether each source bundle is a plausible source for the target.
  Once a source passes that plausibility gate, PGS model quality can dominate
  source-label proximity.
- Direct, synonymous, parent, child, or sibling bundle relationships are strong
  source-plausibility signals, but they are not enough when the available PGSs
  from that source are weak, sparse, or poorly validated.
- Broad, well-studied upstream, quantitative, symptom, manifestation, or proxy
  bundles can be valid transfer sources because polygenic architecture can span
  endpoints. They should remain visible to downstream model comparison even when
  a closer-looking source exists.
- PGS quality is mainly about raw performance on meaningful records, sufficient
  training scale, robust method metadata, genome coverage, independent
  validation breadth, cohort diversity, and stable performance. Validation
  breadth is a robustness signal; it should not automatically defeat a PGS with
  materially stronger raw model-quality evidence.
- Keep decisions trait-agnostic. Do not write rules for specific ICD codes,
  diseases, organ systems, or named trait families.

## 1. Bundle Selection Heuristics

Scout should create a broad but intentional probe pool.

Positive inclusion signals:

- Bundle labels or aliases that directly match the target label or target
  aliases.
- Bundles whose labels or ontology identifiers appear to be parent, child, or
  sibling concepts of the target.
- Bundles with many available PGS models, especially broad or upstream traits,
  because they increase the chance that downstream stages can inspect a strong
  transferable PGS.
- Bundles that are not lexical matches but plausibly represent upstream factors,
  downstream manifestations, shared measurements, or proxy constructs based on
  the labels and aliases present in the dossier.
- Symptom-like, manifestation-like, and measurement-like bundles with plausible
  target relation. These can contain strong transferable PGSs and should not be
  crowded out by near-duplicate disease labels.

Selection discipline:

- Prefer inclusion when uncertain. The later stages can reject weak bundles, but
  they cannot recover a plausible source that Scout never exposes.
- Avoid probe pools made only of near-duplicate labels. Include close sources,
  sibling or parent sources, broad high-model-count sources, and plausible
  symptom/proxy/measurement sources.
- Do not rank or score bundles in Scout. The output is an exposure set for the
  evidence and model-selection stages.

## 2. Evidence Channel Hierarchy

With tools closed, Gather is a dossier-reading and note-writing stage.

Useful notes:

- State the apparent relationship between target and bundle: direct match,
  synonym, parent, child, sibling, upstream/proxy, downstream/manifestation, or
  unclear.
- Record why the bundle should stay under consideration using only labels,
  aliases, ontology identifiers, and model availability.
- Record uncertainty explicitly when the relation is inferred only from broad
  wording.
- Flag bundles that look plausible but have very few candidate PGSs, because
  model availability may limit transfer.
- Flag high-model-count broad bundles as breadth candidates, not as confirmed
  best sources.

Note discipline:

- Do not invent pathway, gene, or literature support.
- Do not use specific trait examples as precedent.
- A short, honest note is better than a confident unsupported mechanism claim.

## 3. Same-Trait vs Cross-Trait Bundle Ranking

Judge ranks source bundles for downstream PGS inspection.

Ranking principles:

- Direct, synonymous, parent, child, or close sibling sources normally belong
  near the top because source plausibility is strong.
- If several close sources exist, keep more than one visible so Pick and Global
  Primary can compare their actual PGSs.
- Broad high-model-count, symptom/proxy, and measurement sources should usually
  remain in the ranked list even when they are not the top source; they are
  exposure candidates for strong PGSs.
- A less direct source can outrank a close source when it is still plausible and
  the close source appears weak in the dossier, has sparse model availability,
  or is a poorer semantic fit than its label first suggests.
- A lexical match with no useful PGS candidates is weaker than a less direct
  source with several plausible PGS candidates.

Output shape:

- Produce a long enough ranked list for model comparison, usually several close
  or semantically related sources plus several broad, symptom/proxy, measurement,
  or high-model-count sources.
- Rank-1 should be the best source bundle for transfer, not merely the largest
  bundle.
- Keep reasoning in terms of source proximity, ontology/alias support, model
  availability, and uncertainty.

## 4. PGS Transferability Signals

Pick chooses PGSs within one supporting bundle.

Primary quality signals:

- Strong raw performance on meaningful validation records for the source trait.
- Sufficient training scale, method clarity, and genome coverage.
- Independent validation breadth across multiple performance records and
  cohorts.
- Validation across multiple broad ancestry groups or population contexts.
- Consistent discrimination or explained-variance metrics across records, not
  just one peak metric.
- Clear reported trait and mapped trait alignment with the supporting bundle and
  the target relation.

Trade-off discipline:

- When raw performance and model scale are similar, prefer the PGS with broader
  independent and population-diverse validation.
- When one PGS has a clearly stronger performance profile across meaningful
  records, do not overrule it solely because another has a larger training set or
  a newer publication year.
- Also do not overrule a PGS with clearly stronger raw performance, larger
  training evidence, or a better-established method solely because another PGS
  has broader validation metadata.
- Do not default to the newest, largest, or most complex model without checking
  validation breadth and trait alignment.
- Preserve a small frontier of plausible alternatives when evidence is close;
  Global Primary needs options across bundles.

Warning signals:

- Single-record or single-population validation despite impressive source-trait
  performance.
- Sparse or unclear performance metadata.
- Reported trait text that fits the source bundle poorly.
- Picking a PGS only because it has the largest training sample.

## 5. Cross-Bundle Reconciliation

Global Primary chooses the final PGS across all bundle frontiers.

Decision sequence:

- First compare source-bundle plausibility: direct or near-direct source,
  parent/child/sibling source, plausible upstream/proxy/manifestation source, or
  unclear source.
- If more than one source is plausible, let PGS model quality decide.
- If a less direct source has a markedly stronger PGS and is still plausibly
  related to the target, it can be primary.
- If one source is much more target-plausible, choose within that source unless
  its PGS evidence is genuinely weaker than another plausible source's PGS.

Model-quality comparison:

- Prefer strong raw performance supported by adequate training scale, method
  clarity, broad independent validation, population diversity, and consistency.
- Do not compare source-trait metrics as if they were measured on the same
  endpoint. Treat them as quality evidence for the PGS, not proof that the
  source is the best transfer source.
- When several less-direct sources have strong PGSs, choose the one with the
  clearer target relation and stronger overall model evidence, not just the
  numerically highest source-trait metric.

Reasoning discipline:

- Compare actual candidate records, not only bundle labels.
- Explain the final trade-off between source plausibility and PGS quality.
- Keep every valid frontier candidate in the ordered frontier.

Reference-lane discipline:

- When an independent no-skill reference primary is supplied, treat it as a
  control anchor. The skill is a conservative repair and upgrade layer, not a
  license to restart the search from broad proxies.
- Preserve the reference when the skill-guided challenger mainly swaps to a
  different broad source/proxy/measurement class, a newer publication, larger
  training size, broader validation metadata, or more fluent rationale without a
  clearer target-relevant source/model advantage.
- Override the reference only when the candidate records show a generalizable
  improvement: the reference source looks generic, truncated, ambiguous, or less
  target-aligned than the challenger; or the challenger is a same-source or
  equally plausible source with clearly stronger reported-trait alignment and
  PGS model evidence.
- Same-source PGS switches require record-level support. If two PGSs come from
  the same plausible source and the evidence is close, keep the no-skill
  reference rather than changing because of wording, recency, or validation
  breadth alone.

## 6. PGS Triage

Triage selects which PGS records in a large bundle deserve full hydration.

Selection goals:

- Preserve trait-aligned candidates, high-quality candidates, and diverse
  alternatives for Pick.
- Include candidates with strong compact performance summaries, broad validation
  hints, and clear method metadata.
- Include a mix across methods and publication periods when many candidates look
  plausible.
- Keep candidates whose reported or mapped traits best align with the source
  bundle and target relation.

Avoid:

- Selecting only the newest records.
- Selecting only one method family when other plausible methods exist.
- Filtering out multi-record or population-diverse candidates in favor of a
  single peak metric.

## 7. Critic Cross-Checks

Critic is a conservative verifier, especially when no external evidence tools
are available.

Revision principles:

- Keep the proposed primary when it has plausible source fit and strong PGS
  quality.
- Revise only when another frontier candidate is visibly better from the supplied
  candidate records and the proposed primary's rationale is weak.
- Do not revise merely because another bundle has a closer label if its PGS
  evidence is sparse.
- Do not revise merely because a broad source has a larger training sample if a
  close source has broader validation and adequate performance.
- Same-source PGS revisions require clear model-record evidence; otherwise keep
  the Pick or Global Primary ordering.

Critique discipline:

- State the concrete record-level contradiction that justifies revision.
- Prefer kept=True when evidence is close or uncertain.
- Do not introduce new source bundles or new PGS IDs.
