"""Private DIST1 scorer worker.

The worker receives only the sealed public source copy from the parent
``SandboxedWorker``.  Its check data and assertions stay in this trusted
worker.  The candidate/LLM process never receives this file or its results
until the parent records the response.  This is an operator scorer boundary,
not a claim of hostile-code security or native TeamBench equivalence.
"""
from __future__ import annotations

import functools
import importlib
import json
from pathlib import Path
import sys


SCORER_VERSION = "dist1-independent-scorer-v1"
CHECK_IDS = ("empty_consumer", "payload_and_ack", "retry_after_handler_failure", "drain")


class HandlerRetry(Exception):
    """Private driver exception used to test recipient retry behavior."""


class Driver:
    def __init__(self, source: str, queue_name: str, consumer_name: str):
        sys.path.insert(0, str(Path(source).resolve()))
        queue_type = getattr(importlib.import_module("mqueue.queue"), queue_name)
        consumer_type = getattr(importlib.import_module("mqueue.consumer"), consumer_name)
        self.queue_type = queue_type
        self.consumer_type = consumer_type
        self.queue = None
        self.consumer = None
        self.events = []
        self.queue_events = []
        self.failures_left = 0

    def init(self, handler_failures=0):
        self.queue = self.queue_type(capacity=10)
        self.queue_events = []

        def observe(name):
            original = getattr(self.queue, name, None)
            if original is None:
                return

            @functools.wraps(original)
            def traced(*args, **kwargs):
                value = original(*args, **kwargs)
                self.queue_events.append({"op": name, "args": list(args), "value": value})
                return value

            setattr(self.queue, name, traced)

        for name in ("get", "ack", "nack"):
            observe(name)
        self.failures_left = handler_failures
        self.events = []

        def handler(message):
            failed = self.failures_left > 0
            if failed:
                self.failures_left -= 1
            self.events.append({"message": message, "failed": failed})
            if failed:
                raise HandlerRetry("Private scorer requested one handler failure")

        self.consumer = self.consumer_type(self.queue, handler)
        return None

    def call(self, op, **fields):
        if op == "init":
            value = self.init(fields.get("handler_failures", 0))
        elif op == "put":
            value = self.queue.put(fields["message"])
        elif op == "get":
            value = self.queue.get()
        elif op == "ack":
            value = self.queue.ack(fields["receipt"])
        elif op == "nack":
            value = self.queue.nack(fields["receipt"])
        elif op == "consume_once":
            value = self.consumer.run_once()
        elif op == "drain":
            value = self.consumer.run_until_empty(max_idle_cycles=2)
        elif op == "snapshot":
            value = {"handler_events": self.events,
                     "processed_count": self.consumer.processed_count,
                     "processed_messages": self.consumer.processed_messages,
                     "queue_events": self.queue_events,
                     "queue_size": self.queue.size(),
                     "queue_empty": self.queue.is_empty()}
        else:
            raise ValueError("Unknown private scorer operation: " + str(op))
        return {"ok": True, "value": value}

    def safe_call(self, op, **fields):
        try:
            return self.call(op, **fields)
        except Exception as exc:  # returned to the trusted scorer only
            return {"ok": False, "error_type": type(exc).__name__,
                    "message": str(exc), "errno": getattr(exc, "errno", None)}


def require_ok(answer):
    if not isinstance(answer, dict) or answer.get("ok") is not True:
        raise RuntimeError("private driver operation failed: " + repr(answer))
    return answer.get("value")


def empty(value):
    """Accept the direct tuple and JSON-list forms of an empty dequeue."""
    return value is None or (
        isinstance(value, (tuple, list)) and len(value) == 2
        and value[0] is None and value[1] is None
    )


def pair(value):
    """Accept the in-process tuple and its JSON-list representation."""
    return isinstance(value, (tuple, list)) and len(value) == 2


