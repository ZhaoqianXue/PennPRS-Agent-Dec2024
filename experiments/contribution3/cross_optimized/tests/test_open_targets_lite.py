from __future__ import annotations

import json

from experiments.contribution3.cross_optimized.batch.open_targets_lite import (
    build_open_targets_lite_evidence,
    compact_open_targets_bridge_card,
)


class FakeSearchHit:
    def __init__(self, id_: str) -> None:
        self.id = id_


class FakeOpenTargetsClient:
    def __init__(self) -> None:
        self.search_queries: list[str] = []
        self.profile_ids: list[str] = []

    def search_diseases(self, query: str, size: int = 3) -> dict:
        self.search_queries.append(query)
        if query == "Target disease":
            return {"hits": [FakeSearchHit("EFO_TARGET")]}
        return {"hits": []}

    def get_disease_target_profile(self, efo_id: str, page_size: int = 80) -> dict:
        self.profile_ids.append(efo_id)
        return {
            "EFO_TARGET": {
                "id": "EFO_TARGET",
                "name": "Target disease",
                "associated_targets": [
                    {"id": "ENSG1", "approvedSymbol": "GENE1", "datatypeScores": [{"id": "genetic_association"}]},
                    {"id": "ENSG2", "approvedSymbol": "GENE2", "datatypeScores": []},
                ],
                "therapeutic_areas": [{"id": "TA1", "name": "area"}],
                "ancestors": [{"id": "A1", "name": "ancestor"}],
            },
            "EFO_CANDIDATE": {
                "id": "EFO_CANDIDATE",
                "name": "Candidate trait",
                "associated_targets": [
                    {"id": "ENSG1", "approvedSymbol": "GENE1", "datatypeScores": [{"id": "known_drug"}]},
                    {"id": "ENSG3", "approvedSymbol": "GENE3", "datatypeScores": []},
                ],
                "therapeutic_areas": [{"id": "TA1", "name": "area"}],
                "ancestors": [{"id": "A1", "name": "ancestor"}],
            },
        }[efo_id]


def test_open_targets_lite_builds_cached_raw_overlap_without_scores(tmp_path) -> None:
    candidate_request = tmp_path / "stage_d.jsonl"
    payload = {
        "target": {"target_id": "X01", "label": "Target disease, extra wording"},
        "candidate_evidence_cards": [
            {"pgs_id": "PGS000001", "reported_trait": "Candidate trait", "mapped_trait_ids": ["EFO_CANDIDATE"]},
            {"pgs_id": "PGS000002", "reported_trait": "Candidate duplicate", "mapped_trait_ids": ["EFO_CANDIDATE"]},
        ],
    }
    candidate_request.write_text(
        json.dumps({"body": {"input": [{"role": "system", "content": "s"}, {"role": "user", "content": json.dumps(payload)}]}})
        + "\n",
        encoding="utf-8",
    )
    client = FakeOpenTargetsClient()

    evidence = build_open_targets_lite_evidence(
        candidate_request_path=candidate_request,
        client=client,
        top_n=2,
        profile_page_size=80,
    )

    assert client.search_queries[:2] == ["Target disease, extra wording", "Target disease"]
    assert client.profile_ids == ["EFO_TARGET", "EFO_CANDIDATE"]
    row = evidence["X01"]["PGS000001"]
    assert row["target_disease_id"] == "EFO_TARGET"
    assert row["candidate_disease_id"] == "EFO_CANDIDATE"
    assert row["shared_gene_count"] == 1
    assert row["shared_genes"] == [
        {
            "gene": "GENE1",
            "target_id": "ENSG1",
            "target_datatypes": ["genetic_association"],
            "candidate_datatypes": ["known_drug"],
        }
    ]
    assert row["shared_therapeutic_areas"] == [{"id": "TA1", "name": "area"}]
    assert row["shared_ancestors"] == [{"id": "A1", "name": "ancestor"}]
    payload_text = json.dumps(evidence).lower()
    assert "score" not in payload_text
    assert "recommend" not in payload_text


def test_open_targets_bridge_card_compacts_raw_evidence_without_selection_language() -> None:
    raw = {
        "target_disease_id": "EFO_TARGET",
        "target_disease_label": "Target disease",
        "candidate_disease_id": "EFO_CANDIDATE",
        "candidate_disease_label": "Candidate trait",
        "candidate_trait_basis": {
            "mapped_trait_ids": ["EFO_CANDIDATE"],
            "mapped_trait_labels": ["Candidate trait"],
            "reported_trait": "Candidate trait from PGS Catalog",
        },
        "target_associated_gene_count": 80,
        "candidate_associated_gene_count": 80,
        "shared_gene_count": 2,
        "shared_genes": [
            {
                "gene": "GENE1",
                "target_id": "ENSG1",
                "target_datatypes": ["genetic_association"],
                "candidate_datatypes": ["literature", "known_drug"],
            },
            {
                "gene": "GENE2",
                "target_id": "ENSG2",
                "target_datatypes": ["somatic_mutation"],
                "candidate_datatypes": ["somatic_mutation"],
            },
        ],
        "shared_therapeutic_areas": [{"id": "TA1", "name": "shared area"}],
        "shared_ancestors": [{"id": "A1", "name": "shared ancestor"}],
    }

    card = compact_open_targets_bridge_card(raw, shared_gene_cap=1)

    assert card == {
        "target_disease_id": "EFO_TARGET",
        "target_disease_label": "Target disease",
        "candidate_disease_id": "EFO_CANDIDATE",
        "candidate_disease_label": "Candidate trait",
        "candidate_trait_basis": {
            "mapped_trait_ids": ["EFO_CANDIDATE"],
            "mapped_trait_labels": ["Candidate trait"],
            "reported_trait": "Candidate trait from PGS Catalog",
        },
        "relationship_observations": [
            "different ontology ids",
            "shared therapeutic area: shared area",
            "shared ancestor: shared ancestor",
            "shared associated targets: 2 of target_top80 and candidate_top80",
        ],
        "shared_target_examples": [
            {
                "gene": "GENE1",
                "target_id": "ENSG1",
                "target_datatypes": ["genetic_association"],
                "candidate_datatypes": ["literature", "known_drug"],
            }
        ],
        "caveats": [
            "associated target overlap is raw OpenTargets context, not a causal or predictive claim",
            "top-page associated targets can overrepresent broad, well-studied traits",
        ],
    }
    payload_text = json.dumps(card).lower()
    assert "score" not in payload_text
    assert "rank" not in payload_text
    assert "recommend" not in payload_text
    assert "winner" not in payload_text
