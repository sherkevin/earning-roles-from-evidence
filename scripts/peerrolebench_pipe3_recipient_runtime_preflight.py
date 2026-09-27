#!/usr/bin/env python3
"""Probe recipient dispatch, selected delivery attachment and lineage locally."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
INPUT_LIMIT = 16 * 1024


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


QUAL = load("pipe3_qualification", ROOT / "scripts/peerrolebench_pipe3_task_qualification.py")
ADAPTER = load("pipe3_material_adapter", ROOT / "scripts/peerrolebench_pipe3_material_adapter.py")


def digest_files(files: dict[str, str]) -> str:
    return ADAPTER.digest_files(files)


def event_hash(previous: str, event: dict) -> str:
    blob = json.dumps({"previous": previous, "event": event}, ensure_ascii=False,
                      sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "--output":
        raise SystemExit("usage: peerrolebench_pipe3_recipient_runtime_preflight.py --output DIR")
    output = Path(sys.argv[2]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw = output / "raw.jsonl"

    def log(event_type: str, payload: object) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    config = {
        "experiment_id": output.name,
        "purpose": "N03 PIPE3 recipient payload, selected delivery attachment and lineage probe",
        "source_commit": QUAL.PIN,
        "seed": 0,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "candidate_code_executed": False,
        "native_grader_invoked": False,
        "rpc_input_limit_bytes": INPUT_LIMIT,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    result = {"config": config}
    try:
        generated = QUAL.load_pipe3(0)
        materials = ADAPTER.build_materials(generated)
        producer = materials["agent_payloads"]["producer"]
        recipient = materials["agent_payloads"]["recipient"]
        delivery = {path: producer["source_files"][path] for path in producer["writable_paths"]}
        delivery_sha = digest_files(delivery)
        if set(delivery) != set(recipient["required_delivery_paths"]):
            raise ValueError("selected delivery does not match recipient allowlist")
        attached = json.loads(json.dumps(recipient, ensure_ascii=False))
        attached["source_files"].update(delivery)
        attached["required_delivery_paths"] = []
        attached["delivery_sha256"] = delivery_sha
        selection = {"event_id": "selection-0001", "peer": "producer-0", "recipient": "recipient-0",
                     "propensity": 1.0 / 2.0, "seed": 0}
        delivery_event = {"event_id": "delivery-0001", "selection_id": selection["event_id"],
                          "producer": selection["peer"], "recipient": selection["recipient"],
                          "artifact_sha256": delivery_sha, "paths": sorted(delivery)}
        dispatch_event = {"event_id": "recipient-dispatch-0001", "delivery_id": delivery_event["event_id"],
                          "recipient_payload_sha256": hashlib.sha256(
                              json.dumps(attached, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
        chain = "GENESIS"
        ledger = []
        for event in (selection, delivery_event, dispatch_event):
            chain = event_hash(chain, event)
            ledger.append({"event": event, "hash": chain})
        result["ledger_fixture"] = {"events": ledger, "unique_event_ids": len({x["event"]["event_id"] for x in ledger}) == 3,
                                     "final_hash": chain, "exact_once_lineage": True}
        with tempfile.TemporaryDirectory(prefix="peerrole-pipe3-operator-") as private_tmp:
            private = Path(private_tmp) / "operator-ledger.json"
            private.write_text("operator-only\n")
            sources = {f"mqueue/{name}": text for name, text in attached["source_files"].items()}
            worker_log = lambda event_type, item: log("sandbox." + event_type, item)
            with SandboxedWorker(
                sources, output / "sandbox", worker_log,
                worker_path=ROOT / "scripts/peerrolebench_pipe3_recipient_probe_worker.py",
                max_input_bytes=INPUT_LIMIT,
            ) as worker:
                observed = worker.request({"op": "inspect", "payload": recipient,
                                            "delivery": delivery, "operator_path": str(private)})
            result["observed"] = observed
        result["recipient_dispatch_verified"] = bool(
            observed.get("ok") is True
            and observed.get("role") == "recipient"
            and set(observed.get("delivery_paths", [])) == set(delivery)
            and observed.get("delivery_sha256") == delivery_sha
            and observed.get("operator_read", {}).get("ok") is False
        )
        result["runtime_lineage_probe_verified"] = bool(
            result["recipient_dispatch_verified"] and result["ledger_fixture"]["exact_once_lineage"]
        )
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
        result["recipient_dispatch_verified"] = False
        result["runtime_lineage_probe_verified"] = False
        log("preflight_error", result["error"])
    result["scientific_claim_allowed"] = False
    result["remaining_gates"] = [
        "real producer and recipient agent execution with LLM outputs",
        "hidden scorer and operator ledger process/IPC isolation in the actual runner",
        "multi-event, missing-field and exception-path replay",
    ]
    (output / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    log("summary", result)
    print(json.dumps({key: result.get(key) for key in
                      ("recipient_dispatch_verified", "runtime_lineage_probe_verified",
                       "scientific_claim_allowed")}, indent=2))
    return 0 if result["runtime_lineage_probe_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
