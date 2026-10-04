"""Build and append one canonical peer-history row after target credit.

This adapter is intentionally a thin boundary around the existing PIPE3
ledger, role-evidence offer, delayed-credit object, and ``PeerHistoryV1``
store.  It does not choose a peer, score an artifact, or update a policy.  A
caller must pass a successful ``LaterCredit`` and the already sealed target
assignment/selection; otherwise construction fails closed.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from peerrolebench_peer_history import (
    AssignmentSealV1,
    HistoryCostV1,
    HistoryEntryV1,
    PeerHistoryV1,
)
from peerrolebench_peer_history_binding import (
    HistoryBindingReceiptV1,
    build_history_binding_receipt,
)
from peerrolebench_role_evidence_offer import RoleEvidenceOffer
from peerrolebench_two_stage_gate import DelayedCreditLedger, LaterCredit


VERSION = "peer-history-canonical-adapter-v1"
JUDGMENT_LABELS = {
    "accept": 1.0,
    "accept_with_rework": 0.5,
    "reject_redo": 0.0,
}


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _scope_hashes(*, offer: RoleEvidenceOffer, assignment: Any,
                  target_selection: Any, candidate_key: str) -> tuple[str, str]:
    role_signature_hash = _digest({
        "task_id": offer.task_id,
        "role": offer.role,
        "context_key": offer.context_key,
        "candidate_registry_digest": offer.candidate_registry_digest,
    })
    execution_state_fingerprint = _digest({
        "assignment_id": assignment.assignment_id,
        "task_index": int(assignment.task_index),
        "candidate_key": candidate_key,
        "selection_id": target_selection.selection_id,
        "propensity": float(target_selection.propensity),
    })
    return role_signature_hash, execution_state_fingerprint


def _build_entry(*, ledger: Any, offer: RoleEvidenceOffer, assignment: Any,
                 target_selection: Any, target_outcome_id: str,
                 candidate_key: str, target_arrival_index: int,
                 cost: HistoryCostV1) -> HistoryEntryV1:
    if len(offer.evidence_ids) != 1:
        raise ValueError("history adapter requires exactly one source evidence row")
    source_evidence_id = offer.evidence_ids[0]
    source_row = next((row for row in offer.public_evidence
                       if row["evidence_id"] == source_evidence_id), None)
    if source_row is None:
        raise ValueError("source evidence row is missing")
    source_judgment = ledger.judgments.get(str(source_row["judgment_id"]))
    if source_judgment is None:
        raise ValueError("source recipient judgment is missing")
    if source_judgment.decision not in JUDGMENT_LABELS:
        raise ValueError("source recipient judgment has no registered label mapping")
    outcome = ledger.outcomes.get(target_outcome_id)
    if outcome is None or outcome.delivery_id not in ledger.deliveries:
        raise ValueError("target outcome is not sealed in the canonical ledger")
    if outcome.success not in (True, False):
        raise ValueError("target outcome success must be boolean")
    status = "PASS" if outcome.success else "FAIL"
    later_label = outcome.partial_score
    if later_label is None:
        later_label = 1.0 if outcome.success else 0.0
    role_hash, state_hash = _scope_hashes(
        offer=offer, assignment=assignment, target_selection=target_selection,
        candidate_key=candidate_key,
    )
    delivery = ledger.deliveries[source_row["delivery_id"]]
    metric_digest = _digest({
        "source_evidence_id": source_evidence_id,
        "source_judgment_id": source_judgment.judgment_id,
        "target_outcome_id": target_outcome_id,
        "target_quality": outcome.partial_score,
        "target_success": outcome.success,
    })
    return HistoryEntryV1(
        entry_id=f"history-{assignment.assignment_id}",
        agent_key=assignment.agent_id,
        subject_key=assignment.agent_id,
        role_signature_hash=role_hash,
        execution_state_fingerprint=state_hash,
        delivery_digest=delivery.artifact_sha256,
        recipient_judgment_id=source_judgment.judgment_id,
        recipient_judgment_label=JUDGMENT_LABELS[source_judgment.decision],
        later_outcome_id=target_outcome_id,
        later_outcome_label=float(later_label),
        metric_digest=metric_digest,
        cost=cost,
        arrival_index=int(target_arrival_index),
        assignment_id=assignment.assignment_id,
        status=status,
    )


def append_history_after_credit(
    *, history: PeerHistoryV1, ledger: Any, offer: RoleEvidenceOffer,
    target_assignment: Any, target_selection: Any, credit: LaterCredit,
    delayed_ledger: DelayedCreditLedger,
    assignment_read_cut: int, target_decision_index: int,
    target_arrival_index: int, candidate_key: str,
    candidate_registry_digest: str,
    cost: HistoryCostV1 | None = None,
) -> dict[str, Any]:
    """Validate target credit, then seal and append one history row.

    The caller invokes this only after ``DelayedCreditLedger.apply_once`` has
    returned ``True``.  The adapter uses the exact credit digest in the
    binding receipt, so a fabricated or unrelated delayed update cannot be
    attached to the row.
    """
    if not isinstance(history, PeerHistoryV1):
        raise TypeError("history must be a PeerHistoryV1")
    if not isinstance(credit, LaterCredit):
        raise TypeError("credit must be a LaterCredit")
    if not isinstance(delayed_ledger, DelayedCreditLedger):
        raise TypeError("delayed_ledger must be a DelayedCreditLedger")
    credit_key = f"{credit.assignment_id}\x1f{credit.later_outcome_id}"
    committed = delayed_ledger.credits.get(credit_key)
    if committed is None or committed.credit_digest != credit.credit_digest:
        raise ValueError("history append requires the exact delayed credit to be committed")
    if target_assignment.assignment_id != credit.assignment_id:
        raise ValueError("target assignment does not match delayed credit")
    if credit.source_evidence_id not in offer.evidence_ids:
        raise ValueError("delayed credit cites evidence outside the role offer")
    candidate_base = candidate_key.split("@", 1)[0]
    if candidate_base != target_assignment.agent_id:
        raise ValueError("candidate key does not match target assignment")
    existing = [item for item in history.entries
                if item.assignment_id == target_assignment.assignment_id]
    if existing:
        prior = existing[0]
        if (prior.later_outcome_id != credit.later_outcome_id
                or prior.subject_key != target_assignment.agent_id):
            raise ValueError("assignment already has a different history lineage")
        return {
            "adapter_version": VERSION,
            "status": "NOOP",
            "entry": prior.payload(),
            "seal": next((seal.payload() for seal in history.seals
                           if seal.assignment_id == prior.assignment_id), None),
            "receipt": None,
            "history_projection": history.selector_projection(candidate_key=candidate_key),
            "history_state_digest": history.state_digest(),
        }
    entry = _build_entry(
        ledger=ledger, offer=offer, assignment=target_assignment,
        target_selection=target_selection, target_outcome_id=credit.later_outcome_id,
        candidate_key=candidate_key, target_arrival_index=target_arrival_index,
        cost=cost or HistoryCostV1(),
    )
    role_hash, state_hash = _scope_hashes(
        offer=offer, assignment=target_assignment,
        target_selection=target_selection, candidate_key=candidate_key,
    )
    if entry.role_signature_hash != role_hash or entry.execution_state_fingerprint != state_hash:
        raise AssertionError("history scope hash construction is inconsistent")
    seal = AssignmentSealV1(
        assignment_id=target_assignment.assignment_id,
        subject_key=target_assignment.agent_id,
        role_signature_hash=role_hash,
        execution_state_fingerprint=state_hash,
        sealed_arrival_index=int(target_decision_index),
        candidate_registry_digest=candidate_registry_digest,
    )
    receipt: HistoryBindingReceiptV1 = build_history_binding_receipt(
        entry=entry, ledger=ledger, offer=offer,
        target_assignment=target_assignment, target_selection=target_selection,
        target_outcome_id=credit.later_outcome_id,
        assignment_read_cut=int(assignment_read_cut),
        target_decision_index=int(target_decision_index),
        target_arrival_index=int(target_arrival_index), candidate_key=candidate_key,
        candidate_registry_digest=candidate_registry_digest,
        later_credit_digest=credit.credit_digest,
    )
    # Seal and append are one logical publication.  A future history backend
    # may reject the second operation (duplicate lineage, arrival order, or
    # scope conflict); restore the in-memory append-only store so a retry
    # cannot observe an orphan seal.
    history_state = deepcopy(history.__dict__)
    try:
        history.seal_assignment(seal)
        history.append(entry)
    except Exception:
        history.__dict__.clear()
        history.__dict__.update(history_state)
        raise
    return {
        "adapter_version": VERSION,
        "status": "APPENDED",
        "entry": entry.payload(),
        "seal": seal.payload(),
        "receipt": receipt.payload(),
        "history_projection": history.selector_projection(candidate_key=candidate_key),
        "history_state_digest": history.state_digest(),
    }


__all__ = ["JUDGMENT_LABELS", "VERSION", "append_history_after_credit"]
