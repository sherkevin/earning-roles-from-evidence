#!/usr/bin/env python3
"""Zero-LLM native AppWorld contract fixture for the paired visibility controller.

Synthetic sentinels are only safety probes. They are never task predictions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import traceback

import aamas_delivery_visibility_dev_v1 as pair

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/aamas2027/runtime_checks/peer_delivery_visibility_native_v1_20260923/attempt_0001'
SENTINELS = ('EXCLUSIVE_RECIPIENT_Q9', '987654.31', 'SCORER_SECRET_Q9')
SECRET = 'SYNTHETIC_ACCESS_TOKEN_Q9_ABCDEF'


def child(arm: str) -> None:
    cfg = pair.config(parent_validation=False)
    pair.verify_runtime(cfg)
    directory = OUT / arm
    directory.mkdir(parents=True, exist_ok=False)
    raw = directory / 'raw.jsonl'
    secrets = pair.base.Secrets()
    pair.a0.safe_log(secrets)
    native_name = 'pj_delivery_native_fixture_v1_' + arm
    native = pair.prior.APP / 'experiments/outputs' / native_name
    pair.require(not native.exists(), 'Fixture native output already exists')
    AppWorld, _ = pair.prior.initialize_runtime()
    with AppWorld(task_id=cfg['task_id'], experiment_name=native_name,
                  load_ground_truth=False, random_seed=cfg['world_seed'],
                  raise_on_extra_parameters=True) as world:
        pair.require(world.task.ground_truth is None and
                     world.raise_on_unsafe_execution, 'Fixture world unsafe')
        pair.install_safe_native_logs(world,secrets)
        counters = pair.a0.task_state_hashes(world)
        records = pair.record_fingerprints(world)
        deferred = []
        sources = {}
        public_probe = pair.a0.initial_public_probe(world,'fixture_initial',arm,
            secrets,raw,deferred,sources)
        pair.require(pair.a0.task_state_hashes(world)==counters and
                     pair.record_fingerprints(world)==records,
                     'Fixture controller probe changed task state')
        synthetic_cfg = json.loads(json.dumps(cfg))
        if arm == 'visible':
            synthetic = OUT / 'synthetic_delivery.json'
            synthetic_cfg['treatment']['proposal_path'] = str(synthetic.relative_to(ROOT))
            synthetic_cfg['treatment']['proposal_sha256'] = pair.sha(synthetic)
        else:
            synthetic_cfg['treatment']['proposal_path'] = 'NONEXISTENT_HIDDEN_SENTINEL_FILE'
        messages = pair.render_messages(world,synthetic_cfg,arm)
        rendered = pair.canonical(messages)
        if arm == 'hidden':
            pair.require('NO_DELIVERY' in rendered and
                         all(sentinel not in rendered for sentinel in SENTINELS),
                         'Hidden initial prompt received synthetic delivery')
        else:
            pair.require(all(sentinel in rendered for sentinel in SENTINELS),
                         'Visible initial prompt missed synthetic delivery')
        context = {'step':1,'origin':'actor'}
        audit = pair.a0.api_guard(world,'consumer_review',arm,secrets,
                                  raw,deferred,context,sources)
        original = pair.install_strict_review_execute(world,counters,records,
                                                       raw,deferred)
        observation = world.execute('print(apis.phone.get_current_date_and_time())')
        pair.a0.flush(raw,deferred)
        pair.require('2023' in observation and len(audit)>=1,
                     'Fixture public GET failed')
        pair.require(all(sentinel not in observation for sentinel in SENTINELS),
                     'Synthetic delivery leaked via public feedback')
        blocked = False
        try:
            world.execute("apis.venmo.create_payment_request(user_email='fixture@example.com', "
                          "amount=1.0, description='fixture', access_token='FIXTURE_TOKEN')")
        except pair.a0.InfrastructureError as exc:
            blocked = 'Read-only review attempted a task write' in str(exc)
        pair.require(blocked,'Read-only write attempt was not immediate global stop')
        world.execute = original
        pair.require(pair.a0.task_state_hashes(world)==counters and
                     pair.record_fingerprints(world)==records,
                     'Fixture read-only review changed task data')
        secrets.observe({'access_token':SECRET})
        world.requester.request_tracker.add_request('get','https://fixture.invalid/sentinel',
                                                     {'access_token':SECRET})
        world.environment_io.append({'number':'synthetic',
                                     'input':"print('access_token="+SECRET+"')",
                                     'output':'Bearer '+SECRET})
        world.save_logs()
        log_paths = (Path(world.output_logs_directory)/'api_calls.jsonl',
                     Path(world.output_logs_directory)/'environment_io.md')
        pair.require(all(SECRET not in path.read_text() and
                         '[REDACTED]' in path.read_text() for path in log_paths),
                     'Native log credential sentinel persisted')
        result = {'arm':arm,'ok':True,'record_fingerprints':records,
                  'write_counters':counters,'public_probe_sha256':public_probe,
                  'task_spec_sha256':pair.a0.sha_text(world.task.instruction+
                                                      pair.canonical(str(world.task.supervisor))),
                  'read_only_write_attempt_immediate_stop':blocked,
                  'synthetic_delivery_isolated':True,
                  'safe_native_logs_no_secret_sentinel':True,
                  'config_sha256':pair.sha(pair.CONFIG),
                  'runner_sha256':pair.sha(Path(pair.__file__))}
        pair.prior.save(directory/'result.json',result)


def parent() -> None:
    cfg = pair.config(parent_validation=True)
    pair.verify_runtime(cfg)
    OUT.mkdir(parents=True,exist_ok=False)
    synthetic = {'recipient':SENTINELS[0], 'amount':SENTINELS[1],
                 'private_score':SENTINELS[2]}
    pair.prior.save(OUT/'synthetic_delivery.json',synthetic)
    rows = []
    try:
        for arm in ('visible','hidden'):
            child = subprocess.run([sys.executable,str(Path(__file__)),'_child',arm],
                                   cwd=ROOT,text=True,capture_output=True,timeout=300)
            (OUT/(arm+'.stdout.txt')).write_text(child.stdout)
            (OUT/(arm+'.stderr.txt')).write_text(child.stderr)
            pair.require(child.returncode==0,arm+' child failed')
            rows.append(json.loads((OUT/arm/'result.json').read_text()))
        for key in ('record_fingerprints','write_counters','public_probe_sha256',
                    'task_spec_sha256'):
            pair.require(rows[0][key]==rows[1][key],
                         'Native two-world initial '+key+' unequal')
        result = {'ok':True,'status':'ZERO_LLM_NATIVE_FIXTURE_PASS',
                  'llm_calls':0,'task_id':cfg['task_id'],
                  'arms':[row['arm'] for row in rows],
                  'record_table_count':len(rows[0]['record_fingerprints']),
                  'record_fingerprints_sha256':pair.a0.sha_text(
                      pair.canonical(rows[0]['record_fingerprints'])),
                  'config_sha256':pair.sha(pair.CONFIG),
                  'runner_sha256':pair.sha(Path(pair.__file__)),
                  'fixture_script_sha256':pair.sha(Path(__file__))}
    except Exception as exc:
        result = {'ok':False,'status':'ZERO_LLM_NATIVE_FIXTURE_FAIL',
                  'llm_calls':0,'error_type':type(exc).__name__,
                  'error':str(exc),'traceback':traceback.format_exc(),
                  'config_sha256':pair.sha(pair.CONFIG),
                  'runner_sha256':pair.sha(Path(pair.__file__)),
                  'fixture_script_sha256':pair.sha(Path(__file__))}
        pair.prior.save(OUT/'result.json',result)
        raise
    pair.prior.save(OUT/'result.json',result)
    print(pair.canonical(result))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command',choices=('run','_child'))
    parser.add_argument('arm',nargs='?')
    args = parser.parse_args()
    if args.command=='run':
        parent()
    else:
        pair.require(args.arm in pair.ARMS,'Invalid fixture arm')
        child(args.arm)
