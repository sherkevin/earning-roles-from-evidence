"""Direct call ReAgent's api_call() to reproduce the exact bug."""
import sys, os, traceback
from pathlib import Path

_REAGENT = Path("/media/data3/dengkw/idea04/external_baselines/reagent")
os.chdir(_REAGENT)
sys.path.insert(0, str(_REAGENT))

# ensure env.yaml is writable with real key
import json
cfg = json.load(open("/media/data3/dengkw/idea04/configs/llm.json"))
nb = cfg.get("newapi") or cfg.get("providers", {}).get("newapi")
KEY = nb["key"]
URL = str(nb.get("url") or "https://xh.v1api.cc/v1").rstrip("/")
(_REAGENT / "config").mkdir(exist_ok=True)
(_REAGENT / "config/env.yaml").write_text(f"""services:
  openai:
    api_key: {KEY}
    base_url: {URL}
  qwen:
    api_key: stub
    base_url: https://stub.invalid
  deepseek:
    api_key: stub
    base_url: https://stub.invalid
  claude:
    api_key: stub
    base_url: https://stub.invalid
""")

print("=== Test A: direct api_call with json_format=True ===")
from backend.api import api_call
try:
    r = api_call(
        messages=[
            {"role": "system", "content": "Return JSON: {step, reasoning, next_action}"},
            {"role": "user", "content": "Q: 2+2=? JSON please."},
        ],
        model="gpt-4.1-mini",
        temperature=0.0,
        max_tokens=50,
        max_retries=2,
        json_format=True,
    )
    print("  type:", type(r).__name__, "  value:", r)
except Exception as e:
    print("  api_call raised:", type(e).__name__, e)
    traceback.print_exc(limit=5)
print()

print("=== Test B: direct openai call, same params ===")
from openai import OpenAI
client = OpenAI(api_key=KEY, base_url=URL)
try:
    r = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Return JSON: {step, reasoning, next_action}"},
            {"role": "user", "content": "Q: 2+2=? JSON please."},
        ],
        max_tokens=50,
        temperature=0.0,
        response_format={"type": "json_object"},
        stream=False,
    )
    print("  type:", type(r).__name__)
    print("  .choices[0].message.content:", r.choices[0].message.content[:200])
except Exception as e:
    print("  ERR:", type(e).__name__, e)
