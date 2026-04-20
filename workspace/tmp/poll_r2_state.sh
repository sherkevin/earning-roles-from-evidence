#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== MA-RAG install log (tail) ==="
for L in logs/e018_marag_install_202604192333*.log; do
  if [ -f "$L" ]; then tail -20 "$L"; fi
done
echo
echo "=== ReAgent install log (tail) ==="
for L in logs/e018_reagent_install_202604192333*.log; do
  if [ -f "$L" ]; then tail -20 "$L"; fi
done
echo
echo "=== E-017 scheduler tail ==="
tail -3 logs/e017_scheduler_main.log
echo
echo "=== alive procs ==="
ps -ef | grep -E 'pip install|virtualenv|run_e017|schedule_e017' | grep -v grep | grep -v _recbole
echo
echo "=== disk ==="
df -h /media/data3 | tail -1
