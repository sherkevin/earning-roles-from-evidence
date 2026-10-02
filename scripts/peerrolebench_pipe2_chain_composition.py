"""Minimal PIPE2 ledger composition for the next responsibility decision.

This module composes the already qualified responsibility gate with the typed
peer-role ledger.  It uses authored control payloads and never calls a model or
executes candidate code; the purpose is to catch ordering, digest, assignment
and no-label failures before a live runner is attempted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from peerrolebench_pipe2_derived_material_adapter import build_derived_materials, load_derived_pipe2
from peerrolebench_pipe2_responsibility_label import evaluate_pipe2_feedback

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ROOT = ROOT / "references/aamas"
if str(PROTOCOL_ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(PROTOCOL_ROOT))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    ProducerScore,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)


TASK_ID = "PIPE2_data_pipeline"
CHAIN_VERSION = "pipe2-responsibility-chain-v1"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _artifact(seed: int, variant: str) -> str:
    return hashlib.sha256(f"{TASK_ID}:{seed}:{variant}".encode()).hexdigest()


def compose_pipe2_chain(seed: int = 0, *, variant: str = "eligible") -> dict[str, Any]:
    """Compose one authored PIPE2 chain and return a serializable receipt."""
    generated = load_derived_pipe2(seed)
    materials = build_derived_materials(seed)
    root_digest = str(generated.metadata["derived_root_digest"])
    artifact_sha256 = _artifact(seed, variant)
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)

    selection = PeerSelection(
        "pipe2-selection-0", TASK_ID, 0, "recipient-0", "producer",
        ("producer-a", "producer-b"), "producer-a", 0.5,
    )
    ledger.record_selection(selection)
    ledger.record_task_start(TASK_ID, 0)
    delivery = Delivery(
        "pipe2-delivery-0", TASK_ID, "producer-a", "recipient-0", artifact_sha256,
        selection.selection_id, 0, selection.selection_id, root_digest,
    )
    ledger.record_delivery(delivery)

    accepted = variant == "eligible"
    mixed = variant == "mixed"
    decision = "accept" if accepted else "accept_with_rework"
    action_name = "use" if accepted else "repair"
    changed = [] if accepted else ["pipeline/extract.py", "pipeline/transform.py"] if mixed else ["pipeline/transform.py"]
    producer_score = {
        "status": "PASS", "label": 1, "quality_score": 1.0,
        "coverage_complete": True, "decision_complete": True,
        "artifact_sha256": artifact_sha256,
    }
    producer_score_event = ProducerScore(
        "pipe2-producer-score-0", delivery.delivery_id, artifact_sha256,
        "pipe2-producer-objective-v1", "PASS", 1, 1.0, "c" * 64, True, True,
    )
    ledger.record_producer_score(producer_score_event)
    judgment_event = RecipientJudgment(
        "pipe2-judgment-0", delivery.delivery_id, "recipient-0", decision,
        artifact_sha256, False, "authored control",
    )
    ledger.record_judgment(judgment_event)
    action_event = ConsumerAction(
        "pipe2-action-0", delivery.delivery_id, "recipient-0", True,
        artifact_sha256, artifact_sha256, 0.0 if accepted else 1.0, action_name,
    )
    ledger.record_action(action_event)
    outcome_event = TerminalOutcome(
        "pipe2-outcome-0", delivery.delivery_id, True,
        "pipe2-recipient-objective-v1", 1.0, "d" * 64,
    )
    ledger.record_outcome(outcome_event)

    # The gate and the typed ledger must describe the same sealed facts.  Keep
    # this check in the composition itself so a future live runner cannot
    # silently score a dict that differs from the event it records.
    if producer_score_event.artifact_sha256 != producer_score["artifact_sha256"]:
        raise ValueError("producer score digest differs between ledger and gate input")
    if producer_score_event.status != producer_score["status"]:
        raise ValueError("producer score status differs between ledger and gate input")
    if judgment_event.decision != decision or judgment_event.observed_artifact_sha256 != artifact_sha256:
        raise ValueError("recipient judgment differs between ledger and gate input")
    if (action_event.action != action_name
            or action_event.used_artifact != (action_name in {"use", "repair"})
            or action_event.input_artifact_sha256 != artifact_sha256):
        raise ValueError("consumer action differs between ledger and gate input")
    if outcome_event.delivery_id != delivery.delivery_id or not outcome_event.success:
        raise ValueError("terminal outcome differs between ledger and gate input")

    gate = evaluate_pipe2_feedback(
        materials,
        artifact_sha256=artifact_sha256,
        producer_score=producer_score,
        judgment={
            "decision": decision, "target_role": "producer",
            "observed_artifact_sha256": artifact_sha256,
            "coverage_complete": True, "decision_complete": True,
        },
        action={
            "consumer_action": action_name, "changed_paths": changed,
            "delivery_sha256": artifact_sha256, "used_artifact": True,
        },
        outcome={
            "status": "PASS", "artifact_sha256": artifact_sha256,
            "coverage_complete": True, "decision_complete": True,
        },
    )
    evidence_recorded = False
    assignment_recorded = False
    next_selection_recorded = False
    if gate["feedback_eligible"]:
        ledger.record_evidence_update(RoleEvidenceUpdate(
            "pipe2-evidence-0", judgment_event.judgment_id, action_event.action_id,
            outcome_event.outcome_id, "pipe2-evidence-v1", 4.0,
        ))
        evidence_recorded = True
        ledger.record_assignment(LaterAssignment(
            "pipe2-assignment-1", TASK_ID, 1, "producer-a", "producer",
            ("pipe2-evidence-0",), 0.7,
        ))
        assignment_recorded = True
        next_selection = PeerSelection(
            "pipe2-selection-1", TASK_ID, 1, "recipient-1", "producer",
            ("producer-a", "producer-b"), "producer-a", 0.7,
        )
        ledger.record_selection(next_selection)
        ledger.record_task_start(TASK_ID, 1)
        next_selection_recorded = True

    return {
        "chain_version": CHAIN_VERSION,
        "task_id": TASK_ID,
        "seed": seed,
        "variant": variant,
        "material_root_digest": root_digest,
        "artifact_sha256": artifact_sha256,
        "gate": gate,
        "evidence_recorded": evidence_recorded,
        "assignment_recorded": assignment_recorded,
        "next_selection_recorded": next_selection_recorded,
        "ledger_snapshot": ledger.snapshot(),
        "ledger_event_digest": _digest(ledger.events),
        "ledger_event_types": [event["event_type"] for event in ledger.events],
        "ledger_event_hashes": [event["record_hash"] for event in ledger.events],
        "scientific_claim_allowed": False,
    }


__all__ = ["CHAIN_VERSION", "compose_pipe2_chain"]
