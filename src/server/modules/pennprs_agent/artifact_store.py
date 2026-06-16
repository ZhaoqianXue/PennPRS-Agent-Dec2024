from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[4]

C2_RUN_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution2"
    / "recommendation"
    / "runs"
    / "pairwise-rerank-gpt-5.2-t1__89disease__round47-r38-fresh2-top5-holistic-hidden-cur89-20260503-021720"
)
C2_SOURCE_MANIFEST = (
    PROJECT_ROOT
    / "experiments"
    / "contribution2"
    / "recommendation"
    / "runs"
    / "minimal-lift-gpt-5.2-t1__89disease__iterD-final-cur89-t1-20260430-234950"
    / "experiment_minimal_lift_batch_manifest.json"
)
C3_RESULT_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "transfer"
    / "runs"
    / "tool_calling_agent"
    / "unified"
    / "ablation__no_all_tools_plus_pgs_skill"
    / "all-tools__paired80_pgs_skill_iter11_repeat2_20260430_024834_w20"
    / "results.json"
)
C3_DOSSIER_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "transfer"
    / "runs"
    / "tool_calling_agent"
    / "unified"
    / "candidate_dossiers.json"
)
C3_EVAL_SUMMARY_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "transfer"
    / "runs"
    / "tool_calling_agent"
    / "unified"
    / "ablation__no_all_tools_plus_pgs_skill"
    / "evaluation__paired80_pgs_skill_iter11_repeat2_20260430_024834_w20"
    / "all-tools__end_to_end_eval_summary.json"
)

CANONICAL_TRAIT_ALIASES: dict[str, tuple[str, ...]] = {
    "breast carcinoma": ("breast cancer", "breast neoplasm", "carcinoma of breast"),
    "coronary artery disease": ("cad", "coronary heart disease"),
    "late-onset alzheimer's disease": (
        "alzheimer disease",
        "alzheimer's disease",
        "late onset alzheimer disease",
        "late-onset alzheimer disease",
    ),
    "melanoma": ("cutaneous melanoma", "skin melanoma"),
    "prostate cancer": ("prostate carcinoma",),
    "type 2 diabetes mellitus": ("type 2 diabetes", "t2d", "t2dm"),
}


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    stopwords = {"trait", "disease", "disorder", "syndrome", "of", "and", "the"}
    tokens = [token for token in cleaned.split() if token not in stopwords]
    return " ".join(tokens)


def slugify(text: str, max_len: int = 52) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (cleaned or "target")[:max_len]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _score(query: str, label: str) -> float:
    q = normalize_text(query)
    c = normalize_text(label)
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    q_tokens = set(q.split())
    c_tokens = set(c.split())
    overlap = len(q_tokens & c_tokens) / max(1, len(q_tokens | c_tokens))
    containment = 0.0
    if q in c or c in q:
        containment = min(len(q), len(c)) / max(len(q), len(c))
    sequence = SequenceMatcher(None, q, c).ratio()
    return max(sequence, overlap, containment)


def _candidate_labels(meta: dict[str, Any]) -> list[str]:
    labels = [str(meta.get("ontology") or "")]
    for model in meta.get("candidate_models_visible_to_llm") or []:
        for key in ("trait_reported", "trait_efo", "phenotyping_reported"):
            raw = model.get(key)
            if isinstance(raw, list):
                labels.extend(str(item) for item in raw)
            elif raw:
                labels.append(str(raw))
    return [label for label in labels if label.strip()]


def _unique_labels(labels: list[str]) -> list[str]:
    seen: set[str] = set()
    unique = []
    for label in labels:
        normalized = normalize_text(label)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(label)
    return unique


def _canonical_labels(ontology: str) -> list[str]:
    labels = [ontology]
    labels.extend(CANONICAL_TRAIT_ALIASES.get((ontology or "").lower(), ()))
    return _unique_labels(labels)


def _exact_match(query: str, labels: list[str]) -> Optional[str]:
    query_norm = normalize_text(query)
    for label in labels:
        if normalize_text(label) == query_norm:
            return label
    return None


