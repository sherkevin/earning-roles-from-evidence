"""Diagnose the newapi + openai 2.32.0 + response_format=json_object interaction.

We want to figure out which layer produces the `'str' object has no attribute
'choices'` error observed when ReAgent's api_call uses json_format=True.
"""
import sys, traceback
from openai import OpenAI

KEY = sys.argv[1] if len(sys.argv) > 1 else ""
BASE = sys.argv[2] if len(sys.argv) > 2 else "https://xh.v1api.cc/v1"
MODEL = "gpt-4.1-mini"

client = OpenAI(api_key=KEY, base_url=BASE)

print("=== Test 1: plain (no response_format) ===")
try:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "say hi"}],
        max_tokens=10,
        temperature=0.0,
    )
    print("  type:", type(r).__name__)
    print("  has .choices:", hasattr(r, "choices"))
    if hasattr(r, "choices"):
        print("  content:", r.choices[0].message.content[:60])
except Exception as e:
    print("  ERR:", type(e).__name__, e)

print("\n=== Test 2: response_format={'type':'json_object'} (the failing path) ===")
try:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Output JSON: {\"step\":\"x\",\"reasoning\":\"y\",\"next_action\":\"z\"}"},
            {"role": "user", "content": "hello"}
        ],
        max_tokens=80,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    print("  type:", type(r).__name__)
    print("  has .choices:", hasattr(r, "choices"))
    if hasattr(r, "choices"):
        content = r.choices[0].message.content
        print("  content type:", type(content).__name__)
        print("  content:", content[:120])
except Exception as e:
    print("  ERR:", type(e).__name__, e)
    traceback.print_exc(limit=3)

print("\n=== Test 3: stream=False explicit ===")
try:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Output JSON: {\"a\":1}"}],
        max_tokens=20,
        temperature=0.0,
        response_format={"type": "json_object"},
        stream=False,
    )
    print("  type:", type(r).__name__)
    print("  has .choices:", hasattr(r, "choices"))
    if hasattr(r, "choices"):
        print("  content:", r.choices[0].message.content[:120])
except Exception as e:
    print("  ERR:", type(e).__name__, e)

print("\n=== Test 4: stream=True (which is what happens if stream kwarg is passed as string?) ===")
try:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Output JSON: {\"a\":1}"}],
        max_tokens=20,
        temperature=0.0,
        response_format={"type": "json_object"},
        stream=True,
    )
    print("  type:", type(r).__name__)
    print("  has .choices:", hasattr(r, "choices"))
    # stream returns iterator, not a single response
    print("  first chunk test...")
    for chunk in r:
        print("    chunk type:", type(chunk).__name__, "has .choices:", hasattr(chunk, "choices"))
        break
except Exception as e:
    print("  ERR:", type(e).__name__, e)
