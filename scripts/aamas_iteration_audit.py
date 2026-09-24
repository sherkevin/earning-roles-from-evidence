#!/usr/bin/env python3
"""Reconcile this iteration's retained real requests and native call logs.

Analysis only: no model, benchmark execution, regeneration or scorer call.
"""
from __future__ import annotations
import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'artifacts/experiments/aamas2027'
OUT=EXP/'iteration_20260922'
USAGE_KEYS=['input_tokens','cache_read_input_tokens','cache_creation_input_tokens','output_tokens']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def log(event,**payload):
    with (OUT/'analysis_raw.jsonl').open('a') as f:
        f.write(json.dumps({'timestamp':now(),'event':event,'payload':payload})+'\n')


def raw_counts(paths):
    attempts=responses=errors=known_usage_responses=0
    usage=Counter(); manifest=[]
    for path in paths:
        events=[json.loads(line) for line in path.read_text().splitlines()]
        for event in events:
            if event['event']=='request_start':attempts+=1
            elif event['event'] in ['request_error','error']:errors+=1
            elif event['event']=='response':
                responses+=1
                u=event['payload']['response'].get('usage',{})
                known_usage_responses+=all(type(u.get(k)) is int for k in ['input_tokens','output_tokens'])
                for key in USAGE_KEYS:usage[key]+=int(u.get(key,0) or 0)
        manifest.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
    return {'attempts':attempts,'responses':responses,'errors':errors,
            'unknown_usage_attempts':attempts-known_usage_responses,
            'usage':{k:usage[k] for k in USAGE_KEYS},'raw_files':manifest}


def native_logs(results):
    rows=[]
    for path in results:
        result=json.loads(path.read_text())
        f=Path(result['native_output'])/'tasks'/result['task_id']/'logs/api_calls.jsonl'
        trace=path.parent/'public_trace.json'
        if not f.exists():raise RuntimeError('Native call log missing: '+str(f))
        calls=[json.loads(line) for line in f.read_text().splitlines()]
        rows.append({'id':result['id'],'path':str(f),'sha256':sha(f),
                     'logged_native_calls':len(calls),
                     'http_methods':dict(Counter(c['method'] for c in calls)),
                     'solver_completion_checks_untracked':len(json.loads(trace.read_text())['steps']) if trace.exists() else None})
    return {'episodes':rows,'logged_native_calls':sum(r['logged_native_calls'] for r in rows),
            'untracked_solver_completion_checks':sum(r['solver_completion_checks_untracked'] or 0 for r in rows),
            'boundary':'Native api_calls logs plus known per-step task_completed checks; not every hidden evaluator/runtime operation. No public-task content is copied here.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--allow-incomplete',action='store_true');args=ap.parse_args()
    OUT.mkdir(exist_ok=True)
    log('audit_config',command=sys.argv,script_sha256=sha(__file__),new_LLM_calls=0,
        new_native_worlds=0,allow_incomplete=args.allow_incomplete)
    first=EXP/'dev_20260922'; census=EXP/'headroom_20260922'
    first_results=sorted((first/'episodes').glob('*/result.json'))
    census_results=sorted((census/'episodes').glob('*/result.json'))
    if len(census_results)!=57 and not args.allow_incomplete:
        raise RuntimeError('Complete census required unless explicitly analyzing stopped work')
    groups={
        'acquisition_probe':sorted((first/'episodes').glob('*/raw.jsonl'))+sorted((first/'induction').glob('*/raw.jsonl')),
        'headroom_census':sorted((census/'episodes').glob('*/raw.jsonl')),
        'separate_health':[first/'preflight_raw.jsonl',census/'recovery_health_raw.jsonl']}
    counts={k:raw_counts(v) for k,v in groups.items()}
    # No active partial case may be silently included as a completed result.
    assert len(groups['headroom_census'])==len(census_results)
    existing=json.loads((first/'summary.json').read_text())
    assert counts['acquisition_probe']['attempts']==existing['total_attempted_calls_including_induction']==329
    assert counts['acquisition_probe']['usage']==existing['total_known_usage_including_induction']
    census_summary=json.loads((census/('summary.json' if len(census_results)==57 else 'progress.json')).read_text())
    assert counts['headroom_census']['attempts']==census_summary['attempted_calls']
    assert counts['headroom_census']['usage']==census_summary['usage']
    assert counts['separate_health']['attempts']==3
    summary={'timestamp':now(),'census_attempted_tasks':len(census_results),
             'complete_population_attempted':len(census_results)==57,'groups':counts,
             'benchmark_and_induction_attempts':counts['acquisition_probe']['attempts']+counts['headroom_census']['attempts'],
             'separate_health_attempts':3,'all_actual_inference_attempts':sum(v['attempts'] for v in counts.values()),
             'known_usage_all':{k:sum(v['usage'][k] for v in counts.values()) for k in USAGE_KEYS},
             'unknown_usage_attempts_all':sum(v['unknown_usage_attempts'] for v in counts.values()),
             'native_execution':{'acquisition_probe':native_logs(first_results),'headroom_census':native_logs(census_results)},
             'separate_replay_fixture':json.loads((EXP/'replay_fixture_20260922/summary.json').read_text()),
             'usd_cost':None,'inference_hardware':None,
             'boundary':'Development experiments only. Health and zero-LLM replay are separate. Error and response events may overlap for HTTP200 with unusable text. Known usage is not an exact total bill. No implication of scientific readiness.'}
    save(OUT/'accounting.json',summary)
    log('audit_result',accounting_sha256=sha(OUT/'accounting.json'),
        benchmark_attempts=summary['benchmark_and_induction_attempts'],
        separate_health_attempts=3,all_attempts=summary['all_actual_inference_attempts'])
    print(json.dumps({k:summary[k] for k in ['complete_population_attempted','benchmark_and_induction_attempts','separate_health_attempts','all_actual_inference_attempts','known_usage_all','unknown_usage_attempts_all']}))


if __name__=='__main__':main()
