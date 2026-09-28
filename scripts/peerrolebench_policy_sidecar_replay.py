"""Canonical replay gate for versioned policy sidecars.

This module is intentionally separate from the live PIPE3 runner.  It first
validates the append-only protocol ledger, then validates every sidecar against
the sealed record, registers selections in canonical ledger order, and finally
applies feedback in deterministic arrival order.  A partial or invalid ledger
never reaches a policy update.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

from peerrolebench_ledger_replay import LedgerReplayError, replay_ledger_events
from peerrolebench_baseline_policies import BaselinePolicy
from peerrolebench_policy_sidecar import (
    DecisionSidecar,
    FeedbackSidecar,
    LINEAGE_SIDECAR_VERSION,
    PolicySidecarBridge,
    bind_to_ledger_record,
)
from peerrolebench_policy_sidecar_manifest import validate_manifest


@dataclass(frozen=True)
class SidecarRow:
    sidecar: DecisionSidecar | FeedbackSidecar
    ledger_record: Mapping[str, Any]
    sidecar_digest: str | None = None


def _record_index(records: Iterable[Mapping[str, Any]]) -> dict[str, tuple[int, Mapping[str, Any]]]:
    index: dict[str, tuple[int, Mapping[str, Any]]] = {}
    for position, record in enumerate(records):
        record_hash = record.get("record_hash")
        if not isinstance(record_hash, str) or record_hash in index:
            raise ValueError("ledger record hashes must be unique strings")
        index[record_hash] = (position, record)
    return index


def _protocol_key(record: Mapping[str, Any]) -> tuple[str, str] | None:
    event_type = record.get("event_type")
    field = {"peer_selection": "selection_id", "recipient_judgment": "judgment_id",
             "terminal_outcome": "outcome_id"}.get(event_type)
    payload = record.get("payload")
    if field is None or not isinstance(payload, Mapping) or field not in payload:
        return None
    return str(event_type), str(payload[field])


def _event_record_index(ledger: Any) -> dict[tuple[str, str], Mapping[str, Any]]:
    index: dict[tuple[str, str], Mapping[str, Any]] = {}
    for record in ledger.events:
        event_type = record.get("event_type")
        payload = record.get("payload")
        id_field = {
            "peer_selection": "selection_id", "producer_delivery": "delivery_id",
            "consumer_action": "action_id", "recipient_judgment": "judgment_id",
            "terminal_outcome": "outcome_id", "role_evidence_update": "evidence_id",
            "later_assignment": "assignment_id",
        }.get(event_type)
        if id_field is not None and isinstance(payload, Mapping) and id_field in payload:
            index[(str(event_type), str(payload[id_field]))] = record
    return index


def _validate_responsibility_lineage(
    sidecar: FeedbackSidecar,
    selection: DecisionSidecar,
    ledger: Any,
    record_index: Mapping[tuple[str, str], Mapping[str, Any]],
) -> None:
    """Validate each feedback hop against the replayed canonical ledger.

    v2 sidecars remain valid for historical/offline replay.  The live runner
    must opt into this stricter v3 gate so a valid event hash cannot hide a
    mismatched delivery, recipient, artifact, or consumer action.
    """
    if sidecar.sidecar_version != LINEAGE_SIDECAR_VERSION:
        raise ValueError("responsibility lineage requires sidecar v3")
    delivery = ledger.deliveries.get(sidecar.delivery_id)
    if delivery is None:
        raise ValueError("feedback references an unknown delivery")
    delivery_record = record_index.get(("producer_delivery", sidecar.delivery_id))
    if delivery_record is None or sidecar.delivery_record_hash != delivery_record.get("record_hash"):
        raise ValueError("feedback delivery record binding does not match canonical ledger")
    if delivery.selection_id != selection.protocol_event_id:
        raise ValueError("delivery selection lineage does not match feedback selection")
    if (delivery.task_id, delivery.task_index) != (selection.task_id, selection.task_index):
        raise ValueError("delivery task lineage does not match selection")
    chosen = selection.candidates[selection.chosen_index]
    if (delivery.producer_id, sidecar.producer_id, sidecar.producer_version) != (
        chosen.candidate_id, chosen.candidate_id, chosen.candidate_version
    ):
        raise ValueError("feedback producer does not match selected delivery")
    if delivery.recipient_id != sidecar.recipient_id:
        raise ValueError("feedback recipient does not match delivery")
    if sidecar.artifact_sha256 != delivery.artifact_sha256:
        raise ValueError("feedback artifact digest does not match delivery")

    action = next((value for value in ledger.actions.values()
                   if value.delivery_id == sidecar.delivery_id), None)
    if action is None:
        raise ValueError("feedback delivery has no canonical consumer action")
    action_record = record_index.get(("consumer_action", action.action_id))
    if sidecar.action != action.action:
        raise ValueError("feedback action does not match canonical consumer action")
    if sidecar.action_id is not None:
        if sidecar.action_id != action.action_id:
            raise ValueError("feedback action id does not match canonical consumer action")
        if action_record is None or sidecar.action_record_hash != action_record.get("record_hash"):
            raise ValueError("feedback action record binding does not match canonical ledger")

    if sidecar.protocol_event_type == "recipient_judgment":
        judgment = ledger.judgments.get(sidecar.protocol_event_id)
        if judgment is None or judgment.delivery_id != sidecar.delivery_id:
            raise ValueError("feedback judgment does not match delivery")
        if judgment.consumer_id != sidecar.recipient_id:
            raise ValueError("feedback judgment recipient does not match delivery")
        if judgment.observed_artifact_sha256 != delivery.artifact_sha256:
            raise ValueError("canonical judgment artifact does not match delivery")
    else:
        outcome = ledger.outcomes.get(sidecar.protocol_event_id)
        if outcome is None or outcome.delivery_id != sidecar.delivery_id:
            raise ValueError("feedback outcome does not match delivery")


def replay_policy_sidecars(
    ledger_events: Iterable[Mapping[str, Any]],
    sidecar_rows: Iterable[SidecarRow],
    policy_factory: Callable[[], BaselinePolicy],
    manifest: Iterable[Mapping[str, Any]] | None = None,
    require_responsibility_lineage: bool = False,
) -> dict[str, Any]:
    """Replay a sidecar stream under a strict ledger and update gate.

    Feedback input order is deliberately ignored after validation: the replay
    order is `(arrived_at, protocol_event_id)`, while selections are always
    registered in canonical ledger order.  This makes delayed feedback
    deterministic without pretending that online policy updates commute.
    """

    ledger = list(ledger_events)
    try:
        replay = replay_ledger_events(ledger, allow_incomplete=True)
    except LedgerReplayError as exc:
        return {
            "status": "INVALID", "ledger_status": "INVALID", "sidecar_status": "NOT_RUN",
            "update_allowed": False, "update_count": 0, "unknown_count": 0,
            "duplicate_count": 0, "pending_count": 0, "error": str(exc),
            "error_code": exc.code, "final_snapshot": None,
        }
    rows = list(sidecar_rows)
    try:
        records = _record_index(ledger)
    except ValueError as exc:
        return {
            "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
            "update_allowed": False, "update_count": 0, "unknown_count": 0,
            "duplicate_count": 0, "pending_count": 0, "error": str(exc),
            "final_snapshot": None,
        }

    decisions: list[tuple[int, SidecarRow]] = []
    feedback: list[tuple[int, SidecarRow]] = []
    seen_protocol_ids: set[tuple[str, str]] = set()
    seen_feedback_ids: set[str] = set()
    required_keys: dict[tuple[str, str], str] = {}
    for record in ledger:
        key = _protocol_key(record)
        if key is not None:
            required_keys[key] = str(record["record_hash"])
    supplied_keys: dict[tuple[str, str], str] = {}
    try:
        for row in rows:
            sidecar = row.sidecar
            record_hash = sidecar.payload().get("ledger_record_hash")
            if record_hash not in records:
                raise ValueError("sidecar references an unknown ledger record hash")
            expected_position, expected_record = records[record_hash]
            if row.ledger_record.get("record_hash") != record_hash:
                raise ValueError("sidecar row ledger record differs from sidecar binding")
            if expected_record != row.ledger_record:
                raise ValueError("sidecar row is not the canonical ledger record")
            bind_to_ledger_record(sidecar.payload(), expected_record,
                                  expected_event_type=sidecar.protocol_event_type,
                                  expected_event_id=sidecar.protocol_event_id)
            if not row.sidecar_digest or row.sidecar_digest != sidecar.sidecar_digest:
                raise ValueError("sidecar digest is required and must match payload")
            protocol_key = (sidecar.protocol_event_type, sidecar.protocol_event_id)
            if protocol_key in seen_protocol_ids:
                raise ValueError("duplicate sidecar protocol event")
            seen_protocol_ids.add(protocol_key)
            if protocol_key in supplied_keys:
                raise ValueError("duplicate sidecar protocol event")
            supplied_keys[protocol_key] = str(record_hash)
            if isinstance(sidecar, DecisionSidecar):
                decisions.append((expected_position, row))
            elif isinstance(sidecar, FeedbackSidecar):
                if sidecar.feedback_id in seen_feedback_ids:
                    raise ValueError("duplicate sidecar feedback id")
                seen_feedback_ids.add(sidecar.feedback_id)
                feedback.append((expected_position, row))
            else:
                raise ValueError("unsupported sidecar type")
        if set(required_keys) != set(supplied_keys):
            missing = sorted(set(required_keys) - set(supplied_keys))
            extra = sorted(set(supplied_keys) - set(required_keys))
            raise ValueError(f"sidecar event coverage mismatch: missing={missing}, extra={extra}")
        for key, record_hash in required_keys.items():
            if supplied_keys[key] != record_hash:
                raise ValueError(f"sidecar event {key} points to a different ledger record")
    except (TypeError, ValueError) as exc:
        return {
            "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
            "update_allowed": False, "update_count": 0, "unknown_count": 0,
            "duplicate_count": 0, "pending_count": 0, "error": str(exc),
            "final_snapshot": None,
        }

    manifest_root = None
    if manifest is not None:
        manifest_rows = [
            {
                "ledger_record_hash": row.sidecar.payload()["ledger_record_hash"],
                "protocol_event_type": row.sidecar.protocol_event_type,
                "protocol_event_id": row.sidecar.protocol_event_id,
                "sidecar_digest": row.sidecar.sidecar_digest,
            }
            for row in rows
        ]
        try:
            manifest_root = validate_manifest(manifest, manifest_rows)
        except ValueError as exc:
            return {
                "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
                "update_allowed": False, "update_count": 0, "unknown_count": 0,
                "duplicate_count": 0, "ignored_channel_count": 0, "pending_count": 0,
                "error": str(exc), "final_snapshot": None,
            }

    # An incomplete/UNKNOWN canonical ledger is never usable for policy state,
    # even if its sidecars happen to validate individually.
    if replay.status != "PASS":
        return {
            "status": "UNKNOWN", "ledger_status": replay.status, "sidecar_status": "PASS",
            "update_allowed": False, "update_count": 0, "unknown_count": 0,
            "duplicate_count": 0, "ignored_channel_count": 0, "pending_count": 0,
            "manifest_root": manifest_root, "final_snapshot": None,
        }

    decisions.sort(key=lambda item: item[0])
    feedback.sort(key=lambda item: (float(item[1].sidecar.arrived_at), item[1].sidecar.protocol_event_id))
    policy = policy_factory()
    bridge = PolicySidecarBridge(policy)
    record_index = _event_record_index(replay.ledger)
    selection_by_protocol: dict[str, DecisionSidecar] = {}
    for _, row in decisions:
        selection = row.sidecar
        assert isinstance(selection, DecisionSidecar)
        try:
            bridge.ingest_selection(selection, row.ledger_record)
        except ValueError as exc:
            return {
                "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
                "update_allowed": False, "update_count": 0, "unknown_count": 0,
                "duplicate_count": 0, "ignored_channel_count": 0, "pending_count": 0,
                "error": str(exc), "manifest_root": manifest_root, "final_snapshot": None,
            }
        selection_by_protocol[selection.protocol_event_id] = selection

    if require_responsibility_lineage:
        try:
            for _, row in feedback:
                event = row.sidecar
                assert isinstance(event, FeedbackSidecar)
                selection = selection_by_protocol.get(event.selection_event_id)
                if selection is None:
                    raise ValueError("feedback references unknown protocol selection")
                _validate_responsibility_lineage(event, selection, replay.ledger, record_index)
        except ValueError as exc:
            return {
                "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
                "update_allowed": False, "update_count": 0, "unknown_count": 0,
                "duplicate_count": 0, "ignored_channel_count": 0, "pending_count": 0,
                "error": str(exc), "manifest_root": manifest_root, "final_snapshot": None,
            }

    unknown_count = 0
    duplicate_count = 0
    ignored_channel_count = 0
    pending_count = 0
    for _, row in feedback:
        event = row.sidecar
        assert isinstance(event, FeedbackSidecar)
        selection = selection_by_protocol.get(event.selection_event_id)
        if selection is None:
            return {
                "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
                "update_allowed": False, "update_count": 0, "unknown_count": unknown_count,
                "duplicate_count": duplicate_count, "pending_count": pending_count,
                "error": "feedback references unknown protocol selection", "manifest_root": manifest_root,
                "final_snapshot": None,
            }
        expected_delay = float(event.arrived_at) - float(selection.selected_at)
        if event.arrived_at < selection.selected_at or abs(expected_delay - float(event.delay)) > 1e-9:
            return {
                "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
                "update_allowed": False, "update_count": 0, "unknown_count": unknown_count,
                "duplicate_count": duplicate_count, "pending_count": pending_count,
                "error": "feedback arrival/delay is inconsistent with selection time",
                "manifest_root": manifest_root, "final_snapshot": None,
            }
        if event.disposition != "eligible" or event.provenance != "public":
            unknown_count += 1
            continue
        if event.source not in policy.accepted_sources:
            ignored_channel_count += 1
            continue
        seen_channel = (event.source_event_id, event.source) in policy._seen_source_channels
        try:
            changed = bridge.ingest_feedback(event, row.ledger_record)
        except ValueError as exc:
            return {
                "status": "INVALID", "ledger_status": replay.status, "sidecar_status": "INVALID",
                "update_allowed": False, "update_count": 0, "unknown_count": unknown_count,
                "duplicate_count": duplicate_count, "ignored_channel_count": ignored_channel_count,
                "pending_count": pending_count, "error": str(exc), "manifest_root": manifest_root,
                "final_snapshot": None,
            }
        if not changed and seen_channel:
            duplicate_count += 1

    snapshot = policy.snapshot()
    return {
        "status": "PASS", "ledger_status": replay.status, "sidecar_status": "PASS",
        "update_allowed": True, "update_count": int(policy.updates),
        "unknown_count": unknown_count, "duplicate_count": duplicate_count,
        "ignored_channel_count": ignored_channel_count,
        "pending_count": pending_count, "manifest_root": manifest_root, "final_snapshot": snapshot,
    }


__all__ = ["SidecarRow", "replay_policy_sidecars"]
