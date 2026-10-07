from __future__ import annotations

from copy import deepcopy

from scripts.peerrolebench_independent_y_contract_v2 import (
    SCHEMA_VERSION,
    TERMINAL_SCORER_VERSION,
    canonical_digest,
    validate_independent_y,
)


def _sha(tag: str) -> str:
    return canonical_digest({"tag": tag})


def _context() -> dict:
    delivery = _sha("delivery")
    worker_input = _sha("worker-input")
    target = _sha("target-snapshot")
    response = _sha("response")
    holdout = _sha("holdout")
    return {
        "assignment_id": "assignment-arm",
        "selection_id": "selection-arm-1",
        "delivery_id": "arm-delivery-1",
        "candidate_key": "peer-b@v1",
        "assignment_event_index": 10,
        "selection_event_index": 11,
        "task_start_event_index": 12,
        "delivery_event_index": 13,
        "action_event_index": 16,
        "task_start_binding_digest": _sha("task-start-prefix"),
        "delivery_artifact_sha256": delivery,
        "action_input_sha256": delivery,
        "target_snapshot_sha256": target,
        "artifact_sha256": target,
        "worker_input_sha256": worker_input,
        "response_digest": response,
        "holdout_digest": holdout,
        "read_cut": 20,
    }


def _receipt(context: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "source": "independent_terminal_holdout",
        "scorer_version": TERMINAL_SCORER_VERSION,
        "episode_role": "target",
        "derived_from": [],
        "policy_visible": False,
        "feedback_id": "feedback-y-1",
        "assignment_id": context["assignment_id"],
        "selection_id": context["selection_id"],
        "delivery_id": context["delivery_id"],
        "task_start_binding_digest": context["task_start_binding_digest"],
        "delivery_artifact_sha256": context["delivery_artifact_sha256"],
        "action_input_sha256": context["action_input_sha256"],
        "target_snapshot_sha256": context["target_snapshot_sha256"],
        "artifact_sha256": context["artifact_sha256"],
        "worker_input_sha256": context["worker_input_sha256"],
        "response_digest": context["response_digest"],
        "holdout_digest": context["holdout_digest"],
        "status": "PASS",
        "label": 1,
        "quality_score": 1.0,
        "coverage_complete": True,
        "arrival_index": 18,
    }


def test_target_y_binds_post_action_snapshot_and_event_order():
    context = _context()
    receipt = _receipt(context)
    state = {"updates": 0, "weights": [0.5, 0.5]}
    before = deepcopy(state)
    result = validate_independent_y(receipt, context)
    assert result["valid"] is True
    assert result["policy_update_allowed"] is True
    assert state == before


def test_source_and_d_substitutions_are_unknown():
    context = _context()
    source = _receipt(context)
    source["episode_role"] = "source"
    assert validate_independent_y(source, context)["disposition"] == "UNKNOWN"
    derived = _receipt(context)
    derived["derived_from"] = ["D", "recipient"]
    assert validate_independent_y(derived, context)["disposition"] == "UNKNOWN"


def test_action_snapshot_and_order_mutations_are_rejected():
    context = _context()
    wrong_target = _receipt(context)
    wrong_target["target_snapshot_sha256"] = _sha("other-target")
    assert validate_independent_y(wrong_target, context)["disposition"] == "UNKNOWN"
    late_selection = _context()
    late_selection["selection_event_index"] = late_selection["task_start_event_index"] + 1
    assert validate_independent_y(_receipt(late_selection), late_selection)["disposition"] == "UNKNOWN"
    late = _receipt(context)
    late["arrival_index"] = 21
    assert validate_independent_y(late, context)["disposition"] == "UNKNOWN"


def test_duplicate_and_incomplete_feedback_fail_closed():
    context = _context()
    duplicate = _receipt(context)
    assert validate_independent_y(duplicate, context, seen_feedback_ids=["feedback-y-1"])["disposition"] == "UNKNOWN"
    incomplete = _receipt(context)
    incomplete["coverage_complete"] = False
    assert validate_independent_y(incomplete, context)["disposition"] == "UNKNOWN"
