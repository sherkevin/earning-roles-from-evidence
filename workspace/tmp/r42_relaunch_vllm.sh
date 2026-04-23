#!/bin/bash
set -u
cd /media/data3/dengkw/idea04
TS="$(date +%Y%m%d_%H%M%S)"
LOG="logs/r42_vllm_env_setup_v3_${TS}.log"
nohup bash workspace/tmp/r42_vllm_env_setup.sh > "${LOG}" 2>&1 &
PID=$!
disown
sleep 2
echo "launched PID=${PID} log=${LOG}"
ps -ef | grep r42_vllm_env | grep -v grep | head -3 || echo "(proc not found, maybe already exited)"
