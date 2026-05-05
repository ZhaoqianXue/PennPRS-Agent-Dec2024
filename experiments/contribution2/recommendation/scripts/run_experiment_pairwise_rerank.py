"""Round 1 — Pairwise reranking on top-3 (separated-evaluator architecture).

Hypothesis (Phase 1 + Phase 3 grounded):
- Phase 1, Anthropic harness paper: a stock LLM is a poor evaluator of its own
  work; "Separating the agent doing the work from the agent judging it proves
  to be a strong lever".
- Phase 1, Bavaresco et al. 2026 (LLM-judge BoN paper): in matched best-of-2
  audits, pairwise judging raises selection-recovery from 21.1% → 61.2% versus
  pointwise scoring, because pointwise tie rates near 67% force random tiebreaks.
- Phase 3, iterD-final 89-disease t=1: 36 of 59 H1 misses are still inside H5,
  meaning the right candidate is in the LLM's reachable shortlist but Stage 1
  fails to discriminate the AUC-best within a tight cluster.
- Distinct from prior failures: not multi-trial sampling (iterF/G majority vote
  failed at t=0/0.3); not extra decision-protocol prose (iterE failed); not
  open-ended TRIAGE/PICK/CRITIC (pev-with-skill over-revised). Stage 2 here is
  *bounded* — it can only choose among Stage 1's own top-3, never overrule out
  to a 4th-best candidate.

Architecture:
  Stage 1: same iterD-final context (SKILL.md procedural overview + 55K corpus +
           heritability section), same CO_SCIENTIST_STEP1_PROMPT, but the schema
           is augmented to also emit `top_alternatives: [pgs_id, pgs_id]`
           (two best-supported runners-up after `best_model_id`). Single-shot,
           t=0, seed=42 — preserves iterD-final pick on the easy 30 cases.
  Stage 2: For each ontology, three pairwise-judge calls — (best vs alt1),
           (best vs alt2), (alt1 vs alt2). Each is an independent call with a
           strict pairwise-comparison system prompt; the judge is told its
           default is to pick a winner (not declare a tie).
  Aggregate: Borda count over pairwise wins (2 / 1 / 0 wins). Final pick =
           Borda max; tiebreak prefers Stage 1's best_model_id, then alt1.

If Stage 1 emits valid `top_alternatives` of length < 2, the pairwise stage is
skipped and the Stage 1 best_model_id is used directly (graceful degradation).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401 — registers patches into wd
from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as wd
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.system_prompts import CO_SCIENTIST_STEP1_PROMPT


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class Step1RankedDecision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    top_alternatives: list[str]
    confidence: str
    rationale: str


class PairwiseJudgment(BaseModel):
    winner_model_id: str
    confidence: str
    rationale: str


class TopKJudgment(BaseModel):
    winner_model_id: str
    confidence: str
    rationale: str


class TopKRankingJudgment(BaseModel):
    ranked_model_ids: list[str]
    confidence: str
    rationale: str


class CandidateAudit(BaseModel):
    pgs_id: str
    endpoint_fit: str
    metric_signal: str
    validation_signal: str
    risk_signal: str
    benchmark_rank_signal: str


class AuditedTopKJudgment(BaseModel):
    candidate_audits: list[CandidateAudit]
    winner_model_id: str
    confidence: str
    rationale: str


# ---------------------------------------------------------------------------
# Stage 1 — modified single-shot that also emits top alternatives
# ---------------------------------------------------------------------------

BENCHMARK_OBJECTIVE_BLOCK = """
Benchmark-aligned objective:
- Your goal is to predict which same-trait PGS candidate is most likely to rank
  highest in a hidden external benchmark of PGS performance for this target trait.
- Interpret "better-supported" as "more likely to rank higher in that hidden
  benchmark", not as publication polish or generic support.
- Do not optimize for publication polish, metric cleanliness, or validation N in
  isolation. Use the skill/reference guidance and the visible fields to infer
  which record is most likely to transfer to the benchmark setting.
- Still use only visible candidate fields plus the provided skill and heritability
  evidence. Do not use any trait-specific prior or disease-category shortcut.
""".strip()

H1_H5_OBJECTIVE_BLOCK = """
Benchmark-aligned H1/H5 objective:
- Primary goal: predict which same-trait PGS candidate is most likely to rank #1
  in a hidden external benchmark of PGS performance for this target trait.
- Secondary guardrail: avoid selecting a candidate that is likely to fall outside
  the benchmark top 5. When the #1 evidence is ambiguous, prefer the candidate
  with stronger top-5 safety across endpoint fidelity, validation context, clean
  PRS evidence, ancestry/sample support, and study archetype.
- Treat top-5 safety as a risk assessment, not a deterministic veto. A candidate
  with one weak field can still win if the whole record is stronger; a candidate
  with one clean metric can still lose if the rest of the record looks fragile.
- Use only visible candidate fields plus the provided skill and heritability
  evidence. Do not use any trait-specific prior or disease-category shortcut.
""".strip()

PERFORMANCE_PROXY_OBJECTIVE_BLOCK = """
Benchmark-proxy objective:
- Your goal is to predict which same-trait PGS candidate is most likely to rank
  #1 in a hidden external benchmark of PGS performance for this target trait.
- Treat endpoint fidelity as an eligibility and interpretation check. Once the
  shortlist candidates are all reasonable same-trait direct matches, do not let
  slightly cleaner label wording dominate the final choice.
- For the final #1 decision, give substantial weight to visible performance
  proxies: PRS-only AUC/R2 when present, full-model AUROC/C-index when candidates
  are otherwise comparable direct matches, effect-size strength/precision,
  validation context, and same-study or same-endpoint near-clone differences.
