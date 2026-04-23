#!/bin/bash
# R41h server audit — search all reasonable locations for local LLM weights
set -u
echo "=== date + disk ==="
date
df -h /media/data3 /media/data1 /media/data2 /home 2>/dev/null | head -15
echo ""

echo "=== HuggingFace cache on dengkw user ==="
ls -la ~/.cache/huggingface/hub/ 2>/dev/null | head -30
du -sh ~/.cache/huggingface/ 2>/dev/null | head -5
echo ""

echo "=== Global HuggingFace caches ==="
for d in /media/*/hf_cache /media/*/huggingface_cache /media/*/cache /root/.cache/huggingface; do
  [ -d "$d" ] && echo "  $d:" && ls -la "$d" 2>/dev/null | head -10
done
echo ""

echo "=== GGUF / safetensors / bin files across /media ==="
find /media/data1 /media/data2 /media/data3 /media/data4 2>/dev/null \
    -maxdepth 6 \( -name "*.gguf" -o -name "*.safetensors" -o -name "pytorch_model.bin" \) \
    2>/dev/null | head -40
echo ""

echo "=== Ollama models ==="
ls -la ~/.ollama/models/ 2>/dev/null | head -10
[ -d /usr/share/ollama ] && ls /usr/share/ollama 2>/dev/null | head -10
which ollama 2>/dev/null
echo ""

echo "=== vllm / llama.cpp installed? ==="
which vllm python3 2>/dev/null
python3 -c "import vllm; print('vllm', vllm.__version__)" 2>/dev/null || echo "(no vllm in system python)"
which llama-cli llama-server main 2>/dev/null
ls ~/llama.cpp /opt/llama.cpp 2>/dev/null | head -3
echo ""

echo "=== GPU VRAM + load ==="
nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu --format=csv 2>/dev/null
echo ""

echo "=== FNC/recsys siblings' models (other people on this server) ==="
ls -la /media/data3/FNC/ 2>/dev/null | head -15
ls -la /media/data3/recsys/ 2>/dev/null | head -15
find /media/data3/{FNC,recsys} -maxdepth 4 \( -name "*.safetensors" -o -name "*.gguf" \) 2>/dev/null | head -10
echo ""

echo "=== Possible model dirs by name ==="
find /media/data1 /media/data2 /media/data3 /media/data4 2>/dev/null -maxdepth 4 -type d \
    \( -iname "*llama*" -o -iname "*qwen*" -o -iname "*mistral*" -o -iname "*gemma*" \
       -o -iname "*phi*" -o -iname "*deepseek*" -o -iname "*glm*" -o -iname "*yi*" \
       -o -iname "*internlm*" \) 2>/dev/null | head -30

echo ""
echo "__AUDIT_DONE__"
