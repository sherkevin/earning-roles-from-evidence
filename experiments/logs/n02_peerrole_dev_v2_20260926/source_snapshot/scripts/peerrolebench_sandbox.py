"""Bounded consumer RPC using pinned Anthropic sandbox-runtime on macOS.

Only public source and a public driver enter the worker. Expected values and
assertions remain in its parent. This is a non-adversarial development evaluator,
not a claim that Python instrumentation is tamper-proof against hostile code.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time

import psutil


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools/peerrole-runtime"
CLI = RUNTIME / "node_modules/@anthropic-ai/sandbox-runtime/dist/cli.js"
PYTHON = Path.home() / ".local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12"
MAX_LINE_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
RPC_SECONDS = 5
SESSION_SECONDS = 40
RSS_LIMIT_BYTES = 512 * 1024 * 1024


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SandboxedWorker:
    """A fresh, read-only source copy for each sealed evaluation.

    stdout/stderr are drained together without blocking readline(); partial
    lines, oversized output and timeouts are transport UNKNOWNs. No score or
    stderr is returned to the acting agent by this class.
    """

    def __init__(self, sources, evidence_dir, log, queue_name="TaskQueue", consumer_name="TaskConsumer",
                 *, worker_path=None):
        if sys.platform != "darwin":
            raise RuntimeError("This qualified adapter currently supports macOS only")
        if not CLI.is_file() or not PYTHON.is_file():
            raise RuntimeError("Install pinned runtime and the recorded Python before execution")
        manifest = json.loads((CLI.parent.parent / "package.json").read_text())
        if manifest["version"] != "0.0.77":
            raise RuntimeError("Unexpected sandbox-runtime version")
        self.log = log
        self.evidence = Path(evidence_dir)
        self.evidence.mkdir(parents=True, exist_ok=False)
        self.temp = tempfile.TemporaryDirectory(prefix="peerrole-worker-")
        self.base = Path(self.temp.name).resolve()
        self.source = self.base / "public"
        self.trusted = self.base / "driver"
        self.scratch = self.base / "scratch"
        for directory in (self.source, self.trusted, self.scratch):
            directory.mkdir()
        for name, contents in sources.items():
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or not name.startswith("mqueue/") or path.suffix != ".py":
                raise ValueError("Unexpected candidate source path")
            target = self.source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)
        worker_path = Path(worker_path or ROOT / "scripts/peerrolebench_consumer_worker.py")
        worker = self.trusted / "worker.py"
        launcher = self.trusted / "limits.py"
        shutil.copyfile(worker_path, worker)
        shutil.copyfile(ROOT / "scripts/peerrolebench_worker_limits.py", launcher)
        runtime_root = PYTHON.resolve().parent.parent
        settings = {
            "network": {"allowedDomains": [], "deniedDomains": [], "allowUnixSockets": [],
                        "allowLocalBinding": False},
            "filesystem": {
                "denyRead": ["/"],
                "allowRead": [str(self.source), str(self.trusted), str(self.scratch), str(runtime_root),
                              "/System", "/usr/lib", "/bin", "/dev/null", "/dev/urandom"],
                "allowWrite": [str(self.scratch)],
                "denyWrite": [str(self.source), str(self.trusted), str(runtime_root),
                              "/tmp/claude", "/private/tmp/claude"],
            },
            "allowAppleEvents": False,
            "enableWeakerNetworkIsolation": False,
            "enableWeakerNestedSandbox": False,
        }
        settings_path = self.evidence / "settings.json"
        settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node runtime unavailable")
        self.command = [node, str(CLI), "--settings", str(settings_path.resolve()), "--",
                        str(PYTHON.resolve()), "-I", "-B", str(launcher), str(worker),
                        str(self.source), queue_name, consumer_name]
        env = {"PATH": str(Path(node).parent) + ":/usr/bin:/bin", "LANG": "C",
               "CLAUDE_CODE_TMPDIR": str(self.scratch), "PEERROLE_SCRATCH": str(self.scratch)}
        metadata = {"command": self.command, "environment": env, "runtime_version": manifest["version"],
                    "runtime_lock_sha256": sha(RUNTIME / "package-lock.json"),
                    "worker_sha256": sha(worker), "limits_sha256": sha(launcher),
                    "sources": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sources.items()},
                    "rpc_timeout_seconds": RPC_SECONDS, "session_timeout_seconds": SESSION_SECONDS,
                    "max_response_line_bytes": MAX_LINE_BYTES, "max_total_output_bytes": MAX_OUTPUT_BYTES,
                    "rss_watchdog_bytes": RSS_LIMIT_BYTES, "rss_poll_seconds": 0.1,
                    "rss_limit_is_hard": False, "psutil_version": psutil.__version__,
                    "source_read_only": True, "same_process_instrumentation_tamper_proof": False}
        (self.evidence / "launch.json").write_text(json.dumps(metadata, indent=2) + "\n")
        self.log("sandbox_start", metadata)
        self.started = time.monotonic()
        self.proc = subprocess.Popen(self.command, cwd=self.source, env=env, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        self.log("sandbox_pid", {"pid": self.proc.pid, "process_group": self.proc.pid})
        self.selector = selectors.DefaultSelector()
        for stream, name in ((self.proc.stdout, "stdout"), (self.proc.stderr, "stderr")):
            os.set_blocking(stream.fileno(), False)
            self.selector.register(stream, selectors.EVENT_READ, name)
        os.set_blocking(self.proc.stdin.fileno(), False)
        self.buffer = bytearray()
        self.total_output = 0
        self.closed = False

    def _resource_check(self):
        try:
            parent = psutil.Process(self.proc.pid)
            processes = [parent, *parent.children(recursive=True)]
            rss = 0
            for process in processes:
                try:
                    rss += process.memory_info().rss
                except psutil.NoSuchProcess:
                    pass
            if rss > RSS_LIMIT_BYTES:
                self.log("resource_limit", {"tree_rss_bytes": rss, "cap_bytes": RSS_LIMIT_BYTES})
                os.killpg(self.proc.pid, signal.SIGKILL)
                raise RuntimeError("Worker process tree exceeded RSS watchdog")
        except psutil.NoSuchProcess:
            pass

    def request(self, payload):
        if self.closed:
            raise RuntimeError("Worker already closed")
        data = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
        if len(data) > 4096:
            raise ValueError("Public operation exceeds 4096-byte input cap")
        deadline = min(time.monotonic() + RPC_SECONDS, self.started + SESSION_SECONDS)
        self.log("worker_request", payload)
        try:
            count = os.write(self.proc.stdin.fileno(), data)
        except (BlockingIOError, BrokenPipeError) as exc:
            raise RuntimeError("Worker cannot accept a bounded request") from exc
        if count != len(data):
            raise RuntimeError("Partial worker request")
        while True:
            self._resource_check()
            if b"\n" in self.buffer:
                line, _, remainder = self.buffer.partition(b"\n")
                self.buffer = bytearray(remainder)
                if len(line) > MAX_LINE_BYTES:
                    raise ValueError("Worker response exceeds line cap")
                response = json.loads(line)
                if not isinstance(response, dict):
                    raise ValueError("Worker response must be an object")
                self.log("worker_response", response)
                return response
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Worker RPC/session deadline exceeded")
            events = self.selector.select(min(remaining, 0.1))
            if not events:
                continue
            for key, _ in events:
                chunk = os.read(key.fileobj.fileno(), 8192)
                if not chunk:
                    self.selector.unregister(key.fileobj)
                    if key.data == "stdout":
                        raise RuntimeError("Worker exited before a complete response")
                    continue
                self.total_output += len(chunk)
                if self.total_output > MAX_OUTPUT_BYTES:
                    raise ValueError("Worker total output cap exceeded")
                with (self.evidence / (key.data + ".bin")).open("ab") as stream:
                    stream.write(chunk)
                if key.data == "stdout":
                    self.buffer.extend(chunk)
                    if len(self.buffer) > MAX_LINE_BYTES:
                        raise ValueError("Worker response buffer cap exceeded")

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait(timeout=2)
        finally:
            # Candidate forks are prohibited by RLIMIT_NPROC. Kill remaining
            # wrapper descendants in the same process group as a final cleanup.
            live_group = []
            for process in psutil.process_iter(["pid", "status"]):
                try:
                    if (process.info["status"] != psutil.STATUS_ZOMBIE and
                            os.getpgid(process.pid) == self.proc.pid):
                        live_group.append(process.pid)
                except (ProcessLookupError, PermissionError, psutil.NoSuchProcess):
                    continue
            if live_group:
                try:
                    os.killpg(self.proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            self.log("sandbox_cleanup", {"live_group_before_final_kill": live_group})
            self.selector.close()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.log("sandbox_end", {"returncode": self.proc.returncode,
                                     "wall_seconds": time.monotonic() - self.started,
                                     "output_bytes": self.total_output})
            self.temp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