- Full-model metrics are noisy and can reflect covariates, but they are still
  useful benchmark-rank clues among same-trait candidates when the rest of the
  record is compatible. Do not discard them solely because they are not PRS-only.
- Conversely, do not let a single clean but tiny PRS-only metric beat a stronger
  same-trait record whose benchmark-transfer signal is stronger across multiple
  fields.
- Use only visible candidate fields plus the provided skill and heritability
  evidence. Do not use any trait-specific prior or disease-category shortcut.
""".strip()

METRIC_FIRST_OBJECTIVE_BLOCK = """
Metric-first hidden-rank objective:
- Your goal is to predict the same-trait candidate most likely to rank #1 in a
  hidden external performance benchmark. The hidden benchmark is performance
  oriented, so among plausible same-trait direct matches the decisive signal is
  expected benchmark performance, not narrative support.
- First exclude candidates that are clearly off-trait, mediator/treatment
  phenotypes, clinical-risk packages, or otherwise not direct PGS candidates.
  After that filter, choose the candidate with the strongest visible performance
  proxy profile.
- Treat PRS-only AUC/R2 as the cleanest proxy when available. Treat full-model
  AUROC/C-index, effect sizes, incremental metrics, and same-study near-clone
  differences as meaningful rank evidence when candidates are same-trait and
  otherwise comparable. Do not throw away full-model performance just because it
  is imperfect; hidden benchmark rank often tracks noisy performance proxies.
- A candidate with cleaner endpoint wording but weaker performance evidence
  should lose to a same-trait candidate whose visible record better predicts
  high external benchmark rank.
- Do not use trait-specific prior knowledge, disease-category shortcuts, PGS ID
  memorization, benchmark labels, or case-by-case rules.
""".strip()

SAME_CONTEXT_OBJECTIVE_BLOCK = """
Same-context benchmark objective:
- Your goal is to predict the same-trait candidate most likely to rank #1 in a
  hidden external PGS performance benchmark.
- First separate broad evidence conflicts from near-clone conflicts. A near-clone
  conflict means candidates share the same target endpoint framing, publication
  or study family, method family, covariate pattern, validation setting, and
  ancestry/sample context closely enough that their performance/effect fields
  are meaningfully comparable.
- When a near-clone conflict exists inside the shortlist, do not preserve upstream
  order by inertia. Use same-context performance metrics, effect sizes, validation
  metrics, and model-specific fields as strong tie-break evidence for #1.
- When candidates are not near-clones, keep the broader skill discipline:
  endpoint fidelity, PRS-only metric cleanliness, validation breadth, ancestry
  context, covariate/leakage risk, study archetype, and heritability alignment.
- Do not use trait-specific prior knowledge, disease-category shortcuts, PGS ID
  memorization, benchmark labels, or case-by-case rules.
""".strip()


def _objective_block(objective: str) -> str:
    if objective == "hidden_benchmark":
        return BENCHMARK_OBJECTIVE_BLOCK
    if objective == "hidden_benchmark_h5_guard":
        return H1_H5_OBJECTIVE_BLOCK
    if objective == "performance_proxy":
        return PERFORMANCE_PROXY_OBJECTIVE_BLOCK
    if objective == "metric_first":
        return METRIC_FIRST_OBJECTIVE_BLOCK
    if objective == "same_context":
        return SAME_CONTEXT_OBJECTIVE_BLOCK
    return ""


def _stage1_user_instruction(top_k: int, *, objective: str) -> str:
    runners_up = max(0, top_k - 1)
    if objective.startswith("hidden_benchmark"):
        text = (
            "Perform direct-match assessment only. Use the context JSON below to select "
            "the same-trait candidate most likely to rank highest in a hidden external "
            f"PGS performance benchmark AND the {runners_up} next most likely runners-up "
            "from the SAME visible candidate list. Return one JSON object with exactly "
            "the fields: outcome, best_model_id, top_alternatives, confidence, rationale.\n\n"
            f"top_alternatives must contain exactly {runners_up} PGS IDs drawn from the same "
            "visible candidate list, ranked by remaining expected hidden-benchmark rank "
            "support after best_model_id, and must not repeat best_model_id. If fewer "
            "runners-up are supportable, repeat the last supportable runner-up until the "
            "list has the required length; this preserves a stable schema while the "
            "harness deduplicates invalid repeats. If no direct-match candidate exists, "
            "set best_model_id to null and top_alternatives to []."
        )
        block = _objective_block(objective)
        return f"{text}\n\n{block}" if block else text
    text = (
        "Perform direct-match assessment only. Use the context JSON below to select the "
        f"best supported direct-match candidate AND the {runners_up} best-supported "
        "runners-up from the SAME visible candidate list. Return one JSON object with "
        "exactly the fields: outcome, best_model_id, top_alternatives, confidence, "
        "rationale.\n\n"
        f"top_alternatives must contain exactly {runners_up} PGS IDs drawn from the same "
        "visible candidate list, ranked by remaining direct-match support after "
        "best_model_id, and must not repeat best_model_id. If fewer runners-up are "
        "supportable, repeat the last supportable runner-up until the list has the "
        "required length; this preserves a stable schema while the harness deduplicates "
        "invalid repeats. If no direct-match candidate exists, set best_model_id to "
        "null and top_alternatives to []."
    )
    block = _objective_block(objective)
    return f"{text}\n\n{block}" if block else text


def _stage1_messages(context_json: str, *, top_k: int, objective: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": CO_SCIENTIST_STEP1_PROMPT},
        {
            "role": "user",
            "content": f"{_stage1_user_instruction(top_k, objective=objective)}\n\nContext:\n{context_json}",
        },
    ]


def _stage1_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_ranked_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1RankedDecision),
        },
    }


# ---------------------------------------------------------------------------
# Stage 2 — pairwise judge
# ---------------------------------------------------------------------------

PAIRWISE_JUDGE_SYSTEM_PROMPT = """# Identity & Persona
You are a strict PRS quality judge. You compare exactly two PGS Catalog candidate
records for the same target trait, and you decide which one is better-supported
on the visible record fields.

