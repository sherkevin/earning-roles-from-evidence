"""Native saved-code intervention. No new task-policy LLM calls."""
from __future__ import annotations
import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from r1_role_contract_core import Contract, first_consumer_boundary
from r1_role_contract_core import replace_handoff, library_adapter
from r2_handoff_guard import guarded_helper

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/experiments/aamas2027/handoff_effect_20260922'
MANIFEST = OUT / 'native_manifest.json'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def load_prior():
    spec=importlib.util.spec_from_file_location('r1_prior',ROOT/'scripts/aamas_real_probe.py')
    prior=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    return prior

def helper_code(endpoint, field, hypotheses):
    expressions={'source':'_r1_s','predicate':'_r1_p','union':'_r1_s | _r1_p',
        'intersection':'_r1_s & _r1_p','source_minus_predicate':'_r1_s - _r1_p',
        'predicate_minus_source':'_r1_p - _r1_s'}
    outputs=', '.join('('+expressions[h]+')' for h in hypotheses)
    return f'''import json

def _r1_pages(fn):
    rows = []
    for page in range(100):
        batch = fn(access_token=access_token, page_index=page, page_limit=20)
        rows.extend(batch)
        if len(batch) < 20:
            return rows
    raise RuntimeError("R1 pagination cap reached")

_r1_rows = _r1_pages(apis.spotify.{endpoint})
_r1_liked = _r1_pages(apis.spotify.show_liked_songs)
_r1_s = {{sid for row in _r1_rows for sid in (row[{field!r}] if {field!r} == 'song_ids' else [row[{field!r}]])}}
_r1_p = {{row['song_id'] for row in _r1_liked}}
_r1_outputs = [{outputs}]
assert _r1_outputs and all(x == _r1_outputs[0] for x in _r1_outputs), "R1 UNKNOWN"
role_handoff_ids = sorted(_r1_outputs[0])
print(json.dumps({{"source":sorted(_r1_s),"predicate":sorted(_r1_p),"selected":role_handoff_ids,"entity_type":"song"}}))
'''

