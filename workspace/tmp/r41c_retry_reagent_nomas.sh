#!/bin/bash
# Run ReAgent smoke with mas=False (no voting) + unbuffered output
set -u
cd /media/data3/dengkw/idea04
OUT=artifacts/external_baselines/reagent/r41c_nomas_$(date +%H%M%S)
mkdir -p "${OUT}"
echo "out: ${OUT}  (mas disabled, no voting; unbuffered)"
PYTHONUNBUFFERED=1 timeout 300 external_baselines/reagent/venv_reagent/bin/python -u \
  external_baselines/reagent/run_reagent_hotpotqa.py \
    --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
    --n 2 \
    --out-dir "${OUT}" \
    --model gpt-4.1-mini \
    --no-mas 2>&1 | tail -80
echo "=== METRICS (if landed) ==="
cat "${OUT}/metrics.json" 2>/dev/null || echo "(no metrics)"
echo "=== PREDICTIONS (if any) ==="
cat "${OUT}/predictions.jsonl" 2>/dev/null | head -3
