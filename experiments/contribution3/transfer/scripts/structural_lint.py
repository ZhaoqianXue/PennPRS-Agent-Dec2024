"""Structural lint for the LLM-led transfer refactor.

Runs the three CI grep assertions from REFACTOR_PLAN.md §12:
  - Prompt lint: forbidden phrases outside the sentinel tuple / docstring.
  - Forbidden-field scan: forbidden derived-score fields in logic code.
  - Trait-agnostic audit: no hardcoded trait / ICD / disease strings in
    decision code.

Returns non-zero if any check fails. Exclusion rule: a match is ignored
when its **logical** context is one of the sanctioned sentinel lists
(`FORBIDDEN_PROMPT_PHRASES`, `FORBIDDEN_SCHEMA_FIELDS`) or a module
docstring explicitly documenting the ban. We implement this simply by
excluding files' sentinel regions and top-level triple-quoted strings.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[4]  # .../PennPRS_Agent/
TRANSFER = ROOT / "experiments" / "contribution3" / "transfer"

PROMPT_FILE = TRANSFER / "prompts" / "transfer_prompt.py"

FORBIDDEN_PROMPT_PHRASES = (
    "strong prior",
    "deterministic score",
    "fallback ranking",
    "priority score",
    "ordering as prior",
)

# Kept separate because "anchor" / "override" are too generic to scan freely;
# we only ban them inside *prompt text literals*, not in any code.
FORBIDDEN_PROMPT_WORDS_IN_TEXT = (
    "anchor",
    "override",
)

FORBIDDEN_FIELD_NAMES = (
    "archetype",
    "phenotype_fidelity_score",
    "utility_score",
    "selection_priority_score",
    "transferability_prior_score",
    "cheap_rank_score",
    "evidence_tags",
    "weighted_overlap",
    "confidence_level",
    "confidence_tier",
    "genetic_support_present",
)

QUARANTINED_SYMBOLS = (
    # Symbols left in `src/server/core/tools/prs_model_tools.py` for legacy
    # disease-workflow callers. New contribution3 transfer code may never
    # import them — they encode trait-specific or priority-tier logic.
    "DOMAIN_QUERY_EXPANSION",
    "STRUCTURED_SECTION_KEYWORDS",
    "TARGET_DISEASE_SECTION_TITLES",
    "_select_representative_performance_record",
    "_build_selected_performance_summary",
    "_is_european_ancestry",
)

TRAIT_AGNOSTIC_BLACKLIST = (
    # Sample ICD codes / trait names that must never appear as hardcoded
    # strings in decision code. Debug CLI fixtures may reference them,
    # but transfer/agent.py / driver.py / tools/ / prompts/ may not.
    r"\bI\d{2}\b",
    r"\bJ\d{2}\b",
    r"\bF\d{2}\b",
    r"\bE\d{2}\b",
    r"\bN\d{2}\b",
    r"\bD\d{2}\b",
    r"\bM\d{2}[A-Z]?\b",
    r"\bS\d{2}\b",
    r"\bB\d{2}\b",
    r"\bdiabetes\b",
    r"\basthma\b",
    r"\bdepression\b",
    r"\bobesity\b",
    r"\bhypertension\b",
    r"\bHodgkin\b",
)

# Paths that MUST be clean (decision code + prompts + tools + schemas).
SCAN_PATHS = (
    TRANSFER / "agent.py",
    TRANSFER / "driver.py",
    TRANSFER / "harness.py",
    TRANSFER / "state.py",
    TRANSFER / "schemas.py",
    TRANSFER / "prompts" / "transfer_prompt.py",
    TRANSFER / "tools",  # directory — all *.py inside
)


def _iter_py_files(paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            out.extend(sorted(p.rglob("*.py")))
        elif p.is_file():
            out.append(p)
    return out


def _all_docstring_ranges(tree: ast.Module) -> list[tuple[int, int]]:
    """Collect module / class / function docstring line ranges for exclusion."""
    ranges: list[tuple[int, int]] = []

    def _maybe_add(body: list[ast.stmt]) -> None:
        if not body:
            return
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            ranges.append((first.lineno, first.end_lineno or first.lineno))

    _maybe_add(tree.body)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            _maybe_add(node.body)
    return ranges


def _comment_line_ranges(src: str) -> list[tuple[int, int]]:
    """Lines whose stripped content begins with `#` (true comments)."""
    ranges: list[tuple[int, int]] = []
    for idx, line in enumerate(src.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            ranges.append((idx, idx))
    return ranges


def _sentinel_tuple_ranges(tree: ast.Module, names: tuple[str, ...]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if any(name in names for name in targets):
                ranges.append((node.lineno, node.end_lineno or node.lineno))
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id in names:
                ranges.append((node.lineno, node.end_lineno or node.lineno))
    return ranges


def _line_in_ranges(lineno: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= lineno <= b for a, b in ranges)


def _check_file(
    path: Path,
    needle_regexes: list[re.Pattern[str]],
    sentinel_names: tuple[str, ...],
    *,
    allow_module_docstring: bool = True,
) -> list[tuple[int, str, str]]:
    """Return list of (line_no, pattern, line_text) hits not in excluded ranges."""
    text = path.read_text()
    tree = ast.parse(text)
    excluded: list[tuple[int, int]] = []
    if allow_module_docstring:
        excluded.extend(_all_docstring_ranges(tree))
    excluded.extend(_comment_line_ranges(text))
    excluded.extend(_sentinel_tuple_ranges(tree, sentinel_names))

    hits: list[tuple[int, str, str]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if _line_in_ranges(idx, excluded):
            continue
        for regex in needle_regexes:
            if regex.search(line):
                hits.append((idx, regex.pattern, line.strip()))
    return hits


def run() -> int:
    errors: list[str] = []

    # 1. Prompt-only lint: forbidden phrases in any string LITERAL within prompt file.
    prompt_phrase_regexes = [
        re.compile(rf"\"[^\"]*{re.escape(p)}[^\"]*\"", re.IGNORECASE)
        for p in FORBIDDEN_PROMPT_PHRASES
    ]
    prompt_word_in_literal_regexes = [
        re.compile(rf"\"[^\"]*\b{re.escape(w)}\b[^\"]*\"", re.IGNORECASE)
        for w in FORBIDDEN_PROMPT_WORDS_IN_TEXT
    ]
    # Only scan the prompt file for these literals — and exclude sentinel tuple.
    hits = _check_file(
        PROMPT_FILE,
        prompt_phrase_regexes + prompt_word_in_literal_regexes,
        sentinel_names=("FORBIDDEN_PROMPT_PHRASES", "FORBIDDEN_PROMPT_WORDS_IN_TEXT"),
        allow_module_docstring=True,
    )
    if hits:
        for lineno, pat, text in hits:
            errors.append(f"[prompt lint] {PROMPT_FILE}:{lineno} — {pat!r}: {text}")

    # 2. Forbidden field scan across all decision code.
    field_regexes = [re.compile(rf"\b{re.escape(f)}\b") for f in FORBIDDEN_FIELD_NAMES]
    for path in _iter_py_files(SCAN_PATHS):
        hits = _check_file(
            path,
            field_regexes,
            sentinel_names=("FORBIDDEN_SCHEMA_FIELDS",),
            allow_module_docstring=True,
        )
        for lineno, pat, text in hits:
            errors.append(f"[field scan] {path}:{lineno} — {pat!r}: {text}")

    # 3. Trait-agnostic audit.
    trait_regexes = [re.compile(p, re.IGNORECASE) for p in TRAIT_AGNOSTIC_BLACKLIST]
    for path in _iter_py_files(SCAN_PATHS):
        hits = _check_file(
            path,
            trait_regexes,
            sentinel_names=(),
            allow_module_docstring=True,
        )
        for lineno, pat, text in hits:
            errors.append(f"[trait-agnostic] {path}:{lineno} — {pat!r}: {text}")

    # 4. Quarantined-symbol audit: new transfer code must not import or
    # call symbols left in prs_model_tools.py for legacy callers.
    quarantine_regexes = [re.compile(rf"\b{re.escape(s)}\b") for s in QUARANTINED_SYMBOLS]
    # Also scan contribution2_adapter.py — decision-adjacent.
    extra_paths = [TRANSFER / "contribution2_adapter.py"]
    for path in list(_iter_py_files(SCAN_PATHS)) + extra_paths:
        if not path.exists():
            continue
        hits = _check_file(
            path,
            quarantine_regexes,
            sentinel_names=("QUARANTINED_SYMBOLS",),
            allow_module_docstring=True,
        )
        for lineno, pat, text in hits:
            errors.append(f"[quarantined-symbol] {path}:{lineno} — {pat!r}: {text}")

    if errors:
        print(f"Structural lint FAILED ({len(errors)} issues):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("Structural lint OK")
    return 0


if __name__ == "__main__":
    sys.exit(run())
