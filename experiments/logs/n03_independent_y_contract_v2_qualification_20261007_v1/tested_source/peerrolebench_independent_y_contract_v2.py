"""Fail-closed contract for an independent later terminal receipt.

Version 2 makes the live integration seam explicit.  The native ledger keeps
its historical adoption outcome for replay; this sidecar is the only object
that may represent the independent terminal signal.  The validator is pure:
it never executes a worker and never mutates policy state.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "pipe3-independent-y-contract-v2"
TERMINAL_SCORER_VERSION = "pipe3-terminal-holdout-v1"
TERMINAL_SOURCE = "independent_terminal_holdout"


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value.lower() != value:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest") from exc
    return value


def _unknown(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": False,
        "disposition": "UNKNOWN",
        "policy_update_allowed": False,
        "label": None,
        "quality_score": None,
        "reason": reason,
    }


def validate_independent_y(
    receipt: Mapping[str, Any],
    context: Mapping[str, Any],
    *,
    seen_feedback_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Validate one target-only Y sidecar without changing any state.

    The event-index checks are deliberately outside the old v1 contract.  A
    native task-start event has no opaque ID, so the parent binds it by its
    immutable event index and a context digest rather than inventing an ID.
    """
    try:
        if not isinstance(receipt, Mapping) or not isinstance(context, Mapping):
            return _unknown("receipt_or_context_not_object")
        if receipt.get("schema_version") != SCHEMA_VERSION:
            return _unknown("schema_version_mismatch")
        if receipt.get("source") != TERMINAL_SOURCE:
            return _unknown("source_is_not_independent_terminal")
        if receipt.get("scorer_version") != TERMINAL_SCORER_VERSION:
            return _unknown("terminal_scorer_version_mismatch")
        if receipt.get("episode_role") != "target":
            return _unknown("terminal_signal_requires_target_episode")
        if receipt.get("derived_from") != []:
            return _unknown("terminal_signal_must_not_be_derived")
        if receipt.get("policy_visible") is not False:
            return _unknown("raw_terminal_receipt_must_be_policy_invisible")
        feedback_id = receipt.get("feedback_id")
        if not isinstance(feedback_id, str) or not feedback_id:
            return _unknown("feedback_id_missing")
        if feedback_id in set(seen_feedback_ids):
            return _unknown("duplicate_terminal_feedback")

        for key in ("assignment_id", "selection_id", "delivery_id"):
            expected = context.get(key)
            if not isinstance(expected, str) or not expected:
                return _unknown(f"missing_context_{key}")
            if receipt.get(key) != expected:
                return _unknown(f"{key}_binding_mismatch")

        # Native task-start has no ID.  Bind it by index plus an immutable
        # parent-provided digest of the task-start event/prefix.
        for key in (
            "assignment_event_index", "selection_event_index", "task_start_event_index",
            "delivery_event_index", "action_event_index",
        ):
            value = context.get(key)
            if type(value) is not int or value < 0:
                return _unknown(f"{key}_invalid")
        if not (
            context["assignment_event_index"] < context["selection_event_index"]
            < context["task_start_event_index"] <= context["delivery_event_index"]
            < context["action_event_index"]
        ):
            return _unknown("native_event_order_invalid")
        _sha(context.get("task_start_binding_digest"), "task_start_binding_digest")
        if receipt.get("task_start_binding_digest") != context["task_start_binding_digest"]:
            return _unknown("task_start_binding_mismatch")

        for key in (
            "delivery_artifact_sha256", "action_input_sha256", "target_snapshot_sha256",
            "artifact_sha256", "worker_input_sha256", "response_digest", "holdout_digest",
        ):
            _sha(receipt.get(key), key)
            if receipt.get(key) != context.get(key):
                return _unknown(f"{key}_mismatch")
        # The worker must score the post-action snapshot, while retaining the
        # original delivery and action input as separate provenance fields.
        if receipt["artifact_sha256"] != receipt["target_snapshot_sha256"]:
            return _unknown("worker_artifact_is_not_target_snapshot")
        if receipt["action_input_sha256"] != receipt["delivery_artifact_sha256"]:
            return _unknown("action_input_is_not_delivery_snapshot")

        if receipt.get("status") not in {"PASS", "FAIL"}:
            return _unknown("terminal_status_unknown_or_incomplete")
        label = receipt.get("label")
        expected_label = 1 if receipt["status"] == "PASS" else 0
        if label != expected_label:
            return _unknown("terminal_label_status_mismatch")
        quality = receipt.get("quality_score")
        if (
            not isinstance(quality, (int, float)) or isinstance(quality, bool)
            or not math.isfinite(float(quality)) or not 0.0 <= float(quality) <= 1.0
        ):
            return _unknown("terminal_quality_score_invalid")
        arrival = receipt.get("arrival_index")
        read_cut = context.get("read_cut")
        if type(arrival) is not int or arrival < 0 or type(read_cut) is not int or read_cut < 0:
            return _unknown("terminal_arrival_or_read_cut_invalid")
        if arrival > read_cut:
            return _unknown("terminal_arrives_after_read_cut")
        if receipt.get("coverage_complete") is not True:
            return _unknown("terminal_coverage_incomplete")
    except (TypeError, ValueError, KeyError):
        return _unknown("terminal_receipt_field_invalid")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "disposition": "ELIGIBLE",
        "policy_update_allowed": True,
        "source": TERMINAL_SOURCE,
        "feedback_id": feedback_id,
        "candidate_key": context.get("candidate_key"),
        "label": int(receipt["label"]),
        "quality_score": float(receipt["quality_score"]),
        "arrival_index": arrival,
        "read_cut": read_cut,
        "receipt_digest": canonical_digest(dict(receipt)),
    }


__all__ = ["SCHEMA_VERSION", "TERMINAL_SCORER_VERSION", "TERMINAL_SOURCE",
           "canonical_digest", "validate_independent_y"]
