#!/bin/zsh
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
: "${IDEALAB_API_KEY:?IDEALAB_API_KEY is required}"
url="https://idealab.alibaba-inc.com/api/openai/v1/images/edits"
code=$(curl -sS --max-time 300 \
  -o "$D/api_response.json" \
  -w '%{http_code}' \
  -X POST "$url" \
  -H "Authorization: Bearer $IDEALAB_API_KEY" \
  -F 'model=gpt-image-2.5' \
  -F "prompt=<${D}/prompt.md" \
  -F 'size=auto' \
  -F 'quality=high' \
  -F 'output_format=png' \
  -F "image=@${D}/../v1_collabllm_style_20261004/overview_ai.png;type=image/png")
printf 'http_status=%s\n' "$code" | tee "$D/http_status.txt"
if [[ "$code" != 2* ]]; then
  echo 'response_excerpt:'
  head -c 2000 "$D/api_response.json" || true
  exit 1
fi
python3 - "$D/api_response.json" "$D/overview_gpt_image_2_5.png" <<'PY'
import base64, json, pathlib, sys
src, dst = sys.argv[1:]
d = json.loads(pathlib.Path(src).read_text())
item = d.get('data', [{}])[0]
b64 = item.get('b64_json')
if not b64:
    raise SystemExit('successful response has no data[0].b64_json')
pathlib.Path(dst).write_bytes(base64.b64decode(b64))
print('decoded_bytes=%d' % pathlib.Path(dst).stat().st_size)
PY
shasum -a 256 "$D/overview_gpt_image_2_5.png" | tee "$D/sha256.txt"
file "$D/overview_gpt_image_2_5.png" | tee "$D/file.txt"
