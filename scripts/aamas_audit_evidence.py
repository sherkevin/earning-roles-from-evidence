"""Read-only reanalysis of preserved results; never invokes a model endpoint."""
from pathlib import Path
import ast
from collections import Counter
import hashlib
import importlib.util
import json
import statistics
import sys
import re
import string

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'analysis' / 's518_aamas_audit_20260916'
spec = importlib.util.spec_from_file_location('edo_evaluation', ROOT / 'workspace/idea04_core/evaluation.py')
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)

JOBS = [
    ('HotpotQA', 'e155_qwen_hotpotqa_fullval_adaptive_20260510_auto',
     'hotpotqa/seed_42/edo_adaptive_protocol_router_backbone',
     'e155_qwen_fullval_bootstrap/paired_bootstrap.json',
     'edo_adaptive_protocol_router_backbone_minus_single_agent_fullval', 7405),
    ('MuSiQue', 'e170_qwen_musique_role_pool_guarded_fullval_20260512_0030',
     'musique_role_pool_guarded/seed_42/edo_adaptive_protocol_router_musique_role_pool_guarded',
     'posthoc_baseline_compare/e170_musique_qwen_baseline_bootstrap.json', 'agentverse_mas', 4834),
    ('2Wiki', 'e182_qwen_2wiki_bridge_tool_v6_fullval_20260514_1310',
     '2wiki_fullval/seed_42/edo_adaptive_protocol_router_tool_pool_bridge_gated_v6',
     'posthoc_final_mad_compare_20260515_110641/e179_2wiki_qwen_baseline_bootstrap.json', 'mad_final', 12576),
]

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def jsonl(path):
    return [json.loads(line) for line in path.open(encoding='utf-8') if line.strip()]

