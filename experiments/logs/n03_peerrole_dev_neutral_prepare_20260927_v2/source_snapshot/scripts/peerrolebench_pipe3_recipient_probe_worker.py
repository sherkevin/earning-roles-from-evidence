"""Probe recipient payload plus one selected producer delivery."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def digest_files(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        raw = value.encode("utf-8")
        h.update(len(name.encode()).to_bytes(8, "big"))
        h.update(name.encode())
        h.update(len(raw).to_bytes(8, "big"))
        h.update(raw)
    return h.hexdigest()


def main() -> int:
    source_root = Path(sys.argv[1]).resolve()
    for line in sys.stdin:
        request = json.loads(line)
        try:
            payload = request["payload"]
            delivery = request["delivery"]
            required = set(payload["required_delivery_paths"])
            if set(delivery) != required:
                raise ValueError("delivery paths do not match recipient contract")
            if not all(isinstance(name, str) and isinstance(text, str)
                       for name, text in delivery.items()):
                raise ValueError("delivery must contain text files")
            operator_path = Path(request["operator_path"])
            try:
                operator_path.read_bytes()
            except Exception as exc:
                operator_read = {"ok": False, "error_type": type(exc).__name__}
            else:
                operator_read = {"ok": True}
            response = {
                "ok": True,
                "role": payload["role"],
                "payload_source_names": sorted(payload["source_files"]),
                "delivery_paths": sorted(delivery),
                "delivery_sha256": digest_files(delivery),
                "source_root_exists": source_root.is_dir(),
                "operator_read": operator_read,
            }
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__}
        print(json.dumps(response, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
