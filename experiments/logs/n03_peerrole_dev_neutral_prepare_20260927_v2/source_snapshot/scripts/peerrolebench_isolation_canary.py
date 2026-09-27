"""Check a local macOS sandbox with harmless canaries, never model code.

This is an engineering probe, not a portable sandbox implementation or proof
against all escapes. In particular, it cannot protect a scorer's in-process
Python objects from candidate code. All attempted accesses target files and a
loopback socket created by this program, not user credentials or remote hosts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import sysconfig
import tempfile
import time


PROBE = r'''
import json, os, socket, subprocess, sys
from pathlib import Path
public, private, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
results = {}
def attempt(name, operation):
    try:
        operation()
        results[name] = {"allowed": True}
    except Exception as exc:
        results[name] = {"allowed": False, "error": type(exc).__name__, "errno": getattr(exc, "errno", None)}
attempt("public_read", lambda: Path(public, "input.txt").read_text())
attempt("public_write", lambda: Path(public, "output.txt").write_text("canary-output"))
attempt("private_read", lambda: Path(private, "expected.txt").read_text())
attempt("private_write", lambda: Path(private, "output.txt").write_text("canary-output"))
attempt("symlink_read", lambda: Path(public, "escape.txt").read_text())
def network():
    with socket.create_connection(("127.0.0.1", port), timeout=1):
        pass
attempt("loopback_connect", network)
child = subprocess.run([sys.executable, "-I", "-B", "-c",
    "from pathlib import Path; import sys; Path(sys.argv[1]).read_text()",
    str(Path(private, "expected.txt"))], capture_output=True, text=True, timeout=3)
results["child_private_read"] = {"allowed": child.returncode == 0, "returncode": child.returncode,
                                  "denied_as_permission_error": "PermissionError" in child.stderr}
print(json.dumps(results, sort_keys=True))
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    raw = args.output / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a") as stream:
            stream.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload}) + "\n")

    config = {"purpose": "harmless engineering isolation canary", "platform": platform.platform(),
              "python": sys.version, "python_executable": sys.executable,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "command": sys.argv, "llm_calls": 0, "gpu_jobs": 0,
              "candidate_code_executed": False, "scientific_claim_allowed": False,
              "process_timeout_seconds": 8, "same_process_gold_protected": False}
    (args.output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    log("config", config)
    with tempfile.TemporaryDirectory(prefix="peerrole-canary-") as temp, socket.socket() as listener:
        base = Path(temp).resolve()
        public, private = base / "public", base / "private"
        public.mkdir()
        private.mkdir()
        (public / "input.txt").write_text("public-input")
        (private / "expected.txt").write_text("private-canary-not-a-credential")
        (public / "escape.txt").symlink_to(private / "expected.txt")
        listener.bind(("127.0.0.1", 0))
        listener.listen(4)
        port = listener.getsockname()[1]
        runtime_roots = sorted({str(Path(sysconfig.get_path("stdlib")).resolve().parent),
                                str(Path(sys.base_prefix).resolve()),
                                str(Path(sys.executable).resolve().parent),
                                "/System", "/usr/lib", "/Library/Apple", "/private/preboot"})
        reads = "\n".join("    (subpath " + json.dumps(path) + ")" for path in runtime_roots + [str(public)])
        profile = ('(version 1)\n(deny default)\n(allow process*)\n(allow sysctl-read)\n'
                   '(allow file-read-metadata)\n'
                   # Upstream sandbox-runtime's allow-read regression documents
                   # dyld requiring access to the root vnode (not its subtree).
                   '(allow file-read* (literal "/"))\n'
                   '(allow file-map-executable\n' + reads + ')\n'
                   '(allow file-read*\n' + reads + '\n    (literal "/dev/null") (literal "/dev/urandom"))\n'
                   '(allow file-write* (subpath ' + json.dumps(str(public)) + ') (literal "/dev/null"))\n')
        (args.output / "profile.sb").write_text(profile)
        # macOS checks the invoked path as well as its target. Invoke the
        # allowlisted runtime directly instead of a CommandLineTools symlink.
        probe_args = [str(Path(sys.executable).resolve()), "-I", "-B", "-c", PROBE,
                      str(public), str(private), str(port)]
        clean_env = {"PATH": "/usr/bin:/bin", "LANG": "C", "TMPDIR": str(public)}
        records = {}
        for name, command in [("unsandboxed_control", probe_args),
                              ("sandboxed", ["/usr/bin/sandbox-exec", "-p", profile, *probe_args])]:
            started = time.monotonic()
            log("process_start", {"name": name, "command": command, "environment": clean_env})
            try:
                proc = subprocess.run(command, capture_output=True, text=True, env=clean_env,
                                      cwd=public, timeout=8)
                record = {"name": name, "exit_code": proc.returncode, "stdout": proc.stdout,
                          "stderr": proc.stderr, "wall_seconds": time.monotonic() - started}
                if proc.returncode == 0:
                    record["checks"] = json.loads(proc.stdout)
            except Exception as exc:
                record = {"name": name, "error": repr(exc), "wall_seconds": time.monotonic() - started}
            records[name] = record
            log("process_result", record)
        control, checked = records["unsandboxed_control"].get("checks", {}), records["sandboxed"].get("checks", {})
        public_checks = ("public_read", "public_write")
        denied_checks = ("private_read", "private_write", "symlink_read", "loopback_connect", "child_private_read")
        passed = (all(control.get(k, {}).get("allowed") is True for k in public_checks + denied_checks)
                  and all(checked.get(k, {}).get("allowed") is True for k in public_checks)
                  and all(checked.get(k, {}).get("allowed") is False for k in denied_checks))
        result = {"canary_contract_passed": passed, "production_sandbox_qualified": False,
                  "same_process_gold_protected": False, "scientific_claim_allowed": False,
                  "records": records, "boundary": "This probe checks listed accesses only; native pytest shares candidate and test memory."}
        (args.output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
        log("summary", {k: v for k, v in result.items() if k != "records"})
        print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
