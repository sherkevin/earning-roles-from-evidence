"""Source-bound PIPE3 sidecar -> public offer adapter.

This is the guarded composition missing between the typed projection seam and
the live runner.  It requires canonical ledger records, v4 responsibility
lineage, and a frozen arrival schedule before it creates public rows.  The
adapter intentionally exposes no scorer/gate-private fields and has no raw
acceptance path; that comparator remains a separate projection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from peerrolebench_assignment_attestation import AssignmentEvidenceOffer
from peerrolebench_event_time_schedule import ArrivalAssignment, schedule_digest, validate_schedule
from peerrolebench_pipe3_runner_v1 import make_offer
from peerrolebench_policy_projection import AttributionGate, PolicyFeedbackProjection, project_feedback
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar, bind_to_ledger_record
from peerrolebench_policy_sidecar_replay import _event_record_index, _validate_responsibility_lineage
from peerrolebench_public_feedback_rows import projection_to_public_row


@dataclass(frozen=True)
class SourceBoundOffer:
    """An offer plus the schedule identity that made its rows admissible."""

    offer: AssignmentEvidenceOffer
    schedule_digest: str
    projection_digests: tuple[str, ...]
    previous_aux_hash: str = "GENESIS"


def _record_for(
    ledger_records: Mapping[tuple[str, str], Mapping[str, Any]],
    event_type: str,
    event_id: str,
) -> Mapping[str, Any]:
    try:
        return ledger_records[(event_type, event_id)]
    except KeyError as exc:
        raise ValueError(f"missing canonical ledger record for {event_type}:{event_id}") from exc


def build_source_bound_offer(
    *,
    selection: DecisionSidecar,
    selection_record: Mapping[str, Any],
    feedback_inputs: Sequence[tuple[FeedbackSidecar, Mapping[str, Any], AttributionGate, str | None]],
    ledger: Any,
    arrival_schedule: Iterable[ArrivalAssignment | Mapping[str, Any]],
    offer_id: str,
    context_key: str,
    target_task_index: int | None = None,
    previous_aux_hash: str = "GENESIS",
) -> SourceBoundOffer:
    """Validate canonical lineage and seal an assignment evidence offer.

    ``feedback_inputs`` contains typed sidecars, their exact canonical ledger
    records, the operator-only attribution gate, and an optional fixed public
    reason for UNKNOWN.  It is deliberately not a mapping of raw dictionaries.
    """

    bind_to_ledger_record(
        selection.payload(), selection_record,
        expected_event_type="peer_selection", expected_event_id=selection.protocol_event_id,
    )
    if not feedback_inputs:
        raise ValueError("source-bound offer requires at least one feedback sidecar")
    record_index = _event_record_index(ledger)
    canonical_selection_record = _record_for(record_index, "peer_selection", selection.protocol_event_id)
    if canonical_selection_record != selection_record:
        raise ValueError("selection record is not the canonical record in the supplied ledger")
    sidecars = tuple(item[0] for item in feedback_inputs)
    schedule = validate_schedule(
        arrival_schedule,
        expected_feedback_ids=[sidecar.feedback_id for sidecar in sidecars],
    )
    by_feedback_id = {row.feedback_id: row for row in schedule}
    projections: list[tuple[PolicyFeedbackProjection, str | None]] = []
    evidence_versions: set[str] = set()
    for sidecar, ledger_record, gate, unknown_reason in feedback_inputs:
        if sidecar.sidecar_version != "peerrole-policy-sidecar-v4":
            raise ValueError("source-bound online offer requires event-time sidecar v4")
        canonical_feedback_record = _record_for(record_index, sidecar.protocol_event_type, sidecar.protocol_event_id)
        if canonical_feedback_record != ledger_record:
            raise ValueError("feedback record is not the canonical record in the supplied ledger")
        bind_to_ledger_record(
            sidecar.payload(), ledger_record,
            expected_event_type=sidecar.protocol_event_type,
            expected_event_id=sidecar.protocol_event_id,
        )
        _validate_responsibility_lineage(sidecar, selection, ledger, record_index)
        assignment = by_feedback_id[sidecar.feedback_id]
        if (
            assignment.protocol_event_type != sidecar.protocol_event_type
            or assignment.protocol_event_id != sidecar.protocol_event_id
            or assignment.source_event_id != sidecar.source_event_id
            or assignment.arrival_index != sidecar.arrival_index
        ):
            raise ValueError("sidecar does not match the frozen arrival schedule")
        projection = project_feedback(sidecar, gate, selection=selection)
        evidence_versions.add(projection.evidence_version)
        row_reason = unknown_reason if projection.disposition == "unknown" else None
        projections.append((projection, row_reason))

    if len(evidence_versions) != 1:
        raise ValueError("source-bound offer cannot mix evidence versions")

    candidate_keys = tuple(candidate.key for candidate in selection.candidates)
    if target_task_index is None:
        target_task_index = int(selection.task_index)
    elif int(target_task_index) <= int(selection.task_index):
        raise ValueError("explicit target task index must follow the source selection")
    offer = make_offer(
        offer_id=offer_id, task_id=selection.task_id, task_index=int(target_task_index),
        role=selection.role, context_key=context_key, candidate_keys=candidate_keys,
        public_rows=tuple(projection_to_public_row(projection, unknown_reason=reason)
                           for projection, reason in projections),
        evidence_version=next(iter(evidence_versions)),
        available_index=max(sidecar.arrival_index for sidecar in sidecars),
        previous_aux_hash=previous_aux_hash,
    )
    return SourceBoundOffer(
        offer=offer,
        schedule_digest=schedule_digest(schedule),
        projection_digests=tuple(sidecar.sidecar_digest for sidecar in sidecars),
        previous_aux_hash=previous_aux_hash,
    )


__all__ = ["SourceBoundOffer", "build_source_bound_offer"]
