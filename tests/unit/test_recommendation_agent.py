import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_resolve_efo_id_returns_none_for_no_hits():
    from src.server.modules.disease.recommendation_agent import resolve_efo_id

    class StubOtClient:
        def search_diseases(self, query, page=0, size=10):
            return {"hits": []}

    assert resolve_efo_id(
        "Example Trait",
        ot_client=StubOtClient(),
        pgs_client=None,
        pgs_models=None
    ) is None


def test_resolve_efo_id_prefers_pgs_mapping():
    from src.server.modules.disease.recommendation_agent import resolve_efo_id

    class StubPgsClient:
        def search_traits(self, term):
            return []

        def get_score_details(self, pgs_id):
            return {
                "trait_efo": [
                    {"id": "EFO_123", "label": "Example Trait"}
                ]
            }

    class StubOtClient:
        def __init__(self):
            self.called = False

        def search_diseases(self, query, page=0, size=10):
            self.called = True
            return {"hits": [{"id": "EFO_999", "name": "Example"}]}

    class StubModel:
        id = "PGS000001"

    ot_client = StubOtClient()
    efo_id = resolve_efo_id(
        "Example Trait",
        ot_client=ot_client,
        pgs_client=StubPgsClient(),
        pgs_models=[StubModel()]
    )

    assert efo_id == "EFO_123"
    assert ot_client.called is False


def test_select_best_efo_candidate_prefers_mechanism_confidence():
    from src.server.modules.disease.recommendation_agent import (
        select_best_efo_candidate,
        EfoCandidate
    )
    from src.server.core.tool_schemas import MechanismValidation

    def validate_fn(source_efo, target_efo, source_trait, target_trait):
        if target_efo == "EFO_1":
            return MechanismValidation(
                source_trait=source_trait,
                target_trait=target_trait,
                shared_genes=[],
                shared_pathways=[],
                phewas_evidence_count=0,
                mechanism_summary="Low evidence",
                confidence_level="Low"
            )
        return MechanismValidation(
            source_trait=source_trait,
            target_trait=target_trait,
            shared_genes=[],
            shared_pathways=[],
            phewas_evidence_count=0,
            mechanism_summary="High evidence",
            confidence_level="High"
        )

    candidates = [
        EfoCandidate(id="EFO_1", label="Trait A", score=0.52, source="ot"),
        EfoCandidate(id="EFO_2", label="Trait B", score=0.50, source="ot")
    ]

    chosen, mechanism = select_best_efo_candidate(
        target_trait_name="Trait X",
        target_efo_id="EFO_TARGET",
        neighbor_trait_name="Trait Y",
        candidates=candidates,
        validate_fn=validate_fn,
        gap_threshold=0.05
    )

    assert chosen is not None
    assert chosen.id == "EFO_2"
    assert mechanism is not None
    assert mechanism.confidence_level == "High"


def test_ensure_follow_up_options_inserts_train_option():
    from src.server.modules.disease.recommendation_agent import ensure_follow_up_options
    from src.server.modules.disease.models import RecommendationReport

    report = RecommendationReport(
        recommendation_type="NO_MATCH_FOUND",
        primary_recommendation=None,
        alternative_recommendations=[],
        direct_match_evidence=None,
        cross_disease_evidence=None,
        caveats_and_limitations=[],
        follow_up_options=[]
    )

    updated = ensure_follow_up_options(report)

    assert any(
        option.action == "TRIGGER_PENNPRS_CONFIG"
        for option in updated.follow_up_options
    )
