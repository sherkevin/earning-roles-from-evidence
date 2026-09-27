"""Post-hoc coverage audit using sealed actual deliveries, not a new LLM run."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import traceback

from peerrolebench_consumer_checks import require_behavior_response
from peerrolebench_sandbox import ROOT, SandboxedWorker
from peerrolebench_task_contract import _digest_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False, parents=True)
    worker_path = ROOT / "scripts/peerrolebench_priority_worker.py"
    config = {"purpose": "posthoc priority-module coverage audit; not native grade or original N02 outcome",
              "command": sys.argv, "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [Path(__file__), worker_path, ROOT / "scripts/peerrolebench_sandbox.py"]},
              "arms": ["authored_correct_control", "episode_0", "episode_1"],
              "llm_calls": 0, "gpu_jobs": 0, "grades_modified": False, "scientific_claim_allowed": False}
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    def log(event, payload):
        with (out / "raw.jsonl").open("a") as stream:
            stream.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event, "payload": payload}) + "\n")
    log("config", config)
    control = '''from dataclasses import dataclass, field
from typing import Any
@dataclass(order=True)
class PriorityTask:
    urgency: int
    message: Any = field(compare=False)
'''
    arms = [("authored_correct_control", {"mqueue/__init__.py": "", "mqueue/priority.py": control},
             "PriorityTask", "urgency")]
    for index, name, field in [(0, "PriorityTask", "urgency"), (1, "PriorityEvent", "severity")]:
        path = args.run / f"episode_{index}/sealed_consumer.json"
        sealed = json.loads(path.read_text())
        if _digest_files(sealed["source_files"]) != sealed["output_source_sha256"]:
            raise RuntimeError("Frozen source digest mismatch")
        log("source_provenance", {"index": index, "file": str(path),
                                  "sealed_sha256": sealed["output_source_sha256"],
                                  "source_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        arms.append((f"episode_{index}", sealed["source_files"], name, field))
    all_results = []
    for arm, sources, class_name, field in arms:
        results = []
        try:
            with SandboxedWorker(sources, out / arm, log, worker_path=worker_path) as worker:
                requests = [
                    ("import", {"op": "import", "class_name": class_name}),
                    ("original_constructor_equal_priority", {"op": "heap", "class_name": class_name,
                        "priority_field": field, "items": [{"priority": 1, "message": {"task": 1}},
                                                            {"priority": 1, "message": [2, 3]}]})]
                for name, request in requests:
                    try:
                        response = require_behavior_response(worker.request(request))
                        passed = response.get("ok") is True
                        if passed and name == "original_constructor_equal_priority":
                            passed = sorted(map(json.dumps, response["value"])) == sorted(map(json.dumps, [{"task": 1}, [2, 3]]))
                        result = {"check": name, "status": "PASS" if passed else "FAIL", "response": response}
                    except (RuntimeError, ValueError, OSError, TimeoutError) as exc:
                        result = {"check": name, "status": "UNKNOWN", "error": repr(exc)}
                    results.append(result)
                    log("check_result", {"arm": arm, **result})
        except Exception as exc:
            log("arm_error", {"arm": arm, "error": repr(exc), "traceback": traceback.format_exc()})
            results.append({"check": "runtime", "status": "UNKNOWN", "error": repr(exc)})
        all_results.append({"arm": arm, "checks": results})
    summary = {"results": all_results, "grade_changed": False, "posthoc_diagnostic": True,
               "scientific_claim_allowed": False}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    log("summary", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
