import copy

from scripts.peerrolebench_independent_y_contract import (
    SCHEMA_VERSION,
    TERMINAL_SCORER_VERSION,
    TERMINAL_SOURCE,
    validate_independent_y,
)


def _sha(char):
    return char * 64


def _context():
    return {
        "assignment_id": "assignment-1",
        "selection_id": "selection-1",
        "task_start_id": "task-start-1",
        "delivery_id": "delivery-1",
        "artifact_sha256": _sha("a"),
        "worker_input_sha256": _sha("b"),
        "holdout_digest": _sha("c"),
        "candidate_key": "peer-b@v1",
        "read_cut": 9,
    }


def _receipt():
    return {
        "schema_version": SCHEMA_VERSION,
        "source": TERMINAL_SOURCE,
        "scorer_version": TERMINAL_SCORER_VERSION,
        "episode_role": "target",
        "derived_from": [],
        "policy_visible": False,
        "feedback_id": "y-1",
        "assignment_id": "assignment-1",
        "selection_id": "selection-1",
        "task_start_id": "task-start-1",
        "delivery_id": "delivery-1",
        "artifact_sha256": _sha("a"),
        "worker_input_sha256": _sha("b"),
        "holdout_digest": _sha("c"),
        "response_digest": _sha("d"),
        "status": "PASS",
        "label": 1,
        "quality_score": 1.0,
        "arrival_index": 8,
        "coverage_complete": True,
    }


def test_target_independent_y_is_eligible():
    result = validate_independent_y(_receipt(), _context())
    assert result["valid"] is True
    assert result["policy_update_allowed"] is True
    assert result["label"] == 1


def test_source_or_d_relabel_is_unknown():
    for mutation in ({"episode_role": "source"}, {"source": "downstream_adoption"}, {"derived_from": ["D"]}):
        receipt = _receipt(); receipt.update(mutation)
        result = validate_independent_y(receipt, _context())
        assert result["disposition"] == "UNKNOWN"
        assert result["policy_update_allowed"] is False


def test_assignment_and_digest_bindings_fail_closed():
    for field in ("assignment_id", "selection_id", "task_start_id", "delivery_id", "artifact_sha256", "worker_input_sha256", "holdout_digest"):
        receipt = _receipt()
        if field.endswith("sha256") or field == "holdout_digest":
            receipt[field] = _sha("e")
        else:
            receipt[field] = "wrong"
        result = validate_independent_y(receipt, _context())
        assert result["disposition"] == "UNKNOWN"
        assert result["policy_update_allowed"] is False


def test_unknown_partial_duplicate_and_late_do_not_update():
    for mutation, seen in (
        ({"status": "UNKNOWN", "label": None}, ()),
        ({"coverage_complete": False}, ()),
        ({}, ("y-1",)),
        ({"arrival_index": 10}, ()),
    ):
        receipt = _receipt(); receipt.update(mutation)
        result = validate_independent_y(receipt, _context(), seen_feedback_ids=seen)
        assert result["disposition"] == "UNKNOWN"
        assert result["policy_update_allowed"] is False
