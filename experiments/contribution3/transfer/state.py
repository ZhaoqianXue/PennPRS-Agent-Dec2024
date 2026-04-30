"""Persistent structured state for the LLM-led cross-trait transfer agent.

`EvidenceRegistry` is the BioMedAgent-style persistent memory: structured
findings survive across Gather rounds even as raw tool JSON is truncated
from LLM context. Judge and Critic read only the Registry's compressed
digest (not the ReAct scratchpad) to enforce GeneAgent-style separation
between Generation and Self-Verification.

`ProvenanceLog` is the audit surface for Nature-MI-2026 transparency:
every final decision field is tagged with `source: str` and the only
legal prefixes are `llm:stage_{1..5}` or `harness:drop_invalid_id`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

SourceTag = str  # "llm:stage_1" .. "llm:stage_5" | "harness:drop_invalid_id"


# ---------------------------------------------------------------------------
# EvidenceRegistry
# ---------------------------------------------------------------------------

@dataclass
class BundleEvidence:
    """All structured evidence ever gathered for one candidate bundle."""

    bundle_id: str
    canonical_label: Optional[str] = None
    aliases: list[str] = field(default_factory=list)
    n_models: Optional[int] = None
    efo_ids: list[str] = field(default_factory=list)
    mondo_ids: list[str] = field(default_factory=list)

    # Raw tool outputs (flat-keyed so the LLM can cite a dot-path).
    gc: Optional[dict[str, Any]] = None
    h2_source: Optional[list[dict[str, Any]]] = None
    h2_candidate: Optional[list[dict[str, Any]]] = None
    ot: Optional[dict[str, Any]] = None

    # PGS model evidence — keyed by pgs_id.
    model_records: dict[str, dict[str, Any]] = field(default_factory=dict)

    # LLM-authored free-text observations, keyed by round index.
    notes: dict[int, str] = field(default_factory=dict)

    last_round: int = -1


@dataclass
class EvidenceRegistry:
    """Structured, persistent memory across all Gather rounds.

    Raw tool JSON lives in `round_tool_outputs` with a sliding window of
    `stale_rounds` — older entries are dropped from the prompt-facing
    history but their distilled form persists in `BundleEvidence`.
    """

    stale_rounds: int = 3
    _store: dict[str, BundleEvidence] = field(default_factory=dict)
    round_tool_outputs: dict[int, list[dict[str, Any]]] = field(default_factory=dict)

    # -- ingestion -----------------------------------------------------------

    def ensure(self, bundle_id: str) -> BundleEvidence:
        ev = self._store.get(bundle_id)
        if ev is None:
            ev = BundleEvidence(bundle_id=bundle_id)
            self._store[bundle_id] = ev
        return ev

    def ingest(
        self,
        *,
        round_idx: int,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
    ) -> None:
        """Attach a tool return to the appropriate bundle records.

        Tool-side translation: each tool module is responsible for calling
        the dedicated setter below (e.g., `set_gc(bundle_id, payload)`).
        `ingest` only logs the raw call for prompt history; structural
        ownership lives on `BundleEvidence` fields.
        """
        self.round_tool_outputs.setdefault(round_idx, []).append(
            {
                "tool": tool_name,
                "args": args,
                "result": result,
            }
        )

    def set_gc(self, bundle_id: str, payload: dict[str, Any], round_idx: int) -> None:
        ev = self.ensure(bundle_id)
        ev.gc = payload
        ev.last_round = max(ev.last_round, round_idx)

    def set_h2(
        self,
        *,
        bundle_id: str,
        source_h2: Optional[list[dict[str, Any]]],
        candidate_h2: Optional[list[dict[str, Any]]],
        round_idx: int,
    ) -> None:
        ev = self.ensure(bundle_id)
        if source_h2 is not None:
            ev.h2_source = source_h2
        if candidate_h2 is not None:
            ev.h2_candidate = candidate_h2
        ev.last_round = max(ev.last_round, round_idx)

    def set_ot(self, bundle_id: str, payload: dict[str, Any], round_idx: int) -> None:
        ev = self.ensure(bundle_id)
        ev.ot = payload
        ev.last_round = max(ev.last_round, round_idx)

    def set_bundle_meta(
        self,
        *,
        bundle_id: str,
        canonical_label: Optional[str],
        aliases: list[str],
        n_models: Optional[int],
        efo_ids: list[str],
        mondo_ids: list[str],
    ) -> None:
        ev = self.ensure(bundle_id)
        ev.canonical_label = canonical_label or ev.canonical_label
        ev.aliases = aliases or ev.aliases
        ev.n_models = n_models if n_models is not None else ev.n_models
        ev.efo_ids = efo_ids or ev.efo_ids
        ev.mondo_ids = mondo_ids or ev.mondo_ids

    def set_model_record(
        self, *, bundle_id: str, pgs_id: str, record: dict[str, Any], round_idx: int
    ) -> None:
        ev = self.ensure(bundle_id)
        ev.model_records[pgs_id] = record
        ev.last_round = max(ev.last_round, round_idx)

    def add_note(self, *, bundle_id: str, round_idx: int, note: str) -> None:
        if not note:
            return
        ev = self.ensure(bundle_id)
        ev.notes[round_idx] = note
        ev.last_round = max(ev.last_round, round_idx)

    # -- sliding window ------------------------------------------------------

    def truncate_raw_after(self, current_round: int) -> None:
        """Drop raw tool outputs older than `current_round - stale_rounds`."""
        cutoff = current_round - self.stale_rounds
        for r in list(self.round_tool_outputs.keys()):
            if r < cutoff:
                self.round_tool_outputs.pop(r, None)

    # -- consumers -----------------------------------------------------------

    def bundle_ids(self) -> list[str]:
        return list(self._store.keys())

    def get(self, bundle_id: str) -> Optional[BundleEvidence]:
        return self._store.get(bundle_id)

    def snapshot(self) -> dict[str, BundleEvidence]:
        return dict(self._store)

    def compress_for_prompt(self, max_chars: int = 40000, cfg=None) -> str:
        """Return a structured JSON digest suitable for Judge / Critic.

        The digest intentionally omits forbidden derived fields (archetype,
        utility_score, etc.) and exposes only raw evidence + LLM notes.

        When `cfg` is provided, fields for disabled tools (cfg.enable_X=False)
        are completely removed from the digest — not just set to None — so
        the LLM cannot form expectations about absent signals.
        """
        # Determine which fields to include
        include_gc = (cfg is None) or cfg.enable_gc_batch
        include_h2 = (cfg is None) or cfg.enable_h2
        include_ot = (cfg is None) or cfg.enable_ot

        digest: dict[str, dict[str, Any]] = {}
        for bundle_id, ev in self._store.items():
            row: dict[str, Any] = {
                "label": ev.canonical_label,
                "aliases": ev.aliases[:6] if ev.aliases else [],
                "n_models": ev.n_models,
                "efo_ids": ev.efo_ids,
                "mondo_ids": ev.mondo_ids,
                "model_records": {k: v for k, v in ev.model_records.items()},
                "notes": {str(k): v for k, v in sorted(ev.notes.items())},
            }
            if include_gc:
                row["gc"] = ev.gc
            if include_h2:
                row["h2_source"] = ev.h2_source
                row["h2_candidate"] = ev.h2_candidate
            if include_ot:
                row["ot"] = ev.ot
            digest[bundle_id] = row
        payload = json.dumps(digest, ensure_ascii=False, default=str)
        if len(payload) <= max_chars:
            return payload
        # Controlled truncation: trim `model_records` first, then notes,
        # then OT shared_targets arrays — never drop gc / h2 headline fields.
        for bundle_id in list(digest):
            digest[bundle_id]["model_records"] = {}
        payload = json.dumps(digest, ensure_ascii=False, default=str)
        if len(payload) <= max_chars:
            return payload
        for bundle_id in list(digest):
            digest[bundle_id]["notes"] = {}
        payload = json.dumps(digest, ensure_ascii=False, default=str)
        if len(payload) <= max_chars:
            return payload
        for bundle_id in list(digest):
            ot = digest[bundle_id].get("ot") or {}
            if isinstance(ot, dict) and "shared_targets" in ot:
                ot["shared_targets"] = ot["shared_targets"][:5]
        return json.dumps(digest, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# ProvenanceLog
# ---------------------------------------------------------------------------

LEGAL_SOURCE_PREFIXES: tuple[str, ...] = (
    "llm:stage_1",
    "llm:stage_2",
    "llm:stage_3",
    "llm:stage_4",
    "llm:stage_5",
    "harness:drop_invalid_id",
    "harness:breadth_floor",
    "harness:skill_reference_lane",
)


@dataclass
class ProvenanceEntry:
    field_path: str  # e.g. "ranked_bundles[2].bundle_id"
    value: Any
    source: SourceTag
    detail: Optional[str] = None


@dataclass
class ProvenanceLog:
    entries: list[ProvenanceEntry] = field(default_factory=list)

    def tag(self, *, field_path: str, value: Any, source: SourceTag, detail: Optional[str] = None) -> None:
        if not any(source == prefix or source.startswith(prefix + ":") for prefix in LEGAL_SOURCE_PREFIXES):
            raise ValueError(f"Illegal provenance source '{source}' for {field_path}")
        self.entries.append(ProvenanceEntry(field_path=field_path, value=value, source=source, detail=detail))

    def as_list(self) -> list[dict[str, Any]]:
        return [
            {"field_path": e.field_path, "value": e.value, "source": e.source, "detail": e.detail}
            for e in self.entries
        ]


# ---------------------------------------------------------------------------
# AgentTrace
# ---------------------------------------------------------------------------

HaltReason = Literal["llm_terminated", "budget_exhausted_before_done", "not_applicable"]


@dataclass
class RoundState:
    round_idx: int
    directive_json: dict[str, Any]
    tool_calls_executed: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentTrace:
    """Full decision trail for a single target transfer run."""

    target_id: str
    target_label: str

    scout_directive_json: Optional[dict[str, Any]] = None
    scout_biology_json: Optional[dict[str, Any]] = None  # tool output observability
    gather_rounds: list[RoundState] = field(default_factory=list)
    gather_halt_reason: HaltReason = "not_applicable"
    gather_tool_calls_consumed: int = 0
    h2_batch_json: Optional[dict[str, Any]] = None  # Stage 2.5 h2-batch observability
    gc_batch_json: Optional[dict[str, Any]] = None  # gc_batch_estimator output

    judge_output_json: Optional[dict[str, Any]] = None
    pick_output_json: Optional[dict[str, Any]] = None
    critic_output_json: Optional[dict[str, Any]] = None
    skill_reference_json: Optional[dict[str, Any]] = None

    # Tool-level observability (for ablation analysis):
    #   tool_call_counts: per tool name, number of successful invocations
    #     (LLM-driven via Gather + harness-driven for biology Scout / GC batch)
    #   tool_ablation_config: snapshot of which tools were enabled this run
    tool_call_counts: dict[str, int] = field(default_factory=dict)
    tool_ablation_config: Optional[dict[str, Any]] = None

    provenance: ProvenanceLog = field(default_factory=ProvenanceLog)

    def increment_tool_call(self, tool_name: str) -> None:
        self.tool_call_counts[tool_name] = self.tool_call_counts.get(tool_name, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_label": self.target_label,
            "scout": self.scout_directive_json,
            "scout_biology": self.scout_biology_json,
            "h2_batch": self.h2_batch_json,
            "gc_batch": self.gc_batch_json,
            "gather": {
                "halt_reason": self.gather_halt_reason,
                "tool_calls_consumed": self.gather_tool_calls_consumed,
                "rounds": [
                    {
                        "round_idx": r.round_idx,
                        "directive": r.directive_json,
                        "tool_calls_executed": r.tool_calls_executed,
                    }
                    for r in self.gather_rounds
                ],
            },
            "judge": self.judge_output_json,
            "pick": self.pick_output_json,
            "critic": self.critic_output_json,
            "skill_reference": self.skill_reference_json,
            "tool_call_counts": dict(self.tool_call_counts),
            "tool_ablation_config": self.tool_ablation_config,
            "provenance": self.provenance.as_list(),
        }
