"""Domain-knowledge loader shared by transfer LLM chains.

Loads `src/server/core/knowledge/prs_model_domain_knowledge.md`.

The same md is shared with contribution2's recommendation pipeline.
- contribution2 reads sections 1-7 (PGS-model field-level knowledge).
- contribution3 / transfer reads sections 1-8 (adds the cross-trait
  transfer section).

Section 8 is split off via the `## 8. Cross-trait transfer considerations`
header so that the boundary is data-driven (no version handling here).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOMAIN_KNOWLEDGE_MD = PROJECT_ROOT / "src" / "server" / "core" / "knowledge" / "prs_model_domain_knowledge.md"

CROSS_TRAIT_SECTION_HEADER = "## 8. Cross-trait transfer considerations"


@lru_cache(maxsize=2)
def load_domain_knowledge(*, include_cross_trait: bool) -> str:
    """Return the knowledge-base text injected into transfer LLM prompts.

    When ``include_cross_trait`` is False the section header at section 8
    onwards is stripped, matching what contribution2 sees today.
    """
    text = DOMAIN_KNOWLEDGE_MD.read_text()
    if include_cross_trait:
        return text.rstrip() + "\n"
    idx = text.find("\n" + CROSS_TRAIT_SECTION_HEADER)
    if idx < 0:
        return text.rstrip() + "\n"
    return text[:idx].rstrip() + "\n"


@lru_cache(maxsize=1)
def load_cross_trait_section_only() -> str:
    """Return ONLY the cross-trait transfer section (section 8) of the
    domain knowledge md.

    Use this when prompts are already lean (role/IO/constraints only)
    and only need cross-trait guidance — avoids dragging the full PGS
    field-level knowledge (sections 1-7) into every transfer LLM call.
    """
    text = DOMAIN_KNOWLEDGE_MD.read_text()
    idx = text.find(CROSS_TRAIT_SECTION_HEADER)
    if idx < 0:
        return ""
    return text[idx:].rstrip() + "\n"


@lru_cache(maxsize=8)
def load_cross_trait_subsection(subsection_id: str) -> str:
    """Return one ### 8.x subsection of the cross-trait section.

    `subsection_id` is the leading numeric tag, e.g. "8.1", "8.3".
    The returned text starts with the `### 8.x ...` header and ends
    just before the next `### ` (or section end). Returns empty string
    if not found.

    Used for per-stage minimal-injection: each transfer stage receives
    only the cross-trait subsection that is directly relevant to its
    decision (Scout 8.1, Judge 8.2, Pick 8.3, Reconcile 8.4, Triage
    8.5). Compared to injecting the whole section 8 (~6K chars), this
    typically injects ~1K and minimises LLM attention shift on stages
    that already have well-tuned prompts.
    """
    text = DOMAIN_KNOWLEDGE_MD.read_text()
    header_marker = f"### {subsection_id} "
    start = text.find(header_marker)
    if start < 0:
        return ""
    # Find next "### " (any subsection) or "## " (next section) or EOF.
    after = start + len(header_marker)
    next_sub = text.find("\n### ", after)
    next_sec = text.find("\n## ", after)
    candidates = [c for c in (next_sub, next_sec) if c >= 0]
    end = min(candidates) if candidates else len(text)
    return text[start:end].rstrip() + "\n"
