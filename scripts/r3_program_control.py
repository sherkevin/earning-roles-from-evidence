"""R3 same-source executable program control; native replay, no task LLM."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from r2_native_replay import load_prior
from r1_role_contract_core import first_consumer_boundary, replace_handoff, library_adapter
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/experiments/aamas2027/program_control_20260923'
MANIFEST = OUT / 'native_manifest.json'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def program_code(endpoint, field):
    return f'''import json

def _r3_pages(fn):
    rows = []
    for page in range(100):
        batch = fn(access_token=access_token, page_index=page, page_limit=20)
        rows.extend(batch)
        if len(batch) < 20:
            return rows
    raise RuntimeError("R3 pagination limit; UNKNOWN")

_r3_source_rows = _r3_pages(apis.spotify.{endpoint})
_r3_liked_rows = _r3_pages(apis.spotify.show_liked_songs)
_r3_source = {{sid for row in _r3_source_rows for sid in (row[{field!r}] if {field!r} == 'song_ids' else [row[{field!r}]])}}
_r3_liked = {{row['song_id'] for row in _r3_liked_rows}}
_r3_targets = _r3_source & _r3_liked
_r3_done = {{row['song_id'] for row in _r3_pages(apis.spotify.show_downloaded_songs)}}
role_handoff_ids = sorted(_r3_targets - _r3_done)
print(json.dumps({{"target": sorted(_r3_targets), "done": sorted(_r3_done), "selected": role_handoff_ids}}))
'''

def execute(task_id):
    m = json.loads(MANIFEST.read_text())
    assert m['program'] == 'intersection' and m['guard'] == 'exclude_already_done'
    for rel, sha in m['code_sha256'].items():
        if digest(ROOT/rel) != sha:
            raise RuntimeError('Frozen code changed: '+rel)
    task = next(t for t in m['tasks'] if t['task_id'] == task_id)
    trace_path = ROOT / task['trace_path']
    if digest(trace_path) != task['trace_sha256']:
        raise RuntimeError('Frozen source trace changed')
    trace = json.loads(trace_path.read_text())
    boundary, variable = first_consumer_boundary(trace['steps'])
    assert boundary == task['boundary_index'] and variable == task['boundary_variable']
    job = OUT / 'runs' / task_id
    job.mkdir(parents=True, exist_ok=False)
    prior = load_prior()
    AppWorld, _ = prior.initialize_runtime()
    experiment = 'r3_' + hashlib.sha256((task_id+'program_guard').encode()).hexdigest()[:20]
    native = prior.APP / 'experiments/outputs' / experiment
    if native.exists():
        raise RuntimeError('Refusing to overwrite native output')
    row = {'task_id': task_id, 'arm': 'source_program_guard', 'status': 'INVALID',
           'new_task_policy_llm_calls': 0, 'manifest_sha256': digest(MANIFEST),
           'runtime_error': None, 'evaluator_error': None, 'experiment': experiment}
    started = prior.mono()
    try:
        with AppWorld(task_id=task_id, experiment_name=experiment, load_ground_truth=False,
                      random_seed=100, raise_on_extra_parameters=True) as world:
            assert world.task.ground_truth is None
            for index, step in enumerate(trace['steps']):
                code = step['code']
                if index == boundary:
                    endpoint, field = library_adapter(trace['instruction'])
                    insertion = program_code(endpoint, field)
                    obs = world.execute(insertion)
                    prior.log(job/'raw.jsonl', 'program_intervention', code=insertion, observation=obs)
                    row['handoff'] = json.loads(obs)
                    code = replace_handoff(code, variable)
                obs = world.execute(code)
                prior.log(job/'raw.jsonl', 'replayed_step', step=step['step'], code=code, observation=obs)
            row['task_completed'] = world.task_completed()
            world.save()
        row['status'] = 'EXECUTED'
    except Exception as error:
        row['runtime_error'] = {'type': type(error).__name__, 'message': str(error)}
        try:
            AppWorld.close_all()
        except Exception:
            pass
    if row['status'] == 'EXECUTED':
        try:
            from appworld.evaluator import evaluate_task
            ev = evaluate_task(task_id=task_id, experiment_name=experiment,
                 suppress_errors=True, save_report=True).to_dict(stats_only=False)
            save(job/'evaluator_only.json', ev)
            row.update(status='SCORED', official_success=bool(ev['success']),
                       passed_assertions=len(ev['passes']), failed_assertions=len(ev['failures']))
        except Exception as error:
            row['evaluator_error'] = {'type': type(error).__name__, 'message': str(error)}
            row['status'] = 'INVALID'
    task_root = native / 'tasks' / task_id
    call_log = task_root/'logs/api_calls.jsonl'
    row['native_api_calls'] = len(call_log.read_text().splitlines()) if call_log.exists() else None
    row['wall_seconds'] = prior.mono() - started
    row['native_output'] = str(native)
    if task_root.exists():
        shutil.copytree(task_root, job/'native')
    save(job/'result.json', row)
    print(json.dumps(row, ensure_ascii=False), flush=True)

def batch():
    m = json.loads(MANIFEST.read_text())
    baseline_path = ROOT / m['r2_summary_path']
    if digest(baseline_path) != m['r2_summary_sha256']:
        raise RuntimeError('R2 reference changed')
    old = {r['task_id']: r for r in json.loads(baseline_path.read_text())['results']
           if r['arm'] == 'semantic_guard'}
    rows = []
    for task in m['tasks']:
        tid = task['task_id']
        if (OUT/'runs'/tid).exists():
            raise RuntimeError('Existing run; no implicit rerun')
        with (OUT/(tid+'.log')).open('w') as log:
            child = subprocess.run([sys.executable, __file__, 'execute', '--task', tid],
                                   stdout=log, stderr=subprocess.STDOUT, timeout=90)
        path = OUT/'runs'/tid/'result.json'
        if child.returncode or not path.exists():
            save(OUT/'STOP.json', {'task': tid, 'reason': 'child_failure', 'code': child.returncode})
            return
        row = json.loads(path.read_text())
        if row['status'] != 'SCORED':
            save(OUT/'STOP.json', {'task': tid, 'reason': 'invalid_result', 'result': row})
            return
        ref = old[tid]
        base_native = ROOT/m['r2_directory']/'native'/(tid+'_semantic_guard')
        ours_native = OUT/'runs'/tid/'native'
        base_files = sorted((base_native/'dbs').glob('*.jsonl'))
        state_equal = bool(base_files) and all((ours_native/'dbs'/p.name).exists() and
                         p.read_bytes() == (ours_native/'dbs'/p.name).read_bytes() for p in base_files)
        row['comparison_to_r2'] = {'same_selection': row['handoff']['selected']==ref['handoff']['selected'],
          'same_official_success': row['official_success']==ref['official_success'],
          'same_passed_assertions': row['passed_assertions']==ref['passed_assertions'],
          'same_database_bytes': state_equal, 'database_files_compared': len(base_files),
          'native_api_delta': row['native_api_calls']-ref['native_api_calls']}
        rows.append(row)
        print(tid, row['official_success'], row['comparison_to_r2'], flush=True)
    fields = ['same_selection', 'same_official_success', 'same_passed_assertions', 'same_database_bytes']
    equal = len(rows)==3 and all(all(r['comparison_to_r2'][k] for k in fields) and
                     r['comparison_to_r2']['native_api_delta']==0 for r in rows)
    save(OUT/'summary.json', {'status': 'COMPLETE', 'decision':
         'PROGRAM_EXPLAINS_R2' if equal else 'INSPECT_NON_EQUIVALENCE', 'results': rows,
         'new_worlds': len(rows), 'new_task_policy_llm_calls': 0,
         'native_api_calls': sum(r['native_api_calls'] for r in rows),
         'scope': 'Post-hoc same-source program control, not full ASI/AWM reproduction.'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['batch', 'execute'])
    parser.add_argument('--task')
    args = parser.parse_args()
    if args.command == 'batch':
        batch()
    else:
        execute(args.task)
