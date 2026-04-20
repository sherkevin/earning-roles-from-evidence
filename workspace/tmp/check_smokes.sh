#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== MAD smoke log ==="
for L in logs/e015_mad_smoke_*.log; do
  if [ -f "$L" ]; then
    echo "--- $L (lines=$(wc -l < "$L")) ---"
    tail -30 "$L"
    echo
  fi
done
echo "=== MA-RAG smoke log ==="
for L in logs/e018_marag_smoke_*.log; do
  if [ -f "$L" ]; then
    echo "--- $L (lines=$(wc -l < "$L")) ---"
    tail -30 "$L"
    echo
  fi
done
echo "=== output artifacts ==="
find artifacts/external_baselines/ -type f -newer /tmp/smoke_mad_marag.sh 2>/dev/null | head -20
echo
echo "=== alive smoke procs ==="
ps -ef | grep -E 'gen_hotpotqa|run_marag' | grep -v grep
echo
echo "=== E-017 progress ==="
tail -3 logs/e017_scheduler_main.log
