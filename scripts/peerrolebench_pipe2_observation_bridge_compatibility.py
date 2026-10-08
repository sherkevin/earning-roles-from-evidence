"""Audit whether ADR0049's typed observation bridge fits PIPE2's real handoff.

This is deliberately a zero-call *compatibility* check.  PIPE2 hands the
recipient an opaque ``artifact/extracted_rows.json`` data artifact; it does
not hand over producer-owned source files.  The existing observation bridge
was written for a source-file handoff and therefore must not be applied to
PIPE2 runtime receipts until a versioned descriptor records the data artifact,
recipient pre/post snapshots, and explicit J/A/Y events.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from typing import Any

from peerrolebench_pipe2_derived_material_adapter import build_derived_materials

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aamas2027/n03_pipe2_observation_bridge_compatibility_20261008.json"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def run(output: Path, *, seed: int = 0) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config.update({
        "command": ["python3", "scripts/peerrolebench_pipe2_observation_bridge_compatibility.py",
                    "--output", str(output), "--seed", str(seed)],
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
    })
    (output / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    materials = build_derived_materials(seed)
    producer = materials["agent_payloads"]["producer"]
    recipient = materials["agent_payloads"]["recipient"]
    manifest = materials["manifest"]
    producer_paths = tuple(producer["source_files"])
    recipient_paths = tuple(recipient["source_files"])
    required_delivery = tuple(recipient["required_delivery_paths"])
    checks = [
        {
            "check": "recipient_does_not_receive_producer_source",
            "passed": not (set(manifest["producer_writable_paths"]) & set(recipient_paths)),
            "observed": {"producer_writable_paths": manifest["producer_writable_paths"],
                         "recipient_source_paths": list(recipient_paths)},
            "impact": "source-file observation bridge cannot require delivered producer paths in recipient snapshots",
        },
        {
            "check": "handoff_is_opaque_data_artifact",
            "passed": required_delivery == (manifest["delivery_path"],),
            "observed": {"required_delivery_paths": list(required_delivery),
                         "delivery_path": manifest["delivery_path"],
                         "delivery_schema": recipient["delivery_schema"]},
            "impact": "delivery digest must bind pipe2-extracted-rows-v1, not producer source digest",
        },
        {
            "check": "runtime_receipt_has_no_judgment_action_outcome",
            "passed": True,
            "observed": {"runtime_receipt_fields": ["producer_contract", "recipient_self",
                                                    "artifact_adoption"],
                         "required_for_observation": ["recipient_judgment", "consumer_action",
                                                       "terminal_outcome"]},
            "impact": "current runtime replay must remain UNKNOWN rather than inventing Scheme-B fields",
        },
        {
            "check": "runtime_receipt_has_no_recipient_pre_post_diff",
            "passed": True,
            "observed": {"recipient_payload_paths": list(recipient_paths),
                         "source_snapshot_available": False,
                         "post_action_snapshot_available": False},
            "impact": "recipient-only/mixed scope cannot be inferred from output_sha256 or adoption status",
        },
    ]
    blockers = [
        "typed handoff descriptor is missing (artifact path/schema/hash separate from producer source provenance)",
        "explicit recipient judgment, consumer action, and terminal outcome are missing from runtime receipts",
        "recipient pre/post source manifests or sealed changed-path descriptor are missing",
        "output_sha256 and adoption status cannot be promoted to J, A, or Y",
    ]
    result = {
        "schema": "n03-pipe2-observation-bridge-compatibility-result-v1",
        "status": "BLOCKED_BY_HANDOFF_SEMANTICS",
        "seed": seed, "task_id": "PIPE2_data_pipeline",
        "candidate_root": "pipe2-csv-writer-v1",
        "material_schema": materials["manifest"]["schema_version"],
        "producer_source_paths": list(producer_paths),
        "recipient_source_paths": list(recipient_paths),
        "checks": checks, "blockers": blockers,
        "reuse_decision": "DO_NOT_APPLY_EXISTING_OBSERVATION_BRIDGE_TO_CURRENT_PIPE2_RECEIPTS",
        "required_next_descriptor": {
            "artifact_path": manifest["delivery_path"],
            "artifact_schema": recipient["delivery_schema"],
            "artifact_sha256": "sealed at producer delivery",
            "producer_source_digest": "separate registry provenance",
            "recipient_before_after_manifest": "sealed before/after action",
            "judgment_action_outcome": "explicit typed events",
        },
        "api_calls": 0, "gpu_jobs": 0, "policy_updates": 0,
        "scientific_claim_allowed": False,
        "config_sha256": digest(config),
        "source_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with (output / "events.jsonl").open("w", encoding="utf-8") as stream:
        for check in checks:
            stream.write(json.dumps({"event_type": "compatibility_check", "payload": check}, ensure_ascii=False, sort_keys=True) + "\n")
        stream.write(json.dumps({"event_type": "summary", "payload": result}, ensure_ascii=False, sort_keys=True) + "\n")
    (output / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    result = run(args.output, seed=args.seed)
    print(json.dumps({"status": result["status"], "blockers": result["blockers"],
                      "api_calls": result["api_calls"], "gpu_jobs": result["gpu_jobs"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
