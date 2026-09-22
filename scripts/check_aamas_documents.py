"""Check the two canonical AAMAS documents and derive a conservative release gate.

This checks document consistency, not scientific validity. Only a human-reviewed
VERIFIED requirement row can become verified in the machine gate.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / 'docs/paper/aamas2027/REQUIREMENTS.md'
TASKS = ROOT / 'docs/coordination/AAMAS_TASKS.md'
GATE = ROOT / 'docs/paper/aamas2027/submission_gate.json'
REPORT = ROOT / 'artifacts/analysis/aamas2027/document_check.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(text, prefix):
    found = {}
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if cells and re.fullmatch(prefix + r'\d{2}', cells[0]):
            if cells[0] in found:
                raise ValueError('Duplicate row: ' + cells[0])
            found[cells[0]] = cells[1:]
    return found


def check(sync_gate=False, check_gate=False):
    requirements = REQ.read_text(encoding='utf-8')
    tasks = TASKS.read_text(encoding='utf-8')
    req_ids = re.findall(r'^### (A-R\d{2})\b', requirements, re.M)
    task_ids = re.findall(r'^### (A-T\d{2})\b', tasks, re.M)
    gaps, queue, reviews = rows(tasks, 'A-R'), rows(tasks, 'A-T'), rows(requirements, 'V')
    assert req_ids and len(req_ids) == len(set(req_ids)), 'Missing/duplicate requirement sections'
    assert task_ids and len(task_ids) == len(set(task_ids)), 'Missing/duplicate task cards'
    assert set(req_ids) == set(gaps), 'Requirement/gap coverage differs'
    assert set(task_ids) == set(queue), 'Task cards/queue coverage differs'
    assert set(reviews) == {f'V{i:02d}' for i in range(1, 14)}, 'Actual-review coverage differs'
    allowed_req = {'OPEN', 'PARTIAL', 'WAITING_AUTHOR', 'VERIFIED', 'SCOPE_REVISED'}
    allowed_task = {'TODO', 'READY', 'RUNNING', 'DONE', 'STOPPED', 'WAITING_AUTHOR', 'BLOCKED', 'SCOPE_REVISED', 'SUPERSEDED'}
    mapping = {}
    for key, cells in gaps.items():
        assert len(cells) == 3 and cells[0] in allowed_req, f'Invalid gap row: {key}'
        linked = re.findall(r'A-T\d{2}', cells[2])
        assert linked and set(linked) <= set(task_ids), f'Uncovered requirement: {key}'
        mapping[key] = linked
    for key, cells in reviews.items():
        linked = re.findall(r'A-R\d{2}', cells[-1])
        assert linked and set(linked) <= set(req_ids), f'Unmapped review: {key}'
    graph = {}
    for key, cells in queue.items():
        assert len(cells) == 4 and cells[1] in allowed_task, f'Invalid queue row: {key}'
        graph[key] = re.findall(r'A-T\d{2}', cells[2])
        assert set(graph[key]) <= set(task_ids), f'Unknown dependency: {key}'
    visited = set()

    def visit(key, active):
        assert key not in active, f'Cyclic task dependency: {key}'
        if key not in visited:
            for dependency in graph[key]:
                visit(dependency, active | {key})
            visited.add(key)

    for key in graph:
        visit(key, set())

    link_files = [REQ, TASKS,
        ROOT / 'docs/paper/aamas2027/VENUE_REQUIREMENTS.md',
        ROOT / 'docs/scientist/analysis/S-518_AAMAS_positioning_20260916.md',
        ROOT / 'docs/scientist/analysis/S-518_reviewer_action_matrix_20260916.md',
        ROOT / 'docs/scientist/handoffs/S-518_to_engineer_AAMAS_experiments_20260916.md',
        ROOT / 'article/aamas2027/README.md',
        ROOT / 'references/aamas/README.md',
        ROOT / 'docs/archive/aamas2027/s518/README.md']
    local_links = 0
    for path in link_files:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            target = target.strip('<>').split('#', 1)[0]
            assert (path.parent / target).exists(), f'Broken link in {path}: {target}'
            local_links += 1
    archive = ROOT / 'docs/archive/aamas2027/s518'
    archived = json.loads((archive / 'manifest.json').read_text(encoding='utf-8-sig'))
    for item in archived:
        assert sha(archive / item['archive_file']) == item['sha256'], 'Historical snapshot changed'
    gate = {
        'target': 'AAMAS 2027 Main Track, proposed area GAAI',
        'status': 'requirements_verified' if all(v[0] == 'VERIFIED' for v in gaps.values()) else 'internal_revision_not_submission_ready',
        'authority': TASKS.relative_to(ROOT).as_posix(),
        'requirements_document': REQ.relative_to(ROOT).as_posix(),
        'requirements_sha256': sha(REQ),
        'task_ledger_sha256': sha(TASKS),
        'requirements': {key: 'verified' if gaps[key][0] == 'VERIFIED' else 'pending' for key in req_ids},
        'requirement_tasks': mapping,
        'release_boundary': 'A-R15 gates author prerequisites and abstract ID; full-paper receipt and future rebuttal follow release. SCOPE_REVISED alone is not verified.',
    }
    if sync_gate:
        GATE.write_text(json.dumps(gate, indent=2) + '\n', encoding='utf-8')
    if check_gate:
        assert json.loads(GATE.read_text(encoding='utf-8')) == gate, 'Stale machine gate; run check_aamas_documents.py --sync-gate after reviewed ledger edits'
    report = {
        'requirements': len(req_ids), 'review_groups': len(reviews), 'tasks': len(task_ids),
        'local_links_checked': local_links, 'archived_snapshots_verified': len(archived),
        'acyclic_dependencies': True, 'task_statuses': dict(Counter(v[1] for v in queue.values())),
        'all_requirements_mapped': True, 'all_reviews_mapped': True,
        'requirements_sha256': sha(REQ), 'task_ledger_sha256': sha(TASKS),
        'scientific_readiness': False if any(v[0] != 'VERIFIED' for v in gaps.values()) else 'requires_author_and_artifact_release_check',
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sync-gate', action='store_true')
    parser.add_argument('--check-gate', action='store_true')
    args = parser.parse_args()
    check(args.sync_gate, args.check_gate)
