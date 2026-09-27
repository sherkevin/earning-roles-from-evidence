from __future__ import annotations

import copy
import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_producer_scorer_v2 import (  # noqa: E402
    CHECK_IDS, SCHEMA_VERSION, SCORER_VERSION, classify,
)


def complete_response():
    checks = [{"id": check_id, "status": "PASS"} for check_id in CHECK_IDS]
    return {"ok": True, "value": {
        "schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
        "task_id": "DIST1_queue_race", "seed": 0,
        "artifact_sha256": "a" * 64, "status": "PASS", "label": 1,
        "quality_score": 1.0, "decision_complete": True,
        "coverage_complete": True, "checks": checks,
        "failed_check_ids": [], "observed_check_count": len(checks),
        "required_check_ids": list(CHECK_IDS),
    }}


def candidate_import_failure_response():
    checks = [{"id": "P1_source_parse", "status": "FAIL"}]
    checks += [{"id": check_id, "status": "UNKNOWN"} for check_id in CHECK_IDS[1:]]
    return {"ok": True, "value": {
        "schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
        "task_id": "DIST1_queue_race", "seed": 0,
        "artifact_sha256": "a" * 64, "status": "FAIL", "label": 0,
        "quality_score": 0.0, "decision_complete": True,
        "coverage_complete": False, "checks": checks,
        "failed_check_ids": ["P1_source_parse"],
        "observed_check_count": len(checks), "required_check_ids": list(CHECK_IDS),
        "failure_origin": "candidate", "failure_stage": "import",
        "failure_code": "DATACLASS_FIELD_ORDER", "exception_class": "TypeError",
        "source_path": "mqueue/priority.py",
    }}


def test_complete_response_is_label_eligible():
    result = classify(complete_response(), "a" * 64, "DIST1_queue_race", 0)
    assert result["status"] == "PASS" and result["label"] == 1
    assert result["decision_complete"] and result["coverage_complete"]


def test_candidate_import_failure_is_a_hard_negative_without_fake_coverage():
    result = classify(candidate_import_failure_response(), "a" * 64, "DIST1_queue_race", 0)
    assert result["status"] == "FAIL" and result["label"] == 0
    assert result["decision_complete"] and not result["coverage_complete"]
    assert result["failure_code"] == "DATACLASS_FIELD_ORDER"


def test_trusted_driver_typeerror_and_unclassified_partial_failure_are_unknown():
    response = candidate_import_failure_response()
    response["value"]["failure_origin"] = "trusted_driver"
    assert classify(response, "a" * 64, "DIST1_queue_race", 0)["status"] == "UNKNOWN"
    response = candidate_import_failure_response()
    response["value"]["failure_code"] = "ARBITRARY_TYPEERROR"
    assert classify(response, "a" * 64, "DIST1_queue_race", 0)["status"] == "UNKNOWN"


def test_incomplete_decision_and_digest_mutation_are_unknown():
    response = complete_response()
    response["value"]["decision_complete"] = False
    assert classify(response, "a" * 64, "DIST1_queue_race", 0)["status"] == "UNKNOWN"
    response = complete_response()
    response["value"]["artifact_sha256"] = "b" * 64
    assert classify(response, "a" * 64, "DIST1_queue_race", 0)["status"] == "UNKNOWN"
