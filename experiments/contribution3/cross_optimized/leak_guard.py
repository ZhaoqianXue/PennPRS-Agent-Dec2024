from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.data_contract import (
    FORBIDDEN_PROMPT_KEY_SUBSTRINGS,
    FORBIDDEN_PROMPT_VALUE_PATTERNS,
)


@dataclass(frozen=True)
class LeakFinding:
    path: str
    kind: str
    value: str


def _short(value: Any, limit: int = 180) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def _scan(obj: Any, path: str, findings: list[LeakFinding]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_text = str(key)
            key_lower = key_text.lower()
            for forbidden in FORBIDDEN_PROMPT_KEY_SUBSTRINGS:
                if forbidden in key_lower:
                    findings.append(LeakFinding(path=f"{path}.{key_text}", kind="key", value=key_text))
            _scan(value, f"{path}.{key_text}", findings)
        return
    if isinstance(obj, list):
        for idx, item in enumerate(obj):
            _scan(item, f"{path}[{idx}]", findings)
        return
    if isinstance(obj, str):
        for pattern in FORBIDDEN_PROMPT_VALUE_PATTERNS:
            if pattern.search(obj):
                findings.append(LeakFinding(path=path, kind="value", value=_short(obj)))


def scan_payload(payload: Any, *, root: str = "payload") -> list[LeakFinding]:
    findings: list[LeakFinding] = []
    _scan(payload, root, findings)
    return findings


def assert_no_leakage(payload: Any, *, root: str = "payload") -> None:
    findings = scan_payload(payload, root=root)
    if findings:
        rendered = "\n".join(
            f"- {finding.kind} at {finding.path}: {finding.value}" for finding in findings[:20]
        )
        raise ValueError(f"Potential Contribution1 AUC leakage detected:\n{rendered}")


def scan_jsonl_file(path: Path) -> list[LeakFinding]:
    findings: list[LeakFinding] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                findings.append(LeakFinding(path=f"{path}:{line_no}", kind="json", value=str(exc)))
                continue
            findings.extend(scan_payload(payload, root=f"{path}:{line_no}"))
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan generated cross-optimized prompt artifacts for AUC leakage.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    findings: list[LeakFinding] = []
    for path in args.paths:
        if path.suffix == ".jsonl":
            findings.extend(scan_jsonl_file(path))
        else:
            payload = json.loads(path.read_text(encoding="utf-8"))
            findings.extend(scan_payload(payload, root=str(path)))
    if findings:
        for finding in findings:
            print(f"{finding.kind}\t{finding.path}\t{finding.value}")
        raise SystemExit(1)
    print("No leakage findings.")


if __name__ == "__main__":
    main()