@lru_cache(maxsize=1)
def load_c2_artifacts() -> dict[str, Any]:
    results = _load_json(C2_RUN_DIR / "experiment_pairwise_rerank_results.json")
    stage1 = _load_json(C2_RUN_DIR / "experiment_pairwise_rerank_stage1_results.json")
    stage2 = _load_json(C2_RUN_DIR / "experiment_pairwise_rerank_stage2_results.json")
    manifest = _load_json(C2_SOURCE_MANIFEST)
    return {
        "results": results,
        "stage1_by_ontology": {row.get("ontology"): row for row in stage1},
        "stage2_by_ontology": {row.get("ontology"): row for row in stage2},
        "manifest": manifest,
        "metadata_by_ontology": {
            row.get("ontology"): row for row in manifest.get("disease_metadata") or []
        },
        "request_by_ontology": {
            row.get("ontology"): row for row in manifest.get("requests") or []
        },
    }


@lru_cache(maxsize=1)
def load_c3_results() -> list[dict[str, Any]]:
    return _load_json(C3_RESULT_PATH)


@lru_cache(maxsize=1)
def load_c3_dossiers() -> list[dict[str, Any]]:
    return _load_json(C3_DOSSIER_PATH)


@lru_cache(maxsize=1)
def load_c3_eval_summary() -> dict[str, Any]:
    return _load_json(C3_EVAL_SUMMARY_PATH)


def _c2_payload(
    artifacts: dict[str, Any],
    row: dict[str, Any],
    *,
    score: float,
    match_kind: str,
    matched_label: str,
) -> dict[str, Any]:
    ontology = row.get("ontology")
    return {
        "score": score,
        "match_kind": match_kind,
        "matched_label": matched_label,
        "result": row,
        "stage1": artifacts["stage1_by_ontology"].get(ontology),
        "stage2": artifacts["stage2_by_ontology"].get(ontology),
        "metadata": artifacts["metadata_by_ontology"].get(ontology),
        "request": artifacts["request_by_ontology"].get(ontology),
    }


def find_c2_artifact(
    target_trait: str,
    canonical_min_score: float = 0.72,
    fallback_min_score: float = 0.78,
) -> Optional[dict[str, Any]]:
    artifacts = load_c2_artifacts()

    for row in artifacts["results"]:
        ontology = row.get("ontology") or ""
        matched_label = _exact_match(target_trait, _canonical_labels(ontology))
        if matched_label:
            return _c2_payload(
                artifacts,
                row,
                score=1.0,
                match_kind="canonical_exact",
                matched_label=matched_label,
            )

    best_canonical: tuple[float, str, Optional[dict[str, Any]]] = (0.0, "", None)
    for row in artifacts["results"]:
        ontology = row.get("ontology") or ""
        for label in _canonical_labels(ontology):
            score = _score(target_trait, label)
            if score > best_canonical[0]:
                best_canonical = (score, label, row)
    if best_canonical[2] is not None and best_canonical[0] >= canonical_min_score:
        return _c2_payload(
            artifacts,
            best_canonical[2],
            score=best_canonical[0],
            match_kind="canonical_fuzzy",
            matched_label=best_canonical[1],
        )

    best_fallback: tuple[float, str, Optional[dict[str, Any]]] = (0.0, "", None)
    for row in artifacts["results"]:
        ontology = row.get("ontology") or ""
        meta = artifacts["metadata_by_ontology"].get(ontology) or {}
        for label in _candidate_labels(meta):
            score = _score(target_trait, label)
            if score > best_fallback[0]:
                best_fallback = (score, label, row)
    if best_fallback[2] is None or best_fallback[0] < fallback_min_score:
        return None
    return _c2_payload(
        artifacts,
        best_fallback[2],
        score=best_fallback[0],
        match_kind="candidate_label_fuzzy",
        matched_label=best_fallback[1],
    )


def find_c3_result(target_trait: str, min_score: float = 0.7) -> Optional[dict[str, Any]]:
    best: tuple[float, str, Optional[dict[str, Any]]] = (0.0, "", None)
    for row in load_c3_results():
        target = row.get("target") or {}
        labels = [target.get("target_label") or "", target.get("target_code") or ""]
        labels.extend(target.get("aliases") or [])
        matched_label = _exact_match(target_trait, [label for label in labels if label])
        if matched_label:
            return {
                "score": 1.0,
                "match_kind": "target_exact",
                "matched_label": matched_label,
                "result": row,
            }
        score = max((_score(target_trait, label) for label in labels if label), default=0.0)
        if score > best[0]:
            matched_label = max((label for label in labels if label), key=lambda label: _score(target_trait, label), default="")
            best = (score, matched_label, row)
    if best[2] is None or best[0] < min_score:
        return None
    return {
        "score": best[0],
        "match_kind": "target_fuzzy",
        "matched_label": best[1],
        "result": best[2],
    }


