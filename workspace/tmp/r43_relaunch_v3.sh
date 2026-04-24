#!/bin/bash
# R43 v3 relaunch: kill stale, clear JIT caches, relaunch emergence pipeline
# after pyconfig.h cp fix

set -u

echo "=== [1] kill stale vllm + runner processes ==="
pkill -9 -f 'vllm.entrypoints' 2>/dev/null
pkill -9 -f 'run_e017_fullval_seed' 2>/dev/null
pkill -9 -f 'r42_emergence_pipeline' 2>/dev/null
sleep 3

echo "=== [2] verify nothing alive ==="
pgrep -af 'vllm.entrypoints|run_e017_fullval_seed|r42_emergence_pipeline' 2>/dev/null || echo "  none alive"

echo "=== [3] clear JIT caches (torch._inductor + triton) ==="
rm -rf /home/dengkw/.cache/vllm/torch_compile_cache/ 2>/dev/null
rm -rf /home/dengkw/.triton/ 2>/dev/null
rm -rf /tmp/cuda_utils* 2>/dev/null
echo "  caches cleared"

echo "=== [4] verify pyconfig.h fix is in place ==="
ls -la /media/data3/dengkw/python-headers-310/usr/include/python3.10/Python.h 2>&1 | head -1
ls -la /media/data3/dengkw/python-headers-310/usr/include/python3.10/pyconfig.h 2>&1 | head -1

echo "=== [5] relaunch emergence pipeline v3 ==="
TS=$(date +%Y%m%d_%H%M%S)
cd /media/data3/dengkw/idea04
mkdir -p logs
nohup bash workspace/tmp/r42_emergence_pipeline.sh \
  > logs/r42_pipeline_launch_v3_${TS}.out 2>&1 &
PID=$!
disown || true
echo "  PIPELINE_PID=${PID} launch_log=logs/r42_pipeline_launch_v3_${TS}.out"

sleep 3
echo "=== [6] pipeline alive check ==="
if ps -p ${PID} >/dev/null 2>&1; then
  echo "  pipeline ${PID} alive"
else
  echo "  pipeline ${PID} exited within 3s; tail launch log:"
  tail -20 logs/r42_pipeline_launch_v3_${TS}.out
fi
