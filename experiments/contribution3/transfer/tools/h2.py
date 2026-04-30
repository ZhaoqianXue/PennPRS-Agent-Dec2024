"""Heritability tool — returns all raw records, no source priority tier.

The old `get_best_estimate` applied a GWAS_ATLAS > UKBB_LDSC > PAN_UKB
priority tier that decided for the LLM; this tool returns the flat list
and lets the LLM weigh sample size / standard error / source itself.
"""
from __future__ import annotations

import logging
import json
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


def _estimate_to_dict(est) -> dict[str, Any]:
    return {
        "trait": getattr(est, "trait", None),
        "h2": float(est.h2_obs) if est.h2_obs is not None else None,
        "h2_se": float(est.h2_obs_se) if est.h2_obs_se is not None else None,
        "n_samples": int(est.n_samples) if est.n_samples else None,
        "method": getattr(est, "method", None),
        "ancestry": getattr(est, "population", None),
        "source": est.source.value if getattr(est, "source", None) is not None else None,
        "match_score": float(getattr(est, "match_score", 0.0) or 0.0),
    }


def get_heritability(
    trait_label: str,
    ancestry: str = "EUR",
    *,
    min_score: int = 70,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return all available heritability records for a trait, unsorted.

    The LLM sees every record's `source`, `n_samples`, `h2_se`, and method.
    No priority tiers, no "best" selection.
    """
    trait_label = str(trait_label or "").strip()
    if not trait_label:
        return []
    return [json.loads(row) for row in _get_heritability_cached(trait_label, ancestry, min_score, limit)]


@lru_cache(maxsize=4096)
def _get_heritability_cached(
    trait_label: str,
    ancestry: str,
    min_score: int,
    limit: int,
) -> tuple[str, ...]:
    try:
        # The underlying source clients lazy-load pandas DataFrames and are not
        # thread-safe on first access. Serialize searches so a 20-worker run
        # does not load the same files 20 times.
        with _SEARCH_LOCK:
            results = _get_aggregator().search(
                trait_label, ancestry=ancestry, min_score=min_score, limit=limit
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Heritability search failed for '%s': %s", trait_label, exc)
        return (json.dumps({"error": f"heritability_search_error:{exc}", "trait": trait_label}),)
    return tuple(json.dumps(_estimate_to_dict(est), sort_keys=True) for est in results)
