#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== Task progress ==="
for L in logs/e018_marag_clone_*.log logs/e018_reagent_clone_*.log logs/e015_mad_install_*.log logs/e010_chateval_install_*.log; do
  if [ -f "$L" ]; then
    echo "--- $L ---"
    tail -10 "$L" 2>/dev/null
    echo
  fi
done
echo "=== E-017 stage1 progress (last 3 heartbeats) ==="
tail -3 logs/e017_scheduler_main.log
echo
echo "=== external_baselines dir ==="
ls -la external_baselines/
echo
echo "=== alive parallel tasks ==="
ps -ef | grep -E 'git clone|pip install' | grep -v grep
