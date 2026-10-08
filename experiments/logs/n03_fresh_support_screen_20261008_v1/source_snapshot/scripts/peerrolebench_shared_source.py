"""Typed shared-source projection for the next bounded policy comparison.

One real source episode is acquired once, then projected into independent policy
namespaces.  The projection never lets an arm rewrite the source digest,
judgment/action/outcome, ownership gate, or acquisition cost.  This is an
engineering seam; it does not turn a shared source into an independent root.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Iterable, Mapping


VERSION = "shared-source-projection-v1"
ARM_NAMES = ("no_update", "contextual_trust_linear", "RARE")
GATE_STATUSES = {"ELIGIBLE", "PENDING_ATTRIBUTION", "UNKNOWN"}
EPISODE_STATUSES = {"SOURCE_COMPLETE", "STOPPED_PRE_TARGET"}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def freeze_source_receipt(source: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and deep-copy one source episode for arm projection."""
    required = {
        "source_event_id", "task_id", "root", "seed", "delivery_digest",
        "judgment", "action", "producer_score", "outcome", "gate", "cost",
        "episode_status", "gate_status", "estimand_inclusion",
    }
    missing = sorted(required - set(source))
    if missing:
        raise ValueError(f"shared source is missing fields: {missing}")
    gate_status = source["gate_status"]
    episode_status = source["episode_status"]
    if gate_status not in GATE_STATUSES:
        raise ValueError(f"invalid gate_status: {gate_status!r}")
    if episode_status not in EPISODE_STATUSES:
        raise ValueError(f"invalid episode_status: {episode_status!r}")
    if not isinstance(source["delivery_digest"], str) or len(source["delivery_digest"]) != 64:
        raise ValueError("delivery_digest must be a sha256 string")
    if gate_status == "ELIGIBLE" and episode_status != "SOURCE_COMPLETE":
        raise ValueError("eligible source must be complete")
    if gate_status == "PENDING_ATTRIBUTION" and source["estimand_inclusion"] != "ITT_ONLY":
        raise ValueError("PENDING_ATTRIBUTION source must remain ITT_ONLY")
    if gate_status == "UNKNOWN" and source["estimand_inclusion"] != "ITT_ONLY":
        raise ValueError("UNKNOWN source must remain ITT_ONLY")
    receipt = deepcopy(dict(source))
    receipt["projection_version"] = VERSION
    receipt["source_receipt_digest"] = _digest(receipt)
    return receipt


def project_source_to_arms(source: Mapping[str, Any], arms: Iterable[str] = ARM_NAMES) -> list[dict[str, Any]]:
    """Project an immutable source receipt into isolated policy namespaces."""
    receipt = freeze_source_receipt(source)
    arm_list = list(arms)
    if sorted(arm_list) != sorted(set(arm_list)) or not arm_list:
        raise ValueError("arms must be non-empty and unique")
    projections = []
    for arm in arm_list:
        if not isinstance(arm, str) or not arm:
            raise ValueError("arm name must be non-empty")
        row = deepcopy(receipt)
        row["policy_arm"] = arm
        row["policy_namespace"] = f"source:{receipt['source_event_id']}:policy:{arm}"
        row["arm_projection_digest"] = _digest(row)
        projections.append(row)
    return projections


def validate_arm_projections(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in rows]
    if not rows:
        raise ValueError("at least one arm projection is required")
    invariant_fields = (
        "source_event_id", "task_id", "root", "seed", "delivery_digest", "judgment",
        "action", "producer_score", "outcome", "gate", "cost", "episode_status",
        "gate_status", "estimand_inclusion", "source_receipt_digest",
    )
    baseline = {field: rows[0].get(field) for field in invariant_fields}
    for row in rows:
        for field, expected in baseline.items():
            if row.get(field) != expected:
                raise ValueError(f"shared source mutation in {field}")
        if not row.get("policy_arm") or not row.get("policy_namespace"):
            raise ValueError("arm projection lacks isolated policy namespace")
    arms = [row["policy_arm"] for row in rows]
    if len(set(arms)) != len(arms):
        raise ValueError("duplicate policy arm projection")
    return {
        "projection_version": VERSION,
        "source_receipt_digest": baseline["source_receipt_digest"],
        "arms": arms,
        "gate_status": baseline["gate_status"],
        "estimand_inclusion": baseline["estimand_inclusion"],
        "valid": True,
    }


__all__ = ["VERSION", "ARM_NAMES", "freeze_source_receipt", "project_source_to_arms", "validate_arm_projections"]
