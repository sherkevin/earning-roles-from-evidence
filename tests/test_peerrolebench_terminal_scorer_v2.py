"""Frozen development controls for the manifest-bound PIPE3 terminal scorer."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_terminal_scorer_v2 import (  # noqa: E402
    MANIFEST, MANIFEST_SHA256, classify, run_terminal_scorer,
)

CASES = ('correct_both', 'original', 'producer_only_fixed', 'recipient_only_fixed',
         'unicode_escaped_correct', 'permission_failure')
EXPECTED = {'correct_both': 'PASS', 'original': 'FAIL', 'producer_only_fixed': 'FAIL',
            'recipient_only_fixed': 'PASS', 'unicode_escaped_correct': 'PASS',
            'permission_failure': 'UNKNOWN'}


@pytest.fixture(scope='session')
def runlog(tmp_path_factory):
    configured = os.environ.get('PEERROLE_Y_TEST_LOG')
    if configured:
        output = Path(configured).resolve()
        output.mkdir(parents=True, exist_ok=False)
    else:
        output = tmp_path_factory.mktemp('terminal-v2')
    files = [ROOT / 'scripts/peerrolebench_pipe3_terminal_scorer_v2.py',
             ROOT / 'scripts/peerrolebench_pipe3_terminal_scorer_worker_v2.py',
             ROOT / 'tests/test_peerrolebench_terminal_scorer_v2.py']
    config = {'qualification_version': 'pipe3-terminal-holdout-qualification-v2',
              'frozen_before_execution': True, 'task_id': 'PIPE3_stream_processing',
              'manifest_path': str(MANIFEST), 'manifest_sha256': MANIFEST_SHA256,
              'seeds': [0, 1], 'cases': list(CASES), 'expected_status': EXPECTED,
              'controls': ['malformed_response', 'digest_mismatch', 'resource_failure',
                           'manifest_hash_mismatch'], 'real_api_calls': 0, 'gpu_jobs': 0,
              'native_grader_invoked': False, 'scientific_claim_allowed': False,
              'same_process_instrumentation_tamper_proof': False,
              'seed_root_relation': 'same structural root; development-only',
              'source_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in files},
              'test_command': 'python3 -m pytest -q tests/test_peerrolebench_terminal_scorer_v2.py',
              'python': sys.version, 'platform': platform.platform(),
              'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'started_at_utc': datetime.now(timezone.utc).isoformat()}
    (output / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    yield output
    rows = [json.loads(line) for line in (output / 'raw.jsonl').read_text().splitlines()]
    cases = [row['payload'] for row in rows if row['event_type'] == 'case_result']
    controls = [row['payload'] for row in rows if row['event_type'] == 'control_result']
    summary = {'passed': len(cases) == 12 and all(row['result']['status'] == EXPECTED[row['case']] for row in cases)
               and len(controls) == 4 and all(row['result']['status'] == 'UNKNOWN' for row in controls),
               'case_count': len(cases), 'control_count': len(controls),
               'statuses': {str(seed): {row['case']: row['result']['status'] for row in cases if row['seed'] == seed}
                            for seed in (0, 1)},
               'controls': {row['case']: row['result']['status'] for row in controls},
               'config_sha256': hashlib.sha256((output / 'config.json').read_bytes()).hexdigest(),
               'ended_at_utc': datetime.now(timezone.utc).isoformat()}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')


def _log(output, event_type, payload):
    with (output / 'raw.jsonl').open('a', encoding='utf-8') as stream:
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
@pytest.mark.parametrize('name', CASES)
def test_real_local_worker_cases(seed, name, runlog):
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256
    sources = _sources(seed)
    timestamp = 'timestamp' if seed == 0 else 'measured_at'
    if name in ('correct_both', 'producer_only_fixed', 'recipient_only_fixed', 'unicode_escaped_correct'):
        if name in ('correct_both', 'producer_only_fixed', 'unicode_escaped_correct'):
            sources['producer.py'] = _correct_producer(sources['producer.py'], timestamp)
        if name in ('correct_both', 'recipient_only_fixed', 'unicode_escaped_correct'):
            sources['processor.py'] = _correct_processor(sources['processor.py'], escape=name == 'unicode_escaped_correct')
    elif name == 'permission_failure':
        sources['producer.py'] = 'def produce_events(events, output_path):\n    raise PermissionError("denied")\n'
    case_dir = runlog / f'seed_{seed}' / name
    case_dir.parent.mkdir(exist_ok=True)
    result = run_terminal_scorer(sources, 'PIPE3_stream_processing', seed, case_dir,
                                 lambda event, payload: _log(runlog, event, payload))
    row = {'seed': seed, 'case': name, 'expected': EXPECTED[name],
           'result': result, 'source_sha256': {key: hashlib.sha256(value.encode()).hexdigest()
                                              for key, value in sources.items()},
           'manifest_sha256': MANIFEST_SHA256}
    _log(runlog, 'case_result', row)
    assert result['status'] == EXPECTED[name]
    assert result['label'] == (None if result['status'] == 'UNKNOWN' else int(result['status'] == 'PASS'))
    assert result['scorer_wall_seconds'] >= 0
    assert result['worker_input_sha256']
    assert result['response_digest']
    assert (case_dir / 'sandbox/launch.json').is_file()


def test_strict_response_controls(tmp_path, runlog):
    response = json.loads((runlog / 'seed_0/correct_both/response.json').read_text())
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
        _log(runlog, 'control_result', {'case': name, 'result': result, 'input_digest': hashlib.sha256(json.dumps(altered,sort_keys=True).encode()).hexdigest()})
        assert result['status'] == 'UNKNOWN' and result['label'] is None
    sources = _sources(0)
    corrupt = tmp_path / 'manifest.json'
    corrupt.write_bytes(MANIFEST.read_bytes() + b' ')
    result = run_terminal_scorer(sources, 'PIPE3_stream_processing', 0, tmp_path / 'mismatch',
                                 lambda event, payload: _log(runlog, event, payload),
                                 manifest_path=corrupt)
    _log(runlog, 'control_result', {'case': 'manifest_hash_mismatch', 'result': result})
    assert result['status'] == 'UNKNOWN' and result['label'] is None
    assert result['scorer_wall_seconds'] >= 0
