#!/bin/bash
cd /media/data3/dengkw/idea04
mkdir -p logs
chmod +x scripts/schedule_e017_seeds.sh
nohup bash scripts/schedule_e017_seeds.sh > logs/e017_scheduler_main.log 2>&1 &
SCHED_PID=$!
echo "SCHEDULER_PID=${SCHED_PID}"
sleep 3
echo "=== scheduler log ==="
cat logs/e017_scheduler_main.log 2>/dev/null || echo "(no log yet)"
echo
echo "=== all e017 procs ==="
ps -ef | grep -E 'run_e017|schedule_e017' | grep -v grep
