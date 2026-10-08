"""Public, single-operation PIPE3 serializer probe; no private checks or labels."""
from __future__ import annotations

from datetime import datetime
import importlib
import json
from pathlib import Path
import sys


def main() -> None:
    source = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(source))
    line = sys.stdin.readline()
    if line:
        try:
            request = json.loads(line)
            if set(request) != {"op", "probe_input"} or request["op"] != "serialize_event":
                raise ValueError("unsupported public operation")
            fields = request["probe_input"]
            if not isinstance(fields, dict) or set(fields) != {
                    "event_id", "timestamp", "user_name", "action", "page_url"}:
                raise ValueError("public event shape invalid")
            if any(not isinstance(value, str) or not value for value in fields.values()):
                raise ValueError("public event values invalid")
            models = importlib.import_module("models")
            producer = importlib.import_module("producer")
            if fields["action"] not in models.VALID_ACTIONS:
                raise ValueError("public action is not valid")
            event = models.UserEvent(**{**fields, "timestamp": datetime.fromisoformat(fields["timestamp"])})
            if event.validate() is not True:
                raise ValueError("public event validation failed")
            serialized = producer.serialize_event(event)
            if not isinstance(serialized, str):
                raise ValueError("serializer did not return text")
            decoded = json.loads(serialized)
            if not isinstance(decoded, dict):
                raise ValueError("serializer did not return an object")
            response = {"ok": True, "serialized_output": serialized,
                        "timestamp_value": decoded.get("timestamp")}
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
