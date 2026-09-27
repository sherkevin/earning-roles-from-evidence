from __future__ import annotations

import copy
import sys
import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_producer_scorer import (  # noqa: E402
    CHECK_IDS,
    SCHEMA_VERSION,
    SCORER_VERSION,
    classify,
)
from peerrolebench_real_closed_loop import append_producer_score  # noqa: E402
from peer_role_protocol_20260925 import Delivery, PeerRoleLedger  # noqa: E402


def complete_response():
    checks = [{"id": check_id, "status": "PASS"} for check_id in CHECK_IDS]
    return {"ok": True, "value": {
        "schema_version": SCHEMA_VERSION,
        "scorer_version": SCORER_VERSION,
        "task_id": "DIST1_queue_race",
        "seed": 0,
        "artifact_sha256": "a" * 64,
        "status": "PASS", "label": 1, "quality_score": 1.0,
        "coverage_complete": True, "checks": checks,
        "failed_check_ids": [], "observed_check_count": len(checks),
        "required_check_ids": list(CHECK_IDS),
    }}


def test_complete_response_is_label_eligible():
    result = classify(complete_response(), "a" * 64, "DIST1_queue_race", 0)
    assert result["status"] == "PASS"
    assert result["label"] == 1
    assert result["coverage_complete"] is True


def test_artifact_mismatch_is_unknown_not_negative_label():
    result = classify(complete_response(), "b" * 64, "DIST1_queue_race", 0)
    assert result["status"] == "UNKNOWN"
    assert result["label"] is None


def test_unknown_check_or_incomplete_coverage_cannot_update():
    response = complete_response()
    response["value"]["checks"][0]["status"] = "UNKNOWN"
    response["value"]["status"] = "UNKNOWN"
    response["value"]["label"] = None
    response["value"]["coverage_complete"] = False
    result = classify(response, "a" * 64, "DIST1_queue_race", 0)
    assert result["status"] == "UNKNOWN"
    assert result["label"] is None


def test_worker_error_and_schema_mismatch_are_unknown():
    assert classify({"ok": False, "error_type": "TimeoutError"}, "a" * 64,
                    "DIST1_queue_race", 0)["status"] == "UNKNOWN"
    response = complete_response()
    response["value"]["schema_version"] = "future"
    assert classify(response, "a" * 64, "DIST1_queue_race", 0)["status"] == "UNKNOWN"


def test_complete_score_digest_mismatch_is_rejected_before_ledger_append(tmp_path):
    ledger = PeerRoleLedger(require_selection=False, require_terminal_outcome=False)
    delivery = Delivery("d0", "task", "producer", "recipient", "a" * 64,
                        "request", 0, "selection")
    with pytest.raises(ValueError, match="not bound to the delivered artifact"):
        append_producer_score(tmp_path, ledger, delivery, {
            "status": "PASS", "label": 1, "quality_score": 1.0,
            "artifact_sha256": "b" * 64, "scorer_version": "v1",
            "response_digest": "c" * 64, "coverage_complete": True,
        })
