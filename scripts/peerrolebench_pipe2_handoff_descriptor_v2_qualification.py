"""Zero-call qualification for the versioned PIPE2 handoff descriptor v2.

The runner uses the actual public material adapter and delivery artifact shape,
then exercises only typed descriptor construction with an explicitly marked
synthetic event-reference fixture.  It must never be read as a benchmark or
LLM result: no candidate code, API, policy, native grader, or GPU is run.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

from peerrolebench_pipe2_derived_material_adapter import build_derived_materials
from peerrolebench_pipe2_material_adapter_v2 import validate_extracted_rows
from peerrolebench_pipe2_handoff_descriptor_v2 import (
    DELIVERY_PATH, DELIVERY_SCHEMA, SCHEMA, canonical_digest,
    make_descriptor_from_snapshots,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER_VERSION = "pipe2-typed-handoff-v2-qualification-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_fixture(values: dict[str, object]) -> dict[str, dict[str, object]]:
    delivery = {"delivery_id": values["delivery_id"]}
    judgment = {"judgment_id": values["judgment_id"], "delivery_id": values["delivery_id"],
                "decision": values["judgment"]}
    action = {"action_id": values["action_id"], "delivery_id": values["delivery_id"],
              "action": values["action"]}
    outcome = {"outcome_id": values["outcome_id"], "delivery_id": values["delivery_id"],
               "success": values["outcome_status"] == "PASS"}
    return {
        "delivery": {"event_type": "producer_delivery", "event_index": 2,
                     "record_hash": canonical_digest(delivery), "payload": delivery},
        "judgment": {"event_type": "recipient_judgment", "event_index": 3,
                      "record_hash": canonical_digest(judgment), "payload": judgment},
        "action": {"event_type": "consumer_action", "event_index": 4,
                    "record_hash": canonical_digest(action), "payload": action},
        "outcome": {"event_type": "terminal_outcome", "event_index": 5,
                     "record_hash": canonical_digest(outcome), "payload": outcome},
    }


def log_event(raw: Path, event_type: str, payload: object) -> None:
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event_type": event_type, "payload": payload},
                                ensure_ascii=False) + "\n")
        handle.flush()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    raw = out / "events.jsonl"
    config = {
        "runner_version": RUNNER_VERSION, "descriptor_schema": SCHEMA,
        "task_id": "PIPE2_data_pipeline", "seed": 0,
        "python": sys.version, "platform": platform.platform(), "command": sys.argv,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runner_sha256": sha(Path(__file__).resolve()),
        "api_calls": 0, "gpu_jobs": 0, "policy_updates": 0,
        "candidate_code_executed": False, "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "fixture_event_kind": "synthetic_contract_fixture_only",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log_event(raw, "config", config)
    checks: dict[str, object] = {}
    try:
        materials = build_derived_materials(0)
        producer = materials["agent_payloads"]["producer"]
        recipient = materials["agent_payloads"]["recipient"]
        source = producer["source_files"]["data/source.csv"]
        import csv
        import io
        reader = csv.DictReader(io.StringIO(source, newline=""))
        artifact = validate_extracted_rows(list(reader), columns=tuple(reader.fieldnames or ()))
        checks["actual_material_visibility"] = {
            "producer_has_extract": "pipeline/extract.py" in producer["source_files"],
            "recipient_has_no_extract": "pipeline/extract.py" not in recipient["source_files"],
            "recipient_required_delivery": recipient["required_delivery_paths"] == [DELIVERY_PATH],
            "delivery_schema": artifact["schema"],
            "delivery_artifact_sha256": artifact["artifact_sha256"],
        }
        allowed_paths = tuple(sorted(recipient["source_files"]))
        before = {path: recipient["source_files"][path] for path in allowed_paths}
        after = dict(before)
        after["pipeline/transform.py"] += "\n# explicit recipient action fixture\n"
        values = {
            "delivery_id": "fixture-delivery-0", "judgment_id": "fixture-judgment-0",
            "action_id": "fixture-action-0", "outcome_id": "fixture-outcome-0",
            "judgment": "accept", "action": "repair", "outcome_status": "PASS",
        }
        base = {
            "task_id": "PIPE2_data_pipeline", "source_task_index": 0,
            "candidate_key": "producer-a@v1",
            "candidate_source_digest": canonical_digest({"pipeline/extract.py": producer["source_files"]["pipeline/extract.py"]}),
            "delivery_id": values["delivery_id"], "delivery_path": DELIVERY_PATH,
            "delivery_schema": DELIVERY_SCHEMA, "delivery_artifact_sha256": artifact["artifact_sha256"],
            "producer_contract_digest": canonical_digest(materials["manifest"]),
            "judgment": values["judgment"], "action": values["action"], "used_artifact": True,
            "outcome_status": values["outcome_status"], "delivery_event_index": 2,
            "judgment_event_index": 3, "action_event_index": 4, "outcome_event_index": 5,
            "judgment_id": values["judgment_id"], "action_id": values["action_id"],
            "outcome_id": values["outcome_id"], "target_task_index": 1,
            "judgment_record_hash": canonical_digest({"judgment_id": values["judgment_id"], "delivery_id": values["delivery_id"], "decision": values["judgment"]}),
            "action_record_hash": canonical_digest({"action_id": values["action_id"], "delivery_id": values["delivery_id"], "action": values["action"]}),
            "outcome_record_hash": canonical_digest({"outcome_id": values["outcome_id"], "delivery_id": values["delivery_id"], "success": True}),
            "source_read_cut": 6, "observation_available_index": 6,
        }
        descriptor = make_descriptor_from_snapshots(
            recipient_before=before, recipient_after=after,
            recipient_allowed_paths=allowed_paths, event_records=event_fixture(values), **base)
        checks["explicit_event_binding_and_snapshot_digest"] = {
            "status": "PASS", "descriptor_digest": descriptor.descriptor_digest,
            "changed_paths_digest": descriptor.recipient_changed_paths_digest,
            "mismatch_retained": descriptor.judgment == "accept" and descriptor.action == "repair",
        }
        try:
            make_descriptor_from_snapshots(
                recipient_before=before, recipient_after=after,
                recipient_allowed_paths=allowed_paths, event_records={}, **base)
        except ValueError as exc:
            checks["missing_judgment_action_outcome_fail_closed"] = {
                "status": "PASS", "error_type": type(exc).__name__, "error": str(exc)}
        else:
            checks["missing_judgment_action_outcome_fail_closed"] = {"status": "FAIL"}
        try:
            make_descriptor_from_snapshots(
                recipient_before={DELIVERY_PATH: "opaque"}, recipient_after={DELIVERY_PATH: "opaque"},
                recipient_allowed_paths=(DELIVERY_PATH,), event_records=event_fixture(values), **base)
        except ValueError as exc:
            checks["opaque_artifact_not_source_manifest_fail_closed"] = {
                "status": "PASS", "error_type": type(exc).__name__, "error": str(exc)}
        else:
            checks["opaque_artifact_not_source_manifest_fail_closed"] = {"status": "FAIL"}
        summary = {
            **config, "status": "QUALIFIED_OFFLINE" if all(
                value is True or (isinstance(value, dict) and value.get("status") == "PASS")
                for value in [
                    checks["actual_material_visibility"]["producer_has_extract"],
                    checks["actual_material_visibility"]["recipient_has_no_extract"],
                    checks["actual_material_visibility"]["recipient_required_delivery"],
                    checks["explicit_event_binding_and_snapshot_digest"],
                    checks["missing_judgment_action_outcome_fail_closed"],
                    checks["opaque_artifact_not_source_manifest_fail_closed"],
                ]) else "FAILED_OFFLINE",
            "checks": checks, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
            "interpretation": "Actual PIPE2 public material visibility and delivery schema were checked; the event records are synthetic contract fixtures only. No benchmark, efficacy, or selector claim.",
        }
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
        log_event(raw, "summary", summary)
        print(json.dumps({"status": summary["status"], "api_calls": 0,
                          "gpu_jobs": 0, "scientific_claim_allowed": False}, indent=2))
        return 0 if summary["status"] == "QUALIFIED_OFFLINE" else 1
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        summary = {**config, "status": "FAILED_OFFLINE", "checks": checks,
                   "error": error, "ended_at_utc": datetime.now(timezone.utc).isoformat()}
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
        log_event(raw, "failure", error)
        print(json.dumps({"status": "FAILED_OFFLINE", "error": error}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
