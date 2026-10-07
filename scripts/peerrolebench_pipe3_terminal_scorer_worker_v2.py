"""Private, development-only PIPE3 terminal worker (non-adversarial same process)."""
from __future__ import annotations

from datetime import datetime
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback

REQUEST_SCHEMA = 'pipe3-terminal-holdout-request-v2'
RESPONSE_SCHEMA = 'pipe3-terminal-holdout-response-v2'
SCORER_VERSION = 'pipe3-terminal-holdout-v2'
CHECK_IDS = ('T1_holdout_projection', 'T2_batch_cardinality', 'T3_unicode_semantics')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def _candidate_failure(exc, root):
    if isinstance(exc, (PermissionError, OSError, MemoryError, TimeoutError)):
        return None
    candidates = {(Path(root) / name).resolve(): name for name in ('producer.py', 'processor.py', 'sink.py', 'models.py')}
    for frame in traceback.extract_tb(exc.__traceback__):
        path = candidates.get(Path(frame.filename).resolve())
        if path:
            return {'failure_origin': 'candidate', 'source_path': path,
                    'exception_class': type(exc).__name__, 'reason': str(exc)}
    return None


def score(root, request):
    root = Path(root).resolve()
    try:
        sys.path.insert(0, str(root))
        models = importlib.import_module('models')
        producer = importlib.import_module('producer')
        processor = importlib.import_module('processor')
        sink = importlib.import_module('sink')
        case = request['case']
        fields = case['fields']
        cls = getattr(models, case['event_class'])
        events = []
        for record in case['input_records']:
            values = {name: (datetime.fromisoformat(record[name]) if name == fields['timestamp'] else record[name])
                      for name in cls.__dataclass_fields__}
            events.append(cls(**values))
        produced = root.parent / 'scratch' / 'terminal_produced.jsonl'
        processed = root.parent / 'scratch' / 'terminal_processed.jsonl'
        producer.produce_events(events, str(produced))
        processor.process_events(str(produced), str(processed))
        # JSON escapes are valid UTF-8 JSON. Check decoded meaning, never raw glyphs.
        decoded_lines = [json.loads(line) for line in processed.read_text(encoding='utf-8').splitlines() if line.strip()]
        records = sink.load_processed_events(str(processed))
        keys = [fields[key] for key in ('id', 'timestamp', 'user', 'action', 'value')]
        projection = [{key: row.get(key) for key in keys} for row in records]
        expected = case['expected_projection']
        checks = [
            {'id': CHECK_IDS[0], 'status': 'PASS' if projection == expected else 'FAIL',
             'observed_projection_digest': digest(projection)},
            {'id': CHECK_IDS[1], 'status': 'PASS' if len(records) == len(expected)
             and [row.get(fields['id']) for row in records] == [row[fields['id']] for row in expected] else 'FAIL'},
            {'id': CHECK_IDS[2], 'status': 'PASS' if len(decoded_lines) == len(expected)
             and all(isinstance(row, dict) and all(row.get(k) == exp[k] for k in (fields['user'], fields['value']))
                     for row, exp in zip(decoded_lines, expected)) else 'FAIL'},
        ]
        passed = all(c['status'] == 'PASS' for c in checks)
        return {'ok': True, 'schema_version': RESPONSE_SCHEMA, 'scorer_version': SCORER_VERSION,
                'task_id': request['task_id'], 'seed': request['seed'],
                'artifact_sha256': request['artifact_sha256'], 'manifest_sha256': request['manifest_sha256'],
                'holdout_digest': request['holdout_digest'], 'manifest_case_seed': request['manifest_case_seed'],
                'worker_input_sha256': request['worker_input_sha256'],
                'status': 'PASS' if passed else 'FAIL', 'label': int(passed),
                'quality_score': sum(c['status'] == 'PASS' for c in checks) / len(checks),
                'coverage_complete': True, 'checks': checks, 'required_check_ids': list(CHECK_IDS)}
    except Exception as exc:
        failure = _candidate_failure(exc, root)
        if failure:
            return {'ok': True, 'schema_version': RESPONSE_SCHEMA, 'scorer_version': SCORER_VERSION,
                    'task_id': request['task_id'], 'seed': request['seed'],
                    'artifact_sha256': request['artifact_sha256'], 'manifest_sha256': request['manifest_sha256'],
                    'holdout_digest': request['holdout_digest'], 'manifest_case_seed': request['manifest_case_seed'],
                    'worker_input_sha256': request['worker_input_sha256'],
                    'status': 'FAIL', 'label': 0, 'quality_score': 0.0, 'coverage_complete': True,
                    'checks': [{'id': cid, 'status': 'FAIL', **failure} for cid in CHECK_IDS],
                    'required_check_ids': list(CHECK_IDS)}
        return {'ok': False, 'error_type': type(exc).__name__, 'message': str(exc)}


def main():
    root = sys.argv[1]
    for line in sys.stdin:
        try:
            request = json.loads(line)
            required = {'op', 'schema_version', 'task_id', 'seed', 'artifact_sha256',
                        'manifest_sha256', 'holdout_digest', 'manifest_case_seed',
                        'worker_input_sha256', 'scorer_version', 'case'}
            if not isinstance(request, dict) or set(request) != required or request['op'] != 'score_terminal':
                raise ValueError('invalid terminal request fields')
            if request['schema_version'] != REQUEST_SCHEMA or request['scorer_version'] != SCORER_VERSION:
                raise ValueError('terminal request version mismatch')
            unsigned = {key: value for key, value in request.items() if key != 'worker_input_sha256'}
            if digest(unsigned) != request['worker_input_sha256']:
                raise ValueError('worker input digest mismatch')
            if digest(request['case']) != request['holdout_digest'] or request['case']['seed'] != request['manifest_case_seed']:
                raise ValueError('terminal holdout case digest mismatch')
            response = score(root, request)
        except Exception as exc:
            response = {'ok': False, 'error_type': type(exc).__name__, 'message': str(exc)}
        print(json.dumps(response, separators=(',', ':'), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
