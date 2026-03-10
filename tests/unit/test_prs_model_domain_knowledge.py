from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge


def test_domain_knowledge_prioritizes_endpoint_specificity_sections():
    result = prs_model_domain_knowledge(
        "endpoint specificity phenotype proxy time-to-event clinical disease"
    )
    sections = [snippet.section for snippet in result.snippets]

    assert "Endpoint Specificity Hierarchy" in sections


def test_domain_knowledge_prioritizes_external_transfer_cautions():
    result = prs_model_domain_knowledge(
        "external transfer transportability biobank snpnet time-to-event"
    )
    sections = [snippet.section for snippet in result.snippets]

    assert any(
        section in sections
        for section in [
            "External Transfer Reliability Heuristics",
            "Large-Biobank snpnet / Time-to-Event Caution",
        ]
    )


def test_domain_knowledge_prioritizes_relevant_family_section():
    result = prs_model_domain_knowledge(
        "target_trait: open-angle glaucoma; validation sample size tie-break snpnet"
    )
    sections = [snippet.section for snippet in result.snippets]

    assert "Open-Angle Glaucoma" in sections


def test_domain_knowledge_prioritizes_thyroid_family_section():
    result = prs_model_domain_knowledge(
        "target_trait: hashimoto's thyroiditis; autoimmune thyroid endocrine prs-cs"
    )
    sections = [snippet.section for snippet in result.snippets]

    assert "Hashimoto's Thyroiditis" in sections


def test_domain_knowledge_prioritizes_validation_tiebreak_section():
    result = prs_model_domain_knowledge(
        "target_trait: primary open-angle glaucoma; validation sample size tie-break"
    )
    sections = [snippet.section for snippet in result.snippets]

    assert "Validation Sample-Size Tie-Break" in sections
