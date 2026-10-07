"""Offline software contract tests. No model request or model result is simulated."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from peerrolebench_actor_experience import ActorExperience
from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_live_producer_stage import (
    finalize, model_config_digest, policy_digest, prepare_request, run_generation,
)
from peerrolebench_pipe3_public_contract_v2 import CLAUSES


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
                'elapsed_seconds': 0.1}
    first = finalize(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                     metadata=metadata, recipient_id='recipient', interaction_id='i0',
                     delivery_id='d0', source_event_id='e0',
                     expected_request_digest=prepared['decision_digest'])
    second = finalize(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 3\n'}},
                      metadata=metadata, recipient_id='recipient', interaction_id='i1',
                      delivery_id='d1', source_event_id='e1',
                      expected_request_digest=prepared['decision_digest'])
    assert first['candidate'] == second['candidate']
    assert first['delivery']['artifact_sha256'] != second['delivery']['artifact_sha256']
    assert first['after'] != second['after']
    assert experience.snapshot() == prepared['before']
    with pytest.raises(ValueError):
        finalize(prepared=prepared, parsed={'source_files': {}}, metadata=metadata,
                 recipient_id='recipient', interaction_id='bad', delivery_id='bad', source_event_id='bad',
                 expected_request_digest=prepared['decision_digest'])
    with pytest.raises(ValueError):
        finalize(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                 metadata={'usage_complete': False}, recipient_id='recipient',
                 interaction_id='bad', delivery_id='bad', source_event_id='bad',
                 expected_request_digest=prepared['decision_digest'])
    with pytest.raises(ValueError):
        finalize(prepared=prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
                 metadata=metadata, recipient_id='recipient', interaction_id='bad',
                 delivery_id='bad', source_event_id='bad', expected_request_digest='0' * 64)
    changed_prepared = dict(prepared, prompt=prepared['prompt'] + 'changed')
    with pytest.raises(ValueError):
        finalize(prepared=changed_prepared, parsed={'source_files': {'producer.py': 'x = 2\n'}},
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
