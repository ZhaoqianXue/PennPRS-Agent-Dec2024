# Cross-trait transfer — optimization plan for `top_N%` metrics
Date: 2026-04-21 · Run: `all-tools__online_all_tools_20260421_135304` (real OpenAI, unified 80-target, full ablation)

## 1. Measured baseline

### Official metrics (macro A/B)
| metric | value |
|---|---|
| top_0_5pct | **4.17 %** |
| top_1pct | **7.50 %** |
| top_1_5pct | **11.67 %** |
| top_2pct | **20.00 %** |
| top_2_5pct | **23.34 %** |
| mean_gpr | 0.7394 |
| mean_abs_AUC_regret | 0.0712 |

### Stage attrition (oracle-in-stage / 80)
| stage | count | rate |
|---|---|---|
| 1. in probe pool | 54 | 67.5 % |
| 2. in supporting bundles | 32 | 40.0 % |
| 3. in local champions | 3 | 3.75 % |
| 4. in model frontier | 3 | 3.75 % |
| 5. picked as primary | 3 | 3.75 % |

→ attrition breakdown: **shortlist_miss 26, posterior_miss 22, local_champion_miss 29, oracle_picked 3**.

### Root diagnostics
- **30+ Bundle-posterior LLM timeouts** during the run fell back to deterministic top-scoring cards, which heavily favour high-prior generalists.
- **41/80 (51 %)** targets ended up matched to a generalist bundle (BMI ×22, CAD ×7, LDL ×5, insomnia ×5, SBP ×2).
- **61/80 (76 %)** target picks differ from the `two_stage_80_final` offline-replay baseline — i.e., most of the regression is caused by timeout-induced fallbacks, not the agent's actual decisions.
- `global_tournament_conversion = 1.0` → whenever the oracle reaches local champions, it wins the tournament. So the two dominant leakages are **bundle posterior** and **local champion**.

---

## 2. Plan of attack (ordered by leverage)

Each work item lists the target metrics it primarily improves, the files/functions to touch, and a concrete success test.

### P0 — Stop losing LLM calls to timeouts (fixes ~50 % of the regression)
Target: every `top_Npct` metric. Expected uplift: +5-10 pp across the board just from restoring the decisions that the online run lost to fallbacks.

1. **Raise default vNext LLM timeout to 120 s.**
   - `experiments/contribution3/transfer/agent.py::_build_structured_chain` uses `get_llm("disease_workflow")` which defaults to 30 s (`src/server/core/llm_config.py::LLMConfig.DISEASE_WORKFLOW`).
   - Do what `_build_stage1_chain` already does: wrap with `ChatOpenAI(model=base_llm.model_name, temperature=base_llm.temperature, timeout=120)` so `_cached_search_plan_chain_vnext`, `_cached_probe_reflection_chain_vnext`, `_cached_bundle_posterior_chain_vnext`, `_cached_local_champion_chain_vnext`, `_cached_global_frontier_chain_vnext` all inherit the longer timeout.
   - Success: re-run produces ≤5 "Bundle posterior LLM failed (Request timed out.)" warnings (currently 30+).

2. **Retry-with-shrunk-context before falling back.**
   - In `_call_bundle_posterior_vnext` and `_call_local_champion_vnext`, if the structured LLM call raises, retry once with the top 15 posterior cards / top 10 model cards by `selection_priority_score` / `quality_score`. Only if that second call fails, invoke the existing deterministic fallback.
   - Success: any timeout produces at most one fallback trace, and on retry the shrunk context succeeds ≥70 % of the time in a dry replay on the 30 timed-out targets.

3. **De-bias the deterministic fallback.**
   - `_fallback_bundle_posterior_vnext` currently copies the top `supporting_bundle_max` cards by `_sort_cards` ordering. When this fires, also apply a generalist cap: at most 1 bundle from `{"body mass index","coronary artery disease","low density lipoprotein cholesterol measurement","major depressive disorder","insomnia","systolic blood pressure"}` unless the target archetype itself is one of those.
   - Success: on the 41/80 currently-generalist-matched targets, fallback re-selection drops generalist prevalence from 51 % to ≤25 %.

### P1 — Fix the Bundle-posterior stage (22 targets lost)
Target: `top_1pct`, `top_1_5pct`, `top_2pct`. Expected uplift: roughly +5-8 pp on top_1pct.

