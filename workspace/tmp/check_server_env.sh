#!/bin/bash
echo "=== python ==="
python3 --version
echo "=== pip ==="
python3 -m pip --version
echo "=== packages ==="
python3 << 'PYEOF'
import importlib
mods = ['openai', 'requests', 'yaml', 'tqdm', 'numpy', 'pandas', 'scipy', 'tiktoken']
for m in mods:
    try:
        v = importlib.import_module(m)
        print(f"{m}\t{getattr(v, '__version__', 'no-ver')}")
    except ImportError:
        print(f"{m}\tMISSING")
PYEOF
echo "=== quota check ==="
df -h /media/data3 | tail -1
echo "=== gpu free ==="
nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader
echo "=== existing idea04 dir ==="
ls -la /media/data3/dengkw/idea04/ 2>&1
