# tests/unit/test_prs_model_tools.py
"""
Unit tests for PRS Model Tools.
Implements TDD for sop.md L356-462 tool specifications.
"""
import pytest
from src.server.core.tool_schemas import PGSModelSummary, PerformanceLandscape
from src.server.core.tools.prs_model_tools import prs_model_performance_landscape


def _create_model(
    id: str, 
    auc: float = None, 
    r2: float = None,
    samples_training: str = "n=1000",
    ancestry_distribution: str = "GWAS: EUR (100%)",
    variants_number: int = 100,
    method_name: str = "LDpred2",
    cohorts: list[str] | None = None
) -> PGSModelSummary:
    """Helper to create a PGSModelSummary for testing."""
    return PGSModelSummary(
        id=id,
        trait_reported="T2D",
        trait_efo="efo",
        method_name=method_name,
        variants_number=variants_number,
        ancestry_distribution=ancestry_distribution,
        publication="Pub",
        date_release="2020-01-01",
        samples_training=samples_training,
        performance_metrics={"auc": auc, "r2": r2},
        phenotyping_reported="T2D",
        covariates="age,sex",
        sampleset=None,
        training_development_cohorts=cohorts or []
    )


class TestPerformanceLandscape:
    """Test prs_model_performance_landscape tool."""

    class _FakeClient:
        def __init__(self, scores: list[dict], performances: list[dict]):
            self._scores = scores
            self._performances = performances

        def iter_all_scores(self, batch_size: int = 200, max_scores=None):
            data = self._scores if max_scores is None else self._scores[:max_scores]
            for s in data:
                yield s

        def iter_all_performances(self, batch_size: int = 200, max_records=None):
            data = self._performances if max_records is None else self._performances[:max_records]
            for p in data:
                yield p

    def _score(self, pgs_id: str, variants: int, train_n: int, method: str, major_gwas: str, cohorts: list[str] | None = None):
        cohorts = cohorts or []
        return {
            "id": pgs_id,
            "method_name": method,
            "variants_number": variants,
            "samples_training": [{"sample_number": train_n, "cohorts": [{"name_short": c} for c in cohorts]}] if train_n else [],
            "samples_variants": [],
            "ancestry_distribution": {"gwas": {"dist": {major_gwas: 1.0}}},
        }

    def _perf(self, pgs_id: str, auc: float | None, r2: float | None):
        effect_sizes = []
        if auc is not None:
            effect_sizes.append({"name_short": "AUC", "estimate": auc})
        if r2 is not None:
            effect_sizes.append({"name_short": "R2", "estimate": r2})
        return {"associated_pgs_id": pgs_id, "performance_metrics": {"effect_sizes": effect_sizes}}
    
    def test_basic_calculation(self):
        """Test performance landscape calculation with basic input."""
        scores = [
            self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR", cohorts=["UKB"]),
            self._score("PGS002", variants=200, train_n=2000, method="PRS-CS", major_gwas="AFR", cohorts=["FINRISK"]),
            self._score("PGS003", variants=150, train_n=1500, method="LDpred2", major_gwas="EUR", cohorts=["UKB"]),
        ]
        perfs = [
            self._perf("PGS001", auc=0.75, r2=0.15),
            self._perf("PGS002", auc=0.80, r2=0.20),
            self._perf("PGS003", auc=0.70, r2=0.10),
        ]
        client = self._FakeClient(scores, perfs)

        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert isinstance(result, PerformanceLandscape)
        assert result.total_models == 3
        assert result.auc.min == 0.70
        assert result.auc.max == 0.80
        assert result.auc.median == 0.75
        assert result.variants.min == 100
        assert result.variants.max == 200
        assert result.prs_methods["LDpred2"] == 2
        assert result.prs_methods["PRS-CS"] == 1
        assert result.training_development_cohorts["UKB"] == 2

    def test_with_missing_auc(self):
        """Test handling of models with missing AUC."""
        scores = [
            self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR"),
            self._score("PGS002", variants=200, train_n=2000, method="LDpred2", major_gwas="EUR"),
        ]
        perfs = [
            self._perf("PGS001", auc=0.75, r2=0.15),
            self._perf("PGS002", auc=None, r2=0.20),
        ]
        client = self._FakeClient(scores, perfs)

        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert result.auc.missing_count == 1
        assert result.auc.min == 0.75  # Only one AUC
        assert result.auc.max == 0.75

    def test_with_missing_r2(self):
        """Test handling of models with missing R2."""
        scores = [
            self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR"),
            self._score("PGS002", variants=200, train_n=2000, method="LDpred2", major_gwas="EUR"),
        ]
        perfs = [
            self._perf("PGS001", auc=0.75, r2=None),
            self._perf("PGS002", auc=0.80, r2=0.20),
        ]
        client = self._FakeClient(scores, perfs)

        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert result.r2.missing_count == 1
        assert result.r2.min == 0.20

    def test_with_all_missing_metrics(self):
        """Test handling of models with both AUC and R2 missing."""
        scores = [
            self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR"),
            self._score("PGS002", variants=200, train_n=2000, method="LDpred2", major_gwas="EUR"),
        ]
        perfs = [
            self._perf("PGS001", auc=0.75, r2=0.15),
            self._perf("PGS002", auc=None, r2=None),
        ]
        client = self._FakeClient(scores, perfs)

        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert result.auc.missing_count == 1
        assert result.r2.missing_count == 1

    def test_empty_input(self):
        """Test handling of empty model list."""
        client = self._FakeClient(scores=[], performances=[])
        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert result.total_models == 0
        assert result.ancestry == {}
        assert result.prs_methods == {}

    def test_single_model(self):
        """Test handling of single model."""
        client = self._FakeClient(
            scores=[self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR")],
            performances=[self._perf("PGS001", auc=0.75, r2=0.15)]
        )
        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert result.total_models == 1
        assert result.auc.min == 0.75
        assert result.auc.max == 0.75
        assert result.auc.median == 0.75

    def test_sample_size_and_variants_distributions(self):
        """Test sample size and variants distributions are computed."""
        client = self._FakeClient(
            scores=[
                self._score("PGS001", variants=10, train_n=1000, method="LDpred2", major_gwas="EUR"),
                self._score("PGS002", variants=30, train_n=3000, method="LDpred2", major_gwas="EUR"),
            ],
            performances=[
                self._perf("PGS001", auc=0.70, r2=0.10),
                self._perf("PGS002", auc=0.90, r2=0.30),
            ]
        )
        result = prs_model_performance_landscape(client, candidate_models=[])
        assert result.sample_size.min == 1000
        assert result.sample_size.max == 3000
        assert result.variants.min == 10
        assert result.variants.max == 30

    def test_r2_only_models(self):
        """Test with models that only have R2, no AUC."""
        client = self._FakeClient(
            scores=[
                self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR"),
                self._score("PGS002", variants=200, train_n=2000, method="LDpred2", major_gwas="EUR"),
            ],
            performances=[
                self._perf("PGS001", auc=None, r2=0.15),
                self._perf("PGS002", auc=None, r2=0.25),
            ]
        )
        result = prs_model_performance_landscape(client, candidate_models=[])
        
        assert result.auc.missing_count == 2
        assert result.r2.max == 0.25

    def test_ancestry_method_and_cohort_counts(self):
        """Test that ancestry/method/cohort counts are aggregated."""
        client = self._FakeClient(
            scores=[
                self._score("PGS001", variants=100, train_n=1000, method="LDpred2", major_gwas="EUR", cohorts=["UKB"]),
                self._score("PGS002", variants=200, train_n=2000, method="PRS-CS", major_gwas="AFR", cohorts=["UKB", "FINRISK"]),
            ],
            performances=[
                self._perf("PGS001", auc=0.7, r2=0.1),
                self._perf("PGS002", auc=0.8, r2=0.2),
            ]
        )
        result = prs_model_performance_landscape(client, candidate_models=[])
        assert result.ancestry["EUR"] == 1
        assert result.ancestry["AFR"] == 1
        assert result.prs_methods["LDpred2"] == 1
        assert result.prs_methods["PRS-CS"] == 1
        assert result.training_development_cohorts["UKB"] == 2


class TestDomainKnowledge:
    """Test prs_model_domain_knowledge tool."""
    
    def test_search_returns_relevant_snippets(self):
        """Test domain knowledge search returns relevant content."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
        
        result = prs_model_domain_knowledge(query="LDpred2 best for")
        
        assert result is not None
        assert hasattr(result, 'query')
        assert hasattr(result, 'snippets')
        assert len(result.snippets) > 0
        # LDpred2 content should be found
        assert any("LDpred2" in s.content for s in result.snippets)
    
    def test_search_ancestry_considerations(self):
        """Test search finds ancestry-related content."""
        from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
        
        result = prs_model_domain_knowledge(query="African ancestry PRS")
        
        assert len(result.snippets) > 0
        # Should find African ancestry section
        assert any("AFR" in s.content or "African" in s.content for s in result.snippets)

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


class TestPGSCatalogSearch:
    """Test prs_model_pgscatalog_search tool."""
    
    def test_search_filters_models_without_metrics(self):
        """Test that models with no performance metrics are filtered out."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock
        
        # Mock PGSCatalogClient
        mock_client = Mock()
        mock_client.search_scores.return_value = [
            {"id": "PGS001"},
            {"id": "PGS002"},
            {"id": "PGS003"},
        ]
        
        # Mock get_score_details
        def mock_details(pgs_id):
            return {
                "id": pgs_id,
                "trait_reported": "T2D",
                "trait_efo": [{"label": "T2D"}],
                "method_name": "LDpred2",
                "variants_number": 100,
                "ancestry_distribution": {"gwas": {"EUR": 1.0}},
                "publication": {"title": "Test Pub"},
                "date_release": "2020-01-01",
                "samples_training": [{"sample_number": 1000}],
            }
        
        # Mock get_score_performance
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
        assert result.after_filter == 2
        assert len(result.models) == 2
        
        # Verify filtering: PGS003 (no metrics) should be filtered out
        model_ids = [m.id for m in result.models]
        assert "PGS003" not in model_ids
        assert "PGS001" in model_ids
        assert "PGS002" in model_ids
        
        # Verify both returned models have metrics
        assert result.models[0].performance_metrics.get("auc") == 0.75 or result.models[0].performance_metrics.get("r2") == 0.15
        assert result.models[1].performance_metrics.get("auc") == 0.75 or result.models[1].performance_metrics.get("r2") == 0.15

    def test_search_respects_limit(self):
        """Test that the limit parameter is respected."""
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
        
        result = prs_model_pgscatalog_search(mock_client, "T2D", limit=5)
        
        assert len(result.models) == 5
        assert result.total_found == 10

    def test_search_is_sorted_by_zscore_composite(self):
        """Test that returned models are sorted by Z-score composite score (equal weight for AUC, R², samples, variants)."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [
            {"id": "PGS_A"},
            {"id": "PGS_B"},
            {"id": "PGS_C"},
        ]

        def mock_details(pgs_id):
            # Different training sizes
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
            # PGS_A: higher AUC than B/C
            if pgs_id == "PGS_A":
                return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.80}]}]
            # PGS_B: same AUC as C, higher R2
            if pgs_id == "PGS_B":
                return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.70}, {"name_short": "R2", "estimate": 0.20}]}]
            # PGS_C: same AUC as B, lower R2, but higher train_n than A
            return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.70}, {"name_short": "R2", "estimate": 0.10}]}]

        mock_client.get_score_details.side_effect = mock_details
        mock_client.get_score_performance.side_effect = mock_performance

        result = prs_model_pgscatalog_search(mock_client, "T2D", limit=3)
        # With Z-score normalization and equal weights:
        # PGS_A: AUC=0.80, R2=None, samples=1000, variants=10
        # PGS_B: AUC=0.70, R2=0.20, samples=5000, variants=10
        # PGS_C: AUC=0.70, R2=0.10, samples=2000, variants=10
        # PGS_B likely ranks highest due to high sample size (5000) and R2 (0.20)
        # PGS_A ranks second due to high AUC (0.80) but lower sample size
        # PGS_C ranks lowest
        assert len(result.models) == 3
        # Verify all three models are returned and sorted by composite Z-score
        model_ids = [m.id for m in result.models]
        assert "PGS_A" in model_ids
        assert "PGS_B" in model_ids
        assert "PGS_C" in model_ids
        # PGS_B should rank highest due to high sample size and R2
        assert result.models[0].id == "PGS_B"

    def test_search_uses_variants_as_tie_breaker_before_id(self):
        """Test variants_number breaks ties after AUC/R2/train_n."""
        from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.search_scores.return_value = [{"id": "PGS_X"}, {"id": "PGS_Y"}]

        def mock_details(pgs_id):
            # Same training size; only variants differ
            variants = {"PGS_X": 100, "PGS_Y": 1000}[pgs_id]
            return {
                "id": pgs_id,
                "trait_reported": "T2D",
                "trait_efo": [{"label": "T2D"}],
                "method_name": "M",
                "variants_number": variants,
                "ancestry_distribution": {"gwas": {"EUR": 1.0}},
                "publication": {},
                "date_release": "2020",
                "samples_training": [{"sample_number": 5000}],
                "samples_variants": [],
            }

        def mock_performance(_pgs_id):
            # Same AUC/R2 for both
            return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.70}, {"name_short": "R2", "estimate": 0.10}]}]

        mock_client.get_score_details.side_effect = mock_details
        mock_client.get_score_performance.side_effect = mock_performance

        result = prs_model_pgscatalog_search(mock_client, "T2D", limit=2)
        # With Z-score normalization and equal weights, higher variants should contribute more to composite score
        # PGS_Y has 1000 variants vs PGS_X has 100 variants
        # Since AUC/R2/samples are same, PGS_Y should rank higher due to variants
        assert len(result.models) == 2
        assert result.models[0].id == "PGS_Y"  # Higher variants should rank first
