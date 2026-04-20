#!/bin/bash
set -u
cd /media/data3/dengkw/idea04
OUT=artifacts/external_baselines/reagent/r41c_retry_$(date +%H%M%S)
mkdir -p "${OUT}"
echo "out: ${OUT}"
external_baselines/reagent/venv_reagent/bin/python external_baselines/reagent/run_reagent_hotpotqa.py \
  --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
  --n 2 \
  --out-dir "${OUT}" \
  --model gpt-4.1-mini 2>&1 | tail -40
echo "=== METRICS (if landed) ==="
cat "${OUT}/metrics.json" 2>/dev/null || echo "(no metrics)"
