"""Batch genetic-correlation tool — pure LLM reasoning, candidate-shortlist mode.

Runs **2 LLM calls per target** regardless of candidate count: one
evidence-recall call enumerates everything the LLM knows about the target
paired with each candidate; one self-verify call produces all per-candidate
structured estimates. Cost scales linearly with target count, not with
target × candidates.

Per-candidate output dict populates the EvidenceRegistry's `gc` field via
the harness and is consumed by Judge / Critic:

    {
        "rg": float,
        "p_value": float | None,
        "z": float | None,
        "n_snps": int | None,
        "source": "llm_batch_evidence",
        "pair_status": "published_rg" | "inferred_shared_pathway" |
                       "inferred_comorbidity" | "no_evidence",
        "confidence": "High" | "Moderate" | "Low",
        "citations": [...],
        "rationale": str,
        "shared_pathways": [...],
        "comorbidity_signals": [...],
        "target_label": str,
        "candidate_label": str,
    }

GeneAgent-style self-verification preserved: the verify step downgrades
to confidence="Low" when the recall step's citations are uncertain.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any, Literal, Optional

from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from pydantic import BaseModel, Field

from src.server.core.llm_config import get_llm

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1 — batch evidence recall
# ---------------------------------------------------------------------------

_BATCH_RECALL_PROMPT = """\
You are a quantitative genetics domain expert. Recall what you know
about the genetic correlation between ONE target trait and EACH of a
list of candidate traits — in a single structured response.

# Inputs
- target_trait: the phenotype of interest
- candidates: a list of {bundle_id, candidate_label} pairs

# What to produce, PER candidate
For every candidate, produce one CandidateEvidenceRecall entry with:
- bundle_id (echo input verbatim)
- candidate_label (echo input verbatim)
- published_rg_estimates: up to 3 entries, each tied to a specific
  recalled study (not generic impressions). Fields per entry:
    study_citation (author et al., year, journal),
    method (LDSC, HDL, GREML, other),
    rg_value (float in [-1.0, 1.0]),
    p_value (if recalled),
    cohort_or_consortium (UKBB, PGC, etc.),
    confidence_self_rating ({High, Moderate, Low}).
- shared_pathways: up to 5 biological pathways / loci / mechanisms
  known to be pleiotropic for this (target, candidate) pair.
- comorbidity_signals: up to 3 epidemiological comorbidity relationships
  relevant to shared polygenic architecture.
- recall_completeness: one of {extensive, moderate, sparse, none}.

# Hard rules
- NEVER fabricate a study citation. If you cannot anchor an rg value
  to a specific paper, DO NOT list it under published_rg_estimates.
- Confidence ratings MUST be honest. Mark Low when uncertain.
- Each candidate's recall is INDEPENDENT — do not let pleiotropy
  between candidates inflate the target↔candidate evidence.
- No numeric scoring formulas, no priority tiers.
- Echo bundle_id and candidate_label EXACTLY as given.
"""


class _PublishedRgEstimate(BaseModel):
    study_citation: str
    method: str = ""
    rg_value: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    p_value: Optional[float] = None
    cohort_or_consortium: str = ""
    confidence_self_rating: Literal["High", "Moderate", "Low"] = "Low"


class _CandidateEvidenceRecall(BaseModel):
    bundle_id: str
    candidate_label: str
    published_rg_estimates: list[_PublishedRgEstimate] = Field(default_factory=list)
    shared_pathways: list[str] = Field(default_factory=list)
    comorbidity_signals: list[str] = Field(default_factory=list)
    recall_completeness: Literal["extensive", "moderate", "sparse", "none"] = "none"


class _GCBatchEvidenceRecall(BaseModel):
    target_trait: str
    candidates: list[_CandidateEvidenceRecall] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Step 2 — batch self-verified estimate
# ---------------------------------------------------------------------------

_BATCH_VERIFY_PROMPT = """\
You are the self-verification layer for a batch genetic-correlation
estimate. A previous LLM step recalled all evidence it knew about each
(target, candidate) pair. You now produce final structured estimates
for EVERY candidate.

