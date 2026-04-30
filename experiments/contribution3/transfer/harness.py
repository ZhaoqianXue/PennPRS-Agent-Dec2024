"""Execution harness for the LLM-led transfer agent.

Responsibilities:
- Enforce a hard `BudgetGuard` on tool calls (observability only, never
  overrides LLM selection).
- Dispatch `ToolCall` objects emitted by the LLM to the concrete tool
  functions in `tools/`, catch errors, and return structured results.
- Drop invalid bundle / pgs IDs (tagging `harness:drop_invalid_id`) without
  substituting replacement IDs.

No scoring, no ranking, no merging. If you find yourself sorting or
thresholding anything inside this module, you have drifted from the plan.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

from experiments.contribution3.transfer.schemas import ToolCall
from experiments.contribution3.transfer.state import EvidenceRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# BudgetGuard
# ---------------------------------------------------------------------------

@dataclass
class BudgetGuard:
    max_tool_calls: int = 40
    consumed: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.max_tool_calls - self.consumed)

    def can_spend(self, n: int = 1) -> bool:
        return self.consumed + n <= self.max_tool_calls

    def spend(self, n: int = 1) -> None:
        self.consumed += n


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

class ToolDispatcher:
    """Maps ToolCall.tool string to a concrete callable.

    Tools are registered by name; unknown tool names raise ValueError. No
    hardcoded scoring or routing — the LLM chooses the tool, this class
    simply calls it.
    """

    def __init__(
        self,
        *,
        bundle_universe: dict[str, Any],
        target_label: str,
        target_aliases: list[str],
        registry: EvidenceRegistry,
        budget: BudgetGuard,
    ) -> None:
        self.bundle_universe = bundle_universe
        self.target_label = target_label
        self.target_aliases = target_aliases
        self.registry = registry
        self.budget = budget
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._handlers[name] = handler

    def is_known(self, name: str) -> bool:
        return name in self._handlers

    def call(self, tc: ToolCall, *, round_idx: int) -> dict[str, Any]:
        if tc.tool not in self._handlers:
            return {
                "tool": tc.tool,
                "args": tc.args,
                "error": f"unknown_tool:{tc.tool}",
                "round_idx": round_idx,
            }
        if not self.budget.can_spend(1):
            return {
                "tool": tc.tool,
                "args": tc.args,
                "error": "budget_exhausted",
                "round_idx": round_idx,
            }
        self.budget.spend(1)
        try:
            result = self._handlers[tc.tool](**tc.args)
        except TypeError as exc:
            logger.warning("Tool %s argument error: %s", tc.tool, exc)
            return {"tool": tc.tool, "args": tc.args, "error": f"bad_args:{exc}", "round_idx": round_idx}
        except Exception as exc:  # noqa: BLE001 — tool errors must not halt the ReAct loop
            logger.warning("Tool %s raised: %s", tc.tool, exc)
            return {"tool": tc.tool, "args": tc.args, "error": f"runtime:{exc}", "round_idx": round_idx}
        self.registry.ingest(round_idx=round_idx, tool_name=tc.tool, args=tc.args, result=result)
        self._route_to_structured_slot(tc, result, round_idx)
        return {"tool": tc.tool, "args": tc.args, "result": result, "round_idx": round_idx}

    def _route_to_structured_slot(self, tc: ToolCall, result: Any, round_idx: int) -> None:
        """Write the tool result into the matching per-bundle structured
        slot on the EvidenceRegistry. Deterministic I/O routing, not a
        decision.
        """
        if not isinstance(result, (dict, list)):
            return
        args = tc.args if isinstance(tc.args, dict) else {}
        bundle_id = args.get("bundle_id")
        # If bundle_id wasn't provided, try to resolve from candidate_label
        # against the known bundle universe — hygiene only.
        if not bundle_id and (cand := args.get("candidate_label")):
            needle = str(cand).strip().lower()
            for bid, meta in self.bundle_universe.items():
                cand_label = (getattr(meta, "canonical_label", None) or "").strip().lower()
                if cand_label and cand_label == needle:
                    bundle_id = bid
                    break
        if tc.tool == "get_open_targets_overlap" and bundle_id and isinstance(result, dict):
            self.registry.set_ot(bundle_id, result, round_idx=round_idx)


# ---------------------------------------------------------------------------
# ID validation (hygiene, not reranking)
# ---------------------------------------------------------------------------

def filter_known_bundle_ids(
    candidate_ids: list[str],
    known_ids: set[str],
) -> tuple[list[str], list[str]]:
    """Return (kept_in_order, dropped) — preserves LLM's ordering.

    Per plan §12.1, the harness may drop IDs the LLM hallucinated, but
    must NEVER substitute a replacement.
    """
    kept: list[str] = []
    dropped: list[str] = []
    seen: set[str] = set()
    for bid in candidate_ids:
        if bid in known_ids and bid not in seen:
            kept.append(bid)
            seen.add(bid)
        else:
            dropped.append(bid)
    return kept, dropped
