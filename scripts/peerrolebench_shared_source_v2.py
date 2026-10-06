"""Fail-closed shared-source projection contract.

This v2 seam is intentionally stricter than the historical v1 qualification:
the caller supplies an external source digest, source provenance is explicit,
projection digests are recomputed, denominator state is typed, and shared source
cost is counted once rather than once per policy arm.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from typing import Any, Iterable, Mapping


VERSION = "shared-source-projection-v2"
ARM_NAMES = ("no_update", "contextual_trust_linear", "RARE")
GATE_STATUSES = {"ELIGIBLE", "PENDING_ATTRIBUTION", "UNKNOWN"}
EPISODE_STATUSES = {"SOURCE_COMPLETE", "STOPPED_PRE_TARGET", "SOURCE_INCOMPLETE"}
TARGET_STATUSES = {"NOT_STARTED", "STARTED", "COMPLETED"}
FINGERPRINT_FIELDS = (
    "artifact_digest", "contract_digest", "registry_digest", "scorer_digest",
    "prompt_digest", "raw_response_digest",
)
_PROJECTION_FIELDS = {"projection_version", "policy_arm", "policy_namespace", "arm_projection_digest"}
_SEAL_FIELDS = {"source_receipt_digest"}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _is_digest(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _canonical_source_payload(source: Mapping[str, Any]) -> dict[str, Any]:
    payload = {key: deepcopy(value) for key, value in source.items() if key not in _PROJECTION_FIELDS | _SEAL_FIELDS}
    # The embedded seal is evidence about this payload, so its digest is excluded
    # from the payload being sealed.  The caller still has to provide the same
    # digest through the external manifest and the embedded field.
    if isinstance(payload.get("source_seal"), Mapping):
        payload["source_seal"].pop("source_digest", None)
    return payload


def canonical_source_digest(source: Mapping[str, Any]) -> str:
    """Digest the source payload without trusting any supplied seal field."""
    return _digest(_canonical_source_payload(source))


def _projection_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: deepcopy(value) for key, value in row.items() if key != "arm_projection_digest"}


def _validate_state(source: Mapping[str, Any]) -> None:
    gate_status = source["gate_status"]
    episode_status = source["episode_status"]
    target_status = source["target_status"]
    source_complete = source["source_complete"]
    target_started = source["target_started"]
    if gate_status not in GATE_STATUSES:
        raise ValueError(f"invalid gate_status: {gate_status!r}")
    if episode_status not in EPISODE_STATUSES:
        raise ValueError(f"invalid episode_status: {episode_status!r}")
    if target_status not in TARGET_STATUSES:
        raise ValueError(f"invalid target_status: {target_status!r}")
    if not isinstance(source_complete, bool) or not isinstance(target_started, bool):
        raise ValueError("source_complete and target_started must be booleans")
    if target_started != (target_status != "NOT_STARTED"):
        raise ValueError("target_started disagrees with target_status")
    if gate_status == "ELIGIBLE":
        if not source_complete or episode_status != "SOURCE_COMPLETE":
            raise ValueError("eligible source must be complete")
        if source["estimand_inclusion"] != "ITT_AND_ELIGIBLE":
            raise ValueError("eligible source must enter ITT_AND_ELIGIBLE")
    elif gate_status == "PENDING_ATTRIBUTION":
        if not source_complete or episode_status != "STOPPED_PRE_TARGET" or target_started:
            raise ValueError("pending attribution must stop before target after complete source")
        if source["estimand_inclusion"] != "ITT_ONLY":
            raise ValueError("pending attribution must remain ITT_ONLY")
    else:
        if source_complete or episode_status != "SOURCE_INCOMPLETE" or target_started:
            raise ValueError("unknown source must be incomplete and pre-target")
        if source["estimand_inclusion"] != "ITT_ONLY":
            raise ValueError("unknown source must remain ITT_ONLY")


def _validate_provenance(source: Mapping[str, Any]) -> None:
    provenance = source.get("provenance")
    if not isinstance(provenance, Mapping) or provenance.get("policy_invariant") is not True:
        raise ValueError("source provenance must explicitly be policy_invariant")
    for field in FINGERPRINT_FIELDS:
        if not _is_digest(provenance.get(field)):
            raise ValueError(f"missing or invalid provenance fingerprint: {field}")
    if source["delivery_digest"] != provenance["artifact_digest"]:
        raise ValueError("delivery_digest is not bound to artifact_digest")
    seal = source.get("source_seal")
    if not isinstance(seal, Mapping) or not seal.get("manifest_id"):
        raise ValueError("external source seal manifest_id is required")


def freeze_source_receipt(source: Mapping[str, Any], expected_source_digest: str) -> dict[str, Any]:
    """Validate a source against an externally supplied, immutable digest."""
    required = {
        "source_event_id", "task_id", "root", "seed", "delivery_digest",
        "judgment", "action", "producer_score", "outcome", "gate", "cost",
        "episode_status", "gate_status", "estimand_inclusion", "source_complete",
        "target_started", "target_status", "provenance", "source_seal",
        "source_receipt_digest",
    }
    missing = sorted(required - set(source))
    if missing:
        raise ValueError(f"shared source is missing fields: {missing}")
    if not _is_digest(expected_source_digest):
        raise ValueError("expected_source_digest must be an external sha256 seal")
    if not _is_digest(source["delivery_digest"]):
        raise ValueError("delivery_digest must be a sha256 string")
    computed = canonical_source_digest(source)
    if computed != expected_source_digest:
        raise ValueError("source payload does not match external source seal")
    if source["source_receipt_digest"] != computed:
        raise ValueError("source_receipt_digest does not match canonical payload")
    if source["source_seal"].get("source_digest") != expected_source_digest:
        raise ValueError("embedded source seal disagrees with external seal")
    _validate_state(source)
    _validate_provenance(source)
    cost = source["cost"]
    if not isinstance(cost, Mapping) or cost.get("source_cost_id") != source["source_event_id"]:
        raise ValueError("source cost must have a stable source_cost_id")
    for field in ("source_cost_units", "target_cost_units"):
        value = cost.get(field)
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"cost.{field} must be a finite non-negative number")
    receipt = deepcopy(dict(source))
    receipt["projection_version"] = VERSION
    return receipt


def project_source_to_arms(
    source: Mapping[str, Any], expected_source_digest: str,
    arms: Iterable[str] = ARM_NAMES,
) -> list[dict[str, Any]]:
    receipt = freeze_source_receipt(source, expected_source_digest)
    arm_list = list(arms)
    if not arm_list or any(not isinstance(arm, str) or not arm for arm in arm_list) or len(set(arm_list)) != len(arm_list):
        raise ValueError("arms must be non-empty, unique strings")
    rows = []
    for arm in arm_list:
        row = deepcopy(receipt)
        row["policy_arm"] = arm
        row["policy_namespace"] = f"source:{receipt['source_event_id']}:policy:{arm}"
        row["arm_projection_digest"] = _digest(_projection_payload(row))
        rows.append(row)
    return rows


def validate_cost_ledger(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [dict(row) for row in rows]
    if not rows:
        raise ValueError("at least one row is required for cost accounting")
    costs = [row["cost"] for row in rows]
    source_ids = {cost["source_cost_id"] for cost in costs}
    source_units = {cost["source_cost_units"] for cost in costs}
    if len(source_ids) != 1 or len(source_units) != 1:
        raise ValueError("shared source cost must be identical across arm projections")
    target_units = sum(cost["target_cost_units"] for cost in costs)
    return {
        "source_cost_id": next(iter(source_ids)),
        "source_cost_units_counted_once": next(iter(source_units)),
        "target_cost_units_sum": target_units,
        "arm_count": len(rows),
        "double_count_rejected": True,
    }


def validate_arm_projections(
    rows: Iterable[Mapping[str, Any]], expected_source_digest: str,
) -> dict[str, Any]:
    rows = [dict(row) for row in rows]
    if not rows:
        raise ValueError("at least one arm projection is required")
    frozen = freeze_source_receipt(rows[0], expected_source_digest)
    baseline = _canonical_source_payload(frozen)
    arms = []
    for row in rows:
        if _canonical_source_payload(row) != baseline:
            raise ValueError("shared source mutation detected")
        if row.get("source_receipt_digest") != expected_source_digest:
            raise ValueError("projection has an invalid source receipt digest")
        if row.get("projection_version") != VERSION:
            raise ValueError("projection version mismatch")
        arm = row.get("policy_arm")
        namespace = row.get("policy_namespace")
        if not isinstance(arm, str) or not arm or namespace != f"source:{row['source_event_id']}:policy:{arm}":
            raise ValueError("invalid policy namespace")
        if not _is_digest(row.get("arm_projection_digest")):
            raise ValueError("missing arm projection digest")
        if _digest(_projection_payload(row)) != row["arm_projection_digest"]:
            raise ValueError("arm projection digest mismatch")
        arms.append(arm)
    if len(set(arms)) != len(arms):
        raise ValueError("duplicate policy arm projection")
    cost = validate_cost_ledger(rows)
    return {
        "projection_version": VERSION,
        "source_receipt_digest": expected_source_digest,
        "arms": arms,
        "gate_status": frozen["gate_status"],
        "episode_status": frozen["episode_status"],
        "estimand_inclusion": frozen["estimand_inclusion"],
        "cost_ledger": cost,
        "valid": True,
    }


def validate_selection_binding(binding: Mapping[str, Any]) -> dict[str, Any]:
    """Contract-only check for the future policy→native selection bridge."""
    required = {
        "policy_decision_id", "native_selection_id", "decision_digest",
        "native_record_digest", "candidate_registry_digest", "policy_input_digest",
        "state_before_digest", "chosen_candidate", "candidate_menu", "propensity",
        "binding_digest",
    }
    missing = sorted(required - set(binding))
    if missing:
        raise ValueError(f"selection binding missing fields: {missing}")
    for field in ("decision_digest", "native_record_digest", "candidate_registry_digest", "policy_input_digest", "state_before_digest"):
        if not _is_digest(binding[field]):
            raise ValueError(f"invalid selection binding digest: {field}")
    if binding["chosen_candidate"] not in binding["candidate_menu"]:
        raise ValueError("chosen candidate is absent from candidate menu")
    propensity = binding["propensity"]
    if not isinstance(propensity, (int, float)) or not math.isfinite(propensity) or not 0 < propensity <= 1:
        raise ValueError("propensity must be in (0, 1]")
    payload = {key: deepcopy(value) for key, value in binding.items() if key != "binding_digest"}
    if _digest(payload) != binding["binding_digest"]:
        raise ValueError("selection binding digest mismatch")
    return {"valid": True, "binding_digest": binding["binding_digest"], "chosen_candidate": binding["chosen_candidate"]}


__all__ = [
    "VERSION", "ARM_NAMES", "canonical_source_digest", "freeze_source_receipt",
    "project_source_to_arms", "validate_arm_projections", "validate_cost_ledger",
    "validate_selection_binding",
]
