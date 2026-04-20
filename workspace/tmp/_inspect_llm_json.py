#!/usr/bin/env python3
"""Quick inspect configs/llm.json structure to locate newapi key (local vs server layout may differ)."""
import json
import sys

cfg_path = sys.argv[1] if len(sys.argv) > 1 else "configs/llm.json"
cfg = json.load(open(cfg_path))
print(f"top-level keys: {list(cfg.keys())[:15]}")

def find_newapi(d, path=""):
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{path}.{k}" if path else k
            if isinstance(k, str) and "newapi" in k.lower():
                print(f"  found block at {p}: keys={list(v.keys()) if isinstance(v, dict) else type(v).__name__}")
            if isinstance(v, (dict, list)):
                find_newapi(v, p)
    elif isinstance(d, list):
        for i, item in enumerate(d):
            if isinstance(item, dict):
                nm = item.get("name", item.get("id", f"item_{i}"))
                if "newapi" in str(nm).lower() or "xh.v1api" in str(item).lower():
                    print(f"  found list block at {path}[{i}]: name/id={nm}")
                    if "key" in item: print(f"    key prefix: {item['key'][:15]}...")
                    if "base_url" in item: print(f"    base_url: {item['base_url']}")

find_newapi(cfg)
