"""Structured zero-call qualification for the event-time interleaving seam."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_event_time_interleaving import (  # noqa: E402
    qualify_event_time_interleaving,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out_dir: Path, *, experiment_id: str = "n03_event_time_interleaving_20260928_v1") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "experiment_id": experiment_id,
        "kind": "zero_call_event_time_interleaving_qualification",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {
                "runner": _sha256(ROOT / "scripts/peerrolebench_event_time_interleaving.py"),
                "qualification": _sha256(Path(__file__)),
            },
        },
        "schedule": {"decision_indices": [0, 2, 4], "arrival_conditions": [1, 3], "seed": 41},
        "policies": ["contextual_trust", "no_update"],
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    # The configuration is persisted before executing the qualification.
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    try:
        result = qualify_event_time_interleaving()
        status = result["status"]
        error = None
    except Exception as exc:  # preserve a structured failure instead of hiding it
        result = {"status": "FAILED_OFFLINE", "checks": {}, "runs": {}}
        status = "FAILED_OFFLINE"
        error = {"type": type(exc).__name__, "message": str(exc)}
    raw_lines = []
    for run_name, run in sorted(result.get("runs", {}).items()):
        for ordinal, trace in enumerate(run.get("traces", [])):
            raw_lines.append({
                "event_type": "decision_trace",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "experiment_id": experiment_id,
                "run": run_name,
                "ordinal": ordinal,
                "payload": trace,
            })
    raw_lines.append({
        "event_type": "qualification_result",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": experiment_id,
        "status": status,
        "checks": result.get("checks", {}),
        "error": error,
    })
    (out_dir / "raw.jsonl").write_text(
        "".join(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n" for line in raw_lines),
        encoding="utf-8",
    )
    summary = {
        "experiment_id": experiment_id,
        "status": status,
        "passed": status == "QUALIFIED_OFFLINE",
        "checks": result.get("checks", {}),
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "failure": error,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "event-time protocol seam only; no benchmark efficacy, real API, or role-learning claim",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--experiment-id", default="n03_event_time_interleaving_20260928_v1")
    args = parser.parse_args()
    result = run(args.out_dir, experiment_id=args.experiment_id)
    print(json.dumps({"status": result["status"], "passed": result["passed"],
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
