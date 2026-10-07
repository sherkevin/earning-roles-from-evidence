"""Offline software contract tests. No model request or model result is simulated."""
from pathlib import Path
import hashlib
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from peerrolebench_actor_experience import ActorExperience, canonical_bytes
from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_live_producer_stage import (
    _finalize_software_fixture, finalize, model_config_digest, policy_digest,
    prepare_request, run_generation,
)
from peerrolebench_pipe3_public_contract_v2 import CLAUSES
from peerrolebench_actor_experience import digest
from peerrolebench_real_closed_loop import parse_sse
import peerrolebench_live_producer_stage as stage


BASE = {'task_id': 'PIPE3_stream_processing', 'seed': 0, 'role': 'producer',
        'task_text': {'spec_md': 'Public specification', 'brief_md': 'Public brief'},
        'source_files': {'producer.py': 'x = 1\n', 'models.py': 'class Event: pass\n',
                         'sink.py': 'def sink(x): pass\n'},
        'writable_paths': ['producer.py'], 'required_delivery_paths': [],
        'contract_clause_refs': list(CLAUSES)}
CARD = {'real_api_runs_allowed': False, 'stream_id': 's', 'arm_id': 'a',
        'model': 'fixture-model', 'temperature': 0,
        'max_tokens': {'producer': 1024}, 'stream': True, 'thinking': {'type': 'disabled'},
        'request_timeout_seconds': 30, 'maximum_task_requests': 1,
        'budget': {'prior_attempted_episodes': 31, 'additional_cap': 1,
                   'attempted_ledger': []}}


def fixture(version='v1', card=CARD):
    candidate = CandidateRegistryEntry('producer-a', version, policy_digest(),
                                       card['model'], model_config_digest(card))
    experience = ActorExperience(stream_id='s', arm_id='a', actor_id=candidate.key)
    return candidate, experience


def test_history_excludes_metadata_ids_and_future_rows():
    candidate, experience = fixture()
    experience.record_completed_interaction(interaction_id='secret-id', task_index=0,
        task_input=BASE, actor_response={'source_files': {'producer.py': 'x = 2\n'}},
        model_metadata={'model_id': 'fixture-model', 'request_id': 'secret-request'})
    prepared = prepare_request(base_payload=BASE, candidate=candidate,
                               experience=experience, task_index=1, card=CARD)
    assert 'secret-id' not in prepared['prompt']
    assert 'secret-request' not in prepared['prompt']
    assert 'model_metadata' not in prepared['prompt']
    assert prepared['history'][0]['task_index'] == 0
    assert prepared['before'] == experience.snapshot()
    assert experience.snapshot() == prepared['before']
    with pytest.raises(ValueError):
        prepare_request(base_payload=BASE, candidate=candidate,
                        experience=experience, task_index=0, card=CARD)


def test_wrong_actor_version_policy_and_config_rejected():
    candidate, experience = fixture()
    other, _ = fixture('v2')
    with pytest.raises(ValueError):
        prepare_request(base_payload=BASE, candidate=other,
                        experience=experience, task_index=0, card=CARD)
    changed = dict(CARD, temperature=0.5)
    with pytest.raises(ValueError):
        prepare_request(base_payload=BASE, candidate=candidate,
                        experience=experience, task_index=0, card=changed)
    changed_source = CandidateRegistryEntry('producer-a', 'v1', 'a' * 64,
                                            CARD['model'], model_config_digest(CARD))
    with pytest.raises(ValueError):
        prepare_request(base_payload=BASE, candidate=changed_source,
                        experience=experience, task_index=0, card=CARD)
    with pytest.raises(ValueError):
        prepare_request(base_payload=BASE, candidate=candidate,
                        experience=experience, task_index=0, card=dict(CARD, arm_id='other'))
    with pytest.raises(ValueError):
        prepare_request(base_payload={k: v for k, v in BASE.items() if k != 'contract_clause_refs'},
                        candidate=candidate, experience=experience, task_index=0, card=CARD)