def execute(task_id, arm):
    manifest=json.loads(MANIFEST.read_text())
    if digest(OUT/'guard_candidate.json') != manifest['guard_sha256']:
        raise RuntimeError('Guard changed after freeze')
    if json.loads((OUT/'guard_candidate.json').read_text())['candidate']['guard']!='exclude_already_done':
        raise RuntimeError('No valid learned candidate for this execution')
    for relative, expected in manifest['code_sha256'].items():
        if digest(ROOT/relative) != expected:
            raise RuntimeError('Frozen code changed: '+relative)
    task=next(t for t in manifest['tasks'] if t['task_id']==task_id)
    trace_path=ROOT/task['trace_path']
    if digest(trace_path)!=task['trace_sha256']:
        raise RuntimeError('Source trace changed')
    trace=json.loads(trace_path.read_text())
    index, variable=first_consumer_boundary(trace['steps'])
    if index!=task['boundary_index'] or variable!=task['boundary_variable']:
        raise RuntimeError('Boundary differs from freeze')
    hypotheses=manifest['source_contract']['hypotheses']
    if arm=='single_program': hypotheses=hypotheses[:1]
    job_id=task_id+'_'+arm
    job=OUT/'replays'/job_id
    job.mkdir(parents=True,exist_ok=False)
    prior=load_prior(); AppWorld, _=prior.initialize_runtime()
    experiment='r2_'+hashlib.sha256(job_id.encode()).hexdigest()[:20]
    native=prior.APP/'experiments/outputs'/experiment
    if native.exists(): raise RuntimeError('Refusing native-output overwrite')
    raw=job/'raw.jsonl'; started=prior.mono()
    result={'task_id':task_id,'arm':arm,'experiment':experiment,
        'new_policy_llm_calls':0,'contract_sha256':digest(MANIFEST),
        'status':'INVALID','runtime_error':None,'evaluator_error':None}
    try:
        with AppWorld(task_id=task_id,experiment_name=experiment,
                load_ground_truth=False,random_seed=100,
                raise_on_extra_parameters=True) as world:
            assert world.task.ground_truth is None
            for i, step in enumerate(trace['steps']):
                code=step['code']
                if i==index and arm!='original':
                    endpoint, field=library_adapter(trace['instruction'])
                    insertion=guarded_helper(endpoint,field,hypotheses,code,variable,arm=='semantic_guard')
                    observation=world.execute(insertion)
                    prior.log(raw,'role_intervention',code=insertion,observation=observation)
                    result['handoff']=json.loads(observation)
                    code=replace_handoff(code,variable)
                    result['patch']={'original_sha256':hashlib.sha256(step['code'].encode()).hexdigest(),
                        'patched_sha256':hashlib.sha256(code.encode()).hexdigest(),
                        'code':code,'variable':variable,'boundary_step':step['step']}
                observation=world.execute(code)
                prior.log(raw,'replayed_step',original_step=step['step'],code=code,observation=observation)
                if i==index:
                    capture=world.execute('import json\nprint(json.dumps(sorted(list('+variable+'))))')
                    result['actual_consumed_selection']=json.loads(capture)
                    prior.log(raw,'boundary_capture',variable=variable,observation=capture)
            result['task_completed']=world.task_completed()
            world.save()
        result['status']='EXECUTED'
    except Exception as error:
        result['runtime_error']={'type':type(error).__name__,'message':str(error)}
        try: AppWorld.close_all()
        except Exception: pass
    if result['status']=='EXECUTED':
        try:
            from appworld.evaluator import evaluate_task
            ev=evaluate_task(task_id=task_id,experiment_name=experiment,
                suppress_errors=True,save_report=True).to_dict(stats_only=False)
            save(job/'evaluator_only.json',ev)
            result.update(official_success=bool(ev['success']),
                passed_assertions=len(ev['passes']),failed_assertions=len(ev['failures']),
                status='SCORED')
        except Exception as error:
            result['evaluator_error']={'type':type(error).__name__,'message':str(error)}
            result['status']='INVALID'
    calls=native/'tasks'/task_id/'logs/api_calls.jsonl'
    result['native_api_calls']=len(calls.read_text().splitlines()) if calls.exists() else None
    result['wall_seconds']=prior.mono()-started
    result['native_output']=str(native)
    save(job/'result.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)

def batch():
    manifest=json.loads(MANIFEST.read_text())
    results=[]
    for task in manifest['tasks']:
        for arm in manifest['arms']:
            job=OUT/'replays'/(task['task_id']+'_'+arm)
            if job.exists(): raise RuntimeError('Existing replay; explicit new version required')
            log_path=OUT/(task['task_id']+'_'+arm+'.log')
            with log_path.open('w') as stream:
                process=subprocess.run([sys.executable,__file__,'execute',
                    '--task',task['task_id'],'--arm',arm],stdout=stream,stderr=subprocess.STDOUT)
            result_path=job/'result.json'
            if process.returncode or not result_path.exists():
                save(OUT/'batch_stop.json',{'reason':'child_error','task':task['task_id'],'arm':arm})
                return
            row=json.loads(result_path.read_text()); results.append(row)
            print(task['task_id'],arm,row['status'],row.get('official_success'),flush=True)
            if row['status']!='SCORED' or (arm=='original' and
                    row['official_success']!=task['archived_official_success']):
                save(OUT/'batch_stop.json',{'reason':'invalid_or_replay_mismatch','results':results})
                return
    baseline_path=ROOT/manifest['r1_summary_path']
    if digest(baseline_path)!=manifest['r1_summary_sha256']:
        raise RuntimeError('R1 baseline changed')
    baseline=json.loads(baseline_path.read_text())
    by={(r['task_id'],r['arm']):r for r in results}
    old={(r['task_id'],r['arm']):r for r in baseline['results']}
    effects=[]
    for t in manifest['tasks']:
        tid=t['task_id']
        a=int(old[(tid,'original')]['official_success'])
        b=int(old[(tid,'qualified')]['official_success'])
        c=int(by[(tid,'original_guard')]['official_success'])
        d=int(by[(tid,'semantic_guard')]['official_success'])
        effects.append({'task_id':tid,'old_plain':a,'semantic_plain':b,
                       'old_guard':c,'semantic_guard':d,'interaction':d-c-b+a})
    summary={'status':'COMPLETE','new_policy_llm_calls':0,'results':results,
        'paired_effects':effects,'guard_induction_calls':1,
        'guard_is_common_consumer_control':True,
        'decision':'INSPECT_JOINT_SEMANTIC_STATE_EFFECT',
        'boundary':'Post-hoc native factorial; not autonomous multiagent superiority or independent confirmation.'}
    save(OUT/'native_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['batch','execute'])
    parser.add_argument('--task'); parser.add_argument('--arm',choices=['original_guard','semantic_guard'])
    args=parser.parse_args()
    if args.command=='batch': batch()
    else: execute(args.task,args.arm)
