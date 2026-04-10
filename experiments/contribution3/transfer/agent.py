from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from langchain_core.prompts import ChatPromptTemplate
from thefuzz import fuzz

from experiments.contribution3.transfer.common import (
    CONTINUOUS_HINTS,
    CandidateBundleDossier,
    TraitBundle,
    is_self_like_bundle,
    normalize_text,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    CandidateEvidenceCard,
    CrossTraitTransferFrontierDecision,
    DecisionMode,
    EvidenceState,
    GeneticCorrelationEvidence,
    HeritabilityEvidence,
    JudgeFrontierSelection,
    OpenTargetsEvidence,
    TRANSFER_FRONTIER_JUDGE_PROMPT,
    TRANSFER_FRONTIER_VERIFY_PROMPT,
    VerifiedSelection,
)
from experiments.contribution3.transfer.tools import CrossTraitToolbox
from src.server.core.llm_config import get_llm


@dataclass(frozen=True)
class TransferConfig:
    """Benchmark-family-aware configuration for the transfer pipeline."""

    w_statistical_overlap: float
    w_mechanistic_overlap: float
    w_signal_capacity: float
    w_phenotype_fidelity: float
    gc_track_size: int
    semantic_track_size: int
    concordance_bonus: float
    concordance_penalty: float
    gc_cheap_rank_significant: float
    gc_cheap_rank_nonsignificant: float
    shortlist_strategy: Literal["dual_track", "gc_first"]
    shortlist_cap: int
    apply_gc_resolution_discount: bool
    allow_ot_promotion: bool


BINARY_TO_BINARY_CONFIG = TransferConfig(
    w_statistical_overlap=2.0,
    w_mechanistic_overlap=3.5,
    w_signal_capacity=1.2,
    w_phenotype_fidelity=2.8,
    gc_track_size=6,
    semantic_track_size=6,
    concordance_bonus=0.8,
    concordance_penalty=-0.4,
    gc_cheap_rank_significant=1.6,
    gc_cheap_rank_nonsignificant=0.6,
    shortlist_strategy="dual_track",
    shortlist_cap=14,
    apply_gc_resolution_discount=True,
    allow_ot_promotion=True,
)

BINARY_TO_CONTINUOUS_CONFIG = TransferConfig(
    w_statistical_overlap=3.2,
    w_mechanistic_overlap=2.5,
    w_signal_capacity=1.4,
    w_phenotype_fidelity=2.1,
    gc_track_size=7,
    semantic_track_size=4,
    concordance_bonus=0.5,
    concordance_penalty=-0.2,
    gc_cheap_rank_significant=2.4,
    gc_cheap_rank_nonsignificant=0.8,
    shortlist_strategy="gc_first",
    shortlist_cap=8,
    apply_gc_resolution_discount=False,
    allow_ot_promotion=False,
)

DEFAULT_CONFIG = BINARY_TO_BINARY_CONFIG

BENCHMARK_FAMILY_CONFIGS: dict[str, TransferConfig] = {
    "binary_to_binary": BINARY_TO_BINARY_CONFIG,
    "binary_to_continuous": BINARY_TO_CONTINUOUS_CONFIG,
}


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

PROXY_MARKERS = (
    "family history",
    "history of",
    "personal history of",
    "medication",
    "treatment",
    "self reported",
    "health trait",
    "smoking status",
    "cigarettes per day",
    "therapy",
    "drug use",
    "aspirin use",
)
ENDOPHENOTYPE_MARKERS = tuple(CONTINUOUS_HINTS) + (
    "fev",
    "fvc",
    "biomarker",
    "lab",
)
COMPOSITE_MARKERS = (
    "syndrome",
    "joint disease",
    "metabolic disease",
    "mental or behavioural disorder",
    "system disease",
    "obesity",
    "overnutrition",
    "body mass index",
)


def _target_texts(dossier: CandidateBundleDossier) -> list[str]:
    return [dossier.target.target_label, *dossier.target.aliases]


def _plain_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _target_text_blob(dossier: CandidateBundleDossier) -> str:
    return normalize_text(" ".join(_target_texts(dossier)))


def _bundle_texts(bundle: TraitBundle) -> list[str]:
    return [bundle.canonical_label, *bundle.aliases]


def _bundle_text_blob(bundle: TraitBundle) -> str:
    return normalize_text(" ".join(_bundle_texts(bundle)))


