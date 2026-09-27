"""Execute authored mutation controls for the consumer scorer, with raw logs.

Only reviewed deterministic fixtures from this repository are executed. This
runner explicitly refuses arbitrary candidate paths: production sandbox and
real-model orchestration are separate qualification gates.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import selectors
import subprocess
import sys
import time

from peerrolebench_consumer_checks import run_checks
from peerrolebench_task_contract import TEAMBENCH, TEAMBENCH_SOURCE_COMMIT, load_generated_task
from peerrolebench_tb_vertical_slice import write_dist1_repair


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_consumer_worker.py"
ARMS = ("fixed", "original_consumer", "no_ack", "no_nack", "drops_falsy")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    raw = out / "raw.jsonl"

    def log(event, payload):
        with raw.open("a") as f:
            f.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "event_type": event, "payload": payload}) + "\n")

    pin = subprocess.check_output(["git", "-C", str(TEAMBENCH), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(TEAMBENCH), "status", "--porcelain"], text=True)
    if pin != TEAMBENCH_SOURCE_COMMIT or dirty:
        raise RuntimeError("TeamBench checkout must match the reviewed clean source pin")
    source_names = [Path(__file__).name, WORKER.name, "peerrolebench_consumer_checks.py",
                    "peerrolebench_task_contract.py", "peerrolebench_tb_vertical_slice.py"]
    config = {"kind": "consumer_scorer_mutation_qualification", "command": sys.argv,
              "source_commit": pin, "source_hashes": {name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest() for name in source_names},
              "task_id": "DIST1_queue_race", "seed": 0, "arms": ARMS,
              "python": sys.version, "platform": platform.platform(), "random_seed": None,
              "execution": "trusted hand-written fixtures only; not sandbox-qualified",
              "timeout_per_rpc_seconds": 3, "native_grade_invoked": False,
              "real_llm_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False}
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    log("config", config)
    generated = load_generated_task("DIST1_queue_race", 0)
    results = []
    for arm in ARMS:
        directory = out / arm
        (directory / "mqueue").mkdir(parents=True)
        for name, text in generated.workspace_files.items():
            if name.startswith("mqueue/"):
                (directory / name).write_text(text)
        write_dist1_repair(directory)
        consumer = directory / "mqueue/consumer.py"
        fixed = consumer.read_text()
        if arm == "original_consumer":
            consumer.write_text(generated.workspace_files["mqueue/consumer.py"])
        elif arm == "no_ack":
            consumer.write_text(fixed.replace("        self._queue.ack(receipt)", "        pass  # MUTATION: no successful acknowledgement"))
        elif arm == "no_nack":
            consumer.write_text(fixed.replace("            self._queue.nack(receipt)", "            pass  # MUTATION: lose failed delivery"))
        elif arm == "drops_falsy":
            consumer.write_text(fixed.replace("if message is None or receipt is None:", "if not message or receipt is None:"))
        command = [sys.executable, "-I", "-B", str(WORKER), str(directory), "TaskQueue", "TaskConsumer"]
        log("worker_start", {"arm": arm, "command": command,
                             "source_hashes": {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob("*.py")}})
        started = time.monotonic()
        with (directory / "stderr.txt").open("w") as stderr:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                                    text=True, bufsize=1, cwd=directory,
                                    env={"PATH": "/usr/bin:/bin", "LANG": "C"})
            ready = selectors.DefaultSelector()
            ready.register(proc.stdout, selectors.EVENT_READ)
            def request(payload):
                log("worker_request", {"arm": arm, "request": payload})
                proc.stdin.write(json.dumps(payload) + "\n")
                proc.stdin.flush()
                if not ready.select(3):
                    raise TimeoutError("worker response exceeded 3 seconds")
                line = proc.stdout.readline()
                log("worker_response", {"arm": arm, "raw": line})
                if not line:
                    raise RuntimeError("worker exited before response")
                return json.loads(line)
            try:
                result = run_checks(request)
            except Exception as exc:
                result = {"status": "UNKNOWN", "error": repr(exc), "coverage_complete": False}
            finally:
                ready.close()
                proc.stdin.close()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                proc.stdout.close()
        result.update({"arm": arm, "worker_exit_code": proc.returncode,
                       "wall_seconds": time.monotonic() - started})
        results.append(result)
        log("arm_result", result)
    passed = results[0]["status"] == "PASS" and all(r.get("observed_behavioral_failure") for r in results[1:])
    summary = {"fixture_discrimination_passed": passed, "results": results,
               "native_scorer_implementation_modified": False, "native_score_executed_in_this_run": False,
               "benchmark_qualified": False, "scientific_claim_allowed": False,
               "remaining": "This single seed demonstrates sensitivity to reviewed consumer defects, not untrusted execution safety, full queue correctness or method efficacy."}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    log("summary", summary)
    print(json.dumps(summary, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
