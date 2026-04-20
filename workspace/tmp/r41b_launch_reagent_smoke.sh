#!/bin/bash
# R41b ReAgent smoke launcher
set -u
cd /media/data3/dengkw/idea04

TS="$(date +%Y%m%d_%H%M%S)"
OUT="artifacts/external_baselines/reagent/r41b_smoke_${TS}"
LOG="logs/r41_smoke/reagent_${TS}.log"
mkdir -p "${OUT}" logs/r41_smoke

echo "launching ReAgent smoke; out=${OUT} log=${LOG}"
nohup external_baselines/reagent/venv_reagent/bin/python \
    external_baselines/reagent/run_reagent_hotpotqa.py \
      --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
      --n 5 \
      --out-dir "${OUT}" \
      --model gpt-4.1-mini \
    > "${LOG}" 2>&1 &
PID=$!
echo "PID=${PID}"
echo "${PID}" > "${OUT}/.pid"
echo "${OUT}" > /tmp/r41b_reagent_smoke_dir
echo "${LOG}" > /tmp/r41b_reagent_smoke_log
sleep 3
ps -fp "${PID}" | tail -1
echo "done launching; tail ${LOG}"