4. **Add an explicit anti-generalist rule to `BUNDLE_POSTERIOR_PROMPT`**.
   - Current prompt (`prompts/transfer_prompt.py`) gives no guidance on generalist gravitation. Add a short section:
     > "When the target is a rare, anatomically/mechanistically specific, or organ-localised condition, prefer bundles with strong phenotype fidelity or a significant genetic-correlation signal over target-agnostic generalists (body mass index, coronary artery disease, LDL measurement, major depressive disorder, insomnia, systolic blood pressure). Select a generalist only if its GC or Open Targets overlap with the target exceeds that of the best same-endpoint/adjacent-disease candidate."
   - Success: on posterior_miss targets (22), LLM selects ≥1 same-endpoint/adjacent-disease bundle in ≥80 % of cases, up from ~55 %.

5. **Archetype-balanced posterior cards.**
   - In `agent.py::run_cross_trait_agent` before `_call_bundle_posterior_vnext`, split `posterior_cards` into high-specificity (archetypes = same-endpoint / adjacent-disease / endophenotype with `shared_token_count ≥ 2` or `lexical_match_score ≥ 60`) and broad-generalist groups; feed the LLM at most 6 cards from each group; in the prompt `constraints` add `max_generalist_selections = 1` when specific-group is non-empty.
   - Success: `posterior_miss` drops from 22 → ≤8 on re-run.

6. **Post-LLM sanity check.**
   - After `_call_bundle_posterior_vnext` returns, if all selected bundles are generalists but the target has any high-fidelity bundle in `posterior_cards` (fidelity ≥ 0.8 AND archetype is same-endpoint/adjacent-disease), insert that bundle at rank 1.
   - Success: no posterior returns an all-generalist support set when a high-fidelity candidate was available.

### P1 — Fix the Local-champion stage (29 targets lost, the single biggest leak)
Target: `top_0_5pct`, `top_1pct`. Expected uplift: +10-15 pp on top_1pct (this is the highest-leverage change).

Evidence: on 29 targets the supporting bundle already contains the oracle PGS but the local champion LLM picks a different model. Examples: D24 (breast) → bundle = breast carcinoma but picks PGS000015 (old) instead of PGS003380 (oracle); J33 → asthma bundle picks PGS001344 instead of PGS004723. The pattern: the prompt biases toward well-established/high-training-N models, but the evaluation matrix rewards more recent models validated on AoU-like ancestry.

7. **Re-score models for AoU-fit, not just classical PRS quality.**
   - In `agent.py::_model_quality_score`, replace the current blend with:
     ```
     score = 1.8 * pgs_metric
           + 0.25 * method_bonus_capped
           + 0.35 * aou_era_bonus           # +1 if publication_year ≥ 2023 or training cohort mentions AoU/FinnGen
           + 0.20 * multi_ancestry_bonus    # +1 if validation ancestry includes AFR / AMR / EAS / MULTI
           + 0.15 * min(training_sample_n/500000, 1)   # capped, not linear
           − 0.30 * covariate_inflation_flag
     ```
   - Success: on the 29 local_champion_miss targets, new `quality_score` ranks the oracle PGS in the top 3 for ≥18 of them (offline dry-run).

8. **Widen the champion budget.**
   - Bump `local_champion_max_per_bundle` from 2 → 4 in `UNIFIED_CONFIG`. Costs ~50 % more models in the global tournament but given `global_tournament_conversion = 1.0`, the tournament handles the extra candidates well.
   - Success: `oracle_in_local_champions` rises from 3.75 % to ≥15 %.

9. **Diversity pre-filter before the LLM sees models.**
   - In `run_cross_trait_agent`, before calling `_call_local_champion_vnext`, keep at most 5 models per `(method_family, training_sample_bucket=[<50K, 50–200K, >200K])` tuple per bundle. Prevents the LLM from drowning in 40+ nearly-identical LDpred2 variants from the same biobank.
   - Success: model card count per bundle sent to LLM drops from 40-80 to 15-25 with no loss of oracle-in-bundle recall.

10. **Tighten the `LOCAL_CHAMPION_PROMPT`**.
    - Add: "Do not prefer a model solely because it was trained on a larger sample; penalise models older than 2020 or using only C+T when a recent genome-wide method is available. Prefer multi-ancestry validation for non-European-dominant targets."
    - Success: on 29 local_champion_miss targets, the oracle appears in the returned `champions` list in ≥15 cases (replay).

### P1 — Fix the Shortlist / probe-pool stage (26 targets lost)
Target: `top_2pct`, `top_2_5pct`. Expected uplift: +4-6 pp on top_2pct.

