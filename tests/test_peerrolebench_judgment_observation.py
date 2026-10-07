"""Zero-API semantic matrix for noisy J versus producer credit."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'references/aamas'))
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_judgment_observation import (  # noqa: E402
    FrozenObservationContract, build_judgment_observation,
)
from peerrolebench_pipe3_material_adapter import digest_files  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402

LOG = ROOT / 'experiments/logs/n03_judgment_observation_qualification_20261007_v4'
DELIVERED = {'producer.py': "def serialize(): return 'delivered'\n"}
BASE_RECIPIENT = {'processor.py': "def process(): return 'before'\n",
                  'sink.py': "def load(): return 'ok'\n"}
REGISTRY = CandidateRegistryEntry('peer-b', 'v1', 'a' * 64, 'model', 'b' * 64)
DECISIONS = {'accept': ('use', True), 'accept_with_rework': ('repair', True),
             'reject_redo': ('independent_redo', False)}
MODES = ('neither', 'producer_only', 'recipient_only', 'both')


def _log(case, result, **extra):
    with (LOG / 'raw.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                                 'case': case, 'result': result.payload(), **extra},
                                ensure_ascii=False, sort_keys=True) + '\n')
        stream.flush()


def fixture(decision='accept', mode='neither', *, score_status='PASS', outcome_payload=True):
    producer_before = dict(DELIVERED)
    if mode in ('producer_only', 'both'):
        producer_before['producer.py'] = "def serialize(): return 'template'\n"
    recipient_before = {**DELIVERED, **BASE_RECIPIENT}
    recipient_after = dict(recipient_before)
    if mode in ('recipient_only', 'both'):
        recipient_after['processor.py'] = "def process(): return 'after'\n"
    contract = FrozenObservationContract(
        task_id='PIPE3', candidate_key=REGISTRY.key, candidate_source_digest=REGISTRY.source_digest,
        producer_owned_paths=('producer.py',), recipient_owned_paths=('processor.py',),
        support_paths=('sink.py',), producer_input_sha256=digest_files(producer_before),
        recipient_base_sha256=digest_files(BASE_RECIPIENT),
    )
    artifact = digest_files(DELIVERED)
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection('s0', 'PIPE3', 0, 'peer-a', 'producer', ('peer-b', 'peer-c'), 'peer-b', 0.5))
    ledger.record_task_start('PIPE3', 0)
    ledger.record_delivery(Delivery('d0', 'PIPE3', 'peer-b', 'peer-a', artifact, 'produce-0', 0, 's0', REGISTRY.source_digest))
    if score_status == 'UNKNOWN':
        score = ProducerScore('q0', 'd0', artifact, 'qp-v2', 'UNKNOWN')
    else:
        score = ProducerScore('q0', 'd0', artifact, 'qp-v2', 'PASS', 1, 1.0, 'c' * 64, True, True)
    ledger.record_producer_score(score)
    ledger.record_judgment(RecipientJudgment('j0', 'd0', 'peer-a', decision, artifact))
    action, used = DECISIONS[decision]
    ledger.record_action(ConsumerAction('a0', 'd0', 'peer-a', used, artifact,
                                        digest_files(recipient_after), 0.0, action))
    ledger.record_outcome(TerminalOutcome('y0', 'd0', True, 'terminal-v2', 1.0,
                                          'd' * 64 if outcome_payload else None))
    kwargs = {'events': deepcopy(ledger.events), 'delivery_id': 'd0', 'registry_entry': REGISTRY,
              'contract': contract, 'expected_contract_digest': contract.contract_digest,
              'producer_before': producer_before,
              'producer_delivered': DELIVERED, 'recipient_before': recipient_before,
              'recipient_after': recipient_after, 'target_task_index': 1,
              'read_cut': len(ledger.events)}
    return kwargs


@pytest.mark.parametrize('decision', tuple(DECISIONS))
@pytest.mark.parametrize('mode', MODES)
def test_all_j_and_diff_modes_are_observations_without_credit(decision, mode):
    kwargs = fixture(decision, mode)
    original_events = deepcopy(kwargs['events'])
    result = build_judgment_observation(**kwargs)
    _log(f'{decision}/{mode}', result, delivery_sha256=digest_files(DELIVERED),
         event_chain_sha256=hashlib.sha256(json.dumps(original_events, sort_keys=True).encode()).hexdigest(),
         contract_digest=kwargs['contract'].contract_digest)
    assert result.status == 'PUBLISHED'
    assert result.source_policy_update_allowed is False and result.producer_credit_allowed is False
    row = result.observation
    assert row is not None and row.judgment == decision
    assert bool(row.producer_generation_changed_paths) == (mode in ('producer_only', 'both'))
    assert bool(row.recipient_action_changed_paths) == (mode in ('recipient_only', 'both'))
    assert row.recipient_scope == ('recipient_owned' if mode in ('recipient_only', 'both') else 'none')
    assert not {'reward', 'quality_score', 'producer_label', 'outcome_status'} & set(row.payload())
    assert kwargs['events'] == original_events


@pytest.mark.parametrize('control', ('missing_outcome', 'late_read_cut', 'wrong_registry',
                                     'wrong_artifact', 'unknown_qp', 'judgment_after_outcome',
                                     'wrong_contract_pin', 'missing_outcome_payload'))
def test_missing_late_wrong_or_unknown_fail_closed(control):
    kwargs = fixture(score_status='UNKNOWN' if control == 'unknown_qp' else 'PASS',
                     outcome_payload=control != 'missing_outcome_payload')
    if control == 'missing_outcome':
        kwargs['events'].pop()
        kwargs['read_cut'] = len(kwargs['events'])
    elif control == 'late_read_cut':
        kwargs['read_cut'] -= 1
    elif control == 'wrong_registry':
        kwargs['registry_entry'] = CandidateRegistryEntry('peer-b', 'v1', 'e' * 64, 'model', 'b' * 64)
    elif control == 'wrong_artifact':
        kwargs['producer_delivered'] = {'producer.py': 'different'}
    elif control == 'wrong_contract_pin':
        kwargs['expected_contract_digest'] = 'f' * 64
    elif control == 'judgment_after_outcome':
        row = next(x for x in kwargs['events'] if x['event_type'] == 'recipient_judgment')
        row['payload']['terminal_outcome_available'] = True
    result = build_judgment_observation(**kwargs)
    _log(control, result)
    assert result.status == 'UNKNOWN' and result.observation is None
    assert result.source_policy_update_allowed is False and result.producer_credit_allowed is False
    assert result.reason


def test_recipient_rewrite_and_mixed_scope_warn_but_support_fails_closed():
    for name, changed in (('recipient_rewrites_producer', {'producer.py'}),
                          ('mixed_rewrite', {'producer.py', 'processor.py'}),
                          ('support_rewrite', {'sink.py'})):
        kwargs = fixture('accept_with_rework', 'neither')
        for path in changed:
            kwargs['recipient_after'][path] += '# changed\n'
        # Rebuild the action event through the native factory so its output
        # digest remains bound to the final snapshot; other records stay fixed.
        events = kwargs['events']
        ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
        for event in events[:5]:
            kind = event['event_type']
            if kind == 'peer_selection': ledger.record_selection(PeerSelection(**event['payload']))
            elif kind == 'task_start': ledger.record_task_start(**event['payload'])
            elif kind == 'producer_delivery': ledger.record_delivery(Delivery(**event['payload']))
            elif kind == 'producer_score': ledger.record_producer_score(ProducerScore(**event['payload']))
            elif kind == 'recipient_judgment': ledger.record_judgment(RecipientJudgment(**event['payload']))
        artifact = digest_files(DELIVERED)
        ledger.record_action(ConsumerAction('a0', 'd0', 'peer-a', True, artifact,
                                            digest_files(kwargs['recipient_after']), 0.0, 'repair'))
        ledger.record_outcome(TerminalOutcome('y0', 'd0', True, 'terminal-v2', 1.0, 'd' * 64))
        kwargs['events'], kwargs['read_cut'] = ledger.events, len(ledger.events)
        result = build_judgment_observation(**kwargs)
        _log(name, result)
        if name == 'support_rewrite':
            assert result.status == 'UNKNOWN' and result.observation is None
            assert 'support path' in result.reason
        else:
            assert result.status == 'PUBLISHED'
            assert result.observation.scope_warning
        assert result.producer_credit_allowed is False


def test_preexisting_target_assignment_is_not_retroactively_influenced():
    kwargs = fixture()
    ledger = replay_ledger_events(kwargs['events'], allow_incomplete=True).ledger
    # These are legal native lineage records for a target assignment that
    # already happened; they do not grant this observation producer credit.
    ledger.record_evidence_update(RoleEvidenceUpdate('e0', 'j0', 'a0', 'y0',
                                                     'native-fixture-v1', 1.0))
    ledger.record_assignment(LaterAssignment('as1', 'PIPE3', 1, 'peer-b', 'producer',
                                             ('e0',), 0.5))
    kwargs['events'], kwargs['read_cut'] = ledger.events, len(ledger.events)
    replay = replay_ledger_events(kwargs['events'])
    assert replay.status == 'PASS' and replay.complete and not replay.missing
    result = build_judgment_observation(**kwargs)
    _log('target_assignment_already_recorded', result,
         native_replay_status=replay.status, native_replay_complete=replay.complete)
    assert result.status == 'UNKNOWN' and result.observation is None
    assert 'target assignment' in result.reason
    assert result.source_policy_update_allowed is False and result.producer_credit_allowed is False


def test_typed_observation_cannot_be_promoted_to_credit():
    result = build_judgment_observation(**fixture())
    assert result.status == 'PUBLISHED'
    with pytest.raises(ValueError, match='cannot authorize'):
        replace(result.observation, producer_credit_allowed=True)
    _log('typed_promotion_rejected', result)
