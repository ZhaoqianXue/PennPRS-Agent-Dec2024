"""Cross-Trait Transfer domain-knowledge skill (peer to contribution2).

Mirrors prs_model_domain_knowledge() in src/server/core/tools/
prs_model_tools.py — same retrieval architecture, separate KB. Loaded
by agent.py and injected into per-stage `context_json` as the
`domain_knowledge` field. Each stage requests its own slice via
`stage=...`.

Skill layering (Agent Skills, three-level progressive disclosure):
- Level 1 metadata: this docstring + the function signature.
- Level 2 body: stage-conditional KB sections returned via primary_section.
- Level 3 resources: deferred (heritability tables, ancestry priors etc.
  not loaded for parity-with-P21 task; structure does not preclude later
  extension).

CFG-aware filtering: when a `ToolAblationConfig` is passed, sentences
referring to disabled tools (gc/ot/h2/biology) are stripped from the
returned text. This keeps the LLM from being primed to look for
signals from tools that are absent — essential for strict ablation.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Literal, Optional, Tuple, TYPE_CHECKING

from pydantic import BaseModel, Field

from src.server.core.tools.prs_model_tools import (
    _calculate_relevance,
    _expand_domain_query_terms,
    _extract_target_trait_phrase,
    _parse_markdown_sections,
)

if TYPE_CHECKING:
    from experiments.contribution3.transfer.agent import ToolAblationConfig

KB_PATH = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "cross_trait_domain_knowledge.md"
)

STAGE_TO_SECTION_PREFIX = {
    "scout":           "1. Bundle Selection Heuristics",
    "gather":          "2. Evidence Channel Hierarchy",
    "judge":           "3. Same-Trait vs Cross-Trait Bundle Ranking",
    "pick":            "4. PGS Transferability Signals",
    "global_primary":  "5. Cross-Bundle Reconciliation",
    "pgs_triage":      "6. PGS Triage",
    "critic":          "7. Critic Cross-Checks",
}

Stage = Literal["scout", "gather", "judge", "pick",
                "global_primary", "pgs_triage", "critic"]


class CrossTraitSnippet(BaseModel):
    section: str
    content: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class CrossTraitDomainKnowledgeResult(BaseModel):
    stage: str
    query: str
    primary_section: str = Field(
        description="The KB section dedicated to this stage. Always returned."
    )
    full_document: str = Field(
        description="Full KB markdown. Always returned for fallback context."
    )
    snippets: List[CrossTraitSnippet] = Field(
        default_factory=list,
        description=(
            "Extra sections ranked by query relevance (in addition to "
            "primary_section). Empty when query is empty or no other "
            "section meets the relevance threshold."
        ),
    )


def _filter_text_by_cfg(text: str, cfg) -> str:
    """Strip sentences referring to disabled tools/signals from KB text.

    Each line / list item in the KB markdown is treated as a unit:
    - A line referencing OT-specific terms (`OT`, `Open Targets`, `shared_targets`,
      `ot.shared_targets`, `shared_pathways`, `ot.phenotypes`) is dropped when
      `cfg.enable_ot=False`.
    - A line referencing GC-specific terms (`gc.rg`, `gc.p_value`,
      `gc.confidence`, `genetic correlation` (rg), `rg`-as-variable) is
      dropped when `cfg.enable_gc_batch=False`.
    - A line referencing h2-specific terms (`h2_candidate`, `h2_source`,
      `heritability`, `candidate h2`, `target h2`) is dropped when
      `cfg.enable_h2=False`.
    - A line referencing biology-helper terms (`biology-retrieval helper`,
      `biology retrieval`) is dropped when `cfg.enable_biology=False`.

    Lines that mention multiple signals (e.g., the cross-cutting note) are
    kept if any referenced signal is still enabled — they're shortened
    rather than removed.
    """
    if cfg is None:
        return text

    disabled_patterns: list[tuple[str, list[re.Pattern]]] = []
    if not cfg.enable_ot:
        disabled_patterns.append((
            "ot", [
                re.compile(r"\bOT\b"),
                re.compile(r"Open Targets", re.IGNORECASE),
                re.compile(r"\bshared_targets\b"),
                re.compile(r"\bshared_pathways\b"),
                re.compile(r"\bot\.\w+"),
                re.compile(r"shared-target", re.IGNORECASE),
                re.compile(r"shared targets", re.IGNORECASE),
            ]
        ))
    if not cfg.enable_gc_batch:
        disabled_patterns.append((
            "gc", [
                re.compile(r"\bgc\.\w+"),
                re.compile(r"\bgenetic correlation\b", re.IGNORECASE),
                re.compile(r"\brg\b"),
                re.compile(r"\babs_rg\b"),
                re.compile(r"\bp_value\b"),
            ]
        ))
    if not cfg.enable_h2:
        disabled_patterns.append((
            "h2", [
                re.compile(r"\bh2_candidate\b"),
                re.compile(r"\bh2_source\b"),
                re.compile(r"\bheritability\b", re.IGNORECASE),
                re.compile(r"\bcandidate h2\b", re.IGNORECASE),
                re.compile(r"\btarget h2\b", re.IGNORECASE),
                re.compile(r"\bh2\b"),
            ]
        ))
    if not cfg.enable_biology:
        disabled_patterns.append((
            "biology", [
                re.compile(r"biology[-\s]+retrieval", re.IGNORECASE),
                re.compile(r"biology[-\s]+notes?", re.IGNORECASE),
            ]
        ))

    if not disabled_patterns:
        return text

    out_lines: list[str] = []
    for line in text.splitlines():
        # STRICT POLICY: drop any line that references a disabled tool,
        # even if the same line also references enabled tools. This is
        # more aggressive than a "multi-signal pass-through" but avoids
        # ablation leakage where the LLM sees rg/OT/h2/biology terms in
        # the KB text and forms expectations from them.
        matched_disabled = any(
            any(p.search(line) for p in pats) for _, pats in disabled_patterns
        )
        if matched_disabled:
            continue
        out_lines.append(line)
    return "\n".join(out_lines)


def cross_trait_domain_knowledge(
    stage: Stage,
    query: str = "",
    max_snippets: int = 4,
    knowledge_file: Optional[str] = None,
    cfg: Optional["ToolAblationConfig"] = None,
) -> CrossTraitDomainKnowledgeResult:
    """Retrieve cross-trait transfer domain knowledge for one pipeline stage.

    Always returns the stage's primary section + full document. If `query`
    is non-empty, also returns up to `max_snippets` extra sections ranked
    by keyword relevance — mirrors prs_model_domain_knowledge's behavior.

    When `cfg` is provided, sentences referring to tools disabled by the
    cfg (e.g., `gc.rg` references when `cfg.enable_gc_batch=False`) are
    stripped from the returned text. When `cfg.enable_skill=False`, this
    function returns an empty result entirely — the LLM receives an
    empty `cross_trait_guidance` field at every stage.
    """
    # No-skill ablation: skill entirely disabled
    if cfg is not None and getattr(cfg, "enable_skill", True) is False:
        return CrossTraitDomainKnowledgeResult(
            stage=stage,
            query=query,
            primary_section="",
            full_document="",
            snippets=[],
        )
    kb_path = Path(knowledge_file) if knowledge_file else KB_PATH

    try:
        content = kb_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return CrossTraitDomainKnowledgeResult(
            stage=stage, query=query, primary_section="",
            full_document="", snippets=[],
        )

    sections: List[Tuple[str, str]] = _parse_markdown_sections(content)

    primary_prefix = STAGE_TO_SECTION_PREFIX.get(stage, "")
    primary_section_text = ""
    for title, body in sections:
        if title.strip().startswith(primary_prefix):
            primary_section_text = f"## {title}\n\n{body}"
            break

    # CFG-aware filtering pass
    primary_section_text = _filter_text_by_cfg(primary_section_text, cfg)
    full_document = _filter_text_by_cfg(content.strip(), cfg)

    snippets: List[CrossTraitSnippet] = []
    if query.strip():
        query_terms = _expand_domain_query_terms(query)
        target_trait_phrase = _extract_target_trait_phrase(query)
        scored = []
        for title, body in sections:
            if title.strip().startswith(primary_prefix):
                continue
            filtered_body = _filter_text_by_cfg(body, cfg)
            if not filtered_body.strip():
                continue
            score = _calculate_relevance(
                query_terms, title, filtered_body,
                target_trait_phrase=target_trait_phrase,
            )
            if score > 0:
                scored.append((title, filtered_body, score))
        scored.sort(key=lambda x: x[2], reverse=True)
        for title, body, score in scored[:max_snippets]:
            truncated = body[:500] + "..." if len(body) > 500 else body
            snippets.append(
                CrossTraitSnippet(
                    section=title,
                    content=truncated,
                    relevance_score=min(score / 10.0, 1.0),
                )
            )

    return CrossTraitDomainKnowledgeResult(
        stage=stage,
        query=query,
        primary_section=primary_section_text,
        full_document=full_document,
        snippets=snippets,
    )
