"""Parent-side behavioral checks; never copy these assertions to the worker.

These check a real delivered queue through the actual consumer, independently
of the native TeamBench score. This is a versioned extension, not the native
benchmark. A production run must seal consumer output before evaluation.
"""
from __future__ import annotations


CHECK_VERSION = "dist1-consumer-behavior-v2"
CHECK_IDS = ("empty_consumer", "payload_and_ack", "retry_after_handler_failure", "drain")
RUNTIME_ERROR_TYPES = frozenset({"MemoryError", "PermissionError", "BlockingIOError", "OSError",
                                "TimeoutError", "InterruptedError", "BrokenPipeError",
                                "ConnectionError", "ConnectionResetError", "ConnectionAbortedError"})


def require_behavior_response(answer):
    """Environment/resource refusals cannot become a peer capability label."""
    if not isinstance(answer, dict):
        raise RuntimeError("Malformed public worker response")
    if answer.get("ok") is False and answer.get("error_type") in RUNTIME_ERROR_TYPES:
        raise RuntimeError("Worker runtime/permission/resource failure: " + repr(answer))
    return answer


def run_checks(request):
    """Run trusted assertions through a callable public request/response bridge.

    Transport exceptions yield UNKNOWN without erasing earlier observed
    failures. Completed behavioral violations yield FAIL. Full grading
    requires exactly the four check ids with no missing or UNKNOWN result.
    """
    results = []

    def call(op, **fields):
        answer = require_behavior_response(request({"op": op, **fields}))
        assert answer.get("ok") is True, f"{op} failed: {answer}"
        return answer.get("value")

    def empty(value):
        return value is None or value == [None, None]

    def case(name, check):
        try:
            check()
            results.append({"id": name, "status": "PASS"})
        except AssertionError as exc:
            results.append({"id": name, "status": "FAIL", "reason": str(exc)})
        except (TimeoutError, RuntimeError, ValueError, OSError, KeyError, TypeError, IndexError) as exc:
            results.append({"id": name, "status": "UNKNOWN", "reason": repr(exc)})

    def check_empty():
        call("init")
        assert call("consume_once") is False, "Empty queue must not invoke handler"
        state = call("snapshot")
        assert state["handler_events"] == [], "Consumer passed an empty sentinel to handler"
        assert state["processed_count"] == 0

    def check_ack():
        message = {"job": "payload-object", "values": [3, 1]}
        call("init")
        call("put", message=message)
        first = call("get")
        assert isinstance(first, list) and len(first) == 2 and first[0] == message, "Queue get needs payload and receipt"
        assert first[1] is not None, "Queue must issue a receipt"
        call("nack", receipt=first[1])
        assert call("consume_once") is True
        state = call("snapshot")
        assert state["handler_events"] == [{"message": message, "failed": False}], "Handler must receive the message, not (message, receipt)"
        assert state["processed_messages"] == [message] and state["processed_count"] == 1
        observed = state["queue_events"]
        get_index = max(i for i, e in enumerate(observed) if e["op"] == "get")
        receipt = observed[get_index]["value"][1]
        assert any(e["op"] == "ack" and e["args"] == [receipt] for e in observed[get_index + 1:]), "Consumer never acknowledged its successful receipt"
        assert state["queue_empty"] is True
        assert empty(call("get")), "Successful work remained queued"
        # Existing receipt must not revive already completed work.
        call("nack", receipt=receipt)
        assert empty(call("get")), "Completed work was redelivered"

    def check_retry():
        message = {"job": "retryable", "value": 0}
        call("init", handler_failures=1)
        call("put", message=message)
        first = require_behavior_response(request({"op": "consume_once"}))
        assert first.get("ok") or first.get("error_type") == "HandlerRetry", "Unexpected consumer failure"
        state = call("snapshot")
        assert state["handler_events"] == [{"message": message, "failed": True}]
        assert state["processed_count"] == 0, "Failed processing was counted as completed"
        assert call("consume_once") is True, "Failed message must remain retryable"
        state = call("snapshot")
        assert state["handler_events"] == [{"message": message, "failed": True}, {"message": message, "failed": False}]
        assert state["processed_messages"] == [message] and state["processed_count"] == 1
        assert call("consume_once") is False, "Retry duplicated completed work"

    def check_drain():
        messages = [0, False, "", {"nested": [1, 2]}]
        call("init")
        for message in messages:
            call("put", message=message)
        call("drain")
        state = call("snapshot")
        assert state["processed_messages"] == messages, "Drain lost, duplicated or changed payloads"
        assert state["processed_count"] == len(messages)
        assert state["handler_events"] == [{"message": m, "failed": False} for m in messages]
        assert state["queue_empty"] is True

    for name, check in zip(CHECK_IDS, (check_empty, check_ack, check_retry, check_drain)):
        if results and results[-1]["status"] in {"UNKNOWN", "NOT_RUN"}:
            results.append({"id": name, "status": "NOT_RUN", "reason": "Prior transport failure"})
            continue
        case(name, check)
    complete = all(r["status"] in {"PASS", "FAIL"} for r in results)
    return {"version": CHECK_VERSION, "required_check_ids": list(CHECK_IDS), "checks": results,
            "status": ("UNKNOWN" if not complete else
                       "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"),
            "observed_behavioral_failure": any(r["status"] == "FAIL" for r in results),
            "coverage_complete": complete and [r["id"] for r in results] == list(CHECK_IDS)}
