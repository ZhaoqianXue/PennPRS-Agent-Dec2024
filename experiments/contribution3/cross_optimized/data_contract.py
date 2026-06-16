from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "cross_optimized.v1"

FORBIDDEN_PROMPT_KEY_SUBSTRINGS = (
    "auc_matrix",
    "prs_adjauc",
    "benchmark_top",
    "oracle",
    "gpr",
    "regret",
    "auc_gain",
    "self_best_auc",
    "selected_model_auc",
    "selected_model_rank",
    "rank_fraction",
    "ground_truth",
)

FORBIDDEN_PROMPT_VALUE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"benchmark_top_model_id",
        r"benchmark_top_model_auc",
        r"oracle_pgs",
        r"oracle_model",
        r"selected_model_auc",
        r"selected_model_rank",
        r"selected_model_gpr",
        r"prs_adjauc",
        r"rootcode_auc",
        r"nontarget_auc",
        r"auc_gain_over_self",
        r"absolute_auc_regret",
        r"held[- ]out evaluation",
        r"empirical oracle",
        r"old target[- ]level rank",
        r"old target[- ]specific rank",
        r"previous run outcome",
        r"target[- ]specific learned answer",
        r"hit@top",
        r"top[- ]25%",
        r"top[- ]25\s+(breadth|coverage)",
        r"top 0\.5%",
        r"top 1%",
        r"early[-_ ]tail",
        r"early[-_ ]hit",
        r"extreme[-_ ]tail",
        r"extreme[-_ ]top",
        r"very top tail",
        r"predicted[- ]risk tail",
        r"all_of_us",
        r"allofus",
        r"aou_binary",
        r"aou_extend_trait",
        r"ground_truth_ranking",
    )
)


def clean_text(raw: Any) -> str:
    if raw is None:
        return ""
    try:
        import pandas as pd

        if pd.isna(raw):
            return ""
    except Exception:
        pass
    text = str(raw).strip()
    return "" if not text or text.lower() == "nan" else text


def compact_text(raw: Any, max_chars: int = 220) -> str:
    text = re.sub(r"\s+", " ", clean_text(raw)).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def split_multi_value(raw: Any) -> list[str]:
    text = clean_text(raw)
    if not text:
        return []
    values = re.split(r"[|;]", text)
    return [value.strip() for value in values if value and value.strip()]


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    stopwords = {"disease", "disorder", "syndrome", "trait", "of", "and", "the"}
    return " ".join(token for token in cleaned.split() if token not in stopwords)


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        key = normalize_text(value)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(value.strip())
    return out


@dataclass(frozen=True)
class TargetRecord:
    target_id: str
    input_type: str
    target_source: str
    label: str
    aliases: list[str] = field(default_factory=list)

    def to_prompt_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompactPgsRecord:
    pgs_id: str
    pgs_name: str
    reported_trait: str
    mapped_trait_labels: list[str]
    mapped_trait_ids: list[str]
    method: str
    method_details: str
    variant_count: int | None
    ancestry_gwas: str
    ancestry_training: str
    ancestry_evaluation: str
    publication: dict[str, str]
    release_date: str
    performance: dict[str, Any] = field(default_factory=dict)

    def to_prompt_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if not payload["performance"]:
            payload.pop("performance")
        return payload


@dataclass(frozen=True)
class CompactBundleRecord:
    bundle_id: str
    canonical_label: str
    bundle_type: str
    aliases: list[str]
    candidate_pgs_ids: list[str]
    n_models: int
    source_efo_ids: list[str] = field(default_factory=list)
    source_mondo_ids: list[str] = field(default_factory=list)

    def to_prompt_dict(self, candidate_pgs_ids: list[str] | None = None) -> dict[str, Any]:
        pgs_ids = candidate_pgs_ids if candidate_pgs_ids is not None else self.candidate_pgs_ids
        return {
            "bundle_id": self.bundle_id,
            "canonical_label": self.canonical_label,
            "bundle_type": self.bundle_type,
            "aliases": self.aliases[:5],
            "n_models": len(pgs_ids),
            "candidate_pgs_ids": pgs_ids,
            "source_efo_ids": self.source_efo_ids[:6],
            "source_mondo_ids": self.source_mondo_ids[:6],
        }


@dataclass(frozen=True)
class RetrievedBundle:
    bundle: CompactBundleRecord
    candidate_pgs_ids: list[str]
    lanes: list[str]
    position: int

    def to_prompt_dict(self) -> dict[str, Any]:
        row = self.bundle.to_prompt_dict(candidate_pgs_ids=self.candidate_pgs_ids)
        row["retrieval_lanes"] = self.lanes
        row["position"] = self.position
        return row
