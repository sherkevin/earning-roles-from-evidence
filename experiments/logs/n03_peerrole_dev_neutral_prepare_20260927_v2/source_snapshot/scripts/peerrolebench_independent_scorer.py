"""Parent adapter for the private DIST1 scorer worker.

The adapter is deliberately narrow: it returns a structured scorer result or
an explicit UNKNOWN disposition.  It never converts transport/permission or
malformed responses into a capability label.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_hidden_consumer_scorer_worker.py"
SCORER_VERSION = "dist1-independent-scorer-v1"
CHECK_IDS = ("empty_consumer", "payload_and_ack", "retry_after_handler_failure", "drain")


def canonical_digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def unknown(reason: str, *, error_type: str | None = None) -> dict:
    result = {"status": "UNKNOWN", "label": None, "score": None,
              "scorer_version": SCORER_VERSION, "coverage_complete": False,
              "reason": reason}
    if error_type:
        result["error_type"] = error_type
    return result


def classify(response: object) -> dict:
    if not isinstance(response, dict):
        return unknown("scorer_response_not_object")
    if response.get("ok") is not True:
        return unknown("scorer_worker_error", error_type=str(response.get("error_type", "unknown")))
    if response.get("scorer_version") != SCORER_VERSION:
        return unknown("scorer_version_mismatch")
    if response.get("required_check_ids") != list(CHECK_IDS):
        return unknown("scorer_check_coverage_mismatch")
    checks = response.get("checks")
    if not isinstance(checks, list) or [item.get("id") for item in checks if isinstance(item, dict)] != list(CHECK_IDS):
        return unknown("scorer_check_shape_invalid")
    if response.get("coverage_complete") is not True or response.get("status") not in {"PASS", "FAIL"}:
        return unknown("scorer_coverage_incomplete")
    statuses = [item.get("status") for item in checks]
    if any(status not in {"PASS", "FAIL"} for status in statuses):
        return unknown("scorer_contains_unknown_check")
    score = response.get("score")
    if not isinstance(score, (int, float)) or not 0 <= float(score) <= 1:
        return unknown("scorer_score_invalid")
    expected_status = "PASS" if all(status == "PASS" for status in statuses) else "FAIL"
    if response["status"] != expected_status:
        return unknown("scorer_status_inconsistent")
    return {"status": response["status"], "label": int(response["status"] == "PASS"),
            "score": float(score), "scorer_version": SCORER_VERSION,
            "coverage_complete": True}


def run_independent_scorer(sources, interfaces, evidence_dir, log):
    """Score a sealed public source snapshot in a separate private worker."""
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=False, exist_ok=False)
    config = {"scorer_version": SCORER_VERSION, "worker": str(WORKER.relative_to(ROOT)),
              "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "queue_name": interfaces["queue"], "consumer_name": interfaces["consumer"],
              "candidate_received_hidden_assertions": False, "scientific_claim_allowed": False}
    (evidence_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    log("independent_scorer_config", config)
    response = None
    transport = {"status": "not_started"}
    try:
        with SandboxedWorker(sources, evidence_dir / "sandbox", log,
                             interfaces["queue"], interfaces["consumer"], worker_path=WORKER) as worker:
            response = worker.request({"op": "score"})
        transport = {"status": "complete"}
    except TimeoutError as exc:
        transport = {"status": "timeout", "error_type": type(exc).__name__, "message": str(exc)}
    except (PermissionError, OSError, RuntimeError, ValueError) as exc:
        transport = {"status": "error", "error_type": type(exc).__name__, "message": str(exc)}
    if response is None:
        result = unknown("scorer_transport_" + transport["status"], error_type=transport.get("error_type"))
        response_digest = None
    else:
        response_digest = canonical_digest(response)
        result = classify(response)
    payload = {"transport": transport, "response": response, "response_digest": response_digest,
               "result": result, "candidate_received_hidden_assertions": False}
    with (evidence_dir / "response.json").open("w") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    log("independent_scorer_response", payload)
    return {**result, "response_digest": response_digest, "transport": transport}
