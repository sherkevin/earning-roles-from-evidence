"""Zero-call native completion and assignment chain for noisy observations."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import pytest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'references/aamas'))
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, ProducerScore,
    RecipientJudgment, TerminalOutcome,
)
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_baseline_policies import CandidateRef, NoUpdatePolicy, UniformPolicy  # noqa: E402
from peerrolebench_judgment_observation import (  # noqa: E402
    FrozenObservationContract, ObservationResult, build_judgment_observation,
)
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_observation_bridge import (  # noqa: E402
    OBSERVATION_ANCHOR_VERSION, make_assignment_projection,
    publish_completion_anchor, record_projected_assignment,
)
from peerrolebench_pipe3_material_adapter import digest_files  # noqa: E402

_LOG_ENV = os.environ.get('PEERROLE_OBSERVATION_BRIDGE_TEST_LOG')
LOG = Path(_LOG_ENV).resolve() if _LOG_ENV else None
if LOG is not None:
    if not LOG.is_dir() or (LOG / 'raw.jsonl').exists():
        raise RuntimeError('explicit observation bridge test log must be a new prepared directory')
REGISTRY = CandidateRegistryEntry('peer-b', 'v1', 'a' * 64, 'model', 'b' * 64)
PAIRS = {'accept': ('use', True), 'accept_with_rework': ('repair', True),
         'reject_redo': ('independent_redo', False)}


def _log(case, *, outcome, **extra):
    if LOG is None:
        return
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
    policy = UniformPolicy()
    preview = policy.choose(event_id='preview-1', context_key='PIPE3', selector_id='peer-a',
                            candidates=(CandidateRef('peer-c', 'v1'), CandidateRef('peer-b', 'v1')),
                            base_scores=(0.0, 0.0), rng=np.random.default_rng(0),
                            state_version='initial', encoder_version='public-v1',
                            feature_schema='public-v1')
    assert preview.chosen.key == REGISTRY.key and policy.updates == 0
    return dict(anchored_events=ledger.events, receipt=receipt, assignment_id='as1',
                expected_receipt_digest=receipt.receipt_digest, preview=preview,
                expected_preview_digest=canonical_digest(asdict(preview)),
                expected_menu_keys=('peer-c@v1', 'peer-b@v1'),
                expected_candidate_source_digest=REGISTRY.source_digest,
                expected_contract_digest=receipt.contract_digest,
                expected_source_subject=receipt.candidate_key,
                expected_anchor_version=OBSERVATION_ANCHOR_VERSION,
                task_id=receipt.task_id, target_task_index=receipt.target_task_index,
                assignment_read_cut=len(ledger.events), decision_propensity=preview.propensity)


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()


def record_args(events, receipt, projection, preview_args):
    return dict(anchored_events=events, receipt=receipt, projection=projection,
                expected_projection_digest=projection.projection_digest,
                expected_receipt_digest=preview_args['expected_receipt_digest'],
                preview=preview_args['preview'],
                expected_preview_digest=preview_args['expected_preview_digest'],
                expected_menu_keys=preview_args['expected_menu_keys'],
                expected_candidate_source_digest=preview_args['expected_candidate_source_digest'],
                expected_contract_digest=receipt.contract_digest,
                expected_source_subject=receipt.candidate_key,
                expected_anchor_version=OBSERVATION_ANCHOR_VERSION,
                assignment_read_cut=projection.assignment_read_cut,
                decision_propensity=projection.decision_propensity)


@pytest.mark.parametrize('decision', tuple(PAIRS))
def test_complete_native_chain_keeps_observation_separate_from_credit(decision):
    values, observation = source(decision)
    source_copy = deepcopy(values['events'])
    anchored, receipt = publish_completion_anchor(**anchor_args(values, observation))
    preview_args = projection_args(anchored, receipt)
    projection = make_assignment_projection(**preview_args)
    assigned = record_projected_assignment(**record_args(anchored.events, receipt, projection, preview_args))
    assigned.record_selection(PeerSelection('s1', 'PIPE3', 1, 'peer-a', 'producer',
                                            tuple(ref.candidate_id for ref in preview_args['preview'].candidates),
                                            preview_args['preview'].chosen_id,
                                            preview_args['preview'].propensity))
    replay = replay_ledger_events(assigned.events, allow_incomplete=True)
    assert replay.status == 'UNKNOWN' and replay.missing == (
        {'stage': 'task_start', 'task_id': 'PIPE3', 'task_index': 1},
        {'stage': 'producer_delivery', 'task_id': 'PIPE3', 'task_index': 1})
    assert [x['event_type'] for x in assigned.events[-3:]] == [
        'role_evidence_update', 'later_assignment', 'peer_selection']
    assert assigned.assignments['as1'].evidence_ids == (receipt.native_evidence_id,)
    assert receipt.native_evidence_id != receipt.auxiliary_observation_id
    assert projection.judgment == decision and projection.action == PAIRS[decision][0]
    assert projection.preview_digest == preview_args['expected_preview_digest']
    assert not projection.source_policy_update_allowed and not projection.producer_credit_allowed
    assert values['events'] == source_copy
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
                                     'mutated_projection', 'duplicate_assignment',
                                     'wrong_receipt_pin', 'recomputed_receipt_mutation',
                                     'wrong_preview_pin', 'preview_selects_c',
                                     'preview_probability_mismatch'))
def test_assignment_controls_fail_closed(control):
    values, observation = source('accept_with_rework')
    anchored, receipt = publish_completion_anchor(**anchor_args(values, observation))
    args = projection_args(anchored, receipt)
    if control == 'wrong_anchor_version': args['expected_anchor_version'] = 'attributed-v1'
    elif control == 'wrong_subject': args['expected_source_subject'] = 'peer-c@v1'
    elif control == 'wrong_assignment_cut': args['assignment_read_cut'] -= 1
    elif control == 'wrong_propensity': args['decision_propensity'] = 0.0
    elif control == 'wrong_receipt_pin': args['expected_receipt_digest'] = 'f' * 64
    elif control == 'recomputed_receipt_mutation':
        body = receipt.payload(include_digest=False)
        body['observation_digest'] = 'f' * 64
        args['receipt'] = replace(receipt, observation_digest='f' * 64,
                                  receipt_digest=canonical_digest(body))
    elif control == 'wrong_preview_pin': args['expected_preview_digest'] = 'f' * 64
    elif control == 'preview_selects_c':
        policy = UniformPolicy()
        args['preview'] = policy.choose(event_id='preview-c', context_key='PIPE3', selector_id='peer-a',
            candidates=(CandidateRef('peer-c', 'v1'), CandidateRef('peer-b', 'v1')),
            base_scores=(0.0, 0.0), rng=np.random.default_rng(2),
            state_version='initial', encoder_version='public-v1', feature_schema='public-v1')
        assert args['preview'].chosen.key == 'peer-c@v1'
        args['expected_preview_digest'] = canonical_digest(asdict(args['preview']))
    elif control == 'preview_probability_mismatch':
        policy = NoUpdatePolicy()
        args['preview'] = policy.choose(event_id='preview-unequal', context_key='PIPE3', selector_id='peer-a',
            candidates=(CandidateRef('peer-c', 'v1'), CandidateRef('peer-b', 'v1')),
            base_scores=(0.5, 0.0), rng=np.random.default_rng(0),
            state_version='initial', encoder_version='public-v1', feature_schema='public-v1')
        assert args['preview'].chosen.key == REGISTRY.key
        assert args['preview'].propensity != 0.5
        args['expected_preview_digest'] = canonical_digest(asdict(args['preview']))
    if control not in {'mutated_projection','duplicate_assignment'}:
        with pytest.raises(ValueError) as exc:
            make_assignment_projection(**args)
    else:
        projection = make_assignment_projection(**args)
        if control == 'mutated_projection':
            with pytest.raises(ValueError) as exc:
                replace(projection, judgment='reject_redo')
        else:
            assigned = record_projected_assignment(**record_args(anchored.events, receipt, projection, args))
            with pytest.raises(ValueError) as exc:
                record_projected_assignment(**record_args(assigned.events, receipt, projection, args))
    _log(f'assignment/{control}', outcome='REJECTED', reason=str(exc.value))


@pytest.mark.parametrize('control', ('wrong_selected_peer', 'mismatched_selection_propensity'))
def test_native_selection_must_consume_sealed_assignment(control):
    values, observation = source()
    anchored, receipt = publish_completion_anchor(**anchor_args(values, observation))
    preview_args = projection_args(anchored, receipt)
    projection = make_assignment_projection(**preview_args)
    assigned = record_projected_assignment(**record_args(anchored.events, receipt, projection, preview_args))
    assert assigned.assignments['as1'].decision_propensity == 0.5
    chosen = 'peer-c' if control == 'wrong_selected_peer' else 'peer-b'
    propensity = 0.5 if control == 'wrong_selected_peer' else 0.6
    with pytest.raises(ValueError) as exc:
        assigned.record_selection(PeerSelection('s1', 'PIPE3', 1, 'peer-a', 'producer',
                                                ('peer-b', 'peer-c'), chosen, propensity))
    _log(f'native_selection/{control}', outcome='REJECTED', reason=str(exc.value),
         assigned_propensity=0.5, attempted_propensity=propensity,
         assigned_peer='peer-b', attempted_peer=chosen)
