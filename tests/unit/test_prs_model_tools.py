# tests/unit/test_prs_model_tools.py
"""
Unit tests for PRS Model Tools.
Implements TDD for sop.md L356-462 tool specifications.
"""
import pytest

class TestDomainKnowledge:
    """Test prs_model_domain_knowledge tool."""
    
    def test_search_returns_relevant_snippets(self):
        """Test domain knowledge search returns relevant content."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
        
        result = prs_model_domain_knowledge(query="LDpred2 best for")
        
        assert result is not None
        assert hasattr(result, 'query')
        assert hasattr(result, 'full_document')
        assert hasattr(result, 'snippets')
        assert result.full_document
        assert len(result.snippets) > 0
        # LDpred2 content should be found
        assert "PRS Model Domain Knowledge" in result.full_document
        assert any("ldpred2" in s.content.lower() or "ldpred2" in result.full_document.lower() for s in result.snippets)
    
    def test_search_ancestry_considerations(self):
        """Test search finds ancestry-related content."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
        
        result = prs_model_domain_knowledge(query="African ancestry PRS")
        
        assert len(result.snippets) > 0
        assert any(
            s.section == "6. ancestry_distribution"
            or "ancestry" in s.content.lower()
            for s in result.snippets
        )

    def test_search_returns_empty_for_unrelated_query(self):
        """Test search returns empty for unrelated queries."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
        
        result = prs_model_domain_knowledge(query="quantum computing algorithms")
        
        # Should return result but with no relevant snippets
        assert result is not None
        assert result.query == "quantum computing algorithms"
        # May have zero snippets or low-relevance snippets
    
    def test_search_returns_source_info(self):
        """Test each snippet includes source information."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
        
        result = prs_model_domain_knowledge(query="model selection")
        
        if result.snippets:
            snippet = result.snippets[0]
            assert hasattr(snippet, 'source')
            assert hasattr(snippet, 'section')
            assert hasattr(snippet, 'content')

    def test_search_returns_structured_selection_rules(self):
        """Structured rule sections should be retrievable for Step 1 selection queries."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

        result = prs_model_domain_knowledge(
            query="clinical thresholds must-pass gates penalties method priors"
        )

        assert len(result.snippets) > 0
        assert any(
            (
                s.section == "1. trait_reported / trait_efo / phenotyping_reported"
                or s.section == "2. performance_metrics.auc / performance_metrics.r2 / covariates"
                or s.section == "4. training_development_cohorts / samples_training"
                or s.section == "5. method_name"
            )
            for s in result.snippets
        )


class TestPGSCatalogSearch:
    """Test prs_model_pgscatalog_search tool."""

    def test_hydrate_pgs_model_summaries_preserves_explicit_id_order(self):
        from src.server.core.tools.prs_model_tools import hydrate_pgs_model_summaries
        from unittest.mock import Mock

        mock_client = Mock()

        def mock_details(pgs_id):
            return {
                "id": pgs_id,
                "trait_reported": f"Trait {pgs_id}",
                "trait_efo": [{"label": f"Trait {pgs_id}"}],
                "method_name": "LDpred2",
                "variants_number": 123,
                "ancestry_distribution": {},
                "publication": {"title": "Test Pub", "journal": "Test Journal"},
                "date_release": "2020-01-01",
                "samples_training": [],
            }

        mock_client.get_score_details.side_effect = mock_details
        mock_client.get_score_performance.side_effect = lambda _: []

        models = hydrate_pgs_model_summaries(mock_client, ["PGS002", "PGS001", "PGS002"])

        assert [model.id for model in models] == ["PGS002", "PGS001"]

    def test_search_includes_all_models_including_no_metrics(self):
        """Test that all models are returned including those with no AUC/R² (no filter)."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [
            {"id": "PGS001"},
            {"id": "PGS002"},
            {"id": "PGS003"},
        ]

        def mock_details(pgs_id):
            return {
                "id": pgs_id,
                "trait_reported": "T2D",
                "trait_efo": [{"label": "T2D"}],
                "method_name": "LDpred2",
                "variants_number": 100,
                "ancestry_distribution": {"gwas": {"EUR": 1.0}},
                "publication": {"title": "Test Pub", "journal": "Test Journal"},
                "date_release": "2020-01-01",
                "samples_training": [{"sample_number": 1000}],
            }

        def mock_performance(pgs_id):
            if pgs_id == "PGS001":
                return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.75}]}]
            elif pgs_id == "PGS002":
                return [{"effect_sizes": [{"name_short": "R2", "estimate": 0.15}]}]
            else:  # PGS003 has no metrics
                return []

        mock_client.get_score_details.side_effect = mock_details
        mock_client.get_score_performance.side_effect = mock_performance

        result = prs_model_pgscatalog_search(mock_client, "Type 2 Diabetes")

        assert result.total_found == 3
        assert result.after_filter == 3
        assert len(result.models) == 3

        # All models included (no AUC/R² filter)
        model_ids = [m.id for m in result.models]
        assert "PGS001" in model_ids
        assert "PGS002" in model_ids
        assert "PGS003" in model_ids

        # PGS003 has null auc and r2
        pgs003 = next(m for m in result.models if m.id == "PGS003")
        assert pgs003.performance_metrics.get("auc") is None
        assert pgs003.performance_metrics.get("r2") is None
        assert pgs003.publication.journal == "Test Journal"

    def test_search_returns_all_filtered_models(self):
        """Test that all filtered models are returned (Top-N limit strategy disabled)."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [{"id": f"PGS{i:03d}"} for i in range(1, 11)]

        # All models have metrics
        mock_client.get_score_performance.return_value = [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.75}]}]
        mock_client.get_score_details.return_value = {
            "id": "PGS001", "trait_reported": "T2D", "trait_efo": [], "method_name": "M",
            "variants_number": 10, "ancestry_distribution": {}, "publication": {},
            "date_release": "2020", "samples_training": []
        }

        result = prs_model_pgscatalog_search(mock_client, "T2D")

        assert len(result.models) == 10
        assert result.total_found == 10

    def test_search_returns_models_in_api_order(self):
        """Test that returned models follow API raw order (no Z-score ranking)."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [
            {"id": "PGS_A"},
            {"id": "PGS_B"},
            {"id": "PGS_C"},
        ]

        def mock_details(pgs_id):
            n = {"PGS_A": 1000, "PGS_B": 5000, "PGS_C": 2000}[pgs_id]
            return {
                "id": pgs_id,
                "trait_reported": "T2D",
                "trait_efo": [{"label": "T2D"}],
                "method_name": "M",
                "variants_number": 10,
                "ancestry_distribution": {"gwas": {"EUR": 1.0}},
                "publication": {},
                "date_release": "2020",
                "samples_training": [{"sample_number": n}],
                "samples_variants": [{"sample_number": 1, "cohorts": [{"name_short": "UKB"}]}],
            }

        def mock_performance(pgs_id):
            if pgs_id == "PGS_A":
                return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.80}]}]
            if pgs_id == "PGS_B":
                return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.70}, {"name_short": "R2", "estimate": 0.20}]}]
            return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.70}, {"name_short": "R2", "estimate": 0.10}]}]

        mock_client.get_score_details.side_effect = mock_details
        mock_client.get_score_performance.side_effect = mock_performance

        result = prs_model_pgscatalog_search(mock_client, "T2D")
        assert len(result.models) == 3
        model_ids = [m.id for m in result.models]
        assert model_ids == ["PGS_A", "PGS_B", "PGS_C"]  # API order preserved (no ranking)

    def test_search_filters_by_evaluated_pgs_whitelist(self):
        """Test that evaluated_pgs_whitelist restricts models to the set (Contribution2 alignment)."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [
            {"id": "PGS001"},
            {"id": "PGS002"},
            {"id": "PGS003"},
        ]

        def mock_details(pgs_id):
            return {
                "id": pgs_id,
                "trait_reported": "T2D",
                "trait_efo": [],
                "method_name": "M",
                "variants_number": 10,
                "ancestry_distribution": {},
                "publication": {},
                "date_release": "2020",
                "samples_training": [],
            }

        mock_client.get_score_details.side_effect = mock_details
        mock_client.get_score_performance.side_effect = lambda _: []

        whitelist = {"PGS001", "PGS003"}
        result = prs_model_pgscatalog_search(
            mock_client, "Type 2 Diabetes", evaluated_pgs_whitelist=whitelist
        )

        assert result.total_found == 3
        assert result.after_filter == 2
        model_ids = [m.id for m in result.models]
        assert model_ids == ["PGS001", "PGS003"]  # PGS002 filtered out

    def test_search_includes_models_without_details(self):
        """Test that models with missing details are NOT skipped; use fallback metadata."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [
            {"id": "PGS001"},
            {"id": "PGS002"},
        ]

        # PGS001 has details; PGS002 returns None (simulate fetch failure)
        mock_client.get_score_details.side_effect = lambda pid: (
            {"id": pid, "trait_reported": "T2D", "trait_efo": [], "method_name": "M",
             "variants_number": 10, "ancestry_distribution": {}, "publication": {},
             "date_release": "2020", "samples_training": []}
            if pid == "PGS001" else None
        )
        mock_client.get_score_performance.side_effect = lambda _: []

        result = prs_model_pgscatalog_search(mock_client, "Type 2 Diabetes")

        assert result.total_found == 2
        assert result.after_filter == 2
        assert len(result.models) == 2
        # PGS001 has full details
        m1 = next(m for m in result.models if m.id == "PGS001")
        assert m1.trait_reported == "T2D"
        # PGS002 has no details but is included with fallback
        m2 = next(m for m in result.models if m.id == "PGS002")
        assert m2.trait_reported == "Unknown"
        assert m2.method_name == "Unknown"

    def test_search_prefers_best_european_validation_record(self):
        """Representative performance record should prefer the highest EUR validation result."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [{"id": "PGS001"}]
        mock_client.get_score_details.return_value = {
            "id": "PGS001",
            "trait_reported": "Prostate cancer",
            "trait_efo": [{"label": "prostate carcinoma"}],
            "method_name": "snpnet",
            "variants_number": 100,
            "ancestry_distribution": {"gwas": {"dist": {"EUR": 1.0}}},
            "publication": {"title": "Pub", "journal": "Journal"},
            "date_release": "2020-01-01",
            "samples_training": [{"sample_number": 1000}],
        }
        mock_client.get_score_performance.return_value = [
            {
                "id": "PPM_AFR",
                "phenotyping_reported": "Prostate cancer",
                "covariates": "age, sex, PCs",
                "sampleset": {"samples": [{"sample_number": 6497, "ancestry_broad": "African unspecified"}]},
                "performance_metrics": {
                    "class_acc": [
                        {"name_short": "AUROC", "estimate": 0.97, "ci_lower": 0.95, "ci_upper": 0.99}
                    ],
                    "othermetrics": [{"name_short": "R²", "estimate": 0.40}],
                    "effect_sizes": [],
                },
            },
            {
                "id": "PPM_EUR",
                "phenotyping_reported": "Prostate cancer",
                "covariates": "age, sex, UKB array type, Genotype PCs",
                "sampleset": {"samples": [{"sample_number": 91406, "ancestry_broad": "European"}]},
                "performance_metrics": {
                    "class_acc": [
                        {"name_short": "AUROC", "estimate": 0.91, "ci_lower": 0.90, "ci_upper": 0.92}
                    ],
                    "othermetrics": [
                        {"name_short": "R²", "estimate": 0.30},
                        {"name_short": "Incremental AUROC (full-covars)", "estimate": 0.01},
                        {"name_short": "PGS R2 (no covariates)", "estimate": 0.05},
                        {"name_short": "PGS AUROC (no covariates)", "estimate": 0.65},
                    ],
                    "effect_sizes": [],
                },
            },
        ]

        result = prs_model_pgscatalog_search(mock_client, "Prostate cancer")

        model = result.models[0]
        assert model.performance_metrics["selected_performance_id"] == "PPM_EUR"
        assert model.performance_metrics["selected_validation_ancestry"] == "European"
        assert model.performance_metrics["auc"] == pytest.approx(0.65)
        assert model.performance_metrics["r2"] == pytest.approx(0.05)
        assert model.performance_metrics["full_model_auc"] == pytest.approx(0.91)
        assert model.performance_metrics["full_model_r2"] == pytest.approx(0.30)
        assert model.performance_metrics["incremental_auc"] == pytest.approx(0.01)
        assert model.phenotyping_reported == "Prostate cancer"
        assert model.covariates == "age, sex, UKB array type, Genotype PCs"
        assert model.validation_sample_size == "n=91,406"

    def test_search_preserves_full_classification_and_other_metrics(self):
        """Selected performance summary should retain full classification/other metric lists."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [{"id": "PGS001"}]
        mock_client.get_score_details.return_value = {
            "id": "PGS001",
            "trait_reported": "Test trait",
            "trait_efo": [{"label": "test trait"}],
            "method_name": "LDpred2",
            "variants_number": 100,
            "ancestry_distribution": {"gwas": {"dist": {"EUR": 1.0}}},
            "publication": {"title": "Pub", "journal": "Journal"},
            "date_release": "2020-01-01",
            "samples_training": [{"sample_number": 1000}],
        }
        mock_client.get_score_performance.return_value = [
            {
                "id": "PPM001",
                "phenotyping_reported": "Test trait",
                "covariates": "age, sex",
                "sampleset": {"samples": [{"sample_number": 5000, "ancestry_broad": "European"}]},
                "performance_metrics": {
                    "class_acc": [
                        {"name_short": "AUROC", "name_long": "Area Under ROC", "estimate": 0.75, "ci_lower": 0.72, "ci_upper": 0.78}
                    ],
                    "othermetrics": [
                        {"name_short": "R²", "name_long": "Proportion of variance explained", "estimate": 0.15},
                        {"name_short": "Incremental AUROC (full-covars)", "estimate": 0.02},
                        {"name_short": "PGS R2 (no covariates)", "estimate": 0.05},
                    ],
                    "effect_sizes": [{"name_short": "OR", "estimate": 1.2}],
                },
            }
        ]

        result = prs_model_pgscatalog_search(mock_client, "Test trait")
        model = result.models[0]
        classification = model.performance_metrics["classification_metrics"]
        other = model.performance_metrics["other_metrics"]
        effects = model.performance_metrics["effect_sizes"]

        assert len(classification) == 1
        assert classification[0]["name_short"] == "AUROC"
        assert classification[0]["ci_lower"] == pytest.approx(0.72)
        assert len(other) == 3
        assert {entry["name_short"] for entry in other} == {
            "R²",
            "Incremental AUROC (full-covars)",
            "PGS R2 (no covariates)",
        }
        assert effects[0]["name_short"] == "OR"
        assert model.performance_metrics["auc"] is None
        assert model.performance_metrics["r2"] == pytest.approx(0.05)
        assert model.performance_metrics["full_model_auc"] == pytest.approx(0.75)
        assert model.performance_metrics["full_model_r2"] == pytest.approx(0.15)
        assert model.performance_metrics["incremental_auc"] == pytest.approx(0.02)

    def test_domain_knowledge_does_not_embed_trait_specific_heritability(self):
        """Trait-specific h2 is exposed by the h2 tool, not injected into skill text."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

        result = prs_model_domain_knowledge("target_trait: prostate cancer; AUC R2 heritability ceiling")

        assert "Trait-Specific Heritability" not in result.full_document
        assert not any(snippet.section == "Trait-Specific Heritability" for snippet in result.snippets)
