import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT
    / "experiments"
    / "contribution2"
    / "presentation"
    / "scripts"
    / "plot_44disease_three_method_comparison.py"
)


def load_plot_module():
    spec = importlib.util.spec_from_file_location("plot_44disease_three_method_comparison", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_within_presentation_uses_current_44_disease_script():
    """The current presentation entrypoint is the EFO-clean 44-disease comparison script."""
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "44-disease benchmark" in source
    assert "plot_44disease_three_method_comparison.py" in source
    assert "plot_82disease_baseline_vs_prs_agent.py" in source
    assert "contaminated" in source


def test_current_three_arm_labels_are_formal_names():
    """Display labels should match the archived three-arm definitions."""
    module = load_plot_module()

    assert module.AGENT_LABEL == "PRS Agent"
    assert module.GENERAL_LLM_LABEL == "General LLM"
    assert module.CATALOG_LABEL == "PGS Report"


def test_hitk_plot_supports_all_five_k_values():
    """The current Hit@K figure uses the full Hit@1-Hit@5 curve."""
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "ks = [1, 2, 3, 4, 5]" in source
    assert "Hit@1..5 selection accuracy" in source
    assert "Hit@K accuracy" in source


def test_presentation_copy_does_not_surface_retired_82_disease_labels():
    """Rendered presentation copy should not use retired 82-disease labels."""
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    forbidden = [
        "All evaluated diseases",
        "Candidate-rich",
        "candidate-rich",
        "Filtered to diseases with >",
        "restricted to diseases with more than",
        "82disease_hitk_accuracy_curve",
        "gain over baseline",
        "within_hitk_gain_curve",
        "Baseline LLM",
    ]
    for phrase in forbidden:
        assert phrase not in source
    assert "General LLM" in source
    assert "PGS Report" in source


def test_micro_case_studies_use_current_44_disease_examples():
    """Micro case studies should use the curated EFO-clean 44-disease examples."""
    module = load_plot_module()

    assert module.MICRO_CASES == [
        "coronary artery disease",
        "atrial fibrillation",
        "asthma",
        "rheumatoid arthritis",
        "obesity",
        "ankylosing spondylitis",
        "angina pectoris",
        "abdominal aortic aneurysm",
    ]


def test_helper_functions_keep_expected_rank_and_delta_semantics():
    module = load_plot_module()

    assert module._delta_tier(0.0) == "identical"
    assert module._delta_tier(0.01) == "higher"
    assert module._delta_tier(-0.01) == "lower"
    assert module._landscape_log_ticks(220) == [1, 2, 3, 5, 10, 20, 50, 100, 150, 200]
