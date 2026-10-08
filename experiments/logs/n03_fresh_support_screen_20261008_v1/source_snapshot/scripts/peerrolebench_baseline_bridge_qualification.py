"""Run the no-fabrication ledger-to-policy bridge audit with full logs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess

from peerrolebench_baseline_bridge_audit import _records, audit_records


def run(ledger: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    source = json.loads(ledger.read_text(encoding="utf-8"))
    records = _records(source)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": "n03_baseline_bridge_audit_20260928",
        "kind": "engineering_qualification_not_scientific_benchmark",
        "ledger": str(ledger),
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "git_commit": commit},
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for index, record in enumerate(records):
            handle.write(json.dumps({"index": index, "record": record}, ensure_ascii=False, sort_keys=True) + "\n")
    result = audit_records(records)
    summary = {
        "experiment_id": config["experiment_id"],
        "source_commit": commit,
        "audit": result,
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.ledger, args.out_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # A refusal is the expected result for the current historical ledger; the
    # qualification itself succeeds if the refusal is explicit and complete.
    return 0 if result["audit"]["status"] in {"MAPPABLE", "NOT_MAPPABLE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
