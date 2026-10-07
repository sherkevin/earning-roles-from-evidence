"""Read-only, noisy recipient observation of a completed native handoff.

This channel is distinct from RoleEvidenceOffer, source policy feedback, and
producer reward. It never calls evaluate_source_gate or derive_later_credit.
A source ledger prefix is replayed, then one frozen public-file contract binds
the delivered producer artifact and recipient's final action separately.
Replay proves event lineage and internal digest consistency, not independent
measurement truth: the upstream operator must supply authentic scorer payloads,
public file snapshots, and the pre-execution contract pin.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_ledger_replay import LedgerReplayError, replay_ledger_events
from peerrolebench_pipe3_material_adapter import digest_files

SCHEMA = 'noisy-judgment-observation-v1'
_SHA = re.compile(r'^[0-9a-f]{64}$')
_J = frozenset({'accept', 'accept_with_rework', 'reject_redo'})


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()


def _sha(value: str, name: str) -> None:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ValueError(f'{name} must be a lowercase SHA-256 digest')


@dataclass(frozen=True)
class FrozenObservationContract:
    """Pre-execution file ownership and public baseline digests."""
    task_id: str
    candidate_key: str
    candidate_source_digest: str
    producer_owned_paths: tuple[str, ...]
    recipient_owned_paths: tuple[str, ...]
    support_paths: tuple[str, ...]
    producer_input_sha256: str
    recipient_base_sha256: str

    def __post_init__(self) -> None:
        if not self.task_id or not self.candidate_key or '@' not in self.candidate_key:
            raise ValueError('contract task/candidate identity is required')
        for name in ('candidate_source_digest', 'producer_input_sha256', 'recipient_base_sha256'):
            _sha(getattr(self, name), name)
        groups = (self.producer_owned_paths, self.recipient_owned_paths, self.support_paths)
        if any(not group or tuple(sorted(set(group))) != group for group in groups):
            raise ValueError('contract path groups must be sorted and unique')
        if len(set().union(*map(set, groups))) != sum(map(len, groups)):
            raise ValueError('contract ownership groups overlap')

    @property
    def contract_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class NoisyJudgmentObservation:
    schema: str
    observation_id: str
    task_id: str
    source_task_index: int
    target_task_index: int
    available_index: int
    candidate_key: str
    candidate_source_digest: str
    contract_digest: str
    delivery_id: str
    delivery_artifact_sha256: str
    producer_score_id: str
    judgment_id: str
    action_id: str
    outcome_id: str
    judgment: str
    action: str
    producer_generation_changed_paths: tuple[str, ...]
    recipient_action_changed_paths: tuple[str, ...]
    recipient_scope: str
    scope_warning: str | None
    judgment_record_hash: str
    outcome_record_hash: str
    source_policy_update_allowed: bool = False
    producer_credit_allowed: bool = False

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.judgment not in _J:
            raise ValueError('noisy observation schema or judgment invalid')
        if self.source_policy_update_allowed or self.producer_credit_allowed:
            raise ValueError('noisy observation cannot authorize policy update or producer credit')

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ObservationResult:
    status: str
    observation: NoisyJudgmentObservation | None
    reason: str | None
    source_policy_update_allowed: bool = False
    producer_credit_allowed: bool = False

    def payload(self) -> dict[str, Any]:
        return {'status': self.status, 'observation': self.observation.payload() if self.observation else None,
                'reason': self.reason, 'source_policy_update_allowed': False,
                'producer_credit_allowed': False}


def _files(value: Mapping[str, str], paths: set[str], name: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != paths or any(not isinstance(text, str) for text in value.values()):
        raise ValueError(f'{name} file set is outside frozen contract')
    return dict(value)


def _record_hash(events: Sequence[Mapping[str, Any]], event_type: str, id_field: str, identity: str) -> str:
    rows = [row for row in events if row['event_type'] == event_type and row['payload'][id_field] == identity]
    if len(rows) != 1:
        raise ValueError(f'{event_type} record is missing or duplicated')
    return rows[0]['record_hash']


def build_judgment_observation(
    events: Sequence[Mapping[str, Any]], *, delivery_id: str,
    registry_entry: CandidateRegistryEntry, contract: FrozenObservationContract,
    expected_contract_digest: str,
    producer_before: Mapping[str, str], producer_delivered: Mapping[str, str],
    recipient_before: Mapping[str, str], recipient_after: Mapping[str, str],
    target_task_index: int, read_cut: int,
) -> ObservationResult:
    """Publish only after a complete source ledger prefix; fail closed to UNKNOWN.

    read_cut is this adapter's exclusive global event index for the supplied
    prefix and must equal len(events); it is not the older RoleEvidenceOffer
    inclusive read-cut convention. The returned observation never carries Qp/Y
    labels or reward. Native replay validates lineage, not scorer truth or the
    upstream operator's public-file provenance. This does not qualify later
    assignment credit or estimate producer benefit.
    """
    try:
        if not isinstance(registry_entry, CandidateRegistryEntry) or not isinstance(contract, FrozenObservationContract):
            raise ValueError('typed registry entry and frozen contract are required')
        _sha(expected_contract_digest, 'expected_contract_digest')
        if contract.contract_digest != expected_contract_digest:
            raise ValueError('frozen contract digest mismatch')
        if registry_entry.key != contract.candidate_key or registry_entry.source_digest != contract.candidate_source_digest:
            raise ValueError('candidate registry does not match frozen contract')
        if type(read_cut) is not int or read_cut != len(events):
            raise ValueError('read cut must be the completed source prefix boundary')
        if type(target_task_index) is not int or target_task_index < 0:
            raise ValueError('target task index is invalid')
        replay = replay_ledger_events(events, allow_incomplete=True)
        if any(item['stage'] != 'role_evidence_update' for item in replay.missing):
            raise ValueError('source handoff is incomplete')
        ledger = replay.ledger
        if len(ledger.deliveries) != 1 or delivery_id not in ledger.deliveries:
            raise ValueError('observation requires exactly one source delivery')
        delivery = ledger.deliveries[delivery_id]
        if delivery.task_id != contract.task_id or delivery.producer_id != registry_entry.candidate_id:
            raise ValueError('delivery task or producer mismatch')
        if delivery.candidate_source_digest != registry_entry.source_digest:
            raise ValueError('delivery candidate source binding mismatch')
        if target_task_index <= delivery.task_index:
            raise ValueError('target task must follow source task')
        target_key = (contract.task_id, target_task_index)
        if any((item.task_id, item.task_index) == target_key for item in ledger.assignments.values()):
            raise ValueError('target assignment already exists in source prefix')
        if target_key in ledger.started_tasks:
            raise ValueError('target task already started in source prefix')
        if any(item.task_index >= target_task_index for item in ledger.selections.values()):
            raise ValueError('target selection already exists in source prefix')
        scores = [row for row in ledger.producer_scores.values() if row.delivery_id == delivery_id]
        judgments = [row for row in ledger.judgments.values() if row.delivery_id == delivery_id]
        actions = [row for row in ledger.actions.values() if row.delivery_id == delivery_id]
        outcomes = [row for row in ledger.outcomes.values() if row.delivery_id == delivery_id]
        if any(len(rows) != 1 for rows in (scores, judgments, actions, outcomes)):
            raise ValueError('source score, judgment, action, or terminal outcome missing')
        score, judgment, action, outcome = scores[0], judgments[0], actions[0], outcomes[0]
        if (score.status not in {'PASS', 'FAIL'} or not score.coverage_complete or not score.decision_complete
                or judgment.decision not in _J or judgment.terminal_outcome_available
                or type(outcome.success) is not bool or outcome.score_payload_sha256 is None):
            raise ValueError('source score, judgment, or outcome is UNKNOWN/incomplete')
        p_paths = set(contract.producer_owned_paths)
        r_paths = set(contract.recipient_owned_paths)
        s_paths = set(contract.support_paths)
        before = _files(producer_before, p_paths, 'producer_before')
        delivered = _files(producer_delivered, p_paths, 'producer_delivered')
        rec_before = _files(recipient_before, p_paths | r_paths | s_paths, 'recipient_before')
        rec_after = _files(recipient_after, p_paths | r_paths | s_paths, 'recipient_after')
        if digest_files(before) != contract.producer_input_sha256:
            raise ValueError('producer preimage differs from frozen contract')
        if digest_files({path: rec_before[path] for path in r_paths | s_paths}) != contract.recipient_base_sha256:
            raise ValueError('recipient baseline differs from frozen contract')
        if any(rec_before[path] != delivered[path] for path in p_paths):
            raise ValueError('recipient input does not contain delivered producer source')
        if digest_files(delivered) != delivery.artifact_sha256 or digest_files(rec_after) != action.output_artifact_sha256:
            raise ValueError('delivery or recipient output artifact hash mismatch')
        if score.artifact_sha256 != delivery.artifact_sha256 or judgment.observed_artifact_sha256 != delivery.artifact_sha256:
            raise ValueError('scorer or judgment artifact binding mismatch')
        producer_diff = tuple(sorted(path for path in p_paths if before[path] != delivered[path]))
        recipient_diff = tuple(sorted(path for path in rec_before if rec_before[path] != rec_after[path]))
        changed = set(recipient_diff)
        if changed & s_paths:
            raise ValueError('recipient changed read-only support path')
        if not changed:
            scope, warning = 'none', None
        elif changed <= r_paths:
            scope, warning = 'recipient_owned', 'recipient work is not producer contribution'
        elif changed <= p_paths:
            scope, warning = 'producer_rewrite_by_recipient', 'recipient rewrote producer-owned source'
        elif changed <= p_paths | r_paths and changed & p_paths and changed & r_paths:
            scope, warning = 'mixed', 'mixed recipient/producer paths require separate attribution'
        else:
            raise ValueError('recipient change has invalid ownership scope')
        observation = NoisyJudgmentObservation(
            schema=SCHEMA, observation_id=f'observation-{judgment.judgment_id}',
            task_id=delivery.task_id, source_task_index=delivery.task_index,
            target_task_index=target_task_index, available_index=read_cut,
            candidate_key=registry_entry.key, candidate_source_digest=registry_entry.source_digest,
            contract_digest=contract.contract_digest, delivery_id=delivery.delivery_id,
            delivery_artifact_sha256=delivery.artifact_sha256, producer_score_id=score.producer_score_id,
            judgment_id=judgment.judgment_id, action_id=action.action_id,
            outcome_id=outcome.outcome_id, judgment=judgment.decision, action=action.action,
            producer_generation_changed_paths=producer_diff, recipient_action_changed_paths=recipient_diff,
            recipient_scope=scope, scope_warning=warning,
            judgment_record_hash=_record_hash(events, 'recipient_judgment', 'judgment_id', judgment.judgment_id),
            outcome_record_hash=_record_hash(events, 'terminal_outcome', 'outcome_id', outcome.outcome_id),
        )
        return ObservationResult('PUBLISHED', observation, None)
    except (ValueError, TypeError, KeyError, LedgerReplayError) as exc:
        return ObservationResult('UNKNOWN', None, f'{type(exc).__name__}: {exc}')


__all__ = ['SCHEMA', 'FrozenObservationContract', 'NoisyJudgmentObservation',
           'ObservationResult', 'build_judgment_observation']
