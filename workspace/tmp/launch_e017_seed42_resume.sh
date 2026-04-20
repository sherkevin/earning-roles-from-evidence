#!/bin/bash
# Launch E-017 seed=42 stage2 + stage1 resume on server.
# Resumes from existing _ckpt_preds.jsonl (1946 + 1445 done locally, migrated R26).
set -e
cd /media/data3/dengkw/idea04
mkdir -p logs

export PYTHONPATH=/media/data3/dengkw/idea04/workspace:/media/data3/dengkw/idea04/scripts
unset LLM_BACKEND LLM_BASE_URL LLM_API_KEY LLM_MODEL

TS=$(date +%Y%m%d_%H%M%S)

# stage2 resume
RUN_DIR_S2="artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain"
LOG_S2="logs/e017_seed42_stage2_resume_${TS}.log"
nohup python3 -u scripts/run_e017_fullval_seed.py \
    --seed 42 --method edo_stage2_chain \
    --workers 8 --run-dir "${RUN_DIR_S2}" \
    > "${LOG_S2}" 2>&1 &
echo "stage2 PID=$!"
echo "stage2 LOG=${LOG_S2}"
sleep 1

# stage1 paired resume
RUN_DIR_S1="artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated"
LOG_S1="logs/e017_seed42_stage1_resume_${TS}.log"
nohup python3 -u scripts/run_e017_fullval_seed.py \
    --seed 42 --method fixed_peer_calibrated \
    --workers 8 --run-dir "${RUN_DIR_S1}" \
    > "${LOG_S1}" 2>&1 &
echo "stage1 PID=$!"
echo "stage1 LOG=${LOG_S1}"
sleep 1

echo
echo "=== process snapshot ==="
ps -ef | grep run_e017_fullval_seed | grep -v grep
