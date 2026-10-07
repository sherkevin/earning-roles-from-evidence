"""Frozen development controls for the manifest-bound PIPE3 terminal scorer."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_terminal_scorer_v2 import (  # noqa: E402
    MANIFEST, MANIFEST_SHA256, classify, run_terminal_scorer,
)

LOG = ROOT / 'experiments/logs/n03_terminal_scorer_v2_20261007'
CONFIG = json.loads((LOG / 'config.json').read_text())


def _log(event_type, payload):
    with (LOG / 'raw.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                                 'event_type': event_type, 'payload': payload},
                                ensure_ascii=False, sort_keys=True) + '\n')
        stream.flush()


def _sources(seed):
    materials = build_materials(load_pipe3(seed))
    producer = materials['agent_payloads']['producer']['source_files']
    recipient = materials['agent_payloads']['recipient']['source_files']
    return {'producer.py': producer['producer.py'], 'processor.py': recipient['processor.py'],
            'sink.py': recipient['sink.py'], 'models.py': recipient['models.py']}


def _correct_producer(source, timestamp):
    anchor = '    return json.dumps(data, default=str)'
    assert anchor in source
    return source.replace(anchor, f'    data["{timestamp}"] = event.{timestamp}.isoformat()\n    return json.dumps(data)', 1)


def _correct_processor(source, *, escape=False):
    source = source.replace('open(output_path, "w", encoding="latin-1")',
                            'open(output_path, "w", encoding="utf-8")', 1)
    old = '            envelope = {"data": processed}\n            fout.write(json.dumps(envelope, ensure_ascii=False) + "\\n")'
    assert old in source
    replacement = '            fout.write(json.dumps(processed, ensure_ascii=' + ('True' if escape else 'False') + ') + "\\n")'
    return source.replace(old, replacement, 1)


@pytest.mark.parametrize('seed', [0, 1])
@pytest.mark.parametrize('name', CONFIG['cases'])
def test_real_local_worker_cases(seed, name):
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256 == CONFIG['manifest_sha256']
    sources = _sources(seed)
    timestamp = 'timestamp' if seed == 0 else 'measured_at'
    if name in ('correct_both', 'producer_only_fixed', 'recipient_only_fixed', 'unicode_escaped_correct'):
        if name in ('correct_both', 'producer_only_fixed', 'unicode_escaped_correct'):
            sources['producer.py'] = _correct_producer(sources['producer.py'], timestamp)
        if name in ('correct_both', 'recipient_only_fixed', 'unicode_escaped_correct'):
            sources['processor.py'] = _correct_processor(sources['processor.py'], escape=name == 'unicode_escaped_correct')
    elif name == 'permission_failure':
        sources['producer.py'] = 'def produce_events(events, output_path):\n    raise PermissionError("denied")\n'
    case_dir = LOG / f'seed_{seed}' / name
    case_dir.parent.mkdir(exist_ok=True)
    result = run_terminal_scorer(sources, 'PIPE3_stream_processing', seed, case_dir, _log)
    row = {'seed': seed, 'case': name, 'expected': CONFIG['expected_status'][name],
           'result': result, 'source_sha256': {key: hashlib.sha256(value.encode()).hexdigest()
                                              for key, value in sources.items()},
           'manifest_sha256': MANIFEST_SHA256}
    _log('case_result', row)
    assert result['status'] == CONFIG['expected_status'][name]
    assert result['label'] == (None if result['status'] == 'UNKNOWN' else int(result['status'] == 'PASS'))
    assert result['scorer_wall_seconds'] >= 0
    assert result['worker_input_sha256']
    assert result['response_digest']
    assert (case_dir / 'sandbox/launch.json').is_file()


def test_strict_response_controls(tmp_path):
    response = json.loads((LOG / 'seed_0/correct_both/response.json').read_text())
    request = response['request']
    worker = response['response']
    kwargs = {'artifact_sha256': request['artifact_sha256'], 'manifest_sha256': request['manifest_sha256'],
              'holdout_digest': request['holdout_digest'], 'manifest_case_seed': request['manifest_case_seed'],
              'worker_input_sha256': request['worker_input_sha256'], 'task_id': request['task_id'], 'seed': request['seed']}
    cases = {'malformed_response': {**worker, 'checks': 'bad'},
             'digest_mismatch': {**worker, 'worker_input_sha256': 'f' * 64},
             'resource_failure': {'ok': False, 'error_type': 'MemoryError', 'message': 'resource'}}
    for name, altered in cases.items():
        result = classify(altered, **kwargs)
        _log('control_result', {'case': name, 'result': result, 'input_digest': hashlib.sha256(json.dumps(altered,sort_keys=True).encode()).hexdigest()})
        assert result['status'] == 'UNKNOWN' and result['label'] is None
    sources = _sources(0)
    corrupt = tmp_path / 'manifest.json'
    corrupt.write_bytes(MANIFEST.read_bytes() + b' ')
    result = run_terminal_scorer(sources, 'PIPE3_stream_processing', 0, tmp_path / 'mismatch', _log,
                                 manifest_path=corrupt)
    _log('control_result', {'case': 'manifest_hash_mismatch', 'result': result})
    assert result['status'] == 'UNKNOWN' and result['label'] is None
    assert result['scorer_wall_seconds'] >= 0
