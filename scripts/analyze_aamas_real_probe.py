#!/usr/bin/env python3
"""Reconcile raw real-API evidence and produce a bounded development report."""
from __future__ import annotations
import json
import math
import platform
import sys
from pathlib import Path

import aamas_real_probe as probe


def wilson(successes, count):
    if not count:
        return None
    z=1.959963984540054
    p=successes/count
    denom=1+z*z/count
    center=(p+z*z/(2*count))/denom
    radius=z*math.sqrt(p*(1-p)/count+z*z/(4*count*count))/denom
    return [max(0,center-radius),min(1,center+radius)]


def main():
    root=probe.OUT
    probe.log(root/'analysis_raw.jsonl','analysis_config',
              command=sys.argv,python=sys.version,platform=platform.platform(),
              script_sha256=probe.digest(__file__),
              contract_sha256=probe.digest(probe.CONTRACT),
              statistics='All paired outcomes; descriptive Wilson95 marginal intervals; exact two-sided discordant-pair binomial test; no optional sample selection',
              random_seed=None)
    summary=probe.analyze()
    if not summary['train_validation_complete']:
        raise SystemExit('Validation not complete; refuse a final scientific report')
    rows=summary['per_episode_results']
    by_id={r['id']:r for r in rows}
    checks=[]
    counts={'attempts':0,'responses':0,'errors':0,'total_api_operations':0,
            'input_tokens':0,'output_tokens':0,'cache_read_input_tokens':0,
            'cache_creation_input_tokens':0,'cap_exceedances':0}
    files=[]
    error_events=[]
    ledger_paths=sorted(list((root/'episodes').glob('*/raw.jsonl'))+
                        list((root/'induction').glob('*/raw.jsonl')))
    for path in ledger_paths:
        raw=[json.loads(line) for line in path.read_text().splitlines()]
        requests=[r['payload'] for r in raw if r['event']=='request_start']
        responses=[r['payload'] for r in raw if r['event']=='response']
        errors=[r['payload'] for r in raw if r['event']=='request_error']
        error_events.extend({'ledger':str(path.relative_to(probe.ROOT)),
                             'attempt':r['attempt'],'error_type':r['error_type'],
                             'message':r['message']} for r in errors)
        counts['attempts']+=len(requests);counts['responses']+=len(responses);counts['errors']+=len(errors)
        req_by_id={r['attempt']:r for r in requests}
        assert len(req_by_id)==len(requests),f'Duplicate attempt number in {path}'
        for r in responses:
            assert r['attempt'] in req_by_id
            for key in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']:
                counts[key]+=int(r['response'].get('usage',{}).get(key,0) or 0)
            if r['response'].get('usage',{}).get('output_tokens',0)>req_by_id[r['attempt']]['request']['max_tokens']:
                counts['cap_exceedances']+=1
        for request in requests:
            assert request['request']['model']=='qwen3.8-max'
            assert request['request']['temperature']==0
            assert request['request']['max_tokens'] in [1536,2048]
        files.append({'path':str(path.relative_to(probe.ROOT)),
                      'sha256':probe.digest(path),'bytes':path.stat().st_size})
    assert counts['attempts']==summary['total_attempted_calls_including_induction']
    for key in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']:
        assert counts[key]==summary['total_known_usage_including_induction'][key]
    for row in rows:
        assert row['attempted_calls']<=30
        path=Path(row['native_output'])/'tasks'/row['task_id']/'logs/api_calls.jsonl'
        if path.exists():
            row['native_api_operations']=len(path.read_text().splitlines())
            counts['total_api_operations']+=row['native_api_operations']
        else:
            row['native_api_operations']=None
    checks=['All raw ledgers parse','Unique attempt IDs','Requests match frozen model/settings',
            'Every native episode stays within 30 attempted calls',
            'Raw attempt totals equal processed totals','Raw token totals equal processed totals']
    rescoring_files=[]
    for path in sorted(root.glob('episodes/*/rescor*.json*')):
        if path.suffix=='.jsonl':
            for line in path.read_text().splitlines():
                json.loads(line)
        else:
            json.loads(path.read_text())
        rescoring_files.append({'path':str(path.relative_to(probe.ROOT)),
                               'sha256':probe.digest(path),'bytes':path.stat().st_size})
    pairs=summary['validation_pairs'];n=len(pairs)
    wins=sum(p['difference']>0 for p in pairs);losses=sum(p['difference']<0 for p in pairs)
    discordance=wins+losses
    pvalue=min(1.0,2*sum(math.comb(discordance,k) for k in range(min(wins,losses)+1))/(2**discordance)) if discordance else None
    empty_successes=sum(p['empty'] for p in pairs);memory_successes=sum(p['memory'] for p in pairs)
    empty_rows=[by_id['validate_empty_'+p['family']] for p in pairs]
    memory_rows=[by_id['validate_memory_'+p['family']] for p in pairs]
    inputs=lambda r:sum(r['usage'].get(k,0) for k in ['input_tokens','cache_read_input_tokens','cache_creation_input_tokens'])
    arm_stats={}
    for arm,arm_rows in [('empty',empty_rows),('memory',memory_rows)]:
        arm_stats[arm]={'successes':sum(r['official_success'] for r in arm_rows),'n':len(arm_rows),
            'attempted_calls':sum(r['attempted_calls'] for r in arm_rows),
            'known_context_tokens_including_cache':sum(inputs(r) for r in arm_rows),
            'known_output_tokens_including_reasoning':sum(r['usage']['output_tokens'] for r in arm_rows),
            'wall_seconds':sum(r['wall_seconds'] for r in arm_rows),
            'api_errors':sum(r['api_errors'] for r in arm_rows),
            'unknown_usage_attempts':sum(r['unknown_usage_attempts'] for r in arm_rows)}
    invalid_pairs=[p['family'] for p in pairs if not p['runtime_valid']]
    gate_failures=[]
    if wins<2:gate_failures.append('Fewer than two paired official-success wins')
    if losses:gate_failures.append('At least one paired official-success loss')
    if invalid_pairs:gate_failures.append('Unwaived infrastructure error in pair(s): '+', '.join(invalid_pairs))
    if any(p['success_flip'] for p in summary['unchanged_package_controls']):gate_failures.append('Unchanged-package success flip')
    if not summary['acquisition_infrastructure_valid']:gate_failures.append('Invalid acquisition infrastructure')
    if not summary['memory_package_valid']:gate_failures.append('Memory package provenance invalid')
    if any(not p['runtime_valid'] for p in summary['unchanged_package_controls']):gate_failures.append('Invalid unchanged-package control infrastructure')
    if sum(p['assertion_difference'] for p in pairs)<0:gate_failures.append('Negative mean assertion-fraction change')
    acquisition_rows=[r for r in rows if r['stage'] in ['acquire','acquire_transport_repair']]+summary['induction_results']
    acquisition_cost={'attempted_calls':sum(r['attempted_calls'] for r in acquisition_rows),
                      'known_context_tokens_including_cache':sum(inputs(r) for r in acquisition_rows),
                      'known_output_tokens_including_reasoning':sum(r['usage']['output_tokens'] for r in acquisition_rows)}
    control_rows=[r for r in rows if r['stage']=='unchanged_control']
    cost_partition={'acquisition_and_induction':acquisition_cost['attempted_calls'],
                    'paired_validation':sum(r['attempted_calls'] for r in empty_rows+memory_rows),
                    'unchanged_controls':sum(r['attempted_calls'] for r in control_rows)}
    assert sum(cost_partition.values())==counts['attempts'],'Unassigned or duplicate cost category'
    checks.append('Acquisition including repair, validation and null-control cost partitions reconcile')
    metrics={'paired_n':n,'paired_wins':wins,'paired_losses':losses,
             'success_difference':(memory_successes-empty_successes)/n,
             'empty_wilson95':wilson(empty_successes,n),'memory_wilson95':wilson(memory_successes,n),
             'exact_discordant_pair_two_sided_p':pvalue,
             'uncertainty_boundary':'Descriptive small-development statistics, conditional on one learned checkpoint; not confirmatory inference or proof of equivalence.',
             'arm_statistics':arm_stats,'all_run_costs_from_raw':counts,
             'checks':checks,'raw_file_manifest':files,'rescoring_file_manifest':rescoring_files,
             'infrastructure_invalid_pairs':invalid_pairs,'gate_failure_reasons':gate_failures,
             'error_events':error_events,'acquisition_and_induction_cost':acquisition_cost,
             'attempt_cost_partition':cost_partition,
             'decision':'ENTER_PREDECLARED_DEV' if summary['dev_gate_pass'] else 'DO_NOT_LOCK_Q1_OR_ENTER_CONDITIONAL_DEV',
             'unknown_usage_attempts':summary['total_unknown_usage_attempts'],
             'price_usd':None,'complete_dollar_cost_known':False}
    probe.save(root/'analysis.json',metrics)
    e=arm_stats['empty'];m=arm_stats['memory']
    lines=['# Real AppWorld acquisition probe — observed results','',
           f"The frozen memory package achieved {memory_successes}/{n} official successes; the identical agent without memory achieved {empty_successes}/{n}. There were {wins} paired wins and {losses} paired losses.",'',
           f"Prospective development gate: **{'PASS' if summary['dev_gate_pass'] else 'NOT PASSED'}**. This is a prerequisite experiment, not evidence of collaboration compatibility or role emergence.",'',
           'Gate reasons: '+('; '.join(gate_failures) or 'All declared conditions satisfied')+'.','',
           'Official scores describe saved final states. The recovered HTTP200 response with no executable text in family 692c77d is still an unwaived infrastructure error; this pair is not silently promoted to a clean treatment comparison. Two separate path-only scoring failures were repaired using byte-identical saved databases and the unchanged evaluator, with no additional model calls.','',
           '| Native validation task | Empty success | Memory success | Empty calls | Memory calls |',
           '|---|---:|---:|---:|---:|']
    for p in pairs:
        er=by_id['validate_empty_'+p['family']];mr=by_id['validate_memory_'+p['family']]
        lines.append(f"| {p['family']}_2 | {int(p['empty'])} | {int(p['memory'])} | {er['attempted_calls']} | {mr['attempted_calls']} |")
    lines += ['',f"The two unchanged-package controls had {sum(v['success_flip'] for v in summary['unchanged_package_controls'])} success flips. They are limited variability diagnostics.",'',
              f"Empty/memory paired validation used {e['attempted_calls']}/{m['attempted_calls']} attempted calls, {e['known_context_tokens_including_cache']:,}/{m['known_context_tokens_including_cache']:,} known context tokens including cache, and {e['known_output_tokens_including_reasoning']:,}/{m['known_output_tokens_including_reasoning']:,} reported output tokens including reasoning.",'',
              f"Acquisition and induction separately cost {acquisition_cost['attempted_calls']} attempted calls, {acquisition_cost['known_context_tokens_including_cache']:,} known context tokens and {acquisition_cost['known_output_tokens_including_reasoning']:,} reported output tokens. This overhead is not excluded when evaluating reuse economics.",'',
              f"Including acquisition, its recorded infrastructure retry, induction, paired validation and unchanged controls, there are {counts['attempts']} real attempted LLM calls. {summary['total_unknown_usage_attempts']} failed attempts have unknown token usage. Known token counts are lower bounds on full consumption, not an exact monetary bill. Provider prices were unavailable; USD cost remains unknown.",'',
              f"The provider returned total output above the requested text cap on {counts['cap_exceedances']} calls. This experiment matches requested settings and attempted-call limits; it cannot claim a hard equal actual-token budget.",'',
              f"Descriptive Wilson95 success intervals are {metrics['empty_wilson95']} (empty) and {metrics['memory_wilson95']} (memory). The paired exact discordance test is {pvalue}; None means no discordant cases, not demonstrated equivalence. Six families and one acquired checkpoint cannot establish broad improvement or absence of an effect.",'',
              'All tasks, package candidates, failures and costs are retained. Original failed acquisition is not mislabeled as a scientific failure; its one declared same-task replacement is explicit. No test-normal or test-challenge inference was performed.','',
              'The two API-health preflight attempts (one authentication-format error and one success) are recorded separately in preflight_raw.jsonl; they are not benchmark or induction attempts. Raw benchmark traces contain simulated accounts and remain local.','',
              'Reused assets: the verified named-provider adapter, official native prompt/runtime/scorer, hashed split selection, six actual training traces, six bounded source-linked procedural candidates, and an auditable paired runner. Candidate advice is not automatically semantically verified.','',
              'Reproduce analysis: `/Users/jingwu/work/AppWorld/.venv-b1-api/bin/python scripts/analyze_aamas_real_probe.py` from this project. The JSON analysis holds every raw log hash and separate task/cost statistics.']
    (root/'report.md').write_text('\n'.join(lines)+'\n')
    probe.log(root/'analysis_raw.jsonl','analysis_result',metrics_sha256=probe.digest(root/'analysis.json'),
              report_sha256=probe.digest(root/'report.md'),checks=checks,decision=metrics['decision'])
    print(json.dumps({k:metrics[k] for k in ['paired_n','paired_wins','paired_losses','success_difference','decision']},indent=2))


if __name__=='__main__':main()
