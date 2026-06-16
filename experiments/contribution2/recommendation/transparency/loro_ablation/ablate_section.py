#!/usr/bin/env python3
"""Deterministic single-section remover for the PGS evidence-appraisal corpus.

Removes exactly one appraisal section (its ``## `` H2 block, up to the next H2
header, which includes that section's own trailing ``---`` rule) plus its
matching bullet in the ``## Contents`` table. Everything else is byte-identical.

Section keys: ``cross`` (the unnumbered Cross-cutting principles) or ``1``..``7``.

Never edits in place implicitly: caller passes --in and --out. For the actual
LORO run the driver writes the ablated text to the deployed corpus path, bakes
the manifest, then restores from the backup.
"""
import argparse
import re
import sys
from pathlib import Path


def _h2_indices(lines):
    return [i for i, ln in enumerate(lines) if re.match(r"^## ", ln)]


def _target_h2(lines, key):
    pat = r"^## Cross-cutting" if key == "cross" else rf"^## {int(key)}\."
    hits = [i for i, ln in enumerate(lines) if re.match(pat, ln)]
    if len(hits) != 1:
        raise SystemExit(f"section key {key!r}: expected 1 H2 match, found {len(hits)}")
    return hits[0]


def _toc_bullet_index(lines, key):
    # Contents block = from '## Contents' to the next '## '
    h2s = _h2_indices(lines)
    try:
        c_start = next(i for i in h2s if lines[i].strip() == "## Contents")
    except StopIteration:
        raise SystemExit("no '## Contents' header found")
    c_end = next((i for i in h2s if i > c_start), len(lines))
    anchor = "#cross-cutting-appraisal-principles" if key == "cross" else f"#{int(key)}-"
    hits = [
        i for i in range(c_start, c_end)
        if lines[i].lstrip().startswith("- [") and anchor in lines[i]
    ]
    if len(hits) != 1:
        raise SystemExit(f"TOC bullet for {key!r}: expected 1, found {len(hits)}")
    return hits[0]


def ablate(text, key):
    lines = text.split("\n")
    body_start = _target_h2(lines, key)
    h2s = _h2_indices(lines)
    body_end = next((i for i in h2s if i > body_start), len(lines))  # exclusive
    toc_i = _toc_bullet_index(lines, key)
    # Delete body first (higher indices) then TOC bullet, so indices stay valid.
    drop = set(range(body_start, body_end)) | {toc_i}
    kept = [ln for i, ln in enumerate(lines) if i not in drop]
    return "\n".join(kept), (body_end - body_start), (body_start, body_end, toc_i)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--section", required=True, help="cross | 1..7")
    args = ap.parse_args()
    text = Path(args.inp).read_text(encoding="utf-8")
    out, n_body, span = ablate(text, args.section)
    Path(args.out).write_text(out, encoding="utf-8")
    print(f"section={args.section} removed_body_lines={n_body} span={span} "
          f"in_bytes={len(text)} out_bytes={len(out)} delta={len(text)-len(out)}")


if __name__ == "__main__":
    sys.exit(main())