def test_distinct_delivery_artifacts_keep_stable_candidate():
    candidate, experience = fixture()
    prepared = prepare_request(base_payload=BASE, candidate=candidate,
                               experience=experience, task_index=0, card=CARD)
    # Explicit handwritten software fixtures, not claimed as model outputs.
    metadata = {'usage_complete': True, 'usage': {'input_tokens': 1, 'output_tokens': 1},
                'http_status': '200', 'exit_code': 0, 'stop_reason': 'end_turn',
                'elapsed_seconds': 0.1, 'returned_model': 'fixture-model',
                'thinking_delta_count': 0}
    first = _finalize_software_fixture(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                     metadata=metadata, recipient_id='recipient', interaction_id='i0',
                     delivery_id='d0', source_event_id='e0',
                     expected_request_digest=prepared['decision_digest'])
    second = _finalize_software_fixture(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 3\n'}},
                      metadata=metadata, recipient_id='recipient', interaction_id='i1',
                      delivery_id='d1', source_event_id='e1',
                      expected_request_digest=prepared['decision_digest'])
    assert first['candidate'] == second['candidate']
    assert first['delivery']['artifact_sha256'] != second['delivery']['artifact_sha256']
    assert first['after'] != second['after']
    assert experience.snapshot() == prepared['before']
    with pytest.raises(ValueError):
        _finalize_software_fixture(prepared=prepared, parsed={'source_files': {}}, metadata=metadata,
                 recipient_id='recipient', interaction_id='bad', delivery_id='bad', source_event_id='bad',
                 expected_request_digest=prepared['decision_digest'])
    with pytest.raises(ValueError):
        _finalize_software_fixture(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                 metadata={'usage_complete': False}, recipient_id='recipient',
                 interaction_id='bad', delivery_id='bad', source_event_id='bad',
                 expected_request_digest=prepared['decision_digest'])
    with pytest.raises(ValueError):
        _finalize_software_fixture(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                 metadata=metadata, recipient_id='recipient', interaction_id='bad',
                 delivery_id='bad', source_event_id='bad', expected_request_digest='0' * 64)
    changed_prepared = dict(prepared, prompt=prepared['prompt'] + 'changed')
    with pytest.raises(ValueError):
        _finalize_software_fixture(prepared=changed_prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                 metadata=metadata, recipient_id='recipient', interaction_id='bad',
                 delivery_id='bad', source_event_id='bad',
                 expected_request_digest=prepared['decision_digest'])


def test_disabled_gate_rejects_before_provider_or_directory(tmp_path):
    candidate, experience = fixture()
    prepared = prepare_request(base_payload=BASE, candidate=candidate,
                               experience=experience, task_index=0, card=CARD)
    output = tmp_path / 'attempt'
    with pytest.raises(PermissionError, match='disabled'):
        run_generation(prepared=prepared, card=CARD, expected_card_digest='anything',
                       output_dir=output, reservation_path=tmp_path / 'absent.json',
                       expected_reservation_digest='anything')
    assert not output.exists()


