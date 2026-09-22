"""Finite, observational role contracts; agreement is NOT semantic truth."""
from __future__ import annotations
import ast
from dataclasses import dataclass
from typing import Iterable

HYPOTHESES = ('source', 'predicate', 'union', 'intersection',
              'source_minus_predicate', 'predicate_minus_source')

def evaluate(name: str, source: Iterable[int], predicate: Iterable[int]) -> frozenset:
    a, b = frozenset(source), frozenset(predicate)
    operations = {'source': a, 'predicate': b, 'union': a | b,
                  'intersection': a & b, 'source_minus_predicate': a - b,
                  'predicate_minus_source': b - a}
    if name not in operations:
        raise ValueError('Unknown hypothesis: ' + name)
    return operations[name]

@dataclass(frozen=True)
class Contract:
    hypotheses: tuple[str, ...]
    entity_type: str
    source_sha256: str

    @classmethod
    def fit(cls, records: list[dict], source_sha256: str) -> 'Contract':
        if not records:
            raise ValueError('No source observations; cannot earn a contract')
        entity = records[0]['entity_type']
        if any(r['entity_type'] != entity for r in records):
            raise ValueError('Cannot pool different entity types')
        viable = tuple(h for h in HYPOTHESES if all(
            evaluate(h, r['source'], r['predicate']) == frozenset(r['selected'])
            for r in records))
        return cls(viable, entity, source_sha256)

    def qualify(self, source, predicate, *, entity_type: str, covered: bool) -> dict:
        if not covered or entity_type != self.entity_type or not self.hypotheses:
            return {'status': 'UNKNOWN', 'selected': None}
        outputs = {evaluate(h, source, predicate) for h in self.hypotheses}
        if len(outputs) != 1:
            return {'status': 'UNKNOWN', 'selected': None}
        return {'status': 'SUPPORTED_IN_GRAMMAR', 'selected': sorted(next(iter(outputs)))}

def first_consumer_boundary(steps: list[dict]) -> tuple[int, str]:
    for index, row in enumerate(steps):
        tree = ast.parse(row['code'])
        for node in ast.walk(tree):
            if not isinstance(node, ast.For):
                continue
            has_download = any(isinstance(n, ast.Call) and
                ast.unparse(n.func) == 'apis.spotify.download_song' for n in ast.walk(node))
            if not has_download:
                continue
            it = node.iter
            if isinstance(it, ast.Call) and ast.unparse(it.func) == 'sorted' and len(it.args) == 1:
                it = it.args[0]
            if not isinstance(it, ast.Name):
                raise ValueError('Unsupported consumer iteration; no guessed patch')
            return index, it.id
    raise ValueError('No actual download consumer found')

def replace_handoff(code: str, target_name: str) -> str:
    tree = ast.parse(code)
    assignments = [n for n in tree.body if isinstance(n, ast.Assign) and
                   any(isinstance(t, ast.Name) and t.id == target_name for t in n.targets)]
    if len(assignments) > 1:
        raise ValueError('Ambiguous handoff assignment')
    replacement = ast.Name(id='role_handoff_ids', ctx=ast.Load())
    if assignments:
        assignments[0].value = replacement
    else:
        tree.body.insert(0, ast.Assign(
            targets=[ast.Name(id=target_name, ctx=ast.Store())], value=replacement))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def library_adapter(instruction: str) -> tuple[str, str]:
    text = instruction.lower()
    if 'album library' in text:
        return 'show_album_library', 'song_ids'
    if 'song library' in text:
        return 'show_song_library', 'song_id'
    if 'playlists' in text:
        return 'show_playlist_library', 'song_ids'
    raise ValueError('Unsupported public task scope; do not infer from task id')
