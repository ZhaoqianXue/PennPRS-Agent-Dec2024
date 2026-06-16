from __future__ import annotations

import pandas as pd

from experiments.contribution3.cross_optimized.assets.build_compact_catalog import build_compact_catalog


def test_build_compact_catalog_groups_pgs_by_mapped_trait(tmp_path) -> None:
    scores = tmp_path / "scores.csv"
    efo = tmp_path / "efo.csv"
    pd.DataFrame(
        [
            {
                "Polygenic Score (PGS) ID": "PGS000001",
                "PGS Name": "Score one",
                "Reported Trait": "Trait A",
                "Mapped Trait(s) (EFO label)": "Trait A mapped",
                "Mapped Trait(s) (EFO ID)": "EFO_000001",
                "PGS Development Method": "LDpred2",
                "PGS Development Details/Relevant Parameters": "details",
                "Number of Variants": 1000,
                "PGS Publication (PGP) ID": "PGP000001",
                "Publication (PMID)": "123",
                "Publication (doi)": "10/test",
                "Ancestry Distribution (%) - Source of Variant Associations (GWAS)": "European:100",
                "Ancestry Distribution (%) - Score Development/Training": "European:100",
                "Ancestry Distribution (%) - PGS Evaluation": "European:100",
                "Release Date": "2026-01-01",
            },
            {
                "Polygenic Score (PGS) ID": "PGS000002",
                "PGS Name": "Score two",
                "Reported Trait": "Trait A subtype",
                "Mapped Trait(s) (EFO label)": "Trait A mapped",
                "Mapped Trait(s) (EFO ID)": "EFO_000001",
                "PGS Development Method": "PRS-CS",
                "PGS Development Details/Relevant Parameters": "details",
                "Number of Variants": 2000,
                "PGS Publication (PGP) ID": "PGP000002",
                "Publication (PMID)": "456",
                "Publication (doi)": "10/test2",
                "Ancestry Distribution (%) - Source of Variant Associations (GWAS)": "European:100",
                "Ancestry Distribution (%) - Score Development/Training": "European:100",
                "Ancestry Distribution (%) - PGS Evaluation": "European:100",
                "Release Date": "2026-01-02",
            },
        ]
    ).to_csv(scores, index=False)
    pd.DataFrame(
        [
            {
                "Ontology Trait ID": "EFO_000001",
                "Ontology Trait Label": "Canonical Trait A",
                "Ontology Trait Description": "",
                "Ontology URL": "",
            }
        ]
    ).to_csv(efo, index=False)

    catalog = build_compact_catalog(scores_csv=scores, efo_traits_csv=efo)

    assert len(catalog["pgs_records"]) == 2
    assert len(catalog["bundles"]) == 1
    bundle = catalog["bundles"][0]
    assert bundle["canonical_label"] == "Canonical Trait A"
    assert bundle["candidate_pgs_ids"] == ["PGS000001", "PGS000002"]


def test_build_compact_catalog_adds_pgs_catalog_performance_summary(tmp_path) -> None:
    scores = tmp_path / "scores.csv"
    efo = tmp_path / "efo.csv"
    metrics = tmp_path / "metrics.csv"
    sample_sets = tmp_path / "sample_sets.csv"
    pd.DataFrame(
        [
            {
                "Polygenic Score (PGS) ID": "PGS000003",
                "PGS Name": "Score three",
                "Reported Trait": "Trait B",
                "Mapped Trait(s) (EFO label)": "Trait B mapped",
                "Mapped Trait(s) (EFO ID)": "EFO_000002",
                "PGS Development Method": "BOLT-LMM",
                "PGS Development Details/Relevant Parameters": "details",
                "Number of Variants": 100,
                "PGS Publication (PGP) ID": "PGP000003",
                "Publication (PMID)": "789",
                "Publication (doi)": "10/test3",
                "Ancestry Distribution (%) - Source of Variant Associations (GWAS)": "European:100",
                "Ancestry Distribution (%) - Score Development/Training": "European:100",
                "Ancestry Distribution (%) - PGS Evaluation": "European:100",
                "Release Date": "2026-01-03",
            }
        ]
    ).to_csv(scores, index=False)
    pd.DataFrame(
        [
            {
                "Ontology Trait ID": "EFO_000002",
                "Ontology Trait Label": "Canonical Trait B",
                "Ontology Trait Description": "",
                "Ontology URL": "",
            }
        ]
    ).to_csv(efo, index=False)
    pd.DataFrame(
        [
            {
                "PGS Performance Metric (PPM) ID": "PPM000001",
                "Evaluated Score": "PGS000003",
                "PGS Sample Set (PSS)": "PSS000001",
                "Reported Trait": "Trait B",
                "Hazard Ratio (HR)": "",
                "Odds Ratio (OR)": "",
                "Beta": "0.42 (0.01)",
                "Area Under the Receiver-Operating Characteristic Curve (AUROC)": "",
                "Concordance Statistic (C-index)": "",
                "Other Metric(s)": "Incremental R2 = 0.12",
            },
            {
                "PGS Performance Metric (PPM) ID": "PPM000002",
                "Evaluated Score": "PGS000003",
                "PGS Sample Set (PSS)": "PSS000002",
                "Reported Trait": "Trait B",
                "Hazard Ratio (HR)": "",
                "Odds Ratio (OR)": "",
                "Beta": "",
                "Area Under the Receiver-Operating Characteristic Curve (AUROC)": "0.71 [0.68,0.74]",
                "Concordance Statistic (C-index)": "",
                "Other Metric(s)": "",
            },
        ]
    ).to_csv(metrics, index=False)
    pd.DataFrame(
        [
            {
                "PGS Sample Set (PSS)": "PSS000001",
                "Polygenic Score (PGS) ID": "PGS000003",
                "Number of Individuals": 1000,
                "Number of Cases": 400,
                "Number of Controls": 600,
                "Broad Ancestry Category": "European",
            },
            {
                "PGS Sample Set (PSS)": "PSS000002",
                "Polygenic Score (PGS) ID": "PGS000003",
                "Number of Individuals": 2500,
                "Number of Cases": 1000,
                "Number of Controls": 1500,
                "Broad Ancestry Category": "East Asian",
            },
        ]
    ).to_csv(sample_sets, index=False)

    catalog = build_compact_catalog(
        scores_csv=scores,
        efo_traits_csv=efo,
        performance_metrics_csv=metrics,
        evaluation_sample_sets_csv=sample_sets,
    )

    performance = catalog["pgs_records"][0]["performance"]
    assert performance["performance_record_count"] == 2
    assert performance["sample_set_count"] == 2
    assert performance["evaluation_sample_max"] == 2500
    assert performance["evaluation_sample_total"] == 3500
    assert performance["best_auc"] == 0.71
    assert performance["best_r2"] == 0.12
    assert performance["best_abs_beta"] == 0.42
    assert performance["evaluation_ancestry"] == ["East Asian", "European"]
