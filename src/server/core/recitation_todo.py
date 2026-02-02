"""
Recitation todo (scratchpad) utility.

Implements the "Manipulate Attention Through Recitation" pattern by:
- Maintaining a small, structured todo list
- Writing it to disk (file-based memory)
- Allowing the agent to re-inject the todo content near the end of context
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class RecitationTodo:
    path: Path
    title: str
    items: List[Tuple[str, bool]]

    def set_done(self, item_label: str) -> None:
        updated = []
        for label, done in self.items:
            if label == item_label:
                updated.append((label, True))
            else:
                updated.append((label, done))
        self.items = updated

    def render(self) -> str:
        lines = [f"## {self.title}"]
        for label, done in self.items:
            mark = "x" if done else " "
            lines.append(f"- [{mark}] {label}")
        lines.append("")  # trailing newline
        return "\n".join(lines)

    def write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.render(), encoding="utf-8")

