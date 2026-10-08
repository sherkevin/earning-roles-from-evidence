"""Probe both candidate roots through the real sandbox payload boundary."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

from peerrolebench_manifest_provenance import load_materials
from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_material_payload_probe_worker.py"
DEFAULT_MANIFEST = ROOT / "configs/aamas2027/n03_benchmark_baseline_candidate_v1.json"
INPUT_LIMIT = 64 * 1024


def digest_files(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        name_bytes = name.encode("utf-8")
        raw = value.encode("utf-8")
        h.update(len(name_bytes).to_bytes(8, "big"))
        h.update(name_bytes)
        h.update(len(raw).to_bytes(8, "big"))
        h.update(raw)
    return h.hexdigest()


def event_hash(previous: str, event: dict) -> str:
    blob = json.dumps({"previous": previous, "event": event}, sort_keys=True,
                      ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def sandbox_sources(files: dict[str, str]) -> dict[str, str]:
    """Map arbitrary task paths into the sandbox's public ``mqueue/`` root."""
    mapped = {}
    for name, text in files.items():
        sandbox_name = name if name.startswith("mqueue/") else "mqueue/payload/" + name
        if sandbox_name in mapped:
            raise ValueError(f"sandbox source path collision: {sandbox_name}")
        mapped[sandbox_name] = text
    return mapped


def probe_role(payload: dict, delivery: dict[str, str], output: Path, log) -> dict:
    with tempfile.TemporaryDirectory(prefix="peerrole-material-operator-") as private_tmp:
        private = Path(private_tmp) / "operator-ledger.json"
        private.write_text("operator-only\n")
        sources = sandbox_sources({**payload["source_files"], **delivery})
        with SandboxedWorker(
            sources, output, log, worker_path=WORKER, max_input_bytes=INPUT_LIMIT,
        ) as worker:
            return worker.request({"op": "inspect", "payload": payload,
                                   "delivery": delivery, "operator_path": str(private)})


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw = output / "raw.jsonl"

    def log(event_type: str, payload: object) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = {
        "experiment_id": output.name,
        "purpose": "candidate DIST1/PIPE3 payload dispatch, delivery binding and operator denial",
        "manifest_version": manifest.get("manifest_version"),
        "manifest_path": str(manifest_path),
        "command": sys.argv,
        "python": sys.version,
        "platform": platform.platform(),
        "input_limit_bytes": INPUT_LIMIT,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "candidate_code_executed": False,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    results = []
    chain = "GENESIS"
    try:
        for root in manifest["roots"]:
            seed = root["seeds"][0]
            materials, _ = load_materials(root["task_id"], seed, root.get("material_adapter"))
            producer = materials["agent_payloads"]["producer"]
            recipient = materials["agent_payloads"]["recipient"]
            delivery = {path: producer["source_files"][path]
                        for path in producer["writable_paths"]}
            if set(delivery) != set(recipient["required_delivery_paths"]):
                raise ValueError(f"delivery allowlist mismatch for {root['root_id']}")
            selection = {"event_id": f"selection-{root['root_id']}",
                         "root_id": root["root_id"], "seed": seed,
                         "propensity": 0.5, "peer": "producer-0", "recipient": "recipient-0"}
            delivery_event = {"event_id": f"delivery-{root['root_id']}",
                              "selection_id": selection["event_id"],
                              "artifact_sha256": digest_files(delivery),
                              "paths": sorted(delivery)}
            dispatch_event = {"event_id": f"dispatch-{root['root_id']}",
                              "delivery_id": delivery_event["event_id"],
                              "recipient_payload_sha256": hashlib.sha256(
                                  json.dumps(recipient, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
            for event in (selection, delivery_event, dispatch_event):
                chain = event_hash(chain, event)
            producer_probe = probe_role(producer, {}, output / root["root_id"] / "producer", log)
            recipient_probe = probe_role(recipient, delivery,
                                         output / root["root_id"] / "recipient", log)
            row = {
                "root_id": root["root_id"], "task_id": root["task_id"], "seed": seed,
                "producer_probe": producer_probe, "recipient_probe": recipient_probe,
                "delivery_sha256": delivery_event["artifact_sha256"],
                "producer_dispatch_verified": bool(
                    producer_probe.get("ok") is True
                    and producer_probe.get("role") == "producer"
                    and producer_probe.get("operator_read", {}).get("ok") is False
                    and producer_probe.get("delivery_paths") == []
                ),
                "recipient_dispatch_verified": bool(
                    recipient_probe.get("ok") is True
                    and recipient_probe.get("role") == "recipient"
                    and set(recipient_probe.get("delivery_paths", [])) == set(delivery)
                    and recipient_probe.get("delivery_sha256") == delivery_event["artifact_sha256"]
                    and recipient_probe.get("operator_read", {}).get("ok") is False
                ),
            }
            row["lineage_verified"] = row["producer_dispatch_verified"] and row["recipient_dispatch_verified"]
            results.append(row)
            log("root_result", row)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
        log("preflight_error", error)
        summary = {"config": config, "results": results, "error": error,
                   "runtime_payload_preflight_passed": False, "final_lineage_hash": chain,
                   "scientific_claim_allowed": False}
        (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
        return 1
    summary = {
        "config": config, "results": results, "final_lineage_hash": chain,
        "runtime_payload_preflight_passed": bool(results) and all(row["lineage_verified"] for row in results),
        "scientific_claim_allowed": False,
        "remaining_gates": [
            "real actor output dispatch in the closed-loop runner",
            "hidden scorer and operator ledger isolation in live episodes",
            "multi-event exception/retry/unknown replay",
            "producer contract and recipient outcome qualification",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"runtime_payload_preflight_passed": summary["runtime_payload_preflight_passed"],
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["runtime_payload_preflight_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