# Inputs
- target_trait
- candidates: list of CandidateEvidenceRecall (the recall output)

# What to produce, per candidate (CandidateGCEstimate)
- bundle_id, candidate_label: echo from recall.
- rg: point estimate of the genetic correlation, float in [-1.0, 1.0].
- p_value: best-estimate statistical significance for rg. Null when only
  inferring from pathways / comorbidity with NO cited study.
- z: only set when converting a published z-score.
- n_snps: only set when a recalled study reported it.
- pair_status: one of {published_rg / inferred_shared_pathway /
  inferred_comorbidity / no_evidence}.
- confidence: {High / Moderate / Low}.
- citations: the recall-step citations you actually relied on.
- rationale: 1-2 sentences explaining the per-candidate number.
- shared_pathways, comorbidity_signals: pass through from recall (top 3 each).

# Hard rules
- NEVER pass through a citation that recall rated "Low" as if it were
  solid evidence. Downgrade confidence accordingly.
- If recall_completeness is "none", set pair_status = "no_evidence",
  rg = 0.0, confidence = "Low". Do not guess non-zero rg.
- Each candidate is independent. Do not let one candidate's strong rg
  inflate another's.
- No numeric scoring formulas, no priority tiers.

# Comparative rationale (optional, free text)
After per-candidate estimates, write 2-3 sentences comparing
candidates: which candidates have the strongest cross-trait evidence
relative to the target, and why. This is advisory for downstream
ranking; it does NOT change the per-candidate rg numbers above.
"""


class _CandidateGCEstimate(BaseModel):
    bundle_id: str
    candidate_label: str
    rg: float = Field(ge=-1.0, le=1.0)
    p_value: Optional[float] = None
    z: Optional[float] = None
    n_snps: Optional[int] = None
    pair_status: Literal[
        "published_rg",
        "inferred_shared_pathway",
        "inferred_comorbidity",
        "no_evidence",
    ] = "no_evidence"
    confidence: Literal["High", "Moderate", "Low"] = "Low"
    citations: list[str] = Field(default_factory=list)
    rationale: str = ""
    shared_pathways: list[str] = Field(default_factory=list)
    comorbidity_signals: list[str] = Field(default_factory=list)


class _GCBatchEstimate(BaseModel):
    estimates: list[_CandidateGCEstimate] = Field(default_factory=list)
    comparative_rationale: str = ""


# ---------------------------------------------------------------------------
# Public output type
# ---------------------------------------------------------------------------


class GCCandidateEstimate(BaseModel):
    """One candidate's final GC estimate (per-bundle rg / p-value / confidence)."""

    bundle_id: str
    candidate_label: str
    rg: float = Field(ge=-1.0, le=1.0)
    p_value: Optional[float] = None
    z: Optional[float] = None
    n_snps: Optional[int] = None
    source: Literal["llm_batch_evidence"] = "llm_batch_evidence"
    pair_status: Literal[
        "published_rg",
        "inferred_shared_pathway",
        "inferred_comorbidity",
        "no_evidence",
    ] = "no_evidence"
    confidence: Literal["High", "Moderate", "Low"] = "Low"
    citations: list[str] = Field(default_factory=list)
    rationale: str = ""
    shared_pathways: list[str] = Field(default_factory=list)
    comorbidity_signals: list[str] = Field(default_factory=list)
    target_label: str = ""

    def as_registry_payload(self) -> dict[str, Any]:
        """Dict shape compatible with EvidenceRegistry.set_gc."""
        return self.model_dump()


class GCBatchResult(BaseModel):
    target_label: str
    estimates: list[GCCandidateEstimate] = Field(default_factory=list)
    comparative_rationale: str = ""
    n_candidates_total: int = 0
    n_estimated: int = 0
    skipped_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Chain builders
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _recall_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=_BATCH_RECALL_PROMPT),
            HumanMessagePromptTemplate.from_template("{context_json}"),
        ]
    )
    return prompt | llm.with_structured_output(
        _GCBatchEvidenceRecall, method="function_calling"
    )


