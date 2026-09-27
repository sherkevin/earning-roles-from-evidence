"""Zero-LLM qualification matrix for the DIST1 producer-only scorer.

This deliberately does not run the native TeamBench grader or the real API.
It checks the scorer's ownership boundary and label/error semantics before any
producer score can become role evidence.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from peerrolebench_producer_scorer import classify, run_producer_scorer  # noqa: E402
from peerrolebench_task_contract import load_generated_task  # noqa: E402


def fixed_queue():
    return '''"""Correct producer-owned queue control."""
import threading
import uuid
from collections import deque
from typing import Any

class QueueFull(Exception):
    pass

class QueueEmpty(Exception):
    pass

class TaskQueue:
    def __init__(self, capacity: int = 500):
        self._capacity = capacity
        self._queue = deque()
        self._in_flight = {}
        self._lock = threading.Lock()

    def put(self, message: Any) -> None:
        with self._lock:
            if len(self._queue) + len(self._in_flight) >= self._capacity:
                raise QueueFull()
            self._queue.append(message)

    def get(self):
        with self._lock:
            if not self._queue:
                return None
            message = self._queue.popleft()
            receipt = str(uuid.uuid4())
            self._in_flight[receipt] = message
            return (message, receipt)

    def ack(self, receipt):
        with self._lock:
            self._in_flight.pop(receipt, None)

    def nack(self, receipt):
        with self._lock:
            message = self._in_flight.pop(receipt, None)
            if message is not None:
                self._queue.appendleft(message)

    def size(self):
        with self._lock:
            return len(self._queue)
'''


def fixed_priority():
    return '''from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PriorityTask:
    urgency: int
    seq: int
    message: Any = field(compare=False)
'''


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    raw = out / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    generated = load_generated_task("DIST1_queue_race", 0)
    base = {path: generated.workspace_files[path]
            for path in ("mqueue/__init__.py", "mqueue/config.py", "mqueue/queue.py", "mqueue/priority.py")}
    correct = dict(base)
    correct["mqueue/queue.py"] = fixed_queue()
    correct["mqueue/priority.py"] = fixed_priority()
    priority_only = dict(correct)
    priority_only["mqueue/queue.py"] = base["mqueue/queue.py"]
    ack_only = dict(correct)
    ack_only["mqueue/priority.py"] = base["mqueue/priority.py"]
    malformed = dict(base)
    malformed["mqueue/queue.py"] = "def broken(:\n"
    # The full 10k/20-producer+20-consumer contract intentionally preserves
    # resource failures as UNKNOWN: the original buggy queue can spin under
    # this stress and hit the scorer CPU cap.  A bounded scorer must never turn
    # that infrastructure/resource outcome into a negative capability label.
    cases = [("original_buggy", base, ["FAIL", "UNKNOWN"]), ("authored_correct", correct, ["PASS"]),
             ("near_priority_only", priority_only, ["FAIL", "UNKNOWN"]), ("near_ack_only", ack_only, ["FAIL"]),
             ("malformed_source", malformed, "UNKNOWN")]
    config = {"qualification_version": "dist1-producer-scorer-qualification-v2",
              "task_id": "DIST1_queue_race", "seed": 0,
              "cases": [{"name": name, "expected_status": expected,
                          "source_digests": {path: digest(files[path]) for path in files}}
                         for name, files, expected in cases],
              "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
              "candidate_received_hidden_assertions": False,
              "scientific_claim_allowed": False,
              "scorer_scope": "TeamBench DIST1 generated source shape; not contract-general"}
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    results = []
    for name, files, expected in cases:
        case_dir = out / name
        case_dir.mkdir()
        result = run_producer_scorer(files, {"queue": "TaskQueue", "priority": "PriorityTask"},
                                     "DIST1_queue_race", 0, case_dir / "scorer", log)
        observed = result.get("status")
        results.append({"name": name, "expected_status": expected, "observed_status": observed,
                        "label": result.get("label"), "quality_score": result.get("quality_score"),
                        "response_digest": result.get("response_digest"),
                        "transport": result.get("transport")})
        log("case_result", results[-1])
    correct_envelope = json.loads(
        (out / "authored_correct/scorer/response.json").read_text())["response"]
    correct_value = correct_envelope["value"]
    expected_digest = correct_value["artifact_sha256"]
    mutations = []
    for name, mutated in [
        ("worker_timeout", {"ok": False, "error_type": "TimeoutError"}),
        ("artifact_mismatch", copy.deepcopy(correct_envelope)),
        ("coverage_incomplete", copy.deepcopy(correct_envelope)),
        ("unknown_check", copy.deepcopy(correct_envelope)),
    ]:
        if name == "artifact_mismatch":
            mutated["value"]["artifact_sha256"] = "c" * 64
        elif name == "coverage_incomplete":
            mutated["value"]["status"] = "UNKNOWN"
            mutated["value"]["label"] = None
            mutated["value"]["quality_score"] = None
            mutated["value"]["coverage_complete"] = False
        elif name == "unknown_check":
            mutated["value"]["checks"][0]["status"] = "UNKNOWN"
            mutated["value"]["status"] = "UNKNOWN"
            mutated["value"]["label"] = None
            mutated["value"]["quality_score"] = None
            mutated["value"]["coverage_complete"] = False
        observed = classify(mutated, expected_digest, "DIST1_queue_race", 0)["status"]
        mutations.append({"name": name, "expected_status": "UNKNOWN", "observed_status": observed})
        log("mutation_result", mutations[-1])
    passed = all(item["observed_status"] in (item["expected_status"] if isinstance(item["expected_status"], list)
                                                else [item["expected_status"]]) for item in results)
    mutations_passed = all(item["observed_status"] == item["expected_status"] for item in mutations)
    passed = passed and mutations_passed
    summary = {"qualification_version": config["qualification_version"], "passed": passed,
               "cases": results, "mutations": mutations, "scorer_is_qualified": False,
               "scientific_claim_allowed": False,
               "remaining_gates": [
                   "near-miss coverage must be expanded across all producer checks and seeds",
                   "candidate/scorer isolation is non-adversarial Python instrumentation",
                   "producer score must be compared with situated judgment and strong baselines",
                   "second independent structural task root remains open",
               ]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": passed, "scorer_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
