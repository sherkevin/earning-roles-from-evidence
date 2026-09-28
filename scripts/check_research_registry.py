#!/usr/bin/env python3
"""Validate the six-category research registry and its single ACTIVE invariant."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/research/canonical/active_versions.json"
EXPECTED = {
    "storyline", "method", "benchmark-baseline",
    "evaluation/storyline", "evaluation/method", "evaluation/benchmark-baseline",
}

def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    categories = registry.get("categories", {})
    if set(categories) != EXPECTED:
        raise SystemExit(f"category set mismatch: {sorted(categories)}")
    paths = []
    for category, rel in categories.items():
        path = (REGISTRY.parent / rel).resolve()
        if not path.is_file():
            raise SystemExit(f"missing active document for {category}: {path}")
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^- \*\*状态\*\*：`ACTIVE`$", text, re.MULTILINE):
            raise SystemExit(f"document is not ACTIVE: {path}")
        paths.append(path)
    if len(set(paths)) != len(paths):
        raise SystemExit("two categories point to the same active document")
    print(json.dumps({"categories": len(categories), "unique_active_documents": len(paths), "ok": True}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
