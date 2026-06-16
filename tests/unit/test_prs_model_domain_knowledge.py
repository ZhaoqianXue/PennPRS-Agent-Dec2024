from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge


def test_domain_knowledge_returns_full_document():
    result = prs_model_domain_knowledge(
        "target_trait: obesity; phenotype alignment validation sample size"
    )

    assert result.full_document
    assert "# PGS Evidence Appraisal" in result.full_document


def test_domain_knowledge_returns_current_field_sections():
    result = prs_model_domain_knowledge(
        "target_trait: obesity; phenotype alignment endpoint specificity auc r2 "
        "validation sample size training cohorts method ancestry publication variants"
    )
    sections = [snippet.section for snippet in result.snippets]

    # Corpus sections strictly correspond to the PGS schema; a broad selection
    # query should surface several of them (predicted_trait, a performance_metrics
    # block, and a development/method block). performance_metrics is subsectioned,
    # so accept its sub-blocks as well.
    assert "2. predicted_trait" in sections
    assert any(
        s == "8. performance_metrics"
        or s.startswith("Metrics and the usable-axis")
        or s == "Covariates"
        or s.startswith("Fallback when no PRS-only")
        or s.startswith("Heritability sanity check")
        or s.startswith("Evaluation sample")
        for s in sections
    )
    assert any(
        s in {
            "3. source_of_variant_associations_gwas",
            "7. score_development_training",
            "3. development_method",
        }
        for s in sections
    )


def test_domain_knowledge_snippets_include_transportability_guidance():
    result = prs_model_domain_knowledge(
        "external transfer transportability biobank pan-phenome disease-focused"
    )

    assert any(
        (
            snippet.section
            in {
                "3. source_of_variant_associations_gwas",
                "4. score_development_training",
            }
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
        snippet.section == "5. development_method" or "shrinkage" in snippet.content.lower()
        for snippet in result.snippets
    )
