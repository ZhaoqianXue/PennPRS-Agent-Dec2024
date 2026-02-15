#!/usr/bin/env python3
"""
Split aou_pgs_trait_overlap_by_pgs.csv into two files:
1. Four SOP focus categories: cancer, mental, neurodegenerative, heart
2. Remaining categories
"""

import csv
from pathlib import Path

SOP_FOUR_CATEGORIES = {"cancer", "mental", "neurodegenerative", "heart"}

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "all_of_us"
INPUT_CSV = DATA_DIR / "aou_pgs_trait_overlap_by_pgs.csv"
OUTPUT_DIR = DATA_DIR / "sop_focus_split"
OUTPUT_FOUR = OUTPUT_DIR / "aou_pgs_four_categories.csv"
OUTPUT_OTHER = OUTPUT_DIR / "aou_pgs_other_categories.csv"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(INPUT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    four_rows = [r for r in rows if r.get("label", "").lower() in SOP_FOUR_CATEGORIES]
    other_rows = [r for r in rows if r.get("label", "").lower() not in SOP_FOUR_CATEGORIES]

    with open(OUTPUT_FOUR, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(four_rows)

    with open(OUTPUT_OTHER, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(other_rows)

    print(f"Written {len(four_rows)} rows to {OUTPUT_FOUR}")
    print(f"Written {len(other_rows)} rows to {OUTPUT_OTHER}")


if __name__ == "__main__":
    main()
