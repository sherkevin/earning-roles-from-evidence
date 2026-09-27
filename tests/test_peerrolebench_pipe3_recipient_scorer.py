from __future__ import annotations

import copy
import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_recipient_scorer import (  # noqa: E402
    CHECKS, SCHEMA_VERSION, SCORER_VERSION, classify,
)


def response(mode="recipient", statuses=None):
    statuses = statuses or ["PASS"] * len(CHECKS[mode])
    checks = [{"id": check_id, "status": status}
              for check_id, status in zip(CHECKS[mode], statuses)]
    return {"ok": True, "value": {
        "schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
        "task_id": "PIPE3_stream_processing", "seed": 0, "mode": mode,
        "artifact_sha256": "a" * 64,
        "status": "PASS" if all(status == "PASS" for status in statuses) else "FAIL",
        "label": int(all(status == "PASS" for status in statuses)),
        "quality_score": sum(status == "PASS" for status in statuses) / len(statuses),
        "decision_complete": True, "coverage_complete": True,
        "checks": checks, "failed_check_ids": [item["id"] for item in checks if item["status"] == "FAIL"],
        "observed_check_count": len(checks), "required_check_ids": list(CHECKS[mode]),
    }}


def test_recipient_and_adoption_complete_responses_are_label_eligible():
    for mode in CHECKS:
        result = classify(response(mode), "a" * 64, "PIPE3_stream_processing", 0, mode)
        assert result["status"] == "PASS" and result["label"] == 1


def test_candidate_recipient_failure_is_a_determinate_negative():
    mutated = response("recipient", ["FAIL", "FAIL", "FAIL"])
    result = classify(mutated, "a" * 64, "PIPE3_stream_processing", 0, "recipient")
    assert result["status"] == "FAIL" and result["label"] == 0


def test_unknown_or_digest_mutation_cannot_be_used_as_a_label():
    mutated = copy.deepcopy(response("adoption"))
    mutated["value"]["decision_complete"] = False
    assert classify(mutated, "a" * 64, "PIPE3_stream_processing", 0, "adoption")["status"] == "UNKNOWN"
    mutated = copy.deepcopy(response("adoption"))
    mutated["value"]["artifact_sha256"] = "b" * 64
    assert classify(mutated, "a" * 64, "PIPE3_stream_processing", 0, "adoption")["status"] == "UNKNOWN"
