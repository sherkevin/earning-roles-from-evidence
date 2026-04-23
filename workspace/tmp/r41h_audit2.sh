#!/bin/bash
set -u
echo "=== ext-baselines models ==="
find /media/data3/dengkw/idea04/external_baselines -maxdepth 4 \
  \( -name "*.safetensors" -o -name "*.gguf" -o -name "pytorch_model*.bin" \
     -o \( -name "config.json" -path "*model*" \) \) 2>/dev/null \
  | grep -v venv_ | head -30 || echo "(no bundled model weights)"
echo ""

echo "=== venv pytorch inventory ==="
for v in /media/data3/dengkw/idea04/external_baselines/*/venv_*; do
  echo -n "$v: "
  "$v/bin/python" -c "import torch; print(torch.__version__, 'cuda=', torch.cuda.is_available())" 2>/dev/null || echo "(no torch)"
done

echo ""
echo "=== vllm in any venv ==="
for v in /media/data3/dengkw/idea04/external_baselines/*/venv_*; do
  "$v/bin/python" -c "import vllm; print('$v', vllm.__version__)" 2>/dev/null
done || true

echo ""
echo "=== storage ==="
df -h /media/data3 | head -3
echo "home size:"
du -sh ~ 2>/dev/null | head -3

echo ""
echo "=== MA-RAG requirements hints (vllm?) ==="
grep -i "vllm\|torch\|transformers" /media/data3/dengkw/idea04/external_baselines/marag/requirements*.txt 2>/dev/null | head -10 || echo "(no req file)"

echo ""
echo "=== Pip install candidates check ==="
which curl wget python3 python3.10 python3.11

echo "__AUDIT2_DONE__"
