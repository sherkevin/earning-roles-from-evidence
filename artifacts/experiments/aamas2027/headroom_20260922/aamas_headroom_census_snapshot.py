#!/usr/bin/env python3
"""One complete, prospectively specified native AppWorld dev baseline census.

No treatment, learner, hidden retries or outcome-dependent task selection.
Reuses the real API/native runtime audited in aamas_real_probe.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import aamas_real_probe as probe

ROOT=probe.ROOT
OUT=ROOT/'artifacts/experiments/aamas2027/headroom_20260922'
CONTRACT=ROOT/'configs/aamas2027/headroom_census_v1.json'


def configure():
    probe.OUT=OUT
    probe.CONTRACT=CONTRACT
    # Only retry settings are consumed by the shared native episode runner.
    probe.AMENDMENT=CONTRACT
    contract=json.loads(CONTRACT.read_text())
    freeze=json.loads((OUT/'freeze.json').read_text())
    if probe.digest(CONTRACT)!=freeze['contract_sha256']:
        raise RuntimeError('Prospective census contract changed')
    for path,expected in freeze['code_hashes'].items():
        if probe.digest(ROOT/path)!=expected:
            raise RuntimeError('Frozen runtime code changed: '+path)
    return contract


def analyze(final=False):
    contract=configure()
    paths=sorted((OUT/'episodes').glob('*/result.json'))
    rows=[json.loads(p.read_text()) for p in paths]
    expected={j['id']:j for j in contract['jobs']}
    assert len(rows)==len({r['id'] for r in rows})
    for row in rows:
        assert row['id'] in expected and row['task_id']==expected[row['id']]['task_id']
        assert row['arm']=='empty' and row['memory_sha256'] is None
        assert row['attempted_calls']<=30
    valid=[r for r in rows if probe.infrastructure_valid(r)]
    success=sum(r['official_success'] for r in valid)
    failure=len(valid)-success
    unknown=57-len(valid)
    complete=len(rows)==57
    decision='INCOMPLETE'
    if complete:
        if success>=52:decision='CEILING_STOP_CONTENT_GAIN_REGIME'
        elif success+unknown<=5:decision='FLOOR_STOP_CONTENT_GAIN_REGIME'
        elif success>=6 and failure>=6:decision='HEADROOM_ONLY_NO_TREATMENT_AUTHORIZATION'
        else:decision='INCONCLUSIVE_INFRASTRUCTURE'
    summary={'timestamp':probe.now(),'contract_sha256':probe.digest(CONTRACT),
             'completed':len(rows),'planned':57,'complete':complete,
             'valid_successes':success,'valid_failures':failure,
             'unknown_or_unrun':unknown,'success_count_bounds':[success,success+unknown],
             'observed_official_successes_including_flagged':sum(r['official_success'] for r in rows),
             'attempted_calls':sum(r['attempted_calls'] for r in rows),
             'api_errors':sum(r['api_errors'] for r in rows),
             'unknown_usage_attempts':sum(r['unknown_usage_attempts'] for r in rows),
             'usage':{k:sum(r['usage'].get(k,0) for r in rows) for k in
                      ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']},
             'wall_seconds_sum_not_elapsed':sum(r['wall_seconds'] for r in rows),
             'api_seconds_including_failed_calls':sum(r['api_seconds'] for r in rows),
             'decision':decision,'price_usd':None,'per_task_results':rows,
             'boundary':'Complete dev census under one fixed native agent; no treatment, no new capability or compatibility claim, no confirmatory inference.'}
    probe.save(OUT/('summary.json' if final else 'progress.json'),summary)
    if final:
        if not complete:raise RuntimeError('Cannot issue final census with unrun tasks')
        audit_raw(summary)
        write_report(summary)
        probe.log(OUT/'analysis_raw.jsonl','analysis_result',
                  summary_sha256=probe.digest(OUT/'summary.json'),
                  report_sha256=probe.digest(OUT/'report.md'),decision=decision)
    return summary


def audit_raw(summary):
    counts={'attempts':0,'responses':0,'errors':0,'output_above_requested':0}
    usage={k:0 for k in summary['usage']}
    manifest=[]
    for result in summary['per_task_results']:
        path=OUT/'episodes'/result['id']/'raw.jsonl'
        events=[json.loads(line) for line in path.read_text().splitlines()]
        configs=[r['payload'] for r in events if r['event']=='episode_config']
        assert len(configs)==1 and configs[0]['contract_sha256']==summary['contract_sha256']
        assert not any(r['event']=='memory_loaded' for r in events)
        starts=[r['payload'] for r in events if r['event']=='request_start']
        assert len(starts)==result['attempted_calls']
        assert len({r['attempt'] for r in starts})==len(starts)
        for start in starts:
            request=start['request']
            assert request['model']=='qwen3.8-max' and request['temperature']==0 and request['max_tokens']==2048
        counts['attempts']+=len(starts)
        for event in events:
            if event['event']=='request_error':counts['errors']+=1
            if event['event']=='response':
                counts['responses']+=1
                u=event['payload']['response'].get('usage',{})
                for key in usage:usage[key]+=int(u.get(key,0) or 0)
                if u.get('output_tokens',0)>2048:counts['output_above_requested']+=1
        manifest.append({'path':str(path.relative_to(ROOT)),
                         'sha256':probe.digest(path),'bytes':path.stat().st_size})
    assert counts['attempts']==summary['attempted_calls']
    assert counts['errors']==summary['api_errors']
    assert usage==summary['usage']
    probe.save(OUT/'raw_audit.json',{'counts':counts,'usage':usage,'manifest':manifest,
               'checks':['All 57 expected IDs exactly once','Empty agent in every task',
                         'No prompt history truncation or memory injection',
                         '30 attempt limits and frozen model/settings','Raw and summary calls/tokens agree']})


def write_report(s):
    families={}
    for row in s['per_task_results']:
        family=row['task_id'].split('_')[0]
        group=families.setdefault(family,{'success':0,'failure':0,'unknown':0,'calls':0})
        group['calls']+=row['attempted_calls']
        if not probe.infrastructure_valid(row):
            group['unknown']+=1
        else:
            group['success' if row['official_success'] else 'failure']+=1
    lines=['# Complete native AppWorld dev baseline census','',
           f"All {s['completed']}/57 tasks were attempted with the same empty agent. Valid official successes: {s['valid_successes']}; valid task failures: {s['valid_failures']}; infrastructure-flagged cases: {s['unknown_or_unrun']}.",'',
           f"Predeclared decision: **{s['decision']}**. With flagged cases treated as unknown, the full-population success count lies within {s['success_count_bounds']}.",'',
           'This is a development-environment diagnostic. It does not reinstate the failed acquisition package or demonstrate any treatment benefit. No hard-only subset is selected for a revised headline score.','',
           '| Family (all three native siblings) | Success | Failure | Unknown | Attempted calls |',
           '|---|---:|---:|---:|---:|']
    for family,group in sorted(families.items()):
        lines.append(f"| {family} | {group['success']} | {group['failure']} | {group['unknown']} | {group['calls']} |")
    context=sum(s['usage'][k] for k in ['input_tokens','cache_read_input_tokens','cache_creation_input_tokens'])
    lines+=['',f"Real attempted LLM calls: {s['attempted_calls']}; known context tokens including cache: {context:,}; reported output including reasoning: {s['usage']['output_tokens']:,}; unknown-usage attempts: {s['unknown_usage_attempts']}. Dollar cost is unavailable, not zero.",'',
            'The decision uses the previously declared open interval (0.10, 0.90): at most five successes or at least 52 successes stops this content-gain regime. Otherwise at least six clean successes and six clean failures establish headroom only. Infrastructure uncertainty that straddles these conditions produces an inconclusive result.','',
            'The population is the complete 57-task development split (19 families), not 57 independent organizations. No test-normal or test-challenge inference occurred. Prompt, runtime, official evaluator and data remain pinned; API model alias is not an independently verified checkpoint. All errors and exhausted budgets remain recorded.','',
            'Reused: the real named-provider adapter, native prompt/runtime/scorer, neutral output storage and complete per-attempt ledgers. All failure traces support a subsequent zero-new-LLM error census, with measured outcomes kept separate from causal hypotheses.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')


def run():
    contract=configure()
    controller_log=OUT/'controller_raw.jsonl'
    if controller_log.exists():
        events=[json.loads(line) for line in controller_log.read_text().splitlines()]
        if any(e['event']=='outage_stop' for e in events):
            raise RuntimeError('A persisted outage stop forbids automatic paid resumption')
    completed_prefix=[]
    gap=False
    for job in contract['jobs']:
        path=OUT/'episodes'/job['id']/'result.json'
        if not path.exists():
            gap=True
            continue
        if gap:raise RuntimeError('Completed tasks do not form the frozen ordered prefix')
        row=json.loads(path.read_text())
        completed_prefix.append(row)
        if len(completed_prefix)>=2 and all(r['stop_reason']=='transport_failure' for r in completed_prefix[-2:]):
            raise RuntimeError('Existing consecutive transport failures forbid paid resumption')
    probe.log(OUT/'controller_raw.jsonl','controller_start',command=sys.argv,
              contract_sha256=probe.digest(CONTRACT),wrapper_sha256=probe.digest(__file__),
              shared_runner_sha256=probe.digest(ROOT/'scripts/aamas_real_probe.py'),
              python=sys.version,attempt_ceiling=1710,concurrency=1)
    for index,job in enumerate(contract['jobs']):
        result_path=OUT/'episodes'/job['id']/'result.json'
        if result_path.exists():continue
        if result_path.parent.exists():raise RuntimeError('Interrupted task requires explicit provenance review; no automatic restart')
        job_path=OUT/'jobs'/(job['id']+'.json')
        probe.save(job_path,job)
        with job_path.with_suffix('.log').open('w') as stream:
            proc=subprocess.run([sys.executable,__file__,'episode','--job',str(job_path)],
                                cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        if proc.returncode or not result_path.exists():
            probe.log(OUT/'controller_raw.jsonl','controller_failure',job=job,returncode=proc.returncode)
            raise RuntimeError('Task subprocess failed; see retained job log')
        result=json.loads(result_path.read_text())
        summary=analyze()
        print(json.dumps({'completed':index+1,'task':job['task_id'],
                          'official_success':result['official_success'],
                          'infrastructure_valid':probe.infrastructure_valid(result),
                          'attempted_calls':result['attempted_calls'],
                          'api_errors':result['api_errors']}),flush=True)
        by_id={r['id']:r for r in summary['per_task_results']}
        recent=[by_id[j['id']] for j in contract['jobs'][max(0,index-1):index+1]]
        # A sustained provider outage is not a task-capability experiment.
        if len(recent)==2 and all(r['stop_reason']=='transport_failure' for r in recent):
            probe.log(OUT/'controller_raw.jsonl','outage_stop',jobs=[r['id'] for r in recent])
            raise RuntimeError('Two consecutive transport-stopped tasks; no further paid calls')
    analyze(final=True)
    probe.log(OUT/'controller_raw.jsonl','controller_complete',episodes=57)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['run','episode','analyze'])
    parser.add_argument('--job')
    args=parser.parse_args()
    configure()
    if args.command=='episode':probe.episode(json.loads(Path(args.job).read_text()))
    elif args.command=='run':run()
    else:analyze(final=True)


if __name__=='__main__':main()
