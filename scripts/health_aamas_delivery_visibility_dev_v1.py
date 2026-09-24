#!/usr/bin/env python3
"""One real, separately budgeted provider health call for frozen paired v1."""
from __future__ import annotations

from pathlib import Path
import sys
import traceback

import aamas_delivery_visibility_dev_v1 as pair

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cfg = pair.config(parent_validation=True)
    pair.require(cfg['status']=='FROZEN_PROSPECTIVE_PAIRED_DEV_V1',
                 'Health requires frozen prospective config')
    pair.verify_runtime(cfg)
    fixture_path = ROOT / cfg['preflight']['native_fixture_path']
    fixture = pair.json.loads(fixture_path.read_text())
    pair.require(fixture['ok'] and fixture['llm_calls']==0 and
                 fixture['config_sha256']==pair.sha(pair.CONFIG) and
                 fixture['runner_sha256']==pair.sha(Path(pair.__file__)),
                 'Final zero-LLM fixture does not match frozen source')
    provider = pair.prior.load_provider()
    pair.require(provider['base']==cfg['provider']['expected_endpoint'],
                 'Provider endpoint changed')
    result_path = ROOT / cfg['preflight']['provider_health_path']
    directory = result_path.parent
    directory.mkdir(parents=True,exist_ok=False)
    raw = directory/'raw.jsonl'
    pair.prior.log(raw,'health_config',config_sha256=pair.sha(pair.CONFIG),
                   runner_sha256=pair.sha(Path(pair.__file__)),
                   protocol_sha256=cfg['protocol_sha256'],
                   source_dependency_hashes=pair.verify_source_dependencies(cfg),
                   fixture_sha256=pair.sha(fixture_path),
                   health_script_sha256=pair.sha(Path(__file__)),
                   model=cfg['provider']['model'],attempt_cap=1,
                   python=sys.version,sys_executable=sys.executable,
                   provider_base=provider['base'],provider_name='内部')
    api = pair.prior.RealAPI(raw,1)
    result = {'ok':False,'config_sha256':pair.sha(pair.CONFIG),
              'runner_sha256':pair.sha(Path(pair.__file__)),
              'protocol_sha256':cfg['protocol_sha256'],
              'fixture_sha256':pair.sha(fixture_path),
              'health_script_sha256':pair.sha(Path(__file__)),
              'real_provider_attempts':0}
    try:
        reply = api.generate([{'role':'user','content':'Reply with exactly OK.'}],
                             max_tokens=32)
        result.update(ok=reply.strip().upper()=='OK',reply_sha256=pair.a0.sha_text(reply),
                      reply_characters=len(reply),
                      returned_models=api.returned_models)
        pair.require(result['ok'],'Provider did not return the health sentinel')
    except Exception as exc:
        result['error']={'type':type(exc).__name__,'message':str(exc),
                         'traceback':traceback.format_exc()}
    finally:
        result['real_provider_attempts']=api.attempts
        result['usage']=pair.a0.usage(api)
        pair.prior.save(result_path,result)
        pair.prior.log(raw,'health_result',ok=result['ok'],
                       attempts=api.attempts,result_sha256=pair.sha(result_path))
    print(pair.canonical({'ok':result['ok'],'attempts':api.attempts,
                          'config_sha256':result['config_sha256'],
                          'runner_sha256':result['runner_sha256'],
                          'usage':result['usage']}))
    pair.require(result['ok'],'Provider health failed; preserve raw and stop')


if __name__=='__main__':
    main()
