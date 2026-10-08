"""Offline bridge for noisy observations, native completion, and assignment.

The native ``RoleEvidenceUpdate`` below is only a terminal completion anchor.
Its dedicated version must be rejected by attributed offer/credit consumers.
This module never creates a reward, calls an updater, or reads private tests.
Each operation replays input events into a fresh ledger and returns that copy;
caller-owned events and any policy state are not mutated.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_baseline_policies import Selection
from peerrolebench_judgment_observation import (
    FrozenObservationContract, NoisyJudgmentObservation, ObservationResult,
    build_judgment_observation,
)
from peerrolebench_ledger_replay import replay_ledger_events
from peer_role_protocol_20260925 import LaterAssignment, RoleEvidenceUpdate


OBSERVATION_ANCHOR_VERSION = 'noisy-observation-completion-v1'
PROJECTION_SCHEMA = 'noisy-observation-assignment-projection-v1'


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()


def _at(events: Sequence[Mapping[str, Any]], kind: str, key: str, identity: str) -> tuple[int, Mapping[str, Any]]:
    matches = [(i, row) for i, row in enumerate(events)
               if row['event_type'] == kind and row['payload'].get(key) == identity]
    if len(matches) != 1:
        raise ValueError(f'exactly one {kind} record is required')
    return matches[0]


@dataclass(frozen=True)
class ObservationAnchorReceipt:
    native_evidence_id: str
    auxiliary_observation_id: str
    observation_digest: str
    candidate_key: str
    candidate_source_digest: str
    contract_digest: str
    task_id: str
    source_task_index: int
    target_task_index: int
    source_read_cut: int
    native_anchor_index: int
    native_anchor_record_hash: str
    update_version: str
    judgment_id: str
    action_id: str
    outcome_id: str
    source_policy_update_allowed: bool = False
    producer_credit_allowed: bool = False
    receipt_digest: str = ''

    def __post_init__(self) -> None:
        if (self.update_version != OBSERVATION_ANCHOR_VERSION
                or self.source_policy_update_allowed or self.producer_credit_allowed
                or self.native_evidence_id == self.auxiliary_observation_id):
            raise ValueError('completion anchor cannot be attributed credit')
        if self.native_anchor_index != self.source_read_cut:
            raise ValueError('native anchor must immediately follow source read cut')
        if self.receipt_digest != _digest(self.payload(include_digest=False)):
            raise ValueError('completion receipt digest mismatch')

    def payload(self, *, include_digest: bool = True) -> dict[str, Any]:
        row = asdict(self)
        if not include_digest:
            row.pop('receipt_digest')
        return row


@dataclass(frozen=True)
class ObservationAssignmentProjection:
    schema: str
    assignment_id: str
    task_id: str
    target_task_index: int
    subject_candidate_key: str
    subject_agent_id: str
    native_evidence_id: str
    auxiliary_observation_id: str
    observation_digest: str
    receipt_digest: str
    contract_digest: str
    anchor_version: str
    native_anchor_record_hash: str
    judgment: str
    action: str
    source_task_index: int
    source_read_cut: int
    assignment_read_cut: int
    decision_propensity: float
    preview_digest: str
    preview_event_id: str
    preview_menu_keys: tuple[str, ...]
    preview_chosen_index: int
    preview_probabilities: tuple[float, ...]
    preview_state_version: str
    preview_encoder_version: str
    preview_feature_schema: str
    source_policy_update_allowed: bool = False
    producer_credit_allowed: bool = False
    projection_digest: str = ''

    def __post_init__(self) -> None:
        if (self.schema != PROJECTION_SCHEMA or self.anchor_version != OBSERVATION_ANCHOR_VERSION
                or self.source_policy_update_allowed or self.producer_credit_allowed):
            raise ValueError('observation projection cannot authorize update or credit')
        if (not math.isfinite(self.decision_propensity)
                or not 0.0 < self.decision_propensity <= 1.0):
            raise ValueError('decision propensity must be finite in (0,1]')
        if self.projection_digest != _digest(self.payload(include_digest=False)):
            raise ValueError('assignment projection digest mismatch')

    def payload(self, *, include_digest: bool = True) -> dict[str, Any]:
        row = asdict(self)
        if not include_digest:
            row.pop('projection_digest')
        return row


def publish_completion_anchor(
    source_events: Sequence[Mapping[str, Any]], observation: ObservationResult, *,
    registry_entry: CandidateRegistryEntry, contract: FrozenObservationContract,
    expected_contract_digest: str, expected_source_subject: str,
    producer_before: Mapping[str, str], producer_delivered: Mapping[str, str],
    recipient_before: Mapping[str, str], recipient_after: Mapping[str, str],
    source_read_cut: int, native_evidence_id: str, arrived_at: float,
    update_version: str = OBSERVATION_ANCHOR_VERSION,
) -> tuple[Any, ObservationAnchorReceipt]:
    """Revalidate a published observation, then append one neutral native anchor.

    ``source_read_cut`` is the observation adapter's exclusive event boundary.
    The caller must pin the pre-execution contract and exact source subject.
    """
    if update_version != OBSERVATION_ANCHOR_VERSION:
        raise ValueError('wrong observation anchor version')
    if (not isinstance(observation, ObservationResult) or observation.status != 'PUBLISHED'
            or not isinstance(observation.observation, NoisyJudgmentObservation)
            or observation.source_policy_update_allowed or observation.producer_credit_allowed):
        raise ValueError('published typed observation is required')
    row = observation.observation
    if expected_source_subject != registry_entry.key or row.candidate_key != expected_source_subject:
        raise ValueError('source subject does not match candidate registry')
    if type(source_read_cut) is not int or source_read_cut != len(source_events) or row.available_index != source_read_cut:
        raise ValueError('source read cut mismatch')
    if not native_evidence_id or native_evidence_id == row.observation_id:
        raise ValueError('native evidence id must be distinct from auxiliary observation id')
    if not math.isfinite(float(arrived_at)) or float(arrived_at) < 0:
        raise ValueError('arrival time must be finite and nonnegative')
    fresh = build_judgment_observation(
        source_events, delivery_id=row.delivery_id, registry_entry=registry_entry,
        contract=contract, expected_contract_digest=expected_contract_digest,
        producer_before=producer_before, producer_delivered=producer_delivered,
        recipient_before=recipient_before, recipient_after=recipient_after,
        target_task_index=row.target_task_index, read_cut=source_read_cut)
    if fresh != observation:
        raise ValueError('observation differs from revalidated source record')
    replay = replay_ledger_events(source_events, allow_incomplete=True)
    ledger = replay.ledger
    if any(item.judgment_id == row.judgment_id or item.action_id == row.action_id
           for item in ledger.evidence.values()):
        raise ValueError('native completion anchor already exists for judgment/action')
    ledger.record_evidence_update(RoleEvidenceUpdate(
        native_evidence_id, row.judgment_id, row.action_id, row.outcome_id,
        OBSERVATION_ANCHOR_VERSION, float(arrived_at)))
    anchor_index, anchor_record = _at(ledger.events, 'role_evidence_update', 'evidence_id', native_evidence_id)
    body = dict(native_evidence_id=native_evidence_id, auxiliary_observation_id=row.observation_id,
                observation_digest=_digest(row.payload()), candidate_key=row.candidate_key,
                candidate_source_digest=row.candidate_source_digest, contract_digest=row.contract_digest,
                task_id=row.task_id, source_task_index=row.source_task_index,
                target_task_index=row.target_task_index, source_read_cut=source_read_cut,
                native_anchor_index=anchor_index, native_anchor_record_hash=anchor_record['record_hash'],
                update_version=OBSERVATION_ANCHOR_VERSION, judgment_id=row.judgment_id,
                action_id=row.action_id, outcome_id=row.outcome_id)
    receipt = ObservationAnchorReceipt(**body, receipt_digest=_digest({**body,
        'source_policy_update_allowed': False, 'producer_credit_allowed': False}))
    return ledger, receipt


def make_assignment_projection(
    anchored_events: Sequence[Mapping[str, Any]], receipt: ObservationAnchorReceipt, *,
    assignment_id: str, expected_receipt_digest: str,
    preview: Selection, expected_preview_digest: str,
    expected_menu_keys: tuple[str, ...], expected_candidate_source_digest: str,
    expected_contract_digest: str, expected_source_subject: str,
    expected_anchor_version: str, task_id: str, target_task_index: int,
    assignment_read_cut: int, decision_propensity: float,
) -> ObservationAssignmentProjection:
    """Read one neutral anchor into a typed, reward-free preassignment view."""
    if not isinstance(receipt, ObservationAnchorReceipt):
        raise TypeError('typed completion receipt is required')
    if receipt.receipt_digest != expected_receipt_digest:
        raise ValueError('completion receipt external digest pin mismatch')
    if (expected_anchor_version != OBSERVATION_ANCHOR_VERSION
            or receipt.update_version != expected_anchor_version):
        raise ValueError('wrong observation anchor version')
    if (receipt.contract_digest != expected_contract_digest
            or receipt.candidate_key != expected_source_subject
            or receipt.candidate_source_digest != expected_candidate_source_digest
            or receipt.task_id != task_id or receipt.target_task_index != target_task_index):
        raise ValueError('contract, subject, or target binding mismatch')
    if (type(assignment_read_cut) is not int or assignment_read_cut != len(anchored_events)
            or assignment_read_cut <= receipt.native_anchor_index):
        raise ValueError('assignment read cut mismatch')
    if not isinstance(assignment_id, str) or not assignment_id:
        raise ValueError('assignment id is required')
    if not isinstance(decision_propensity, (int, float)) or not math.isfinite(float(decision_propensity)) or not 0.0 < float(decision_propensity) <= 1.0:
        raise ValueError('decision propensity must be finite in (0,1]')
    if not isinstance(preview, Selection) or _digest(asdict(preview)) != expected_preview_digest:
        raise ValueError('selection preview digest pin mismatch')
    menu = tuple(ref.key for ref in preview.candidates)
    probabilities = tuple(preview.probabilities)
    if (not menu or len(menu) != len(set(menu)) or menu != expected_menu_keys
            or not isinstance(preview.chosen_index, int)
            or not 0 <= preview.chosen_index < len(menu)
            or len(probabilities) != len(menu)
            or not all(math.isfinite(p) and p >= 0 for p in probabilities)
            or not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9)
            or preview.chosen.key != expected_source_subject
            or not math.isclose(preview.propensity, probabilities[preview.chosen_index], abs_tol=1e-12)
            or not math.isclose(preview.propensity, float(decision_propensity), abs_tol=1e-12)
            or not all((preview.event_id, preview.context_key, preview.selector_id,
                        preview.state_version, preview.encoder_version, preview.feature_schema))):
        raise ValueError('selection preview menu, choice, version, or propensity mismatch')
    replay = replay_ledger_events(anchored_events)
    if not replay.complete:
        raise ValueError('anchored source ledger is incomplete')
    ledger = replay.ledger
    index, record = _at(ledger.events, 'role_evidence_update', 'evidence_id', receipt.native_evidence_id)
    anchor = ledger.evidence[receipt.native_evidence_id]
    if (index != receipt.native_anchor_index or record['record_hash'] != receipt.native_anchor_record_hash
            or anchor.update_version != OBSERVATION_ANCHOR_VERSION
            or (anchor.judgment_id, anchor.action_id, anchor.outcome_id) !=
            (receipt.judgment_id, receipt.action_id, receipt.outcome_id)):
        raise ValueError('native anchor differs from completion receipt')
    judgment = ledger.judgments[receipt.judgment_id]
    action = ledger.actions[receipt.action_id]
    delivery = ledger.deliveries[judgment.delivery_id]
    if (action.delivery_id != delivery.delivery_id or delivery.producer_id != expected_source_subject.split('@', 1)[0]
            or delivery.candidate_source_digest != receipt.candidate_source_digest
            or delivery.task_index != receipt.source_task_index):
        raise ValueError('native anchor source subject mismatch')
    target_key = (task_id, target_task_index)
    if (target_key in ledger.started_tasks
            or any((x.task_id, x.task_index) == target_key for x in ledger.assignments.values())
            or any((x.task_id, x.task_index) == target_key for x in ledger.selections.values())):
        raise ValueError('target task already assigned or started')
    body = dict(schema=PROJECTION_SCHEMA, assignment_id=assignment_id, task_id=task_id,
                target_task_index=target_task_index, subject_candidate_key=expected_source_subject,
                subject_agent_id=delivery.producer_id, native_evidence_id=receipt.native_evidence_id,
                auxiliary_observation_id=receipt.auxiliary_observation_id,
                observation_digest=receipt.observation_digest, receipt_digest=receipt.receipt_digest,
                contract_digest=receipt.contract_digest,
                anchor_version=OBSERVATION_ANCHOR_VERSION,
                native_anchor_record_hash=receipt.native_anchor_record_hash,
                judgment=judgment.decision, action=action.action,
                source_task_index=receipt.source_task_index, source_read_cut=receipt.source_read_cut,
                assignment_read_cut=assignment_read_cut, decision_propensity=float(decision_propensity),
                preview_digest=expected_preview_digest, preview_event_id=preview.event_id,
                preview_menu_keys=menu, preview_chosen_index=preview.chosen_index,
                preview_probabilities=probabilities, preview_state_version=preview.state_version,
                preview_encoder_version=preview.encoder_version,
                preview_feature_schema=preview.feature_schema)
    return ObservationAssignmentProjection(**body, projection_digest=_digest({**body,
        'source_policy_update_allowed': False, 'producer_credit_allowed': False}))


def record_projected_assignment(
    anchored_events: Sequence[Mapping[str, Any]], receipt: ObservationAnchorReceipt,
    projection: ObservationAssignmentProjection, *, expected_projection_digest: str,
    expected_receipt_digest: str, preview: Selection, expected_preview_digest: str,
    expected_menu_keys: tuple[str, ...], expected_candidate_source_digest: str,
    expected_contract_digest: str, expected_source_subject: str,
    expected_anchor_version: str, assignment_read_cut: int,
    decision_propensity: float,
) -> Any:
    """Seal a native assignment that cites the native id, never the auxiliary id."""
    if not isinstance(projection, ObservationAssignmentProjection):
        raise TypeError('typed assignment projection is required')
    if projection.projection_digest != expected_projection_digest:
        raise ValueError('assignment projection digest pin mismatch')
    fresh = make_assignment_projection(
        anchored_events, receipt, assignment_id=projection.assignment_id,
        expected_receipt_digest=expected_receipt_digest, preview=preview,
        expected_preview_digest=expected_preview_digest,
        expected_menu_keys=expected_menu_keys,
        expected_candidate_source_digest=expected_candidate_source_digest,
        expected_contract_digest=expected_contract_digest,
        expected_source_subject=expected_source_subject,
        expected_anchor_version=expected_anchor_version, task_id=projection.task_id,
        target_task_index=projection.target_task_index,
        assignment_read_cut=assignment_read_cut, decision_propensity=decision_propensity)
    if fresh != projection:
        raise ValueError('assignment projection differs from replayed anchor')
    ledger = replay_ledger_events(anchored_events).ledger
    ledger.record_assignment(LaterAssignment(
        projection.assignment_id, projection.task_id, projection.target_task_index,
        projection.subject_agent_id, 'producer', (projection.native_evidence_id,),
        projection.decision_propensity))
    return ledger


__all__ = ['OBSERVATION_ANCHOR_VERSION', 'PROJECTION_SCHEMA', 'ObservationAnchorReceipt',
           'ObservationAssignmentProjection', 'publish_completion_anchor',
           'make_assignment_projection', 'record_projected_assignment']
