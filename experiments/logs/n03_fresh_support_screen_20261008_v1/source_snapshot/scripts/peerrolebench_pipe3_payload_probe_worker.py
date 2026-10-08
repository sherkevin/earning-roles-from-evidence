"""Probe the exact serialized PIPE3 payload and its operator-file boundary."""
from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    source_root = Path(sys.argv[1]).resolve()
    for line in sys.stdin:
        request = json.loads(line)
        try:
            payload = request["payload"]
            role = payload["role"]
            source_files = payload["source_files"]
            if not isinstance(source_files, dict) or not source_files:
                raise ValueError("payload source_files must be a nonempty object")
            for name, text in source_files.items():
                if not isinstance(name, str) or not isinstance(text, str):
                    raise ValueError("payload source_files must map names to text")
            operator_path = Path(request["operator_path"])
            try:
                operator_path.read_bytes()
            except Exception as exc:
                operator_read = {"ok": False, "error_type": type(exc).__name__}
            else:
                operator_read = {"ok": True}
            response = {
                "ok": True,
                "role": role,
                "payload_source_names": sorted(source_files),
                "payload_source_count": len(source_files),
                "source_root_exists": source_root.is_dir(),
                "operator_read": operator_read,
            }
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__}
        print(json.dumps(response, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
