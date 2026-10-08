#!/usr/bin/env python3
"""Read saved requests and literal domain definitions; never execute task code."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'experiments/logs/n03_c1_pipe3_bounded_live_20261006_v4'
NATIVE = ROOT / 'experiments/logs/n03_pipe1_native_material_audit_20261007_v1'
SOURCES = ROOT / 'references/aamas/task_signal_materials_20261007/upstream/generators'
ARMS = ('no_update', 'contextual_trust_linear', 'RARE')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def domains(path):
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'DOMAINS' for t in n.targets))
    return ast.literal_eval(node.value)


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    inputs = [Path(__file__).resolve(), SOURCES / 'gen_pipe1_etl_fix.py',
              SOURCES / 'gen_pipe3_stream_processing.py', LIVE / 'config.json']
    request_files = {}
    for arm in ARMS:
        inputs.append(LIVE / arm / 'material_manifest.json')
        request_files[arm] = [LIVE / arm / f'decision_{i}/judgment/judgment_request.json'
                              for i in (0, 1)
                              if (LIVE / arm / f'decision_{i}/judgment/judgment_request.json').is_file()]
        inputs.extend(request_files[arm])
    for seed in (0, 3):
        inputs.extend(NATIVE / f'seed_{seed}' / name for name in
                      ('planner_view.json', 'executor_view.json', 'parent_only.json'))
    hashes = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in inputs}
    historical_commit = json.loads((LIVE / 'config.json').read_text())['source_commit']
    historical_runner = subprocess.check_output([
        'git', 'show', historical_commit + ':scripts/peerrolebench_c1_pipe3_bounded_live.py'])
    # Seal the configuration before comparisons; no generator/import/candidate/API.
    write(out / 'config.json', {'kind': 'SAVED_MATERIAL_COMPARISON_NOT_MODEL_EXPERIMENT',
          'started_utc': datetime.now(timezone.utc).isoformat(), 'command': sys.argv,
          'project_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
          'input_sha256': hashes, 'historical_runner_commit': historical_commit,
          'historical_runner_sha256': sha(historical_runner),
          'api_calls': 0, 'gpu_runs': 0, 'generator_calls': 0, 'candidate_executions': 0})
    snapshot = out / 'source'; snapshot.mkdir()
    shutil.copyfile(Path(__file__), snapshot / Path(__file__).name)
    (snapshot / 'historical_c1_runner.py').write_bytes(historical_runner)
    rows = []
    rawlog = out / 'raw.jsonl'
    for arm in ARMS:
        payloads = []
        for request_path in request_files[arm]:
            req = json.loads(request_path.read_text())
            text = req['messages'][0]['content']
            if text.count('\nPUBLIC MATERIAL:\n') != 1:
                raise ValueError('Saved request public boundary is ambiguous')
            payloads.append(json.loads(text.split('\nPUBLIC MATERIAL:\n', 1)[1]))
        a = payloads[0] if payloads else None
        b = payloads[1] if len(payloads) > 1 else None
        # Delivered producer content may differ by selected peer: report separately.
        base = lambda p: {k: v for k, v in p.items() if k != 'source_files'}
        file_keys = sorted(set(a['source_files']) | set(b['source_files'])) if a and b else []
        row = {'arm': arm, 'request_count': len(payloads),
               'source_payload_seed': a['seed'] if a else None, 'target_payload_seed': b['seed'] if b else None,
               'task_contract_identical': bool(a and b and base(a) == base(b)),
               'source_contract_sha256': sha(canonical(base(a))) if a else None,
               'target_contract_sha256': sha(canonical(base(b))) if b else None,
               'same_files': [k for k in file_keys if a['source_files'].get(k) == b['source_files'].get(k)] if a and b else [],
               'different_files': [k for k in file_keys if a['source_files'].get(k) != b['source_files'].get(k)] if a and b else [],
               'all_payload_identical': bool(a and b and a == b),
               'material_manifest_seed': json.loads((LIVE / arm / 'material_manifest.json').read_text())['seed']}
        rows.append(row)
        with rawlog.open('a') as f:
            f.write(json.dumps({'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                               'event': 'saved_source_target_comparison', 'payload': row}) + '\n')
    pipe1 = domains(SOURCES / 'gen_pipe1_etl_fix.py')
    rulekeys = ('field_map', 'type_conversions', 'nested_fields', 'enum_maps', 'null_rules')
    rules = [{k: pipe1[i][k] for k in rulekeys} for i in (0, 3)]
    source_rules = {k + ':' + json.dumps(v, sort_keys=True) for k, v in rules[0].items()}
    target_rules = {k + ':' + json.dumps(v, sort_keys=True) for k, v in rules[1].items()}
    pipe1_pair = {'source_seed': 0, 'target_seed': 3, 'source_domain': pipe1[0]['name'],
                 'target_domain': pipe1[3]['name'], 'rule_digests': [sha(canonical(r)) for r in rules],
                 'exact_rule_groups_shared': sorted(source_rules & target_rules),
                 'source_rule_groups': rules[0], 'target_rule_groups': rules[1],
                 'contains_fromtimestamp': ['fromtimestamp' in json.dumps(r) for r in rules],
                 'structural_roots': 1, 'generalization_evidence': False,
                 'overlap_measure': 'Exact whole rule-group equality; not semantic independence'}
    write(out / 'pipe1_rule_pair.json', pipe1_pair)
    summary = {'status': 'MATERIAL_AUDIT_COMPLETED',
               'saved_judgment_requests': sum(len(v) for v in request_files.values()),
               'source_target_rows': rows, 'pipe1_pair': {k: v for k, v in pipe1_pair.items()
                    if k not in ('source_rule_groups', 'target_rule_groups')},
               'api_calls': 0, 'gpu_runs': 0, 'generator_calls': 0, 'candidate_executions': 0,
               'scientific_claim_allowed': False, 'historical_results_modified': False}
    write(out / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    run(parser.parse_args().out.resolve())
