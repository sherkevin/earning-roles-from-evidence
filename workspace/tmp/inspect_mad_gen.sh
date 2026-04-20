#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== MAD math/gen_math.py (MAD's debate driver) ==="
cat external_baselines/mad/math/gen_math.py 2>/dev/null
echo
echo "=== MAD biography/ (debate task) ==="
ls external_baselines/mad/biography/
echo
head -80 external_baselines/mad/biography/gen_conversation.py 2>/dev/null
echo
echo "=== MAD readme ==="
head -80 external_baselines/mad/README.md 2>/dev/null
echo
echo "=== Current GPU state (others may be using) ==="
nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader
echo
echo "=== E-017 progress ==="
tail -3 logs/e017_scheduler_main.log
