#!/bin/bash
# EMERGENCY: newapi quota exhausted, E-017 writing F1=0 garbage predictions
# Stop all E-017 processes + scheduler to preserve what valid data remains
echo "=== BEFORE STOP: alive procs ==="
ps -ef | grep -E 'run_e017|schedule_e017' | grep -v grep
echo
echo "=== Killing E-017 stage1 + scheduler ==="
pkill -SIGTERM -f 'run_e017_fullval_seed' 2>&1 || true
pkill -SIGTERM -f 'schedule_e017_seeds' 2>&1 || true
sleep 3
echo
echo "=== AFTER STOP: any stragglers? ==="
ALIVE=$(ps -ef | grep -E 'run_e017|schedule_e017' | grep -v grep)
if [ -n "$ALIVE" ]; then
  echo "$ALIVE"
  echo "... escalating to SIGKILL ..."
  pkill -SIGKILL -f 'run_e017_fullval_seed' 2>&1 || true
  pkill -SIGKILL -f 'schedule_e017_seeds' 2>&1 || true
  sleep 1
  ps -ef | grep -E 'run_e017|schedule_e017' | grep -v grep
else
  echo "(all gone ✓)"
fi
echo
echo "=== Inspect seed=42 stage2 final metrics (check if quota affected it too) ==="
cat /media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain/metrics.json 2>/dev/null | head -30
echo
echo "=== Inspect seed=42 stage1 final ckpt size ==="
wc -l /media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated/_ckpt_preds.jsonl
echo
echo "=== Inspect F1 distribution in stage1 ckpt: where did F1 collapse? ==="
python3 << 'PYEOF'
import json
from collections import defaultdict

ckpt_path = "/media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated/_ckpt_preds.jsonl"
bins = defaultdict(lambda: {"count": 0, "f1_sum": 0.0, "em_sum": 0.0, "zero_f1_count": 0})
with open(ckpt_path) as fh:
    for i, line in enumerate(fh):
        d = json.loads(line)
        bin_id = i // 500  # 500-sample bins
        b = bins[bin_id]
        b["count"] += 1
        b["f1_sum"] += d.get("answer_f1", 0.0)
        b["em_sum"] += d.get("answer_em", 0.0)
        if d.get("answer_f1", 0.0) == 0.0:
            b["zero_f1_count"] += 1

print(f"{'bin':<10} {'range':<15} {'n':<5} {'mean_f1':<10} {'mean_em':<10} {'zero_f1_frac':<15}")
for bin_id in sorted(bins.keys()):
    b = bins[bin_id]
    r = f"{bin_id*500}-{(bin_id+1)*500-1}"
    mean_f1 = b["f1_sum"] / b["count"]
    mean_em = b["em_sum"] / b["count"]
    zero_frac = b["zero_f1_count"] / b["count"]
    print(f"{bin_id:<10} {r:<15} {b['count']:<5} {mean_f1:<10.4f} {mean_em:<10.4f} {zero_frac:<15.4f}")
PYEOF
echo
echo "=== Do same for stage2 ==="
python3 << 'PYEOF'
import json
from collections import defaultdict

ckpt_path = "/media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain/_ckpt_preds.jsonl"
bins = defaultdict(lambda: {"count": 0, "f1_sum": 0.0, "em_sum": 0.0, "zero_f1_count": 0})
with open(ckpt_path) as fh:
    for i, line in enumerate(fh):
        d = json.loads(line)
        bin_id = i // 500
        b = bins[bin_id]
        b["count"] += 1
        b["f1_sum"] += d.get("answer_f1", 0.0)
        b["em_sum"] += d.get("answer_em", 0.0)
        if d.get("answer_f1", 0.0) == 0.0:
            b["zero_f1_count"] += 1

print(f"{'bin':<10} {'range':<15} {'n':<5} {'mean_f1':<10} {'mean_em':<10} {'zero_f1_frac':<15}")
for bin_id in sorted(bins.keys()):
    b = bins[bin_id]
    r = f"{bin_id*500}-{(bin_id+1)*500-1}"
    mean_f1 = b["f1_sum"] / b["count"]
    mean_em = b["em_sum"] / b["count"]
    zero_frac = b["zero_f1_count"] / b["count"]
    print(f"{bin_id:<10} {r:<15} {b['count']:<5} {mean_f1:<10.4f} {mean_em:<10.4f} {zero_frac:<15.4f}")
PYEOF
