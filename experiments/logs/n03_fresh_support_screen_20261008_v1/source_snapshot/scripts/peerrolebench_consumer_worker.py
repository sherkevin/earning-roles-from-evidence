"""Public JSON-lines driver for a DIST1 candidate's queue and consumer.

This worker contains no expected outputs, assertions, task scores or labels.
The parent must launch it in an independently qualified sandbox before using
untrusted source. Its protocol is public; it is not a security boundary itself.
"""
import importlib
import functools
import json
from pathlib import Path
import sys


class HandlerRetry(Exception):
    pass


def main():
    source, queue_name, consumer_name = sys.argv[1:4]
    sys.path.insert(0, str(Path(source).resolve()))
    queue_type = getattr(importlib.import_module("mqueue.queue"), queue_name)
    consumer_type = getattr(importlib.import_module("mqueue.consumer"), consumer_name)
    queue = None
    consumer = None
    events = []
    queue_events = []
    failures_left = 0

    def handler(message):
        nonlocal failures_left
        failed = failures_left > 0
        if failed:
            failures_left -= 1
        events.append({"message": message, "failed": failed})
        if failed:
            raise HandlerRetry("Public driver requested one handler failure")

    for line in sys.stdin:
        try:
            request = json.loads(line)
            op = request["op"]
            if op == "init":
                queue = queue_type(capacity=request.get("capacity", 10))
                queue_events = []
                def observe(name):
                    original = getattr(queue, name, None)
                    if original is None:
                        return
                    @functools.wraps(original)
                    def traced(*args, **kwargs):
                        value = original(*args, **kwargs)
                        queue_events.append({"op": name, "args": list(args), "value": value})
                        return value
                    setattr(queue, name, traced)
                for name in ("get", "ack", "nack"):
                    observe(name)
                consumer = consumer_type(queue, handler)
                events = []
                failures_left = request.get("handler_failures", 0)
                result = None
            elif op == "put":
                result = queue.put(request["message"])
            elif op == "get":
                result = queue.get()
            elif op == "ack":
                result = queue.ack(request["receipt"])
            elif op == "nack":
                result = queue.nack(request["receipt"])
            elif op == "consume_once":
                result = consumer.run_once()
            elif op == "drain":
                result = consumer.run_until_empty(max_idle_cycles=2)
            elif op == "snapshot":
                result = {"handler_events": events, "processed_count": consumer.processed_count,
                          "processed_messages": consumer.processed_messages,
                          "queue_events": queue_events,
                          "queue_size": queue.size(), "queue_empty": queue.is_empty()}
            else:
                raise ValueError("Unknown public operation: " + str(op))
            response = {"ok": True, "value": result}
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc),
                        "errno": getattr(exc, "errno", None)}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
