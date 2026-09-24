#!/usr/bin/env python3
"""Deterministic, offline report for the frozen paired delivery diagnosis."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT/'configs/aamas2027/peer_delivery_visibility_dev_v1.json'
RUNNER = ROOT/'scripts/aamas_delivery_visibility_dev_v1.py'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def raw_rows(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise RuntimeError(reason)


def main() -> None:
    cfg=read_json(CFG)
    out=ROOT/cfg['output_root']
    manifest=read_json(out/'source_manifest.json')
    run=read_json(out/'results.json')
    run_rows=raw_rows(out/'run_raw.jsonl')
    require(sha(CFG)==manifest['config_sha256']==sha(out/'frozen_config.json'),
            'Frozen config provenance mismatch')
    require(sha(RUNNER)==manifest['runner_sha256']==sha(out/'runner_at_execution.py'),
            'Runner provenance mismatch')
    require(sha(ROOT/cfg['protocol_path'])==cfg['protocol_sha256']==
            manifest['protocol_sha256'],'Protocol provenance mismatch')
    require(run['arm_order']==cfg['arm_order'] and run['attempted_arms']==cfg['arm_order'],
            'Run did not attempt exact frozen order')
    require(any(row['event']=='both_arms_terminal_barrier' for row in run_rows) and
            any(row['event']=='run_final' for row in run_rows),
            'Missing completed parent raw barrier/final')
    health=read_json(ROOT/cfg['preflight']['provider_health_path'])
    fixture=read_json(ROOT/cfg['preflight']['native_fixture_path'])
    import_deviation=read_json(out/'protocol_import_deviation.json')
    prompt_isolation=read_json(out/'postrun_initial_prompt_isolation_audit.json')
    require(import_deviation['type']=='FROZEN_PROTOCOL_LITERAL_IMPORT_BARRIER_DEVIATION' and
            import_deviation['protocol_sha256']==cfg['protocol_sha256'] and
            import_deviation['zero_llm_same_venv_sys_modules_probe'][
                'evaluator_loaded_after_appworld_import'] and
            prompt_isolation['result']=='PASS',
            'Postrun protocol-deviation/prompt-isolation audit mismatch')
    require(health['ok'] and fixture['ok'] and
            all(row['config_sha256']==sha(CFG) and row['runner_sha256']==sha(RUNNER)
                for row in (health,fixture)), 'Preflight provenance mismatch')
    arms={}
    for arm in cfg['arm_order']:
        directory=out/'arms'/arm
        row=read_json(directory/'result.json')
        events=raw_rows(directory/'raw.jsonl')
        counts=Counter(event['event'] for event in events)
        api=[event['payload'] for event in events if event['event']=='public_api_call']
        actor=[call for call in api if call.get('origin')=='actor']
        actor_gets=[call for call in actor if call['method']=='get']
        failed_calls=[call for call in actor if not call.get('ok')]
        task_reads=[call for call in actor_gets if call.get('public_read_observation')]
        auth=[call for call in actor if call['method']!='get' and
              call['api']=='login' and '/auth/' in call['api_path']]
        task_writes=[call for call in actor if call['method']!='get' and
                     call not in auth and
                     not (call['app']=='supervisor' and call['api']=='complete_task')]
        completion=[call for call in actor if call['app']=='supervisor' and
                    call['api']=='complete_task']
        attempted=counts['request_start']
        responses=counts['response']
        errors=counts['request_error']
        require(attempted==row['attempted_task_calls']==
                sum(phase['attempts'] for phase in row['phase_costs'].values()),
                arm+' request-count disagreement')
        require(responses+errors==attempted,arm+' unanswered request not classified')
        require(counts['environment_observation']==row['world_execute_count'],
                arm+' world-step disagreement')
        require(len(task_writes)==0 and not row['action_sealed'] and
                not row['task_completed'] and row['status']=='UNKNOWN',
                arm+' unexpectedly completed an action')
        phase=row['phase_costs']['consumer_review']
        arms[arm]={
            'status':row['status'],
            'stop_reason':row['stop_reason'],
            'stop_phase':row['stop_phase'],
            'infrastructure_error_category':row['infrastructure_error_category'],
            'attempted_llm_calls':attempted,'returned_responses':responses,
            'request_errors':errors,
            'unknown_usage_attempts':phase['unknown_usage_attempts'],
            'tokens':phase['tokens'],'provider_api_seconds':phase['api_seconds'],
            'wall_seconds':row['wall_seconds'],
            'world_steps':row['world_execute_count'],
            'actor_public_get_calls':len(actor_gets),
            'actor_failed_public_calls':[{'step':call['step'],'app':call['app'],
                                          'api':call['api'],
                                          'error_type':call.get('error_type')}
                                         for call in failed_calls],
            'actor_successful_task_data_get_calls':len(task_reads),
            'actor_task_data_get_steps':sorted(set(call['step'] for call in task_reads)),
            'actor_task_data_get_apis':dict(sorted(Counter(
                call['app']+'.'+call['api'] for call in task_reads).items())),
            'auth_login_posts':len(auth),
            'actor_task_write_calls':len(task_writes),
            'complete_task_calls':len(completion),
            'pre_action_plan_sealed':(directory/'pre_action_plan.json').exists(),
            'action_audit_sealed':(directory/'action_use.json').exists(),
            'official_score_available':run['scores'][arm]['available'],
            'official_task_state_assertions':None,
            'official_completion_answer_assertion':None,
            'official_overall_success':None,
            'historical_proposal_row_match':None,
            'raw_sha256':sha(directory/'raw.jsonl'),
            'result_sha256':sha(directory/'result.json'),
            'native_experiment_name':cfg['arm_experiment_names'][arm]}
    require(sum(a['attempted_llm_calls'] for a in arms.values())==
            run['new_task_attempts']==16,'Run total disagrees with raw')
    historical=cfg['historical_context_not_model_input']
    producer=historical['producer_reported_tokens']
    visible=arms['visible']
    hidden=arms['hidden']
    visible_full={
        'attempted_llm_calls':historical['producer_attempts']+
                              visible['attempted_llm_calls'],
        'reported_tokens':{key:producer.get(key,0)+visible['tokens'].get(key,0)
                           for key in visible['tokens']},
        'provider_api_seconds':historical['producer_provider_api_seconds']+
                               visible['provider_api_seconds'],
        'historical_producer_attribution_is_not_new_call':True}
    processed={
        'status':'PAIRED_QUALITY_COMPARISON_INDETERMINATE_BOTH_REVIEW_CAPPED',
        'selection':'One posthoc selected AppWorld train case; development only',
        'raw_provenance':{'config_sha256':sha(CFG),'runner_sha256':sha(RUNNER),
                          'protocol_sha256':cfg['protocol_sha256'],
                          'manifest_sha256':sha(out/'source_manifest.json'),
                          'run_raw_sha256':sha(out/'run_raw.jsonl'),
                          'results_sha256':sha(out/'results.json'),
                          'fixture_sha256':sha(ROOT/cfg['preflight']['native_fixture_path']),
                          'health_sha256':sha(ROOT/cfg['preflight']['provider_health_path'])},
        'postrun_initial_prompt_isolation_audit_sha256':sha(
            out/'postrun_initial_prompt_isolation_audit.json'),
        'protocol_import_deviation_sha256':sha(out/'protocol_import_deviation.json'),
        'protocol_import_deviation':{
            'evaluator_module_implicitly_imported_before_actor_terminal':True,
            'actor_evaluate_task_calls':0,
            'any_actor_world_ground_truth_loaded':False,
            'score_or_label_in_actor_prompt_observed':False,
            'scorer_barrier_completed_means_no_explicit_scorer_call_before_both_terminal':True,
            'strict_no_import_barrier_met':False},
        'preflight':{'zero_llm_fixture_calls':fixture['llm_calls'],
                     'separate_real_health_attempts':health['real_provider_attempts'],
                     'health_ok':health['ok']},
        'arms':arms,
        'new_task_attempted_calls':run['new_task_attempts'],
        'new_task_returned_responses':sum(a['returned_responses'] for a in arms.values()),
        'new_task_request_errors':sum(a['request_errors'] for a in arms.values()),
        'new_task_unknown_usage_attempts':sum(a['unknown_usage_attempts']
                                               for a in arms.values()),
        'visible_full_system_cost_with_historical_producer':visible_full,
        'hidden_recipient_system_cost':{'attempted_llm_calls':hidden['attempted_llm_calls'],
            'reported_tokens':hidden['tokens'],
            'provider_api_seconds':hidden['provider_api_seconds']},
        'quality_cost_gate':'INDETERMINATE_NO_PREACTION_PLANS_OR_ACTIONS_OR_OFFICIAL_SCORES',
        'actual_proposal_visibility_effect':'NOT_ESTIMABLE',
        'role_learning_tested':False,
        'method_or_population_claim':False,
        'usd_cost':None,
        'no_task_write_evidence':all(a['actor_task_write_calls']==0
                                     for a in arms.values())}
    processed_path=out/'processed_results.json'
    require(not processed_path.exists(),'Refuse processed overwrite')
    processed_path.write_text(json.dumps(processed,ensure_ascii=False,indent=2)+'\n')
    def token_line(tokens):
        return (f"{tokens['input_tokens']}/{tokens['output_tokens']}/"
                f"{tokens['cache_read_input_tokens']}/"
                f"{tokens['cache_creation_input_tokens']}")
    lines=[
        '# 交付可见性配对开发诊断：两臂均在审阅额度处删失',
        '',
        '已按前瞻冻结顺序在同一 AppWorld train 任务 `3c13f5a_3` 的两个全新、'
        '初态内容指纹相等的世界运行 visible → hidden。两臂都在 8 次审阅模型尝试后'
        '未封存事前计划，均未进入行动；因此**不能判断交付可见性的任务质量或净成本效应**。'
        '这不是官方失败率、方法负结果或角色学习实验。',
        '',
        '| 臂 | 模型尝试/响应 | 公开 GET / 任务数据 GET | 计划/行动/任务写入 | 状态 |',
        '|---|---:|---:|---|---|',
    ]
    for arm in cfg['arm_order']:
        a=arms[arm]
        lines.append(f"| {arm} | {a['attempted_llm_calls']}/{a['returned_responses']} | "
                     f"{a['actor_public_get_calls']}/{a['actor_successful_task_data_get_calls']} | "
                     f"无/无/{a['actor_task_write_calls']} | UNKNOWN/review cap |")
    lines += ['',
        '两个臂均无 `complete_task` 调用，官方 evaluator 未运行，任务状态断言、'
        '完成答案断言和整体 success 均为**未测**。旧 v4 交付逐行采纳/修改/舍弃也'
        '无法审计，因为没有行动。visible 直到第 8 步才首次成功读到任务数据，且仅为文件目录；'
        '没有读账单金额或室友联系人。hidden 在第 4/5 步读取目录、日期及账单文件，'
        '第 8 步只查询联系人关系类型，仍未查到实际室友条目。'
        '两臂各有一次 phone 登录失败并在后续尝试修复；这些是公开 API 轨迹，'
        '不能把审阅 cap 归因于 API 故障或交付质量。目录 GET 本身也不足以支持金额/收件人主张，'
        '须逐项来源审计。',
        '',
        '成本 token 顺序为 input/output/cache-read/cache-creation；均为提供商报告值：',
        '',
        '| 口径 | 请求 | token 四类 | provider API 秒 | 未知用量 |',
        '|---|---:|---:|---:|---:|',
        f"| visible 接收者 | {visible['attempted_llm_calls']} | "
        f"{token_line(visible['tokens'])} | {visible['provider_api_seconds']:.3f} | "
        f"{visible['unknown_usage_attempts']} |",
        f"| visible 全系统（含历史生产者） | {visible_full['attempted_llm_calls']} | "
        f"{token_line(visible_full['reported_tokens'])} | "
        f"{visible_full['provider_api_seconds']:.3f} | 0（历史报告口径） |",
        f"| hidden 接收者 | {hidden['attempted_llm_calls']} | "
        f"{token_line(hidden['tokens'])} | {hidden['provider_api_seconds']:.3f} | "
        f"{hidden['unknown_usage_attempts']} |",
        '',
        '共 16 次真实任务请求、16 次返回、0 次传输错误；另有独立健康请求 1 次，'
        '不计入任务额度。两个臂都按冻结规则自然结束，父进程写有 '
        '`both_arms_terminal_barrier` 和 `run_final`。受审阅额度删失，'
        '预定的质量—全系统成本解释门为 **INDETERMINATE**；'
        '不能把 visible 更高的成本或 hidden 更多的读取解释为交付的因果效果。',
        '',
        '**冻结协议字面偏差：** AppWorld 包在导入 `AppWorld` 时隐式导入 '
        '`appworld.evaluator`，所以“两个 actor 封存前评分模块不得 import”并未满足。'
        '用相同虚拟环境做的零模型 `sys.modules` 复核为真，'
        '而实际 actor 进程没有直接记录 `sys.modules`；源码顶层导入加上已记录的'
        '世界初始化构成这一判断。两臂 `load_ground_truth=False`，actor 期间没有'
        '`evaluate_task` 调用，也未观察到标签或评分进入模型；'
        '`scorer_barrier_completed` 只能表示**显式离线评分调用屏障**，不能表示模块未导入。'
        '偏差的[原始核查](protocol_import_deviation.json)单独保留，'
        '不改变两臂删失及不可判定结论。实际首请求的[字节隔离核查]'
        '(postrun_initial_prompt_isolation_audit.json)则确认初始模板仅交付槽不同。',
        '',
        '该任务由已观察到交付结果的 train 单例事后选出，AppWorld 原生是单用户任务；'
        '本配对只诊断交付可见性，既无自然多主体协作依赖，也无跨任务角色状态。'
        '下一步需要另行冻结多家族或自然依赖任务的探针，不能在本例按结果调提示或额度。',
        '',
        f"原始结果：[results.json]({out/'results.json'})；"
        f"逐次日志：[run_raw.jsonl]({out/'run_raw.jsonl'}) 与各臂 `raw.jsonl`；"
        f"机器汇总：[processed_results.json]({processed_path})。",
        '',
        f"配置 SHA256 `{sha(CFG)}`；runner `{sha(RUNNER)}`；"
        f"协议 `{cfg['protocol_sha256']}`；results `{sha(out/'results.json')}`。",
        ''
    ]
    report_path=out/'report.md'
    require(not report_path.exists(),'Refuse report overwrite')
    report_path.write_text('\n'.join(lines))
    print(json.dumps({'processed_results':str(processed_path),
                      'processed_sha256':sha(processed_path),
                      'report':str(report_path),'report_sha256':sha(report_path),
                      'status':processed['status']},ensure_ascii=False))


if __name__=='__main__':
    main()
