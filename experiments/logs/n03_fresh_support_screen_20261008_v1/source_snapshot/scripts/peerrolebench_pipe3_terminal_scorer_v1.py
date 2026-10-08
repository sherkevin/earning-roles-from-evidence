"""Parent adapter for the private PIPE3 terminal holdout worker."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from peerrolebench_sandbox import SandboxedWorker
from peerrolebench_pipe3_material_adapter import digest_files


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_pipe3_terminal_scorer_worker_v1.py"
REQUEST_SCHEMA = "pipe3-terminal-holdout-request-v1"
SCHEMA_VERSION = "pipe3-terminal-holdout-response-v1"
SCORER_VERSION = "pipe3-terminal-holdout-v1"
CHECK_IDS = ("T1_holdout_projection", "T2_batch_cardinality", "T3_utf8_holdout")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def reference_projection_digest(info: Mapping[str, Any]) -> str:
    action = str(info["action_value"]).upper()
    records = [{
        info["id_field"]: identifier,
        info["timestamp_field"]: "2023-11-14T22:13:20",
        info["user_field"]: info["user_value"],
        info["action_field"]: action,
        info["value_field"]: info["value_value"],
    } for identifier in ("terminal-001", "terminal-002")]
    return canonical_digest(records)


def _unknown(reason: str, error_type: str | None = None) -> dict[str, Any]:
    result = {"status": "UNKNOWN", "label": None, "quality_score": None,
              "scorer_version": SCORER_VERSION, "coverage_complete": False,
              "reason": reason}
    if error_type:
        result["error_type"] = error_type
    return result


def classify(response: Any, expected_digest: str, holdout_digest: str,
             task_id: str, seed: int) -> dict[str, Any]:
    if not isinstance(response, dict) or response.get("ok") is not True:
        return _unknown("terminal_worker_error", response.get("error_type") if isinstance(response, dict) else None)
    if response.get("schema_version") != SCHEMA_VERSION or response.get("scorer_version") != SCORER_VERSION:
        return _unknown("terminal_response_schema_mismatch")
    if response.get("task_id") != task_id or response.get("seed") != seed:
        return _unknown("terminal_task_identity_mismatch")
    if response.get("artifact_sha256") != expected_digest:
        return _unknown("terminal_artifact_digest_mismatch")
    if response.get("holdout_digest") != holdout_digest:
        return _unknown("terminal_holdout_digest_mismatch")
    if response.get("required_check_ids") != list(CHECK_IDS):
        return _unknown("terminal_check_inventory_mismatch")
    checks = response.get("checks")
    if not isinstance(checks, list) or [item.get("id") for item in checks] != list(CHECK_IDS):
        return _unknown("terminal_check_shape_invalid")
    if response.get("coverage_complete") is not True:
        return _unknown("terminal_coverage_incomplete")
    statuses = [item.get("status") for item in checks]
    if any(status not in {"PASS", "FAIL"} for status in statuses):
        return _unknown("terminal_check_contains_unknown")
    expected_status = "PASS" if all(status == "PASS" for status in statuses) else "FAIL"
    if response.get("status") != expected_status or response.get("label") != int(expected_status == "PASS"):
        return _unknown("terminal_status_label_inconsistent")
    quality = response.get("quality_score")
    if not isinstance(quality, (int, float)) or isinstance(quality, bool) or not 0 <= float(quality) <= 1:
        return _unknown("terminal_quality_invalid")
    return {"status": expected_status, "label": int(expected_status == "PASS"),
            "quality_score": float(quality), "scorer_version": SCORER_VERSION,
            "coverage_complete": True, "checks": checks}


def run_terminal_scorer(sources: Mapping[str, str], info: Mapping[str, Any],
                        task_id: str, seed: int, evidence_dir: Path, log) -> dict[str, Any]:
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=False, exist_ok=False)
    score_files = {name: sources[name] for name in ("producer.py", "processor.py", "sink.py", "models.py")}
    artifact_digest = digest_files(score_files)
    holdout_digest = canonical_digest({"task_id": task_id, "seed": seed, "checks": list(CHECK_IDS),
                                       "reference_projection_digest": reference_projection_digest(info)})
    config = {"scorer_version": SCORER_VERSION, "request_schema": REQUEST_SCHEMA,
              "response_schema": SCHEMA_VERSION, "worker": str(WORKER.relative_to(ROOT)),
              "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "task_id": task_id, "seed": seed, "score_files": sorted(score_files),
              "artifact_sha256": artifact_digest, "holdout_digest": holdout_digest,
              "reference_projection_digest": reference_projection_digest(info),
              "candidate_received_hidden_assertions": False, "scientific_claim_allowed": False}
    (evidence_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("terminal_scorer_config", config)
    request = {"op": "score_terminal", "schema_version": REQUEST_SCHEMA,
               "task_id": task_id, "seed": seed, "artifact_sha256": artifact_digest,
               "holdout_digest": holdout_digest,
               "reference_projection_digest": reference_projection_digest(info),
               "scorer_version": SCORER_VERSION, **dict(info)}
    response = None; transport = {"status": "not_started"}
    try:
        with SandboxedWorker(score_files, evidence_dir / "sandbox", log,
                             "unused", "unused", worker_path=WORKER, rpc_seconds=20,
                             source_prefixes=("producer.py", "processor.py", "sink.py", "models.py")) as worker:
            response = worker.request(request)
        transport = {"status": "complete"}
    except TimeoutError as exc:
        transport = {"status": "timeout", "error_type": type(exc).__name__, "message": str(exc)}
    except (PermissionError, OSError, RuntimeError, ValueError) as exc:
        transport = {"status": "error", "error_type": type(exc).__name__, "message": str(exc)}
    response_digest = canonical_digest(response) if response is not None else None
    result = classify(response, artifact_digest, holdout_digest, task_id, seed) if response is not None else _unknown("terminal_transport_" + transport["status"], transport.get("error_type"))
    payload = {"transport": transport, "request": request, "response": response,
               "response_digest": response_digest, "result": result,
               "candidate_received_hidden_assertions": False}
    (evidence_dir / "response.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    log("terminal_scorer_response", payload)
    return {**result, "response_digest": response_digest, "transport": transport,
            "artifact_sha256": artifact_digest, "holdout_digest": holdout_digest}


__all__ = ["CHECK_IDS", "SCORER_VERSION", "reference_projection_digest", "run_terminal_scorer", "classify"]
