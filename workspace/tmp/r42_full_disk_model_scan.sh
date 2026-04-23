#!/bin/bash
# R42 full-disk model scan — deeper than R41h's probe (which missed other
# /media/data{1,2,4} partitions + system-level locations).
# Looks for existing weights the R41h audit might have missed.
set -u

echo "=== scan 1: all .safetensors files ≥ 100 MB anywhere we can read ==="
for root in /media/data1 /media/data2 /media/data3 /media/data4 /home /opt /usr/local /srv; do
  if [ -d "$root" ]; then
    find "$root" -type f \( -name '*.safetensors' -o -name '*.bin' -o -name '*.gguf' -o -name '*.pt' \) -size +100M 2>/dev/null | head -20
  fi
done

echo ""
echo "=== scan 2: HF-style repo dirs with config.json ==="
for root in /media/data1 /media/data2 /media/data3 /media/data4 /home /opt; do
  if [ -d "$root" ]; then
    find "$root" -type f -name 'config.json' 2>/dev/null | xargs grep -l -E '("model_type"|"architectures")' 2>/dev/null | head -30
  fi
done

echo ""
echo "=== scan 3: Ollama / LM-Studio / GPT4All / vLLM / SGLang blob dirs ==="
for candidate in \
    /home/dengkw/.ollama \
    /usr/share/ollama \
    /var/lib/ollama \
    /root/.ollama \
    /home/dengkw/.cache/lm-studio \
    /home/dengkw/.cache/gpt4all \
    /home/dengkw/.cache/vllm \
    /home/dengkw/.cache/sglang \
    /opt/models \
    /opt/ollama \
    /srv/models \
    /media/data1/models \
    /media/data2/models \
    /media/data4/models \
    /media/data1/huggingface \
    /media/data2/huggingface \
    /media/data4/huggingface \
    /media/data1/dengkw \
    /media/data2/dengkw \
    /media/data4/dengkw; do
  if [ -d "$candidate" ]; then
    sz=$(du -sh "$candidate" 2>/dev/null | awk '{print $1}')
    echo "FOUND: ${candidate}  (${sz})"
    ls "$candidate" 2>/dev/null | head -10 | sed 's/^/    /'
  fi
done

echo ""
echo "=== scan 4: sibling-project model candidates (read-only view only) ==="
# sibling projects on /media/data3
for sib in /media/data3/*; do
  if [ -d "$sib" ] && [ "$(basename $sib)" != "dengkw" ]; then
    models=$(find "$sib" -type d \( -name 'models' -o -name 'hf_models' -o -name 'weights' -o -name 'checkpoints' -o -name 'ckpts' \) 2>/dev/null | head -5)
    if [ -n "$models" ]; then
      echo "SIBLING: $sib has model-like dirs:"
      echo "$models" | sed 's/^/    /'
      # Sample a few subdirs
      for m in $(echo "$models" | head -3); do
        ls "$m" 2>/dev/null | head -5 | sed 's/^/      /'
      done
    fi
  fi
done

echo ""
echo "=== scan 5: running vllm / ollama services (port probe) ==="
ss -tln 2>/dev/null | grep -E ':(8000|8001|8002|8003|8004|11434|5000|7860)' | head -10 || echo "(no common model-serving ports open)"

echo ""
echo "=== scan 6: environment hints ==="
env | grep -iE 'model|hf|transformer|vllm|ollama' | head -10

echo ""
echo "=== scan 7: which agentic SLMs are on pypi / HF mirror (optional, no DL) ==="
which huggingface-cli 2>/dev/null || echo "(no global huggingface-cli)"
ls /usr/local/cuda 2>/dev/null | head -3 || echo "(no /usr/local/cuda symlink)"
nvidia-smi --version 2>/dev/null | head -3

echo ""
echo "=== R42 full-disk model scan DONE ==="
