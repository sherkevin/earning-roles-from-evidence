#!/bin/bash
cd /media/data3/dengkw/idea04
unset LLM_BACKEND LLM_BASE_URL LLM_API_KEY LLM_MODEL
export PYTHONPATH=/media/data3/dengkw/idea04/workspace:/media/data3/dengkw/idea04/scripts

echo "=== 1. Configs synced ==="
ls configs/round2_gpt41mini_ablation_*.yaml

echo
echo "=== 2. Parse all 4 configs via merge_experiment_config ==="
python3 - << 'PYEOF'
import sys
sys.path.insert(0, '/media/data3/dengkw/idea04/scripts')
import idea04_paths
from pathlib import Path

for name in ['baseline', 'evidence', 'no_tcpb', 'no_gate']:
    p = Path(f'/media/data3/dengkw/idea04/configs/round2_gpt41mini_ablation_{name}.yaml')
    cfg = idea04_paths.merge_experiment_config(p)
    print(f"{name:15s}: model={cfg['main_model']}, methods={cfg.get('methods')}, knobs={cfg.get('method_knobs')}")
PYEOF

echo
echo "=== 3. Verify run_round1_v3.py is on server ==="
ls -la scripts/run_round1_v3.py 2>&1 || echo "NOT PRESENT — need to sync"

echo
echo "=== 4. Verify HotpotQA seed file present ==="
ls -la artifacts/seed/hotpotqa_validation_200.jsonl 2>&1 || echo "NOT PRESENT — need to sync"
ls -la artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl 2>&1
echo
wc -l artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl 2>&1

echo
echo "=== 5. Check existing artifacts/round2_gpt41mini_ablations dir ==="
ls -la artifacts/round2_gpt41mini_ablations/ 2>/dev/null || echo "(empty / not yet created — engineer will create on first batch run)"

echo
echo "=== 6. MAD math/ structure (for E-015 step 4 + E-016 SWAP-4 reference) ==="
ls external_baselines/mad/math/
echo
echo "--- MAD math/eval_math_gpt.py first 60 lines ---"
head -60 external_baselines/mad/math/eval_math_gpt.py 2>/dev/null
