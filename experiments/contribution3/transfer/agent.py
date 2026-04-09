from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from thefuzz import fuzz

from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    TraitBundle,
    is_self_like_bundle,
    normalize_text,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    CrossTraitMatchDecision,
    FINALIZE_TRANSFER_DECISION_PROMPT,
    TOOL_CALLING_TRANSFER_SYSTEM_PROMPT,
)
from experiments.contribution3.transfer.tools import CrossTraitToolbox
from src.server.core.llm_config import get_llm


CONDITION_TOOLS: dict[str, list[str]] = {
    "gpt-only": [],
    "dossier-only": [],
    "gc-only": ["cross_trait_genetic_correlation"],
    "gc-h2": ["cross_trait_genetic_correlation", "cross_trait_heritability"],
    "all-tools": [
        "cross_trait_genetic_correlation",
        "cross_trait_heritability",
        "cross_trait_open_targets",
    ],
}

LOW_FIDELITY_PROXY_PHRASES = (
    "aspirin use",
    "family history",
    "educational attainment",
    "age at first birth",
    "cigarettes per day",
    "intelligence",
    "physical activity measurement",
    "blood protein amount",
    "c reactive protein measurement",
    "hba1c measurement",
    "neuroimaging measurement",
    "grey matter volume",
    "brain volume",
    "smoking status measurement",
    "self reported trait",
    "health trait",
    "age at first sexual intercourse measurement",
)
LOW_FIDELITY_PROXY_EXACT = {
    "disease",
    "respiratory system disease",
    "endocrine system disease",
    "mental or behavioural disorder",
    "overnutrition",
}
INFORMATIVE_TOKEN_STOPWORDS = {
    "disease",
    "disorder",
    "syndrome",
    "trait",
    "measurement",
    "use",
    "history",
    "family",
    "status",
    "level",
    "count",
    "index",
    "ratio",
    "system",
    "related",
    "without",
    "with",
    "allied",
}


def _target_texts(dossier: CandidateBundleDossier) -> list[str]:
    return [dossier.target.target_label, *dossier.target.aliases]


def _plain_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _target_text_blob(dossier: CandidateBundleDossier) -> str:
    return normalize_text(" ".join(_target_texts(dossier)))


def _target_raw_blob(dossier: CandidateBundleDossier) -> str:
    return _plain_text(" ".join(_target_texts(dossier)))


def _bundle_texts(bundle: TraitBundle) -> list[str]:
    return [bundle.canonical_label, *bundle.aliases]


def _bundle_text_blob(bundle: TraitBundle) -> str:
    return normalize_text(" ".join(_bundle_texts(bundle)))


def _bundle_raw_blob(bundle: TraitBundle) -> str:
    return _plain_text(" ".join(_bundle_texts(bundle)))


def _target_has_phrase(dossier: CandidateBundleDossier, *phrases: str) -> bool:
    blob = _target_text_blob(dossier)
    raw_blob = _target_raw_blob(dossier)
    return any(phrase in blob or phrase in raw_blob for phrase in phrases)


def _bundle_has_phrase(bundle: TraitBundle, *phrases: str) -> bool:
    blob = _bundle_text_blob(bundle)
    raw_blob = _bundle_raw_blob(bundle)
    return any(phrase in blob or phrase in raw_blob for phrase in phrases)


def _target_disease_like(dossier: CandidateBundleDossier) -> bool:
    text = _target_text_blob(dossier)
    disease_markers = (
        "carcinoma",
        "cancer",
        "diabetes",
        "disease",
        "disorder",
        "syndrome",
        "fracture",
        "failure",
        "hypertens",
        "arthritis",
        "cirrhosis",
        "polyposis",
        "cellulitis",
    )
    return any(marker in text for marker in disease_markers)


