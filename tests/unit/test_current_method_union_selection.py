from experiments.contribution2.disease_selection.configs.build_current_method_union import (
    build_current_method_union,
)


def test_default_current_method_union_builds_rootcode_45_disease_list():
    union_df, detail_df = build_current_method_union()

    ontologies = set(union_df["Ontology"])

    assert len(union_df) == 45
    assert len(detail_df) == 45
    assert set(union_df["Source"]) == {"rootcode"}
    assert "varicose veins" in ontologies
    assert "alzheimer disease" in ontologies
    assert "prostate disease" not in ontologies
    assert "overnutrition" not in ontologies
    assert "testicular neoplasm" not in ontologies
