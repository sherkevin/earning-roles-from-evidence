"""Parent adapter for the private DIST1 producer-only scorer."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_hidden_producer_scorer_worker.py"
REQUEST_SCHEMA = "dist1-producer-score-request-v1"
SCHEMA_VERSION = "dist1-producer-score-response-v1"
SCORER_VERSION = "dist1-producer-objective-v1"
CHECK_IDS = ("P1_source_parse", "P2_capacity", "P3_ack_receipt",
             "P4_nack_recovery", "P5_priority_type_safety", "P6_priority_order",
             "P7_zero_loss")
PRODUCER_FILES = ("mqueue/queue.py", "mqueue/priority.py")
OPERATOR_SUPPORT_FILES = ("mqueue/__init__.py", "mqueue/config.py")


def digest_files(files):
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        part = path.encode()
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
        part = content.encode() if isinstance(content, str) else content
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
    return digest.hexdigest()


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode()).hexdigest()


def unknown(reason, error_type=None):
    result = {"status": "UNKNOWN", "label": None, "quality_score": None,
              "scorer_version": SCORER_VERSION, "coverage_complete": False,
              "reason": reason}
    if error_type:
        result["error_type"] = error_type
    return result


def classify(response, expected_digest, task_id, seed):
    if not isinstance(response, dict) or response.get("ok") is not True:
        return unknown("scorer_worker_error", str(response.get("error_type", "unknown"))
                       if isinstance(response, dict) else None)
    value = response.get("value")
    if not isinstance(value, dict):
        return unknown("scorer_response_value_not_object")
    if value.get("schema_version") != SCHEMA_VERSION or value.get("scorer_version") != SCORER_VERSION:
        return unknown("scorer_schema_or_version_mismatch")
    if value.get("task_id") != task_id or value.get("seed") != seed:
        return unknown("scorer_task_identity_mismatch")
    if value.get("artifact_sha256") != expected_digest:
        return unknown("scorer_artifact_digest_mismatch")
    if value.get("required_check_ids") != list(CHECK_IDS):
        return unknown("scorer_check_inventory_mismatch")
    checks = value.get("checks")
    if not isinstance(checks, list) or [item.get("id") for item in checks if isinstance(item, dict)] != list(CHECK_IDS):
        return unknown("scorer_check_shape_invalid")
    if value.get("coverage_complete") is not True or value.get("status") not in {"PASS", "FAIL"}:
        return unknown("scorer_coverage_incomplete")
    statuses = [item.get("status") for item in checks]
    if any(status not in {"PASS", "FAIL"} for status in statuses):
        return unknown("scorer_contains_unknown_check")
    quality = value.get("quality_score")
    if not isinstance(quality, (int, float)) or not 0 <= float(quality) <= 1:
        return unknown("scorer_quality_score_invalid")
    expected_status = "PASS" if all(status == "PASS" for status in statuses) else "FAIL"
    if value.get("status") != expected_status or value.get("label") != int(expected_status == "PASS"):
        return unknown("scorer_status_label_inconsistent")
    return {"status": value["status"], "label": value["label"],
            "quality_score": float(quality), "scorer_version": SCORER_VERSION,
            "coverage_complete": True, "checks": checks,
            "failed_check_ids": value.get("failed_check_ids", [])}


def run_producer_scorer(sources, interfaces, task_id, seed, evidence_dir, log):
    """Run the producer scorer on an immutable delivery source snapshot."""
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=False, exist_ok=False)
    files = {path: sources[path] for path in PRODUCER_FILES if path in sources}
    worker_sources = {path: sources[path] for path in (*PRODUCER_FILES, *OPERATOR_SUPPORT_FILES)
                      if path in sources}
    expected_digest = digest_files(files) if set(files) == set(PRODUCER_FILES) else None
    config = {"scorer_version": SCORER_VERSION, "request_schema": REQUEST_SCHEMA,
              "response_schema": SCHEMA_VERSION, "worker": str(WORKER.relative_to(ROOT)),
              "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "task_id": task_id, "seed": seed, "producer_files": list(PRODUCER_FILES),
              "worker_visible_files": sorted(worker_sources),
              "artifact_sha256": expected_digest, "queue_name": interfaces["queue"],
              "priority_name": interfaces["priority"],
              "candidate_received_hidden_assertions": False,
              "scientific_claim_allowed": False}
    (evidence_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("producer_scorer_config", config)
    if expected_digest is None:
        result = unknown("producer_artifact_missing")
        payload = {"transport": {"status": "not_started"}, "request": None,
                   "response": None, "response_digest": None, "result": result}
        (evidence_dir / "response.json").write_text(json.dumps(payload, indent=2) + "\n")
        log("producer_scorer_response", payload)
        return result
    request = {"op": "score_producer", "schema_version": REQUEST_SCHEMA,
               "task_id": task_id, "seed": seed, "artifact_sha256": expected_digest,
               "scorer_version": SCORER_VERSION}
    response = None
    transport = {"status": "not_started"}
    try:
        with SandboxedWorker(worker_sources, evidence_dir / "sandbox", log,
                             interfaces["queue"], interfaces["priority"], worker_path=WORKER) as worker:
            response = worker.request(request)
        transport = {"status": "complete"}
    except TimeoutError as exc:
        transport = {"status": "timeout", "error_type": type(exc).__name__, "message": str(exc)}
    except (PermissionError, OSError, RuntimeError, ValueError) as exc:
        transport = {"status": "error", "error_type": type(exc).__name__, "message": str(exc)}
    if response is None:
        result = unknown("scorer_transport_" + transport["status"], transport.get("error_type"))
        response_digest = None
    else:
        response_digest = canonical_digest(response)
        result = classify(response, expected_digest, task_id, seed)
    payload = {"transport": transport, "request": request, "response": response,
               "response_digest": response_digest, "result": result,
               "candidate_received_hidden_assertions": False}
    (evidence_dir / "response.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    log("producer_scorer_response", payload)
    return {**result, "response_digest": response_digest, "transport": transport,
            "artifact_sha256": expected_digest}