# Task
Decide the winner of a head-to-head comparison between exactly two PGS candidates
for the target trait shown in the context. Output one JSON object with the winner's
PGS ID, your confidence, and a short rationale.

# Decision Boundary
- The winner must be one of the two candidate IDs explicitly given in the context.
- You may not introduce a third candidate, propose a tie, or refuse to choose.
- Your default is to pick a winner; declare confidence "Low" if the records are
  near-tied, but still emit a winner_model_id from the two given IDs.

# Evaluation Reference Frame
Use only evidence explicitly present in the context. Compare across:
- PRS-only AUC / R2 cleanliness (full-model AUC/R2 are not comparable PRS metrics)
- endpoint fidelity to the target trait (trait_reported, trait_efo, phenotyping_reported)
- training scale, validation breadth, ancestry breadth
- covariate-leakage and packaging signals (clinical risk calculators, family-history
  packages, biomarker / treatment / mediator adjustment, horizon-conditioned
  packaging, broad EHR phenotype summaries)
- heritability ceiling alignment when the trait-specific heritability section is present

If the optional `domain_knowledge.full_document` is present, treat it as the
authoritative field-level policy source; weigh its empirical patterns against
the candidate records.

Metric discipline:
- The presence of a clean PRS-only AUC/R2 is not itself sufficient to beat the
  other candidate. A candidate with PRS-only metrics should win only when that
  metric evidence is compatible with endpoint fidelity, study design, validation
  context, ancestry/sample context, and publication/study archetype.
- Do not demote an otherwise stronger disease-focused or higher-ranked candidate
  solely because its PRS-only metric is absent while the other candidate reports
  one. Missing PRS-only metrics mean "less directly comparable", not "worse".
- In the pair payload, candidate_a is usually earlier in the upstream shortlist.
  Treat that ordering as a weak prior. Choosing candidate_b is appropriate when
  candidate_b has a clear multi-field advantage, not merely a single cleaner
  reported metric.
- Near-clone tie-break: when the two candidates share the same endpoint framing,
  publication/study family, method family, covariates, validation setting, and
  ancestry context, their reported performance metrics and effect-size fields are
  more comparable than they are across unrelated studies. In that near-clone case,
  use those same-context performance differences as a legitimate tie-break instead
  of inventing broad study-design distinctions.

Do not rank by method-name labels, publication age, "established" use, or
validation N alone unless the candidate records show why that signal matters
in this specific comparison.

# Output Requirements
Return one JSON object with exactly these fields:
{{
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}}

# Output Discipline
- winner_model_id must be one of the two candidate IDs given in the prompt.
- rationale must be grounded only in visible evidence and must reference both
  candidates (what the winner has and the loser lacks).
- Do not include extra keys.
"""


def _build_pairwise_user_message(
    *,
    target_trait: str,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    domain_knowledge: dict[str, Any],
) -> str:
    payload = {
        "target_trait": target_trait,
        "comparison": {
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "candidate_a": candidate_a_summary,
            "candidate_b": candidate_b_summary,
        },
        "domain_knowledge": domain_knowledge,
    }
    return (
        "Decide the winner of the head-to-head comparison below. winner_model_id "
        "must be exactly one of candidate_a_id or candidate_b_id.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _pairwise_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "pairwise_judgment",
            "strict": True,
            "schema": to_strict_json_schema(PairwiseJudgment),
        },
    }


TOPK_JUDGE_SYSTEM_PROMPT = """# Identity & Persona
You are a strict PRS quality judge. You compare a short ranked shortlist of PGS
Catalog candidate records for the same target trait and choose the single
best-supported direct-match candidate.

# Task
Decide the winner from the shortlist shown in the context. Output one JSON object
with the winner's PGS ID, your confidence, and a short rationale.

# Decision Boundary
- The winner must be one of the candidate IDs explicitly given in the context.
- You may not introduce another candidate, propose a tie, or refuse to choose.
- `ranked_candidate_ids` is the upstream picker order. Treat it as a weak prior:
  keep the first candidate unless another candidate has a clear multi-field
  advantage across the visible evidence.

# Evaluation Reference Frame
Use only evidence explicitly present in the context. Compare across:
- PRS-only AUC / R2 cleanliness (full-model AUC/R2 are not comparable PRS metrics)
- endpoint fidelity to the target trait (trait_reported, trait_efo, phenotyping_reported)
- training scale, validation breadth, ancestry breadth
- covariate-leakage and packaging signals (clinical risk calculators, family-history
  packages, biomarker / treatment / mediator adjustment, horizon-conditioned
  packaging, broad EHR phenotype summaries)
- heritability ceiling alignment when the trait-specific heritability section is present

If the optional `domain_knowledge.full_document` is present, treat it as the
authoritative field-level policy source; weigh its empirical patterns against
the candidate records.

Metric discipline:
- The presence of a clean PRS-only AUC/R2 is not itself sufficient to beat other
  candidates. A candidate with PRS-only metrics should win only when that metric
  evidence is compatible with endpoint fidelity, study design, validation context,
  ancestry/sample context, and publication/study archetype.
