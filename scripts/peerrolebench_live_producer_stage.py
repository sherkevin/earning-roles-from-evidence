"""One bounded PIPE3 producer call with personal, public prior interactions.

The caller supplies a separately qualified public payload, persists both snapshots,
and serializes calls for each stream/arm/candidate. This module does not score work.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
from typing import Any, Mapping

from peerrolebench_actor_experience import ActorExperience, canonical_bytes, digest
from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_pipe3_material_adapter import digest_files
from peerrolebench_pipe3_public_contract_v2 import CLAUSES

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'references/aamas'
sys.path.insert(0, str(PROTOCOL))
from peer_role_protocol_20260925 import Delivery  # noqa: E402

# Hash at import so prepare_request does no file or network I/O.
MODULE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TRANSPORT_SHA256 = hashlib.sha256((ROOT / 'scripts/peerrolebench_real_closed_loop.py').read_bytes()).hexdigest()
PROVIDER_SHA256 = hashlib.sha256((ROOT / 'scripts/aamas_real_probe.py').read_bytes()).hexdigest()
EXPERIENCE_SHA256 = hashlib.sha256((ROOT / 'scripts/peerrolebench_actor_experience.py').read_bytes()).hexdigest()
CONTRACT_SHA256 = hashlib.sha256((ROOT / 'scripts/peerrolebench_pipe3_public_contract_v2.py').read_bytes()).hexdigest()
RESERVATION_ROOT = ROOT / 'experiments/live_producer_budget_reservations'
SCHEMA = 'peerrolebench-live-producer-stage-v1'
PROMPT_TEMPLATE = (
    'You are the producer for the public PIPE3 task. Repair only producer.py. '
    'Preserve public names and signatures. Use the supplied public source and task text. '
    'No tools are available. Return one JSON object with exactly '
    '{{"source_files":{{"producer.py":"complete file text"}}}}; no markdown.\n'
    'Prior completed public producer interactions (oldest first):\n{history}\n'
    'Current task payload:\n{payload}'
)
MEMORY_POLICY = {'max_entries': 2, 'visible_row_keys': ['task_index', 'task_input', 'actor_response'],
                 'current_input_only_in_record': True, 'future_rows_excluded': True}


def policy_digest() -> str:
    return digest({'schema': SCHEMA, 'template': PROMPT_TEMPLATE,
                   'module_sha256': MODULE_SHA256, 'memory_policy': MEMORY_POLICY,
                   'experience_sha256': EXPERIENCE_SHA256, 'contract_sha256': CONTRACT_SHA256})


def model_config_digest(card: Mapping[str, Any]) -> str:
    """Bind every call_api request/timeout field and the transport implementations."""
    fields = ('model', 'temperature', 'max_tokens', 'stream', 'thinking',
              'request_timeout_seconds', 'maximum_task_requests')
    if not isinstance(card, Mapping) or not all(k in card for k in fields):
        raise ValueError('model card missing transport configuration')
    if not isinstance(card['max_tokens'], Mapping) or set(card['max_tokens']) != {'producer'}:
        raise ValueError('only producer token cap is supported')
    if (not isinstance(card['model'], str) or not card['model']
            or type(card['max_tokens']['producer']) is not int or card['max_tokens']['producer'] < 1
            or type(card['maximum_task_requests']) is not int or card['maximum_task_requests'] < 1
            or type(card['request_timeout_seconds']) not in (int, float)
            or not math.isfinite(card['request_timeout_seconds']) or card['request_timeout_seconds'] <= 0
            or type(card['temperature']) not in (int, float)
            or not math.isfinite(card['temperature'])
            or type(card['stream']) is not bool
            or card['thinking'] != {'type': 'disabled'}):
        raise ValueError('invalid producer transport configuration')
    return digest({'card_fields': {k: card[k] for k in fields},
                   'transport_sha256': TRANSPORT_SHA256, 'provider_sha256': PROVIDER_SHA256})


def _payload(base: Mapping[str, Any]) -> dict[str, Any]:
    keys = {'task_id', 'seed', 'role', 'task_text', 'source_files', 'writable_paths',
            'required_delivery_paths', 'contract_clause_refs'}
    if not isinstance(base, Mapping) or set(base) != keys:
        raise ValueError('unqualified PIPE3 producer payload schema')
    if base['task_id'] != 'PIPE3_stream_processing' or base['role'] != 'producer':
        raise ValueError('wrong producer task')
    if type(base['seed']) is not int or base['seed'] < 0:
        raise ValueError('invalid seed')
    if (base['writable_paths'] != ['producer.py'] or base['required_delivery_paths'] != []
            or base['contract_clause_refs'] != list(CLAUSES)
            or not isinstance(base['task_text'], Mapping)
            or set(base['task_text']) != {'spec_md', 'brief_md'}
            or not all(isinstance(v, str) for v in base['task_text'].values())
            or not isinstance(base['source_files'], Mapping)
            or set(base['source_files']) != {'producer.py', 'models.py', 'sink.py'}
            or not all(isinstance(v, str) for v in base['source_files'].values())):
        raise ValueError('wrong producer public fields')
    clean = json.loads(canonical_bytes(base))
    if len(canonical_bytes(clean)) > 256 * 1024:
        raise ValueError('public producer payload exceeds byte cap')
    return clean


def _response_files(parsed: Mapping[str, Any], metadata: Mapping[str, Any]) -> dict[str, str]:
    if not isinstance(parsed, Mapping) or set(parsed) != {'source_files'} or not isinstance(parsed['source_files'], Mapping):
        raise ValueError('malformed producer response')
    files = parsed['source_files']
    if (set(files) != {'producer.py'} or not isinstance(files['producer.py'], str)
            or not files['producer.py'] or len(files['producer.py'].encode()) > 64 * 1024):
        raise ValueError('malformed or oversized producer source files')
    if not isinstance(metadata, Mapping) or not metadata.get('usage_complete'):
        raise ValueError('incomplete response metadata')
    if (metadata.get('http_status') != '200' or metadata.get('exit_code') != 0
            or metadata.get('stop_reason') != 'end_turn'
            or type(metadata.get('elapsed_seconds')) not in (int, float)
            or not math.isfinite(metadata['elapsed_seconds']) or metadata['elapsed_seconds'] < 0):
        raise ValueError('transport or completion evidence invalid')
    usage = metadata.get('usage') or {}
    if not all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens')):
        raise ValueError('incomplete token usage')
    return dict(files)


def _visible_history(store: ActorExperience, task_index: int) -> list[dict[str, Any]]:
    rows = store.read_before(task_index)
    for row in rows:
        _payload(row['task_input'])  # Reject older combined history prompts.
    return [{key: row[key] for key in MEMORY_POLICY['visible_row_keys']} for row in rows]


def prepare_request(*, base_payload: Mapping[str, Any], candidate: CandidateRegistryEntry,
                    experience: ActorExperience, task_index: int,
                    card: Mapping[str, Any]) -> dict[str, Any]:
    """Pure decision cut: no provider access and no state mutation."""
    base = _payload(base_payload)
    if not isinstance(candidate, CandidateRegistryEntry) or experience.actor_id != candidate.key:
        raise ValueError('candidate and actor namespace mismatch')
    if (card.get('stream_id'), card.get('arm_id')) != (experience.stream_id, experience.arm_id):
        raise ValueError('card and experience stream/arm mismatch')
    if (experience.max_entries, experience.max_state_bytes) != (2, 32768):
        raise ValueError('unsupported actor memory bounds')
    if candidate.source_digest != policy_digest() or candidate.model_id != card.get('model'):
        raise ValueError('candidate generation policy or model mismatch')
    if candidate.model_config_digest != model_config_digest(card):
        raise ValueError('candidate model configuration mismatch')
    before = experience.snapshot()
    history = _visible_history(experience, task_index)
    prompt = PROMPT_TEMPLATE.format(history=json.dumps(history, sort_keys=True, ensure_ascii=False),
                                    payload=json.dumps(base, sort_keys=True, ensure_ascii=False))
    prepared = {'schema': SCHEMA, 'candidate': candidate.payload(), 'task_index': task_index,
            'base_payload': base, 'before': before, 'history': history, 'prompt': prompt,
            'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
            'generation_policy_digest': policy_digest(),
            'model_config_digest': candidate.model_config_digest}
    prepared['decision_digest'] = digest(prepared)
    return prepared


def _check_live_gate(card: Mapping[str, Any], expected_card_digest: str,
                     prepared: Mapping[str, Any], output_dir: Path,
                     reservation_path: Path, expected_reservation_digest: str) -> None:
    if card.get('real_api_runs_allowed') is not True:
        raise PermissionError('real API runs are disabled')
    if not isinstance(expected_card_digest, str) or digest(card) != expected_card_digest:
        raise PermissionError('externally supplied card digest mismatch')
    budget = card.get('budget')
    if (not isinstance(budget, Mapping) or set(budget) !=
            {'prior_attempted_episodes', 'additional_cap', 'attempted_ledger'}
            or type(budget['prior_attempted_episodes']) is not int
            or budget['prior_attempted_episodes'] < 31
            or type(budget['additional_cap']) is not int
            or not 1 <= budget['additional_cap'] <= 8
            or not isinstance(budget['attempted_ledger'], list)
            or len(budget['attempted_ledger']) >= budget['additional_cap']
            or len(set(budget['attempted_ledger'])) != len(budget['attempted_ledger'])
            or not all(isinstance(x, str) and x for x in budget['attempted_ledger'])):
        raise ValueError('invalid or exhausted cumulative budget declaration')
    if model_config_digest(card) != prepared['model_config_digest']:
        raise ValueError('model configuration changed after preparation')
    if digest({k: v for k, v in prepared.items() if k != 'decision_digest'}) != prepared['decision_digest']:
        raise ValueError('decision digest changed')
    entry = CandidateRegistryEntry(**prepared['candidate'])
    if entry.source_digest != policy_digest() or entry.model_config_digest != model_config_digest(card):
        raise ValueError('candidate identity changed after preparation')
    restored = ActorExperience.restore(prepared['before'], stream_id=prepared['before']['stream_id'],
                                       arm_id=prepared['before']['arm_id'], actor_id=entry.key)
    if prepare_request(base_payload=prepared['base_payload'], candidate=entry,
                       experience=restored, task_index=prepared['task_index'], card=card) != prepared:
        raise ValueError('prepared request changed after decision cut')
    if not isinstance(output_dir, Path) or output_dir.exists():
        raise ValueError('output directory must be a fresh reserved path')
    if not isinstance(reservation_path, Path) or not reservation_path.is_file():
        raise PermissionError('external persisted budget reservation required')
    raw = reservation_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_reservation_digest:
        raise PermissionError('external reservation digest mismatch')
    reservation = json.loads(raw)
    if (not isinstance(reservation, dict) or not isinstance(reservation.get('reservation_id'), str)
            or not re.fullmatch(r'[A-Za-z0-9_-]+', reservation['reservation_id'])
            or reservation_path != RESERVATION_ROOT / (reservation['reservation_id'] + '.json')
            or reservation_path != reservation_path.resolve()):
        raise PermissionError('reservation must occupy its canonical absolute path')
    if (not isinstance(reservation, dict) or set(reservation) !=
            {'status', 'reservation_id', 'card_digest', 'prompt_sha256',
             'candidate_key', 'task_index', 'ordinal'}
            or reservation['status'] != 'reserved'
            or not isinstance(reservation['reservation_id'], str) or not reservation['reservation_id']
            or reservation['card_digest'] != expected_card_digest
            or reservation['prompt_sha256'] != prepared['prompt_sha256']
            or reservation['candidate_key'] != entry.key
            or reservation['task_index'] != prepared['task_index']
            or reservation['ordinal'] != len(budget['attempted_ledger']) + 1):
        raise PermissionError('reservation does not bind this request and budget cut')
    if reservation_path.with_suffix('.claimed').exists():
        raise PermissionError('reservation already claimed')


def run_generation(*, prepared: Mapping[str, Any], card: Mapping[str, Any],
                   expected_card_digest: str, output_dir: Path,
                   reservation_path: Path, expected_reservation_digest: str) -> dict[str, Any]:
    """One real request, no retries. A failure remains UNKNOWN with transport files."""
    _check_live_gate(card, expected_card_digest, prepared, output_dir,
                     reservation_path, expected_reservation_digest)
    claim = reservation_path.with_suffix('.claimed')
    fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(json.dumps({'reservation_digest': expected_reservation_digest,
                                 'output_dir': str(output_dir)}) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    output_dir.mkdir(parents=True, exist_ok=False)
    stage_dir = output_dir / 'episode'
    stage_dir.mkdir()
    (output_dir / 'config.json').write_bytes(canonical_bytes({'card': card, 'card_digest': expected_card_digest,
        'prepared': prepared, 'reservation_digest': expected_reservation_digest,
        'reservation_path': str(reservation_path), 'status': 'UNKNOWN'}))
    from peerrolebench_real_closed_loop import call_api, log  # provider loads inside call_api
    log(output_dir, 'generation_stage_config', {'card_digest': expected_card_digest,
        'prompt_sha256': prepared['prompt_sha256'], 'before_digest': prepared['before']['state_digest'],
        'cumulative_prior_attempted': card['budget']['prior_attempted_episodes'],
        'additional_attempted': len(card['budget']['attempted_ledger'])})
    try:
        parsed, metadata = call_api(output_dir, stage_dir, 'producer', prepared['prompt'], dict(card))
    except Exception as exc:
        log(output_dir, 'generation_stage_unknown', {'error_type': type(exc).__name__, 'error': str(exc)})
        return {'status': 'UNKNOWN', 'output_dir': str(output_dir), 'error': str(exc)}
    try:
        _response_files(parsed, metadata)
        if metadata.get('returned_model') != prepared['candidate']['model_id']:
            raise ValueError('returned model differs from registered model')
    except ValueError as exc:
        log(output_dir, 'generation_stage_unknown', {'error_type': type(exc).__name__, 'error': str(exc)})
        return {'status': 'UNKNOWN', 'output_dir': str(output_dir), 'error': str(exc)}
    result = {'status': 'PARSED', 'parsed': parsed, 'metadata': metadata,
              'output_dir': str(output_dir)}
    (output_dir / 'parsed_result.json').write_bytes(canonical_bytes(result))
    sealed_paths = ['config.json', 'episode/producer_request.json',
                    'episode/producer_response.sse' if card['stream'] else 'episode/producer_response.json',
                    'episode/producer_cost.json', 'parsed_result.json']
    if card['stream']:
        sealed_paths.append('episode/producer_parsed_response.json')
    receipt = {'schema': SCHEMA, 'status': 'PARSED', 'decision_digest': prepared['decision_digest'],
               'card_digest': expected_card_digest, 'reservation_digest': expected_reservation_digest,
               'files': {name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest()
                         for name in sealed_paths}}
    receipt_path = output_dir / 'completion_receipt.json'
    receipt_path.write_bytes(canonical_bytes(receipt))
    result['completion_receipt_sha256'] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    return result


def _finalize_software_fixture(*, prepared: Mapping[str, Any], parsed: Mapping[str, Any],
                               metadata: Mapping[str, Any], recipient_id: str,
                               interaction_id: str, delivery_id: str, source_event_id: str,
                               expected_request_digest: str, selection_id: str | None = None) -> dict[str, Any]:
    """Pure offline contract helper; arbitrary inputs here are never live evidence."""
    entry = CandidateRegistryEntry(**prepared['candidate'])
    if (expected_request_digest != prepared['decision_digest']
            or digest({k: v for k, v in prepared.items() if k != 'decision_digest'}) != expected_request_digest
            or entry.source_digest != policy_digest()):
        raise ValueError('request seal or producer policy mismatch')
    store = ActorExperience.restore(prepared['before'], stream_id=prepared['before']['stream_id'],
                                    arm_id=prepared['before']['arm_id'], actor_id=entry.key)
    base = _payload(prepared['base_payload'])
    if (prepared['generation_policy_digest'] != policy_digest()
            or prepared['model_config_digest'] != entry.model_config_digest
            or prepared['prompt_sha256'] != hashlib.sha256(prepared['prompt'].encode()).hexdigest()
            or prepared['history'] != _visible_history(store, prepared['task_index'])):
        raise ValueError('prepared decision cut changed')
    # No card is needed to re-create the prompt; the candidate digests were sealed at prepare time.
    prompt = PROMPT_TEMPLATE.format(history=json.dumps(prepared['history'], sort_keys=True, ensure_ascii=False),
                                    payload=json.dumps(base, sort_keys=True, ensure_ascii=False))
    if prepared['prompt'] != prompt:
        raise ValueError('prompt differs from frozen inputs')
    files = _response_files(parsed, metadata)
    if metadata.get('returned_model') != entry.model_id:
        raise ValueError('returned model differs from registered model')
    usage = metadata['usage']
    model_metadata = {'model_id': entry.model_id, 'stage': 'producer',
                      'usage': {k: usage[k] for k in ('input_tokens', 'output_tokens')}}
    for source, target in (('returned_model', 'returned_model'), ('stop_reason', 'stop_reason'),
                           ('elapsed_seconds', 'elapsed_seconds')):
        if metadata.get(source) is not None:
            model_metadata[target] = metadata[source]
    store.record_completed_interaction(interaction_id=interaction_id, task_index=prepared['task_index'],
                                       task_input=base, actor_response={'source_files': dict(files)},
                                       model_metadata=model_metadata)
    delivery = Delivery(delivery_id, base['task_id'], entry.candidate_id, recipient_id,
                        digest_files(files), source_event_id, prepared['task_index'],
                        selection_id, entry.source_digest)
    return {'status': 'COMPLETED', 'candidate': entry.payload(), 'delivery': asdict(delivery),
            'source_files': dict(files), 'before': prepared['before'], 'after': store.snapshot()}


def finalize(*, prepared: Mapping[str, Any], output_dir: Path, expected_receipt_digest: str,
             recipient_id: str, interaction_id: str, delivery_id: str,
             source_event_id: str, selection_id: str | None = None) -> dict[str, Any]:
    """Complete only the sealed on-disk result of run_generation."""
    receipt_path = output_dir / 'completion_receipt.json'
    raw_receipt = receipt_path.read_bytes()
    if hashlib.sha256(raw_receipt).hexdigest() != expected_receipt_digest:
        raise ValueError('completion receipt seal mismatch')
    receipt = json.loads(raw_receipt)
    if (receipt.get('schema') != SCHEMA or receipt.get('status') != 'PARSED'
            or receipt.get('decision_digest') != prepared['decision_digest']):
        raise ValueError('completion receipt request mismatch')
    files = receipt.get('files')
    if not isinstance(files, dict) or set(files) not in ({'config.json', 'episode/producer_request.json',
            'episode/producer_response.sse', 'episode/producer_parsed_response.json',
            'episode/producer_cost.json', 'parsed_result.json'},
            {'config.json', 'episode/producer_request.json', 'episode/producer_response.json',
             'episode/producer_cost.json', 'parsed_result.json'}):
        raise ValueError('completion receipt inventory invalid')
    for name, expected in files.items():
        if hashlib.sha256((output_dir / name).read_bytes()).hexdigest() != expected:
            raise ValueError('sealed transport file changed: ' + name)
    config = json.loads((output_dir / 'config.json').read_bytes())
    request = json.loads((output_dir / 'episode/producer_request.json').read_bytes())
    result = json.loads((output_dir / 'parsed_result.json').read_bytes())
    cost = json.loads((output_dir / 'episode/producer_cost.json').read_bytes())
    card = config.get('card')
    if (not isinstance(card, dict) or card.get('real_api_runs_allowed') is not True
            or digest(card) != receipt['card_digest']
            or model_config_digest(card) != prepared['model_config_digest']):
        raise ValueError('sealed model card mismatch')
    reservation_path = Path(config.get('reservation_path', ''))
    if (not reservation_path.is_absolute() or not reservation_path.is_file()
            or hashlib.sha256(reservation_path.read_bytes()).hexdigest() != receipt['reservation_digest']):
        raise ValueError('sealed reservation mismatch')
    reservation = json.loads(reservation_path.read_bytes())
    if (not re.fullmatch(r'[A-Za-z0-9_-]+', reservation.get('reservation_id', ''))
            or reservation_path != RESERVATION_ROOT / (reservation['reservation_id'] + '.json')
            or reservation_path != reservation_path.resolve()):
        raise ValueError('sealed reservation path mismatch')
    claim_path = reservation_path.with_suffix('.claimed')
    if (not claim_path.is_file() or json.loads(claim_path.read_bytes()) !=
            {'reservation_digest': receipt['reservation_digest'], 'output_dir': str(output_dir)}):
        raise ValueError('sealed reservation claim mismatch')
    expected_request = {'model': card['model'], 'messages': [{'role': 'user', 'content': prepared['prompt']}],
                        'temperature': card['temperature'], 'max_tokens': card['max_tokens']['producer'],
                        'stream': card['stream'], 'thinking': card['thinking']}
    if request != expected_request:
        raise ValueError('sealed provider request mismatch')
    from peerrolebench_real_closed_loop import parse_object, parse_sse
    raw_path = output_dir / ('episode/producer_response.sse' if card['stream'] else 'episode/producer_response.json')
    raw = raw_path.read_text()
    wire = parse_sse(raw) if card['stream'] else json.loads(raw)
    if card['stream'] and json.loads((output_dir / 'episode/producer_parsed_response.json').read_bytes()) != wire:
        raise ValueError('stream parser output differs from raw response')
    text = '\n'.join(block.get('text', '') for block in wire.get('content', []) if block.get('type') == 'text')
    wire_usage_complete = all(type((wire.get('usage') or {}).get(key)) is int
                              for key in ('input_tokens', 'output_tokens'))
    if card['stream']:
        wire_usage_complete = wire_usage_complete and wire.get('final_usage_observed') is True
    if (parse_object(text) != result.get('parsed') or wire.get('model') != cost.get('returned_model')
            or wire.get('usage') != cost.get('usage')
            or wire.get('stop_reason') != cost.get('stop_reason')
            or wire.get('thinking_delta_count') != cost.get('thinking_delta_count')
            or wire.get('thinking_delta_count', 0) != 0
            or wire_usage_complete != cost.get('usage_complete')):
        raise ValueError('parsed result or cost differs from raw response')
    if (config.get('prepared') != prepared or config.get('card_digest') != receipt['card_digest']
            or config.get('reservation_digest') != receipt['reservation_digest']
            or result.get('status') != 'PARSED' or result.get('metadata') != cost
            or result.get('output_dir') != str(output_dir)):
        raise ValueError('sealed request or response mismatch')
    completed = _finalize_software_fixture(prepared=prepared, parsed=result['parsed'], metadata=cost,
        recipient_id=recipient_id, interaction_id=interaction_id, delivery_id=delivery_id,
        source_event_id=source_event_id, expected_request_digest=prepared['decision_digest'],
        selection_id=selection_id)
    completed['completion_receipt_sha256'] = expected_receipt_digest
    path = output_dir / 'completion.json'
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(canonical_bytes(completed))
        stream.flush()
        os.fsync(stream.fileno())
    return completed
