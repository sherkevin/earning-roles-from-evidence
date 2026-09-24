#!/usr/bin/env python3
"""Score identical saved native states through an arm-neutral disk path.

No model calls, no state replay, no scorer patch and no outcome-dependent retry.
"""
import argparse
import json
import hashlib
import os
from pathlib import Path
import shutil
import traceback

import aamas_real_probe as p


def main():
    args=argparse.ArgumentParser()
    args.add_argument('job_id')
    job=args.parse_args().job_id
    directory=p.OUT/'episodes'/job
    original_path=directory/'result.json'
    original=json.loads(original_path.read_text())
    if original['scorer_available']:
        raise RuntimeError('Original scorer available; no rescoring is needed')
    if original['runtime_error']:
        raise RuntimeError('Task runtime failed; do not reinterpret as scorer path defect')
    raw=[json.loads(line) for line in (directory/'raw.jsonl').read_text().splitlines()]
    errors=[r['payload'] for r in raw if r['event']=='evaluation_error']
    if not errors or errors[-1]['message']!='Invalid changes_file_path. It cannot contain in-memory connection strings.':
        raise RuntimeError('Unexpected scorer failure; explicit diagnosis required')
    log=directory/'rescoring_raw.jsonl'
    experiment='aamas_score_20260922_'+hashlib.sha256(job.encode()).hexdigest()[:16]
    source=Path(original['native_output'])/'tasks'/original['task_id']/'dbs'
    target=p.APP/'experiments/outputs'/experiment/'tasks'/original['task_id']/'dbs'
    if target.exists() or (directory/'rescored_result.json').exists():
        raise RuntimeError('Refuse overwrite')
    files=[{'name':x.name,'sha256':p.digest(x),'bytes':x.stat().st_size} for x in sorted(source.iterdir()) if x.is_file()]
    p.log(log,'rescoring_config',job=job,reason='Pinned upstream substring memory path test',
          original_result_sha256=p.digest(original_path),original_db_files=files,
          source=str(source),target=str(target),llm_calls=0,
          source_script_sha256=p.digest(__file__))
    shutil.copytree(source,target)
    for item in files:
        assert p.digest(target/item['name'])==item['sha256']
    os.environ['APPWORLD_ROOT']=str(p.APP)
    from appworld.evaluator import evaluate_task
    try:
        evaluation=evaluate_task(task_id=original['task_id'],experiment_name=experiment,
                                 suppress_errors=True,save_report=True).to_dict(stats_only=False)
    except Exception as exc:
        p.log(log,'rescoring_error',message=str(exc),traceback=traceback.format_exc())
        raise
    p.save(directory/'rescored_evaluator_only.json',evaluation)
    passes=len(evaluation.get('passes',[]));failures=len(evaluation.get('failures',[]))
    result={**original,'official_success':bool(evaluation.get('success',False)),
            'scorer_available':True,'passed_assertions':passes,'failed_assertions':failures,
            'assertion_fraction':passes/(passes+failures) if passes+failures else None,
            'scoring_output':str(target.parent.parent.parent),
            'rescoring_provenance':{'original_result_sha256':p.digest(original_path),
                 'db_files_byte_identical':True,'new_llm_calls':0,'scorer_source_unchanged':True}}
    p.save(directory/'rescored_result.json',result)
    p.log(log,'rescored_result',**result)
    print(json.dumps({k:result[k] for k in ['id','official_success','passed_assertions','failed_assertions']},indent=2))


if __name__=='__main__':main()
