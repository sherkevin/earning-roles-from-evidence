"""Public priority-module RPC using the original task's constructor contract.

No assertions, expected rankings or labels enter this process. This extension
is post-hoc for N02; it must not silently change the frozen consumer scores.
"""
import heapq
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))

for line in sys.stdin:
    try:
        request = json.loads(line)
        module = importlib.import_module("mqueue.priority")
        priority_type = getattr(module, request["class_name"])
        if request["op"] == "import":
            value = {"class_name": priority_type.__name__}
        elif request["op"] == "heap":
            items = [priority_type(**{request["priority_field"]: item["priority"],
                                      "message": item["message"]}) for item in request["items"]]
            heapq.heapify(items)
            value = [heapq.heappop(items).message for _ in range(len(items))]
        else:
            raise ValueError("Unknown public operation")
        response = {"ok": True, "value": value}
    except Exception as exc:
        response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc),
                    "errno": getattr(exc, "errno", None)}
    print(json.dumps(response), flush=True)
