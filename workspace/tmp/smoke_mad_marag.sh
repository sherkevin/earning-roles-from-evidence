#!/bin/bash
# Tiny smoke test for MAD + MA-RAG adapters — 2 samples each, totally sequential
# to minimise newapi load impact on concurrent E-017.
set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/external_baselines/mad artifacts/external_baselines/marag
TS=$(date +%Y%m%d_%H%M%S)

SAMPLES_JSONL="artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl"

echo "=== Fire MAD smoke (2 samples × 3 agents × 2 rounds = 12 LLM calls, ~\$0.05, ~1 min wall) ==="
LOG_MAD="logs/e015_mad_smoke_${TS}.log"
OUT_MAD="artifacts/external_baselines/mad/smoke_${TS}"
nohup bash -c "
cd /media/data3/dengkw/idea04 &&
source external_baselines/mad/venv_mad/bin/activate &&
python external_baselines/mad/hotpotqa/gen_hotpotqa.py \
    --samples-jsonl ${SAMPLES_JSONL} \
    --n 2 \
    --agents 3 --rounds 2 \
    --out-dir ${OUT_MAD} 2>&1
" > "${LOG_MAD}" 2>&1 &
MAD_PID=$!
echo "MAD smoke PID=${MAD_PID}  LOG=${LOG_MAD}  OUT=${OUT_MAD}"
sleep 1

echo
echo "=== Fire MA-RAG smoke (2 samples × 2 LLM calls = 4 calls, ~\$0.02, ~20 sec wall) ==="
LOG_MARAG="logs/e018_marag_smoke_${TS}.log"
OUT_MARAG="artifacts/external_baselines/marag/smoke_${TS}"
nohup bash -c "
cd /media/data3/dengkw/idea04 &&
source external_baselines/marag/venv_marag/bin/activate &&
python external_baselines/marag/run_marag_hotpotqa.py \
    --samples-jsonl ${SAMPLES_JSONL} \
    --n 2 \
    --out-dir ${OUT_MARAG} 2>&1
" > "${LOG_MARAG}" 2>&1 &
MARAG_PID=$!
echo "MA-RAG smoke PID=${MARAG_PID}  LOG=${LOG_MARAG}  OUT=${OUT_MARAG}"

echo
echo "=== launched smoke tests at ${TS} ==="
sleep 3
ps -ef | grep -E 'gen_hotpotqa|run_marag|python.*hotpotqa|python.*marag' | grep -v grep
