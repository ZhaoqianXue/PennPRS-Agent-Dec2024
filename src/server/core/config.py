
import os
from pathlib import Path

# Define project root relative to this file
# This file is in src/server/core/config.py
# Root is ../../../
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def get_data_path(relative_path: str) -> Path:
    """
    Get absolute path to a data file, ensuring it resolves correctly 
    relative to the project root.
    """
    return PROJECT_ROOT / relative_path
