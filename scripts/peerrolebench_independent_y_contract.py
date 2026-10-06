"""Fail-closed contract for a later target-task terminal signal.

This module validates provenance only.  It does not run a scorer, execute
candidate code, or update a policy.  The private terminal worker must supply a
versioned holdout digest and a response digest; the public policy can receive a
label only after the source-to-target assignment binding is complete.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "pipe3-independent-y-contract-v1"
TERMINAL_SCORER_VERSION = "pipe3-terminal-holdout-v1"
TERMINAL_SOURCE = "independent_terminal_holdout"


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


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
    """Validate one later target terminal receipt without changing state.

    ``context`` is sealed by the parent before the worker runs.  It contains
    the target assignment/selection/task-start identifiers, target artifact
    digest, and the expected hidden holdout digest.  A source episode or a D
    receipt is never eligible, even when its label is determinate.
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
        if receipt.get("feedback_id") in set(seen_feedback_ids):
            return _unknown("duplicate_terminal_feedback")
        expected_ids = {
            "assignment_id": context.get("assignment_id"),
            "selection_id": context.get("selection_id"),
            "task_start_id": context.get("task_start_id"),
            "delivery_id": context.get("delivery_id"),
        }
        for key, expected in expected_ids.items():
            if not isinstance(expected, str) or not expected:
                return _unknown(f"missing_context_{key}")
            if receipt.get(key) != expected:
                return _unknown(f"{key}_binding_mismatch")
        _sha(receipt.get("artifact_sha256"), "artifact_sha256")
        _sha(receipt.get("worker_input_sha256"), "worker_input_sha256")
        _sha(receipt.get("response_digest"), "response_digest")
        if receipt["artifact_sha256"] != context.get("artifact_sha256"):
            return _unknown("target_artifact_digest_mismatch")
        if receipt["worker_input_sha256"] != context.get("worker_input_sha256"):
            return _unknown("terminal_worker_input_digest_mismatch")
        if receipt.get("holdout_digest") != context.get("holdout_digest"):
            return _unknown("holdout_digest_mismatch")
        if receipt.get("status") not in {"PASS", "FAIL"}:
            return _unknown("terminal_status_unknown_or_incomplete")
        label = receipt.get("label")
        expected_label = 1 if receipt["status"] == "PASS" else 0
        if label != expected_label:
            return _unknown("terminal_label_status_mismatch")
        quality = receipt.get("quality_score")
        if not isinstance(quality, (int, float)) or isinstance(quality, bool) or not math.isfinite(float(quality)) or not 0.0 <= float(quality) <= 1.0:
            return _unknown("terminal_quality_score_invalid")
        arrival = receipt.get("arrival_index")
        read_cut = context.get("read_cut")
        if type(arrival) is not int or arrival < 0 or type(read_cut) is not int or read_cut < 0:
            return _unknown("terminal_arrival_or_read_cut_invalid")
        if arrival > read_cut:
            return _unknown("terminal_arrives_after_read_cut")
        if not receipt.get("coverage_complete") is True:
            return _unknown("terminal_coverage_incomplete")
    except (TypeError, ValueError, KeyError):
        return _unknown("terminal_receipt_field_invalid")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "disposition": "ELIGIBLE",
        "policy_update_allowed": True,
        "source": TERMINAL_SOURCE,
        "feedback_id": receipt["feedback_id"],
        "candidate_key": context.get("candidate_key"),
        "label": int(receipt["label"]),
        "quality_score": float(receipt["quality_score"]),
        "arrival_index": arrival,
        "read_cut": read_cut,
        "receipt_digest": _digest(dict(receipt)),
    }


__all__ = ["SCHEMA_VERSION", "TERMINAL_SCORER_VERSION", "TERMINAL_SOURCE", "validate_independent_y"]
