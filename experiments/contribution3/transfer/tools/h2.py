"""Contribution3 heritability tool wrapper.

The implementation lives in ``src.server.core.tools.heritability`` so c2 and
c3 consume the same raw h2 evidence contract.
"""
from __future__ import annotations

from typing import Any

from src.server.core.tools.heritability import get_heritability_records


def get_heritability(
    trait_label: str,
    ancestry: str = "EUR",
    *,
    min_score: int = 70,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return raw heritability records for LLM-led case-by-case use."""
    return get_heritability_records(
        trait_label=trait_label,
        ancestry=ancestry,
        min_score=min_score,
        limit=limit,
    )

