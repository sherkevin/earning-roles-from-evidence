"""Verify frozen design/source evidence; no model or task execution."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
config = json.loads((OUT / 'config.json').read_text())
assert config['status'] == 'FROZEN_BEFORE_CHECKS'
for name, expected in config['inspected_source_sha256'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
ref = ROOT / 'references/aamas/reflexion_memory_origin_20261007'
manifest = json.loads((ref / 'manifest.json').read_text())
for item in manifest['files']:
    assert hashlib.sha256((ref / item['path']).read_bytes()).hexdigest() == item['sha256']
links = 0
for name in config['document_paths']:
    path = ROOT / name
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if target.startswith(('http://', 'https://', '#')):
            continue
        target = re.sub(r':\d+$', '', target.split('#')[0])
        assert (path.parent / target).exists(), (name, target)
        links += 1
for index, command in enumerate(config['commands']):
    start = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (OUT / f'check_{index}.stdout.txt').write_text(result.stdout)
    (OUT / f'check_{index}.stderr.txt').write_text(result.stderr)
    with (OUT / 'raw.jsonl').open('a') as stream:
        stream.write(json.dumps({'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(),
                                 'command': command, 'returncode': result.returncode,
                                 'wall_seconds': time.monotonic() - tick}) + '\n')
    if result.returncode:
        raise RuntimeError(result.stderr)
assert json.loads((ROOT / 'artifacts/analysis/aamas2027/document_check.json').read_text())['scientific_readiness'] is False
summary = {'status': 'DESIGN_SOURCE_AND_DOCUMENT_CHECKS_PASSED',
           'inspected_local_source_hashes': len(config['inspected_source_sha256']),
           'pinned_upstream_file_hashes': len(manifest['files']), 'local_links_checked': links,
           'registry_unique_active': 6, 'scientific_readiness': False,
           'llm_api_calls': 0, 'candidate_executions': 0, 'generator_calls': 0, 'gpu_runs': 0}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
