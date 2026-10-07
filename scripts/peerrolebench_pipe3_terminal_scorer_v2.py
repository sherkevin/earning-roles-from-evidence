"""Manifest-bound parent adapter for the development-only PIPE3 terminal scorer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping

from peerrolebench_sandbox import SandboxedWorker
from peerrolebench_pipe3_material_adapter import digest_files

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / 'scripts/peerrolebench_pipe3_terminal_scorer_worker_v2.py'
MANIFEST = ROOT / 'configs/aamas2027/pipe3_terminal_holdout_v2.json'
MANIFEST_SHA256 = '0cc909b56d25eff8b7badd47ac94fef3afb68ce1eb7b7238abd3e0cb89930424'
REQUEST_SCHEMA = 'pipe3-terminal-holdout-request-v2'
SCHEMA_VERSION = 'pipe3-terminal-holdout-response-v2'
SCORER_VERSION = 'pipe3-terminal-holdout-v2'
CHECK_IDS = ('T1_holdout_projection', 'T2_batch_cardinality', 'T3_unicode_semantics')
SCORE_FILES = ('producer.py', 'processor.py', 'sink.py', 'models.py')


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def load_manifest(path: Path = MANIFEST, expected_sha256: str = MANIFEST_SHA256) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    if expected_sha256 != MANIFEST_SHA256 or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('terminal holdout manifest hash mismatch')
    manifest = json.loads(raw)
    if manifest.get('schema_version') != 'pipe3-terminal-holdout-manifest-v2' or manifest.get('task_id') != 'PIPE3_stream_processing':
        raise ValueError('terminal holdout manifest schema mismatch')
    if [case.get('seed') for case in manifest.get('cases', [])] != [0, 1]:
        raise ValueError('terminal holdout manifest case inventory mismatch')
    return manifest


def _unknown(reason: str, error_type: str | None = None) -> dict[str, Any]:
    row = {'status': 'UNKNOWN', 'label': None, 'quality_score': None,
           'scorer_version': SCORER_VERSION, 'coverage_complete': False, 'reason': reason}
    if error_type:
        row['error_type'] = error_type
    return row


def classify(response: Any, *, artifact_sha256: str, manifest_sha256: str,
             worker_input_sha256: str, holdout_digest: str, manifest_case_seed: int,
             task_id: str, seed: int) -> dict[str, Any]:
    if not isinstance(response, dict) or response.get('ok') is not True:
        return _unknown('terminal_worker_error', response.get('error_type') if isinstance(response, dict) else None)
    required = {'ok', 'schema_version', 'scorer_version', 'task_id', 'seed', 'artifact_sha256',
                'manifest_sha256', 'holdout_digest', 'manifest_case_seed',
                'worker_input_sha256', 'status', 'label', 'quality_score',
                'coverage_complete', 'checks', 'required_check_ids'}
    if set(response) != required:
        return _unknown('terminal_response_shape_invalid')
    expected = {'schema_version': SCHEMA_VERSION, 'scorer_version': SCORER_VERSION,
                'task_id': task_id, 'seed': seed, 'artifact_sha256': artifact_sha256,
                'manifest_sha256': manifest_sha256, 'holdout_digest': holdout_digest,
                'manifest_case_seed': manifest_case_seed, 'worker_input_sha256': worker_input_sha256,
                'required_check_ids': list(CHECK_IDS), 'coverage_complete': True}
    if any(response[key] != value for key, value in expected.items()):
        return _unknown('terminal_response_binding_mismatch')
    checks = response['checks']
    if (not isinstance(checks, list) or len(checks) != len(CHECK_IDS)
            or any(not isinstance(item, dict) or item.get('id') != cid
                   or item.get('status') not in ('PASS', 'FAIL')
                   for item, cid in zip(checks, CHECK_IDS))):
        return _unknown('terminal_check_shape_invalid')
    for item in checks:
        allowed = {'id', 'status', 'observed_projection_digest', 'failure_origin',
                   'source_path', 'exception_class', 'reason'}
        if set(item) - allowed:
            return _unknown('terminal_check_shape_invalid')
    passed = all(item['status'] == 'PASS' for item in checks)
    status = 'PASS' if passed else 'FAIL'
    quality = sum(item['status'] == 'PASS' for item in checks) / len(checks)
    if (response['status'] != status or type(response['label']) is not int
            or response['label'] != int(passed) or type(response['quality_score']) not in (int, float)
            or abs(response['quality_score'] - quality) > 1e-12):
        return _unknown('terminal_result_inconsistent')
    return {'status': status, 'label': int(passed), 'quality_score': quality,
            'scorer_version': SCORER_VERSION, 'coverage_complete': True, 'checks': checks}


def run_terminal_scorer(sources: Mapping[str, str], task_id: str, seed: int,
                        evidence_dir: Path, log, *, manifest_path: Path = MANIFEST,
                        expected_manifest_sha256: str = MANIFEST_SHA256,
                        manifest_case_seed: int | None = None) -> dict[str, Any]:
    """Score four public source files; unknown transport/contract states never yield a label."""
    started = time.monotonic()
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=False, exist_ok=False)
    response = None
    request = None
    artifact_digest = None
    transport = {'status': 'not_started'}
    try:
        manifest = load_manifest(manifest_path, expected_manifest_sha256)
        if task_id != manifest['task_id'] or type(seed) is not int or seed not in (0, 1):
            raise ValueError('terminal task identity mismatch')
        case_seed = seed if manifest_case_seed is None else manifest_case_seed
        if type(case_seed) is not int or case_seed not in (0, 1):
            raise ValueError('terminal manifest case identity mismatch')
        if set(sources) != set(SCORE_FILES) or any(not isinstance(value, str) for value in sources.values()):
            raise ValueError('terminal score files invalid')
        score_files = {name: sources[name] for name in SCORE_FILES}
        artifact_digest = digest_files(score_files)
        case = manifest['cases'][case_seed]
        holdout_digest = canonical_digest(case)
        config = {'scorer_version': SCORER_VERSION, 'task_id': task_id, 'seed': seed,
                  'manifest_path': str(Path(manifest_path).resolve()), 'manifest_sha256': MANIFEST_SHA256,
                  'manifest_case_seed': case_seed, 'holdout_digest': holdout_digest,
                  'worker_sha256': hashlib.sha256(WORKER.read_bytes()).hexdigest(),
                  'artifact_sha256': artifact_digest, 'score_files': {name: hashlib.sha256(value.encode()).hexdigest()
                                                                     for name, value in score_files.items()},
                  'candidate_received_hidden_assertions': False, 'scientific_claim_allowed': False,
                  'same_process_instrumentation_tamper_proof': False}
        (evidence_dir / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
        log('terminal_scorer_config', config)
        request = {'op': 'score_terminal', 'schema_version': REQUEST_SCHEMA,
                   'scorer_version': SCORER_VERSION, 'task_id': task_id, 'seed': seed,
                   'artifact_sha256': artifact_digest, 'manifest_sha256': MANIFEST_SHA256,
                   'holdout_digest': holdout_digest, 'manifest_case_seed': case_seed, 'case': case}
        request['worker_input_sha256'] = canonical_digest(request)
        with SandboxedWorker(score_files, evidence_dir / 'sandbox', log, 'unused', 'unused',
                             worker_path=WORKER, rpc_seconds=20, source_prefixes=SCORE_FILES) as worker:
            response = worker.request(request)
        transport = {'status': 'complete'}
        result = classify(response, artifact_sha256=artifact_digest, manifest_sha256=MANIFEST_SHA256,
                          worker_input_sha256=request['worker_input_sha256'],
                          holdout_digest=holdout_digest, manifest_case_seed=case_seed,
                          task_id=task_id, seed=seed)
    except Exception as exc:
        transport = {'status': 'error', 'error_type': type(exc).__name__, 'message': str(exc)}
        result = _unknown('terminal_transport_or_contract_error', type(exc).__name__)
    response_digest = canonical_digest(response) if response is not None else None
    payload = {'transport': transport, 'request': request, 'response': response,
               'response_digest': response_digest, 'result': result,
               'scorer_wall_seconds': time.monotonic() - started}
    (evidence_dir / 'response.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    log('terminal_scorer_response', payload)
    return {**result, 'transport': transport, 'artifact_sha256': artifact_digest,
            'manifest_sha256': MANIFEST_SHA256, 'worker_input_sha256': request.get('worker_input_sha256') if request else None,
            'holdout_digest': request.get('holdout_digest') if request else None,
            'response_digest': response_digest, 'scorer_wall_seconds': payload['scorer_wall_seconds']}


__all__ = ['CHECK_IDS', 'SCORER_VERSION', 'MANIFEST_SHA256', 'load_manifest', 'classify', 'run_terminal_scorer']
