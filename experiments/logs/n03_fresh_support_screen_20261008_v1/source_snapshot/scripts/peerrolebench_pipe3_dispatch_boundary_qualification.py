"""Qualify the PIPE3 actor/scorer view boundary without an LLM call.

The check exercises the real sandbox RPC and the root-specific material/action
adapter.  It verifies public producer/recipient payloads, selected delivery,
operator-file denial, scorer view separation, and write-set enforcement.  It
does not execute candidate code or produce a benchmark label.
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
import tempfile
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    adoption_scorer_sources, attach_pipe3_delivery, prepare_pipe3_action,
    producer_scorer_sources, recipient_scorer_sources,
    validate_pipe3_action_result,
)
from peerrolebench_pipe3_payload_runtime_preflight import ADAPTER, QUAL  # noqa: E402
from peerrolebench_sandbox import SandboxedWorker  # noqa: E402


WORKER = ROOT / "scripts/peerrolebench_pipe3_payload_probe_worker.py"


def _digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _sandbox_sources(source_files: Mapping[str, str]) -> dict[str, str]:
    return {f"mqueue/{name}": text for name, text in source_files.items()}


def _probe(payload: Mapping[str, Any], output: Path, log) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="peerrole-pipe3-dispatch-") as private_tmp:
        operator = Path(private_tmp) / "operator-ledger.json"
        operator.write_text("operator-only\n", encoding="utf-8")
        with SandboxedWorker(_sandbox_sources(payload["source_files"]), output, log,
                             worker_path=WORKER, max_input_bytes=64 * 1024) as worker:
            return worker.request({"op": "inspect", "payload": payload,
                                   "operator_path": str(operator)})


def run(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    config = {
        "experiment_id": "n03_pipe3_dispatch_boundary_qualification_20260928_v1",
        "kind": "zero_api_zero_gpu_actor_scorer_view_and_sandbox_boundary",
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "worker": str(WORKER.relative_to(ROOT)),
        "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "git_commit": commit},
        "llm_calls": 0, "gpu_jobs": 0, "candidate_code_executed": False,
        "native_grader_invoked": False, "scientific_claim_allowed": False,
        "checks": ["producer_dispatch", "recipient_dispatch", "scorer_views",
                    "wrong_delivery_rejected", "read_only_action_rejected"],
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"

    def log(event_type: str, payload: Any) -> None:
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()

    log("config", config)
    generated = QUAL.load_pipe3(0)
    materials = build_materials(generated)
    producer_payload = materials["agent_payloads"]["producer"]
    recipient_template = materials["agent_payloads"]["recipient"]
    producer_delivery = {path: producer_payload["source_files"][path]
                         for path in producer_payload["writable_paths"]}
    recipient_payload = attach_pipe3_delivery(recipient_template, producer_delivery)
    action_payload = prepare_pipe3_action(materials, producer_delivery, "repair")
    source_files = dict(action_payload["source_files"])

    producer_probe = _probe(producer_payload, out_dir / "producer_probe", log)
    recipient_probe = _probe(recipient_payload, out_dir / "recipient_probe", log)
    producer_dispatch = (
        producer_probe.get("ok") is True
        and producer_probe.get("role") == "producer"
        and producer_probe.get("operator_read", {}).get("ok") is False
        and "tests/test_pipeline.py" not in producer_probe.get("payload_source_names", [])
    )
    recipient_dispatch = (
        recipient_probe.get("ok") is True
        and recipient_probe.get("role") == "recipient"
        and recipient_probe.get("operator_read", {}).get("ok") is False
        and "producer.py" in recipient_probe.get("payload_source_names", [])
        and "tests/test_pipeline.py" not in recipient_probe.get("payload_source_names", [])
    )
    log("producer_probe", producer_probe)
    log("recipient_probe", recipient_probe)

    views = {
        "producer": sorted(producer_scorer_sources(materials, producer_delivery)),
        "recipient": sorted(recipient_scorer_sources(source_files)),
        "adoption": sorted(adoption_scorer_sources(source_files)),
    }
    views_ok = views == {
        "producer": ["models.py", "producer.py"],
        "recipient": ["models.py", "processor.py"],
        "adoption": ["models.py", "processor.py", "producer.py", "sink.py"],
    }
    log("scorer_views", views)

    negative: dict[str, Any] = {}
    try:
        attach_pipe3_delivery(recipient_template, {"processor.py": "wrong"})
        negative["wrong_delivery"] = {"status": "FAIL_TO_REJECT"}
    except ValueError as exc:
        negative["wrong_delivery"] = {"status": "REJECTED", "error": str(exc)}
    mutated = dict(source_files)
    mutated["models.py"] = mutated["models.py"] + "\n# unauthorized\n"
    try:
        validate_pipe3_action_result(action_payload, mutated)
        negative["read_only_action"] = {"status": "FAIL_TO_REJECT"}
    except ValueError as exc:
        negative["read_only_action"] = {"status": "REJECTED", "error": str(exc)}
    log("negative_cases", negative)

    checks = {
        "producer_dispatch": producer_dispatch,
        "recipient_dispatch": recipient_dispatch,
        "scorer_views": views_ok,
        "wrong_delivery_rejected": negative["wrong_delivery"]["status"] == "REJECTED",
        "read_only_action_rejected": negative["read_only_action"]["status"] == "REJECTED",
    }
    summary = {
        **config, "checks": checks, "passed": all(checks.values()),
        "payload_digests": {
            "producer": _digest(producer_payload), "recipient": _digest(recipient_payload),
            "action": _digest(action_payload),
        },
        "scorer_views": views, "negative_cases": negative,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "payload_manifest.json").write_text(json.dumps({
        "producer": producer_payload, "recipient": recipient_payload,
        "action": action_payload, "materials": materials["manifest"],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log("summary", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({key: result[key] for key in ("passed", "checks", "llm_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
