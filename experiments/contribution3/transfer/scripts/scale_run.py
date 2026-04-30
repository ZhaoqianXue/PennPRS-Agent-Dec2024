"""P8 helper: scale the LLM-led agent from the 5-target debug set to
larger subsets using the existing batch runner.

Usage:
  python -m experiments.contribution3.transfer.scripts.scale_run \
      --target-ids D25,B20,L02,F33,G56,...  \
      --run-id scale_20_20260423 \
      --workers 4

Emits results + recommendations + evaluation for the chosen subset.
No decision-layer code here; this is just an orchestrator that invokes
`batch.run_batch` with a subset target list.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.batch import run_batch  # noqa: E402
from experiments.contribution3.transfer.common import (  # noqa: E402
    DEFAULT_TRANSFER_ABLATION,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-ids", default="", type=str,
                        help="Comma-separated target IDs. Empty = full set (80).")
    parser.add_argument("--run-id", required=True, type=str)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--condition", default="all-tools")
    parser.add_argument("--benchmark-family", default="unified")
    parser.add_argument("--ablation", default=DEFAULT_TRANSFER_ABLATION)
    parser.add_argument("--skip-prepare-assets", action="store_true")
    args = parser.parse_args()

    run_batch.cmd_offline_unified(
        argparse.Namespace(
            condition=args.condition,
            target_ids=args.target_ids,
            run_id=args.run_id,
            workers=args.workers,
            ablation=args.ablation,
            skip_prepare_assets=bool(args.skip_prepare_assets),
        )
    )


if __name__ == "__main__":
    main()
