#!/bin/bash
# R40 orchestrator: resume seed=42 from truncated ckpt (path a) + start fresh scheduler chain 43+44
# Invoked after U-EXEC-007 recharge + U-Rollback-001 ✅ (a).
set -uo pipefail
cd /media/data3/dengkw/idea04

echo "=== step 0: pre-flight quota probe ==="
bash workspace/tmp/newapi_quota_probe.sh | tail -3
echo

# Guard: if probe says QUOTA STILL DEPLETED, abort
if bash workspace/tmp/newapi_quota_probe.sh 2>&1 | grep -q "QUOTA STILL DEPLETED"; then
  echo "ABORT: quota still depleted. Retry after recharge."
  exit 1
fi

echo "=== step 1: kill any stale scheduler or worker procs ==="
pkill -f schedule_e017_seeds.sh 2>/dev/null || true
pkill -f run_e017_fullval_seed 2>/dev/null || true
sleep 2
ps -ef | grep -E "run_e017|schedule_e017" | grep -v grep || echo "  (no stale procs remain)"
echo

echo "=== step 2: launch seed=42 stage1+stage2 RESUME ==="
bash workspace/tmp/launch_e017_seed42_resume.sh
sleep 8
echo

echo "=== step 3: verify resume workers alive ==="
ps -ef | grep run_e017_fullval_seed | grep -v grep
echo

echo "=== step 4: start fresh scheduler (monitors seed=42 → chain 43+44 → paired_bootstrap) ==="
SCHED_LOG="logs/scheduler_r40_$(date +%Y%m%d_%H%M%S).log"
nohup bash workspace/tmp/schedule_e017_seeds.sh > "${SCHED_LOG}" 2>&1 &
SCHED_PID=$!
disown
echo "scheduler PID=${SCHED_PID}"
echo "scheduler log=${SCHED_LOG}"
sleep 4
echo

echo "=== step 5: scheduler log tail (expect 'Step 1: waiting for seed=42') ==="
tail -10 "${SCHED_LOG}" 2>/dev/null || echo "(log not ready yet)"
echo
# Also update main log symlink for poll convenience
LATEST_SCHED=$(ls -t logs/e017_scheduler_*.log 2>/dev/null | head -1)
if [ -n "${LATEST_SCHED}" ]; then
  echo "latest e017_scheduler_*.log=${LATEST_SCHED}"
  tail -5 "${LATEST_SCHED}"
fi

echo "=== R40 orchestrator DONE ==="
