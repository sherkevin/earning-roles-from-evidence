"""Convert a typed policy projection into a public assignment row.

``project_feedback`` and ``project_raw_acceptance`` are the only places that
may cross from operator/scorer sidecars into a ``PolicyFeedbackProjection``.
This module is the next, deliberately small boundary: it serializes that
typed projection into the public row consumed by ``AssignmentEvidenceOffer``
and the versioned PIPE3 runner.  It does not accept raw scorer dictionaries or
invent a label for an UNKNOWN event.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from peerrolebench_assignment_attestation import AssignmentEvidenceOffer
from peerrolebench_pipe3_runner_v1 import make_offer
from peerrolebench_policy_projection import PolicyFeedbackProjection


def projection_to_public_row(
    projection: PolicyFeedbackProjection,
    *,
    unknown_reason: str | None = None,
) -> dict[str, Any]:
    """Serialize one already-validated projection for a public offer.

    The event-time runner requires ``arrival_index``.  A projection from an
    older wall-clock-only sidecar is rejected rather than assigned a guessed
    index.  UNKNOWN rows carry a reason for diagnostics but never a label.
    """

    if not isinstance(projection, PolicyFeedbackProjection):
        raise TypeError("projection must be a PolicyFeedbackProjection")
    if projection.arrival_index is None:
        raise ValueError("public feedback row requires event-time arrival_index")
    if projection.disposition == "unknown":
        if not isinstance(unknown_reason, str) or not unknown_reason.strip():
            raise ValueError("unknown public feedback row requires unknown_reason")
    elif unknown_reason is not None:
        raise ValueError("eligible public feedback row cannot carry unknown_reason")
    row = projection.public_payload()
    if unknown_reason is not None:
        row["unknown_reason"] = unknown_reason
    # Keep the final allowlist visible at this boundary.  AssignmentEvidence-
    # Offer performs the complete scalar/range validation after this check.
    forbidden = set(row) - {
        "feedback_id", "source_event_id", "source", "candidate_key",
        "evidence_version", "source_index", "arrival_index", "arrived_at",
        "delay", "action", "disposition", "provenance", "label",
        "supersedes", "unknown_reason",
    }
    if forbidden:
        raise ValueError(f"projection contains non-public fields: {sorted(forbidden)}")
    return row


def offer_from_projections(
    *,
    offer_id: str,
    task_id: str,
    task_index: int,
    role: str,
    context_key: str,
    candidate_keys: Sequence[str],
    projections: Sequence[tuple[PolicyFeedbackProjection, str | None]],
    evidence_version: str,
    available_index: int,
    previous_aux_hash: str = "GENESIS",
) -> AssignmentEvidenceOffer:
    """Build a versioned assignment offer from typed public projections."""

    keys = tuple(candidate_keys)
    if not keys or len(set(keys)) != len(keys) or not all(isinstance(key, str) and key for key in keys):
        raise ValueError("candidate_keys must be non-empty unique strings")
    rows = tuple(
        projection_to_public_row(projection, unknown_reason=reason)
        for projection, reason in projections
    )
    for row in rows:
        if row["candidate_key"] not in keys:
            raise ValueError("public projection candidate is outside the offer menu")
        if row["evidence_version"] != evidence_version:
            raise ValueError("public projection evidence version does not match offer")
    # Use the canonical runner constructor so the auxiliary-chain record hash
    # and bundle digest have exactly the same semantics as live PIPE3 offers.
    return make_offer(
        offer_id=offer_id, task_id=task_id, task_index=task_index, role=role,
        context_key=context_key, candidate_keys=keys, public_rows=rows,
        evidence_version=evidence_version, available_index=available_index,
        previous_aux_hash=previous_aux_hash,
    )


__all__ = ["projection_to_public_row", "offer_from_projections"]
