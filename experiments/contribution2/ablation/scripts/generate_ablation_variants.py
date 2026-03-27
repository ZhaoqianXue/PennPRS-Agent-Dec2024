"""
Generate ablation variant .md files by removing one ## section at a time
from the source prs_model_domain_knowledge.md.

Each variant is a complete copy of the source with exactly one ## section
removed.  A manifest.json is written alongside the variants for downstream
consumption by the experiment runner.

Usage:
    python experiments/contribution2/ablation/scripts/generate_ablation_variants.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SOURCE_MD = PROJECT_ROOT / "src" / "server" / "core" / "knowledge" / "prs_model_domain_knowledge.md"
VARIANTS_DIR = Path(__file__).resolve().parent.parent / "variants"

# Ordered list of (variant_id, section_heading_pattern) pairs.
# The heading pattern is matched against the line starting with "## ".
ABLATION_SECTIONS: list[tuple[str, str]] = [
    ("no-section1-trait-endpoint", "## 1. trait_reported"),
    ("no-section2-performance-covariates", "## 2. performance_metrics"),
    ("no-section3-validation-sample-size", "## 3. validation_sample_size"),
    ("no-section4-training-cohorts-ancestry", "## 4. training_development_cohorts"),
    ("no-section5-method-name", "## 5. method_name"),
    ("no-section6-publication", "## 6. publication.title"),
    ("no-section7-variants-number", "## 7. variants_number"),
]


def _parse_sections(text: str) -> list[tuple[str, str, int, int]]:
    """Parse markdown into sections delimited by ## headings.

    Returns a list of (heading_line, body, start_line_0based, end_line_0based).
    The first element is the preamble (heading_line="").
    """
    lines = text.split("\n")
    sections: list[tuple[str, str, int, int]] = []
    current_heading = ""
    current_start = 0
    current_lines: list[str] = []

    for i, line in enumerate(lines):
        if re.match(r"^## ", line):
            # Close previous section
            sections.append((
                current_heading,
                "\n".join(current_lines),
                current_start,
                i - 1,
            ))
            current_heading = line
            current_start = i
            current_lines = [line]
        else:
            current_lines.append(line)

    # Close last section
    sections.append((
        current_heading,
        "\n".join(current_lines),
        current_start,
        len(lines) - 1,
    ))
    return sections


def _find_section_index(
    sections: list[tuple[str, str, int, int]],
    heading_prefix: str,
) -> int:
    """Find the section whose heading starts with the given prefix."""
    for idx, (heading, _, _, _) in enumerate(sections):
        if heading.startswith(heading_prefix):
            return idx
    raise ValueError(f"Section not found for prefix: {heading_prefix!r}")


def _build_variant(
    sections: list[tuple[str, str, int, int]],
    remove_idx: int,
    variant_id: str,
) -> str:
    """Rebuild the document with one section removed."""
    removed_heading = sections[remove_idx][0]
    parts: list[str] = []
    parts.append(f"<!-- ABLATION: removed section \"{removed_heading}\" -->")
    for idx, (_, body, _, _) in enumerate(sections):
        if idx == remove_idx:
            continue
        parts.append(body)
    return "\n".join(parts)


def main() -> int:
    if not SOURCE_MD.exists():
        print(f"ERROR: Source file not found: {SOURCE_MD}")
        return 1

    VARIANTS_DIR.mkdir(parents=True, exist_ok=True)

    source_text = SOURCE_MD.read_text(encoding="utf-8")
    sections = _parse_sections(source_text)

    print(f"Parsed {len(sections)} sections from source ({len(source_text)} chars):")
    for idx, (heading, body, start, end) in enumerate(sections):
        label = heading if heading else "(preamble)"
        print(f"  [{idx}] L{start+1}-L{end+1}  {label}  ({len(body)} chars)")

    manifest_entries: list[dict] = []

    for variant_id, heading_prefix in ABLATION_SECTIONS:
        try:
            remove_idx = _find_section_index(sections, heading_prefix)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1

        heading, _, start, end = sections[remove_idx]
        variant_text = _build_variant(sections, remove_idx, variant_id)
        out_file = VARIANTS_DIR / f"{variant_id}.md"
        out_file.write_text(variant_text, encoding="utf-8")

        manifest_entries.append({
            "variant_id": variant_id,
            "removed_section_heading": heading,
            "removed_line_range": f"L{start+1}-L{end+1}",
            "output_file": out_file.name,
            "source_chars": len(source_text),
            "variant_chars": len(variant_text),
            "chars_removed": len(source_text) - len(variant_text),
        })
        print(f"  Generated: {out_file.name}  (removed {heading}, L{start+1}-L{end+1}, -{len(source_text) - len(variant_text)} chars)")

    manifest_path = VARIANTS_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest_entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nManifest written to {manifest_path}")
    print(f"Total variants generated: {len(manifest_entries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
