"""Parent adapter for the private PIPE3 producer scorer.

This is a diagnostic contract scorer only.  It binds the score to the sealed
producer.py digest and keeps the consumer, sink, tests, expected output and
operator ledger out of the worker source tree.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_pipe3_producer_scorer_worker_v2.py"
REQUEST_SCHEMA = "pipe3-producer-score-request-v2"
SCHEMA_VERSION = "pipe3-producer-score-response-v2"
SCORER_VERSION = "pipe3-producer-objective-v2"
CHECK_IDS = ("P1_import", "P2_iso_serialization", "P3_batch_output")
FAILURE_CODES = {"SYNTAX_ERROR_IN_DELIVERY", "TYPE_ERROR_IN_DELIVERY", "IMPORT_ERROR_IN_DELIVERY"}
PRODUCER_FILES = ("producer.py",)
SUPPORT_FILES = ("models.py",)


def digest_files(files):
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        name_bytes = name.encode()
        value_bytes = value.encode() if isinstance(value, str) else value
        h.update(len(name_bytes).to_bytes(8, "big")); h.update(name_bytes)
        h.update(len(value_bytes).to_bytes(8, "big")); h.update(value_bytes)
    return h.hexdigest()


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode()).hexdigest()


def unknown(reason, error_type=None):
    result = {"status": "UNKNOWN", "label": None, "quality_score": None,
              "scorer_version": SCORER_VERSION, "decision_complete": False,
              "coverage_complete": False, "reason": reason}
    if error_type:
        result["error_type"] = error_type
    return result


def classify(response, expected_digest, task_id, seed):
    if not isinstance(response, dict) or response.get("ok") is not True:
        return unknown("scorer_worker_error", response.get("error_type") if isinstance(response, dict) else None)
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
    if value.get("status") == "FAIL" and value.get("coverage_complete") is False:
        eligible = (value.get("decision_complete") is True and value.get("label") == 0
                    and value.get("quality_score") == 0.0
                    and value.get("failure_origin") == "candidate"
                    and value.get("failure_code") in FAILURE_CODES
                    and value.get("source_path") == "producer.py")
        if not eligible:
            return unknown("scorer_incomplete_failure_not_candidate_eligible")
        return {"status": "FAIL", "label": 0, "quality_score": 0.0,
                "scorer_version": SCORER_VERSION, "decision_complete": True,
                "coverage_complete": False, "checks": checks,
                "failed_check_ids": value.get("failed_check_ids", []),
                "failure_origin": value["failure_origin"], "failure_stage": value.get("failure_stage"),
                "failure_code": value["failure_code"], "exception_class": value.get("exception_class"),
                "source_path": value["source_path"]}
    if value.get("decision_complete") is not True or value.get("coverage_complete") is not True:
        return unknown("scorer_coverage_or_decision_incomplete")
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
            "decision_complete": True, "coverage_complete": True, "checks": checks,
            "failed_check_ids": value.get("failed_check_ids", [])}


def run_producer_scorer(sources, interfaces, task_id, seed, evidence_dir, log):
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=False, exist_ok=False)
    producer = {path: sources[path] for path in PRODUCER_FILES if path in sources}
    worker_sources = {path: sources[path] for path in (*PRODUCER_FILES, *SUPPORT_FILES) if path in sources}
    expected_digest = digest_files(producer) if set(producer) == set(PRODUCER_FILES) else None
    config = {"scorer_version": SCORER_VERSION, "request_schema": REQUEST_SCHEMA,
              "response_schema": SCHEMA_VERSION, "worker": str(WORKER.relative_to(ROOT)),
              "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "task_id": task_id, "seed": seed, "producer_files": list(PRODUCER_FILES),
              "worker_visible_files": sorted(worker_sources), "rpc_timeout_seconds": 20,
              "artifact_sha256": expected_digest, "event_class": interfaces["event_class"],
              "timestamp_field": interfaces["timestamp_field"], "id_field": interfaces["id_field"],
              "candidate_received_hidden_assertions": False, "scientific_claim_allowed": False}
    (evidence_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("pipe3_producer_scorer_config", config)
    if expected_digest is None:
        result = unknown("producer_artifact_missing")
        payload = {"transport": {"status": "not_started"}, "request": None,
                   "response": None, "response_digest": None, "result": result}
        (evidence_dir / "response.json").write_text(json.dumps(payload, indent=2) + "\n")
        log("pipe3_producer_scorer_response", payload)
        return result
    request = {"op": "score_producer", "schema_version": REQUEST_SCHEMA,
               "task_id": task_id, "seed": seed, "artifact_sha256": expected_digest,
               "scorer_version": SCORER_VERSION, "event_class": interfaces["event_class"],
               "timestamp_field": interfaces["timestamp_field"], "id_field": interfaces["id_field"]}
    response = None
    transport = {"status": "not_started"}
    try:
        with SandboxedWorker(worker_sources, evidence_dir / "sandbox", log,
                             "unused", interfaces["event_class"], worker_path=WORKER,
                             rpc_seconds=20, source_prefixes=("producer.py", "models.py")) as worker:
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
    log("pipe3_producer_scorer_response", payload)
    return {**result, "response_digest": response_digest, "transport": transport,
            "artifact_sha256": expected_digest}
