"""Record a reproducible zero-call qualification for the history binding seam."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VERSION = "peer-history-binding-qualification-v1"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    command = [sys.executable, "-m", "pytest", "-q",
               "tests/test_peerrolebench_peer_history_binding.py",
               "tests/test_peerrolebench_peer_history.py"]
    config = {
        "qualification_version": VERSION,
        "command": command,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version,
        "platform": platform.platform(),
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    raw = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": "focused_test_run",
        "payload": {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr},
    }
    (out / "raw.jsonl").write_text(json.dumps(raw, ensure_ascii=False) + "\n")
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if result.returncode == 0 else "FAILED_OFFLINE",
        "focused_tests": 10,
        "passed": result.returncode == 0,
        "interpretation": "Canonical source-to-target binding and history judgment-label checks only; no API/GPU/benchmark/effect claim.",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: summary[key] for key in ("status", "focused_tests", "llm_calls", "gpu_jobs")}, ensure_ascii=False))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
