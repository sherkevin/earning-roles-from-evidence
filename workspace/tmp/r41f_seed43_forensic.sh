#!/bin/bash
set -u
cd /media/data3/dengkw/idea04
echo "=== SEED43 META CHECK ==="
ls artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/*/_ckpt_meta.json 2>/dev/null || echo "(no _ckpt_meta.json — workers did not halt gracefully)"

echo ""
echo "=== SEED43 STAGE2 TAIL F1 ==="
tail -10 artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/edo_stage2_chain/_ckpt_preds.jsonl 2>/dev/null | \
  python3 -c 'import sys,json
for l in sys.stdin:
    l=l.strip()
    if not l: continue
    r=json.loads(l)
    print(f"  {r[\"task_id\"]} f1={r[\"answer_f1\"]:.3f} em={r[\"answer_em\"]:.1f}")'

echo ""
echo "=== SEED43 STAGE1 TAIL F1 ==="
tail -10 artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/fixed_peer_calibrated/_ckpt_preds.jsonl 2>/dev/null | \
  python3 -c 'import sys,json
for l in sys.stdin:
    l=l.strip()
    if not l: continue
    r=json.loads(l)
    print(f"  {r[\"task_id\"]} f1={r[\"answer_f1\"]:.3f} em={r[\"answer_em\"]:.1f}")'

echo ""
echo "=== SCHEDULER LOG TAIL ==="
tail -15 logs/e017_scheduler_20260420_210742.log 2>/dev/null

echo ""
echo "=== SEED43 STAGE2 LOG TAIL ==="
tail -15 logs/e017_seed43_stage2.log 2>/dev/null

echo ""
echo "=== SEED43 STAGE1 LOG TAIL ==="
tail -15 logs/e017_seed43_stage1.log 2>/dev/null

echo "__DONE__"