def digest(path):
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results, inputs = [], []
    for dataset, stem, sub, boot, comparison, expected_n in JOBS:
        root = ROOT / 'artifacts/emergence' / stem
        directory = root / sub
        metrics = load(directory / 'metrics.json')
        predictions = jsonl(directory / 'parsed_predictions.jsonl')
        assert len(predictions) == expected_n
        assert len({r['task_id'] for r in predictions}) == expected_n
        f1 = statistics.mean(r['answer_f1'] for r in predictions)
        em = statistics.mean(r['answer_em'] for r in predictions)
        assert abs(f1 - metrics['answer_f1']) <= 0.000051
        assert abs(em - metrics['answer_em']) <= 0.000051
        rescored = [evaluation.token_f1(r['final_answer'], r['gold_answer']) for r in predictions]
        rescored_em = [evaluation.exact_match(r['final_answer'], r['gold_answer']) for r in predictions]
        assert all(abs(a - b['answer_f1']) < 1e-10 for a, b in zip(rescored, predictions))
        assert all(abs(a - b['answer_em']) < 1e-10 for a, b in zip(rescored_em, predictions))
        b = next(r for r in load(root / boot)['rows'] if r['comparison'] == comparison)
        baseline = ROOT / b['baseline_dir'].split('/idea04/', 1)[1]
        bp = baseline / 'parsed_predictions.jsonl'
        baseline_verified = False
        if bp.exists():
            other = {r['task_id']: r for r in jsonl(bp)}
            assert set(other) == {r['task_id'] for r in predictions}
            diffs = [r['answer_f1'] - other[r['task_id']]['answer_f1'] for r in predictions]
            paired_mean = statistics.mean(diffs)
            expected = b.get('delta_f1', b.get('mean_delta_f1'))
            assert abs(paired_mean - expected) < 1e-9
            baseline_verified = True
            inputs.append(digest(bp))
        result = dict(dataset=dataset, n=expected_n, f1=f1, em=em,
                      baseline=comparison, baseline_predictions_verified=baseline_verified,
                      delta=b.get('delta_f1', b.get('mean_delta_f1')),
                      ci95=b.get('f1_ci95', [b.get('ci95_low_f1'), b.get('ci95_high_f1')]),
                      tokens_per_example=metrics['api_total_tokens_per_sample'],
                      mean_outer_handoffs=metrics['mean_handoff_count'],
                      total_calls=None, wall_seconds=None,
                      raw_metrics=metrics)
        if 'baseline_metrics' in b:
            result['baseline_metrics'] = b['baseline_metrics']
        results.append(result)
        inputs.extend(digest(p) for p in [directory/'metrics.json', directory/'parsed_predictions.jsonl', root/boot])

    component_root = ROOT / 'artifacts/emergence/e432_qwen_hotpotqa_component_matrix_20260524'
    summary = load(component_root/'e432_component_matrix_summary.json')
    components = []
    for row in summary['rows']:
        run = ROOT / row['run_dir']
        pred = jsonl(run/'parsed_predictions.jsonl')
        assert len(pred) == len({x['task_id'] for x in pred}) == 500
        assert abs(statistics.mean(x['answer_f1'] for x in pred)-row['answer_f1']) <= 0.000051
        raw_path = run / 'raw_model_outputs.jsonl'
        usage = []
        raw_count = None
        if raw_path.exists():
            raw = jsonl(raw_path)
            raw_count = len(raw)
            for event in raw:
                usage.extend(event.get('usage_calls', []))
        components.append(dict(label=row['label'], f1=row['answer_f1'], em=row['answer_em'],
                               comparisons=row['comparisons'], logged_usage_records=len(usage),
                               logged_total_tokens=sum(u.get('total_tokens', 0) for u in usage),
                               raw_event_rows=raw_count,
                               accounting_boundary='Observed usage records only; failed or unlogged calls may be absent.'))
        inputs.append(digest(run/'parsed_predictions.jsonl'))
    inputs.append(digest(component_root/'e432_component_matrix_summary.json'))

    trace_dir = component_root/'hotpotqa/seed_42/frame_full'
    trace = {}
    for name in ['parsed_predictions.jsonl','routing_traces.jsonl','raw_model_outputs.jsonl']:
        trace[name] = [r for r in jsonl(trace_dir/name) if r['task_id']=='hotpotqa-0000']
        inputs.append(digest(trace_dir/name))
    (OUT/'worked_failure_trace.json').write_text(json.dumps(trace, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
    report = dict(kind='Offline reanalysis, no new model runs', scorer='Existing project token F1 and exact match; official scorer equivalence is a separate open check',
                  headline=results, components=components, inputs=inputs)
    (OUT/'evidence_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lines = ['# S-518 preserved-evidence audit', '', 'No new model calls. All 24,815 headline predictions have unique IDs and reproduce the stored project-scored F1/EM.', '',
             '| Dataset | n | Recomputed F1 | EM | Paired delta | Archived 95% CI | Raw baseline pairing verified |',
             '|---|---:|---:|---:|---:|---|---|']
    for r in results:
        lines.append(f"| {r['dataset']} | {r['n']} | {r['f1']:.6f} | {r['em']:.6f} | {r['delta']:.6f} | {r['ci95']} | {r['baseline_predictions_verified']} |")
    ratio=results[0]['tokens_per_example']/results[0]['baseline_metrics']['api_total_tokens_per_sample']
    lines += ['', f'HotpotQA router/direct token ratio: {ratio:.6f} ({(ratio-1)*100:.2f}% more recorded API tokens).',
              '', 'The CIs above are read from archived bootstrap outputs, not newly estimated and not corrected for model selection. Missing total calls and elapsed time stay missing.',
              '', 'Component usage totals in JSON count available usage records, not independently verified attempted-call totals.',
              '', 'The actual worked failure shows a split, a REJECT_REROUTE audit label, then acceptance of an incorrect answer. A logged label is not proof that its prescribed control action was enforced.',
              '', 'Hashes cover inspected files. This does not establish that the current working-tree implementation is identical to each historical runtime.']
    (OUT/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Run only the reviewed pure answer-scoring functions, not the downloaded
    # script's imports, CLI, pickle code, or dataset loading.
    official_path = ROOT / 'references/aamas/official/hotpot_evaluate_v1.py'
    parsed = ast.parse(official_path.read_text(encoding='utf-8'))
    pure_functions = ast.Module(body=[n for n in parsed.body if isinstance(n, ast.FunctionDef)
                           and n.name in {'normalize_answer','f1_score','exact_match_score'}], type_ignores=[])
    official = {'re': re, 'string': string, 'Counter': Counter}
    exec(compile(pure_functions, str(official_path), 'exec'), official)
    hroot = ROOT/'artifacts/emergence'/JOBS[0][1]/JOBS[0][2]
    hrows = jsonl(hroot/'parsed_predictions.jsonl')
    changes = []
    scores = []
    for row in hrows:
        score = official['f1_score'](row['final_answer'], row['gold_answer'])[0]
        scores.append(score)
        if abs(score-row['answer_f1']) > 1e-12:
            changes.append(dict(id=row['task_id'],project_f1=row['answer_f1'],official_f1=score))
    parity = dict(dataset='HotpotQA',n=len(hrows),project_f1=results[0]['f1'],
                  official_f1=statistics.mean(scores),changed_rows=changes,source=digest(official_path),
                  boundary='Router only; both paired methods must be rescored for official-scored comparisons.')
    (OUT/'official_scorer_check.json').write_text(json.dumps(parity,indent=2)+'\n',encoding='utf-8')
    print('\n'.join(lines[:12]))
    print('OUTPUT', OUT)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
