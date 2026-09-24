#!/usr/bin/env python3
"""Two fresh AppWorld recipients with a frozen delivery-visibility contrast.

`check` is zero-LLM. `run` refuses the draft config and later requires matching
native-fixture and provider-health receipts. This is development-only evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
import traceback
from typing import Any

import aamas_real_probe as prior
import aamas_peer_judgment_a0_v4 as a0
import aamas_peer_judgment_smoke_v4 as base

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'configs/aamas2027/peer_delivery_visibility_dev_v1.json'
ARMS = ('visible', 'hidden')
SOURCE_PIN = '42b5bcf3cd334fee33f0c37c02070a9f5807add5'
PYTHON_PIN = ROOT.parent / 'AppWorld/.venv-b1-api/bin/python'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=str)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise a0.InfrastructureError(message)


def verify_runtime(cfg: dict[str, Any]) -> None:
    require(Path(sys.executable).absolute() == Path(cfg['python_interpreter']).absolute() and
            Path(sys.prefix).resolve() == PYTHON_PIN.parent.parent.resolve(),
            'Wrong Python interpreter for AppWorld experiment')
    require(importlib.metadata.version('appworld') == cfg['appworld_distribution_version'],
            'Wrong AppWorld installation')
    require(prior.APP.resolve() == ROOT.parent / 'AppWorld',
            'Wrong AppWorld source checkout')
    require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=prior.APP,
                                    text=True).strip() == cfg['appworld_source_commit'],
            'AppWorld source commit changed')
    require(not subprocess.check_output(['git', 'status', '--porcelain=v1',
                                         '--untracked-files=no'], cwd=prior.APP,
                                        text=True).strip(),
            'AppWorld tracked source checkout is dirty')


def source_dependency_hashes(cfg: dict[str, Any]) -> dict[str, str]:
    return {name: sha(ROOT / row['path']) for name, row in
            cfg['source_dependencies'].items()}


def verify_source_dependencies(cfg: dict[str, Any]) -> dict[str, str]:
    actual = source_dependency_hashes(cfg)
    require(actual == {name: row['sha256'] for name, row in
                       cfg['source_dependencies'].items()},
            'Imported source dependency changed')
    return actual


def record_fingerprints(world: Any) -> dict[str, str]:
    """Controller-only actual row-content fingerprints, not ORM write counters."""
    models = world.models
    require(models is not None, 'Native model collection unavailable')
    models.clear_ids_record_hashes()
    fingerprints = {}
    for app_name, names in sorted(models.items()):
        for model_name in sorted(name for name in names if name != 'SQLModel'):
            rows = models.ids_record_hashes(app_name, model_name)
            fingerprints[f'{app_name}.{model_name}'] = a0.sha_text(
                canonical(sorted(rows, key=lambda row: (row[0], row[1]))))
    require(fingerprints, 'No native record fingerprints produced')
    return fingerprints


def install_safe_native_logs(world: Any, secrets: base.Secrets) -> None:
    """Redact native log objects in memory before any post-install disk write."""
    logs_dir = Path(world.output_logs_directory)

    def safe_save_logs() -> None:
        requests = secrets.scrub(world.requester.request_tracker.requests)
        environment_io = secrets.scrub(world.environment_io)
        (logs_dir/'api_calls.jsonl').write_text(''.join(
            canonical(row)+'\n' for row in requests))
        (logs_dir/'environment_io.md').write_text(''.join(
            f"\n### Environment Interaction {row['number']}\n"
            f"```python\n{row['input']}\n```\n"
            f"```\n{row['output']}\n```\n\n" for row in environment_io))

    world.save_logs = safe_save_logs


def config(parent_validation: bool = True) -> dict[str, Any]:
    cfg = json.loads(CONFIG.read_text())
    draw = ['hidden', 'visible']
    random.Random(100).shuffle(draw)
    require(cfg['version'] == 1 and cfg['status'] in (
        'DRAFT_FOR_INDEPENDENT_REVIEW_NO_MODEL_CALLS',
        'FROZEN_PROSPECTIVE_PAIRED_DEV_V1'), 'Unknown version/status')
    require(cfg['task_id'] == '3c13f5a_3' and cfg['arm_order'] == draw and
            cfg['order_randomization']['drawn_order'] == draw and
            cfg['world_seed'] == 100 and cfg['appworld_data_version'] == '0.2.0' and
            cfg['appworld_source_commit'] == SOURCE_PIN, 'Task/order/world pin changed')
    caps = cfg['caps']
    require(tuple(caps[k] for k in ('per_arm_review_attempts','per_arm_action_attempts',
        'per_arm_total_attempts','global_new_task_attempts',
        'historical_producer_attempts_attributed_to_visible_net_cost')) ==
        (8,18,26,52,7), 'Attempt budget changed')
    provider = cfg['provider']
    require(tuple(provider[k] for k in ('cc_switch_name','expected_endpoint','model',
        'temperature','max_output_tokens_request')) ==
        ('内部','https://idealab.alibaba-inc.com/api/code','qwen3.8-max',0,1024),
        'Provider contract changed')
    require(cfg['world_constructor']['separate_processes'] and
            cfg['world_constructor']['initial_record_fingerprint_equality_required_before_actor_calls'] and
            cfg['common_prompt_source']['delivery_placeholder_is_the_only_arm_substitution'] and
            cfg['common_prompt_source']['extra_template'].count('{DELIVERY_SLOT}') == 1,
            'World/prompt isolation changed')
    require(sha(ROOT / cfg['protocol_path']) == cfg['protocol_sha256'], 'Protocol hash changed')
    verify_source_dependencies(cfg)
    if parent_validation:
        for pin in cfg['historical_pins'].values():
            require(sha(ROOT / pin['path']) == pin['sha256'], 'Historical source changed')
        common = cfg['common_prompt_source']
        require(sha(ROOT / common['historical_runner_path']) == common['historical_runner_sha256'],
                'Public base prompt source changed')
        treatment = cfg['treatment']
        require(sha(ROOT / treatment['proposal_path']) == treatment['proposal_sha256'],
                'Visible proposal changed')
    require(cfg['runner_path'] == 'scripts/aamas_delivery_visibility_dev_v1.py',
            'Runner path changed')
    require((ROOT / cfg['output_root']).resolve().is_relative_to(
            ROOT / 'artifacts/experiments/aamas2027'), 'Output path escaped project')
    return cfg


def delivery_slot(cfg: dict[str, Any], arm: str) -> str:
    if arm == 'hidden':
        return 'NO_DELIVERY'
    require(arm == 'visible', 'Unknown delivery arm')
    source = ROOT / cfg['treatment']['proposal_path']
    require(sha(source) == cfg['treatment']['proposal_sha256'], 'Visible proposal changed')
    return '<delivered_proposal>' + source.read_bytes().decode() + '</delivered_proposal>'


def render_messages(world: Any, cfg: dict[str, Any], arm: str) -> list[dict[str, str]]:
    extra = cfg['common_prompt_source']['extra_template'].replace(
        '{DELIVERY_SLOT}', delivery_slot(cfg, arm))
    return base.render_native_prompt(world, None, extra)


def validate_plan(value: Any, steps: list[dict[str, Any]], arm: str,
                  secrets: base.Secrets) -> dict[str, Any]:
    keys = {'plan_status','planned_actions','review_reason','uncertainties',
            'delivery_assessment','intended_delivery_use'}
    if not isinstance(value, dict) or set(value) != keys or len(canonical(value).encode()) > 32768:
        raise a0.ArtifactInvalid('Plan schema/size invalid')
    if secrets.contains(value):
        raise a0.ArtifactInvalid('Plan contains credential')
    if (value['plan_status'] not in ('ready','unknown') or
            not isinstance(value['planned_actions'], list) or len(value['planned_actions']) > 30 or
            not isinstance(value['review_reason'], str) or not value['review_reason'].strip() or
            not isinstance(value['uncertainties'], list) or
            not all(isinstance(s, str) for s in value['uncertainties'])):
        raise a0.ArtifactInvalid('Plan fields invalid')
    if arm == 'hidden':
        if value['delivery_assessment'] != 'not_available' or value['intended_delivery_use'] is not None:
            raise a0.ArtifactInvalid('Hidden delivery fields invalid')
    elif value['delivery_assessment'] not in ('accept','repair','reject','unknown') or (
            value['intended_delivery_use'] is not None and
            type(value['intended_delivery_use']) is not bool):
        raise a0.ArtifactInvalid('Visible delivery fields invalid')
    if value['plan_status'] == 'unknown':
        if value['planned_actions'] or not value['uncertainties'] or (
                arm == 'visible' and value['delivery_assessment'] != 'unknown'):
            raise a0.ArtifactInvalid('Unknown plan must contain no fabricated actions')
        return value
    reads = {row['step'] for row in steps if row['public_task_data_reads'] > 0}
    if not reads:
        raise a0.ArtifactInvalid('Ready plan needs its own successful public task-data GET')
    for action in value['planned_actions']:
        if (not isinstance(action, dict) or set(action) !=
                {'app','api','non_secret_arguments','public_source_steps'} or
                not isinstance(action['app'], str) or not isinstance(action['api'], str) or
                not isinstance(action['non_secret_arguments'], dict) or
                not isinstance(action['public_source_steps'], list) or
                not action['public_source_steps'] or
                any(type(step) is not int or step not in reads
                    for step in action['public_source_steps']) or
                any(base.Secrets.KEY.search(str(key))
                    for key in action['non_secret_arguments'])):
            raise a0.ArtifactInvalid('Plan action requires an own public-data GET, no secrets')
    return value


def action_use(plan: dict[str, Any], audit: list[dict[str, Any]],
               secrets: base.Secrets) -> dict[str, Any]:
    writes = [call for call in audit if call.get('origin') == 'actor' and
              call['method'] != 'get' and not call['api_path'].endswith('/auth/token') and
              not (call['app'] == 'supervisor' and call['api'] == 'complete_task')]
    matched, successful, used = [], [], set()
    for index, planned in enumerate(plan['planned_actions']):
        for call_index, call in enumerate(writes):
            arguments = a0.material_args(call['arguments'])
            expected = planned['non_secret_arguments']
            if (call_index not in used and call['app'] == planned['app'] and
                    call['api'] == planned['api'] and set(arguments) == set(expected) and
                    all(a0.equivalent(arguments[key], val) for key, val in expected.items())):
                matched.append(index)
                if call.get('ok') and not (isinstance(call.get('response'),dict) and
                        set(call['response']).intersection({'error','errors','detail'})):
                    successful.append(index)
                used.add(call_index)
                break
    return {'exact_planned_attempted_action_matches': matched,
            'matched_api_success_planned_action_indices':successful,
            'unmatched_planned_action_indices': [i for i in range(len(plan['planned_actions']))
                                                 if i not in matched],
            'actor_task_write_calls': [secrets.scrub(call) for call in writes],
            'extra_or_modified_writes': [secrets.scrub(call) for i, call in enumerate(writes)
                                         if i not in used],
            'argument_match_is_causal_proof': False,
            'api_success_is_official_transition_proof': False}


def historical_proposal_row_audit(proposal: dict[str, Any],
                                  action_use_row: dict[str, Any]) -> dict[str, Any]:
    """Offline old-artifact overlap only; hidden overlap never implies delivery use."""
    rows = proposal['requests']
    writes = action_use_row['actor_task_write_calls']
    used: set[int] = set()
    matched, modified, omitted = [], [], []
    expected_note = 'I paid for cable bill.'
    for index, row in enumerate(rows):
        candidates = [(i, call, a0.material_args(call['arguments']))
                      for i, call in enumerate(writes) if i not in used and
                      call['app'] == 'venmo' and call['api'] == 'create_payment_request']
        exact = [(i, call) for i, call, args in candidates if
                 args.get('user_email') == row['recipient_email'] and
                 a0.equivalent(args.get('amount'), row['amount_usd']) and
                 args.get('description') == expected_note]
        same_target = [(i, call, args) for i, call, args in candidates if
                       args.get('user_email') == row['recipient_email']]
        if exact:
            call_index, call = exact[0]
            matched.append({'proposal_row_index':index,'write_index':call_index,
                            'api_success':bool(call.get('ok'))})
            used.add(call_index)
        elif same_target:
            call_index, call, args = same_target[0]
            modified.append({'proposal_row_index':index,'write_index':call_index,
                             'api_success':bool(call.get('ok')),
                             'changed_fields':[field for field, same in (
                                ('amount',a0.equivalent(args.get('amount'),row['amount_usd'])),
                                ('description',args.get('description')==expected_note))
                                if not same]})
            used.add(call_index)
        else:
            omitted.append(index)
    return {'exact_attempted_proposal_row_matches':matched,
            'same_recipient_modified_writes':modified,
            'unmatched_proposal_row_indices':omitted,
            'additional_task_write_indices':[i for i in range(len(writes)) if i not in used],
            'matching_uses_historical_row_email_amount_and_task_note':True,
            'api_success_is_not_official_state_transition_proof':True,
            'content_overlap_is_not_causal_proof_of_delivery_use':True}


def install_strict_review_execute(world: Any, baseline_hashes: dict[str, Any],
                                  baseline_records: dict[str, str],
                                  raw: Path,
                                  deferred: list[tuple[str, dict[str, Any]]]) -> Any:
    """Stop before another model call if review attempted a write or changed task DB."""
    original = world.execute

    def checked(code: str) -> str:
        deferred_before = len(deferred)
        observation = original(code)
        blocked = any(event == 'write_blocked' for event, _ in deferred[deferred_before:])
        if blocked:
            a0.flush(raw, deferred)
            prior.log(raw, 'review_unsafe_write_stop',
                      observation_sha256=a0.sha_text(observation),
                      attempted_write_was_guard_blocked=True)
            raise a0.InfrastructureError('Read-only review attempted a task write')
        if (a0.task_state_hashes(world) != baseline_hashes or
                record_fingerprints(world) != baseline_records):
            a0.flush(raw, deferred)
            prior.log(raw, 'review_unsafe_state_change_stop',
                      observation_sha256=a0.sha_text(observation))
            raise a0.InfrastructureError('Read-only review changed task state')
        return observation

    world.execute = checked
    return original


def arm_episode(cfg: dict[str, Any], arm: str) -> dict[str, Any]:
    verify_runtime(cfg)
    dependencies = verify_source_dependencies(cfg)
    out = ROOT / cfg['output_root']
    manifest = json.loads((out / 'source_manifest.json').read_text())
    require(sha(CONFIG) == manifest['config_sha256'] and
            sha(Path(__file__)) == manifest['runner_sha256'] and
            sha(out / 'runner_at_execution.py') == manifest['runner_sha256'] and
            dependencies == manifest['source_dependency_hashes'],
            'Runner/config differs from execution snapshot')
    directory = out / 'arms' / arm
    raw = directory / 'raw.jsonl'
    secrets = base.Secrets()
    a0.safe_log(secrets)
    started = prior.mono()
    apis: dict[str, prior.RealAPI] = {}
    deferred: list[tuple[str, dict[str, Any]]] = []
    state = {'world_execute_count':0, 'timeout_retry_used':False,
             'action_budget_exhausted':False, 'last_phase':None,
             'validation_rejections':{'producer':0,'consumer_review':0,'consumer_action':0}}
    result: dict[str, Any] = {'arm':arm, 'task_id':cfg['task_id'], 'status':'UNKNOWN',
        'error':None, 'global_stop':False, 'action_sealed':False, 'task_completed':False,
        'official_score_available_in_actor_process':False, 'usd_cost':None}
    native = prior.APP / 'experiments/outputs' / cfg['arm_experiment_names'][arm]
    native_preexisted = native.exists()
    prior.log(raw, 'arm_config', arm=arm, task_id=cfg['task_id'],
              config_sha256=sha(CONFIG), runner_sha256=sha(Path(__file__)),
              order=cfg['arm_order'], caps=cfg['caps'], seed=cfg['world_seed'],
              provider=cfg['provider']['cc_switch_name'], model=cfg['provider']['model'],
              development_only=True, host=platform.node(), python=sys.version,
              command=sys.argv, git_head=subprocess.check_output(
                  ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    try:
        require(not native_preexisted, 'Refuse native world output overwrite')
        AppWorld, parser = prior.initialize_runtime()
        with AppWorld(task_id=cfg['task_id'], experiment_name=cfg['arm_experiment_names'][arm],
                      load_ground_truth=False, random_seed=cfg['world_seed'],
                      raise_on_extra_parameters=True) as world:
            require(world.task.ground_truth is None and world.raise_on_unsafe_execution and
                    world.task.db_version == cfg['appworld_data_version'],
                    'Unsafe or wrong-data AppWorld world')
            install_safe_native_logs(world, secrets)
            hashes = a0.task_state_hashes(world)
            records = record_fingerprints(world)
            sources: dict[str, dict[str, Any]] = {}
            probe = a0.initial_public_probe(world,'paired_initial',arm,secrets,
                                            raw,deferred,sources)
            require(a0.task_state_hashes(world) == hashes and
                    record_fingerprints(world) == records,
                    'Controller public probe changed task state')
            ready = {'arm':arm,'config_sha256':sha(CONFIG),
                     'model_write_counters':hashes,'record_fingerprints':records,
                     'probe_sha256':probe,
                     'task_spec_sha256':a0.sha_text(world.task.instruction +
                                                   canonical(str(world.task.supervisor))),
                     'data_version':world.task.db_version,'ground_truth_loaded':False,
                     'native_guard_enabled':True}
            prior.save(directory / 'ready.json', ready)
            prior.log(raw,'arm_ready_initial_state',
                      model_write_counters_sha256=a0.sha_text(canonical(hashes)),
                      record_fingerprints_sha256=a0.sha_text(canonical(records)),
                      public_probe_sha256=probe,never_actor_visible=True)
            released = False
            deadline = prior.mono() + 7200
            while prior.mono() < deadline:
                if (directory / 'cancel.json').exists():
                    raise a0.InfrastructureError('Pair cancelled before actor call')
                release = directory / 'release.json'
                if release.exists():
                    require(json.loads(release.read_text()) ==
                            {'arm':arm,'config_sha256':sha(CONFIG)},'Invalid release barrier')
                    released = True
                    break
                time.sleep(0.2)
            require(released,'Initial-state barrier timed out')
            prior.log(raw,'arm_released',arm=arm)
            provider = prior.load_provider()
            require(provider['base'] == cfg['provider']['expected_endpoint'],
                    'Provider endpoint mismatch')
            prior.log(raw,'runtime_versions',provider={k:v for k,v in provider.items()
                if k != 'secret'},package_versions={name:importlib.metadata.version(name)
                for name in ('appworld','openai','freezegun','jinja2')})
            context = {'step':0,'origin':'actor'}
            review_audit = a0.api_guard(world,'consumer_review',arm,secrets,
                                        raw,deferred,context,sources)
            original_execute = install_strict_review_execute(world, hashes, records,
                                                              raw, deferred)
            messages = render_messages(world,cfg,arm)
            if arm == 'hidden':
                require('<delivered_proposal>' not in messages[-1]['content'],
                        'Hidden delivery leaked into initial prompt')
            prior.log(raw,'initial_prompt',phase='consumer_review',
                      prompt_sha256=a0.sha_text(messages[-1]['content']),
                      prompt_characters=len(messages[-1]['content']),
                      delivery_visible=arm == 'visible')
            call_cfg = {'max_output_tokens_per_call':cfg['provider']['max_output_tokens_request'],
                        'model_request':cfg['provider']['model'],
                        'temperature':cfg['provider']['temperature']}
            apis['consumer_review'] = prior.RealAPI(raw,cfg['caps']['per_arm_review_attempts'])
            state['last_phase'] = 'consumer_review'
            plan, review_steps = a0.phase_loop(world,parser,apis['consumer_review'],
                messages,raw,'consumer_review','plan',call_cfg,secrets,review_audit,
                deferred,context,state,
                lambda value,steps:validate_plan(value,steps,arm,secrets))
            result['plan_sha256'] = a0.seal_json(directory/'pre_action_plan.json',plan,secrets)
            world.execute = original_execute
            prior.log(raw,'pre_action_plan_sealed',plan_sha256=result['plan_sha256'],
                      plan_status=plan['plan_status'],review_steps=len(review_steps),
                      review_api_calls=len(review_audit))
            require(a0.task_state_hashes(world) == hashes and
                    record_fingerprints(world) == records,
                    'Read-only review changed task state')
            if plan['plan_status'] == 'unknown':
                result['stop_reason'] = 'public_evidence_insufficient_plan_unknown'
                result['review_world_steps'] = len(review_steps)
                world.save()
            else:
                context = {'step':0,'origin':'actor'}
                action_audit = a0.api_guard(world,'consumer_action',arm,secrets,
                                            raw,deferred,context,sources)
                messages.append({'role':'user','content':
                    'Your pre-action plan is sealed. You may now use public write APIs, '
                    'inspect and repair as needed, and finish the supervisor task. '
                    'Do not use private evaluator data. Your actual calls are audited '
                    'separately from your plan.'})
                apis['consumer_action'] = prior.RealAPI(raw,cfg['caps']['per_arm_action_attempts'])
                state['last_phase'] = 'consumer_action'
                _,action_steps = a0.phase_loop(world,parser,apis['consumer_action'],
                    messages,raw,'consumer_action',None,call_cfg,secrets,action_audit,
                    deferred,context,state)
                context['origin'] = 'controller'
                completed = world.task_completed()
                a0.flush(raw,deferred)
                context['origin'] = 'actor'
                after_action = a0.task_state_hashes(world)
                changed = sorted(name for name in hashes if hashes[name] != after_action.get(name))
                use = action_use(plan,action_audit,secrets)
                use.update({'review_world_steps':len(review_steps),
                            'action_world_steps':len(action_steps),
                            'controller_changed_models':changed,
                            'generic_model_change_is_per_action_proof':False,
                            'task_completed':completed,
                            'action_budget_exhausted':state['action_budget_exhausted']})
                result['action_use_sha256'] = a0.seal_json(directory/'action_use.json',use,secrets)
                result['action_sealed'] = True
                result['task_completed'] = completed
                result['status'] = ('ACTION_SEALED' if completed and
                    not state['action_budget_exhausted'] else 'UNKNOWN')
                result['stop_reason'] = ('task_completed' if result['status']=='ACTION_SEALED'
                    else 'action_cap_or_uncompleted_unknown')
                prior.log(raw,'action_sealed',action_use_sha256=result['action_use_sha256'],
                          task_completed=completed,action_budget_exhausted=
                          state['action_budget_exhausted'],changed_models=changed)
                world.save()
        if not native_preexisted:
            base.sanitize_native_logs(native,secrets)
    except Exception as exc:
        result['status'] = 'UNKNOWN'
        result['error'] = {'type':type(exc).__name__,'message':secrets.scrub(str(exc)),
                           'traceback':secrets.scrub(traceback.format_exc())}
        result['stop_reason'] = secrets.scrub(str(exc))
        result['stop_phase'] = state['last_phase']
        result['global_stop'] = isinstance(exc,(a0.InfrastructureError,PermissionError))
        result['infrastructure_error_category'] = (
            'provider_transport' if isinstance(exc,a0.TransportUnknown) else
            'phase_cap' if isinstance(exc,a0.PhaseExhausted) else
            'infrastructure_contract' if result['global_stop'] else
            'unexpected_'+type(exc).__name__)
        if result['infrastructure_error_category'].startswith('unexpected_'):
            result['global_stop'] = True
        prior.log(raw,'arm_error',**result['error'],
                  category=result['infrastructure_error_category'],
                  global_stop=result['global_stop'])
        try:
            from appworld import AppWorld
            AppWorld.close_all()
        except Exception:
            pass
    finally:
        a0.flush(raw,deferred)
        if not native_preexisted:
            base.sanitize_native_logs(native,secrets)
        result['phase_costs'] = {phase:a0.usage(api) for phase,api in apis.items()}
        result['attempted_task_calls'] = sum(api.attempts for api in apis.values())
        result['world_execute_count'] = state['world_execute_count']
        result['validation_rejections'] = state['validation_rejections']
        result['timeout_retry_used'] = state['timeout_retry_used']
        result['wall_seconds'] = prior.mono()-started
        prior.save(directory/'result.json',secrets.scrub(result))
        prior.log(raw,'arm_result',**result)
    return result


def preflights(cfg: dict[str, Any]) -> dict[str, Any]:
    receipts = {}
    for key in ('native_fixture_path','provider_health_path'):
        path = ROOT / cfg['preflight'][key]
        require(path.exists(),f'Missing {key} preflight')
        row = json.loads(path.read_text())
        require(row.get('ok') is True and row.get('config_sha256') == sha(CONFIG) and
                row.get('runner_sha256') == sha(Path(__file__)),
                f'{key} failed or refers to another source')
        receipts[key] = {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
    return receipts


def run_all(cfg: dict[str, Any]) -> None:
    require(cfg['status']=='FROZEN_PROSPECTIVE_PAIRED_DEV_V1',
            'Draft config blocks all task model calls')
    verify_runtime(cfg)
    dependencies = verify_source_dependencies(cfg)
    receipts = preflights(cfg)
    out = ROOT / cfg['output_root']
    out.mkdir(parents=True,exist_ok=False)
    (out/'frozen_config.json').write_bytes(CONFIG.read_bytes())
    require(sha(out/'frozen_config.json') == sha(CONFIG),
            'Frozen config byte snapshot mismatch')
    runner_bytes = Path(__file__).read_bytes()
    (out/'runner_at_execution.py').write_bytes(runner_bytes)
    source_snapshots = out/'source_snapshots'
    source_snapshots.mkdir()
    for name,row in cfg['source_dependencies'].items():
        (source_snapshots / (name+'.py')).write_bytes((ROOT/row['path']).read_bytes())
    manifest = {'config_sha256':sha(CONFIG),
                'runner_sha256':hashlib.sha256(runner_bytes).hexdigest(),
                'protocol_sha256':cfg['protocol_sha256'],
                'proposal_sha256':cfg['treatment']['proposal_sha256'],
                'source_dependency_hashes':dependencies,
                'preflight':receipts,'arm_order':cfg['arm_order'],
                'python':sys.version,'sys_executable':sys.executable,
                'sys_prefix':sys.prefix,
                'versions':{name:importlib.metadata.version(name)
                    for name in ('appworld','openai','freezegun','jinja2')},
                'development_only':True}
    prior.save(out/'source_manifest.json',manifest)
    raw = out/'run_raw.jsonl'
    prior.log(raw,'run_reserved',config_sha256=manifest['config_sha256'],
              runner_sha256=manifest['runner_sha256'],
              protocol_sha256=manifest['protocol_sha256'],
              arm_order=cfg['arm_order'],cap=cfg['caps']['global_new_task_attempts'],
              preflight=receipts,scorer_hidden_until_both_sealed=True)
    processes: dict[str,subprocess.Popen] = {}
    handles = []
    for arm in ARMS:
        directory = out/'arms'/arm
        directory.mkdir(parents=True,exist_ok=False)
        stdout = (directory/'stdout.txt').open('w')
        stderr = (directory/'stderr.txt').open('w')
        handles += [stdout,stderr]
        processes[arm] = subprocess.Popen(
            [sys.executable,str(Path(__file__).resolve()),'_arm',arm],
            cwd=ROOT,stdout=stdout,stderr=stderr)
    try:
        ready: dict[str,dict[str,Any]] = {}
        deadline = prior.mono()+300
        while len(ready)<2 and prior.mono()<deadline:
            for arm in ARMS:
                path = out/'arms'/arm/'ready.json'
                if arm not in ready and path.exists():
                    ready[arm] = json.loads(path.read_text())
                if arm not in ready and processes[arm].poll() is not None:
                    raise a0.InfrastructureError(f'{arm} child exited before ready')
            time.sleep(0.2)
        require(len(ready)==2,'Two-world initial-state barrier timed out')
        keys = ('record_fingerprints','model_write_counters',
                'probe_sha256','task_spec_sha256','data_version')
        require(all(ready['visible'][key]==ready['hidden'][key] for key in keys),
                'Paired worlds have unequal initial public/task-model state')
        require(all(ready[arm]['config_sha256']==sha(CONFIG) and
                    not ready[arm]['ground_truth_loaded'] and
                    ready[arm]['native_guard_enabled'] for arm in ARMS),
                'Initial-state barrier contract failed')
        prior.log(raw,'initial_state_equal',record_fingerprints_sha256=
                  a0.sha_text(canonical(ready['visible']['record_fingerprints'])),
                  model_write_counters_sha256=
                  a0.sha_text(canonical(ready['visible']['model_write_counters'])),
                  public_probe_sha256=ready['visible']['probe_sha256'],
                  never_actor_visible=True)
        results = []
        for arm in cfg['arm_order']:
            prior.save(out/'arms'/arm/'release.json',
                       {'arm':arm,'config_sha256':sha(CONFIG)})
            prior.log(raw,'arm_released',arm=arm)
            processes[arm].wait(timeout=7200)
            result_path = out/'arms'/arm/'result.json'
            require(result_path.exists(),f'{arm} result missing')
            result = json.loads(result_path.read_text())
            results.append(result)
            prior.save(out/'partial_results.json',results)
            prior.log(raw,'arm_collected',arm=arm,result_sha256=sha(result_path),
                      status=result['status'],attempts=result['attempted_task_calls'])
            require(sum(r['attempted_task_calls'] for r in results)<=
                    cfg['caps']['global_new_task_attempts'],'Global attempt cap exceeded')
            if result['global_stop']:
                prior.log(raw,'run_stopped',reason='arm_global_stop',arm=arm)
                break
        for arm,process in processes.items():
            if process.poll() is None:
                prior.save(out/'arms'/arm/'cancel.json',{'reason':'global_stop'})
                process.wait(timeout=30)
        # No scorer import has occurred before both actors are terminal.
        prior.log(raw,'both_arms_terminal_barrier',
                  observed_arms=[r['arm'] for r in results],
                  attempted_calls=sum(r['attempted_task_calls'] for r in results),
                  all_actor_processes_closed=all(p.poll() is not None for p in processes.values()))
        # The parent alone opens the historical proposal after all actor processes
        # are closed. In the hidden arm this is content overlap, never use evidence.
        proposal_path = ROOT / cfg['treatment']['proposal_path']
        require(sha(proposal_path) == cfg['treatment']['proposal_sha256'],
                'Historical proposal changed before offline audit')
        proposal = json.loads(proposal_path.read_text())
        historical_overlap = {}
        for arm in ARMS:
            use_path = out/'arms'/arm/'action_use.json'
            if use_path.exists():
                overlap = historical_proposal_row_audit(
                    proposal,json.loads(use_path.read_text()))
                overlap['interpretation'] = ('VISIBLE_BEHAVIORAL_OVERLAP_NOT_CAUSAL_PROOF'
                    if arm == 'visible' else 'HIDDEN_INDEPENDENT_OVERLAP_NOT_DELIVERY_USE')
                path = out/'arms'/arm/'historical_proposal_overlap_offline.json'
                prior.save(path,overlap)
                historical_overlap[arm] = {'available':True,'sha256':sha(path),
                                           'interpretation':overlap['interpretation']}
            else:
                historical_overlap[arm] = {'available':False,
                                           'reason':'no_sealed_action_audit'}
        scores = {}
        if len(results)==2 and all(not r['global_stop'] for r in results):
            from appworld.evaluator import evaluate_task
            for arm in cfg['arm_order']:
                row = next(r for r in results if r['arm']==arm)
                if row['action_sealed']:
                    value = evaluate_task(task_id=cfg['task_id'],
                                          experiment_name=cfg['arm_experiment_names'][arm],
                                          suppress_errors=True,save_report=False).to_dict(stats_only=False)
                    path = out/'arms'/arm/'evaluator_only.json'
                    prior.save(path,base.Secrets().scrub(value))
                    scores[arm] = {'available':True,'success':bool(value['success']),
                                   'passes':len(value['passes']),
                                   'failures':len(value['failures']),
                                   'action_or_completion_censored':
                                   row['status']!='ACTION_SEALED',
                                   'evaluator_sha256':sha(path)}
                else:
                    scores[arm] = {'available':False,
                                   'reason':'action_censored_or_incomplete'}
        result = {'status':'PAIRED_DEVELOPMENT_DIAGNOSTIC',
                  'arm_order':cfg['arm_order'],
                  'attempted_arms':[r['arm'] for r in results],
                  'unstarted_arms':[a for a in cfg['arm_order']
                                    if a not in [r['arm'] for r in results]],
                  'new_task_attempts':sum(r['attempted_task_calls'] for r in results),
                  'historical_producer_attempts_attributed_to_visible_net_cost':7,
                  'scorer_barrier_completed':True,'scores':scores,
                  'historical_proposal_overlap_offline':historical_overlap,
                  'no_population_or_role_learning_claim':True,'arms':results}
        prior.save(out/'results.json',result)
        prior.log(raw,'run_final',results_sha256=sha(out/'results.json'),
                  new_task_attempts=result['new_task_attempts'])
    except Exception as exc:
        prior.log(raw,'run_error',type=type(exc).__name__,message=str(exc),
                  traceback=traceback.format_exc())
        for arm,process in processes.items():
            if process.poll() is None:
                prior.save(out/'arms'/arm/'cancel.json',{'reason':'parent_exception'})
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=10)
        raise
    finally:
        for handle in handles:
            handle.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('check','run','_arm'),nargs='?',default='check')
    parser.add_argument('arm',nargs='?')
    args = parser.parse_args()
    cfg = config(parent_validation=args.command!='_arm')
    if args.command=='check':
        print(canonical({'status':'contract_ok_no_model_calls',
                         'config_status':cfg['status'],
                         'config_sha256':sha(CONFIG),
                         'protocol_sha256':cfg['protocol_sha256'],
                         'order':cfg['arm_order'],'caps':cfg['caps']}))
    elif args.command=='run':
        require(args.arm is None,'run cannot override arms')
        run_all(cfg)
    else:
        require(args.arm in ARMS and cfg['status']=='FROZEN_PROSPECTIVE_PAIRED_DEV_V1',
                'Internal arm command needs an approved frozen run')
        result = arm_episode(cfg,args.arm)
        print(canonical({'arm':args.arm,'status':result['status'],
                         'attempts':result['attempted_task_calls']}))

if __name__=='__main__':
    main()
