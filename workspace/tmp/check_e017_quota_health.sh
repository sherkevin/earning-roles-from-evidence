#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== E-017 stage1 most recent 5 predictions (check F1 quality) ==="
tail -5 artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated/_ckpt_preds.jsonl | python3 -c "
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    print(f'  task_id={d.get(\"task_id\")}  em={d.get(\"answer_em\")}  f1={d.get(\"answer_f1\"):.3f}  accepted_node={d.get(\"accepted_node\")}')
"
echo
echo "=== E-017 stage1 recent raw_model_outputs (last 5 lines to check for API errors) ==="
tail -5 artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated/raw_model_outputs.jsonl | python3 -c "
import json, sys
for i, line in enumerate(sys.stdin):
    try:
        d = json.loads(line)
        role = d.get('role', '?')
        content = d.get('content', '')
        err = d.get('error', None)
        print(f'  [{i}] role={role}  err={err}  content_head={content[:120]!r}')
    except Exception as e:
        print(f'  [{i}] JSON parse error: {e}')
"
echo
echo "=== E-017 stage1 log tail (engineer background run log) ==="
ls -la logs/e017_seed42_stage1_resume_*.log 2>/dev/null
for L in logs/e017_seed42_stage1_resume_*.log; do
  if [ -f "$L" ]; then
    echo "--- $L (lines=$(wc -l < "$L")) ---"
    tail -20 "$L"
  fi
done
echo
echo "=== newapi status check via curl (direct probe) ==="
KEY=$(python3 -c "import json; print(json.load(open('configs/llm.json'))['newapi']['key'])")
curl -s -o /tmp/newapi_probe.json -w 'HTTP_CODE=%{http_code}\n' \
  -X POST https://xh.v1api.cc/v1/chat/completions \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5,"temperature":0}'
cat /tmp/newapi_probe.json
echo
echo
echo "=== E-017 scheduler heartbeat (latest 5) ==="
tail -5 logs/e017_scheduler_main.log