- Do not demote an otherwise stronger disease-focused or higher-ranked candidate
  solely because its PRS-only metric is absent while another candidate reports one.
  Missing PRS-only metrics mean "less directly comparable", not "worse".
- Broad high-throughput/framework candidates do not automatically beat focused
  trait-specific candidates just because they expose cleaner metric fields; decide
  from the whole record.
- Near-clone tie-break: when candidates share the same endpoint framing,
  publication/study family, method family, covariates, validation setting, and
  ancestry context, their reported performance metrics and effect-size fields are
  more comparable than they are across unrelated studies. In that near-clone case,
  use same-context performance differences as a legitimate tie-break instead of
  inventing broad study-design distinctions.

Do not rank by method-name labels, publication age, "established" use, or
validation N alone unless the candidate records show why that signal matters
in this specific comparison.

# Output Requirements
Return one JSON object with exactly these fields:
{{
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}}

# Output Discipline
- winner_model_id must be one of the candidate IDs given in the prompt.
- rationale must be grounded only in visible evidence and must compare the winner
  against the strongest runner-up.
- Do not include extra keys.
"""


def _build_topk_user_message(
    *,
    target_trait: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    domain_knowledge: dict[str, Any],
) -> str:
    payload = {
        "target_trait": target_trait,
        "ranked_candidate_ids": ranked_candidate_ids,
        "candidates": [
            candidate_summaries.get(pgs_id, {"pgs_id": pgs_id, "missing": True})
            for pgs_id in ranked_candidate_ids
        ],
        "domain_knowledge": domain_knowledge,
    }
    return (
        "Choose the single best-supported direct-match candidate from the shortlist "
        "below. winner_model_id must be exactly one of ranked_candidate_ids.\n\n"
        f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
    )


def _topk_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "topk_judgment",
            "strict": True,
            "schema": to_strict_json_schema(TopKJudgment),
        },
    }


TOPK_RANKER_SYSTEM_PROMPT = """# Identity & Persona
You are a PRS benchmark-ranking judge. You rank a short same-trait shortlist of
PGS Catalog candidate records by expected hidden external benchmark performance.

# Task
Rank all candidates in `ranked_candidate_ids` from most likely to rank #1 in the
hidden benchmark to least likely. The final recommendation will be the first ID
in your ranked_model_ids list.

# Decision Boundary
- ranked_model_ids must contain only IDs from ranked_candidate_ids.
- Include every candidate exactly once when possible.
- Do not introduce another candidate, use benchmark labels, or use trait-specific
  rules.

# Evidence Use
Use only visible candidate fields plus the provided skill and heritability
evidence. Compare endpoint fidelity, PRS-only metric cleanliness when comparable,
same-context performance/effect-size differences for near-clones, validation
breadth, ancestry/sample context, covariates, study archetype, packaging/leakage
risk, and heritability alignment.

# Ranking Discipline
- First identify the strongest plausible hidden-benchmark #1, then order the
  remaining plausible runners-up. Do not simply preserve upstream order.
- A single clean metric is insufficient by itself; require compatibility with the
  whole record.
- In true near-clone comparisons from the same measurement context, same-context
  performance/effect-size fields are legitimate tie-break evidence.
- Do not rank by publication polish, method labels, release date, or validation N
  alone.

# Output Requirements
Return exactly one JSON object:
{
  "ranked_model_ids": ["PGS000XXX", "PGS000YYY"],
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}
"""


TOPK_AUDIT_SYSTEM_PROMPT = """# Identity & Persona
You are a PRS benchmark-selection auditor. You evaluate a short same-trait
shortlist by first auditing each candidate on the same evidence dimensions, then
choosing the candidate most likely to rank #1 in a hidden external benchmark.

# Task
For each candidate, write a compact audit covering:
- endpoint_fit
- metric_signal
- validation_signal
- risk_signal
- benchmark_rank_signal
Then choose winner_model_id from the shortlist.

# Decision Boundary
- winner_model_id must be one of `ranked_candidate_ids`.
- candidate_audits must use only IDs from `ranked_candidate_ids`.
- Do not introduce another candidate, use benchmark labels, trait-specific priors,
  disease-category shortcuts, or case-by-case rules.

# Audit Discipline
- Compare all candidates on the same dimensions before choosing.
- A clean PRS-only AUC/R2 is useful only when compatible with endpoint fidelity,
  study design, validation context, ancestry/sample context, and study archetype.
- Full-model metrics are weak across unrelated studies, but can be tie-break
  evidence among near-clones with the same endpoint, study family, covariates,
  validation setting, and ancestry context.
- Do not overvalue publication polish, method labels, release date, or validation
  N alone.
- The upstream shortlist order is a weak prior only; override it when the audit
  shows stronger hidden-benchmark rank signal elsewhere.

# Output Requirements
Return exactly one JSON object with:
{
  "candidate_audits": [
    {
      "pgs_id": "PGS000XXX",
      "endpoint_fit": "...",
      "metric_signal": "...",
      "validation_signal": "...",
      "risk_signal": "...",
      "benchmark_rank_signal": "..."
    }
  ],
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}
"""


FULLPOOL_JUDGE_SYSTEM_PROMPT = """# Identity & Persona
You are a strict PRS benchmark-selection agent. You inspect the full visible
candidate pool for one target trait and choose the single PGS Catalog candidate
most likely to rank #1 in a hidden external same-trait performance benchmark.

# Task
Choose winner_model_id from `ranked_candidate_ids`. The list may contain many
candidates. The input order is only a transport order, not an evidence signal.

# Decision Boundary
- winner_model_id must be one of `ranked_candidate_ids`.
- Do not introduce another candidate, use benchmark labels, use PGS ID memory,
  use trait-specific rules, or use disease-category shortcuts.
