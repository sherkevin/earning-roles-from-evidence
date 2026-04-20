#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== ChatEval llm_eval.py first 100 lines ==="
head -100 external_baselines/chateval/llm_eval.py 2>/dev/null
echo
echo "=== ChatEval agentverse/ structure ==="
find external_baselines/chateval/agentverse/ -type f -name '*.py' 2>/dev/null | head -20
echo
echo "=== ChatEval install_to_note.md (existing notes from prior install) ==="
cat external_baselines/chateval/install_to_note.md 2>/dev/null | head -60
echo
echo "=== ChatEval main.py / FastChat structure ==="
ls external_baselines/chateval/FastChat/ 2>/dev/null | head -10
echo
echo "=== Search for 'MetaReviewer' in ChatEval (the SWAP-3 target per E-012) ==="
grep -rn "MetaReviewer\|meta_reviewer\|aggregate" external_baselines/chateval --include='*.py' 2>/dev/null | head -10
echo
echo "=== E-017 progress ==="
tail -3 logs/e017_scheduler_main.log
echo
echo "=== Current GPU state ==="
nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader 2>&1 | head -10
echo
echo "=== Server-side openai_compat_shim.py ==="
ls -la external_baselines/mad/openai_compat_shim.py 2>&1
