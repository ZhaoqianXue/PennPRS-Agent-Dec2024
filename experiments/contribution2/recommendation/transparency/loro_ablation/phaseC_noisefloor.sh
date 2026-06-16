#!/usr/bin/env bash
# Phase C: noise-floor replicates. Re-run the 2-stage topk on already-baked
# manifests (ZERO skill-file edits): 3x full-skill (measures the t=1 flip
# baseline) + 2x -section-cross + 2x -section-2 (tests whether those drops
# reproduce above the baseline). Detached; fail-soft per run.
cd /Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent

PY=".venv/bin/python"
RUNS="experiments/contribution2/recommendation/runs"
TOPK="experiments/contribution2/recommendation/scripts/run_experiment_topk_holistic_rerank_batch.py"
LOG="experiments/contribution2/recommendation/transparency/loro_ablation/results/phaseC.log"
SENT="experiments/contribution2/recommendation/transparency/loro_ablation/results/.phaseC_done"
rm -f "$SENT"

FULL="$RUNS/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-20260610-002512/experiment_topk_holistic_rerank_batch_manifest.json"
CROSS="$RUNS/with-domain-gpt-5.4-t1__44disease__loro-no-cross/experiment_with_domain_batch_manifest.json"
S2="$RUNS/with-domain-gpt-5.4-t1__44disease__loro-no-2/experiment_with_domain_batch_manifest.json"

stamp () { date "+%Y-%m-%d %H:%M:%S"; }
say () { echo "[$(stamp)] $*" >> "$LOG"; }
hit1 () {
  local dir; dir=$(ls -dt "$RUNS"/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__"$1"-* 2>/dev/null | head -1)
  [ -z "$dir" ] && { echo "NO_DIR"; return; }
  $PY -c "import json;s=json.load(open('$dir/experiment_topk_holistic_rerank_batch_summary.json'));print(f\"Hit@1={s.get('majority_vote_accuracy')} cost=\${s.get('cost',{}).get('estimated_total_cost_usd')}\")" 2>/dev/null || echo NO_SUMMARY
}
run_topk () {  # $1=manifest $2=tag
  say "TOPK START tag=$2"
  if $PY "$TOPK" --manifest "$1" --run-tag "$2" --model gpt-5.4 --mode run \
        --top-k 5 --objective performance_proxy --stage1-objective support \
        --poll-interval-seconds 30 >>"$LOG" 2>&1; then
    say "TOPK DONE  tag=$2 -> $(hit1 "$2")"
  else say "TOPK FAIL  tag=$2"; fi
}

say "================= PHASE C noise-floor (7 runs) ================="
run_topk "$FULL"  "noise-full-r1"
run_topk "$FULL"  "noise-full-r2"
run_topk "$FULL"  "noise-full-r3"
run_topk "$CROSS" "noise-cross-r1"
run_topk "$CROSS" "noise-cross-r2"
run_topk "$S2"    "noise-2-r1"
run_topk "$S2"    "noise-2-r2"
say "================= PHASE C COMPLETE ================="
touch "$SENT"
