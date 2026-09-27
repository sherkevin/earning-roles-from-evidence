"""Private producer-only scorer for the DIST1 queue/priority contract.

The second launch argument is the generated priority class name (the existing
SandboxedWorker calls it ``consumer_name`` for the recipient driver).  This
worker never imports or scores ``consumer.py``.  Its checks are kept in the
trusted driver directory and the public request carries only an artifact
digest and versioned task metadata.
"""
from __future__ import annotations

import ast
from dataclasses import fields
import hashlib
import importlib
import json
from pathlib import Path
import sys
import threading


SCHEMA_VERSION = "dist1-producer-score-response-v1"
REQUEST_SCHEMA = "dist1-producer-score-request-v1"
SCORER_VERSION = "dist1-producer-objective-v1"
CHECK_IDS = ("P1_source_parse", "P2_capacity", "P3_ack_receipt",
             "P4_nack_recovery", "P5_priority_type_safety", "P6_priority_order",
             "P7_zero_loss")


class ContractFailure(AssertionError):
    pass


def digest_files(files):
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        part = path.encode()
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
        part = content.encode() if isinstance(content, str) else content
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
    return digest.hexdigest()


class RaceDeque:
    """Deterministically exposes a check/append race in a buggy queue."""
    def __init__(self):
        self.items = []
        self.barrier = threading.Barrier(2)

    def __len__(self):
        return len(self.items)

    def append(self, item):
        try:
            self.barrier.wait(timeout=0.25)
        except threading.BrokenBarrierError:
            pass
        self.items.append(item)

    def popleft(self):
        return self.items.pop(0)

    def appendleft(self, item):
        self.items.insert(0, item)

    def __bool__(self):
        return bool(self.items)


