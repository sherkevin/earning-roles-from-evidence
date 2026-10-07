"""Zero-call native completion and assignment chain for noisy observations."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'references/aamas'))
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, ProducerScore,
    RecipientJudgment, TerminalOutcome,
)
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_judgment_observation import (  # noqa: E402
    FrozenObservationContract, ObservationResult, build_judgment_observation,
)
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_observation_bridge import (  # noqa: E402
    OBSERVATION_ANCHOR_VERSION, make_assignment_projection,
    publish_completion_anchor, record_projected_assignment,
)
from peerrolebench_pipe3_material_adapter import digest_files  # noqa: E402

LOG = ROOT / 'experiments/logs/n03_observation_bridge_20261007_v1'
REGISTRY = CandidateRegistryEntry('peer-b', 'v1', 'a' * 64, 'model', 'b' * 64)
PAIRS = {'accept': ('use', True), 'accept_with_rework': ('repair', True),
         'reject_redo': ('independent_redo', False)}


def _log(case, *, outcome, **extra):
    with (LOG / 'raw.jsonl').open('a', encoding='utf-8') as file:
        file.write(json.dumps({'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                               'case': case, 'outcome': outcome, **extra},
                              sort_keys=True, ensure_ascii=False) + '\n')
        file.flush()


def source(decision='accept'):
    producer_before = {'producer.py': 'old producer\n'}
    producer_delivered = {'producer.py': 'new producer\n'}
    recipient_before = {**producer_delivered, 'processor.py': 'old processor\n', 'sink.py': 'support\n'}
    recipient_after = dict(recipient_before)
    if decision != 'accept':
        recipient_after['processor.py'] = 'new processor\n'
    contract = FrozenObservationContract(
        task_id='PIPE3', candidate_key=REGISTRY.key,
        candidate_source_digest=REGISTRY.source_digest,
        producer_owned_paths=('producer.py',), recipient_owned_paths=('processor.py',),
        support_paths=('sink.py',), producer_input_sha256=digest_files(producer_before),
        recipient_base_sha256=digest_files({'processor.py': 'old processor\n', 'sink.py': 'support\n'}))
    artifact = digest_files(producer_delivered)
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection('s0', 'PIPE3', 0, 'peer-a', 'producer',
                                          ('peer-b', 'peer-c'), 'peer-b', 0.5))
    ledger.record_task_start('PIPE3', 0)
    ledger.record_delivery(Delivery('d0', 'PIPE3', 'peer-b', 'peer-a', artifact,
                                    'produce-0', 0, 's0', REGISTRY.source_digest))
    ledger.record_producer_score(ProducerScore('q0', 'd0', artifact, 'qp-v2', 'PASS',
                                               1, 1.0, 'c' * 64, True, True))
    ledger.record_judgment(RecipientJudgment('j0', 'd0', 'peer-a', decision, artifact))
    action, used = PAIRS[decision]
    ledger.record_action(ConsumerAction('a0', 'd0', 'peer-a', used, artifact,
                                        digest_files(recipient_after), 0.0, action))
    ledger.record_outcome(TerminalOutcome('y0', 'd0', True, 'terminal-v2', 1.0, 'd' * 64))
    values = {'events': deepcopy(ledger.events), 'delivery_id': 'd0',
              'registry_entry': REGISTRY, 'contract': contract,
              'expected_contract_digest': contract.contract_digest,
              'producer_before': producer_before, 'producer_delivered': producer_delivered,
              'recipient_before': recipient_before, 'recipient_after': recipient_after,
              'target_task_index': 1, 'read_cut': len(ledger.events)}
    observation = build_judgment_observation(**values)
    assert observation.status == 'PUBLISHED'
    return values, observation


def anchor_args(values, observation):
    return dict(source_events=values['events'], observation=observation,
                registry_entry=REGISTRY, contract=values['contract'],
                expected_contract_digest=values['expected_contract_digest'],
                expected_source_subject=REGISTRY.key,
                producer_before=values['producer_before'],
                producer_delivered=values['producer_delivered'],
                recipient_before=values['recipient_before'], recipient_after=values['recipient_after'],
                source_read_cut=values['read_cut'], native_evidence_id='native-e0',
                arrived_at=7.0, update_version=OBSERVATION_ANCHOR_VERSION)


def projection_args(ledger, receipt):
    return dict(anchored_events=ledger.events, receipt=receipt, assignment_id='as1',
                expected_contract_digest=receipt.contract_digest,
                expected_source_subject=receipt.candidate_key,
                expected_anchor_version=OBSERVATION_ANCHOR_VERSION,
                task_id=receipt.task_id, target_task_index=receipt.target_task_index,
                assignment_read_cut=len(ledger.events), decision_propensity=0.5)


@pytest.mark.parametrize('decision', tuple(PAIRS))
def test_complete_native_chain_keeps_observation_separate_from_credit(decision):
    values, observation = source(decision)
    source_copy = deepcopy(values['events'])
    policy_state = {'updates': 0, 'digest': 'unchanged'}
    policy_copy = deepcopy(policy_state)
    anchored, receipt = publish_completion_anchor(**anchor_args(values, observation))
    projection = make_assignment_projection(**projection_args(anchored, receipt))
    assigned = record_projected_assignment(
        anchored.events, receipt, projection,
        expected_projection_digest=projection.projection_digest,
        expected_contract_digest=receipt.contract_digest,
        expected_source_subject=receipt.candidate_key,
        expected_anchor_version=OBSERVATION_ANCHOR_VERSION,
        assignment_read_cut=projection.assignment_read_cut,
        decision_propensity=projection.decision_propensity)
    assigned.record_selection(PeerSelection('s1', 'PIPE3', 1, 'peer-a', 'producer',
                                            ('peer-b', 'peer-c'), 'peer-b', 0.5))
    replay = replay_ledger_events(assigned.events, allow_incomplete=True)
    assert replay.status == 'UNKNOWN' and replay.missing == (
        {'stage': 'task_start', 'task_id': 'PIPE3', 'task_index': 1},
        {'stage': 'producer_delivery', 'task_id': 'PIPE3', 'task_index': 1})
    assert [x['event_type'] for x in assigned.events[-3:]] == [
        'role_evidence_update', 'later_assignment', 'peer_selection']
    assert assigned.assignments['as1'].evidence_ids == (receipt.native_evidence_id,)
    assert receipt.native_evidence_id != receipt.auxiliary_observation_id
    assert projection.judgment == decision and projection.action == PAIRS[decision][0]
    assert not projection.source_policy_update_allowed and not projection.producer_credit_allowed
    assert values['events'] == source_copy and policy_state == policy_copy
    _log(f'complete/{decision}', outcome='PASS', source_events=len(source_copy),
         anchored_events=len(anchored.events), assigned_events=len(assigned.events),
         native_evidence_id=receipt.native_evidence_id,
         auxiliary_observation_id=receipt.auxiliary_observation_id,
         projection=projection.payload(), native_replay_status=replay.status)


@pytest.mark.parametrize('control', ('wrong_version', 'wrong_subject', 'wrong_contract',
                                     'wrong_source_cut', 'preterminal', 'duplicate_anchor',
                                     'mutated_observation'))
def test_publication_controls_fail_closed(control):
    values, observation = source()
    args = anchor_args(values, observation)
    if control == 'wrong_version': args['update_version'] = 'attributed-v1'
    elif control == 'wrong_subject': args['expected_source_subject'] = 'peer-c@v1'
    elif control == 'wrong_contract': args['expected_contract_digest'] = 'f' * 64
    elif control == 'wrong_source_cut': args['source_read_cut'] -= 1
    elif control == 'preterminal':
        values['events'].pop(); args['source_events'] = values['events']
        args['source_read_cut'] = len(values['events'])
    elif control == 'duplicate_anchor':
        anchored, _ = publish_completion_anchor(**args)
        args['source_events'] = anchored.events
        args['source_read_cut'] = len(anchored.events)
    elif control == 'mutated_observation':
        args['observation'] = ObservationResult('PUBLISHED',
            replace(observation.observation, judgment='reject_redo'), None)
    with pytest.raises(ValueError) as exc:
        publish_completion_anchor(**args)
    _log(f'publication/{control}', outcome='REJECTED', reason=str(exc.value))


@pytest.mark.parametrize('control', ('wrong_anchor_version', 'wrong_subject',
                                     'wrong_assignment_cut', 'wrong_propensity',
                                     'mutated_projection', 'duplicate_assignment'))
def test_assignment_controls_fail_closed(control):
    values, observation = source('accept_with_rework')
    anchored, receipt = publish_completion_anchor(**anchor_args(values, observation))
    args = projection_args(anchored, receipt)
    if control == 'wrong_anchor_version': args['expected_anchor_version'] = 'attributed-v1'
    elif control == 'wrong_subject': args['expected_source_subject'] = 'peer-c@v1'
    elif control == 'wrong_assignment_cut': args['assignment_read_cut'] -= 1
    elif control == 'wrong_propensity': args['decision_propensity'] = 0.0
    if control in {'wrong_anchor_version','wrong_subject','wrong_assignment_cut','wrong_propensity'}:
        with pytest.raises(ValueError) as exc:
            make_assignment_projection(**args)
    else:
        projection = make_assignment_projection(**args)
        if control == 'mutated_projection':
            with pytest.raises(ValueError) as exc:
                replace(projection, judgment='reject_redo')
        else:
            assigned = record_projected_assignment(
                anchored.events, receipt, projection,
                expected_projection_digest=projection.projection_digest,
                expected_contract_digest=receipt.contract_digest,
                expected_source_subject=receipt.candidate_key,
                expected_anchor_version=OBSERVATION_ANCHOR_VERSION,
                assignment_read_cut=projection.assignment_read_cut,
                decision_propensity=projection.decision_propensity)
            with pytest.raises(ValueError) as exc:
                record_projected_assignment(
                    assigned.events, receipt, projection,
                    expected_projection_digest=projection.projection_digest,
                    expected_contract_digest=receipt.contract_digest,
                    expected_source_subject=receipt.candidate_key,
                    expected_anchor_version=OBSERVATION_ANCHOR_VERSION,
                    assignment_read_cut=projection.assignment_read_cut,
                    decision_propensity=projection.decision_propensity)
    _log(f'assignment/{control}', outcome='REJECTED', reason=str(exc.value))
