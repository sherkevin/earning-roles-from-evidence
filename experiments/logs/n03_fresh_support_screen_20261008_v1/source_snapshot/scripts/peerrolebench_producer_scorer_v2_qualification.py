"""Pre-registered zero-LLM qualification for producer scorer v2.

The matrix is deliberately separate from the historical v1/v2 exploratory
runs.  It tests the new distinction between a candidate-origin hard failure
(``FAIL/0`` with incomplete downstream coverage) and scorer uncertainty
(``UNKNOWN``).  It never calls an LLM, native TeamBench grader, Nebula, or GPU.
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
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_dist1_material_adapter_v2 import build_materials  # noqa: E402
from peerrolebench_producer_scorer_v2 import (  # noqa: E402
    CHECK_IDS, SCHEMA_VERSION, SCORER_VERSION, classify, run_producer_scorer,
)
from peerrolebench_task_contract import load_generated_task  # noqa: E402


def fixed_queue():
    return '''import threading\nimport uuid\nfrom collections import deque\nfrom typing import Any\n\nclass QueueFull(Exception):\n    pass\n\nclass TaskQueue:\n    def __init__(self, capacity: int = 500):\n        self._capacity = capacity\n        self._queue = deque()\n        self._in_flight = {}\n        self._lock = threading.Lock()\n\n    def put(self, message: Any) -> None:\n        with self._lock:\n            if len(self._queue) + len(self._in_flight) >= self._capacity:\n                raise QueueFull()\n            self._queue.append(message)\n\n    def get(self):\n        with self._lock:\n            if not self._queue:\n                return None\n            message = self._queue.popleft()\n            receipt = str(uuid.uuid4())\n            self._in_flight[receipt] = message\n            return (message, receipt)\n\n    def ack(self, receipt):\n        with self._lock:\n            self._in_flight.pop(receipt, None)\n\n    def nack(self, receipt):\n        with self._lock:\n            message = self._in_flight.pop(receipt, None)\n            if message is not None:\n                self._queue.appendleft(message)\n\n    def size(self):\n        with self._lock:\n            return len(self._queue)\n'''


def fixed_priority():
    return '''from dataclasses import dataclass, field\nfrom typing import Any\n\n@dataclass(order=True)\nclass PriorityTask:\n    urgency: int\n    seq: int\n    message: Any = field(compare=False)\n'''


def dataclass_failure_priority():
    return '''from dataclasses import dataclass\nfrom typing import Any\n\n@dataclass(order=True)\nclass PriorityTask:\n    urgency: int\n    seq: int = 0\n    message: Any\n'''


def syntax_failure_queue():
    return "class TaskQueue(:\n"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def main() -> int:
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
    materials = build_materials(generated)
    support = {path: materials["agent_payloads"]["producer"]["source_files"][path]
               for path in ("mqueue/__init__.py", "mqueue/config.py")}
    base = {path: materials["agent_payloads"]["producer"]["source_files"][path]
            for path in ("mqueue/queue.py", "mqueue/priority.py")}
    correct = {**support, "mqueue/queue.py": fixed_queue(),
               "mqueue/priority.py": fixed_priority()}
    dataclass_failure = {**support, "mqueue/queue.py": fixed_queue(),
                         "mqueue/priority.py": dataclass_failure_priority()}
    syntax_failure = {**support, "mqueue/queue.py": syntax_failure_queue(),
                      "mqueue/priority.py": fixed_priority()}
    near_priority = {**correct,
                     "mqueue/priority.py": '''from dataclasses import dataclass\nfrom typing import Any\n\n@dataclass(order=True)\nclass PriorityTask:\n    urgency: int\n    message: Any\n'''}
    cases = [
        {"name": "authored_correct", "files": correct, "expected": "PASS", "repeat": 2},
        {"name": "candidate_dataclass_import_failure", "files": dataclass_failure,
         "expected": "FAIL", "repeat": 2},
        {"name": "candidate_syntax_failure", "files": syntax_failure,
         "expected": "FAIL", "repeat": 1},
        {"name": "near_priority_contract_failure", "files": near_priority,
         "expected": "FAIL", "repeat": 1},
    ]
    config = {
        "qualification_version": "dist1-producer-scorer-qualification-v3",
        "scorer_version": SCORER_VERSION, "response_schema": SCHEMA_VERSION,
        "task_id": "DIST1_queue_race", "seed": 0,
        "cases": [{"name": item["name"], "expected_status": item["expected"],
                   "repeat": item["repeat"],
                   "source_digests": {path: digest(text) for path, text in item["files"].items()}}
                  for item in cases],
        "negative_controls": ["trusted_driver_typeerror", "worker_timeout",
                              "artifact_digest_mismatch", "incomplete_response"],
        "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
        "candidate_received_hidden_assertions": False,
        "scientific_claim_allowed": False,
        "repeat_count_frozen_before_execution": True,
        "scorer_scope": "DIST1 public producer contract; no benchmark/generalization claim",
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    results = []
    for item in cases:
        observations = []
        for repeat in range(item["repeat"]):
            case_dir = out / item["name"] / f"repeat_{repeat}"
            case_dir.parent.mkdir(exist_ok=True)
            result = run_producer_scorer(item["files"], {"queue": "TaskQueue", "priority": "PriorityTask"},
                                         "DIST1_queue_race", 0, case_dir, log)
            observations.append({"status": result.get("status"), "label": result.get("label"),
                                 "quality_score": result.get("quality_score"),
                                 "decision_complete": result.get("decision_complete"),
                                 "coverage_complete": result.get("coverage_complete"),
                                 "failure_origin": result.get("failure_origin"),
                                 "failure_code": result.get("failure_code"),
                                 "source_path": result.get("source_path"),
                                 "response_digest": result.get("response_digest"),
                                 "transport": result.get("transport")})
            log("case_repeat", {"case": item["name"], "repeat": repeat,
                                 "observation": observations[-1]})
        stable = len({json.dumps(observation, sort_keys=True) for observation in observations}) == 1
        results.append({"name": item["name"], "expected_status": item["expected"],
                        "repeat": item["repeat"], "stable": stable,
                        "observations": observations})
        log("case_result", results[-1])

    # Response-level controls use the authored-correct response but mutate only
    # receipt fields; they must never become negative candidate evidence.
    correct_response = json.loads(
        (out / "authored_correct/repeat_0/response.json").read_text())["response"]
    expected_digest = correct_response["value"]["artifact_sha256"]
    controls = []
    for name, mutated in [
        ("trusted_driver_typeerror", {"ok": False, "error_type": "TypeError",
                                      "message": "non-default argument 'message' follows default argument"}),
        ("worker_timeout", {"ok": False, "error_type": "TimeoutError"}),
        ("artifact_digest_mismatch", copy.deepcopy(correct_response)),
        ("incomplete_response", copy.deepcopy(correct_response)),
    ]:
        if name == "artifact_digest_mismatch":
            mutated["value"]["artifact_sha256"] = "c" * 64
        elif name == "incomplete_response":
            mutated["value"]["decision_complete"] = False
            mutated["value"]["coverage_complete"] = False
        result = classify(mutated, expected_digest, "DIST1_queue_race", 0)
        controls.append({"name": name, "expected_status": "UNKNOWN",
                         "observed_status": result.get("status"),
                         "label": result.get("label"), "reason": result.get("reason")})
        log("negative_control", controls[-1])

    passed = all(item["stable"] and all(obs["status"] == item["expected_status"]
                                        for obs in item["observations"])
                  for item in results)
    passed = passed and all(item["observed_status"] == "UNKNOWN" and item["label"] is None
                            for item in controls)
    summary = {"qualification_version": config["qualification_version"],
               "scorer_version": SCORER_VERSION, "passed": passed,
               "cases": results, "negative_controls": controls,
               "scorer_is_qualified": False,
               "scientific_claim_allowed": False,
               "remaining_gates": [
                   "candidate/scorer isolation remains non-adversarial Python instrumentation",
                   "second independent structural task root remains open",
                   "same-information baselines and live responsibility evidence remain open",
               ]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": passed, "scorer_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
