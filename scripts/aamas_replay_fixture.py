#!/usr/bin/env python3
"""Replay one existing training trace in native worlds; make no LLM requests.

This is an infrastructure fixture, not an agent capability experiment. Complete
code-prefix re-execution is compared with database-only checkpoint restoration.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import sys

import aamas_real_probe as probe

ROOT=probe.ROOT
OUT=ROOT/'artifacts/experiments/aamas2027/replay_fixture_20260922'
CONFIG=OUT/'config.json'


def file_hashes(directory):
    return {p.name:probe.digest(p) for p in sorted(Path(directory).glob('*')) if p.is_file()}


def main():
    config=json.loads(CONFIG.read_text())
    assert probe.digest(__file__)==config['script_sha256']
    source=ROOT/config['source_trace']
    assert probe.digest(source)==config['source_sha256']
    if (OUT/'raw.jsonl').exists():raise RuntimeError('Refuse fixture overwrite')
    raw=OUT/'raw.jsonl'
    probe.log(raw,'fixture_config',**config,command=sys.argv)
    trace=json.loads(source.read_text())
    steps=trace['steps']; cut=len(steps)//2
    AppWorld,_=probe.initialize_runtime()
    records=[]; checkpoint=None
    for mode in ['full_prefix_a','full_prefix_b','database_only']:
        experiment='aamas_replay_fixture_20260922_'+mode
        record={'mode':mode,'observations':[],'new_LLM_calls':0}
        started=probe.mono()
        try:
            with AppWorld(task_id=config['task_id'],experiment_name=experiment,
                          load_ground_truth=False,random_seed=100,
                          raise_on_extra_parameters=True) as world:
                assert world.task.ground_truth is None
                if mode=='database_only':
                    destination=Path(world.output_checkpoints_directory)/'prefix'
                    shutil.copytree(checkpoint,destination)
                    assert file_hashes(checkpoint)==file_hashes(destination)
                    world.load_state('prefix')
                    selected=steps[cut:]
                else:selected=steps
                for ordinal,step in enumerate(selected):
                    observation=world.execute(step['code'])
                    row={'step':step['step'],'code':step['code'],'observation':observation}
                    record['observations'].append(row)
                    probe.log(raw,'native_replay_step',mode=mode,**row)
                    if mode=='database_only':
                        # One continuation is enough to test state restoration;
                        # never repair or execute further after inspecting it.
                        break
                    if ordinal+1==cut:
                        world.save_state('prefix')
                        prefix=Path(world.output_checkpoints_directory)/'prefix'
                        record['prefix_db_hashes']=file_hashes(prefix)
                        if mode=='full_prefix_a':checkpoint=prefix
                world.save()
                record['final_db_hashes']=file_hashes(world.output_db_home_path_on_disk)
                record['task_completed']=world.task_completed()
                logs=Path(world.output_logs_directory)/'api_calls.jsonl'
                record['native_api_calls']=len(logs.read_text().splitlines())
                record['native_output']=str(Path(world.output_directory))
        except Exception as exc:
            import traceback
            record['error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
            AppWorld.close_all()
        record['wall_seconds']=probe.mono()-started
        probe.save(OUT/(mode+'.json'),record)
        probe.log(raw,'mode_result',mode=mode,record_sha256=probe.digest(OUT/(mode+'.json')),
                  native_api_calls=record.get('native_api_calls'),error=record.get('error'),
                  wall_seconds=record['wall_seconds'])
        records.append(record)
    a,b,c=records
    summary={'timestamp':probe.now(),'fixture_only':True,'task_id':config['task_id'],
             'config_sha256':probe.digest(CONFIG),'new_LLM_calls':0,
             'official_evaluator_invoked':False,'native_prefix_steps':cut,
             'prefix_db_equal':a.get('prefix_db_hashes')==b.get('prefix_db_hashes'),
             'full_observations_equal':a['observations']==b['observations'],
             'final_db_equal':a.get('final_db_hashes')==b.get('final_db_hashes'),
             'source_observations_equal':a['observations']==steps,
             'database_only_first_continuation':c['observations'][0] if c['observations'] else None,
             'database_only_error':c.get('error'),
             'native_api_calls':sum(r.get('native_api_calls',0) for r in records),
             'boundary':'One saved native training trace; does not establish arbitrary replay, LLM determinism, new capability, causal repair, or a free test-world reset.'}
    probe.save(OUT/'summary.json',summary)
    probe.log(raw,'fixture_complete',summary_sha256=probe.digest(OUT/'summary.json'))
    print(json.dumps({k:v for k,v in summary.items() if k!='database_only_first_continuation'}))


if __name__=='__main__':main()
