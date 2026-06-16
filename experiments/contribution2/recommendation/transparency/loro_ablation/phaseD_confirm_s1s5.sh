#!/usr/bin/env bash
# Phase D: confirm the red-team's missed candidate dilated-cardiomyopathy -> §1/§5.
# Replicate the §1 and §5 LORO (2x each) on already-baked manifests (zero skill edits).
cd /Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent
PY=".venv/bin/python"
RUNS="experiments/contribution2/recommendation/runs"
TOPK="experiments/contribution2/recommendation/scripts/run_experiment_topk_holistic_rerank_batch.py"
LOG="experiments/contribution2/recommendation/transparency/loro_ablation/results/phaseD.log"
SENT="experiments/contribution2/recommendation/transparency/loro_ablation/results/.phaseD_done"
rm -f "$SENT"
S1="$RUNS/with-domain-gpt-5.4-t1__44disease__loro-no-1/experiment_with_domain_batch_manifest.json"
S5="$RUNS/with-domain-gpt-5.4-t1__44disease__loro-no-5/experiment_with_domain_batch_manifest.json"
say(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }
hit1(){ local d; d=$(ls -dt "$RUNS"/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__"$1"-* 2>/dev/null|head -1); [ -z "$d" ]&&{ echo NO_DIR;return;}; $PY -c "import json;s=json.load(open('$d/experiment_topk_holistic_rerank_batch_summary.json'));print('Hit@1='+str(s.get('majority_vote_accuracy')))" 2>/dev/null||echo NO_SUM; }
run(){ say "START $2"; if $PY "$TOPK" --manifest "$1" --run-tag "$2" --model gpt-5.4 --mode run --top-k 5 --objective performance_proxy --stage1-objective support --poll-interval-seconds 30 >>"$LOG" 2>&1; then say "DONE $2 -> $(hit1 "$2")"; else say "FAIL $2"; fi; }
say "===== PHASE D confirm §1/§5 (4 runs) ====="
run "$S1" "noise-1-r1"; run "$S1" "noise-1-r2"; run "$S5" "noise-5-r1"; run "$S5" "noise-5-r2"
say "===== PHASE D COMPLETE ====="
touch "$SENT"
