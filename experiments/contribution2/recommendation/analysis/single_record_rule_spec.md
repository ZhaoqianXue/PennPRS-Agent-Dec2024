# Unrestricted 7-section candidate serialization — engineering spec

Trait-agnostic. One self-contained 7-section record per candidate PGS, with all
multi-row PGS Catalog source blocks preserved as arrays. The implementation
builds from `data/pgs_all_metadata/pgs_full_rest_dump.jsonl`; the CSV columns
below are the source-table equivalents.

## Local CSV sources
| File | Key columns used |
|---|---|
| `pgs_all_metadata_scores.csv` | `Polygenic Score (PGS) ID`, `Reported Trait` (= **Predicted Trait**, containment key), `Mapped Trait(s) (EFO label)`, `Mapped Trait(s) (EFO ID)`, `PGS Development Method`, `Number of Variants`, `Release Date`, `PGS Publication (PGP) ID`/`Publication (PMID)`/`Publication (doi)` |
| `pgs_all_metadata_performance_metrics.csv` | `Evaluated Score`, `PGS Performance Metric (PPM) ID`, `PGS Sample Set (PSS)`, `Reported Trait` (per-record), `Covariates Included in the Model`, `Hazard Ratio (HR)`, `Odds Ratio (OR)`, `Area Under the Receiver-Operating Characteristic Curve (AUROC)`, `Concordance Statistic (C-index)`, `Other Metric(s)` |
| `pgs_all_metadata_evaluation_sample_sets.csv` | `PGS Sample Set (PSS)`, `Number of Individuals/Cases/Controls`, `Broad Ancestry Category`, `Cohort(s)`, `Phenotype Definitions and Methods` |
| `pgs_all_metadata_score_development_samples.csv` | `Polygenic Score (PGS) ID`, `Stage of PGS Development` ∈ {`Source of Variant Associations (GWAS)`, `Score Development/Training`}, `Number of Individuals/Cases/Controls`, `Broad Ancestry Category`, `Cohort(s)` |

## Helpers
```
# Do not split metric values into PRS-only/full-model/R2/AUROC/C-index fields
# in the LLM-facing schema. Preserve the PGS Catalog metric buckets:
# REST effect_sizes -> effect_sizes
# REST class_acc    -> classification_metrics
# REST othermetrics -> other_metrics
# Individual metric entries are compacted to metric_name + estimate/CI fields;
# source name_short/name_long fields are not exposed in the candidate payload.
```

## Output assembly (fixed sections, fixed order)
```
gwas  = dev_samples[pgs_id, Stage == "Source of Variant Associations (GWAS)"]
train = dev_samples[pgs_id, Stage == "Score Development/Training"]

{
  "id": pgs_id,
  "predicted_trait": {
    "trait_reported": score["Reported Trait"],
    "trait_efo": [{ "label": score["Mapped Trait(s) (EFO label)"], "id": score["Mapped Trait(s) (EFO ID)"] }]
  },
  "development_method": { "method_name": score["PGS Development Method"] },
  "variants": { "variants_number": score["Number of Variants"] },
  "pgs_source": {
    "publication_title": publications[score.PGP]["title"],
    "publication_journal": publications[score.PGP]["journal"],
    "date_release": score["Release Date"]
  },
  "source_of_variant_associations_gwas": [
    {
      "sample_numbers": { "individuals": gwas_row.Individuals, "cases": gwas_row.Cases, "controls": gwas_row.Controls },
      "ancestry": gwas_row["Broad Ancestry Category"],
      "cohorts": split(gwas_row["Cohort(s)"], "|")
    }
  ],
  "score_development_training": [
    {
      "sample_numbers": { "individuals": train_row.Individuals, "cases": train_row.Cases, "controls": train_row.Controls },
      "ancestry": train_row["Broad Ancestry Category"]
    }
  ],
  "performance_metrics": [
    {
      "performance_id": performance_row["PGS Performance Metric (PPM) ID"],
      "phenotyping_reported": performance_row["Reported Trait"],
      "covariates": performance_row["Covariates Included in the Model"],
      "effect_sizes": rest_performance["performance_metrics"]["effect_sizes"],
      "classification_metrics": rest_performance["performance_metrics"]["class_acc"],
      "other_metrics": rest_performance["performance_metrics"]["othermetrics"],
      "evaluation_samples": [
        {
          "sample_numbers": { "individuals": ss.Individuals, "cases": ss.Cases, "controls": ss.Controls },
          "ancestry": ss["Broad Ancestry Category"],
          "cohorts": split(ss["Cohort(s)"], "|")
        }
      ]
    }
  ]
}
```

## Field cleanups (vs prior schema) — all applied above
- DROP `percent_male`, ancestry `free`/`country` from the primary representative record (keep `broad` only, renamed `ancestry`), `sample_set_id`.
- `phenotyping_reported` lives in each `performance_metrics[]` item, not `predicted_trait`.
- GWAS and Training are SEPARATE sections and preserve all source rows.

## Known limitations (carry into LLM, do not hard-fix in code)
- Classification metrics and other metrics can encode PRS-only, full-model,
  incremental, C-index, R²-like, and study-specific values. The schema does not
  pre-classify them; downstream rules or the LLM must interpret metric names and
  covariate context explicitly.
