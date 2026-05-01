"""Shared heritability evidence tool.

This module exposes raw heritability records from the local aggregator for
LLM-led use. It deliberately does not pick a "best" estimate or apply source
priority tiers; callers see source, sample size, standard error, ancestry, and
match score and decide how to weigh them in context.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from threading import Lock
from typing import Any, Optional

from src.server.modules.heritability.aggregator import HeritabilityAggregator

logger = logging.getLogger(__name__)

_AGGREGATOR: Optional[HeritabilityAggregator] = None
_AGGREGATOR_LOCK = Lock()
_SEARCH_LOCK = Lock()


def _get_aggregator() -> HeritabilityAggregator:
    global _AGGREGATOR
    if _AGGREGATOR is None:
        with _AGGREGATOR_LOCK:
            if _AGGREGATOR is None:
                _AGGREGATOR = HeritabilityAggregator()
    return _AGGREGATOR


def _estimate_to_dict(est: Any) -> dict[str, Any]:
    return {
        "trait": getattr(est, "trait", None),
        "trait_name": getattr(est, "trait_name", None),
        "h2": float(est.h2_obs) if getattr(est, "h2_obs", None) is not None else None,
        "h2_liability": (
            float(est.h2_liability)
            if getattr(est, "h2_liability", None) is not None
            else None
        ),
        "h2_se": (
            float(est.h2_obs_se)
            if getattr(est, "h2_obs_se", None) is not None
            else None
        ),
        "h2_z": float(est.h2_z) if getattr(est, "h2_z", None) is not None else None,
        "n_samples": int(est.n_samples) if getattr(est, "n_samples", None) else None,
        "method": getattr(est, "method", None),
        "ancestry": getattr(est, "population", None),
        "source": (
            est.source.value
            if getattr(est, "source", None) is not None and hasattr(est.source, "value")
            else getattr(est, "source", None)
        ),
        "match_score": float(getattr(est, "match_score", 0.0) or 0.0),
    }


def get_heritability_records(
    trait_label: str,
    ancestry: str = "EUR",
    *,
    min_score: int = 70,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return raw matching heritability records for a trait.

    The returned list preserves the aggregator's source traversal order. No
    score, rank, threshold interpretation, or "best" record is added here.
    """
    trait_label = str(trait_label or "").strip()
    if not trait_label:
        return []
    return [
        json.loads(row)
        for row in _get_heritability_cached(trait_label, ancestry, min_score, limit)
    ]


@lru_cache(maxsize=4096)
def _get_heritability_cached(
    trait_label: str,
    ancestry: str,
    min_score: int,
    limit: int,
) -> tuple[str, ...]:
    try:
        # Source clients lazy-load data frames and are not thread-safe on first
        # access. Serialize searches so parallel harness workers do not load
        # the same files repeatedly.
        with _SEARCH_LOCK:
            results = _get_aggregator().search(
                trait_label,
                ancestry=ancestry,
                min_score=min_score,
                limit=limit,
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Heritability search failed for '%s': %s", trait_label, exc)
        return (
            json.dumps(
                {"error": f"heritability_search_error:{exc}", "trait": trait_label},
                sort_keys=True,
            ),
        )
    return tuple(json.dumps(_estimate_to_dict(est), sort_keys=True) for est in results)

