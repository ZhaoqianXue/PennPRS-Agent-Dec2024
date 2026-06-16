from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CROSS_OPT_DIR = Path(__file__).resolve().parent
RUNS_DIR = CROSS_OPT_DIR / "runs"

PGS_SCORES_CSV = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_all_metadata_scores.csv"
PGS_EFO_TRAITS_CSV = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_all_metadata_efo_traits.csv"
PGS_PERFORMANCE_METRICS_CSV = (
    PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_all_metadata_performance_metrics.csv"
)
PGS_EVALUATION_SAMPLE_SETS_CSV = (
    PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_all_metadata_evaluation_sample_sets.csv"
)
PGS_CATALOG_CACHE = PROJECT_ROOT / "data" / "pgs_catalog_cache" / "pgs_catalog_cache.pkl"

BENCHMARK_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy_no_aou_pgs"
)
TARGET_SELECTION_CSV = BENCHMARK_DIR / "unified" / "target_selection.csv"

LEGACY_NO_AOU_ROOT = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "legacy_no_aou_pgs"
)
ROOTCODE_AUC_MATRIX = (
    LEGACY_NO_AOU_ROOT / "aou_binary" / "prs_adjauc_matrix_binary_combined_rootcode.csv"
)
EXTEND_TRAIT_AUC_MATRIX = (
    LEGACY_NO_AOU_ROOT / "aou_extend_trait" / "prs_adjauc_matrix_binary_extend_qc.csv"
)

DEFAULT_COMPACT_CATALOG_JSON = RUNS_DIR / "assets" / "compact_catalog.json"


def matrix_path_for_target_source(target_source: str | None) -> Path:
    source = str(target_source or "").strip()
    if source in {"extend_trait", "nontarget_pgs"}:
        return EXTEND_TRAIT_AUC_MATRIX
    return ROOTCODE_AUC_MATRIX