def test_sealed_disk_completion_and_replay_rejection(tmp_path, monkeypatch):
    # SOFTWARE FIXTURE: handwritten wire frames; no provider request occurred.
    live_card = dict(CARD, real_api_runs_allowed=True)
    candidate, experience = fixture(card=live_card)
    prepared = prepare_request(base_payload=BASE, candidate=candidate,
                               experience=experience, task_index=0, card=live_card)
    out = tmp_path / 'software_fixture'
    (out / 'episode').mkdir(parents=True)
    reservation_root = tmp_path / 'software_reservations'
    reservation_root.mkdir()
    monkeypatch.setattr(stage, 'RESERVATION_ROOT', reservation_root)
    reservation_path = reservation_root / 'software-r1.json'
    reservation = {'status': 'reserved', 'reservation_id': 'software-r1',
                   'card_digest': digest(live_card), 'prompt_sha256': prepared['prompt_sha256'],
                   'candidate_key': candidate.key, 'task_index': 0, 'ordinal': 1}
    reservation_path.write_bytes(canonical_bytes(reservation))
    reservation_sha = hashlib.sha256(reservation_path.read_bytes()).hexdigest()
    (reservation_root / 'software-r1.claimed').write_bytes(canonical_bytes(
        {'reservation_digest': reservation_sha, 'output_dir': str(out)}))
    metadata = {'usage_complete': True, 'usage': {'input_tokens': 1, 'output_tokens': 1},
                'http_status': '200', 'exit_code': 0, 'stop_reason': 'end_turn',
                'elapsed_seconds': 0.1, 'returned_model': 'fixture-model',
                'thinking_delta_count': 0}
    sources = {'source_files': {'producer.py': 'x = 2\n'}}
    frames = [
        {'type': 'message_start', 'message': {'model': 'fixture-model', 'id': 'fixture-id',
                                               'usage': {'input_tokens': 0, 'output_tokens': 0}}},
        {'type': 'content_block_start', 'index': 0,
         'content_block': {'type': 'text', 'text': json.dumps(sources)}},
        {'type': 'message_delta', 'delta': {'stop_reason': 'end_turn'},
         'usage': {'input_tokens': 1, 'output_tokens': 1}},
        {'type': 'message_stop'},
    ]
    wire_text = ''.join('data: ' + json.dumps(frame) + '\n\n' for frame in frames)
    parsed_wire = parse_sse(wire_text)
    card_sha = digest(live_card)
    documents = {
        'config.json': {'card': live_card, 'card_digest': card_sha, 'prepared': prepared,
                        'reservation_digest': reservation_sha, 'reservation_path': str(reservation_path),
                        'status': 'UNKNOWN'},
        'episode/producer_request.json': {'model': live_card['model'],
            'messages': [{'role': 'user', 'content': prepared['prompt']}],
            'temperature': live_card['temperature'], 'max_tokens': live_card['max_tokens']['producer'],
            'stream': True, 'thinking': live_card['thinking']},
        'episode/producer_parsed_response.json': parsed_wire,
        'episode/producer_cost.json': metadata,
        'parsed_result.json': {'status': 'PARSED', 'parsed': sources, 'metadata': metadata,
                               'output_dir': str(out)},
    }
    for name, value in documents.items():
        (out / name).write_bytes(canonical_bytes(value))
    (out / 'episode/producer_response.sse').write_text(wire_text)
    paths = [*documents, 'episode/producer_response.sse']
    receipt = {'schema': 'peerrolebench-live-producer-stage-v1', 'status': 'PARSED',
               'decision_digest': prepared['decision_digest'], 'card_digest': card_sha,
               'reservation_digest': reservation_sha,
               'files': {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in paths}}
    (out / 'completion_receipt.json').write_bytes(canonical_bytes(receipt))
    seal = hashlib.sha256((out / 'completion_receipt.json').read_bytes()).hexdigest()
    done = finalize(prepared=prepared, output_dir=out, expected_receipt_digest=seal,
                    recipient_id='recipient', interaction_id='i0', delivery_id='d0', source_event_id='e0')
    assert done['status'] == 'COMPLETED'
    assert (out / 'completion.json').is_file()
    with pytest.raises(FileExistsError):
        finalize(prepared=prepared, output_dir=out, expected_receipt_digest=seal,
                 recipient_id='recipient', interaction_id='i0', delivery_id='d0', source_event_id='e0')
    tampered = dict(documents['parsed_result.json'])
    tampered['parsed'] = {'source_files': {'producer.py': 'x = 3\n'}}
    (out / 'parsed_result.json').write_bytes(canonical_bytes(tampered))
    receipt['files']['parsed_result.json'] = hashlib.sha256((out / 'parsed_result.json').read_bytes()).hexdigest()
    (out / 'completion_receipt.json').write_bytes(canonical_bytes(receipt))
    forged_seal = hashlib.sha256((out / 'completion_receipt.json').read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='differs from raw response'):
        finalize(prepared=prepared, output_dir=out, expected_receipt_digest=forged_seal,
                 recipient_id='recipient', interaction_id='i1', delivery_id='d1', source_event_id='e1')
    (out / 'parsed_result.json').write_bytes(canonical_bytes(documents['parsed_result.json']))
    receipt['files']['parsed_result.json'] = hashlib.sha256((out / 'parsed_result.json').read_bytes()).hexdigest()
    (out / 'completion_receipt.json').write_bytes(canonical_bytes(receipt))
    (out / 'episode/producer_response.sse').write_text('changed')
    with pytest.raises(ValueError, match='sealed transport file changed'):
        finalize(prepared=prepared, output_dir=out, expected_receipt_digest=seal,
                 recipient_id='recipient', interaction_id='i1', delivery_id='d1', source_event_id='e1')


