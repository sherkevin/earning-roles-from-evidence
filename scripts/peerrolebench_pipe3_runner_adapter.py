"""PIPE3-specific material and action adapter for the future live runner.

The existing closed-loop runner is intentionally DIST1-specific.  This module
keeps PIPE3's source ownership and scorer views explicit without changing old
cards or silently routing a stream task through mqueue assumptions.  It never
calls an LLM and never executes candidate source.
"""
from __future__ import annotations

import ast
import copy
from typing import Any, Mapping

from peerrolebench_pipe3_material_adapter import digest_files


TASK_ID = "PIPE3_stream_processing"
PRODUCER_OWNED = ("producer.py",)
RECIPIENT_OWNED = ("processor.py",)
SUPPORT_READ_ONLY = ("models.py", "sink.py")
PUBLIC_FILES = (*PRODUCER_OWNED, *RECIPIENT_OWNED, *SUPPORT_READ_ONLY)
CONSUMER_ACTIONS = {"use", "repair", "independent_redo"}


def _copy_sources(value: Mapping[str, str], required: tuple[str, ...]) -> dict[str, str]:
    if set(value) != set(required) or not all(isinstance(text, str) for text in value.values()):
        raise ValueError(f"PIPE3 source snapshot must contain exactly {sorted(required)}")
    return copy.deepcopy(dict(value))


def validate_pipe3_sources(source_files: Mapping[str, str]) -> None:
    """Check shape and syntax only; execution remains inside the scorer sandbox."""
    if not set(source_files) <= set(PUBLIC_FILES):
        raise ValueError("PIPE3 source contains a path outside the public contract")
    for path, text in source_files.items():
        if not isinstance(text, str) or len(text.encode("utf-8")) > 64 * 1024:
            raise ValueError(f"PIPE3 source is not bounded text: {path}")
        ast.parse(text, filename=path)


def attach_pipe3_delivery(recipient_payload: Mapping[str, Any],
                          delivery: Mapping[str, str]) -> dict[str, Any]:
    """Attach only producer.py to the recipient's processor/support payload."""
    if recipient_payload.get("task_id") != TASK_ID or recipient_payload.get("role") != "recipient":
        raise ValueError("Expected a PIPE3 recipient payload")
    required = tuple(recipient_payload.get("required_delivery_paths", ()))
    if required != PRODUCER_OWNED or set(delivery) != set(PRODUCER_OWNED):
        raise ValueError("PIPE3 delivery must contain exactly producer.py")
    if not all(isinstance(text, str) for text in delivery.values()):
        raise ValueError("PIPE3 delivery source must be text")
    result = copy.deepcopy(dict(recipient_payload))
    result["source_files"] = _copy_sources(result["source_files"], RECIPIENT_OWNED + SUPPORT_READ_ONLY)
    result["source_files"].update(copy.deepcopy(dict(delivery)))
    result["required_delivery_paths"] = []
    result["ready_for_dispatch"] = True
    result["delivery_sha256"] = digest_files(delivery)
    validate_pipe3_sources(result["source_files"])
    return result


def prepare_pipe3_action(materials: Mapping[str, Any], delivery: Mapping[str, str], action: str) -> dict[str, Any]:
    """Prepare the recipient action view and its explicit write permissions.

    ``use`` can complete only processor.py. ``repair`` may revise the selected
    producer copy as a repair action, while the immutable pre-action producer
    digest remains the Qp subject. ``independent_redo`` starts from the original
    public producer/processor snapshot and is not treated as use of the delivery.
    """
    if action not in CONSUMER_ACTIONS:
        raise ValueError(f"Unsupported PIPE3 action: {action}")
    recipient_template = materials["agent_payloads"]["recipient"]
    attached = attach_pipe3_delivery(recipient_template, delivery)
    original = materials["agent_payloads"]["producer"]["source_files"]
    original = _copy_sources(original, PRODUCER_OWNED + SUPPORT_READ_ONLY)
    if action == "independent_redo":
        processor = attached["source_files"]["processor.py"]
        attached["source_files"] = {**original, "processor.py": processor}
        writable = set(RECIPIENT_OWNED)
        initialization = "original_public_template"
    elif action == "use":
        writable = set(RECIPIENT_OWNED)
        initialization = "selected_delivery_copy"
    else:
        writable = set(RECIPIENT_OWNED) | set(PRODUCER_OWNED)
        initialization = "selected_delivery_copy"
    attached["writable_paths"] = sorted(writable)
    attached.update({"consumer_action": action,
                     "action_initialization": initialization,
                     "input_source_sha256": digest_files(attached["source_files"]),
                     "prior_delivery_may_have_been_seen": True,
                     "independent_redo_is_blinded_control": False})
    validate_pipe3_sources(attached["source_files"])
    return attached


def validate_pipe3_action_result(action_payload: Mapping[str, Any],
                                 source_files: Mapping[str, str]) -> dict[str, Any]:
    """Validate a returned complete snapshot against the declared write set."""
    if action_payload.get("consumer_action") not in CONSUMER_ACTIONS:
        raise ValueError("Expected a PIPE3 action payload")
    initial = action_payload.get("source_files")
    if not isinstance(initial, Mapping) or set(source_files) != set(initial):
        raise ValueError("PIPE3 action result must contain the complete current snapshot")
    if not all(isinstance(text, str) for text in source_files.values()):
        raise ValueError("PIPE3 action result source must be text")
    if digest_files(initial) != action_payload.get("input_source_sha256"):
        raise ValueError("PIPE3 action input snapshot changed before validation")
    changed = sorted(path for path in initial if initial[path] != source_files[path])
    if set(changed) - set(action_payload.get("writable_paths", ())):
        raise ValueError("PIPE3 action changed a read-only source")
    validate_pipe3_sources(source_files)
    return {
        "consumer_action": action_payload["consumer_action"],
        "source_files": copy.deepcopy(dict(source_files)),
        "input_source_sha256": action_payload["input_source_sha256"],
        "output_source_sha256": digest_files(source_files),
        "delivery_sha256": action_payload.get("delivery_sha256"),
        "changed_paths": changed,
        "action_initialization": action_payload["action_initialization"],
        "prior_delivery_may_have_been_seen": True,
        "independent_redo_is_blinded_control": False,
    }


def producer_scorer_sources(materials: Mapping[str, Any], producer_source: Mapping[str, str]) -> dict[str, str]:
    """View for Qp: producer.py plus read-only models.py only."""
    if set(producer_source) != set(PRODUCER_OWNED):
        raise ValueError("PIPE3 producer delivery must contain exactly producer.py")
    support = materials["agent_payloads"]["producer"]["source_files"]
    return {"producer.py": producer_source["producer.py"], "models.py": support["models.py"]}


def recipient_scorer_sources(final_source: Mapping[str, str]) -> dict[str, str]:
    """View for Qr: processor.py plus read-only models.py."""
    return {path: final_source[path] for path in ("processor.py", "models.py")}


def adoption_scorer_sources(final_source: Mapping[str, str]) -> dict[str, str]:
    """View for final adoption: all public runtime files, excluding tests."""
    return {path: final_source[path] for path in PUBLIC_FILES}
