"""Bind diagnostic terminal measurements to actual PIPE3 execution artifacts.

The original v2 dictionary-only qualification is preserved in its log directory.
This revision replays the native ledger and hashes actual input/output files.
It observes Y for every arm, but never invents a LaterAssignment or policy
update. Online credit requires a separately qualified adapter.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from peerrolebench_ledger_replay import replay_ledger_events
from peerrolebench_pipe3_material_adapter import digest_files
from peerrolebench_pipe3_runner_adapter import validate_pipe3_action_result, PUBLIC_FILES


SCHEMA_VERSION = "pipe3-independent-y-contract-v2"
BINDING_VERSION = "pipe3-y-native-artifact-binding-v1"
TERMINAL_SOURCE = "independent_terminal_holdout"


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def _sha(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 64 or value.lower() != value:
        raise ValueError("expected lowercase sha256")
    int(value, 16)
    return value


def bind_episode(ledger_events, delivery_id: str, action_payload, final_sources) -> dict:
    """Verify ledger order plus the producer subset of the four-file input.

    The structural prefix may end at the action: legacy terminal completeness
    is not a prerequisite for independently measuring its output snapshot.
    Invalid hash chains and state-machine transitions always raise.
    """
    replay = replay_ledger_events(ledger_events, allow_incomplete=True)
    ledger = replay.ledger
    delivery = ledger.deliveries[delivery_id]
    selection = ledger.selections[delivery.selection_id]
    action = next(a for a in ledger.actions.values() if a.delivery_id == delivery_id)
    if set(action_payload["source_files"]) != set(PUBLIC_FILES) or set(final_sources) != set(PUBLIC_FILES):
        raise ValueError("expected complete four-file snapshots")
    result = validate_pipe3_action_result(action_payload, final_sources)
    if action_payload.get("delivery_sha256") != delivery.artifact_sha256:
        raise ValueError("action delivery reference mismatch")
    # An independent redo is permitted to start from a different producer.
    # For use/repair the producer slice must equal the original delivery.
    if action.action != "independent_redo" and digest_files({
        "producer.py": action_payload["source_files"]["producer.py"]
    }) != delivery.artifact_sha256:
        raise ValueError("delivered producer subset mismatch")
    if (action.action != result["consumer_action"]
            or action.used_artifact != (action.action != "independent_redo")
            or action.input_artifact_sha256 != delivery.artifact_sha256
            or action.output_artifact_sha256 != result["output_source_sha256"]):
        raise ValueError("action snapshot/native record mismatch")

    def locate(kind, field, value):
        rows = [(i, r) for i, r in enumerate(ledger_events)
                if r["event_type"] == kind and r["payload"].get(field) == value]
        if len(rows) != 1:
            raise ValueError("missing or ambiguous event")
        return rows[0]

    si, se = locate("peer_selection", "selection_id", selection.selection_id)
    ti = ledger.started_tasks[(delivery.task_id, delivery.task_index)]
    te = ledger_events[ti]
    di, de = locate("producer_delivery", "delivery_id", delivery_id)
    ai, ae = locate("consumer_action", "action_id", action.action_id)
    if not si < ti < di < ai:
        raise ValueError("selection/start/delivery/action order mismatch")
    assignments = [a for a in ledger.assignments.values()
                   if (a.task_id, a.task_index) == (delivery.task_id, delivery.task_index)]
    if len(assignments) > 1:
        raise ValueError("ambiguous assignment")
    assignment = assignments[0] if assignments else None
    assignment_event = None
    if assignment:
        asi, assignment_event = locate("later_assignment", "assignment_id", assignment.assignment_id)
        if not asi < si or assignment.agent_id != selection.chosen_peer_id:
            raise ValueError("assignment/selection mismatch")
    binding = {
        "binding_version": BINDING_VERSION,
        "task_id": delivery.task_id, "task_index": delivery.task_index,
        "delivery_id": delivery_id, "selection_id": selection.selection_id,
        "action_id": action.action_id,
        "assignment_id": assignment.assignment_id if assignment else None,
        "assignment_bound": assignment is not None,
        "assignment_record_hash": assignment_event["record_hash"] if assignment else None,
        "candidate_id": selection.chosen_peer_id,
        "ledger_action_prefix_hash": ae["record_hash"],
        "selection_record_hash": se["record_hash"],
        "task_start_record_hash": te["record_hash"],
        "delivery_record_hash": de["record_hash"],
        "task_start_event_index": ti,
        "delivery_artifact_sha256": delivery.artifact_sha256,
        "action_input_sha256": result["input_source_sha256"],
        "target_snapshot_sha256": result["output_source_sha256"],
        "action": action.action, "used_artifact": action.used_artifact,
    }
    binding["binding_digest"] = canonical_digest(binding)
    return binding


def _unknown(reason):
    return {"schema_version": SCHEMA_VERSION, "valid": False,
            "disposition": "UNKNOWN", "policy_update_allowed": False,
            "label": None, "quality_score": None, "reason": reason}


def validate_independent_y(receipt: Mapping[str, Any], context: Mapping[str, Any], *,
                           seen_feedback_ids: Sequence[str] = ()) -> dict:
    """Recompute receipt bindings using parent-owned raw artifacts.

    This is a diagnostic bridge, not an online learning permission. Scorer
    results and raw requests in context come from the separately validated
    terminal adapter. Feedback clocks are optional for retrospective scoring;
    retrospective labels can never be backdated into a historical read cut.
    """
    try:
        if not isinstance(receipt, Mapping) or not isinstance(context, Mapping):
            return _unknown("receipt_or_context_not_object")
        if receipt.get("schema_version") != SCHEMA_VERSION or receipt.get("source") != TERMINAL_SOURCE:
            return _unknown("schema_or_source_mismatch")
        if receipt.get("derived_from") != [] or receipt.get("policy_visible") is not False:
            return _unknown("derived_or_policy_visible_measurement")
        feedback_id = receipt.get("feedback_id")
        if not isinstance(feedback_id, str) or not feedback_id:
            return _unknown("feedback_id_missing")
        if feedback_id in set(seen_feedback_ids):
            return _unknown("duplicate_terminal_feedback")
        binding = bind_episode(context["ledger_events"], receipt["delivery_id"],
                               context["action_payload"], context["final_sources"])
        if receipt.get("binding") != binding:
            return _unknown("native_artifact_binding_mismatch")
        expected_role = "source" if binding["task_index"] == 0 else "target"
        if receipt.get("episode_role") != expected_role:
            return _unknown("episode_role_mismatch")
        request = context["worker_request"]
        score = context["scorer_result"]
        if score.get("response_digest") != canonical_digest(context["raw_response"]):
            return _unknown("raw_response_digest_mismatch")
        if request["artifact_sha256"] != binding["target_snapshot_sha256"]:
            return _unknown("worker_did_not_score_action_output")
        if request["task_id"] != binding["task_id"] or request["seed"] != context["execution_seed"]:
            return _unknown("worker_task_mismatch")
        input_digest = canonical_digest({k: v for k, v in request.items() if k != "worker_input_sha256"})
        if request.get("worker_input_sha256") != input_digest:
            return _unknown("request_self_digest_mismatch")
        for key, expected in {
            "artifact_sha256": binding["target_snapshot_sha256"],
            "worker_input_sha256": input_digest,
            "holdout_digest": context["holdout_digest"],
            "response_digest": score.get("response_digest"),
        }.items():
            _sha(expected)
            if receipt.get(key) != expected or score.get(key) != expected:
                return _unknown(key + "_mismatch")
        if request["holdout_digest"] != context["holdout_digest"]:
            return _unknown("request_holdout_mismatch")
        if receipt.get("scorer_version") != request.get("scorer_version") or score.get("scorer_version") != request.get("scorer_version"):
            return _unknown("scorer_version_mismatch")
        if score.get("status") not in {"PASS", "FAIL"} or score.get("coverage_complete") is not True:
            return _unknown("terminal_score_unknown_or_incomplete")
        for key in ("status", "label", "quality_score", "coverage_complete"):
            if receipt.get(key) != score.get(key):
                return _unknown("score_field_mismatch_" + key)
        if type(receipt.get("label")) is not int or receipt["label"] != int(receipt["status"] == "PASS"):
            return _unknown("terminal_label_invalid")
        quality = receipt["quality_score"]
        if type(quality) not in (int, float) or not math.isfinite(quality) or not 0 <= quality <= 1:
            return _unknown("quality_invalid")
        mode = context.get("mode")
        if mode == "posthoc":
            if receipt.get("arrival_index") is not None:
                return _unknown("posthoc_feedback_must_not_be_backdated")
        elif mode == "online_diagnostic":
            arrival, before, after = receipt.get("arrival_index"), context.get("selection_read_cut"), context.get("feedback_read_cut")
            if any(type(x) is not int or x < 0 for x in (arrival, before, after)) or not before < arrival <= after:
                return _unknown("feedback_clock_invalid_or_not_available")
        else:
            return _unknown("unsupported_observation_mode")
        if receipt.get("mode") != mode:
            return _unknown("mode_mismatch")
    except (TypeError, ValueError, KeyError, StopIteration, AttributeError, OverflowError):
        return _unknown("invalid_native_artifacts_or_receipt")
    return {"schema_version": SCHEMA_VERSION, "valid": True,
            "disposition": "VALID_MEASUREMENT", "policy_update_allowed": False,
            "assignment_bound": binding["assignment_bound"],
            "credit_created": False, "mode": mode,
            "feedback_id": feedback_id, "label": receipt["label"],
            "quality_score": float(quality), "receipt_digest": canonical_digest(receipt),
            "reason": "diagnostic measurement only; independent online credit adapter not promoted"}


def make_diagnostic_receipt(context: Mapping[str, Any], *, delivery_id: str,
                            feedback_id: str) -> dict:
    binding = bind_episode(context["ledger_events"], delivery_id,
                           context["action_payload"], context["final_sources"])
    score = context["scorer_result"]
    return {"schema_version": SCHEMA_VERSION, "source": TERMINAL_SOURCE,
            "derived_from": [], "policy_visible": False, "mode": "posthoc",
            "arrival_index": None, "feedback_id": feedback_id, "delivery_id": delivery_id,
            "episode_role": "source" if binding["task_index"] == 0 else "target",
            "binding": binding,
            **{key: score.get(key) for key in ("scorer_version", "artifact_sha256",
               "worker_input_sha256", "holdout_digest", "response_digest", "status",
               "label", "quality_score", "coverage_complete")}}