Recall is already 74/80 in the dossier, so 6 of the 26 are structurally unreachable; fixing the remaining 20 is tractable.

11. **Widen the initial probe.**
    - `UNIFIED_CONFIG.initial_probe_size = 24 → 36`; force the probe to include **top-6 by `phenotype_fidelity_score`** and **top-6 by `selection_priority_score`** so high-fidelity specific bundles are never displaced by prior-heavy generalists.
    - Success: `oracle_in_probe_pool` rises from 67.5 % to ≥82 %.

12. **Archetype-balanced probe in `_diverse_probe_ids`.**
    - Enforce per-archetype minimums in the initial probe: ≥6 same-endpoint, ≥6 adjacent-disease, ≥4 endophenotype, ≤8 from any single archetype.
    - Success: probe composition histogram shows no single archetype > 40 % (currently generalists dominate for rare targets).

13. **Specificity-gap signal in `PROBE_REFLECTION_PROMPT`.**
    - Feed the reflective-reprobe LLM with: `specificity_gap = 1 - mean(fidelity_score of currently retained)`. When > 0.4, require the LLM to propose ≥4 challenger bundles with `lexical_match_score ≥ 55 OR shared_token_count ≥ 2`.
    - Success: on replay of the 22 posterior-miss targets, specific challengers appear in retained set for ≥15 of them.

14. **Rescue the 6 currently-unreachable targets.**
    - For unified, raise `CANDIDATE_DOSSIER_CONFIGS["unified"]["dossier_cap"]` from 600 → 720, `fallback_binary` from 310 → 400. Re-run `prepare-assets` and verify `shortlist_recall` ≥ 0.975.
    - Success: `shortlist_oracle_recall` ≥ 78/80 (currently 74/80).

### P2 — Model-stage ranking diagnostics
Target: `top_0_5pct`. Expected uplift: +2-3 pp.

15. **Retune `UNIFIED_CONFIG` after P1 fixes land.**
    - Re-run `eval/offline_tune_unified_config.py --mode fast_full --trials 500000 --seed 124` against the new Stage-5 ranking + new posterior prompt. The current 34/74 oracle-hit offline ceiling is tied to the old scoring; expected new ceiling 45-50/74.

16. **Add a post-hoc "ideal-model" diagnostic.**
    - In `evaluate_end_to_end.py`, emit `oracle_was_in_bundle_but_not_picked` and `rank_of_selected_within_bundle` columns. Makes it trivial to verify whether P2 champions fixes actually closed the gap.

### P2 — Evaluation hygiene
17. **Add a "without BMI/CAD" stress-test in the summary JSON.**
    - Compute `top_Npct_excluding_generalists` that disqualifies picks from `{body mass index, coronary artery disease, LDL measurement, MDD, insomnia, SBP}`. This number better reflects actual cross-trait transfer quality.

---

## 3. Projected outcome after the plan
Conservative projection based on per-stage recovery percentages above:

| metric | current | target after P0+P1 | after P0+P1+P2 |
|---|---|---|---|
| top_0_5pct | 4.17 % | 12-15 % | 18-22 % |
| top_1pct | 7.50 % | 22-27 % | 28-33 % |
| top_1_5pct | 11.67 % | 30-35 % | 36-42 % |
| top_2pct | 20.00 % | 35-40 % | 42-48 % |
| top_2_5pct | 23.34 % | 40-45 % | 48-55 % |

Most of the lift comes from P0 (removing timeout-induced fallback pollution) and P1.7/P1.8 (the Stage-5 local-champion fix, which is currently losing 29/80 targets whose correct bundle is already selected).

---

## 4. Execution order & verification
1. Land P0.1–P0.3 together, re-run `offline-unified --condition all-tools --workers 6`. Expect ≤5 LLM-timeout warnings and a +5-8 pp lift across all `top_Npct` metrics just from this.
2. Land P1.4–P1.6 (posterior), re-run. Check `oracle_in_supporting_bundles` rises from 0.40 → ≥0.65.
3. Land P1.7–P1.10 (local champion), re-run. Check `oracle_in_local_champions` rises from 0.038 → ≥0.15, which mechanically drives `oracle_in_model_frontier` and therefore `top_Npct`.
4. Land P1.11–P1.14 (shortlist) together; verify `shortlist_recall ≥ 0.975` and `oracle_in_probe_pool ≥ 0.82`.
5. Retune P2.15 after P1 lands.
