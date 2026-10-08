"""Join the offline PIPE1 adapter with a route receipt before preflight.

This is a zero-call consistency gate.  It deliberately does not replace the
route receipt validator or native-material preflight, and it never enables a
policy update.  Its purpose is to reject two individually valid objects whose
task or allocation facts disagree.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from peerrolebench_pipe1_route_receipt import validate_pipe1_route_receipt
from peerrolebench_pipe3_live_contract import unknown_no_update


VERSION = "pipe1-adapter-route-join-v2"


def _fail(errors: list[str]) -> dict[str, Any]:
    update = unknown_no_update(
        state_before="adapter-route-join-before",
        state_after="adapter-route-join-before",
        reason="; ".join(errors),
    )
    return {
        "schema": VERSION,
        "status": "UNKNOWN",
        "valid": False,
        "route_valid": False,
        "policy_update_allowed": False,
        "errors": errors,
        "update_boundary": update,
    }


def validate_adapter_route_join(
    *, adapter_result: Mapping[str, Any], route_receipt: Mapping[str, Any],
    native_events: Sequence[Mapping[str, Any]] | None = None,
    adapter_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Require one allocation and re-bind the result to its native ledger.

    A serialized adapter result is not an attestation: a caller can edit its
    nested selection/evidence fields after the adapter ran.  Therefore a
    ``READY_FOR_PREFLIGHT`` result is only possible when the original event
    rows and the exact adapter request are supplied and produce the same
    binding-critical projection.  Missing revalidation inputs fail closed.
    """
    errors: list[str] = []
    if not isinstance(adapter_result, Mapping):
        return _fail(["adapter result must be an object"])
    if adapter_result.get("schema") != "pipe1-offline-adapter-v1":
        errors.append("adapter schema is unsupported")
    if adapter_result.get("status") != "READY_FOR_ROUTE" or adapter_result.get("route_ready") is not True:
        errors.append("adapter is not READY_FOR_ROUTE")
    if adapter_result.get("policy_update_allowed") is not False:
        errors.append("adapter policy_update_allowed must remain false")
    binding = adapter_result.get("selection_binding")
    if not isinstance(binding, Mapping) or binding.get("valid") is not True:
        errors.append("native selection binding is not valid")
    schedule = adapter_result.get("schedule")
    if not isinstance(schedule, Mapping) or schedule.get("valid") is not True:
        errors.append("source-target schedule is not valid")

    if not isinstance(native_events, Sequence) or isinstance(native_events, (str, bytes)):
        errors.append("native event rows are required for adapter revalidation")
    if not isinstance(adapter_request, Mapping):
        errors.append("adapter request is required for adapter revalidation")
    else:
        # Keep the request surface explicit.  Extra fields could silently
        # change the meaning of the recomputation without being audited.
        expected_request = {
            "task_id", "source_task_index", "target_task_index", "evidence_id",
            "assignment_id", "target_selection_id", "registry", "menu_keys",
            "chosen_key", "probabilities", "chosen_index", "propensity",
        }
        if set(adapter_request) != expected_request:
            errors.append("adapter request keys are not the frozen revalidation contract")
        elif isinstance(native_events, Sequence) and not isinstance(native_events, (str, bytes)):
            try:
                from peerrolebench_pipe1_offline_adapter import validate_source_target_fixture
                recomputed = validate_source_target_fixture(
                    events=native_events, **dict(adapter_request),
                )
            except (TypeError, ValueError, AttributeError, KeyError) as exc:
                recomputed = None
                errors.append(f"native adapter revalidation failed: {type(exc).__name__}: {exc}")
            if recomputed is not None:
                # These fields contain the complete identity and lineage join;
                # comparing only status would leave evidence/peer swaps
                # undetected.
                for field in (
                    "status", "route_ready", "policy_update_allowed", "task_ids",
                    "selection_input", "selection_binding", "schedule", "ledger",
                ):
                    if recomputed.get(field) != adapter_result.get(field):
                        errors.append(f"adapter field {field!r} differs from native recomputation")

    try:
        route_check = validate_pipe1_route_receipt(route_receipt)
    except (TypeError, ValueError, AttributeError) as exc:
        route_check = {"valid": False, "errors": [f"{type(exc).__name__}: {exc}"]}
    if route_check.get("valid") is not True:
        errors.append("route receipt validation failed")

    source = route_receipt.get("source") if isinstance(route_receipt, Mapping) else None
    target = route_receipt.get("target") if isinstance(route_receipt, Mapping) else None
    task_id = adapter_result.get("task_ids")
    if not isinstance(task_id, list) or len(task_id) != 1:
        errors.append("adapter must expose exactly one task id")
    else:
        task_id = task_id[0]
        for role, material in (("source", source), ("target", target)):
            if not isinstance(material, Mapping) or material.get("task_id") != task_id:
                errors.append(f"route {role} task id differs from adapter")

    selection_input = adapter_result.get("selection_input")
    allocation = route_receipt.get("allocation") if isinstance(route_receipt, Mapping) else None
    registry = route_receipt.get("candidate_registry") if isinstance(route_receipt, Mapping) else None
    if not isinstance(selection_input, Mapping) or not isinstance(allocation, Mapping) or not isinstance(registry, Mapping):
        errors.append("selection input, allocation, and registry are required")
    else:
        menu = selection_input.get("menu_keys")
        candidates = registry.get("candidates")
        route_keys = [f"{row.get('candidate_id')}@{row.get('version')}" for row in candidates] if isinstance(candidates, list) else []
        if menu != route_keys:
            errors.append("route registry order differs from adapter menu")
        if allocation.get("permutation") != menu:
            errors.append("route allocation permutation differs from adapter menu")
        if allocation.get("chosen") != selection_input.get("chosen_key"):
            errors.append("route chosen candidate differs from adapter")
        probabilities = selection_input.get("probabilities")
        if not isinstance(probabilities, list) or len(probabilities) != len(route_keys):
            errors.append("adapter probability vector is invalid")
        else:
            expected = {key: float(value) for key, value in zip(route_keys, probabilities)}
            actual = allocation.get("probabilities")
            if not isinstance(actual, Mapping) or any(abs(float(actual.get(key, -1)) - value) > 1e-12 for key, value in expected.items()):
                errors.append("route probabilities differ from adapter")
            actual_props = allocation.get("propensities")
            if not isinstance(actual_props, Mapping) or abs(float(actual_props.get(selection_input.get("chosen_key"), -1)) - float(selection_input.get("propensity", -2))) > 1e-12:
                errors.append("route chosen propensity differs from adapter")

    if errors:
        result = _fail(errors)
        result["route_check"] = route_check
        return result
    return {
        "schema": VERSION,
        "status": "READY_FOR_PREFLIGHT",
        "valid": True,
        "route_valid": True,
        "policy_update_allowed": False,
        "errors": [],
        "route_check": route_check,
        "update_boundary": {
            "status": "READY_FOR_PREFLIGHT",
            "state_unchanged": True,
            "label": None,
            "assignment_created": False,
            "target_selection_created": False,
            "policy_update_allowed": False,
        },
    }


__all__ = ["VERSION", "validate_adapter_route_join"]
