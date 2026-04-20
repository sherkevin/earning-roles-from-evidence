#!/bin/bash
# Quick newapi quota probe: 1 minimal call to gpt-4.1-mini, check balance indicator
# Safe to run — only costs ~$0.00001 if quota restored; no-op cost if depleted
# Usage: bash workspace/tmp/newapi_quota_probe.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
KEY=$(python3 -c 'import json
d = json.load(open("configs/llm.json"))
# server layout = flat {newapi: {...}}; local layout = {providers: {newapi: {...}}}
nb = d.get("newapi") or d.get("providers", {}).get("newapi")
print(nb["key"])')
echo "key len: ${#KEY}, prefix: ${KEY:0:12}..."
echo ""
echo "=== probe newapi POST /v1/chat/completions gpt-4.1-mini 1 token ==="
RESP=$(curl -s -m 15 -X POST https://xh.v1api.cc/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hi"}],"max_tokens":1}')
echo "response (first 500 char): ${RESP:0:500}"
echo ""
if echo "$RESP" | grep -q '"content":'; then
  echo "STATUS: newapi ACTIVE (quota OK, ready to resume)"
elif echo "$RESP" | grep -q 'insufficient_user_quota'; then
  echo "STATUS: QUOTA STILL DEPLETED — need U-EXEC-007 recharge"
elif echo "$RESP" | grep -q 'Invalid token'; then
  echo "STATUS: TOKEN INVALID (key rotated? check configs/llm.json newapi block)"
else
  echo "STATUS: UNKNOWN — inspect response above"
fi
