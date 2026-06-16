from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_workplace_route_and_legacy_entrypoint_exist():
    workplace_page = PROJECT_ROOT / "src/client/app/workplace/page.tsx"
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    legacy_agent_page = PROJECT_ROOT / "src/client/components/PennPRSAgentPage.tsx"

    assert workplace_page.exists()
    assert workplace_component.exists()

    page_source = workplace_page.read_text(encoding="utf-8")
    component_source = workplace_component.read_text(encoding="utf-8")
    legacy_source = legacy_agent_page.read_text(encoding="utf-8")

    assert "ProposalFigureWorkspace" in page_source
    assert "/pennprs-agent/recommend" in component_source
    assert "Open Research Workplace" in legacy_source
    assert 'href="/workplace"' in legacy_source


def test_workplace_uses_codex_like_chat_first_shell():
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    component_source = workplace_component.read_text(encoding="utf-8")

    assert "Local run history" in component_source
    assert "type ChatMessage" in component_source
    assert "Ask PennPRS Agent" in component_source
    assert "selectedPanel" in component_source
    assert "RecommendationCard" in component_source
    assert "ExpandableDetail" in component_source


def test_workplace_shows_reasoning_trace_before_final_result():
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    component_source = workplace_component.read_text(encoding="utf-8")

    assert "type ReasoningStep" in component_source
    assert "ReasoningTraceMessage" in component_source
    assert "REASONING_STEPS" in component_source
    assert "Frame the scientific question" in component_source
    assert "Read the PRS model inventory" in component_source
    assert "Compare candidate tradeoffs" in component_source
    assert "Visible reasoning notes" in component_source
    assert "reasoningDetailForStep" in component_source
    assert "evidence first, answer last" in component_source
    assert "Transfer evidence does not override the retained candidate" in component_source


def test_workplace_orders_model_evidence_before_final_recommendation():
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    component_source = workplace_component.read_text(encoding="utf-8")

    assert "PRS evidence review" in component_source
    assert "EvidenceReviewCard" in component_source
    assert "RecommendationCard" in component_source
    assert "evidence review complete" in component_source
    assert "final recommendation follows" in component_source
    assert component_source.index("PRS evidence review") < component_source.index("Final recommendation")


def test_workplace_shell_uses_pennprs_specific_labels_not_copied_codex_labels():
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    component_source = workplace_component.read_text(encoding="utf-8")

    assert "New recommendation" in component_source
    assert "Trait search" in component_source
    assert "Credential setup" in component_source
    assert "Local run history" in component_source
    assert "Demo validation traits" in component_source
    assert "Artifacts" in component_source
    assert "PRS model summary" in component_source
    assert "recommendation-report.md" in component_source
    assert "candidate-models.csv" in component_source
    assert "provenance.json" in component_source
    assert "training-request.json" in component_source
    assert "Plugins" not in component_source
    assert "Automations" not in component_source
    assert "PRS Engineering" not in component_source
    assert "PRS Web" not in component_source
    assert "Create pull request" not in component_source
    assert "Git actions" not in component_source
    assert "Branch details" not in component_source
    assert "127.0.0.1:3000/workplace" not in component_source


def test_workplace_migrates_prs_disease_model_landscape_features():
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    component_source = workplace_component.read_text(encoding="utf-8")

    assert "PRS model summary viz" in component_source
    assert "ModelSummaryViz" in component_source
    assert "computeModelLandscape" in component_source
    assert "MetricDistributionStrip" in component_source
    assert "Sample size distribution" in component_source
    assert "AUC distribution" in component_source
    assert "Performance landscape" in component_source
    assert "Ancestry coverage" in component_source
    assert "Evidence completeness" in component_source
    assert "Method mix" in component_source
    assert "Source mix" in component_source


def test_workplace_distinguishes_decision_summary_from_model_landscape():
    workplace_component = PROJECT_ROOT / "src/client/components/workplace/PennPRSWorkplace.tsx"
    component_source = workplace_component.read_text(encoding="utf-8")

    assert 'label: "Model inventory"' in component_source
    assert 'label: "Performance landscape"' in component_source
    assert 'label: "Candidate tradeoffs"' in component_source
    assert 'label: "Decision rationale"' in component_source
    assert 'DetailShell title="PRS model inventory summary"' in component_source
    assert 'DetailShell title="Performance landscape"' in component_source
    assert 'DetailShell title="Decision rationale"' in component_source
    decision_block = component_source[
        component_source.index('DetailShell title="Decision rationale"') : component_source.index('if (panel === "warnings")')
    ]
    assert "ModelSummaryViz" not in decision_block
    inventory_block = component_source[
        component_source.index('DetailShell title="PRS model inventory summary"') : component_source.index('if (panel === "landscape")')
    ]
    assert "ModelSummaryViz" in inventory_block
    landscape_block = component_source[
        component_source.index('DetailShell title="Performance landscape"') : component_source.index('if (panel === "candidates")')
    ]
    assert "ModelLandscapePanel" in landscape_block