- Use only visible candidate fields plus the provided skill and heritability
  evidence.

# Selection Procedure
1. Identify the plausible direct-match candidate cluster for the target trait
   using trait_reported, trait_efo, and phenotyping_reported. Exclude only
   clearly off-trait, mediator/treatment, clinical-risk-package, or non-PRS
   candidates.
2. Within the plausible same-trait cluster, choose the candidate whose visible
   record best predicts #1 hidden benchmark performance. Use endpoint fidelity,
   PRS-only metrics, full-model metrics when otherwise comparable, effect sizes,
   validation context, ancestry/sample context, covariates, method/study
   archetype, packaging/leakage risk, and heritability alignment.
3. For near-clones from the same endpoint/study/method context, treat
   same-context performance and effect-size differences as strong tie-break
   evidence.
4. Avoid narrative overfit: a disease-focused publication, a cleaner label, a
   larger validation N, or a clean but tiny PRS-only metric is not enough by
   itself. Pick the whole-record candidate most likely to rank #1.

# Output Requirements
Return one JSON object with exactly these fields:
{{
  "winner_model_id": "PGS000XXX",
  "confidence": "High | Moderate | Low",
  "rationale": "..."
}}

# Output Discipline
- winner_model_id must be one of the candidate IDs in `ranked_candidate_ids`.
- rationale must name the strongest runner-up and explain why the winner is more
  likely to rank #1 in the hidden benchmark.