def _bundle_match_score(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    best = 0
    for target_text in _target_texts(dossier):
        if not target_text:
            continue
        for choice in _bundle_texts(bundle):
            best = max(
                best,
                fuzz.token_set_ratio(normalize_text(target_text), normalize_text(choice)),
            )
    return best


def _informative_tokens(text: str) -> set[str]:
    stopwords = {
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
        "with",
        "without",
    }
    return {
        token
        for token in normalize_text(text).split()
        if token and token not in stopwords
    }


def _shared_token_count(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    target_tokens: set[str] = set()
    for text in _target_texts(dossier):
        target_tokens.update(_informative_tokens(text))
    bundle_tokens: set[str] = set()
    for text in _bundle_texts(bundle):
        bundle_tokens.update(_informative_tokens(text))
    return len(target_tokens & bundle_tokens)


def _candidate_archetype(dossier: CandidateBundleDossier, bundle: TraitBundle) -> str:
    blob = _bundle_text_blob(bundle)
    raw = _plain_text(" ".join(_bundle_texts(bundle)))
    lexical = _bundle_match_score(dossier, bundle)
    shared_tokens = _shared_token_count(dossier, bundle)

    if any(marker in raw or marker in blob for marker in PROXY_MARKERS):
        return "administrative/exposure/treatment/family-history proxy"
    if bundle.bundle_type == "continuous" or any(marker in raw or marker in blob for marker in ENDOPHENOTYPE_MARKERS):
        return "mechanistic endophenotype / organ-function measurement"
    if any(marker in raw or marker in blob for marker in COMPOSITE_MARKERS):
        return "composite liability trait"
    if bundle.bundle_type == "binary" and (lexical >= 72 or shared_tokens >= 2):
        return "same-endpoint disease"
    return "adjacent disease family"


def _phenotype_fidelity_score(dossier: CandidateBundleDossier, bundle: TraitBundle, archetype: str) -> float:
    base = {
        "same-endpoint disease": 0.95,
        "adjacent disease family": 0.76,
        "composite liability trait": 0.68,
        "mechanistic endophenotype / organ-function measurement": 0.66,
        "administrative/exposure/treatment/family-history proxy": 0.15,
    }[archetype]
    lexical = _bundle_match_score(dossier, bundle) / 100.0
    shared = min(_shared_token_count(dossier, bundle), 3) * 0.05
    score = min(1.0, base + (0.15 * lexical) + shared)
    return round(score, 6)


def _gc_lookup(result: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("bundle_id") or ""): row
        for row in (result or {}).get("results", [])
        if row.get("bundle_id")
    }


def _is_significant_gc(gc: GeneticCorrelationEvidence | None) -> bool:
    return bool(gc and gc.rg is not None and gc.p_value is not None and gc.p_value < 0.05)


def _is_strong_gc(gc: GeneticCorrelationEvidence | None) -> bool:
    return bool(_is_significant_gc(gc) and abs(float(gc.rg or 0.0)) >= 0.30)


def _is_supported_ot(ot: OpenTargetsEvidence | None) -> bool:
    return bool(
        ot
        and ot.weighted_shared_target_overlap_score >= 0.20
        and ot.shared_target_count >= 1
    )


def _is_strong_ot(ot: OpenTargetsEvidence | None) -> bool:
    return bool(
        ot
        and ot.confidence_level in {"High", "Moderate"}
        and ot.genetic_support_present
        and ot.weighted_shared_target_overlap_score >= 0.35
    )


def _is_explicit_ot_discordance(ot: OpenTargetsEvidence | None) -> bool:
    return bool(ot and ot.pair_status == "no_shared_targets")


def _gc_resolution_discount(gc_row: dict[str, Any] | None) -> float:
    """Discount GC evidence when trait resolution confidence is low."""
    if gc_row is None:
        return 0.0
    multiplier = 1.0
    for key in ("target_resolution", "candidate_resolution"):
        resolution = gc_row.get(key)
        if not resolution:
            continue
        conf = resolution.get("confidence", "Unresolved") if isinstance(resolution, dict) else "Unresolved"
        if conf == "High":
            pass
        elif conf == "Moderate":
            multiplier *= 0.7
        elif conf == "Low":
            multiplier *= 0.3
        else:
            multiplier *= 0.0
    return multiplier


def _configured_gc_discount(gc_row: dict[str, Any] | None, config: TransferConfig) -> float:
    if not config.apply_gc_resolution_discount:
        return 1.0
    return _gc_resolution_discount(gc_row)


def _cheap_rank_score(
    dossier: CandidateBundleDossier,
    bundle: TraitBundle,
    archetype: str,
    fidelity_score: float,
    gc_row: dict[str, Any] | None,
    config: TransferConfig = DEFAULT_CONFIG,
) -> float:
    score = (fidelity_score * 2.0) + (min(bundle.n_models, 50) / 80.0)
    score += (_bundle_match_score(dossier, bundle) / 250.0)
    score += (_shared_token_count(dossier, bundle) * 0.08)
    if gc_row and gc_row.get("rg") is not None:
        rg = abs(float(gc_row.get("rg") or 0.0))
        p_value = gc_row.get("p_value")
        gc_discount = _configured_gc_discount(gc_row, config)
        gc_mult = config.gc_cheap_rank_significant if p_value is not None and p_value < 0.05 else config.gc_cheap_rank_nonsignificant
        score += rg * gc_mult * gc_discount
    if archetype == "administrative/exposure/treatment/family-history proxy":
        score -= 1.4
    return round(score, 6)


def _utility_score(
    *,
    archetype: str,
    phenotype_fidelity_score: float,
    gc: GeneticCorrelationEvidence | None,
    h2: HeritabilityEvidence | None,
    ot: OpenTargetsEvidence | None,
    gc_row: dict[str, Any] | None = None,
    config: TransferConfig = DEFAULT_CONFIG,
) -> tuple[float, list[str]]:
    tags: list[str] = []
    statistical_overlap = 0.0
    if gc and gc.rg is not None:
        rg = abs(float(gc.rg))
        if gc.p_value is not None and gc.p_value < 0.05:
            statistical_overlap = min(1.5, rg / 0.20)
            tags.append("significant_gc")
            if rg >= 0.30:
                tags.append("strong_gc")
        else:
            statistical_overlap = min(0.5, rg / 0.40)
        # Only binary-to-binary applies the GC resolution discount; b2c keeps GC-first behavior.
        gc_discount = _configured_gc_discount(gc_row, config)
        statistical_overlap *= gc_discount

    mechanistic_overlap = 0.0
    if ot:
        mechanistic_overlap = min(1.5, ot.weighted_shared_target_overlap_score / 0.30)
        if _is_supported_ot(ot):
            tags.append("ot_overlap")
        if ot.genetic_support_present:
            tags.append("ot_genetic_support")
        if ot.literature_dominance_warning:
            mechanistic_overlap = max(0.0, mechanistic_overlap - 0.25)
            tags.append("ot_literature_dominant")

    signal_capacity = 0.0
    if h2:
        candidate_h2 = h2.candidate_signal_capacity or 0.0
        shared_ceiling = h2.shared_signal_ceiling_proxy or candidate_h2
        signal_capacity = min(1.0, shared_ceiling / 0.010)
        if candidate_h2 >= 0.005:
            tags.append("nontrivial_h2")
        if h2.confidence_tier == "High":
            tags.append("high_confidence_h2")

    utility = (
        (statistical_overlap * config.w_statistical_overlap)
        + (mechanistic_overlap * config.w_mechanistic_overlap)
        + (signal_capacity * config.w_signal_capacity)
        + (phenotype_fidelity_score * config.w_phenotype_fidelity)
    )

    # Phase 4: evidence concordance bonus/penalty
    gc_strong = _is_strong_gc(gc)
    ot_strong = _is_strong_ot(ot)
    ot_supported = _is_supported_ot(ot)
    if gc_strong and ot_strong:
        utility += config.concordance_bonus
        tags.append("gc_ot_concordant")
    elif gc_strong and _is_explicit_ot_discordance(ot) and not ot_supported:
        utility += config.concordance_penalty
        tags.append("gc_ot_discordant")

    if archetype == "same-endpoint disease":
        tags.append("same_endpoint_disease")
    elif archetype == "adjacent disease family":
        tags.append("adjacent_disease_family")
    elif archetype == "composite liability trait":
        tags.append("composite_liability_trait")
    elif archetype == "mechanistic endophenotype / organ-function measurement":
        tags.append("endophenotype_trait")
    else:
        utility -= 1.6
        tags.append("strong_proxy_penalty")
    return round(utility, 6), tags


def _build_candidate_card(
    dossier: CandidateBundleDossier,
    bundle: TraitBundle,
    *,
    gc_row: dict[str, Any] | None = None,
    h2_row: dict[str, Any] | None = None,
    ot_row: dict[str, Any] | None = None,
    config: TransferConfig = DEFAULT_CONFIG,
) -> CandidateEvidenceCard:
    archetype = _candidate_archetype(dossier, bundle)
    fidelity_score = _phenotype_fidelity_score(dossier, bundle, archetype)
    gc = GeneticCorrelationEvidence.model_validate(gc_row) if gc_row else None
    h2 = HeritabilityEvidence.model_validate(h2_row) if h2_row else None
    ot = OpenTargetsEvidence.model_validate(ot_row) if ot_row else None
    cheap_rank_score = _cheap_rank_score(dossier, bundle, archetype, fidelity_score, gc_row, config=config)
    utility_score, evidence_tags = _utility_score(
        archetype=archetype,
        phenotype_fidelity_score=fidelity_score,
        gc=gc,
        h2=h2,
        ot=ot,
        gc_row=gc_row,
        config=config,
    )
    return CandidateEvidenceCard(
        bundle_id=bundle.bundle_id,
        canonical_label=bundle.canonical_label,
        bundle_type=bundle.bundle_type,
        candidate_pgs_ids=bundle.candidate_pgs_ids,
        n_models=bundle.n_models,
        archetype=archetype,
        phenotype_fidelity=archetype,
        phenotype_fidelity_score=fidelity_score,
        lexical_match_score=_bundle_match_score(dossier, bundle),
        shared_token_count=_shared_token_count(dossier, bundle),
        cheap_rank_score=cheap_rank_score,
        utility_score=utility_score,
        evidence_tags=sorted(set(evidence_tags)),
        gc=gc,
        h2=h2,
        open_targets=ot,
    )


def _sort_cards(cards: list[CandidateEvidenceCard]) -> list[CandidateEvidenceCard]:
    return sorted(
        cards,
        key=lambda card: (-card.utility_score, -card.cheap_rank_score, card.bundle_id),
    )


def _needs_detailed_pass(cards: list[CandidateEvidenceCard]) -> bool:
    if len(cards) < 2:
        return False
    top, second = cards[0], cards[1]
    if top.utility_score - second.utility_score < 0.45:
        return True
    if top.gc is None and (top.open_targets is None or not _is_supported_ot(top.open_targets)):
        return True
    return False


def _strong_single_match(primary: CandidateEvidenceCard, runner_up: CandidateEvidenceCard | None) -> bool:
    if runner_up is None:
        return bool(_is_significant_gc(primary.gc) or _is_strong_ot(primary.open_targets))
    if primary.utility_score - runner_up.utility_score < 0.55:
        return False
    return bool(_is_significant_gc(primary.gc) or _is_strong_ot(primary.open_targets))


def _decision_mode_from_cards(cards: list[CandidateEvidenceCard]) -> DecisionMode:
    if not cards:
        return "abstain_only_if_no_valid_bundle"
    if _strong_single_match(cards[0], cards[1] if len(cards) > 1 else None):
        return "single_confident"
    return "frontier_uncertain"


def _default_frontier_ids(cards: list[CandidateEvidenceCard], decision_mode: DecisionMode) -> list[str]:
    if not cards:
        return []
    if decision_mode == "single_confident":
        return [card.bundle_id for card in cards[: min(2, len(cards))]]
    return [card.bundle_id for card in cards[: min(3, len(cards))]]


def _bundle_lookup(dossier: CandidateBundleDossier) -> dict[str, TraitBundle]:
    return {bundle.bundle_id: bundle for bundle in dossier.candidates}


def _normalize_frontier_ids(
    *,
    dossier: CandidateBundleDossier,
    cards: list[CandidateEvidenceCard],
    candidate_ids: list[str],
) -> list[str]:
    card_lookup = {card.bundle_id: card for card in cards}
    ordered: list[str] = []
    seen: set[str] = set()
    for raw in candidate_ids:
        bundle_id = str(raw or "").strip()
        if not bundle_id or bundle_id in seen:
            continue
        bundle = _bundle_lookup(dossier).get(bundle_id)
        if bundle is None or is_self_like_bundle(dossier.target, bundle):
            continue
        if bundle_id not in card_lookup:
            continue
        seen.add(bundle_id)
        ordered.append(bundle_id)
        if len(ordered) >= 3:
            break
    return ordered


def _build_target_summary(
    dossier: CandidateBundleDossier,
    *,
    benchmark_family: str,
    config: TransferConfig,
) -> dict[str, Any]:
    return {
        "target_id": dossier.target.target_id,
        "target_code": dossier.target.target_code,
        "target_label": dossier.target.target_label,
        "aliases": dossier.target.aliases,
        "target_type": dossier.target.target_type,
        "benchmark_family": benchmark_family,
        "selection_policy": {
            "shortlist_strategy": config.shortlist_strategy,
            "apply_gc_resolution_discount": config.apply_gc_resolution_discount,
            "allow_ot_promotion": config.allow_ot_promotion,
        },
    }


def _build_judge_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRANSFER_FRONTIER_JUDGE_PROMPT),
            (
                "human",
                "Select the transfer frontier from the context below.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        JudgeFrontierSelection,
        method="function_calling",
    )
    return prompt | structured


