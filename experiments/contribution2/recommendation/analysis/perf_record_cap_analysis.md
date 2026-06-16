# Performance-record CAP analysis (45-disease, offline)

Source: local `data/pgs_all_metadata/` (scores 5,332; performance 20,709; sample sets 10,108).
Population: 1,363 unique candidate PGS across 43/45 diseases (82-disease evaluated pool; alzheimer + varicose veins absent from that pool).

## Filters applied (the final rule)
1. PSS collapse (one row per distinct sample set).
2. Ancestry: pure-European (broad ancestry ⊆ {European, NR}).
3. Endpoint: containment — performance-record `Reported Trait` must contain the score's Predicted Trait (`Reported Trait` in scores.csv), case-insensitive. No per-disease lexicon.
4. Comparable axes = {PRS_R2, OR, HR, C-index} (full-model AUROC excluded as weak/inflated).

## Key distributions (n=1363)
- Distinct European+containment PSS per PGS: median **1**, p90 **2**, max 44. ≥2: **16%**; ≥3: 10%; ≥5: 2%; ≥10: 0.4%.
- Distinct comparable axes available: 0→811 PGS, 1→356, 2→161, 3→33, 4→2.
- **Records needed to cover ALL available comparable axes**: 0→811, **1→524**, 2→26, 3→2, max **3**.
  - Among PGS with any comparable axis (552): **95% need 1 record; 5% benefit from 2+; only 2 PGS need 3.**

## Recommendation
- **Cap = 3 (absolute ceiling).** Not a fixed 3–5; the earlier 3–5 was anchored to the PGS000013 outlier (44 European records — one of only 2 PGS in the whole set needing 3).
- Rule: **keep the anchor (most comparable axes, then largest n); add a further record ONLY if it introduces a NEW comparable axis; stop at 3.**
- Realized count: **1 for the overwhelming majority**, 2 for ~2%, 3 for ~0.1%. Multi-record (≥2) adds comparable-axis signal for only ~28/1363 (2%) of candidates.

## Worked examples (under this rule)
- **PGS000013** → keep **3**: PSS000468 (HR+C-index, "Incident coronary artery disease"), PSS000900 (OR, n=474k), PSS000015 (PRS_R2). Covers all 4 axes.
- **PGS003725** → keep **1**: PSS010960 (HR+OR; covers both its axes). MVP OR record adds no new axis → dropped.

## Caveats
- Containment drops literal-synonym endpoints (e.g. "coronary heart disease") — for PGS000013 it drops the CHD survival records but retains the "Incident coronary **artery** disease" survival record (PSS000468), so the HR/C-index axis survives here by luck of wording.
- Objective = comparable-axis coverage. Cross-cohort replication value is NOT counted (record_count Spearman≈0.03, validation_n≈0.13 — both weak), so it is intentionally ignored.
- `phenotyping_reported` is still carried into the JSON per kept record for the LLM's endpoint judgment.
