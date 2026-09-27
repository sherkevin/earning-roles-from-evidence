"""Generic worker for role-payload and selected-delivery visibility probes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def digest_files(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        name_bytes = name.encode("utf-8")
        raw = value.encode("utf-8")
        h.update(len(name_bytes).to_bytes(8, "big"))
        h.update(name_bytes)
        h.update(len(raw).to_bytes(8, "big"))
        h.update(raw)
    return h.hexdigest()


def main() -> int:
    source_root = Path(sys.argv[1]).resolve()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            payload = request["payload"]
            source_files = payload["source_files"]
            delivery = request.get("delivery", {})
            required = set(payload.get("required_delivery_paths", []))
            if not isinstance(source_files, dict) or not source_files:
                raise ValueError("payload source_files must be a nonempty object")
            if not isinstance(delivery, dict) or set(delivery) != required:
                raise ValueError("delivery paths do not match recipient contract")
            if not all(isinstance(name, str) and isinstance(text, str)
                       for name, text in {**source_files, **delivery}.items()):
                raise ValueError("payload and delivery must contain text files")
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
                "payload_source_names": sorted(source_files),
                "payload_source_count": len(source_files),
                "delivery_paths": sorted(delivery),
                "delivery_sha256": digest_files(delivery) if delivery else None,
                "source_root_exists": source_root.is_dir(),
                "operator_read": operator_read,
            }
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(response, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
