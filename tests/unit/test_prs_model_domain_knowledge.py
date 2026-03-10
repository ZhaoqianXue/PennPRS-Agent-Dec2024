from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge


def test_domain_knowledge_returns_full_document():
    result = prs_model_domain_knowledge(
        "target_trait: obesity; phenotype alignment validation sample size"
    )

    assert result.full_document
    assert "# PRS Model Domain Knowledge" in result.full_document


def test_domain_knowledge_returns_current_field_sections():
    result = prs_model_domain_knowledge(
        "target_trait: obesity; phenotype alignment endpoint specificity auc r2 "
        "validation sample size training cohorts method ancestry publication variants"
    )
    sections = [snippet.section for snippet in result.snippets]

    assert "1. trait_reported / trait_efo / phenotyping_reported" in sections
    assert "2. performance_metrics.auc / performance_metrics.r2 / covariates" in sections
    assert "3. validation_sample_size" in sections


def test_domain_knowledge_snippets_include_transportability_guidance():
    result = prs_model_domain_knowledge(
        "external transfer transportability biobank pan-phenome disease-focused"
    )

    assert any(
        (
            snippet.section == "4. training_development_cohorts / samples_training"
            or "transportability" in snippet.content.lower()
            or "single-biobank" in snippet.content.lower()
        )
        for snippet in result.snippets
    )


def test_domain_knowledge_snippets_include_method_caution():
    result = prs_model_domain_knowledge(
        "snpnet method prior prs-cs ldpred2 high-capacity penalized regression"
    )

    assert any(
        snippet.section == "5. method_name" or "snpnet" in snippet.content.lower()
        for snippet in result.snippets
    )
