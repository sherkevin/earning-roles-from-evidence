#!/usr/bin/env python3
"""One manually authorized infrastructure continuation of unstarted census IDs.

Original interrupted outcomes remain UNKNOWN. Frozen native runtime and original
controller are not changed or restarted. No benchmark task is replaced.
"""
from __future__ import annotations
import fcntl
import json
from pathlib import Path
import subprocess
import sys

import aamas_headroom_census as census

OUT=census.OUT
AMENDMENT=census.ROOT/'configs/aamas2027/headroom_recovery_v1.json'
LOG=OUT/'recovery_controller_raw.jsonl'


def check():
    original=census.configure()
    amended=json.loads(AMENDMENT.read_text())
    frozen=json.loads((OUT/'recovery_freeze.json').read_text())
    assert census.probe.digest(AMENDMENT)==frozen['amendment_sha256']
    assert census.probe.digest(__file__)==frozen['recovery_code_sha256']
    health_path=census.ROOT/amended['health_result']['path']
    assert census.probe.digest(health_path)==amended['health_result']['sha256']
    assert json.loads(health_path.read_text())['health_pass']
    for item in amended['preserved_prefix_files']:
        assert census.probe.digest(census.ROOT/item['path'])==item['sha256']
    assert original['jobs'][27:]==amended['remaining_original_jobs']
    if LOG.exists():
        events=[json.loads(line) for line in LOG.read_text().splitlines()]
        permanent_stops={'recovery_outage_stop','recovery_process_failure'}
        if any(e['event'] in permanent_stops for e in events):
            raise RuntimeError('Recovery stop is permanent; no automatic replay')
    gap=False
    for job in amended['remaining_original_jobs']:
        path=OUT/'episodes'/job['id']/'result.json'
        if not path.exists():gap=True;continue
        if gap:raise RuntimeError('Recovered results are not an ordered prefix')
        result=json.loads(path.read_text())
        if result['stop_reason']=='transport_failure':
            raise RuntimeError('Persisted recovered transport failure forbids further paid work')
    return amended,frozen


def main():
    # A second shell must not duplicate the active recovery controller.
    lock=(OUT/'recovery.lock').open('a')
    fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    amended,frozen=check()
    census.probe.log(LOG,'manual_recovery_start',command=sys.argv,
        amendment_sha256=frozen['amendment_sha256'],
        recovery_code_sha256=frozen['recovery_code_sha256'],
        original_outage_preserved=True,original_interrupted_cases_remain_unknown=True,
        observed_results_before_amendment={'clean_success':23,'clean_failure':2,'unknown':2},
        new_episodes_max=30,combined_census_attempt_ceiling=1333)
    for job in amended['remaining_original_jobs']:
        result_path=OUT/'episodes'/job['id']/'result.json'
        if result_path.exists():continue
        if result_path.parent.exists():raise RuntimeError('Partial episode retained; automatic retry forbidden')
        # Metadata only: no change to native task, arm, prompt, model or budget.
        dispatched={**job,'recovery_amendment_sha256':frozen['amendment_sha256']}
        job_path=OUT/'jobs'/(job['id']+'.json')
        census.probe.save(job_path,dispatched)
        census.probe.log(LOG,'recovery_dispatch',job=job,
                         amendment_sha256=frozen['amendment_sha256'])
        with job_path.with_suffix('.log').open('w') as stream:
            proc=subprocess.run([sys.executable,str(census.ROOT/'scripts/aamas_headroom_census.py'),
                                 'episode','--job',str(job_path)],cwd=census.ROOT,
                                stdout=stream,stderr=subprocess.STDOUT)
        if proc.returncode or not result_path.exists():
            census.probe.log(LOG,'recovery_process_failure',job=job,returncode=proc.returncode)
            raise RuntimeError('Recovery child failed; no automatic retry')
        result=json.loads(result_path.read_text())
        summary=census.analyze()
        assert summary['attempted_calls']<=1333
        print(json.dumps({'completed':summary['completed'],'task':job['task_id'],
                          'official_success':result['official_success'],
                          'infrastructure_valid':census.probe.infrastructure_valid(result),
                          'attempted_calls':result['attempted_calls'],
                          'api_errors':result['api_errors']}),flush=True)
        if result['stop_reason']=='transport_failure':
            census.probe.log(LOG,'recovery_outage_stop',job=job)
            raise RuntimeError('Transport failure during one allowed recovery; no more paid work')
    summary=census.analyze(final=True)
    report=OUT/'report.md'
    text=report.read_text()
    # Preserve the unamended generated report and its already-logged hash.
    (OUT/'report_before_recovery_context.md').write_text(text)
    context=('\nInfrastructure amendment: after observing the first 27 attempts '
             '(23 clean successes,2 clean failures,2 transport-interrupted UNKNOWNs), '
             'the original outage stop was honored. DNS and one separately charged '
             'nonbenchmark inference health request later succeeded. A prospectively '
             'logged recovery amendment continued only the 30 original unstarted IDs. '
             'Original interrupted cases were not replaced or reclassified, and all '
             'original thresholds remained unchanged. This is an infrastructure-amended '
             'census, not an unchanged original preregistration.\n')
    report.write_text(text.split('\n',1)[0]+'\n'+context+text.split('\n',1)[1])
    census.probe.log(LOG,'recovery_complete',episodes=57,
                     total_census_attempts=summary['attempted_calls'],
                     report_sha256=census.probe.digest(report),
                     health_cost_separately_recorded=True)


if __name__=='__main__':main()
