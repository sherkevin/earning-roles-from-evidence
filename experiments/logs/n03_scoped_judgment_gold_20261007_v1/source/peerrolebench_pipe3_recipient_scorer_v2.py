"""Parent adapter for separate PIPE3 recipient-self and adoption scores."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_pipe3_recipient_scorer_worker_v2.py"
REQUEST_SCHEMA = "pipe3-recipient-score-request-v2"
SCHEMA_VERSION = "pipe3-recipient-score-response-v2"
SCORER_VERSION = "pipe3-recipient-objective-v2"
CHECKS = {"recipient": ("R1_process", "R2_shape", "R3_utf8_semantics"),
          "adoption": ("A1_producer_boundary", "A2_sink_adoption")}


def digest_files(files):
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        nb = name.encode(); vb = value.encode() if isinstance(value, str) else value
        h.update(len(nb).to_bytes(8, "big")); h.update(nb)
        h.update(len(vb).to_bytes(8, "big")); h.update(vb)
    return h.hexdigest()


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode()).hexdigest()


def unknown(reason, error_type=None):
    result = {"status": "UNKNOWN", "label": None, "quality_score": None,
              "scorer_version": SCORER_VERSION, "mode": None,
              "decision_complete": False, "coverage_complete": False, "reason": reason}
    if error_type:
        result["error_type"] = error_type
    return result


def classify(response, expected_digest, task_id, seed, mode):
    if not isinstance(response, dict) or response.get("ok") is not True:
        return unknown("scorer_worker_error", response.get("error_type") if isinstance(response, dict) else None)
    value = response.get("value")
    if not isinstance(value, dict):
        return unknown("scorer_response_value_not_object")
    if (value.get("schema_version") != SCHEMA_VERSION
            or value.get("scorer_version") != SCORER_VERSION
            or value.get("mode") != mode):
        return unknown("scorer_schema_version_or_mode_mismatch")
    if value.get("task_id") != task_id or value.get("seed") != seed:
        return unknown("scorer_task_identity_mismatch")
    if value.get("artifact_sha256") != expected_digest:
        return unknown("scorer_artifact_digest_mismatch")
    required = list(CHECKS[mode])
    if value.get("required_check_ids") != required:
        return unknown("scorer_check_inventory_mismatch")
    checks = value.get("checks")
    if not isinstance(checks, list) or [item.get("id") for item in checks if isinstance(item, dict)] != required:
        return unknown("scorer_check_shape_invalid")
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
            "mode": mode, "decision_complete": True, "coverage_complete": True,
            "checks": checks, "failed_check_ids": value.get("failed_check_ids", [])}


def run_scorer(sources, interfaces, mode, task_id, seed, evidence_dir, log):
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=False, exist_ok=False)
    if mode == "recipient":
        score_files = {"processor.py": sources["processor.py"]}
        visible = {path: sources[path] for path in ("processor.py", "models.py") if path in sources}
    elif mode == "adoption":
        score_files = {path: sources[path] for path in ("producer.py", "processor.py", "sink.py")}
        visible = {path: sources[path] for path in ("producer.py", "processor.py", "sink.py", "models.py") if path in sources}
    else:
        raise ValueError(f"unsupported PIPE3 scorer mode: {mode}")
    expected_digest = digest_files(score_files) if len(score_files) == (1 if mode == "recipient" else 3) and "models.py" in visible else None
    config = {"scorer_version": SCORER_VERSION, "request_schema": REQUEST_SCHEMA,
              "response_schema": SCHEMA_VERSION, "mode": mode,
              "worker": str(WORKER.relative_to(ROOT)),
              "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "task_id": task_id, "seed": seed, "score_files": sorted(score_files),
              "worker_visible_files": sorted(visible), "artifact_sha256": expected_digest,
              "event_class": interfaces["event_class"], "timestamp_field": interfaces["timestamp_field"],
              "id_field": interfaces["id_field"], "candidate_received_hidden_assertions": False,
              "scientific_claim_allowed": False}
    (evidence_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("pipe3_recipient_scorer_config", config)
    if expected_digest is None:
        result = unknown("scorer_artifact_missing")
        return result
    request = {"op": "score_recipient", "schema_version": REQUEST_SCHEMA,
               "task_id": task_id, "seed": seed, "artifact_sha256": expected_digest,
               "scorer_version": SCORER_VERSION, "mode": mode,
               "event_class": interfaces["event_class"], "timestamp_field": interfaces["timestamp_field"],
               "id_field": interfaces["id_field"]}
    response = None; transport = {"status": "not_started"}
    try:
        # SandboxedWorker exposes two positional worker arguments after the
        # public source directory.  The recipient worker interprets them as
        # ``mode`` and ``event_class`` (the producer worker uses the first as
        # an unused queue slot), so pass the root-specific contract explicitly.
        with SandboxedWorker(visible, evidence_dir / "sandbox", log,
                             mode, interfaces["event_class"], worker_path=WORKER, rpc_seconds=20,
                             source_prefixes=("producer.py", "processor.py", "sink.py", "models.py")) as worker:
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
        result = classify(response, expected_digest, task_id, seed, mode)
    payload = {"transport": transport, "request": request, "response": response,
               "response_digest": response_digest, "result": result,
               "candidate_received_hidden_assertions": False}
    (evidence_dir / "response.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    log("pipe3_recipient_scorer_response", payload)
    return {**result, "response_digest": response_digest, "transport": transport,
            "artifact_sha256": expected_digest}