def _build_verify_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRANSFER_FRONTIER_VERIFY_PROMPT),
            (
                "human",
                "Verify the proposed selection against the evidence cards.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        VerifiedSelection,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_judge_chain():
    return _build_judge_chain()


@lru_cache(maxsize=1)
def _cached_verify_chain():
    return _build_verify_chain()


def _judge_frontier(
    evidence_state: EvidenceState,
    default_frontier_ids: list[str],
    default_mode: DecisionMode,
) -> JudgeFrontierSelection:
    context = {
        "target_summary": evidence_state.target_summary,
        "available_tools": evidence_state.available_tools,
        "shortlist_bundle_ids": evidence_state.shortlist_bundle_ids,
        "candidate_cards": [card.model_dump() for card in evidence_state.candidate_cards],
        "default_frontier_ids": default_frontier_ids,
        "default_decision_mode": default_mode,
    }
    try:
        return _cached_judge_chain().invoke({"context_json": json.dumps(context, ensure_ascii=False)})
    except Exception:
        return JudgeFrontierSelection(
            primary_bundle_id=default_frontier_ids[0] if default_frontier_ids else None,
            frontier_bundle_ids=default_frontier_ids,
            confidence="Moderate" if default_mode == "frontier_uncertain" else "High",
            decision_mode=default_mode,
            rationale="Deterministic fallback selected the frontier from the highest-utility evidence cards.",
            evidence_tags=[],
        )


def _verify_selection(
    evidence_state: EvidenceState,
    proposed: JudgeFrontierSelection,
    selected_cards: list[CandidateEvidenceCard],
) -> VerifiedSelection:
    context = {
        "target_summary": evidence_state.target_summary,
        "candidate_cards": [card.model_dump() for card in evidence_state.candidate_cards],
        "selected_cards": [card.model_dump() for card in selected_cards],
        "proposed_selection": proposed.model_dump(),
    }
    try:
        return _cached_verify_chain().invoke({"context_json": json.dumps(context, ensure_ascii=False)})
    except Exception:
        visible_tags = sorted({tag for card in selected_cards for tag in card.evidence_tags})
        return VerifiedSelection(
            confidence=proposed.confidence,
            decision_mode=proposed.decision_mode,
            rationale=proposed.rationale,
            evidence_tags=visible_tags[:8],
            supported=True,
            issues=[],
            revised_primary_bundle_id=None,
            revised_frontier_bundle_ids=[],
        )


def _finalize_frontier_decision(
    dossier: CandidateBundleDossier,
    evidence_state: EvidenceState,
    judged: JudgeFrontierSelection,
    *,
    config: TransferConfig,
) -> CrossTraitTransferFrontierDecision:
    cards_by_id = {card.bundle_id: card for card in evidence_state.candidate_cards}
    normalized_frontier_ids = _normalize_frontier_ids(
        dossier=dossier,
        cards=evidence_state.candidate_cards,
        candidate_ids=judged.frontier_bundle_ids or ([judged.primary_bundle_id] if judged.primary_bundle_id else []),
    )
    if not normalized_frontier_ids:
        normalized_frontier_ids = _default_frontier_ids(
            evidence_state.candidate_cards,
            _decision_mode_from_cards(evidence_state.candidate_cards),
        )

    primary_bundle_id = judged.primary_bundle_id if judged.primary_bundle_id in normalized_frontier_ids else None
    if primary_bundle_id is None and normalized_frontier_ids:
        primary_bundle_id = normalized_frontier_ids[0]
    if primary_bundle_id and primary_bundle_id not in normalized_frontier_ids:
        normalized_frontier_ids = [primary_bundle_id, *normalized_frontier_ids][:3]

    selected_cards = [cards_by_id[bundle_id] for bundle_id in normalized_frontier_ids if bundle_id in cards_by_id]
    if not selected_cards:
        return CrossTraitTransferFrontierDecision(
            primary_bundle_id=None,
            frontier_bundle_ids=[],
            frontier_bundle_weights={},
            candidate_pgs_ids_union=[],
            confidence="Low",
            decision_mode="abstain_only_if_no_valid_bundle",
            rationale="No valid non-self candidate bundle remained after evidence filtering.",
            evidence_state=evidence_state,
            bundle_evidence_tags={},
            outcome="NO_MATCH",
            best_bundle_id=None,
            best_cross_trait=None,
            candidate_pgs_ids=[],
        )

    verified = _verify_selection(evidence_state, judged, selected_cards)
    if config.allow_ot_promotion and (verified.revised_frontier_bundle_ids or verified.revised_primary_bundle_id):
        revised_candidate_ids = list(verified.revised_frontier_bundle_ids)
        if verified.revised_primary_bundle_id:
            revised_candidate_ids = [verified.revised_primary_bundle_id, *revised_candidate_ids]
        revised_frontier_ids = _normalize_frontier_ids(
            dossier=dossier,
            cards=evidence_state.candidate_cards,
            candidate_ids=revised_candidate_ids,
        )
        if revised_frontier_ids:
            normalized_frontier_ids = revised_frontier_ids
            primary_bundle_id = (
                verified.revised_primary_bundle_id
                if verified.revised_primary_bundle_id in normalized_frontier_ids
                else normalized_frontier_ids[0]
            )
            selected_cards = [cards_by_id[bundle_id] for bundle_id in normalized_frontier_ids if bundle_id in cards_by_id]

    bundle_weights_raw = {
        card.bundle_id: max(card.utility_score, 0.01)
        for card in selected_cards
    }
    weight_total = sum(bundle_weights_raw.values()) or 1.0
    frontier_bundle_weights = {
        bundle_id: round(weight / weight_total, 4)
        for bundle_id, weight in bundle_weights_raw.items()
    }

    candidate_pgs_ids_union: list[str] = []
    seen_pgs: set[str] = set()
    for card in selected_cards:
        for pgs_id in card.candidate_pgs_ids:
            if pgs_id not in seen_pgs:
                seen_pgs.add(pgs_id)
                candidate_pgs_ids_union.append(pgs_id)

    primary_card = cards_by_id.get(primary_bundle_id) if primary_bundle_id else None
    decision_mode = verified.decision_mode
    if decision_mode == "single_confident":
        if len(selected_cards) < 2:
            supplemental_cards = [
                card
                for card in evidence_state.candidate_cards
                if card.bundle_id not in {selected.bundle_id for selected in selected_cards}
            ]
            if supplemental_cards:
                selected_cards = [*selected_cards, supplemental_cards[0]]
        if len(selected_cards) > 2:
            selected_cards = selected_cards[:2]
        normalized_frontier_ids = [card.bundle_id for card in selected_cards]
        raw_weights = {card.bundle_id: max(card.utility_score, 0.01) for card in selected_cards}
        total = sum(raw_weights.values()) or 1.0
        frontier_bundle_weights = {bid: round(w / total, 4) for bid, w in raw_weights.items()}
        candidate_pgs_ids_union = []
        seen_pgs_recompute: set[str] = set()
        for card in selected_cards:
            for pgs_id in card.candidate_pgs_ids:
                if pgs_id not in seen_pgs_recompute:
                    seen_pgs_recompute.add(pgs_id)
                    candidate_pgs_ids_union.append(pgs_id)
        primary_card = cards_by_id.get(primary_bundle_id) if primary_bundle_id else selected_cards[0]
    elif decision_mode == "abstain_only_if_no_valid_bundle" and primary_card is not None:
        decision_mode = "frontier_uncertain"

    bundle_evidence_tags = {card.bundle_id: card.evidence_tags for card in selected_cards}
    visible_tags = {tag for card in selected_cards for tag in card.evidence_tags}
    verified_tags = [tag for tag in verified.evidence_tags if tag in visible_tags][:12]

    rationale = verified.rationale
    if verified_tags:
        rationale = f"{rationale} Evidence tags: {', '.join(verified_tags)}."

    return CrossTraitTransferFrontierDecision(
        primary_bundle_id=primary_card.bundle_id if primary_card else None,
        frontier_bundle_ids=[card.bundle_id for card in selected_cards],
        frontier_bundle_weights=frontier_bundle_weights,
        candidate_pgs_ids_union=candidate_pgs_ids_union,
        confidence=verified.confidence,
        decision_mode=decision_mode,
        rationale=rationale.strip(),
        evidence_state=evidence_state,
        bundle_evidence_tags=bundle_evidence_tags,
        outcome="MATCHED" if primary_card else "NO_MATCH",
        best_bundle_id=primary_card.bundle_id if primary_card else None,
        best_cross_trait=primary_card.canonical_label if primary_card else None,
        candidate_pgs_ids=candidate_pgs_ids_union,
    )


def run_cross_trait_agent(
    dossier: CandidateBundleDossier,
    condition: Literal["gpt-only", "dossier-only", "gc-only", "gc-h2", "all-tools"],
    bundles: list[TraitBundle] | None = None,
    toolbox: CrossTraitToolbox | None = None,
    max_steps: int = 8,
    enable_semantic_backstop: bool = True,
    enable_forced_match: bool = True,
    benchmark_family: str = "binary_to_binary",
) -> dict[str, Any]:
    del max_steps, enable_semantic_backstop, enable_forced_match
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    if toolbox is None and bundles is None:
        raise ValueError("Either bundles or toolbox must be provided.")
    if toolbox is None:
        assert bundles is not None
        toolbox = CrossTraitToolbox(bundles)

    config = BENCHMARK_FAMILY_CONFIGS.get(benchmark_family, DEFAULT_CONFIG)
    available_tools = CONDITION_TOOLS[condition]
    candidate_bundle_ids = [
        bundle.bundle_id
        for bundle in dossier.candidates
        if not is_self_like_bundle(dossier.target, bundle)
    ]
    bundle_lookup = _bundle_lookup(dossier)

    tool_trace: list[dict[str, Any]] = []
    gc_result: dict[str, Any] | None = None
    if "cross_trait_genetic_correlation" in available_tools:
        gc_result = toolbox.cross_trait_genetic_correlation(
            dossier.target.target_label,
            candidate_bundle_ids,
            response_format="concise",
        )
        tool_trace.append(
            {
                "name": "cross_trait_genetic_correlation",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": candidate_bundle_ids,
                    "response_format": "concise",
                },
                "result": gc_result,
            }
        )
    gc_lookup = _gc_lookup(gc_result)

    provisional_cards = [
        _build_candidate_card(
            dossier,
            bundle_lookup[bundle_id],
            gc_row=gc_lookup.get(bundle_id),
            config=config,
        )
        for bundle_id in candidate_bundle_ids
        if bundle_id in bundle_lookup
    ]

    if config.shortlist_strategy == "gc_first":
        provisional_cards = _sort_cards(provisional_cards)
        shortlist_ids = [card.bundle_id for card in provisional_cards[: config.shortlist_cap]]
    else:
        # binary-to-binary keeps the dual-track shortlist that protects semantic matches.
        gc_ranked = sorted(
            provisional_cards,
            key=lambda c: (-c.cheap_rank_score, -c.utility_score, c.bundle_id),
        )
        gc_shortlist = [card.bundle_id for card in gc_ranked[: config.gc_track_size]]
        semantic_ranked = sorted(
            provisional_cards,
            key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models),
        )
        semantic_shortlist = [card.bundle_id for card in semantic_ranked[: config.semantic_track_size]]
        same_endpoint_ids = [
            card.bundle_id
            for card in semantic_ranked
            if card.archetype == "same-endpoint disease"
        ][:3]
        shortlist_ids = list(dict.fromkeys(same_endpoint_ids + gc_shortlist + semantic_shortlist))[: config.shortlist_cap]

    h2_lookup: dict[str, dict[str, Any]] = {}
    if "cross_trait_heritability" in available_tools and shortlist_ids:
        h2_result = toolbox.cross_trait_heritability(
            dossier.target.target_label,
            shortlist_ids,
            ancestry="EUR",
            response_format="concise",
        )
        tool_trace.append(
            {
                "name": "cross_trait_heritability",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": shortlist_ids,
                    "ancestry": "EUR",
                    "response_format": "concise",
                },
                "result": h2_result,
            }
        )
        h2_lookup = _gc_lookup(h2_result)

    ot_lookup: dict[str, dict[str, Any]] = {}
    if "cross_trait_open_targets" in available_tools and shortlist_ids:
        ot_result = toolbox.cross_trait_open_targets(
            dossier.target.target_label,
            shortlist_ids,
            response_format="concise",
        )
        tool_trace.append(
            {
                "name": "cross_trait_open_targets",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": shortlist_ids,
                    "response_format": "concise",
                },
                "result": ot_result,
            }
        )
        ot_lookup = _gc_lookup(ot_result)

    cards = _sort_cards(
        [
            _build_candidate_card(
                dossier,
                bundle_lookup[bundle_id],
                gc_row=gc_lookup.get(bundle_id),
                h2_row=h2_lookup.get(bundle_id),
                ot_row=ot_lookup.get(bundle_id),
                config=config,
            )
            for bundle_id in shortlist_ids
            if bundle_id in bundle_lookup
        ]
    )

    if _needs_detailed_pass(cards):
        detailed_ids = [card.bundle_id for card in cards[:3]]
        if "cross_trait_genetic_correlation" in available_tools:
            detailed_gc = toolbox.cross_trait_genetic_correlation(
                dossier.target.target_label,
                detailed_ids,
                response_format="detailed",
            )
            tool_trace.append(
                {
                    "name": "cross_trait_genetic_correlation",
                    "args": {
                        "target_trait": dossier.target.target_label,
                        "candidate_bundle_ids": detailed_ids,
                        "response_format": "detailed",
                    },
                    "result": detailed_gc,
                }
            )
            gc_lookup.update(_gc_lookup(detailed_gc))
        if "cross_trait_heritability" in available_tools:
            detailed_h2 = toolbox.cross_trait_heritability(
                dossier.target.target_label,
                detailed_ids,
                ancestry="EUR",
                response_format="detailed",
            )
            tool_trace.append(
                {
                    "name": "cross_trait_heritability",
                    "args": {
                        "target_trait": dossier.target.target_label,
                        "candidate_bundle_ids": detailed_ids,
                        "ancestry": "EUR",
                        "response_format": "detailed",
                    },
                    "result": detailed_h2,
                }
            )
            h2_lookup.update(_gc_lookup(detailed_h2))
        if "cross_trait_open_targets" in available_tools:
            detailed_ot = toolbox.cross_trait_open_targets(
                dossier.target.target_label,
                detailed_ids,
                response_format="detailed",
            )
            tool_trace.append(
                {
                    "name": "cross_trait_open_targets",
                    "args": {
                        "target_trait": dossier.target.target_label,
                        "candidate_bundle_ids": detailed_ids,
                        "response_format": "detailed",
                    },
                    "result": detailed_ot,
                }
            )
            ot_lookup.update(_gc_lookup(detailed_ot))
        cards = _sort_cards(
            [
                _build_candidate_card(
                    dossier,
                    bundle_lookup[bundle_id],
                    gc_row=gc_lookup.get(bundle_id),
                    h2_row=h2_lookup.get(bundle_id),
                    ot_row=ot_lookup.get(bundle_id),
                    config=config,
                )
                for bundle_id in shortlist_ids
                if bundle_id in bundle_lookup
            ]
        )

    evidence_state = EvidenceState(
        available_tools=available_tools,
        shortlist_bundle_ids=[card.bundle_id for card in cards],
        target_summary=_build_target_summary(
            dossier,
            benchmark_family=benchmark_family,
            config=config,
        ),
        candidate_cards=cards,
    )

    default_mode = _decision_mode_from_cards(cards)
    default_frontier_ids = _default_frontier_ids(cards, default_mode)
    judged = _judge_frontier(evidence_state, default_frontier_ids, default_mode)
    decision = _finalize_frontier_decision(
        dossier,
        evidence_state,
        judged,
        config=config,
    )

    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "tool_trace": tool_trace,
        "gc_prescreening_count": len((gc_result or {}).get("results", [])),
        "semantic_backstop_decision": None,
        "decision": decision.model_dump(),
    }


def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False))
