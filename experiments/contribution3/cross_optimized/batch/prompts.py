from __future__ import annotations

import json
from pathlib import Path

from experiments.contribution3.cross_optimized.paths import CROSS_OPT_DIR


SKILL_PATH = CROSS_OPT_DIR / "skills" / "cross_transfer" / "SKILL.md"


def load_cross_transfer_skill() -> str:
    text = SKILL_PATH.read_text(encoding="utf-8")
    return text.strip()


STAGE_A_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "selected_bundle_ids": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 12,
        },
        "frontier_bundle_ids": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 24,
        },
        "abstain": {"type": "boolean"},
        "rationale": {"type": "string"},
        "evidence_cited": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 24,
        },
    },
    "required": ["selected_bundle_ids", "frontier_bundle_ids", "abstain", "rationale", "evidence_cited"],
}


STAGE_B_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "primary_pgs_id": {"type": "string"},
        "source_bundle_id": {"type": "string"},
        "frontier_pgs_ids": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 12,
        },
        "confidence": {"type": "string", "enum": ["low", "moderate", "high"]},
        "rationale": {"type": "string", "maxLength": 900},
        "evidence_cited": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 12,
        },
    },
    "required": [
        "primary_pgs_id",
        "source_bundle_id",
        "frontier_pgs_ids",
        "confidence",
        "rationale",
        "evidence_cited",
    ],
}


STAGE_C_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "accepted": {"type": "boolean"},
        "primary_pgs_id": {"type": "string"},
        "source_bundle_id": {"type": "string"},
        "frontier_pgs_ids": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 12,
        },
        "issues": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 12,
        },
        "rationale": {"type": "string", "maxLength": 900},
    },
    "required": ["accepted", "primary_pgs_id", "source_bundle_id", "frontier_pgs_ids", "issues", "rationale"],
}


def response_json_schema(name: str, schema: dict) -> dict:
    return {
        "type": "json_schema",
        "name": name,
        "strict": True,
        "schema": schema,
    }


def static_system_prompt(stage: str) -> str:
    skill = load_cross_transfer_skill()
    stage_instruction = {
        "stage_a": (
            "Stage A task: select a small set of source bundles from compact "
            "metadata cards. Preserve plausible alternatives in the frontier."
        ),
        "stage_b": (
            "Stage B task: act as a chunk-local recall picker. Select a provisional "
            "primary PGS from fixed source bundles and return a broad, diverse frontier "
            "for Stage C. Do not expand to new bundles."
        ),
        "stage_c": (
            "Stage C task: act as the cross-bundle Primary Reconciler. Several "
            "local or tournament pickers have proposed PGS frontiers, but they "
            "could not compare all source axes together. Pick one final primary "
            "PGS only from the provided frontier records, then keep an ordered "
            "frontier. Decide source fit first, then use PGS metadata to break "
            "within-source or close-source ties. Do not choose a broader proxy "
            "from support counts, method branding, scale, recency, or validation "
            "breadth alone unless its source remains a coherent transfer source."
        ),
    }[stage]
    return "\n\n".join(
        [
            "You are a cross-trait PRS transfer judge.",
            "Use only the fields in the user payload. Treat missing evidence as unavailable; do not assume access to hidden files, private data, external calculations, or prior decisions.",
            "Cite evidence fields by ID or field path. Keep output compact; rationale fields must be <=120 words.",
            stage_instruction,
            "# Skill",
            skill,
        ]
    )


def dumps_compact(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
