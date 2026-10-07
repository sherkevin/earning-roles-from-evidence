"""Check saved evidence without rerunning experiments or generators."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CAPTURE = ROOT / 'experiments/logs/n03_pipe1_native_material_audit_20261007_v1'
TZ = ROOT / 'experiments/logs/n03_pipe1_timezone_audit_20261007_v1'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert read(OUT / 'config.json')['status'] == 'FROZEN_BEFORE_CHECKS'
    summary = read(CAPTURE / 'summary.json')
    assert summary['generator_calls'] == summary['case_count'] == 4
    file_hashes = 0
    for row in summary['cases']:
        folder = CAPTURE / ('seed_' + str(row['seed']))
        for role, digest in row['view_file_sha256'].items():
            name = 'parent_only.json' if role == 'parent_only' else role + '_view.json'
            assert sha(folder / name) == digest
            file_hashes += 1
        executor = read(folder / 'executor_view.json')
        assert executor['peer_message'] is None
    manifest = read(ROOT / 'references/aamas/task_signal_materials_20261007/native_harness/manifest.json')
    for row in manifest['files']:
        assert sha(ROOT / row['local_copy']) == row['sha256']
        file_hashes += 1
    timezone_config = read(TZ / 'config.json')
    assert sha(TZ / 'audit.py') == timezone_config['source_sha256']['audit_script']
    for seed in (1, 2):
        for name in ('executor_view.json', 'parent_only.json'):
            assert sha(CAPTURE / ('seed_' + str(seed)) / name) == timezone_config['source_sha256'][f'seed_{seed}_{name}']
            file_hashes += 1
    rows = [json.loads(line) for line in (TZ / 'raw.jsonl').read_text().splitlines()]
    assert len(rows) == len({(r['seed'], r['record_index']) for r in rows}) == 20
    assert all(not r['utc_equals_shanghai'] and r['parent_matches_asia_shanghai'] and not r['parent_matches_utc'] for r in rows)
    assert read(TZ / 'summary.json')['record_count'] == 20
    for path in (ROOT / 'scripts/peerrolebench_pipe1_native_material_audit.py', TZ / 'audit.py'):
        compile(path.read_text(), str(path), 'exec')
    links = 0
    for relative in ('docs/research/candidates/benchmark_selection_value_20261007.md',
                     'docs/coordination/task_reports/20261007_selection_value_and_native_handoff.md',
                     'references/aamas/task_signal_materials_20261007/README.md'):
        path = ROOT / relative
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if target.startswith(('http:', 'https:', '#')):
                continue
            target = re.sub(r':\d+$', '', target.split('#')[0])
            assert (path.parent / target).exists(), (relative, target)
            links += 1
    result = {'status': 'STATIC_EVIDENCE_CHECKED', 'saved_file_hashes_checked': file_hashes,
              'timezone_rows_checked': len(rows), 'local_links_checked': links,
              'llm_api_calls': 0, 'gpu_runs': 0, 'generator_calls': 0,
              'candidate_executions': 0, 'grader_calls': 0,
              'scientific_readiness': False}
    (OUT / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
