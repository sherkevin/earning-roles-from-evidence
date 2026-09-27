#!/usr/bin/env python3
"""Dispatch one redacted PIPE3 payload through the qualified worker boundary."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


QUAL = load("pipe3_qualification", ROOT / "scripts/peerrolebench_pipe3_task_qualification.py")
ADAPTER = load("pipe3_material_adapter", ROOT / "scripts/peerrolebench_pipe3_material_adapter.py")


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "--output":
        raise SystemExit("usage: peerrolebench_pipe3_payload_runtime_preflight.py --output DIR")
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
        "purpose": "N03 PIPE3 redacted payload dispatch and operator-file visibility probe",
        "source_commit": QUAL.PIN,
        "seed": 0,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "candidate_code_executed": False,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    result = {"config": config}
    try:
        generated = QUAL.load_pipe3(0)
        materials = ADAPTER.build_materials(generated)
        payload = materials["agent_payloads"]["producer"]
        result["material_manifest"] = materials["manifest"]
        with tempfile.TemporaryDirectory(prefix="peerrole-pipe3-operator-") as private_tmp:
            private = Path(private_tmp) / "operator-ledger.json"
            private.write_text("operator-only\n")
            sources = {f"mqueue/{name}": text for name, text in payload["source_files"].items()}
            worker_log = lambda event_type, item: log("sandbox." + event_type, item)
            with SandboxedWorker(
                sources,
                output / "sandbox",
                worker_log,
                worker_path=ROOT / "scripts/peerrolebench_pipe3_payload_probe_worker.py",
            ) as worker:
                observed = worker.request({"op": "inspect", "payload": payload,
                                            "operator_path": str(private)})
            result["observed"] = observed
        result["payload_dispatch_verified"] = bool(
            observed.get("ok") is True
            and observed.get("role") == "producer"
            and observed.get("payload_source_count") == len(payload["source_files"])
            and observed.get("source_root_exists") is True
            and observed.get("operator_read", {}).get("ok") is False
        )
        result["runtime_dispatch_verified"] = result["payload_dispatch_verified"]
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
        result["payload_dispatch_verified"] = False
        result["runtime_dispatch_verified"] = False
        log("preflight_error", result["error"])
    result["scientific_claim_allowed"] = False
    result["remaining_gates"] = [
        "dispatch both producer and recipient payloads through the real runner",
        "prove hidden scorer and operator ledger remain outside candidate-visible IPC",
        "replay real selection/delivery/judgment/action/score lineage",
    ]
    (output / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    log("summary", result)
    print(json.dumps({key: result.get(key) for key in
                      ("payload_dispatch_verified", "runtime_dispatch_verified",
                       "scientific_claim_allowed")}, indent=2))
    return 0 if result["runtime_dispatch_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
