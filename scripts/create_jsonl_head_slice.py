"""Create a deterministic head-N JSONL slice with lightweight validation.

This is intentionally boring: preserve input order, copy the first N non-empty
JSON lines, and fail if fewer than N rows are available. It is used for E-030
matrix seed files where "deterministic slice" must be reproducible by command.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="source JSONL path")
    parser.add_argument("--out", required=True, help="output JSONL path")
    parser.add_argument("--n", type=int, required=True, help="number of rows")
    args = parser.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    rows: list[str] = []
    seen_task_ids: set[str] = set()

    with src.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            text = line.strip()
            if not text:
                continue
            obj = json.loads(text)
            task_id = obj.get("task_id")
            if task_id:
                if task_id in seen_task_ids:
                    raise ValueError(f"duplicate task_id {task_id!r} at line {line_no}")
                seen_task_ids.add(task_id)
            rows.append(json.dumps(obj, ensure_ascii=False))
            if len(rows) >= args.n:
                break

    if len(rows) != args.n:
        raise ValueError(f"{src} has only {len(rows)} non-empty JSONL rows; need {args.n}")

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(row + "\n")

    print(f"[create_jsonl_head_slice] wrote {len(rows)} rows: {out}")
    print(f"[create_jsonl_head_slice] source: {src}")
    print(f"[create_jsonl_head_slice] unique task_ids: {len(seen_task_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
