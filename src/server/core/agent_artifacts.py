"""
Artifact utilities for context engineering.

This module implements the "Use the File System as Context" pattern:
- Persist large payloads to disk under `output/agent_artifacts/`
- Return a compact inline summary plus a stable artifact reference

All serialization is deterministic to preserve KV-cache friendliness.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Dict

from pydantic import BaseModel, Field


class ArtifactRef(BaseModel):
    artifact_id: str = Field(..., description="Stable artifact identifier (sha256 hex)")
    artifact_path: str = Field(..., description="Absolute path to artifact file")
    sha256: str = Field(..., description="SHA-256 of artifact content")
    content_type: str = Field(..., description="MIME type")
    bytes: int = Field(..., description="Artifact size in bytes")
    summary: str = Field("", description="Compact human/LLM-friendly summary")


def get_repo_root() -> Path:
    # src/server/core -> repo root is 3 levels up
    return Path(__file__).resolve().parents[3]


def get_artifacts_dir() -> Path:
    return get_repo_root() / "output" / "agent_artifacts"


def stable_json_dumps(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":")
    )


def stable_json_bytes(payload: Any) -> bytes:
    return stable_json_dumps(payload).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_bytes_if_missing(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)


_SENSITIVE_KEY_SUBSTRINGS = (
    "api_key",
    "apikey",
    "token",
    "authorization",
    "password",
    "secret",
    "bearer",
)


def redact_secrets(payload: Any) -> Any:
    """
    Best-effort redaction to ensure artifacts are human-safe.
    This is deterministic and only redacts values for sensitive keys.
    """
    if isinstance(payload, dict):
        out: Dict[str, Any] = {}
        for k, v in payload.items():
            k_str = str(k)
            k_lower = k_str.lower()
            if any(s in k_lower for s in _SENSITIVE_KEY_SUBSTRINGS):
                out[k_str] = "[REDACTED]"
            else:
                out[k_str] = redact_secrets(v)
        return out
    if isinstance(payload, list):
        return [redact_secrets(v) for v in payload]
    return payload


def estimate_tokens_from_bytes(data: bytes) -> int:
    # Rough heuristic: ~4 bytes per token (English-like text).
    return max(1, len(data) // 4)


def write_json_artifact(payload: Any, artifact_prefix: str, summary: str = "") -> ArtifactRef:
    safe_payload = redact_secrets(payload)
    data = stable_json_bytes(safe_payload)
    sha = _sha256_hex(data)
    filename = f"{artifact_prefix}_{sha[:12]}.json"
    path = get_artifacts_dir() / filename
    _write_bytes_if_missing(path, data)
    return ArtifactRef(
        artifact_id=sha,
        artifact_path=str(path),
        sha256=sha,
        content_type="application/json",
        bytes=len(data),
        summary=summary
    )


def maybe_externalize_json(
    payload: Any,
    artifact_prefix: str,
    max_inline_bytes: int,
    max_inline_tokens: Optional[int],
    summary_builder: Callable[[Any], Any]
) -> Tuple[Any, Optional[ArtifactRef]]:
    """
    If the payload is small enough, return it inline.
    Otherwise, persist the full payload to disk and return a compact summary inline.
    """
    safe_payload = redact_secrets(payload)
    data = stable_json_bytes(safe_payload)
    token_estimate = estimate_tokens_from_bytes(data)
    within_bytes = len(data) <= max_inline_bytes
    within_tokens = True if max_inline_tokens is None else token_estimate <= max_inline_tokens
    if within_bytes and within_tokens:
        return safe_payload, None

    summary = redact_secrets(summary_builder(safe_payload))
    artifact = write_json_artifact(
        payload=safe_payload,
        artifact_prefix=artifact_prefix,
        summary="Large payload persisted to disk for restorable context."
    )
    return summary, artifact

