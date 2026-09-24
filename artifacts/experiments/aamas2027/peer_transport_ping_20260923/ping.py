#!/usr/bin/env python3
"""One real, one-attempt idealab transport diagnostic; no benchmark task."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import traceback

sys.path.insert(0, '/Users/jingwu/work/earning-roles/scripts')
import aamas_real_probe as prior

OUT = Path(__file__).resolve().parent
CONFIG = json.loads((OUT / 'config.json').read_text())
RAW = OUT / 'raw.jsonl'
RESULT = OUT / 'results.json'
assert CONFIG['max_attempts'] == 1
assert CONFIG['max_output_tokens'] == 16
assert CONFIG['prompt'] == 'Reply exactly OK'
assert CONFIG['model'] == 'qwen3.8-max'
assert CONFIG['request_timeout_seconds'] == 120
messages = [{'role': 'user', 'content': CONFIG['prompt']}]
started_at = datetime.now(timezone.utc).isoformat()
started = time.monotonic()
api = None
result = {'status': 'UNKNOWN', 'started_at_utc': started_at, 'ended_at_utc': None,
          'wall_seconds': None, 'attempts': 0, 'response_text': None,
          'returned_models': [], 'usage': None, 'unknown_usage_attempts': 0,
          'api_errors': 0, 'error_codes': [], 'error': None,
          'limitation': 'One minimal prompt tests the provider transport at this time; it does not diagnose long native prompt processing or benchmark validity.'}
try:
    api = prior.RealAPI(RAW, max_attempts=1)
    if api.provider['base'] != CONFIG['endpoint_expected']:
        raise RuntimeError('Named provider endpoint changed')
    prior.log(RAW, 'diagnostic_start', config_sha256=CONFIG['config_sha256'],
              provider={k: v for k, v in api.provider.items() if k != 'secret'},
              max_attempts=1, request_timeout_seconds=120, no_benchmark_task=True)
    response = api.generate(messages, max_tokens=16)
    result['response_text'] = response
    result['status'] = 'SUCCESS' if response.strip() == 'OK' else 'RESPONSE_MISMATCH'
except Exception as error:
    secret = api.provider['secret'] if api is not None else ''
    message = str(error).replace(secret, '[REDACTED]') if secret else str(error)
    result['error'] = {'type': type(error).__name__, 'message': message,
                       'traceback': traceback.format_exc().replace(secret, '[REDACTED]') if secret else traceback.format_exc()}
    result['status'] = 'TRANSPORT_ERROR' if api is not None and api.attempts else 'SETUP_ERROR'
finally:
    result['ended_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['wall_seconds'] = time.monotonic() - started
    if api is not None:
        result['attempts'] = api.attempts
        result['returned_models'] = api.returned_models
        result['usage'] = api.usage
        result['unknown_usage_attempts'] = api.unknown_usage_attempts
        result['api_errors'] = api.errors
        result['error_codes'] = api.error_codes
        result['api_seconds'] = api.seconds
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if api is not None:
        prior.log(RAW, 'diagnostic_result', status=result['status'], attempts=result['attempts'],
                  wall_seconds=result['wall_seconds'], usage=result['usage'],
                  error_type=result['error']['type'] if result['error'] else None)
print(json.dumps({k: result[k] for k in ('status', 'attempts', 'wall_seconds', 'response_text', 'error_codes')}, ensure_ascii=False))