def score(driver):
    results = []

    def case(name, check):
        try:
            check()
            results.append({"id": name, "status": "PASS"})
        except AssertionError as exc:
            results.append({"id": name, "status": "FAIL", "reason": str(exc)})
        except (RuntimeError, ValueError, OSError, KeyError, TypeError, IndexError) as exc:
            results.append({"id": name, "status": "UNKNOWN", "reason": repr(exc)})

    def check_empty():
        require_ok(driver.safe_call("init"))
        assert require_ok(driver.safe_call("consume_once")) is False
        state = require_ok(driver.safe_call("snapshot"))
        assert state["handler_events"] == []
        assert state["processed_count"] == 0

    def check_ack():
        message = {"job": "payload-object", "values": [3, 1]}
        require_ok(driver.safe_call("init"))
        require_ok(driver.safe_call("put", message=message))
        first = require_ok(driver.safe_call("get"))
        assert pair(first) and first[0] == message
        assert first[1] is not None
        require_ok(driver.safe_call("nack", receipt=first[1]))
        assert require_ok(driver.safe_call("consume_once")) is True
        state = require_ok(driver.safe_call("snapshot"))
        assert state["handler_events"] == [{"message": message, "failed": False}]
        assert state["processed_messages"] == [message]
        assert state["processed_count"] == 1
        observed = state["queue_events"]
        get_index = max(i for i, event in enumerate(observed) if event["op"] == "get")
        receipt = observed[get_index]["value"][1]
        assert any(event["op"] == "ack" and event["args"] == [receipt]
                   for event in observed[get_index + 1:])
        assert state["queue_empty"] is True
        assert empty(require_ok(driver.safe_call("get")))
        require_ok(driver.safe_call("nack", receipt=receipt))
        assert empty(require_ok(driver.safe_call("get")))

    def check_retry():
        message = {"job": "retryable", "value": 0}
        require_ok(driver.safe_call("init", handler_failures=1))
        require_ok(driver.safe_call("put", message=message))
        first = driver.safe_call("consume_once")
        assert first.get("ok") or first.get("error_type") == "HandlerRetry"
        state = require_ok(driver.safe_call("snapshot"))
        assert state["handler_events"] == [{"message": message, "failed": True}]
        assert state["processed_count"] == 0
        assert require_ok(driver.safe_call("consume_once")) is True
        state = require_ok(driver.safe_call("snapshot"))
        assert state["handler_events"] == [
            {"message": message, "failed": True},
            {"message": message, "failed": False},
        ]
        assert state["processed_messages"] == [message]
        assert state["processed_count"] == 1
        assert require_ok(driver.safe_call("consume_once")) is False

    def check_drain():
        messages = [0, False, "", {"nested": [1, 2]}]
        require_ok(driver.safe_call("init"))
        for message in messages:
            require_ok(driver.safe_call("put", message=message))
        require_ok(driver.safe_call("drain"))
        state = require_ok(driver.safe_call("snapshot"))
        assert state["processed_messages"] == messages
        assert state["processed_count"] == len(messages)
        assert state["handler_events"] == [{"message": m, "failed": False} for m in messages]
        assert state["queue_empty"] is True

    checks = (check_empty, check_ack, check_retry, check_drain)
    for name, check in zip(CHECK_IDS, checks):
        if results and results[-1]["status"] in {"UNKNOWN", "NOT_RUN"}:
            results.append({"id": name, "status": "NOT_RUN", "reason": "prior private transport failure"})
            continue
        case(name, check)
    complete = all(item["status"] in {"PASS", "FAIL"} for item in results)
    passed = complete and all(item["status"] == "PASS" for item in results)
    score_value = (sum(item["status"] == "PASS" for item in results) / len(results)) if results else 0.0
    return {"ok": True, "scorer_version": SCORER_VERSION,
            "required_check_ids": list(CHECK_IDS), "checks": results,
            "status": "PASS" if passed else "FAIL" if complete else "UNKNOWN",
            "score": score_value, "coverage_complete": complete}


def main():
    source, queue_name, consumer_name = sys.argv[1:4]
    driver = Driver(source, queue_name, consumer_name)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request != {"op": "score"}:
                raise ValueError("private scorer accepts only {op: score}")
            result = score(driver)
        except Exception as exc:
            result = {"ok": False, "scorer_version": SCORER_VERSION,
                      "status": "UNKNOWN", "coverage_complete": False,
                      "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(result, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
