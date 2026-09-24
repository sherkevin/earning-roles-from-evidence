#!/usr/bin/env python3
"""Summarize saved public traces without any new benchmark API request.

AST endpoint inventories and error flags are descriptive. They are not causal
failure labels, correctness oracles or inputs to the unchanged solver.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
import sys

import aamas_headroom_census as census


def endpoint_calls(code):
    try:
        tree=ast.parse(code)
    except SyntaxError:
        return [],True
    endpoints=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):continue
        f=node.func
        if (isinstance(f,ast.Attribute) and isinstance(f.value,ast.Attribute)
            and isinstance(f.value.value,ast.Name) and f.value.value.id=='apis'):
            endpoints.append(f.value.attr+'.'+f.attr)
    return endpoints,False


def main():
    census.configure()
    root=census.OUT
    audit=root/'failure_audit'
    audit.mkdir(exist_ok=True)
    census.probe.log(audit/'audit_raw.jsonl','inventory_start',
                     command=sys.argv,script_sha256=census.probe.digest(__file__),
                     new_benchmark_LLM_calls=0,ground_truth_solution_read=False,
                     interpretation='Exploratory public-trace inventory; not a treatment or counterfactual experiment')
    rows=[]
    for result_path in sorted((root/'episodes').glob('*/result.json')):
        result=json.loads(result_path.read_text())
        path=result_path.parent/'public_trace.json'
        trace=json.loads(path.read_text()) if path.exists() else {'steps':[]}
        step_inventory=[]
        for step in trace['steps']:
            endpoints,syntax_error=endpoint_calls(step['code'])
            observation=step['observation']
            step_inventory.append({'step':step['step'],'endpoint_calls':endpoints,
                'python_syntax_error':syntax_error,
                'execution_error_flag':('Traceback (most recent call last)' in observation or
                                        observation.startswith('Execution failed.'))})
        record={k:result[k] for k in ['id','task_id','official_success','passed_assertions',
                'failed_assertions','attempted_calls','task_completed','stop_reason','api_errors','error_codes']}
        record.update(infrastructure_valid=census.probe.infrastructure_valid(result),
            public_trace_sha256=census.probe.digest(path) if path.exists() else None,
            public_steps=len(trace['steps']),step_inventory=step_inventory)
        annotation=audit/(result['task_id']+'.json')
        if annotation.exists():
            note=json.loads(annotation.read_text())
            assert note['trace_sha256']==record['public_trace_sha256']
            step_ids={s['step'] for s in trace['steps']}
            for evidence in note.get('public_evidence',[]):
                assert set(evidence['steps'])<=step_ids
            record['manual_annotation']=note
        rows.append(record)
    failures=[r for r in rows if r['infrastructure_valid'] and not r['official_success']]
    output={'timestamp':census.probe.now(),'completed_tasks':len(rows),'final_population':len(rows)==57,
            'new_benchmark_LLM_calls':0,'ground_truth_solution_read':False,
            'valid_failure_ids':[r['task_id'] for r in failures],
            'unannotated_failure_ids':[r['task_id'] for r in failures if 'manual_annotation' not in r],
            'infrastructure_flagged_ids':[r['task_id'] for r in rows if not r['infrastructure_valid']],
            'rows':rows,'interpretation':'Observed behaviors only. Causal repairs and capability transfer remain untested.'}
    census.probe.save(audit/'inventory.json',output)
    census.probe.log(audit/'audit_raw.jsonl','inventory_result',
                     sha256=census.probe.digest(audit/'inventory.json'),
                     completed_tasks=len(rows),valid_failures=len(failures),
                     unannotated=len(output['unannotated_failure_ids']))
    print(json.dumps({k:output[k] for k in ['completed_tasks','final_population',
        'valid_failure_ids','unannotated_failure_ids','infrastructure_flagged_ids']}))


if __name__=='__main__':main()
