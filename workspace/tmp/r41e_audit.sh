#!/bin/bash
set -u
echo "=== date ==="
date
echo ""
echo "=== DAEMONS ==="
ps -ef | grep -E 'schedule_e017|r41b_n50_smokes|r41d_musique|332171' | grep -v grep | head -10
echo ""
echo "=== RUNNING BATCHES ==="
ps -ef | grep -E 'run_e017|gen_hotpotqa|run_marag|run_reagent|run_mad' | grep -v grep | head -15
echo ""
echo "=== SEED42 METRICS (paired) ==="
for m in /media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_*_seed42/*/metrics.json; do
  [ -f "$m" ] && echo "$m:" && cat "$m" | head -3 && echo "---"
done
echo ""
echo "=== SEED43 CKPT PROGRESS ==="
for d in /media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/*/; do
  ckpt=$(wc -l < "$d/_ckpt_preds.jsonl" 2>/dev/null || echo 0)
  done_flag=$([ -f "$d/metrics.json" ] && echo DONE || echo running)
  echo "  $d: ckpt=${ckpt}/7405 ${done_flag}"
done
echo ""
echo "=== SEED44 DIR ==="
ls -d /media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_fullval/run_*_seed44* 2>/dev/null | head -5 || echo "(not yet launched)"
echo ""
echo "=== N50 SMOKES ==="
for d in /media/data3/dengkw/idea04/artifacts/external_baselines/*/r41b_n50_*/; do
  status=$([ -f "$d/metrics.json" ] && echo DONE || echo running)
  preds=$(wc -l < "$d/predictions.jsonl" 2>/dev/null || echo 0)
  echo "  $d: status=${status} preds=${preds}"
done
echo ""
echo "=== MUSIQUE MATRIX DIR ==="
ls -d /media/data3/dengkw/idea04/artifacts/matrix/musique_n50_*/ 2>/dev/null | head -5 || echo "(not yet launched; watcher PID 342216 still polling)"
echo ""
echo "=== WATCHER TAIL ==="
for l in /media/data3/dengkw/idea04/artifacts/monitor/r41d_musique_matrix_watch_*.log; do
  [ -f "$l" ] && echo "--- $l (last 3 lines) ---" && tail -3 "$l"
done
echo ""
echo "=== QUOTA ==="
bash /media/data3/dengkw/idea04/workspace/tmp/newapi_quota_probe.sh 2>&1 | tail -3
echo ""
echo "__AUDIT_DONE__"