def find_c3_dossier(target_trait: str, min_score: float = 0.7) -> Optional[dict[str, Any]]:
    best: tuple[float, Optional[dict[str, Any]]] = (0.0, None)
    for dossier in load_c3_dossiers():
        target = dossier.get("target") or {}
        labels = [target.get("target_label") or "", target.get("target_code") or ""]
        labels.extend(target.get("aliases") or [])
        if _exact_match(target_trait, [label for label in labels if label]):
            return dossier
        score = max((_score(target_trait, label) for label in labels if label), default=0.0)
        if score > best[0]:
            best = (score, dossier)
    if best[1] is None or best[0] < min_score:
        return None
    return best[1]


def format_candidate_model_preview(candidate: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if not candidate:
        return None
    perf = candidate.get("performance_metrics") or {}
    publication = candidate.get("publication") if isinstance(candidate.get("publication"), dict) else {}
    return {
        "id": candidate.get("id"),
        "name": candidate.get("id"),
        "trait": candidate.get("trait_reported") or candidate.get("trait_efo") or "Unknown",
        "ancestry": candidate.get("ancestry_distribution") or "N/A",
        "method": candidate.get("method_name") or "Unknown",
        "metrics": {
            "AUC": perf.get("auc") or perf.get("pgs_only_auc") or perf.get("full_model_auc"),
            "R2": perf.get("r2") or perf.get("pgs_only_r2") or perf.get("full_model_r2"),
        },
        "source": "PGS Catalog",
        "num_variants": candidate.get("variants_number") or 0,
        "sample_size": _parse_sample_size(candidate.get("samples_training")),
        "dev_cohorts": ", ".join(candidate.get("training_development_cohorts") or []),
        "publication": {
            "date": "",
            "citation": publication.get("title") or "Stored PGS Catalog artifact",
            "id": "",
            "doi": "",
        },
    }


def selected_candidate_summary(metadata: Optional[dict[str, Any]], pgs_id: Optional[str]) -> Optional[dict[str, Any]]:
    if not metadata or not pgs_id:
        return None
    for candidate in metadata.get("candidate_models_visible_to_llm") or []:
        if candidate.get("id") == pgs_id:
            return candidate
    return None


def _parse_sample_size(raw: Any) -> Optional[int]:
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    match = re.search(r"n\s*=\s*([0-9,]+)", str(raw))
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def cached_examples() -> list[dict[str, Any]]:
    return [
        {
            "id": "breast-carcinoma",
            "label": "Breast cancer",
            "target_trait": "breast carcinoma",
            "area": "cancer",
            "expected_path": "same_trait",
            "description": "A direct same-trait PGS baseline is accepted without transfer escalation.",
        },
        {
            "id": "melanoma",
            "label": "Melanoma",
            "target_trait": "melanoma",
            "area": "cancer",
            "expected_path": "same_trait",
            "description": "A cancer example with a sufficient same-trait recommendation.",
        },
        {
            "id": "alzheimer-disease",
            "label": "Alzheimer disease",
            "target_trait": "late-onset Alzheimer's disease",
            "area": "neurodegenerative disease",
            "expected_path": "conditional_transfer",
            "description": "A weak same-trait baseline triggers cross-trait transfer evaluation.",
        },
        {
            "id": "bipolar-disorder",
            "label": "Bipolar disorder",
            "target_trait": "bipolar disorder",
            "area": "mental health",
            "expected_path": "conditional_transfer",
            "description": "A low-confidence direct baseline escalates to transfer evidence.",
        },
        {
            "id": "coronary-artery-disease",
            "label": "Coronary artery disease",
            "target_trait": "coronary artery disease",
            "area": "cardiovascular disease",
            "expected_path": "same_trait",
            "description": "A direct cardiovascular baseline is accepted before transfer is considered.",
        },
        {
            "id": "type-2-diabetes",
            "label": "Type 2 diabetes",
            "target_trait": "type 2 diabetes mellitus",
            "area": "metabolic disease",
            "expected_path": "same_trait",
            "description": "A metabolic disease case with a sufficient same-trait model.",
        },
    ]