@lru_cache(maxsize=1)
def _verify_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=_BATCH_VERIFY_PROMPT),
            HumanMessagePromptTemplate.from_template("{context_json}"),
        ]
    )
    return prompt | llm.with_structured_output(
        _GCBatchEstimate, method="function_calling"
    )


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def genetic_correlation_batch_estimator(
    *,
    target_label: str,
    target_aliases: list[str] | None = None,
    candidates: list[dict[str, Any]],
) -> GCBatchResult:
    """Estimate genetic correlation for `target` paired with each of
    `candidates`, in a SINGLE batched 2-step LLM pipeline.

    Args:
        target_label: canonical label of the target trait.
        target_aliases: optional aliases (truncated to 6 in the request).
        candidates: list of dicts each with at minimum
            {"bundle_id": str, "candidate_label": str}. Optional keys
            (e.g. aliases) are tolerated and passed through.

    Returns:
        GCBatchResult — typed, never raises. On degenerate inputs or
        LLM failure, returns an empty estimates list with `skipped_reason`
        populated so callers can audit.
    """
    target_label = str(target_label or "").strip()
    if not target_label:
        return GCBatchResult(
            target_label="", skipped_reason="empty_target",
        )
    candidates = [c for c in (candidates or []) if c.get("bundle_id") and c.get("candidate_label")]
    if not candidates:
        return GCBatchResult(
            target_label=target_label, skipped_reason="empty_candidates",
        )

    recall_ctx = {
        "target_trait": target_label,
        "target_aliases": list(target_aliases or [])[:6],
        "candidates": [
            {"bundle_id": c["bundle_id"], "candidate_label": c["candidate_label"]}
            for c in candidates
        ],
    }

    try:
        recall: _GCBatchEvidenceRecall = _recall_chain().invoke(
            {"context_json": json.dumps(recall_ctx, ensure_ascii=False)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("GC batch recall failed: %s", exc)
        return GCBatchResult(
            target_label=target_label,
            n_candidates_total=len(candidates),
            skipped_reason=f"recall_error:{exc}",
        )

    verify_ctx = {
        "target_trait": target_label,
        "candidates": [c.model_dump() for c in recall.candidates],
    }
    try:
        verified: _GCBatchEstimate = _verify_chain().invoke(
            {"context_json": json.dumps(verify_ctx, ensure_ascii=False)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("GC batch verify failed: %s", exc)
        return GCBatchResult(
            target_label=target_label,
            n_candidates_total=len(candidates),
            skipped_reason=f"verify_error:{exc}",
        )

    # Map the verify output back to the public schema, attaching target_label
    # for downstream consumers, and filter to candidates the LLM actually
    # echoed (drop hallucinated bundle_ids).
    valid_ids = {c["bundle_id"] for c in candidates}
    estimates: list[GCCandidateEstimate] = []
    for est in verified.estimates:
        if est.bundle_id not in valid_ids:
            continue
        estimates.append(
            GCCandidateEstimate(
                bundle_id=est.bundle_id,
                candidate_label=est.candidate_label,
                rg=est.rg,
                p_value=est.p_value,
                z=est.z,
                n_snps=est.n_snps,
                pair_status=est.pair_status,
                confidence=est.confidence,
                citations=est.citations,
                rationale=est.rationale,
                shared_pathways=est.shared_pathways[:3],
                comorbidity_signals=est.comorbidity_signals[:3],
                target_label=target_label,
            )
        )

    return GCBatchResult(
        target_label=target_label,
        estimates=estimates,
        comparative_rationale=verified.comparative_rationale,
        n_candidates_total=len(candidates),
        n_estimated=len(estimates),
        skipped_reason=None,
    )
