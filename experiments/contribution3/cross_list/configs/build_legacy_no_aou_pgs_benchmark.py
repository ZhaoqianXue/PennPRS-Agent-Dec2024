"""Restore the C3 80-target benchmark on the legacy target universe.

Contribution3's paper-facing paired80 experiments used Type A targets from
`aou_extend_trait` plus Type B rootcode targets. The Contribution1 refresh
should only remove no-AoU PGS columns, not switch Type A to the broader
`aou_nontarget_pgs` target universe.

This script reconstructs the unified target_selection.csv from a known paired80
evaluation detail file and writes it under:
  experiments/contribution3/cross_list/benchmark_legacy_no_aou_pgs/unified/
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PAIRED80_DETAIL = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "transfer"
    / "runs"
    / "tool_calling_agent"
    / "unified"
    / "ablation__no_all_tools_plus_pgs_skill"
    / "evaluation__paired80_pgs_skill_iter11_repeat2_20260430_024834_w20"
    / "all-tools__end_to_end_eval_detail.csv"
)
OUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy_no_aou_pgs"
)


def main() -> None:
    if not DEFAULT_PAIRED80_DETAIL.exists():
        raise FileNotFoundError(f"Paired80 detail file not found: {DEFAULT_PAIRED80_DETAIL}")

    detail = pd.read_csv(DEFAULT_PAIRED80_DETAIL)
    required = {"target_id", "input_type", "target_source", "target_ontology", "target_description"}
    missing = sorted(required - set(detail.columns))
    if missing:
        raise ValueError(f"Paired80 detail missing required columns: {missing}")

    target_selection = detail.loc[
        :,
        ["input_type", "target_source", "target_id", "target_ontology", "target_description"],
    ].rename(
        columns={
            "target_id": "input_icd",
            "target_ontology": "input_ontology",
            "target_description": "input_description",
        }
    )
    target_selection["target_source"] = target_selection["target_source"].replace(
        {"nontarget_pgs": "extend_trait"}
    )
    target_selection["selected"] = True
    target_selection = target_selection.drop_duplicates("input_icd", keep="first").reset_index(drop=True)

    type_counts = target_selection["input_type"].value_counts(dropna=False).to_dict()
    source_counts = target_selection["target_source"].value_counts(dropna=False).to_dict()
    if len(target_selection) != 80:
        raise ValueError(f"Expected 80 C3 benchmark targets, found {len(target_selection)}")
    if type_counts.get("A") != 60 or type_counts.get("B") != 20:
        raise ValueError(f"Expected 60 Type A and 20 Type B targets, found {type_counts}")
    if source_counts.get("extend_trait") != 60 or source_counts.get("rootcode_main_analysis") != 20:
        raise ValueError(f"Unexpected target_source counts: {source_counts}")

    unified_dir = OUT_DIR / "unified"
    unified_dir.mkdir(parents=True, exist_ok=True)
    target_selection.to_csv(unified_dir / "target_selection.csv", index=False)

    config = {
        "name": "benchmark_legacy_no_aou_pgs",
        "source_detail": str(DEFAULT_PAIRED80_DETAIL.relative_to(PROJECT_ROOT)),
        "target_count": int(len(target_selection)),
        "type_counts": {str(k): int(v) for k, v in type_counts.items()},
        "target_source_counts": {str(k): int(v) for k, v in source_counts.items()},
        "contribution1_matrix_source": "experiments/contribution1/result/legacy_no_aou_pgs",
    }
    (OUT_DIR / "benchmark_config.json").write_text(
        json.dumps(config, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(target_selection)} targets -> {unified_dir / 'target_selection.csv'}")


if __name__ == "__main__":
    main()
