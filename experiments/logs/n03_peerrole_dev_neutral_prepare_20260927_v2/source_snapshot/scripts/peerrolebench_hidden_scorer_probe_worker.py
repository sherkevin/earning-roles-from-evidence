"""Private scorer probe used only for IPC qualification.

The expected digest is intentionally kept in this worker's private trusted
copy.  The public request contains only a candidate artifact digest and public
context.  This is a boundary diagnostic, not a benchmark grader.
"""
from __future__ import annotations

import hashlib
import json
import sys


# Frozen digest from the preserved N02-v3 delivery fixture.  The candidate
# worker never receives this module or its trusted directory.
EXPECTED_ARTIFACT_SHA256 = "22151c18471bf6a4e909cfc457b53288c60b4712927b26cbd4a6fc778da23f8b"
SCORER_VERSION = "hidden-ipc-probe-v1"


def response_digest(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if not isinstance(request, dict) or set(request) != {"op", "artifact_sha256", "public_context"}:
                raise ValueError("scorer request must contain only public fields")
            if request["op"] != "score" or not isinstance(request["artifact_sha256"], str):
                raise ValueError("invalid public scorer request")
            if not isinstance(request["public_context"], dict):
                raise ValueError("public_context must be an object")
            status = "PASS" if request["artifact_sha256"] == EXPECTED_ARTIFACT_SHA256 else "FAIL"
            result = {"ok": True, "status": status, "scorer_version": SCORER_VERSION,
                      "coverage_complete": True, "public_context_keys": sorted(request["public_context"])}
        except Exception as exc:
            result = {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
        result["response_sha256"] = response_digest(result)
        print(json.dumps(result, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
