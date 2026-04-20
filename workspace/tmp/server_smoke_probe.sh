#!/bin/bash
set -e
cd /media/data3/dengkw/idea04
export PYTHONPATH=/media/data3/dengkw/idea04/workspace:/media/data3/dengkw/idea04/scripts
echo "=== File checks ==="
ls -la artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl
wc -l artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl
echo
echo "=== Newapi smoke probe via actual llm_client + ModelDriftError guard ==="
python3 - << 'PYEOF'
import os
os.environ.pop("LLM_BACKEND", None)
os.environ.pop("LLM_BASE_URL", None)
os.environ.pop("LLM_API_KEY", None)
os.environ.pop("LLM_MODEL", None)

import sys
sys.path.insert(0, '/media/data3/dengkw/idea04/workspace')

from idea04_core.llm_client import call_llm, configure_runtime, _runtime
import time

# Configure with the runner's standard backbone, fail-fast on drift
configure_runtime("gpt-4.1-mini", enforce_model=True)
print(f"[config] backend={_runtime['backend']} model={_runtime['model']}")
print(f"[config] chat_url={_runtime['chat_url']}")

t0 = time.time()
res = call_llm(
    messages=[{"role": "user", "content": "Reply with only the word OK."}],
    temperature=0.0,
    max_tokens=10,
)
dt = time.time() - t0

print(f"\n[smoke] dt = {dt:.2f}s")
print(f"[smoke] resp model = {res.get('model')}")
print(f"[smoke] resp content = {res['choices'][0]['message']['content']!r}")
print(f"[smoke] usage = {res.get('usage')}")
print(f"[smoke] _sent_model = {res.get('_sent_model')}  _sent_provider = {res.get('_sent_provider')}")

assert res['model'].startswith('gpt-4.1-mini'), f"MODEL DRIFT: {res['model']}"
print("\n__SMOKE_OK__")
PYEOF
