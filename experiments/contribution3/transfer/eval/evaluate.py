from __future__ import annotations

"""
Compatibility entrypoint for Cross Trait Evaluation.

Cross Trait Evaluation now defaults to the end-to-end setup:

Cross Trait Transfer + PRS Recommendation -> full Contribution1 AUC-matrix
GPR / Hit@Top% / Absolute AUC Regret evaluation.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.evaluate_end_to_end import (
    evaluate_end_to_end_condition,
    main,
)

__all__ = ["evaluate_end_to_end_condition", "main"]


if __name__ == "__main__":
    main()