class Scorer:
    def __init__(self, source, queue_name, priority_name):
        self.source = Path(source).resolve()
        self.queue_name = queue_name
        self.priority_name = priority_name
        sys.path.insert(0, str(self.source))
        self.queue_module = None
        self.priority_module = None
        self.queue_type = None
        self.priority_type = None

    def load_modules(self):
        try:
            self.queue_module = importlib.import_module("mqueue.queue")
            self.priority_module = importlib.import_module("mqueue.priority")
            self.queue_type = getattr(self.queue_module, self.queue_name)
            self.priority_type = getattr(self.priority_module, self.priority_name)
        except (SyntaxError, ImportError, AttributeError) as exc:
            raise ContractFailure("queue/priority source cannot be imported") from exc

    def fresh_queue_module(self):
        if self.queue_module is None:
            self.load_modules()
        self.queue_module = importlib.reload(self.queue_module)
        self.queue_type = getattr(self.queue_module, self.queue_name)

    def check_p1(self):
        for name in ("mqueue/queue.py", "mqueue/priority.py"):
            ast.parse((self.source / name).read_text(), filename=name)
        self.load_modules()
        assert self.queue_type and self.priority_type

    def check_p2(self):
        self.fresh_queue_module()
        original = self.queue_module.deque
        self.queue_module.deque = RaceDeque
        try:
            queue = self.queue_type(capacity=1)
            successes, errors = [], []
            start = threading.Barrier(2)

            def put(value):
                try:
                    start.wait(timeout=1)
                    queue.put(value)
                    successes.append(value)
                except Exception as exc:
                    errors.append(exc)

            threads = [threading.Thread(target=put, args=(i,)) for i in (1, 2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=2)
            assert not any(thread.is_alive() for thread in threads), "capacity harness timed out"
            assert len(successes) <= 1, "capacity exceeded under forced concurrent append"
            current_size = len(queue) if hasattr(queue, "__len__") else queue.size()
            assert current_size <= 1, "queue size exceeded capacity"
        finally:
            self.queue_module.deque = original

    def check_p3(self):
        self.fresh_queue_module()
        queue = self.queue_type(capacity=2)
        message = {"payload": [1, 2]}
        queue.put(message)
        result = queue.get()
        if not isinstance(result, tuple) or len(result) != 2:
            raise ContractFailure("get must return (message, receipt)")
        assert result[0] == message and result[1] is not None
        assert hasattr(queue, "ack"), "missing ack"
        queue.ack(result[1])
        value = queue.get()
        assert value is None or value == (None, None) or value == [None, None]

    def check_p4(self):
        self.fresh_queue_module()
        queue = self.queue_type(capacity=2)
        message = {"recover": True}
        queue.put(message)
        first = queue.get()
        if not isinstance(first, tuple) or len(first) != 2:
            raise ContractFailure("nack requires a receipt returned by get")
        assert hasattr(queue, "nack"), "missing nack"
        queue.nack(first[1])
        second = queue.get()
        assert isinstance(second, tuple) and second[0] == message

    def priority_instance(self, priority, message, sequence=0):
        names = [field.name for field in fields(self.priority_type)]
        if len(names) < 2:
            raise ContractFailure("priority wrapper has no payload field")
        message_name = "message" if "message" in names else names[-1]
        values = {names[0]: priority, message_name: message}
        if "seq" in names:
            values["seq"] = sequence
        elif "counter" in names:
            values["counter"] = sequence
        return self.priority_type(**values)

    def check_p5(self):
        for first, second in (({"a": 1}, {"b": 2}), ([1, 2], [3, 4])):
            a = self.priority_instance(1, first, sequence=0)
            b = self.priority_instance(1, second, sequence=1)
            try:
                _ = a < b
            except TypeError as exc:
                raise ContractFailure("equal-priority payloads are not comparable") from exc

    def check_p6(self):
        values = [self.priority_instance(2, {"id": "late"}, sequence=1),
                  self.priority_instance(0, {"id": "early"}, sequence=0)]
        names = [field.name for field in fields(self.priority_type)]
        try:
            ordered = sorted(values)
        except TypeError as exc:
            raise ContractFailure("priority ordering compares payload values") from exc
        assert getattr(ordered[0], names[0]) == 0
        equal = [self.priority_instance(1, {"id": "late"}, sequence=1),
                 self.priority_instance(1, {"id": "early"}, sequence=0)]
        try:
            equal_ordered = sorted(equal)
        except TypeError as exc:
            raise ContractFailure("equal-priority ordering is not deterministic") from exc
        if "seq" in names or "counter" in names:
            tie_value = getattr(equal_ordered[0], "seq", getattr(equal_ordered[0], "counter", None))
            assert tie_value == 0
        else:
            assert getattr(equal_ordered[0], names[-1])["id"] == "late"

    def check_p7(self):
        self.fresh_queue_module()
        total = 10_000
        queue = self.queue_type(capacity=total + 1)
        messages = list(range(total))
        errors = []
        seen = []
        seen_lock = threading.Lock()
        producers_done = threading.Event()

        def put_range(start):
            try:
                for value in range(start, start + total // 20):
                    queue.put(value)
            except Exception as exc:
                errors.append(exc)

        def consume():
            idle = 0
            while not producers_done.is_set() or (queue.size() if hasattr(queue, "size") else True):
                try:
                    value = queue.get()
                except Exception as exc:
                    errors.append(exc)
                    return
                if value is None:
                    idle += 1
                    if producers_done.is_set() and idle > 20:
                        return
                    continue
                idle = 0
                if isinstance(value, tuple):
                    message, receipt = value
                    if hasattr(queue, "ack"):
                        queue.ack(receipt)
                else:
                    message = value
                with seen_lock:
                    seen.append(message)

        threads = [threading.Thread(target=put_range, args=(i * (total // 20),)) for i in range(20)]
        consumers = [threading.Thread(target=consume) for _ in range(20)]
        for thread in consumers:
            thread.start()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        producers_done.set()
        for thread in consumers:
            thread.join(timeout=5)
        assert not any(thread.is_alive() for thread in threads + consumers), "zero-loss harness timed out"
        assert not errors, "producer failed during zero-loss workload"
        assert sorted(seen) == messages

    def run(self):
        files = {name: (self.source / name).read_text()
                 for name in ("mqueue/queue.py", "mqueue/priority.py")}
        result_digest = digest_files(files)
        checks = []
        functions = (self.check_p1, self.check_p2, self.check_p3, self.check_p4,
                     self.check_p5, self.check_p6, self.check_p7)
        for check_id, function in zip(CHECK_IDS, functions):
            try:
                function()
                checks.append({"id": check_id, "status": "PASS"})
            except ContractFailure as exc:
                checks.append({"id": check_id, "status": "FAIL", "reason": str(exc)})
            except AssertionError as exc:
                checks.append({"id": check_id, "status": "FAIL", "reason": str(exc)})
            except (TimeoutError, OSError, RuntimeError, ValueError, TypeError, ImportError) as exc:
                checks.append({"id": check_id, "status": "UNKNOWN",
                               "reason": type(exc).__name__ + ": " + str(exc)})
        complete = len(checks) == len(CHECK_IDS) and all(item["status"] in {"PASS", "FAIL"} for item in checks)
        passed = complete and all(item["status"] == "PASS" for item in checks)
        score = (sum(item["status"] == "PASS" for item in checks) / len(CHECK_IDS)) if complete else None
        return {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                "task_id": "DIST1_queue_race", "seed": None,
                "artifact_sha256": result_digest,
                "status": "PASS" if passed else "FAIL" if complete else "UNKNOWN",
                "label": 1 if passed else 0 if complete else None,
                "quality_score": score, "coverage_complete": complete,
                "checks": checks, "failed_check_ids": [item["id"] for item in checks if item["status"] == "FAIL"],
                "observed_check_count": len(checks), "required_check_ids": list(CHECK_IDS)}


def main():
    source, queue_name, priority_name = sys.argv[1:4]
    scorer = Scorer(source, queue_name, priority_name)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            required = {"op", "schema_version", "task_id", "seed", "artifact_sha256", "scorer_version"}
            if set(request) != required or request["op"] != "score_producer":
                raise ValueError("producer scorer request fields are invalid")
            if request["schema_version"] != REQUEST_SCHEMA or request["task_id"] != "DIST1_queue_race":
                raise ValueError("producer scorer request schema/task mismatch")
            if request["scorer_version"] != SCORER_VERSION:
                raise ValueError("producer scorer version mismatch")
            result = scorer.run()
            result["seed"] = request["seed"]
            if request["artifact_sha256"] != result["artifact_sha256"]:
                result = {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                          "task_id": request["task_id"], "seed": request["seed"],
                          "artifact_sha256": result["artifact_sha256"], "status": "UNKNOWN",
                          "label": None, "quality_score": None, "coverage_complete": False,
                          "checks": [], "failed_check_ids": [], "observed_check_count": 0,
                          "required_check_ids": list(CHECK_IDS), "reason": "artifact_digest_mismatch"}
            response = {"ok": True, "value": result}
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(response, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
