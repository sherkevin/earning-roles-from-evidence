"""One bounded qualification of the actual runtime, without LLM or GPU calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import traceback

from peerrolebench_consumer_checks import run_checks
from peerrolebench_consumer_qualification import ARMS
from peerrolebench_sandbox import ROOT, SandboxedWorker
from peerrolebench_task_contract import TEAMBENCH, TEAMBENCH_SOURCE_COMMIT, load_generated_task
from peerrolebench_tb_vertical_slice import write_dist1_repair


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    raw = out / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a") as stream:
            stream.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload}) + "\n")

    names = [Path(__file__).name, "peerrolebench_sandbox.py", "peerrolebench_worker_limits.py",
             "peerrolebench_runtime_probe_worker.py", "peerrolebench_consumer_worker.py",
             "peerrolebench_consumer_checks.py", "peerrolebench_task_contract.py",
             "peerrolebench_tb_vertical_slice.py"]
    config = {"purpose": "N01 actual-boundary canary and known consumer mutations",
              "command": sys.argv, "python": sys.version, "platform": platform.platform(),
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "working_tree_dirty": True, "source_sha256": {name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest() for name in names},
              "source_pin": TEAMBENCH_SOURCE_COMMIT, "task": "DIST1_queue_race", "seed": 0,
              "arms": ARMS, "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
              "scientific_claim_allowed": False,
              "qualification_scope": "listed engineering boundaries; no claim of adversarial scoring security",
              "checks": ["public_read", "scratch_write", "source_write_denied", "private_read_denied",
                         "private_write_denied", "symlink_denied", "parent_scorer_denied",
                         "network_denied", "fork_denied", "memory_limited", "partial_line_timeout", "output_cap"]}
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    log("config", config)
    results = {"canaries": {}, "arms": []}
    try:
        actual_pin = subprocess.check_output(["git", "-C", str(TEAMBENCH), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(TEAMBENCH), "status", "--porcelain"], text=True)
        if actual_pin != TEAMBENCH_SOURCE_COMMIT or dirty:
            raise RuntimeError("Pinned task source mismatch")
        probe = ROOT / "scripts/peerrolebench_runtime_probe_worker.py"
        with tempfile.TemporaryDirectory(prefix="peerrole-private-") as tmp, socket.socket() as listener:
            private = Path(tmp).resolve() / "expected.txt"
            private.write_text("harmless-private-canary")
            listener.bind(("127.0.0.1", 0))
            listener.listen(4)
            with SandboxedWorker({"mqueue/input.py": "# public input\n"}, out / "canary", log, worker_path=probe) as worker:
                (worker.source / "escape.py").symlink_to(private)
                probes = {
                    "public_read": ({"op": "read", "path": str(worker.source / "mqueue/input.py")}, True),
                    "scratch_write": ({"op": "write", "path": str(worker.scratch / "output")}, True),
                    "source_write_denied": ({"op": "write", "path": str(worker.source / "mqueue/input.py")}, False),
                    "private_read_denied": ({"op": "read", "path": str(private)}, False),
                    "private_write_denied": ({"op": "write", "path": str(private)}, False),
                    "symlink_denied": ({"op": "read", "path": str(worker.source / "escape.py")}, False),
                    "parent_scorer_denied": ({"op": "read", "path": str(ROOT / "scripts/peerrolebench_consumer_checks.py")}, False),
                    "network_denied": ({"op": "network", "port": listener.getsockname()[1]}, False),
                    "fork_denied": ({"op": "fork"}, False),
                }
                for name, (request, expected) in probes.items():
                    observed = worker.request(request)
                    denied_types = {"BlockingIOError", "PermissionError"} if name == "fork_denied" else {"PermissionError"}
                    passed = observed.get("ok") is expected and (expected or observed.get("error_type") in denied_types)
                    results["canaries"][name] = {"passed": passed, "observed": observed}
                    log("canary_result", {"name": name, **results["canaries"][name]})
            for op, name, error in [("partial_line", "partial_line_timeout", TimeoutError),
                                    ("flood", "output_cap", ValueError),
                                    ("memory", "memory_limited", RuntimeError)]:
                with SandboxedWorker({}, out / name, log, worker_path=probe) as worker:
                    try:
                        worker.request({"op": op})
                        result = {"passed": False, "reason": "Unbounded operation returned"}
                    except (TimeoutError, ValueError, RuntimeError) as exc:
                        passed = type(exc) is error and (op != "memory" or "RSS watchdog" in str(exc))
                        result = {"passed": passed, "error": repr(exc)}
                    results["canaries"][name] = result
                    log("canary_result", {"name": name, **result})
        if not all(item["passed"] for item in results["canaries"].values()):
            raise RuntimeError("Isolation canary failed; do not execute candidate fixtures")
        generated = load_generated_task("DIST1_queue_race", 0)
        with tempfile.TemporaryDirectory(prefix="peerrole-fixed-") as tmp:
            fixture = Path(tmp)
            (fixture / "mqueue").mkdir()
            for name, text in generated.workspace_files.items():
                if name.startswith("mqueue/"):
                    (fixture / name).write_text(text)
            write_dist1_repair(fixture)
            fixed = {str(p.relative_to(fixture)): p.read_text() for p in fixture.rglob("*.py")}
            for arm in ARMS:
                sources = dict(fixed)
                consumer = sources["mqueue/consumer.py"]
                if arm == "original_consumer":
                    consumer = generated.workspace_files["mqueue/consumer.py"]
                elif arm == "no_ack":
                    consumer = consumer.replace("        self._queue.ack(receipt)", "        pass  # missing ack")
                elif arm == "no_nack":
                    consumer = consumer.replace("            self._queue.nack(receipt)", "            pass  # missing nack")
                elif arm == "drops_falsy":
                    consumer = consumer.replace("if message is None or receipt is None:", "if not message or receipt is None:")
                sources["mqueue/consumer.py"] = consumer
                with SandboxedWorker(sources, out / arm, log) as worker:
                    result = run_checks(worker.request)
                result["arm"] = arm
                results["arms"].append(result)
                log("arm_result", result)
    except Exception as exc:
        results["error"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        log("qualification_failure", results["error"])
    canaries_pass = (set(results["canaries"]) == set(config["checks"]) and all(r["passed"] for r in results["canaries"].values()))
    arms = results["arms"]
    mutation_pass = (len(arms) == len(ARMS) and arms[0]["status"] == "PASS" and
                     all(item["observed_behavioral_failure"] for item in arms[1:]))
    results.update({"listed_runtime_checks_passed": canaries_pass, "fixture_discrimination_passed": mutation_pass,
                    "qualified_for_listed_development_checks": canaries_pass and mutation_pass,
                    "strict_N01_gate_passed": False, "benchmark_qualified": False,
                    "scientific_claim_allowed": False, "native_score_available": False})
    (out / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
    log("summary", results)
    print(json.dumps({k: v for k, v in results.items() if k not in {"canaries", "arms"}}, indent=2))
    return 0 if results["qualified_for_listed_development_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
