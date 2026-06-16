"""Contract for the (target_trait, target_ancestry) task input of the within-trait
PGS recommendation experiment.

The within-trait task input changed from target_trait only to a
(target_trait, target_ancestry) pair, and the candidate schema is the id-plus-seven-
evidence-section schema. The recommendation task REQUIRES an explicit target_ancestry (the input
stage confirms ancestry with the user), so there is no missing/unspecified-ancestry
path. The experiment runner is fixed to European because the AoU benchmark is a
European evaluation. This change only adds the input and reads ancestry fields
against it — it introduces no ancestry-evidence weighting and no fallback rules.

The experiment runner module is loaded in a SUBPROCESS: importing it pulls in heavy
modules with import-time side effects that pollute other in-process tests (notably
the recommendation_agent synonym-integration tests), so it must stay isolated.
"""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "contribution2"
    / "recommendation"
    / "scripts"
    / "run_experiment_without_domain.py"
)
WITH_DOMAIN_RUNNER_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "contribution2"
    / "recommendation"
    / "scripts"
    / "run_experiment_with_domain.py"
)


@pytest.fixture(scope="module")
def runner_facts():
    """Load the experiment runner in an isolated subprocess and return the few
    target_ancestry-relevant facts as plain JSON (no in-process import → no pollution)."""
    code = textwrap.dedent(
        f"""
        import importlib.util, json
        spec = importlib.util.spec_from_file_location("rew_probe", {str(RUNNER_PATH)!r})
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        ctx = m._step1_context("type 2 diabetes", [], 0, target_ancestry=m.EXPERIMENT_TARGET_ANCESTRY)
        print(json.dumps({{
            "constant": m.EXPERIMENT_TARGET_ANCESTRY,
            "ctx_trait": ctx["target_trait"],
            "ctx_ancestry": ctx["target_ancestry"],
            "ctx_has_ancestry_key": "target_ancestry" in ctx,
        }}))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"runner probe failed:\n{result.stderr}"
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_runner_default_target_ancestry_is_european(runner_facts):
    """The experiment runner is fixed to European because the benchmark is EUR."""
    assert runner_facts["constant"] == "European"


def test_step1_context_includes_explicit_target_ancestry(runner_facts):
    """The context JSON shown to the LLM carries the runner-injected target_ancestry
    alongside target_trait."""
    assert runner_facts["ctx_has_ancestry_key"] is True
    assert runner_facts["ctx_trait"] == "type 2 diabetes"
    assert runner_facts["ctx_ancestry"] == "European"


def test_with_domain_step1_context_uses_same_explicit_target_ancestry_contract():
    """The with-domain runner overrides the shared Step 1 context builder, so it
    must accept and emit the same explicit target_ancestry field."""
    code = textwrap.dedent(
        f"""
        import importlib.util, json
        from types import SimpleNamespace

        spec = importlib.util.spec_from_file_location("rwd_probe", {str(WITH_DOMAIN_RUNNER_PATH)!r})
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.prs_model_domain_knowledge = lambda query, max_snippets=8: SimpleNamespace(
            model_dump=lambda: {{"query": query, "snippets": [], "source_type": "stub"}}
        )
        ctx = m._step1_context(
            "type 2 diabetes",
            [],
            0,
            target_ancestry=m.without_domain.EXPERIMENT_TARGET_ANCESTRY,
        )
        print(json.dumps({{
            "ctx_trait": ctx["target_trait"],
            "ctx_ancestry": ctx["target_ancestry"],
            "skill_query": ctx["skill_context"]["query"],
        }}))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"with-domain runner probe failed:\n{result.stderr}"
    facts = json.loads(result.stdout.strip().splitlines()[-1])
    assert facts["ctx_trait"] == "type 2 diabetes"
    assert facts["ctx_ancestry"] == "European"
    assert "target_ancestry: European" in facts["skill_query"]


def test_recommendation_skill_interprets_ancestry_relative_to_target_ancestry():
    """The skill reads ancestry fields relative to the explicit target_ancestry, with
    no newly-introduced evidence hierarchy, weight change, or unspecified fallback."""
    from src.server.core.tools.prs_model_evaluator_skill import load_recommendation_view

    view = load_recommendation_view()
    # The task input names target_ancestry, and evaluation ancestry is read against it.
    assert "target_ancestry" in view
    assert "validation ancestry matches the `target_ancestry`" in view
    # No invented ancestry-evidence hierarchy / weight change was introduced.
    assert "most direct" not in view
    assert "auxiliary transportability evidence" not in view
    # No unspecified-ancestry fallback.
    assert "unspecified" not in view
