"""Offline controls for per-actor, per-stream public transcript memory."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from peerrolebench_actor_experience import ActorExperience, digest  # noqa: E402


def record(store, index, *, response=None, interaction_id=None):
    return store.record_completed_interaction(
        interaction_id=interaction_id or f'call-{index}', task_index=index,
        task_input={'task_id': 'PIPE3', 'public_prompt': f'Produce artifact for task {index}'},
        actor_response=response or {'source_files': {'producer.py': f'# answer {index}'}},
        model_metadata={'model_id': 'same-model', 'usage': {'input_tokens': 10, 'output_tokens': 4},
                        'stage': 'producer'},
    )


def test_independent_actor_stream_arm_and_future_exclusion():
    stores = {(stream, arm, actor): ActorExperience(stream_id=stream, arm_id=arm, actor_id=actor)
              for stream, arm, actor in [('s0', 'RARE', 'peer-b'), ('s0', 'RARE', 'peer-c'),
                                         ('s0', 'control', 'peer-b'), ('s1', 'RARE', 'peer-b')]}
    assert len({store.materialize_prompt(1) for store in stores.values()}) == 1
    record(stores['s0', 'RARE', 'peer-b'], 0)
    assert len(stores['s0', 'RARE', 'peer-b'].read_before(1)) == 1
    with pytest.raises(ValueError, match='future decision'):
        stores['s0', 'RARE', 'peer-b'].read_before(0)
    assert all(other.read_before(1) == [] for key, other in stores.items() if key != ('s0', 'RARE', 'peer-b'))


def test_suffix_retention_copy_and_replay():
    store = ActorExperience(stream_id='s', arm_id='a', actor_id='p', max_entries=2)
    for index in range(2):
        record(store, index)
    decision_2_snapshot = store.snapshot()
    assert [row['task_index'] for row in store.read_before(2)] == [0, 1]
    record(store, 2)
    assert [row['task_index'] for row in store.read_before(3)] == [1, 2]
    copied = store.read_before(3)
    copied[0]['actor_response']['source_files']['producer.py'] = 'mutated'
    assert store.read_before(3)[0]['actor_response']['source_files']['producer.py'] == '# answer 1'
    snapshot = store.snapshot()
    restored = ActorExperience.restore(json.loads(json.dumps(snapshot)), stream_id='s', arm_id='a', actor_id='p')
    assert restored.snapshot() == snapshot
    assert restored.materialize_prompt(3) == store.materialize_prompt(3)
    with pytest.raises(ValueError, match='future decision'):
        store.read_before(2)
    decision_2 = ActorExperience.restore(decision_2_snapshot, stream_id='s', arm_id='a', actor_id='p')
    assert [row['task_index'] for row in decision_2.read_before(2)] == [0, 1]


def test_idempotence_monotonicity_and_state_cap_are_fail_closed():
    store = ActorExperience(stream_id='s', arm_id='a', actor_id='p', max_entries=1)
    first = record(store, 0)
    assert record(store, 0) == first
    record(store, 1)
    # An evicted interaction still has an idempotence receipt.
    assert record(store, 0) == first
    before = store.snapshot()
    with pytest.raises(ValueError, match='conflicting duplicate'):
        record(store, 0, response={'source_files': {'producer.py': '# changed'}})
    with pytest.raises(ValueError, match='strictly'):
        record(store, 1, interaction_id='different')
    assert store.snapshot() == before
    tight = ActorExperience(stream_id='s', arm_id='a', actor_id='p', max_state_bytes=1024)
    with pytest.raises(ValueError, match='byte cap'):
        tight.record_completed_interaction(
            interaction_id='oversize', task_index=0,
            task_input={'prompt': 'A' * 1500}, actor_response={'result': 'ok'},
            model_metadata={'model_id': 'same-model'},
        )
    assert tight.read_before(1) == []


def test_private_fields_extra_fields_and_tampered_restore_rejected():
    store = ActorExperience(stream_id='s', arm_id='a', actor_id='p')
    with pytest.raises(ValueError, match='private/evaluator'):
        store.record_completed_interaction(
            interaction_id='bad', task_index=0, task_input={'hidden_tests': ['secret']},
            actor_response={}, model_metadata={'model_id': 'm'},
        )
    with pytest.raises(ValueError, match='unsupported'):
        store.record_completed_interaction(
            interaction_id='bad', task_index=0, task_input={}, actor_response={},
            model_metadata={'model_id': 'm', 'evaluator_score': 1},
        )
    record(store, 0)
    snap = store.snapshot()
    with pytest.raises(ValueError, match='namespace'):
        ActorExperience.restore(snap, stream_id='other', arm_id='a', actor_id='p')
    rekeyed = deepcopy(snap)
    rekeyed['actor_id'] = 'other'
    rekeyed['state_digest'] = digest({k: v for k, v in rekeyed.items() if k != 'state_digest'})
    with pytest.raises(ValueError, match='namespace'):
        ActorExperience.restore(rekeyed, stream_id='s', arm_id='a', actor_id='p')
    altered = deepcopy(snap)
    altered['entries'][0]['actor_response']['source_files']['producer.py'] = 'tampered'
    with pytest.raises(ValueError, match='hash mismatch'):
        ActorExperience.restore(altered, stream_id='s', arm_id='a', actor_id='p')
    altered = deepcopy(snap)
    altered['entries'][0]['extra'] = 'illegal'
    altered['state_digest'] = digest({k: v for k, v in altered.items() if k != 'state_digest'})
    with pytest.raises(ValueError, match='entry schema'):
        ActorExperience.restore(altered, stream_id='s', arm_id='a', actor_id='p')