@pytest.mark.parametrize('field,value', [
    ('temperature', float('nan')),
    ('request_timeout_seconds', 0),
    ('maximum_task_requests', 0),
    ('stream', 'true'),
    ('thinking', {'type': 'enabled'}),
    ('max_tokens', {'producer': 0}),
])
def test_invalid_transport_fields_rejected_before_provider(field, value):
    with pytest.raises(ValueError, match='transport configuration'):
        model_config_digest(dict(CARD, **{field: value}))


def test_returned_model_mismatch_is_not_completed():
    candidate, experience = fixture()
    prepared = prepare_request(base_payload=BASE, candidate=candidate,
                               experience=experience, task_index=0, card=CARD)
    metadata = {'usage_complete': True, 'usage': {'input_tokens': 1, 'output_tokens': 1},
                'http_status': '200', 'exit_code': 0, 'stop_reason': 'end_turn',
                'elapsed_seconds': 0.1, 'returned_model': 'another-model'}
    with pytest.raises(ValueError, match='returned model'):
        _finalize_software_fixture(prepared=prepared,
            parsed={'source_files': {'producer.py': 'x = 2\n'}}, metadata=metadata,
            recipient_id='recipient', interaction_id='i0', delivery_id='d0',
            source_event_id='e0', expected_request_digest=prepared['decision_digest'])
    assert experience.snapshot() == prepared['before']


def test_canonical_reservation_copy_and_reuse_rejected(tmp_path, monkeypatch):
    # Offline gate test: no provider or run_generation invocation.
    enabled = dict(CARD, real_api_runs_allowed=True)
    candidate, experience = fixture(card=enabled)
    prepared = prepare_request(base_payload=BASE, candidate=candidate,
                               experience=experience, task_index=0, card=enabled)
    root = tmp_path / 'budget_reservations'
    root.mkdir()
    monkeypatch.setattr(stage, 'RESERVATION_ROOT', root)
    reservation = {'status': 'reserved', 'reservation_id': 'r1', 'card_digest': digest(enabled),
                   'prompt_sha256': prepared['prompt_sha256'], 'candidate_key': candidate.key,
                   'task_index': 0, 'ordinal': 1}
    original = root / 'r1.json'
    original.write_bytes(canonical_bytes(reservation))
    seal = hashlib.sha256(original.read_bytes()).hexdigest()
    stage._check_live_gate(enabled, digest(enabled), prepared, tmp_path / 'fresh', original, seal)
    copied = tmp_path / 'r1.json'
    copied.write_bytes(original.read_bytes())
    with pytest.raises(PermissionError, match='canonical'):
        stage._check_live_gate(enabled, digest(enabled), prepared, tmp_path / 'fresh', copied, seal)
    (root / 'r1.claimed').write_text('used')
    with pytest.raises(PermissionError, match='claimed'):
        stage._check_live_gate(enabled, digest(enabled), prepared, tmp_path / 'fresh', original, seal)
