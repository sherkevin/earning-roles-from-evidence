import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid

sys.path.insert(0, '/Users/jingwu/work/earning-roles/scripts')
import aamas_peer_judgment_smoke_v2 as smoke
import aamas_real_probe as prior

fixture_root = Path('/tmp/pj2_guard_fixture_' + uuid.uuid4().hex[:12])
fixture_root.mkdir(parents=True, exist_ok=False)
results = {'fixture_root': str(fixture_root), 'python': sys.version,
           'host': platform.node(), 'task_id': '22cc237_2',
           'appworld_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=prior.APP,text=True).strip(),
           'runner_sha256': hashlib.sha256(Path(smoke.__file__).read_bytes()).hexdigest(),
           'cases': []}
(fixture_root / 'config.json').write_text(json.dumps(results, indent=2) + '\n')
AppWorld, _ = prior.initialize_runtime()
code = "print(apis.api_docs.show_app_descriptions())"
smoke.safe_code(code)

for case in ('baseline', 'buffered'):
    name = 'pj2_guard_' + case + '_' + uuid.uuid4().hex[:12]
    case_root = fixture_root / case
    case_root.mkdir()
    raw = case_root / 'raw.jsonl'
    secrets = smoke.Secrets()
    original_log = prior.log
    smoke.install_redacted_logging(secrets)
    safe_log = prior.log
    pending = []
    active = False
    def maybe_defer(path, event, **payload):
        if active:
            pending.append((Path(path), event, secrets.scrub(payload)))
        else:
            safe_log(path, event, **payload)
    if case == 'buffered':
        prior.log = maybe_defer
    row = {'case': case, 'experiment_name': name, 'code': code,
           'raise_on_unsafe_execution': None, 'observation': None,
           'audit_n': None, 'deferred_n': None, 'error': None}
    started = time.monotonic()
    try:
        with AppWorld(task_id='22cc237_2', experiment_name=name,
                      load_ground_truth=False, random_seed=100,
                      raise_on_extra_parameters=True) as world:
            row['raise_on_unsafe_execution'] = world.raise_on_unsafe_execution
            smoke.install_native_log_scrubber(world, prior.APP / 'experiments/outputs' / name, secrets)
            audit = smoke.api_guard(world, 'producer', secrets, raw)
            if case == 'buffered':
                active = True
            try:
                row['observation'] = world.execute(code)
            finally:
                active = False
                for path, event, payload in pending:
                    safe_log(path, event, **payload)
            row['audit_n'] = len(audit)
            row['audit_rows'] = [{k: v for k, v in item.items() if k not in ('arguments',)} for item in audit]
            row['deferred_n'] = len(pending)
            row['public_api_log_n'] = sum(1 for line in raw.read_text().splitlines()
                                           if json.loads(line)['event'] == 'public_api_call') if raw.exists() else 0
    except Exception as exc:
        row['error'] = repr(exc)
    finally:
        prior.log = original_log
    row['elapsed_seconds'] = round(time.monotonic() - started, 3)
    results['cases'].append(row)
    (fixture_root / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({k: v for k, v in row.items() if k not in ('observation', 'audit_rows')}, ensure_ascii=False))
    print('observation_prefix:', repr((row['observation'] or '')[:240]))
print('fixture_root:', fixture_root)
