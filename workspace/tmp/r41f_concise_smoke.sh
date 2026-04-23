#!/bin/bash
set -u
cd /media/data3/dengkw/idea04
OUT=artifacts/external_baselines/reagent/r41f_concise_n5_$(date +%H%M%S)
mkdir -p "${OUT}"
echo "out: ${OUT}"
PYTHONUNBUFFERED=1 timeout 180 external_baselines/reagent/venv_reagent/bin/python -u \
  external_baselines/reagent/run_reagent_hotpotqa.py \
    --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
    --n 5 \
    --out-dir "${OUT}" \
    --model gpt-4.1-mini \
    --no-mas --concise 2>&1 | tail -40
echo "=== METRICS ==="
cat "${OUT}/metrics.json" 2>/dev/null
echo ""
echo "=== PREDICTIONS ==="
cat "${OUT}/predictions.jsonl" 2>/dev/null
