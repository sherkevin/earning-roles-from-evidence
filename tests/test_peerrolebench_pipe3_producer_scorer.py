from __future__ import annotations

import copy
import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_producer_scorer import (  # noqa: E402
    CHECK_IDS, SCHEMA_VERSION, SCORER_VERSION, classify,
)


def response():
    checks = [{"id": check_id, "status": "PASS"} for check_id in CHECK_IDS]
    return {"ok": True, "value": {
        "schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "artifact_sha256": "a" * 64, "status": "PASS", "label": 1,
        "quality_score": 1.0, "decision_complete": True, "coverage_complete": True,
        "checks": checks, "failed_check_ids": [],
        "observed_check_count": len(checks), "required_check_ids": list(CHECK_IDS),
    }}


def test_pipe3_complete_response_is_label_eligible():
    result = classify(response(), "a" * 64, "PIPE3_stream_processing", 0)
    assert result["status"] == "PASS" and result["label"] == 1


def test_pipe3_digest_and_incomplete_mutations_are_unknown():
    mutated = copy.deepcopy(response())
    mutated["value"]["artifact_sha256"] = "b" * 64
    assert classify(mutated, "a" * 64, "PIPE3_stream_processing", 0)["status"] == "UNKNOWN"
    mutated = copy.deepcopy(response())
    mutated["value"]["decision_complete"] = False
    assert classify(mutated, "a" * 64, "PIPE3_stream_processing", 0)["status"] == "UNKNOWN"


def test_pipe3_candidate_syntax_failure_is_a_hard_negative():
    mutated = copy.deepcopy(response())
    checks = [{"id": "P1_import", "status": "FAIL"}]
    checks += [{"id": check_id, "status": "UNKNOWN"} for check_id in CHECK_IDS[1:]]
    value = mutated["value"]
    value.update({"status": "FAIL", "label": 0, "quality_score": 0.0,
                  "decision_complete": True, "coverage_complete": False,
                  "checks": checks, "failed_check_ids": ["P1_import"],
                  "failure_origin": "candidate", "failure_stage": "import",
                  "failure_code": "SYNTAX_ERROR_IN_DELIVERY",
                  "exception_class": "SyntaxError", "source_path": "producer.py"})
    result = classify(mutated, "a" * 64, "PIPE3_stream_processing", 0)
    assert result["status"] == "FAIL" and result["label"] == 0
    assert result["decision_complete"] and not result["coverage_complete"]
