import sys
from pathlib import Path
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_maybe_externalize_json_returns_inline_when_small():
    from src.server.core.agent_artifacts import maybe_externalize_json

    payload = {"a": 1, "b": {"c": 2}}

    inline, artifact = maybe_externalize_json(
        payload=payload,
        artifact_prefix="unit_test_small",
        max_inline_bytes=50_000,
        max_inline_tokens=2_000,
        summary_builder=lambda p: {"summary": True}
    )

    assert inline == payload
    assert artifact is None


def test_maybe_externalize_json_writes_artifact_when_large():
    from src.server.core.agent_artifacts import maybe_externalize_json

    payload = {"data": "x" * 60_000}

    inline, artifact = maybe_externalize_json(
        payload=payload,
        artifact_prefix="unit_test_large",
        max_inline_bytes=50_000,
        max_inline_tokens=2_000,
        summary_builder=lambda p: {"data": "summary"}
    )

    assert inline == {"data": "summary"}
    assert artifact is not None
    assert len(artifact.sha256) == 64
    assert artifact.bytes > 50_000
    assert artifact.artifact_path.endswith(".json")
    assert Path(artifact.artifact_path).exists()


def test_maybe_externalize_json_externalizes_when_token_limit_exceeded():
    from src.server.core.agent_artifacts import maybe_externalize_json

    # ~9k bytes -> ~2.25k tokens (rough), below 50KB but above 2k token budget.
    payload = {"data": "x" * 9_000}

    inline, artifact = maybe_externalize_json(
        payload=payload,
        artifact_prefix="unit_test_token_limit",
        max_inline_bytes=50_000,
        max_inline_tokens=2_000,
        summary_builder=lambda p: {"data": "summary"}
    )

    assert inline == {"data": "summary"}
    assert artifact is not None


def test_recitation_todo_writes_and_updates():
    from src.server.core.recitation_todo import RecitationTodo

    with tempfile.TemporaryDirectory() as tmp:
        todo_path = Path(tmp) / "todo.md"
        todo = RecitationTodo(
            path=todo_path,
            title="Current Task Progress",
            items=[
                ("Step 1: Query PGS Catalog", False),
                ("Step 1: Evaluate models", False),
            ]
        )

        todo.write()
        text = todo_path.read_text(encoding="utf-8")
        assert "- [ ] Step 1: Query PGS Catalog" in text

        todo.set_done("Step 1: Query PGS Catalog")
        todo.write()
        text2 = todo_path.read_text(encoding="utf-8")
        assert "- [x] Step 1: Query PGS Catalog" in text2