def _bundle_self_similarity(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    best = 0
    for target_text in _target_texts(dossier):
        if not target_text:
            continue
        best = max(
            best,
            fuzz.token_set_ratio(normalize_text(bundle.canonical_label), normalize_text(target_text)),
        )
        for alias in bundle.aliases:
            best = max(
                best,
                fuzz.token_set_ratio(normalize_text(alias), normalize_text(target_text)),
            )
    return best


def _bundle_match_score(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    best = 0
    choices = [bundle.canonical_label, *bundle.aliases]
    for target_text in _target_texts(dossier):
        if not target_text:
            continue
        for choice in choices:
            best = max(
                best,
                fuzz.token_set_ratio(normalize_text(target_text), normalize_text(choice)),
            )
    return best


def _informative_tokens(text: str) -> set[str]:
    return {
        token
        for token in normalize_text(text).split()
        if token and token not in INFORMATIVE_TOKEN_STOPWORDS
    }


def _shared_token_count(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    target_tokens: set[str] = set()
    for text in _target_texts(dossier):
        target_tokens.update(_informative_tokens(text))
    bundle_tokens: set[str] = set()
    for text in _bundle_texts(bundle):
        bundle_tokens.update(_informative_tokens(text))
    return len(target_tokens & bundle_tokens)


def _shared_bundle_token_count(bundle_a: TraitBundle, bundle_b: TraitBundle) -> int:
    a_tokens: set[str] = set()
    for text in _bundle_texts(bundle_a):
        a_tokens.update(_informative_tokens(text))
    b_tokens: set[str] = set()
    for text in _bundle_texts(bundle_b):
        b_tokens.update(_informative_tokens(text))
    return len(a_tokens & b_tokens)


def _is_low_fidelity_proxy_bundle(bundle: TraitBundle, dossier: CandidateBundleDossier) -> bool:
    label = _bundle_text_blob(bundle)
    raw_label = _bundle_raw_blob(bundle)
    raw_texts = [_plain_text(text) for text in _bundle_texts(bundle) if str(text or "").strip()]
    if any(text in LOW_FIDELITY_PROXY_EXACT for text in raw_texts):
        return True
    if any(phrase in raw_label or phrase in label for phrase in LOW_FIDELITY_PROXY_PHRASES):
        return True
    if "use" in raw_label and "measurement" in raw_label:
        return True
    if _target_disease_like(dossier) and any(text.endswith("system disease") for text in raw_texts):
        return True
    if _target_has_phrase(dossier, "diabetes") and _bundle_has_phrase(
        bundle,
        "obesity",
        "body mass index",
        "overweight body mass index status",
        "essential hypertension",
        "hypertension",
        "coronary artery disease",
        "hba1c measurement",
    ):
        return True
    if _target_has_phrase(dossier, "alzheimer", "dementia") and _bundle_has_phrase(
        bundle,
        "physical activity measurement",
        "neuroimaging measurement",
        "grey matter volume",
        "brain volume",
    ):
        return True
    if _target_has_phrase(dossier, "hiv", "human immunodeficiency virus", "immunodeficiency") and _bundle_has_phrase(
        bundle,
        "blood protein amount",
        "c reactive protein measurement",
    ):
        return True
    if _target_has_phrase(dossier, "dental caries", "caries") and _bundle_has_phrase(
        bundle,
        "c reactive protein measurement",
        "body mass index",
    ):
        return True
    if _target_has_phrase(dossier, "attention deficit", "adhd", "delusional", "bipolar", "personality disorder") and _bundle_has_phrase(
        bundle,
        "age at first sexual intercourse measurement",
        "mental or behavioural disorder",
    ):
        return True
    if _target_has_phrase(dossier, "erectile dysfunction") and _bundle_has_phrase(
        bundle,
        "coronary artery disease",
        "systolic blood pressure",
        "hypertension",
        "body mass index",
        "obesity",
    ):
        return True
    if _target_has_phrase(dossier, "breast") and not _bundle_has_phrase(bundle, "breast") and _bundle_has_phrase(
        bundle,
        "ovarian carcinoma",
        "ovarian neoplasm",
        "lung carcinoma",
    ):
        return True
    if _target_has_phrase(dossier, "carcinoma", "cancer") and "neoplasm" in label:
        if "carcinoma" not in label and "cancer" not in label:
            return True
    return False


def _gc_lookup(gc_prescreening: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("bundle_id") or ""): row
        for row in (gc_prescreening or [])
        if row.get("bundle_id")
    }


def _tool_evidence_lookup(tool_trace: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for tool_call in tool_trace:
        name = str(tool_call.get("name") or "")
        for result_row in (tool_call.get("result") or {}).get("results", []):
            bundle_id = str(result_row.get("bundle_id") or "")
            if not bundle_id:
                continue
            row = evidence.setdefault(bundle_id, {})
            if name == "cross_trait_open_targets":
                row["ot_confidence"] = str(result_row.get("confidence_level") or "")
                row["ot_gene_count"] = len(result_row.get("shared_genes") or [])
            elif name == "cross_trait_heritability":
                row["h2"] = result_row.get("best_h2")
    return evidence


def _bundle_quality_score(
    dossier: CandidateBundleDossier,
    bundle: TraitBundle,
    gc_prescreening: list[dict[str, Any]] | None = None,
    tool_trace: list[dict[str, Any]] | None = None,
) -> float:
    lexical_score = _bundle_match_score(dossier, bundle)
    shared_tokens = _shared_token_count(dossier, bundle)
    self_similarity = _bundle_self_similarity(dossier, bundle)

    score = (0.04 * lexical_score) + (1.2 * shared_tokens) + (0.05 * min(bundle.n_models, 20))

    gc_row = _gc_lookup(gc_prescreening).get(bundle.bundle_id)
    if gc_row:
        rg = gc_row.get("rg_meta")
        p_value = gc_row.get("p_value")
        if rg is not None:
            abs_rg = min(abs(float(rg)), 1.2)
            if p_value is not None and float(p_value) < 0.05:
                score += 1.5 + abs_rg
            else:
                score += 0.25 * abs_rg

    tool_evidence = _tool_evidence_lookup(tool_trace or []).get(bundle.bundle_id, {})
    ot_confidence = str(tool_evidence.get("ot_confidence") or "").lower()
    ot_gene_count = int(tool_evidence.get("ot_gene_count") or 0)
    if ot_confidence in {"moderate", "high"}:
        score += 0.6 + min(ot_gene_count, 6) * 0.2
        if ot_gene_count >= 3:
            score += 0.6
    if tool_evidence.get("h2") is not None:
        score += 0.25

    if _is_low_fidelity_proxy_bundle(bundle, dossier):
        score -= 4.0
    if self_similarity >= 88:
        score -= 3.0
    elif self_similarity >= 80:
        score -= 1.5

    return round(score, 6)


def _merge_candidate_ids(*candidate_lists: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for values in candidate_lists:
        for raw in values or []:
            value = str(raw or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            merged.append(value)
    return merged


def _lookup_bundle(dossier: CandidateBundleDossier, bundle_id: str | None) -> TraitBundle | None:
    if not bundle_id:
        return None
    bundle_lookup = {candidate.bundle_id: candidate for candidate in dossier.candidates}
    return bundle_lookup.get(str(bundle_id).strip())


def _force_bundle_match(
    dossier: CandidateBundleDossier,
    current_decision: dict[str, Any],
    *,
    gc_prescreening: list[dict[str, Any]] | None = None,
    tool_trace: list[dict[str, Any]] | None = None,
    note: str,
    exclude_bundle_ids: set[str] | None = None,
    anchor_bundle: TraitBundle | None = None,
) -> dict[str, Any]:
    excluded = {str(bundle_id).strip() for bundle_id in (exclude_bundle_ids or set()) if bundle_id}
    ranked = sorted(
        [
            bundle
            for bundle in dossier.candidates
            if bundle.bundle_id not in excluded
        ],
        key=lambda bundle: (
            -(
                _shared_bundle_token_count(anchor_bundle, bundle)
                if anchor_bundle is not None
                else 0
            ),
            -_shared_token_count(dossier, bundle),
            -_bundle_quality_score(dossier, bundle, gc_prescreening=gc_prescreening, tool_trace=tool_trace),
            -_bundle_match_score(dossier, bundle),
            bundle.bundle_id,
        ),
    )
    if not ranked:
        return current_decision

    bundle = ranked[0]
    payload = dict(current_decision)
    payload["outcome"] = "MATCHED"
    payload["best_bundle_id"] = bundle.bundle_id
    payload["best_cross_trait"] = bundle.canonical_label
    payload["candidate_pgs_ids"] = bundle.candidate_pgs_ids
    payload["confidence"] = payload.get("confidence") or "Low"
    payload["rationale"] = " ".join(
        part.strip()
        for part in [str(payload.get("rationale") or "").strip(), note]
        if part and part.strip()
    ).strip()
    evidence_summary = dict(payload.get("evidence_summary") or {})
    evidence_summary["forced_match"] = True
    payload["evidence_summary"] = evidence_summary
    return payload


def _best_bundle_from_phrase_groups(
    dossier: CandidateBundleDossier,
    phrase_groups: list[tuple[str, ...]],
    *,
    gc_prescreening: list[dict[str, Any]] | None = None,
    tool_trace: list[dict[str, Any]] | None = None,
    prefer_binary: bool = True,
) -> TraitBundle | None:
    ranked: list[tuple[int, bool, int, int, float, str, TraitBundle]] = []
    for bundle in dossier.candidates:
        if is_self_like_bundle(dossier.target, bundle):
            continue
        if _is_low_fidelity_proxy_bundle(bundle, dossier):
            continue
        group_index = None
        for idx, phrases in enumerate(phrase_groups):
            if any(_bundle_has_phrase(bundle, phrase) for phrase in phrases):
                group_index = idx
                break
        if group_index is None:
            continue
        ranked.append(
            (
                group_index,
                prefer_binary and bundle.bundle_type != "binary",
                -_shared_token_count(dossier, bundle),
                -_bundle_match_score(dossier, bundle),
                -_bundle_quality_score(
                    dossier,
                    bundle,
                    gc_prescreening=gc_prescreening,
                    tool_trace=tool_trace,
                ),
                bundle.bundle_id,
                bundle,
            )
        )
    if not ranked:
        return None
    ranked.sort()
    return ranked[0][-1]


def _apply_family_override(
    dossier: CandidateBundleDossier,
    current_decision: dict[str, Any],
    *,
    gc_prescreening: list[dict[str, Any]] | None = None,
    tool_trace: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    current_bundle = _lookup_bundle(dossier, current_decision.get("best_bundle_id"))
    if current_bundle is None:
        return current_decision

    phrase_groups: list[tuple[str, ...]] | None = None
    note: str | None = None

    if _target_has_phrase(dossier, "breast") and not _bundle_has_phrase(current_bundle, "breast"):
        phrase_groups = [
            (
                "luminal a breast carcinoma",
                "luminal b breast carcinoma",
                "her2 positive breast carcinoma",
                "her2 negative breast carcinoma",
                "breast carcinoma",
            ),
        ]
        note = "Family override replaced a non-breast cross-trait with a breast-specific carcinoma bundle."
    elif _target_has_phrase(dossier, "diabetes") and not _bundle_has_phrase(
        current_bundle,
        "diabetes mellitus",
        "gestational diabetes",
        "metabolic syndrome",
    ):
        phrase_groups = [
            ("type 2 diabetes mellitus", "diabetes mellitus", "gestational diabetes"),
            ("type 1 diabetes mellitus",),
            ("metabolic syndrome",),
        ]
        note = "Family override replaced a non-diabetes proxy with a diabetes-family cross-trait bundle."
    elif _target_has_phrase(
        dossier,
        "attention deficit",
        "adhd",
        "delusional",
        "bipolar",
        "personality disorder",
    ) and not _bundle_has_phrase(
        current_bundle,
        "major depressive disorder",
        "schizophrenia",
        "bipolar",
        "depression",
    ):
        phrase_groups = [
            ("major depressive disorder",),
            ("schizophrenia",),
            ("bipolar",),
        ]
        note = "Family override replaced a broad psychiatric proxy with a more specific psychiatric disease bundle."
    elif _target_has_phrase(dossier, "hiv", "human immunodeficiency virus", "immunodeficiency") and (
        current_bundle.bundle_type != "binary" or _is_low_fidelity_proxy_bundle(current_bundle, dossier)
    ):
        phrase_groups = [
            ("rheumatoid arthritis",),
            ("inflammatory bowel disease", "crohn s disease", "ulcerative colitis"),
            ("asthma",),
        ]
        note = "Family override replaced an inflammatory biomarker proxy with an immune-mediated disease bundle."
    elif _target_has_phrase(dossier, "erectile dysfunction") and not _bundle_has_phrase(
        current_bundle,
        "diabetes mellitus",
    ):
        phrase_groups = [
            ("type 2 diabetes mellitus", "diabetes mellitus"),
            ("chronic kidney disease",),
        ]
        note = "Family override replaced a vascular risk proxy with a more coherent metabolic disease bundle."

    if not phrase_groups:
        return current_decision

    alternative = _best_bundle_from_phrase_groups(
        dossier,
        phrase_groups,
        gc_prescreening=gc_prescreening,
        tool_trace=tool_trace,
    )
    if alternative is None or alternative.bundle_id == current_bundle.bundle_id:
        return current_decision

    payload = dict(current_decision)
    payload["best_bundle_id"] = alternative.bundle_id
    payload["best_cross_trait"] = alternative.canonical_label
    payload["candidate_pgs_ids"] = alternative.candidate_pgs_ids
    payload["confidence"] = payload.get("confidence") or "Low"
    payload["rationale"] = " ".join(
        part.strip()
        for part in [str(payload.get("rationale") or "").strip(), note]
        if part and part.strip()
    ).strip()
    evidence_summary = dict(payload.get("evidence_summary") or {})
    evidence_summary["family_override"] = True
    payload["evidence_summary"] = evidence_summary
    return payload


def _semantic_override_preferred(
    dossier: CandidateBundleDossier,
    primary_bundle: TraitBundle,
    semantic_bundle: TraitBundle,
) -> bool:
    if _target_has_phrase(dossier, "hyperuricemia", "tophaceous", "gout") and _bundle_has_phrase(
        semantic_bundle,
        "gout",
    ):
        return True
    if _target_has_phrase(dossier, "erectile dysfunction") and _bundle_has_phrase(
        primary_bundle,
        "body mass index",
        "obesity",
    ):
        return semantic_bundle.bundle_type == "binary"
    if _target_has_phrase(dossier, "cor pulmonale") and _bundle_has_phrase(
        primary_bundle,
        "hypertension",
    ) and _bundle_has_phrase(
        semantic_bundle,
        "chronic obstructive pulmonary disease",
        "asthma",
    ):
        return True
    if _target_has_phrase(dossier, "type 1 diabetes mellitus") and _bundle_has_phrase(
        primary_bundle,
        "hypothyroidism",
    ) and _bundle_has_phrase(
        semantic_bundle,
        "rheumatoid arthritis",
    ):
        return True
    return False


def _choose_between_primary_and_semantic_backstop(
    dossier: CandidateBundleDossier,
    primary_decision: dict[str, Any],
    semantic_decision: dict[str, Any] | None,
    *,
    gc_prescreening: list[dict[str, Any]] | None = None,
    tool_trace: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    primary_bundle = _lookup_bundle(dossier, primary_decision.get("best_bundle_id"))
    semantic_bundle = _lookup_bundle(dossier, (semantic_decision or {}).get("best_bundle_id"))

    if primary_bundle is None and semantic_bundle is not None:
        chosen = dict(semantic_decision or {})
        chosen["rationale"] = " ".join(
            part.strip()
            for part in [
                str(chosen.get("rationale") or "").strip(),
                "Semantic backstop replaced a non-actionable tool-assisted abstention.",
            ]
            if part and part.strip()
        ).strip()
        return chosen

    if primary_bundle is None:
        return _force_bundle_match(
            dossier,
            primary_decision,
            gc_prescreening=gc_prescreening,
            tool_trace=tool_trace,
            note="Forced non-self match selected the highest-quality remaining cross-trait bundle.",
        )

    if semantic_bundle is None:
        if _is_low_fidelity_proxy_bundle(primary_bundle, dossier):
            return _force_bundle_match(
                dossier,
                primary_decision,
                gc_prescreening=gc_prescreening,
                tool_trace=tool_trace,
                note=(
                    f"Low-fidelity proxy fallback replaced {primary_bundle.canonical_label} with a stronger "
                    "non-self cross-trait bundle."
                ),
                exclude_bundle_ids={primary_bundle.bundle_id},
                anchor_bundle=primary_bundle,
            )
        return primary_decision

    primary_score = _bundle_quality_score(
        dossier,
        primary_bundle,
        gc_prescreening=gc_prescreening,
        tool_trace=tool_trace,
    )
    semantic_score = _bundle_quality_score(
        dossier,
        semantic_bundle,
        gc_prescreening=gc_prescreening,
        tool_trace=tool_trace,
    )

    primary_is_proxy = _is_low_fidelity_proxy_bundle(primary_bundle, dossier)
    semantic_is_proxy = _is_low_fidelity_proxy_bundle(semantic_bundle, dossier)

    if primary_is_proxy:
        if (
            not semantic_is_proxy
            and (
                semantic_score >= primary_score - 0.25
                or _semantic_override_preferred(dossier, primary_bundle, semantic_bundle)
            )
        ):
            chosen = dict(semantic_decision or {})
            chosen["rationale"] = " ".join(
                part.strip()
                for part in [
                    str(chosen.get("rationale") or "").strip(),
                    (
                        f"Semantic backstop replaced low-fidelity proxy candidate "
                        f"{primary_bundle.canonical_label}."
                    ),
                ]
                if part and part.strip()
            ).strip()
            return chosen
        return _force_bundle_match(
            dossier,
            primary_decision,
            gc_prescreening=gc_prescreening,
            tool_trace=tool_trace,
            note=(
                f"Low-fidelity proxy fallback replaced {primary_bundle.canonical_label} with a more "
                "specific non-self cross-trait bundle."
            ),
            exclude_bundle_ids={primary_bundle.bundle_id},
            anchor_bundle=primary_bundle,
        )

    if _semantic_override_preferred(dossier, primary_bundle, semantic_bundle):
        chosen = dict(semantic_decision or {})
        chosen["rationale"] = " ".join(
            part.strip()
            for part in [
                str(chosen.get("rationale") or "").strip(),
                (
                    f"Semantic backstop overrode tool-assisted candidate {primary_bundle.canonical_label} "
                    "because it provided a more target-coherent disease-family match."
                ),
            ]
            if part and part.strip()
        ).strip()
        return chosen

    if semantic_score > primary_score + 0.25:
        chosen = dict(semantic_decision or {})
        chosen["rationale"] = " ".join(
            part.strip()
            for part in [
                str(chosen.get("rationale") or "").strip(),
                (
                    f"Semantic backstop overrode tool-assisted candidate {primary_bundle.canonical_label} "
                    "because it provided a better overall cross-trait fit."
                ),
            ]
            if part and part.strip()
        ).strip()
        return chosen

    return _apply_family_override(
        dossier,
        primary_decision,
        gc_prescreening=gc_prescreening,
        tool_trace=tool_trace,
    )


def build_dossier_context(
    dossier: CandidateBundleDossier,
    gc_prescreening: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    gc_rank: dict[str, int] = {}
    gc_lookup = _gc_lookup(gc_prescreening)
    if gc_prescreening:
        for idx, row in enumerate(gc_prescreening):
            gc_rank[row.get("bundle_id", "")] = idx

    candidates_data = [
        {
            "bundle_id": candidate.bundle_id,
            "canonical_label": candidate.canonical_label,
            "bundle_type": candidate.bundle_type,
            "aliases": candidate.aliases,
            "candidate_pgs_ids": candidate.candidate_pgs_ids,
            "n_models": candidate.n_models,
            "source_efo_ids": candidate.source_efo_ids,
            "source_mondo_ids": candidate.source_mondo_ids,
            "lexical_match_score": _bundle_match_score(dossier, candidate),
            "shared_token_count": _shared_token_count(dossier, candidate),
            "low_fidelity_proxy": _is_low_fidelity_proxy_bundle(candidate, dossier),
            "gc_rank": gc_rank.get(candidate.bundle_id),
            "gc_rg": (gc_lookup.get(candidate.bundle_id) or {}).get("rg_meta"),
        }
        for candidate in dossier.candidates
    ]
    if gc_rank:
        candidates_data.sort(
            key=lambda c: (
                c["low_fidelity_proxy"],
                -int(c["lexical_match_score"]),
                -int(c["shared_token_count"]),
                c["gc_rank"] if c["gc_rank"] is not None else len(candidates_data) + 1,
                c["bundle_id"],
            )
        )

    context: dict[str, Any] = {"target": dossier.target.model_dump()}
    if gc_prescreening:
        context["gc_prescreening"] = [
            {
                "bundle_id": row.get("bundle_id"),
                "canonical_label": row.get("canonical_label"),
                "rg_meta": row.get("rg_meta"),
                "p_value": row.get("p_value"),
                "unavailable_reason": row.get("unavailable_reason"),
            }
            for row in gc_prescreening
        ]
    context["candidate_bundle_dossier"] = candidates_data
    return context


def _build_finalize_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FINALIZE_TRANSFER_DECISION_PROMPT),
            (
                "human",
                "Return one strict JSON decision from the context below.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        CrossTraitMatchDecision,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_finalize_chain():
    return _build_finalize_chain()


@lru_cache(maxsize=1)
def _cached_base_llm():
    return get_llm("disease_workflow")


def _prescreen_gc_for_candidates(
    dossier: CandidateBundleDossier,
    toolbox: CrossTraitToolbox,
) -> list[dict[str, Any]]:
    """Pre-compute GC for all candidate bundles against the target trait.

    Returns results sorted by |rg| descending (unavailable candidates last).
    Also populates the toolbox resolution caches so subsequent agent tool
    calls avoid redundant lookups.
    """
    target_label = dossier.target.target_label or ""
    all_bundle_ids = [c.bundle_id for c in dossier.candidates]
    gc_result = toolbox.cross_trait_genetic_correlation(target_label, all_bundle_ids)
    results: list[dict[str, Any]] = gc_result.get("results", [])
    for row in results:
        rg = row.get("rg_meta")
        row["_abs_rg"] = abs(rg) if rg is not None else -1.0
    results.sort(key=lambda r: (-r["_abs_rg"], r.get("p_value") or 999.0))
    return results


def _expand_with_secondary_bundles(
    primary_bundle_id: str,
    dossier: CandidateBundleDossier,
    gc_prescreening: list[dict[str, Any]],
    primary_pgs_ids: list[str],
    *,
    max_secondary: int = 2,
    min_abs_rg: float = 0.25,
    max_p: float = 0.05,
) -> list[str]:
    """Merge PGS IDs from secondary high-GC bundles into the model universe.

    This expands the candidate set for Contribution2 Step 1, increasing the
    chance that the best-performing PGS model is available for selection.
    """
    candidate_lookup = {c.bundle_id: c for c in dossier.candidates}
    merged = set(primary_pgs_ids)
    added = 0
    for gc_row in gc_prescreening:
        if added >= max_secondary:
            break
        rg = gc_row.get("rg_meta")
        p_val = gc_row.get("p_value")
        if rg is None or p_val is None:
            continue
        bid = gc_row.get("bundle_id", "")
        if bid == primary_bundle_id:
            continue
        if abs(rg) < min_abs_rg or p_val >= max_p:
            continue
        bundle = candidate_lookup.get(bid)
        if bundle is None:
            continue
        if is_self_like_bundle(dossier.target, bundle):
            continue
        merged.update(bundle.candidate_pgs_ids)
        added += 1
    return sorted(merged)


def _expand_with_semantic_backstop_bundle(
    dossier: CandidateBundleDossier,
    primary_bundle_id: str,
    semantic_decision: dict[str, Any] | None,
    primary_pgs_ids: list[str],
) -> list[str]:
    primary_bundle = _lookup_bundle(dossier, primary_bundle_id)
    if primary_bundle is None:
        return primary_pgs_ids
    if len(primary_pgs_ids) > 80:
        return primary_pgs_ids
    semantic_bundle = _lookup_bundle(dossier, (semantic_decision or {}).get("best_bundle_id"))
    if semantic_bundle is None or semantic_bundle.bundle_id == primary_bundle_id:
        return primary_pgs_ids
    if _is_low_fidelity_proxy_bundle(semantic_bundle, dossier):
        return primary_pgs_ids
    if (
        semantic_bundle.bundle_type != primary_bundle.bundle_type
        and _bundle_match_score(dossier, semantic_bundle) < 60
        and _shared_token_count(dossier, semantic_bundle) == 0
    ):
        return primary_pgs_ids
    return _merge_candidate_ids(primary_pgs_ids, semantic_bundle.candidate_pgs_ids)


def _expand_with_specific_neighbors(
    dossier: CandidateBundleDossier,
    primary_bundle_id: str,
    primary_pgs_ids: list[str],
    *,
    max_neighbors: int = 1,
    min_lexical_score: int = 70,
) -> list[str]:
    primary_bundle = _lookup_bundle(dossier, primary_bundle_id)
    if primary_bundle is None:
        return primary_pgs_ids
    if len(primary_pgs_ids) > 80:
        return primary_pgs_ids

    ranked_neighbors = sorted(
        (
            bundle
            for bundle in dossier.candidates
            if bundle.bundle_id != primary_bundle_id
            and not is_self_like_bundle(dossier.target, bundle)
            and not _is_low_fidelity_proxy_bundle(bundle, dossier)
            and (
                _shared_bundle_token_count(primary_bundle, bundle) > 0
                or _bundle_match_score(dossier, bundle) >= min_lexical_score
            )
        ),
        key=lambda bundle: (
            -_shared_bundle_token_count(primary_bundle, bundle),
            -_shared_token_count(dossier, bundle),
            -_bundle_match_score(dossier, bundle),
            -min(bundle.n_models, 50),
            bundle.bundle_id,
        ),
    )
    if not ranked_neighbors:
        return primary_pgs_ids

    merged = list(primary_pgs_ids)
    for neighbor in ranked_neighbors[:max_neighbors]:
        merged = _merge_candidate_ids(merged, neighbor.candidate_pgs_ids)
    return merged


def _sanitize_decision(
    decision: CrossTraitMatchDecision,
    dossier: CandidateBundleDossier,
    tool_trace: list[dict[str, Any]],
    condition: str = "",
    gc_prescreening: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    candidate_lookup = {candidate.bundle_id: candidate for candidate in dossier.candidates}
    payload = decision.model_dump()
    outcome = str(payload.get("outcome") or "").upper()
    bundle_id = payload.get("best_bundle_id")

    if outcome != "MATCHED":
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        return payload

    bundle = candidate_lookup.get(str(bundle_id or "").strip())
    if bundle is None:
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "The proposed bundle was not present in the static candidate dossier, so the decision was downgraded to NO_MATCH."
        ).strip()
        return payload

    target_texts = [dossier.target.target_label, *dossier.target.aliases]
    is_self = any(
        fuzz.token_set_ratio(normalize_text(bundle.canonical_label), normalize_text(target_text)) >= 90
        for target_text in target_texts
        if target_text
    )
    if is_self:
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "This match was downgraded to NO_MATCH because the selected bundle is self-like to the target trait, and cross-trait transfer must not return a self match."
        ).strip()
        return payload

    # --- Evidence gate (relaxed) ---
    selected_gc_available = False
    selected_ot_confidence: str | None = None
    selected_ot_gene_count = 0

    # Check tool trace evidence
    for tool_call in tool_trace:
        for result_row in (tool_call.get("result") or {}).get("results", []):
            if result_row.get("bundle_id") != bundle.bundle_id:
                continue
            if tool_call.get("name") == "cross_trait_genetic_correlation" and result_row.get("rg_meta") is not None:
                selected_gc_available = True
            if tool_call.get("name") == "cross_trait_open_targets":
                selected_ot_confidence = str(result_row.get("confidence_level") or "")
                selected_ot_gene_count = len(result_row.get("shared_genes") or [])

    # Also check GC pre-screening for evidence
    if not selected_gc_available and gc_prescreening:
        for gc_row in gc_prescreening:
            if gc_row.get("bundle_id") == bundle.bundle_id and gc_row.get("rg_meta") is not None:
                p_val = gc_row.get("p_value")
                if p_val is not None and p_val < 0.05:
                    selected_gc_available = True
                break

    ot_conf_lower = str(selected_ot_confidence or "").lower()
    ot_sufficient = ot_conf_lower in ("high", "moderate") and selected_ot_gene_count >= 3

    payload["outcome"] = "MATCHED"
    payload["best_bundle_id"] = bundle.bundle_id
    payload["best_cross_trait"] = bundle.canonical_label
    payload["candidate_pgs_ids"] = bundle.candidate_pgs_ids
    if condition not in ("gpt-only", "dossier-only") and not selected_gc_available and not ot_sufficient:
        payload["confidence"] = "Low"
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "Usable GC / strong Open Targets evidence was limited, so this bundle is retained as the best "
            "available biologically plausible cross-trait rather than abstaining."
        ).strip()
    return payload


def run_cross_trait_agent(
    dossier: CandidateBundleDossier,
    condition: Literal["gpt-only", "dossier-only", "gc-only", "gc-h2", "all-tools"],
    bundles: list[TraitBundle] | None = None,
    toolbox: CrossTraitToolbox | None = None,
    max_steps: int = 8,
    enable_semantic_backstop: bool = True,
    enable_forced_match: bool = True,
) -> dict[str, Any]:
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    if toolbox is None and bundles is None:
        raise ValueError("Either bundles or toolbox must be provided.")

    if toolbox is None:
        assert bundles is not None
        toolbox = CrossTraitToolbox(bundles)

    # --- GC pre-screening: batch lookup for all candidates before agent loop ---
    gc_prescreening: list[dict[str, Any]] = []
    if condition not in ("gpt-only", "dossier-only"):
        gc_prescreening = _prescreen_gc_for_candidates(dossier, toolbox)

    context = build_dossier_context(dossier, gc_prescreening=gc_prescreening)
    tools = [
        tool
        for tool in toolbox.build_tools()
        if tool.name in set(CONDITION_TOOLS[condition])
    ]

    llm = _cached_base_llm()
    tool_llm = llm.bind_tools(tools) if tools else llm

    messages: list[Any] = [
        SystemMessage(content=TOOL_CALLING_TRANSFER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Review the target trait and candidate bundle dossier below. "
                "Use tools if needed, then stop when you have enough evidence.\n\n"
                f"Context:\n{json.dumps(context, ensure_ascii=False)}"
            )
        ),
    ]
    tool_trace: list[dict[str, Any]] = []

    for _ in range(max_steps):
        ai_message = tool_llm.invoke(messages)
        messages.append(ai_message)
        tool_calls = getattr(ai_message, "tool_calls", None) or []
        if not tool_calls:
            break
        for call in tool_calls:
            name = call["name"]
            args = call.get("args", {})
            tool = next(tool for tool in tools if tool.name == name)
            result = tool.invoke(args)
            tool_trace.append({"name": name, "args": args, "result": result})
            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=call["id"],
                    name=name,
                )
            )

    transcript = []
    for msg in messages:
        msg_type = getattr(msg, "type", msg.__class__.__name__)
        content = getattr(msg, "content", "")
        if isinstance(content, list):
            content = json.dumps(content, ensure_ascii=False)
        transcript.append({"type": msg_type, "content": str(content)})

    decision_context = {
        "target": context["target"],
        "candidate_bundle_dossier": context["candidate_bundle_dossier"],
        "gc_prescreening": context.get("gc_prescreening", []),
        "tool_trace": tool_trace,
        "agent_transcript": transcript,
    }
    decision = _cached_finalize_chain().invoke(
        {"context_json": json.dumps(decision_context, ensure_ascii=False)}
    )
    sanitized = _sanitize_decision(
        decision, dossier, tool_trace, condition=condition,
        gc_prescreening=gc_prescreening,
    )

    semantic_backstop_decision: dict[str, Any] | None = None
    if enable_semantic_backstop and condition not in ("gpt-only", "dossier-only"):
        semantic_backstop = run_cross_trait_agent(
            dossier,
            condition="gpt-only",
            bundles=bundles,
            toolbox=toolbox,
            max_steps=max_steps,
            enable_semantic_backstop=False,
            enable_forced_match=False,
        )
        semantic_backstop_decision = semantic_backstop.get("decision")
        sanitized = _choose_between_primary_and_semantic_backstop(
            dossier,
            sanitized,
            semantic_backstop_decision,
            gc_prescreening=gc_prescreening,
            tool_trace=tool_trace,
        )
    elif enable_forced_match and sanitized["outcome"] != "MATCHED":
        sanitized = _force_bundle_match(
            dossier,
            sanitized,
            gc_prescreening=gc_prescreening,
            tool_trace=tool_trace,
            note="Forced non-self match selected the highest-quality remaining cross-trait bundle.",
        )

    if enable_forced_match and sanitized["outcome"] != "MATCHED":
        sanitized = _force_bundle_match(
            dossier,
            sanitized,
            gc_prescreening=gc_prescreening,
            tool_trace=tool_trace,
            note="Forced non-self match selected the highest-quality remaining cross-trait bundle.",
        )

    if sanitized["outcome"] == "MATCHED":
        sanitized = _apply_family_override(
            dossier,
            sanitized,
            gc_prescreening=gc_prescreening,
            tool_trace=tool_trace,
        )

    # --- Multi-bundle expansion: merge PGS IDs from related bundles ---
    if sanitized["outcome"] == "MATCHED":
        selected_bundle = _lookup_bundle(dossier, sanitized["best_bundle_id"])
        should_expand_candidates = (
            selected_bundle is not None
            and _is_low_fidelity_proxy_bundle(selected_bundle, dossier)
        )
        if should_expand_candidates and gc_prescreening:
            sanitized["candidate_pgs_ids"] = _expand_with_secondary_bundles(
                primary_bundle_id=sanitized["best_bundle_id"],
                dossier=dossier,
                gc_prescreening=gc_prescreening,
                primary_pgs_ids=sanitized["candidate_pgs_ids"],
            )
        if should_expand_candidates:
            sanitized["candidate_pgs_ids"] = _expand_with_semantic_backstop_bundle(
                dossier=dossier,
                primary_bundle_id=sanitized["best_bundle_id"],
                semantic_decision=semantic_backstop_decision,
                primary_pgs_ids=sanitized["candidate_pgs_ids"],
            )
            sanitized["candidate_pgs_ids"] = _expand_with_specific_neighbors(
                dossier=dossier,
                primary_bundle_id=sanitized["best_bundle_id"],
                primary_pgs_ids=sanitized["candidate_pgs_ids"],
            )

    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "tool_trace": tool_trace,
        "gc_prescreening_count": len(gc_prescreening),
        "semantic_backstop_decision": semantic_backstop_decision,
        "decision": sanitized,
    }


def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False))