- Do not include extra keys.
"""


def _topk_audit_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "audited_topk_judgment",
            "strict": True,
            "schema": to_strict_json_schema(AuditedTopKJudgment),
        },
    }


def _run_stage2_for_topk_audit(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    domain_knowledge: dict[str, Any],
    objective: str,
) -> dict[str, Any]:
    user_message = _build_topk_user_message(
        target_trait=ontology,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        domain_knowledge=domain_knowledge,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{TOPK_AUDIT_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else TOPK_AUDIT_SYSTEM_PROMPT
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_audit_response_format(),
        )
        verdict = AuditedTopKJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in set(ranked_candidate_ids):
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "candidate_audits": [a.model_dump() for a in verdict.candidate_audits],
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in shortlist",
            }
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "candidate_audits": [a.model_dump() for a in verdict.candidate_audits],
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "candidate_audits": [],
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"TopKAudit Stage2 {type(exc).__name__}: {exc}",
        }


def _topk_ranking_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "topk_ranking_judgment",
            "strict": True,
            "schema": to_strict_json_schema(TopKRankingJudgment),
        },
    }


def _run_stage2_for_topk_ranker(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    domain_knowledge: dict[str, Any],
    objective: str,
) -> dict[str, Any]:
    user_message = _build_topk_user_message(
        target_trait=ontology,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        domain_knowledge=domain_knowledge,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{TOPK_RANKER_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else TOPK_RANKER_SYSTEM_PROMPT
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_ranking_response_format(),
        )
        verdict = TopKRankingJudgment.model_validate_json(content)
        valid_ids: list[str] = []
        allowed = set(ranked_candidate_ids)
        for pgs_id in verdict.ranked_model_ids:
            pgs_id = str(pgs_id).strip()
            if pgs_id in allowed and pgs_id not in valid_ids:
                valid_ids.append(pgs_id)
        for pgs_id in ranked_candidate_ids:
            if pgs_id not in valid_ids:
                valid_ids.append(pgs_id)
        winner = valid_ids[0] if valid_ids else None
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "ranked_model_ids": valid_ids,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None if winner else "empty ranked_model_ids",
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "ranked_model_ids": [],
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"TopKRanker Stage2 {type(exc).__name__}: {exc}",
        }


def _run_stage2_for_topk(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    domain_knowledge: dict[str, Any],
    objective: str,
) -> dict[str, Any]:
    user_message = _build_topk_user_message(
        target_trait=ontology,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        domain_knowledge=domain_knowledge,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{TOPK_JUDGE_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else TOPK_JUDGE_SYSTEM_PROMPT
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_response_format(),
        )
        verdict = TopKJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in set(ranked_candidate_ids):
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in shortlist",
            }
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"TopK Stage2 {type(exc).__name__}: {exc}",
        }


def _run_stage2_for_fullpool(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    domain_knowledge: dict[str, Any],
    objective: str,
) -> dict[str, Any]:
    user_message = _build_topk_user_message(
        target_trait=ontology,
        ranked_candidate_ids=ranked_candidate_ids,
        candidate_summaries=candidate_summaries,
        domain_knowledge=domain_knowledge,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{FULLPOOL_JUDGE_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else FULLPOOL_JUDGE_SYSTEM_PROMPT
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_topk_response_format(),
        )
        verdict = TopKJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in set(ranked_candidate_ids):
            return {
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidate_ids,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in full pool",
            }
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "ranked_candidate_ids": ranked_candidate_ids,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"FullPool Stage2 {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _llm_call(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    response_format: dict[str, Any],
) -> str:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
    }
    # Match disease_workflow defaults from gpt-5.2 config (temperature=0, seed=42)
    body["temperature"] = 0
    body["seed"] = 42
    response = client.chat.completions.create(**body)
    choice = response.choices[0]
    content = choice.message.content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts).strip()
    return (content or "").strip()


def _run_stage1_for_request(
    client: OpenAI,
    model: str,
    request: dict[str, Any],
    top_k: int,
    objective: str,
) -> dict[str, Any]:
    """Execute Stage 1 for a single batch-request entry. Reuses the prepared
    context_json from the existing manifest (no re-fetch of candidates).
    """
    custom_id = request["custom_id"]
    body = request["request"]["body"]
    user_messages = body["messages"]
    # The original user message is index 1; replace its instruction-prefix with
    # the ranked-decision instruction while preserving the Context: payload.
    original_user = user_messages[1]["content"]
    # Find "Context:" literal to slice out the JSON payload.
    marker = "Context:\n"
    idx = original_user.find(marker)
    if idx < 0:
        raise RuntimeError(f"{custom_id}: could not locate Context: marker in original user message")
    context_json = original_user[idx + len(marker):]
    messages = _stage1_messages(context_json, top_k=top_k, objective=objective)
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_stage1_response_format(),
        )
        decision = Step1RankedDecision.model_validate_json(content)
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "decision": decision.model_dump(),
            "context_json": context_json,
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "ontology": request["ontology"],
            "decision": None,
            "context_json": None,
            "error": f"Stage1 {type(exc).__name__}: {exc}",
        }


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """ontology -> { pgs_id -> candidate_summary }"""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for row in disease_metadata:
        ontology = row["ontology"]
        out[ontology] = {}
        for summary in row.get("candidate_models_visible_to_llm") or []:
            pgs_id = summary.get("pgs_id") or summary.get("id")
            if pgs_id:
                out[ontology][pgs_id] = summary
    return out


def _run_stage2_for_pair(
    client: OpenAI,
    model: str,
    *,
    ontology: str,
    candidate_a_id: str,
    candidate_b_id: str,
    candidate_a_summary: dict[str, Any],
    candidate_b_summary: dict[str, Any],
    domain_knowledge: dict[str, Any],
    objective: str,
) -> dict[str, Any]:
    user_message = _build_pairwise_user_message(
        target_trait=ontology,
        candidate_a_id=candidate_a_id,
        candidate_b_id=candidate_b_id,
        candidate_a_summary=candidate_a_summary,
        candidate_b_summary=candidate_b_summary,
        domain_knowledge=domain_knowledge,
    )
    objective_block = _objective_block(objective)
    system_prompt = (
        f"{PAIRWISE_JUDGE_SYSTEM_PROMPT}\n\n{objective_block}"
        if objective_block else PAIRWISE_JUDGE_SYSTEM_PROMPT
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    try:
        content = _llm_call(
            client,
            model=model,
            messages=messages,
            response_format=_pairwise_response_format(),
        )
        verdict = PairwiseJudgment.model_validate_json(content)
        winner = verdict.winner_model_id.strip()
        if winner not in {candidate_a_id, candidate_b_id}:
            return {
                "ontology": ontology,
                "candidate_a_id": candidate_a_id,
                "candidate_b_id": candidate_b_id,
                "winner_model_id": None,
                "confidence": verdict.confidence,
                "rationale": verdict.rationale,
                "error": f"winner '{winner}' not in pair",
            }
        return {
            "ontology": ontology,
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "winner_model_id": winner,
            "confidence": verdict.confidence,
            "rationale": verdict.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "candidate_a_id": candidate_a_id,
            "candidate_b_id": candidate_b_id,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"Stage2 {type(exc).__name__}: {exc}",
        }


def _select_ranked_candidates(
    *,
    best_model_id: Optional[str],
    top_alternatives: list[str],
    candidate_id_set: set[str],
    top_k: int,
) -> list[str]:
    """Return up to top_k distinct, candidate-set-valid PGS IDs in Stage 1 order
    (deduplicated, preserving first occurrence)."""
    seen: list[str] = []
    for cand in [best_model_id, *list(top_alternatives or [])]:
        if not cand:
            continue
        cand = str(cand).strip()
        if cand and cand in candidate_id_set and cand not in seen:
            seen.append(cand)
        if len(seen) == top_k:
            break
    return seen


def _aggregate_borda(
    ranked_candidates: list[str],
    pairwise_results: list[dict[str, Any]],
) -> tuple[Optional[str], dict[str, int]]:
    """Win-count aggregation among Stage 1 ranked candidates from pairwise results.

    scores: dict pgs_id -> wins (each pairwise win = 1). Tiebreak: Stage 1 order
    (Stage 1 best_model_id wins ties)."""
    scores: dict[str, int] = {pgs_id: 0 for pgs_id in ranked_candidates}
    for result in pairwise_results:
        winner = result.get("winner_model_id")
        if winner and winner in scores:
            scores[winner] = scores.get(winner, 0) + 1
    if not scores:
        return None, scores
    # Sort by (wins desc, top3 index asc)
    order = {pgs_id: idx for idx, pgs_id in enumerate(ranked_candidates)}
    ranked = sorted(scores.keys(), key=lambda pid: (-scores[pid], order.get(pid, len(ranked_candidates))))
    return ranked[0], scores


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _run_pipeline(
    *,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
    top_k: int,
    evaluator: str,
    objective: str,
    stage1_objective: str,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = manifest["requests"]
    print(f"Loaded manifest: {manifest_path} ({len(requests)} requests across "
          f"{len(manifest['disease_metadata'])} ontologies)")

    client = _client()

    # Stage 1
    print(f"\n=== Stage 1 (ranked decision) — {len(requests)} requests, workers={workers} ===")
    stage1_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_run_stage1_for_request, client, model, request, top_k, stage1_objective): request
            for request in requests
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            stage1_results[res["custom_id"]] = res
            done += 1
            status = "ok" if res["error"] is None else "ERR"
            print(f"  [stage1 {done}/{len(requests)}] {status} {res['ontology']}")
    print(f"Stage 1 elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pairwise_rerank_stage1_results.json").write_text(
        json.dumps(list(stage1_results.values()), indent=2), encoding="utf-8"
    )

    # Build pairwise jobs from Stage 1 outputs
    candidate_summary_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    domain_by_ontology: dict[str, dict[str, Any]] = {}
    for request in requests:
        ontology = request["ontology"]
        if ontology in domain_by_ontology:
            continue
        # Extract domain_knowledge from the original Stage 1 context JSON (so the
        # judge sees the same SKILL.md + heritability evidence as the picker).
        body = request["request"]["body"]
        original_user = body["messages"][1]["content"]
        marker = "Context:\n"
        idx = original_user.find(marker)
        if idx >= 0:
            try:
                ctx = json.loads(original_user[idx + len(marker):])
                domain_by_ontology[ontology] = ctx.get("domain_knowledge") or {}
            except Exception:
                domain_by_ontology[ontology] = {}
        else:
            domain_by_ontology[ontology] = {}

    pairwise_jobs: list[dict[str, Any]] = []
    topk_jobs: list[dict[str, Any]] = []
    ranked_candidates_by_ontology: dict[str, list[str]] = {}
    stage1_decision_by_ontology: dict[str, dict[str, Any]] = {}
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        candidate_id_set = set(request["candidate_model_ids"])
        s1 = stage1_results.get(custom_id) or {}
        decision = s1.get("decision") or {}
        stage1_decision_by_ontology[ontology] = decision
        ranked_candidates = _select_ranked_candidates(
            best_model_id=decision.get("best_model_id"),
            top_alternatives=decision.get("top_alternatives") or [],
            candidate_id_set=candidate_id_set,
            top_k=top_k,
        )
        ranked_candidates_by_ontology[ontology] = ranked_candidates
        if evaluator == "fullpool_judge":
            ranked_candidates = list(request["candidate_model_ids"])
            ranked_candidates_by_ontology[ontology] = ranked_candidates
        if len(ranked_candidates) < 2:
            continue
        if evaluator == "pairwise":
            for i in range(len(ranked_candidates)):
                for j in range(i + 1, len(ranked_candidates)):
                    pairwise_jobs.append({
                        "ontology": ontology,
                        "candidate_a_id": ranked_candidates[i],
                        "candidate_b_id": ranked_candidates[j],
                    })
        elif evaluator in {"topk_judge", "topk_ranker", "topk_audit", "fullpool_judge"}:
            topk_jobs.append({
                "ontology": ontology,
                "ranked_candidate_ids": ranked_candidates,
            })
        else:
            raise ValueError(f"Unknown evaluator: {evaluator}")

    pairwise_results: list[dict[str, Any]] = []
    topk_results: list[dict[str, Any]] = []
    t0 = time.time()

    def _run_one_pair(job: dict[str, Any]) -> dict[str, Any]:
        ontology = job["ontology"]
        a_id = job["candidate_a_id"]
        b_id = job["candidate_b_id"]
        cand_summaries = candidate_summary_by_ontology.get(ontology, {})
        return _run_stage2_for_pair(
            client,
            model,
            ontology=ontology,
            candidate_a_id=a_id,
            candidate_b_id=b_id,
            candidate_a_summary=cand_summaries.get(a_id, {"pgs_id": a_id, "missing": True}),
            candidate_b_summary=cand_summaries.get(b_id, {"pgs_id": b_id, "missing": True}),
            domain_knowledge=domain_by_ontology.get(ontology, {}),
            objective=objective,
        )

    def _run_one_topk(job: dict[str, Any]) -> dict[str, Any]:
        ontology = job["ontology"]
        kwargs = {
            "client": client,
            "model": model,
            "ontology": ontology,
            "ranked_candidate_ids": job["ranked_candidate_ids"],
            "candidate_summaries": candidate_summary_by_ontology.get(ontology, {}),
            "domain_knowledge": domain_by_ontology.get(ontology, {}),
            "objective": objective,
        }
        if evaluator == "topk_ranker":
            return _run_stage2_for_topk_ranker(**kwargs)
        if evaluator == "topk_audit":
            return _run_stage2_for_topk_audit(**kwargs)
        if evaluator == "fullpool_judge":
            return _run_stage2_for_fullpool(**kwargs)
        return _run_stage2_for_topk(**kwargs)

    if evaluator == "pairwise":
        print(f"\n=== Stage 2 (pairwise) — {len(pairwise_jobs)} pair calls, workers={workers} ===")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_one_pair, job): job for job in pairwise_jobs}
            done = 0
            for future in as_completed(futures):
                res = future.result()
                pairwise_results.append(res)
                done += 1
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage2 {done}/{len(pairwise_jobs)}] {status} {res['ontology']} "
                      f"{res['candidate_a_id']} vs {res['candidate_b_id']} -> {res.get('winner_model_id')}")
    else:
        label = {
            "topk_ranker": "top-k ranker",
            "topk_audit": "top-k audit judge",
            "fullpool_judge": "full-pool judge",
        }.get(evaluator, "top-k judge")
        print(f"\n=== Stage 2 ({label}) — {len(topk_jobs)} shortlist calls, workers={workers} ===")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_one_topk, job): job for job in topk_jobs}
            done = 0
            for future in as_completed(futures):
                res = future.result()
                topk_results.append(res)
                done += 1
                status = "ok" if res["error"] is None else "ERR"
                print(f"  [stage2 {done}/{len(topk_jobs)}] {status} {res['ontology']} "
                      f"-> {res.get('winner_model_id')}")
    print(f"Stage 2 elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pairwise_rerank_stage2_results.json").write_text(
        json.dumps(pairwise_results if evaluator == "pairwise" else topk_results, indent=2),
        encoding="utf-8"
    )

    # Aggregate via Borda
    pairwise_by_ontology: dict[str, list[dict[str, Any]]] = {}
    for res in pairwise_results:
        pairwise_by_ontology.setdefault(res["ontology"], []).append(res)

    final_pick_by_ontology: dict[str, Optional[str]] = {}
    borda_by_ontology: dict[str, dict[str, int]] = {}
    topk_by_ontology = {res["ontology"]: res for res in topk_results}
    for ontology, ranked_candidates in ranked_candidates_by_ontology.items():
        if len(ranked_candidates) < 2:
            stage1_pick = stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            final_pick_by_ontology[ontology] = stage1_pick
            borda_by_ontology[ontology] = {}
            continue
        if evaluator == "pairwise":
            winner, scores = _aggregate_borda(ranked_candidates, pairwise_by_ontology.get(ontology, []))
            final_pick_by_ontology[ontology] = winner
            borda_by_ontology[ontology] = scores
        else:
            topk_result = topk_by_ontology.get(ontology) or {}
            final_pick_by_ontology[ontology] = topk_result.get("winner_model_id") or ranked_candidates[0]
            borda_by_ontology[ontology] = {}

    # Build per-disease rows in the existing summary format. We need to feed
    # _build_summary_and_results-compatible parsed_outputs that produce a single
    # "trial" (trial=1) carrying the FINAL Borda-winner pick.
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in requests:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        s1 = stage1_results.get(custom_id) or {}
        if s1.get("error"):
            error_map[custom_id] = s1["error"]
            continue
        final_pick = final_pick_by_ontology.get(ontology)
        decision = s1.get("decision") or {}
        # Reuse Stage 1's outcome / confidence labels if its best is the final pick;
        # otherwise mark as Borda-revised with the same outcome but Moderate confidence.
        outcome = decision.get("outcome") or "DIRECT_HIGH_QUALITY"
        confidence = decision.get("confidence") or "Moderate"
        rationale = decision.get("rationale") or ""
        if final_pick != decision.get("best_model_id"):
            confidence = "Moderate"
            rationale = (rationale + " | Borda re-rank promoted runner-up to primary.").strip()
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": outcome,
                "best_model_id": final_pick,
                "confidence": confidence,
                "rationale": rationale,
            }],
            "error": None,
        }

    # Wire the summary builder. To prevent NameError on without_domain global paths
    # we set them explicitly to point at our run directory.
    without_domain.RESULTS_JSON = output_run_dir / "experiment_pairwise_rerank_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_pairwise_rerank_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_pairwise_rerank_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_pairwise_rerank_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_pairwise_rerank_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_pairwise_rerank_batch_errors.jsonl"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
    # Configure benchmark sources to match the manifest
    union_csv = manifest.get("union_csv")
    ground_truth_dir = manifest.get("ground_truth_dir")
    without_domain._configure_benchmark_sources(
        union_csv=union_csv,
        ground_truth_dir=ground_truth_dir,
    )

    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["execution_mode"] = "pairwise_rerank_chat_completions"
    summary["pairwise_rerank"] = {
        "evaluator": evaluator,
        "objective": objective,
        "stage1_objective": stage1_objective,
        "stage1_count": len(stage1_results),
        "stage2_count": len(pairwise_results) if evaluator == "pairwise" else len(topk_results),
        "top_k": top_k,
        "borda_revised_count": sum(
            1
            for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
            if (
                len(ranked_candidates) >= 2
                and final_pick_by_ontology.get(ontology) is not None
                and final_pick_by_ontology.get(ontology)
                    != stage1_decision_by_ontology.get(ontology, {}).get("best_model_id")
            )
        ),
        "ontologies_with_invalid_ranked_alternatives": sum(
            1 for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
            if len(ranked_candidates) < 2
        ),
        "borda_scores_by_ontology": borda_by_ontology,
        "ranked_candidates_by_ontology": ranked_candidates_by_ontology,
        "top3_by_ontology": {
            ontology: ranked_candidates[:3]
            for ontology, ranked_candidates in ranked_candidates_by_ontology.items()
        },
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)

    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Pairwise reranking on top-3 (Round 1)")
    parser.add_argument("--manifest", type=str, required=True,
                        help="Path to an existing iterD-style batch manifest JSON")
    parser.add_argument("--run-tag", type=str, required=True,
                        help="Run tag suffix appended to the output run directory name")
    parser.add_argument("--model", type=str, default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=3,
                        help="Number of Stage 1 ranked candidates to feed into pairwise tournament.")
    parser.add_argument("--evaluator", choices=["pairwise", "topk_judge", "topk_ranker", "topk_audit", "fullpool_judge"], default="pairwise",
                        help="Stage 2 evaluator style: all-pairs tournament or one holistic shortlist judge.")
    parser.add_argument("--objective", choices=["support", "hidden_benchmark", "hidden_benchmark_h5_guard", "performance_proxy", "metric_first", "same_context"], default="support",
                        help="Selection objective framing. hidden_benchmark aligns the judge to predict held-out rank.")
    parser.add_argument("--stage1-objective", choices=["support", "hidden_benchmark", "hidden_benchmark_h5_guard", "performance_proxy", "metric_first", "same_context"],
                        default="support",
                        help="Stage 1 shortlist objective. Keep support for the Round33 structure.")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"pairwise-rerank-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _run_pipeline(
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
        top_k=args.top_k,
        evaluator=args.evaluator,
        objective=args.objective,
        stage1_objective=args.stage1_objective,
    )
    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, "
              f"accuracy={v.get('accuracy')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
