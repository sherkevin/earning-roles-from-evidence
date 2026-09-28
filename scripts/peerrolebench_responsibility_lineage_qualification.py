"""Qualify strict v3 feedback sidecar responsibility lineage without APIs."""

from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import TerminalOnlyPolicy  # noqa: E402
from peerrolebench_policy_sidecar import LINEAGE_SIDECAR_VERSION  # noqa: E402
from peerrolebench_policy_sidecar_replay import SidecarRow, replay_policy_sidecars  # noqa: E402
from peerrolebench_policy_sidecar_stream_qualification import (  # noqa: E402
    ARTIFACT, canonical_ledger, manifest_for, sidecars,
)


def _lineage_rows(events: list[dict]) -> dict[str, SidecarRow]:
    base = sidecars(events)
    delivery = next(row for row in events if row["event_type"] == "producer_delivery")
    action = next(row for row in events if row["event_type"] == "consumer_action")
    rows: dict[str, SidecarRow] = {}
    for name, row in base.items():
        if name == "selection":
            rows[name] = row
            continue
        value = replace(
            row.sidecar,
            sidecar_version=LINEAGE_SIDECAR_VERSION,
            artifact_sha256=ARTIFACT,
            delivery_record_hash=delivery["record_hash"],
            action_id="action-0",
            action_record_hash=action["record_hash"],
            action="repair" if name == "outcome" else row.sidecar.action,
        )
        rows[name] = SidecarRow(value, row.ledger_record, value.sidecar_digest)
    return rows


def _result(events: list[dict], rows: dict[str, SidecarRow], *, mutate: str | None = None) -> dict:
    selected = [rows["selection"], rows["judgment"], rows["outcome"]]
    if mutate == "wrong_delivery":
        wrong = replace(rows["outcome"].sidecar, delivery_id="delivery-other")
        selected[-1] = SidecarRow(wrong, rows["outcome"].ledger_record, wrong.sidecar_digest)
    elif mutate == "wrong_artifact":
        wrong = replace(rows["outcome"].sidecar, artifact_sha256="c" * 64)
        selected[-1] = SidecarRow(wrong, rows["outcome"].ledger_record, wrong.sidecar_digest)
    elif mutate == "wrong_action":
        wrong = replace(rows["outcome"].sidecar, action="use")
        selected[-1] = SidecarRow(wrong, rows["outcome"].ledger_record, wrong.sidecar_digest)
    elif mutate == "wrong_producer":
        wrong = replace(rows["outcome"].sidecar, producer_id="peer-c")
        selected[-1] = SidecarRow(wrong, rows["outcome"].ledger_record, wrong.sidecar_digest)
    manifest = manifest_for(selected)
    return replay_policy_sidecars(
        events, selected, TerminalOnlyPolicy, manifest,
        require_responsibility_lineage=True,
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": "n03_responsibility_lineage_qualification_20260928",
        "kind": "zero_api_sidecar_lineage_qualification_not_scientific_benchmark",
        "runtime": {"started_at_utc": started, "python": platform.python_version(), "git_commit": commit},
        "fixture": "in_memory_complete_peer_role_ledger_v1",
        "sidecar_version": LINEAGE_SIDECAR_VERSION,
        "cases": ["canonical", "wrong_delivery", "wrong_artifact", "wrong_action", "wrong_producer"],
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"
    events = canonical_ledger()
    rows = _lineage_rows(events)
    cases = []
    for name, mutate, expected in [
        ("canonical", None, "PASS"),
        ("wrong_delivery", "wrong_delivery", "INVALID"),
        ("wrong_artifact", "wrong_artifact", "INVALID"),
        ("wrong_action", "wrong_action", "INVALID"),
        ("wrong_producer", "wrong_producer", "INVALID"),
    ]:
        result = _result(events, rows, mutate=mutate)
        case = {
            "case": name, "status": result["status"], "update_count": result["update_count"],
            "expected_status": expected,
            "expectation_met": result["status"] == expected and (
                result["update_count"] == 1 if mutate is None else result["update_count"] == 0
            ),
            "error": result.get("error"),
        }
        cases.append(case)
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": "lineage_case", "payload": case}, sort_keys=True) + "\n")
    summary = {
        "experiment_id": config["experiment_id"], "passed": all(case["expectation_met"] for case in cases),
        "case_count": len(cases), "cases": cases, "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({key: result[key] for key in ("passed", "case_count", "real_api_calls",
                                                   "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
